"""Audit AISHELL-1 metadata and WAV headers without loading audio samples or models."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile
import wave


OFFICIAL_PAGE = "https://www.openslr.org/33/"
OFFICIAL_AUDIO_URL = "https://openslr.trmal.net/resources/33/data_aishell.tgz"
OFFICIAL_RESOURCE_URL = "https://openslr.trmal.net/resources/33/resource_aishell.tgz"
EXPECTED_AUDIO_BYTES = 15_582_913_665
SPEAKER_RE = re.compile(r"S(\d{4})", re.IGNORECASE)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _speaker_info(path: Path) -> tuple[dict[str, str], list[str]]:
    rows: dict[str, str] = {}
    malformed: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 2 or fields[1] not in {"M", "F"}:
            malformed.append(line)
            continue
        rows[fields[0]] = fields[1]
    return rows, malformed


def _transcript_ids(path: Path) -> tuple[dict[str, str], int]:
    ids: dict[str, str] = {}
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) != 2 or not fields[0]:
            malformed += 1
            continue
        ids[fields[0]] = fields[1]
    return ids, malformed


def _first_file(*paths: Path) -> Path | None:
    return next((path for path in paths if path.is_file()), None)


def _hash_stream(fileobj: object) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: fileobj.read(1024 * 1024), b""):  # type: ignore[attr-defined]
        digest.update(block)
    return digest.hexdigest().upper()


def audit(root: Path, *, include_records: bool = False) -> dict[str, object]:
    resource_root = root / "resource_aishell"
    data_root = root / "data_aishell"
    speaker_path = resource_root / "speaker.info"
    transcript_path = data_root / "transcript" / "aishell_transcript_v0.8.txt"
    wav_root = data_root / "wav"
    if not speaker_path.is_file():
        raise FileNotFoundError(f"missing speaker metadata: {speaker_path}")
    if not wav_root.is_dir():
        raise FileNotFoundError(f"missing extracted WAV root: {wav_root}")

    speakers, malformed_speaker_rows = _speaker_info(speaker_path)
    transcript_texts: dict[str, str] = {}
    malformed_transcript_rows = None
    if transcript_path.is_file():
        transcript_texts, malformed_transcript_rows = _transcript_ids(transcript_path)

    records: list[dict[str, object]] = []
    format_counts: dict[str, int] = {}
    split_counts: dict[str, int] = {}
    eligible_split_counts: dict[str, int] = {}
    wav_paths = sorted(wav_root.rglob("*.wav"))
    nested_archives = sorted(wav_root.glob("S*.tar.gz"))

    def consume(path_label: str, fileobj: object, size_bytes: int) -> None:
        try:
            with wave.open(fileobj, "rb") as handle:  # type: ignore[arg-type]
                channels = handle.getnchannels()
                sample_rate = handle.getframerate()
                sample_width = handle.getsampwidth()
                frames = handle.getnframes()
        except (EOFError, wave.Error) as exc:
            records.append({"path": path_label, "status": "INVALID_WAV", "error": str(exc)})
            return
        duration = frames / sample_rate if sample_rate else 0.0
        speaker_match = SPEAKER_RE.search(Path(path_label).name)
        speaker_id = speaker_match.group(1) if speaker_match else None
        split = next((part for part in Path(path_label).parts if part.lower() in {"train", "dev", "test"}), None)
        split = split.lower() if split else "UNKNOWN"
        key = f"{sample_rate}Hz/{channels}ch/{sample_width}byte"
        format_counts[key] = format_counts.get(key, 0) + 1
        split_counts[split] = split_counts.get(split, 0) + 1
        eligible = 8.0 <= duration <= 30.0 and channels == 1 and sample_rate == 16_000 and sample_width == 2
        if eligible:
            eligible_split_counts[split] = eligible_split_counts.get(split, 0) + 1
        records.append(
            {
                "path": path_label,
                "utterance_id": Path(path_label).stem,
                "speaker_id": speaker_id,
                "split": split,
                "duration_sec": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width,
                "transcript_present": Path(path_label).stem in transcript_texts if transcript_path.is_file() else None,
                "text_sha256": hashlib.sha256(transcript_texts[Path(path_label).stem].encode("utf-8")).hexdigest().upper() if Path(path_label).stem in transcript_texts else None,
                "audio_size_bytes": size_bytes,
                "eligible_under_frozen_filter": eligible,
            }
        )
        if include_records:
            try:
                current = fileobj.tell()  # type: ignore[attr-defined]
                fileobj.seek(0)  # type: ignore[attr-defined]
                records[-1]["source_audio_sha256"] = _hash_stream(fileobj)
                fileobj.seek(current)  # type: ignore[attr-defined]
            except (AttributeError, OSError):
                records[-1]["source_audio_sha256"] = None

    for path in wav_paths:
        with path.open("rb") as handle:
            consume(path.relative_to(root).as_posix(), handle, path.stat().st_size)
    if not wav_paths:
        for archive in nested_archives:
            with tarfile.open(archive, mode="r:gz") as bundle:
                for member in sorted(bundle.getmembers(), key=lambda item: item.name):
                    if not member.isfile() or not member.name.lower().endswith(".wav"):
                        continue
                    extracted = bundle.extractfile(member)
                    if extracted is None:
                        continue
                    with extracted:
                        consume(f"data_aishell/wav/{member.name}", extracted, member.size)

    valid = [row for row in records if row.get("status") != "INVALID_WAV"]
    eligible_rows = [row for row in valid if row.get("eligible_under_frozen_filter") is True]
    all_speaker_ids = {row["speaker_id"] for row in valid if row.get("speaker_id")}
    eligible_speaker_ids = {row["speaker_id"] for row in eligible_rows if row.get("speaker_id")}
    missing_speaker_metadata = sorted(all_speaker_ids - set(speakers))
    missing_transcripts = sum(1 for row in valid if row.get("transcript_present") is False)

    audio_archive = _first_file(root / "data_aishell.tgz", root.parent / "data_aishell.tgz")
    resource_archive = _first_file(root / "resource_aishell.tgz", root.parent / "resource_aishell.tgz")
    return {
        "schema_version": "topconf.level2.aishell1-feasibility.v1",
        "status": "AUDITED_METADATA_AND_WAV_HEADERS",
        "corpus_id": "AISHELL-1",
        "source_authority": "Beijing Shell Shell Technology Co.,Ltd via OpenSLR SLR33",
        "official_page": OFFICIAL_PAGE,
        "license": "Apache License 2.0",
        "language": "Mandarin Chinese",
        "official_audio_archive": {
            "url": OFFICIAL_AUDIO_URL,
            "declared_bytes": EXPECTED_AUDIO_BYTES,
            "observed_archive_sha256": _sha256(audio_archive) if audio_archive else None,
            "archive_present": audio_archive is not None,
        },
        "official_resource_archive": {
            "url": OFFICIAL_RESOURCE_URL,
            "sha256": _sha256(resource_archive) if resource_archive else None,
        },
        "speaker_metadata": {
            "path": speaker_path.relative_to(root).as_posix(),
            "rows": len(speakers),
            "unique_ids": len(speakers),
            "malformed_rows": len(malformed_speaker_rows),
            "gender_values": sorted(set(speakers.values())),
            "missing_for_audio_speakers": missing_speaker_metadata,
        },
        "transcription": {
            "path": transcript_path.relative_to(root).as_posix(),
            "present": transcript_path.is_file(),
            "unique_ids": len(transcript_texts),
            "malformed_rows": malformed_transcript_rows,
            "audio_rows_missing_transcript": missing_transcripts,
        },
        "frozen_filter": {
            "duration_sec_inclusive": [8, 30],
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_width_bytes": 2,
            "selection_is_model_free": True,
        },
        "counts": {
            "wav_files": len(records),
            "valid_wav_files": len(valid),
            "invalid_wav_files": len(records) - len(valid),
            "all_speakers_from_audio": len(all_speaker_ids),
            "eligible_wav_files": len(eligible_rows),
            "eligible_speakers": len(eligible_speaker_ids),
            "split_wav_files": split_counts,
            "split_eligible_wav_files": eligible_split_counts,
            "format_counts": format_counts,
        },
        "records": records if include_records else [],
        "historical_usage": "NONE_FOUND_IN_REPOSITORY_SCAN; requires final exclusion-universe review",
        "freshness_eligibility": "PENDING_COMPLETE_HISTORICAL_EXCLUSION_AND_CROSS_CORPUS_IDENTITY_REVIEW",
        "model_inference_runs": 0,
        "scientific_outcomes_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="extracted AISHELL-1 root containing data_aishell and resource_aishell")
    parser.add_argument("output", type=Path)
    parser.add_argument("--include-records", action="store_true", help="retain every audited WAV header row in the output")
    args = parser.parse_args()
    result = audit(args.root, include_records=args.include_records)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
