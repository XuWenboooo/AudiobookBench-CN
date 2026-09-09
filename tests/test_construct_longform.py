from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audiobookbench.data.construct_longform import (
    LONGFORM_TYPE,
    LongformValidationError,
    construct_longform_sequences,
    validate_longform_lineage,
)


def _records(tmp_path: Path) -> list[dict[str, object]]:
    records = []
    for speaker, split in (("speaker_a", "train"), ("speaker_b", "val")):
        for index in range(8):
            relpath = Path("raw") / speaker / f"u{index:02d}.wav"
            path = tmp_path / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            samples = np.full(8000, 0.01 * (index + 1), dtype=np.float32)
            sf.write(path, samples, 8000)
            records.append(
                {
                    "audio_path": str(path),
                    "audio_relpath": relpath.as_posix(),
                    "sample_id": f"{speaker}_u{index:02d}",
                    "speaker": speaker,
                    "split": split,
                    "selection_rank": index,
                    "is_manipulated": "false",
                }
            )
    return records


def test_constructed_sequences_preserve_lineage_and_alignment(tmp_path: Path) -> None:
    records = _records(tmp_path)
    before = {
        row["sample_id"]: hashlib.sha256(Path(row["audio_path"]).read_bytes()).hexdigest()
        for row in records
    }
    rows = construct_longform_sequences(
        records,
        dataset_root=tmp_path,
        repository_root=tmp_path,
        output_directory="constructed",
        target_sr=16000,
        gap_seconds=0.25,
        min_duration=3.0,
        preferred_duration=4.5,
        max_duration=6.0,
        min_utterances=3,
        max_utterances=5,
        sequences_per_speaker=1,
    )
    validate_longform_lineage(
        rows,
        source_sample_ids={str(row["sample_id"]) for row in records},
        check_audio=True,
    )

    sequence_ids = sorted({row["sequence_id"] for row in rows})
    assert len(sequence_ids) == len(set(sequence_ids)) == 2
    assert all(row["longform_type"] == LONGFORM_TYPE for row in rows)
    for sequence_id in sequence_ids:
        sequence = [row for row in rows if row["sequence_id"] == sequence_id]
        assert len({row["speaker"] for row in sequence}) == 1
        assert len({row["split"] for row in sequence}) == 1
        assert [row["source_order"] for row in sequence] == list(range(len(sequence)))
        assert all(row["source_sample_id"] in before for row in sequence)
        assert sequence[0]["gap_before"] == 0.0
        assert sequence[-1]["gap_after"] == 0.0
        for left, right in zip(sequence, sequence[1:]):
            assert left["gap_after"] == right["gap_before"] == 0.25
            assert left["gap_after_end"] == right["sequence_start"]
        audio, sr = sf.read(sequence[0]["sequence_audio_path"], dtype="float32")
        assert sr == 16000
        assert np.isfinite(audio).all()
        assert len(audio) == sequence[0]["sequence_num_samples"]
        assert len(audio) / sr == pytest.approx(sequence[0]["sequence_duration"], abs=1 / sr)

    after = {
        row["sample_id"]: hashlib.sha256(Path(row["audio_path"]).read_bytes()).hexdigest()
        for row in records
    }
    assert after == before


def test_same_speaker_cannot_cross_splits(tmp_path: Path) -> None:
    records = _records(tmp_path)
    records[0]["split"] = "test"
    with pytest.raises(LongformValidationError, match="speaker must not cross splits"):
        construct_longform_sequences(
            records,
            dataset_root=tmp_path,
            repository_root=tmp_path,
            output_directory="constructed",
            min_duration=1.0,
            preferred_duration=2.0,
            max_duration=4.0,
            min_utterances=2,
            max_utterances=4,
            sequences_per_speaker=1,
        )
