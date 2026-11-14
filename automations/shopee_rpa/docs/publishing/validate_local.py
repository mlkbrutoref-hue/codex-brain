"""Run from repository root: python docs/publishing/validate_local.py.

Local test only. Never opens apps, transfers media, or publishes.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.publishing.assisted import AssistedSession, prepare_session, read_json

output = ROOT / "output/mobile_publisher"
output.mkdir(parents=True, exist_ok=True)
manifest = ROOT / "output/e2e_full_content_factory_20260928_0955/manifests/product_stories_manifest.json"
brief = read_json(ROOT / "docs/publishing/example_brief.json")
session = prepare_session(manifest, **brief)
session.advance("TIME_RECOMMENDATION", evidence="No analytics delivery. Time remains unknown. Phone connection postponed by user.")
session.save(output / "session.json")
reopened = AssistedSession.load(output / "session.json")
assert reopened.data == session.data
blocked = {}
try:
    prepare_session(manifest, **dict(brief, asset_ids=["product_story_01"]))
except ValueError as exc:
    blocked["review_content"] = str(exc)
try:
    session.advance("OPEN_PHONE_LINK", evidence="No connected device observed")
except ValueError as exc:
    blocked["phone_unverified"] = str(exc)
assert set(blocked) == {"review_content", "phone_unverified"}
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests/publishing"))
with (output / "tests.txt").open("w", encoding="utf-8") as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
report = dict(status="PASS" if result.wasSuccessful() else "FAIL", tests_run=result.testsRun,
              failures=len(result.failures), errors=len(result.errors), state=session.data["state"],
              local_real_asset="product_story_02", fingerprint=session.data["fingerprint"],
              blocked_as_expected=blocked, published=False, transferred=False,
              phone_test="POSTPONED_BY_USER_UNTIL_TOMORROW", analytics="NOT_INTEGRATED",
              visual_inspection="Existing PNG inspected by Codex: readable text, product visible, Nina absent; app preview NOT_TESTED")
(output / "local_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
