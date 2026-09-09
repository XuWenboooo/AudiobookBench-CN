from pathlib import Path

import numpy as np

from audiobookbench.security.week3_evaluation_repro import (
    _bootstrap,
    _expected_score_commitments,
    _h1,
    _h3,
    sha256_file,
)


def test_score_vector_npy_round_trip_preserves_tobytes_hash(tmp_path: Path):
    values = np.asarray([0.25, -1.0, np.nan, 4.5], dtype=np.float64)
    path = tmp_path / "scores.npy"
    np.save(path, values, allow_pickle=False)
    restored = np.load(path, allow_pickle=False)
    assert restored.dtype == values.dtype
    assert restored.shape == values.shape
    assert restored.tobytes() == values.tobytes()
    assert sha256_file(path)


def test_h1_and_h3_can_be_recomputed_from_persisted_fixture_rows():
    score_a = np.asarray([0.1, 0.8, 0.2, 0.7], dtype=np.float64)
    score_b = np.asarray([0.3, 0.9, 0.4, 0.6], dtype=np.float64)
    full_a = np.asarray([False, True, False, True])
    full_b = np.asarray([False, True, False, True])
    core_a = np.asarray([False, False, False, True])
    core_b = np.asarray([False, False, False, True])
    cases = [(score_a, full_a), (score_b, full_b)]
    h3_cases = [(score_a, full_a, core_a), (score_b, full_b, core_b)]
    assert np.isfinite(_h1(cases, "auroc"))
    assert np.isfinite(_h3(h3_cases, "auroc"))
    assert _bootstrap(cases, lambda sample: _h1(sample, "auroc"))["finite_replicates"] == 2000
    assert _bootstrap(h3_cases, lambda sample: _h3(sample, "auroc"))["finite_replicates"] == 2000


def test_original_score_commitments_are_exactly_23():
    commitments = _expected_score_commitments(Path(__file__).resolve().parents[1])
    assert list(commitments) == [f"paircase_{i:04d}" for i in range(1, 24)]
    assert all(len(value) == 64 for value in commitments.values())
