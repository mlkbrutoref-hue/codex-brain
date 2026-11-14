"""Resume the inspected USB test; publishing requires the explicit --publish flag."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.mobile.shopee_video import ShopeeVideoPublisher, RpaError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--resume-evidence")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    try:
        worker = ShopeeVideoPublisher(None, config)
        result = worker.run_prepared(args.resume_evidence, publish=args.publish)
    except RpaError as exc:
        print(json.dumps(dict(state='STOP', reason=str(exc)), ensure_ascii=False))
        return 1
    print(json.dumps(dict(state=result["state"], session=str(worker.session_path)), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
