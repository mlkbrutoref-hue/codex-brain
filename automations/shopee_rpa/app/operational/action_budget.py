from datetime import datetime
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import timezone, timedelta
from app.operational.config import ActionType
from app.operational.deadlines import OperationalStop


class AccountBudget:
    def __init__(self, store, account, session, worker, config, clock=time.time):
        self.store, self.account, self.session, self.worker = store, account, session, worker
        self.config, self.clock = config, clock
        try:
            self.tz = ZoneInfo(config.timezone)
        except ZoneInfoNotFoundError:
            if config.timezone != 'America/Sao_Paulo':
                raise
            self.tz = timezone(timedelta(hours=-3))  # Current Brazil timezone; explicit fallback.

    def scopes(self):
        day = datetime.fromtimestamp(self.clock(), self.tz).date().isoformat()
        return ('account:' + self.account + ':' + day, 'session:' + self.account + ':' + self.session,
                'worker:' + self.account + ':' + self.worker)

    def charge(self, db, action):
        day, session, worker = self.scopes()
        key='session_started:' + session
        started=self.store.get(db,key)
        if started is None:
            started=self.clock()
            self.store.put(db,key,started)
        if self.clock()-started >= self.config.session_seconds:
            raise OperationalStop('SESSION_DURATION_BUDGET_EXCEEDED')
        limits = self.config.limits
        entries = [(worker, 'actions', limits.actions_worker)]
        if action == ActionType.PUBLISH_ATTEMPT:
            entries += [(day, 'posts_attempted', limits.posts_per_day), (session, 'posts_attempted', limits.posts_per_session)]
        elif action == ActionType.UPLOAD_START:
            entries += [(day, 'uploads_started', limits.uploads_per_day), (session, 'uploads_started', limits.uploads_per_session)]
        elif action == ActionType.PRODUCT_LOOKUP:
            entries += [(session, 'product_views', limits.product_views_session)]
        for scope, name, maximum in entries:
            row = db.execute('SELECT amount FROM counters WHERE scope=? AND name=?', (scope, name)).fetchone()
            if (row['amount'] if row else 0) + 1 > maximum:
                raise OperationalStop('BUDGET_EXCEEDED:' + name)
        for scope, name, _ in entries:
            db.execute('INSERT INTO counters VALUES (?,?,1) ON CONFLICT(scope,name) DO UPDATE SET amount=amount+1', (scope, name))

    def snapshot(self):
        with self.store.transaction() as db:
            result={scope: {r['name']: r['amount'] for r in db.execute('SELECT name,amount FROM counters WHERE scope=?', (scope,))} for scope in self.scopes()}
            started=self.store.get(db,'session_started:'+self.scopes()[1],self.clock())
            result['session_duration']=max(0,self.clock()-started)
            return result


class ActionBudget:
    def __init__(self, store, account_budget, breaker, config, clock=time.time):
        self.store, self.account_budget, self.breaker, self.config, self.clock = store, account_budget, breaker, config, clock
        self.key = 'tokens:' + account_budget.account

    def _bucket(self, db):
        stamp = self.clock()
        value = self.store.get(db, self.key, dict(tokens=self.config.max_tokens, updated=stamp))
        value['tokens'] = min(self.config.max_tokens, value['tokens'] + max(0, stamp - value['updated']) * self.config.refill_rate)
        value['updated'] = max(stamp, value['updated'])
        return value

    def consume(self, action_type, *, db=None):
        action_type = ActionType(action_type)
        def charge(connection):
            self.breaker.check(read_only=action_type == ActionType.READ_STATE, db=connection)
            value = self._bucket(connection)
            cost = self.config.action_costs[action_type]
            if value['tokens'] < cost:
                raise OperationalStop('TOKEN_BUDGET_EXHAUSTED')
            self.account_budget.charge(connection, action_type)
            value['tokens'] -= cost
            self.store.put(connection, self.key, value)
            return cost
        if db is not None:
            return charge(db)
        with self.store.transaction() as connection:
            return charge(connection)

    def can_consume(self, action_type):
        with self.store.transaction() as db:
            db.execute('SAVEPOINT budget_preview')
            try:
                self.consume(action_type,db=db)
                return True
            except OperationalStop:
                return False
            finally:
                db.execute('ROLLBACK TO budget_preview')
                db.execute('RELEASE budget_preview')

    def remaining_tokens(self):
        with self.store.transaction() as db:
            return self._bucket(db)['tokens']

    def wait_for_tokens(self, cost, deadline):
        if cost <= 0 or cost > self.config.max_tokens:
            raise OperationalStop('INVALID_TOKEN_COST')
        while True:
            deadline.raise_if_expired()
            self.breaker.check()
            remaining = self.remaining_tokens()
            if remaining >= cost:
                return
            deadline.wait(min(.25, (cost - remaining) / self.config.refill_rate))

    def reset_session(self, session_id):
        # A new session must not refill account tokens or erase day/worker counters.
        if not session_id or session_id == self.account_budget.session:
            raise OperationalStop('NEW_SESSION_ID_REQUIRED_COUNTERS_PRESERVED')
        self.account_budget.session = session_id
        return self.snapshot()

    def snapshot(self):
        return dict(tokens=self.remaining_tokens(), counters=self.account_budget.snapshot())
