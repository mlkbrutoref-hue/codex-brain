"""CLI for local preparation and explicitly observed assisted steps."""
import argparse
import json
from .assisted import AssistedSession, prepare_session, read_json
from app.mobile.discovery import discover_phone_link


def main():
    parser = argparse.ArgumentParser(description="ASSISTED_MODE: never publishes")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--manifest", required=True)
    prepare.add_argument("--brief", required=True, help="JSON: platform/account/content_type/category/caption/cta/disclosure/scheduled_at/asset_ids")
    prepare.add_argument("--out", required=True)
    discover = commands.add_parser("discover")
    discover.add_argument("--out")
    for name in ("inspect", "advance", "review"):
        command = commands.add_parser(name)
        command.add_argument("--session", required=True)
        if name != "inspect":
            command.add_argument("--evidence", required=True, help="JSON file with observed evidence or nine QA checks")
    args = parser.parse_args()
    if args.command == "discover":
        data = discover_phone_link()
        if args.out:
            from pathlib import Path
            destination = Path(args.out)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif args.command == "prepare":
        session = prepare_session(args.manifest, **read_json(args.brief))
        session.save(args.out)
        data = session.data
    else:
        session = AssistedSession.load(args.session)
        if args.command == "advance":
            session.advance(**read_json(args.evidence))
            session.save(args.session)
        elif args.command == "review":
            session.review(read_json(args.evidence))
            session.save(args.session)
        data = session.data
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
