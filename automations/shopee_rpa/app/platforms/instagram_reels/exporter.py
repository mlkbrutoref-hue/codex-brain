"""Instagram Reels export from an already compliant master."""
from pathlib import Path
from app.platforms.common import PlatformExportResult, hardlink_or_copy


class InstagramReelsExporter:
    def export(self, master: Path, job_dir: Path) -> PlatformExportResult:
        return hardlink_or_copy(master, Path(job_dir) / "platforms" / "instagram.mp4", "instagram")
