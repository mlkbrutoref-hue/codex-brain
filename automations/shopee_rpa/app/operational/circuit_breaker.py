from enum import Enum
import json
import time
from app.operational.deadlines import OperationalStop


class CircuitState(str, Enum):
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    HALF_OPEN = 'HALF_OPEN'


class OperationCircuitBreaker:
    CRITICAL = {'CAPTCHA', 'LOGIN', 'SMS', 'DEVICE_CONFIRMATION', 'SECURITY_ALERT',
                'ACCOUNT_RESTRICTED', 'PUBLICATION_UNKNOWN', 'PRODUCT_MISMATCH',
                'MEDIA_MISMATCH', 'ACCOUNT_MISMATCH', 'RPC_EFFECT_UNKNOWN'}

    def __init__(self, store, account, config, clock=time.time):
        self.store, self.account, self.config, self.clock = store, account, config, clock
        self.key = 'breaker:' + account

    def snapshot(self, db=None):
        if db is not None:
            return self.store.get(db, self.key, dict(state='CLOSED', failures=0, critical=False, not_before=0))
        with self.store.transaction() as connection:
            return self.snapshot(connection)

    def check(self, *, read_only=False, db=None):
        def verify(connection):
            state = self.snapshot(connection)
            if self.store.killed(connection):
                raise OperationalStop('KILL_SWITCH')
            if state['state'] == 'OPEN' or (state['state'] == 'HALF_OPEN' and not read_only):
                raise OperationalStop('CIRCUIT_' + state['state'])
        if db is not None:
            return verify(db)
        with self.store.transaction() as connection:
            verify(connection)

    def failure(self, reason, *, critical=False, retry_after=0, job_id=None):
        with self.store.transaction() as db:
            state = self.snapshot(db)
            was_critical = state['critical']
            new_critical = critical or reason in self.CRITICAL
            state['failures'] += 1
            state['critical'] = was_critical or new_critical
            if state['critical'] or state['failures'] >= self.config.breaker_threshold or retry_after > 0:
                state.update(state='OPEN',
                    not_before=max(state.get('not_before', 0), self.clock() + max(self.config.cooldown_seconds, retry_after)))
                if not was_critical or new_critical:
                    state['reason'] = reason
            self.store.put(db, self.key, state)
            db.execute('INSERT INTO breaker_events(account,kind,reason,job,timestamp,snapshot) VALUES (?,?,?,?,?,?)',
                (self.account,'FAILURE',reason,job_id,self.clock(),json.dumps(state)))

    def success(self):
        with self.store.transaction() as db:
            state = self.snapshot(db)
            if state['state'] == 'CLOSED':
                state['failures'] = 0
                self.store.put(db, self.key, state)

    def release(self, *, reviewer, reason, evidence, close=False, db=None):
        if not reviewer or not reason or not evidence:
            raise OperationalStop('EXPLICIT_RELEASE_REQUIRED')
        def apply(db):
            state = self.snapshot(db)
            if not state['critical'] and self.clock() < state.get('not_before', 0):
                raise OperationalStop('COOLDOWN_ACTIVE')
            if close and state['state'] != 'HALF_OPEN':
                raise OperationalStop('READ_PREFLIGHT_REQUIRED')
            state.update(state='CLOSED' if close else 'HALF_OPEN', failures=0,
                         reviewer=reviewer, reason=reason, evidence=evidence)
            if close:
                state['critical'] = False
            self.store.put(db, self.key, state)
            db.execute('INSERT INTO breaker_events(account,kind,reason,job,timestamp,snapshot) VALUES (?,?,?,?,?,?)',
                (self.account,'RELEASE',state['state'],None,self.clock(),json.dumps(state)))
        if db is not None:
            apply(db)
        else:
            with self.store.transaction() as connection:
                apply(connection)
