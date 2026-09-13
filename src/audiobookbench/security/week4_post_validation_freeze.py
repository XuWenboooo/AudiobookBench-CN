"""Evidence-only post-validation A0 freeze gate for a future held-out run.

This module never imports F5, D0, search code, or an evaluator.  It verifies a
completed validation namespace and can emit the compact, deterministic record
that a later held-out authorization must cryptographically bind.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from audiobookbench.security.week4_adaptive import CandidateLedger, canonical_waveform_sha256
from audiobookbench.security.week4_authorization import CANONICAL_SOURCES, sha256_file


class PostValidationFreezeError(RuntimeError):
    """Raised if validation evidence cannot support an A0 freeze."""


FREEZE_CLAIMS = {
    "VALIDATION_STAGE_COMPLETE": "YES",
    "ATTACK_METHOD_CHANGED_AFTER_VALIDATION": "NO",
    "OBJECTIVE_CHANGED_AFTER_VALIDATION": "NO",
    "SEARCH_CHANGED_AFTER_VALIDATION": "NO",
    "QUERY_BUDGET_CHANGED_AFTER_VALIDATION": "NO",
    "EXECUTION_IMPLEMENTATION_CHANGED_AFTER_VALIDATION": "NO",
    "A0_FROZEN_FOR_HELD_OUT": "YES",
}


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
        import hashlib
        if not isinstance(supplied, str) or row.get("previous_record_sha256") != previous or hashlib.sha256(raw).hexdigest().upper() != supplied:
            raise PostValidationFreezeError("validation status-event chain is broken")
        previous = supplied


def _canonical_validation_case_ids() -> list[str]:
    return [f"week4_case_{index:04d}" for index in range(25, 37)]


def validate_validation_evidence(
    runtime_root: Path,
    *,
    expected_source_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate 12 terminal validation cases without inspecting any metrics."""
    root = Path(runtime_root)
    metadata = _load_json(root / "run_metadata.json", "validation run metadata")
    if metadata.get("stage") != "VALIDATION" or metadata.get("status") != "COMPLETED" or metadata.get("final_status") != "COMPLETED":
        raise PostValidationFreezeError("validation stage is not completed")
    if metadata.get("completed_case_count") != 12 or metadata.get("generation_invoked") is not True or metadata.get("d0_invoked") is not True or metadata.get("evaluator_invoked") is not False:
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
    for row in outcomes.values():
        if row.get("adaptive_case_status") not in {"COMPLETE_WITH_WINNER", "NO_VALID_ADAPTIVE_PARENT"}:
            raise PostValidationFreezeError("validation case lacks a valid terminal status")
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
    if expected_source_hashes is None:
        expected_source_hashes = {name: sha256_file(path) for name, path in CANONICAL_SOURCES.items()}
    if not isinstance(supplied, Mapping) or {name: str(supplied.get(name, "")).upper() for name in expected_source_hashes} != {name: str(value).upper() for name, value in expected_source_hashes.items()}:
        raise PostValidationFreezeError("validation authorization source hashes are not current")
    return {"metadata": metadata, "case_ids": expected_cases, "terminal_cases": len(outcomes), "ledger_rows": len(ledger)}


def build_freeze_record(runtime_root: Path, output_path: Path) -> dict[str, Any]:
    """Validate evidence and write the canonical claims to a caller-selected path."""
    evidence = validate_validation_evidence(runtime_root)
    metadata = evidence["metadata"]
    lines = ["# Week4 Post-Validation A0 Freeze", ""]
    lines.extend(f"{name} = {value}" for name, value in FREEZE_CLAIMS.items())
    lines.extend(["", f"VALIDATION_INVOCATION_ID = {metadata.get('invocation_id')}"])
    for name, value in sorted(dict(metadata["authorization_source_sha256"]).items()):
        lines.append(f"{name.upper()}_SHA256 = {value}")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return {"path": str(path), "sha256": sha256_file(path), "terminal_cases": evidence["terminal_cases"]}


def validate_freeze_record(path: Path) -> None:
    """Accept only an immutable-looking record with the seven frozen claims."""
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
    if {key: fields.get(key) for key in FREEZE_CLAIMS} != FREEZE_CLAIMS:
        raise PostValidationFreezeError("post-validation A0 freeze claims are incomplete or changed")
    if not isinstance(fields.get("VALIDATION_INVOCATION_ID"), str) or not fields["VALIDATION_INVOCATION_ID"]:
        raise PostValidationFreezeError("post-validation A0 freeze does not bind a validation invocation")
