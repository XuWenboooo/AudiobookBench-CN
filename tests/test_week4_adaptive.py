from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import yaml

from audiobookbench.security.week4_adaptive import (
    ADAPTIVE_PHASE,
    BOOTSTRAP_N,
    BOOTSTRAP_SEED,
    MAX_ADAPTIVE_D0_QUERIES_PER_CASE,
    MIN_FINITE_BOOTSTRAPS,
    STATIC_PHASE,
    A0AttackController,
    AuthorizationError,
    CandidateLedger,
    DetectorQuery,
    DetectorOutcome,
    FreezeViolation,
    FrozenAttackSpec,
    LedgerError,
    QueryBudgetExceeded,
    SplitProtectionError,
    Week4ContractError,
    a0_freeze_sha256,
    canonical_waveform_sha256,
    paired_case_bootstrap,
)
from audiobookbench.security.week4_population import build_candidate_population


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = ROOT / "configs/week4_adaptive_red_team.yaml"


def _spec_mapping() -> dict[str, object]:
    return {
        "protocol": "WEEK4_ADAPTIVE_RED_TEAM_A0",
        "run_id": "TEST_ONLY_week4_run",
        "parameter_bounds": {"crossfade": [0.0, 4.0], "gain": [-4.0, 4.0]},
        "parameter_defaults": {"crossfade": 4.0, "gain": 0.0},
        "parameter_resolution": {"crossfade": 1.0, "gain": 1.0},
        "window_spec": {"name": "TEST_ONLY_window", "window_samples": 8, "hop_samples": 2},
        "score_direction": "higher_is_more_anomalous",
        "objective": {"name": "TEST_ONLY_J", "direction": "minimize"},
        "search_algorithm": {
            "population_size": 8, "generations": 5, "elite_count": 1,
            "mutation_scale_steps": 1, "total_max_queries": 40, "seed": 11,
            "initialization": "seeded_grid_without_replacement",
            "mutation": "seeded_symmetric_step_from_best_valid_candidate",
            "parent_selection": "lowest_objective_then_query_index",
            "duplicate_handling": "lexicographic_next_unseen_grid_point",
            "early_stopping": "none", "rng": "numpy_pcg64_seed_plus_case_sha256",
        },
        "splits": ["dev", "validation", "held_out"],
        "max_adaptive_d0_queries_per_case": MAX_ADAPTIVE_D0_QUERIES_PER_CASE,
        "bootstrap_n": BOOTSTRAP_N, "bootstrap_seed": BOOTSTRAP_SEED,
        "min_finite_bootstraps": MIN_FINITE_BOOTSTRAPS,
    }


def spec() -> FrozenAttackSpec:
    return FrozenAttackSpec.from_mapping(_spec_mapping())


def authorization(frozen: FrozenAttackSpec, split: str) -> dict[str, object]:
    return {"protocol": "WEEK4_ADAPTIVE_RED_TEAM_A0", "authorization_status": "ACTIVE", "run_id": frozen.run_id, "split": split, "spec_sha256": frozen.sha256(), "a0_freeze_sha256": a0_freeze_sha256(frozen), "ready": True}


def controller(tmp_path: Path, *, split: str = "dev", auth: dict[str, object] | None = None, detector=None):
    frozen, calls = spec(), []

    def default_detector(query: DetectorQuery) -> float:
        calls.append(query)
        return float(query.waveform[0])

    return A0AttackController(spec=frozen, authorization=authorization(frozen, split) if auth is None else auth, case_id="TEST_ONLY_case_0001", split=split, ledger=CandidateLedger(tmp_path / "candidate_ledger.jsonl"), detector=default_detector if detector is None else detector), calls


def evaluate_next(ctl: A0AttackController, score: float = 1.0):
    return ctl.evaluate_candidate(waveform=np.array([score], dtype=float), sample_rate=16000, params=ctl.next_candidate())


def test_canonical_config_is_schema_valid_and_loadable(tmp_path):
    frozen = FrozenAttackSpec.from_path(CANONICAL_CONFIG)
    assert frozen.window_spec.name == "S2_1500ms_250ms"
    assert frozen.max_adaptive_queries_per_case == 40
    assert frozen.objective_direction == "minimize"
    altered = yaml.safe_load(CANONICAL_CONFIG.read_text(encoding="utf-8"))
    altered["score_direction"] = "lower_is_more_anomalous"
    altered["unexpected_scientific_override"] = True
    path = tmp_path / "altered.yaml"
    path.write_text(yaml.safe_dump(altered, sort_keys=False), encoding="utf-8")
    with pytest.raises(Week4ContractError):
        FrozenAttackSpec.from_path(path)


def test_scientific_cli_override_is_rejected():
    import importlib.util
    module_path = ROOT / "experiments/week4_adaptive_red_team/run.py"
    loader = importlib.util.spec_from_file_location("week4_runner", module_path)
    assert loader and loader.loader
    module = importlib.util.module_from_spec(loader); loader.loader.exec_module(module)
    with pytest.raises(SystemExit):
        module.parse_args(["--score-direction", "lower_is_more_anomalous"])
    assert module.main(["--test-only"]) == 0
    with pytest.raises(RuntimeError):
        module.main([])


def test_static_and_adaptive_accounting_are_separate(tmp_path):
    ctl, calls = controller(tmp_path)
    ctl.evaluate_candidate(waveform=np.array([0.2]), sample_rate=16000, params=dict(ctl.spec.parameter_defaults), phase=STATIC_PHASE)
    evaluate_next(ctl, .4)
    assert ctl.accounting() == {"adaptive_detector_queries": 1, "static_baseline_detector_queries": 1, "max_adaptive_detector_queries": 40}
    assert len(calls) == 2


def test_query_1_to_40_allowed_41_rejected_and_restart_persists(tmp_path):
    ctl, calls = controller(tmp_path)
    for index in range(MAX_ADAPTIVE_D0_QUERIES_PER_CASE):
        evaluate_next(ctl, float(index + 1))
    restarted, restarted_calls = controller(tmp_path)
    with pytest.raises(QueryBudgetExceeded):
        restarted.evaluate_candidate(waveform=np.array([1.0]), sample_rate=16000, params=dict(restarted.spec.parameter_defaults))
    assert len(calls) == 40 and restarted_calls == []
    assert restarted.accounting()["adaptive_detector_queries"] == 40


def test_failed_invoked_query_is_counted_and_invalid_uninvoked_candidate_is_retained(tmp_path):
    def broken(_query: DetectorQuery) -> float:
        raise RuntimeError("synthetic detector failure")
    ctl, _ = controller(tmp_path, detector=broken)
    with pytest.raises(RuntimeError):
        evaluate_next(ctl)
    assert ctl.accounting()["adaptive_detector_queries"] == 1
    valid_detector_ctl, calls = controller(tmp_path / "invalid")
    proposal = valid_detector_ctl.next_candidate()
    row = valid_detector_ctl.evaluate_candidate(waveform=np.array([np.nan]), sample_rate=16000, params=proposal)
    assert row["valid"] is False and row["detector_query"] is False and row["params"] == proposal
    assert calls == []
    assert all(row["candidate_id"] for row in valid_detector_ctl.ledger.records())


def test_candidate_ledger_rows_include_replay_and_accounting_contract(tmp_path):
    ctl, _ = controller(tmp_path)
    proposal = ctl.next_candidate()
    row = ctl.evaluate_candidate(waveform=np.array([0.25]), sample_rate=16000, params=proposal)
    required = {"case_id", "generation", "parameters", "validity", "validity_reason", "candidate_waveform_sha256", "detector_invoked", "detector_outcome_hash", "selected_status", "parent_candidate", "previous_ledger_hash", "row_hash"}
    assert required.issubset(row)
    assert row["case_id"] == row["paired_case_id"] == ctl.case_id
    assert row["validity"] == "VALID" and row["detector_invoked"] is True
    assert row["selected_status"] == "NOT_SELECTED" and row["parent_candidate"] is None
    assert row["row_hash"] == row["record_sha256"] and row["previous_ledger_hash"] == ""


def test_ledger_is_append_only_hash_chained_and_detects_tamper(tmp_path):
    ledger = CandidateLedger(tmp_path / "ledger.jsonl")
    ledger.append({"candidate_id": "one"})
    ledger.append({"candidate_id": "two"})
    path = tmp_path / "ledger.jsonl"
    path.write_text(path.read_text(encoding="utf-8").replace('"candidate_id": "two"', '"candidate_id": "evil"'), encoding="utf-8")
    with pytest.raises(LedgerError):
        ledger.records()


def test_every_adaptive_proposal_is_unique_and_deterministic(tmp_path):
    first, _ = controller(tmp_path / "first")
    second, _ = controller(tmp_path / "second")
    first_proposals, second_proposals = [], []
    for score in range(8):
        first_proposals.append(first.next_candidate()); evaluate_next(first, float(score))
        second_proposals.append(second.next_candidate()); evaluate_next(second, float(score))
    assert first_proposals == second_proposals
    assert len({tuple(sorted(value.items())) for value in first_proposals}) == 8
    assert len({row["candidate_id"] for row in first.ledger.records()}) == 8


def test_search_depends_on_prior_detector_outcomes(tmp_path):
    left, _ = controller(tmp_path / "left")
    right, _ = controller(tmp_path / "right")
    for index in range(8):
        evaluate_next(left, 0.0 if index == 0 else 10.0)
        evaluate_next(right, 0.0 if index == 1 else 10.0)
    assert left.next_candidate() != right.next_candidate()


def test_mixed_generation_zero_uses_the_only_defined_parent_and_reaches_40_queries(tmp_path):
    calls: list[DetectorQuery] = []

    def mixed_detector(query: DetectorQuery) -> DetectorOutcome:
        calls.append(query)
        if len(calls) <= 7:
            return DetectorOutcome(None, "OBJECTIVE_UNDEFINED")
        return DetectorOutcome(0.5 if len(calls) == 8 else 1.0, "DEFINED")

    ctl, _ = controller(tmp_path, detector=mixed_detector)
    rows = []
    for _ in range(MAX_ADAPTIVE_D0_QUERIES_PER_CASE):
        proposal = ctl.next_candidate()
        rows.append(ctl.evaluate_candidate(waveform=np.array([0.25], dtype=np.float32), sample_rate=16000, params=proposal))
    eighth = rows[7]["candidate_id"]
    assert len(calls) == len(rows) == MAX_ADAPTIVE_D0_QUERIES_PER_CASE
    assert [row["objective_status"] for row in rows[:7]] == ["OBJECTIVE_UNDEFINED"] * 7
    assert rows[7]["objective_status"] == "DEFINED"
    assert all(row["parent_candidate"] == eighth for row in rows[8:])
    assert all(row["valid_for_winner"] is True for row in rows[7:])


def test_canonical_waveform_hash_normalizes_dtype_and_memory_layout():
    waveform = np.asarray([0.1, -0.2, 0.3, -0.4], dtype=np.float32)
    noncontiguous = np.column_stack([waveform, waveform])[:, 0]
    assert not noncontiguous.flags.c_contiguous
    expected = canonical_waveform_sha256(waveform)
    assert expected == canonical_waveform_sha256(noncontiguous)
    assert expected == canonical_waveform_sha256(waveform.astype(np.float64))


def test_missing_wrong_authorization_wrong_split_and_heldout_tuning_fail_closed(tmp_path):
    ctl, calls = controller(tmp_path)
    ctl.authorization = None
    with pytest.raises(AuthorizationError):
        ctl.next_candidate()
    assert calls == []
    frozen = spec(); bad = authorization(frozen, "dev"); bad["run_id"] = "wrong"
    wrong, _ = controller(tmp_path / "wrong", auth=bad)
    with pytest.raises(AuthorizationError):
        wrong.next_candidate()
    split_mismatch = authorization(frozen, "validation")
    wrong_split, _ = controller(tmp_path / "wrong_split", auth=split_mismatch)
    with pytest.raises(AuthorizationError):
        wrong_split.next_candidate()
    hash_mismatch = authorization(frozen, "dev"); hash_mismatch["spec_sha256"] = "0" * 64
    wrong_hash, _ = controller(tmp_path / "wrong_hash", auth=hash_mismatch)
    with pytest.raises(AuthorizationError):
        wrong_hash.next_candidate()
    freeze_mismatch = authorization(frozen, "dev"); freeze_mismatch["a0_freeze_sha256"] = "f" * 64
    wrong_freeze, _ = controller(tmp_path / "wrong_freeze", auth=freeze_mismatch)
    with pytest.raises(AuthorizationError):
        wrong_freeze.next_candidate()
    held, held_calls = controller(tmp_path / "held", split="held_out")
    with pytest.raises(SplitProtectionError):
        held.evaluate_candidate(waveform=np.array([.1]), sample_rate=16000, params=dict(held.spec.parameter_defaults), phase="tuning")
    assert held_calls == []
    # A frozen adaptive execution itself is allowed on held-out, while tuning is not.
    evaluate_next(held, .2)


def test_a0_freeze_score_direction_and_manual_candidate_changes_fail_closed(tmp_path):
    ctl, _ = controller(tmp_path)
    with pytest.raises(FreezeViolation):
        ctl.set_method("A1")
    expected = ctl.next_candidate()
    manual = dict(expected); manual["gain"] = 0.0 if expected["gain"] != 0.0 else 1.0
    with pytest.raises(FreezeViolation):
        ctl.evaluate_candidate(waveform=np.array([.2]), sample_rate=16000, params=manual)
    invalid = _spec_mapping(); invalid["score_direction"] = "lower_is_more_anomalous"
    with pytest.raises(Week4ContractError):
        FrozenAttackSpec.from_mapping(invalid)


def test_invalid_candidate_cannot_be_selected_as_adaptive_elite(tmp_path):
    ctl, _ = controller(tmp_path)
    proposal = ctl.next_candidate()
    ctl.evaluate_candidate(waveform=np.array([np.nan]), sample_rate=16000, params=proposal)
    for score in range(8):
        evaluate_next(ctl, float(score + 1))
    elite = ctl._best_valid()
    assert elite["valid"] is True
    assert elite["status"] == "VALID"


def test_paired_bootstrap_is_fixed_to_case_unit_2000_and_1900():
    result = paired_case_bootstrap({"a": [1.0, 2.0], "b": [3.0, 4.0]})
    assert result["unit"] == "paired_case_id" and result["requested"] == 2000 and result["finite"] == 2000
    for kwargs in ({"n": 1999}, {"seed": 7}, {"min_finite": 1899}):
        with pytest.raises(Week4ContractError):
            paired_case_bootstrap({"a": 1.0, "b": 2.0}, **kwargs)


def _candidate_rows(count: int = 49) -> list[dict[str, object]]:
    return [{"speaker": f"speaker_{index:03d}", "source_speaker": f"speaker_{index:03d}", "reference_speaker": f"speaker_{index:03d}", "source_sample_id": f"source_{index:03d}", "reference_sample_id": f"reference_{index:03d}", "source_text_sha256": "a" * 64, "reference_text_sha256": "b" * 64, "source_audio_sha256": "c" * 64, "reference_audio_sha256": "d" * 64, "same_speaker": True, "different_utterance": True, "different_text": True, "eligible": True} for index in range(count)]


def test_population_builder_is_deterministic_speaker_disjoint_and_outcome_blind():
    rows = _candidate_rows(); rows[0]["speaker"] = rows[0]["source_speaker"] = rows[0]["reference_speaker"] = "prior"
    first = build_candidate_population(rows, selection_seed=20260912, prior_week_speakers={"prior"})
    second = build_candidate_population(rows, selection_seed=20260912, prior_week_speakers={"prior"})
    assert first == second
    assert first["status"] == "CANDIDATE_POPULATION_REQUIRES_INDEPENDENT_ELIGIBILITY_REVIEW"
    assert len(first["selected_cases"]) == 48
    assert len({row["speaker"] for row in first["selected_cases"]}) == 48
    assert first["split_counts"] == {"dev": 24, "validation": 12, "held_out": 12}
    assert any(row["reason"] == "prior_week_speaker_overlap" for row in first["exclusions"])


def test_week3_closure_and_aishell3_are_read_only_during_week4_fixture_work():
    closure = ROOT / "research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md"
    expected = "24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C"
    aishell = ROOT.parent / "datasets/AISHELL-3"
    before_hash = hashlib.sha256(closure.read_bytes()).hexdigest().upper()
    before_aishell_mtime = aishell.stat().st_mtime_ns
    build_candidate_population(_candidate_rows(), selection_seed=20260912, prior_week_speakers={"not_present"})
    assert hashlib.sha256(closure.read_bytes()).hexdigest().upper() == before_hash == expected
    assert aishell.stat().st_mtime_ns == before_aishell_mtime
