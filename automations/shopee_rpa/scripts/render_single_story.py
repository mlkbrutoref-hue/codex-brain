"""Render or re-QA a real single Story from a creative package and generated base."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.single_story.pipeline import RealSingleStoryPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Render one final 1080x1920 Story with deterministic typography.")
    parser.add_argument("--creative-package", type=Path)
    parser.add_argument("--generated-image", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--provider", default="CODEX_BUILT_IN_IMAGEGEN")
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--semantic-review", type=Path)
    parser.add_argument("--compare-to", type=Path, help="Prior Story output directory for anti-monotony QA")
    parser.add_argument("--refresh-qa", action="store_true")
    args = parser.parse_args()

    pipeline = RealSingleStoryPipeline()
    if args.refresh_qa:
        if not args.semantic_review:
            parser.error("--semantic-review is required with --refresh-qa")
        report = pipeline.refresh_qa(args.output_dir, args.semantic_review)
        print(json.dumps({"qa_result": report["qa_result"], "output_dir": str(args.output_dir)}, ensure_ascii=False))
        return 0 if report["qa_result"] != "FAIL" else 1
    if not args.creative_package or not args.generated_image:
        parser.error("--creative-package and --generated-image are required")
    manifest = pipeline.run(
        args.creative_package,
        args.generated_image,
        args.output_dir,
        image_provider=args.provider,
        prompt_path=args.prompt,
        semantic_review_path=args.semantic_review,
        comparison_baseline_dir=args.compare_to,
    )
    print(json.dumps({
        "status": manifest["status"],
        "qa_result": manifest["qa_result"],
        "story_final": str(args.output_dir / "story_final.png"),
    }, ensure_ascii=False))
    return 0 if manifest["qa_result"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
