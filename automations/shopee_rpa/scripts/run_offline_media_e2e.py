"""Run the complete local synthetic media pipeline without network or AI services."""
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.media.ffmpeg import FFmpegAssembler, FFmpegLocator, SyntheticTakeFactory
from app.orchestration.pipeline import PipelineOrchestrator
from app.providers.shopee.fixture import LocalFixtureShopeeProvider
from app.providers.visual.manual_flow import ManualFlowProvider
from app.validation.media import FFprobeInspector, TechnicalMediaValidator, TechnicalQAStatus
from app.validation.visual import VisualQAResult


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    locator = FFmpegLocator(project_dir=ROOT)
    tools = locator.locate()
    print(f"FFMPEG_PATH={tools.ffmpeg or 'NOT_FOUND'}")
    print(f"FFPROBE_PATH={tools.ffprobe or 'NOT_FOUND'}")
    if not tools.complete:
        print("OFFLINE_E2E=BLOCKED_NATIVE_TOOLCHAIN")
        return 2

    job_id = "synthetic_offline_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    pipeline = PipelineOrchestrator(
        base_dir=ROOT,
        product_provider=LocalFixtureShopeeProvider(),
        visual_provider=ManualFlowProvider(),
    )
    job = pipeline.run_up_to_prompts("sample_product", job_id)
    operation = pipeline.prepare_generation(job.job_id)
    pipeline.record_generation_started(
        job.job_id, operator_confirmation=True, media_origin="SYNTHETIC"
    )
    SyntheticTakeFactory(locator).generate(Path(job.output_dir) / "generated", len(operation.scenes))
    if not pipeline.refresh_media_status(job.job_id)["all_ready"]:
        print("OFFLINE_E2E=FAIL_TAKE_INVENTORY")
        return 1

    inspector = FFprobeInspector(tools.ffprobe)
    validator = TechnicalMediaValidator(inspector)
    if any(result.status != TechnicalQAStatus.PASS
           for result in pipeline.run_technical_qa(job.job_id, validator)):
        print("OFFLINE_E2E=FAIL_TAKE_QA")
        return 1

    pipeline.complete_visual_qa(
        job.job_id, VisualQAResult.not_executed(), synthetic_fixture_waiver=True
    )
    pipeline.assemble_master(
        job.job_id,
        FFmpegAssembler(binary=tools.ffmpeg, inspector=inspector, project_dir=ROOT),
    )
    master_qa = pipeline.validate_and_package(job.job_id, validator)
    if master_qa.status != TechnicalQAStatus.PASS:
        print("OFFLINE_E2E=FAIL_MASTER_QA")
        return 1
    print(f"JOB_ID={job.job_id}")
    print("SEMANTIC_VISUAL_QA=NOT_EXECUTED")
    print("OFFLINE_E2E=PASS_SYNTHETIC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
