"""Summarize local telemetry only; never calls Shopee, Antigravity or Flow."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.telemetry import summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "telemetry")
    parser.add_argument("--job-id")
    args = parser.parse_args()
    print(json.dumps(summarize(args.directory.glob("*.jsonl"), args.job_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
