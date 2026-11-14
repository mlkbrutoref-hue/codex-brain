"""Deterministic discovery and basic integrity checks for generated video takes."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


@dataclass(frozen=True)
class TakeInventory:
    ordered_takes: List[Path] = field(default_factory=list)
    missing_scenes: List[int] = field(default_factory=list)
    empty_files: List[str] = field(default_factory=list)
    invalid_extensions: List[str] = field(default_factory=list)
    corrupt_files: List[str] = field(default_factory=list)
    duplicate_scenes: List[int] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not (
            self.missing_scenes or self.empty_files or self.invalid_extensions
            or self.corrupt_files or self.duplicate_scenes
        ) and bool(self.ordered_takes)


def _has_known_container_signature(path: Path) -> bool:
    try:
        header = path.read_bytes()[:32]
    except OSError:
        return False
    suffix = path.suffix.lower()
    if suffix in {".mp4", ".mov"}:
        return len(header) >= 12 and header[4:8] == b"ftyp"
    if suffix in {".mkv", ".webm"}:
        return header.startswith(b"\x1aE\xdf\xa3")
    return False


def inspect_take_inventory(generated_dir: Path, expected_scene_count: int) -> TakeInventory:
    if expected_scene_count < 1:
        raise ValueError("expected_scene_count must be positive")
    generated_dir = Path(generated_dir)
    if not generated_dir.is_dir():
        return TakeInventory(missing_scenes=list(range(1, expected_scene_count + 1)))

    ordered: List[Path] = []
    missing: List[int] = []
    empty: List[str] = []
    invalid: List[str] = []
    corrupt: List[str] = []
    duplicates: List[int] = []

    for scene in range(1, expected_scene_count + 1):
        stem = f"take_{scene:02d}"
        matches = sorted(path for path in generated_dir.glob(f"{stem}.*") if path.is_file())
        supported = [path for path in matches if path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS]
        invalid.extend(path.name for path in matches if path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS)
        if not supported:
            missing.append(scene)
            continue
        if len(supported) > 1:
            duplicates.append(scene)
            continue
        take = supported[0]
        if take.stat().st_size == 0:
            empty.append(take.name)
            continue
        if not _has_known_container_signature(take):
            corrupt.append(take.name)
            continue
        ordered.append(take)

    return TakeInventory(
        ordered_takes=ordered,
        missing_scenes=missing,
        empty_files=empty,
        invalid_extensions=invalid,
        corrupt_files=corrupt,
        duplicate_scenes=duplicates,
    )
