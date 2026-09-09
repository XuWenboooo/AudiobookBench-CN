"""Fail-closed validator for additive Day 9 A2 sidecars."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from audiobookbench.security.a2_readiness import validate_a2_sidecar_row


REQUIRED = {
    "protocol_version", "paired_case_id", "split", "target_source_sample_id",
    "target_speaker", "reference_sample_id", "reference_audio_path",
    "reference_text_exact", "generator_checkpoint_revision",
    "generator_checkpoint_sha256", "manipulated_audio_path", "sample_rate",
    "generation_attempt_count", "generation_status",
    "qa_flags", "official_smoke", "smoke_only",
}


def _text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def validate_row(row: dict[str, str], expected: dict[str, dict[str, str]], *, official_smoke: bool) -> None:
    missing = sorted(k for k in REQUIRED if not row.get(k, ""))
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    if row["protocol_version"] not in {"WEEK3_STAGE_A_F5", "week2a-a2-v1.1-corrected"}:
        raise ValueError("protocol version mismatch")
    if "generation_failure_reason" not in row or row["generation_status"] != "success" or row["generation_failure_reason"]:
        raise ValueError("row is not a successful generation")
    if row["official_smoke"] != str(official_smoke) or row["smoke_only"] != "False":
        raise ValueError("formal-generation flags invalid")
    if row["paired_case_id"] not in expected:
        raise ValueError("unplanned paircase")
    plan = expected[row["paired_case_id"]]
    for key in ("split", "target_source_sample_id", "target_speaker", "tts_input_text", "source_text_exact"):
        if row.get(key) != plan.get(key):
            raise ValueError(f"frozen plan mismatch: {key}")
    if row["protocol_version"] == "WEEK3_STAGE_A_F5":
        for key in ("source_audio_path", "clean_sequence_audio_path"):
            if not row.get(key) or row.get(key) != plan.get(key):
                raise ValueError(f"frozen lineage mismatch: {key}")
    if row["tts_input_text"] != row["source_text_exact"]:
        raise ValueError("exact text mismatch")
    if row["source_text_sha256"].upper() != _text_hash(row["source_text_exact"]):
        raise ValueError("source text hash mismatch")
    if row["tts_input_text_sha256"].upper() != _text_hash(row["tts_input_text"]):
        raise ValueError("tts text hash mismatch")
    if int(row["sample_rate"]) != 16000:
        raise ValueError("final sample rate is not 16 kHz")
    if row.get("reference_text_sha256") and row["reference_text_sha256"].upper() != _text_hash(row["reference_text_exact"]):
        raise ValueError("reference text hash mismatch")
    for path_key, hash_key in (("raw_waveform_path", "raw_waveform_sha256"), ("standardized_waveform_path", "standardized_waveform_sha256")):
        if row.get(path_key) and row.get(hash_key) and Path(row[path_key]).is_file() and sha256_file(Path(row[path_key])) != row[hash_key].upper():
            raise ValueError(f"{path_key} hash mismatch")
    if int(row["generation_attempt_count"]) not in (1, 2):
        raise ValueError("unexpected retry count")
    json.loads(row["qa_flags"])
    validate_a2_sidecar_row(row)


def run(sidecar_path: Path, planned_path: Path, *, expected_count: int = 3,
        official_smoke: bool = True) -> dict[str, Any]:
    rows = list(csv.DictReader(sidecar_path.open(encoding="utf-8", newline="")))
    plans = {r["paired_case_id"]: r for r in csv.DictReader(planned_path.open(encoding="utf-8", newline=""))}
    errors: list[dict[str, str]] = []
    for row in rows:
        try:
            validate_row(row, plans, official_smoke=official_smoke)
        except Exception as exc:
            errors.append({"paired_case_id": row.get("paired_case_id", ""), "error": str(exc)})
    return {"status": "PASS" if not errors and len(rows) == expected_count else "FAIL", "passed": len(rows) - len(errors),
            "failed": len(errors), "errors": errors, "case_ids": [r.get("paired_case_id") for r in rows],
            "tool": "a2_sidecar_validator"}
