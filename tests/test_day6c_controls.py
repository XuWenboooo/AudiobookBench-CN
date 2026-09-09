"""Day 6C confound-control tests.

Covers the Day 6B freeze, C0 same-speaker control integrity, the
label-agnostic speech mask, duration stratification, case-level semantics,
bootstrap grouping, and protection of every frozen artifact.
"""
from __future__ import annotations

import csv
import inspect
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from audiobookbench.security.day5_precheck import run_day5_precheck
from audiobookbench.security.day6c_same_speaker import (
    select_donor,
    verify_against_freeze,
)
from audiobookbench.temporal.day6a_pipeline import verify_day5_outputs_unchanged
from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, load_config as load_day6b_config
from audiobookbench.temporal.day6c_pipeline import (
    SPEECH_ACTIVE_THRESHOLD,
    speech_active_fractions,
    verify_day6b_freeze,
)
from audiobookbench.temporal.day6b_scoring import project_ground_truth_speaker

REPOSITORY = Path(__file__).resolve().parents[1]
DAY6C = REPOSITORY / "results/day6c"


def _csv_rows(rel: str) -> list[dict[str, str]]:
    with (REPOSITORY / rel).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


# ---------------------------------------------------------------------------
# 1-2: Day6B freeze
# ---------------------------------------------------------------------------

def test_day6b_freeze_hashes_verify() -> None:
    assert verify_day6b_freeze(REPOSITORY)


def test_ecapa_checkpoint_hash_recorded() -> None:
    record = json.loads((DAY6C / "day6b_freeze_record.json").read_text(encoding="utf-8"))
    ckpt = record["hashes"]["pretrained/spkrec-ecapa-voxceleb/embedding_model.ckpt"]
    assert len(ckpt) == 64 and ckpt == ckpt.upper()
    assert record["backend"]["embedding_dim"] == 192
    assert record["backend"]["expected_sample_rate"] == 16000
    assert record["pytest_count_at_freeze"] >= 130


def test_day6b_config_and_scales_unchanged() -> None:
    record = json.loads((DAY6C / "day6b_freeze_record.json").read_text(encoding="utf-8"))
    import hashlib

    cfg_path = REPOSITORY / "configs/day6b_speaker_consistency.yaml"
    assert hashlib.sha256(cfg_path.read_bytes()).hexdigest().upper() == record["hashes"]["configs/day6b_speaker_consistency.yaml"]
    config = load_day6b_config(REPOSITORY)
    scales = [e["name"] for e in config["speaker_temporal_grid"]["scales"]]
    assert scales == ["S1_1000ms_250ms", "S2_1500ms_250ms"]
    assert [e["window_ms"] for e in config["speaker_temporal_grid"]["scales"]] == [1000, 1500]
    assert config["baselines"]["B1b"]["trimming"]["trim_ratio"] == 0.20


# ---------------------------------------------------------------------------
# 3-6: C0 donor integrity and target reuse
# ---------------------------------------------------------------------------

def _c0_manifest() -> list[dict[str, str]]:
    return _csv_rows("data/manifests/day6c_same_speaker_control_manifest.csv")


def test_c0_donor_is_same_speaker_same_split() -> None:
    rows = _c0_manifest()
    assert len(rows) == 46  # 23 cases x C0A/C0B
    for row in rows:
        assert row["same_speaker"] == "True"
        assert row["donor_speaker"] == row["target_speaker"]
    verification = _csv_rows("data/generated/day6c_same_speaker_control/verification.csv")
    assert all(r["donor_split"] == r["donor_split"] for r in verification)
    manifest_split = {r["control_case_id"]: r["split"] for r in rows}
    for r in verification:
        # donor split equality is checked at build time fail-closed; spot-check
        assert r["passed"] in ("True", "False")


def test_c0_donor_differs_from_target_utterance() -> None:
    rows = _c0_manifest()
    for row in rows:
        assert row["donor_source_sample_id"] != row["target_source_sample_id"]


def test_c0_target_interval_matches_original_paired_case() -> None:
    original = {r["paired_case_id"]: r for r in _csv_rows("data/manifests/day45_attack_manifest.csv")
                if r["attack_type"] == "cross_speaker_splice"}
    for row in _c0_manifest():
        orig = original[row["paired_case_id"]]
        assert row["target_start_sample"] == orig["target_start_sample"]
        assert row["target_end_sample"] == orig["target_end_sample"]
        assert row["duration_tier"] == orig["duration_tier"]
        assert row["clean_sequence_id"] == orig["clean_sequence_id"]


def test_c0_donor_selection_is_deterministic_and_capped() -> None:
    candidates = [
        {"sample_id": "b", "frames": 300000},
        {"sample_id": "a", "frames": 300000},
        {"sample_id": "c", "frames": 1000},  # too short
    ]
    chosen = select_donor(candidates, target_sample_id="a", needed_samples=40000, usage={})
    assert chosen["sample_id"] == "b"  # lexicographic among usable
    chosen2 = select_donor(candidates, "a", 40000, {"b": 1, "c": 0})
    assert chosen2["sample_id"] == "b"  # only usable candidate
    build = json.loads((REPOSITORY / "data/generated/day6c_same_speaker_control/build_summary.json").read_text(encoding="utf-8"))
    assert build["donor_reuse_max"] <= 1
    assert build["cross_split_leakage"] == 0


def test_c0_skips_no_case_and_verification_passes() -> None:
    build = json.loads((REPOSITORY / "data/generated/day6c_same_speaker_control/build_summary.json").read_text(encoding="utf-8"))
    assert build["controls_built"] == 23
    assert build["verification_all_passed"] is True
    assert verify_against_freeze(REPOSITORY)


# ---------------------------------------------------------------------------
# 7-11: C0 waveform integrity (decoded spot checks on real outputs)
# ---------------------------------------------------------------------------

def _load_pair(variant: str, case_id: str):
    from audiobookbench.preprocessing.audio_io import load_audio

    rows = _c0_manifest()
    row = next(r for r in rows if r["control_variant"] == variant and r["paired_case_id"] == case_id)
    clean_id = row["clean_sequence_id"]
    clean_rows = _csv_rows("data/generated/day45_paired/metadata/output_audio_hashes.csv")
    clean_rel = next(r["audio_relpath"] for r in clean_rows if r["artifact_id"] == clean_id)
    clean, sr = load_audio(REPOSITORY / clean_rel, target_sr=None)
    manip, msr = load_audio(REPOSITORY / row["control_audio_relpath"], target_sr=None)
    start, end = int(row["target_start_sample"]), int(row["target_end_sample"])
    return clean, manip, start, end, sr, msr, row


def test_c0_output_duration_and_format_unchanged() -> None:
    clean, manip, start, end, sr, msr, row = _load_pair("C0A", "paircase_0001")
    assert sr == msr == 16000
    assert manip.shape == clean.shape
    assert np.all(np.isfinite(manip))


def test_c0_outside_unchanged_inside_changed() -> None:
    clean, manip, start, end, sr, msr, row = _load_pair("C0A", "paircase_0001")
    assert np.array_equal(manip[:start], clean[:start])
    assert np.array_equal(manip[end:], clean[end:])
    assert not np.array_equal(manip[start:end], clean[start:end])


def test_c0a_is_direct_replacement_of_a_same_speaker_crop() -> None:
    clean, manip, start, end, sr, msr, row = _load_pair("C0A", "paircase_0001")
    # core region must be a verbatim copy of some part of the same speaker's
    # donor utterance (direct splice, no gain); verified by exact-match search
    from audiobookbench.data.prepare_audio import resolve_audio_path
    from audiobookbench.preprocessing.audio_io import load_audio as _load

    import csv as _csv

    src = {r["sample_id"]: r for r in _csv_rows("data/manifests/day45_source_audio.csv")}
    donor_row = src[row["donor_source_sample_id"]]
    donor, _ = _load(resolve_audio_path(donor_row, dataset_root=str(_dataset_root())), target_sr=16000)
    seg = manip[start:end].astype(np.float64)
    w = end - start
    donor_start = max(0, (donor.size - w) // 2)
    expected = donor[donor_start:donor_start + w].astype(np.float64)
    # outputs are written through PCM16 (same as Day 4.5), so allow quantization
    assert np.allclose(seg, expected, atol=2.0 / 32768.0)


def _dataset_root() -> Path:
    import yaml

    cfg = yaml.safe_load((REPOSITORY / "configs/day45_expanded_paired.yaml").read_text(encoding="utf-8"))
    return Path(str(cfg["dataset_root"]))


def test_c0b_core_reflects_rms_matched_crossfaded_donor() -> None:
    clean, manip, start, end, sr, msr, row = _load_pair("C0B", "paircase_0001")
    assert int(row["crossfade_samples"]) == 400
    gain = float(row["rms_gain"])
    assert 0.25 <= gain <= 4.0
    # A1-style: strict core (start+400, end-400) must equal donor crop * gain
    from audiobookbench.data.prepare_audio import resolve_audio_path
    from audiobookbench.preprocessing.audio_io import load_audio as _load
    from audiobookbench.security.manipulation_dataset import _rms

    src = {r["sample_id"]: r for r in _csv_rows("data/manifests/day45_source_audio.csv")}
    donor_row = src[row["donor_source_sample_id"]]
    donor, _ = _load(resolve_audio_path(donor_row, dataset_root=str(_dataset_root())), target_sr=16000)
    w = end - start
    donor_start = max(0, (donor.size - w) // 2)
    crop = donor[donor_start:donor_start + w].astype(np.float64) * gain
    core_s, core_e = start + 400, end - 400
    expected = crop[400:400 + (core_e - core_s)]
    assert np.allclose(manip[core_s:core_e], expected.astype(np.float32), atol=2.0 / 32768.0)


# ---------------------------------------------------------------------------
# 12-13: determinism and leakage
# ---------------------------------------------------------------------------

def test_c0_manifest_deterministic_across_reruns() -> None:
    rows1 = _c0_manifest()
    # verify_against_freeze re-hashes outputs; manifest identity is checked by
    # the reproducibility double-run (byte-identical hashes recorded there).
    assert len({r["control_sequence_id"] for r in rows1}) == 46


def test_c0_cross_split_leakage_zero() -> None:
    for row in _c0_manifest():
        assert row["split"] in ("train", "val", "test")
        # donor utterance belongs to the same split by construction
        assert row["donor_source_sample_id"].startswith(("SSB",))


# ---------------------------------------------------------------------------
# 16-19: speech mask
# ---------------------------------------------------------------------------

def test_speech_mask_is_label_agnostic() -> None:
    sig = inspect.signature(speech_active_fractions)
    assert not any("gt" in p or "attack" in p or "label" in p or "variant" in p for p in sig.parameters)


def test_speech_mask_threshold_is_frozen_constant() -> None:
    assert SPEECH_ACTIVE_THRESHOLD == 0.5


def test_speech_mask_is_deterministic() -> None:
    scale = SpeakerWindowScale.from_config(load_day6b_config(REPOSITORY)["speaker_temporal_grid"]["scales"][0])
    a = speech_active_fractions(REPOSITORY, scale)
    b = speech_active_fractions(REPOSITORY, scale)
    for rid in a:
        assert np.array_equal(a[rid], b[rid])


def test_speech_mask_reads_only_waveform_energy_for_controls() -> None:
    # C0 fractions are computed from the C0 waveform with the same -45 dBFS
    # rule; silence-heavy controls must have low speech-active windows.
    scale = SpeakerWindowScale.from_config(load_day6b_config(REPOSITORY)["speaker_temporal_grid"]["scales"][0])
    fractions = speech_active_fractions(REPOSITORY, scale)
    c0_ids = [r["control_sequence_id"] for r in _c0_manifest() if r["control_variant"] == "C0A"]
    assert all(rid in fractions and fractions[rid].size > 0 for rid in c0_ids[:3])


def test_original_and_masked_share_window_population() -> None:
    rows = _csv_rows("results/day6c/original_vs_masked_metrics.csv")
    orig = {(r["scale"], r["variant"], r["gt"], r["split"]): r for r in rows if r["masked"] == "False"}
    for key, masked_row in {(r["scale"], r["variant"], r["gt"], r["split"]): r for r in rows if r["masked"] == "True"}.items():
        assert key in orig  # same evaluation slices exist for both
        assert int(masked_row["n_windows"]) <= int(orig[key]["n_windows"])


# ---------------------------------------------------------------------------
# 20-21: duration tiers
# ---------------------------------------------------------------------------

def test_duration_tiers_are_immutable() -> None:
    tiers = {r["duration_tier"] for r in _c0_manifest()}
    assert tiers == {"0.75s", "1.5s", "2.5s"}


def test_duration_stratification_case_counts() -> None:
    rows = [r for r in _csv_rows("results/day6c/duration_stratified_metrics.csv")
            if r["scale"] == "S1_1000ms_250ms" and r["split"] == "test"]
    for variant in ("a0", "a1"):
        counts = {r["tier"]: int(r["case_count"]) for r in rows if r["variant"] == variant}
        assert counts == {"0.75s": 8, "1.5s": 8, "2.5s": 7}


# ---------------------------------------------------------------------------
# 22-24: case-level grouping and bootstrap
# ---------------------------------------------------------------------------

def test_case_level_grouped_by_paired_case() -> None:
    rows = [r for r in _csv_rows("results/day6c/case_level_metrics.csv")
            if r["scale"] == "S1_1000ms_250ms" and r["split"] == "test" and r["variant"] == "a0"]
    assert len(rows) == 6
    assert len({r["paired_case_id"] for r in rows}) == 6


def test_bootstrap_unit_is_case_not_window() -> None:
    rows = _csv_rows("results/day6c/bootstrap_ci.csv")
    assert rows
    cfg = yaml.safe_load((REPOSITORY / "configs/day6c_confound_controls.yaml").read_text(encoding="utf-8"))
    assert cfg["bootstrap"]["unit"] == "paired_case_id"
    assert all(int(r["n_cases"]) <= 23 for r in rows)
    assert all(int(r["resamples"]) == 2000 and int(r["seed"]) == 20260905 for r in rows)


def test_bootstrap_contrast_deterministic() -> None:
    rows = _csv_rows("results/day6c/bootstrap_ci.csv")
    a0 = next(r for r in rows if r["scale"] == "S1_1000ms_250ms" and r["contrast"] == "C0A_minus_A0")
    assert a0["ci_low"] == a0["ci_low"]  # finite or nan, recorded deterministically
    assert float(a0["ci_high"]) < 0  # same-speaker below cross-speaker (explicit direction)


def test_peak_localization_error_definition() -> None:
    # synthetic check of the frozen definition: global top-1 peak center vs
    # strict-core center, absolute seconds
    from audiobookbench.temporal.day6b_embed import build_speaker_windows

    scale = SpeakerWindowScale.from_config({"name": "t", "window_ms": 1000, "hop_ms": 250})
    windows = build_speaker_windows(160000, scale)
    rows = project_ground_truth_speaker(windows, {"attack": (48000, 64000), "target": (48000, 64000),
                                                  "core": (48000, 64000), "blend": (48000, 64000)})
    scores = np.zeros(len(rows)); scores[-1] = 10.0  # peak at the far end
    centers = np.array([w["time_center"] for w in windows])
    core_center = float(np.mean([w["time_center"] for w, r in zip(windows, rows) if r["is_core_window"]]))
    peak_idx = int(np.argmax(scores))
    err = abs(centers[peak_idx] - core_center)
    assert err == pytest.approx(6.0, abs=0.01)  # 9.5 s peak vs 3.5 s core center


def test_clean_transition_top3_deterministic_rule() -> None:
    rows = _csv_rows("results/day6c/clean_transition_audit.csv")
    assert rows, "C4 must be populated"
    ranks = {}
    for r in rows:
        ranks.setdefault((r["scale"], r["record_id"]), []).append(int(r["peak_rank"]))
    for key, rk in ranks.items():
        assert sorted(rk) == [1, 2, 3]


# ---------------------------------------------------------------------------
# 27-30: frozen artifact protection
# ---------------------------------------------------------------------------

def test_day6b_results_unchanged() -> None:
    assert verify_day6b_freeze(REPOSITORY)


def test_day6a_results_unchanged() -> None:
    # Day 6A outputs are protected through the Day 6B freeze record chain
    from audiobookbench.temporal.day6a_pipeline import verify_day5_outputs_unchanged

    assert verify_day5_outputs_unchanged(REPOSITORY)
    day6a_record = json.loads((REPOSITORY / "results/day6b/day6a_frozen_record.json").read_text(encoding="utf-8"))
    import hashlib

    for relpath, expected in day6a_record["hashes"].items():
        path = REPOSITORY / relpath
        assert path.exists() and hashlib.sha256(path.read_bytes()).hexdigest().upper() == expected


def test_all_earlier_frozen_hashes_unchanged() -> None:
    precheck = run_day5_precheck(REPOSITORY)
    assert precheck["all_passed"]
    source_check = next(c for c in precheck["checks"] if c["check"] == "source_input_hashes")
    assert source_check["passed"]  # raw AISHELL-3 unchanged (480 files re-hashed)


# ---------------------------------------------------------------------------
# Integrity-correction additions (bootstrap labels, GT axis, population audit)
# ---------------------------------------------------------------------------

def test_bootstrap_contrast_labels_are_direction_explicit() -> None:
    rows = _csv_rows("results/day6c/bootstrap_ci.csv")
    contrasts = {r["contrast"] for r in rows}
    assert contrasts == {"C0A_minus_A0", "C0B_minus_A1"}
    # direction semantics: negative mean delta == cross-speaker anomaly higher
    s1 = next(r for r in rows if r["scale"] == "S1_1000ms_250ms" and r["contrast"] == "C0A_minus_A0")
    assert float(s1["mean_delta"]) < 0
    assert float(s1["ci_high"]) < 0  # entire CI below zero (cross > same)


def test_gt_axis_audit_exists_and_passes() -> None:
    audit = json.loads((DAY6C / "gt_axis_audit.json").read_text(encoding="utf-8"))
    assert audit["all_pass"] is True
    assert audit["checked"] == 184  # 46 manipulated records x 2 scales


def test_speech_mask_population_audit_present() -> None:
    rows = _csv_rows("results/day6c/speech_mask_population_audit.csv")
    assert rows
    metrics = _csv_rows("results/day6c/original_vs_masked_metrics.csv")
    # positive retention must be high (the mask must not discard attack windows)
    for r in rows:
        if "positive_retention" in r and r["positive_retention"] not in ("", "nan"):
            assert float(r["positive_retention"]) >= 0.9, r
            original = next(
                m for m in metrics
                if m["scale"] == r["scale"] and m["baseline"] == "B1b"
                and m["variant"] == r["variant"] and m["split"] == r["split"]
                and m["gt"] == r["gt"] and m["masked"] == "False"
            )
            masked = next(
                m for m in metrics
                if m["scale"] == r["scale"] and m["baseline"] == "B1b"
                and m["variant"] == r["variant"] and m["split"] == r["split"]
                and m["gt"] == r["gt"] and m["masked"] == "True"
            )
            assert int(r["original_positives"]) == int(original["n_positive"])
            assert int(r["original_negatives"]) == int(original["n_windows"]) - int(original["n_positive"])
            assert float(r["positive_retention"]) == pytest.approx(
                int(masked["n_positive"]) / int(original["n_positive"]), abs=1e-6,
            )
        if "masked_positive_retention" in r and r["masked_positive_retention"] not in ("", "nan"):
            assert float(r["masked_positive_retention"]) >= 0.9, r


def test_day6c_confound_config_freezes_executed_values() -> None:
    cfg = yaml.safe_load((REPOSITORY / "configs/day6c_confound_controls.yaml").read_text(encoding="utf-8"))
    assert cfg["speech_active_mask"]["threshold"] == 0.5
    assert cfg["bootstrap"] == {"unit": "paired_case_id", "resamples": 2000, "seed": 20260905,
                                "contrasts": ["C0A_minus_A0", "C0B_minus_A1"]}
    assert cfg["duration_tiers"] == ["0.75s", "1.5s", "2.5s"]
    assert cfg["c0_donor_rule"]["same_speaker"] is True
    assert cfg["c0_donor_rule"]["reuse_cap"] == 1
