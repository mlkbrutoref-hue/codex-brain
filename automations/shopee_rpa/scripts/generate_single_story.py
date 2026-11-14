"""CLI for the isolated single-story generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.single_story import SingleStoryGenerator, SingleStoryRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate one independent 9:16 Story creative package.")
    parser.add_argument("--input", required=True, type=Path, help="Request JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Creative package JSON path")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    request = SingleStoryRequest.from_dict(data)
    package = SingleStoryGenerator().generate_to_file(request, args.output)
    print(json.dumps({
        "generator": package.generator_name,
        "story_type": package.story_type,
        "validation": package.validation_status,
        "prompt_ready": package.final_image_prompt_ready,
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0 if package.validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
