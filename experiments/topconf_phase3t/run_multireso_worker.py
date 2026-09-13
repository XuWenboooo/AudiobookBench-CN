"""Authorized MultiResoModel-Simple x PartialEdit E1 raw-output worker.

This worker is intentionally not an evaluator: it preserves native outputs and
engineering accounting only.  It never reads target spans/labels or computes
scientific metrics.  Paths and identities are frozen by the Phase3T
authorization; change them only in a new authorized invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch
import torchaudio


AUTHORIZATION_ID = "P3T-2026-09-13-01"
BASE_COMMIT = "ee8d3a157dd329116e5ea8607a14446f90f26e8d"
MODEL_ID = "MultiResoModel-Simple"
MODEL_REPOSITORY_COMMIT = "0f69db3a2d654de47822d951fe6ad256bbaac9ba"
CHECKPOINT_SHA256 = "0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32"
CHECKPOINT_PATH = Path("F:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/MultiResoModel-Simple-schannel/materialized/baseline-ps-e55/exp/baseline/55.pth")
MODEL_REPO = Path("F:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/MultiResoModel-Simple-schannel")
DATASET_CSV = Path("F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/PartialEdit_E1E2.csv")
AUDIO_ROOT = Path("F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/materialized") / "E1"
DATASET_CSV_SHA256 = "ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC"
UNITS = (0.02, 0.04, 0.08, 0.16, 0.32, 0.64)
SAMPLE_RATE = 16000
EXPECTED_CASES = 42471
INVOCATION_ID = "PHASE3T_MRM_FULL_E1_001"
NAMESPACE = Path("results/topconf_phase3t/multireso_worker_01")
RAW_JSONL = NAMESPACE / "multireso_raw_v1.jsonl"
LEDGER_JSONL = NAMESPACE / "multireso_case_ledger_v1.jsonl"
RETRY_JSONL = NAMESPACE / "multireso_retry_ledger_v1.jsonl"
RUN_MANIFEST = NAMESPACE / "MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def read_case_order() -> list[dict[str, Any]]:
    if sha256_file(DATASET_CSV) != DATASET_CSV_SHA256:
        raise RuntimeError("DATASET_CSV_SHA256 mismatch")
    rows: list[dict[str, Any]] = []
    with DATASET_CSV.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            # Deliberately consume only the audio-path field.  The remaining
            # CSV fields are GT and are not parsed or stored by this worker.
            relative = line.rstrip("\r\n").split(",", 1)[0]
            if not relative.startswith("E1/"):
                continue
            path = AUDIO_ROOT / relative.removeprefix("E1/")
            rows.append({"case_id": relative.removesuffix(".wav"), "audio_path": path, "csv_line": line_number})
    if len(rows) != EXPECTED_CASES:
        raise RuntimeError(f"expected {EXPECTED_CASES} E1 cases, got {len(rows)}")
    if len({row["case_id"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate case IDs in frozen canonical order")
    return rows


def _load_model(device: torch.device):
    sys.path.insert(0, str(MODEL_REPO))
    from modules.multiresomodel import MultiResoModel  # type: ignore

    ssl_path = str(MODEL_REPO / "pretrained/w2v_large_lv_fsh_swbd_cv_fixed.pt")
    model = MultiResoModel(
        num_scales=6, include_utt=True, use_mask=True, ssl_path=ssl_path,
        ssl_dim=1024, ssl_tuning=True, device=str(device),
    ).to(device)
    # Stage on CPU so checkpoint loading cannot transiently duplicate the
    # multi-gigabyte SSL/model weights in the 8 GiB worker GPU.
    state = torch.load(str(CHECKPOINT_PATH), map_location="cpu")
    model.load_state_dict(state["modules"]["model"], strict=True)
    model.eval()
    return model


def preflight() -> int:
    """One deterministic technical check; no artifact or metric is produced."""
    case = read_case_order()[0]
    waveform, samples, _ = _load_audio(case)
    model = _load_model(torch.device("cuda"))
    with torch.inference_mode():
        logits, _ = model(_padded([waveform]).cuda())
    native = _native_outputs(logits, [samples])[0]
    if len(native) != 6 or not all(torch.isfinite(torch.tensor([score for item in scale["temporal_scores"] for score in (item["class_0"], item["class_1"])] )).all() for scale in native):
        raise RuntimeError("technical preflight failed")
    print(json.dumps({"preflight": "PASS", "case_id": case["case_id"], "scales": 6, "scientific_metrics_computed": 0, "gt_accessed": "NO"}, sort_keys=True))
    return 0


def _load_audio(row: dict[str, Any]) -> tuple[torch.Tensor, int, str]:
    path = row["audio_path"]
    if not path.is_file():
        raise FileNotFoundError(str(path))
    waveform, sample_rate = torchaudio.load(str(path))
    if sample_rate != SAMPLE_RATE or waveform.ndim != 2 or waveform.shape[0] != 1:
        raise ValueError("audio input contract violation")
    if waveform.shape[-1] == 0:
        raise ValueError("empty waveform")
    return waveform, int(waveform.shape[-1]), sha256_file(path)


def _padded(waveforms: list[torch.Tensor]) -> torch.Tensor:
    target = max(max(int(item.shape[-1]), int(0.645 * SAMPLE_RATE)) for item in waveforms) + int(0.005 * SAMPLE_RATE)
    return torch.cat([torch.nn.functional.pad(item, (0, target - item.shape[-1])) for item in waveforms], dim=0)


def _native_outputs(logits: list[torch.Tensor], durations: list[int]) -> list[list[dict[str, Any]]]:
    if len(logits) < 6:
        raise ValueError("fewer than six native temporal scales")
    output: list[list[dict[str, Any]]] = []
    for batch_index, samples in enumerate(durations):
        per_case: list[dict[str, Any]] = []
        for scale, unit in enumerate(UNITS):
            tensor = logits[scale].reshape(len(durations), -1, 2)[batch_index].detach().cpu()
            nsegs = max(int(samples / (0.02 * SAMPLE_RATE) / (2 ** scale)), 1)
            if tensor.shape[0] < nsegs or tensor.shape[-1] != 2:
                raise ValueError(f"native scale {scale} output shape is incompatible")
            rows = []
            for index in range(nsegs):
                rows.append({"start_sec": index * unit, "end_sec": (index + 1) * unit, "class_0": float(tensor[index, 0]), "class_1": float(tensor[index, 1])})
            per_case.append({"scale_id": f"native_{unit:.2f}s", "unit_sec": unit, "output_shape": [nsegs, 2], "temporal_scores": rows})
        output.append(per_case)
    return output


def _terminal(case: dict[str, Any], status: str, started: float, failure: str | None = None, attempt: int = 1) -> dict[str, Any]:
    return {"case_id": case["case_id"], "invocation_id": INVOCATION_ID, "attempt": attempt, "terminal_status": status, "failure": failure, "runtime_sec": time.perf_counter() - started, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def _append(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _existing_case_ids() -> set[str]:
    if not LEDGER_JSONL.exists():
        return set()
    ids: set[str] = set()
    with LEDGER_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            case_id = record["case_id"]
            if case_id in ids:
                raise RuntimeError("duplicate terminal record in existing ledger")
            ids.add(case_id)
    return ids


def _write_run_manifest(status: str, planned: int, terminal: int, valid: int, failed: int, runtime_sec: float) -> None:
    payload = {"schema_version": "phase3t_raw_manifest_v1", "status": status, "data_source": "PartialEdit_v1.1_E1", "authorization_id": AUTHORIZATION_ID, "authorization_base_commit": BASE_COMMIT, "invocation_id": INVOCATION_ID, "namespace": str(NAMESPACE).replace("\\", "/"), "model_id": MODEL_ID, "model_repository_commit": MODEL_REPOSITORY_COMMIT, "checkpoint_sha256": CHECKPOINT_SHA256, "dataset_csv_sha256": DATASET_CSV_SHA256, "planned": planned, "terminal": terminal, "valid": valid, "failed": failed, "missing": planned - terminal, "scales_expected": 6, "scales_preserved": 6 if status == "COMPLETE" else "PENDING", "scientific_metrics_computed": 0, "result_based_scale_selections": 0, "result_based_case_exclusions": 0, "gt_accessed": "NO", "runtime_sec": runtime_sec, "raw_output_path": str(RAW_JSONL).replace("\\", "/"), "ledger_path": str(LEDGER_JSONL).replace("\\", "/"), "retry_ledger_path": str(RETRY_JSONL).replace("\\", "/")}
    NAMESPACE.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(batch_size: int, resume: bool = False) -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; worker is GPU-only")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if NAMESPACE.exists() and not resume:
        raise RuntimeError("dedicated namespace already exists; use explicit resume only")
    if not CHECKPOINT_PATH.is_file():
        raise RuntimeError("authorized checkpoint path missing")
    cases = read_case_order()
    completed = _existing_case_ids() if resume else set()
    if len(completed) > len(cases):
        raise RuntimeError("existing ledger exceeds planned population")
    NAMESPACE.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    device = torch.device("cuda")
    model = _load_model(device)
    _write_run_manifest("RUNNING", len(cases), len(completed), 0, 0, 0.0)
    valid = 0
    failed = 0
    index = 0
    while index < len(cases):
        pending = [row for row in cases[index:index + batch_size] if row["case_id"] not in completed]
        index += batch_size
        if not pending:
            continue
        loaded: list[tuple[dict[str, Any], torch.Tensor, int, str]] = []
        for row in pending:
            started = time.perf_counter()
            try:
                waveform, samples, audio_hash = _load_audio(row)
                loaded.append((row, waveform, samples, audio_hash))
            except FileNotFoundError as exc:
                _append(LEDGER_JSONL, _terminal(row, "FAILED", started, "AUDIO_LOAD_FAILURE")); failed += 1; completed.add(row["case_id"])
            except Exception:
                _append(LEDGER_JSONL, _terminal(row, "FAILED", started, "AUDIO_LOAD_FAILURE")); failed += 1; completed.add(row["case_id"])
        if not loaded:
            continue
        attempts = 0
        while True:
            attempts += 1
            try:
                batch = _padded([item[1] for item in loaded]).to(device)
                infer_started = time.perf_counter()
                with torch.inference_mode():
                    logits, _ = model(batch)
                per_case = _native_outputs(logits, [item[2] for item in loaded])
                if len(per_case) != len(loaded):
                    raise ValueError("batch output length mismatch")
                for (row, _, samples, audio_hash), native in zip(loaded, per_case):
                    started = time.perf_counter()
                    scores = [entry["temporal_scores"] for entry in native]
                    if not all(torch.isfinite(torch.tensor([x["class_0"] for x in scale])).all() and torch.isfinite(torch.tensor([x["class_1"] for x in scale])).all() for scale in scores):
                        raise FloatingPointError("nonfinite native output")
                    raw = {"case_id": row["case_id"], "model_id": MODEL_ID, "checkpoint_sha256": CHECKPOINT_SHA256, "audio_sha256": audio_hash, "sample_rate": SAMPLE_RATE, "duration_sec": samples / SAMPLE_RATE, "native_scales": native, "scale_count": len(native), "finite": True, "runtime_sec": time.perf_counter() - infer_started, "attempt": attempts, "retry_count": max(attempts - 1, 0), "terminal_status": "VALID_INFERENCE", "failure": None}
                    raw["raw_output_sha256"] = canonical_hash(raw)
                    _append(RAW_JSONL, raw)
                    _append(LEDGER_JSONL, _terminal(row, "VALID", started, None, attempts))
                    valid += 1; completed.add(row["case_id"])
                break
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower() and batch_size > 1 and attempts == 1:
                    _append(RETRY_JSONL, {"attempt_id": f"{INVOCATION_ID}-{index}-oom", "case_id": pending[0]["case_id"], "attempt_type": "batch_size_reduction", "invoked": True, "failure": "CUDA_OOM", "retry_reason": "predeclared infrastructure policy; reduce batch only", "authorization_id": AUTHORIZATION_ID})
                    batch_size = 1
                    torch.cuda.empty_cache()
                    continue
                for row, _, _, _ in loaded:
                    _append(LEDGER_JSONL, _terminal(row, "FAILED", time.perf_counter(), "MODEL_INFERENCE_FAILURE", attempts)); failed += 1; completed.add(row["case_id"])
                break
            except FloatingPointError:
                for row, _, _, _ in loaded:
                    _append(LEDGER_JSONL, _terminal(row, "FAILED", time.perf_counter(), "NONFINITE_OUTPUT", attempts)); failed += 1; completed.add(row["case_id"])
                break
            except ValueError:
                for row, _, _, _ in loaded:
                    _append(LEDGER_JSONL, _terminal(row, "FAILED", time.perf_counter(), "INVALID_OUTPUT_SHAPE", attempts)); failed += 1; completed.add(row["case_id"])
                break
            except OSError:
                for row, _, _, _ in loaded:
                    _append(LEDGER_JSONL, _terminal(row, "FAILED", time.perf_counter(), "SERIALIZATION_FAILURE", attempts)); failed += 1; completed.add(row["case_id"])
                break
    total = time.perf_counter() - start
    terminal = len(completed)
    status = "COMPLETE" if terminal == len(cases) and terminal == valid + failed else "INCOMPLETE"
    _write_run_manifest(status, len(cases), terminal, valid, failed, total)
    if status != "COMPLETE":
        raise RuntimeError("RAW_OUTPUT_COMPLETENESS=FAIL")
    print(json.dumps({"status": status, "planned": len(cases), "terminal": terminal, "valid": valid, "failed": failed, "missing": len(cases) - terminal, "scales_preserved": "6/6", "scientific_metrics_computed": 0, "gt_accessed": "NO", "runtime_sec": total, "peak_vram_bytes": torch.cuda.max_memory_allocated(device)}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        return preflight()
    return run(args.batch_size, args.resume)


if __name__ == "__main__":
    raise SystemExit(main())
