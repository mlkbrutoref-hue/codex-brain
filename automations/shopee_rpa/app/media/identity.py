from dataclasses import dataclass
import hashlib
from pathlib import Path
import re


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value) is not None


@dataclass(frozen=True)
class MediaIdentity:
    logical_asset_id: str
    source_asset_hash: str
    prepared_asset_hash: str
    campaign_id: str = ''
    generation_id: str = ''
    perceptual_hash: str | None = None
    embedding_reference: str | None = None

    def __post_init__(self):
        if not self.logical_asset_id or not valid_hash(self.source_asset_hash) or not valid_hash(self.prepared_asset_hash):
            raise ValueError('INVALID_MEDIA_IDENTITY')

    def duplicate_keys(self):
        return self.logical_asset_id, self.source_asset_hash, self.prepared_asset_hash
