"""Explicit abandonment of an assisted preparation, never publication reconciliation."""
import hashlib
import json
from pathlib import Path
import time
from datetime import datetime

from app.mobile.preparation_diagnostic import PreparationReadUI, observe_preparation
from app.mobile.shopee_video import Screen
from app.operational.config import FeatureMode
from app.operational.deadlines import OperationalStop
from app.validation.product_media_truth import PostCandidate
from app.media.identity import file_sha256


def read_evidence(path, runtime, job):
    raw=Path(path).read_bytes()
    proof=json.loads(raw)
    stamp=proof.get('reviewed_at',0)
    if (proof.get('decision')!='ABANDON_ASSISTED_PREPARATION' or not proof.get('reviewer')
            or not proof.get('authorization_reference') or proof.get('job_id')!=job
            or proof.get('candidate_fingerprint')!=runtime.candidate.fingerprint()
            or proof.get('operator_confirms_no_final_publish') is not True
            or proof.get('old_editor_discarded') is not True
            or proof.get('historical_add_effect')!='UNKNOWN' or proof.get('native_upload_status')!='UNKNOWN'
            or not isinstance(stamp,(int,float)) or not 0<=time.time()-stamp<=runtime.config.approval_ttl):
        raise OperationalStop('EXPLICIT_ABANDONMENT_REVIEW_REQUIRED')
    sources={}
    for name in ('config','session','log'):
        ref=proof['historical_sources'][name]
        content=Path(ref['path']).read_bytes()
        if hashlib.sha256(content).hexdigest()!=ref['sha256']:
            raise OperationalStop('HISTORICAL_SOURCE_CHANGED')
        sources[name]=content.decode('utf-8-sig')
    config=json.loads(sources['config']); session=json.loads(sources['session'])
    if (PostCandidate.from_dict(config['candidate']).fingerprint()!=runtime.candidate.fingerprint()
            or config.get('serial')!=runtime.input['serial']
            or config.get('operational',{}).get('mode')!='ASSISTED_MODE'
            or config.get('publish_authorized') or session.get('publish_attempted') is not False
            or session.get('job_id')!=config['job_id']
            or session.get('central_job_id',job)!=job
            or session.get('config_sha256')!=hashlib.sha256(json.dumps(config,sort_keys=True,ensure_ascii=False).encode()).hexdigest()):
        raise OperationalStop('HISTORICAL_ASSISTED_SCOPE_NOT_PROVEN')
    events=[json.loads(line) for line in sources['log'].splitlines() if line.strip()]
    if not events or any(e.get('account_id')!=runtime.candidate.account_id or e.get('job_id')!=config['job_id'] for e in events):
        raise OperationalStop('HISTORICAL_LOG_SCOPE_MISMATCH')
    actions=[e for e in events if e.get('event')=='action' and e.get('action_type')!='READ_STATE']
    if (not actions or any(e.get('event')=='publish_attempt' or e.get('action_type') in ('PUBLISH_ATTEMPT','UPLOAD_START') for e in events)
            or any(actions[-1].get(key)!=value for key,value in dict(action_type='CLICK',element='product_card',status='UNKNOWN').items())):
        raise OperationalStop('INCIDENT_IS_NOT_ASSISTED_ADD')
    try:
        logged_at=datetime.fromisoformat(actions[-1]['timestamp']).timestamp()
        with runtime.store.transaction() as db:
            event=db.execute("SELECT timestamp FROM ledger_events WHERE job=? AND state='UNKNOWN' ORDER BY id DESC LIMIT 1",(job,)).fetchone()
        if not event or abs(logged_at-event['timestamp'])>30:
            raise ValueError('different incident')
    except (KeyError,ValueError,TypeError):
        raise OperationalStop('HISTORICAL_LOG_DOES_NOT_MATCH_INCIDENT') from None
    return proof,raw,sources


def assess(runtime,job,db):
    row=runtime.ledger.get(job,db)
    if (not row or row['state']!='UNKNOWN' or row['attempted']
            or row['fingerprint']!=runtime.candidate.fingerprint() or row['account']!=runtime.candidate.account_id
            or json.loads(row['evidence'] or '{}').get('reason')!='RPC_EFFECT_UNKNOWN'):
        raise OperationalStop('ABANDONMENT_SCOPE_INVALID')
    if runtime.store.killed(db): raise OperationalStop('KILL_SWITCH')
    if db.execute('SELECT 1 FROM authorizations WHERE job=?',(job,)).fetchone():
        raise OperationalStop('PUBLISH_AUTHORIZATION_REQUIRES_RECONCILIATION')
    if db.execute("SELECT 1 FROM ledger_events WHERE job=? AND state IN ('PUBLISHING','UPLOADING','PUBLISHED','PUBLISHED_LEGACY')",(job,)).fetchone():
        raise OperationalStop('PUBLISH_OR_UPLOAD_ATTEMPT_REQUIRES_RECONCILIATION')
    if db.execute("SELECT 1 FROM jobs WHERE account=? AND id<>? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING','RESERVED','PREPARING','READY')",(row['account'],job)).fetchone():
        raise OperationalStop('OTHER_ACTIVE_ACCOUNT_JOB')
    for key in ('account:'+row['account'],'device:'+runtime.input['serial']):
        lease=db.execute('SELECT owner FROM leases WHERE key=?',(key,)).fetchone()
        if not lease or lease['owner']!=row['owner']: raise OperationalStop('INCIDENT_LEASE_MISMATCH')
    events=db.execute('SELECT * FROM breaker_events WHERE account=? ORDER BY id',(row['account'],)).fetchall()
    closed=max((e['id'] for e in events if json.loads(e['snapshot'])['state']=='CLOSED'),default=0)
    failures=[e for e in events if e['id']>closed and e['kind']=='FAILURE']
    if not failures or any(e['job']!=job or e['reason']!='RPC_EFFECT_UNKNOWN' for e in failures):
        raise OperationalStop('BREAKER_HAS_OTHER_INCIDENTS')
    incident=db.execute("SELECT id FROM ledger_events WHERE job=? AND state='UNKNOWN' ORDER BY id DESC LIMIT 1",(job,)).fetchone()
    if not incident: raise OperationalStop('INCIDENT_EVENT_MISSING')
    return row,incident['id'],[e['id'] for e in failures]


def read_preflight(runtime,ui):
    report=observe_preparation(ui,runtime)
    if report['account_match']!='PASS': raise OperationalStop('RECOVERY_PROFILE_ACCOUNT_REQUIRED')
    screen=Screen(ui.dump_hierarchy()); screen.guard()
    if (runtime._evidence_digest(screen.nodes)!=report['screen_sha256']
            or not any(n.get('content-desc')=='click to post video' for n in screen.nodes)
            or any(screen.has(s) for s in ('btn_post','rv_gallery','et_caption','tv_compress'))):
        raise OperationalStop('CLEAN_VIDEO_PROFILE_REQUIRED')
    local=Path(runtime.input['local_media_path'])
    if file_sha256(local)!=runtime.candidate.media.prepared_asset_hash:
        raise OperationalStop('LOCAL_MEDIA_HASH_MISMATCH')
    remote=ui.shell(['sha256sum',runtime.input['video_path']])
    if remote.exit_code or not remote.output.split() or remote.output.split()[0]!=runtime.candidate.media.prepared_asset_hash:
        raise OperationalStop('ANDROID_MEDIA_HASH_MISMATCH')
    if runtime.validator.validate_assisted(runtime.candidate).status!='PASS':
        raise OperationalStop('ASSISTED_CONTENT_GATE_FAILED')
    return dict(report,media_hash_match=True,old_editor_present=False,validation_scope='ASSISTED_PREPARATION_RESTART_ONLY')


def abandon_preparation(runtime,ui,evidence_path):
    if runtime.config.mode!=FeatureMode.ASSISTED_MODE or not isinstance(ui,PreparationReadUI):
        raise OperationalStop('ASSISTED_READ_ONLY_RECOVERY_REQUIRED')
    job=ui.breaker.job
    if runtime.ledger.identity(runtime.candidate)!=job: raise OperationalStop('RECOVERY_JOB_MISMATCH')
    proof,raw,sources=read_evidence(evidence_path,runtime,job)
    with runtime.store.transaction() as db:
        original,incident,failures=assess(runtime,job,db)
        before=runtime.breaker.snapshot(db)
    if before['state']!='OPEN': raise OperationalStop('RECOVERY_REQUIRES_OPEN')
    read_preflight(runtime,ui)
    with runtime.store.transaction() as db:
        if assess(runtime,job,db)!=(original,incident,failures) or runtime.breaker.snapshot(db)!=before:
            raise OperationalStop('INCIDENT_CHANGED_DURING_PREFLIGHT')
        runtime.breaker.release(reviewer=proof['reviewer'],reason='PREPARATION_ABANDONMENT_PREFLIGHT',evidence=str(evidence_path),db=db)
        half=runtime.breaker.snapshot(db)
    try:
        fresh=read_preflight(runtime,ui)
        # Re-read every original reference before the administrative commit.
        if read_evidence(evidence_path,runtime,job)!=(proof,raw,sources):
            raise OperationalStop('RECOVERY_EVIDENCE_CHANGED')
        with runtime.store.transaction() as db:
            if assess(runtime,job,db)!=(original,incident,failures) or runtime.breaker.snapshot(db)!=half:
                raise OperationalStop('INCIDENT_CHANGED_DURING_PREFLIGHT')
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchone():
                raise OperationalStop('LEDGER_INTEGRITY_FAILED')
            record=dict(proof,preflight=fresh,historical_sources_content=sources,
                resolution='PREPARATION_ABANDONED',publication_status='NOT_AUTHORIZED',ready_for_publish=False,
                evidence_reference=str(Path(evidence_path).resolve()),evidence_sha256=hashlib.sha256(raw).hexdigest())
            db.execute('INSERT INTO preparation_abandonments(job,incident_event,fingerprint,original_snapshot,evidence,timestamp) VALUES (?,?,?,?,?,?)',
                (job,incident,original['fingerprint'],json.dumps(original),json.dumps(record),time.time()))
            # Original evidence stays in the job as well as the immutable incident snapshot.
            db.execute("UPDATE jobs SET state='PREPARATION_ABANDONED' WHERE id=?",(job,))
            runtime.ledger.record(db,job,'PREPARATION_ABANDONED',proof['reviewer'])
            db.execute('DELETE FROM leases WHERE owner=? AND key IN (?,?)',
                (original['owner'],'account:'+runtime.candidate.account_id,'device:'+runtime.input['serial']))
            runtime.breaker.release(reviewer=proof['reviewer'],reason='PREPARATION_ABANDONED_ASSISTED_ONLY',
                evidence=str(evidence_path),close=True,db=db)
        return dict(job_id=job,state='PREPARATION_ABANDONED',breaker='CLOSED',historical_add_effect='UNKNOWN',native_upload_status='UNKNOWN',ready_for_publish=False)
    except Exception:
        runtime.breaker.failure('ABANDONMENT_PREFLIGHT_FAILED',critical=True,job_id=job)
        raise
