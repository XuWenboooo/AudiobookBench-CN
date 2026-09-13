"""Metadata-only schemas and gates for a future, still-unfrozen Level-2 lane."""

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
PRIVATE_GT_KEYS = frozenset({"ground_truth", "target_start_sec", "target_end_sec", "label", "mechanism_id", "source_id", "reference_id", "session_id", "text_hash"})


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
    source_id: str; speaker_id: str; session_id: str; language: str
    duration_sec: float; waveform_sha256: str; text_hash: str
    def __post_init__(self) -> None:
        for key in ("source_id", "speaker_id", "session_id", "language"):
            _text(getattr(self, key), key)
        if _number(self.duration_sec, "duration_sec") <= 0: raise Level2ValidationError("duration_sec must be positive")
        _hash(self.waveform_sha256, "source.waveform_sha256"); _hash(self.text_hash, "source.text_hash")


@dataclass(frozen=True)
class Level2Reference:
    reference_id: str; source_id: str; speaker_id: str; waveform_sha256: str; text_hash: str
    def __post_init__(self) -> None:
        for key in ("reference_id", "source_id", "speaker_id"): _text(getattr(self, key), key)
        _hash(self.waveform_sha256, "reference.waveform_sha256"); _hash(self.text_hash, "reference.text_hash")


@dataclass(frozen=True)
class Level2ManipulationVariant:
    case_id: str; source_id: str; speaker_id: str; mechanism_id: str; generator_id: str
    generator_version: str; seed: int; waveform_sha256: str; duration_sec: float
    reference_id: str | None = None
    def __post_init__(self) -> None:
        for key in ("case_id", "source_id", "speaker_id", "mechanism_id", "generator_id", "generator_version"):
            _text(getattr(self, key), key)
        if not isinstance(self.seed, int): raise Level2ValidationError("seed must be an integer")
        if _number(self.duration_sec, "variant.duration_sec") <= 0: raise Level2ValidationError("variant.duration_sec must be positive")
        _hash(self.waveform_sha256, "variant.waveform_sha256")
        if self.reference_id is not None: _text(self.reference_id, "reference_id")


@dataclass(frozen=True)
class Level2SplitAssignment:
    case_id: str; split: str; seed: int
    def __post_init__(self) -> None:
        _text(self.case_id, "split.case_id"); _text(self.split, "split")
        if not isinstance(self.seed, int): raise Level2ValidationError("split seed must be an integer")


@dataclass(frozen=True)
class Level2GroundTruth:
    case_id: str; target_start_sec: float; target_end_sec: float; label: str; visibility: str
    def __post_init__(self) -> None:
        _text(self.case_id, "gt.case_id"); _text(self.label, "gt.label")
        if self.visibility not in {"PRIVATE_GT", "REVEALED_AFTER_GATE"}: raise Level2ValidationError("invalid GT visibility")
        if _number(self.target_start_sec, "target_start_sec") < 0 or _number(self.target_end_sec, "target_end_sec") <= self.target_start_sec:
            raise Level2ValidationError("invalid GT interval")


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _records(manifest: Mapping[str, Any], name: str) -> list[Mapping[str, Any]]:
    value = manifest.get(name)
    if not isinstance(value, list): raise Level2ValidationError(f"missing {name}")
    if not all(isinstance(item, Mapping) for item in value): raise Level2ValidationError(f"invalid {name} record")
    return list(value)


def validate_level2_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate identities, bounds, pairing, and split leakage without outcomes."""
    if manifest.get("schema_version") != "topconf.level2.synthetic.v1": raise Level2ValidationError("synthetic Level-2 schema required")
    if manifest.get("data_source") != "SYNTHETIC_GOVERNANCE_DRY_RUN": raise Level2ValidationError("real Level-2 data is not accepted by this lane")
    sources = [Level2SourceRecord(**dict(row)) for row in _records(manifest, "sources")]
    refs = [Level2Reference(**dict(row)) for row in _records(manifest, "references")]
    variants = [Level2ManipulationVariant(**dict(row)) for row in _records(manifest, "variants")]
    splits = [Level2SplitAssignment(**dict(row)) for row in _records(manifest, "splits")]
    gt = [Level2GroundTruth(**dict(row)) for row in _records(manifest, "ground_truth")]
    def ids(items: Iterable[Any], attr: str, label: str) -> set[str]:
        values = [getattr(item, attr) for item in items]
        if len(values) != len(set(values)): raise Level2ValidationError(f"duplicate {label}")
        return set(values)
    source_ids = ids(sources, "source_id", "source ID")
    ref_ids = ids(refs, "reference_id", "reference ID")
    case_ids = ids(variants, "case_id", "case ID")
    if ids(splits, "case_id", "split case ID") != case_ids: raise Level2ValidationError("split assignments must cover each case exactly once")
    if ids(gt, "case_id", "GT case ID") != case_ids: raise Level2ValidationError("GT must cover each case exactly once")
    source_by_id = {item.source_id: item for item in sources}; ref_by_id = {item.reference_id: item for item in refs}; split_by_case = {item.case_id: item.split for item in splits}
    seen_waveforms: set[str] = set()
    for variant in variants:
        if variant.source_id not in source_ids: raise Level2ValidationError("missing source identity")
        source = source_by_id[variant.source_id]
        if source.speaker_id != variant.speaker_id: raise Level2ValidationError("variant/source speaker mismatch")
        if variant.waveform_sha256 in seen_waveforms: raise Level2ValidationError("duplicate waveform")
        seen_waveforms.add(variant.waveform_sha256)
        if variant.reference_id:
            if variant.reference_id not in ref_ids: raise Level2ValidationError("missing reference identity")
            reference = ref_by_id[variant.reference_id]
            if reference.source_id == variant.source_id or reference.waveform_sha256 == source.waveform_sha256: raise Level2ValidationError("reference equals source utterance")
    for item in gt:
        variant = next(v for v in variants if v.case_id == item.case_id)
        if item.target_end_sec > variant.duration_sec: raise Level2ValidationError("GT interval outside waveform")
    speaker_splits: dict[str, set[str]] = {}; source_splits: dict[str, set[str]] = {}
    for variant in variants:
        split = split_by_case[variant.case_id]
        speaker_splits.setdefault(variant.speaker_id, set()).add(split); source_splits.setdefault(variant.source_id, set()).add(split)
    if any(len(value) > 1 for value in source_splits.values()): raise Level2ValidationError("source leakage across splits")
    if any(len(value) > 1 for value in speaker_splits.values()): raise Level2ValidationError("speaker leakage across splits")


def build_blinded_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    validate_level2_manifest(manifest)
    split_by_case = {row["case_id"]: row["split"] for row in manifest["splits"]}
    cases = [{"opaque_case_id": row["case_id"], "audio_identity_sha256": row["waveform_sha256"], "duration_sec": row["duration_sec"], "split": split_by_case[row["case_id"]]} for row in manifest["variants"]]
    return {"schema_version": "topconf.level2.blinded-inference.v1", "data_source": "SYNTHETIC_GOVERNANCE_DRY_RUN", "cases": cases, "ground_truth_visible": False, "prohibited_fields": sorted(PRIVATE_GT_KEYS)}


def validate_failure_ledger(rows: Iterable[Mapping[str, Any]]) -> None:
    terminal: dict[str, str] = {}
    for row in rows:
        case_id, category = _text(row.get("case_id"), "ledger.case_id"), _text(row.get("terminal_category"), "ledger.terminal_category")
        if category not in FAILURE_CATEGORIES: raise Level2ValidationError("invalid terminal category")
        if case_id in terminal: raise Level2ValidationError("exactly one terminal state per case")
        terminal[case_id] = category


def validate_retry_ledger(rows: Iterable[Mapping[str, Any]], terminal_rows: Iterable[Mapping[str, Any]]) -> None:
    valid_cases = {row.get("case_id") for row in terminal_rows if row.get("terminal_category") == "SCIENTIFIC_VALID_CASE"}
    for row in rows:
        _text(row.get("attempt_id"), "retry.attempt_id"); case_id = _text(row.get("case_id"), "retry.case_id")
        _text(row.get("attempt_type"), "retry.attempt_type"); _text(row.get("retry_reason"), "retry.retry_reason"); _text(row.get("authorization_hash"), "retry.authorization_hash")
        if row.get("invoked") is not True: raise Level2ValidationError("retry must record invoked=true")
        if case_id in valid_cases: raise Level2ValidationError("retry after valid scientific result")
        if "result" in str(row.get("retry_reason", "")).lower(): raise Level2ValidationError("result-based retry forbidden")


def validate_namespace(candidate: Mapping[str, Any], registry: Iterable[Mapping[str, Any]]) -> None:
    for key in ("invocation_id", "output_namespace", "authorization_hash", "protocol_hash", "dataset_hash"):
        _text(candidate.get(key), f"namespace.{key}")
    for old in registry:
        if candidate["invocation_id"] == old.get("invocation_id") or candidate["output_namespace"] == old.get("output_namespace"):
            raise Level2ValidationError("namespace collision or overwrite")


def validate_reveal_gate(authorization: Mapping[str, Any], inference: Mapping[str, Any], expected_protocol_hash: str, expected_dataset_hash: str) -> None:
    if authorization.get("status") != "SYNTHETIC_GOVERNANCE_DRY_RUN": raise Level2ValidationError("authorization marker missing")
    if authorization.get("protocol_hash") != expected_protocol_hash or authorization.get("dataset_hash") != expected_dataset_hash: raise Level2ValidationError("protocol/dataset hash mismatch")
    if inference.get("completed") is not True: raise Level2ValidationError("inference completion marker missing")
    if inference.get("protocol_hash") != expected_protocol_hash: raise Level2ValidationError("inference protocol hash mismatch")
