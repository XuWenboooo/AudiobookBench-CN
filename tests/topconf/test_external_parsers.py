from __future__ import annotations

import csv

import numpy as np
import pytest

from audiobookbench.topconf.datasets import (
    parse_partialedit_csv,
    parse_partialspoof_segment_labels,
    summarize_partialedit,
)


def test_partialedit_parser_accepts_single_and_multiple_regions(tmp_path):
    path = tmp_path / "PartialEdit_E1E2.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["E1/p001/a.wav", "0.5", "1.0", "2.0"])
        writer.writerow(["E2/p002/b.wav", "0.2", "0.4", "1.0", "1.3", "2.0"])

    records = parse_partialedit_csv(path)

    assert records[0].edited_regions == ((0.5, 1.0),)
    assert records[1].edited_regions == ((0.2, 0.4), (1.0, 1.3))
    assert summarize_partialedit(records) == {
        "records": 2,
        "edited_regions": 3,
        "unique_audio_paths": 2,
    }


@pytest.mark.parametrize(
    "row",
    [
        ["a.wav", "0.5", "0.5", "2.0"],
        ["a.wav", "1.5", "1.0", "2.0"],
        ["a.wav", "0.5", "2.5", "2.0"],
        ["a.wav", "0.1", "0.8", "0.5", "1.0"],
    ],
)
def test_partialedit_parser_rejects_invalid_regions(tmp_path, row):
    path = tmp_path / "bad.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(row)
    with pytest.raises(ValueError):
        parse_partialedit_csv(path)


def test_partialspoof_parser_validates_binary_mapping(tmp_path):
    path = tmp_path / "eval_seglab_0.16.npy"
    np.save(path, {"CON_E_1": np.array(["0", "1"]), "CON_E_2": np.array(["1"])})
    assert parse_partialspoof_segment_labels(path) == {
        "CON_E_1": (0, 1),
        "CON_E_2": (1,),
    }


def test_partialspoof_parser_rejects_nonbinary_mapping(tmp_path):
    path = tmp_path / "bad.npy"
    np.save(path, {"CON_E_1": np.array(["0", "2"])})
    with pytest.raises(ValueError):
        parse_partialspoof_segment_labels(path)
