from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from audiobookbench.security.week4_adaptive import FrozenAttackSpec
from audiobookbench.security.week4_execution import (
    SAMPLE_RATE, active_interval, attacker_objective, construct_candidate,
    execute_protocol, project_gt, trim_synthetic,
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
    result = execute_protocol(cases=cases, spec=spec, runtime_root=tmp_path / "TEST_ONLY", f5_generator=fake_f5, d0_backend=_FakeD0(), source_loader=lambda _: np.full(64000, 0.1, dtype=np.float32))
    assert seeds == list(range(20260914, 20260962))
    assert result["A0_FROZEN"] is True
    assert result["final"]["PRIMARY_H4"] == "REPORTABLE"
    assert result["final"]["paired_bootstrap"]["auroc"]["finite"] >= 1900
    assert len(result["ledger"]) == 48 * 41
    assert all(row["candidate_id"] for row in result["ledger"])
    assert (tmp_path / "TEST_ONLY/final.json").is_file()


def test_vector_sidecar_is_committed_with_raw_score_hash(tmp_path: Path):
    from audiobookbench.security.week4_execution import _persist_candidate, vector_record
    waveform = np.full(24000, 0.1, dtype=np.float32)
    rows = project_gt(waveform, {"attack": (0, 12000), "core": (400, 11600), "blend_in": (0, 400), "blend_out": (11600, 12000)})
    record = vector_record(case_id="week4_case_0001", candidate_id="TEST_ONLY:static:000000", waveform=waveform, scores=np.array([0.25]), windows=[{k: v for k, v in rows[0].items() if k not in {"FULL_ATTACK", "OUTSIDE_CLEAN", "attack_overlap_ratio"}}], projection=rows)
    committed = _persist_candidate(tmp_path, record)
    path = tmp_path / committed["sidecar_relpath"]
    assert path.is_file() and committed["sidecar_sha256"]
    assert json.loads(path.read_text(encoding="utf-8"))["score_vector_sha256"] == record["score_vector_sha256"]
