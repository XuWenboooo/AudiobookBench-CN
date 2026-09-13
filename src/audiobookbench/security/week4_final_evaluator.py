"""Frozen evidence-only Week4 H4 evaluator for a committed held-out namespace."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audiobookbench.security.week4_adaptive import CandidateLedger
from audiobookbench.security.week4_execution import final_evaluate


class Week4FinalEvaluationError(RuntimeError):
    """Raised when held-out evidence is incomplete or internally inconsistent."""


def _read(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Week4FinalEvaluationError(f"{label} is unreadable") from exc
    if not isinstance(value, dict):
        raise Week4FinalEvaluationError(f"{label} is malformed")
    return value


def _case_ids() -> list[str]:
    return [f"week4_case_{index:04d}" for index in range(37, 49)]


def load_committed_held_out(runtime_root: Path) -> dict[str, dict[str, Any]]:
    """Read only verified held-out sidecars and selections; never invoke F5/D0/A0."""
    root = Path(runtime_root)
    metadata = _read(root / "run_metadata.json", "held-out run metadata")
    if metadata.get("stage") != "HELD_OUT" or metadata.get("status") != "COMPLETED" or metadata.get("final_status") != "COMPLETED":
        raise Week4FinalEvaluationError("held-out stage is not complete")
    if metadata.get("completed_case_count") != 12 or metadata.get("evaluator_invoked") is not False:
        raise Week4FinalEvaluationError("held-out evidence does not describe exactly 12 unevaluated cases")
    try:
        rows = CandidateLedger(root / "accounting" / "candidate_ledger.jsonl").records()
    except Exception as exc:
        raise Week4FinalEvaluationError("held-out candidate ledger integrity failed") from exc
    expected = _case_ids()
    if {str(row.get("case_id")) for row in rows} != set(expected):
        raise Week4FinalEvaluationError("held-out ledger does not bind exactly the frozen 12 cases")
    output: dict[str, dict[str, Any]] = {}
    for case_id in expected:
        outcome = _read(root / "case_outcomes" / f"{case_id}.json", "held-out case outcome")
        if outcome.get("case_id") != case_id or outcome.get("split") != "held_out":
            raise Week4FinalEvaluationError("held-out terminal outcome is malformed")
        static_rows = [row for row in rows if row.get("case_id") == case_id and row.get("phase") == "static_baseline" and row.get("detector_invoked") is True]
        if len(static_rows) != 1:
            raise Week4FinalEvaluationError("held-out case does not have exactly one static D0 record")
        static_id = str(static_rows[0]["candidate_id"])
        static = _read(root / "sidecars" / case_id / f"{static_id.replace(':', '__')}.json", "held-out static sidecar")
        if static.get("candidate_id") != static_id or static.get("waveform_sha256") != static_rows[0].get("candidate_waveform_sha256"):
            raise Week4FinalEvaluationError("held-out static sidecar disagrees with ledger")
        assembled: dict[str, Any] = {"static": static, "adaptive_case_status": outcome.get("adaptive_case_status")}
        if outcome.get("adaptive_case_status") == "COMPLETE_WITH_WINNER":
            selection = _read(root / "selections" / f"{case_id}.json", "held-out winner selection")
            selected_id = selection.get("selected_candidate_id")
            if not isinstance(selected_id, str) or selection.get("sidecar_sha256") is None:
                raise Week4FinalEvaluationError("held-out adaptive winner selection is incomplete")
            adaptive = _read(root / str(selection.get("sidecar_relpath", "")), "held-out adaptive sidecar")
            if adaptive.get("candidate_id") != selected_id:
                raise Week4FinalEvaluationError("held-out winner selection and sidecar disagree")
            assembled["adaptive"] = adaptive
        elif outcome.get("adaptive_case_status") != "NO_VALID_ADAPTIVE_PARENT":
            raise Week4FinalEvaluationError("held-out adaptive terminal status is invalid")
        output[case_id] = assembled
    return output


def evaluate_committed_held_out(runtime_root: Path, output_path: Path | None = None) -> dict[str, Any]:
    """Compute only frozen H4 quantities from previously committed evidence."""
    result = final_evaluate(load_committed_held_out(runtime_root))
    if output_path is not None:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return result
