"""Recover only incidents proven to belong to an archived manual publication."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.operational.deadlines import OperationalStop


def recover_archived_publication(ledger, job, *, session_path, log_path, reviewer,
                                 evidence_reference, read_only_preflight):
    session_path, log_path=Path(session_path),Path(log_path)
    session=json.loads(session_path.read_text(encoding='utf-8-sig'))
    logs=[json.loads(line) for line in log_path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    with ledger.store.transaction() as db:
        row=ledger.get(job,db)
        if not row or row['state']!='ARCHIVED_MANUAL_PUBLICATION_REPORTED' or not reviewer or not Path(evidence_reference).is_file():
            raise OperationalStop('ARCHIVED_PUBLICATION_REVIEW_REQUIRED')
        selection=session.get('selection_evidence',{})
        if (session.get('central_job_id')!=job or selection.get('expected_account')!=row['account'] or
                selection.get('video_sha256') not in (row['source_hash'],row['prepared_hash'])):
            raise OperationalStop('HISTORICAL_ARCHIVE_SESSION_MISMATCH')
        breaker=OperationCircuitBreaker(ledger.store,row['account'],ledger.config)
        before=breaker.snapshot(db)
        if before['state']!='OPEN' or before.get('reason')!='MANUAL_PUBLICATION_REPORTED_PENDING_RECONCILIATION':
            raise OperationalStop('BREAKER_SCOPE_CHANGED')
        boundary=db.execute("SELECT COALESCE(MAX(id),0) FROM breaker_events WHERE account=? AND kind='RELEASE' AND reason='CLOSED'",(row['account'],)).fetchone()[0]
        events=db.execute("SELECT * FROM breaker_events WHERE account=? AND id>? AND kind='FAILURE'",(row['account'],boundary)).fetchall()
        for event in events:
            if event['job']==job and event['reason']=='MANUAL_PUBLICATION_REPORTED_PENDING_RECONCILIATION':
                continue
            matching=[entry for entry in logs if entry.get('account_id')==row['account'] and
                entry.get('session_id')==session_path.parent.name and entry.get('event')=='error' and
                entry.get('error_code')==event['reason'] and
                abs(datetime.fromisoformat(entry['timestamp']).timestamp()-event['timestamp'])<1]
            if event['job'] not in (None,job) or event['reason']!='PRODUCT_BINDING_REVIEW_INVALID' or len(matching)!=1:
                raise OperationalStop('OTHER_OR_UNSCOPED_BREAKER_INCIDENT')
        if not events:
            raise OperationalStop('INCIDENT_EVIDENCE_REQUIRED')
        _local_preflight(ledger,db,row['account'])
        breaker.release(reviewer=reviewer,reason='ARCHIVED_MANUAL_PUBLICATION_SCOPE_REVIEWED',evidence=evidence_reference,db=db)
        half=breaker.snapshot(db)
        event_ids=[e['id'] for e in events]
    observed=read_only_preflight(row['account'])
    if not isinstance(observed,dict) or any(observed.get(key) is not True for key in ('account_confirmed','app_expected','no_editor','device_connected','no_security_challenge')):
        raise OperationalStop('ARCHIVE_READ_ONLY_PREFLIGHT_FAILED')
    with ledger.store.transaction() as db:
        _local_preflight(ledger,db,row['account'])
        current=breaker.snapshot(db)
        latest=db.execute("SELECT COALESCE(MAX(id),0) FROM breaker_events WHERE account=? AND kind='FAILURE'",(row['account'],)).fetchone()[0]
        if current!=half or latest!=max(event_ids):
            raise OperationalStop('NEW_INCIDENT_DURING_ARCHIVE_PREFLIGHT')
        current.update(recovery_job=job,recovery_token='archive:'+job,
            recovery_type='ADMINISTRATIVE_MANUAL_ARCHIVE',not_before=0,
            scope_assessment_sha256=hashlib.sha256(Path(evidence_reference).read_bytes()).hexdigest(),
            preflight_reference=observed.get('xml_reference',evidence_reference),
            preflight_at=ledger.clock(),preflight_checks=observed,resolved_incident_ids=event_ids)
        ledger.store.put(db,breaker.key,current)
        breaker.release(reviewer=reviewer,reason='ARCHIVED_MANUAL_PUBLICATION_READ_PREFLIGHT_PASSED',evidence=evidence_reference,close=True,db=db)
        after=breaker.snapshot(db)
    return dict(before=before,after=after,incident_ids=event_ids,read_only_preflight=observed,
                session_sha256=hashlib.sha256(session_path.read_bytes()).hexdigest(),
                log_sha256=hashlib.sha256(log_path.read_bytes()).hexdigest(),publish_attempt_created=False)


def _local_preflight(ledger,db,account):
    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchone():
        raise OperationalStop('LEDGER_INTEGRITY_FAILED')
    if ledger.store.killed(db):
        raise OperationalStop('KILL_SWITCH')
    if db.execute("SELECT 1 FROM jobs WHERE account=? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING','RESERVED','PREPARING','READY')",(account,)).fetchone():
        raise OperationalStop('OTHER_ACCOUNT_JOB_REQUIRES_REVIEW')
    if db.execute('SELECT 1 FROM leases WHERE key=?',('account:'+account,)).fetchone():
        raise OperationalStop('ACCOUNT_ALREADY_IN_USE')
    if db.execute('SELECT 1 FROM authorizations a JOIN jobs j ON j.id=a.job WHERE j.account=? AND a.used=0 AND a.expires>?',(account,ledger.clock())).fetchone():
        raise OperationalStop('OTHER_PUBLISH_AUTHORIZATION')
