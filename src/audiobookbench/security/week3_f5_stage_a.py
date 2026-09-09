"""Frozen, isolated Week3 F5 mechanics; no scientific selection logic."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.preprocessing.audio_io import load_audio, resample_audio, write_audio
from audiobookbench.security.a2_readiness import (
    SAMPLE_RATE, match_active_speech_rms, replace_whole_utterance_with_crossfade,
    serialize_roundtrip, sha256_utf8, trim_synthetic_silence, validate_a2_sidecar_row,
)

BASE_SEED = 20260905
MAX_RETRIES = 1
FAILURE_CLASSES = frozenset({
    "infrastructure_transient", "infrastructure_terminal", "model_load_failure",
    "inference_failure", "invalid_output", "waveform_QA_failure",
    "sidecar_contract_failure", "integrity_failure",
})

REFERENCE_PREPROCESSING_CONTRACT = {
    "project_ref_text_is_exact": True,
    "nonempty_ref_text_disables_asr": True,
    "official_internal_audio_preprocess": True,
    "official_internal_terminal_punctuation_behavior": "record_metadata_only",
    "project_side_text_rewrite": False,
}

@dataclass(frozen=True)
class InferenceSettings:
    model: str = "F5TTS_v1_Base"
    device: str = "cpu"
    ode_method: str = "euler"
    use_ema: bool = True
    target_rms: float = 0.1
    cross_fade_duration: float = 0.15  # F5 internal generation parameter, not A2 fade.
    sway_sampling_coef: float = -1
    cfg_strength: float = 2
    nfe_step: int = 32
    speed: float = 1.0
    fix_duration: None = None
    remove_silence: bool = False

def generation_seed(zero_based_case_index: int) -> int:
    if zero_based_case_index < 0 or zero_based_case_index >= 23:
        raise ValueError("Week3 case index must be in [0, 22]")
    return BASE_SEED + zero_based_case_index

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()

def build_f5_api(repo_source: Path, settings: InferenceSettings, *, ckpt_file: Path, vocab_file: Path, vocoder_local_path: Path):
    """Construct only from the frozen official local F5 source and assets."""
    import sys
    if str(repo_source) not in sys.path:
        sys.path.insert(0, str(repo_source))
    from f5_tts.api import F5TTS
    return F5TTS(model=settings.model, ckpt_file=str(ckpt_file), vocab_file=str(vocab_file),
                 ode_method=settings.ode_method, use_ema=settings.use_ema,
                 vocoder_local_path=str(vocoder_local_path), device=settings.device)

def infer_once(api: Any, *, ref_file: Path, ref_text: str, gen_text: str, seed: int, settings: InferenceSettings):
    if not ref_text or not gen_text:
        raise ValueError("reference and generation text must be non-empty")
    # torch 2.2.2+cpu exposes an XPU namespace without the private fork
    # predicate that torch.random.manual_seed calls when the official F5
    # implementation seeds an inference.  Keep the frozen CPU path intact by
    # supplying the missing false predicate only on that CPU-only runtime.
    import torch
    if settings.device == "cpu" and hasattr(torch, "xpu"):
        if not hasattr(torch.xpu, "_is_in_bad_fork"):
            torch.xpu._is_in_bad_fork = lambda: False
        if not hasattr(torch.xpu, "manual_seed_all"):
            torch.xpu.manual_seed_all = lambda _seed: None
    return api.infer(str(ref_file), ref_text, gen_text, target_rms=settings.target_rms,
                     cross_fade_duration=settings.cross_fade_duration,
                     sway_sampling_coef=settings.sway_sampling_coef,
                     cfg_strength=settings.cfg_strength, nfe_step=settings.nfe_step,
                     speed=settings.speed, fix_duration=settings.fix_duration,
                     remove_silence=settings.remove_silence, seed=int(seed))

def construct_replacement(clean_path: Path, native_wave: np.ndarray, native_sr: int, *, start: int, end: int, out_path: Path):
    clean, clean_sr = load_audio(clean_path, target_sr=SAMPLE_RATE)
    standardized = resample_audio(np.asarray(native_wave, dtype=np.float32), int(native_sr), SAMPLE_RATE)
    trimmed = trim_synthetic_silence(standardized)
    if not np.all(np.isfinite(trimmed.waveform)) or trimmed.waveform.size == 0:
        raise ValueError("invalid_output")
    if trimmed.waveform.size <= 2 * 400 or end <= start or end - start <= 800:
        raise ValueError("crossfade_interval_too_short")
    synthetic, gain = match_active_speech_rms(clean[start:end], trimmed.waveform)
    manipulated, layout = replace_whole_utterance_with_crossfade(clean, synthetic, start, end, fade=400)
    if not np.all(np.isfinite(manipulated)) or float(np.max(np.abs(manipulated))) >= 0.999:
        raise ValueError("waveform_QA_failure")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serialization = serialize_roundtrip(manipulated, out_path, SAMPLE_RATE)
    return manipulated, trimmed, gain, layout, serialization, clean_sr

def validate_row(row: dict[str, Any]) -> None:
    validate_a2_sidecar_row(row)

def build_success_sidecar(case: dict[str, Any], *, index: int, seed: int,
                          raw_path: Path, standardized_path: Path,
                          raw_sr: int, raw_wave: np.ndarray, final_wave: np.ndarray,
                          trim: Any, gain: Any, layout: Any, attempts: int,
                          repo_commit: str, model_revision: str,
                          checkpoint_sha256: str, vocab_sha256: str,
                          vocoder_sha256: str, reference_preprocessing: str,
                          serialization: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build the additive Week3 sidecar while preserving generic A2 fields."""
    source_text = str(case["source_text_exact"]); ref_text = str(case.get("reference_text_exact", ""))
    row: dict[str, Any] = {
        "protocol_version": "WEEK3_STAGE_A_F5", "paired_case_id": case["paired_case_id"], "frozen_case_index": index + 1,
        "zero_based_case_index": index, "generation_seed": seed,
        "target_source_sample_id": case["target_source_sample_id"], "target_speaker": case["target_speaker"],
        "source_sample_id": case["target_source_sample_id"],
        "split": case["split"], "reference_sample_id": case["reference_sample_id"],
        "reference_audio_path": case["reference_audio_path"],
        "reference_text_exact": ref_text, "reference_text_sha256": sha256_utf8(ref_text),
        "attack_generator": "F5-TTS v1 Base", "attack_generator_family": "F5-TTS",
        "generator": "F5-TTS v1 Base", "model": "F5TTS_v1_Base", "repo_commit": repo_commit,
        "model_revision": model_revision, "generator_checkpoint_revision": model_revision,
        "generator_checkpoint_sha256": checkpoint_sha256,
        "vocab_sha256": vocab_sha256, "vocoder_asset_sha256": vocoder_sha256,
        "source_text_exact": source_text, "tts_input_text": source_text,
        "source_text_sha256": sha256_utf8(source_text), "tts_input_text_sha256": sha256_utf8(source_text),
        "clean_sequence_id": case["clean_sequence_id"],
        "clean_sequence_audio_path": case.get("clean_sequence_audio_path", ""),
        "clean_audio_path": case.get("clean_sequence_audio_path", ""),
        "clean_longform_audio_path": case.get("clean_sequence_audio_path", ""),
        "source_audio_path": case.get("source_audio_path", ""),
        "clean_source_utterance_start_sample": int(case["clean_source_utterance_start_sample"]),
        "clean_source_utterance_end_sample": int(case["clean_source_utterance_end_sample"]),
        "source_real_num_samples": int(case["source_real_num_samples"]),
        "raw_waveform_path": str(raw_path), "raw_waveform_sha256": sha256_file(raw_path),
        "standardized_waveform_path": str(standardized_path), "standardized_waveform_sha256": sha256_file(standardized_path),
        "manipulated_audio_path": str(standardized_path),
        "sample_rate": SAMPLE_RATE, "native_sample_rate": raw_sr, "standardized_sample_rate": SAMPLE_RATE,
        "native_channels": 1, "standardized_channels": 1,
        "native_samples": int(raw_wave.size), "standardized_samples": int(final_wave.size),
        "clean_timeline_start_sample": int(case["clean_source_utterance_start_sample"]),
        "clean_timeline_end_sample": int(case["clean_source_utterance_end_sample"]),
        "manipulated_timeline_start_sample": int(case["clean_source_utterance_start_sample"]),
        "manipulated_timeline_end_sample": int(case["clean_source_utterance_start_sample"]) + int(layout.final_synthetic_num_samples),
        "synthetic_duration": layout.final_synthetic_num_samples / SAMPLE_RATE,
        "removed_real_duration": layout.source_real_num_samples / SAMPLE_RATE,
        "suffix_shift_samples": layout.duration_delta_samples,
        "crossfade_samples": 400, "generation_attempt_count": attempts,
        "generation_status": "success", "generation_failure_reason": "",
        "reference_preprocessing": reference_preprocessing,
        "f5_inference_cross_fade_duration": 0.15,
        "a2_insertion_crossfade_samples": 400,
        "a2_insertion_crossfade_ms": 25.0,
        "official_smoke": False, "smoke_only": False,
        "clipping": bool(float(np.max(np.abs(final_wave))) >= 1.0),
        "serialization_max_abs_error": float((serialization or {}).get("max_abs_error", 0.0)),
        "inference_device": "cpu", "python_version": "3.12.9", "torch_version": "2.2.2+cpu",
        "qa_flags": json.dumps({"finite": True, "mono": True, "sample_rate": SAMPLE_RATE, "peak_safe": True}, sort_keys=True), "failure_class": "",
    }
    row.update(layout.as_dict())
    row.update(trim.metadata())
    row.update({f"gain_{k}": v for k, v in gain.as_dict().items()})
    return row

def build_failure_sidecar(case: dict[str, Any], *, index: int, seed: int,
                          attempts: int, failure_class: str, reason: str) -> dict[str, Any]:
    if failure_class not in FAILURE_CLASSES:
        raise ValueError(f"unknown failure class: {failure_class}")
    return {"paired_case_id": case["paired_case_id"], "frozen_case_index": index + 1,
            "zero_based_case_index": index, "generation_seed": seed,
            "target_source_sample_id": case["target_source_sample_id"],
            "target_speaker": case["target_speaker"], "split": case["split"],
            "reference_sample_id": case["reference_sample_id"],
            "attack_generator": "F5-TTS v1 Base", "attack_generator_family": "F5-TTS",
            "generator_checkpoint_sha256": "", "source_text_exact": case["source_text_exact"],
            "tts_input_text": case["source_text_exact"], "source_text_sha256": sha256_utf8(str(case["source_text_exact"])),
            "tts_input_text_sha256": sha256_utf8(str(case["source_text_exact"])),
            "clean_source_utterance_start_sample": case["clean_source_utterance_start_sample"],
            "clean_source_utterance_end_sample": case["clean_source_utterance_end_sample"],
            "source_real_num_samples": case["source_real_num_samples"],
            "generation_attempt_count": attempts, "generation_status": "failed",
            "generation_failure_reason": reason, "failure_class": failure_class}

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
