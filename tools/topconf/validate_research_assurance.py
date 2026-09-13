"""Validate provenance and governance completeness for a run manifest.

The validator intentionally does not inspect AUROC, AUPRC, RangeEER, effect
direction, or any other scientific outcome. It checks only whether an artifact
package has the metadata needed for auditability and whether explicitly listed
forbidden historical paths were mutated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
NON_EMPTY = re.compile(r"\S+")

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"^research_assurance/archive(?:/|\\|$)"),
    re.compile(r"(?:^|/|\\)PHASE3_EXTERNAL_REPRODUCTION_"),
    re.compile(r"(?:^|/|\\)PHASE3R_"),
    re.compile(r"(?:^|/|\\)EXTERNAL_DATASET_LOCAL_MANIFEST_V1\.json$"),
    re.compile(r"(?:^|/|\\)EXTERNAL_REPRODUCTION_REGISTER_V1\.md$"),
    re.compile(r"(?:^|/|\\)MODEL_CAPABILITY_MATRIX_V1\.md$"),
    re.compile(r"(?:^|/|\\)BASELINE_PROVENANCE_REGISTER_V2\.md$"),
    re.compile(r"(?:^|/|\\)TOPCONF_RESEARCH_PREREGISTRATION_V1\.md$"),
    re.compile(r"(?:^|/|\\)CONFIRMATORY_PROTOCOL_SKELETON_V1\.md$"),
    re.compile(r"(?:^|/|\\)NOVELTY_LEDGER_V1\.md$"),
)


def _has(mapping: dict[str, Any], key: str) -> bool:
    return key in mapping and mapping[key] not in (None, "", {})


def _is_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not NON_EMPTY.search(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _require(mapping: dict[str, Any], key: str, errors: list[str], prefix: str) -> Any:
    if not _has(mapping, key):
        errors.append(f"missing {prefix}.{key}")
        return None
    return mapping[key]


def _require_hash(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        errors.append(f"missing or invalid SHA256: {name}")


def _validate_artifact_hashes(artifacts: dict[str, Any], errors: list[str]) -> None:
    for name, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            errors.append(f"artifact entry is not an object: {name}")
            continue
        _require(artifact, "path", errors, f"artifacts.{name}")
        _require_hash(artifact.get("sha256"), f"artifacts.{name}.sha256", errors)


def validate_manifest(
    manifest: dict[str, Any],
    *,
    registry_manifests: Iterable[dict[str, Any]] = (),
    changed_paths: Iterable[str] = (),
    check_files: bool = False,
    base_dir: Path | None = None,
) -> list[str]:
    """Return human-readable governance errors; an empty list means PASS."""

    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]

    if manifest.get("schema_version") != "topconf.research-assurance.v1":
        errors.append("unsupported or missing schema_version")

    authorization = manifest.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("missing authorization object")
    else:
        _require(authorization, "id", errors, "authorization")
        status = authorization.get("status")
        if status in {"CONFIRMATORY", "PHASE4_FINAL_FREEZE", "AUTHORIZED"}:
            errors.append("confirmatory authorization status is not allowed by this validator")
        created_at = authorization.get("created_at")
        if created_at is not None and not _is_iso_timestamp(created_at):
            errors.append("authorization.created_at must be timezone-aware ISO-8601")

    run = manifest.get("run")
    if not isinstance(run, dict):
        errors.append("missing run object")
        run = {}
    invocation_id = _require(run, "invocation_id", errors, "run")
    namespace = _require(run, "output_namespace", errors, "run")
    results_present = bool(run.get("results_present", False))
    results_at = run.get("results_at")
    if results_at is not None and not _is_iso_timestamp(results_at):
        errors.append("run.results_at must be timezone-aware ISO-8601")

    if isinstance(invocation_id, str):
        if any(
            isinstance(other.get("run"), dict)
            and other.get("run", {}).get("invocation_id") == invocation_id
            for other in registry_manifests
        ):
            errors.append(f"duplicate invocation_id: {invocation_id}")
    if isinstance(namespace, str):
        if any(
            isinstance(other.get("run"), dict)
            and other.get("run", {}).get("output_namespace") == namespace
            for other in registry_manifests
        ):
            errors.append(f"duplicate output_namespace: {namespace}")

    if isinstance(authorization, dict) and authorization.get("created_at") and results_at:
        if _is_iso_timestamp(authorization["created_at"]) and _is_iso_timestamp(results_at):
            if _timestamp(authorization["created_at"]) > _timestamp(results_at):
                errors.append("authorization postdates results")

    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("missing provenance object")
        provenance = {}
    dataset = provenance.get("dataset_identity")
    if not isinstance(dataset, dict):
        errors.append("missing provenance.dataset_identity")
    else:
        _require(dataset, "name", errors, "provenance.dataset_identity")
        _require(dataset, "version", errors, "provenance.dataset_identity")
        _require_hash(
            dataset.get("manifest_sha256"),
            "provenance.dataset_identity.manifest_sha256",
            errors,
        )
    checkpoint = provenance.get("checkpoint_identity")
    if not isinstance(checkpoint, dict):
        errors.append("missing provenance.checkpoint_identity")
    else:
        _require(checkpoint, "name", errors, "provenance.checkpoint_identity")
        _require(checkpoint, "version", errors, "provenance.checkpoint_identity")
        _require_hash(
            checkpoint.get("sha256"),
            "provenance.checkpoint_identity.sha256",
            errors,
        )
    _require(provenance, "git_commit", errors, "provenance")
    seed = _require(provenance, "seed", errors, "provenance")
    if seed is not None and not isinstance(seed, int):
        errors.append("provenance.seed must be an integer")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("missing artifacts object")
        artifacts = {}
    failure_ledger = artifacts.get("failure_ledger")
    if not isinstance(failure_ledger, dict):
        errors.append("missing artifacts.failure_ledger")
    closure = artifacts.get("closure")
    if results_present and not isinstance(closure, dict):
        errors.append("results present without artifacts.closure")
    _validate_artifact_hashes(artifacts, errors)

    if check_files:
        root = base_dir or Path.cwd()
        for name, artifact in artifacts.items():
            if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
                continue
            path = Path(artifact["path"])
            path = path if path.is_absolute() else root / path
            if not path.is_file():
                errors.append(f"artifact path does not exist: {name}: {path}")
            else:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual.lower() != str(artifact.get("sha256", "")).lower():
                    errors.append(f"artifact hash mismatch: {name}")

    errors.extend(find_forbidden_path_mutations(changed_paths))
    return errors


def find_forbidden_path_mutations(changed_paths: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for raw_path in changed_paths:
        normalized = str(raw_path).replace("\\", "/")
        if any(pattern.search(normalized) for pattern in FORBIDDEN_PATH_PATTERNS):
            errors.append(f"forbidden historical/authority path mutated: {raw_path}")
    return errors


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object expected: {path}")
    return payload


def _load_registry(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    if path.is_dir():
        return [_load_json(candidate) for candidate in sorted(path.glob("*.json"))]
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("manifests"), list):
        return [item for item in payload["manifests"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise ValueError("registry must be a JSON list, {manifests: [...]}, or directory")


def _git_changed_paths(repo_root: Path, base_commit: str | None) -> list[str]:
    if not base_commit:
        return []
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-only", base_commit, "--"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--base-commit")
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    registry = _load_registry(args.registry)
    changed_paths = _git_changed_paths(args.repo_root, args.base_commit) if args.repo_root else []
    errors = validate_manifest(
        manifest,
        registry_manifests=registry,
        changed_paths=changed_paths,
        check_files=args.check_files,
        base_dir=args.manifest.parent,
    )
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: governance and provenance completeness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
