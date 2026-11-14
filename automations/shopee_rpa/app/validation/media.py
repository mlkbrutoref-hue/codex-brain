"""Technical media inspection through ffprobe, separate from semantic visual review."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from fractions import Fraction
import json
from pathlib import Path
import subprocess
from typing import Dict, List, Optional


class TechnicalQAStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass(frozen=True)
class MediaProbe:
    path: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    video_codec: str
    audio_codec: Optional[str]
    container_format: str = ""

    @property
    def has_audio(self) -> bool:
        return self.audio_codec is not None


@dataclass(frozen=True)
class TechnicalQAResult:
    path: str
    status: TechnicalQAStatus
    exists: bool
    non_empty: bool
    probe_executed: bool
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class FFprobeInspector:
    """Runs ffprobe without a shell and converts its JSON into typed media facts."""

    def __init__(self, binary: Path | str, timeout: float = 30.0):
        self.binary = str(binary)
        self.timeout = timeout

    def build_command(self, path: Path) -> List[str]:
        return [
            self.binary, "-v", "error", "-show_entries",
            "stream=codec_type,codec_name,width,height,avg_frame_rate:format=duration,format_name",
            "-of", "json", str(Path(path)),
        ]

    @staticmethod
    def _fps(value: object) -> float:
        if not value or value == "0/0":
            return 0.0
        try:
            return float(Fraction(str(value)))
        except (ValueError, ZeroDivisionError):
            return 0.0

    def probe(self, path: Path) -> MediaProbe:
        path = Path(path)
        completed = subprocess.run(
            self.build_command(path),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=self.timeout,
            shell=False,
        )
        if completed.returncode != 0:
            raise RuntimeError("ffprobe could not read the media file")
        try:
            payload = json.loads(completed.stdout)
            streams = payload["streams"]
            video = next(stream for stream in streams if stream.get("codec_type") == "video")
            audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
            duration = float(payload["format"]["duration"])
            width = int(video["width"])
            height = int(video["height"])
            fps = self._fps(video.get("avg_frame_rate"))
            codec = str(video["codec_name"])
        except (KeyError, TypeError, ValueError, StopIteration, json.JSONDecodeError) as exc:
            raise RuntimeError("ffprobe returned incomplete media metadata") from None
        if width <= 0 or height <= 0 or fps <= 0 or duration <= 0 or not codec:
            raise RuntimeError("ffprobe returned invalid media metadata")
        return MediaProbe(
            path=str(path), width=width, height=height, fps=fps,
            duration_seconds=duration, video_codec=codec,
            audio_codec=(str(audio.get("codec_name")) if audio else None),
            container_format=str(payload["format"].get("format_name", "")),
        )


class TechnicalMediaValidator:
    """Validates observable media properties; it makes no semantic visual claim."""

    def __init__(self, inspector: Optional[FFprobeInspector]):
        self.inspector = inspector

    def validate(
        self,
        path: Path,
        *,
        expected_width: Optional[int] = None,
        expected_height: Optional[int] = None,
        expected_fps: Optional[float] = None,
        expected_video_codec: Optional[str] = None,
        allowed_audio_codecs: Optional[set[str]] = None,
    ) -> TechnicalQAResult:
        path = Path(path)
        exists = path.is_file()
        non_empty = exists and path.stat().st_size > 0
        if not exists or not non_empty:
            return TechnicalQAResult(
                path=str(path), status=TechnicalQAStatus.FAIL,
                exists=exists, non_empty=non_empty, probe_executed=False,
                issues=["FILE_MISSING" if not exists else "FILE_EMPTY"],
            )
        if self.inspector is None:
            return TechnicalQAResult(
                path=str(path), status=TechnicalQAStatus.NOT_EXECUTED,
                exists=True, non_empty=True, probe_executed=False,
                issues=["FFPROBE_NOT_FOUND"],
            )
        try:
            probe = self.inspector.probe(path)
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            return TechnicalQAResult(
                path=str(path), status=TechnicalQAStatus.FAIL,
                exists=True, non_empty=True, probe_executed=True,
                issues=["PROBE_FAILED"],
            )

        issues: List[str] = []
        if expected_width is not None and probe.width != expected_width:
            issues.append("WIDTH_MISMATCH")
        if expected_height is not None and probe.height != expected_height:
            issues.append("HEIGHT_MISMATCH")
        if expected_fps is not None and abs(probe.fps - expected_fps) > 0.1:
            issues.append("FPS_MISMATCH")
        if expected_video_codec is not None and probe.video_codec != expected_video_codec:
            issues.append("VIDEO_CODEC_MISMATCH")
        if probe.audio_codec is not None and allowed_audio_codecs is not None:
            if probe.audio_codec not in allowed_audio_codecs:
                issues.append("AUDIO_CODEC_MISMATCH")
        return TechnicalQAResult(
            path=str(path), status=TechnicalQAStatus.FAIL if issues else TechnicalQAStatus.PASS,
            exists=True, non_empty=True, probe_executed=True,
            width=probe.width, height=probe.height, fps=probe.fps,
            duration_seconds=probe.duration_seconds, video_codec=probe.video_codec,
            audio_codec=probe.audio_codec, issues=issues,
        )
