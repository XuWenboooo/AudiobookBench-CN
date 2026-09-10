from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from audiobookbench.security.week3_accounting import (
    final_accounting_rows, validate_formal_attempt_provenance,
)
from audiobookbench.security import week3_pipeline as pipeline
from audiobookbench.security.week3_pipeline import run_formal_generation
from audiobookbench.security.week3_pipeline import canonical_run_root, _require_empty_clean_namespace, FrozenInputs


def _attempt(case: str, status: str, failure_class: str = "") -> dict[str, object]:
    return {"paired_case_id": case, "status": status, "failure_class": failure_class,
            "attempt_count": 1, "retry_count": 0}


def test_terminal_history_cannot_be_followed_by_execution() -> None:
    planned = [{"paired_case_id": "paircase_0001"}]
    with pytest.raises(ValueError, match="terminal outcome"):
        final_accounting_rows(planned, [_attempt("paircase_0001", "FAILED", "infrastructure_terminal"),
                                       _attempt("paircase_0001", "SUCCESS")])


def test_only_one_transient_retry_is_allowed() -> None:
    planned = [{"paired_case_id": "paircase_0001"}]
    rows = [_attempt("paircase_0001", "FAILED", "infrastructure_transient"),
            _attempt("paircase_0001", "SUCCESS")]
    assert final_accounting_rows(planned, rows)[0]["retry_count"] == 1
    with pytest.raises(ValueError, match="terminal outcome"):
        final_accounting_rows(planned, rows + [_attempt("paircase_0001", "SUCCESS")])


def test_formal_attempt_requires_complete_provenance() -> None:
    with pytest.raises(ValueError, match="provenance missing"):
        validate_formal_attempt_provenance({"run_id": "r", "invocation_id": "i"})


def test_current_legacy_authorization_is_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[1]
    # Do not depend on the live repository's post-run authorization state.
    # This remains the real production entrypoint and real validator path.
    monkeypatch.setattr(pipeline, "FUTURE_AUTH_REL", tmp_path / "authorization.json")
    with pytest.raises(RuntimeError, match="authorization artifact is missing|authorization source hash mismatch|identity missing"):
        run_formal_generation(root)


def test_future_evaluator_declares_source_and_f5_provenance() -> None:
    source = Path(__file__).resolve().parents[1] / "experiments/week3_stage_a_f5/evaluate.py"
    text = source.read_text(encoding="utf-8")
    assert '"evaluator_sha256"' in text
    assert '"f5_source_identity_sha256"' in text
    assert '"f5_local_source_manifest_sha256"' in text


def test_forensic_index_is_readable_and_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "results/week3_stage_a_f5/forensics/week3_attempt_lineage.json").read_text(encoding="utf-8"))
    assert len(data["invocations"]) == 5
    assert data["attempts"]["total"] == 115
    assert data["attempts"]["failure_rows"]["count"] == 46
    assert data["attempts"]["success_rows"]["count"] == 69


def test_run_id_derives_clean_namespace_and_rejects_traversal(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    assert canonical_run_root(root, "rerun_20260907") == (root / "results/week3_stage_a_f5_runs/rerun_20260907").resolve()
    with pytest.raises(RuntimeError, match="invalid run_id"):
        canonical_run_root(root, "../week3_stage_a_f5")


def test_historical_namespace_is_rejected_and_test_only_does_not_touch_it() -> None:
    root = Path(__file__).resolve().parents[1]
    historical = (root / "results/week3_stage_a_f5").resolve()
    with pytest.raises(RuntimeError, match="historical namespace"):
        _require_empty_clean_namespace(historical, root)


def test_existing_clean_namespace_is_fail_closed(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    clean = canonical_run_root(root, "fixture_empty_check")
    # Use an isolated temporary root to avoid touching the repository.
    clean = tmp_path / "results/week3_stage_a_f5_runs/fixture_empty_check"
    clean.mkdir(parents=True)
    (clean / "scientific_output_hashes.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="not empty"):
        _require_empty_clean_namespace(clean, tmp_path)


def test_formal_caller_cannot_override_authorized_run_namespace(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    from audiobookbench.security import week3_pipeline as pipeline
    inputs = FrozenInputs({"output_root": "ignored", "f5": {}}, [], "cfg", "env", pipeline._source_paths(root))
    auth = {"artifact_sha256": "AUTH", "run_id": "run_a", "invocation_id": "inv_a"}
    with pytest.raises(RuntimeError, match="authorized run namespace"):
        pipeline._execute_generation(root, inputs, auth, output_root=tmp_path / "arbitrary", test_only=False)


def test_evaluator_rejects_cross_run_binding() -> None:
    from experiments.week3_stage_a_f5.evaluate import validate_run_binding
    with pytest.raises(RuntimeError, match="run_id mismatch"):
        validate_run_binding([{"paired_case_id": "paircase_0001", "run_id": "run_b"}], "run_a")
