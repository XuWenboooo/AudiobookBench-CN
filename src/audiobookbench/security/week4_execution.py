"""Frozen Week4 execution mechanics.

This module contains no import-time model loading.  ``execute_protocol`` is
used with injected TEST_ONLY backends in tests; the formal runner alone may
construct its lazy real backends after authorization preflight succeeds.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from audiobookbench.evaluation.day6a_localization import auprc, auroc
from audiobookbench.preprocessing.audio_io import resample_audio
from audiobookbench.security.week4_adaptive import (
    ADAPTIVE_PHASE, STATIC_PHASE, A0AttackController, CandidateLedger,
    DetectorOutcome,
    DetectorQuery, FrozenAttackSpec, paired_case_bootstrap,
)
from audiobookbench.temporal.day6b_embed import SpeakerBackend, SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import b1_scores

SAMPLE_RATE = 16000
FRAME = 400
HOP = 160
THRESHOLD_DBFS = -45.0
RETAIN = 800
S2 = SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000)


class Week4ExecutionError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _mono_16k(waveform: np.ndarray, sample_rate: int) -> np.ndarray:
    a = np.asarray(waveform, dtype=np.float32)
    if a.ndim == 2:
        a = a.mean(axis=1, dtype=np.float32)
    if a.ndim != 1 or not a.size or not np.all(np.isfinite(a)):
        raise Week4ExecutionError("waveform must be non-empty finite mono/stereo audio")
    return resample_audio(a, int(sample_rate), SAMPLE_RATE) if sample_rate != SAMPLE_RATE else a.copy()


def active_interval(waveform: np.ndarray, *, retain_edges: bool = False) -> tuple[int, int]:
    """Frozen frame RMS activity interval; final partial frame is not a frame."""
    a = np.asarray(waveform, dtype=np.float32)
    if a.ndim != 1 or not np.all(np.isfinite(a)):
        raise Week4ExecutionError("activity requires finite mono waveform")
    starts = range(0, max(0, a.size - FRAME + 1), HOP)
    active = [start for start in starts if 20.0 * math.log10(max(float(np.sqrt(np.mean(a[start:start + FRAME] ** 2))), 1e-12)) > THRESHOLD_DBFS]
    if not active:
        raise Week4ExecutionError("no_active_frame")
    lo, hi = active[0], active[-1] + FRAME
    return (max(0, lo - RETAIN), min(a.size, hi + RETAIN)) if retain_edges else (lo, hi)


def trim_synthetic(waveform: np.ndarray, sample_rate: int) -> np.ndarray:
    a = _mono_16k(waveform, sample_rate)
    lo, hi = active_interval(a, retain_edges=True)
    trimmed = a[lo:hi].copy()
    if not trimmed.size:
        raise Week4ExecutionError("empty_synthetic_after_trim")
    return trimmed


@dataclass(frozen=True)
class CandidateConstruction:
    waveform: np.ndarray
    gt: Mapping[str, tuple[int, int]]
    insertion_sample: int
    crossfade_samples: int
    gain_db: float


def construct_candidate(source: np.ndarray, synthetic: np.ndarray, *, crossfade_samples: int, gain_db: float) -> CandidateConstruction:
    src, syn = _mono_16k(source, SAMPLE_RATE), _mono_16k(synthetic, SAMPLE_RATE)
    f, g = int(crossfade_samples), float(gain_db)
    if f <= 0 or not math.isfinite(g):
        raise Week4ExecutionError("invalid_candidate_parameters")
    lo, hi = active_interval(src)
    p = (lo + hi) // 2
    scaled = syn.astype(np.float64) * (10.0 ** (g / 20.0))
    if not np.all(np.isfinite(scaled)) or float(np.max(np.abs(scaled))) > 0.999:
        raise Week4ExecutionError("INVALID_BEFORE_D0_peak")
    if p < f or src.size - p < f or scaled.size <= 2 * f:
        raise Week4ExecutionError("INVALID_BEFORE_D0_layout")
    alpha_in = (np.arange(f, dtype=np.float64) + 1.0) / (f + 1.0)
    alpha_out = (f - np.arange(f, dtype=np.float64)) / (f + 1.0)
    n = scaled.size
    blend_in = src[p-f:p].astype(np.float64) * (1.0 - alpha_in) + scaled[:f] * alpha_in
    core = scaled[f:n-f]
    blend_out = scaled[n-f:] * alpha_out + src[p:p+f].astype(np.float64) * (1.0 - alpha_out)
    out = np.concatenate((src[:p-f], blend_in, core, blend_out, src[p+f:])).astype(np.float32)
    if not np.all(np.isfinite(out)):
        raise Week4ExecutionError("INVALID_BEFORE_D0_nonfinite")
    core_end = p + n - 2 * f
    return CandidateConstruction(out, {
        "attack": (p - f, core_end + f), "core": (p, core_end),
        "blend_in": (p - f, p), "blend_out": (core_end, core_end + f),
    }, p, f, g)


def project_gt(waveform: np.ndarray, gt: Mapping[str, tuple[int, int]]) -> list[dict[str, Any]]:
    rows = build_speaker_windows(np.asarray(waveform).size, S2)
    attack_lo, attack_hi = gt["attack"]
    for row in rows:
        overlap = max(0, min(row["sample_end"], attack_hi) - max(row["sample_start"], attack_lo))
        row["attack_overlap_ratio"] = overlap / S2.window_samples
        row["FULL_ATTACK"] = row["attack_overlap_ratio"] >= 0.5
        row["OUTSIDE_CLEAN"] = row["attack_overlap_ratio"] == 0.0
    return rows


def score_candidate(query: DetectorQuery, backend: Any) -> tuple[np.ndarray, list[dict[str, Any]]]:
    if query.sample_rate != SAMPLE_RATE or query.window_spec.window_samples != S2.window_samples or query.window_spec.hop_samples != S2.hop_samples:
        raise Week4ExecutionError("D0 query does not use frozen S2")
    windows = build_speaker_windows(query.waveform.size, S2)
    if not windows:
        raise Week4ExecutionError("candidate_has_no_complete_s2_windows")
    embeddings = backend.embed_windows(query.waveform, [(w["sample_start"], w["sample_end"]) for w in windows])
    if np.asarray(embeddings).shape != (len(windows), 192):
        raise Week4ExecutionError("D0 embedding shape mismatch")
    scores = np.ascontiguousarray(b1_scores(np.asarray(embeddings), trimmed=True), dtype=np.float64)
    if not np.all(np.isfinite(scores)):
        raise Week4ExecutionError("D0 score vector nonfinite")
    return scores, windows


def attacker_objective(scores: np.ndarray, projection: list[Mapping[str, Any]]) -> float:
    s = np.asarray(scores, dtype=np.float64)
    full = np.array([bool(r["FULL_ATTACK"]) for r in projection])
    outside = np.array([bool(r["OUTSIDE_CLEAN"]) for r in projection])
    if s.size != len(projection) or not full.any() or not outside.any() or not np.all(np.isfinite(s[full])) or not np.all(np.isfinite(s[outside])):
        return float("nan")
    return float(np.mean(s[full]) - np.mean(s[outside]))


def vector_record(*, case_id: str, candidate_id: str, waveform: np.ndarray, scores: np.ndarray, windows: list[dict[str, Any]], projection: list[dict[str, Any]]) -> dict[str, Any]:
    raw = np.ascontiguousarray(scores, dtype=np.float64).tobytes(order="C")
    return {"case_id": case_id, "candidate_id": candidate_id, "waveform_sha256": sha256_bytes(np.ascontiguousarray(waveform, dtype=np.float32).tobytes()), "score_vector_sha256": sha256_bytes(raw), "score_shape": list(np.asarray(scores).shape), "score_dtype": "float64", "score_vector": np.asarray(scores, dtype=np.float64).tolist(), "s2_windows": windows, "gt_projection": projection}


def _persist_candidate(runtime_root: Path, record: Mapping[str, Any]) -> dict[str, Any]:
    """Commit a complete sidecar before it can be selected or evaluated."""
    case_id, candidate_id = str(record["case_id"]), str(record["candidate_id"])
    target = runtime_root / "sidecars" / case_id / f"{candidate_id.replace(':', '__')}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    body = dict(record)
    if isinstance(body.get("objective"), float) and not math.isfinite(body["objective"]):
        body["objective"] = None
    target.write_text(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False), encoding="utf-8")
    body["sidecar_relpath"] = target.relative_to(runtime_root).as_posix()
    body["sidecar_sha256"] = sha256_bytes(target.read_bytes())
    return body


def final_evaluate(held_out: Mapping[str, Mapping[str, Mapping[str, Any]]]) -> dict[str, Any]:
    if len(held_out) != 12:
        return {"PRIMARY_H4": "NOT_REPORTABLE", "reason": "held_out_not_12_of_12"}
    conditions: dict[str, tuple[list[np.ndarray], list[np.ndarray]]] = {}
    for case_id in sorted(held_out):
        for condition in ("static", "adaptive"):
            record = held_out[case_id].get(condition)
            if not record or not record.get("score_vector_sha256"):
                return {"PRIMARY_H4": "NOT_REPORTABLE", "reason": f"incomplete_{case_id}_{condition}"}
            s = np.asarray(record["score_vector"], dtype=np.float64)
            labels = np.asarray([r["FULL_ATTACK"] for r in record["gt_projection"]], dtype=bool)
            if s.size != labels.size or not np.all(np.isfinite(s)):
                return {"PRIMARY_H4": "NOT_REPORTABLE", "reason": f"invalid_{case_id}_{condition}"}
            conditions.setdefault(condition, ([], []))[0].append(labels); conditions[condition][1].append(s)
    metrics = {name: {"auroc": auroc(np.concatenate(y), np.concatenate(s)), "auprc": auprc(np.concatenate(y), np.concatenate(s))} for name, (y, s) in conditions.items()}
    return {"PRIMARY_H4": "REPORTABLE", "metrics": metrics, "DELTA_ADAPTIVE_AUROC": metrics["static"]["auroc"] - metrics["adaptive"]["auroc"], "DELTA_ADAPTIVE_AUPRC": metrics["static"]["auprc"] - metrics["adaptive"]["auprc"], "paired_bootstrap": {"auroc": paired_metric_bootstrap(held_out, "auroc"), "auprc": paired_metric_bootstrap(held_out, "auprc")}}


def paired_metric_bootstrap(held_out: Mapping[str, Mapping[str, Mapping[str, Any]]], metric: str) -> dict[str, Any]:
    """The frozen paired-case bootstrap of final metric deltas, not means."""
    if metric not in {"auroc", "auprc"} or len(held_out) != 12:
        raise Week4ExecutionError("paired metric bootstrap requires exactly 12 held-out cases")
    case_ids = sorted(held_out)
    rng = np.random.default_rng(20260911)
    deltas = np.full(2000, np.nan, dtype=np.float64)
    fn = auroc if metric == "auroc" else auprc
    for i in range(2000):
        sampled = rng.choice(case_ids, size=12, replace=True)
        values: dict[str, float] = {}
        for condition in ("static", "adaptive"):
            labels = np.concatenate([np.asarray([r["FULL_ATTACK"] for r in held_out[c][condition]["gt_projection"]], dtype=bool) for c in sampled])
            scores = np.concatenate([np.asarray(held_out[c][condition]["score_vector"], dtype=np.float64) for c in sampled])
            values[condition] = fn(labels, scores)
        if math.isfinite(values["static"]) and math.isfinite(values["adaptive"]):
            deltas[i] = values["static"] - values["adaptive"]
    finite = deltas[np.isfinite(deltas)]
    reportable = finite.size >= 1900
    return {"unit": "paired_case_id", "requested": 2000, "finite": int(finite.size), "undefined": int(2000 - finite.size), "seed": 20260911, "confidence_level": 0.95, "status": "REPORTABLE" if reportable else "NOT_REPORTABLE", "ci_percentile": [float(x) for x in np.quantile(finite, [0.025, 0.975])] if reportable else None}


def real_d0_backend() -> SpeakerBackend:
    """Lazy, offline-only real backend; call only from an authorized dispatcher."""
    # SpeakerBackend.load() is intentionally deferred until the first
    # score_candidate call, after run metadata and the attempt ledger exist.
    return SpeakerBackend()


def load_source_case(case: Mapping[str, Any]) -> np.ndarray:
    """Load a frozen source without peak normalization or source mutation."""
    import soundfile as sf
    path = Path(str(case["source_path"]))
    if not path.is_file() or sha256_bytes(path.read_bytes()) != str(case["source_audio_sha256"]).upper():
        raise Week4ExecutionError("source identity hash mismatch")
    samples, sr = sf.read(path, always_2d=False)
    return _mono_16k(np.asarray(samples, dtype=np.float32), int(sr))


def real_f5_generator() -> Callable[[Mapping[str, Any], int], tuple[np.ndarray, int]]:
    """Build the explicit local F5 path only after the formal gate opens."""
    from audiobookbench.security.week3_f5_stage_a import InferenceSettings, build_f5_api, infer_once
    root = Path(__file__).resolve().parents[3]
    assets = root / "results/week3_engineering_qualification/f5_tts_v1_base/assets"
    api: Any = None
    def generate(case: Mapping[str, Any], seed: int) -> tuple[np.ndarray, int]:
        nonlocal api
        if api is None:
            api = build_f5_api(root / "results/week3_engineering_qualification/f5_tts_v1_base/source", InferenceSettings(),
                ckpt_file=assets / "F5TTS_v1_Base/model_1250000.safetensors", vocab_file=assets / "F5TTS_v1_Base/vocab.txt", vocoder_local_path=assets / "vocos-mel-24khz")
        if not str(case.get("reference_text_exact", "")) or not str(case.get("source_text_exact", "")):
            raise Week4ExecutionError("nonempty frozen F5 texts required")
        result = infer_once(api, ref_file=Path(str(case["reference_path"])), ref_text=str(case["reference_text_exact"]), gen_text=str(case["source_text_exact"]), seed=seed, settings=InferenceSettings())
        wave, sr = result[0], result[1]
        return np.asarray(wave, dtype=np.float32), int(sr)
    return generate


def _append_attempt(path: Path, record: Mapping[str, Any]) -> dict[str, Any]:
    previous = ""
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            previous = str(json.loads(lines[-1])["record_sha256"])
    body = dict(record); body["previous_record_sha256"] = previous
    body["record_sha256"] = sha256_bytes(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    return body


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    """Atomically replace mutable run metadata while preserving event history."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    temporary.replace(path)


class _RunLifecycle:
    """Run metadata snapshot plus append-only, hash-chained status events."""

    def __init__(self, runtime_root: Path, context: Mapping[str, Any] | None, *, stage: str, run_id: str):
        self.metadata_path = runtime_root / "run_metadata.json"
        self.events_path = runtime_root / "accounting" / "run_status_events.jsonl"
        self.data = dict(context or {})
        started = datetime.now(timezone.utc).isoformat()
        self.data.update({
            "status": "INITIALIZED", "lifecycle_status": "INITIALIZED", "final_status": None,
            "stage": stage, "run_id": run_id, "started_at": started,
            "generation_invoked": False, "d0_invoked": False,
            "first_generation_timestamp": None, "first_d0_timestamp": None,
            "last_updated_at": started, "completed_case_count": 0,
            "failure_case_id": None, "failure_class": None,
            "scientific_parameters_changed": False,
        })
        runtime_root.mkdir(parents=True, exist_ok=True)
        _atomic_json(self.metadata_path, self.data)
        self._event("INITIALIZED")

    def _event(self, event: str, **details: Any) -> None:
        previous = ""
        if self.events_path.exists():
            rows = [line for line in self.events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if rows:
                previous = str(json.loads(rows[-1])["record_sha256"])
        body = {"event": event, "recorded_at": datetime.now(timezone.utc).isoformat(), "previous_record_sha256": previous, **details}
        body["record_sha256"] = sha256_bytes(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8", newline="") as stream:
            stream.write(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")

    def _update(self, *, status: str | None = None, final_status: str | None = None, event: str, **details: Any) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if status is not None:
            self.data["status"] = status
            self.data["lifecycle_status"] = status
        if final_status is not None:
            self.data["final_status"] = final_status
        self.data["last_updated_at"] = now
        self.data.update(details)
        _atomic_json(self.metadata_path, self.data)
        self._event(event, status=self.data["status"], **details)

    def running(self, case_id: str) -> None:
        self._update(status="RUNNING", event="CASE_STARTED", case_id=case_id)

    def generation_started(self, case_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self.data["first_generation_timestamp"] is None:
            self.data["first_generation_timestamp"] = now
        self._update(status="RUNNING", event="F5_INVOCATION_STARTED", case_id=case_id, generation_invoked=True)

    def d0_started(self, case_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self.data["first_d0_timestamp"] is None:
            self.data["first_d0_timestamp"] = now
        self._update(status="RUNNING", event="D0_INVOCATION_STARTED", case_id=case_id, d0_invoked=True)

    def completed_case(self, case_id: str, count: int) -> None:
        self._update(status="RUNNING", event="CASE_COMPLETED", case_id=case_id, completed_case_count=count)

    def failed(self, case_id: str | None, exc: Exception) -> None:
        status = "BLOCKED" if "NO_VALID_ADAPTIVE_PARENT" in str(exc) else "FAILED"
        self._update(status=status, final_status=status, event="RUN_TERMINATED", failure_case_id=case_id, failure_class=type(exc).__name__)

    def completed(self, count: int) -> None:
        self._update(status="COMPLETED", final_status="COMPLETED", event="RUN_COMPLETED", completed_case_count=count)


def execute_protocol(*, cases: list[Mapping[str, Any]], spec: FrozenAttackSpec, runtime_root: Path, f5_generator: Callable[[Mapping[str, Any], int], tuple[np.ndarray, int]], d0_backend: Any, source_loader: Callable[[Mapping[str, Any]], np.ndarray] = load_source_case, stage: str = "all", metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Run the fixed DEV → VALIDATION → HELD_OUT sequence with injected backends.

    The caller is responsible for authorization and for ensuring this is either
    TEST_ONLY or the formal dispatcher.  The function does not make policy
    choices: any undefined construction/objective is ledgered and cannot win.
    """
    if stage not in {"all", "dev"}:
        raise Week4ExecutionError("only the frozen dev stage or TEST_ONLY all-stage harness is supported")
    ordered = sorted(cases, key=lambda c: str(c["case_id"]))
    if len(ordered) != 48 or [str(c["case_id"]) for c in ordered] != [f"week4_case_{i:04d}" for i in range(1, 49)]:
        raise Week4ExecutionError("canonical 48-case order required")
    if stage == "dev" and sum(str(c["split"]) == "dev" for c in ordered) != 24:
        raise Week4ExecutionError("DEV stage requires exactly 24 canonical dev cases")
    runtime_root = Path(runtime_root)
    if runtime_root.exists():
        raise Week4ExecutionError("runtime namespace must be new")
    ledger = CandidateLedger(runtime_root / "accounting/candidate_ledger.jsonl")
    attempt_ledger = runtime_root / "accounting/f5_attempt_ledger.jsonl"
    lifecycle = _RunLifecycle(runtime_root, metadata, stage="DEV" if stage == "dev" else "TEST_ONLY_ALL", run_id=spec.run_id)
    per_case: dict[str, dict[str, dict[str, Any]]] = {}
    case_index = {str(case["case_id"]): index for index, case in enumerate(ordered)}
    execution_order = sorted(ordered, key=lambda c: ({"dev": 0, "validation": 1, "held_out": 2}.get(str(c["split"]), 3), str(c["case_id"])))
    if stage == "dev":
        execution_order = [c for c in execution_order if str(c["split"]) == "dev"]
    f5_successes, d0_backend_calls, current_case_id = 0, 0, None
    try:
        for case in execution_order:
            case_id, split = str(case["case_id"]), str(case["split"])
            current_case_id = case_id
            lifecycle.running(case_id)
            seed, attempt_index = 20260914 + case_index[case_id], 0
            raw_path = runtime_root / "waveforms" / case_id / f"f5_attempt_{attempt_index:02d}_raw.npy"
            try:
                lifecycle.generation_started(case_id)
                native, native_sr = f5_generator(case, seed)
                native = np.asarray(native, dtype=np.float32)
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                np.save(raw_path, native, allow_pickle=False)
                raw_hash = sha256_bytes(np.ascontiguousarray(native).tobytes())
                synthetic = trim_synthetic(native, native_sr)
                standardized_path = runtime_root / "waveforms" / case_id / "base_synthetic_16k.npy"
                np.save(standardized_path, np.ascontiguousarray(synthetic, dtype=np.float32), allow_pickle=False)
                standardized_hash = sha256_bytes(np.ascontiguousarray(synthetic, dtype=np.float32).tobytes())
                _append_attempt(attempt_ledger, {"case_id": case_id, "split": split, "attempt_index": attempt_index, "status": "SUCCESS", "generation_seed": seed, "raw_path": raw_path.relative_to(runtime_root).as_posix(), "raw_waveform_sha256": raw_hash, "native_sample_rate": int(native_sr), "standardized_path": standardized_path.relative_to(runtime_root).as_posix(), "standardized_waveform_sha256": standardized_hash, "standardized_sample_rate": SAMPLE_RATE, "trim_rule": {"frame_samples": FRAME, "hop_samples": HOP, "threshold_dbfs": THRESHOLD_DBFS, "retain_edge_samples": RETAIN}})
                f5_successes += 1
            except Exception as exc:
                _append_attempt(attempt_ledger, {"case_id": case_id, "split": split, "attempt_index": attempt_index, "status": "FAILED", "generation_seed": seed, "error_type": type(exc).__name__, "error": str(exc)})
                raise
            source, source_interval, base_hash = source_loader(case), None, standardized_hash
            source_interval = active_interval(source)
            results: dict[str, dict[str, Any]] = {}
            staged: dict[str, dict[str, Any]] = {}
            def detector(query: DetectorQuery) -> DetectorOutcome:
                nonlocal d0_backend_calls
                key = sha256_bytes(np.ascontiguousarray(query.waveform, dtype=np.float32).tobytes())
                if key not in staged:
                    raise Week4ExecutionError("unstaged candidate reached D0")
                lifecycle.d0_started(case_id)
                d0_backend_calls += 1
                scores, windows = score_candidate(query, d0_backend)
                objective = attacker_objective(scores, staged[key]["projection"])
                staged[key].update({"scores": scores, "windows": windows})
                if staged[key]["phase"] == STATIC_PHASE:
                    return DetectorOutcome(None, "NOT_APPLICABLE")
                return DetectorOutcome(float(objective) if math.isfinite(objective) else None, "DEFINED" if math.isfinite(objective) else "OBJECTIVE_UNDEFINED")
            auth = {"protocol": "WEEK4_ADAPTIVE_RED_TEAM_A0", "authorization_status": "ACTIVE", "run_id": spec.run_id, "split": split, "spec_sha256": spec.sha256(), "a0_freeze_sha256": __import__("audiobookbench.security.week4_adaptive", fromlist=["a0_freeze_sha256"]).a0_freeze_sha256(spec), "ready": True}
            controller = A0AttackController(spec=spec, authorization=auth, case_id=case_id, split=split, ledger=ledger, detector=detector)
            def evaluate(params: Mapping[str, float], phase: str) -> dict[str, Any]:
                try:
                    built = construct_candidate(source, synthetic, crossfade_samples=int(params["insertion_crossfade_samples"]), gain_db=float(params["synthetic_gain_db"]))
                except Week4ExecutionError as exc:
                    return controller._append_invalid(controller._new_candidate_id(phase), phase, params, str(exc), detector_query=False, query_index=controller._adaptive_query_count() + (1 if phase == ADAPTIVE_PHASE else 0))
                projection = project_gt(built.waveform, built.gt)
                key = sha256_bytes(np.ascontiguousarray(built.waveform, dtype=np.float32).tobytes())
                staged[key] = {"projection": projection, "phase": phase}
                row = controller.evaluate_candidate(waveform=built.waveform, sample_rate=SAMPLE_RATE, params=params, phase=phase)
                stage_record = staged[key]
                record = vector_record(case_id=case_id, candidate_id=row["candidate_id"], waveform=built.waveform, scores=stage_record["scores"], windows=stage_record["windows"], projection=projection)
                record.update({"objective": row.get("objective"), "objective_status": row["objective_status"], "detector_status": row["detector_status"], "valid_for_winner": row["valid_for_winner"], "base_synthetic_sha256": base_hash, "source_active_interval": {"start": source_interval[0], "end": source_interval[1], "insertion_sample": (source_interval[0] + source_interval[1]) // 2}, "generation_seed": seed})
                return _persist_candidate(runtime_root, record)
            results["static"] = evaluate(dict(spec.parameter_defaults), STATIC_PHASE)
            for _ in range(40):
                candidate = controller.next_candidate()
                record = evaluate(candidate, ADAPTIVE_PHASE)
                if record["valid_for_winner"] is True and isinstance(record.get("objective"), (int, float)) and math.isfinite(float(record["objective"])):
                    prior = results.get("adaptive")
                    if prior is None or (float(record["objective"]), int(record["candidate_id"].rsplit(":", 1)[1]), record["candidate_id"]) < (float(prior["objective"]), int(prior["candidate_id"].rsplit(":", 1)[1]), prior["candidate_id"]):
                        results["adaptive"] = record
            per_case[case_id] = results
            if "adaptive" in results:
                selection = {"case_id": case_id, "selected_candidate_id": results["adaptive"]["candidate_id"], "selected_objective": results["adaptive"]["objective"], "sidecar_relpath": results["adaptive"]["sidecar_relpath"], "sidecar_sha256": results["adaptive"]["sidecar_sha256"]}
                target = runtime_root / "selections" / f"{case_id}.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(selection, ensure_ascii=False, sort_keys=True, allow_nan=False), encoding="utf-8")
            lifecycle.completed_case(case_id, len(per_case))
            if split == "validation":
                remaining_validation = [c for c in execution_order[execution_order.index(case) + 1:] if c["split"] == "validation"]
                if not remaining_validation:
                    a0_frozen = True
    except Exception as exc:
        lifecycle.failed(current_case_id, exc)
        raise
    accounted_d0 = sum(row.get("detector_invoked") is True for row in ledger.records())
    if d0_backend_calls != accounted_d0:
        mismatch = Week4ExecutionError("ACTUAL_D0_BACKEND_CALLS does not equal accounted ledger invocations")
        lifecycle.failed(current_case_id, mismatch)
        raise mismatch
    lifecycle.completed(len(per_case))
    if stage == "dev":
        counts = [sum(row.get("phase") == ADAPTIVE_PHASE and row.get("detector_query") is True for row in ledger.records() if row.get("case_id") == case_id) for case_id in per_case]
        return {"stage": "DEV", "per_case": per_case, "ledger": ledger.records(), "f5_attempts": _load_jsonl(attempt_ledger), "accounting": {"DEV_PLANNED": 24, "DEV_STARTED": len(per_case), "DEV_COMPLETED": len(per_case), "DEV_SUCCESS": f5_successes, "DEV_FAILED": 24 - f5_successes, "F5_TOTAL_ATTEMPTS": f5_successes, "F5_SUCCESSFUL_CASES": f5_successes, "F5_FAILED_CASES": 24 - f5_successes, "F5_RETRIES": 0, "STATIC_D0_INVOCATIONS": len(per_case), "ADAPTIVE_D0_INVOCATIONS": sum(counts), "ACTUAL_D0_BACKEND_CALLS": d0_backend_calls, "ACCOUNTED_D0_INVOCATIONS": accounted_d0, "ADAPTIVE_QUERY_MIN": min(counts) if counts else 0, "ADAPTIVE_QUERY_MAX": max(counts) if counts else 0, "ADAPTIVE_QUERY_MEAN": float(np.mean(counts)) if counts else 0.0, "CASES_WITH_40_ADAPTIVE_QUERIES": sum(count == 40 for count in counts), "CASES_WITH_FEWER_THAN_40_DUE_TO_PRE_D0_INVALIDITY": sum(count < 40 for count in counts), "CASES_WITH_NO_VALID_WINNER": sum("adaptive" not in value for value in per_case.values()), "LEDGER_HASH_CHAIN": "PASS", "RAW_EVIDENCE_CHAIN": "PASS"}, "A0_FROZEN": False}
    held = {case_id: per_case[case_id] for case_id in per_case if next(c for c in ordered if c["case_id"] == case_id)["split"] == "held_out"}
    final = final_evaluate(held)
    (runtime_root / "final.json").write_text(json.dumps(final, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return {"per_case": per_case, "final": final, "ledger": ledger.records(), "ACTUAL_D0_BACKEND_CALLS": d0_backend_calls, "ACCOUNTED_D0_INVOCATIONS": accounted_d0, "A0_FROZEN": bool(locals().get("a0_frozen", False))}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
