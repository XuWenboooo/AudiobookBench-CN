"""Day 5 pre-check: rerun hashes, freeze verification and manifest validation.

This module re-verifies, without modifying anything:

- output audio hashes   : sha256 of all 70 Day 4.5 output WAVs
                          (24 clean + 23 A0 + 23 A1) against
                          ``output_audio_hashes.csv``.
- protected artifacts   : sha256 of every protected prior-stage artifact against
                          the recorded ``sha256_after`` column (freeze check).
- raw source inputs     : sha256 of the 480 selected AISHELL-3 WAVs against
                          ``source_input_hashes.csv`` (read-only guarantee).
- manifest validation   : the full Day 4.5 paired attack manifest through
                          ``validate_paired_attack_manifest`` plus a full rerun
                          of ``verify_paired_waveforms`` over all 46 WAVs.

Results are collected as JSON-serializable dicts; the pipeline writes them to
``results/day5_validation/day5_precheck.json``. Nothing is rewritten.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from audiobookbench.security.paired_manipulation import (
    load_paired_attack_manifest,
    validate_paired_attack_manifest,
    verify_paired_waveforms,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_HASH_CSV = "data/generated/day45_paired/metadata/output_audio_hashes.csv"
PROTECTED_HASH_CSV = "data/generated/day45_paired/metadata/protected_artifact_hashes.csv"
SOURCE_HASH_CSV = "data/generated/day45_paired/metadata/source_input_hashes.csv"
ATTACK_MANIFEST_CSV = "data/manifests/day45_attack_manifest.csv"
SOURCE_AUDIO_CSV = "data/manifests/day45_source_audio.csv"
DAY45_DATASET_ROOT_KEY = "dataset_root"


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read_csv(repo_root: Path, relative: str) -> list[dict[str, str]]:
    with (repo_root / relative).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def verify_output_audio_hashes(
    repo_root: Path = REPO_ROOT,
    hash_csv: str = OUTPUT_HASH_CSV,
) -> dict[str, Any]:
    rows = _read_csv(repo_root, hash_csv)
    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    for row in rows:
        path = repo_root / row["audio_relpath"]
        if not path.exists():
            missing.append(row["audio_relpath"])
            continue
        actual = _sha256(path)
        if actual != row["sha256"].upper():
            mismatches.append({"artifact_id": row["artifact_id"], "expected": row["sha256"], "actual": actual})
    return {
        "check": "output_audio_hashes",
        "rows": len(rows),
        "missing": missing,
        "mismatches": mismatches,
        "passed": not missing and not mismatches,
    }


def verify_protected_artifact_hashes(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    rows = _read_csv(repo_root, PROTECTED_HASH_CSV)
    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    for row in rows:
        path = repo_root / row["path"]
        if not path.exists():
            missing.append(row["path"])
            continue
        actual = _sha256(path)
        if actual != row["sha256_after"].upper():
            mismatches.append({"path": row["path"], "expected": row["sha256_after"], "actual": actual})
    return {
        "check": "protected_artifact_hashes",
        "rows": len(rows),
        "missing": missing,
        "mismatches": mismatches,
        "passed": not missing and not mismatches,
    }


def verify_source_input_hashes(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    rows = _read_csv(repo_root, SOURCE_HASH_CSV)
    dataset_root = _dataset_root(repo_root)
    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    for row in rows:
        path = dataset_root / row["audio_relpath"]
        if not path.exists():
            missing.append(row["audio_relpath"])
            continue
        actual = _sha256(path)
        if actual != row["sha256_after"].upper():
            mismatches.append({"sample_id": row["sample_id"], "expected": row["sha256_after"], "actual": actual})
    return {
        "check": "source_input_hashes",
        "rows": len(rows),
        "missing": missing,
        "mismatches": mismatches,
        "passed": not missing and not mismatches,
    }


def run_manifest_validation(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Full paired-attack manifest validation plus a waveform verification rerun."""
    manifest_path = repo_root / ATTACK_MANIFEST_CSV
    records = load_paired_attack_manifest(manifest_path)
    try:
        validate_paired_attack_manifest(records)
        structural_ok = True
        structural_error = ""
    except Exception as exc:  # noqa: BLE001 - record the failure, never raise through reporting
        structural_ok = False
        structural_error = str(exc)

    waveform_rows: list[dict[str, Any]] = []
    waveform_error = ""
    if structural_ok:
        source_rows = _read_csv(repo_root, SOURCE_AUDIO_CSV)
        try:
            waveform_rows = verify_paired_waveforms(
                records, source_rows, dataset_root=str(_dataset_root(repo_root)),
            )
        except Exception as exc:  # noqa: BLE001
            waveform_error = str(exc)

    return {
        "check": "manifest_validation",
        "manifest_rows": len(records),
        "structural_ok": structural_ok,
        "structural_error": structural_error,
        "waveform_rows": len(waveform_rows),
        "waveform_error": waveform_error,
        "passed": structural_ok and not waveform_error and len(waveform_rows) == len(records),
    }


def run_day5_precheck(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Run every pre-check and return the combined report."""
    checks = [
        verify_output_audio_hashes(repo_root),
        verify_protected_artifact_hashes(repo_root),
        verify_source_input_hashes(repo_root),
        run_manifest_validation(repo_root),
    ]
    return {
        "precheck": "day5",
        "checks": checks,
        "all_passed": all(check["passed"] for check in checks),
    }


def save_precheck_report(report: dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _dataset_root(repo_root: Path) -> Path:
    import yaml
    import os

    from audiobookbench.data.prepare_audio import DATASET_ROOT_ENV

    config_path = repo_root / "configs/day45_expanded_paired.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return Path(os.environ.get(DATASET_ROOT_ENV) or str(config[DAY45_DATASET_ROOT_KEY]))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}
