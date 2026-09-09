"""Append-only Week3 attempt and final-accounting primitives."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FAILURE_CLASSES = frozenset({
    "infrastructure_transient", "infrastructure_terminal", "model_load_failure",
    "inference_failure", "invalid_output", "waveform_QA_failure",
    "sidecar_contract_failure", "integrity_failure",
})

FORMAL_PROVENANCE_FIELDS = (
    "run_id", "invocation_id", "authorization_sha256",
    "independent_review_sha256", "environment_manifest_sha256",
    "config_sha256", "case_table_sha256", "runner_sha256",
)

def classify_failure(exc: BaseException) -> str:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    explicit = {
        "invalid_output": "invalid_output",
        "inference_failure": "inference_failure",
        "waveform_qa_failure": "waveform_QA_failure",
        "sidecar_contract_failure": "sidecar_contract_failure",
        "integrity_failure": "integrity_failure",
    }
    for token, result in explicit.items():
        if token in msg:
            return result
    if "invalid sample rate" in msg or "invalid channel" in msg or "zero-length output" in msg or "empty generated waveform" in msg:
        return "invalid_output"
    if "invalid output waveform" not in msg and "invalid output" in msg:
        return "invalid_output"
    if getattr(exc, "retryable", False) or any(token in name + " " + msg for token in ("timeout", "temporarily", "connectionreset", "resource temporarily")):
        return "infrastructure_transient"
    if any(token in msg for token in ("model", "checkpoint", "asset")) and any(token in msg for token in ("load", "checkpoint", "asset")):
        return "model_load_failure"
    if any(token in msg for token in ("waveform", "peak", "finite", "sample rate")):
        return "waveform_QA_failure"
    if any(token in msg for token in ("sidecar", "schema", "contract")):
        return "sidecar_contract_failure"
    if any(token in msg for token in ("hash", "integrity")):
        return "integrity_failure"
    if any(token in name + " " + msg for token in ("infer", "generation")):
        return "inference_failure"
    return "infrastructure_terminal"

def append_attempt(path: Path, row: dict[str, Any]) -> None:
    if row.get("failure_class") and row["failure_class"] not in FAILURE_CLASSES:
        raise ValueError("unknown failure class")
    record = {"recorded_at": datetime.now(timezone.utc).isoformat(), **row}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

def validate_formal_attempt_provenance(row: dict[str, Any]) -> None:
    missing = [key for key in FORMAL_PROVENANCE_FIELDS if not row.get(key)]
    if missing:
        raise ValueError(f"formal attempt provenance missing: {missing}")

def terminal_history(attempts: list[dict[str, Any]], *, run_id: str | None = None) -> list[dict[str, Any]]:
    terminal = {"infrastructure_terminal", "model_load_failure", "inference_failure",
                "invalid_output", "waveform_QA_failure", "sidecar_contract_failure", "integrity_failure"}
    return [row for row in attempts if (run_id is None or row.get("run_id") == run_id)
            and row.get("failure_class") in terminal]

def final_accounting_rows(planned: list[dict[str, str]], attempts: list[dict[str, Any]], *, run_id: str | None = None) -> list[dict[str, Any]]:
    selected = [row for row in attempts if run_id is None or row.get("run_id") == run_id]
    histories: dict[str, list[dict[str, Any]]] = {}
    for row in selected:
        case_id = str(row["paired_case_id"])
        history = histories.setdefault(case_id, [])
        if history:
            prior = history[-1]
            if prior.get("status") != "FAILED" or prior.get("failure_class") != "infrastructure_transient":
                raise ValueError(f"attempt history has execution after terminal outcome: {case_id}")
            if len(history) >= 2:
                raise ValueError(f"attempt history exceeds one transient retry: {case_id}")
        history.append(row)
    by_case = {case_id: {**history[-1], "attempt_count": len(history), "retry_count": len(history) - 1}
               for case_id, history in histories.items()}
    return [{"paired_case_id": plan["paired_case_id"], "planned": True,
             "status": by_case.get(plan["paired_case_id"], {}).get("status", "NOT_EXECUTED"),
             **{key: value for key, value in by_case.get(plan["paired_case_id"], {}).items() if key in {"attempt_count", "retry_count", "failure_class", "failure_reason", "successful_waveform_path", "sidecar_path"}}} for plan in planned]

def write_cases_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["paired_case_id", "planned", "status", "attempt_count", "retry_count", "failure_class", "failure_reason", "successful_waveform_path", "sidecar_path"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
