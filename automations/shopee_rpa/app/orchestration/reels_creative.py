"""Focused Shopee Product -> ProductFacts -> Nina CreativePackage pipeline."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.models.enums import FactConfidence
from app.models.facts import FactItem
from app.providers.shopee.base import ShopeeProductProvider
from app.providers.shopee.factory import get_shopee_provider
from app.validation.facts.extractor import FactExtractor


class ReelsCreativePipeline:
    """Builds and validates a CreativePackage without invoking a visual provider."""

    SKILL_NAME = "nina-reels-content-director"

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        product_provider: Optional[ShopeeProductProvider] = None,
        skill_dir: Optional[Path] = None,
    ) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parents[2]
        self.product_provider = product_provider or get_shopee_provider()
        self.skill_dir = Path(skill_dir) if skill_dir else (
            self.base_dir / ".agents" / "skills" / self.SKILL_NAME
        )
        self.fact_extractor = FactExtractor()
        self._builder = self._load_script("build_creative_package").build_creative_package
        self._validator = self._load_script("validate_creative_package").validate

    def _load_script(self, name: str):
        path = self.skill_dir / "scripts" / f"{name}.py"
        if not path.is_file():
            raise FileNotFoundError(f"Skill script missing: {path}")
        spec = importlib.util.spec_from_file_location(f"{self.SKILL_NAME}_{name}", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load Skill script: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run(self, product_id: str, output_dir: Path) -> Dict[str, Any]:
        product = self.product_provider.get_product(product_id)
        facts = self.fact_extractor.extract(product)
        if product.title.strip() and not any(
            item.source == "shopee_api_product_title" for item in facts.confirmed_facts
        ):
            facts.confirmed_facts.insert(
                0,
                FactItem(
                    claim=product.title.strip(),
                    confidence=FactConfidence.CONFIRMED_FACTS,
                    source="shopee_api_product_title",
                    verifiable=True,
                ),
            )

        provider_kind = (
            "FIXTURE" if "fixture" in type(self.product_provider).__name__.casefold() else "LIVE"
        )
        package = self._builder(
            product.to_dict(),
            facts.to_dict(),
            product_provider=provider_kind,
            pipeline_integrated=True,
        )
        errors = self._validator(package)
        if errors:
            raise ValueError("CreativePackage validation failed: " + "; ".join(errors))

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(output_dir / "product.json", product.to_dict())
        self._write_json(output_dir / "facts.json", facts.to_dict())
        self._write_json(output_dir / "creative_package.json", package)
        return package

    @staticmethod
    def _write_json(path: Path, data: Dict[str, Any]) -> None:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
