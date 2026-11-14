"""Content-addressed local checkpoints; no inferred approval or provider access."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
from app.core.telemetry import count


def digest(path):
    path = Path(path)
    if not path.is_file():
        return None
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def fingerprint(paths):
    return {str(Path(path)): digest(path) for path in paths}


def read_json(path, default=None):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else default
    except (OSError, ValueError):
        return default


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".checkpoint-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def exclusive(path):
    """An interrupted lock requires inspection, never a silent paid retry."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError("Operation locked; inspect prior attempt before resuming") from None
    try:
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


class ArtifactCache:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / "resume_index.json"
        self.records = read_json(self.path, {})
        self.changed = False

    def valid(self, name, dependencies, outputs):
        record = self.records.get(name, {})
        actual = fingerprint(outputs)
        return (bool(actual) and all(actual.values()) and
                record.get("dependencies") == fingerprint(dependencies) and
                record.get("outputs") == actual)

    def save(self, name, dependencies, outputs):
        self.records[name] = {"dependencies": fingerprint(dependencies), "outputs": fingerprint(outputs)}
        atomic_json(self.path, self.records)

    def use(self, name, dependencies, outputs, build, load, validate, *, adopt=False):
        hit = self.valid(name, dependencies, outputs)
        legacy = adopt and name not in self.records and not self.changed
        if hit or legacy:
            try:
                value = load()
                if validate(value):
                    if legacy:
                        self.save(name, dependencies, outputs)
                    count("resume_skips")
                    return value
            except (OSError, ValueError, TypeError, KeyError, AttributeError):
                pass
        value = build()
        if not validate(value):
            raise ValueError(f"Invalid artifact: {name}")
        self.save(name, dependencies, outputs)
        self.changed = True
        count("creative_rebuilds")
        return value
