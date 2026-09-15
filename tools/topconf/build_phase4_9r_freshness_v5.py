"""Build and validate the prospective Phase 4.9R V5 freshness manifest.

The script changes no population or scientific artifact. It derives V5 from
the immutable V4 evidence, attaches the committed governance fields, derives
the verdict through the reconciled validator, and writes a new V5 manifest.
It never loads audio, checkpoints, predictions, labels, or outcomes.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ASSURANCE = ROOT / "research_assurance" / "topconf"
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.materialization import (  # noqa: E402
    FRESHNESS_PATH_B,
    FRESHNESS_POLICY_CLARIFICATION_ID,
    V3_UNIVERSES,
    validate_level2_freshness_v3,
)


POLICY_PATH = ASSURANCE / "PHASE4_9R_FRESHNESS_POLICY_CLARIFICATION_V1.md"
AMENDMENT_PATH = ASSURANCE / "TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_AMENDMENT_V1.md"
AUDIT_REPORT_PATH = ASSURANCE / "PHASE4_9_INDEPENDENT_FRESHNESS_SEMANTICS_AUDIT_V1.md"
V3_PATH = ASSURANCE / "LEVEL2_RQ1_POPULATION_MANIFEST_V3.json"
V4_PATH = ASSURANCE / "LEVEL2_FRESHNESS_MANIFEST_V4.json"
V5_PATH = ASSURANCE / "LEVEL2_FRESHNESS_MANIFEST_V5.json"

STRONG_CHECKS = [
    "UNIQUE_CORPUS_ARCHIVE_IDENTITY",
    "OFFICIAL_SOURCE_PROVENANCE",
    "ARCHIVE_OR_FILE_HASH",
    "FIRST_GIT_REFERENCE",
    "FIRST_MANIFEST_REFERENCE",
    "FIRST_PROJECT_USE_REFERENCE",
    "REPOSITORY_WIDE_HISTORICAL_SEARCH",
    "ALIAS_PATH_ARCHIVE_SEARCH",
    "NO_PRIOR_SCIENTIFIC_PROJECT_USAGE",
    "ACQUISITION_PROJECT_ENTRY_TIMING",
    "ASSET_LINEAGE_BOUND_TO_ARCHIVE_IDENTITY",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load_universes(freshness: dict) -> dict[str, dict]:
    universes: dict[str, dict] = {}
    for universe_id in V3_UNIVERSES:
        reference = freshness["universe_references"][universe_id]
        path = Path(reference["path"])
        if not path.is_absolute():
            path = ASSURANCE / path
        universes[universe_id] = _load(path)
    return universes


def _entry(*, pool_id: str, corpus: str, proof: str, channel_type: str) -> dict:
    return {
        "corpus": corpus,
        "pool_id": pool_id,
        "status": "PASS_POST_FREEZE_ACQUISITION",
        "evidence_sources": [proof, "LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json"],
        "path": FRESHNESS_PATH_B,
        "proof_strength": "STRONG",
        "prior_use_status": "NO_PRIOR_PROJECT_USAGE_FOUND",
        "project_entry_after_freeze": True,
        "asset_lineage_binding": "BOUND",
        "proof_checks": STRONG_CHECKS,
        "corpus_identity_proof": True,
        "project_entry_proof": proof,
        "channel_semantics": {
            "channel_type": channel_type,
            "audio_rendering": "MONO",
            "sample_rate_hz": 16000,
            "far_field_8ch_included": False,
        },
    }


def build(validator_commit: str) -> tuple[dict, dict]:
    population = _load(V3_PATH)
    previous = _load(V4_PATH)
    manifest = deepcopy(previous)
    manifest.pop("status", None)
    manifest.pop("freshness_verdict", None)
    manifest.pop("manifest_sha256", None)
    manifest.update({
        "manifest_id": "TOPCONF_RQ1_LEVEL2_FRESH_V5",
        "level2_population_manifest_sha256": _sha256(V3_PATH),
        "previous_freshness_manifest": V4_PATH.name,
        "previous_freshness_manifest_sha256": _sha256(V4_PATH),
        "freshness_policy_id": FRESHNESS_POLICY_CLARIFICATION_ID,
        "freshness_evidence_path": FRESHNESS_PATH_B,
        "policy_clarification": POLICY_PATH.name,
        "policy_clarification_sha256": _sha256(POLICY_PATH),
        "preregistration_amendment": AMENDMENT_PATH.name,
        "preregistration_amendment_sha256": _sha256(AMENDMENT_PATH),
        "independent_audit_commit": "58e036d",
        "independent_audit_report": AUDIT_REPORT_PATH.name,
        "independent_audit_report_sha256": _sha256(AUDIT_REPORT_PATH),
        "validator_commit": validator_commit,
        "validator_version": "validate_level2_freshness_v3:phase4_9r",
        "historical_universe_relevance": {
            pool_id: {
                universe_id: "IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY"
                for universe_id in V3_UNIVERSES
            }
            for pool_id in (
                "SOURCE_POOL_A_ALIMEETING_SLR119",
                "SOURCE_POOL_B_AISHELL1",
            )
        },
        "corpus_isolation": [
            _entry(
                pool_id="SOURCE_POOL_A_ALIMEETING_SLR119",
                corpus="ALIMEETING_SLR119",
                proof="LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json",
                channel_type="NEAR_FIELD_PARTICIPANT_HEADSET",
            ),
            _entry(
                pool_id="SOURCE_POOL_B_AISHELL1",
                corpus="AISHELL1_SLR33",
                proof="AISHELL1_PROJECT_ENTRY_PROOF_V1.json",
                channel_type="SINGLE_SPEAKER_MONO",
            ),
        ],
        "provenance_bindings": {
            "population_manifest": V3_PATH.name,
            "population_manifest_sha256": _sha256(V3_PATH),
            "previous_freshness_manifest": V4_PATH.name,
            "previous_freshness_manifest_sha256": _sha256(V4_PATH),
            "independent_audit_report": AUDIT_REPORT_PATH.name,
            "independent_audit_report_sha256": _sha256(AUDIT_REPORT_PATH),
            "policy_clarification": POLICY_PATH.name,
            "policy_clarification_sha256": _sha256(POLICY_PATH),
            "preregistration_amendment": AMENDMENT_PATH.name,
            "preregistration_amendment_sha256": _sha256(AMENDMENT_PATH),
            "validator_commit": validator_commit,
        },
    })

    summary = validate_level2_freshness_v3(
        population,
        manifest,
        universes=_load_universes(previous),
        allow_undecided_verdict=True,
    )
    manifest["status"] = summary["status"]
    manifest["freshness_verdict"] = summary["freshness_verdict"]
    manifest["decision"] = {
        **dict(manifest.get("decision", {})),
        "reason": summary["decision_reason"],
        "freshness_path": summary.get("freshness_evidence_path"),
        "closure": "PASS_WITHOUT_AUTHORIZATION" if summary["status"] == "PASS" else "NO_GO",
        "authorization": "PENDING_FINAL_HUMAN_REVIEW" if summary["status"] == "PASS" else "NO_GO",
        "real_level2_outcomes_accessed": False,
    }
    manifest["manifest_hash_scope"] = "canonical JSON excluding manifest_sha256"
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    manifest["manifest_sha256"] = hashlib.sha256(canonical).hexdigest().upper()
    return manifest, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validator-commit", required=True)
    args = parser.parse_args()
    manifest, summary = build(args.validator_commit)
    V5_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "freshness_verdict": summary["freshness_verdict"],
        "freshness_evidence_path": summary.get("freshness_evidence_path"),
        "decision_reason": summary["decision_reason"],
        "manifest": str(V5_PATH),
        "manifest_sha256": _sha256(V5_PATH),
        "population_sha256": _sha256(V3_PATH),
    }, ensure_ascii=False, sort_keys=True))
    return {"PASS": 0, "FAIL": 1, "INSUFFICIENT_EVIDENCE": 2}[summary["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
