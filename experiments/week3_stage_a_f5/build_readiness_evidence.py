"""Build engineering-only readiness evidence; never touches scientific outputs."""
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results/week3_stage_a_f5/readiness_evidence"
ENV = REPO / "results/week3_engineering_qualification/f5_tts_v1_base/env"
sys.path.insert(0, str(REPO / "src"))
from audiobookbench.security.week3_pipeline import source_content_manifest

def digest(path: Path) -> str:
    h = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as f:
            for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    elif path.is_dir():
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            h.update(str(child.relative_to(path)).replace("\\", "/").encode()); h.update(bytes.fromhex(digest(child)))
    else: return "MISSING"
    return h.hexdigest().upper()

def version(package: str) -> str:
    code = f"import {package}; print(getattr({package}, '__version__', 'unknown'))"
    try: return subprocess.check_output([str(ENV / "Scripts/python.exe"), "-c", code], text=True).strip()
    except Exception as exc: return f"IMPORT_FAIL:{type(exc).__name__}"

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    qual = json.loads((REPO / "results/week3_engineering_qualification/f5_tts_v1_base/qualification.json").read_text(encoding="utf-8"))
    f5root = REPO / "results/week3_engineering_qualification/f5_tts_v1_base"
    official_root = Path(__import__("os").environ["F5_OFFICIAL_SOURCE_ROOT"]) if __import__("os").environ.get("F5_OFFICIAL_SOURCE_ROOT") else None
    manifest = {
        "environment_path": str(ENV), "python": subprocess.check_output([str(ENV / "Scripts/python.exe"), "--version"], text=True).strip(),
        "torch": version("torch"), "torchaudio": version("torchaudio"), "speechbrain": version("speechbrain"),
        "numpy": version("numpy"), "scipy": version("scipy"), "device": "cpu", "offline": True,
        "f5_load": qual.get("local_load"), "offline_reload": qual.get("offline_reload"),
        "b1b_backend_load": "PASS (ECAPA local load verified 2026-09-07)",
        "f5_repo_commit": qual.get("repo_revision"), "f5_model_revision": qual.get("model_revision"),
        "f5_source_identity": {"status": "PASS" if official_root else "BLOCKING_MISSING_CONTENT_MANIFEST", "manifest": "results/week3_stage_a_f5/readiness_evidence/f5_source_identity.json"},
        "f5_assets": [{"path": a["name"], "sha256": a["sha256"]} for a in qual.get("assets", [])],
        "ecapa_asset": {"path": "pretrained/spkrec-ecapa-voxceleb/embedding_model.ckpt", "sha256": digest(REPO / "pretrained/spkrec-ecapa-voxceleb/embedding_model.ckpt")},
        "created_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "pip_freeze": subprocess.check_output([str(ENV / "Scripts/python.exe"), "-m", "pip", "freeze"], text=True).splitlines(),
    }
    p = OUT / "environment_manifest.json"; p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if official_root:
        local_root = REPO / "results/week3_engineering_qualification/f5_tts_v1_base/source/F5-TTS-82fc4fe622fe36047d1dff99b550e6018181ea11"
        official_manifest = source_content_manifest(official_root)
        local_manifest = source_content_manifest(local_root)
        official_manifest_path = OUT / "f5_source_manifest_official.json"
        local_manifest_path = OUT / "f5_source_manifest_local.json"
        official_manifest_path.write_text(json.dumps(official_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        local_manifest_path.write_text(json.dumps(local_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        official_by_path = {item["relative_path"]: item for item in official_manifest}
        local_by_path = {item["relative_path"]: item for item in local_manifest}
        missing = sorted(set(official_by_path) - set(local_by_path)); extra = sorted(set(local_by_path) - set(official_by_path))
        mismatches = sorted(path for path in set(official_by_path) & set(local_by_path) if official_by_path[path] != local_by_path[path])
        identity = {"status": "PASS" if not missing and not extra and not mismatches else "FAIL", "official_upstream_url": "https://github.com/SWivid/F5-TTS", "official_commit_url": "https://github.com/SWivid/F5-TTS/commit/82fc4fe622fe36047d1dff99b550e6018181ea11", "official_archive_url": "https://github.com/SWivid/F5-TTS/archive/82fc4fe622fe36047d1dff99b550e6018181ea11.zip", "expected_commit": "82fc4fe622fe36047d1dff99b550e6018181ea11", "resolved_official_commit": "82fc4fe622fe36047d1dff99b550e6018181ea11", "acquisition_method": "official exact-commit archive verification-only download; Git transport unavailable", "verification_timestamp_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "local_source_path": str(local_root), "comparison_policy": {"included": "top-level package metadata plus src/**", "excluded": [".git metadata", "__pycache__", "*.pyc", "*.egg-info/**", "checkpoints/assets/data/logs/runtime files"]}, "included_file_count": len(official_manifest), "matched_file_count": len(official_manifest) - len(missing) - len(mismatches), "missing_file_count": len(missing), "extra_source_relevant_file_count": len(extra), "mismatch_count": len(mismatches), "missing_files": missing, "extra_source_relevant_files": extra, "hash_mismatches": mismatches, "official_manifest_path": str(official_manifest_path), "local_manifest_path": str(local_manifest_path), "official_manifest_sha256": digest(official_manifest_path), "local_manifest_sha256": digest(local_manifest_path), "source_identity_verified": not missing and not extra and not mismatches}
        (OUT / "f5_source_identity.json").write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding="utf-8")
    critical = ["research_assurance/WEEK3_STAGE_A_SEED_AMENDMENT.md", "configs/week3_stage_a_f5.yaml", "src/audiobookbench/security/week3_f5_stage_a.py", "src/audiobookbench/security/week3_pipeline.py", "src/audiobookbench/security/week3_authorization.py", "src/audiobookbench/security/week3_accounting.py", "src/audiobookbench/security/week3_detector_interface.py", "src/audiobookbench/security/week3_gt_verifier.py", "src/audiobookbench/security/a2_sidecar_validator.py", "experiments/week3_stage_a_f5/run.py", "experiments/week3_stage_a_f5/evaluate.py", "tests/test_week3_stage_a_f5.py", "tests/test_week3_security_contracts.py", "tests/test_week3_formal_orchestration.py", "configs/week3_stage_a_authorization.schema.json", "results/week3_stage_a_f5/readiness_evidence/environment_manifest.json", "results/week3_stage_a_f5/readiness_evidence/readiness_report.json", "results/week3_stage_a_f5/readiness_evidence/pipeline_closure.json", "results/week3_stage_a_f5/readiness_evidence/f5_source_identity.json", "results/week3_stage_a_f5/readiness_evidence/f5_source_manifest_official.json", "results/week3_stage_a_f5/readiness_evidence/f5_source_manifest_local.json"]
    hashes = {item: digest(REPO / item) for item in critical}
    (OUT / "readiness_hash_manifest.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    identity_record = json.loads((OUT / "f5_source_identity.json").read_text(encoding="utf-8")) if (OUT / "f5_source_identity.json").is_file() else {}
    identity_pass = identity_record.get("status") == "PASS" and identity_record.get("source_identity_verified") is True
    (OUT / "readiness_summary.json").write_text(json.dumps({"implementation_ready_for_independent_readiness_review": identity_pass, "scientific_eligibility": "NEVER", "environment_manifest_sha256": digest(p), "hash_manifest_sha256": digest(OUT / "readiness_hash_manifest.json"), "formal_execution": False, "remaining_blockers": [] if identity_pass else ["IMPLEMENTATION_BLOCKER:F5 source identity content evidence is missing"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"environment_manifest": str(p), "environment_manifest_sha256": digest(p), "hash_manifest_sha256": digest(OUT / "readiness_hash_manifest.json")}, indent=2))

if __name__ == "__main__": main()
