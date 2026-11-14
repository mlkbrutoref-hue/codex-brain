"""Provider-independent contracts for a sequenced static carousel."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SlideType(str, Enum):
    COVER = "COVER"
    PRODUCT = "PRODUCT"
    CTA = "CTA"


@dataclass
class CarouselSlide:
    slide_number: int
    slide_type: SlideType
    reference_id: str
    copy: Dict[str, str]
    scene_prompt: str
    product_id: str = ""
    use_nina: bool = False
    composition_requirements: List[str] = field(default_factory=list)
    realism_constraints: List[str] = field(default_factory=list)
    correction_attempt: int = 0

    def __post_init__(self) -> None:
        if isinstance(self.slide_type, str):
            self.slide_type = SlideType(self.slide_type.upper())
        self.copy = {str(key): str(value).strip() for key, value in self.copy.items() if str(value).strip()}
        if self.slide_number < 1:
            raise ValueError("slide_number must be positive")
        if not self.reference_id.strip():
            raise ValueError(f"slide {self.slide_number}: reference_id is required")
        if not self.scene_prompt.strip():
            raise ValueError(f"slide {self.slide_number}: scene_prompt is required")
        if self.correction_attempt not in (0, 1):
            raise ValueError(f"slide {self.slide_number}: correction_attempt must be 0 or 1")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["slide_type"] = self.slide_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CarouselSlide":
        return cls(
            slide_number=int(data.get("slide_number", 0)),
            slide_type=SlideType(str(data.get("slide_type", "")).upper()),
            reference_id=str(data.get("reference_id", "")),
            copy=dict(data.get("copy", {})),
            scene_prompt=str(data.get("scene_prompt", "")),
            product_id=str(data.get("product_id", "")),
            use_nina=bool(data.get("use_nina", False)),
            composition_requirements=list(data.get("composition_requirements", [])),
            realism_constraints=list(data.get("realism_constraints", [])),
            correction_attempt=int(data.get("correction_attempt", 0)),
        )


@dataclass
class CarouselPlan:
    campaign_id: str
    slides: List[CarouselSlide]
    selected_products: List[Dict[str, Any]]
    pinterest_references: List[Dict[str, Any]]
    persona_reference_paths: List[str] = field(default_factory=list)
    style_reference_paths: List[str] = field(default_factory=list)
    cta_keyword: str = ""

    def __post_init__(self) -> None:
        if not self.campaign_id.strip():
            raise ValueError("campaign_id is required")
        if not self.slides:
            raise ValueError("slides cannot be empty")
        numbers = [slide.slide_number for slide in self.slides]
        if numbers != list(range(1, len(self.slides) + 1)):
            raise ValueError("slides must be ordered consecutively from 1")
        if self.slides[0].slide_type is not SlideType.COVER:
            raise ValueError("first slide must be COVER")
        if self.slides[-1].slide_type is not SlideType.CTA:
            raise ValueError("last slide must be CTA")
        products = {str(item.get("product_id", "")): item for item in self.selected_products}
        references = {str(item.get("reference_id", "")): item for item in self.pinterest_references}
        for slide in self.slides:
            if slide.reference_id not in references:
                raise ValueError(f"slide {slide.slide_number}: unknown reference_id {slide.reference_id}")
            reference = references[slide.reference_id]
            if not (reference.get("path") or reference.get("scene_reference_path")):
                raise ValueError(f"slide {slide.slide_number}: Pinterest reference path is required")
            if slide.slide_type is SlideType.PRODUCT:
                if not slide.product_id or slide.product_id not in products:
                    raise ValueError(f"slide {slide.slide_number}: valid product_id is required")
                product = products[slide.product_id]
                if not (product.get("official_product_reference") or product.get("official_asset")):
                    raise ValueError(f"slide {slide.slide_number}: official product reference is required")
            if slide.use_nina and len(self.persona_reference_paths) < 2:
                raise ValueError(f"slide {slide.slide_number}: Nina requires both canonical persona references")
            self._validate_copy(slide)

    def _validate_copy(self, slide: CarouselSlide) -> None:
        required = {
            SlideType.COVER: ("top_pill", "headline", "subheadline"),
            SlideType.PRODUCT: ("micro_hook", "product_name", "benefit"),
            SlideType.CTA: ("question", "cta"),
        }[slide.slide_type]
        missing = [key for key in required if not slide.copy.get(key)]
        if slide.slide_type is SlideType.CTA and not (slide.copy.get("keyword") or self.cta_keyword):
            missing.append("keyword")
        if missing:
            raise ValueError(f"slide {slide.slide_number}: missing copy fields {', '.join(missing)}")

    def product(self, product_id: str) -> Dict[str, Any]:
        return next((item for item in self.selected_products if str(item.get("product_id")) == product_id), {})

    def reference(self, reference_id: str) -> Dict[str, Any]:
        return next((item for item in self.pinterest_references if str(item.get("reference_id")) == reference_id), {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "format_spec": {"width": 1080, "height": 1440, "aspect_ratio": "3:4"},
            "cta_keyword": self.cta_keyword,
            "persona_reference_paths": list(self.persona_reference_paths),
            "style_reference_paths": list(self.style_reference_paths),
            "selected_products": self.selected_products,
            "pinterest_references": self.pinterest_references,
            "slides": [slide.to_dict() for slide in self.slides],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CarouselPlan":
        return cls(
            campaign_id=str(data.get("campaign_id", "")),
            slides=[CarouselSlide.from_dict(item) for item in data.get("slides", [])],
            selected_products=list(data.get("selected_products", [])),
            pinterest_references=list(data.get("pinterest_references", [])),
            persona_reference_paths=list(data.get("persona_reference_paths", [])),
            style_reference_paths=list(data.get("style_reference_paths", [])),
            cta_keyword=str(data.get("cta_keyword", "")).strip(),
        )
