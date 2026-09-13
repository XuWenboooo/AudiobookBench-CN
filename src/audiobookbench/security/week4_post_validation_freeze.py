"""Evidence-only post-validation A0 freeze gate for a future held-out run.

The sole permitted post-validation repair is governance-record tooling.  This
module reads immutable validation evidence and never imports F5, D0, A0 search,
or the final evaluator.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from audiobookbench.security.week4_adaptive import CandidateLedger, canonical_waveform_sha256
from audiobookbench.security.week4_authorization import CANONICAL_SOURCES, sha256_file


class PostValidationFreezeError(RuntimeError):
    """Raised if validation evidence cannot support an A0 freeze."""


VALIDATION_CASE_COUNT = 12
_HASH = re.compile(r"^[A-Fa-f0-9]{64}$")
VALIDATION_SOURCE_NAMES = tuple(CANONICAL_SOURCES)
# Validation recorded the pre-repair execution-source manifest.  This repair
# may change that manifest, but cannot change any scientific validation input.
SCIENTIFIC_VALIDATION_SOURCE_NAMES = tuple(name for name in VALIDATION_SOURCE_NAMES if name != "execution_source_manifest")
FREEZE_CLAIMS = {
    "VALIDATION_STAGE_COMPLETE": "YES",
    "ATTACK_METHOD_CHANGED_AFTER_VALIDATION": "NO",
    "OBJECTIVE_CHANGED_AFTER_VALIDATION": "NO",
    "SEARCH_CHANGED_AFTER_VALIDATION": "NO",
    "QUERY_BUDGET_CHANGED_AFTER_VALIDATION": "NO",
    "EXECUTION_IMPLEMENTATION_CHANGED_AFTER_VALIDATION": "NO",
    "HELD_OUT_OUTCOME_OBSERVED": "NO",
    "H4_OUTCOME_OBSERVED": "NO",
    "A0_FROZEN_FOR_HELD_OUT": "YES",
    "POST_VALIDATION_FREEZE_TOOLING_CHANGED_AFTER_VALIDATION": "YES",
}
COUNT_FIELDS = (
    "VALIDATION_PLANNED", "VALIDATION_TERMINAL", "VALIDATION_WITH_WINNER",
    "VALIDATION_NO_VALID_ADAPTIVE_PARENT", "VALIDATION_OTHER_FAILURES",
)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PostValidationFreezeError(f"{label} is unreadable") from exc
    if not isinstance(value, dict):
        raise PostValidationFreezeError(f"{label} is not an object")
    return value


def _verify_chain(path: Path) -> None:
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise PostValidationFreezeError("validation status-event chain is unreadable") from exc
    if not rows:
        raise PostValidationFreezeError("validation status-event chain is empty")
    previous = ""
    for row in rows:
        supplied = row.pop("record_sha256", None)
        raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if not isinstance(supplied, str) or row.get("previous_record_sha256") != previous or hashlib.sha256(raw).hexdigest().upper() != supplied:
            raise PostValidationFreezeError("validation status-event chain is broken")
        previous = supplied


def _canonical_validation_case_ids() -> list[str]:
    return [f"week4_case_{index:04d}" for index in range(25, 37)]


def _terminal_counts(outcomes: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    statuses = [row.get("adaptive_case_status") for row in outcomes.values()]
    winner = statuses.count("COMPLETE_WITH_WINNER")
    no_parent = statuses.count("NO_VALID_ADAPTIVE_PARENT")
    terminal = winner + no_parent
    return {
        "VALIDATION_PLANNED": VALIDATION_CASE_COUNT,
        "VALIDATION_TERMINAL": terminal,
        "VALIDATION_WITH_WINNER": winner,
        "VALIDATION_NO_VALID_ADAPTIVE_PARENT": no_parent,
        "VALIDATION_OTHER_FAILURES": len(statuses) - terminal,
    }


def validate_validation_evidence(runtime_root: Path, *, expected_source_hashes: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Validate immutable validation evidence without inspecting effect metrics."""
    root = Path(runtime_root)
    metadata = _load_json(root / "run_metadata.json", "validation run metadata")
    if metadata.get("stage") != "VALIDATION" or metadata.get("status") != "COMPLETED" or metadata.get("final_status") != "COMPLETED":
        raise PostValidationFreezeError("validation stage is not completed")
    if metadata.get("completed_case_count") != VALIDATION_CASE_COUNT or metadata.get("generation_invoked") is not True or metadata.get("d0_invoked") is not True or metadata.get("evaluator_invoked") is not False:
        raise PostValidationFreezeError("validation lifecycle is not a completed generation/D0-only stage")
    expected_cases = _canonical_validation_case_ids()
    outcomes: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "case_outcomes").glob("*.json")):
        row = _load_json(path, "validation case outcome")
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id in outcomes or row.get("split") != "validation":
            raise PostValidationFreezeError("validation terminal outcomes are malformed")
        outcomes[case_id] = row
    if sorted(outcomes) != expected_cases:
        raise PostValidationFreezeError("validation must contain exactly its 12 canonical terminal cases")
    counts = _terminal_counts(outcomes)
    if counts["VALIDATION_TERMINAL"] != VALIDATION_CASE_COUNT or counts["VALIDATION_OTHER_FAILURES"] != 0:
        raise PostValidationFreezeError("validation terminal counts are incomplete")
    try:
        ledger = CandidateLedger(root / "accounting" / "candidate_ledger.jsonl").records()
    except Exception as exc:
        raise PostValidationFreezeError("validation candidate ledger integrity failed") from exc
    if not ledger or {str(row.get("case_id")) for row in ledger} != set(expected_cases):
        raise PostValidationFreezeError("validation ledger does not bind exactly the validation cases")
    _verify_chain(root / "accounting" / "run_status_events.jsonl")
    for row in ledger:
        if row.get("detector_invoked") is not True:
            continue
        case_id, candidate_id = str(row["case_id"]), str(row["candidate_id"])
        sidecar = root / "sidecars" / case_id / f"{candidate_id.replace(':', '__')}.json"
        record = _load_json(sidecar, "validation sidecar")
        if record.get("candidate_id") != candidate_id or record.get("waveform_sha256") != row.get("candidate_waveform_sha256"):
            raise PostValidationFreezeError("validation sidecar and ledger disagree")
        wave_path = root / "waveforms" / case_id / "base_synthetic_16k.npy"
        if not wave_path.is_file() or canonical_waveform_sha256(np.load(wave_path, allow_pickle=False)) != record.get("base_synthetic_sha256"):
            raise PostValidationFreezeError("validation waveform evidence is missing or stale")
    supplied = metadata.get("authorization_source_sha256")
    if not isinstance(supplied, Mapping) or any(not isinstance(supplied.get(name), str) or not _HASH.fullmatch(str(supplied[name])) for name in VALIDATION_SOURCE_NAMES):
        raise PostValidationFreezeError("validation authorization source hashes are incomplete")
    if expected_source_hashes is not None:
        if {name: str(supplied.get(name, "")).upper() for name in expected_source_hashes} != {name: str(value).upper() for name, value in expected_source_hashes.items()}:
            raise PostValidationFreezeError("validation authorization source hashes are not current")
    else:
        for name in SCIENTIFIC_VALIDATION_SOURCE_NAMES:
            if sha256_file(CANONICAL_SOURCES[name]) != str(supplied[name]).upper():
                raise PostValidationFreezeError(f"validation scientific source changed after execution: {name}")
    return {"metadata": metadata, "case_ids": expected_cases, "outcomes": outcomes, "counts": counts, "ledger_rows": len(ledger), "validation_source_sha256": {name: str(supplied[name]).upper() for name in VALIDATION_SOURCE_NAMES}}


def _source_field(name: str) -> str:
    return f"VALIDATION_SOURCE_{name.upper()}_SHA256"


def freeze_fields_from_evidence(evidence: Mapping[str, Any]) -> dict[str, str]:
    """Render non-effect governance facts from already-validated evidence."""
    metadata, counts = evidence["metadata"], evidence["counts"]
    fields = dict(FREEZE_CLAIMS)
    fields.update({name: str(counts[name]) for name in COUNT_FIELDS})
    fields["VALIDATION_INVOCATION_ID"] = str(metadata.get("invocation_id", ""))
    fields["VALIDATION_AUTHORIZATION_SHA256"] = str(metadata.get("authorization_sha256", "")).upper()
    fields["VALIDATION_OUTPUT_NAMESPACE"] = str(metadata.get("output_namespace", ""))
    fields.update({_source_field(name): str(evidence["validation_source_sha256"][name]).upper() for name in VALIDATION_SOURCE_NAMES})
    validate_freeze_fields(fields)
    return fields


def build_freeze_record(runtime_root: Path, output_path: Path) -> dict[str, Any]:
    """Validate evidence and write a deterministic complete governance record."""
    evidence = validate_validation_evidence(runtime_root)
    fields = freeze_fields_from_evidence(evidence)
    order = [*FREEZE_CLAIMS, *COUNT_FIELDS, "VALIDATION_INVOCATION_ID", "VALIDATION_AUTHORIZATION_SHA256", "VALIDATION_OUTPUT_NAMESPACE"]
    order.extend(_source_field(name) for name in VALIDATION_SOURCE_NAMES)
    lines = ["# Week4 Post-Validation A0 Freeze", ""]
    lines.extend(f"{name} = {fields[name]}" for name in order)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return {
        "path": str(path), "sha256": sha256_file(path), "counts": dict(evidence["counts"]),
        "terminal_cases": evidence["counts"]["VALIDATION_TERMINAL"],
    }


def validate_freeze_fields(fields: Mapping[str, str]) -> dict[str, int]:
    """Validate the non-effect, 12-case post-validation eligibility contract."""
    required = set(FREEZE_CLAIMS) | set(COUNT_FIELDS) | {"VALIDATION_INVOCATION_ID", "VALIDATION_AUTHORIZATION_SHA256", "VALIDATION_OUTPUT_NAMESPACE"} | {_source_field(name) for name in VALIDATION_SOURCE_NAMES}
    missing = required - set(fields)
    if missing:
        raise PostValidationFreezeError(f"post-validation A0 freeze fields are missing: {sorted(missing)}")
    if any(str(fields.get(name)) != value for name, value in FREEZE_CLAIMS.items()):
        raise PostValidationFreezeError("post-validation A0 freeze claims are incomplete or changed")
    try:
        counts = {name: int(str(fields[name])) for name in COUNT_FIELDS}
    except (TypeError, ValueError) as exc:
        raise PostValidationFreezeError("post-validation A0 freeze counts are not integers") from exc
    if any(str(counts[name]) != str(fields[name]) or counts[name] < 0 for name in COUNT_FIELDS):
        raise PostValidationFreezeError("post-validation A0 freeze counts are malformed")
    if counts["VALIDATION_PLANNED"] != VALIDATION_CASE_COUNT or counts["VALIDATION_TERMINAL"] != VALIDATION_CASE_COUNT or counts["VALIDATION_OTHER_FAILURES"] != 0:
        raise PostValidationFreezeError("post-validation A0 freeze terminal counts are not eligible")
    if counts["VALIDATION_TERMINAL"] != counts["VALIDATION_WITH_WINNER"] + counts["VALIDATION_NO_VALID_ADAPTIVE_PARENT"] + counts["VALIDATION_OTHER_FAILURES"]:
        raise PostValidationFreezeError("post-validation A0 freeze terminal counts are inconsistent")
    if not str(fields["VALIDATION_INVOCATION_ID"]).strip() or not _HASH.fullmatch(str(fields["VALIDATION_AUTHORIZATION_SHA256"])):
        raise PostValidationFreezeError("post-validation A0 freeze invocation identity is invalid")
    if not str(fields["VALIDATION_OUTPUT_NAMESPACE"]).startswith("results/week4_adaptive_redteam_runs/"):
        raise PostValidationFreezeError("post-validation A0 freeze output namespace is invalid")
    if any(not _HASH.fullmatch(str(fields[_source_field(name)])) for name in VALIDATION_SOURCE_NAMES):
        raise PostValidationFreezeError("post-validation A0 freeze source identity is incomplete")
    return counts


def validate_freeze_record(path: Path, *, expected_invocation_id: str | None = None) -> dict[str, int]:
    """Accept only a complete, internally consistent post-validation record."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PostValidationFreezeError("post-validation A0 freeze record is missing") from exc
    fields: dict[str, str] = {}
    for line in lines:
        if " = " in line:
            key, value = line.split(" = ", 1)
            if key in fields:
                raise PostValidationFreezeError("post-validation A0 freeze has duplicate fields")
            fields[key] = value
    counts = validate_freeze_fields(fields)
    if expected_invocation_id is not None and fields["VALIDATION_INVOCATION_ID"] != expected_invocation_id:
        raise PostValidationFreezeError("post-validation A0 freeze invocation identity does not match")
    return counts
