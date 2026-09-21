"""Rebuild the pre-inference W7 case manifest with immutable identities.

This script hashes source assets and official GT only. It does not materialize
codec/resampling/mechanism audio and never invokes a model.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import tarfile
from pathlib import Path


CONDITIONS = {
    "clean": "topconf.w7.transform.clean.v1",
    "mechanism_shift": "topconf.w7.transform.mechanism_shift.v1",
    "codec": "topconf.w7.transform.codec_opus_64k.v1",
    "resampling": "topconf.w7.resampling.16k_8k_16k.scipy-resample-poly.v1",
}
ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = Path(os.environ["TOPCONF_EXTERNAL_ROOT"])
LLAMA = Path(os.environ["TOPCONF_W7_LLAMACACHE"])


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_stream(handle) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def parse_partialedit(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in csv.reader(path.open("r", encoding="utf-8", newline="")):
        if not row or not row[0].startswith("E1/"):
            continue
        values = [float(value) for value in row[1:]]
        if len(values) < 3 or len(values) % 2 == 0:
            raise ValueError(f"unexpected PartialEdit row: {row!r}")
        duration = values[-1]
        intervals = [[values[i], values[i + 1]] for i in range(0, len(values) - 1, 2)]
        rows.append({"source_id": row[0], "duration": duration, "intervals": intervals, "gt_version": "PartialEdit_E1E2.csv_v1.1"})
    return rows


def parse_llama(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        fields = raw.split()
        source_id, duration, utterance_label, *segments = fields
        parsed = []
        for segment in segments:
            start, end, label = segment.split("-")
            parsed.append([float(start), float(end), label])
        rows.append({"source_id": source_id, "duration": float(duration), "utterance_label": utterance_label, "segments": parsed, "gt_version": "label_R01TTS.0.b.txt_official"})
    return rows


def official_llama_hashes(archive: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with tarfile.open(archive, "r:") as tf:
        for member in tf:
            if member.isdir():
                continue
            if not member.name.lower().endswith(".wav"):
                raise ValueError(f"unexpected non-WAV member: {member.name}")
            case_id = Path(member.name).stem
            if case_id in result:
                raise ValueError(f"duplicate Llama audio ID: {case_id}")
            extracted = tf.extractfile(member)
            if extracted is None:
                raise ValueError(f"cannot read Llama member: {member.name}")
            result[case_id] = sha256_stream(extracted)
    return result


def base_record(distribution: str, version: str, split: str, row: dict[str, object], source_hash: str, gt_hash: str, condition: str, transform_config_hash: str) -> dict[str, object]:
    source_id = str(row["source_id"])
    gt_id = f"partial_edit_e1_gt::{source_id}" if distribution == "PartialEdit" else f"llama_partialspoof_gt::{split}::{source_id}"
    manipulation_family = "partial_edit" if distribution == "PartialEdit" else "partial_spoof"
    manipulation_mechanism = "official_partial_edit_e1" if distribution == "PartialEdit" else "official_llamapartialspoof_r01tts_0_b"
    transform_id = CONDITIONS[condition]
    derivation = {
        "source_audio_sha256": source_hash,
        "transform_id": transform_id,
        "transform_config_sha256": transform_config_hash,
        "condition_id": condition,
    }
    derivation_hash = hashlib.sha256(canonical(derivation)).hexdigest()
    artifact_materialized = condition == "clean"
    artifact_id = f"source::{source_id}" if artifact_materialized else f"derivation::{derivation_hash}"
    artifact_hash = source_hash if artifact_materialized else derivation_hash
    identity = {
        "distribution_id": distribution,
        "distribution_version": version,
        "split_id": split,
        "source_audio_id": source_id,
        "source_audio_hash": source_hash,
        "manipulation_id": f"{distribution.lower()}::{source_id}",
        "manipulation_family": manipulation_family,
        "manipulation_mechanism": manipulation_mechanism,
        "condition_id": condition,
        "condition_type": condition,
        "transform_id": transform_id,
        "transform_version": transform_id,
        "audio_artifact_id": artifact_id,
        "audio_artifact_hash": artifact_hash,
        "gt_id": gt_id,
        "gt_version": str(row["gt_version"]),
        "gt_hash": gt_hash,
        "whether_definition_id": "W7_WHETHER_A_B_FROZEN_V1",
        "localizer_id": "W7_LOCALIZER_SET_CFPRF_MULTIRESo_SAL_BAM_V1",
        "model_checkpoint_id": "W7_LOCALIZER_CHECKPOINT_SET_FROZEN_V1",
        "adapter_version": "W7_GENERIC_TEMPORAL_GT_ADAPTER_V1",
        "source_speaker_id": None,
        "source_utterance_id": source_id,
    }
    case_identity_hash = hashlib.sha256(canonical(identity)).hexdigest()
    identity["case_identity_hash"] = case_identity_hash
    identity["case_id"] = "w7case_" + case_identity_hash[:32]
    return identity


def main() -> None:
    external = EXTERNAL / "topconf_phase3_cache"
    partial_csv = external / "PartialEdit_v1.1" / "PartialEdit_E1E2.csv"
    partial_root = external / "PartialEdit_v1.1" / "materialized"
    llama_labels = LLAMA / "label_R01TTS.0.b.txt"
    llama_archive = LLAMA / "R01TTS.0.b.tgz"
    transform_hashes = {
        "clean": hashlib.sha256(b"topconf.w7.transform.clean.v1\n").hexdigest(),
        "mechanism_shift": sha256_file(ROOT / "research_assurance/topconf/w7_preparation/MECHANISM_CONFIG_SCHEMA_V1.json"),
        "codec": hashlib.sha256(b"topconf.w7.transform.codec_opus_64k.v1\n").hexdigest(),
        "resampling": sha256_file(ROOT / "research_assurance/topconf/w7_preparation/RESAMPLING_TRANSFORM_SCHEMA_V1.json"),
    }
    partial_rows = parse_partialedit(partial_csv)
    llama_rows = parse_llama(llama_labels)
    partial_hashes = {}
    for row in partial_rows:
        source_id = str(row["source_id"])
        path = partial_root / Path(source_id)
        if not path.exists():
            raise FileNotFoundError(path)
        partial_hashes[source_id] = sha256_file(path)
    llama_hashes = official_llama_hashes(llama_archive)
    if set(llama_hashes) != {str(row["source_id"]) for row in llama_rows}:
        raise ValueError("Llama audio/label identity mismatch")
    records = []
    logical_keys = set()
    for distribution, version, split, rows, hashes in [
        ("PartialEdit", "1.1", "E1", partial_rows, partial_hashes),
        ("LlamaPartialSpoof", "1.0.b", "R01TTS.0.b", llama_rows, llama_hashes),
    ]:
        for row in rows:
            source_id = str(row["source_id"])
            gt_id = f"partial_edit_e1_gt::{source_id}" if distribution == "PartialEdit" else f"llama_partialspoof_gt::{split}::{source_id}"
            gt_payload = {key: value for key, value in row.items() if key != "source_id"}
            gt_hash = hashlib.sha256(canonical(gt_payload)).hexdigest()
            logical_keys.add((distribution, version, split, source_id, gt_id))
            for condition in CONDITIONS:
                records.append(base_record(distribution, version, split, row, hashes[source_id], gt_hash, condition, transform_hashes[condition]))
    records.sort(key=lambda item: item["case_id"])
    old = json.loads((ROOT / "research_assurance/topconf/W7_FINAL_CASE_MANIFEST_V1.json").read_text(encoding="utf-8"))
    old_keys = {(r["distribution_id"], r["distribution_version"], r["split_id"], r["source_audio_id"], r["gt_id"]) for r in old["records"]}
    if old_keys != logical_keys:
        raise ValueError(f"population mismatch: old={len(old_keys)} new={len(logical_keys)}")
    out = ROOT / "research_assurance/topconf/W7_FINAL_CASE_MANIFEST_V2.jsonl.gz"
    with out.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz:
            for record in records:
                gz.write(canonical(record))
    summary = {
        "schema_version": "topconf.w7.case_identity.v1.jsonl.gz",
        "manifest_status": "FROZEN_PRE_INFERENCE_NO_PREDICTIONS",
        "records": len(records),
        "logical_cases": len(logical_keys),
        "conditions": list(CONDITIONS),
        "distribution_counts": {"PartialEdit": len(partial_rows), "LlamaPartialSpoof": len(llama_rows)},
        "old_case_count": len(old_keys),
        "new_case_count": len(logical_keys),
        "condition_rows": len(records),
        "source_audio_hash_coverage": len(logical_keys),
        "materialized_asset_hash_coverage": len(logical_keys),
        "derivation_identity_coverage": len(records) - len(logical_keys),
        "not_yet_materialized_condition_rows": len(records) - len(logical_keys),
        "artifact_hash_semantics": "clean rows use materialized source bytes; non-clean rows use DERIVATION_IDENTITY_HASH and have no materialized transformed bytes",
        "population_semantic_equivalence": "PASS",
        "w7_executed": False,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "metrics": "NOT_MEASURED",
        "manifest_sha256": sha256_file(out),
    }
    summary_path = ROOT / "research_assurance/topconf/W7_FINAL_CASE_MANIFEST_V2.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
