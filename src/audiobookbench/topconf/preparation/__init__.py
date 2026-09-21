"""Outcome-blind preparation components for the TopConf W7 pilot."""

from .distribution_acceptance import (
    ACCEPTANCE_VALIDATOR_VERSION,
    validate_distribution_file,
    validate_distribution_manifest,
)
from .temporal_gt_adapter import (
    CanonicalCase,
    TemporalInterval,
    TemporalGTAdapterError,
    emit_canonical_case,
    normalize_ground_truth,
)
from .case_identity import (
    CaseIdentityError,
    SourceBinding,
    assert_same_case_across_views,
    build_case_identity,
    validate_source_binding,
)
from .mechanism_identity import MechanismIdentityError, build_mechanism_identity
from .resampling_identity import (
    ResamplingIdentityError,
    ResamplingTransformIdentity,
    apply_declared_resampling,
    validate_synthetic_transform,
)

__all__ = [
    "ACCEPTANCE_VALIDATOR_VERSION",
    "CanonicalCase",
    "TemporalInterval",
    "TemporalGTAdapterError",
    "emit_canonical_case",
    "normalize_ground_truth",
    "CaseIdentityError",
    "SourceBinding",
    "assert_same_case_across_views",
    "build_case_identity",
    "validate_source_binding",
    "MechanismIdentityError",
    "build_mechanism_identity",
    "ResamplingIdentityError",
    "ResamplingTransformIdentity",
    "apply_declared_resampling",
    "validate_synthetic_transform",
    "validate_distribution_file",
    "validate_distribution_manifest",
]
