from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.a2_readiness import (
    A2ReadinessError,
    CROSSFADE_SAMPLES,
    active_speech_rms,
    match_active_speech_rms,
    replace_whole_utterance_with_crossfade,
    trim_synthetic_silence,
    validate_a2_sidecar_row,
    validate_crossfade_reconstruction,
    validate_same_text,
)
from audiobookbench.security.day8_detector_denylist import DetectorLeakageError, assert_detector_inputs_safe
from audiobookbench.data.manifest import load_manifest


REPOSITORY = Path(__file__).resolve().parents[1]


def _planned_row() -> dict[str, object]:
    return {
        "paired_case_id": "paircase_test", "target_source_sample_id": "target", "target_speaker": "spk",
        "split": "train", "reference_sample_id": "reference", "attack_generator": "CosyVoice2-0.5B",
        "attack_generator_family": "CosyVoice", "generator_checkpoint_sha256": "A" * 64,
        "source_text_exact": "完全一致的文本", "tts_input_text": "完全一致的文本",
        "source_text_sha256": validate_same_text("完全一致的文本", "完全一致的文本")["source_text_sha256"],
        "tts_input_text_sha256": validate_same_text("完全一致的文本", "完全一致的文本")["tts_input_text_sha256"],
        "clean_source_utterance_start_sample": 1200, "clean_source_utterance_end_sample": 3600,
        "source_real_num_samples": 2400, "generation_status": "planned", "generation_seed": 1,
    }


def test_same_text_contract_is_codepoint_exact() -> None:
    evidence = validate_same_text("测试", "测试")
    assert evidence["same_text_exact"] is True
    with pytest.raises(A2ReadinessError, match="code-point identical"):
        validate_same_text("测试", "测试 ")


def test_same_text_contract_rejects_non_nfc_source() -> None:
    with pytest.raises(A2ReadinessError, match="Unicode NFC"):
        validate_same_text("e\u0301", "e\u0301")


def test_crossfade_preserves_prefix_suffix_and_strict_core() -> None:
    clean = np.linspace(-0.5, 0.5, 10_000, dtype=np.float32)
    synthetic = np.linspace(0.3, -0.3, 3_000, dtype=np.float32)
    output, layout = replace_whole_utterance_with_crossfade(clean, synthetic, 2_000, 4_500)
    validate_crossfade_reconstruction(clean, synthetic, output, layout, 4_500)
    assert layout.attack_start_sample == 2_000
    assert layout.attack_core_start_sample == 2_000 + CROSSFADE_SAMPLES
    assert layout.duration_delta_samples == 500
    assert np.array_equal(output[layout.attack_core_start_sample:layout.attack_core_end_sample], synthetic[400:-400])


def test_crossfade_fails_closed_without_a_core() -> None:
    with pytest.raises(A2ReadinessError, match="INSUFFICIENT_SYNTHETIC_CORE"):
        replace_whole_utterance_with_crossfade(np.zeros(2_000, dtype=np.float32), np.zeros(800, dtype=np.float32), 500, 1_500)


def test_trim_keeps_fixed_frame_margin() -> None:
    wave = np.concatenate((np.zeros(1600, dtype=np.float32), np.full(3200, 0.1, dtype=np.float32), np.zeros(1600, dtype=np.float32)))
    result = trim_synthetic_silence(wave)
    assert result.leading_trim_samples == 480
    assert result.trailing_trim_samples == 560
    with pytest.raises(A2ReadinessError, match="no_speech_detected"):
        trim_synthetic_silence(np.zeros(2_000, dtype=np.float32))


def test_rms_gain_is_clamped_and_peak_safe() -> None:
    target = np.full(3_200, 0.1, dtype=np.float32)
    synthetic = np.full(3_200, 0.01, dtype=np.float32)
    scaled, metadata = match_active_speech_rms(target, synthetic)
    assert metadata.clamped_gain == 4.0
    assert metadata.peak_after_gain < 1.0
    assert active_speech_rms(scaled) > active_speech_rms(synthetic)


def test_sidecar_requires_complete_utterance_and_generated_timeline() -> None:
    row = _planned_row()
    validate_a2_sidecar_row(row)
    generated = deepcopy(row)
    generated.update({
            "generation_status": "smoke", "final_synthetic_num_samples": 2800,
            "duration_delta_samples": 400, "attack_start_sample": 1200, "attack_end_sample": 4000,
            "clean_timeline_start_sample": 1200, "clean_timeline_end_sample": 3600,
            "manipulated_timeline_start_sample": 1200, "manipulated_timeline_end_sample": 4000,
        "attack_core_start_sample": 1600, "attack_core_end_sample": 3600,
        "blend_in_start_sample": 1200, "blend_in_end_sample": 1600,
        "blend_out_start_sample": 3600, "blend_out_end_sample": 4000,
        "crossfade_samples": 400,
    })
    validate_a2_sidecar_row(generated)
    generated["attack_start_sample"] = 1201
    with pytest.raises(A2ReadinessError, match="complete source utterance start"):
        validate_a2_sidecar_row(generated)


def test_detector_inputs_reject_reference_and_attack_side_data() -> None:
    assert_detector_inputs_safe({"waveform": [0.1], "features": {"rms": 0.2}})
    with pytest.raises(DetectorLeakageError):
        assert_detector_inputs_safe({"reference_audio_path": "forbidden.wav"})
    with pytest.raises(DetectorLeakageError):
        assert_detector_inputs_safe({"attack_side_embedding": [0.1]})


def test_corrected_protocol_keeps_whole_utterance_natural_duration_and_crossfade() -> None:
    protocol = (REPOSITORY / "WEEK2_A2_PROTOCOL_DESIGN.md").read_text(encoding="utf-8")
    correction = (REPOSITORY / "WEEK2_A2_PREIMPLEMENTATION_CORRECTION.md").read_text(encoding="utf-8")
    assert "whole-utterance" in protocol.lower()
    assert "natural" in protocol.lower()
    assert "400" in correction
    assert "0.75" in correction and "forbidden" in correction.lower()


def test_frozen_reference_manifest_has_one_eligible_row_per_target_speaker() -> None:
    references = load_manifest(REPOSITORY / "data/manifests/week2a_reference_manifest.csv")
    planned = load_manifest(REPOSITORY / "data/manifests/week2a_a2_planned_manifest.csv")
    assert len(references) == 12
    assert len({row["speaker"] for row in references}) == 12
    by_speaker = {row["speaker"]: row for row in references}
    for row in planned:
        reference = by_speaker[row["target_speaker"]]
        assert reference["split"] == row["split"]
        assert reference["reference_sample_id"] != row["target_source_sample_id"]
        assert 3.0 <= float(reference["duration"]) <= 8.0


def test_reference_does_not_appear_in_any_attacked_sequence_for_its_speaker() -> None:
    references = load_manifest(REPOSITORY / "data/manifests/week2a_reference_manifest.csv")
    planned = load_manifest(REPOSITORY / "data/manifests/week2a_a2_planned_manifest.csv")
    attacked = {}
    for row in planned:
        attacked.setdefault(row["target_speaker"], set()).add(row["target_source_sample_id"])
    assert all(row["reference_sample_id"] not in attacked[row["speaker"]] for row in references)


@pytest.mark.parametrize("synthetic_length,source_end", [(1800, 3600), (3000, 5200), (2400, 6600), (2000, 3300), (2600, 10000)])
def test_variable_duration_timeline_has_sample_first_suffix_shift(synthetic_length: int, source_end: int) -> None:
    start = source_end - 2400
    clean = np.arange(12_000, dtype=np.float32)
    synthetic = np.linspace(-0.1, 0.1, synthetic_length, dtype=np.float32)
    output, layout = replace_whole_utterance_with_crossfade(clean, synthetic, start, source_end)
    validate_crossfade_reconstruction(clean, synthetic, output, layout, source_end)
    assert output.size == clean.size - 2400 + synthetic_length
    assert layout.attack_end_sample == start + synthetic_length
    assert layout.duration_delta_samples == synthetic_length - 2400


def test_planned_sidecars_explicitly_forbid_week1_short_interval_reuse() -> None:
    planned = load_manifest(REPOSITORY / "data/manifests/week2a_a2_planned_manifest.csv")
    assert len(planned) == 23
    for row in planned:
        assert row["week1_lineage_only"] == "True"
        assert "week1_duration_tier" in row["week1_forbidden_interval_fields"]
        assert int(row["clean_source_utterance_end_sample"]) > int(row["clean_source_utterance_start_sample"])


def test_detector_denylist_rejects_all_reserved_prefixes() -> None:
    for key in ("reference_id", "conditioning_vector", "speaker_enrollment_id"):
        with pytest.raises(DetectorLeakageError):
            assert_detector_inputs_safe({key: "forbidden"})


def test_protocol_config_records_dual_timeline_and_sample_first_gt() -> None:
    config = (REPOSITORY / "configs/week2a_a2_protocol_draft.yaml").read_text(encoding="utf-8")
    assert "clean_timeline" in config
    assert "manipulated_timeline" in config
    assert "zero_based_half_open_samples" in config
    assert "400" in config


def test_attack_and_core_are_half_open_intervals() -> None:
    clean = np.zeros(8_000, dtype=np.float32)
    synthetic = np.ones(2_400, dtype=np.float32) * 0.1
    _, layout = replace_whole_utterance_with_crossfade(clean, synthetic, 1_600, 4_000)
    assert layout.attack_start_sample < layout.attack_core_start_sample < layout.attack_core_end_sample < layout.attack_end_sample
    assert layout.blend_in_end_sample == layout.attack_core_start_sample
    assert layout.blend_out_start_sample == layout.attack_core_end_sample
