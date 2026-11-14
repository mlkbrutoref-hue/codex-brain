from enum import Enum
import hashlib
import json
import time
import uuid
from app.operational.deadlines import OperationalStop
from app.operational.config import FeatureMode


class JobState(str, Enum):
    CREATED = 'CREATED'
    PREPARING = 'PREPARING'
    READY = 'READY'
    ASSISTED_VALIDATED = 'ASSISTED_VALIDATED'
    RESERVED = 'RESERVED'
    UPLOADING = 'UPLOADING'
    PUBLISHING = 'PUBLISHING'
    PUBLISHED = 'PUBLISHED'
    PUBLISHED_LEGACY = 'PUBLISHED_LEGACY'
    ARCHIVED_MANUAL_PUBLICATION_REPORTED = 'ARCHIVED_MANUAL_PUBLICATION_REPORTED'
    UNKNOWN = 'UNKNOWN'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    PREPARATION_ABANDONED = 'PREPARATION_ABANDONED'


class JobLedger:
    def __init__(self, store, config, clock=time.time):
        self.store, self.config, self.clock = store, config, clock

    @staticmethod
    def identity(candidate):
        c = candidate
        value = ['shopee_video', c.account_id, c.media.logical_asset_id, c.product.shop_id,
                 c.product.item_id, c.product.variant_id]
        return hashlib.sha256(json.dumps(value).encode()).hexdigest()

    def record(self,db,job,state,owner):
        cursor=db.execute('INSERT INTO ledger_events(job,state,owner,timestamp) VALUES (?,?,?,?)',
                         (job,state,owner,self.clock()))
        row=db.execute('SELECT fingerprint FROM jobs WHERE id=?',(job,)).fetchone()
        db.execute('INSERT INTO ledger_event_context VALUES (?,?)',(cursor.lastrowid,row['fingerprint'] if row else ''))

    def get(self, job, db=None):
        if db is not None:
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone()
            if not row:
                return None
            result=dict(row)
            details=db.execute('SELECT summary FROM job_details WHERE job=? AND fingerprint=?',(job,row['fingerprint'])).fetchone()
            result['details']=json.loads(details['summary']) if details else None
            legacy=db.execute('SELECT metadata FROM legacy_publications WHERE job=?',(job,)).fetchone()
            if legacy:
                result['legacy_publication']=json.loads(legacy['metadata'])
            archived=db.execute('SELECT evidence FROM publication_archives WHERE job=?',(job,)).fetchone()
            if archived:
                result['publication_archive']=json.loads(archived['evidence'])
            abandoned=db.execute('SELECT evidence FROM preparation_abandonments WHERE job=? ORDER BY id',(job,)).fetchall()
            if abandoned:
                result['preparation_history']=[json.loads(r['evidence']) for r in abandoned]
            return result
        with self.store.transaction() as connection:
            return self.get(job, connection)

    def duplicate(self, candidate, db, *, exclude=None):
        m = candidate.media
        rows = db.execute('''SELECT * FROM jobs WHERE platform='shopee_video' AND account=?
            AND (logical=? OR source_hash IN (?,?) OR prepared_hash IN (?,?))''',
            (candidate.account_id, m.logical_asset_id, m.source_asset_hash, m.prepared_asset_hash,
             m.source_asset_hash, m.prepared_asset_hash)).fetchall()
        for row in rows:
            if row['id'] == exclude:
                continue
            if db.execute('SELECT 1 FROM preparation_abandonments WHERE job=?',(row['id'],)).fetchone():
                return True  # Only the same central job can restart its preparation.
            if row['state'] in ('PUBLISHED_LEGACY','ARCHIVED_MANUAL_PUBLICATION_REPORTED'):
                return True  # Permanent tombstone, independent of dedup_window.
            if row['state'] in ('UNKNOWN', 'PUBLISHING', 'UPLOADING', 'RESERVED', 'PREPARING', 'READY', 'ASSISTED_VALIDATED'):
                return True
            if row['attempted'] and (row['state'] != 'PUBLISHED' or self.clock() - row['created'] <= self.config.dedup_window):
                return True
        return False

    def reserve_job(self, candidate, owner, serial):
        job = self.identity(candidate)
        with self.store.transaction() as db:
            if self.store.killed(db):
                raise OperationalStop('KILL_SWITCH')
            if db.execute("SELECT 1 FROM jobs WHERE account=? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING')", (candidate.account_id,)).fetchone():
                raise OperationalStop('PREVIOUS_PUBLISH_ATTEMPT_REQUIRES_RECONCILIATION')
            old = self.get(job, db)
            if old and old['attempted']:
                raise OperationalStop('PREVIOUS_PUBLISH_ATTEMPT_REQUIRES_RECONCILIATION')
            if old and old.get('preparation_history'):
                if self.config.mode != FeatureMode.ASSISTED_MODE or old['fingerprint']!=candidate.fingerprint():
                    raise OperationalStop('ABANDONED_PREPARATION_ASSISTED_ONLY')
                if self.store.get(db,'breaker:'+candidate.account_id,{}).get('state')!='CLOSED':
                    raise OperationalStop('ABANDONED_PREPARATION_PREFLIGHT_REQUIRED')
            if old and old['state'] not in ('FAILED', 'CANCELLED', 'ASSISTED_VALIDATED', 'PREPARATION_ABANDONED'):
                raise OperationalStop('JOB_ALREADY_RESERVED')
            if self.duplicate(candidate, db, exclude=job):
                raise OperationalStop('DUPLICATE_MEDIA')
            try:
                for key in ('account:' + candidate.account_id, 'device:' + serial):
                    db.execute('INSERT INTO leases VALUES (?,?)', (key, owner))
            except Exception:
                raise OperationalStop('ACCOUNT_OR_DEVICE_ALREADY_IN_USE') from None
            m = candidate.media
            db.execute('INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (job, 'shopee_video', candidate.account_id, m.logical_asset_id, m.source_asset_hash,
                 m.prepared_asset_hash, candidate.fingerprint(), 'RESERVED', owner, self.clock(), 0, None))
            summary=dict(product=dict(shop_id=candidate.product.shop_id,item_id=candidate.product.item_id,
                variant_id=candidate.product.variant_id,attributes=candidate.product.attributes),
                caption_sha256=hashlib.sha256(json.dumps([candidate.caption,candidate.hashtags],ensure_ascii=False).encode()).hexdigest(),
                reviewer=candidate.human_review.reviewer if candidate.human_review else None,
                reviewed_at=candidate.human_review.timestamp if candidate.human_review else None,
                provenance=dict(source_type=candidate.provenance.source_type, source_category=candidate.provenance.source_category,
                    source_url=candidate.provenance.source_url, source_match=candidate.provenance.source_match,
                    rights_status=candidate.provenance.rights_status.value, ai_generated=candidate.provenance.ai_generated))
            summary['listing_reuse_review']=candidate.listing_reuse_review
            summary['originality']=candidate.originality
            db.execute('INSERT OR IGNORE INTO job_details VALUES (?,?,?)',(job,candidate.fingerprint(),json.dumps(summary,ensure_ascii=False)))
            self.record(db,job,'RESERVED',owner)
        return job

    def transition(self, job, owner, state, evidence=None):
        allowed = {'RESERVED': {'PREPARING', 'FAILED', 'CANCELLED'},
                   'PREPARING': {'READY', 'ASSISTED_VALIDATED', 'UPLOADING', 'FAILED', 'CANCELLED'},
                   'UPLOADING': {'READY', 'UNKNOWN'}, 'READY': {'FAILED', 'CANCELLED'},
                   'PUBLISHING': {'UNKNOWN'}}
        with self.store.transaction() as db:
            row = self.get(job, db)
            if not row or row['owner'] != owner or state not in allowed.get(row['state'], set()):
                raise OperationalStop('INVALID_LEDGER_TRANSITION')
            db.execute('UPDATE jobs SET state=?, evidence=? WHERE id=?', (state, json.dumps(evidence), job))
            self.record(db,job,state,owner)
            if state in ('FAILED', 'CANCELLED', 'ASSISTED_VALIDATED'):
                db.execute('DELETE FROM leases WHERE owner=?', (owner,))

    def reserve_publish_attempt(self, db, job, owner, fingerprint, ttl):
        if db.execute('SELECT 1 FROM preparation_abandonments WHERE job=?',(job,)).fetchone():
            raise OperationalStop('ABANDONED_PREPARATION_ASSISTED_ONLY')
        row = self.get(job, db)
        if not row or row['owner'] != owner or row['fingerprint'] != fingerprint or row['state'] != 'READY' or row['attempted']:
            raise OperationalStop('INVALID_PUBLISH_RESERVATION')
        token = uuid.uuid4().hex
        db.execute('UPDATE jobs SET state=\'PUBLISHING\', attempted=1 WHERE id=?', (job,))
        db.execute('INSERT INTO authorizations VALUES (?,?,?,?,?,0)', (token, job, owner, fingerprint, self.clock() + ttl))
        self.record(db,job,'PUBLISHING',owner)
        return token

    def consume_authorization(self, db, authorization, candidate, owner):
        row = db.execute('SELECT * FROM authorizations WHERE token=?', (authorization.token,)).fetchone()
        job = self.get(authorization.job_id, db)
        if not row or row['job'] != authorization.job_id or row['used'] or row['owner'] != owner or row['fingerprint'] != candidate.fingerprint() or row['expires'] <= self.clock() or not job or job['state'] != 'PUBLISHING' or job['owner'] != owner or job['fingerprint'] != candidate.fingerprint():
            raise OperationalStop('INVALID_OR_USED_PUBLISH_AUTHORIZATION')
        db.execute('UPDATE authorizations SET used=1 WHERE token=?', (authorization.token,))

    def mark_unknown(self, job, owner, reason):
        with self.store.transaction() as db:
            row = self.get(job, db)
            if row and row['owner'] == owner and row['state'] not in ('PUBLISHED', 'PUBLISHED_LEGACY', 'ARCHIVED_MANUAL_PUBLICATION_REPORTED'):
                db.execute("UPDATE jobs SET state='UNKNOWN', evidence=? WHERE id=?", (json.dumps({'reason': reason}), job))
                db.execute('UPDATE authorizations SET used=1 WHERE job=?', (job,))
                self.record(db,job,'UNKNOWN',owner)
        # Leases intentionally retained. Explicit reconciliation/recovery only.

    def import_legacy(self, root, account):
        from pathlib import Path
        for path in (Path(root) / 'debug/shopee_android').glob('*/session.json'):
            value = json.loads(path.read_text(encoding='utf-8-sig'))
            if value.get('central_job_id'):
                continue
            if not value.get('publish_attempted'):
                continue
            digest = value.get('media', {}).get('video_sha256') or value.get('selection_evidence', {}).get('video_sha256', '')
            key = 'legacy:' + hashlib.sha256(str(path.resolve()).encode()).hexdigest()
            with self.store.transaction() as db:
                if self.get(key, db):
                    continue
                db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (key, 'shopee_video', account, 'legacy:' + digest, digest, digest, '', 'UNKNOWN',
                     'legacy', self.clock(), 1, json.dumps({'session': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})))
                self.record(db,key,'UNKNOWN','legacy')

    def release_preparation(self, job, *, reviewer, reason, evidence):
        if not reviewer or not reason or not evidence:
            raise OperationalStop('EXPLICIT_RELEASE_REQUIRED')
        with self.store.transaction() as db:
            row = self.get(job,db)
            if not row or row['attempted'] or row['state'] not in ('RESERVED','PREPARING','READY'):
                raise OperationalStop('ATTEMPT_OR_UNKNOWN_REQUIRES_RECONCILIATION')
            db.execute("UPDATE jobs SET state='CANCELLED', evidence=? WHERE id=?",
                (json.dumps(dict(reviewer=reviewer,reason=reason,evidence=evidence)),job))
            db.execute('DELETE FROM leases WHERE owner=?',(row['owner'],))
            self.record(db,job,'CANCELLED',reviewer)

    def archive_manual_publication(self, job, evidence):
        """Retire a manually published incident without claiming full reconciliation.

        Keep the original evidence/fingerprint/attempt counter and permanent dedup.
        This method never closes a breaker or authorizes a new publication.
        """
        from pathlib import Path
        reference=Path(evidence.get('authorization_reference',''))
        if (evidence.get('operator_requested_archive') is not True or
                evidence.get('operator_reported_manual_publication') is not True or
                not evidence.get('reviewer') or not reference.is_file() or
                hashlib.sha256(reference.read_bytes()).hexdigest()!=evidence.get('authorization_sha256')):
            raise OperationalStop('EXPLICIT_MANUAL_ARCHIVE_EVIDENCE_REQUIRED')
        with self.store.transaction() as db:
            row=self.get(job,db)
            if not row or row['state']!='UNKNOWN' or row['account']!=evidence.get('account_id'):
                raise OperationalStop('UNKNOWN_ARCHIVE_ACCOUNT_REQUIRED')
            db.execute('INSERT INTO publication_archives VALUES (?,?,?,?)',
                (job,json.dumps(row,ensure_ascii=False),json.dumps(evidence,ensure_ascii=False),self.clock()))
            db.execute("UPDATE jobs SET state='ARCHIVED_MANUAL_PUBLICATION_REPORTED' WHERE id=?",(job,))
            db.execute('UPDATE authorizations SET used=1 WHERE job=?',(job,))
            db.execute('DELETE FROM leases WHERE owner=?',(row['owner'],))
            self.record(db,job,'ARCHIVED_MANUAL_PUBLICATION_REPORTED',evidence['reviewer'])
        return 'ARCHIVED_MANUAL_PUBLICATION_REPORTED'

    def resolve_preparation_unknown(self, job, *, reviewer, reason, evidence,
                                    verified_no_publish=False, verified_no_upload=False):
        """Explicit human cancellation only; never clears a durable publish attempt."""
        if not reviewer or not reason or not evidence or verified_no_publish is not True or verified_no_upload is not True:
            raise OperationalStop('EXPLICIT_NO_EFFECT_EVIDENCE_REQUIRED')
        with self.store.transaction() as db:
            row=self.get(job,db)
            if not row or row['state']!='UNKNOWN' or row['attempted']:
                raise OperationalStop('PUBLISH_ATTEMPT_REQUIRES_PUBLICATION_RECONCILIATION')
            db.execute("UPDATE jobs SET state='CANCELLED', evidence=? WHERE id=?",(json.dumps(dict(
                reviewer=reviewer,reason=reason,evidence=evidence,verified_no_publish=True,verified_no_upload=True)),job))
            db.execute('DELETE FROM leases WHERE owner=?',(row['owner'],))
            self.record(db,job,'CANCELLED',reviewer)
