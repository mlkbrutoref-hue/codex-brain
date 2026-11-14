import time
import threading


class OperationalStop(RuntimeError):
    pass


class ExecutionDeadline:
    def __init__(self, seconds, *, clock=time.monotonic, cancel_event=None):
        if seconds <= 0:
            raise ValueError('INVALID_DEADLINE')
        self.clock = clock
        self.ends_at = clock() + seconds
        self.cancel_event = cancel_event or threading.Event()

    def remaining(self):
        return max(0., self.ends_at - self.clock())

    def expired(self):
        return self.remaining() <= 0 or self.cancel_event.is_set()

    def raise_if_expired(self):
        if self.cancel_event.is_set():
            raise OperationalStop('CANCELLED')
        if self.remaining() <= 0:
            raise OperationalStop('GLOBAL_DEADLINE_EXPIRED')

    def child_timeout(self, max_seconds):
        self.raise_if_expired()
        if max_seconds <= 0:
            raise OperationalStop('INVALID_CHILD_TIMEOUT')
        return min(max_seconds, self.remaining())

    def wait(self, seconds):
        self.raise_if_expired()
        self.cancel_event.wait(self.child_timeout(seconds))
        self.raise_if_expired()


Deadline = ExecutionDeadline
