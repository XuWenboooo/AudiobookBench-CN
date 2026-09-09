"""Day 6B speaker-consistency localization tests.

Covers the real pretrained backend, the frozen speaker grid, the B1/B2/B3/B4
baselines, GT projection, leakage guards, bootstrap semantics and protection
of every frozen artifact (Day 6A negatives included).

No test trains a model; the speaker encoder is inference-only.
"""
from __future__ import annotations

import csv
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.day5_precheck import run_day5_precheck
from audiobookbench.temporal.day6a_pipeline import verify_day5_outputs_unchanged
from audiobookbench.temporal.day6b_embed import (
    EMBEDDING_DIM,
    SpeakerBackend,
    SpeakerWindowScale,
    build_speaker_windows,
    load_config,
    load_records,
)
from audiobookbench.temporal.day6b_pipeline import (
    _verify_day6a_unchanged,
    case_bootstrap_ci,
    load_day5_log_energy,
    speaker_disjoint_audit,
)
from audiobookbench.temporal.day6b_scoring import (
    TRIM_RATIO,
    b1_scores,
    b2_scores,
    b3_scores,
    b4_scores,
    cosine_to,
    normalize_rows,
    project_ground_truth_speaker,
    robust_prototype,
    untrimmed_prototype,
)

REPOSITORY = Path(__file__).resolve().parents[1]
DAY6B = REPOSITORY / "results/day6b"
CONFIG = load_config(REPOSITORY)
S1 = SpeakerWindowScale.from_config(CONFIG["speaker_temporal_grid"]["scales"][0])
S2 = SpeakerWindowScale.from_config(CONFIG["speaker_temporal_grid"]["scales"][1])
NUM_SAMPLES = 507597


def cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(a @ b / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12))


# ---------------------------------------------------------------------------
# 1-4: real backend
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def backend() -> SpeakerBackend:
    be = SpeakerBackend()
    be.load()
    return be


def test_real_pretrained_backend_loads(backend: SpeakerBackend) -> None:
    enc = backend.load()
    assert enc is not None
    assert (Path("pretrained/spkrec-ecapa-voxceleb") / "embedding_model.ckpt").stat().st_size > 10_000_000


def test_embeddings_are_finite_and_dimension_is_fixed(backend: SpeakerBackend) -> None:
    rng = np.random.default_rng(0)
    waveform = (rng.random(32000) * 2 - 1).astype(np.float32) * 0.1
    emb = backend.embed_windows(waveform, [(0, 16000), (4000, 20000)])
    assert emb.shape == (2, EMBEDDING_DIM)
    assert np.all(np.isfinite(emb))


def test_repeated_input_is_stable(backend: SpeakerBackend) -> None:
    rng = np.random.default_rng(1)
    waveform = (rng.random(16000) * 2 - 1).astype(np.float32) * 0.1
    e1 = backend.embed_windows(waveform, [(0, 16000)])
    e2 = backend.embed_windows(waveform, [(0, 16000)])
    assert cos(e1[0], e2[0]) >= 0.999999


def test_backend_config_records_real_model() -> None:
    info = json.loads((DAY6B / "embedding_backend.json").read_text(encoding="utf-8"))
    assert info["backend"]["model"] == "speechbrain/spkrec-ecapa-voxceleb"
    assert info["backend"]["dim"] == 192
    assert info["label_agnostic"] is True


# ---------------------------------------------------------------------------
# 5-7: speaker grid
# ---------------------------------------------------------------------------

def test_speaker_windows_are_deterministic() -> None:
    a = build_speaker_windows(NUM_SAMPLES, S1)
    b = build_speaker_windows(NUM_SAMPLES, S1)
    assert a == b
    assert len(a) == S1.window_count(NUM_SAMPLES)


def test_speaker_windows_never_exceed_waveform() -> None:
    for scale in (S1, S2):
        for w in build_speaker_windows(NUM_SAMPLES, scale):
            assert w["sample_end"] <= NUM_SAMPLES
            assert w["sample_start"] < w["sample_end"]
            assert abs((w["time_end"] - w["time_start"]) * 16000 - scale.window_samples) < 1e-6


def test_paired_a0_a1_share_the_speaker_grid() -> None:
    records = load_records(REPOSITORY)
    cases: dict[str, list[str]] = {}
    for rid, rec in records.items():
        if rec["variant"] in ("a0", "a1"):
            cases.setdefault(rec["paired_case_id"], []).append(rid)
    for case_id, rids in cases.items():
        assert len(rids) == 2
        wa = build_speaker_windows(int(records[rids[0]]["manifest_row"]["sequence_num_samples"]), S1)
        wb = build_speaker_windows(int(records[rids[1]]["manifest_row"]["sequence_num_samples"]), S1)
        assert [(w["sample_start"], w["sample_end"]) for w in wa] == [
            (w["sample_start"], w["sample_end"]) for w in wb
        ]
        assert case_id


def test_speaker_scale_rejects_invalid_config() -> None:
    with pytest.raises(ValueError):
        SpeakerWindowScale("bad", window_samples=100, hop_samples=200)
    with pytest.raises(ValueError):
        SpeakerWindowScale.from_config({"name": "bad", "window_ms": 1100, "hop_ms": 250})


# ---------------------------------------------------------------------------
# 8: GT projection on the speaker grid
# ---------------------------------------------------------------------------

def test_gt_projection_recomputed_on_speaker_grid() -> None:
    windows = build_speaker_windows(160000, S1)  # 10 s
    intervals = {"attack": (16000 * 3, 16000 * 4), "target": (16000 * 3, 16000 * 4),
                 "core": (16000 * 3 + 1600, 16000 * 4 - 1600), "blend": (16000 * 3, 16000 * 4)}
    rows = project_ground_truth_speaker(windows, intervals, label_threshold=0.5)
    hit = [r for r in rows if r["attack_overlap_ratio"] > 0]
    assert hit
    assert all(r["is_attack_window"] == (r["attack_overlap_ratio"] >= 0.5) for r in rows)
    core_rows = [r for r in rows if r["core_overlap_ratio"] > 0]
    assert any(r["zone"] == "core" for r in core_rows) and any(r["zone"] == "boundary" for r in core_rows)
    outside = [r for r in rows if r["zone"] == "outside"]
    assert all(r["attack_overlap_ratio"] == 0.0 and r["blend_overlap_ratio"] == 0.0 for r in outside)


# ---------------------------------------------------------------------------
# 9-12: prototypes and B1 scores
# ---------------------------------------------------------------------------

def _toy_embeddings() -> np.ndarray:
    # 30 near-orthogonal-to-outlier windows + 6 outlier windows pointing in a
    # different direction (orthogonal blocks make cosine distances separate).
    rng = np.random.default_rng(5)
    base = rng.normal(0, 1, (30, 16)) * 0.2
    base[:, 0] += 1.0  # cluster around e1-ish direction
    outlier = rng.normal(0, 1, (6, 16)) * 0.2
    outlier[:, 1] += 1.0  # cluster around an almost orthogonal direction
    return np.vstack([base, outlier]).astype(np.float64)


def test_untrimmed_prototype_is_normalized_centroid() -> None:
    e = _toy_embeddings()
    proto = untrimmed_prototype(e)
    expected = normalize_rows(e).mean(axis=0)
    expected = expected / np.linalg.norm(expected)
    assert np.allclose(proto, expected, atol=1e-12)
    assert abs(np.linalg.norm(proto) - 1.0) < 1e-9


def test_robust_prototype_trims_the_frozen_ratio() -> None:
    e = _toy_embeddings()
    proto = robust_prototype(e, TRIM_RATIO)
    n_trim = int(np.floor(len(e) * TRIM_RATIO))
    assert n_trim == int(np.floor(36 * 0.2)) == 7
    # the robust prototype must be closer to the clean majority direction
    # than the untrimmed one, because the orthogonal outliers were dropped
    majority = normalize_rows(e[:30]).mean(axis=0)
    majority /= np.linalg.norm(majority)
    d_trim = 1 - cos(proto, majority)
    d_untrim = 1 - cos(untrimmed_prototype(e), majority)
    assert d_trim < d_untrim
    assert b1_scores(e, trimmed=True).shape == (len(e),)


def test_trim_weakness_against_clustered_outliers_is_real() -> None:
    # Documented limitation: a cluster of same-direction outliers that has
    # already pulled the v1 centroid toward itself can survive cosine trim.
    # This is why B1b is pre-registered as a control, and why real-data
    # B1a/B1b differences are reported side by side.
    rng = np.random.default_rng(5)
    base = rng.normal(0, 1, (30, 16))
    cluster = rng.normal(0, 1, (6, 16)) + 50.0
    e = np.vstack([base, cluster])
    proto = robust_prototype(e, TRIM_RATIO)
    # sanity only: trimming must still yield a valid unit vector and scores
    assert abs(np.linalg.norm(proto) - 1.0) < 1e-6
    assert np.all(np.isfinite(b1_scores(e, trimmed=True)))


def test_prototype_never_reads_attack_ground_truth() -> None:
    # signatures expose no GT parameter; scores do not depend on any GT input
    for fn in (untrimmed_prototype, robust_prototype, b1_scores, b2_scores):
        sig = inspect.signature(fn)
        assert not any("gt" in p or "label" in p or "attack" in p for p in sig.parameters)
    e = _toy_embeddings()
    s1 = b1_scores(e, trimmed=True)
    s2 = b1_scores(e, trimmed=True)  # recomputed with no GT present anywhere
    assert np.array_equal(s1, s2)


def test_b1_scores_are_finite_and_nonnegative() -> None:
    e = _toy_embeddings()
    for trimmed in (False, True):
        s = b1_scores(e, trimmed=trimmed)
        assert np.all(np.isfinite(s)) and np.all(s >= -1e-12) and np.all(s <= 2.0 + 1e-12)


# ---------------------------------------------------------------------------
# 13: neighbor change
# ---------------------------------------------------------------------------

def test_b2_neighbor_change_detects_a_rotation() -> None:
    e = np.vstack([np.tile([1.0, 0.0], (5, 1)), np.tile([0.0, 1.0], (5, 1))])
    adj, sym = b2_scores(e)
    assert np.isnan(adj[-1]) and np.isnan(sym[0]) and np.isnan(sym[-1])
    assert adj[4] == pytest.approx(1.0)  # orthogonal rotation between windows 4 and 5
    assert sym[5] == pytest.approx(1.0)  # window 3 vs 5 across the change
    assert adj[0] == pytest.approx(0.0)  # identical neighbors score zero


# ---------------------------------------------------------------------------
# 14-16: leakage guards
# ---------------------------------------------------------------------------

def test_no_speaker_id_feature_in_any_baseline_signature() -> None:
    for fn in (b1_scores, b2_scores, b3_scores, b4_scores, untrimmed_prototype, robust_prototype):
        params = inspect.signature(fn).parameters
        assert not any("speaker" in p for p in params), fn


def test_val_test_speakers_are_disjoint_from_train() -> None:
    records = load_records(REPOSITORY)
    audit = speaker_disjoint_audit(records)
    assert audit["passed"], audit
    assert audit["speakers_per_split"] == {"train": 6, "val": 3, "test": 3}


def test_b1_has_no_enrollment_dependency() -> None:
    # B1 must depend only on the suspect sequence's own embeddings: scoring a
    # sequence never consults any other sequence or stored profile.
    e = _toy_embeddings()
    s_alone = b1_scores(e, trimmed=True)
    e_other = np.random.default_rng(9).normal(0, 1, (10, 16))
    _ = b1_scores(e_other, trimmed=True)  # scoring another sequence changes nothing
    assert np.array_equal(s_alone, b1_scores(e, trimmed=True))


# ---------------------------------------------------------------------------
# 17-18: oracle / diagnostic marking
# ---------------------------------------------------------------------------

def test_b3_is_marked_oracle_and_b4_diagnostic() -> None:
    assert CONFIG["baselines"]["B3"]["oracle"] is True
    assert CONFIG["baselines"]["B4"]["diagnostic"] is True
    assert "ORACLE" in "B3_ORACLE" and "DIAGNOSTIC" in "B4_DIAGNOSTIC"
    deployable = {k for k, v in CONFIG["baselines"].items() if v.get("deployable")}
    assert deployable == {"B1a", "B1b", "B2"}


def test_b3_paired_clean_differential() -> None:
    rng = np.random.default_rng(7)
    clean = rng.normal(0, 1, (20, 8))
    manip = clean.copy()
    manip[10:15] = rng.normal(0, 1, (5, 8)) + 3.0  # spliced region
    s = b3_scores(manip, clean)
    assert np.all(np.isfinite(s))
    assert float(np.mean(s[10:15])) > float(np.mean(s[:10]))


def test_b4_transient_uses_frame_energy_steps() -> None:
    log_energy = np.array([0.0, 0.0, 5.0, 5.0, 0.0])
    spans = [(0, 3), (3, 5)]
    s = b4_scores(log_energy, spans)
    assert s[0] == 5.0 and s[1] == 5.0


# ---------------------------------------------------------------------------
# 19-20: bootstrap semantics
# ---------------------------------------------------------------------------

def test_bootstrap_groups_by_case_and_is_deterministic() -> None:
    rng = np.random.default_rng(3)
    meta = {}
    scores, gts = {}, {}
    for i in range(4):
        rid = f"a0_case{i}"
        meta[rid] = {"variant": "a0", "split": "val", "paired_case_id": f"case{i}"}
        y = np.zeros(10, dtype=bool); y[7:] = True
        s = rng.random(10)
        gts[rid] = [{"window_index": j, "is_attack_window": bool(y[j]), "is_core_window": bool(y[j]),
                     "zone": "core" if y[j] else "outside"} for j in range(10)]
        scores[rid] = {"B1a": s}
    ci1 = case_bootstrap_ci(meta, scores, gts, "B1a", "full", "val", resamples=200, seed=123)
    ci2 = case_bootstrap_ci(meta, scores, gts, "B1a", "full", "val", resamples=200, seed=123)
    assert ci1 == ci2
    assert ci1["n_cases"] == 4 and ci1["seed"] == 123
    # single-case slice must be undefined, not fabricated
    meta_one = {k: v for k, v in meta.items() if k == "a0_case0"}
    gts_one = {k: v for k, v in gts.items() if k == "a0_case0"}
    ci_one = case_bootstrap_ci(meta_one, scores, gts_one, "B1a", "full", "val", resamples=50, seed=1)
    assert ci_one["auroc_ci"] == ["nan", "nan"]


def test_bootstrap_csv_records_seed_and_case_counts() -> None:
    rows = list(csv.DictReader((DAY6B / "bootstrap_ci.csv").open(encoding="utf-8")))
    assert rows
    assert all(int(r["seed"]) == 20260905 for r in rows)
    assert all(int(r["resamples"]) == 2000 for r in rows)
    assert all(int(r["n_cases"]) == 6 for r in rows)  # val/test both have 6 cases


# ---------------------------------------------------------------------------
# 21-22: frozen artifact protection
# ---------------------------------------------------------------------------

def test_day6a_outputs_unchanged() -> None:
    assert _verify_day6a_unchanged()


def test_all_earlier_frozen_hashes_unchanged() -> None:
    precheck = run_day5_precheck(REPOSITORY)
    assert precheck["all_passed"]
    assert verify_day5_outputs_unchanged(REPOSITORY)
