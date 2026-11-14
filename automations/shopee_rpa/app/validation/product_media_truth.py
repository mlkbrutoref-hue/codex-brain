from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import json
import re
import time
import unicodedata
from app.media.identity import MediaIdentity
from app.media.provenance import MediaProvenance, RightsStatus


class CheckStatus(str, Enum):
    PASS = 'PASS'
    REVIEW = 'REVIEW'
    FAIL = 'FAIL'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class ProductIdentity:
    shop_id: str
    item_id: str
    variant_id: str | None = None
    attributes: dict = field(default_factory=dict)

    def valid(self):
        return all(isinstance(v, str) and re.fullmatch(r'[1-9]\d*', v) for v in (self.shop_id, self.item_id))


@dataclass(frozen=True)
class ExpectedAccount:
    account_id: str
    username: str
    stable_profile_marker: str


@dataclass(frozen=True)
class HumanReview:
    fingerprint: str
    timestamp: float
    reviewer: str
    status: str = 'REVIEW'
    evidence_reference: str = ''


@dataclass(frozen=True)
class PostCandidate:
    account_id: str
    media: MediaIdentity
    product: ProductIdentity
    product_title: str
    caption: str
    hashtags: tuple[str, ...]
    provenance: MediaProvenance
    media_quality: str = 'UNKNOWN'
    media_quality_hash: str = ''
    media_product_match: str = 'UNKNOWN'
    caption_review: str = 'UNKNOWN'
    originality: str = 'UNKNOWN'
    ai_disclosure: bool = False
    human_review: HumanReview | None = None
    keywords: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    listing_reuse_review: dict = field(default_factory=dict)

    def __post_init__(self):
        if type(self.ai_disclosure) is not bool:
            raise ValueError('AI_DISCLOSURE_MUST_BE_BOOLEAN')

    def fingerprint(self):
        value = asdict(self)
        value.pop('human_review')
        return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data['media'] = MediaIdentity(**data['media'])
        data['product'] = ProductIdentity(**data['product'])
        data['provenance'] = MediaProvenance(**data.get('provenance', {}))
        if data.get('human_review'):
            data['human_review'] = HumanReview(**data['human_review'])
        for name in ('hashtags', 'keywords', 'aliases'):
            data[name] = tuple(data.get(name, ()))
        return cls(**data)


@dataclass(frozen=True)
class ValidationReport:
    status: CheckStatus
    reasons: list[str]
    checks: dict[str, str]


def normalized_terms(text):
    value = ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))
    return set(re.findall(r'\w+', value))


class ContentValidator:
    def __init__(self, config, clock=time.time):
        self.config, self.clock = config, clock

    def validate(self, candidate, *, observed_product=None, duplicate=False):
        c = candidate
        checks = {}
        checks['account'] = 'PASS' if c.account_id else 'FAIL'
        checks['product_identity'] = 'PASS' if c.product.valid() else 'FAIL'
        if observed_product is not None and c.product != observed_product:
            checks['product_identity'] = 'FAIL'
        checks['variant_match'] = 'PASS' if not c.product.attributes or c.product.variant_id else 'REVIEW'
        checks['media_product_match'] = c.media_product_match
        lexical = any(normalized_terms(term) <= normalized_terms(c.caption) for term in c.keywords + c.aliases if normalized_terms(term))
        checks['caption_relevance'] = 'PASS' if lexical and c.caption_review == 'PASS' else ('FAIL' if c.caption_review == 'FAIL' else 'REVIEW')
        checks['media_uniqueness'] = 'FAIL' if duplicate else 'PASS'
        checks['media_quality'] = 'PASS' if c.media_quality == 'PASS' and c.media_quality_hash == c.media.prepared_asset_hash else ('FAIL' if c.media_quality == 'FAIL' else 'REVIEW')
        checks['rights'] = 'PASS' if c.provenance.rights_status == RightsStatus.VERIFIED and c.provenance.evidence_reference and c.provenance.license_type else 'FAIL'
        checks['originality'] = c.originality
        checks['ai_disclosure'] = ('REVIEW' if c.provenance.ai_generated is None else
            ('PASS' if not (c.provenance.ai_generated or c.provenance.ai_disclosure_required) or c.ai_disclosure else 'FAIL'))
        acceptance=self.operator_listing_approval(c)
        if acceptance:
            # This reports an operator exception, not verified rights/originality/AI.
            if c.provenance.rights_status==RightsStatus.UNKNOWN:
                checks['rights']='OPERATOR_ACCEPTED'
            if c.originality=='UNKNOWN' and acceptance.get('allow_listing_originality_unknown') is True:
                checks['originality']='OPERATOR_ACCEPTED'
            if c.provenance.ai_generated is None and not c.provenance.ai_disclosure_required and acceptance.get('allow_ai_unknown') is True:
                checks['ai_disclosure']='OPERATOR_ACCEPTED'
        review = c.human_review
        valid = review and review.status == 'APPROVED' and review.reviewer and review.evidence_reference and review.fingerprint == c.fingerprint()
        valid = valid and 0 <= self.clock() - review.timestamp <= self.config.approval_ttl
        checks['human_review'] = 'PASS' if valid else 'REVIEW'
        # Unrecognized and UNKNOWN states never pass.
        checks = {k: v if v in ('PASS', 'FAIL','OPERATOR_ACCEPTED') else 'REVIEW' for k, v in checks.items()}
        status = CheckStatus.FAIL if 'FAIL' in checks.values() else (CheckStatus.REVIEW if 'REVIEW' in checks.values() else CheckStatus.PASS)
        return ValidationReport(status, [k + ':' + v for k, v in checks.items() if v != 'PASS'], checks)

    def operator_listing_approval(self,candidate):
        from app.validation.operator_listing_policy import listing_reuse_approval
        return listing_reuse_approval(candidate,self.clock())

    def validate_assisted(self, candidate, *, duplicate=False):
        """UI preparation only: never publication readiness or authorization.

        Unknown commercial rights/AI remain unknown. Product-listing source and
        exact media/product/observable attributes require hash-bound evidence.
        """
        from pathlib import Path
        from urllib.parse import urlsplit
        c = candidate
        # Preserve support for original/owned candidates already fully reviewed
        # under the strict publication contract. Unknown rights never use this path.
        strict = self.validate(c,duplicate=duplicate)
        if strict.status == CheckStatus.PASS and c.provenance.source:
            return strict
        proof = {}
        try:
            raw = Path(c.provenance.evidence_reference).read_bytes()
            if hashlib.sha256(raw).hexdigest() == c.provenance.source_evidence_sha256:
                loaded = json.loads(raw)
                proof = loaded if isinstance(loaded,dict) else {}
        except (OSError, ValueError, TypeError):
            pass
        identity = re.search(r'(?:/product/(\d+)/(\d+)|-i\.(\d+)\.(\d+))$', urlsplit(c.provenance.source_url).path)
        ids = tuple(v for v in identity.groups() if v) if identity else ()
        bound = bool(proof.get('reviewer') and proof.get('media_sha256') == c.media.prepared_asset_hash and
            proof.get('shop_id') == c.product.shop_id and proof.get('item_id') == c.product.item_id and
            ids == (c.product.shop_id, c.product.item_id) and urlsplit(c.provenance.source_url).hostname == 'shopee.com.br')
        attributes = proof.get('observed_attributes', {})
        variant = bound and isinstance(attributes,dict) and all(attributes.get(k) == v for k, v in c.product.attributes.items())
        variant = variant and (not c.product.variant_id or proof.get('variant_id') == c.product.variant_id)
        lexical = any(normalized_terms(term) <= normalized_terms(c.caption) for term in c.keywords + c.aliases if normalized_terms(term))
        checks = dict(account='PASS' if c.account_id else 'FAIL', product_identity='PASS' if c.product.valid() else 'FAIL',
            source_match='PASS' if bound and c.provenance.source_match == 'PASS' and proof.get('source_match') == 'PASS' and
                c.provenance.source_type == 'PLATFORM_PROVIDED' and c.provenance.source_category == 'PRODUCT_LISTING_SOURCE' else 'FAIL',
            media_product_match='PASS' if bound and c.media_product_match == 'PASS' and proof.get('product_match') == 'PASS' else 'FAIL',
            variant_match='PASS' if variant else 'REVIEW', media_uniqueness='FAIL' if duplicate else 'PASS',
            media_quality='PASS' if c.media_quality == 'PASS' and c.media_quality_hash == c.media.prepared_asset_hash else 'FAIL',
            caption_relevance='PASS' if lexical and c.caption_review == 'PASS' else 'REVIEW',
            rights='FAIL' if c.provenance.rights_status == RightsStatus.REJECTED else 'DEFERRED_TO_PUBLISH_GATE',
            ai_disclosure='DEFERRED_TO_PUBLISH_GATE', originality='DEFERRED_TO_PUBLISH_GATE', human_review='DEFERRED_TO_PUBLISH_GATE')
        required = {k:v for k,v in checks.items() if v != 'DEFERRED_TO_PUBLISH_GATE'}
        status = CheckStatus.FAIL if 'FAIL' in required.values() else (CheckStatus.REVIEW if 'REVIEW' in required.values() else CheckStatus.PASS)
        return ValidationReport(status, [k+':'+v for k,v in required.items() if v != 'PASS'], checks)
