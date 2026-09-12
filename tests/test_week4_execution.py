from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.week4_adaptive import CandidateLedger, FrozenAttackSpec, Week4ContractError
from audiobookbench.security.week4_execution import (
    SAMPLE_RATE, active_interval, attacker_objective, construct_candidate,
    execute_protocol, project_gt, trim_synthetic, vector_record,
)


ROOT = Path(__file__).resolve().parents[1]


def test_supplement_schema_and_exact_waveform_contract():
    import jsonschema
    import yaml
    supplement = yaml.safe_load((ROOT / "configs/week4_execution_supplement_v1.yaml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "configs/week4_execution_supplement_v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(supplement)
    source = np.full(48000, 0.1, dtype=np.float32)
    synthetic = np.full(4000, 0.2, dtype=np.float32)
    built = construct_candidate(source, synthetic, crossfade_samples=400, gain_db=0.0)
    p, f = built.insertion_sample, built.crossfade_samples
    assert built.gt["attack"] == (p - f, p + synthetic.size - f)
    assert built.gt["core"] == (p, p + synthetic.size - 2 * f)
    alpha = 1.0 / (f + 1)
    assert np.isclose(built.waveform[p - f], source[p - f] * (1 - alpha) + synthetic[0] * alpha)
    assert active_interval(source) == (0, 47920)
    assert trim_synthetic(np.r_[np.zeros(1600), synthetic, np.zeros(1600)], SAMPLE_RATE).size >= synthetic.size


def test_objective_excludes_partial_windows_and_invalid_peak():
    source = np.full(64000, 0.1, dtype=np.float32)
    synthetic = np.full(32000, 0.2, dtype=np.float32)
    built = construct_candidate(source, synthetic, crossfade_samples=400, gain_db=0.0)
    projection = project_gt(built.waveform, built.gt)
    scores = np.arange(len(projection), dtype=np.float64)
    assert np.isfinite(attacker_objective(scores, projection))
    partial = [r for r in projection if 0 < r["attack_overlap_ratio"] < 0.5]
    assert partial and all(not r["FULL_ATTACK"] and not r["OUTSIDE_CLEAN"] for r in partial)
    try:
        construct_candidate(source, np.ones(32000, dtype=np.float32), crossfade_samples=400, gain_db=3.0)
    except RuntimeError as exc:
        assert "INVALID_BEFORE_D0_peak" in str(exc)
    else:
        raise AssertionError("over-peak candidate must fail before D0")


class _FakeD0:
    def __init__(self):
        self.calls = 0

    def embed_windows(self, waveform, windows):
        self.calls += 1
        rows = []
        for i, (lo, hi) in enumerate(windows):
            row = np.zeros(192, dtype=np.float32)
            row[i % 192] = 1.0
            row[(i + 1) % 192] = float(np.mean(waveform[lo:hi]))
            rows.append(row)
        return np.asarray(rows, dtype=np.float32)


def test_only_full_e2e_dev_validation_freeze_heldout_final(tmp_path: Path, monkeypatch):
    # Candidate-sidecar serialization itself is covered below.  Keeping this
    # 48×41 control-plane proof in memory makes it practical as a unit test.
    import audiobookbench.security.week4_execution as execution
    monkeypatch.setattr(execution, "_persist_candidate", lambda _root, record: dict(record, sidecar_relpath="TEST_ONLY", sidecar_sha256="TEST_ONLY"))
    spec = FrozenAttackSpec.from_path(ROOT / "configs/week4_adaptive_red_team.yaml")
    cases = []
    for i in range(1, 49):
        cases.append({"case_id": f"week4_case_{i:04d}", "split": "dev" if i <= 24 else "validation" if i <= 36 else "held_out", "source_text_exact": "源文本", "reference_text_exact": "参考文本"})
    seeds: list[int] = []
    def fake_f5(case, seed):
        seeds.append(seed)
        return np.full(32000, 0.2, dtype=np.float32), SAMPLE_RATE
    backend = _FakeD0()
    result = execute_protocol(cases=cases, spec=spec, runtime_root=tmp_path / "TEST_ONLY", f5_generator=fake_f5, d0_backend=backend, source_loader=lambda _: np.full(64000, 0.1, dtype=np.float32))
    assert seeds == list(range(20260914, 20260962))
    assert result["A0_FROZEN"] is True
    assert result["final"]["PRIMARY_H4"] == "REPORTABLE"
    assert result["final"]["paired_bootstrap"]["auroc"]["finite"] >= 1900
    assert len(result["ledger"]) == 48 * 41
    assert all(row["candidate_id"] for row in result["ledger"])
    assert backend.calls == len(result["ledger"])
    assert result["ACTUAL_D0_BACKEND_CALLS"] == result["ACCOUNTED_D0_INVOCATIONS"] == backend.calls
    metadata = json.loads((tmp_path / "TEST_ONLY/run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["status"] == metadata["final_status"] == "COMPLETED"
    assert metadata["generation_invoked"] is True and metadata["d0_invoked"] is True and metadata["evaluator_invoked"] is True
    assert metadata["completed_case_count"] == 48
    assert (tmp_path / "TEST_ONLY/accounting/run_status_events.jsonl").is_file()
    assert (tmp_path / "TEST_ONLY/final.json").is_file()


def test_only_no_parent_is_case_terminal_and_next_dev_case_starts(tmp_path: Path):
    """The observed 9-window/6-attack/0-clean geometry is control-flow only."""
    import audiobookbench.security.week4_execution as execution
    spec = FrozenAttackSpec.from_path(ROOT / "configs/week4_adaptive_red_team.yaml")
    cases = [{"case_id": f"week4_case_{i:04d}", "split": "dev" if i <= 24 else "validation" if i <= 36 else "held_out", "source_text_exact": "源文本", "reference_text_exact": "参考文本"} for i in range(1, 49)]
    backend = _FakeD0()
    # 38,336 source samples and 21,200 synthetic samples reproduce the stored
    # case-0004 S2 geometry without using its waveform or score magnitude.
    def fake_f5(case, _seed):
        samples = 21200 if case["case_id"] == "week4_case_0001" else 32000
        return np.full(samples, 0.2, dtype=np.float32), SAMPLE_RATE

    def fake_source(case):
        samples = 38336 if case["case_id"] == "week4_case_0001" else 64000
        return np.full(samples, 0.1, dtype=np.float32)

    result = execute_protocol(cases=cases, spec=spec, runtime_root=tmp_path / "TEST_ONLY_UNDEFINED", f5_generator=fake_f5, d0_backend=backend, source_loader=fake_source, stage="dev")
    root = tmp_path / "TEST_ONLY_UNDEFINED"
    rows = [row for row in CandidateLedger(root / "accounting/candidate_ledger.jsonl").records() if row["case_id"] == "week4_case_0001"]
    static = next(row for row in rows if row["phase"] == "static_baseline")
    adaptive = [row for row in rows if row["phase"] == "adaptive_search"]
    assert len(rows) == 9
    assert static["detector_status"] == "SUCCESS"
    assert static["objective_status"] == "NOT_APPLICABLE"
    assert static["valid_for_winner"] is False
    assert len(adaptive) == 8 and all(row["objective_status"] == "OBJECTIVE_UNDEFINED" for row in adaptive)
    assert all(row["detector_status"] == "SUCCESS" and row["valid_for_winner"] is False for row in adaptive)
    static_sidecar = next((root / "sidecars/week4_case_0001").glob("*static_baseline*.json"))
    static_record = json.loads(static_sidecar.read_text(encoding="utf-8"))
    assert static_record["score_vector"] and static_record["objective_status"] == "NOT_APPLICABLE"
    assert static["candidate_waveform_sha256"] == static_record["waveform_sha256"]
    outcome = json.loads((root / "case_outcomes/week4_case_0001.json").read_text(encoding="utf-8"))
    assert outcome == {
        "adaptive_case_status": "NO_VALID_ADAPTIVE_PARENT",
        "adaptive_d0_queries_consumed": 8,
        "adaptive_search_terminal": True,
        "adaptive_winner": "NONE",
        "case_id": "week4_case_0001",
        "remaining_adaptive_queries_status": "NOT_EXECUTED_STRUCTURALLY_UNAVAILABLE",
        "split": "dev",
    }
    metadata = json.loads((root / "run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["status"] == metadata["final_status"] == "COMPLETED"
    assert metadata["completed_case_count"] == 24
    assert result["accounting"]["DEV_CASE_TERMINAL_NO_VALID_ADAPTIVE_PARENT"] == 1
    assert result["accounting"]["CASES_WITH_STRUCTURAL_NO_VALID_PARENT"] == 1
    assert backend.calls == len(result["ledger"])
    events = [json.loads(line) for line in (root / "accounting/run_status_events.jsonl").read_text(encoding="utf-8").splitlines()]
    terminal = next(index for index, event in enumerate(events) if event["event"] == "CASE_TERMINAL_NO_VALID_ADAPTIVE_PARENT")
    assert any(event["event"] == "CASE_STARTED" and event["case_id"] == "week4_case_0002" for event in events[terminal + 1:])


def test_only_full_e2e_retains_no_parent_cases_and_makes_h4_not_reportable(tmp_path: Path, monkeypatch):
    import audiobookbench.security.week4_execution as execution
    monkeypatch.setattr(execution, "_persist_candidate", lambda _root, record: dict(record, sidecar_relpath="TEST_ONLY", sidecar_sha256="TEST_ONLY"))
    spec = FrozenAttackSpec.from_path(ROOT / "configs/week4_adaptive_red_team.yaml")
    cases = [{"case_id": f"week4_case_{i:04d}", "split": "dev" if i <= 24 else "validation" if i <= 36 else "held_out", "source_text_exact": "源文本", "reference_text_exact": "参考文本"} for i in range(1, 49)]
    no_parent = {"week4_case_0001", "week4_case_0025", "week4_case_0037"}
    backend = _FakeD0()

    def fake_f5(case, _seed):
        return np.full(21200 if case["case_id"] in no_parent else 32000, 0.2, dtype=np.float32), SAMPLE_RATE

    def fake_source(case):
        return np.full(38336 if case["case_id"] in no_parent else 64000, 0.1, dtype=np.float32)

    result = execute_protocol(cases=cases, spec=spec, runtime_root=tmp_path / "TEST_ONLY_ALL_NO_PARENT", f5_generator=fake_f5, d0_backend=backend, source_loader=fake_source)
    assert len(result["per_case"]) == 48
    assert all(result["per_case"][case_id]["adaptive_case_status"] == "NO_VALID_ADAPTIVE_PARENT" for case_id in no_parent)
    assert result["final"] == {"PRIMARY_H4": "NOT_REPORTABLE", "reason": "HELD_OUT_NOT_12_OF_12_PAIRED_COMPLETE"}
    assert len(result["ledger"]) == backend.calls == (45 * 41 + 3 * 9)
    metadata = json.loads((tmp_path / "TEST_ONLY_ALL_NO_PARENT/run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["final_status"] == "COMPLETED" and metadata["completed_case_count"] == 48
    assert metadata["evaluator_invoked"] is True


def test_vector_sidecar_is_committed_with_raw_score_hash(tmp_path: Path):
    from audiobookbench.security.week4_adaptive import canonical_waveform_sha256
    from audiobookbench.security.week4_execution import _persist_candidate
    waveform = np.full(24000, 0.1, dtype=np.float32)
    rows = project_gt(waveform, {"attack": (0, 12000), "core": (400, 11600), "blend_in": (0, 400), "blend_out": (11600, 12000)})
    record = vector_record(case_id="week4_case_0001", candidate_id="TEST_ONLY:static:000000", waveform=waveform, scores=np.array([0.25]), windows=[{k: v for k, v in rows[0].items() if k not in {"FULL_ATTACK", "OUTSIDE_CLEAN", "attack_overlap_ratio"}}], projection=rows)
    committed = _persist_candidate(tmp_path, record)
    path = tmp_path / committed["sidecar_relpath"]
    assert path.is_file() and committed["sidecar_sha256"]
    assert json.loads(path.read_text(encoding="utf-8"))["score_vector_sha256"] == record["score_vector_sha256"]
    noncontiguous = np.column_stack([waveform, waveform])[:, 0]
    assert not noncontiguous.flags.c_contiguous
    assert canonical_waveform_sha256(waveform) == canonical_waveform_sha256(noncontiguous)
    assert canonical_waveform_sha256(waveform) == canonical_waveform_sha256(waveform.astype(np.float64))
    assert record["waveform_sha256"] == canonical_waveform_sha256(waveform)
