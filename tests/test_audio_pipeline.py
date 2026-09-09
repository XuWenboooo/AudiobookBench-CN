from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audiobookbench.data.manifest import validate_manifest
from audiobookbench.data.prepare_audio import (
    build_segment_manifest,
    load_source_catalog,
    prepare_real_audio_manifest,
)
from audiobookbench.preprocessing.audio_io import load_audio, probe_audio
from audiobookbench.preprocessing.segment import fixed_windows, simple_energy_vad, voiced_ratio


def _write_test_wav(path: Path, *, sr: int = 8000, duration: float = 2.4) -> None:
    """Create a tiny deterministic unit-test WAV, never research evidence."""
    n = int(sr * duration)
    t = np.arange(n, dtype=np.float32) / sr
    audio = np.zeros(n, dtype=np.float32)
    active = (t >= 0.4) & (t < 2.0)
    audio[active] = 0.2 * np.sin(2 * np.pi * 220.0 * t[active])
    sf.write(path, audio, sr)


def _catalog_row(audio_path: Path) -> dict[str, str]:
    return {
        "audio_path": str(audio_path),
        "sample_id": "unit_audio_001",
        "pair_id": "unit_pair_001",
        "source_sample_id": "unit_audio_001",
        "source_type": "natural",
        "generator": "human",
        "generator_family": "human",
        "speaker": "unit_speaker",
        "text_id": "unit_text",
        "is_manipulated": "false",
        "attack_type": "",
        "attack_start": "",
        "attack_end": "",
        "attack_generator": "",
        "source_generator": "human",
        "replacement_speaker": "",
        "split": "train",
    }


def test_probe_and_load_audio_resamples(tmp_path: Path) -> None:
    wav = tmp_path / "fixture.wav"
    _write_test_wav(wav, sr=8000, duration=1.0)
    info = probe_audio(wav)
    assert info.sample_rate == 8000
    assert info.channels == 1
    assert info.duration == pytest.approx(1.0, abs=1e-3)

    audio, sr = load_audio(wav, target_sr=16000)
    assert sr == 16000
    assert len(audio) == pytest.approx(16000, abs=4)
    assert np.isfinite(audio).all()


def test_fixed_windows_merges_tiny_tail() -> None:
    segments = fixed_windows(10.4, window_seconds=5.0, min_tail_seconds=1.0)
    assert [(s.start, s.end) for s in segments] == [(0.0, 5.0), (5.0, 10.4)]


def test_fixed_windows_merges_tiny_tail_after_first_window() -> None:
    segments = fixed_windows(5.4, window_seconds=5.0, min_tail_seconds=1.0)
    assert [(s.start, s.end) for s in segments] == [(0.0, 5.4)]


def test_energy_vad_distinguishes_silence_from_tone() -> None:
    sr = 16000
    silence = np.zeros(sr, dtype=np.float32)
    t = np.arange(sr, dtype=np.float32) / sr
    tone = 0.2 * np.sin(2 * np.pi * 220.0 * t)
    assert simple_energy_vad(silence).sum() == 0
    assert voiced_ratio(tone, sr) > 0.9


def test_build_segment_manifest_from_audio(tmp_path: Path) -> None:
    wav = tmp_path / "real_pipeline_fixture.wav"
    _write_test_wav(wav, sr=8000, duration=2.4)
    rows = build_segment_manifest(
        [_catalog_row(wav)],
        target_sr=16000,
        window_seconds=1.0,
        min_tail_seconds=0.5,
    )
    assert len(rows) == 2
    validate_manifest(rows)
    assert rows[0]["sample_rate"] == 16000
    assert rows[0]["original_sample_rate"] == 8000
    assert rows[0]["segment_start"] == 0.0
    assert rows[-1]["segment_end"] == pytest.approx(2.4)
    assert 0.0 <= rows[0]["vad_voiced_ratio"] <= 1.0


def test_prepare_real_audio_manifest_writes_valid_csv(tmp_path: Path) -> None:
    wav = tmp_path / "fixture.wav"
    _write_test_wav(wav, sr=16000, duration=1.8)
    catalog = tmp_path / "source_audio.csv"
    row = _catalog_row(wav)
    with catalog.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    loaded_catalog = load_source_catalog(catalog)
    assert loaded_catalog[0]["sample_id"] == "unit_audio_001"

    output = tmp_path / "week1_manifest.csv"
    rows = prepare_real_audio_manifest(
        catalog,
        output,
        target_sr=16000,
        window_seconds=1.0,
        min_tail_seconds=0.5,
    )
    assert output.exists()
    assert len(rows) == 2
    validate_manifest(rows)


def test_day3_catalog_rejects_manipulated_input(tmp_path: Path) -> None:
    wav = tmp_path / "fixture.wav"
    _write_test_wav(wav)
    row = _catalog_row(wav)
    row["is_manipulated"] = "true"
    row["attack_type"] = "replacement"
    row["attack_start"] = "0.4"
    row["attack_end"] = "0.8"
    with pytest.raises(Exception, match="Day 3 real-audio ingestion accepts clean source rows only"):
        build_segment_manifest([row])
