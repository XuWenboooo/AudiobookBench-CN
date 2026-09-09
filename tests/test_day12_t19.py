"""Focused fixture tests for the frozen Day12 T19 diagnostic only."""
from __future__ import annotations

from collections import Counter

import numpy as np
import pytest

from experiments.day12_mechanism.run import (
    FROZEN_SPLIT_COUNTS,
    T19IntegrityError,
    build_t19_rows,
    pause_fraction,
    render_t19_report,
    summarize_t19,
)


def _row(index: int, split: str, *, status: str = "success") -> dict[str, str]:
    return {
        "paired_case_id": f"paircase_{index:04d}",
        "split": split,
        "generation_status": status,
        "source_audio_path": f"real_{index}",
        "manipulated_audio_path": f"synthetic_{index}",
        "source_real_num_samples": "800",
        "attack_start_sample": "100",
        "attack_end_sample": "900",
        "final_synthetic_num_samples": "800",
        "source_sample_id": f"source_{index}",
        "target_speaker": f"speaker_{index}",
    }


def _fixture_rows() -> list[dict[str, str]]:
    splits = ["train"] * 11 + ["val"] * 6 + ["test"] * 6
    return [_row(index + 1, split) for index, split in enumerate(splits)]


def _loader_factory(*, nonfinite: bool = False):
    def loader(path: str, target_sr: int | None):
        assert target_sr == 16000
        if path.startswith("real_"):
            return np.zeros(800, dtype=np.float32), 16000
        waveform = np.zeros(900, dtype=np.float32)
        waveform[100:900] = 0.1
        if nonfinite:
            waveform[200] = np.nan
        return waveform, 16000
    return loader


def test_t19_reuses_frozen_pause_fraction() -> None:
    silent, silent_frames = pause_fraction(np.zeros(800, dtype=np.float32))
    active, active_frames = pause_fraction(np.full(800, 0.1, dtype=np.float32))
    assert silent == 1.0 and active == 0.0
    assert silent_frames == active_frames == 3  # complete 400-sample frames, 160-sample hop


def test_t19_one_finite_paired_row_per_case_and_split_accounting() -> None:
    all_rows = _fixture_rows()
    computed, unavailable = build_t19_rows(all_rows, loader=_loader_factory())
    assert len(computed) == 23 and unavailable == []
    assert Counter(row["split"] for row in computed) == Counter(FROZEN_SPLIT_COUNTS)
    assert all(np.isfinite(row["delta_pause_fraction"]) for row in computed)
    assert all(row["provenance_valid"] and row["diagnostic_label"] == "DIAGNOSTIC_ONLY" for row in computed)
    summaries = summarize_t19(computed, all_rows)
    assert {row["population"] for row in summaries} == {"all", "train", "val", "test"}


def test_t19_malformed_provenance_fails_closed() -> None:
    row = _fixture_rows()[0]
    row["attack_end_sample"] = "899"
    with pytest.raises(T19IntegrityError, match="inconsistent frozen region provenance"):
        build_t19_rows([row], loader=_loader_factory())


def test_t19_nonfinite_signal_fails_closed() -> None:
    with pytest.raises(T19IntegrityError, match="not finite mono audio"):
        build_t19_rows(_fixture_rows(), loader=_loader_factory(nonfinite=True))


def test_t19_delta_magnitude_does_not_determine_pass() -> None:
    computed, _ = build_t19_rows(_fixture_rows(), loader=_loader_factory())
    assert {row["delta_pause_fraction"] for row in computed} == {-1.0}
    assert all(row["status"] == "PASS" for row in computed)


def test_t19_report_is_explicitly_diagnostic_only() -> None:
    rows = _fixture_rows()
    computed, _ = build_t19_rows(rows, loader=_loader_factory())
    report = render_t19_report(summarize_t19(computed, rows))
    assert "DIAGNOSTIC ONLY" in report
    assert "inferential test or threshold" in report
