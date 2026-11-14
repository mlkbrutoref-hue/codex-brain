"""Generate tiny, local-only video takes for engineering validation."""
import os
from pathlib import Path
import subprocess
from typing import List

from app.media.ffmpeg.locator import FFmpegLocator


class SyntheticTakeFactory:
    COLORS = ("red", "green", "blue", "yellow")

    def __init__(self, locator: FFmpegLocator, timeout: float = 60.0):
        self.binary = str(locator.require("ffmpeg"))
        self.timeout = timeout

    def build_command(self, output: Path, index: int, duration: float = 0.5,
                      with_audio: bool = False) -> List[str]:
        color = self.COLORS[(index - 1) % len(self.COLORS)]
        command = [
            self.binary, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"color=c={color}:s=270x480:r=30:d={duration}",
        ]
        if with_audio:
            command += ["-f", "lavfi", "-i", f"sine=frequency={300 + index * 100}:duration={duration}"]
        command += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30"]
        command += ["-c:a", "aac", "-shortest"] if with_audio else ["-an"]
        command.append(str(output))
        return command

    def generate(self, output_dir: Path, count: int = 4) -> List[Path]:
        if count <= 0:
            raise ValueError("count must be positive")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for index in range(1, count + 1):
            destination = output_dir / f"take_{index:02d}.mp4"
            partial = destination.with_name(destination.stem + ".partial.mp4")
            try:
                completed = subprocess.run(
                    self.build_command(partial, index, with_audio=index % 2 == 0),
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE, text=True, timeout=self.timeout, shell=False,
                )
                if completed.returncode != 0 or not partial.is_file() or partial.stat().st_size == 0:
                    raise RuntimeError("Synthetic FFmpeg generation failed; details omitted")
                os.replace(partial, destination)
                results.append(destination)
            finally:
                partial.unlink(missing_ok=True)
        return results
