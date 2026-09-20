"""Outcome-blind canonicalization of the predeclared W7 mechanism contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .case_identity import CaseIdentityError, canonical_json, sha256_canonical


MECHANISM_FAMILIES = (
    "same_speaker_splice_crossfade_control",
    "cross_speaker_boundary_control",
    "conventional_tts_replacement",
    "voice_conditioned_tts_vc_replacement",
    "neural_speech_editing_infilling",
)
MECHANISM_REQUIRED_FIELDS = (
    "mechanism_family",
    "implementation",
    "version",
    "parameter_set_id",
    "reference_rule",
    "target_span_rule",
    "sample_rate",
    "codec_path",
    "seed_policy",
    "quality_gate_policy",
    "parameters",
)


class MechanismIdentityError(ValueError):
    pass


def canonical_mechanism_config(config: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(config, Mapping):
        raise MechanismIdentityError("mechanism config must be an object")
    missing = [field for field in MECHANISM_REQUIRED_FIELDS if field not in config]
    if missing:
        raise MechanismIdentityError(f"mechanism config missing fields: {missing}")
    family = config["mechanism_family"]
    if family not in MECHANISM_FAMILIES:
        raise MechanismIdentityError(f"unsupported mechanism family: {family}")
    if not isinstance(config["parameters"], Mapping):
        raise MechanismIdentityError("mechanism config parameters must be an object")
    scalar_fields = [field for field in MECHANISM_REQUIRED_FIELDS if field != "parameters"]
    if any(not isinstance(config[field], (str, int, float, bool)) or (isinstance(config[field], str) and not config[field].strip()) for field in scalar_fields):
        raise MechanismIdentityError("mechanism identity fields must be scalar and non-empty")
    result = {field: config[field] for field in MECHANISM_REQUIRED_FIELDS}
    result["parameters"] = dict(config["parameters"])
    return result


def build_mechanism_identity(config: Mapping[str, Any]) -> dict[str, Any]:
    canonical = canonical_mechanism_config(config)
    config_hash = sha256_canonical(canonical)
    return {
        **canonical,
        "mechanism_config_hash": config_hash,
        "mechanism_id": f"w7mech_{config_hash[:24]}",
    }


@dataclass(frozen=True)
class MechanismConfig:
    mechanism_family: str
    implementation: str
    version: str
    parameter_set_id: str
    reference_rule: str
    target_span_rule: str
    sample_rate: int
    codec_path: str
    seed_policy: str
    quality_gate_policy: str
    parameters: Mapping[str, Any]

    def identity(self) -> dict[str, Any]:
        return build_mechanism_identity(self.__dict__)
