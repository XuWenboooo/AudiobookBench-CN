"""Canonical Week4 authorization validation.

An active artifact is intentionally separate from the frozen configuration:
the configuration describes the protocol but cannot authorize execution by
itself.  This module only validates an already-issued artifact; it never
creates one and never starts F5, D0, or an evaluator.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PROTOCOL = "WEEK4_ADAPTIVE_RED_TEAM_A0"
REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_SCHEMA = REPO_ROOT / "configs/week4_formal_authorization.schema.json"
CANONICAL_SOURCES = {
    "preregistration": REPO_ROOT / "research_assurance/WEEK4_ADAPTIVE_REDTEAM_PREREGISTRATION.md",
    "canonical_config": REPO_ROOT / "configs/week4_adaptive_red_team.yaml",
    "population_manifest": REPO_ROOT / "data/manifests/week4_population_manifest.json",
    "controller": REPO_ROOT / "src/audiobookbench/security/week4_adaptive.py",
    "search_implementation": REPO_ROOT / "src/audiobookbench/security/week4_adaptive.py",
    "formal_runner": REPO_ROOT / "experiments/week4_adaptive_red_team/formal_run.py",
    "f5_qualification": REPO_ROOT / "results/week3_engineering_qualification/f5_tts_v1_base/qualification.json",
    "execution_supplement": REPO_ROOT / "research_assurance/WEEK4_EXECUTION_SUPPLEMENT_V1.md",
    "execution_supplement_config": REPO_ROOT / "configs/week4_execution_supplement_v1.yaml",
    "d0_asset_manifest": REPO_ROOT / "research_assurance/WEEK4_D0_ASSET_MANIFEST.json",
    "execution_source_manifest": REPO_ROOT / "research_assurance/WEEK4_EXECUTION_SOURCE_MANIFEST.json",
}
HEX64 = r"^[A-Fa-f0-9]{64}$"


class Week4AuthorizationError(RuntimeError):
    """Raised for any missing, malformed, stale, or out-of-scope artifact."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


@dataclass(frozen=True)
class ValidatedWeek4Authorization:
    artifact: Mapping[str, Any]
    artifact_sha256: str
    source_sha256: Mapping[str, str]
    run_id: str
    invocation_id: str
    output_namespace: str


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Week4AuthorizationError(f"{label} is not valid JSON") from exc


def _validate_schema(artifact: Any) -> None:
    try:
        import jsonschema
        schema = _load_json(CANONICAL_SCHEMA, "canonical Week4 authorization schema")
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(artifact)
    except ImportError as exc:
        raise Week4AuthorizationError("canonical authorization schema validator is unavailable") from exc
    except Exception as exc:
        if exc.__class__.__module__.startswith("jsonschema"):
            raise Week4AuthorizationError("authorization artifact fails canonical JSON Schema validation") from exc
        raise


def _verify_file_manifest(path: Path, *, asset_key: str, hash_key: str, root: Path) -> None:
    """Require a canonical manifest and recompute every listed repository file."""
    manifest = _load_json(path, path.name)
    assets = manifest.get(asset_key)
    if not isinstance(assets, list) or not assets:
        raise Week4AuthorizationError(f"{path.name} has no canonical assets")
    seen: set[str] = set()
    for asset in assets:
        if not isinstance(asset, Mapping):
            raise Week4AuthorizationError(f"{path.name} contains malformed asset")
        rel, supplied = asset.get("relative_path"), asset.get(hash_key)
        if not isinstance(rel, str) or not isinstance(supplied, str) or rel in seen:
            raise Week4AuthorizationError(f"{path.name} contains ambiguous asset identity")
        seen.add(rel)
        resolved = (root / rel).resolve()
        if root not in resolved.parents or not resolved.is_file() or sha256_file(resolved) != supplied.upper():
            raise Week4AuthorizationError(f"{path.name} asset hash mismatch: {rel}")
        if "size_bytes" in asset and asset["size_bytes"] != resolved.stat().st_size:
            raise Week4AuthorizationError(f"{path.name} asset size mismatch: {rel}")


def validate_authorization_artifact(
    artifact_path: Path,
    *,
    repo: Path = REPO_ROOT,
    expected_run_id: str = "week4_adaptive_redteam_v0",
    verify_f5_assets: bool = False,
) -> ValidatedWeek4Authorization:
    """Validate the sole active Week4 authorization and recompute every hash."""
    artifact_path = Path(artifact_path)
    if artifact_path.name not in {"authorization.json", "authorization.template.json"}:
        raise Week4AuthorizationError("only canonical Week4 authorization filenames are accepted")
    artifact = _load_json(artifact_path, "authorization artifact")
    _validate_schema(artifact)
    if artifact.get("protocol") != PROTOCOL or artifact.get("authorization_status") != "ACTIVE":
        raise Week4AuthorizationError("authorization is not active")
    if artifact.get("ready") is not True or artifact.get("READY_FOR_WEEK4_EXECUTION") is not True:
        raise Week4AuthorizationError("authorization readiness is not true")
    if artifact.get("scientific_execution_enabled") is not False:
        raise Week4AuthorizationError("configuration self-authorization is forbidden")
    if artifact.get("week1_3_scientific_results_already_observed") is not True:
        raise Week4AuthorizationError("Week1-3 scientific-result history must be disclosed")
    if artifact.get("week4_scientific_results_observed_before_authorization") is not False:
        raise Week4AuthorizationError("observed Week4 results may not authorize Week4 execution")
    if artifact.get("run_id") != expected_run_id:
        raise Week4AuthorizationError("authorization run_id mismatch")
    output_namespace = str(artifact.get("output_namespace", ""))
    expected_prefix = "results/week4_adaptive_redteam_runs/"
    if not output_namespace.startswith(expected_prefix) or output_namespace == expected_prefix:
        raise Week4AuthorizationError("output namespace must be a unique Week4 run directory")

    root = Path(repo).resolve()
    sources = {name: (root / path.relative_to(REPO_ROOT)).resolve() for name, path in CANONICAL_SOURCES.items()}
    hashes = artifact.get("source_sha256")
    if not isinstance(hashes, Mapping):
        raise Week4AuthorizationError("authorization source hashes are missing")
    mismatches: list[str] = []
    for name, path in sources.items():
        supplied = hashes.get(name)
        if not isinstance(supplied, str) or len(supplied) != 64:
            mismatches.append(name)
            continue
        if not path.is_file() or supplied.upper() != sha256_file(path):
            mismatches.append(name)
    for field, filename in {
        "preregistration_sha256": "preregistration",
        "canonical_config_sha256": "canonical_config",
        "population_manifest_sha256": "population_manifest",
        "controller_sha256": "controller",
        "search_implementation_sha256": "search_implementation",
        "formal_runner_sha256": "formal_runner",
        "f5_qualification_sha256": "f5_qualification",
        "execution_supplement_sha256": "execution_supplement",
        "execution_supplement_config_sha256": "execution_supplement_config",
        "d0_asset_manifest_sha256": "d0_asset_manifest",
        "execution_source_manifest_sha256": "execution_source_manifest",
    }.items():
        if str(artifact.get(field, "")).upper() != str(hashes.get(filename, "")).upper():
            mismatches.append(field)
    if mismatches:
        raise Week4AuthorizationError(f"authorization canonical hash mismatch: {sorted(set(mismatches))}")

    _verify_file_manifest(sources["d0_asset_manifest"], asset_key="assets", hash_key="SHA256", root=root)
    _verify_file_manifest(sources["execution_source_manifest"], asset_key="sources", hash_key="sha256", root=root)

    population = _load_json(sources["population_manifest"], "population manifest")
    if population.get("status") != "FINALIZED" or population.get("final_case_count") != 48:
        raise Week4AuthorizationError("population is not finalized at 48 cases")
    if population.get("selected_without_d0") is not True or population.get("d0_invoked") is not False:
        raise Week4AuthorizationError("population selection is not D0-independent")
    if population.get("split_counts") != {"dev": 24, "validation": 12, "held_out": 12}:
        raise Week4AuthorizationError("population split counts are not 24/12/12")
    qualification = _load_json(sources["f5_qualification"], "F5 qualification")
    if qualification.get("state") != "FULLY_ELIGIBLE" or qualification.get("scientific_execution") is not False:
        raise Week4AuthorizationError("F5 qualification is not engineering-only eligible")
    if verify_f5_assets:
        assets_root = root / "results/week3_engineering_qualification/f5_tts_v1_base/assets"
        asset_mismatches = []
        for asset in qualification.get("assets", []):
            if not isinstance(asset, Mapping) or asset.get("license") != "LICENSE_PASS":
                asset_mismatches.append(str(asset.get("name", "unknown")) if isinstance(asset, Mapping) else "malformed")
                continue
            asset_name = str(asset.get("name", ""))
            relative_name = asset_name.split("/", 1)[1] if asset_name.startswith("charactr/") else asset_name
            asset_path = assets_root / relative_name
            if not asset_path.is_file() or str(asset.get("sha256", "")).upper() != sha256_file(asset_path):
                asset_mismatches.append(asset_name or "unknown")
        if asset_mismatches:
            raise Week4AuthorizationError(f"F5 asset hash mismatch: {asset_mismatches}")
    return ValidatedWeek4Authorization(
        artifact=artifact,
        artifact_sha256=sha256_file(artifact_path),
        source_sha256={name: str(value).upper() for name, value in hashes.items()},
        run_id=str(artifact["run_id"]),
        invocation_id=str(artifact["invocation_id"]),
        output_namespace=output_namespace,
    )
