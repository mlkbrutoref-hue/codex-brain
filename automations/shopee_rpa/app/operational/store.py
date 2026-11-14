from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from app.operational.config import shared_store_path


class OperationalStore:
    def __init__(self, path=None, timeout=2):
        self.path = Path(path) if path is not None else shared_store_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        with self.transaction() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS counters (scope TEXT, name TEXT, amount REAL NOT NULL,
                    PRIMARY KEY(scope,name));
                CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, platform TEXT, account TEXT,
                    logical TEXT, source_hash TEXT, prepared_hash TEXT, fingerprint TEXT,
                    state TEXT NOT NULL, owner TEXT, created REAL, attempted INTEGER DEFAULT 0,
                    evidence TEXT);
                CREATE INDEX IF NOT EXISTS dedup ON jobs(platform,account,logical);
                CREATE TABLE IF NOT EXISTS leases (key TEXT PRIMARY KEY, owner TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS authorizations (token TEXT PRIMARY KEY, job TEXT,
                    owner TEXT, fingerprint TEXT, expires REAL, used INTEGER DEFAULT 0);
                CREATE TABLE IF NOT EXISTS ledger_events (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job TEXT, state TEXT, owner TEXT, timestamp REAL);
                CREATE TABLE IF NOT EXISTS job_details (job TEXT, fingerprint TEXT, summary TEXT,
                    PRIMARY KEY(job,fingerprint));
                CREATE TABLE IF NOT EXISTS ledger_event_context (event_id INTEGER PRIMARY KEY,
                    fingerprint TEXT);
                CREATE TABLE IF NOT EXISTS legacy_publications (job TEXT PRIMARY KEY,
                    evidence TEXT NOT NULL, metadata TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS breaker_events (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account TEXT NOT NULL, kind TEXT NOT NULL, reason TEXT, job TEXT,
                    timestamp REAL NOT NULL, snapshot TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS preparation_abandonments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, job TEXT NOT NULL,
                    incident_event INTEGER NOT NULL UNIQUE, fingerprint TEXT NOT NULL,
                    original_snapshot TEXT NOT NULL, evidence TEXT NOT NULL, timestamp REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS publication_archives (
                    job TEXT PRIMARY KEY, original_snapshot TEXT NOT NULL,
                    evidence TEXT NOT NULL, timestamp REAL NOT NULL);
            ''')

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=self.timeout, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            if db.in_transaction:
                db.commit()
        except BaseException:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def get(db, key, default=None):
        row = db.execute('SELECT value FROM kv WHERE key=?', (key,)).fetchone()
        return json.loads(row['value']) if row else default

    @staticmethod
    def put(db, key, value):
        db.execute('INSERT OR REPLACE INTO kv VALUES (?,?)', (key, json.dumps(value, allow_nan=False)))

    def set_kill_switch(self, enabled, *, reviewer, reason):
        if not reviewer or not reason:
            raise ValueError('RELEASE_REQUIRES_REVIEWER_AND_REASON')
        with self.transaction() as db:
            self.put(db, 'kill_switch', dict(enabled=bool(enabled), reviewer=reviewer, reason=reason))

    def killed(self, db=None):
        if db is not None:
            return bool(self.get(db, 'kill_switch', {}).get('enabled'))
        with self.transaction() as connection:
            return self.killed(connection)
