"""Outcome-blind W7 mechanism specification completion contracts."""
from __future__ import annotations

import hashlib
import json
from typing import Mapping


PROTOCOL_ID = "W7_PILOT_PROTOCOL_V1_1"
ASSIGNMENT_SALT = "W7_MECHANISM_ASSIGNMENT_V1"
SEED_SALT = "W7_MECHANISM_SEED_V1"
SAMPLE_RATE_HZ = 16000
FAMILY_IDS = tuple(sorted((
    "same_speaker_splice_crossfade_control",
    "cross_speaker_boundary_control",
    "conventional_tts_replacement",
    "voice_conditioned_tts_vc_replacement",
    "neural_speech_editing_infilling",
)))
P4_FIELDS = (
    "implementation",
    "version",
    "parameter_set_id",
    "reference_rule",
    "target_span_rule",
    "codec_path",
    "parameters",
)
FIXED_FIELDS = {
    "sample_rate": SAMPLE_RATE_HZ,
    "seed_policy": "SHA256(protocol_id||distribution_id||case_id||mechanism_family||W7_MECHANISM_SEED_V1)[:64bits]",
    "quality_gate_policy": "finite_waveform; valid_duration; valid_sample_rate; no_corruption; contract_structural_validity_only",
    "failure_policy": "terminal_generation_or_quality_failure; no_drop; no_impute; no_outcome_retry",
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_text(*parts: str) -> bytes:
    return hashlib.sha256("".join(parts).encode("utf-8")).digest()


def eligible_families(record: Mapping[str, object]) -> tuple[str, ...]:
    """Return the frozen applicability set; no pre-W7 evidence excludes one."""
    required = ("case_id", "distribution_id")
    source_id = record.get("source_audio_id") or record.get("source_id")
    if any(not record.get(field) for field in required) or not source_id:
        raise ValueError("mechanism assignment requires frozen case identity")
    return FAMILY_IDS


def assign_family(record: Mapping[str, object]) -> dict[str, object]:
    families = eligible_families(record)
    case_id = str(record["case_id"])
    distribution_id = str(record["distribution_id"])
    assignment_hash = digest_text(PROTOCOL_ID, distribution_id, case_id, ASSIGNMENT_SALT).hex().upper()
    index = int.from_bytes(bytes.fromhex(assignment_hash)[:8], "big", signed=False) % len(families)
    family = families[index]
    seed_hash = digest_text(PROTOCOL_ID, distribution_id, case_id, family, SEED_SALT).hex().upper()
    return {
        "eligible_families": list(families),
        "assignment_hash": assignment_hash,
        "family_index": index,
        "mechanism_family": family,
        "seed_hash": seed_hash,
        "seed_uint64": int.from_bytes(bytes.fromhex(seed_hash)[:8], "big", signed=False),
    }


def family_config_status(family: str) -> dict[str, object]:
    if family not in FAMILY_IDS:
        raise ValueError(f"unknown mechanism family: {family}")
    return {
        "mechanism_family": family,
        "configuration_status": "INCOMPLETE_P4_HUMAN_DECISION_REQUIRED",
        "p4_fields": list(P4_FIELDS),
        "fixed_fields": dict(FIXED_FIELDS),
        "mechanism_config_hash": "NOT_AVAILABLE",
    }


def validate_assignment(row: Mapping[str, object]) -> None:
    expected = assign_family(row)
    for key in ("eligible_families", "assignment_hash", "family_index", "mechanism_family", "seed_hash", "seed_uint64"):
        if row[key] != expected[key]:
            raise ValueError(f"non-deterministic mechanism assignment: {key}")
    if row["configuration_status"] != "INCOMPLETE_P4_HUMAN_DECISION_REQUIRED":
        raise ValueError("P4 configuration must fail closed")
