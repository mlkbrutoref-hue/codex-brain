"""Idempotent local media stages, bound to media bytes and upstream decisions."""
from functools import wraps
from pathlib import Path
from dataclasses import asdict
from datetime import datetime

from app.core.resume import ArtifactCache, atomic_json, read_json, exclusive
from app.core.telemetry import count
from app.models.enums import JobState
from app.validation.media import TechnicalQAResult, TechnicalQAStatus


def qa_result(data):
    data = dict(data)
    data["status"] = TechnicalQAStatus(data["status"])
    return TechnicalQAResult(**data)


def media_checkpoint(name):
    def decorate(function):
        @wraps(function)
        def wrapped(self, job_id, *args, **kwargs):
            job, directory = self._load_job(job_id)
            with exclusive(directory / ".media-operation.lock"):
                cache = ArtifactCache(directory)
                storyboard = read_json(directory / "storyboard.json", {})
                takes = [directory / "generated" / f"take_{s['scene_number']:02d}.mp4"
                         for s in storyboard.get("scenes", [])]
                inputs = [directory / "storyboard.json"] + takes
                expected = JobState.MEDIA_READY
                outputs = [directory / "technical_qa.json"]
                if name == "VisualQA":
                    expected = JobState.VISUAL_QA
                    inputs += [directory / "technical_qa.json"]
                    outputs = [directory / "semantic_visual_qa.json"]
                elif name == "Master":
                    expected = JobState.EDITING
                    assembler = args[0] if args else kwargs["assembler"]
                    config_file = directory / "normalization_config.json"
                    config = asdict(assembler.config)
                    if read_json(config_file) != config:
                        atomic_json(config_file, config)
                    inputs += [directory / "technical_qa.json", directory / "semantic_visual_qa.json", config_file]
                    outputs = [directory / "master" / "master.mp4"]
                elif name == "PlatformExports":
                    expected = JobState.VALIDATING
                    inputs = [directory / n for n in ("master/master.mp4", "product.json", "facts.json", "creative_brief.json")]
                    outputs = [directory / n for n in ("master_technical_qa.json", "platforms/shopee.mp4",
                        "platforms/instagram.mp4", "content/shopee.txt", "content/instagram.txt", "content/hashtags.json")]
                hit = cache.valid(name, inputs, outputs)
                if name == "VisualQA" and hit:
                    incoming = args[0] if args else kwargs["result"]
                    hit = read_json(outputs[0]) == incoming.to_dict()
                if hit:
                    count("resume_skips")
                    if name == "TechnicalQA":
                        return [qa_result(item) for item in read_json(outputs[0])["results"]]
                    if name == "VisualQA":
                        return job
                    if name == "Master":
                        return outputs[0]
                    return qa_result(read_json(outputs[0]))
                advanced = {JobState.VISUAL_QA, JobState.EDITING, JobState.VALIDATING, JobState.PACKAGE_READY}
                if job.state in advanced and job.state != expected:
                    # Repair local artifacts only; no generation or paid QA here.
                    if name == "Master":
                        qa_inputs = [directory / "storyboard.json"] + takes + [directory / "technical_qa.json"]
                        if not cache.valid("VisualQA", qa_inputs, [directory / "semantic_visual_qa.json"]):
                            raise ValueError("Visual QA is missing or stale; review the current media first")
                    if name == "PlatformExports" and "Master" in cache.records:
                        master_record = cache.records["Master"]
                        if not cache.valid("Master", list(master_record["dependencies"]), [directory / "master/master.mp4"]):
                            raise ValueError("Master is stale; normalize approved takes before exporting")
                    job.state = expected
                    job.updated_at = datetime.now().isoformat()
                    job.metadata["resume_repair"] = name
                    self._save_job(job)
                result = function(self, job_id, *args, **kwargs)
                current, _ = self._load_job(job_id)
                if current.state not in {JobState.FAILED, JobState.REVIEW_REQUIRED}:
                    cache.save(name, inputs, outputs)
                return result
        return wrapped
    return decorate
