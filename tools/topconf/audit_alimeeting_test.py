"""Audit AliMeeting Test near-field recordings and TextGrid intervals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import wave


NAME_RE = re.compile(r'^\s*name\s*=\s*"([^"]+)"')
XMIN_RE = re.compile(r"^\s*xmin\s*=\s*([0-9.]+)")
XMAX_RE = re.compile(r"^\s*xmax\s*=\s*([0-9.]+)")
TEXT_RE = re.compile(r'^\s*text\s*=\s*"(.*)"')


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def parse_textgrid(path: Path) -> list[dict[str, object]]:
    intervals: list[dict[str, object]] = []
    tier: str | None = None
    xmin: float | None = None
    xmax: float | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = NAME_RE.match(line)
        if match:
            tier = match.group(1)
            continue
        match = XMIN_RE.match(line)
        if match:
            xmin = float(match.group(1))
            continue
        match = XMAX_RE.match(line)
        if match:
            xmax = float(match.group(1))
            continue
        match = TEXT_RE.match(line)
        if match and tier is not None and xmin is not None and xmax is not None:
            text = match.group(1).replace('\\"', '"').strip()
            intervals.append({
                "tier": tier,
                "start_sec": xmin,
                "end_sec": xmax,
                "duration_sec": xmax - xmin,
                "text_sha256": sha256_text(text) if text else None,
                "text_present": bool(text),
            })
            xmin = None
            xmax = None
    return intervals


def audit(near_root: Path, textgrid_root: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    format_counts: dict[str, int] = {}
    speakers: set[str] = set()
    meetings: set[str] = set()
    for audio_path in sorted(near_root.glob("*.wav")):
        fields = audio_path.stem.split("_")
        if len(fields) < 4 or fields[-2] != "N":
            continue
        meeting_id = "_".join(fields[:2])
        speaker_id = fields[-1]
        textgrid_path = textgrid_root / f"{meeting_id}.TextGrid"
        if not textgrid_path.is_file():
            raise FileNotFoundError(textgrid_path)
        with wave.open(str(audio_path), "rb") as handle:
            channels = handle.getnchannels()
            sample_rate = handle.getframerate()
            sample_width = handle.getsampwidth()
            frames = handle.getnframes()
        format_key = f"{sample_rate}Hz/{channels}ch/{sample_width}byte"
        format_counts[format_key] = format_counts.get(format_key, 0) + 1
        speakers.add(speaker_id)
        meetings.add(meeting_id)
        all_intervals = [item for item in parse_textgrid(textgrid_path) if item["tier"] == f"N_{speaker_id}"]
        for index, item in enumerate(all_intervals, 1):
            eligible = (
                bool(item["text_present"])
                and 8.0 <= float(item["duration_sec"]) <= 30.0
                and sample_rate == 16_000
                and channels == 1
                and sample_width == 2
            )
            rows.append({
                "meeting_id": meeting_id,
                "speaker_id": speaker_id,
                "audio_path": str(audio_path.resolve()),
                "textgrid_path": str(textgrid_path.resolve()),
                "interval_index": index,
                **item,
                "sample_rate_hz": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width,
                "audio_duration_sec": frames / sample_rate if sample_rate else 0.0,
                "eligible_under_frozen_filter": eligible,
            })
    eligible = [row for row in rows if row["eligible_under_frozen_filter"] is True]
    by_speaker: dict[str, int] = {}
    for row in eligible:
        speaker = str(row["speaker_id"])
        by_speaker[speaker] = by_speaker.get(speaker, 0) + 1
    return {
        "schema_version": "topconf.level2.alimeeting-feasibility.v1",
        "status": "AUDITED_NEAR_FIELD_HEADERS_AND_TEXTGRID_INTERVALS",
        "corpus_id": "ALIMEETING_SLR119",
        "corpus_name": "AliMeeting Mandarin Multi-channel Multi-party Meeting Speech Corpus",
        "source_authority": "Alibaba Group via OpenSLR SLR119",
        "official_page": "https://www.openslr.org/119/",
        "license": "CC BY-SA 4.0",
        "language": "Mandarin Chinese",
        "frozen_filter": {
            "duration_sec_inclusive": [8, 30],
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_width_bytes": 2,
            "requires_nonempty_textgrid_interval": True,
            "selection_is_model_free": True,
        },
        "counts": {
            "near_wav_files": len({str(row["audio_path"]) for row in rows}),
            "speakers": len(speakers),
            "meetings": len(meetings),
            "textgrid_intervals": len(rows),
            "eligible_intervals": len(eligible),
            "eligible_speakers": len(by_speaker),
            "eligible_intervals_by_speaker": dict(sorted(by_speaker.items())),
            "format_counts": dict(sorted(format_counts.items())),
        },
        "records": rows,
        "model_inference_runs": 0,
        "scientific_outcomes_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--near-root", type=Path, required=True)
    parser.add_argument("--textgrid-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.near_root, args.textgrid_root)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
