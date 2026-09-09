"""Pure Stage-A H1/H2/H3 and case-bootstrap implementation.

This module is inert until a separately authorized scientific run supplies
success-case score timelines. It never selects a generator or tunes a method.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable
import argparse
import hashlib
import sys
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from audiobookbench.evaluation.day6a_localization import auprc, auroc
from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import b1_scores, project_ground_truth_speaker
from audiobookbench.security.week3_detector_interface import FrozenWindowSpec, score_reference_free
from audiobookbench.security.week3_gt_verifier import verify_sample_first_gt
from audiobookbench.security.week3_authorization import validate_authorization_artifact, sha256_file
from audiobookbench.security.week3_pipeline import load_frozen_inputs, validate_preflight, canonical_run_root, FUTURE_AUTH_REL, _resolve_bound_path, _require_formal_identity
from audiobookbench.security.a2_sidecar_validator import validate_row as validate_sidecar_row
from audiobookbench.security.a2_waveform_gt_verifier import verify_row as verify_waveform_row
from audiobookbench.preprocessing.audio_io import load_audio
import csv
import json

BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260905
MIN_FINITE = 1900
S2 = SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000)

def validate_run_binding(rows: list[dict[str, Any]], run_id: str) -> None:
    mismatched = [row.get("paired_case_id", "UNKNOWN") for row in rows if row.get("run_id") != run_id]
    if mismatched:
        raise RuntimeError(f"evaluation run_id mismatch: {mismatched}")

def frozen_b1b_s2_score(backend: Any, suspect_waveform: np.ndarray, interval_row: dict[str, Any]):
    """Compatibility wrapper that keeps detector access behind one boundary."""
    scores, windows = score_reference_free(backend, suspect_waveform, 16000, FrozenWindowSpec())
    gt = project_ground_truth_speaker(windows, interval_row, 0.5)
    return scores, gt, windows

def _finite_metric(y: np.ndarray, s: np.ndarray, metric: str) -> float:
    mask = np.isfinite(s)
    if mask.sum() == 0 or np.unique(y[mask]).size < 2:
        return float("nan")
    return float(auroc(y[mask], s[mask]) if metric == "auroc" else auprc(y[mask], s[mask]))

def h1_full(case_scores: dict[str, np.ndarray], case_labels: dict[str, np.ndarray]) -> dict[str, float]:
    y = np.concatenate([case_labels[k] for k in sorted(case_scores)])
    s = np.concatenate([case_scores[k] for k in sorted(case_scores)])
    return {"AUROC_full": _finite_metric(y, s, "auroc"), "AUPRC_full": _finite_metric(y, s, "auprc")}

def h2_boundary_core(zone_scores: dict[str, dict[str, np.ndarray]]) -> dict[str, Any]:
    diffs: list[float] = []
    unavailable: dict[str, str] = {}
    case_means: dict[str, dict[str, float | None]] = {}
    for case_id in sorted(zone_scores):
        zones = zone_scores[case_id]
        core = zones.get("STRICT_CORE", np.array([])); boundary = zones.get("BOUNDARY_BLEND", np.array([]))
        outside = zones.get("OUTSIDE_CLEAN", np.array([]))
        core = core[np.isfinite(core)]; boundary = boundary[np.isfinite(boundary)]
        outside = outside[np.isfinite(outside)]
        case_means[case_id] = {
            "mean_score_core": float(np.mean(core)) if core.size else None,
            "mean_score_boundary": float(np.mean(boundary)) if boundary.size else None,
            "mean_score_outside": float(np.mean(outside)) if outside.size else None,
        }
        if core.size == 0 or boundary.size == 0:
            unavailable[case_id] = "empty_or_nonfinite_required_zone"
            continue
        diffs.append(float(np.mean(boundary) - np.mean(core)))
    return {"DELTA_BOUNDARY_CORE": float(np.mean(diffs)) if diffs else None,
            "computable_cases": len(diffs), "unavailable_cases": len(unavailable),
            "unavailable": unavailable, "unavailable_reason_counts": dict(Counter(unavailable.values())),
            "case_zone_means": case_means,
            "case_results": {
                case_id: {
                    **means,
                    "contrast_available": case_id not in unavailable,
                    "unavailable_reason": unavailable.get(case_id),
                    "DELTA_BOUNDARY_CORE": (means["mean_score_boundary"] - means["mean_score_core"])
                    if case_id not in unavailable else None,
                }
                for case_id, means in case_means.items()
            }}

def h3_full_core(case_scores: dict[str, np.ndarray], full_labels: dict[str, np.ndarray], core_labels: dict[str, np.ndarray]) -> dict[str, float]:
    def metric(labels: dict[str, np.ndarray], name: str) -> float:
        y = np.concatenate([labels[k] for k in sorted(case_scores)])
        s = np.concatenate([case_scores[k] for k in sorted(case_scores)])
        return _finite_metric(y, s, name)
    full_auc, core_auc = metric(full_labels, "auroc"), metric(core_labels, "auroc")
    full_pr, core_pr = metric(full_labels, "auprc"), metric(core_labels, "auprc")
    return {"DELTA_FULL_CORE_AUROC": full_auc - core_auc, "DELTA_FULL_CORE_AUPRC": full_pr - core_pr}

def case_bootstrap(values: Iterable[Any], statistic, *, n: int = BOOTSTRAP_N, seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    cases = list(values)
    if not cases:
        return {"requested_replicates": n, "finite_replicates": 0, "undefined_replicates": n,
                "undefined_reason_counts": {"empty_case_population": n}, "ci": "NOT_REPORTABLE"}
    rng = np.random.default_rng(seed)
    out: list[float] = []; reasons: Counter[str] = Counter()
    for _ in range(n):
        sample = [cases[i] for i in rng.integers(0, len(cases), size=len(cases))]
        try:
            value = float(statistic(sample))
            if not np.isfinite(value):
                raise ValueError("nonfinite_statistic")
            out.append(value)
        except Exception as exc:
            reasons[type(exc).__name__ + ":" + str(exc)] += 1
    result: dict[str, Any] = {"requested_replicates": n, "finite_replicates": len(out),
                              "undefined_replicates": n - len(out), "undefined_reason_counts": dict(reasons)}
    result["ci"] = [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))] if len(out) >= MIN_FINITE else "NOT_REPORTABLE"
    return result

def formal_case_bootstrap(values: Iterable[Any], statistic) -> dict[str, Any]:
    """Stage-A wrapper with N/seed/minimum finite locked to the protocol."""
    return case_bootstrap(values, statistic, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED)

def zone_timeline(gt_rows: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    """Persistable sample-first membership projection, independent of scores."""
    zones = {"FULL_ATTACK": [], "STRICT_CORE": [], "BOUNDARY_BLEND": [], "OUTSIDE_CLEAN": []}
    for row in gt_rows:
        zones["FULL_ATTACK"].append(bool(row["is_attack_window"]))
        zones["STRICT_CORE"].append(row.get("zone") == "core")
        zones["BOUNDARY_BLEND"].append(row.get("zone") == "boundary")
        zones["OUTSIDE_CLEAN"].append(row.get("zone") == "outside")
    return {key: np.asarray(value, dtype=bool) for key, value in zones.items()}

def load_successful_cases(root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Load only cases named by the authoritative final accounting table."""
    accounting = root / "accounting/cases.csv"
    sidecars = root / "sidecars/sidecars.jsonl"
    if not accounting.is_file() or not sidecars.is_file():
        raise RuntimeError("validated final accounting and sidecar index are required")
    cases = list(csv.DictReader(accounting.open(encoding="utf-8", newline="")))
    if len(cases) != 23 or len({r.get("paired_case_id") for r in cases}) != 23:
        raise RuntimeError("final accounting must retain exactly 23 planned cases")
    side_by_id = {}
    for line in sidecars.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line); side_by_id[row["paired_case_id"]] = row
    successful = []
    for row in cases:
        if row.get("status") == "SUCCESS":
            side = side_by_id.get(row["paired_case_id"])
            if side is None:
                raise RuntimeError(f"successful case lacks sidecar: {row['paired_case_id']}")
            successful.append(side)
        elif row.get("status") != "FAILED":
            raise RuntimeError("final accounting status must be SUCCESS or FAILED")
    failures = sum(row.get("status") == "FAILED" for row in cases)
    failure_classes = Counter(row.get("failure_class") or "unspecified" for row in cases if row.get("status") == "FAILED")
    return successful, {"planned_n": 23, "successful_generation_n": len(successful),
                       "failed_generation_n": failures, "failure_class_counts": dict(failure_classes)}

def _h1_stat(samples: list[tuple[np.ndarray, np.ndarray]], metric: str) -> float:
    scores = np.concatenate([x[0] for x in samples]); labels = np.concatenate([x[1] for x in samples])
    return _finite_metric(labels, scores, metric)

def _h3_stat(samples: list[tuple[np.ndarray, np.ndarray, np.ndarray]], metric: str) -> float:
    scores = np.concatenate([x[0] for x in samples]); full = np.concatenate([x[1] for x in samples]); core = np.concatenate([x[2] for x in samples])
    return _finite_metric(full, scores, metric) - _finite_metric(core, scores, metric)

def run_formal_evaluation(repo: Path, *, backend: Any | None = None) -> dict[str, Any]:
    """Canonical formal evaluation entrypoint; only repository auth is valid."""
    inputs = load_frozen_inputs(repo)
    authorization = validate_authorization_artifact(repo / FUTURE_AUTH_REL, inputs.source_paths)
    _require_formal_identity(authorization)
    missing = [key for key in ("run_id", "invocation_id", "output_root", "independent_review_sha256") if not authorization.get(key)]
    if missing:
        raise RuntimeError(f"formal authorization identity missing: {missing}")
    validate_preflight(repo)
    root = canonical_run_root(repo, str(authorization["run_id"]))
    if _resolve_bound_path(repo, str(authorization["output_root"])) != root:
        raise RuntimeError("authorization output namespace mismatch")
    if not root.is_dir():
        raise RuntimeError("authorized run namespace is missing")
    return _execute_evaluation(repo, inputs, authorization, backend=backend, root=root, test_only=False)

def run_test_fixture_evaluation(repo: Path, inputs: Any, *, backend: Any, output_root: Path) -> dict[str, Any]:
    """Explicit TEST_ONLY fixture entrypoint, separate from formal evaluation."""
    return _execute_evaluation(repo, inputs, {"artifact_sha256": "TEST_ONLY_FIXTURE"}, backend=backend, root=output_root, test_only=True)

def _execute_evaluation(repo: Path, inputs: Any, authorization: dict[str, Any], *, backend: Any | None = None, root: Path, test_only: bool) -> dict[str, Any]:
    root = root.resolve()
    successful, denominator = load_successful_cases(root)
    if not test_only:
        validate_run_binding(successful, str(authorization["run_id"]))
    if backend is None:
        from audiobookbench.temporal.day6b_embed import SpeakerBackend
        # Keep the project wrapper: the narrow detector boundary consumes
        # embed_windows(), while load() returns the underlying ECAPA encoder.
        backend = SpeakerBackend()
    h1_cases: list[tuple[np.ndarray, np.ndarray]] = []; h3_cases: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []; zones: dict[str, dict[str, np.ndarray]] = {}; score_manifest: list[dict[str, Any]] = []
    plan_map = {case["paired_case_id"]: {key: str(value) for key, value in case.items()} for case in inputs.cases}
    case_by_id = {case["paired_case_id"]: case for case in inputs.cases}
    for row in successful:
        waveform, sr = load_audio(Path(row["manipulated_audio_path"]), target_sr=16000)
        csv_row = {key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value) for key, value in row.items()}
        if row["paired_case_id"] in plan_map:
            validate_sidecar_row(csv_row, plan_map, official_smoke=False)
        verify_waveform_row(csv_row, case_by_id[row["paired_case_id"]]["clean_sequence_audio_path"])
        scores, windows = score_reference_free(backend, np.asarray(waveform, dtype=np.float32), sr, FrozenWindowSpec())
        intervals = {"attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])), "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])), "blend": (int(row["blend_in_start_sample"]), int(row["blend_out_end_sample"]))}
        gt_rows = project_ground_truth_speaker(windows, intervals, 0.5)
        verify_sample_first_gt(row, gt_rows)
        timeline = zone_timeline(gt_rows)
        full = np.asarray([bool(g["is_attack_window"]) for g in gt_rows]); core = np.asarray([bool(g["is_core_window"]) for g in gt_rows])
        h1_cases.append((scores, full)); h3_cases.append((scores, full, core))
        zones[row["paired_case_id"]] = {name: scores[mask] for name, mask in timeline.items() if name != "FULL_ATTACK"}
        score_manifest.append({"paired_case_id": row["paired_case_id"], "window_count": int(scores.size), "score_sha256": hashlib.sha256(scores.tobytes()).hexdigest().upper()})
    h1 = h1_full({str(i): x[0] for i, x in enumerate(h1_cases)}, {str(i): x[1] for i, x in enumerate(h1_cases)})
    h2 = h2_boundary_core(zones)
    h3 = h3_full_core({str(i): x[0] for i, x in enumerate(h3_cases)}, {str(i): x[1] for i, x in enumerate(h3_cases)}, {str(i): x[2] for i, x in enumerate(h3_cases)})
    h1_ci = {metric: formal_case_bootstrap(h1_cases, lambda xs, m=metric: _h1_stat(xs, m)) for metric in ("auroc", "auprc")}
    h3_ci = {metric: formal_case_bootstrap(h3_cases, lambda xs, m=metric: _h3_stat(xs, m)) for metric in ("auroc", "auprc")}
    available = []
    for value in zones.values():
        core_values, boundary_values = value.get("STRICT_CORE", np.array([])), value.get("BOUNDARY_BLEND", np.array([]))
        if np.isfinite(core_values).any() and np.isfinite(boundary_values).any():
            available.append(float(np.nanmean(boundary_values) - np.nanmean(core_values)))
    h2_ci = formal_case_bootstrap(available, lambda xs: float(np.mean(xs)))
    out = root / "evaluation"; out.mkdir(parents=True, exist_ok=True)
    case_table_hash = sha256_file(root / "accounting/cases.csv")
    score_payload = {"scores": score_manifest}
    (out / "score_manifest.json").write_text(json.dumps(score_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    provenance = {"authorization_sha256": authorization["artifact_sha256"],
                  "run_id": authorization.get("run_id", "TEST_ONLY_RUN"),
                  "invocation_id": authorization.get("invocation_id", "TEST_ONLY_INVOCATION"),
                  "independent_review_sha256": authorization.get("independent_review_sha256", "TEST_ONLY_FIXTURE"),
                  "review_evidence_sha256": sha256_file(inputs.source_paths["review_evidence"]),
                  "config_sha256": inputs.config_hash,
                  "environment_manifest_sha256": inputs.environment_hash,
                  "evaluator_sha256": sha256_file(Path(__file__)),
                  "runner_sha256": sha256_file(repo / "experiments/week3_stage_a_f5/run.py"),
                  "f5_source_identity_sha256": sha256_file(repo / "results/week3_stage_a_f5/readiness_evidence/f5_source_identity.json"),
                  "f5_local_source_manifest_sha256": sha256_file(repo / "results/week3_stage_a_f5/readiness_evidence/f5_source_manifest_local.json"),
                  "case_table_sha256": case_table_hash,
                  "score_manifest_sha256": sha256_file(out / "score_manifest.json")}
    outputs = {"analysis_population.json": {**denominator, **provenance, "case_ids": [r["paired_case_id"] for r in successful], "analysis_status": "TEST_ONLY" if test_only else "FORMAL"}, "h1_results.json": {**h1, "bootstrap": h1_ci, **provenance}, "h2_results.json": {**h2, "planned_n": denominator["planned_n"], "successful_generation_n": denominator["successful_generation_n"], "H2_available_n": len(available), "H2_unavailable_n": len(successful) - len(available), "bootstrap": h2_ci, **provenance}, "h3_results.json": {**h3, "bootstrap": h3_ci, **provenance}, "bootstrap_summary.json": {"H1": h1_ci, "H2": h2_ci, "H3": h3_ci, **provenance}}
    for name, value in outputs.items(): (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    outputs["score_manifest.json"] = score_payload
    hashes = {name: sha256_file(out / name) for name in outputs}; (out / "scientific_output_hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    return {"status": "PASS", **denominator, "output_dir": str(out), "hashes": hashes}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-a", action="store_true")
    args = parser.parse_args()
    if not args.stage_a:
        raise SystemExit("select --stage-a; formal evaluation requires the canonical authorization artifact")
    result = run_formal_evaluation(Path(__file__).resolve().parents[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    main()
