"""Explicit operator acceptance of listing reuse; never a third-party license."""
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit
import re


def listing_reuse_approval(candidate, now):
    c=candidate
    try:
        reference=c.listing_reuse_review
        raw=Path(reference['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=reference['sha256']:
            return None
        proof=json.loads(raw)
        source_raw=Path(c.provenance.evidence_reference).read_bytes()
        if hashlib.sha256(source_raw).hexdigest()!=c.provenance.source_evidence_sha256:
            return None
        source=json.loads(source_raw)
        auth=Path(proof['authorization_reference']).read_bytes()
        identity=re.search(r'(?:/product/(\d+)/(\d+)|-i\.(\d+)\.(\d+))$',urlsplit(c.provenance.source_url).path)
        ids=tuple(v for v in identity.groups() if v) if identity else ()
        caption_hash=hashlib.sha256(json.dumps([c.caption,c.hashtags],ensure_ascii=False).encode()).hexdigest()
        valid=(isinstance(proof,dict) and isinstance(source,dict) and proof['status']=='OPERATOR_ACCEPTED_LISTING_REUSE'
            and proof['reviewer'] and hashlib.sha256(auth).hexdigest()==proof['authorization_sha256']
            and proof['account_id']==c.account_id and proof['logical_asset_id']==c.media.logical_asset_id
            and proof['source_sha256']==c.media.source_asset_hash and proof['prepared_sha256']==c.media.prepared_asset_hash
            and proof['shop_id']==c.product.shop_id and proof['item_id']==c.product.item_id
            and proof['caption_sha256']==caption_hash and proof['allow_rights_unknown'] is True
            and proof['interaction_scope']=='shopee_video_android_interaction'
            and all(type(proof[k]) in (int,float) and math.isfinite(proof[k]) for k in ('reviewed_at','expires_at'))
            and proof['reviewed_at']<=now<proof['expires_at'] and proof['expires_at']-proof['reviewed_at']<=86400
            and c.provenance.source_type=='PLATFORM_PROVIDED' and c.provenance.source_category=='PRODUCT_LISTING_SOURCE'
            and c.provenance.source_match=='PASS' and ids==(c.product.shop_id,c.product.item_id)
            and urlsplit(c.provenance.source_url).hostname=='shopee.com.br'
            and source.get('reviewer') and source.get('media_sha256')==c.media.prepared_asset_hash
            and source.get('shop_id')==c.product.shop_id and source.get('item_id')==c.product.item_id
            and source.get('source_match')=='PASS' and source.get('product_match')=='PASS')
        if c.product.variant_id or c.product.attributes:
            valid=valid and proof.get('variant_id')==c.product.variant_id and proof.get('attributes')==c.product.attributes
        else:
            valid=valid and proof.get('product_scope')=='BASE_PRODUCT_ALL_COLOURS'
        return proof if valid else None
    except (OSError,KeyError,TypeError,ValueError,AttributeError):
        return None
