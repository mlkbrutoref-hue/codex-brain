"""Centralized, configurable discovery of FFmpeg and ffprobe executables."""
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
from typing import Iterable, Optional


class FFmpegNotFoundError(RuntimeError):
    """Raised when a required native media executable cannot be resolved."""


@dataclass(frozen=True)
class FFmpegToolchain:
    ffmpeg: Optional[Path]
    ffprobe: Optional[Path]

    @property
    def complete(self) -> bool:
        return self.ffmpeg is not None and self.ffprobe is not None


class FFmpegLocator:
    """Resolves configured paths, system PATH, then project-local tool directories."""

    def __init__(self, project_dir: Optional[Path] = None, local_bin_dir: Optional[Path] = None):
        self.project_dir = Path(project_dir).resolve() if project_dir else None
        self.local_bin_dir = Path(local_bin_dir).resolve() if local_bin_dir else None

    @staticmethod
    def _executable_names(tool: str) -> Iterable[str]:
        return (f"{tool}.exe", tool) if os.name == "nt" else (tool, f"{tool}.exe")

    @staticmethod
    def _configured_candidate(value: Optional[str], tool: str) -> Iterable[Path]:
        if not value:
            return ()
        configured = Path(value).expanduser()
        if configured.is_dir():
            return tuple(configured / name for name in FFmpegLocator._executable_names(tool))
        return (configured,)

    def _local_candidates(self, tool: str) -> Iterable[Path]:
        roots = []
        if self.local_bin_dir:
            roots.append(self.local_bin_dir)
        if self.project_dir:
            roots.extend((
                self.project_dir / "tools" / "ffmpeg" / "bin",
                self.project_dir / "tools" / "ffmpeg",
            ))
        for root in roots:
            for name in self._executable_names(tool):
                yield root / name

    def resolve(self, tool: str) -> Optional[Path]:
        if tool not in {"ffmpeg", "ffprobe"}:
            raise ValueError("tool must be ffmpeg or ffprobe")
        env_name = "FFMPEG_PATH" if tool == "ffmpeg" else "FFPROBE_PATH"
        for candidate in self._configured_candidate(os.environ.get(env_name), tool):
            if candidate.is_file():
                return candidate.resolve()
        from_path = shutil.which(tool)
        if from_path and Path(from_path).is_file():
            return Path(from_path).resolve()
        for candidate in self._local_candidates(tool):
            if candidate.is_file():
                return candidate.resolve()
        return None

    def locate(self) -> FFmpegToolchain:
        return FFmpegToolchain(ffmpeg=self.resolve("ffmpeg"), ffprobe=self.resolve("ffprobe"))

    def require(self, tool: str) -> Path:
        resolved = self.resolve(tool)
        if resolved is None:
            env_name = "FFMPEG_PATH" if tool == "ffmpeg" else "FFPROBE_PATH"
            raise FFmpegNotFoundError(
                f"{tool} not found. Install FFmpeg from a trusted distribution and set {env_name}, "
                "add its bin directory to PATH, or place it under tools/ffmpeg/bin."
            )
        return resolved
