"""Audit an acquired OpenSLR SLR68 subset without loading samples or models."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import wave


OFFICIAL_PAGE = "https://www.openslr.org/68/"
OFFICIAL_PROVIDER = "https://openslr.magicdatatech.com/resources/68/"
LICENSE = "CC BY-NC-ND 4.0"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def read_speaker_info(path: Path) -> tuple[dict[str, dict[str, str]], int]:
    rows: dict[str, dict[str, str]] = {}
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) != 4 or fields[0] == "SPKID":
            if line.strip() and not line.startswith("SPKID\t"):
                malformed += 1
            continue
        speaker, age, gender, dialect = (field.strip() for field in fields)
        if not speaker or speaker in rows:
            malformed += 1
            continue
        rows[speaker] = {"age": age, "gender": gender, "dialect": dialect}
    return rows, malformed


def read_transcripts(path: Path) -> tuple[dict[str, tuple[str, str]], int]:
    rows: dict[str, tuple[str, str]] = {}
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t", 2)
        if fields and fields[0] == "UtteranceID":
            continue
        if len(fields) != 3 or not fields[0].strip() or not fields[1].strip():
            malformed += 1
            continue
        utterance_id, speaker_id, text = (field.strip() for field in fields)
        if utterance_id in rows:
            malformed += 1
            continue
        rows[Path(utterance_id).stem] = (speaker_id, text)
    return rows, malformed


def audit(root: Path, metadata_root: Path, archive_path: Path | None = None, include_records: bool = False) -> dict[str, object]:
    speaker_info, malformed_speakers = read_speaker_info(metadata_root / "SPKINFO.txt")
    transcript_path = root / "TRANS.txt"
    transcripts, malformed_transcripts = read_transcripts(transcript_path)
    records: list[dict[str, object]] = []
    format_counts: dict[str, int] = {}
    eligible_by_speaker: dict[str, int] = {}
    invalid_wav = 0
    for path in sorted(root.rglob("*.wav")):
        relative = path.relative_to(root).as_posix()
        utterance_id = path.stem
        speaker_id = path.parent.name
        try:
            with wave.open(str(path), "rb") as handle:
                channels = handle.getnchannels()
                sample_rate = handle.getframerate()
                sample_width = handle.getsampwidth()
                frames = handle.getnframes()
        except (EOFError, wave.Error) as exc:
            invalid_wav += 1
            records.append({"path": relative, "utterance_id": utterance_id, "speaker_id": speaker_id, "status": "INVALID_WAV", "error": str(exc)})
            continue
        duration = frames / sample_rate if sample_rate else 0.0
        format_key = f"{sample_rate}Hz/{channels}ch/{sample_width}byte"
        format_counts[format_key] = format_counts.get(format_key, 0) + 1
        transcript = transcripts.get(utterance_id)
        eligible = (
            8.0 <= duration <= 30.0
            and sample_rate == 16_000
            and channels == 1
            and sample_width == 2
            and transcript is not None
            and transcript[0] == speaker_id
        )
        if eligible:
            eligible_by_speaker[speaker_id] = eligible_by_speaker.get(speaker_id, 0) + 1
        row: dict[str, object] = {
            "path": relative,
            "utterance_id": utterance_id,
            "speaker_id": speaker_id,
            "duration_sec": duration,
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "audio_size_bytes": path.stat().st_size,
            "transcript_present": transcript is not None and transcript[0] == speaker_id,
            "text_sha256": sha256_text(transcript[1]) if transcript is not None and transcript[0] == speaker_id else None,
            "eligible_under_frozen_filter": eligible,
        }
        if include_records:
            row["source_audio_sha256"] = sha256_path(path)
        records.append(row)
    valid = [row for row in records if row.get("status") != "INVALID_WAV"]
    eligible = [row for row in valid if row.get("eligible_under_frozen_filter") is True]
    audio_speakers = {str(row["speaker_id"]) for row in valid}
    eligible_speakers = {str(row["speaker_id"]) for row in eligible}
    return {
        "schema_version": "topconf.level2.slr68-feasibility.v1",
        "status": "AUDITED_METADATA_AND_WAV_HEADERS",
        "corpus_id": "MAGICDATA_SLR68",
        "corpus_name": "MAGICDATA Mandarin Chinese Read Speech Corpus",
        "source_authority": "MAGIC DATA Technology Co., Ltd. via OpenSLR SLR68",
        "official_page": OFFICIAL_PAGE,
        "official_resource_base": OFFICIAL_PROVIDER,
        "license": LICENSE,
        "language": "Mandarin Chinese",
        "speaker_metadata": {
            "path": str((metadata_root / "SPKINFO.txt").resolve()),
            "rows": len(speaker_info),
            "unique_ids": len(speaker_info),
            "malformed_rows": malformed_speakers,
            "observed_speaker_ids": sorted(speaker_info),
        },
        "transcription": {
            "path": str(transcript_path.resolve()),
            "unique_ids": len(transcripts),
            "malformed_rows": malformed_transcripts,
        },
        "frozen_filter": {
            "duration_sec_inclusive": [8, 30],
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_width_bytes": 2,
            "requires_transcript": True,
            "selection_is_model_free": True,
        },
        "counts": {
            "wav_files": len(records),
            "valid_wav_files": len(valid),
            "invalid_wav_files": invalid_wav,
            "all_speakers_from_audio": len(audio_speakers),
            "eligible_wav_files": len(eligible),
            "eligible_speakers": len(eligible_speakers),
            "eligible_files_by_speaker": dict(sorted(eligible_by_speaker.items())),
            "format_counts": dict(sorted(format_counts.items())),
        },
        "archive": {
            "path": str(archive_path.resolve()) if archive_path else None,
            "observed_sha256": sha256_path(archive_path) if archive_path else None,
            "observed_bytes": archive_path.stat().st_size if archive_path else None,
        },
        "records": records,
        "historical_usage": "NONE_FOUND_IN_REPOSITORY_AND_REFS_SCAN; final post-freeze proof required",
        "freshness_eligibility": "PENDING_FINAL_HISTORICAL_EXCLUSION_AND_CROSS_CORPUS_IDENTITY_REVIEW",
        "model_inference_runs": 0,
        "scientific_outcomes_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    result = audit(args.root, args.metadata_root, args.archive, include_records=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
