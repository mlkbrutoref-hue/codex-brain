"""Generate a validated Nina lifestyle Story plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.lifestyle_story import LifestyleHistoryStore, LifestyleStoryRequest, NinaLifestyleStoryGenerator


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan one independent Nina lifestyle Story.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--history", type=Path, default=ROOT / "data" / "lifestyle_story" / "history.json")
    args = parser.parse_args()
    request = LifestyleStoryRequest.from_dict(json.loads(args.input.read_text(encoding="utf-8-sig")))
    history = LifestyleHistoryStore(args.history).load()
    plan = NinaLifestyleStoryGenerator(ROOT).generate_to_file(request, args.output, history=history)
    print(json.dumps({"generator": plan.generator_name, "time_of_day": plan.time_of_day, "category": plan.category, "story_type": plan.story_type, "text_mode": plan.text_mode, "validation": plan.validation_status, "output": str(args.output)}, ensure_ascii=False))
    return 0 if plan.validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
