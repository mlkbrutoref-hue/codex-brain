"""FFmpeg command builder and atomic master assembly."""
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from app.media.ffmpeg.locator import FFmpegLocator, FFmpegNotFoundError
from app.validation.media import FFprobeInspector, MediaProbe
from app.core.telemetry import count


@dataclass(frozen=True)
class FFmpegConfig:
    width: int = 1080
    height: int = 1920
    fps: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    audio_rate: int = 48000
    crf: int = 20
    preset: str = os.environ.get("FFMPEG_PRESET", "veryfast")


class FFmpegAssembler:
    def __init__(
        self,
        binary: Optional[str | Path] = None,
        config: Optional[FFmpegConfig] = None,
        inspector: Optional[FFprobeInspector] = None,
        project_dir: Optional[Path] = None,
    ):
        locator = FFmpegLocator(project_dir=project_dir)
        located = Path(binary) if binary else locator.resolve("ffmpeg")
        self.binary = str(located) if located else ""
        self.config = config or FFmpegConfig()
        if inspector is not None:
            self.inspector = inspector
        else:
            ffprobe = locator.resolve("ffprobe")
            self.inspector = FFprobeInspector(ffprobe) if ffprobe else None

    @property
    def is_available(self) -> bool:
        return bool(self.binary and self.inspector)

    def build_command(
        self,
        takes: List[Path],
        output: Path,
        probes: Optional[List[MediaProbe]] = None,
    ) -> List[str]:
        if not takes:
            raise ValueError("At least one take is required")
        if len({str(Path(t).resolve()) for t in takes}) != len(takes):
            raise ValueError("Duplicate takes are not allowed")
        if probes is not None and len(probes) != len(takes):
            raise ValueError("Probe count must match take count")
        if not self.binary:
            raise FFmpegNotFoundError("ffmpeg not found; configure FFMPEG_PATH or PATH")

        cfg = self.config
        command = [self.binary, "-hide_banner", "-loglevel", "error", "-y"]
        for take in takes:
            command += ["-i", str(Path(take))]

        silent_input_indexes = {}
        if probes is not None:
            for take_index, probe in enumerate(probes):
                if not probe.has_audio:
                    input_index = len(takes) + len(silent_input_indexes)
                    silent_input_indexes[take_index] = input_index
                    command += [
                        "-f", "lavfi", "-t", f"{probe.duration_seconds:.6f}",
                        "-i", f"anullsrc=channel_layout=stereo:sample_rate={cfg.audio_rate}",
                    ]

        filters = []
        concat_inputs = []
        for index in range(len(takes)):
            filters.append(
                f"[{index}:v]scale={cfg.width}:{cfg.height}:force_original_aspect_ratio=decrease,"
                f"pad={cfg.width}:{cfg.height}:(ow-iw)/2:(oh-ih)/2,"
                f"fps={cfg.fps},setsar=1,setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
            )
            audio_index = silent_input_indexes.get(index, index)
            duration = probes[index].duration_seconds if probes is not None else None
            trim = f",atrim=duration={duration:.6f}" if duration is not None else ""
            filters.append(
                f"[{audio_index}:a]aresample={cfg.audio_rate}{trim},asetpts=PTS-STARTPTS[a{index}]"
            )
            concat_inputs.append(f"[v{index}][a{index}]")
        filters.append("".join(concat_inputs) + f"concat=n={len(takes)}:v=1:a=1[v][a]")
        command += [
            "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
            "-c:v", cfg.video_codec, "-preset", cfg.preset, "-crf", str(cfg.crf),
            "-r", str(cfg.fps), "-c:a", cfg.audio_codec, "-ar", str(cfg.audio_rate),
            "-movflags", "+faststart", str(output),
        ]
        return command

    def assemble(self, takes: List[Path], master: Path, timeout: float = 900.0) -> Path:
        ordered = [Path(path) for path in takes]
        if any(not path.is_file() for path in ordered):
            raise FileNotFoundError("One or more input takes are missing")
        if any(path.stat().st_size == 0 for path in ordered):
            raise ValueError("One or more input takes are empty")
        if self.inspector is None:
            raise FFmpegNotFoundError("ffprobe is required to inspect input audio and duration")
        probes = [self.inspector.probe(path) for path in ordered]

        master = Path(master)
        master.parent.mkdir(parents=True, exist_ok=True)
        partial = master.with_name(master.stem + ".partial" + master.suffix)
        command = self.build_command(ordered, partial, probes)
        try:
            count("ffmpeg_encodes")
            completed = subprocess.run(
                command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, text=True, timeout=timeout, shell=False,
            )
            if completed.returncode != 0 or not partial.is_file() or partial.stat().st_size == 0:
                raise RuntimeError("FFmpeg assembly failed; details omitted")
            os.replace(partial, master)
            return master
        finally:
            partial.unlink(missing_ok=True)
