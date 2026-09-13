from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parents[2] / "tools" / "topconf"
sys.path.insert(0, str(TOOLS_DIR))

from validate_research_assurance import (  # noqa: E402
    find_forbidden_path_mutations,
    validate_manifest,
)


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def valid_manifest(*, results_present: bool = True) -> dict:
    artifacts = {
        "failure_ledger": {"path": "failure.json", "sha256": _hash("failure")},
        "config": {"path": "config.json", "sha256": _hash("config")},
    }
    if results_present:
        artifacts["closure"] = {"path": "closure.json", "sha256": _hash("closure")}
    return {
        "schema_version": "topconf.research-assurance.v1",
        "authorization": {
            "id": "synthetic-auth-001",
            "status": "SYNTHETIC_ONLY",
            "created_at": "2026-09-13T08:00:00+00:00",
        },
        "run": {
            "invocation_id": "synthetic-invocation-001",
            "output_namespace": "synthetic/20260913/001",
            "results_present": results_present,
            "results_at": "2026-09-13T08:05:00+00:00" if results_present else None,
        },
        "provenance": {
            "dataset_identity": {
                "name": "synthetic-population",
                "version": "v1",
                "manifest_sha256": _hash("dataset"),
            },
            "checkpoint_identity": {
                "name": "synthetic-statistics-no-model",
                "version": "none",
                "sha256": _hash("checkpoint"),
            },
            "git_commit": "2fe5641274b232a5535df6b36314e665a12c043e",
            "seed": 20260913,
        },
        "artifacts": artifacts,
    }


def test_valid_synthetic_run_passes():
    assert validate_manifest(valid_manifest()) == []


def test_missing_authorization_fails():
    manifest = valid_manifest()
    del manifest["authorization"]
    assert any("authorization" in error for error in validate_manifest(manifest))


def test_missing_checkpoint_hash_fails():
    manifest = valid_manifest()
    del manifest["provenance"]["checkpoint_identity"]["sha256"]
    assert any("checkpoint_identity.sha256" in error for error in validate_manifest(manifest))


def test_duplicate_namespace_fails():
    manifest = valid_manifest()
    assert any(
        "duplicate output_namespace" in error
        for error in validate_manifest(manifest, registry_manifests=[valid_manifest()])
    )


def test_results_without_closure_fails():
    manifest = valid_manifest()
    del manifest["artifacts"]["closure"]
    assert any("without artifacts.closure" in error for error in validate_manifest(manifest))


def test_missing_failure_accounting_fails():
    manifest = valid_manifest()
    del manifest["artifacts"]["failure_ledger"]
    assert any("failure_ledger" in error for error in validate_manifest(manifest))


def test_historical_path_mutation_fixture_fails_closed():
    errors = find_forbidden_path_mutations(
        [
            "research_assurance/archive/WEEK4_CLOSURE.md",
            "research_assurance/topconf/PHASE3R_RECOVERY_CLOSURE.md",
        ]
    )
    assert len(errors) == 2
