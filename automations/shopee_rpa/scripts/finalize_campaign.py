"""Finalize an existing campaign into a canonical READY_TO_POST package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.campaign_finalizer import CampaignFinalizer


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign_id")
    parser.add_argument("--approvals", type=Path, help="Explicit hash-bound APPROVED_BY_USER records")
    parser.add_argument("--source-root", type=Path, default=ROOT / "output")
    parser.add_argument("--output-root", type=Path, default=ROOT / "ready_to_post")
    args = parser.parse_args()

    result = CampaignFinalizer(
        ROOT,
        source_root=args.source_root,
        output_root=args.output_root,
    ).finalize(args.campaign_id, approvals_path=args.approvals)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return {"READY_TO_POST": 0, "REVIEW_REQUIRED": 2, "BLOCKED": 3}[result.state]


if __name__ == "__main__":
    raise SystemExit(main())
