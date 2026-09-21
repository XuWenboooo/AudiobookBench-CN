"""Build the outcome-blind W7 metadata case manifest.

This script reads only official metadata and the already recorded W6
acceptance evidence. It never opens audio, runs a model, computes a metric, or
materializes generated condition assets.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


CONDITIONS = {
    "clean": "topconf.w7.transform.clean.v1",
    "mechanism_shift": "topconf.w7.transform.mechanism_shift.v1",
    "codec": "topconf.w7.transform.codec_opus_64k.v1",
    "resampling": "topconf.w7.resampling.16k_8k_16k.scipy-resample-poly.v1",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def planned_case_id(distribution: str, version: str, split: str, source_id: str, gt_id: str) -> str:
    payload = "|".join((distribution, version, split, source_id, gt_id, *CONDITIONS))
    return "w7plan_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def partialedit_records(csv_path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            source_id = row[0]
            if not source_id.startswith("E1/"):
                continue
            numeric = [float(value) for value in row[1:]]
            if len(numeric) < 3 or len(numeric) % 2 == 0:
                raise ValueError(f"unexpected PartialEdit row shape: {row!r}")
            duration = numeric[-1]
            intervals = [[numeric[index], numeric[index + 1]] for index in range(0, len(numeric) - 1, 2)]
            gt_id = f"partial_edit_e1_gt::{source_id}"
            records.append(
                {
                    "case_id": planned_case_id("PartialEdit", "1.1", "E1", source_id, gt_id),
                    "distribution_id": "PartialEdit",
                    "distribution_version": "1.1",
                    "split_id": "E1",
                    "source_audio_id": source_id,
                    "source_audio_sha256": None,
                    "gt_id": gt_id,
                    "gt_version": "PartialEdit_E1E2.csv_v1.1",
                    "gt": {"representation": "edited_region_seconds", "intervals_sec": intervals, "duration_sec": duration},
                    "condition_ids": list(CONDITIONS),
                    "transform_ids": CONDITIONS,
                    "audio_artifact_sha256": {condition: None for condition in CONDITIONS},
                }
            )
    return records


def llama_records(label_path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with label_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            source_id = parts[0]
            duration = float(parts[1])
            gt_id = f"llama_partialspoof_gt::R01TTS.0.b::{source_id}"
            segments = parts[3:]
            records.append(
                {
                    "case_id": planned_case_id("LlamaPartialSpoof", "1.0.b", "R01TTS.0.b", source_id, gt_id),
                    "distribution_id": "LlamaPartialSpoof",
                    "distribution_version": "1.0.b",
                    "split_id": "R01TTS.0.b",
                    "source_audio_id": source_id,
                    "source_audio_sha256": None,
                    "gt_id": gt_id,
                    "gt_version": "label_R01TTS.0.b.txt_official",
                    "gt": {"representation": "ordered_start_end_segments", "duration_sec": duration, "segment_count": len(segments), "label_source_id": "label_R01TTS.0.b.txt"},
                    "condition_ids": list(CONDITIONS),
                    "transform_ids": CONDITIONS,
                    "audio_artifact_sha256": {condition: None for condition in CONDITIONS},
                }
            )
    return records


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    external_root = Path(os.environ["TOPCONF_EXTERNAL_ROOT"])
    llama_cache = Path(os.environ["TOPCONF_W7_LLAMACACHE"])
    partial_csv = external_root / "PartialEdit_v1.1" / "PartialEdit_E1E2.csv"
    records = partialedit_records(partial_csv) + llama_records(llama_cache / "label_R01TTS.0.b.txt")
    by_distribution: dict[str, int] = {}
    for record in records:
        by_distribution[record["distribution_id"]] = by_distribution.get(record["distribution_id"], 0) + 1

    payload = {
        "schema_version": "topconf.w7.final_case_manifest.metadata_only.v1",
        "manifest_status": "FROZEN_METADATA_ONLY_NO_PREDICTIONS",
        "audit_date": "2026-09-21",
        "purpose": "Freeze accepted source/GT identities and four W7 conditions before any inference; final audio artifacts are not generated here.",
        "w7_executed": False,
        "scientific_inferences": 0,
        "metrics": "NOT_MEASURED",
        "level2_outcomes_accessed": False,
        "hash_status": {
            "source_audio_sha256": "PENDING_EXACT_AUDIO_HASH_BINDING",
            "audio_artifact_sha256": "PENDING_CONDITION_MATERIALIZATION",
            "gt_source_sha256": "RECORDED_AT_DISTRIBUTION_POOL_LEVEL",
        },
        "conditions": list(CONDITIONS),
        "condition_definitions": {
            "clean": "paired reference; no additional transformation",
            "mechanism_shift": "fixed inherited mechanism contract; no outcome-guided search",
            "codec": "Opus 64 kbps at 16 kHz; fixed transform identity",
            "resampling": "16 kHz -> 8 kHz -> 16 kHz; fixed scipy resample_poly identity",
        },
        "distribution_pools": [
            {
                "distribution_id": "PartialEdit",
                "version": "1.1",
                "split": "E1",
                "accepted_case_count": 42471,
                "metadata_source": "external_data/topconf_phase3_cache/PartialEdit_v1.1/PartialEdit_E1E2.csv",
                "metadata_sha256": sha256_file(partial_csv),
                "audio_archive_sha256": "f4bb1a632eed8ddc66bb9285de8b4bc07192d0539385efe9afc9ea04aef3ddcb",
                "audio_hash_status": "EXACT_POOL_AUDIO_HASHES_NOT_REPEATED_IN_RECONCILIATION",
            },
            {
                "distribution_id": "LlamaPartialSpoof",
                "version": "1.0.b",
                "split": "R01TTS.0.b",
                "accepted_case_count": 64388,
                "metadata_source": "official label_R01TTS.0.b.txt in external recovery cache",
                "metadata_sha256": sha256_file(llama_cache / "label_R01TTS.0.b.txt"),
                "archive_md5": "a4de860a845816fa65785dddd7849700",
                "audio_hash_status": "EXACT_ARCHIVE_MEMBER_HASHES_NOT_MATERIALIZED_IN_RECONCILIATION",
            },
        ],
        "counts": {"source_gt_cases": len(records), "by_distribution": by_distribution, "condition_rows_planned": len(records) * len(CONDITIONS)},
        "records": records,
        "blockers_before_first_inference": [
            "exact per-audio source hashes must be bound to the immutable model-input assets",
            "condition-specific audio artifacts must be materialized and hashed under the frozen transform/mechanism contracts",
            "human authorization record must be changed from NO by an authorized human",
        ],
    }
    out = repo / "research_assurance" / "topconf" / "W7_FINAL_CASE_MANIFEST_V1.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "source_gt_cases": len(records), "condition_rows_planned": len(records) * len(CONDITIONS), "status": payload["manifest_status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
