"""Finalize an approved, already-produced campaign without regenerating content."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


READY_TO_POST = "READY_TO_POST"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
BLOCKED = "BLOCKED"

_CAMPAIGN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_COMPONENTS = (
    ("carousel", "CAROUSEL", "carousel"),
    ("product_stories", "PRODUCT_STORIES", "product_stories"),
    ("lifestyle_stories", "LIFESTYLE_STORIES", "lifestyle_stories"),
)
_CONFIDENCE = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
_EVIDENCE_TYPES = {"OBSERVED_ACCOUNT_DATA", "EXTERNAL_HEURISTIC", "EDITORIAL_LOGIC", "UNKNOWN"}


@dataclass
class FinalizationResult:
    campaign_id: str
    state: str
    ready_to_post_path: Optional[str] = None
    blockers: List[Dict[str, str]] = field(default_factory=list)
    review_items: List[Dict[str, str]] = field(default_factory=list)
    asset_count: int = 0
    idempotent_reuse: bool = False
    qa_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CampaignFinalizer:
    """Build a canonical READY_TO_POST package from existing campaign artifacts."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        project_root: Path,
        *,
        source_root: Optional[Path] = None,
        output_root: Optional[Path] = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.source_root = Path(source_root or self.project_root / "output").resolve()
        self.output_root = Path(output_root or self.project_root / "ready_to_post").resolve()

    def finalize(self, campaign_id: str, *, approvals_path: Optional[Path] = None) -> FinalizationResult:
        if not _CAMPAIGN_ID.fullmatch(campaign_id):
            return self._blocked(campaign_id, "INVALID_CAMPAIGN_ID", "campaign_id contains unsupported characters")

        campaign_dir = (self.source_root / campaign_id).resolve()
        if campaign_dir.parent != self.source_root:
            return self._blocked(campaign_id, "INVALID_CAMPAIGN_PATH", "campaign path escapes source_root")
        if not campaign_dir.is_dir():
            return self._blocked(campaign_id, "CAMPAIGN_NOT_FOUND", str(campaign_dir))

        blockers: List[Dict[str, str]] = []
        reviews: List[Dict[str, str]] = []
        campaign_manifest_path = campaign_dir / "manifests" / "campaign_manifest.json"
        campaign_manifest = self._read_required_json(campaign_manifest_path, "campaign manifest", blockers)
        if campaign_manifest is None:
            return self._result(campaign_id, BLOCKED, blockers=blockers)
        if campaign_manifest.get("campaign_id") != campaign_id:
            blockers.append(self._issue("CAMPAIGN_ID_MISMATCH", str(campaign_manifest_path)))

        approvals, approvals_file = self._load_approvals(campaign_id, campaign_dir, approvals_path, blockers)
        assets: List[Dict[str, Any]] = []
        source_manifests = {"campaign": self._file_record(campaign_manifest_path)}

        manifest_refs = campaign_manifest.get("manifests")
        if not isinstance(manifest_refs, Mapping):
            blockers.append(self._issue("MISSING_MANIFEST_MAP", "campaign manifest has no manifests object"))
            manifest_refs = {}

        for manifest_key, expected_kind, output_group in _COMPONENTS:
            component_path = self._resolve_campaign_path(
                manifest_refs.get(manifest_key),
                campaign_dir,
                campaign_dir / "manifests" / f"{manifest_key}_manifest.json",
            )
            component = self._read_required_json(component_path, f"{manifest_key} manifest", blockers)
            if component is None:
                continue
            source_manifests[manifest_key] = self._file_record(component_path)
            if component.get("campaign_id") != campaign_id:
                blockers.append(self._issue("CAMPAIGN_ID_MISMATCH", str(component_path)))
            if component.get("kind") != expected_kind:
                blockers.append(self._issue("MANIFEST_KIND_MISMATCH", f"{component_path}: expected {expected_kind}"))
            records = component.get("assets")
            if not isinstance(records, list) or not records:
                blockers.append(self._issue("EMPTY_ASSET_MANIFEST", str(component_path)))
                continue
            for index, record in enumerate(records, start=1):
                assets.append(
                    self._inspect_asset(
                        record,
                        index=index,
                        output_group=output_group,
                        campaign_dir=campaign_dir,
                        approvals=approvals,
                        blockers=blockers,
                        reviews=reviews,
                    )
                )

        known_assets = {asset.get("asset_id") for asset in assets if asset.get("asset_id")}
        unknown_approvals = sorted(set(approvals) - known_assets)
        for asset_id in unknown_approvals:
            blockers.append(self._issue("APPROVAL_FOR_UNKNOWN_ASSET", asset_id, asset_id))

        caption_path = self._copy_source(campaign_manifest, campaign_dir, "caption", blockers)
        hashtags_path = self._copy_source(campaign_manifest, campaign_dir, "hashtags", blockers)
        recommendation, recommendation_path = self._load_recommendation(campaign_dir, blockers)

        qa_summary = self._qa_summary(assets, blockers, reviews)
        if blockers:
            return self._result(campaign_id, BLOCKED, blockers, reviews, assets, qa_summary=qa_summary)
        if reviews:
            return self._result(campaign_id, REVIEW_REQUIRED, blockers, reviews, assets, qa_summary=qa_summary)

        source_fingerprint = self._fingerprint(
            {
                "campaign_id": campaign_id,
                "source_manifests": source_manifests,
                "assets": [self._fingerprint_asset(asset) for asset in assets],
                "caption": self._file_record(caption_path),
                "hashtags": self._file_record(hashtags_path),
                "recommendation": recommendation,
                "recommendation_file": self._optional_file_record(recommendation_path),
                "approvals_file": self._optional_file_record(approvals_file),
            }
        )
        target_dir = self.output_root / f"campaign_{campaign_id}"
        reused = self._reusable_package(target_dir, source_fingerprint)
        if reused:
            return FinalizationResult(
                campaign_id=campaign_id,
                state=READY_TO_POST,
                ready_to_post_path=str(target_dir),
                asset_count=len(assets),
                idempotent_reuse=True,
                qa_summary=qa_summary,
            )
        if target_dir.exists():
            blockers.append(
                self._issue(
                    "OUTPUT_EXISTS_WITH_DIFFERENT_INPUT",
                    f"refusing to overwrite existing package: {target_dir}",
                )
            )
            return self._result(campaign_id, BLOCKED, blockers, reviews, assets, qa_summary=qa_summary)

        self.output_root.mkdir(parents=True, exist_ok=True)
        stage = self.output_root / f".tmp_campaign_{campaign_id}_{uuid.uuid4().hex}"
        try:
            package_manifest = self._write_package(
                stage,
                campaign_id,
                campaign_dir,
                assets,
                caption_path,
                hashtags_path,
                recommendation,
                qa_summary,
                source_manifests,
                source_fingerprint,
            )
            self._verify_package(stage, package_manifest)
            stage.replace(target_dir)
        except Exception:
            if stage.exists():
                shutil.rmtree(stage)
            raise

        return FinalizationResult(
            campaign_id=campaign_id,
            state=READY_TO_POST,
            ready_to_post_path=str(target_dir),
            asset_count=len(assets),
            qa_summary=qa_summary,
        )

    def _inspect_asset(
        self,
        record: Any,
        *,
        index: int,
        output_group: str,
        campaign_dir: Path,
        approvals: Mapping[str, Dict[str, Any]],
        blockers: List[Dict[str, str]],
        reviews: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        if not isinstance(record, Mapping):
            asset_id = f"{output_group}_{index:02d}"
            blockers.append(self._issue("INVALID_ASSET_RECORD", asset_id, asset_id))
            return {"asset_id": asset_id, "output_group": output_group, "effective_status": BLOCKED}
        asset_id = str(record.get("asset_id") or f"{output_group}_{index:02d}")
        media_path = self._resolve_campaign_path(record.get("final_image"), campaign_dir)
        qa_path = self._resolve_campaign_path(record.get("qa"), campaign_dir)
        media_ok = self._required_file(media_path, "MISSING_ASSET", asset_id, blockers)
        qa_ok = self._required_file(qa_path, "MISSING_QA", asset_id, blockers)
        manifest_status = self._normalize_qa_status(record.get("qa_status"))
        qa_payload: Optional[Dict[str, Any]] = None
        qa_status = None
        if qa_ok:
            qa_payload = self._read_json(qa_path, blockers, "INVALID_QA_JSON", asset_id)
            if qa_payload is not None:
                if qa_payload.get("asset_id") not in (None, asset_id):
                    blockers.append(self._issue("QA_ASSET_ID_MISMATCH", str(qa_path), asset_id))
                qa_status = self._normalize_qa_status(qa_payload.get("status", qa_payload.get("qa_result")))
        if manifest_status is None:
            blockers.append(self._issue("INVALID_MANIFEST_QA_STATUS", str(record.get("qa_status")), asset_id))
        if qa_status is None and qa_ok:
            blockers.append(self._issue("INVALID_QA_STATUS", str(qa_path), asset_id))
        if manifest_status and qa_status and manifest_status != qa_status:
            blockers.append(
                self._issue(
                    "QA_STATUS_MISMATCH",
                    f"manifest={manifest_status}; qa={qa_status}",
                    asset_id,
                )
            )

        media_hash = self._sha256(media_path) if media_ok else None
        qa_hash = self._sha256(qa_path) if qa_ok else None
        declared_hash = record.get("sha256")
        if media_hash and (not declared_hash or media_hash != declared_hash):
            blockers.append(self._issue("ASSET_HASH_MISMATCH", str(media_path), asset_id))

        source_status = qa_status or manifest_status or BLOCKED
        effective_status = source_status
        approval = approvals.get(asset_id)
        if source_status == "FAIL":
            blockers.append(self._issue("QA_FAIL", self._qa_reason(qa_payload), asset_id))
        elif source_status == "REVIEW":
            approval_error = self._approval_error(approval, asset_id, media_hash, qa_hash)
            if approval_error is None:
                effective_status = "APPROVED_BY_USER"
            else:
                reviews.append(self._issue("QA_REVIEW", self._qa_reason(qa_payload, approval_error), asset_id))

        return {
            "asset_id": asset_id,
            "output_group": output_group,
            "source_index": index,
            "source_path": str(media_path),
            "source_sha256": media_hash,
            "qa_path": str(qa_path),
            "qa_sha256": qa_hash,
            "source_status": source_status,
            "effective_status": effective_status,
            "approval": approval if effective_status == "APPROVED_BY_USER" else None,
        }

    def _load_approvals(
        self,
        campaign_id: str,
        campaign_dir: Path,
        supplied: Optional[Path],
        blockers: List[Dict[str, str]],
    ) -> tuple[Dict[str, Dict[str, Any]], Optional[Path]]:
        path = Path(supplied).resolve() if supplied else campaign_dir / "qa" / "user_approvals.json"
        if not path.is_file():
            if supplied:
                blockers.append(self._issue("MISSING_APPROVAL_FILE", str(path)))
            return {}, None
        payload = self._read_json(path, blockers, "INVALID_APPROVAL_JSON", None)
        if payload is None:
            return {}, path
        if payload.get("campaign_id") != campaign_id:
            blockers.append(self._issue("APPROVAL_CAMPAIGN_MISMATCH", str(path)))
        raw = payload.get("approvals")
        if not isinstance(raw, list):
            blockers.append(self._issue("INVALID_APPROVAL_LIST", str(path)))
            return {}, path
        approvals: Dict[str, Dict[str, Any]] = {}
        for item in raw:
            if not isinstance(item, dict) or not item.get("asset_id"):
                blockers.append(self._issue("INVALID_APPROVAL_RECORD", str(path)))
                continue
            asset_id = str(item["asset_id"])
            if asset_id in approvals:
                blockers.append(self._issue("DUPLICATE_APPROVAL", asset_id, asset_id))
            approvals[asset_id] = item
        return approvals, path

    @staticmethod
    def _approval_error(
        approval: Optional[Mapping[str, Any]],
        asset_id: str,
        asset_hash: Optional[str],
        qa_hash: Optional[str],
    ) -> Optional[str]:
        if approval is None:
            return "No explicit user approval is recorded."
        if approval.get("status") != "APPROVED_BY_USER":
            return "Approval status is not APPROVED_BY_USER."
        if not all(isinstance(approval.get(key), str) and approval[key].strip() for key in ("approved_by", "approved_at", "reason")):
            return "Approval requires approved_by, approved_at and reason."
        try:
            approved_at = datetime.fromisoformat(str(approval["approved_at"]).replace("Z", "+00:00"))
        except ValueError:
            return "Approval timestamp is invalid."
        if approved_at.utcoffset() is None:
            return "Approval timestamp must include a timezone."
        if approval.get("asset_sha256") != asset_hash:
            return f"Approval is not bound to the current asset hash for {asset_id}."
        if approval.get("qa_sha256") != qa_hash:
            return f"Approval is not bound to the current QA hash for {asset_id}."
        return None

    def _copy_source(
        self,
        campaign_manifest: Mapping[str, Any],
        campaign_dir: Path,
        name: str,
        blockers: List[Dict[str, str]],
    ) -> Path:
        copy_config = campaign_manifest.get("copy")
        configured = copy_config.get(name) if isinstance(copy_config, Mapping) else None
        candidates = []
        if configured:
            candidates.append(self._resolve_campaign_path(configured, campaign_dir))
        candidates.extend((campaign_dir / "content" / f"{name}.txt", campaign_dir / f"{name}.txt"))
        path = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
        if not path.is_file():
            blockers.append(self._issue(f"MISSING_{name.upper()}", str(path)))
        return path

    def _load_recommendation(
        self, campaign_dir: Path, blockers: List[Dict[str, str]]
    ) -> tuple[Dict[str, Any], Optional[Path]]:
        path = campaign_dir / "content" / "posting_recommendation.json"
        unknown = {
            "recommended_time": None,
            "confidence": "UNKNOWN",
            "evidence_type": "UNKNOWN",
            "reason": "No observed account performance data is available; choose the posting time manually.",
        }
        if not path.is_file():
            return {"default": unknown, "items": {}}, None
        payload = self._read_json(path, blockers, "INVALID_POSTING_RECOMMENDATION", None)
        if payload is None:
            return {"default": unknown, "items": {}}, path
        default = payload.get("default", payload)
        items = payload.get("items", {})
        if not isinstance(default, Mapping) or not isinstance(items, Mapping):
            blockers.append(self._issue("INVALID_POSTING_RECOMMENDATION", str(path)))
            return {"default": unknown, "items": {}}, path
        validated_default = self._validate_recommendation(default, "default", blockers)
        validated_items = {
            str(key): self._validate_recommendation(value, str(key), blockers)
            for key, value in items.items()
            if isinstance(value, Mapping)
        }
        invalid_items = [str(key) for key, value in items.items() if not isinstance(value, Mapping)]
        for key in invalid_items:
            blockers.append(self._issue("INVALID_POSTING_RECOMMENDATION", key))
        return {"default": validated_default, "items": validated_items}, path

    @staticmethod
    def _validate_recommendation(
        value: Mapping[str, Any], label: str, blockers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        recommended_time = value.get("recommended_time")
        confidence = value.get("confidence")
        evidence_type = value.get("evidence_type")
        reason = value.get("reason")
        if recommended_time is not None and (not isinstance(recommended_time, str) or not recommended_time.strip()):
            blockers.append(CampaignFinalizer._issue("INVALID_RECOMMENDED_TIME", label))
        if confidence not in _CONFIDENCE:
            blockers.append(CampaignFinalizer._issue("INVALID_CONFIDENCE", label))
        if evidence_type not in _EVIDENCE_TYPES:
            blockers.append(CampaignFinalizer._issue("INVALID_EVIDENCE_TYPE", label))
        if not isinstance(reason, str) or not reason.strip():
            blockers.append(CampaignFinalizer._issue("MISSING_RECOMMENDATION_REASON", label))
        return {
            "recommended_time": recommended_time,
            "confidence": confidence,
            "evidence_type": evidence_type,
            "reason": reason,
        }

    def _write_package(
        self,
        stage: Path,
        campaign_id: str,
        campaign_dir: Path,
        assets: List[Dict[str, Any]],
        caption_path: Path,
        hashtags_path: Path,
        recommendation: Dict[str, Any],
        qa_summary: Dict[str, Any],
        source_manifests: Dict[str, Any],
        source_fingerprint: str,
    ) -> Dict[str, Any]:
        stage.mkdir(parents=True)
        for group in ("carousel", "product_stories", "lifestyle_stories"):
            (stage / group).mkdir()

        output_assets = []
        group_counters = {"carousel": 0, "product_stories": 0, "lifestyle_stories": 0}
        for asset in assets:
            group = asset["output_group"]
            group_counters[group] += 1
            destination_name = self._destination_name(group, group_counters[group], asset["asset_id"])
            destination = stage / group / destination_name
            shutil.copy2(asset["source_path"], destination)
            output_assets.append(
                {
                    **asset,
                    "package_path": destination.relative_to(stage).as_posix(),
                    "package_sha256": self._sha256(destination),
                }
            )

        shutil.copy2(caption_path, stage / "caption.txt")
        shutil.copy2(hashtags_path, stage / "hashtags.txt")
        posting_plan = self._posting_plan(campaign_id, output_assets, recommendation)
        (stage / "posting_plan.md").write_text(posting_plan, encoding="utf-8")
        self._write_json(stage / "qa_summary.json", qa_summary)
        manifest = {
            "schema_version": self.SCHEMA_VERSION,
            "campaign_id": campaign_id,
            "state": READY_TO_POST,
            "published": False,
            "source_campaign": str(campaign_dir),
            "source_fingerprint": source_fingerprint,
            "source_manifests": source_manifests,
            "assets": output_assets,
            "copy": {
                "caption": self._file_record(stage / "caption.txt", relative_to=stage),
                "hashtags": self._file_record(stage / "hashtags.txt", relative_to=stage),
            },
            "posting_plan": self._file_record(stage / "posting_plan.md", relative_to=stage),
            "qa_summary": self._file_record(stage / "qa_summary.json", relative_to=stage),
            "posting_recommendation": recommendation,
        }
        self._write_json(stage / "manifest.json", manifest)
        return manifest

    @staticmethod
    def _destination_name(group: str, number: int, asset_id: str) -> str:
        if group == "carousel":
            return f"slide_{number:02d}.png"
        if group == "product_stories":
            return f"story_{number:02d}.png"
        prefix = "lifestyle_"
        suffix = asset_id[len(prefix):] if asset_id.startswith(prefix) else f"story_{number:02d}"
        safe_suffix = re.sub(r"[^a-z0-9_-]+", "_", suffix.lower()).strip("_") or f"story_{number:02d}"
        return f"{safe_suffix}.png"

    @staticmethod
    def _posting_plan(campaign_id: str, assets: List[Dict[str, Any]], recommendation: Dict[str, Any]) -> str:
        sections = [("INSTAGRAM CAROUSEL", "carousel", "carousel")]
        sections.extend(
            (f"PRODUCT STORY {index}", asset["asset_id"], asset["asset_id"])
            for index, asset in enumerate((item for item in assets if item["output_group"] == "product_stories"), start=1)
        )
        sections.extend(
            (f"LIFESTYLE {asset['asset_id'].removeprefix('lifestyle_').upper()}", asset["asset_id"], asset["asset_id"])
            for asset in assets
            if asset["output_group"] == "lifestyle_stories"
        )
        lines = ["# Posting Plan", "", f"CAMPAIGN: {campaign_id}", "", "Publication is manual; this file does not authorize or perform publishing."]
        for title, key, asset_id in sections:
            value = recommendation["items"].get(key, recommendation["default"])
            matching = [item["package_path"] for item in assets if item["output_group"] == "carousel"] if key == "carousel" else [item["package_path"] for item in assets if item["asset_id"] == asset_id]
            lines.extend(
                [
                    "",
                    f"## {title}",
                    "",
                    f"assets: {', '.join(matching)}",
                    f"recommended_time: {value['recommended_time'] if value['recommended_time'] is not None else 'UNKNOWN'}",
                    f"confidence: {value['confidence']}",
                    f"evidence_type: {value['evidence_type']}",
                    f"reason: {value['reason']}",
                ]
            )
        return "\n".join(lines) + "\n"

    def _verify_package(self, stage: Path, manifest: Mapping[str, Any]) -> None:
        required = ("caption.txt", "hashtags.txt", "posting_plan.md", "manifest.json", "qa_summary.json")
        missing = [name for name in required if not (stage / name).is_file()]
        if missing:
            raise RuntimeError(f"package verification failed; missing: {missing}")
        for asset in manifest["assets"]:
            path = stage / asset["package_path"]
            if not path.is_file() or self._sha256(path) != asset["package_sha256"]:
                raise RuntimeError(f"package verification failed for {asset['asset_id']}")
        for name in ("caption", "hashtags"):
            record = manifest["copy"][name]
            if self._sha256(stage / record["path"]) != record["sha256"]:
                raise RuntimeError(f"copy verification failed for {name}")

    def _reusable_package(self, target: Path, fingerprint: str) -> bool:
        manifest_path = target / "manifest.json"
        if not manifest_path.is_file():
            return False
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if manifest.get("state") != READY_TO_POST or manifest.get("source_fingerprint") != fingerprint:
                return False
            self._verify_package(target, manifest)
            return True
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return False

    @staticmethod
    def _qa_summary(
        assets: Iterable[Mapping[str, Any]],
        blockers: List[Dict[str, str]],
        reviews: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        assets = list(assets)
        source_counts = {"PASS": 0, "REVIEW": 0, "FAIL": 0, "BLOCKED": 0}
        effective_counts = {"PASS": 0, "APPROVED_BY_USER": 0, "REVIEW": 0, "FAIL": 0, "BLOCKED": 0}
        records = []
        for asset in assets:
            source = str(asset.get("source_status", BLOCKED))
            effective = str(asset.get("effective_status", BLOCKED))
            source_counts[source if source in source_counts else "BLOCKED"] += 1
            effective_counts[effective if effective in effective_counts else "BLOCKED"] += 1
            records.append(
                {
                    "asset_id": asset.get("asset_id"),
                    "source_status": source,
                    "effective_status": effective,
                    "asset_sha256": asset.get("source_sha256"),
                    "qa_sha256": asset.get("qa_sha256"),
                    "approval": asset.get("approval"),
                }
            )
        state = BLOCKED if blockers else (REVIEW_REQUIRED if reviews else READY_TO_POST)
        return {
            "state": state,
            "assets_total": len(assets),
            "source_status_counts": source_counts,
            "effective_status_counts": effective_counts,
            "assets": records,
            "blockers": blockers,
            "review_items": reviews,
        }

    @staticmethod
    def _normalize_qa_status(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None
        normalized = value.strip().upper()
        if normalized in {"PASS", "READY", "READY_TO_POST", "APPROVED_BY_USER"}:
            return "PASS"
        if normalized in {"REVIEW", "REVIEW_REQUIRED", "TEXT_RENDER_REVIEW_REQUIRED"}:
            return "REVIEW"
        if normalized in {"FAIL", "FAILED", "BLOCKED"}:
            return "FAIL"
        return None

    @staticmethod
    def _qa_reason(payload: Optional[Mapping[str, Any]], fallback: str = "QA requires user review.") -> str:
        if not payload:
            return fallback
        limitations = payload.get("limitations")
        if isinstance(limitations, list) and limitations:
            return "; ".join(dict.fromkeys(str(item) for item in limitations))
        failures = payload.get("semantic_failures")
        if isinstance(failures, list) and failures:
            return "; ".join(str(item) for item in failures)
        return fallback

    @staticmethod
    def _resolve_campaign_path(value: Any, campaign_dir: Path, fallback: Optional[Path] = None) -> Path:
        if not value:
            return Path(fallback or campaign_dir / "__missing__")
        path = Path(str(value))
        if not path.is_absolute():
            path = campaign_dir / path
        return path.resolve()

    @staticmethod
    def _required_file(path: Path, code: str, asset_id: str, blockers: List[Dict[str, str]]) -> bool:
        if path.is_file():
            return True
        blockers.append(CampaignFinalizer._issue(code, str(path), asset_id))
        return False

    def _read_required_json(
        self, path: Path, label: str, blockers: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        if not path.is_file():
            blockers.append(self._issue("MISSING_REQUIRED_FILE", f"{label}: {path}"))
            return None
        return self._read_json(path, blockers, "INVALID_JSON", None)

    @staticmethod
    def _read_json(
        path: Path, blockers: List[Dict[str, str]], code: str, asset_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            blockers.append(CampaignFinalizer._issue(code, f"{path}: {type(exc).__name__}", asset_id))
            return None
        if not isinstance(payload, dict):
            blockers.append(CampaignFinalizer._issue(code, f"{path}: root must be an object", asset_id))
            return None
        return payload

    @staticmethod
    def _issue(code: str, reason: str, asset_id: Optional[str] = None) -> Dict[str, str]:
        issue = {"code": code, "reason": reason}
        if asset_id:
            issue["asset_id"] = asset_id
        return issue

    def _blocked(self, campaign_id: str, code: str, reason: str) -> FinalizationResult:
        return self._result(campaign_id, BLOCKED, blockers=[self._issue(code, reason)])

    @staticmethod
    def _result(
        campaign_id: str,
        state: str,
        blockers: Optional[List[Dict[str, str]]] = None,
        reviews: Optional[List[Dict[str, str]]] = None,
        assets: Optional[List[Dict[str, Any]]] = None,
        *,
        qa_summary: Optional[Dict[str, Any]] = None,
    ) -> FinalizationResult:
        return FinalizationResult(
            campaign_id=campaign_id,
            state=state,
            blockers=blockers or [],
            review_items=reviews or [],
            asset_count=len(assets or []),
            qa_summary=qa_summary or {},
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def _file_record(self, path: Path, *, relative_to: Optional[Path] = None) -> Dict[str, Any]:
        display = path.relative_to(relative_to).as_posix() if relative_to else str(path)
        return {"path": display, "bytes": path.stat().st_size, "sha256": self._sha256(path)}

    def _optional_file_record(self, path: Optional[Path]) -> Optional[Dict[str, Any]]:
        return self._file_record(path) if path and path.is_file() else None

    @staticmethod
    def _fingerprint(payload: Mapping[str, Any]) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _fingerprint_asset(asset: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "asset_id": asset.get("asset_id"),
            "output_group": asset.get("output_group"),
            "source_sha256": asset.get("source_sha256"),
            "qa_sha256": asset.get("qa_sha256"),
            "effective_status": asset.get("effective_status"),
            "approval": asset.get("approval"),
        }

    @staticmethod
    def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
