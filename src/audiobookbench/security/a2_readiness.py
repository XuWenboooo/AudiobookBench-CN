"""Day 8 implementation-readiness primitives for A2.

This module intentionally has no TTS-model dependency.  It freezes and tests
lineage, text, reference, DSP, crossfade, GT, and detector-separation behavior
before an external generator is asked to produce a formal pilot waveform.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import math
from pathlib import Path
import unicodedata
from typing import Any, Iterable, Mapping

import numpy as np

from audiobookbench.preprocessing.audio_io import probe_audio, write_audio, load_audio


SAMPLE_RATE = 16000
CROSSFADE_SAMPLES = 400
FRAME_SAMPLES = 400
HOP_SAMPLES = 160
ACTIVITY_THRESHOLD_DBFS = -45.0
RETAIN_EDGE_SAMPLES = 800


class A2ReadinessError(ValueError):
    """Raised for a fail-closed A2 readiness violation."""


@dataclass(frozen=True)
class CrossfadeLayout:
    attack_start_sample: int
    attack_end_sample: int
    attack_core_start_sample: int
    attack_core_end_sample: int
    blend_in_start_sample: int
    blend_in_end_sample: int
    blend_out_start_sample: int
    blend_out_end_sample: int
    source_real_num_samples: int
    final_synthetic_num_samples: int
    duration_delta_samples: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class TrimResult:
    waveform: np.ndarray
    pretrim_num_samples: int
    posttrim_num_samples: int
    leading_trim_samples: int
    trailing_trim_samples: int

    def metadata(self) -> dict[str, int | float]:
        return {
            "pretrim_num_samples": self.pretrim_num_samples,
            "posttrim_num_samples": self.posttrim_num_samples,
            "pretrim_duration": self.pretrim_num_samples / SAMPLE_RATE,
            "posttrim_duration": self.posttrim_num_samples / SAMPLE_RATE,
            "leading_trim_samples": self.leading_trim_samples,
            "trailing_trim_samples": self.trailing_trim_samples,
        }


@dataclass(frozen=True)
class GainResult:
    target_active_rms: float
    synthetic_active_rms: float
    raw_gain: float
    clamped_gain: float
    peak_safe_scale: float
    final_gain: float
    peak_after_gain: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def validate_same_text(source_text_exact: str, tts_input_text: str) -> dict[str, Any]:
    """Validate the strict, identity-only primary A2 text contract."""
    if not isinstance(source_text_exact, str) or not isinstance(tts_input_text, str):
        raise A2ReadinessError("source_text_exact and tts_input_text must be str")
    if not source_text_exact:
        raise A2ReadinessError("source_text_exact must be non-empty")
    if unicodedata.normalize("NFC", source_text_exact) != source_text_exact:
        raise A2ReadinessError("source_text_exact must already be Unicode NFC")
    if source_text_exact != source_text_exact.strip():
        raise A2ReadinessError("source_text_exact may not have leading/trailing whitespace")
    if source_text_exact != tts_input_text:
        raise A2ReadinessError("tts_input_text must be code-point identical to source_text_exact")
    source_hash = sha256_utf8(source_text_exact)
    input_hash = sha256_utf8(tts_input_text)
    if source_hash != input_hash:
        raise A2ReadinessError("exact same text must have equal UTF-8 SHA-256")
    return {
        "source_text_exact": source_text_exact,
        "tts_input_text": tts_input_text,
        "text_normalization": "identity_after_nfc_and_edge_whitespace_validation",
        "same_text_exact": True,
        "same_text_semantic": True,
        "source_text_sha256": source_hash,
        "tts_input_text_sha256": input_hash,
    }


def _as_int_sample(seconds: Any, sample_rate: int = SAMPLE_RATE) -> int:
    return int(round(float(seconds) * sample_rate))


def materialize_whole_utterance_cases(
    attack_rows: Iterable[Mapping[str, Any]], longform_rows: Iterable[Mapping[str, Any]],
    source_rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Use Week 1 paired rows only as lineage; derive A2 whole-utterance bounds."""
    attacks = [dict(row) for row in attack_rows if str(row.get("attack_type")) == "cross_speaker_splice"]
    longform = [dict(row) for row in longform_rows]
    sources = {str(row["sample_id"]): dict(row) for row in source_rows}
    if len(attacks) != 23:
        raise A2ReadinessError(f"expected 23 frozen A0 lineage rows, got {len(attacks)}")
    lookup: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in longform:
        lookup.setdefault((str(row["sequence_id"]), str(row["source_sample_id"])), []).append(row)
    cases: list[dict[str, Any]] = []
    forbidden = {
        "week1_target_start_sample", "week1_target_end_sample", "week1_attack_start_sample",
        "week1_attack_end_sample", "week1_duration_tier", "week1_donor_start_sample",
        "week1_donor_end_sample",
    }
    for attack in sorted(attacks, key=lambda row: str(row["paired_case_id"])):
        source_id = str(attack["target_source_sample_id"])
        sequence_id = str(attack["clean_sequence_id"])
        matches = lookup.get((sequence_id, source_id), [])
        if len(matches) != 1:
            raise A2ReadinessError(f"A2 source lineage must be unique for {attack['paired_case_id']}")
        target = matches[0]
        source = sources.get(source_id)
        if source is None:
            raise A2ReadinessError(f"target source missing from source catalog: {source_id}")
        c0 = _as_int_sample(target["sequence_start"])
        c1 = _as_int_sample(target["sequence_end"])
        if not 0 <= c0 < c1 <= int(target["sequence_num_samples"]):
            raise A2ReadinessError(f"invalid complete-source bounds for {attack['paired_case_id']}")
        text = str(source["transcript_zh"])
        text_fields = validate_same_text(text, text)
        case = {
            "paired_case_id": str(attack["paired_case_id"]),
            "clean_sequence_id": sequence_id,
            "target_source_sample_id": source_id,
            "target_speaker": str(attack["target_speaker"]),
            "split": str(attack["split"]),
            "clean_source_utterance_start_sample": c0,
            "clean_source_utterance_end_sample": c1,
            "source_real_num_samples": c1 - c0,
            "source_real_duration": (c1 - c0) / SAMPLE_RATE,
            "source_audio_path": str(source["audio_path"]),
            "source_audio_relpath": str(source["audio_relpath"]),
            "text_id": str(source["text_id"]),
            "week1_lineage_only": True,
            "week1_forbidden_interval_fields": sorted(forbidden),
            **text_fields,
        }
        cases.append(case)
    if len({row["paired_case_id"] for row in cases}) != 23:
        raise A2ReadinessError("paired_case_id must remain unique")
    return cases


def choose_reference_rows(
    source_rows: Iterable[Mapping[str, Any]], attack_rows: Iterable[Mapping[str, Any]],
    longform_rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Implement the frozen same-speaker/split 3--8 second reference rule."""
    source = [dict(row) for row in source_rows]
    attacks = [dict(row) for row in attack_rows if str(row.get("attack_type")) == "cross_speaker_splice"]
    longform = [dict(row) for row in longform_rows]
    targets_by_speaker: dict[str, set[str]] = {}
    texts_by_speaker: dict[str, set[str]] = {}
    sequences_by_speaker: dict[str, set[str]] = {}
    split_by_speaker: dict[str, str] = {}
    for row in attacks:
        speaker = str(row["target_speaker"])
        targets_by_speaker.setdefault(speaker, set()).add(str(row["target_source_sample_id"]))
        texts_by_speaker.setdefault(speaker, set()).add(str(row["target_text_id"]))
        sequences_by_speaker.setdefault(speaker, set()).add(str(row["clean_sequence_id"]))
        prior = split_by_speaker.setdefault(speaker, str(row["split"]))
        if prior != str(row["split"]):
            raise A2ReadinessError(f"speaker crosses split: {speaker}")
    used_by_speaker: dict[str, set[str]] = {speaker: set() for speaker in targets_by_speaker}
    for row in longform:
        speaker = str(row["speaker"])
        if speaker in used_by_speaker and str(row["sequence_id"]) in sequences_by_speaker[speaker]:
            used_by_speaker[speaker].add(str(row["source_sample_id"]))
    out: list[dict[str, Any]] = []
    for speaker in sorted(targets_by_speaker):
        candidates: list[tuple[int, str, dict[str, Any], float, int]] = []
        for row in source:
            if str(row["speaker"]) != speaker or str(row["split"]) != split_by_speaker[speaker]:
                continue
            if str(row["sample_id"]) in targets_by_speaker[speaker] or str(row["sample_id"]) in used_by_speaker[speaker]:
                continue
            if str(row["text_id"]) in texts_by_speaker[speaker]:
                continue
            info = probe_audio(row["audio_path"])
            if not 3.0 <= info.duration <= 8.0:
                continue
            candidates.append((int(row["selection_rank"]), str(row["sample_id"]), row, info.duration, info.sample_rate))
        if not candidates:
            raise A2ReadinessError(f"no_eligible_reference for {speaker}")
        _, _, selected, duration, sample_rate = min(candidates, key=lambda item: (item[0], item[1]))
        path = Path(str(selected["audio_path"]))
        out.append({
            "speaker": speaker,
            "split": split_by_speaker[speaker],
            "reference_sample_id": str(selected["sample_id"]),
            "reference_audio_path": str(path),
            "reference_audio_relpath": str(selected["audio_relpath"]),
            "reference_text_id": str(selected["text_id"]),
            "reference_text_exact": str(selected["transcript_zh"]),
            "duration": duration,
            "sample_rate": sample_rate,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            "selection_rule": "same_speaker_split;different_target_utterance_text;absent_attacked_clean_sequence;3_to_8s;selection_rank_then_sample_id",
        })
    if len(out) != 12:
        raise A2ReadinessError(f"expected 12 frozen references, got {len(out)}")
    return out


def _frame_activity(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> tuple[np.ndarray, np.ndarray]:
    if sample_rate != SAMPLE_RATE:
        raise A2ReadinessError("activity rule is frozen at 16 kHz")
    wave = np.asarray(audio, dtype=np.float32)
    if wave.ndim != 1 or wave.size < FRAME_SAMPLES:
        raise A2ReadinessError("insufficient_audio_for_activity_frames")
    starts = np.arange(0, wave.size - FRAME_SAMPLES + 1, HOP_SAMPLES, dtype=np.int64)
    frames = np.stack([wave[start:start + FRAME_SAMPLES] for start in starts])
    rms = np.sqrt(np.mean(np.square(frames, dtype=np.float64), axis=1))
    dbfs = 20.0 * np.log10(np.maximum(rms, 1e-12))
    return starts, dbfs > ACTIVITY_THRESHOLD_DBFS


def trim_synthetic_silence(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> TrimResult:
    """Trim only synthetic edge silence with the frozen frame policy."""
    wave = np.asarray(audio, dtype=np.float32)
    if wave.ndim != 1 or not np.all(np.isfinite(wave)):
        raise A2ReadinessError("synthetic_audio_must_be_finite_mono")
    starts, active = _frame_activity(wave, sample_rate)
    if not np.any(active):
        raise A2ReadinessError("no_speech_detected")
    first = int(starts[np.flatnonzero(active)[0]])
    last = int(starts[np.flatnonzero(active)[-1]] + FRAME_SAMPLES)
    begin = max(0, first - RETAIN_EDGE_SAMPLES)
    end = min(wave.size, last + RETAIN_EDGE_SAMPLES)
    if end <= begin:
        raise A2ReadinessError("invalid_trim_bounds")
    return TrimResult(waveform=wave[begin:end].copy(), pretrim_num_samples=wave.size,
                      posttrim_num_samples=end - begin, leading_trim_samples=begin,
                      trailing_trim_samples=wave.size - end)


def active_speech_rms(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> float:
    wave = np.asarray(audio, dtype=np.float32)
    starts, active = _frame_activity(wave, sample_rate)
    if not np.any(active):
        raise A2ReadinessError("insufficient_active_speech")
    mask = np.zeros(wave.size, dtype=bool)
    for start in starts[active]:
        mask[start:start + FRAME_SAMPLES] = True
    values = wave[mask]
    rms = float(np.sqrt(np.mean(np.square(values, dtype=np.float64))))
    if not math.isfinite(rms) or rms <= 0:
        raise A2ReadinessError("invalid_active_speech_rms")
    return rms


def match_active_speech_rms(target: np.ndarray, synthetic: np.ndarray, sample_rate: int = SAMPLE_RATE) -> tuple[np.ndarray, GainResult]:
    target_rms = active_speech_rms(target, sample_rate)
    synth_rms = active_speech_rms(synthetic, sample_rate)
    raw = target_rms / synth_rms
    clamped = float(np.clip(raw, 0.25, 4.0))
    peak_pre_safe = float(np.max(np.abs(synthetic)) * clamped)
    peak_safe = min(1.0, 0.999 / peak_pre_safe) if peak_pre_safe > 0 else 1.0
    final = clamped * peak_safe
    out = np.asarray(synthetic, dtype=np.float32) * final
    return out.astype(np.float32), GainResult(target_rms, synth_rms, raw, clamped, peak_safe, final, float(np.max(np.abs(out))))


def replace_whole_utterance_with_crossfade(clean: np.ndarray, synthetic: np.ndarray, start: int, end: int, fade: int = CROSSFADE_SAMPLES) -> tuple[np.ndarray, CrossfadeLayout]:
    """Replace complete `[start,end)` natural speech with natural-duration synthetic audio."""
    clean_wave = np.asarray(clean, dtype=np.float32)
    synth = np.asarray(synthetic, dtype=np.float32)
    if clean_wave.ndim != 1 or synth.ndim != 1 or not np.all(np.isfinite(clean_wave)) or not np.all(np.isfinite(synth)):
        raise A2ReadinessError("waveforms_must_be_finite_mono")
    if not 0 <= start < end <= clean_wave.size:
        raise A2ReadinessError("complete_source_interval_out_of_bounds")
    source_length = end - start
    if fade <= 0 or 2 * fade >= min(source_length, synth.size):
        raise A2ReadinessError("INSUFFICIENT_SYNTHETIC_CORE")
    alpha_in = (np.arange(fade, dtype=np.float32) + 1.0) / (fade + 1.0)
    alpha_out = (np.arange(fade, 0, -1, dtype=np.float32)) / (fade + 1.0)
    replacement = synth.copy()
    replacement[:fade] = clean_wave[start:start + fade] * (1.0 - alpha_in) + synth[:fade] * alpha_in
    replacement[-fade:] = clean_wave[end - fade:end] * (1.0 - alpha_out) + synth[-fade:] * alpha_out
    output = np.concatenate((clean_wave[:start], replacement, clean_wave[end:])).astype(np.float32)
    attack_end = start + synth.size
    layout = CrossfadeLayout(
        attack_start_sample=start, attack_end_sample=attack_end,
        attack_core_start_sample=start + fade, attack_core_end_sample=attack_end - fade,
        blend_in_start_sample=start, blend_in_end_sample=start + fade,
        blend_out_start_sample=attack_end - fade, blend_out_end_sample=attack_end,
        source_real_num_samples=source_length, final_synthetic_num_samples=synth.size,
        duration_delta_samples=synth.size - source_length,
    )
    return output, layout


def validate_crossfade_reconstruction(clean: np.ndarray, synthetic: np.ndarray, output: np.ndarray, layout: CrossfadeLayout, source_end: int, fade: int = CROSSFADE_SAMPLES) -> None:
    start, end = layout.attack_start_sample, layout.attack_end_sample
    if not np.array_equal(np.asarray(output)[:start], np.asarray(clean)[:start]):
        raise A2ReadinessError("prefix_changed")
    if not np.array_equal(np.asarray(output)[end:], np.asarray(clean)[source_end:]):
        raise A2ReadinessError("suffix_content_changed")
    if output.size != clean.size + layout.duration_delta_samples:
        raise A2ReadinessError("output_length_mismatch")
    if not np.allclose(output[layout.attack_core_start_sample:layout.attack_core_end_sample], synthetic[fade:-fade], atol=0.0, rtol=0.0):
        raise A2ReadinessError("strict_core_not_synthetic")
    alpha_in = (np.arange(fade, dtype=np.float32) + 1.0) / (fade + 1.0)
    alpha_out = (np.arange(fade, 0, -1, dtype=np.float32)) / (fade + 1.0)
    expected_left = clean[start:start + fade] * (1.0 - alpha_in) + synthetic[:fade] * alpha_in
    expected_right = clean[source_end - fade:source_end] * (1.0 - alpha_out) + synthetic[-fade:] * alpha_out
    if not np.allclose(output[start:start + fade], expected_left, atol=0.0, rtol=0.0):
        raise A2ReadinessError("left_blend_mismatch")
    if not np.allclose(output[end - fade:end], expected_right, atol=0.0, rtol=0.0):
        raise A2ReadinessError("right_blend_mismatch")


SIDE_CAR_REQUIRED = {
    "paired_case_id", "target_source_sample_id", "target_speaker", "split", "reference_sample_id",
    "attack_generator", "attack_generator_family", "generator_checkpoint_sha256", "source_text_exact",
    "tts_input_text", "source_text_sha256", "tts_input_text_sha256", "clean_source_utterance_start_sample",
    "clean_source_utterance_end_sample", "source_real_num_samples", "generation_status", "generation_seed",
}


def validate_a2_sidecar_row(row: Mapping[str, Any]) -> None:
    missing = sorted(field for field in SIDE_CAR_REQUIRED if field not in row or row[field] in (None, ""))
    if missing:
        raise A2ReadinessError(f"sidecar missing required fields: {missing}")
    text_evidence = validate_same_text(str(row["source_text_exact"]), str(row["tts_input_text"]))
    if str(row["source_text_sha256"]).upper() != text_evidence["source_text_sha256"]:
        raise A2ReadinessError("source_text_sha256 does not match exact source text")
    if str(row["tts_input_text_sha256"]).upper() != text_evidence["tts_input_text_sha256"]:
        raise A2ReadinessError("tts_input_text_sha256 does not match exact input text")
    if str(row["generation_status"]) not in {"planned", "smoke", "success", "failed"}:
        raise A2ReadinessError("invalid generation_status")
    c0, c1 = int(row["clean_source_utterance_start_sample"]), int(row["clean_source_utterance_end_sample"])
    if c0 < 0 or c1 <= c0 or int(row["source_real_num_samples"]) != c1 - c0:
        raise A2ReadinessError("invalid complete source interval")
    if str(row["generation_status"]) in {"smoke", "success"}:
        fields = ("final_synthetic_num_samples", "duration_delta_samples", "clean_timeline_start_sample", "clean_timeline_end_sample", "manipulated_timeline_start_sample", "manipulated_timeline_end_sample", "attack_start_sample", "attack_end_sample", "attack_core_start_sample", "attack_core_end_sample", "blend_in_start_sample", "blend_in_end_sample", "blend_out_start_sample", "blend_out_end_sample", "crossfade_samples")
        absent = [field for field in fields if field not in row or row[field] in (None, "")]
        if absent:
            raise A2ReadinessError(f"generated sidecar missing fields: {absent}")
        if int(row["crossfade_samples"]) != CROSSFADE_SAMPLES:
            raise A2ReadinessError("crossfade must be 400 samples per edge")
        if int(row["attack_start_sample"]) != c0:
            raise A2ReadinessError("attack must start at complete source utterance start")
        if int(row["attack_end_sample"]) - c0 != int(row["final_synthetic_num_samples"]):
            raise A2ReadinessError("attack end must use natural synthetic duration")
        attack_end = int(row["attack_end_sample"])
        synthetic_length = int(row["final_synthetic_num_samples"])
        if int(row["duration_delta_samples"]) != synthetic_length - int(row["source_real_num_samples"]):
            raise A2ReadinessError("duration delta must reflect natural synthetic duration")
        if int(row["clean_timeline_start_sample"]) != c0 or int(row["clean_timeline_end_sample"]) != c1:
            raise A2ReadinessError("clean timeline must be the complete source utterance")
        if int(row["manipulated_timeline_start_sample"]) != c0 or int(row["manipulated_timeline_end_sample"]) != attack_end:
            raise A2ReadinessError("manipulated timeline must use the replacement duration")
        if int(row["attack_core_start_sample"]) != c0 + CROSSFADE_SAMPLES or int(row["attack_core_end_sample"]) != attack_end - CROSSFADE_SAMPLES:
            raise A2ReadinessError("strict core must exclude both fixed crossfades")
        if int(row["blend_in_start_sample"]) != c0 or int(row["blend_in_end_sample"]) != c0 + CROSSFADE_SAMPLES:
            raise A2ReadinessError("invalid left blend interval")
        if int(row["blend_out_start_sample"]) != attack_end - CROSSFADE_SAMPLES or int(row["blend_out_end_sample"]) != attack_end:
            raise A2ReadinessError("invalid right blend interval")


def serialize_roundtrip(audio: np.ndarray, path: str | Path, sample_rate: int = SAMPLE_RATE) -> dict[str, Any]:
    write_audio(path, np.asarray(audio, dtype=np.float32), sample_rate)
    restored, restored_sr = load_audio(path, target_sr=None)
    expected = np.asarray(audio, dtype=np.float32)
    if restored_sr != sample_rate or restored.shape != expected.shape:
        raise A2ReadinessError("serialization_roundtrip_shape_or_rate_failure")
    max_abs_error = float(np.max(np.abs(restored - expected)))
    if max_abs_error > 2.0 / 32768.0:
        raise A2ReadinessError("serialization_roundtrip_tolerance_failure")
    return {"serialization": "soundfile_default_pcm16", "sample_rate": restored_sr, "max_abs_error": max_abs_error}
