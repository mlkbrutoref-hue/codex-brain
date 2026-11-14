"""Shared safe export primitive that avoids unnecessary transcoding."""
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tempfile


@dataclass(frozen=True)
class PlatformExportResult:
    platform: str
    path: str
    method: str


def hardlink_or_copy(source: Path, destination: Path, platform: str) -> PlatformExportResult:
    source = Path(source)
    destination = Path(destination)
    if not source.is_file() or source.stat().st_size == 0:
        raise FileNotFoundError("Master video is missing or empty")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".export-", suffix=destination.suffix,
                                           dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    temporary.unlink()
    method = "hardlink"
    try:
        os.link(source, temporary)
    except OSError:
        method = "copy"
        shutil.copy2(source, temporary)
    os.replace(temporary, destination)
    return PlatformExportResult(platform=platform, path=str(destination), method=method)
