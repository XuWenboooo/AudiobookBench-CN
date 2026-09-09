from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from audiobookbench.data.manifest import (
    REQUIRED_COLUMNS,
    ManifestValidationError,
    load_manifest,
    save_manifest,
    validate_manifest,
    validate_pair_split_integrity,
    validate_source_lineage,
)

EXAMPLE_MANIFEST = Path("data/manifests/example_manifest.csv")


def _clean_record() -> dict[str, object]:
    return {
        "audio_path": "data/raw/example_tts.wav",
        "sample_id": "tts_demo_001",
        "pair_id": "tts_pair_001",
        "source_sample_id": "tts_demo_001",
        "source_type": "tts",
        "generator": "example_tts",
        "generator_family": "unknown_tts",
        "speaker": "tts_spk_001",
        "text_id": "text_demo_001",
        "duration": "12.0",
        "sample_rate": "16000",
        "segment_id": "tts_demo_001_seg000",
        "segment_start": "0.0",
        "segment_end": "4.0",
        "position": "0",
        "is_manipulated": "false",
        "attack_type": "",
        "attack_start": "",
        "attack_end": "",
        "attack_generator": "",
        "source_generator": "example_tts",
        "replacement_speaker": "",
        "split": "test",
    }


def _valid_record() -> dict[str, object]:
    return {
        "audio_path": "data/manipulated/example_attack.wav",
        "sample_id": "attack_demo_001",
        "pair_id": "tts_pair_001",
        "source_sample_id": "tts_demo_001",
        "source_type": "tts",
        "generator": "example_tts",
        "generator_family": "unknown_tts",
        "speaker": "tts_spk_001",
        "text_id": "text_demo_001",
        "duration": "12.0",
        "sample_rate": "16000",
        "segment_id": "attack_demo_001_seg001",
        "segment_start": "4.0",
        "segment_end": "8.0",
        "position": "1",
        "is_manipulated": "true",
        "attack_type": "localized_tts_segment_replacement",
        "attack_start": "4.0",
        "attack_end": "8.0",
        "attack_generator": "example_tts_B",
        "source_generator": "example_tts",
        "replacement_speaker": "tts_spk_002",
        "split": "test",
    }


def _expect_invalid(records: list[dict[str, object]], message: str | None = None) -> None:
    with pytest.raises(ManifestValidationError, match=message):
        validate_manifest(records)


def test_load_manifest_reads_example_manifest() -> None:
    records = load_manifest(EXAMPLE_MANIFEST)
    assert len(records) == 3
    assert set(REQUIRED_COLUMNS).issubset(records[0].keys())
    assert records[0]["source_type"] == "natural"
    assert records[2]["source_type"] == "tts"
    assert records[2]["is_manipulated"] == "true"
    assert records[2]["source_sample_id"] == records[1]["sample_id"]


def test_validate_manifest_accepts_example_manifest() -> None:
    records = load_manifest(EXAMPLE_MANIFEST)
    validate_manifest(records)


def test_save_manifest_roundtrip_csv(tmp_path: Path) -> None:
    records = load_manifest(EXAMPLE_MANIFEST)
    out = tmp_path / "roundtrip.csv"
    save_manifest(records, out)
    loaded = load_manifest(out)
    validate_manifest(loaded)
    assert loaded[0]["sample_id"] == records[0]["sample_id"]


def test_missing_required_column_raises() -> None:
    clean = _clean_record()
    attack = _valid_record()
    del attack["pair_id"]
    _expect_invalid([clean, attack], "missing required columns")


def test_illegal_source_type_raises() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["source_type"] = "manipulated"
    _expect_invalid([clean, attack], "source_type")


def test_illegal_split_raises() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["split"] = "dev"
    _expect_invalid([clean, attack], "split")


def test_manipulated_missing_attack_interval_raises() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["attack_start"] = ""
    _expect_invalid([clean, attack], "attack_start and attack_end")


def test_segment_start_must_be_before_segment_end() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["segment_start"] = "8.0"
    attack["segment_end"] = "8.0"
    _expect_invalid([clean, attack], "segment_start must be < segment_end")


def test_attack_start_must_be_before_attack_end() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["attack_start"] = "8.0"
    attack["attack_end"] = "8.0"
    _expect_invalid([clean, attack], "attack_start must be < attack_end")


def test_clean_and_manipulated_can_share_source_type() -> None:
    clean = _clean_record()
    attack = _valid_record()
    assert clean["source_type"] == attack["source_type"] == "tts"
    validate_manifest([clean, attack])


def test_duration_must_be_positive() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["duration"] = "0"
    _expect_invalid([clean, attack], "duration must be > 0")


def test_sample_rate_must_be_positive() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["sample_rate"] = "0"
    _expect_invalid([clean, attack], "sample_rate must be > 0")


def test_clean_source_sample_id_must_self_reference() -> None:
    clean = _clean_record()
    clean["source_sample_id"] = "other_clean"
    _expect_invalid([clean], "clean rows must self-reference")


def test_manipulated_source_sample_id_must_be_distinct() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["source_sample_id"] = attack["sample_id"]
    _expect_invalid([clean, attack], "distinct clean source_sample_id")


def test_pair_id_cannot_cross_splits() -> None:
    clean = _clean_record()
    attack = _valid_record()
    attack["split"] = "train"
    with pytest.raises(ManifestValidationError, match="pair_id must not cross splits"):
        validate_pair_split_integrity([clean, attack])


def test_manipulated_source_must_exist() -> None:
    attack = _valid_record()
    with pytest.raises(ManifestValidationError, match="missing clean source_sample_id"):
        validate_source_lineage([attack])


def test_manipulated_source_must_match_pair_and_split() -> None:
    clean = _clean_record()
    attack = _valid_record()
    clean["pair_id"] = "different_pair"
    with pytest.raises(ManifestValidationError, match="same pair_id and split"):
        validate_source_lineage([clean, attack])
