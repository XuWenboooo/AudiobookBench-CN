"""Canonical, stage-scoped Week4 execution authorization validation.

Authorization is deliberately separate from the frozen scientific protocol.
This module validates an already-issued artifact only; it never creates an
artifact and never imports F5, D0, or the final evaluator.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PROTOCOL = "WEEK4_ADAPTIVE_RED_TEAM_A0"
STAGES = ("dev", "validation", "held_out")
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
    "f5_frozen_source_manifest": REPO_ROOT / "research_assurance/WEEK4_F5_FROZEN_SOURCE_MANIFEST.json",
    "formal_runtime_environment_manifest": REPO_ROOT / "research_assurance/WEEK4_FORMAL_RUNTIME_ENVIRONMENT_MANIFEST.json",
    "execution_governance_amendment_v2": REPO_ROOT / "research_assurance/WEEK4_EXECUTION_GOVERNANCE_AMENDMENT_V2.md",
    "partial_dev_invalidation": REPO_ROOT / "research_assurance/WEEK4_DEV_REEXECUTION_02_INVALIDATION.md",
    "dev03_postrun_integrity_review": REPO_ROOT / "research_assurance/WEEK4_DEV03_POSTRUN_INTEGRITY_REVIEW.md",
}
POST_VALIDATION_FREEZE = REPO_ROOT / "research_assurance/WEEK4_POST_VALIDATION_A0_FREEZE.md"
VALIDATION01_REPORT = REPO_ROOT / "research_assurance/WEEK4_VALIDATION_01_REPORT.md"
FREEZE_CONTRACT_REPAIR = REPO_ROOT / "research_assurance/WEEK4_POST_VALIDATION_FREEZE_CONTRACT_REPAIR.md"


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
    stage: str


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


def _stage_sources(root: Path, stage: str) -> dict[str, Path]:
    sources = {name: (root / path.relative_to(REPO_ROOT)).resolve() for name, path in CANONICAL_SOURCES.items()}
    if stage == "held_out":
        sources["post_validation_a0_freeze"] = (root / POST_VALIDATION_FREEZE.relative_to(REPO_ROOT)).resolve()
        sources["validation01_report"] = (root / VALIDATION01_REPORT.relative_to(REPO_ROOT)).resolve()
        sources["post_validation_freeze_contract_repair"] = (root / FREEZE_CONTRACT_REPAIR.relative_to(REPO_ROOT)).resolve()
    return sources


def _require_post_validation_freeze(path: Path) -> None:
    try:
        from audiobookbench.security.week4_post_validation_freeze import validate_freeze_record
        validate_freeze_record(path, expected_invocation_id="week4_validation_01")
    except ImportError as exc:  # pragma: no cover - defensive import boundary
        raise Week4AuthorizationError("post-validation freeze validator is unavailable") from exc
    except Exception as exc:
        raise Week4AuthorizationError("held-out authorization requires a valid post-validation A0 freeze") from exc


def validate_authorization_artifact(
    artifact_path: Path,
    *,
    repo: Path = REPO_ROOT,
    expected_run_id: str = "week4_adaptive_redteam_v0",
    expected_stage: str | None = None,
    verify_f5_assets: bool = False,
) -> ValidatedWeek4Authorization:
    """Validate a canonical authorization and bind it to exactly one stage."""
    artifact_path = Path(artifact_path)
    if artifact_path.name not in {"authorization.json", "authorization.template.json"}:
        raise Week4AuthorizationError("only canonical Week4 authorization filenames are accepted")
    artifact = _load_json(artifact_path, "authorization artifact")
    _validate_schema(artifact)
    if artifact.get("protocol") != PROTOCOL or artifact.get("authorization_status") != "ACTIVE":
        raise Week4AuthorizationError("authorization is not active")
    stage = artifact.get("stage")
    if stage not in STAGES or artifact.get("stage_authorization") != stage:
        raise Week4AuthorizationError("authorization does not bind exactly one valid execution stage")
    if expected_stage is not None and stage != expected_stage:
        raise Week4AuthorizationError("authorization stage does not match requested stage")
    if artifact.get("ready") is not True or artifact.get("READY_FOR_WEEK4_EXECUTION") is not True or artifact.get("READY_FOR_STAGE_EXECUTION") is not True:
        raise Week4AuthorizationError("authorization readiness is not true")
    if artifact.get("scientific_execution_enabled") is not False:
        raise Week4AuthorizationError("configuration self-authorization is forbidden")
    if artifact.get("week1_3_scientific_results_already_observed") is not True:
        raise Week4AuthorizationError("Week1-3 scientific-result history must be disclosed")
    if artifact.get("week4_scientific_results_observed_before_authorization") is not True:
        raise Week4AuthorizationError("prior Week4 DEV outcome history must be disclosed")
    if artifact.get("run_id") != expected_run_id:
        raise Week4AuthorizationError("authorization run_id mismatch")
    output_namespace = str(artifact.get("output_namespace", ""))
    prefix = "results/week4_adaptive_redteam_runs/"
    if not output_namespace.startswith(prefix) or output_namespace == prefix:
        raise Week4AuthorizationError("output namespace must be a unique Week4 run directory")

    root = Path(repo).resolve()
    sources = _stage_sources(root, stage)
    hashes = artifact.get("source_sha256")
    if not isinstance(hashes, Mapping):
        raise Week4AuthorizationError("authorization source hashes are missing")
    mismatches: list[str] = []
    for name, path in sources.items():
        supplied = hashes.get(name)
        if not isinstance(supplied, str) or len(supplied) != 64 or not path.is_file() or supplied.upper() != sha256_file(path):
            mismatches.append(name)
    for name in sources:
        if str(artifact.get(f"{name}_sha256", "")).upper() != str(hashes.get(name, "")).upper():
            mismatches.append(f"{name}_sha256")
    if mismatches:
        raise Week4AuthorizationError(f"authorization canonical hash mismatch: {sorted(set(mismatches))}")

    _verify_file_manifest(sources["d0_asset_manifest"], asset_key="assets", hash_key="SHA256", root=root)
    _verify_file_manifest(sources["execution_source_manifest"], asset_key="sources", hash_key="sha256", root=root)
    _verify_file_manifest(sources["f5_frozen_source_manifest"], asset_key="files", hash_key="sha256", root=root)
    environment = _load_json(sources["formal_runtime_environment_manifest"], "formal runtime environment manifest")
    if environment.get("status") != "QUALIFIED_OFFLINE_PREOUTPUT" or environment.get("f5_source", {}).get("source_manifest_sha256", "").upper() != sha256_file(sources["f5_frozen_source_manifest"]):
        raise Week4AuthorizationError("formal runtime environment does not bind the frozen F5 source")
    if stage == "held_out":
        _require_post_validation_freeze(sources["post_validation_a0_freeze"])

    required_provenance = {
        "WEEK4_SCIENTIFIC_OUTCOME_OBSERVED_BEFORE_REAUTHORIZATION": True,
        "PRIOR_FAILED_ATTEMPT_EXISTED": True,
        "PRIOR_FAILED_ATTEMPT_PRODUCED_SCIENTIFIC_OUTCOME": False,
        "PRIOR_WEEK4_DEV_OUTCOMES_OBSERVED": True,
        "PRIOR_WEEK4_VALIDATION_OUTCOMES_OBSERVED": stage == "held_out",
        "PRIOR_WEEK4_HELD_OUT_OUTCOMES_OBSERVED": False,
        "PRIOR_WEEK4_H4_OUTCOME_OBSERVED": False,
        "PRIOR_PARTIAL_RUNS_SCIENTIFICALLY_ADMISSIBLE": False,
        "POST_DEV_GOVERNANCE_AMENDMENT_EXISTS": True,
        "EXECUTION_GOVERNANCE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION": True,
        "ATTACK_METHOD_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION": False,
        "OBJECTIVE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION": False,
        "SEARCH_PROPOSAL_RULE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION": False,
        "H4_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION": False,
        "SCIENTIFIC_ATTACK_AND_ESTIMAND_SPEC_CHANGED": False,
        "EXECUTION_GOVERNANCE_AMENDED": True,
        "EXECUTION_IMPLEMENTATION_CHANGED_AFTER_PRIOR_DEV_OBSERVATION": True,
        "IMPLEMENTATION_CHANGE_CLASS": "POST_DEV_GOVERNANCE_AMENDMENT_AND_EVIDENCE_CANONICALIZATION_REPAIR",
    }
    if any(artifact.get(name) != expected for name, expected in required_provenance.items()):
        raise Week4AuthorizationError("authorization does not disclose the invalidated partial DEV provenance")
    if artifact.get("POST_DEV_GOVERNANCE_AMENDMENT_SHA256", "").upper() != str(hashes.get("execution_governance_amendment_v2", "")).upper():
        raise Week4AuthorizationError("authorization does not bind the frozen post-DEV governance amendment")

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
        mismatched_assets: list[str] = []
        for asset in qualification.get("assets", []):
            if not isinstance(asset, Mapping) or asset.get("license") != "LICENSE_PASS":
                mismatched_assets.append(str(asset.get("name", "unknown")) if isinstance(asset, Mapping) else "malformed")
                continue
            name = str(asset.get("name", "")); relative = name.split("/", 1)[1] if name.startswith("charactr/") else name
            if not (assets_root / relative).is_file() or str(asset.get("sha256", "")).upper() != sha256_file(assets_root / relative):
                mismatched_assets.append(name or "unknown")
        if mismatched_assets:
            raise Week4AuthorizationError(f"F5 asset hash mismatch: {mismatched_assets}")
    return ValidatedWeek4Authorization(
        artifact=artifact, artifact_sha256=sha256_file(artifact_path),
        source_sha256={name: str(value).upper() for name, value in hashes.items()},
        run_id=str(artifact["run_id"]), invocation_id=str(artifact["invocation_id"]),
        output_namespace=output_namespace, stage=stage,
    )
