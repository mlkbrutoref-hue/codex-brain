"""Local, evidence-driven handoff; UI actions are performed by an operator."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

QA_CHECKS = (
    "CORRECT_ACCOUNT", "CORRECT_PLATFORM", "CORRECT_MEDIA", "CORRECT_ORDER",
    "CORRECT_CAPTION", "CORRECT_CTA", "CORRECT_DISCLOSURE", "CORRECT_TIME", "PREVIEW_OK",
)
STATES = (
    "CONTENT_READY", "TIME_RECOMMENDATION", "OPEN_PHONE_LINK", "OPEN_TARGET_APP",
    "SELECT_CONTENT", "PREPARE_POST", "PRE_PUBLISH_QA", "STOP_BEFORE_FINAL_PUBLISH",
)


class TimeAdvisor(Protocol):
    def recommend_publish_time(self, **context) -> dict: ...


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def aware_datetime(value):
    dt = datetime.fromisoformat(value)
    if dt.utcoffset() is None:
        raise ValueError("Timestamp requires timezone")
    return dt


def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def recommendation(advisor, context):
    fallback = dict(recommended_time=None, confidence="INSUFFICIENT_DATA", samples=0,
                    reason="Analytics integration unavailable; operator must select time.", alternatives=[])
    if advisor is None:
        return fallback
    try:
        result = advisor.recommend_publish_time(**context)
        required = {"recommended_time", "confidence", "reason", "samples", "alternatives"}
        if not isinstance(result, dict) or not required <= result.keys():
            raise ValueError("Invalid recommendation contract")
        if result["recommended_time"] is not None:
            aware_datetime(result["recommended_time"])
        if result["confidence"] not in {"INSUFFICIENT_DATA", "LOW_CONFIDENCE", "MEDIUM_CONFIDENCE", "HIGH_CONFIDENCE"}:
            raise ValueError("Invalid confidence")
        if type(result["samples"]) is not int or result["samples"] < 0:
            raise ValueError("Invalid samples")
        if not isinstance(result["alternatives"], list) or not result["reason"]:
            raise ValueError("Invalid explanation")
        return result
    except Exception as exc:
        fallback["reason"] = f"Analytics unavailable ({type(exc).__name__}); operator must select time."
        return fallback


def prepare_session(manifest_path, *, platform, account, content_type, category,
                    caption, cta, disclosure, scheduled_at=None, asset_ids=None, advisor=None):
    if platform not in {"instagram", "tiktok"}:
        raise ValueError("Unsupported platform")
    if not all(isinstance(v, str) and v.strip() for v in (account, content_type, category)):
        raise ValueError("Account, content type and category are required")
    if not all(isinstance(v, str) for v in (caption, cta, disclosure)):
        raise ValueError("Copy must be explicit strings; empty means operator must verify not applicable")
    if scheduled_at:
        aware_datetime(scheduled_at)
    manifest_path = Path(manifest_path).resolve()
    manifest = read_json(manifest_path)
    assets = manifest["assets"]
    available = [a["asset_id"] for a in assets]
    if len(set(available)) != len(available):
        raise ValueError("Duplicate asset IDs")
    if asset_ids is not None:
        if len(set(asset_ids)) != len(asset_ids) or not set(asset_ids) <= set(available):
            raise ValueError("Unknown or duplicate selection")
        if manifest["kind"] == "CAROUSEL" and asset_ids != available:
            raise ValueError("Carousel requires every slide in manifest order")
        assets = [next(a for a in assets if a["asset_id"] == selected) for selected in asset_ids]
    if not assets:
        raise ValueError("No media selected")
    frozen = []
    for asset in assets:
        media = Path(asset["final_image"])
        qa = Path(asset["qa"])
        if not media.is_absolute():
            media = manifest_path.parent / media
        if not qa.is_absolute():
            qa = manifest_path.parent / qa
        report = read_json(qa)
        if asset["qa_status"] != "PASS" or report.get("status") != "PASS":
            raise ValueError(f"Content QA not PASS: {asset['asset_id']}")
        if report.get("asset_id") != asset["asset_id"]:
            raise ValueError("QA belongs to another asset")
        if sha256(media) != asset["sha256"]:
            raise ValueError("Media hash mismatch")
        frozen.append(dict(asset_id=asset["asset_id"], path=str(media.resolve()),
                           sha256=asset["sha256"], qa_path=str(qa.resolve()), qa_sha256=sha256(qa)))
    payload = dict(campaign_id=manifest["campaign_id"], platform=platform, account=account,
                   content_type=content_type, category=category, caption=caption, cta=cta,
                   disclosure=disclosure, scheduled_at=scheduled_at, assets=frozen,
                   manifest_path=str(manifest_path), manifest_sha256=sha256(manifest_path))
    rec = recommendation(advisor, {k: payload[k] for k in ("platform", "content_type", "category")})
    data = dict(schema_version=1, mode="ASSISTED_MODE", maturity="EXPERIMENTAL", state="CONTENT_READY",
                payload=payload, fingerprint=fingerprint(payload), recommendation=rec,
                qa={k: dict(status="UNKNOWN", evidence="") for k in QA_CHECKS}, history=[])
    return AssistedSession(data)


class AssistedSession:
    def __init__(self, data):
        self.data = data
        self.validate()

    def validate(self):
        data = self.data
        if data["mode"] != "ASSISTED_MODE" or data["state"] not in STATES:
            raise ValueError("Only assisted states allowed")
        if fingerprint(data["payload"]) != data["fingerprint"]:
            raise ValueError("Payload changed; create a new session and QA")
        payload = data["payload"]
        if sha256(payload["manifest_path"]) != payload["manifest_sha256"]:
            raise ValueError("Source manifest changed")
        for asset in payload["assets"]:
            if sha256(asset["path"]) != asset["sha256"] or sha256(asset["qa_path"]) != asset["qa_sha256"]:
                raise ValueError("Media or source QA changed; create new session")

    def advance(self, target, *, evidence, observed=None):
        self.validate()
        if self.data["state"] == STATES[-1]:
            raise ValueError("Final publish is forbidden in ASSISTED_MODE")
        if target != STATES[STATES.index(self.data["state"]) + 1]:
            raise ValueError("Invalid state transition")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("Operator evidence required")
        observed = observed or {}
        payload = self.data["payload"]
        if target == "OPEN_PHONE_LINK":
            if not all(observed.get(k) is True for k in ("phone_link_found", "phone_connected", "apps_available")):
                raise ValueError("Phone Link/connection/apps not verified")
        if target == "OPEN_TARGET_APP":
            if observed.get("platform") != payload["platform"] or observed.get("account") != payload["account"]:
                raise ValueError("Target app/account not verified")
        if target == "SELECT_CONTENT":
            if observed.get("media_sha256") != [a["sha256"] for a in payload["assets"]]:
                raise ValueError("Selected media/order does not match")
        if target == "PREPARE_POST":
            if any(observed.get(k) != payload[k] for k in ("caption", "cta", "disclosure")):
                raise ValueError("Prepared copy not verified")
        if target == "STOP_BEFORE_FINAL_PUBLISH":
            if not payload["scheduled_at"]:
                raise ValueError("An explicit timezone-aware time is required for QA")
            if any(self.data["qa"].get(k, {}).get("status") != "PASS" or
                   self.data["qa"][k].get("fingerprint") != self.data["fingerprint"] or
                   not self.data["qa"][k].get("evidence", "").strip() for k in QA_CHECKS):
                raise ValueError("All nine QA checks require current PASS evidence")
        self.data["state"] = target
        self.data["history"].append(dict(state=target, evidence=evidence, observed=observed,
                                          recorded_at=datetime.now(timezone.utc).isoformat()))

    def review(self, checks):
        self.validate()
        if self.data["state"] != "PRE_PUBLISH_QA":
            raise ValueError("Review must inspect the actual prepared preview")
        if set(checks) != set(QA_CHECKS):
            raise ValueError("Exactly nine checks required")
        validated = {}
        for name, check in checks.items():
            if check.get("status") not in {"PASS", "FAIL", "REVIEW", "UNKNOWN"}:
                raise ValueError("Invalid QA status")
            if not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
                raise ValueError("QA evidence required")
            validated[name] = dict(check, fingerprint=self.data["fingerprint"])
        self.data["qa"] = validated

    def save(self, path):
        self.validate()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)

    @classmethod
    def load(cls, path):
        return cls(read_json(path))
