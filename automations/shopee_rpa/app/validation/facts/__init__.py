"""Facts validation and extraction package."""
from app.validation.facts.extractor import FactExtractor
from app.validation.facts.validator import FactSafetyValidator

__all__ = ["FactExtractor", "FactSafetyValidator"]