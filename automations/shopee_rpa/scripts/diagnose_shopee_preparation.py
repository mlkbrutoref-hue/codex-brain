"""Explicit read-only diagnostic of one UNKNOWN Add; no recovery or click flags."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.mobile.safety_runtime import AndroidSafetyRuntime
from app.mobile.preparation_diagnostic import preparation_diagnostic, observe_preparation
from app.mobile.shopee_video import Screen
from app.operational.deadlines import OperationalStop


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--job',required=True)
    parser.add_argument('--authorization-reference',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    out=Path(args.output).resolve()
    if out.exists(): raise OperationalStop('DIAGNOSTIC_OUTPUT_ALREADY_EXISTS')
    out.mkdir(parents=True)
    runtime=AndroidSafetyRuntime(json.loads(Path(args.config).read_text(encoding='utf-8-sig')),ROOT)
    result=dict(job_id=args.job,authorization_reference=args.authorization_reference,
        publish_button_clicked=False,publish_performed=False)
    try:
        with preparation_diagnostic(runtime,args.job,authorization_reference=args.authorization_reference) as ui:
            result.update(observe_preparation(ui,runtime))
            if result['app'].get('package')=='com.shopee.br' and result.get('screen_sha256'):
                if ui.app_current().get('package')!='com.shopee.br':
                    raise OperationalStop('DIAGNOSTIC_FOREGROUND_CHANGED')
                screen=Screen(ui.dump_hierarchy()); screen.guard()
                digest=hashlib.sha256(json.dumps(screen.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                if digest!=result['screen_sha256']:
                    raise OperationalStop('DIAGNOSTIC_SCREEN_CHANGED')
                image=ui.screenshot()
                after=Screen(ui.dump_hierarchy()); after.guard()
                if (ui.app_current().get('package')!='com.shopee.br'
                        or hashlib.sha256(json.dumps(after.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest()!=digest):
                    raise OperationalStop('DIAGNOSTIC_CAPTURE_CHANGED')
                image.save(out/'current-screen.png')
                result['screenshot_reference']=str(out/'current-screen.png')
                result['screenshot_sha256']=hashlib.sha256((out/'current-screen.png').read_bytes()).hexdigest()
                result['capture_screen_sha256']=digest
    except Exception as exc:
        result['blocker']=str(exc) if isinstance(exc,OperationalStop) else type(exc).__name__
    result['breaker_after']=runtime.breaker.snapshot()['state']
    result['job_state_after']=runtime.ledger.get(args.job)['state']
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return 0 if result.get('read_only') else 1


if __name__=='__main__': sys.exit(main())
