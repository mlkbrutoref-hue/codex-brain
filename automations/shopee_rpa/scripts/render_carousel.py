"""Prepare or ingest complete AI-designed 3:4 carousel slides."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.carousel.pipeline import CarouselPipeline


def _path_map(path: Path | None) -> dict[int, Path]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {int(key): Path(value) for key, value in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--base-images", type=Path, help="JSON map of slide number to generated base image")
    parser.add_argument("--final-slides", type=Path, help="JSON map of slide number to complete AI-designed slide")
    parser.add_argument("--semantic-reviews", type=Path, help="Optional JSON map of slide number to review JSON")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--generation-mode",
        choices=(CarouselPipeline.FULL_AI_CREATIVE, CarouselPipeline.DETERMINISTIC_COMPOSITOR),
        default=CarouselPipeline.DEFAULT_GENERATION_MODE,
    )
    args = parser.parse_args()

    pipeline = CarouselPipeline(generation_mode=args.generation_mode)
    if args.prepare_only:
        result = pipeline.prepare(args.plan, args.output_dir)
    else:
        source_map = args.final_slides if args.generation_mode == CarouselPipeline.FULL_AI_CREATIVE else args.base_images
        if source_map is None:
            expected = "--final-slides" if args.generation_mode == CarouselPipeline.FULL_AI_CREATIVE else "--base-images"
            parser.error(f"{expected} is required unless --prepare-only is used")
        result = pipeline.run(
            args.plan,
            _path_map(source_map),
            args.output_dir,
            semantic_review_paths=_path_map(args.semantic_reviews),
        )
    print(json.dumps({"status": result["status"], "manifest": str(args.output_dir / "carousel_manifest.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
