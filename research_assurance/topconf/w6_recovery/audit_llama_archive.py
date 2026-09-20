"""Audit official LlamaPartialSpoof .b archive against its temporal labels."""
from __future__ import annotations

import argparse
import json
import tarfile
import wave
from pathlib import Path


def read_labels(path: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        fields = raw.split()
        if len(fields) < 4:
            raise ValueError(f"label line {line_no}: too few fields")
        case_id, duration = fields[:2]
        if case_id in result:
            raise ValueError(f"duplicate label id: {case_id}")
        result[case_id] = float(duration)
    return result


def audit(archive: Path, labels_path: Path) -> dict[str, object]:
    labels = read_labels(labels_path)
    audio: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    payload_bytes = 0
    with tarfile.open(archive, "r:") as tf:
        for member in tf:
            if member.isdir():
                continue
            payload_bytes += member.size
            if not member.name.lower().endswith(".wav"):
                errors.append(f"non-wav member: {member.name}")
                continue
            case_id = Path(member.name).stem
            if case_id in audio:
                errors.append(f"duplicate audio id: {case_id}")
                continue
            extracted = tf.extractfile(member)
            if extracted is None:
                errors.append(f"unreadable member: {member.name}")
                continue
            try:
                with wave.open(extracted, "rb") as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    channels = wav.getnchannels()
                    sample_width = wav.getsampwidth()
                    raw_frames = wav.readframes(frames)
                    if len(raw_frames) != frames * channels * sample_width:
                        errors.append(f"short audio payload: {member.name}")
                    actual_duration = frames / rate if rate else -1.0
            except Exception as exc:  # pragma: no cover - exercised by corrupt archives
                errors.append(f"wav decode failure {member.name}: {exc!r}")
                continue
            audio[case_id] = {
                "member": member.name,
                "bytes": member.size,
                "frames": frames,
                "sample_rate": rate,
                "channels": channels,
                "sample_width": sample_width,
                "duration": actual_duration,
            }
            if rate != 16000 or channels != 1:
                errors.append(f"unexpected format {member.name}: {rate}Hz/{channels}ch")
            if case_id not in labels:
                errors.append(f"audio without GT: {case_id}")
            elif abs(actual_duration - labels[case_id]) > 0.011:
                errors.append(
                    f"duration mismatch {case_id}: audio={actual_duration:.6f} label={labels[case_id]:.4f}"
                )
    missing_audio = sorted(set(labels) - set(audio))
    extra_audio = sorted(set(audio) - set(labels))
    errors.extend(f"missing audio: {item}" for item in missing_audio[:20])
    errors.extend(f"extra audio: {item}" for item in extra_audio[:20])
    return {
        "archive": str(archive),
        "label_file": str(labels_path),
        "archive_format": "tar_uncompressed",
        "archive_payload_bytes": payload_bytes,
        "gt_ids": len(labels),
        "audio_ids": len(audio),
        "missing_audio_count": len(missing_audio),
        "extra_audio_count": len(extra_audio),
        "audio_format_counts": {
            "16k_mono": sum(1 for item in audio.values() if item["sample_rate"] == 16000 and item["channels"] == 1),
        },
        "audio_gt_identity": "PASS" if not missing_audio and not extra_audio else "FAIL",
        "audio_decode_and_duration": "PASS" if not errors else "FAIL",
        "errors": errors[:50],
        "error_count": len(errors),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("labels", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.archive, args.labels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
