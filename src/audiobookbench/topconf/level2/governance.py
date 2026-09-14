"""Metadata-only, fail-closed governance for the future Level-2 lane.

This module deliberately accepts only synthetic governance fixtures.  It does
not load audio, checkpoints, labels, predictions, or confirmatory outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Any, Iterable, Mapping


HEX64 = re.compile(r"^[0-9a-f]{64}$", re.I)
FAILURE_CATEGORIES = frozenset({
    "SOURCE_INVALID", "REFERENCE_INVALID", "GENERATION_FAILURE",
    "QUALITY_GATE_FAILURE", "MODEL_LOAD_FAILURE", "INFERENCE_FAILURE",
    "INVALID_OUTPUT", "GT_INVALID", "INFRASTRUCTURE_FAILURE",
    "SCIENTIFIC_VALID_CASE",
})
PRIVATE_GT_KEYS = frozenset({
    "ground_truth", "target_start_sec", "target_end_sec", "label",
    "mechanism_id", "source_id", "reference_id", "session_id", "text_hash",
})
ALLOWED_THRESHOLD_SOURCES = frozenset({
    "OFFICIAL_FIXED_THRESHOLD", "LEVEL1_CALIBRATION", "FROZEN_FIXED_FPR",
})


class Level2ValidationError(ValueError):
    """Raised for governance or identity-contract violations."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level2ValidationError(f"missing identity: {field}")
    return value


def _hash(value: Any, field: str) -> str:
    value = _text(value, field)
    if not HEX64.fullmatch(value):
        raise Level2ValidationError(f"invalid SHA256: {field}")
    return value.lower()


def _number(value: Any, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise Level2ValidationError(f"invalid number: {field}") from exc
    if not math.isfinite(parsed):
        raise Level2ValidationError(f"invalid number: {field}")
    return parsed


@dataclass(frozen=True)
class Level2SourceRecord:
    source_id: str
    speaker_id: str
    session_id: str
    language: str
    duration_sec: float
    waveform_sha256: str
    text_hash: str

    def __post_init__(self) -> None:
        for key in ("source_id", "speaker_id", "session_id", "language"):
            _text(getattr(self, key), key)
        if _number(self.duration_sec, "duration_sec") <= 0:
            raise Level2ValidationError("duration_sec must be positive")
        _hash(self.waveform_sha256, "source.waveform_sha256")
        _hash(self.text_hash, "source.text_hash")


@dataclass(frozen=True)
class Level2Reference:
    reference_id: str
    source_id: str
    speaker_id: str
    waveform_sha256: str
    text_hash: str

    def __post_init__(self) -> None:
        for key in ("reference_id", "source_id", "speaker_id"):
            _text(getattr(self, key), key)
        _hash(self.waveform_sha256, "reference.waveform_sha256")
        _hash(self.text_hash, "reference.text_hash")


@dataclass(frozen=True)
class Level2ManipulationVariant:
    case_id: str
    source_id: str
    speaker_id: str
    mechanism_id: str
    generator_id: str
    generator_version: str
    seed: int
    waveform_sha256: str
    duration_sec: float
    reference_id: str | None = None

    def __post_init__(self) -> None:
        for key in (
            "case_id", "source_id", "speaker_id", "mechanism_id",
            "generator_id", "generator_version",
        ):
            _text(getattr(self, key), key)
        if not isinstance(self.seed, int):
            raise Level2ValidationError("seed must be an integer")
        if _number(self.duration_sec, "variant.duration_sec") <= 0:
            raise Level2ValidationError("variant.duration_sec must be positive")
        _hash(self.waveform_sha256, "variant.waveform_sha256")
        if self.reference_id is not None:
            _text(self.reference_id, "reference_id")


@dataclass(frozen=True)
class Level2SplitAssignment:
    case_id: str
    split: str
    seed: int

    def __post_init__(self) -> None:
        _text(self.case_id, "split.case_id")
        _text(self.split, "split")
        if not isinstance(self.seed, int):
            raise Level2ValidationError("split seed must be an integer")


@dataclass(frozen=True)
class Level2GroundTruth:
    case_id: str
    target_start_sec: float
    target_end_sec: float
    label: str
    visibility: str

    def __post_init__(self) -> None:
        _text(self.case_id, "gt.case_id")
        _text(self.label, "gt.label")
        if self.visibility not in {"PRIVATE_GT", "REVEALED_AFTER_GATE"}:
            raise Level2ValidationError("invalid GT visibility")
        if (
            _number(self.target_start_sec, "target_start_sec") < 0
            or _number(self.target_end_sec, "target_end_sec") <= self.target_start_sec
        ):
            raise Level2ValidationError("invalid GT interval")


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    rendered = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _records(manifest: Mapping[str, Any], name: str) -> list[Mapping[str, Any]]:
    value = manifest.get(name)
    if not isinstance(value, list):
        raise Level2ValidationError(f"missing {name}")
    if not all(isinstance(item, Mapping) for item in value):
        raise Level2ValidationError(f"invalid {name} record")
    return list(value)


def _unique(items: Iterable[Any], attr: str, label: str) -> set[str]:
    values = [getattr(item, attr) for item in items]
    if len(values) != len(set(values)):
        raise Level2ValidationError(f"duplicate {label}")
    return set(values)


def validate_level2_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate identities, bounds, pairing, and split leakage."""
    if manifest.get("schema_version") != "topconf.level2.synthetic.v1":
        raise Level2ValidationError("synthetic Level-2 schema required")
    if manifest.get("data_source") != "SYNTHETIC_GOVERNANCE_DRY_RUN":
        raise Level2ValidationError("real Level-2 data is not accepted by this lane")

    sources = [Level2SourceRecord(**dict(row)) for row in _records(manifest, "sources")]
    refs = [Level2Reference(**dict(row)) for row in _records(manifest, "references")]
    variants = [Level2ManipulationVariant(**dict(row)) for row in _records(manifest, "variants")]
    splits = [Level2SplitAssignment(**dict(row)) for row in _records(manifest, "splits")]
    gt = [Level2GroundTruth(**dict(row)) for row in _records(manifest, "ground_truth")]

    source_ids = _unique(sources, "source_id", "source ID")
    ref_ids = _unique(refs, "reference_id", "reference ID")
    case_ids = _unique(variants, "case_id", "case ID")
    if _unique(splits, "case_id", "split case ID") != case_ids:
        raise Level2ValidationError("split assignments must cover each case exactly once")
    if _unique(gt, "case_id", "GT case ID") != case_ids:
        raise Level2ValidationError("GT must cover each case exactly once")

    source_by_id = {item.source_id: item for item in sources}
    ref_by_id = {item.reference_id: item for item in refs}
    split_by_case = {item.case_id: item.split for item in splits}
    variant_by_case = {item.case_id: item for item in variants}
    seen_waveforms: set[str] = set()

    for variant in variants:
        if variant.source_id not in source_ids:
            raise Level2ValidationError("missing source identity")
        source = source_by_id[variant.source_id]
        if source.speaker_id != variant.speaker_id:
            raise Level2ValidationError("variant/source speaker mismatch")
        if variant.waveform_sha256 in seen_waveforms:
            raise Level2ValidationError("duplicate waveform")
        seen_waveforms.add(variant.waveform_sha256)
        if variant.reference_id:
            if variant.reference_id not in ref_ids:
                raise Level2ValidationError("missing reference identity")
            reference = ref_by_id[variant.reference_id]
            if (
                reference.source_id == variant.source_id
                or reference.waveform_sha256 == source.waveform_sha256
            ):
                raise Level2ValidationError("reference equals source utterance")

    for item in gt:
        variant = variant_by_case[item.case_id]
        if item.target_end_sec > variant.duration_sec:
            raise Level2ValidationError("GT interval outside waveform")

    speaker_splits: dict[str, set[str]] = {}
    source_splits: dict[str, set[str]] = {}
    for variant in variants:
        split = split_by_case[variant.case_id]
        speaker_splits.setdefault(variant.speaker_id, set()).add(split)
        source_splits.setdefault(variant.source_id, set()).add(split)
    if any(len(value) > 1 for value in source_splits.values()):
        raise Level2ValidationError("source leakage across splits")
    if any(len(value) > 1 for value in speaker_splits.values()):
        raise Level2ValidationError("speaker leakage across splits")


def build_blinded_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    validate_level2_manifest(manifest)
    split_by_case = {row["case_id"]: row["split"] for row in manifest["splits"]}
    cases = [
        {
            "opaque_case_id": row["case_id"],
            "audio_identity_sha256": row["waveform_sha256"],
            "duration_sec": row["duration_sec"],
            "split": split_by_case[row["case_id"]],
        }
        for row in manifest["variants"]
    ]
    blinded = {
        "schema_version": "topconf.level2.blinded-inference.v1",
        "data_source": "SYNTHETIC_GOVERNANCE_DRY_RUN",
        "cases": cases,
        "ground_truth_visible": False,
        "prohibited_fields": sorted(PRIVATE_GT_KEYS),
    }
    validate_blinded_manifest(blinded)
    return blinded


def validate_blinded_manifest(blinded: Mapping[str, Any]) -> None:
    """Reject a model-facing manifest that leaks GT or source semantics."""
    if blinded.get("schema_version") != "topconf.level2.blinded-inference.v1":
        raise Level2ValidationError("blinded manifest schema required")
    if blinded.get("data_source") != "SYNTHETIC_GOVERNANCE_DRY_RUN":
        raise Level2ValidationError("synthetic blinded manifest required")
    if blinded.get("ground_truth_visible") is not False:
        raise Level2ValidationError("GT visible to inference")
    cases = blinded.get("cases")
    if not isinstance(cases, list) or not cases:
        raise Level2ValidationError("blinded cases missing")
    seen: set[str] = set()
    for row in cases:
        if not isinstance(row, Mapping):
            raise Level2ValidationError("invalid blinded case")
        case_id = _text(row.get("opaque_case_id"), "blinded.opaque_case_id")
        if case_id in seen:
            raise Level2ValidationError("duplicate blinded case")
        seen.add(case_id)
        _hash(row.get("audio_identity_sha256"), "blinded.audio_identity_sha256")
        _number(row.get("duration_sec"), "blinded.duration_sec")
        _text(row.get("split"), "blinded.split")
        leaked = set(row).intersection(PRIVATE_GT_KEYS)
        if leaked:
            raise Level2ValidationError(f"GT visible to inference: {sorted(leaked)[0]}")


def validate_failure_ledger(rows: Iterable[Mapping[str, Any]]) -> None:
    """Validate one terminal state per listed case."""
    terminal: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise Level2ValidationError("invalid terminal ledger row")
        case_id = _text(row.get("case_id"), "ledger.case_id")
        category = _text(row.get("terminal_category"), "ledger.terminal_category")
        if category not in FAILURE_CATEGORIES:
            raise Level2ValidationError("invalid terminal category")
        if case_id in terminal:
            raise Level2ValidationError("exactly one terminal state per case")
        terminal[case_id] = category


def validate_case_coverage(
    planned_case_ids: Iterable[str],
    terminal_rows: Iterable[Mapping[str, Any]],
) -> None:
    """Require known, complete, exactly-once terminal accounting."""
    planned = {_text(case_id, "planned.case_id") for case_id in planned_case_ids}
    rows = list(terminal_rows)
    validate_failure_ledger(rows)
    observed = {row["case_id"] for row in rows}
    unknown = observed - planned
    missing = planned - observed
    if unknown:
        raise Level2ValidationError(f"unknown case: {sorted(unknown)[0]}")
    if missing:
        raise Level2ValidationError(f"missing terminal status: {sorted(missing)[0]}")


def validate_retry_ledger(
    rows: Iterable[Mapping[str, Any]],
    terminal_rows: Iterable[Mapping[str, Any]],
) -> None:
    """Reject unregistered, result-driven, or post-valid retries."""
    valid_cases = {
        row.get("case_id")
        for row in terminal_rows
        if row.get("terminal_category") == "SCIENTIFIC_VALID_CASE"
    }
    seen_attempts: set[str] = set()
    for row in rows:
        attempt_id = _text(row.get("attempt_id"), "retry.attempt_id")
        if attempt_id in seen_attempts:
            raise Level2ValidationError("duplicate retry attempt")
        seen_attempts.add(attempt_id)
        case_id = _text(row.get("case_id"), "retry.case_id")
        _text(row.get("attempt_type"), "retry.attempt_type")
        reason = _text(row.get("retry_reason"), "retry.retry_reason")
        _hash(row.get("authorization_hash"), "retry.authorization_hash")
        if row.get("registered") is not True:
            raise Level2ValidationError("unregistered retry")
        if row.get("invoked") is not True:
            raise Level2ValidationError("retry must record invoked=true")
        if case_id in valid_cases:
            raise Level2ValidationError("retry after valid scientific result")
        if "result" in reason.lower() or "score" in reason.lower():
            raise Level2ValidationError("result-based retry forbidden")


def validate_namespace(
    candidate: Mapping[str, Any],
    registry: Iterable[Mapping[str, Any]],
) -> None:
    for key in ("invocation_id", "output_namespace", "authorization_hash", "protocol_hash", "dataset_hash"):
        _text(candidate.get(key), f"namespace.{key}")
    _hash(candidate["authorization_hash"], "namespace.authorization_hash")
    _hash(candidate["protocol_hash"], "namespace.protocol_hash")
    _hash(candidate["dataset_hash"], "namespace.dataset_hash")
    for old in registry:
        if (
            candidate["invocation_id"] == old.get("invocation_id")
            or candidate["output_namespace"] == old.get("output_namespace")
        ):
            raise Level2ValidationError("namespace collision or overwrite")


def validate_checkpoint_binding(
    candidate: Mapping[str, Any],
    expected_checkpoint_sha256: str,
) -> None:
    """Require an exact pre-registered checkpoint identity."""
    expected = _hash(expected_checkpoint_sha256, "expected_checkpoint_sha256")
    observed = _hash(candidate.get("checkpoint_sha256"), "checkpoint_sha256")
    if observed != expected:
        raise Level2ValidationError("wrong checkpoint")


def validate_metric_registration(
    metric_id: str,
    preregistered_metrics: Iterable[str],
) -> None:
    metric = _text(metric_id, "metric_id")
    allowed = {_text(value, "preregistered_metric") for value in preregistered_metrics}
    if metric not in allowed:
        raise Level2ValidationError("metric not preregistered")


def validate_threshold_policy(policy: Mapping[str, Any]) -> None:
    """Allow only fixed or independent Level-1 threshold sources."""
    source = _text(policy.get("source"), "threshold.source")
    if source not in ALLOWED_THRESHOLD_SOURCES:
        raise Level2ValidationError("threshold from test set")
    calibration_split = str(policy.get("calibration_split", "")).lower()
    if calibration_split in {"level2", "level2_test", "test", "heldout_test"}:
        raise Level2ValidationError("threshold from test set")
    if policy.get("frozen_before_level2_reveal") is not True:
        raise Level2ValidationError("threshold policy not frozen before Level-2 reveal")


def validate_reveal_gate(
    authorization: Mapping[str, Any],
    inference: Mapping[str, Any],
    expected_protocol_hash: str,
    expected_dataset_hash: str,
) -> None:
    """Allow GT reveal only after the frozen protocol and inference completion."""
    if authorization.get("status") != "SYNTHETIC_GOVERNANCE_DRY_RUN":
        raise Level2ValidationError("authorization marker missing")
    if authorization.get("protocol_frozen") is not True:
        raise Level2ValidationError("reveal before freeze")
    _hash(authorization.get("freeze_record_hash"), "freeze_record_hash")
    if (
        authorization.get("protocol_hash") != expected_protocol_hash
        or authorization.get("dataset_hash") != expected_dataset_hash
    ):
        raise Level2ValidationError("protocol/dataset hash mismatch")
    if inference.get("completed") is not True:
        raise Level2ValidationError("inference completion marker missing")
    if inference.get("protocol_hash") != expected_protocol_hash:
        raise Level2ValidationError("inference protocol hash mismatch")
