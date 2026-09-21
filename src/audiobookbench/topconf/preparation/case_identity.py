"""Stable, outcome-blind W7 scientific case and provenance identities."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


CASE_IDENTITY_FIELDS = (
    "distribution_id",
    "distribution_version",
    "split_id",
    "source_audio_id",
    "source_audio_hash",
    "source_speaker_id",
    "source_utterance_id",
    "manipulation_id",
    "manipulation_family",
    "manipulation_mechanism",
    "condition_id",
    "condition_type",
    "transform_id",
    "transform_version",
    "audio_artifact_id",
    "audio_artifact_hash",
    "gt_id",
    "gt_version",
    "gt_hash",
    "whether_definition_id",
    "localizer_id",
    "model_checkpoint_id",
    "adapter_version",
)
OPTIONAL_CASE_FIELDS = frozenset({"source_speaker_id", "source_utterance_id", "gt_hash"})


class CaseIdentityError(ValueError):
    """Raised when a case cannot be made deterministic and unambiguous."""


def canonical_json(value: Any) -> str:
    """Serialize identity/configuration data without filesystem or time entropy."""

    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CaseIdentityError(f"identity is not canonical JSON: {exc}") from exc


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _required_text(record: Mapping[str, Any], field: str) -> str | None:
    value = record.get(field)
    if value is None and field in OPTIONAL_CASE_FIELDS:
        return None
    if not isinstance(value, str) or not value.strip():
        raise CaseIdentityError(f"{field} must be a non-empty string")
    return value.strip()


def canonical_case_payload(record: Mapping[str, Any]) -> dict[str, str | None]:
    """Return the exact identity payload used for case hashing."""

    if not isinstance(record, Mapping):
        raise CaseIdentityError("case identity must be an object")
    payload: dict[str, str | None] = {}
    for field in CASE_IDENTITY_FIELDS:
        payload[field] = _required_text(record, field)
    return payload


def build_case_identity(record: Mapping[str, Any]) -> dict[str, str | None]:
    """Build a stable opaque case ID from a predeclared identity record.

    The returned ID never depends on an absolute path, timestamp, UUID or model
    output.  The identity payload is suitable for writing into a case manifest.
    """

    payload = canonical_case_payload(record)
    identity_hash = sha256_canonical(payload)
    return {
        "case_id": f"w7case_{identity_hash[:32]}",
        "case_identity_hash": identity_hash,
        **payload,
    }


@dataclass(frozen=True)
class SourceBinding:
    """Parent-child lineage from source through transformed artifact and GT."""

    source: Mapping[str, Any]
    manipulation: Mapping[str, Any]
    condition_transform: Mapping[str, Any]
    final_audio_artifact: Mapping[str, Any]
    gt: Mapping[str, Any]

    def as_dict(self) -> dict[str, Mapping[str, Any]]:
        return {
            "source": dict(self.source),
            "manipulation": dict(self.manipulation),
            "condition_transform": dict(self.condition_transform),
            "final_audio_artifact": dict(self.final_audio_artifact),
            "gt": dict(self.gt),
        }


def validate_source_binding(binding: Mapping[str, Any]) -> None:
    """Validate explicit parent-child references without inspecting audio."""

    required = ("source", "manipulation", "condition_transform", "final_audio_artifact", "gt")
    if not isinstance(binding, Mapping) or any(key not in binding for key in required):
        raise CaseIdentityError("source binding must contain source, manipulation, condition_transform, final_audio_artifact and gt")
    for key in required:
        node = binding[key]
        if not isinstance(node, Mapping) or not node.get("id"):
            raise CaseIdentityError(f"source binding node {key} needs a stable id")
    if binding["manipulation"].get("parent_source_id") != binding["source"].get("id"):
        raise CaseIdentityError("manipulation parent_source_id does not match source id")
    if binding["condition_transform"].get("parent_manipulation_id") != binding["manipulation"].get("id"):
        raise CaseIdentityError("condition_transform parent_manipulation_id does not match manipulation id")
    if binding["final_audio_artifact"].get("parent_condition_id") != binding["condition_transform"].get("id"):
        raise CaseIdentityError("final_audio_artifact parent_condition_id does not match condition_transform id")
    if binding["gt"].get("parent_audio_artifact_id") != binding["final_audio_artifact"].get("id"):
        raise CaseIdentityError("GT parent_audio_artifact_id does not match final audio artifact id")


def assert_same_case_across_views(case_ids: Mapping[str, str]) -> str:
    """Require Whether-A, Whether-B and Where to share one case ID."""

    values = {value for value in case_ids.values() if value}
    if len(values) != 1 or set(case_ids) != {"whether_a", "whether_b", "where"}:
        raise CaseIdentityError("Whether-A, Whether-B and Where must reference one canonical case_id")
    return next(iter(values))
