from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

WORKER_DIR = Path(__file__).parents[2] / "experiments" / "topconf_phase3t"
sys.path.insert(0, str(WORKER_DIR))
import run_multireso_worker as worker  # noqa: E402


def test_native_outputs_preserve_all_six_scales_without_metrics():
    logits = [torch.zeros(1 * 3, 2) + float(index) for index in range(6)]
    output = worker._native_outputs(logits, [int(3 * 0.02 * worker.SAMPLE_RATE)])
    assert len(output) == 1
    assert len(output[0]) == 6
    assert [item["scale_id"] for item in output[0]] == [f"native_{unit:.2f}s" for unit in worker.UNITS]
    assert all(item["output_shape"][-1] == 2 for item in output[0])


def test_append_only_resume_and_duplicate_detection(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setattr(worker, "LEDGER_JSONL", ledger)
    worker._append(ledger, {"case_id": "c1", "terminal_status": "VALID"})
    assert worker._existing_case_ids() == {"c1"}
    worker._append(ledger, {"case_id": "c1", "terminal_status": "VALID"})
    with pytest.raises(RuntimeError, match="duplicate"):
        worker._existing_case_ids()


def test_raw_hash_is_deterministic_and_shape_gate_fails():
    payload = {"case_id": "c1", "native_scales": []}
    assert worker.canonical_hash(payload) == worker.canonical_hash(json.loads(json.dumps(payload)))
    with pytest.raises(ValueError, match="fewer than six"):
        worker._native_outputs([torch.zeros(1, 2)], [320])
