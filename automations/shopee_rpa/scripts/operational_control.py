"""Ledger/breaker control. Legacy recovery uses a read-only public GET; never publishes."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.operational.store import OperationalStore
from app.operational.config import OperationalConfig
from app.operational.deadlines import OperationalStop
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.publishing.ledger import JobLedger
from app.publishing.reconciliation import PublicationReconciler,PublicationEvidence
from app.validation.product_media_truth import PostCandidate
from app.publishing.legacy_reconciliation import (LegacyPublicationReconciler, LegacyPublicationEvidence,
    LegacyBreakerRecovery, LegacyBreakerAssessment)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('status')
    fingerprint=commands.add_parser('fingerprint'); fingerprint.add_argument('--config',required=True)
    kill=commands.add_parser('kill'); kill.add_argument('--enabled',choices=('true','false'),required=True)
    release=commands.add_parser('release-breaker'); release.add_argument('--account',required=True); release.add_argument('--close',action='store_true')
    cancel=commands.add_parser('cancel-preparation'); cancel.add_argument('--job',required=True)
    recover=commands.add_parser('resolve-preparation-unknown');recover.add_argument('--job',required=True)
    recover.add_argument('--verified-no-publish',action='store_true');recover.add_argument('--verified-no-upload',action='store_true')
    reconcile=commands.add_parser('reconcile'); reconcile.add_argument('--job',required=True); reconcile.add_argument('--evidence',required=True)
    legacy=commands.add_parser('reconcile-legacy'); legacy.add_argument('--job',required=True); legacy.add_argument('--evidence',required=True)
    preflight=commands.add_parser('preflight-legacy-breaker'); preflight.add_argument('--job',required=True)
    preflight.add_argument('--evidence',required=True); preflight.add_argument('--output',required=True)
    abandon=commands.add_parser('abandon-preparation')
    for field in ('config','job','evidence','output'):
        abandon.add_argument('--'+field,required=True)
    for command in (kill,release,cancel,recover):
        command.add_argument('--reviewer',required=True); command.add_argument('--reason',required=True)
    for command in (release,cancel,recover):command.add_argument('--evidence',required=True)
    args=parser.parse_args()
    if args.command=='abandon-preparation':
        from app.mobile.safety_runtime import AndroidSafetyRuntime
        from app.mobile.preparation_diagnostic import preparation_diagnostic
        from app.publishing.preparation_abandonment import abandon_preparation
        target=Path(args.output)
        if target.exists(): raise OperationalStop('RECOVERY_OUTPUT_ALREADY_EXISTS')
        runtime=AndroidSafetyRuntime(json.loads(Path(args.config).read_text(encoding='utf-8-sig')),Path(__file__).resolve().parents[1])
        with preparation_diagnostic(runtime,args.job,authorization_reference=args.evidence) as ui:
            result=abandon_preparation(runtime,ui,args.evidence)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False));return 0
    if args.command=='fingerprint':
        data=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
        print(PostCandidate.from_dict(data['candidate']).fingerprint());return
    store=OperationalStore();config=OperationalConfig();ledger=JobLedger(store,config)
    if args.command=='status':
        with store.transaction() as db:
            result=dict(database=str(store.path),kill_switch=store.killed(db),
                jobs=[dict(row) for row in db.execute('SELECT id,account,logical,source_hash,prepared_hash,fingerprint,state,attempted,created FROM jobs')],
                details=[{'job':row['job'],'fingerprint':row['fingerprint'],'summary':json.loads(row['summary'])} for row in db.execute('SELECT * FROM job_details')],
                legacy_publications=[{'job':row['job'],'metadata':json.loads(row['metadata'])} for row in db.execute('SELECT * FROM legacy_publications')],
                preparation_abandonments=[{'job':row['job'],'incident_event':row['incident_event'],
                    'evidence':{key:value for key,value in json.loads(row['evidence']).items() if key!='historical_sources_content'}}
                    for row in db.execute('SELECT * FROM preparation_abandonments ORDER BY id')],
                counters=[dict(row) for row in db.execute('SELECT * FROM counters')],
                controls=[{'key':row['key'],'value':json.loads(row['value'])} for row in db.execute("SELECT * FROM kv WHERE key LIKE 'breaker:%' OR key LIKE 'tokens:%'")])
    elif args.command=='kill':
        store.set_kill_switch(args.enabled=='true',reviewer=args.reviewer,reason=args.reason);result=dict(kill_switch=store.killed())
    elif args.command=='release-breaker':
        breaker=OperationCircuitBreaker(store,args.account,config)
        breaker.release(reviewer=args.reviewer,reason=args.reason,evidence=args.evidence,close=args.close);result=breaker.snapshot()
    elif args.command=='cancel-preparation':
        ledger.release_preparation(args.job,reviewer=args.reviewer,reason=args.reason,evidence=args.evidence);result=ledger.get(args.job)
    elif args.command=='resolve-preparation-unknown':
        ledger.resolve_preparation_unknown(args.job,reviewer=args.reviewer,reason=args.reason,evidence=args.evidence,
            verified_no_publish=args.verified_no_publish,verified_no_upload=args.verified_no_upload);result=ledger.get(args.job)
    elif args.command=='reconcile':
        evidence=PublicationEvidence(**json.loads(Path(args.evidence).read_text(encoding='utf-8-sig')))
        result=dict(state=PublicationReconciler(ledger).reconcile(args.job,evidence))
    elif args.command=='reconcile-legacy':
        evidence=LegacyPublicationEvidence(**json.loads(Path(args.evidence).read_text(encoding='utf-8-sig')))
        result=dict(state=LegacyPublicationReconciler(ledger).reconcile(args.job,evidence),job=ledger.get(args.job))
    else:
        assessment=LegacyBreakerAssessment(**json.loads(Path(args.evidence).read_text(encoding='utf-8-sig')))
        result=LegacyBreakerRecovery(ledger).recover(args.job,assessment,args.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if isinstance(result,dict) and result.get('result')=='FAIL' else 0


if __name__=='__main__':
    try:
        sys.exit(main())
    except OperationalStop as exc:
        print(json.dumps(dict(state='STOP',reason=str(exc)),ensure_ascii=False))
        sys.exit(1)
