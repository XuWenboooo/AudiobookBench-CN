from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audiobookbench.data.construct_longform import construct_longform_sequences
from audiobookbench.security.manipulation_dataset import (
    A0,
    A1,
    AttackValidationError,
    build_day4_attacks,
    load_attack_manifest,
    save_attack_manifest,
    select_donor,
    validate_attack_manifest,
    verify_attack_waveforms,
)


def _source_records(tmp_path: Path) -> list[dict[str, object]]:
    rows = []
    for speaker, split, frequency in (("speaker_a", "train", 180), ("speaker_b", "train", 260), ("speaker_c", "val", 340)):
        for index in range(12):
            relpath = Path("raw") / split / speaker / f"u{index:02d}.wav"
            path = tmp_path / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            sr = 8000
            t = np.arange(sr * 2, dtype=np.float32) / sr
            waveform = (0.03 + index * 0.001) * np.sin(2 * np.pi * frequency * t)
            sf.write(path, waveform, sr)
            rows.append({
                "audio_path": str(path), "audio_relpath": relpath.as_posix(),
                "sample_id": f"{speaker}_u{index:02d}", "speaker": speaker,
                "split": split, "selection_rank": index, "is_manipulated": "false",
                "text_id": f"text_{speaker}_{index:02d}",
                "transcript_zh": f"测试文本{speaker}{index:02d}",
            })
    return rows


@pytest.fixture
def generated_attacks(tmp_path: Path):
    sources = _source_records(tmp_path)
    clean_rows = construct_longform_sequences(
        sources, dataset_root=tmp_path, repository_root=tmp_path,
        output_directory="clean", target_sr=16000, gap_seconds=0.3,
        min_duration=8.0, preferred_duration=10.0, max_duration=16.0,
        min_utterances=4, max_utterances=6, sequences_per_speaker=1,
    )
    clean_hashes = {
        row["sequence_audio_path"]: hashlib.sha256(Path(row["sequence_audio_path"]).read_bytes()).hexdigest()
        for row in clean_rows
    }
    attacks, skips = build_day4_attacks(
        clean_rows, sources, dataset_root=tmp_path, repository_root=tmp_path,
        a0_directory="generated/a0", a1_directory="generated/a1",
        sample_rate=16000, allowed_splits=("train",),
        a1_duration_tiers=(0.75,), a1_margin_seconds=0.25,
        crossfade_seconds=0.025, rms_gain_min=0.25, rms_gain_max=4.0,
    )
    return tmp_path, sources, clean_rows, clean_hashes, attacks, skips


def test_donor_selection_is_deterministic_same_split_and_different_speaker(tmp_path: Path) -> None:
    sources = _source_records(tmp_path)
    first, _ = select_donor(sources, target_speaker="speaker_a", split="train", required_samples=1000, dataset_root=tmp_path)
    second, _ = select_donor(reversed(sources), target_speaker="speaker_a", split="train", required_samples=1000, dataset_root=tmp_path)
    assert first["sample_id"] == second["sample_id"] == "speaker_b_u00"
    assert first["speaker"] != "speaker_a"
    assert first["split"] == "train"


def test_impossible_single_speaker_split_is_rejected(tmp_path: Path) -> None:
    sources = _source_records(tmp_path)
    with pytest.raises(AttackValidationError, match="no same-split different-speaker donor"):
        select_donor(sources, target_speaker="speaker_c", split="val", required_samples=1000, dataset_root=tmp_path)


def test_attack_selection_lineage_and_ids(generated_attacks) -> None:
    _, _, _, _, attacks, skips = generated_attacks
    assert len(attacks) == 4
    assert {row["attack_type"] for row in attacks} == {A0, A1}
    assert len({row["attack_id"] for row in attacks}) == len(attacks)
    assert len({row["manipulated_sequence_id"] for row in attacks}) == len(attacks)
    assert all(row["clean_sequence_id"] in row["attack_id"] for row in attacks)
    assert all(row["sequence_pair_id"].startswith("longform_pair_") for row in attacks)
    assert all(row["donor_source_sample_id"] for row in attacks)
    assert all(row["source_type"] == "natural" for row in attacks)
    assert all(row["longform_type"] == "constructed" for row in attacks)
    assert len(skips) == 2
    assert {row["split"] for row in skips} == {"val"}


def test_attack_selection_and_waveforms_are_deterministic(generated_attacks) -> None:
    tmp_path, sources, clean_rows, _, first_attacks, first_skips = generated_attacks
    second_attacks, second_skips = build_day4_attacks(
        clean_rows, sources, dataset_root=tmp_path, repository_root=tmp_path,
        a0_directory="regenerated/a0", a1_directory="regenerated/a1",
        sample_rate=16000, allowed_splits=("train",),
        a1_duration_tiers=(0.75,), a1_margin_seconds=0.25,
        crossfade_seconds=0.025, rms_gain_min=0.25, rms_gain_max=4.0,
    )
    selection_fields = (
        "attack_id", "attack_type", "clean_sequence_id", "target_source_sample_id",
        "target_source_order", "donor_source_sample_id", "attack_start_sample",
        "attack_end_sample", "attack_core_start_sample", "attack_core_end_sample",
        "donor_start_sample", "donor_end_sample", "rms_gain", "crossfade_samples",
    )
    assert [tuple(row[field] for field in selection_fields) for row in first_attacks] == [
        tuple(row[field] for field in selection_fields) for row in second_attacks
    ]
    assert first_skips == second_skips
    first_hashes = [hashlib.sha256(Path(row["manipulated_audio_path"]).read_bytes()).hexdigest() for row in first_attacks]
    second_hashes = [hashlib.sha256(Path(row["manipulated_audio_path"]).read_bytes()).hexdigest() for row in second_attacks]
    assert first_hashes == second_hashes


def test_boundaries_crossfade_and_gain_are_valid(generated_attacks) -> None:
    _, _, clean_rows, _, attacks, _ = generated_attacks
    lineage = {(row["sequence_id"], int(row["source_order"])): row for row in clean_rows}
    validate_attack_manifest(attacks)
    for row in attacks:
        sr = int(row["sample_rate"])
        assert float(row["attack_start"]) == int(row["attack_start_sample"]) / sr
        assert float(row["attack_end"]) == int(row["attack_end_sample"]) / sr
        assert 0 <= int(row["attack_start_sample"]) < int(row["attack_end_sample"]) <= int(row["sequence_num_samples"])
        assert np.isfinite(float(row["rms_gain"]))
        assert 0.25 <= float(row["rms_gain"]) <= 4.0
        if row["attack_type"] == A0:
            assert int(row["crossfade_samples"]) == 0
        else:
            assert int(row["crossfade_samples"]) == 400
            target = lineage[(row["clean_sequence_id"], int(row["target_source_order"]))]
            assert int(row["attack_start_sample"]) > round(float(target["sequence_start"]) * sr)
            assert int(row["attack_end_sample"]) < round(float(target["sequence_end"]) * sr)
            assert int(row["attack_core_start_sample"]) - int(row["attack_start_sample"]) == 400
            assert int(row["attack_end_sample"]) - int(row["attack_core_end_sample"]) == 400


def test_waveform_verification_and_clean_immutability(generated_attacks) -> None:
    _, sources, _, clean_hashes, attacks, _ = generated_attacks
    results = verify_attack_waveforms(attacks, sources, dataset_root=generated_attacks[0])
    assert len(results) == len(attacks)
    assert all(result["outside_equal"] and result["inside_changed"] and result["core_matches_donor"] for result in results)
    for row in attacks:
        clean = sf.info(row["clean_audio_path"])
        manipulated = sf.info(row["manipulated_audio_path"])
        assert clean.frames == manipulated.frames
        assert clean.samplerate == manipulated.samplerate
        waveform, _ = sf.read(row["manipulated_audio_path"], dtype="float32")
        assert np.isfinite(waveform).all()
    after = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in clean_hashes}
    assert after == clean_hashes


def test_attack_manifest_roundtrip(generated_attacks) -> None:
    tmp_path, _, _, _, attacks, _ = generated_attacks
    path = tmp_path / "attack_manifest.csv"
    save_attack_manifest(attacks, path)
    loaded = load_attack_manifest(path)
    validate_attack_manifest(loaded)
    assert [row["attack_id"] for row in loaded] == [row["attack_id"] for row in attacks]
