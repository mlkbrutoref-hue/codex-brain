"""Local, append-only measurements. No network, prompts, credentials or billing guesses."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
import inspect
import json
import os
from pathlib import Path
import threading
import time
from uuid import uuid4
import warnings


_active = ContextVar("performance_recorder", default=None)
_parent = ContextVar("performance_parent", default=None)
COUNTERS = {
    "antigravity_calls", "antigravity_retries", "antigravity_cli_checks",
    "antigravity_mock_calls", "flow_generations", "flow_regenerations",
    "browser_sessions", "browser_actions", "creative_ai_calls", "polls",
    "downloads", "download_retries", "reference_uploads", "product_uploads",
    "antigravity_failures", "antigravity_timeouts", "antigravity_empty_results",
    "shopee_calls", "download_attempts", "downloads_completed", "resume_skips",
    "ffmpeg_encodes", "creative_rebuilds", "antigravity_visual_qa_calls",
}
EXTERNAL_STAGES = {
    "FLOW_OPEN_MS", "FLOW_NAVIGATION_MS", "REFERENCE_UPLOAD_MS",
    "PRODUCT_UPLOAD_MS", "PROMPT_INSERT_MS", "GENERATION_REQUEST_MS",
    "FLOW_GENERATION_MS", "GENERATION_WAIT_MS", "DOWNLOAD_MS",
    "VISUAL_QA_MS", "POST_PROCESSING_MS",
    "ANTIGRAVITY_QA_MS", "DOWNLOAD_WAIT_MS", "FFMPEG_NORMALIZE_MS", "EXPORT_MS",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Recorder:
    """One file per invocation prevents cross-process writers sharing a file."""

    def __init__(self, directory, job_id=None):
        self.run_id = uuid4().hex
        self.path = Path(directory) / (self.run_id + ".jsonl")
        self.job_id = job_id
        self._lock = threading.Lock()
        self.write_failed = False

    def emit(self, kind, **fields):
        event = {"schema_version": 1, "event": kind, "at": utc_now(),
                 "run_id": self.run_id, "job_id": self.job_id, **fields}
        try:
            with self._lock:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            # Observability must not invalidate an otherwise valid video/job.
            if not self.write_failed:
                warnings.warn("Local telemetry unavailable; measurements are incomplete.", RuntimeWarning)
            self.write_failed = True

    def count(self, name, amount=1, source="instrumented"):
        if name not in COUNTERS or type(amount) is not int or amount < 0:
            raise ValueError("Unknown counter or invalid increment")
        if source not in {"instrumented", "operator_observed", "mock"}:
            raise ValueError("Invalid counter provenance")
        self.emit("counter", name=name, amount=amount, source=source)

    @contextmanager
    def stage(self, name):
        span_id = uuid4().hex
        parent_id = _parent.get()
        started_at, tick = utc_now(), time.perf_counter()
        self.emit("stage_started", name=name, span_id=span_id,
                  parent_id=parent_id, started_at=started_at)
        token = _parent.set(span_id)
        status, error_type = "OK", None
        try:
            yield
        except BaseException as exc:
            status, error_type = "ERROR", type(exc).__name__
            raise
        finally:
            duration_ms = (time.perf_counter() - tick) * 1000
            _parent.reset(token)
            self.emit("stage_finished", name=name, span_id=span_id,
                      parent_id=parent_id, started_at=started_at,
                      finished_at=utc_now(), duration_ms=duration_ms,
                      status=status, error_type=error_type)


@contextmanager
def telemetry_session(directory, job_id=None):
    """Also usable by an authorized external operator; does not operate providers."""
    recorder = Recorder(directory, job_id)
    token, parent_token = _active.set(recorder), _parent.set(None)
    recorder.emit("session_started", cost_status="COST_UNKNOWN", cost=None,
                  external_coverage="NOT_AUTOMATIC")
    try:
        yield recorder
    finally:
        recorder.emit("session_finished")
        _parent.reset(parent_token)
        _active.reset(token)


def bind_job(job_id):
    recorder = _active.get()
    if recorder:
        recorder.job_id = job_id
        recorder.emit("job_bound")


def record_state(state):
    if _active.get():
        _active.get().emit("job_state", state=state)


def count(name, amount=1, source="instrumented"):
    if _active.get():
        _active.get().count(name, amount, source)


def timed_call(name, function, *args, **kwargs):
    recorder = _active.get()
    if not recorder:
        return function(*args, **kwargs)
    with recorder.stage(name):
        return function(*args, **kwargs)


def job_operation(name):
    """Measure one orchestrator invocation, including errors; never retries it."""
    def decorate(function):
        signature = inspect.signature(function)

        @wraps(function)
        def wrapped(self, *args, **kwargs):
            bound = signature.bind(self, *args, **kwargs)
            job_id = bound.arguments.get("job_id")
            if _active.get() is not None:
                return timed_call(name, function, self, *args, **kwargs)
            with telemetry_session(self.base_dir / "data" / "telemetry", job_id):
                return timed_call(name, function, self, *args, **kwargs)
        return wrapped
    return decorate


def antigravity_operation(function):
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        if _active.get() is None:
            directory = Path(os.environ.get("AICC_TELEMETRY_DIR") or
                             Path(__file__).resolve().parents[2] / "data" / "telemetry")
            with telemetry_session(directory):
                return timed_call("ANTIGRAVITY_MS", function, self, *args, **kwargs)
        return timed_call("ANTIGRAVITY_MS", function, self, *args, **kwargs)
    return wrapped


@contextmanager
def external_stage(name):
    """Explicit measurement hook, NOT a claim that browser activity was captured."""
    if name not in EXTERNAL_STAGES:
        raise ValueError("Unknown external stage")
    if _active.get() is None:
        raise RuntimeError("An explicit telemetry_session is required")
    with _active.get().stage(name):
        yield


def summarize(paths, job_id=None):
    """Partial logs remain useful. Unknown external activity is never reported as zero."""
    events, malformed = [], 0
    for path in sorted(map(Path, paths)):
        file_events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("Not an event")
                file_events.append(item)
            except (ValueError, TypeError):
                malformed += 1
        if job_id is None or any(e.get("job_id") == job_id for e in file_events):
            events.extend(file_events)
    starts = {e["span_id"]: e for e in events if e.get("event") == "stage_started"}
    finishes = {e["span_id"]: e for e in events if e.get("event") == "stage_finished"}
    counters = {name: 0 for name in sorted(COUNTERS)}
    for e in events:
        if e.get("event") == "counter" and e.get("name") in counters:
            counters[e["name"]] += e["amount"]
    stages = {}
    for e in finishes.values():
        stage = stages.setdefault(e["name"], {"calls": 0, "duration_ms": 0, "errors": 0})
        stage["calls"] += 1
        stage["duration_ms"] += e["duration_ms"]
        stage["errors"] += e["status"] == "ERROR"
    active_ms = sum(e["duration_ms"] for e in finishes.values() if not e.get("parent_id"))
    begun = [e["started_at"] for e in starts.values() if e["name"] == "CREATIVE_MS"]
    completed = [e["at"] for e in events if e.get("event") == "job_state" and e.get("state") == "PACKAGE_READY"]
    # A meaningful job total requires one job and a complete observed lifecycle.
    total_ms = None
    jobs = {e.get("job_id") for e in events if e.get("job_id")}
    if len(jobs) == 1 and len(begun) == 1 and completed:
        total_ms = (datetime.fromisoformat(max(completed)) - datetime.fromisoformat(min(begun))).total_seconds() * 1000
    return {"job_id": job_id, "stages": stages, "recorded_counters": counters,
            "counter_scope": "OBSERVED_EVENTS_ONLY; absent external events are UNKNOWN, not zero usage",
            "external_actual_counts": "UNKNOWN", "cost_status": "COST_UNKNOWN", "cost": None,
            "TOTAL_JOB_MS": total_ms, "ACTIVE_OPERATIONS_MS": active_ms,
            "incomplete_spans": len(starts.keys() - finishes.keys()),
            "malformed_lines": malformed,
            "note": "Nested durations overlap; do not sum stage totals. No automatic retry or billing inference."}
