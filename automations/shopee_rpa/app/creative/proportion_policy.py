"""Shared Nina proportion rules and evidence-aware recovery; no pixel inference."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PERSONA = ROOT / "data/personas/nina_v1"
REFERENCE_PATHS = tuple(PERSONA / "references" / name for name in ("persona_master.png", "nina_360_master.png"))
ANATOMY_CHECKS = (
    "HEAD_BODY_RATIO_FAIL", "TORSO_WIDTH_FAIL", "WAIST_SHAPE_FAIL",
    "LIMB_PROPORTION_FAIL", "MIRROR_PERSPECTIVE_FAIL", "BODY_IDENTITY_DRIFT",
    "OVERWEIGHT_INTERPRETATION_FAIL",
)


def proportion_rules() -> str:
    return (PERSONA / "proportion_rules.txt").read_text(encoding="utf-8").strip()


def negative_constraints() -> str:
    return (PERSONA / "proportion_negative.txt").read_text(encoding="utf-8").strip()


def file_hash(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review_evidence(image_path) -> dict:
    """Identity binding only; this does not perform visual inspection."""
    return {"image_sha256": file_hash(image_path), "reference_sha256": {
        path.name: file_hash(path) for path in REFERENCE_PATHS
    }}


def anatomy_checks(review, image_path, *, nina_present=True) -> dict:
    if not nina_present:
        return {name: {"status": "PASS", "reason": "Nina absent; not applicable."} for name in ANATOMY_CHECKS}
    supplied = review or {}
    try:
        bound = supplied.get("ANATOMY_EVIDENCE") == review_evidence(image_path)
    except (OSError, TypeError, ValueError):
        bound = False
    result = {}
    for name in ANATOMY_CHECKS:
        item = supplied.get(name, {})
        status = item.get("status")
        reason = str(item.get("reason", "")).strip()
        if status == "FAIL":
            result[name] = {"status": "FAIL", "reason": reason or "Anatomical defect reported."}
        elif bound and status in {"PASS", "REVIEW"} and reason:
            result[name] = {"status": status, "reason": reason}
        else:
            result[name] = {"status": "REVIEW", "reason": "Missing visual evidence tied to this image and both canonical references. Inspect visible anatomy; do not infer hidden limbs."}
    return result


def correction_prompt(original_prompt: str, issues) -> str:
    return ("Regenerate the same scene while preserving the same character identity, outfit, setting and mood. "
            "Correct only the observed anatomy and perspective defects: " + ", ".join(issues) + ". "
            "Reduce head size only if enlarged. Keep torso, waist, shoulders, hips, arms and legs coherent with the base reference. "
            "Remove close-range/wide-angle distortion through camera placement. Do not progressively slim the body. "
            "Preserve realism, mirror physics and the same feminine silhouette.\n"
            + "ORIGINAL SCENE (anatomy policy takes precedence):\n" + original_prompt
            + "\n" + proportion_rules() + "\nAVOID: " + negative_constraints())


def write_recovery(report, original_prompt, output_dir, image_path) -> Path:
    """Always rewrite state: stale recovery requests cannot survive a PASS."""
    issues = [name for name in ANATOMY_CHECKS if report.get("checks", {}).get(name, {}).get("status") in {"FAIL", "REVIEW"}]
    definite = [name for name in issues if report["checks"][name]["status"] == "FAIL"]
    pending_only = issues and all("Missing visual evidence" in report["checks"][name]["reason"] for name in issues)
    state = "NOT_REQUIRED" if not issues else ("AWAITING_VISUAL_REVIEW" if pending_only else "REGENERATION_REQUIRED")
    payload = {"status": state, "issues": issues, "definite_failures": definite,
               "source_image": str(Path(image_path).resolve()), "source_sha256": file_hash(image_path),
               "reference_paths": [str(p) for p in REFERENCE_PATHS], "max_correction_attempts": 1,
               "provider_execution": "CODEX_AGENT_OR_INJECTED_GENERATOR",
               "correction_prompt": correction_prompt(original_prompt, issues) if issues else ""}
    path = Path(output_dir) / "anatomy_recovery.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def execute_recovery(request, generate, inspect, *, attempt=0):
    """Bounded automatic recovery with explicit provider/reviewer callbacks.

    The local pipeline cannot call Codex's imagegen tool by itself. Its agent
    executes this same request, or a host injects the callbacks. No fake PASS.
    """
    if request["status"] != "REGENERATION_REQUIRED" or attempt >= request["max_correction_attempts"]:
        return {"status": "REVIEW", "generated": False}
    image = generate(request["correction_prompt"], request["reference_paths"])
    review = inspect(image, request["reference_paths"])
    checks = anatomy_checks(review, image)
    states = {item["status"] for item in checks.values()}
    return {"status": "FAIL" if "FAIL" in states else ("REVIEW" if "REVIEW" in states else "PASS"),
            "generated": True, "image": str(image), "checks": checks, "review": review, "attempt": attempt + 1}


def validate_portrait_crop(source_size, target_size=(1080, 1920), max_crop_fraction=0.05):
    """Bound permitted center crop; never squash anatomy to the target ratio."""
    sw, sh = source_size; tw, th = target_size
    scale = max(tw / sw, th / sh)
    retained = (tw * th) / ((sw * scale) * (sh * scale))
    if 1 - retained > max_crop_fraction:
        raise ValueError("UNSAFE_BODY_CROP: regenerate with 9:16 framing; do not shorten limbs by cropping")


def finish_with_recovery(manifest, request_path, output_dir, generate, inspect, rerun):
    """Pipeline hook. Provider-free operation leaves the persisted agent handoff."""
    if generate is None or inspect is None:
        return manifest
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    if request["status"] != "REGENERATION_REQUIRED":
        return manifest
    image = Path(generate(request["correction_prompt"], request["reference_paths"]))
    corrected_dir = Path(output_dir) / "correction_01"
    corrected_dir.mkdir(parents=True, exist_ok=True)
    # Review the actual normalized/composited artifact, not an earlier raw PNG.
    rerun(image, corrected_dir, None)
    review = inspect(corrected_dir / "story_final.png", request["reference_paths"])
    review_path = corrected_dir / "visual_review_source.json"
    review_path.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    corrected = rerun(image, corrected_dir, review_path)
    # Rerun omits callbacks: one attempt maximum, and all QA gates run again.
    resolution = {"initial_qa": manifest["qa_result"], "corrected_qa": corrected["qa_result"],
                  "corrected_manifest": str(corrected_dir / "manifest.json"), "attempts": 1}
    (Path(output_dir) / "recovery_resolution.json").write_text(json.dumps(resolution, indent=2), encoding="utf-8")
    return corrected
