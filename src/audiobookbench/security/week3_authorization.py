"""Auditable, fail-closed authorization for Week3 Stage-A.

This module deliberately has no bypass flag.  An active artifact is valid only
when its schema, readiness bit, scope, and exact source hashes all match.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

REQUIRED_PROTOCOL = "WEEK3_STAGE_A_F5"
REQUIRED_SCOPE = "FORMAL_23_CASE_GENERATION_AND_FROZEN_STAGE_A_EVALUATION"
REQUIRED_FILES = ("seed_amendment", "config", "adapter", "runner", "evaluator", "environment_manifest", "review_evidence")
CANONICAL_SCHEMA = Path(__file__).resolve().parents[3] / "configs/week3_stage_a_authorization.schema.json"
CANONICAL_EVIDENCE = {
    "scientific_integrity_adjudication_sha256": Path(__file__).resolve().parents[3] / "research_assurance/WEEK3_CLEAN_RERUN_SCIENTIFIC_INTEGRITY_ADJUDICATION.md",
    "authorization_namespace_verification_sha256": Path(__file__).resolve().parents[3] / "research_assurance/WEEK3_CLEAN_RERUN_AUTHORIZATION_NAMESPACE_VERIFICATION.md",
}

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()

def validate_authorization_artifact(artifact_path: Path, expected: Mapping[str, Path]) -> dict[str, object]:
    if not artifact_path.is_file():
        raise RuntimeError("authorization artifact is missing")
    if artifact_path.name != "authorization.json":
        raise RuntimeError("only canonical authorization.json is accepted")
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("authorization artifact is not valid JSON") from exc
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("canonical authorization schema validator is unavailable") from exc
    try:
        schema = json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(artifact)
    except (OSError, json.JSONDecodeError, jsonschema.exceptions.SchemaError, jsonschema.exceptions.ValidationError) as exc:
        raise RuntimeError("authorization artifact fails canonical JSON Schema validation") from exc
    if artifact.get("protocol") != REQUIRED_PROTOCOL or artifact.get("scope") != REQUIRED_SCOPE:
        raise RuntimeError("authorization protocol or scope mismatch")
    if artifact.get("READY_FOR_STAGE_A_EXECUTION") is not True:
        raise RuntimeError("authorization readiness is not YES")
    if not artifact.get("review_date") or not artifact.get("review_evidence"):
        raise RuntimeError("authorization review evidence metadata is missing")
    hashes = artifact.get("source_sha256", {})
    missing = [name for name in REQUIRED_FILES if name not in hashes]
    if missing:
        raise RuntimeError(f"authorization hashes missing: {missing}")
    mismatches = []
    for name in REQUIRED_FILES:
        if name not in expected or not Path(expected[name]).is_file():
            raise RuntimeError(f"authorization source path missing: {name}")
        actual = sha256_file(Path(expected[name])).upper()
        if str(hashes[name]).upper() != actual:
            mismatches.append(name)
    if mismatches:
        raise RuntimeError(f"authorization source hash mismatch: {mismatches}")
    evidence_mismatches = []
    for field, path in CANONICAL_EVIDENCE.items():
        if not path.is_file() or str(artifact.get(field, "")).upper() != sha256_file(path):
            evidence_mismatches.append(field)
    if evidence_mismatches:
        raise RuntimeError(f"authorization canonical evidence hash mismatch: {evidence_mismatches}")
    expected_review = Path(expected["review_evidence"]).resolve()
    if Path(str(artifact["review_evidence"])).resolve() != expected_review:
        raise RuntimeError("authorization review evidence path mismatch")
    return {"status": "PASS", "artifact": str(artifact_path), "artifact_sha256": sha256_file(artifact_path),
            "source_sha256": dict(hashes), "run_id": artifact.get("run_id"),
            "invocation_id": artifact.get("invocation_id"), "output_root": artifact.get("output_root"),
            "independent_review_sha256": artifact.get("independent_review_sha256"),
            "rerun_classification": artifact.get("rerun_classification"),
            "historical_run_namespace": artifact.get("historical_run_namespace"),
            "historical_run_excluded": artifact.get("historical_run_excluded"),
            "prior_results_observed": artifact.get("prior_results_observed"),
            "scientific_parameters_changed_after_observation": artifact.get("scientific_parameters_changed_after_observation"),
            "scientific_integrity_adjudication_sha256": artifact.get("scientific_integrity_adjudication_sha256"),
            "authorization_namespace_verification_sha256": artifact.get("authorization_namespace_verification_sha256")}
