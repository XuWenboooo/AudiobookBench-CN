"""Audit source capacity for the frozen Level-2 plan without model execution."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.materialization import FROZEN_LEVEL2_PLAN  # noqa: E402


def audit(dataset_root: Path) -> dict[str, object]:
    raw_root = dataset_root / "raw"
    rows: list[dict[str, object]] = []
    for split in ("train", "test"):
        for path in sorted((raw_root / split / "wav").glob("*/*.wav")):
            with wave.open(str(path), "rb") as audio:
                rate = audio.getframerate()
                channels = audio.getnchannels()
                width = audio.getsampwidth()
                duration = audio.getnframes() / rate
            rows.append(
                {
                    "split": split,
                    "speaker_id": path.parent.name,
                    "utterance_id": path.stem,
                    "duration_sec": duration,
                    "sample_rate_hz": rate,
                    "channels": channels,
                    "sample_width_bytes": width,
                }
            )
    eligible = [
        row
        for row in rows
        if float(FROZEN_LEVEL2_PLAN["target_duration_sec"][0])
        <= float(row["duration_sec"])
        <= float(FROZEN_LEVEL2_PLAN["target_duration_sec"][1])
    ]
    speakers_by_split = {
        split: {str(row["speaker_id"]) for row in rows if row["split"] == split}
        for split in ("train", "test")
    }
    eligible_speakers = {str(row["speaker_id"]) for row in eligible}
    return {
        "status": "BLOCKED_FROZEN_CAPACITY",
        "dataset_root": str(dataset_root),
        "frozen_plan": FROZEN_LEVEL2_PLAN,
        "raw_wav_files": len(rows),
        "raw_speakers": len({str(row["speaker_id"]) for row in rows}),
        "eligible_8_30_wav_files": len(eligible),
        "eligible_8_30_speakers": len(eligible_speakers),
        "duration_min_sec": min(float(row["duration_sec"]) for row in rows),
        "duration_max_sec": max(float(row["duration_sec"]) for row in rows),
        "format_counts": {
            "sample_rate_hz": dict(Counter(row["sample_rate_hz"] for row in rows)),
            "channels": dict(Counter(row["channels"] for row in rows)),
            "sample_width_bytes": dict(Counter(row["sample_width_bytes"] for row in rows)),
        },
        "split_counts": {
            split: {
                "wav_files": sum(row["split"] == split for row in rows),
                "speakers": len(speakers_by_split[split]),
                "eligible_8_30_wav_files": sum(row["split"] == split for row in eligible),
            }
            for split in ("train", "test")
        },
        "speaker_partition": {
            "train_only": len(speakers_by_split["train"] - speakers_by_split["test"]),
            "test_only": len(speakers_by_split["test"] - speakers_by_split["train"]),
            "shared": len(speakers_by_split["train"] & speakers_by_split["test"]),
        },
        "capacity_gates": {
            "one_independent_source_corpus": False,
            "eligible_speakers_at_least_frozen": len(eligible_speakers) >= int(FROZEN_LEVEL2_PLAN["speakers"]),
            "eligible_sources_at_least_frozen": len(eligible) >= int(FROZEN_LEVEL2_PLAN["primary_sources"]),
            "train_test_speaker_disjoint": not bool(speakers_by_split["train"] & speakers_by_split["test"]),
        },
        "model_inference_runs": 0,
        "scientific_outcomes_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.dataset_root), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
