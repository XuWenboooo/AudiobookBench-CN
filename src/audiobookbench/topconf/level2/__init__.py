"""Synthetic-only, fail-closed governance contracts for future Level-2 work.

This package handles metadata only.  It must never load audio, models, scores,
or confirmatory outcomes.
"""

from .governance import (
    FAILURE_CATEGORIES,
    Level2GroundTruth,
    Level2ManipulationVariant,
    Level2Reference,
    Level2SourceRecord,
    Level2SplitAssignment,
    Level2ValidationError,
    build_blinded_manifest,
    validate_level2_manifest,
)

__all__ = [
    "FAILURE_CATEGORIES", "Level2GroundTruth", "Level2ManipulationVariant",
    "Level2Reference", "Level2SourceRecord", "Level2SplitAssignment",
    "Level2ValidationError", "build_blinded_manifest", "validate_level2_manifest",
]
