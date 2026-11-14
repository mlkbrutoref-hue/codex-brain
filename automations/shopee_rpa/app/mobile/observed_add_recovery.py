"""Reconcile a confirmed native Add postcondition without repeating the action."""
import hashlib,json,time
from dataclasses import asdict
from pathlib import Path
from app.mobile.shopee_video import Screen,product_sheet_matches
from app.mobile.preparation_diagnostic import PreparationReadUI
from app.operational.config import FeatureMode
from app.operational.deadlines import OperationalStop

def reconcile_observed_add(runtime,ui,worker,request_path,review_path,evidence_path,*,resolved_failures=()):
    if runtime.config.mode != FeatureMode.ASSISTED_MODE or not isinstance(ui,PreparationReadUI):
        raise OperationalStop('ASSISTED_READ_ONLY_RECOVERY_REQUIRED')
    job=runtime.ledger.identity(runtime.candidate)
    resolved={}
    for path in resolved_failures:
        data=Path(path).read_bytes(); prior=json.loads(data)
        if prior.get('job_id')!=job or prior.get('ledger_state')!='FAILED' or prior.get('breaker')!='CLOSED':
            raise OperationalStop('PRIOR_FAILURE_RESOLUTION_INVALID')
        if prior.get('blocker') not in ('MEDIASTORE_GRID_ORDER_NOT_CORROBORATED','AMBIGUOUS_PRODUCT_CARD_REVIEW'):
            raise OperationalStop('UNRELATED_BREAKER_INCIDENT')
        resolved[prior['blocker']]=dict(path=str(path),sha256=hashlib.sha256(data).hexdigest())
    request=json.loads(Path(request_path).read_text(encoding='utf-8'))
    raw=Path(review_path).read_bytes(); proof=json.loads(raw)
    if (request['job_id']!=job or proof.get('status')!='APPROVED_UI_ONLY'
        or proof.get('candidate_fingerprint')!=runtime.candidate.fingerprint()
        or proof.get('product')!=asdict(runtime.candidate.product)
        or not proof.get('reviewer') or not 0<=time.time()-proof.get('reviewed_at',0)<=runtime.config.approval_ttl
        or any(proof.get(k)!=request.get(k) for k in ('card','screen_sha256','button_node_sha256','screenshot_sha256','screenshot_reference','official_source_url'))
        or hashlib.sha256(Path(proof['screenshot_reference']).read_bytes()).hexdigest()!=proof['screenshot_sha256']):
        raise OperationalStop('ADD_RECOVERY_CARD_PROOF_INVALID')
    log_path=runtime.root/'logs/operational'/f'{runtime.input["job_id"]}.jsonl'
    logs=[json.loads(line) for line in log_path.read_text(encoding='utf-8').splitlines()]
    mutations=[r for r in logs if r.get('event')=='action' and r.get('action_type')!='READ_STATE']
    if (not mutations or mutations[-1].get('element')!='product_card' or mutations[-1].get('status')!='SUCCESS'
        or mutations[-1].get('action_type')!='CLICK' or worker.session.get('publish_attempted')
        or worker.session.get('central_job_id')!=job
        or any(r.get('action_type') in ('PUBLISH_ATTEMPT','UPLOAD') for r in logs)):
        raise OperationalStop('ADD_RECOVERY_ACTION_TRACE_INVALID')
    def assess(db):
        row=runtime.ledger.get(job,db)
        if (row['state']!='UNKNOWN' or row['attempted'] or row['fingerprint']!=runtime.candidate.fingerprint()
            or json.loads(row['evidence'] or '{}').get('reason')!='EXPECTED_STATE_TIMEOUT'
            or db.execute('SELECT 1 FROM authorizations WHERE job=?',(job,)).fetchone()
            or db.execute("SELECT 1 FROM jobs WHERE account=? AND id<>? AND state IN ('UNKNOWN','PREPARING','PUBLISHING','UPLOADING','READY','RESERVED')",(row['account'],job)).fetchone()):
            raise OperationalStop('ADD_RECOVERY_SCOPE_INVALID')
        last_closed=db.execute("SELECT COALESCE(MAX(id),0) FROM breaker_events WHERE account=? AND kind='RELEASE' AND reason='CLOSED'",(row['account'],)).fetchone()[0]
        events=[dict(r) for r in db.execute("SELECT * FROM breaker_events WHERE account=? AND id>? AND kind='FAILURE'",(row['account'],last_closed))]
        if not events or any(r['reason'] not in ('PUBLICATION_UNKNOWN','EXPECTED_STATE_TIMEOUT',*resolved) or r['job'] not in (None,job) for r in events):
            raise OperationalStop('UNRELATED_BREAKER_INCIDENT')
        incident=db.execute('SELECT MAX(id) FROM ledger_events WHERE job=?',(job,)).fetchone()[0]
        return row,incident,events
    def observe():
        ui.breaker.check(read_only=True)
        if ui.app_current().get('package')!='com.shopee.br' or str(ui.app_info('com.shopee.br').get('versionName')) not in runtime.config.allowed_app_versions:
            raise OperationalStop('ADD_RECOVERY_APP_CHANGED')
        s=Screen(ui.dump_hierarchy());s.guard()
        if not product_sheet_matches(s,runtime.candidate.product_title):raise OperationalStop('ADD_POSTCONDITION_NOT_CONFIRMED')
        remote=ui.shell(['sha256sum',runtime.input['video_path']])
        expected=runtime.candidate.media.prepared_asset_hash
        if remote.exit_code or remote.output.split()[0]!=expected or hashlib.sha256(Path(runtime.input['local_media_path']).read_bytes()).hexdigest()!=expected:
            raise OperationalStop('MEDIA_HASH_MISMATCH')
        return s
    with runtime.store.transaction() as db: original=assess(db);before=runtime.breaker.snapshot(db)
    if before['state']!='OPEN':raise OperationalStop('ADD_RECOVERY_REQUIRES_OPEN')
    observe()
    with runtime.store.transaction() as db:
        if assess(db)!=original:raise OperationalStop('INCIDENT_CHANGED')
        runtime.breaker.release(reviewer=proof['reviewer'],reason='CONFIRMED_ADD_PREFLIGHT',evidence=str(evidence_path),db=db)
    try:
        screen=observe()
        record=dict(original_snapshot=original[0],incident_event=original[1],last_action=mutations[-1],resolved_prior_failures=resolved,
            product_add_effect='CONFIRMED_PRODUCT_INFO_SHEET',native_upload_status='UNKNOWN',
            reviewer=proof['reviewer'],reviewed_at=time.time(),screen_sha256=runtime._evidence_digest(screen.nodes),
            card_review_sha256=hashlib.sha256(raw).hexdigest(),card_review_reference=str(review_path),
            authorization='Operator explicitly requested Feito; assisted continuation only; no Postar',
            candidate_fingerprint=runtime.candidate.fingerprint())
        target=Path(evidence_path)
        if target.exists():raise OperationalStop('RECOVERY_EVIDENCE_ALREADY_EXISTS')
        target.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        with runtime.store.transaction() as db:
            if assess(db)!=original or runtime.breaker.snapshot(db)['state']!='HALF_OPEN':raise OperationalStop('INCIDENT_CHANGED')
            key=f'confirmed_add_recovery:{job}:{original[1]}'
            if runtime.store.get(db,key) is not None:raise OperationalStop('RECOVERY_ALREADY_RECORDED')
            runtime.store.put(db,key,record)
            db.execute("UPDATE jobs SET state='PREPARING',evidence=? WHERE id=?",(json.dumps(record),job))
            runtime.ledger.record(db,job,'PREPARING',original[0]['owner'])
            runtime.breaker.release(reviewer=proof['reviewer'],reason='ADD_EFFECT_CONFIRMED_ASSISTED_CONTINUATION',evidence=str(target),close=True,db=db)
        return record,proof
    except Exception:
        runtime.breaker.failure('ADD_RECOVERY_PREFLIGHT_FAILED',critical=True,job_id=job);raise
