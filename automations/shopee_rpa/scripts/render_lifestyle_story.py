"""Render and QA a real Nina lifestyle Story."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.lifestyle_story.pipeline import LifestyleStoryPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Render one generated lifestyle Story.")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--generated-image", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--semantic-review", type=Path)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--provider", default="CODEX_BUILT_IN_IMAGEGEN")
    args = parser.parse_args()
    manifest = LifestyleStoryPipeline().run(
        args.plan,
        args.generated_image,
        args.output_dir,
        semantic_review_path=args.semantic_review,
        image_provider=args.provider,
        history_path=args.history,
    )
    print(json.dumps({"status": manifest["status"], "qa_result": manifest["qa_result"], "story_final": str(args.output_dir / "story_final.png")}, ensure_ascii=False))
    return 0 if manifest["qa_result"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
