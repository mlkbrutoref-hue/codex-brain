from dataclasses import dataclass, asdict
import json
from app.operational.deadlines import OperationalStop
from app.media.identity import valid_hash


@dataclass(frozen=True)
class PublicationEvidence:
    account_id: str
    candidate_fingerprint: str
    post_id: str
    post_url: str
    observed_at: float
    reviewer: str
    evidence_reference: str
    media_match: str
    caption_match: str
    product_match: str


class PublicationReconciler:
    """Consumes read-only/manual evidence; never navigates, uploads or reposts."""
    def __init__(self, ledger, logger=None):
        self.ledger, self.logger = ledger, logger

    def reconcile(self, job, evidence=None):
        with self.ledger.store.transaction() as db:
            row = self.ledger.get(job, db)
            if not row or row['state'] not in ('PUBLISHING', 'UNKNOWN', 'PUBLISHED'):
                raise OperationalStop('NO_ATTEMPT_TO_RECONCILE')
            if row['state'] == 'PUBLISHED':
                return 'PUBLISHED'
            valid = evidence and valid_hash(row['fingerprint']) and valid_hash(evidence.candidate_fingerprint) and evidence.account_id == row['account'] and evidence.candidate_fingerprint == row['fingerprint'] and (evidence.post_id or evidence.post_url) and evidence.reviewer and evidence.evidence_reference and row['created'] <= evidence.observed_at <= self.ledger.clock()
            valid = valid and all(getattr(evidence, key) == 'PASS' for key in ('media_match', 'caption_match', 'product_match'))
            state = 'PUBLISHED' if valid else 'UNKNOWN'
            db.execute('UPDATE jobs SET state=?, evidence=? WHERE id=?', (state, json.dumps(asdict(evidence)) if valid else row['evidence'], job))
            db.execute('UPDATE authorizations SET used=1 WHERE job=?', (job,))
            self.ledger.record(db,job,state,evidence.reviewer if valid else 'reconciler')
            if valid:
                db.execute('DELETE FROM leases WHERE owner=?', (row['owner'],))
        if self.logger:
            self.logger.log_reconciliation(status=state)
        return state
