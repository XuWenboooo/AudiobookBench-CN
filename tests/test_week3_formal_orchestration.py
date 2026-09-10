from __future__ import annotations

import json
import inspect
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from audiobookbench.security import week3_pipeline as pipeline
from audiobookbench.security.week3_authorization import sha256_file
from audiobookbench.security.a2_sidecar_validator import validate_row as validate_sidecar_row
from audiobookbench.security.a2_waveform_gt_verifier import verify_row as verify_waveform_row
from audiobookbench.security.week3_f5_stage_a import build_success_sidecar, construct_replacement
from audiobookbench.preprocessing.audio_io import write_audio
from experiments.week3_stage_a_f5 import evaluate as evaluator

ROOT = Path(__file__).resolve().parents[1]

def test_mock_formal_entrypoint_wires_generation_validation_and_accounting(tmp_path, monkeypatch):
    source_paths = pipeline._source_paths(ROOT)
    case = {"paired_case_id": "paircase_0001", "clean_sequence_id": "clean", "source_text_exact": "甲", "tts_input_text": "甲", "source_text_sha256": "x", "reference_text_sha256": "y", "reference_text_exact": "乙", "reference_audio_path": "ref.wav", "target_source_sample_id": "src", "target_speaker": "spk", "reference_sample_id": "ref", "split": "test", "clean_sequence_audio_path": "clean.wav", "clean_source_utterance_start_sample": "1000", "clean_source_utterance_end_sample": "3000", "source_real_num_samples": "2000"}
    config = {"output_root": "results/week3_stage_a_f5", "f5": {"repo_commit": "commit", "model_revision": "revision", "checkpoint_sha256": "ckpt", "vocab_sha256": "vocab", "vocoder_model_sha256": "vocoder", "model": "F5TTS_v1_Base", "device": "cpu", "ode_method": "euler", "use_ema": True, "target_rms": 0.1, "cross_fade_duration": 0.15, "sway_sampling_coef": -1, "cfg_strength": 2, "nfe_step": 32, "speed": 1.0, "fix_duration": None, "remove_silence": False}}
    inputs = pipeline.FrozenInputs(config, [case], "config-hash", "environment-hash", source_paths)
    monkeypatch.setattr(pipeline, "load_frozen_inputs", lambda _: inputs)
    monkeypatch.setattr(pipeline, "validate_preflight", lambda _: inputs)
    infer_calls = {"count": 0}
    def mocked_infer(*args, **kwargs):
        infer_calls["count"] += 1
        if infer_calls["count"] == 1:
            raise TimeoutError("temporary backend timeout")
        return np.ones(4000, dtype=np.float32) * 0.1, 16000, {}
    monkeypatch.setattr(pipeline, "infer_once", mocked_infer)
    layout = SimpleNamespace(final_synthetic_num_samples=4000, source_real_num_samples=2000, duration_delta_samples=2000, as_dict=lambda: {"attack_start_sample": 1000, "attack_end_sample": 5000, "attack_core_start_sample": 1400, "attack_core_end_sample": 4600, "blend_in_start_sample": 1000, "blend_in_end_sample": 1400, "blend_out_start_sample": 4600, "blend_out_end_sample": 5000, "clean_timeline_start_sample": 1000, "clean_timeline_end_sample": 3000, "manipulated_timeline_start_sample": 1000, "manipulated_timeline_end_sample": 5000, "crossfade_samples": 400, "final_synthetic_num_samples": 4000, "duration_delta_samples": 2000})
    monkeypatch.setattr(pipeline, "construct_replacement", lambda *args, **kwargs: (np.ones(5000, dtype=np.float32) * 0.1, SimpleNamespace(metadata=lambda: {}), SimpleNamespace(as_dict=lambda: {}), layout, {"max_abs_error": 0.0}, 16000))
    monkeypatch.setattr(pipeline, "build_success_sidecar", lambda case, **kwargs: {"paired_case_id": case["paired_case_id"], "raw_waveform_sha256": "raw", "manipulated_audio_path": str(tmp_path / "waveform.wav"), **layout.as_dict()})
    calls = []
    monkeypatch.setattr(pipeline, "validate_sidecar_row", lambda *args, **kwargs: calls.append("sidecar"))
    monkeypatch.setattr(pipeline, "verify_waveform_row", lambda *args, **kwargs: calls.append("waveform"))
    monkeypatch.setattr(pipeline, "verify_sample_first_gt", lambda *args, **kwargs: {"status": "PASS"})
    result = pipeline.run_test_fixture_generation(ROOT, inputs, api_factory=lambda _: object(), output_root=tmp_path / "week3")
    assert result["status"] == "PASS"
    assert calls == ["sidecar", "waveform"]
    assert infer_calls["count"] == 2
    assert json.loads((tmp_path / "week3/accounting/attempts.jsonl").read_text(encoding="utf-8").splitlines()[0])["failure_class"] == "infrastructure_transient"
    assert ",2,1," in (tmp_path / "week3/accounting/cases.csv").read_text(encoding="utf-8")
    assert (tmp_path / "week3/accounting/attempts.jsonl").is_file()
    assert (tmp_path / "week3/accounting/cases.csv").is_file()

def test_real_sidecar_builder_passes_frozen_validator_chain(tmp_path):
    clean_path = tmp_path / "clean.wav"
    raw_path = tmp_path / "raw.wav"
    out_path = tmp_path / "waveform.wav"
    clean = np.sin(np.linspace(0, 200, 30000)).astype(np.float32) * 0.1
    raw = np.sin(np.linspace(0, 180, 30000)).astype(np.float32) * 0.1
    write_audio(clean_path, clean, 16000); write_audio(raw_path, raw, 16000)
    source_path = tmp_path / "source.wav"; write_audio(source_path, raw, 16000)
    case = {"paired_case_id": "paircase_0001", "clean_sequence_id": "clean", "clean_sequence_audio_path": str(clean_path), "source_audio_path": str(source_path), "source_text_exact": "甲", "tts_input_text": "甲", "target_source_sample_id": "src", "target_speaker": "spk", "reference_sample_id": "ref", "reference_audio_path": str(tmp_path / "ref.wav"), "reference_text_exact": "乙", "split": "test", "clean_source_utterance_start_sample": "1000", "clean_source_utterance_end_sample": "28000", "source_real_num_samples": "27000"}
    final_wave, trim, gain, layout, serialization, _ = construct_replacement(clean_path, raw, 16000, start=1000, end=28000, out_path=out_path)
    row = build_success_sidecar(case, index=0, seed=20260905, raw_path=raw_path, standardized_path=out_path, raw_sr=16000, raw_wave=raw, final_wave=final_wave, trim=trim, gain=gain, layout=layout, attempts=1, repo_commit="commit", model_revision="revision", checkpoint_sha256="ckpt", vocab_sha256="vocab", vocoder_sha256="vocoder", reference_preprocessing="official_f5_preprocess_ref_audio_text", serialization=serialization)
    csv_row = pipeline._as_csv_row(row)
    plan = {**csv_row, "paired_case_id": "paircase_0001", "source_text_exact": "甲", "tts_input_text": "甲", "target_source_sample_id": "src", "target_speaker": "spk", "split": "test"}
    validate_sidecar_row(csv_row, {"paircase_0001": plan}, official_smoke=False)
    bad_lineage = dict(csv_row); bad_lineage["source_audio_path"] = str(clean_path)
    with pytest.raises(ValueError, match="lineage"):
        validate_sidecar_row(bad_lineage, {"paircase_0001": plan}, official_smoke=False)
    assert row["source_audio_path"] == str(source_path)
    assert row["source_audio_path"] != row["clean_sequence_audio_path"]
    assert row["clean_audio_path"] == str(clean_path)
    assert row["clean_longform_audio_path"] == str(clean_path)
    verify_waveform_row(csv_row, str(clean_path))
    windows = pipeline.build_speaker_windows(final_wave.size, pipeline.SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000))
    gt = pipeline.project_ground_truth_speaker(windows, pipeline._interval_row(row), 0.5)
    assert pipeline.verify_sample_first_gt(row, gt)["status"] == "PASS"

def test_mock_formal_evaluator_uses_authoritative_cases_and_narrow_detector(tmp_path, monkeypatch):
    clean_path = tmp_path / "clean-eval.wav"; raw_path = tmp_path / "raw-eval.wav"; out_path = tmp_path / "wave-eval.wav"
    clean = np.sin(np.linspace(0, 200, 30000)).astype(np.float32) * 0.1; raw = np.sin(np.linspace(0, 180, 30000)).astype(np.float32) * 0.1
    write_audio(clean_path, clean, 16000); write_audio(raw_path, raw, 16000)
    source_path = tmp_path / "source-eval.wav"; write_audio(source_path, raw, 16000)
    case = {"paired_case_id": "paircase_0001", "clean_sequence_id": "clean", "clean_sequence_audio_path": str(clean_path), "source_audio_path": str(source_path), "source_text_exact": "甲", "tts_input_text": "甲", "target_source_sample_id": "src", "target_speaker": "spk", "reference_sample_id": "ref", "reference_audio_path": str(tmp_path / "ref.wav"), "reference_text_exact": "乙", "split": "test", "clean_source_utterance_start_sample": "1000", "clean_source_utterance_end_sample": "28000", "source_real_num_samples": "27000"}
    final_wave, trim, gain, layout, serialization, _ = construct_replacement(clean_path, raw, 16000, start=1000, end=28000, out_path=out_path)
    sidecar = build_success_sidecar(case, index=0, seed=20260905, raw_path=raw_path, standardized_path=out_path, raw_sr=16000, raw_wave=raw, final_wave=final_wave, trim=trim, gain=gain, layout=layout, attempts=1, repo_commit="commit", model_revision="revision", checkpoint_sha256="ckpt", vocab_sha256="vocab", vocoder_sha256="vocoder", reference_preprocessing="official_f5_preprocess_ref_audio_text", serialization=serialization)
    output_root = tmp_path / "week3-eval"; (output_root / "accounting").mkdir(parents=True); (output_root / "sidecars").mkdir()
    rows = [{"paired_case_id": "paircase_0001", "planned": "True", "status": "SUCCESS", "attempt_count": "1", "retry_count": "0"}] + [{"paired_case_id": f"paircase_{i:04d}", "planned": "True", "status": "FAILED", "attempt_count": "1", "retry_count": "0", "failure_class": "inference_failure"} for i in range(2, 24)]
    import csv
    with (output_root / "accounting/cases.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["paired_case_id", "planned", "status", "attempt_count", "retry_count", "failure_class"]); writer.writeheader(); writer.writerows(rows)
    (output_root / "sidecars/sidecars.jsonl").write_text(json.dumps(sidecar, ensure_ascii=False) + "\n", encoding="utf-8")
    source_paths = pipeline._source_paths(ROOT)
    config = {"output_root": str(output_root), "f5": {}}
    inputs = pipeline.FrozenInputs(config, [case], "config-hash", "environment-hash", source_paths)
    monkeypatch.setattr(evaluator, "load_frozen_inputs", lambda _: inputs); monkeypatch.setattr(evaluator, "validate_preflight", lambda _: inputs)
    class Backend:
        def embed_windows(self, waveform, windows): return np.ones((len(windows), 192), dtype=np.float32)
    result = evaluator.run_test_fixture_evaluation(ROOT, inputs, backend=Backend(), output_root=output_root)
    assert result["status"] == "PASS" and result["successful_generation_n"] == 1
    population = json.loads((output_root / "evaluation/analysis_population.json").read_text(encoding="utf-8"))
    h2 = json.loads((output_root / "evaluation/h2_results.json").read_text(encoding="utf-8"))
    assert population["analysis_status"] == "TEST_ONLY"
    assert population["failure_class_counts"]["inference_failure"] == 22
    assert all(population[key] for key in ("config_sha256", "environment_manifest_sha256", "case_table_sha256"))
    assert all(key in h2 for key in ("H2_available_n", "H2_unavailable_n", "unavailable_reason_counts", "case_results"))
    assert all("contrast_available" in value and "unavailable_reason" in value for value in h2["case_results"].values())

def test_formal_entrypoints_have_no_auth_or_test_only_overrides():
    assert list(inspect.signature(pipeline.run_formal_generation).parameters) == ["repo"]
    assert "authorization_path" not in inspect.signature(evaluator.run_formal_evaluation).parameters
    assert "test_only" not in inspect.signature(evaluator.run_formal_evaluation).parameters
    assert "authorization_path" not in inspect.signature(pipeline.run_formal_generation).parameters

def test_formal_entrypoints_fail_without_canonical_authorization(tmp_path, monkeypatch):
    # The real repository now contains a completed clean-rerun authorization.
    # Point both production entrypoints at an isolated absent artifact so this
    # test verifies the missing-authorization gate, not repository history.
    missing_authorization = tmp_path / "authorization.json"
    monkeypatch.setattr(pipeline, "FUTURE_AUTH_REL", missing_authorization)
    monkeypatch.setattr(evaluator, "FUTURE_AUTH_REL", missing_authorization)
    with pytest.raises(RuntimeError, match="authorization artifact is missing|authorization source hash mismatch|identity missing"):
        pipeline.run_formal_generation(ROOT)
    with pytest.raises(RuntimeError, match="authorization artifact is missing|authorization source hash mismatch|identity missing"):
        evaluator.run_formal_evaluation(ROOT, backend=object())

def test_detector_compatibility_wrapper_has_no_direct_backend_path(monkeypatch):
    source = inspect.getsource(evaluator.frozen_b1b_s2_score)
    assert "backend.embed_windows" not in source
    calls = []
    windows = [{"window_index": 0, "sample_start": 0, "sample_end": 24000}]
    monkeypatch.setattr(evaluator, "score_reference_free", lambda *args: (np.array([0.5]), windows))
    monkeypatch.setattr(evaluator, "project_ground_truth_speaker", lambda *args: [])
    scores, gt, actual_windows = evaluator.frozen_b1b_s2_score(object(), np.zeros(24000, dtype=np.float32), {"attack": (0, 1000)})
    assert calls == [] and scores.shape == (1,) and actual_windows == windows
