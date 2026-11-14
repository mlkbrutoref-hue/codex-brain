from dataclasses import dataclass, field
from enum import Enum
import math
import os
from pathlib import Path


class FeatureMode(str, Enum):
    DRY_RUN = 'DRY_RUN'
    ASSISTED_MODE = 'ASSISTED_MODE'
    LIVE_PUBLISH = 'LIVE_PUBLISH'


class ActionType(str, Enum):
    READ_STATE = 'READ_STATE'
    CLICK = 'CLICK'
    SCROLL = 'SCROLL'
    NAVIGATION = 'NAVIGATION'
    PRODUCT_LOOKUP = 'PRODUCT_LOOKUP'
    MEDIA_SELECT = 'MEDIA_SELECT'
    UPLOAD_START = 'UPLOAD_START'
    PUBLISH_ATTEMPT = 'PUBLISH_ATTEMPT'


@dataclass(frozen=True)
class OperationalLimits:
    posts_per_day: int = 1
    posts_per_session: int = 1
    uploads_per_day: int = 1
    uploads_per_session: int = 1
    product_views_session: int = 5
    affiliate_requests_day: int = 30
    affiliate_requests_session: int = 10
    actions_worker: int = 500

    def __post_init__(self):
        if any(type(v) is not int or v < 0 for v in vars(self).values()):
            raise ValueError('INVALID_OPERATIONAL_LIMIT')


@dataclass(frozen=True)
class MediaProfile:
    width: int = 1080
    height: int = 1920
    fallback_width: int = 720
    fallback_height: int = 1280
    fps: float | None = None
    min_duration: float = 1
    max_duration: float = 180
    max_bytes: int = 100_000_000
    require_audio: bool = True
    allow_landscape: bool = True

    def __post_init__(self):
        if type(self.allow_landscape) is not bool:
            raise ValueError('INVALID_MEDIA_PROFILE')
        if min(self.width, self.height, self.fallback_width, self.fallback_height, self.max_bytes) <= 0:
            raise ValueError('INVALID_MEDIA_PROFILE')
        if not 0 < self.min_duration <= self.max_duration or (self.fps is not None and not 0 < self.fps <= 60):
            raise ValueError('INVALID_MEDIA_PROFILE')


def shared_store_path():
    # Independent of job root and Android serial. Override once at deployment level.
    override = os.environ.get('COMMERCE_OPERATIONAL_DB')
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise ValueError('SHARED_DB_MUST_BE_ABSOLUTE')
        return path
    base = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local/share')))
    return base / 'AICommerceContentFactory/operational/state.sqlite3'


@dataclass(frozen=True)
class OperationalConfig:
    mode: FeatureMode = FeatureMode.DRY_RUN
    limits: OperationalLimits = field(default_factory=OperationalLimits)
    media_profile: MediaProfile = field(default_factory=MediaProfile)
    max_tokens: float = 200
    refill_rate: float = 1
    action_costs: dict = field(default_factory=lambda: dict(zip(ActionType, (.25, 1, 2, 3, 3, 5, 10, 20))))
    session_seconds: float = 900
    rpc_seconds: float = 15
    approval_ttl: float = 1800
    authorization_ttl: float = 10
    dedup_window: float = 30 * 86400
    breaker_threshold: int = 2
    cooldown_seconds: float = 900
    timezone: str = 'America/Sao_Paulo'
    allowed_app_versions: tuple[str, ...] = ()
    ui_pixel_fallback: bool = False

    def __post_init__(self):
        values = (self.max_tokens, self.refill_rate, self.session_seconds, self.rpc_seconds,
                  self.approval_ttl, self.authorization_ttl, self.dedup_window, self.cooldown_seconds)
        if any(not math.isfinite(v) or v <= 0 for v in values) or self.breaker_threshold < 1:
            raise ValueError('INVALID_OPERATIONAL_CONFIG')
        if set(self.action_costs) != set(ActionType) or any(not math.isfinite(v) or v <= 0 for v in self.action_costs.values()):
            raise ValueError('INVALID_ACTION_COSTS')

    @classmethod
    def from_dict(cls, data=None):
        data = dict(data or {})
        # Storage location is deployment-wide, never controlled by a job JSON.
        if 'store_path' in data:
            raise ValueError('JOB_CANNOT_OVERRIDE_SHARED_STORE')
        data['mode'] = FeatureMode(data.get('mode', 'DRY_RUN'))
        data['limits'] = OperationalLimits(**data.get('limits', {}))
        data['media_profile'] = MediaProfile(**data.get('media_profile', {}))
        if 'action_costs' in data:
            data['action_costs'] = {ActionType(k): v for k, v in data['action_costs'].items()}
        if 'allowed_app_versions' in data:
            data['allowed_app_versions'] = tuple(data['allowed_app_versions'])
        return cls(**data)
