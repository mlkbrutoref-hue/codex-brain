from dataclasses import dataclass
from enum import Enum


class RightsStatus(str, Enum):
    VERIFIED = 'VERIFIED'
    REVIEW = 'REVIEW'
    UNKNOWN = 'UNKNOWN'
    REJECTED = 'REJECTED'


@dataclass(frozen=True)
class MediaProvenance:
    source: str = ''
    source_url: str = ''
    license_type: str = ''
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    created_at: str = ''
    creator: str = ''
    generation_method: str = ''
    ai_generated: bool | None = False
    ai_disclosure_required: bool = False
    campaign_id: str = ''
    evidence_reference: str = ''
    source_type: str = ''
    source_category: str = ''
    source_match: str = 'UNKNOWN'
    source_evidence_sha256: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'rights_status', RightsStatus(self.rights_status))
        if (self.ai_generated is not None and type(self.ai_generated) is not bool) or type(self.ai_disclosure_required) is not bool:
            raise ValueError('AI_FLAGS_MUST_BE_BOOLEAN')
