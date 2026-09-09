from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from audiobookbench.security.a2_readiness import validate_a2_sidecar_row
from audiobookbench.security.week3_f5_stage_a import generation_seed
from audiobookbench.security.week3_pipeline import validate_f5_source_identity, source_content_manifest
from audiobookbench.security.week3_accounting import classify_failure

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); assert spec and spec.loader
    spec.loader.exec_module(module); return module

def test_week3_zero_based_seed_mapping():
    assert generation_seed(0) == 20260905
    assert generation_seed(22) == 20260927
    with pytest.raises(ValueError): generation_seed(23)

def test_planned_population_and_split_and_seed():
    runner = load_module(ROOT / "experiments/week3_stage_a_f5/run.py", "week3_runner")
    rows = runner.load_planned()
    assert len(rows) == 23
    assert {r["split"] for r in rows} == {"train", "val", "test"}
    assert sum(r["split"] == "train" for r in rows) == 11
    assert sum(r["split"] == "val" for r in rows) == 6
    assert sum(r["split"] == "test" for r in rows) == 6

def test_h1_h2_h3_and_undefined_bootstrap():
    evaluator = load_module(ROOT / "experiments/week3_stage_a_f5/evaluate.py", "week3_eval")
    scores = {"a": np.array([0.1, 0.9]), "b": np.array([0.2, 0.8])}
    full = {k: np.array([0, 1]) for k in scores}; core = {k: np.array([0, 1]) for k in scores}
    h1 = evaluator.h1_full(scores, full)
    assert h1["AUROC_full"] == 1.0 and h1["AUPRC_full"] == 1.0
    h3 = evaluator.h3_full_core(scores, full, core)
    assert h3["DELTA_FULL_CORE_AUROC"] == 0.0
    h2 = evaluator.h2_boundary_core({"a": {"STRICT_CORE": np.array([0.2]), "BOUNDARY_BLEND": np.array([0.5]), "OUTSIDE_CLEAN": np.array([0.1])}})
    assert h2["DELTA_BOUNDARY_CORE"] == pytest.approx(0.3)
    ci = evaluator.case_bootstrap([1, 2], lambda xs: float("nan"))
    assert ci["undefined_replicates"] == 2000 and ci["ci"] == "NOT_REPORTABLE"

def test_success_sidecar_contract_is_sample_first():
    row = {
        "paired_case_id": "paircase_0001", "target_source_sample_id": "src", "target_speaker": "spk",
        "split": "test", "reference_sample_id": "ref", "attack_generator": "F5-TTS",
        "attack_generator_family": "reference_conditioned_tts", "generator_checkpoint_sha256": "x",
        "source_text_exact": "甲", "tts_input_text": "甲", "source_text_sha256": "33E3580C093111E1C4CAC922872C40371F7896BB3FA4E23BE5840BD1834FC622",
        "tts_input_text_sha256": "33E3580C093111E1C4CAC922872C40371F7896BB3FA4E23BE5840BD1834FC622", "clean_source_utterance_start_sample": "1000",
        "clean_source_utterance_end_sample": "3000", "source_real_num_samples": "2000",
        "generation_status": "success", "generation_seed": "20260905",
        "final_synthetic_num_samples": "2400", "duration_delta_samples": "400",
        "clean_timeline_start_sample": "1000", "clean_timeline_end_sample": "3000",
        "manipulated_timeline_start_sample": "1000", "manipulated_timeline_end_sample": "3400",
        "attack_start_sample": "1000", "attack_end_sample": "3400",
        "attack_core_start_sample": "1400", "attack_core_end_sample": "3000",
        "blend_in_start_sample": "1000", "blend_in_end_sample": "1400",
        "blend_out_start_sample": "3000", "blend_out_end_sample": "3400", "crossfade_samples": "400",
    }
    validate_a2_sidecar_row(row)

def test_engineering_fixture_is_not_scientific():
    runner = load_module(ROOT / "experiments/week3_stage_a_f5/run.py", "week3_runner_fixture")
    report = runner.engineering_only_report()
    assert report["status"] == "PASS"
    assert report["engineering_only"] is True
    assert report["scientific_generation"] is False

def test_formal_bootstrap_locks_thresholds_and_reports_undefined():
    evaluator = load_module(ROOT / "experiments/week3_stage_a_f5/evaluate.py", "week3_eval_bootstrap")
    first = {"n": 0}
    def mostly_undefined(_):
        first["n"] += 1
        return float("nan") if first["n"] <= 101 else 1.0
    result = evaluator.formal_case_bootstrap([1, 2], mostly_undefined)
    assert result["requested_replicates"] == 2000
    assert result["finite_replicates"] == 1899
    assert result["ci"] == "NOT_REPORTABLE"
    second = {"n": 0}
    def reportable(_):
        second["n"] += 1
        return float("nan") if second["n"] <= 100 else 1.0
    result = evaluator.formal_case_bootstrap([1, 2], reportable)
    assert result["finite_replicates"] == 1900
    assert isinstance(result["ci"], list)

def test_failure_taxonomy_explicit_invalid_output_and_no_retry():
    assert classify_failure(ValueError("invalid_output")) == "invalid_output"
    assert classify_failure(RuntimeError("checkpoint load failed")) == "model_load_failure"
    assert classify_failure(RuntimeError("inference_failure")) == "inference_failure"
    assert classify_failure(ValueError("waveform_QA_failure")) == "waveform_QA_failure"
    assert classify_failure(ValueError("sidecar_contract_failure")) == "sidecar_contract_failure"
    assert classify_failure(ValueError("integrity_failure")) == "integrity_failure"
    assert classify_failure(TimeoutError("temporary backend timeout")) == "infrastructure_transient"
    assert classify_failure(RuntimeError("unknown terminal infrastructure error")) == "infrastructure_terminal"

def test_f5_source_manifest_rejects_folder_name_spoof(tmp_path):
    source = tmp_path / "results" / "week3_engineering_qualification" / "f5_tts_v1_base" / "source" / "F5-TTS-abc"; source.mkdir(parents=True)
    file = source / "src" / "module.py"; file.parent.mkdir(); file.write_text("frozen", encoding="utf-8")
    from audiobookbench.security.week3_authorization import sha256_file
    evidence_dir = tmp_path / "results" / "week3_stage_a_f5" / "readiness_evidence"; evidence_dir.mkdir(parents=True)
    manifest = evidence_dir / "f5_source_manifest_local.json"
    manifest.write_text(json.dumps(source_content_manifest(source), indent=2), encoding="utf-8")
    (evidence_dir / "f5_source_identity.json").write_text(json.dumps({"status": "PASS", "source_identity_verified": True, "expected_commit": "abc", "resolved_official_commit": "abc", "local_source_path": str(source), "local_manifest_sha256": sha256_file(manifest)}), encoding="utf-8")
    config = {"f5": {"repo_commit": "abc"}}
    assert validate_f5_source_identity(tmp_path, config) == "abc"
    file.write_text("tampered", encoding="utf-8")
    with pytest.raises(RuntimeError, match="source manifest"):
        validate_f5_source_identity(tmp_path, config)
    file.write_text("frozen", encoding="utf-8")
    source.rename(source.with_name("F5-TTS-wrong"))
    with pytest.raises(RuntimeError):
        validate_f5_source_identity(tmp_path, config)
