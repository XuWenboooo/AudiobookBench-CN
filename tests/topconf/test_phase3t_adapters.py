from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.topconf_phase3t.adapter import AdapterError, adapt_cfprf, adapt_multireso, deterministic_supports
from experiments.topconf_phase3t.common import existing_terminal_ids
from experiments.topconf_phase3t.validate_raw import _validate_cfprf


def _cfprf_record() -> dict:
    scores = np.asarray([[0.2, 0.8], [0.7, 0.3], [0.1, 0.9]], dtype=float).tolist()
    return {
        "case_id": "E1/p/case.wav",
        "case_index": 0,
        "model_id": "CFPRF",
        "dataset_id": "PartialEdit_v1.1_E1",
        "duration_sec": 0.1,
        "status": "VALID_INFERENCE",
        "native_outputs": {"fdn_segment_scores": scores, "fdn_boundary_scores": scores},
    }


def test_cfprf_adapter_preserves_shape_and_class_zero_score():
    outputs = adapt_cfprf(_cfprf_record())
    assert [item["representation_id"] for item in outputs] == ["CFPRF_FDN_20ms", "CFPRF_BOUNDARY_20ms"]
    assert np.allclose(outputs[0]["frame_scores"], [0.2, 0.7, 0.1])
    assert np.allclose(outputs[0]["frame_times_sec"][-1], [0.04, 0.06])


def test_multireso_adapter_requires_and_maps_all_six_scales():
    scales = {}
    for index, unit in enumerate((0.02, 0.04, 0.08, 0.16, 0.32, 0.64)):
        count = 2
        scales[f"scale_{index}_{unit:.2f}s"] = {
            "unit_sec": unit,
            "native_times_sec": [[0.0, unit], [unit, unit * 2]],
            "native_class_scores": [[0.1, 0.9], [0.2, 0.8]],
        }
    record = {
        "case_id": "E1/p/case.wav",
        "case_index": 0,
        "model_id": "MultiResoModel-Simple",
        "dataset_id": "PartialEdit_v1.1_E1",
        "duration_sec": 2.0,
        "status": "VALID_INFERENCE",
        "native_outputs": {"scales": scales},
    }
    outputs = adapt_multireso(record)
    assert len(outputs) == 6
    assert {item["representation_id"] for item in outputs} == {f"MRM_scale_{i}_{u:.2f}s" for i, u in enumerate((0.02, 0.04, 0.08, 0.16, 0.32, 0.64))}


def test_time_mapping_refuses_duration_clipping():
    with pytest.raises(AdapterError, match="exceeds waveform duration"):
        deterministic_supports(2, 0.64, 1.0)


def test_time_mapping_normalizes_decimal_grid_roundoff_at_duration_boundary():
    supports = deterministic_supports(138, 0.02, 2.76)
    assert supports[-1].tolist() == [2.74, 2.76]
    assert supports[-1, 1] <= 2.76


def test_nan_is_rejected_by_cfprf_adapter():
    record = _cfprf_record()
    record["native_outputs"]["fdn_segment_scores"][0][0] = float("nan")
    with pytest.raises(ValueError, match="non-finite"):
        adapt_cfprf(record)


def test_cfprf_native_refined_proposal_preserves_unclipped_decoder_end():
    record = _cfprf_record()
    record["duration_sec"] = 0.1
    record["native_outputs"].update({
        "fdn_segment_class_order": ["spoof", "bonafide"],
        "fdn_coarse_proposals": [[1.0, 0.0, 0.1]],
        "prn_input_coarse_proposals": [[1.0, 0.0, 0.1]],
        "prn_scored_coarse_proposals": [[1.0, 0.0, 0.1]],
        "prn_verification_proposals": [[1.0, 0.0, 0.1]],
        "prn_refined_proposals": [[1.0, 0.0, 12.0]],
        "prn_verification_scores": [[1.0]],
        "prn_regression_outputs": [[0.0, 0.0]],
    })
    _validate_cfprf(record)


def test_duplicate_case_ids_are_rejected(tmp_path):
    path = tmp_path / "raw.jsonl"
    value = {"case_id": "E1/a.wav", "terminal": True}
    path.write_text(json.dumps(value) + "\n" + json.dumps(value) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        existing_terminal_ids(path)
