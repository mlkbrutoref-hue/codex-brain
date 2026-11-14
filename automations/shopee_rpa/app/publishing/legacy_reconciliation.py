"""Administrative resolution of pre-PostCandidate attempts. Never authorizes a post."""
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.request
from urllib.parse import urlparse, unquote
import uuid
import xml.etree.ElementTree as ET

from app.media.identity import valid_hash
from app.operational.deadlines import OperationalStop
from app.operational.circuit_breaker import OperationCircuitBreaker


def require(condition, reason):
    if not condition:
        raise OperationalStop(reason)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class _PublicPage(HTMLParser):
    def __init__(self):
        super().__init__(); self.active = False; self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == '__NEXT_DATA__':
            self.active = True

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False


def public_fields(raw, resolved_url):
    page = _PublicPage(); page.feed(raw.decode('utf-8'))
    data = json.loads(''.join(page.parts))
    parsed = urlparse(resolved_url)
    require(parsed.scheme == 'https' and parsed.hostname == 'sv.shopee.com.br'
            and not parsed.username and not parsed.password, 'LEGACY_PUBLIC_HOST_INVALID')
    token = data['query']['postId']
    require(unquote(parsed.path) == '/share-video/' + token, 'LEGACY_PUBLIC_ID_MISMATCH')
    info = data['props']['pageProps']['mediaInfo']
    return dict(account=info['userInfo']['videoUserName'], caption=info['video']['caption'],
                hashtags=info['video']['hashtagContent'], duration=info['video']['duration'] / 1000,
                post_id=token, data=data)


def local_duration(path):
    executable = shutil.which('ffprobe')
    require(bool(executable), 'LEGACY_FFPROBE_REQUIRED')
    probe = subprocess.run([executable, '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'json', str(path)], capture_output=True, text=True,
                           timeout=15, check=True)
    return float(json.loads(probe.stdout)['format']['duration'])


@dataclass(frozen=True)
class LegacyPublicationEvidence:
    account_username: str
    public_post_url: str
    public_post_id: str
    expected_caption: str
    expected_hashtags: list[str]
    expected_media_hash: str
    expected_duration: float
    operator_confirmation: bool
    reviewer: str
    reviewed_at: float
    evidence_reference: str
    local_media_path: str
    historical_account_xml: str
    public_observation_path: str
    public_page_path: str


class LegacyPublicationReconciler:
    DURATION_TOLERANCE = .1

    def __init__(self, ledger):
        self.ledger = ledger

    def validate(self, row, e):
        require(row and row['id'].startswith('legacy:') and row['owner'] == 'legacy'
                and row['platform'] == 'shopee_video' and row['attempted'] == 1
                and row['fingerprint'] == '', 'NOT_AN_UNBOUND_LEGACY_ATTEMPT')
        require(e.operator_confirmation is True and bool(e.reviewer.strip())
                and Path(e.evidence_reference).is_file(), 'LEGACY_EXPLICIT_CONFIRMATION_REQUIRED')
        require(type(e.reviewed_at) in (int, float) and math.isfinite(e.reviewed_at)
                and row['created'] <= e.reviewed_at <= self.ledger.clock(), 'LEGACY_REVIEW_TIME_INVALID')
        require(type(e.expected_duration) in (int, float) and math.isfinite(e.expected_duration)
                and e.expected_duration > 0, 'LEGACY_DURATION_INVALID')
        original = json.loads(row['evidence'])
        session_path = Path(original['session'])
        require(digest(session_path) == original['sha256'], 'LEGACY_SESSION_CHANGED')
        session = json.loads(session_path.read_text(encoding='utf-8-sig'))
        require(session.get('publish_attempted') is True and
                'legacy:' + hashlib.sha256(str(session_path.resolve()).encode()).hexdigest() == row['id'],
                'LEGACY_SESSION_ATTEMPT_MISMATCH')
        selection = session['selection_evidence']
        require(e.account_username == row['account'] == selection['expected_account'],
                'LEGACY_ACCOUNT_MISMATCH')
        account_path = Path(e.historical_account_xml).resolve()
        references = {str(Path(x['path']).resolve()): x['sha256'] for x in selection['files']}
        require(str(account_path) in references and digest(account_path) == references[str(account_path)],
                'LEGACY_ACCOUNT_REFERENCE_CHANGED')
        labels = {n.get('text', '') for n in ET.parse(account_path).iter('node')
                  if n.get('package') == 'com.shopee.br'}
        require(e.account_username in labels or 'Nome de usuário: ' + e.account_username in labels,
                'LEGACY_HISTORICAL_ACCOUNT_NOT_OBSERVED')
        ready = next(t for t in reversed(session['transitions']) if t['state'] == 'READY_TO_PUBLISH')
        ready_path = Path(ready['evidence']['xml'])
        require(digest(ready_path) == ready['evidence']['xml_sha256'], 'LEGACY_CAPTION_REFERENCE_CHANGED')
        captions = [n.get('text') for n in ET.parse(ready_path).iter('node')
                    if n.get('package') == 'com.shopee.br' and n.get('resource-id', '').endswith('/et_caption')]
        tags = e.expected_hashtags
        require(isinstance(tags, list) and tags and all(isinstance(t, str) and re.fullmatch(r'\w+', t) for t in tags)
                and len(set(tags)) == len(tags), 'LEGACY_HASHTAGS_INVALID')
        full_caption = e.expected_caption + ' ' + ' '.join('#' + t for t in tags)
        require(captions == [full_caption], 'LEGACY_HISTORICAL_CAPTION_MISMATCH')
        require(valid_hash(e.expected_media_hash) and digest(e.local_media_path) == e.expected_media_hash
                == row['source_hash'] == row['prepared_hash'] == session['media']['video_sha256']
                == selection['video_sha256'], 'LEGACY_MEDIA_HASH_MISMATCH')
        duration = local_duration(e.local_media_path)
        require(math.isfinite(duration) and abs(duration - e.expected_duration) <= self.DURATION_TOLERANCE,
                'LEGACY_LOCAL_DURATION_MISMATCH')
        observation = json.loads(Path(e.public_observation_path).read_text(encoding='utf-8-sig'))
        raw = Path(e.public_page_path).read_bytes()
        require(digest(e.public_page_path) == observation['html_sha256']
                and observation['requested_url'] == e.public_post_url, 'LEGACY_PUBLIC_REFERENCE_CHANGED')
        request = urlparse(e.public_post_url)
        require(request.scheme == 'https' and request.hostname in ('br.shp.ee', 'sv.shopee.com.br')
                and not request.username and not request.password, 'LEGACY_PUBLIC_URL_INVALID')
        public = public_fields(raw, observation['resolved_url'])
        require(public['data'] == observation['data'], 'LEGACY_PUBLIC_SNAPSHOT_MISMATCH')
        require(public['account'] == e.account_username, 'LEGACY_PUBLIC_ACCOUNT_MISMATCH')
        require(public['post_id'] == e.public_post_id and bool(e.public_post_id), 'LEGACY_PUBLIC_ID_MISMATCH')
        require(public['caption'] == full_caption and public['hashtags'] == tags, 'LEGACY_PUBLIC_CAPTION_MISMATCH')
        require(math.isfinite(public['duration']) and abs(public['duration'] - duration) <= self.DURATION_TOLERANCE,
                'LEGACY_PUBLIC_DURATION_MISMATCH')
        attempted_at = next(t['timestamp'] for t in session['transitions'] if t['state'] == 'PUBLISHING')
        require(datetime.fromisoformat(attempted_at).timestamp() <= e.reviewed_at, 'LEGACY_REVIEW_PRECEDES_ATTEMPT')
        return dict(publication_status='PUBLISHED_LEGACY', reconciliation_quality='LEGACY_PARTIAL',
            product_binding_status='UNKNOWN', candidate_fingerprint_status='NOT_AVAILABLE_LEGACY',
            shop_id=None, item_id=None, variant_id=None, candidate_fingerprint=None,
            public_post_url=e.public_post_url, public_post_id=e.public_post_id,
            reviewer=e.reviewer, reviewed_at=e.reviewed_at, evidence_reference=e.evidence_reference,
            verified_fields=['account_username', 'caption', 'hashtags', 'historical_media_hash',
                             'compatible_duration', 'public_post_url_id', 'operator_confirmation'],
            unknown_fields=['candidate_fingerprint', 'shop_id', 'item_id', 'variant_id',
                            'commercial_binding', 'public_post_created_at'],
            media_match='PASS', media_match_basis='OPERATOR_CONFIRMATION_AND_HISTORICAL_HASH',
            caption_match='PASS', historical_duration=duration, public_duration=public['duration'],
            historical_attempt_at=attempted_at, original_session_sha256=original['sha256'],
            original_evidence=row['evidence'], original_attempted=row['attempted'],
            retry_allowed=False, dedup_permanent=True,
            reference_hashes={str(Path(p).resolve()): digest(p) for p in
                (session_path, account_path, ready_path, e.public_page_path,
                 e.public_observation_path, e.evidence_reference)})

    def reconcile(self, job, evidence):
        row = self.ledger.get(job)
        require(bool(row), 'LEGACY_JOB_NOT_FOUND')
        try:
            serialized = json.dumps(asdict(evidence), sort_keys=True, ensure_ascii=False, allow_nan=False)
        except (ValueError, TypeError):
            raise OperationalStop('LEGACY_INVALID_EVIDENCE_ENCODING') from None
        if row['state'] == 'PUBLISHED_LEGACY':
            with self.ledger.store.transaction() as db:
                old = db.execute('SELECT evidence FROM legacy_publications WHERE job=?', (job,)).fetchone()
                require(old and old['evidence'] == serialized, 'LEGACY_ALREADY_RESOLVED_DIFFERENT_EVIDENCE')
            return 'PUBLISHED_LEGACY'
        require(row['state'] == 'UNKNOWN', 'LEGACY_UNKNOWN_REQUIRED')
        metadata = self.validate(row, evidence)
        with self.ledger.store.transaction() as db:
            current = self.ledger.get(job, db)
            require(current == row, 'LEGACY_JOB_CHANGED_DURING_REVIEW')
            require(all(digest(path) == value for path, value in metadata['reference_hashes'].items())
                    and digest(evidence.local_media_path) == evidence.expected_media_hash,
                    'LEGACY_REFERENCE_CHANGED_DURING_REVIEW')
            db.execute('INSERT INTO legacy_publications VALUES (?,?,?)',
                       (job, serialized, json.dumps(metadata, ensure_ascii=False, allow_nan=False)))
            db.execute("UPDATE jobs SET state='PUBLISHED_LEGACY' WHERE id=?", (job,))
            # Original evidence, empty fingerprint, attempted flag and all counters remain untouched.
            db.execute('UPDATE authorizations SET used=1 WHERE job=?', (job,))
            if not db.execute("SELECT 1 FROM jobs WHERE account=? AND id!=? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING')",
                              (row['account'], job)).fetchone():
                for key in ('account:' + row['account'], 'device:' +
                            json.loads(Path(json.loads(row['evidence'])['session']).read_text(encoding='utf-8-sig'))['selection_evidence']['serial']):
                    db.execute('DELETE FROM leases WHERE key=? AND owner=?', (key, row['owner']))
            self.ledger.record(db, job, 'PUBLISHED_LEGACY', evidence.reviewer)
        return 'PUBLISHED_LEGACY'


@dataclass(frozen=True)
class LegacyBreakerAssessment:
    only_legacy_incident_confirmed: bool
    expected_breaker: dict
    reviewer: str
    reviewed_at: float
    evidence_reference: str


class LegacyBreakerRecovery:
    """Scope-specific preflight: ledger consistency + fresh read-only public post GET.

    This clears only PUBLICATION_UNKNOWN, not any Android/login/security incident.
    Current-device checks and PublishGate remain mandatory for future effects.
    """
    def __init__(self, ledger):
        self.ledger = ledger

    def _check_local(self, db, job):
        row = self.ledger.get(job, db)
        require(row and row['state'] == 'PUBLISHED_LEGACY', 'RESOLVED_LEGACY_REQUIRED')
        require(db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'LEDGER_INTEGRITY_FAILED')
        require(not self.ledger.store.killed(db), 'KILL_SWITCH')
        require(not db.execute("SELECT 1 FROM jobs WHERE account=? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING','RESERVED','PREPARING','READY')",
                               (row['account'],)).fetchone(), 'OTHER_ACCOUNT_JOB_REQUIRES_REVIEW')
        require(not db.execute('SELECT 1 FROM leases WHERE key=?', ('account:' + row['account'],)).fetchone(),
                'ACCOUNT_ALREADY_IN_USE')
        require(not db.execute('SELECT 1 FROM authorizations a JOIN jobs j ON j.id=a.job WHERE j.account=? AND a.used=0 AND a.expires>?',
                               (row['account'], self.ledger.clock())).fetchone(), 'OTHER_PUBLISH_AUTHORIZATION')
        return row

    def recover(self, job, assessment, output_path):
        require(assessment.only_legacy_incident_confirmed is True and assessment.reviewer.strip()
                and Path(assessment.evidence_reference).is_file(), 'LEGACY_INCIDENT_SCOPE_REVIEW_REQUIRED')
        require(type(assessment.reviewed_at) in (int, float) and math.isfinite(assessment.reviewed_at)
                and 0 <= self.ledger.clock() - assessment.reviewed_at <= self.ledger.config.approval_ttl,
                'LEGACY_INCIDENT_SCOPE_REVIEW_EXPIRED')
        output_path = Path(output_path)
        require(not output_path.exists(), 'PREFLIGHT_EVIDENCE_ALREADY_EXISTS')
        token = uuid.uuid4().hex
        with self.ledger.store.transaction() as db:
            row = self._check_local(db, job)
            breaker = OperationCircuitBreaker(self.ledger.store, row['account'], self.ledger.config)
            state = breaker.snapshot(db)
            require(state == assessment.expected_breaker and state['state'] == 'OPEN'
                    and state.get('reason') == 'PUBLICATION_UNKNOWN', 'BREAKER_SCOPE_CHANGED_OR_OTHER_INCIDENT')
            # Last CLOSED is an explicit reviewed resolution boundary. A retained latest
            # reason alone is never used to discard another failure in this epoch.
            boundary = db.execute("SELECT MAX(id) FROM breaker_events WHERE account=? AND kind='RELEASE' AND reason='CLOSED'",
                                  (row['account'],)).fetchone()[0] or 0
            events = db.execute("SELECT * FROM breaker_events WHERE account=? AND id>? AND kind='FAILURE'",
                                (row['account'], boundary)).fetchall()
            require(all(x['reason'] == 'PUBLICATION_UNKNOWN' and x['job'] == job for x in events),
                    'OTHER_OR_UNSCOPED_BREAKER_INCIDENT')
            previous = dict(state)
            state.update(state='HALF_OPEN', recovery_job=job, recovery_token=token,
                         reviewer=assessment.reviewer, evidence=assessment.evidence_reference,
                         scope_assessment_sha256=digest(assessment.evidence_reference))
            self.ledger.store.put(db, breaker.key, state)
            event = db.execute('INSERT INTO breaker_events(account,kind,reason,job,timestamp,snapshot) VALUES (?,?,?,?,?,?)',
                (row['account'], 'LEGACY_HALF_OPEN', 'PUBLICATION_UNKNOWN', job,
                 self.ledger.clock(), json.dumps(state))).lastrowid
        report = dict(job_id=job, scope='LEGACY_LEDGER_AND_PUBLIC_POST_READ_ONLY', before=previous,
                      half_open=state, assessment=asdict(assessment), android_connected=False,
                      publish_attempt_created=False)
        try:
            breaker.check(read_only=True)
            meta = row['legacy_publication']
            # A fresh normal HTTPS GET; no API publication, navigation or authentication.
            with urllib.request.urlopen(meta['public_post_url'], timeout=15) as response:
                raw = response.read(524289)
                require(len(raw) <= 524288, 'PUBLIC_PREFLIGHT_RESPONSE_TOO_LARGE')
                observed = public_fields(raw, response.url)
            legacy = json.loads(self._legacy_evidence(job))
            expected_caption = legacy['expected_caption'] + ' ' + ' '.join('#' + t for t in legacy['expected_hashtags'])
            require(observed['post_id'] == meta['public_post_id'] and observed['account'] == row['account']
                    and observed['caption'] == expected_caption and observed['hashtags'] == legacy['expected_hashtags']
                    and math.isfinite(observed['duration']) and abs(observed['duration'] - meta['historical_duration']) <= .1,
                    'PUBLIC_PREFLIGHT_POST_CHANGED')
            with self.ledger.store.transaction() as db:
                self._check_local(db, job)
                current = breaker.snapshot(db)
                require(current['state'] == 'HALF_OPEN' and current.get('recovery_token') == token,
                        'BREAKER_CHANGED_DURING_PREFLIGHT')
                require(not db.execute("SELECT 1 FROM breaker_events WHERE account=? AND id>? AND kind IN ('FAILURE','RELEASE','LEGACY_HALF_OPEN')",
                                       (row['account'], event)).fetchone(), 'NEW_INCIDENT_DURING_PREFLIGHT')
                current.update(state='CLOSED', failures=0, critical=False, not_before=0,
                               reason='LEGACY_PUBLICATION_RESOLVED', preflight_reference=str(output_path),
                               preflight_at=self.ledger.clock(),
                               preflight_checks=dict(ledger_integrity='ok',kill_switch=False,
                                   no_other_pending_job=True,no_new_breaker_incident=True,
                                   public_post_id=observed['post_id'],account_username=observed['account'],
                                   caption_match='PASS',duration_match='PASS',
                                   public_page_sha256=hashlib.sha256(raw).hexdigest(),
                                   scope='LEGACY_LEDGER_AND_PUBLIC_POST_READ_ONLY'))
                self.ledger.store.put(db, breaker.key, current)
                db.execute('INSERT INTO breaker_events(account,kind,reason,job,timestamp,snapshot) VALUES (?,?,?,?,?,?)',
                    (row['account'], 'RELEASE', 'CLOSED', job, self.ledger.clock(), json.dumps(current)))
            report.update(result='PASS', after=current, public_post_id=observed['post_id'],
                          public_page_sha256=hashlib.sha256(raw).hexdigest())
        except Exception as exc:
            # Keep HALF_OPEN on an unavailable read; any concurrent incident that
            # reopened the breaker is preserved. No automatic close or retry.
            report.update(result='FAIL', reason=str(exc), after=breaker.snapshot())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        return report

    def _legacy_evidence(self, job):
        with self.ledger.store.transaction() as db:
            return db.execute('SELECT evidence FROM legacy_publications WHERE job=?', (job,)).fetchone()['evidence']
