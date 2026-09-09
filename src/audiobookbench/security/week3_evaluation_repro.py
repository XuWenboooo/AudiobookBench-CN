"""Evaluation-only reproducibility evidence reconstruction for Week3.

This module never invokes F5.  It scores only the immutable clean-run
waveforms, and it refuses to compute metrics until every score vector matches
the original precommitted ``SHA256(scores.tobytes())`` value.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from audiobookbench.evaluation.day6a_localization import auprc, auroc
from audiobookbench.preprocessing.audio_io import load_audio
from audiobookbench.security.a2_sidecar_validator import validate_row as validate_sidecar_row
from audiobookbench.security.a2_waveform_gt_verifier import verify_row as verify_waveform_row
from audiobookbench.security.week3_detector_interface import FrozenWindowSpec, score_reference_free
from audiobookbench.temporal.day6b_embed import SpeakerBackend, SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import project_ground_truth_speaker
from audiobookbench.security.week3_gt_verifier import verify_sample_first_gt
from audiobookbench.security.week3_authorization import validate_authorization_artifact

REPO = Path(__file__).resolve().parents[3]
SOURCE_RUN = "clean_rerun_20260907_01"
SOURCE_ROOT_REL = Path("results/week3_stage_a_f5_runs") / SOURCE_RUN
SOURCE_AUTH_REL = Path("results/week3_stage_a_f5_runs/authorization.json")
SOURCE_SCORE_MANIFEST_REL = SOURCE_ROOT_REL / "evaluation/score_manifest.json"
REPAIR_AUTH_REL = Path("results/week3_evaluation_repro_runs/authorization.json")
REPAIR_ROOT_REL = Path("results/week3_evaluation_repro_runs")
EXPECTED_SOURCE_AUTH = "A094979BBAC9E2EE8D9F07E6B7A0268D060E73C60A5AB632AE0FEDC2F56D3DC5"
EXPECTED_SCORE_MANIFEST = "E12E2DC6A707D14DE4AB34E07B8D5722523BF5B10E9C6FC7D76AE94FBEE2B660"
EXPECTED_CASE_IDS = [f"paircase_{i:04d}" for i in range(1, 24)]
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260905
MIN_FINITE = 1900
S2 = SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _canonical(repo: Path, value: str) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else repo / path).resolve()
    if repo.resolve() not in resolved.parents and resolved != repo.resolve():
        raise RuntimeError("evaluation repair path escapes repository")
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON artifact: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON artifact must be an object: {path}")
    return value


def _source_sha256(repo: Path) -> dict[str, Path]:
    return {
        "source_authorization": repo / SOURCE_AUTH_REL,
        "source_score_manifest": repo / SOURCE_SCORE_MANIFEST_REL,
        "detector": repo / "src/audiobookbench/security/week3_detector_interface.py",
        "backend": repo / "src/audiobookbench/temporal/day6b_embed.py",
        "scoring": repo / "src/audiobookbench/temporal/day6b_scoring.py",
        "metrics": repo / "src/audiobookbench/evaluation/day6a_localization.py",
        "gt": repo / "src/audiobookbench/temporal/day6b_scoring.py",
        "bootstrap": repo / "experiments/week3_stage_a_f5/evaluate.py",
        "repair_code": repo / "src/audiobookbench/security/week3_evaluation_repro.py",
    }


def _expected_score_commitments(repo: Path) -> dict[str, str]:
    manifest = _load_json(repo / SOURCE_SCORE_MANIFEST_REL)
    rows = manifest.get("scores")
    if not isinstance(rows, list) or len(rows) != 23:
        raise RuntimeError("original score manifest must contain exactly 23 commitments")
    result: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"paired_case_id", "window_count", "score_sha256"}:
            raise RuntimeError("original score manifest schema mismatch")
        case_id = str(row["paired_case_id"]); value = str(row["score_sha256"]).upper()
        if case_id in result or case_id not in EXPECTED_CASE_IDS or len(value) != 64:
            raise RuntimeError("original score manifest case/hash mismatch")
        result[case_id] = value
    if list(result) != EXPECTED_CASE_IDS:
        raise RuntimeError("original score manifest ordering mismatch")
    return result


def _source_waveforms(repo: Path) -> dict[str, dict[str, Any]]:
    root = repo / SOURCE_ROOT_REL
    accounting = root / "accounting/cases.csv"
    sidecar_index = root / "sidecars/sidecars.jsonl"
    if not accounting.is_file() or not sidecar_index.is_file():
        raise RuntimeError("source clean accounting or sidecar index missing")
    cases = list(csv.DictReader(accounting.open(encoding="utf-8", newline="")))
    if [row.get("paired_case_id") for row in cases] != EXPECTED_CASE_IDS:
        raise RuntimeError("source clean population is not the frozen 23-case population")
    if any(row.get("status") != "SUCCESS" for row in cases):
        raise RuntimeError("source clean population contains a non-success case")
    sidecars = {}
    for line in sidecar_index.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line); sidecars[row["paired_case_id"]] = row
    if list(sidecars) != EXPECTED_CASE_IDS:
        raise RuntimeError("source sidecar index is not the frozen 23-case population")
    for case_id in EXPECTED_CASE_IDS:
        row = sidecars[case_id]
        path = _canonical(repo, str(row["standardized_waveform_path"]))
        if SOURCE_RUN not in path.as_posix() or not path.is_file():
            raise RuntimeError(f"source waveform path is outside clean run: {case_id}")
        if sha256_file(path) != str(row["standardized_waveform_sha256"]).upper():
            raise RuntimeError(f"source waveform hash mismatch: {case_id}")
        if row.get("run_id") != SOURCE_RUN or row.get("authorization_sha256") != EXPECTED_SOURCE_AUTH:
            raise RuntimeError(f"source waveform provenance mismatch: {case_id}")
    return sidecars


def validate_repair_authorization(repo: Path, path: Path | None = None) -> dict[str, Any]:
    path = path or repo / REPAIR_AUTH_REL
    if path.resolve() != (repo / REPAIR_AUTH_REL).resolve():
        raise RuntimeError("evaluation repair authorization must use the canonical path")
    artifact = _load_json(path)
    try:
        import jsonschema
        schema = _load_json(repo / "configs/week3_evaluation_repro_authorization.schema.json")
        jsonschema.Draft202012Validator(schema).validate(artifact)
    except ImportError as exc:
        raise RuntimeError("canonical authorization schema validator is unavailable") from exc
    except Exception as exc:
        raise RuntimeError("evaluation repair authorization fails canonical schema") from exc
    if artifact["source_generation_authorization_sha256"].upper() != EXPECTED_SOURCE_AUTH:
        raise RuntimeError("source generation authorization hash mismatch")
    if artifact["original_score_manifest_sha256"].upper() != EXPECTED_SCORE_MANIFEST:
        raise RuntimeError("original score manifest hash mismatch")
    if sha256_file(repo / SOURCE_AUTH_REL) != EXPECTED_SOURCE_AUTH:
        raise RuntimeError("source generation authorization artifact changed")
    if sha256_file(repo / SOURCE_SCORE_MANIFEST_REL) != EXPECTED_SCORE_MANIFEST:
        raise RuntimeError("original score manifest changed")
    source_auth = _load_json(repo / SOURCE_AUTH_REL)
    if source_auth.get("run_id") != SOURCE_RUN or source_auth.get("READY_FOR_STAGE_A_EXECUTION") is not True:
        raise RuntimeError("source generation authorization identity is invalid")
    commitments = _expected_score_commitments(repo)
    if artifact["score_commitments"] != commitments:
        raise RuntimeError("authorization score commitments do not match canonical manifest")
    if set(artifact["source_waveform_sha256"]) != set(EXPECTED_CASE_IDS):
        raise RuntimeError("authorization source waveform binding is incomplete")
    sidecars = _source_waveforms(repo)
    actual_waveforms = {case_id: str(sidecars[case_id]["standardized_waveform_sha256"]).upper() for case_id in EXPECTED_CASE_IDS}
    if artifact["source_waveform_sha256"] != actual_waveforms:
        raise RuntimeError("authorization source waveform commitments mismatch")
    if artifact["detector_identity"] != {"name": "B1b", "timeline": "S2_1500ms_250ms", "model_asset_sha256": "0575CB64845E6B9A10DB9BCB74D5AC32B326B8DC90352671D345E2EE3D0126A2"}:
        raise RuntimeError("evaluation repair detector identity mismatch")
    bound_paths = _source_sha256(repo)
    for key, expected in artifact["source_sha256"].items():
        if key not in bound_paths or sha256_file(bound_paths[key]) != str(expected).upper():
            raise RuntimeError(f"evaluation repair source hash mismatch: {key}")
    output = _canonical(repo, artifact["output_root"])
    expected_root = (repo / REPAIR_ROOT_REL / artifact["run_id"]).resolve()
    if output != expected_root or output == (repo / SOURCE_ROOT_REL).resolve() or output.exists() and any(output.iterdir()):
        raise RuntimeError("evaluation repair namespace is invalid or non-empty")
    return artifact


def formal_preflight(repo: Path, authorization: dict[str, Any]) -> dict[str, Any]:
    if os.environ.get("HF_HUB_OFFLINE") not in {"1", "true", "True"}:
        raise RuntimeError("offline mode is not enforced")
    if os.environ.get("TRANSFORMERS_OFFLINE") not in {"1", "true", "True"}:
        raise RuntimeError("transformers offline mode is not enforced")
    from audiobookbench.security.week3_pipeline import _source_paths, load_frozen_inputs
    inputs = load_frozen_inputs(repo)
    source_context = validate_authorization_artifact(repo / SOURCE_AUTH_REL, inputs.source_paths)
    if source_context["artifact_sha256"] != EXPECTED_SOURCE_AUTH:
        raise RuntimeError("source generation authorization validation mismatch")
    sidecars = _source_waveforms(repo)
    commitments = _expected_score_commitments(repo)
    return {"status": "PASS", "source_run_id": SOURCE_RUN, "source_authorization_sha256": EXPECTED_SOURCE_AUTH,
            "source_score_manifest_sha256": EXPECTED_SCORE_MANIFEST, "planned_score_vectors": 23,
            "waveform_hashes_verified": len(sidecars), "score_commitments_loaded": len(commitments),
            "detector": "B1b", "timeline": "S2_1500ms_250ms", "generation_invoked": False,
            "source_authorization_valid": True, "original_score_manifest_valid": True}


def _bootstrap(values: Iterable[Any], statistic) -> dict[str, Any]:
    cases = list(values); rng = np.random.default_rng(BOOTSTRAP_SEED); finite = []; reasons: Counter[str] = Counter()
    for _ in range(BOOTSTRAP_N):
        try:
            value = float(statistic([cases[i] for i in rng.integers(0, len(cases), size=len(cases))]))
            if not np.isfinite(value): raise ValueError("nonfinite_statistic")
            finite.append(value)
        except Exception as exc:
            reasons[type(exc).__name__ + ":" + str(exc)] += 1
    return {"requested_replicates": BOOTSTRAP_N, "finite_replicates": len(finite), "undefined_replicates": BOOTSTRAP_N - len(finite), "undefined_reason_counts": dict(reasons), "ci": [float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))] if len(finite) >= MIN_FINITE else "NOT_REPORTABLE"}


def _finite_metric(labels: np.ndarray, scores: np.ndarray, metric: str) -> float:
    mask = np.isfinite(scores)
    if mask.sum() == 0 or np.unique(labels[mask]).size < 2: return float("nan")
    return float(auroc(labels[mask], scores[mask]) if metric == "auroc" else auprc(labels[mask], scores[mask]))


def _h1(cases, metric):
    return _finite_metric(np.concatenate([x[1] for x in cases]), np.concatenate([x[0] for x in cases]), metric)


def _h3(cases, metric):
    scores = np.concatenate([x[0] for x in cases]); full = np.concatenate([x[1] for x in cases]); core = np.concatenate([x[2] for x in cases])
    return _finite_metric(full, scores, metric) - _finite_metric(core, scores, metric)


def _write_npy(path: Path, values: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, np.asarray(values, dtype=np.float64), allow_pickle=False)


def run_formal_repair(repo: Path, *, backend: Any | None = None) -> dict[str, Any]:
    authorization = validate_repair_authorization(repo)
    preflight = formal_preflight(repo, authorization)
    root = _canonical(repo, authorization["output_root"]); root.mkdir(parents=True, exist_ok=False)
    source = _source_waveforms(repo); commitments = _expected_score_commitments(repo)
    auth_sha = sha256_file(repo / REPAIR_AUTH_REL)
    source_rows = [source[case_id] for case_id in EXPECTED_CASE_IDS]
    if backend is None: backend = SpeakerBackend()
    vectors: dict[str, np.ndarray] = {}; h1_cases = []; h3_cases = []; analysis_rows = []; timeline_rows = []; gt_rows_all = []
    commitment_rows = []
    out = root / "evidence"; out.mkdir(parents=True, exist_ok=True)
    for row in source_rows:
        case_id = row["paired_case_id"]; waveform, sr = load_audio(_canonical(repo, row["standardized_waveform_path"]), target_sr=16000)
        scores, windows = score_reference_free(backend, np.asarray(waveform, dtype=np.float32), sr, FrozenWindowSpec())
        scores = np.asarray(scores, dtype=float)
        actual_hash = hashlib.sha256(scores.tobytes()).hexdigest().upper(); expected_hash = commitments[case_id]
        commitment_rows.append({"paired_case_id": case_id, "expected_score_vector_sha256": expected_hash, "computed_score_vector_sha256": actual_hash, "hash_match": actual_hash == expected_hash, "window_count": int(scores.size)})
        vectors[case_id] = scores
        intervals = {"attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])), "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])), "blend": (int(row["blend_in_start_sample"]), int(row["blend_out_end_sample"]))}
        projected = project_ground_truth_speaker(windows, intervals, 0.5); verify_sample_first_gt(row, projected)
        full = np.asarray([bool(g["is_attack_window"]) for g in projected]); core = np.asarray([bool(g["is_core_window"]) for g in projected])
        h1_cases.append((scores, full)); h3_cases.append((scores, full, core))
        for window, gt in zip(windows, projected):
            timeline_rows.append({"paired_case_id": case_id, "repair_authorization_sha256": auth_sha, **window, "score": float(scores[window["window_index"]])})
            gt_rows_all.append({"paired_case_id": case_id, "repair_authorization_sha256": auth_sha, **window, **gt})
        analysis_rows.append({"paired_case_id": case_id, "repair_authorization_sha256": auth_sha, "source_generation_run_id": SOURCE_RUN, "source_waveform_sha256": row["standardized_waveform_sha256"], "score_vector_path": f"score_vectors/{case_id}.npy", "score_dtype": str(scores.dtype), "score_shape": list(scores.shape), "score_order": "C", "score_vector_sha256": actual_hash, "expected_score_vector_sha256": expected_hash, "hash_match": actual_hash == expected_hash})
    matched = sum(row["hash_match"] for row in commitment_rows)
    (out / "preflight.json").write_text(json.dumps({**preflight, "repair_authorization_sha256": auth_sha}, indent=2), encoding="utf-8")
    (out / "score_commitment_verification.json").write_text(json.dumps({"status":"PASS" if matched == 23 else "FAIL","repair_authorization_sha256":auth_sha,"matched":matched,"mismatched":23-matched,"missing":0,"extra":0,"rows":commitment_rows}, indent=2), encoding="utf-8")
    if len(commitment_rows) != 23 or matched != 23: raise RuntimeError("score commitment gate failed")
    for case_id, scores in vectors.items(): _write_npy(root / "score_vectors" / f"{case_id}.npy", scores)
    (out / "window_timeline.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in timeline_rows) + "\n", encoding="utf-8")
    (out / "gt_projection.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in gt_rows_all) + "\n", encoding="utf-8")
    (out / "analysis_rows.json").write_text(json.dumps({"rows":analysis_rows,"unit":"paired_case_id"}, indent=2), encoding="utf-8")
    h1 = {"AUROC_full": _h1(h1_cases, "auroc"), "AUPRC_full": _h1(h1_cases, "auprc")}; h3 = {"DELTA_FULL_CORE_AUROC": _h3(h3_cases, "auroc"), "DELTA_FULL_CORE_AUPRC": _h3(h3_cases, "auprc")}
    h1_ci = {m: _bootstrap(h1_cases, lambda xs, metric=m: _h1(xs, metric)) for m in ("auroc", "auprc")}; h3_ci = {m: _bootstrap(h3_cases, lambda xs, metric=m: _h3(xs, metric)) for m in ("auroc", "auprc")}
    (out / "recomputed_h1.json").write_text(json.dumps({**h1,"bootstrap":h1_ci}, indent=2), encoding="utf-8"); (out / "recomputed_h3.json").write_text(json.dumps({**h3,"bootstrap":h3_ci}, indent=2), encoding="utf-8")
    original = {name: _load_json(repo / SOURCE_ROOT_REL / "evaluation" / name) for name in ("h1_results.json", "h3_results.json")}
    original_h1_ci = original["h1_results.json"]["bootstrap"]; original_h3_ci = original["h3_results.json"]["bootstrap"]
    agreement = {"h1_point_estimates_match": h1 == {"AUROC_full": original["h1_results.json"]["AUROC_full"], "AUPRC_full": original["h1_results.json"]["AUPRC_full"]}, "h1_ci_match": h1_ci == original_h1_ci, "h3_point_estimates_match": h3 == {"DELTA_FULL_CORE_AUROC": original["h3_results.json"]["DELTA_FULL_CORE_AUROC"], "DELTA_FULL_CORE_AUPRC": original["h3_results.json"]["DELTA_FULL_CORE_AUPRC"]}, "h3_ci_match": h3_ci == original_h3_ci, "h1_ci": h1_ci, "h3_ci": h3_ci}
    (out / "original_vs_recomputed.json").write_text(json.dumps(agreement, indent=2), encoding="utf-8")
    manifest = {str(p.relative_to(root)).replace("\\", "/"): sha256_file(p) for p in root.rglob("*") if p.is_file()}
    (root / "repair_artifact_hashes.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"status":"PASS","preflight":preflight,"run_id":authorization["run_id"],"matched":23,"mismatched":0,"output_root":str(root),"agreement":agreement,"artifact_hashes":manifest}
