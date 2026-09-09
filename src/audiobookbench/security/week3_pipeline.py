"""Canonical, fail-closed Week3 F5 generation orchestration.

The pipeline is deliberately callable only with a validated authorization
artifact.  Tests may provide a temporary, explicitly mocked artifact and API;
the repository's canonical active authorization path remains absent until a
future independent review authorizes scientific execution.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from audiobookbench.security.a2_sidecar_validator import validate_row as validate_sidecar_row
from audiobookbench.security.a2_waveform_gt_verifier import verify_row as verify_waveform_row
from audiobookbench.security.week3_accounting import (
    append_attempt, classify_failure, final_accounting_rows, write_cases_csv,
    validate_formal_attempt_provenance, terminal_history,
)
from audiobookbench.security.week3_authorization import validate_authorization_artifact, sha256_file
from audiobookbench.security.week3_f5_stage_a import (
    InferenceSettings, build_f5_api, build_success_sidecar, construct_replacement,
    generation_seed, infer_once,
)
from audiobookbench.security.week3_gt_verifier import verify_sample_first_gt
from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import project_ground_truth_speaker

CONFIG_REL = Path("configs/week3_stage_a_f5.yaml")
PLANNED_REL = Path("data/manifests/week2a_a2_planned_manifest.csv")
REFERENCE_REL = Path("data/manifests/week2a_reference_manifest.csv")
LONGFORM_REL = Path("data/manifests/day45_longform_manifest.csv")
ENV_MANIFEST_REL = Path("results/week3_stage_a_f5/readiness_evidence/environment_manifest.json")
HISTORICAL_AUTH_REL = Path("results/week3_stage_a_f5/authorization.json")
FUTURE_AUTH_REL = Path("results/week3_stage_a_f5_runs/authorization.json")
RUNS_ROOT_REL = Path("results/week3_stage_a_f5_runs")
SOURCE_IDENTITY_REL = Path("results/week3_stage_a_f5/readiness_evidence/f5_source_identity.json")
LOCAL_SOURCE_MANIFEST_REL = Path("results/week3_stage_a_f5/readiness_evidence/f5_source_manifest_local.json")

@dataclass(frozen=True)
class FrozenInputs:
    config: dict[str, Any]
    cases: list[dict[str, str]]
    config_hash: str
    environment_hash: str
    source_paths: dict[str, Path]

def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [dict(row) for row in csv.DictReader(stream)]

def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()

def _source_paths(repo: Path) -> dict[str, Path]:
    return {
        "seed_amendment": repo / "research_assurance/WEEK3_STAGE_A_SEED_AMENDMENT.md",
        "config": repo / CONFIG_REL,
        "adapter": repo / "src/audiobookbench/security/week3_f5_stage_a.py",
        "runner": repo / "experiments/week3_stage_a_f5/run.py",
        "evaluator": repo / "experiments/week3_stage_a_f5/evaluate.py",
        "environment_manifest": repo / ENV_MANIFEST_REL,
        "review_evidence": repo / "results/week3_stage_a_f5/readiness_evidence/readiness_report.json",
    }

def load_frozen_inputs(repo: Path) -> FrozenInputs:
    config_path = repo / CONFIG_REL
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config.get("protocol") != "WEEK3_STAGE_A_F5" or config.get("scientific_execution_enabled") is not False:
        raise RuntimeError("frozen Week3 config is invalid or execution is not fail-closed")
    planned = _read_csv(repo / PLANNED_REL)
    references = {r["reference_sample_id"]: r for r in _read_csv(repo / REFERENCE_REL)}
    longform = _read_csv(repo / LONGFORM_REL)
    sequence_paths: dict[str, list[dict[str, str]]] = {}
    for row in longform:
        sequence_paths.setdefault(row["sequence_id"], []).append(row)
    planned.sort(key=lambda row: row["paired_case_id"])
    if len(planned) != 23 or [r["paired_case_id"] for r in planned] != [f"paircase_{i:04d}" for i in range(1, 24)]:
        raise RuntimeError("frozen planned manifest must contain paircase_0001..paircase_0023 in order")
    if {r["split"] for r in planned} != {"train", "val", "test"} or {s: sum(r["split"] == s for r in planned) for s in ("train", "val", "test")} != {"train": 11, "val": 6, "test": 6}:
        raise RuntimeError("frozen 11/6/6 split contract failed")
    cases: list[dict[str, str]] = []
    for index, plan in enumerate(planned):
        ref = references.get(plan["reference_sample_id"])
        if ref is None or ref["speaker"] != plan["target_speaker"] or ref["split"] != plan["split"]:
            raise RuntimeError(f"reference lineage invalid for {plan['paired_case_id']}")
        if plan["reference_sample_id"] == plan["target_source_sample_id"] or ref["reference_text_exact"] == plan["source_text_exact"]:
            raise RuntimeError(f"reference is not distinct for {plan['paired_case_id']}")
        seq_rows = sequence_paths.get(plan["clean_sequence_id"], [])
        if not seq_rows or any(r["speaker"] != plan["target_speaker"] or r["split"] != plan["split"] for r in seq_rows):
            raise RuntimeError(f"longform/source lineage invalid for {plan['paired_case_id']}")
        case = dict(plan)
        case.update({
            "reference_text_exact": ref["reference_text_exact"],
            "reference_audio_path": ref["reference_audio_path"],
            "clean_sequence_audio_path": seq_rows[0]["sequence_audio_path"],
            "reference_text_sha256": _hash_text(ref["reference_text_exact"]),
        })
        for path_key in ("source_audio_path", "reference_audio_path", "clean_sequence_audio_path"):
            if not Path(case[path_key]).is_file():
                raise RuntimeError(f"frozen lineage audio is missing: {path_key} for {plan['paired_case_id']}")
        if case["source_text_exact"] != case["tts_input_text"]:
            raise RuntimeError(f"source exact text contract failed for {plan['paired_case_id']}")
        cases.append(case)
    return FrozenInputs(config=config, cases=cases, config_hash=sha256_file(config_path),
                        environment_hash=sha256_file(repo / ENV_MANIFEST_REL),
                        source_paths=_source_paths(repo))

def validate_frozen_assets(repo: Path, config: dict[str, Any]) -> dict[str, str]:
    f5 = config["f5"]
    files = {
        "checkpoint": (repo / f5["ckpt_file"], f5["checkpoint_sha256"]),
        "vocab": (repo / f5["vocab_file"], f5["vocab_sha256"]),
        "vocoder_config": (repo / f5["vocoder_config_file"], f5["vocoder_config_sha256"]),
        "vocoder_model": (repo / f5["vocoder_model_file"], f5["vocoder_model_sha256"]),
    }
    actual: dict[str, str] = {}
    for name, (path, expected) in files.items():
        if not path.is_file():
            raise RuntimeError(f"frozen asset missing: {name}")
        actual[name] = sha256_file(path)
        if actual[name] != str(expected).upper():
            raise RuntimeError(f"frozen asset hash mismatch: {name}")
    vocoder_dir = repo / f5["vocoder_local_path"]
    if not vocoder_dir.is_dir():
        raise RuntimeError("frozen vocoder directory missing")
    return actual

def validate_runtime(repo: Path, config: dict[str, Any]) -> dict[str, str]:
    f5 = config["f5"]
    import torch, torchaudio, speechbrain
    values = {"python": platform.python_version(), "torch": torch.__version__, "torchaudio": torchaudio.__version__, "speechbrain": speechbrain.__version__}
    expected = {"python": str(f5["python"]), "torch": str(f5["torch"]), "torchaudio": str(f5["torch"]), "speechbrain": "1.1.1"}
    for key, value in expected.items():
        if values[key] != value:
            raise RuntimeError(f"frozen runtime mismatch: {key}={values[key]} expected={value}")
    if os.environ.get("HF_HUB_OFFLINE") not in {"1", "true", "True"} or os.environ.get("TRANSFORMERS_OFFLINE") not in {"1", "true", "True"}:
        raise RuntimeError("offline execution is not enforced")
    return values

def validate_preflight(repo: Path) -> FrozenInputs:
    inputs = load_frozen_inputs(repo)
    config = inputs.config
    f5 = config["f5"]
    validate_frozen_assets(repo, config)
    validate_f5_source_identity(repo, config)
    validate_runtime(repo, config)
    if int(config["crossfade_samples"]) != 400 or float(config["crossfade_ms_per_edge"]) != 25.0:
        raise RuntimeError("A2 insertion crossfade contract mismatch")
    return inputs

def validate_f5_source_identity(repo: Path, config: dict[str, Any]) -> str:
    """Verify source identity from Git or a frozen content manifest.

    A directory name is intentionally never treated as provenance: the F5
    qualification snapshot is not a worktree, so formal execution remains
    locked until an auditable source-content manifest is supplied.
    """
    expected = str(config["f5"]["repo_commit"])
    source_root = (repo / "results/week3_engineering_qualification/f5_tts_v1_base/source").resolve()
    candidates = [p for p in source_root.iterdir() if p.is_dir() and p.name.startswith("F5-TTS-")]
    if len(candidates) != 1:
        raise RuntimeError("frozen F5 source snapshot is missing or ambiguous")
    source = candidates[0]
    if source.name != f"F5-TTS-{expected}":
        raise RuntimeError("F5 source directory revision label mismatch")
    git_dir = source / ".git"
    if git_dir.exists():
        try:
            actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError("unable to verify F5 Git source identity") from exc
        if actual != expected:
            raise RuntimeError(f"F5 source revision mismatch: {actual} != {expected}")
        return actual
    evidence_path = repo / SOURCE_IDENTITY_REL
    if not evidence_path.is_file():
        raise RuntimeError("F5 source identity evidence is missing")
    try:
        record = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("F5 source identity evidence is invalid") from exc
    if record.get("status") != "PASS" or record.get("source_identity_verified") is not True:
        raise RuntimeError("F5 source identity evidence is not PASS")
    if record.get("expected_commit") != expected or record.get("resolved_official_commit") != expected or Path(str(record.get("local_source_path", ""))).resolve() != source.resolve():
        raise RuntimeError("F5 source identity manifest mismatch")
    manifest_path = repo / LOCAL_SOURCE_MANIFEST_REL
    if not manifest_path.is_file() or sha256_file(manifest_path) != str(record.get("local_manifest_sha256", "")).upper():
        raise RuntimeError("F5 frozen local source manifest is missing or altered")
    frozen_files = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_files = source_content_manifest(source)
    if current_files != frozen_files:
        raise RuntimeError("F5 local source manifest no longer matches frozen snapshot")
    return expected

def source_content_manifest(root: Path) -> list[dict[str, Any]]:
    """Deterministic source-only manifest shared by evidence and preflight."""
    top_level = {"pyproject.toml", "ruff.toml", "README.md", "LICENSE", ".gitmodules"}
    entries: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative not in top_level and not relative.startswith("src/"):
            continue
        if "/__pycache__/" in f"/{relative}" or relative.endswith(".pyc") or ".egg-info/" in relative:
            continue
        entries.append({"relative_path": relative, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return sorted(entries, key=lambda item: item["relative_path"])

def _as_csv_row(row: dict[str, Any]) -> dict[str, str]:
    return {key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value) for key, value in row.items()}

def _interval_row(row: dict[str, Any]) -> dict[str, tuple[int, int]]:
    return {"attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
            "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
            "blend": (int(row["blend_in_start_sample"]), int(row["blend_out_end_sample"]))}

def _attempt_record(case: dict[str, str], attempt: int, seed: int, inputs: FrozenInputs, status: str, failure_class: str = "", failure_reason: str = "", raw_hash: str = "", *, authorization: dict[str, Any] | None = None, run_id: str = "", invocation_id: str = "", repo: Path | None = None, case_table_hash: str = "") -> dict[str, Any]:
    auth = authorization or {}
    source = auth.get("source_sha256", {})
    return {"paired_case_id": case["paired_case_id"], "attempt_number": attempt, "seed": seed,
            "source_hash": case["source_text_sha256"], "reference_hash": case["reference_text_sha256"],
            "config_hash": inputs.config_hash, "environment_hash": inputs.environment_hash,
            "model": inputs.config["f5"]["model"], "model_revision": inputs.config["f5"]["model_revision"],
            "asset_hashes": {"checkpoint": inputs.config["f5"]["checkpoint_sha256"], "vocab": inputs.config["f5"]["vocab_sha256"], "vocoder": inputs.config["f5"]["vocoder_model_sha256"]},
            "inference_settings": {key: inputs.config["f5"][key] for key in ("ode_method", "use_ema", "target_rms", "cross_fade_duration", "sway_sampling_coef", "cfg_strength", "nfe_step", "speed", "fix_duration", "remove_silence")},
            "a2_insertion_crossfade_samples": 400,
            "start_time": datetime.now(timezone.utc).isoformat(), "end_time": datetime.now(timezone.utc).isoformat(),
            "status": status, "failure_class": failure_class, "failure_reason": failure_reason, "raw_output_hash": raw_hash,
            "run_id": run_id, "invocation_id": invocation_id,
            "authorization_sha256": auth.get("artifact_sha256", ""),
            "independent_review_sha256": auth.get("independent_review_sha256") or source.get("review_evidence", ""),
            "environment_manifest_sha256": inputs.environment_hash,
            "config_sha256": inputs.config_hash,
            "case_table_sha256": case_table_hash,
            "runner_sha256": sha256_file(repo / "experiments/week3_stage_a_f5/run.py") if repo else ""}

def run_formal_generation(repo: Path) -> dict[str, Any]:
    """Canonical formal entrypoint; only the repository auth path is valid."""
    inputs = load_frozen_inputs(repo)
    authorization = validate_authorization_artifact(repo / FUTURE_AUTH_REL, inputs.source_paths)
    _require_formal_identity(authorization)
    if _resolve_bound_path(repo, str(authorization["historical_run_namespace"])) != (repo / "results/week3_stage_a_f5").resolve():
        raise RuntimeError("historical run namespace binding mismatch")
    validate_preflight(repo)
    output_root = canonical_run_root(repo, str(authorization["run_id"]))
    if _resolve_bound_path(repo, str(authorization["output_root"])) != output_root:
        raise RuntimeError("authorization output namespace mismatch")
    _require_empty_clean_namespace(output_root, repo)
    return _execute_generation(repo, inputs, authorization, output_root=output_root, test_only=False)

def run_test_fixture_generation(repo: Path, inputs: FrozenInputs, *, api_factory: Callable[[FrozenInputs], Any], output_root: Path) -> dict[str, Any]:
    """Explicit TEST_ONLY fixture entrypoint, never a formal authorization path."""
    return _execute_generation(repo, inputs, {"artifact_sha256": "TEST_ONLY_FIXTURE"}, api_factory=api_factory, output_root=output_root, test_only=True)

def _execute_generation(repo: Path, inputs: FrozenInputs, authorization: dict[str, Any], *, api_factory: Callable[[FrozenInputs], Any] | None = None, output_root: Path, test_only: bool) -> dict[str, Any]:
    root = output_root.resolve()
    canonical = (repo / "results/week3_stage_a_f5").resolve()
    if not test_only and root == canonical:
        raise RuntimeError("formal output cannot use historical Week3 namespace")
    if not test_only and root != canonical_run_root(repo, str(authorization["run_id"])):
        raise RuntimeError("formal output must remain in the authorized run namespace")
    if any(part in {"day10", "day11"} for part in root.parts):
        raise RuntimeError("historical output namespace is forbidden")
    if not test_only:
        _require_empty_clean_namespace(root, repo)
    root.mkdir(parents=True, exist_ok=True)
    accounting_dir = root / "accounting"; sidecar_dir = root / "sidecars"; generation_dir = root / "generation"
    accounting_dir.mkdir(exist_ok=True); sidecar_dir.mkdir(exist_ok=True); generation_dir.mkdir(exist_ok=True)
    attempts_path = accounting_dir / "attempts.jsonl"
    run_id = str(authorization.get("run_id") or "TEST_ONLY_RUN")
    invocation_id = str(authorization.get("invocation_id") or "TEST_ONLY_INVOCATION")
    case_table_hash = sha256_file(repo / PLANNED_REL)
    if not test_only:
        _require_formal_identity(authorization)
        existing = _read_attempts(attempts_path)
        if existing:
            if any(not row.get("run_id") for row in existing):
                raise RuntimeError("existing unbound attempt history detected")
            if any(row.get("run_id") == run_id for row in existing):
                raise RuntimeError("existing terminal scientific attempt history detected")
            raise RuntimeError("existing attempt history belongs to another formal run")
    api = api_factory(inputs) if api_factory else None
    if api is None:
        f5 = inputs.config["f5"]
        source_root = next(p for p in (repo / "results/week3_engineering_qualification/f5_tts_v1_base/source").iterdir() if p.is_dir() and str(f5["repo_commit"]) in p.name)
        settings = InferenceSettings(**{k: f5[k] for k in ("model", "device", "ode_method", "use_ema", "target_rms", "cross_fade_duration", "sway_sampling_coef", "cfg_strength", "nfe_step", "speed", "fix_duration", "remove_silence")})
        api = build_f5_api(source_root, settings, ckpt_file=repo / f5["ckpt_file"], vocab_file=repo / f5["vocab_file"], vocoder_local_path=repo / f5["vocoder_local_path"])
    successful: list[dict[str, Any]] = []; final_attempts: list[dict[str, Any]] = []
    run_attempts: list[dict[str, Any]] = []
    f5 = inputs.config["f5"]
    settings = InferenceSettings(**{k: f5[k] for k in ("model", "device", "ode_method", "use_ema", "target_rms", "cross_fade_duration", "sway_sampling_coef", "cfg_strength", "nfe_step", "speed", "fix_duration", "remove_silence")})
    for index, case in enumerate(inputs.cases):
        seed = generation_seed(index); completed = False; final: dict[str, Any] = {}
        for attempt in (1, 2):
            try:
                raw, native_sr, serialization_info = infer_once(api, ref_file=Path(case["reference_audio_path"]), ref_text=case["reference_text_exact"], gen_text=case["source_text_exact"], seed=seed, settings=settings)
                case_dir = generation_dir / case["paired_case_id"]; case_dir.mkdir(exist_ok=True)
                raw_path = case_dir / "raw_native.wav"; standardized_path = case_dir / "waveform_16k.wav"
                from audiobookbench.preprocessing.audio_io import write_audio
                write_audio(raw_path, raw, native_sr)
                final_wave, trim, gain, layout, serialization, _ = construct_replacement(Path(case["clean_sequence_audio_path"]), raw, native_sr, start=int(case["clean_source_utterance_start_sample"]), end=int(case["clean_source_utterance_end_sample"]), out_path=standardized_path)
                final = build_success_sidecar(case, index=index, seed=seed, raw_path=raw_path, standardized_path=standardized_path, raw_sr=native_sr, raw_wave=raw, final_wave=final_wave, trim=trim, gain=gain, layout=layout, attempts=attempt, repo_commit=f5["repo_commit"], model_revision=f5["model_revision"], checkpoint_sha256=f5["checkpoint_sha256"], vocab_sha256=f5["vocab_sha256"], vocoder_sha256=f5["vocoder_model_sha256"], reference_preprocessing="official_f5_preprocess_ref_audio_text", serialization=serialization)
                csv_row = _as_csv_row(final)
                validate_sidecar_row(csv_row, {c["paired_case_id"]: _as_csv_row(c) for c in inputs.cases}, official_smoke=False)
                verify_waveform_row(csv_row, case["clean_sequence_audio_path"])
                gt_windows = build_speaker_windows(int(final_wave.size), SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000))
                gt_rows = project_ground_truth_speaker(gt_windows, _interval_row(final), 0.5)
                final["gt_validation"] = verify_sample_first_gt(final, gt_rows)["status"]
                final["authorization_sha256"] = authorization["artifact_sha256"]
                final["run_id"] = run_id
                final["invocation_id"] = invocation_id
                final["independent_review_sha256"] = authorization.get("independent_review_sha256") or authorization.get("source_sha256", {}).get("review_evidence", "")
                final["environment_manifest_sha256"] = inputs.environment_hash
                final["config_sha256"] = inputs.config_hash
                final["case_table_sha256"] = case_table_hash
                final["runner_sha256"] = sha256_file(repo / "experiments/week3_stage_a_f5/run.py")
                attempt_row = _attempt_record(case, attempt, seed, inputs, "SUCCESS", raw_hash=final["raw_waveform_sha256"], authorization=authorization, run_id=run_id, invocation_id=invocation_id, repo=repo, case_table_hash=case_table_hash)
                if not test_only: validate_formal_attempt_provenance(attempt_row)
                append_attempt(attempts_path, attempt_row)
                run_attempts.append(attempt_row)
                (sidecar_dir / f"{case['paired_case_id']}.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
                successful.append(final); final_attempts.append({"paired_case_id": case["paired_case_id"], "status": "SUCCESS", "attempt_count": attempt, "retry_count": attempt - 1, "successful_waveform_path": final["manipulated_audio_path"], "sidecar_path": str(sidecar_dir / f"{case['paired_case_id']}.json")}); completed = True; break
            except Exception as exc:
                failure_class = classify_failure(exc); reason = str(exc)
                attempt_row = _attempt_record(case, attempt, seed, inputs, "FAILED", failure_class, reason, authorization=authorization, run_id=run_id, invocation_id=invocation_id, repo=repo, case_table_hash=case_table_hash)
                if not test_only: validate_formal_attempt_provenance(attempt_row)
                append_attempt(attempts_path, attempt_row)
                run_attempts.append(attempt_row)
                if failure_class == "infrastructure_transient" and attempt == 1:
                    continue
                final_attempts.append({"paired_case_id": case["paired_case_id"], "status": "FAILED", "attempt_count": attempt, "retry_count": max(0, attempt - 1), "failure_class": failure_class, "failure_reason": reason}); completed = True; break
        if not completed:
            raise RuntimeError("case lifecycle did not reach terminal accounting")
    sidecar_path = sidecar_dir / "sidecars.jsonl"
    with sidecar_path.open("w", encoding="utf-8") as stream:
        for row in successful: stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    cases = final_accounting_rows(inputs.cases, run_attempts, run_id=run_id if not test_only else None)
    write_cases_csv(accounting_dir / "cases.csv", cases)
    hashes = {"attempts": sha256_file(attempts_path), "cases": sha256_file(accounting_dir / "cases.csv"), "sidecars": sha256_file(sidecar_path), "config": inputs.config_hash, "environment": inputs.environment_hash}
    (accounting_dir / "output_hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    return {"status": "PASS", "test_only": test_only, "planned_n": 23, "successful_n": len(successful), "failed_n": 23 - len(successful), "authorization_sha256": authorization["artifact_sha256"], "hashes": hashes}

def _read_attempts(path: Path) -> list[dict[str, Any]]:
    if not path.is_file(): return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def _require_formal_identity(authorization: dict[str, Any]) -> None:
    missing = [key for key in ("run_id", "invocation_id", "output_root", "independent_review_sha256", "rerun_classification", "historical_run_namespace", "historical_run_excluded", "prior_results_observed", "scientific_parameters_changed_after_observation", "scientific_integrity_adjudication_sha256", "authorization_namespace_verification_sha256") if key not in authorization]
    if missing:
        raise RuntimeError(f"formal authorization identity missing: {missing}")
    if authorization.get("rerun_classification") != "INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL":
        raise RuntimeError("formal authorization rerun classification mismatch")
    if authorization.get("historical_run_excluded") is not True:
        raise RuntimeError("historical run must be explicitly excluded")
    if authorization.get("prior_results_observed") is not True:
        raise RuntimeError("prior results observation must be explicitly acknowledged")
    if authorization.get("scientific_parameters_changed_after_observation") is not False:
        raise RuntimeError("post-observation scientific parameter change must be explicitly denied")

def canonical_run_root(repo: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", run_id):
        raise RuntimeError("invalid run_id for formal namespace")
    return (repo / RUNS_ROOT_REL / run_id).resolve()

def _resolve_bound_path(repo: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else repo / path).resolve()

def _require_empty_clean_namespace(root: Path, repo: Path) -> None:
    historical = (repo / "results/week3_stage_a_f5").resolve()
    runs_root = (repo / RUNS_ROOT_REL).resolve()
    if root == historical or historical in root.parents:
        raise RuntimeError("historical namespace is forbidden for formal output")
    if root != runs_root and runs_root not in root.parents:
        raise RuntimeError("formal output is outside clean run namespace")
    if root.is_symlink():
        raise RuntimeError("clean run namespace symlink is forbidden")
    if root.exists() and any(root.iterdir()):
        raise RuntimeError("clean run namespace is not empty")
