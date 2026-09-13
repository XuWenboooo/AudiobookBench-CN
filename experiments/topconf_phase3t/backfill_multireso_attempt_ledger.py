"""Append-only structural repair for missing audio-load attempt entries.

This utility never changes raw output or the terminal case ledger.  It only
backfills the attempt-start rows that the worker omitted before recording an
audio-load failure, and writes a hash-based repair report beside the frozen
namespace.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = ROOT / "results" / "topconf_phase3t" / "multireso_worker_02"
RAW = NAMESPACE / "multireso_raw_v1.jsonl"
LEDGER = NAMESPACE / "multireso_case_ledger_v1.jsonl"
ATTEMPTS = NAMESPACE / "multireso_attempts_v1.jsonl"
REPORT = NAMESPACE / "MULTIRESO_ATTEMPT_LEDGER_BACKFILL_V1.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("refusing to mutate the frozen namespace without --apply")
    if REPORT.exists():
        raise SystemExit(f"repair report already exists: {REPORT}")

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPTS)
    attempt_keys = {(row.get("case_id"), row.get("attempt")) for row in attempts}
    terminal_by_case = {row["case_id"]: row for row in ledger}
    additions: list[dict[str, Any]] = []
    for row in iter_jsonl(RAW):
        key = (row.get("case_id"), row.get("attempt"))
        if key in attempt_keys:
            continue
        terminal = terminal_by_case.get(row["case_id"])
        if terminal is None or terminal.get("terminal_status") != "FAILED":
            raise RuntimeError(f"unexpected missing attempt for {row['case_id']}")
        if row.get("status") != "AUDIO_LOAD_FAILURE" or row.get("attempt") != 1:
            raise RuntimeError(f"repair scope violation for {row['case_id']}")
        additions.append(
            {
                "authorization_id": row["authorization_id"],
                "case_id": row["case_id"],
                "case_index": row["case_index"],
                "attempt": row["attempt"],
                "retry_count": row.get("retry_count", 0),
                "status": "STARTED",
                "backfilled": True,
                "backfill_reason": "worker omitted attempt-start row before AUDIO_LOAD_FAILURE; structural ledger repair only",
                "timestamp_semantics": "original start timestamp unavailable; terminal evidence retained in raw and case ledger",
            }
        )

    before = sha256_file(ATTEMPTS)
    with ATTEMPTS.open("a", encoding="utf-8", newline="\n") as handle:
        for row in additions:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
    after = sha256_file(ATTEMPTS)
    report = {
        "repair_id": "PHASE3T_MRM_ATTEMPT_LEDGER_BACKFILL_V1",
        "authorization_id": "P3T-2026-09-13-01",
        "namespace": str(NAMESPACE).replace("\\", "/"),
        "scope": "append-only attempt-start rows for AUDIO_LOAD_FAILURE terminal records",
        "raw_modified": False,
        "case_ledger_modified": False,
        "scientific_metrics_computed": 0,
        "gt_accessed": "NO",
        "added_records": len(additions),
        "added_case_ids": [row["case_id"] for row in additions],
        "attempts_sha256_before": before,
        "attempts_sha256_after": after,
        "completed_utc": utc_now(),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
