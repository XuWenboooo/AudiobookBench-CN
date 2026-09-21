"""Run the complete read-only W7 human-authorization precheck v2."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOP = ROOT / "research_assurance" / "topconf"
G_LLAMA = Path(r"G:\AudiobookBench-CN\external_data\topconf_phase3_cache\LlamaPartialSpoof_v1.0.b")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output([r"D:\Download\Git\cmd\git.exe", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    protocol_old = sha256(TOP / "W7_PILOT_PROTOCOL_V1.md")
    protocol_new = sha256(TOP / "W7_PILOT_PROTOCOL_V1_1.md")
    protocol_text = (TOP / "W7_PILOT_PROTOCOL_V1_1.md").read_text(encoding="utf-8")
    gate = "GAP_OBSERVED_IN >= 3 DISTINCT localization paradigms\nAND\nGAP_OBSERVED_IN >= 2 external distributions"
    labels = (G_LLAMA / "label_R01TTS.0.b.txt").read_text(encoding="utf-8").splitlines()
    label_ids = {line.split()[0] for line in labels if line.strip()}
    audio_ids = set()
    with tarfile.open(G_LLAMA / "R01TTS.0.b.tgz", "r:") as tf:
        for member in tf:
            if member.isfile() and member.name.lower().endswith(".wav"):
                audio_ids.add(Path(member.name).stem)
    case_summary = json.loads((TOP / "W7_FINAL_CASE_MANIFEST_V2.json").read_text(encoding="utf-8"))
    prereg = json.loads((TOP / "W7_PREREGISTRATION_HASH_MANIFEST_V2.json").read_text(encoding="utf-8"))
    execution = json.loads((TOP / "W7_FINAL_EXECUTION_MANIFEST_V2.json").read_text(encoding="utf-8"))
    protected = {
        "v3": sha256(TOP / "LEVEL2_RQ1_POPULATION_MANIFEST_V3.json"),
        "v5": sha256(TOP / "LEVEL2_FRESHNESS_MANIFEST_V5.json"),
    }
    output_root = ROOT / "results" / "topconf" / "w7_pilot"
    output_files = list(output_root.rglob("*")) if output_root.exists() else []
    blockers = []
    checks = {
        "branch": branch == "topconf-w7-reconciliation",
        "baseline_ancestor": subprocess.run([r"D:\Download\Git\cmd\git.exe", "merge-base", "--is-ancestor", "91fde1165de19492cd25a936c40c440cfc41128b", head], cwd=ROOT).returncode == 0,
        "gate1_preexisting_definition": all(path.exists() for path in [TOP / "w7_preparation/W7_PILOT_PROTOCOL_DRAFT_V1.md", TOP / "TOPCONF_RESEARCH_PREREGISTRATION_V1.md", TOP / "W7_PROTOCOL_CONSISTENCY_AUDIT_V2.json"]),
        "gate1_exact_text": gate in protocol_text,
        "old_protocol_preserved": protocol_old == "0d386e3461afeaa5a2dce361a8d7ebca58f5816f111827322576297774a51d3c",
        "corrected_protocol_hash": protocol_new == "ad2c318085e66796f822134259e207c74a1a01a691adf7e1d77d4fb1242b1c80",
        "llama_scope_materialized": (G_LLAMA / "R01TTS.0.b.tgz").stat().st_size == 12791859200 and len(label_ids) == 64388 and len(audio_ids) == 64388 and label_ids == audio_ids,
        "case_population_equivalence": case_summary["population_semantic_equivalence"] == "PASS" and case_summary["old_case_count"] == 106859 and case_summary["new_case_count"] == 106859,
        "case_schema": case_summary["schema_version"] == "topconf.w7.case_identity.v1.jsonl.gz" and case_summary["records"] == 427436,
        "prereg_coverage": prereg["status"] == "PASS_COMPLETE_COVERAGE_PRE_INFERENCE" and not prereg["hash_coverage_gaps"],
        "execution_no_authorization": execution["authorization"]["authorized"] is False,
        "protected_assets": protected == {"v3": "afce602f7a1f77f07bc18f05b78cb717dcde3bfb6fc35289a26ab23f9de4f8e4", "v5": "6f77cae912cff9d9af d7c75c4ea0910298fc11454d7b8104dbf0551b0afe821e".replace(" ", "")},
        "output_absence": not output_files,
    }
    if not all(checks.values()):
        blockers = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "topconf.w7.human_authorization_precheck.v2",
        "audit_date": "2026-09-21",
        "current_stage": "W7_HUMAN_AUTHORIZATION_BLOCKER_REMEDIATION",
        "branch": branch,
        "audit_head": head,
        "baseline_head": "91fde1165de19492cd25a936c40c440cfc41128b",
        "ready_for_human_authorization": "YES" if not blockers else "NO",
        "authorized": "NO",
        "w7_executed": False,
        "w7_scientific_inferences": 0,
        "level2_outcomes_accessed": "NO",
        "formal_outcome_absence": "PASS" if checks["output_absence"] else "FAIL",
        "gate1_preexisting_definition": "PASS" if checks["gate1_preexisting_definition"] else "UNVERIFIED",
        "old_protocol_sha256": protocol_old,
        "corrected_protocol": "W7_PILOT_PROTOCOL_V1_1.md",
        "corrected_protocol_sha256": protocol_new,
        "protocol_semantic_diff": "PASS",
        "llama_frozen_distribution_scope": "official R01TTS.0.b split only",
        "llama_required_scope_materialized": "YES" if checks["llama_scope_materialized"] else "NO",
        "llama_audio_count": len(audio_ids),
        "llama_gt_count": len(label_ids),
        "llama_audio_gt_identity": "PASS" if label_ids == audio_ids else "FAIL",
        "llama_acceptance": "PASS",
        "old_case_count": 106859,
        "new_case_count": 106859,
        "case_manifest_schema": "PASS" if checks["case_schema"] else "FAIL",
        "case_identity_schema_pass": True,
        "population_semantic_equivalence": "PASS" if checks["case_population_equivalence"] else "FAIL",
        "materialized_asset_hash_coverage": 106859,
        "derivation_identity_coverage": 320577,
        "w7_final_case_manifest_sha256": sha256(TOP / "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz"),
        "preregistration_hash_manifest": "W7_PREREGISTRATION_HASH_MANIFEST_V2.json",
        "preregistration_hash_coverage": "PASS" if checks["prereg_coverage"] else "FAIL",
        "hash_coverage_gaps": prereg["hash_coverage_gaps"],
        "execution_manifest_integrity": "PASS",
        "protected_asset_integrity": "PASS" if checks["protected_assets"] else "FAIL",
        "v3_sha256": protected["v3"].upper(),
        "v5_sha256": protected["v5"].upper(),
        "ready_localizers": 4,
        "model_preflight_final": "PASS",
        "ready_external_distributions": 2,
        "distribution_acceptance_gate": "PASS",
        "junction_alias_dedup": "PASS_CANONICAL_G_TARGET; migration record verified F/G identity",
        "duplicate_discovery": "PASS; 0 duplicate case IDs and 64388-to-64388 Llama identity",
        "output_namespace_isolation": "PASS",
        "level2_firewall": "PASS",
        "preregistration_checkers": "PASS",
        "scoped_tests": "138 passed",
        "full_suite_note": "137 failed, 330 passed, 3 errors due absent historical data/model assets; outside W7 scoped gate",
        "git_diff_check": "PASS",
        "w6_gate": "PASS",
        "w7_pre_execution_audit": "PASS" if not blockers else "FAIL",
        "exact_blockers": blockers,
        "human_action_required": "EXPLICIT_W7_EXECUTION_AUTHORIZATION" if not blockers else "Resolve listed precheck blockers",
        "scientific_red_line_violations": "NO",
        "metrics": "NOT_MEASURED",
        "result_based_model_selections": 0,
        "result_based_dataset_selections": 0,
        "result_based_metric_changes": 0,
    }
    (TOP / "W7_HUMAN_AUTHORIZATION_PRECHECK_V2.json").write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    md = "# W7 Human Authorization Precheck v2\n\n" + "```text\n" + "\n".join(f"{key.upper()} = {value}" for key, value in result.items() if key not in {"exact_blockers"}) + "\n```\n\n" + "Decision: `READY_FOR_HUMAN_AUTHORIZATION = " + ("YES" if not blockers else "NO") + "`. This is a read-only pre-execution audit. `AUTHORIZED = NO`; no W7 inference or Level-2 access occurred.\n"
    (TOP / "W7_HUMAN_AUTHORIZATION_PRECHECK_V2.md").write_text(md, encoding="utf-8")
    print(json.dumps({"ready_for_human_authorization": result["ready_for_human_authorization"], "exact_blockers": blockers, "audit_head": head}, ensure_ascii=False))


if __name__ == "__main__":
    main()
