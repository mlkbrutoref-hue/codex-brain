"""Product facts classification models enforcing Fact Safety rules."""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from app.models.enums import FactConfidence


@dataclass
class FactItem:
    """Individual assertion with confidence rating and provenance."""
    claim: str
    confidence: FactConfidence
    source: str
    verifiable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "confidence": self.confidence.value if isinstance(self.confidence, FactConfidence) else str(self.confidence),
            "source": self.source,
            "verifiable": self.verifiable,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FactItem":
        conf = data.get("confidence", FactConfidence.UNKNOWN.value)
        if isinstance(conf, str):
            conf = FactConfidence(conf)
        return cls(
            claim=str(data.get("claim", "")),
            confidence=conf,
            source=str(data.get("source", "")),
            verifiable=bool(data.get("verifiable", True)),
        )


@dataclass
class ProductFacts:
    """Classified fact sheet for a product."""
    product_id: str
    confirmed_facts: List[FactItem] = field(default_factory=list)
    inferred_context: List[FactItem] = field(default_factory=list)
    unknown_claims: List[FactItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "confirmed_facts": [f.to_dict() for f in self.confirmed_facts],
            "inferred_context": [f.to_dict() for f in self.inferred_context],
            "unknown_claims": [f.to_dict() for f in self.unknown_claims],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductFacts":
        return cls(
            product_id=str(data.get("product_id", "")),
            confirmed_facts=[FactItem.from_dict(f) for f in data.get("confirmed_facts", [])],
            inferred_context=[FactItem.from_dict(f) for f in data.get("inferred_context", [])],
            unknown_claims=[FactItem.from_dict(f) for f in data.get("unknown_claims", [])],
        )