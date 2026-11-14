"""Verify research artifacts and fingerprint inspected sources; no device/DB access."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
RESEARCH = Path(__file__).resolve().parents[1]
SOURCE_PATHS = [
    'app/mobile/ui.py', 'app/mobile/shopee_video.py',
    'app/mobile/safety_runtime.py', 'app/publishing/ledger.py',
    'app/publishing/reconciliation.py', 'app/operational/action_budget.py',
    'app/operational/circuit_breaker.py', 'app/operational/store.py',
    'app/observability/operation_logger.py', 'requirements-android.txt',
    'output/preparation_abandonment_20261008/latency-analysis.json',
    'output/preparation_abandonment_20261008/manual-publication-report.json',
    'output/preparation_abandonment_20261008/manual-publication-audit.json',
]

def main():
    failures = []
    docs = sorted(RESEARCH.glob('*.md'))
    for doc in docs:
        content = doc.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if target.startswith(('https://', 'http://', '#')):
                continue
            if not (doc.parent / target.split('#')[0]).resolve().exists():
                failures.append(f'{doc.name}: {target}')
    results = json.loads((RESEARCH / 'experiments/offline-replay-results.json').read_text(encoding='utf-8'))
    assert len(results['experiments']) == 3
    assert all(e['status'] == 'PASS_REPRODUCED' for e in results['experiments'])
    manifest = {}
    for relative in SOURCE_PATHS:
        source = ROOT / relative
        if not source.exists():
            failures.append(f'Missing source: {relative}')
        else:
            manifest[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    report = dict(research_date='2026-10-08', document_count=len(docs),
                  local_link_errors=failures, existing_experiment_results='3 PASS_REPRODUCED',
                  source_sha256=manifest,
                  limitation='Snapshot at research completion; not a before/after integrity audit or live-device test')
    (RESEARCH / 'experiments/research-verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(documents=len(docs), errors=failures, source_count=len(manifest))))
    assert not failures

if __name__ == '__main__':
    main()
