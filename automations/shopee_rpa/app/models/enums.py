"""Enums for AI Commerce Content Factory."""
from enum import Enum


class ContentFormat(str, Enum):
    """The 7 canonical content formats."""
    ACHADINHO = "ACHADINHO"
    PROBLEMA_SOLUTION = "PROBLEMA_SOLUTION"
    QUICK_REVIEW = "QUICK_REVIEW"
    PRODUCT_IN_USE = "PRODUCT_IN_USE"
    POV = "POV"
    AESTHETIC = "AESTHETIC"
    LIST = "LIST"


class FactConfidence(str, Enum):
    """Fact safety classifications."""
    CONFIRMED_FACTS = "CONFIRMED_FACTS"
    INFERRED_CONTEXT = "INFERRED_CONTEXT"
    UNKNOWN = "UNKNOWN"


class JobState(str, Enum):
    """Contractual job states in the pipeline."""
    CREATED = "CREATED"
    PRODUCT_LOADED = "PRODUCT_LOADED"
    FACTS_READY = "FACTS_READY"
    BRIEF_READY = "BRIEF_READY"
    HOOKS_READY = "HOOKS_READY"
    SCRIPT_READY = "SCRIPT_READY"
    STORYBOARD_READY = "STORYBOARD_READY"
    PROMPTS_READY = "PROMPTS_READY"
    WAITING_FOR_GENERATION = "WAITING_FOR_GENERATION"
    GENERATING_MEDIA = "GENERATING_MEDIA"
    MEDIA_READY = "MEDIA_READY"
    VISUAL_QA = "VISUAL_QA"
    EDITING = "EDITING"
    VALIDATING = "VALIDATING"
    PACKAGE_READY = "PACKAGE_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class Platform(str, Enum):
    """Target publication platforms."""
    SHOPEE_VIDEO = "SHOPEE_VIDEO"
    INSTAGRAM_REELS = "INSTAGRAM_REELS"


class CameraFraming(str, Enum):
    """Camera framing conventions for Nina storyboards."""
    CLOSE_UP = "CLOSE_UP"
    HALF_BODY = "HALF_BODY"
    FULL_BODY = "FULL_BODY"
    POV_HANDS = "POV_HANDS"
    PRODUCT_MACRO = "PRODUCT_MACRO"
