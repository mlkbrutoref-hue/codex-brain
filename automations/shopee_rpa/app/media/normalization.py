"""Technical normalization only. Logical identity survives reencoding."""
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path
import subprocess
import uuid
from app.media.ffmpeg.locator import FFmpegLocator
from app.media.identity import MediaIdentity, file_sha256
from app.media.provenance import MediaProvenance
from app.operational.config import MediaProfile
from app.operational.deadlines import ExecutionDeadline
from app.validation.media import FFprobeInspector


@dataclass(frozen=True)
class PreparedMedia:
    path: str
    identity: MediaIdentity
    provenance: MediaProvenance
    quality: str
    technical_metadata: dict


class MediaProcessor:
    def __init__(self, locator=None, deadline=None):
        self.locator = locator or FFmpegLocator(project_dir=Path(__file__).resolve().parents[2])
        self.deadline = deadline or ExecutionDeadline(900)

    def _probe(self, path):
        return FFprobeInspector(self.locator.require('ffprobe'), self.deadline.child_timeout(30)).probe(path)

    def inspect(self, path, profile=None):
        profile = profile or MediaProfile()
        probe = self._probe(path)
        valid = (probe.width, probe.height) in ((profile.width, profile.height), (profile.fallback_width, profile.fallback_height))
        # The operator permits square/landscape videos. Preserve their aspect
        # ratio; technical QA still requires at least 720 pixels on the short side.
        if profile.allow_landscape and probe.width >= probe.height:
            valid = profile.fallback_width <= probe.height <= probe.width <= profile.height
        valid = valid and profile.min_duration <= probe.duration_seconds <= profile.max_duration and Path(path).stat().st_size <= profile.max_bytes
        valid = valid and probe.video_codec == 'h264' and (not profile.require_audio or probe.has_audio) and probe.audio_codec in (None, 'aac')
        valid = valid and 0 < probe.fps <= 60 and (profile.fps is None or abs(probe.fps - profile.fps) < .1)
        if Path(path).suffix.lower() != '.mp4' or 'mp4' not in probe.container_format.split(',') or not valid:
            raise ValueError('MEDIA_PROFILE_FAILED')
        # Full decode catches corruption metadata-only inspection misses.
        done = subprocess.run([str(self.locator.require('ffmpeg')), '-v', 'error', '-xerror', '-i', str(path),
            '-f', 'null', '-'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=self.deadline.child_timeout(120), shell=False)
        if done.returncode:
            raise ValueError('MEDIA_DECODE_FAILED')
        self.deadline.raise_if_expired()
        return probe

    def prepare_for_upload(self, input_path, output_path, profile=None, *, logical_asset_id,
                           provenance=None, campaign_id='', generation_id=''):
        profile = profile or MediaProfile()
        source, target = Path(input_path).resolve(), Path(output_path).resolve()
        if source == target or target.exists() or target.suffix.lower() != '.mp4':
            raise ValueError('SOURCE_OR_EXISTING_OUTPUT_MUST_NOT_BE_OVERWRITTEN')
        before = self._probe(source)
        if (before.width >= before.height and not profile.allow_landscape) or not profile.min_duration <= before.duration_seconds <= profile.max_duration:
            raise ValueError('SOURCE_ORIENTATION_OR_DURATION_REQUIRES_REVIEW')
        source_hash = file_sha256(source)
        width, height = (profile.width, profile.height) if before.width >= profile.width else (profile.fallback_width, profile.fallback_height)
        landscape = before.width >= before.height
        if landscape:
            height = profile.fallback_width
            width = 2 * round(height * before.width / before.height / 2)
            if width > profile.height:
                raise ValueError('SOURCE_ASPECT_RATIO_REQUIRES_REVIEW')
        fps = profile.fps or before.fps
        if not 0 < fps <= 60:
            raise ValueError('SOURCE_FPS_REQUIRES_REVIEW')
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.stem + '.' + uuid.uuid4().hex + '.partial.mp4')
        sidecar = target.with_suffix('.provenance.json')
        if sidecar.exists():
            raise ValueError('EXISTING_PROVENANCE_MUST_NOT_BE_OVERWRITTEN')
        try:
            command = [str(self.locator.require('ffmpeg')), '-v', 'error', '-n', '-i', str(source),
                '-map', '0:v:0', '-map', '0:a:0?', '-vf',
                f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-c:v', 'libx264', '-preset', 'veryfast', '-threads', '2', '-pix_fmt', 'yuv420p', '-r', str(fps), '-c:a', 'aac', '-movflags', '+faststart', str(partial)]
            done = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                timeout=self.deadline.child_timeout(600), shell=False)
            if done.returncode:
                raise ValueError('NORMALIZATION_FAILED')
            after = self.inspect(partial, profile)
            if abs(before.duration_seconds - after.duration_seconds) > .25:
                raise ValueError('NORMALIZATION_CHANGED_DURATION')
            if file_sha256(source) != source_hash:
                raise ValueError('SOURCE_CHANGED_DURING_NORMALIZATION')
            identity = MediaIdentity(logical_asset_id, source_hash, file_sha256(partial), campaign_id, generation_id)
            metadata = asdict(after)
            metadata['path'] = str(target)
            result = PreparedMedia(str(target), identity, provenance or MediaProvenance(), 'PASS', metadata)
            # Exclusive creation prevents concurrent output overwrite; originals remain untouched.
            os.link(partial,target)
            with sidecar.open('x',encoding='utf-8') as stream:
                stream.write(json.dumps(asdict(result),ensure_ascii=False,indent=2))
                stream.flush()
                os.fsync(stream.fileno())
            return result
        finally:
            partial.unlink(missing_ok=True)
