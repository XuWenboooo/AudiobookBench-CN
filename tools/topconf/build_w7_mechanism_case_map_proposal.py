"""Build an outcome-blind, fully enumerated mechanism-freeze proposal map."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
SOURCE = ROOT / "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz"
DETAIL = ROOT / "W7_MECHANISM_CASE_MAP_PROPOSAL_V1.jsonl.gz"
SUMMARY = ROOT / "W7_MECHANISM_CASE_MAP_PROPOSAL_V1.json"
UNFROZEN_FIELDS = (
    "mechanism_family",
    "implementation",
    "version",
    "parameter_set_id",
    "reference_rule",
    "target_span_rule",
    "sample_rate",
    "codec_path",
    "seed_policy",
    "quality_gate_policy",
    "parameters",
)
EVIDENCE_SOURCES = (
    "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz",
    "W7_PILOT_PROTOCOL_V1_1.md",
    "w7_preparation/MECHANISM_CONFIG_CONTRACT_V1.md",
    "w7_preparation/MECHANISM_CONFIG_SCHEMA_V1.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical(record: dict[str, object]) -> bytes:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def proposal_row(record: dict[str, object]) -> dict[str, object]:
    return {
        "case_id": record["case_id"],
        "distribution_id": record["distribution_id"],
        "distribution_version": record["distribution_version"],
        "split_id": record["split_id"],
        "source_id": record["source_audio_id"],
        "source_audio_hash": record["source_audio_hash"],
        "gt_id": record["gt_id"],
        "gt_hash": record["gt_hash"],
        "source_manipulation_family": record["manipulation_family"],
        "source_manipulation_mechanism": record["manipulation_mechanism"],
        "condition_id": "mechanism_shift",
        "mechanism_family": "NOT_FROZEN",
        "parameter_fields": {field: "HUMAN_DECISION_REQUIRED" for field in UNFROZEN_FIELDS},
        "evidence_sources": list(EVIDENCE_SOURCES),
        "parameter_status": "HUMAN_DECISION_REQUIRED",
        "required_configuration_fields": list(UNFROZEN_FIELDS),
        "configuration_hash": "NOT_FROZEN",
    }


def main() -> None:
    count = 0
    distributions: dict[str, int] = {}
    with DETAIL.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as output:
            with gzip.open(SOURCE, "rt", encoding="utf-8") as source:
                for line in source:
                    record = json.loads(line)
                    if record["condition_id"] != "mechanism_shift":
                        continue
                    row = proposal_row(record)
                    output.write(canonical(row))
                    count += 1
                    distributions[row["distribution_id"]] = distributions.get(row["distribution_id"], 0) + 1
    summary = {
        "schema_version": "topconf.w7.mechanism_case_map_proposal.v1",
        "status": "PENDING_HUMAN_MECHANISM_FREEZE",
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "source_case_manifest": "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz",
        "source_case_manifest_sha256": sha256(SOURCE),
        "condition_id": "mechanism_shift",
        "records": count,
        "distribution_counts": distributions,
        "detailed_records": DETAIL.name,
        "detailed_records_sha256": sha256(DETAIL),
        "detailed_records_format": "deterministic JSON Lines compressed with gzip mtime=0",
        "record_fields": [
            "case_id", "distribution_id", "distribution_version", "split_id", "source_id",
            "source_audio_hash", "gt_id", "gt_hash", "source_manipulation_family",
            "source_manipulation_mechanism", "condition_id", "mechanism_family",
            "parameter_fields", "evidence_sources", "parameter_status",
            "required_configuration_fields", "configuration_hash",
        ],
        "unfrozen_configuration_fields": list(UNFROZEN_FIELDS),
        "semantic_guard": "The source manipulation label is copied as provenance, not interpreted as a selected W7 mechanism family.",
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "records": count, "detail_sha256": summary["detailed_records_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
