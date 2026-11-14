from collections import deque
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
import time


class OperationLogger:
    # Allowlist rather than attempts to redact arbitrary nested secrets.
    FIELDS = {'operation_mode', 'action_type', 'element', 'token_cost', 'latency_ms', 'status',
              'state', 'previous_state', 'check', 'error_code', 'budget_remaining', 'circuit_breaker_state'}

    def __init__(self, path, *, session_id, job_id, account_id, last_n=500):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.context = dict(session_id=session_id, job_id=job_id, account_id=account_id)
        self.events = deque(maxlen=last_n)
        self.lock = threading.Lock()
        self.started = time.monotonic()
        if self.path.exists():
            with self.path.open(encoding='utf-8') as stream:
                for line in stream:
                    try:
                        event=json.loads(line)
                        if all(event.get(k)==v for k,v in self.context.items()):self.events.append(event)
                    except ValueError:
                        continue

    def _log(self, event, **fields):
        # element must be a technical selector category, never user text/description.
        safe = {k: v for k, v in fields.items() if k in self.FIELDS and isinstance(v, (str, int, float, bool, type(None)))}
        for key in ('element', 'error_code', 'check', 'state', 'previous_state'):
            if key in safe and (not isinstance(safe[key], str) or not all(c.isalnum() or c in '_:.-/' for c in safe[key]) or len(safe[key]) > 120):
                safe[key] = 'REDACTED'
        record = dict(timestamp=datetime.now(timezone.utc).isoformat(), **self.context, event=event, **safe)
        with self.lock:
            with self.path.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
            self.events.append(record)
        return record

    def log_action(self, **fields): return self._log('action', **fields)
    def log_transition(self, **fields): return self._log('transition', **fields)
    def log_validation(self, **fields): return self._log('validation', **fields)
    def log_error(self, **fields): return self._log('error', **fields)
    def log_publish_attempt(self, **fields): return self._log('publish_attempt', **fields)
    def log_reconciliation(self, **fields): return self._log('reconciliation', **fields)

    def get_health_report(self, **current):
        from app.observability.health import health_report
        return health_report(list(self.events), session_duration=time.monotonic() - self.started, **current)
