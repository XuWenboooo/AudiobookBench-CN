"""Authorized MultiResoModel-Simple x PartialEdit v1.1 E1 raw-output worker.

This is a Level-1 external functional reproduction worker.  It records native
model outputs and infrastructure accounting only.  It never reads target
spans or labels, computes scientific metrics, selects a scale, or excludes a
case based on an outcome.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from multireso_integrity import (
    NamespaceOwnershipError,
    acquire_namespace_lock,
    assert_resume_manifest,
    release_namespace_lock,
    utc_now,
    write_json_atomic,
)


AUTHORIZATION_ID = "P3T-2026-09-13-01"
BASE_COMMIT = "ee8d3a157dd329116e5ea8607a14446f90f26e8d"
MODEL_ID = "MultiResoModel-Simple"
MODEL_REPOSITORY_COMMIT = "0f69db3a2d654de47822d951fe6ad256bbaac9ba"
CHECKPOINT_ARCHIVE_SHA256 = "0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32"
CHECKPOINT_PATH = Path(
    "F:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/"
    "MultiResoModel-Simple-schannel/materialized/baseline-ps-e55/exp/baseline/55.pth"
)
CHECKPOINT_ARCHIVE = Path(
    "F:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/"
    "MultiResoModel-Simple-schannel/downloads/baseline-ps-e55.tgz"
)
MODEL_REPO = Path(
    "F:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/MultiResoModel-Simple-schannel"
)
SSL_PATH = MODEL_REPO / "pretrained" / "w2v_large_lv_fsh_swbd_cv_fixed.pt"
DATASET_CSV = Path(
    "F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/PartialEdit_E1E2.csv"
)
AUDIO_ROOT = Path(
    "F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/materialized/E1"
)
DATASET_CSV_SHA256 = "ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC"
UNITS = (0.02, 0.04, 0.08, 0.16, 0.32, 0.64)
SAMPLE_RATE = 16000
EXPECTED_CASES = 42471
INVOCATION_ID = "PHASE3T_MRM_FULL_E1_002"
NAMESPACE_RELATIVE = "results/topconf_phase3t/multireso_worker_02"
REPO_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = REPO_ROOT / Path(NAMESPACE_RELATIVE)
AUTHORIZED_PYTHON = Path(
    "F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310/Scripts/python.exe"
)

RAW_JSONL = NAMESPACE / "multireso_raw_v1.jsonl"
LEDGER_JSONL = NAMESPACE / "multireso_case_ledger_v1.jsonl"
ATTEMPTS_JSONL = NAMESPACE / "multireso_attempts_v1.jsonl"
RETRY_JSONL = NAMESPACE / "multireso_retry_ledger_v1.jsonl"
MANIFEST_JSONL = NAMESPACE / "multireso_output_manifest_v1.jsonl"
RUN_MANIFEST = NAMESPACE / "MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def _git_value(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO_ROOT), *args], text=True).strip()


def read_case_order() -> list[dict[str, Any]]:
    if sha256_file(DATASET_CSV) != DATASET_CSV_SHA256:
        raise RuntimeError("DATASET_CSV_SHA256 mismatch")
    rows: list[dict[str, Any]] = []
    with DATASET_CSV.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            # Only the path field is consumed.  The remaining CSV fields are
            # GT and are deliberately not parsed or stored by this worker.
            relative = line.rstrip("\r\n").split(",", 1)[0]
            if not relative.startswith("E1/"):
                continue
            rows.append(
                {
                    "case_id": relative,
                    "audio_path": AUDIO_ROOT / relative.removeprefix("E1/"),
                    "csv_line": line_number,
                    "case_index": len(rows),
                }
            )
    if len(rows) != EXPECTED_CASES:
        raise RuntimeError(f"expected {EXPECTED_CASES} E1 cases, got {len(rows)}")
    if len({row["case_id"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate case IDs in frozen canonical order")
    return rows


def _environment_gate() -> tuple[Any, dict[str, Any]]:
    actual_executable = Path(sys.executable).resolve()
    if os.path.normcase(str(actual_executable)) != os.path.normcase(str(AUTHORIZED_PYTHON.resolve())):
        raise RuntimeError(f"authorized executable mismatch: {actual_executable}")
    if tuple(sys.version_info[:3]) != (3, 10, 11):
        raise RuntimeError(f"Python 3.10.11 required, got {sys.version}")

    import fairseq
    import torch

    torch_version = str(torch.__version__)
    fairseq_version = str(getattr(fairseq, "__version__", ""))
    if torch_version != "1.13.1+cu117":
        raise RuntimeError(f"torch 1.13.1+cu117 required, got {torch_version}")
    if fairseq_version != "0.12.2":
        raise RuntimeError(f"fairseq 0.12.2 required, got {fairseq_version}")
    cuda_available = bool(torch.cuda.is_available())
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else ""
    if not cuda_available or gpu_name != "NVIDIA GeForce RTX 4060 Laptop GPU":
        raise RuntimeError(f"authorized CUDA/GPU required, got available={cuda_available} gpu={gpu_name!r}")
    identity = {
        "invocation_id": INVOCATION_ID,
        "namespace": NAMESPACE_RELATIVE,
        "branch": _git_value("branch", "--show-current"),
        "repository_commit": _git_value("rev-parse", "HEAD"),
        "authorized_executable": str(AUTHORIZED_PYTHON),
        "python_version": "3.10.11",
        "torch_version": torch_version,
        "fairseq_version": fairseq_version,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
    }
    return torch, identity


def _build_meta(torch_module: Any, builder: Any) -> Any:
    """Build the frozen fairseq architecture without a second full allocation."""

    import importlib

    originals = {name: getattr(torch_module, name) for name in ("empty", "zeros", "ones", "full")}
    weight_norm_module = importlib.import_module("torch.nn.utils.weight_norm")
    original_compute_weight = weight_norm_module.WeightNorm.compute_weight
    wav2vec_module = importlib.import_module("fairseq.models.wav2vec.wav2vec2")
    original_init_bert_params = wav2vec_module.init_bert_params

    def meta_factory(original: Any):
        def factory(*args: Any, **kwargs: Any):
            if kwargs.get("device") is None:
                kwargs["device"] = "meta"
            return original(*args, **kwargs)

        return factory

    try:
        for name, original in originals.items():
            setattr(torch_module, name, meta_factory(original))
        weight_norm_module.WeightNorm.compute_weight = lambda self, module: module.weight_v.data
        wav2vec_module.init_bert_params = lambda module: None
        return builder()
    finally:
        for name, original in originals.items():
            setattr(torch_module, name, original)
        weight_norm_module.WeightNorm.compute_weight = original_compute_weight
        wav2vec_module.init_bert_params = original_init_bert_params


def _load_model(torch: Any, device: Any) -> tuple[Any, dict[str, int]]:
    import torch.nn as nn
    from fairseq.models.wav2vec.wav2vec2 import Wav2Vec2Config, Wav2Vec2Model

    sys.path.insert(0, str(MODEL_REPO))
    import modules.multiresomodel as multireso_module  # type: ignore

    ssl_cfg = Wav2Vec2Config(
        _name="wav2vec2", extractor_mode="layer_norm", encoder_layers=24,
        encoder_embed_dim=1024, encoder_ffn_embed_dim=4096,
        encoder_attention_heads=16, activation_fn="gelu", dropout=0.0,
        attention_dropout=0.0, activation_dropout=0.0, encoder_layerdrop=0.0,
        dropout_input=0.0, dropout_features=0.0, final_dim=768,
        layer_norm_first=True,
        conv_feature_layers="[(512, 10, 5)] + [(512, 3, 2)] * 4 + [(512,2,2)] + [(512,2,2)]",
        conv_bias=True, logit_temp=0.1, quantize_targets=True,
        quantize_input=False, same_quantizer=False, target_glu=False,
        feature_grad_mult=1.0, quantizer_depth=1, quantizer_factor=3,
        latent_vars=320, latent_groups=2, latent_dim=0, mask_length=10,
        mask_prob=0.65, mask_selection="static", mask_other=0.0,
        no_mask_overlap=False, mask_min_space=1, mask_channel_length=10,
        mask_channel_prob=0.0, mask_channel_before=False,
        mask_channel_selection="static", mask_channel_other=0.0,
        no_mask_channel_overlap=False, mask_channel_min_space=1,
        num_negatives=100, negatives_from_everywhere=False,
        cross_sample_negatives=0, codebook_negatives=0, conv_pos=128,
        conv_pos_groups=16, latent_temp=(2.0, 0.1, 0.999995),
    )
    fresh_ssl = _build_meta(torch, lambda: Wav2Vec2Model.build_model(ssl_cfg))

    class LifecycleCompatibleSSL(nn.Module):
        def __init__(self, ssl_path: str = "unused", ssl_dim: int = 1024, device: str = "cuda"):
            super().__init__()
            self.model = fresh_ssl
            self.device = device
            self.out_dim = ssl_dim

        def extract_layers_feat(self, input_data: Any):
            parameter = next(self.model.parameters())
            if parameter.device != input_data.device or parameter.dtype != input_data.dtype:
                self.model.to(input_data.device, dtype=input_data.dtype)
            self.model.train()
            input_tmp = input_data[:, 0, :] if input_data.ndim == 3 else input_data
            results = self.model(input_tmp, mask=False, features_only=True)
            return [hidden[2].transpose(0, 1) for hidden in results["layer_results"]]

        def extract_feat(self, input_data: Any):
            parameter = next(self.model.parameters())
            if parameter.device != input_data.device or parameter.dtype != input_data.dtype:
                self.model.to(input_data.device, dtype=input_data.dtype)
            self.model.train()
            input_tmp = input_data[:, 0, :] if input_data.ndim == 3 else input_data
            return self.model(input_tmp, mask=False, features_only=True)["x"]

    multireso_module.SSLModel = LifecycleCompatibleSSL
    model = _build_meta(
        torch,
        lambda: multireso_module.MultiResoModel(
            num_scales=6, include_utt=True, use_mask=True, ssl_dim=1024,
            ssl_path=str(SSL_PATH), ssl_tuning=True, device="meta",
        ),
    )
    checkpoint = torch.load(str(CHECKPOINT_PATH), map_location="cpu")
    state = checkpoint["modules"]["model"]
    model_keys = set(model.state_dict().keys())
    state_keys = set(state.keys())
    missing = model_keys - state_keys
    unexpected = state_keys - model_keys
    if missing or unexpected:
        raise RuntimeError(f"strict MultiReso state mismatch: missing={sorted(missing)[:5]} unexpected={sorted(unexpected)[:5]}")

    def assign_tensor(module: nn.Module, key: str, tensor: Any) -> None:
        parent_name, _, local_name = key.rpartition(".")
        parent = module.get_submodule(parent_name) if parent_name else module
        if local_name in parent._parameters:
            original = parent._parameters[local_name]
            parent._parameters[local_name] = nn.Parameter(tensor, requires_grad=original.requires_grad)
        elif local_name in parent._buffers:
            parent._buffers[local_name] = tensor
        else:
            raise RuntimeError(f"cannot assign checkpoint tensor {key}")

    for key, tensor in state.items():
        if tuple(tensor.shape) != tuple(model.state_dict()[key].shape):
            raise RuntimeError(f"shape mismatch for {key}")
        assign_tensor(model, key, tensor)
    del state, checkpoint
    gc.collect()
    model.device = str(device)
    model = model.to(device)
    model.eval()
    return model, {"missing": len(missing), "unexpected": len(unexpected)}


def _load_audio(row: dict[str, Any], torchaudio: Any) -> tuple[Any, int, str]:
    path = row["audio_path"]
    if not path.is_file():
        raise FileNotFoundError(str(path))
    waveform, sample_rate = torchaudio.load(str(path))
    if sample_rate != SAMPLE_RATE or waveform.ndim != 2 or waveform.shape[0] != 1:
        raise ValueError("audio input contract violation")
    if waveform.shape[-1] == 0:
        raise ValueError("empty waveform")
    return waveform, int(waveform.shape[-1]), sha256_file(path)


def _padded(waveforms: list[Any], torch: Any) -> Any:
    target = max(max(int(item.shape[-1]), int(0.645 * SAMPLE_RATE)) for item in waveforms) + int(0.005 * SAMPLE_RATE)
    return torch.cat([torch.nn.functional.pad(item, (0, target - item.shape[-1])) for item in waveforms], dim=0)


def _native_outputs(logits: list[Any], durations: list[int], torch: Any) -> list[dict[str, Any]]:
    if len(logits) < 7:
        raise ValueError("fewer than six native temporal scales plus utterance output")
    output: list[dict[str, Any]] = []
    for batch_index, samples in enumerate(durations):
        scales: dict[str, dict[str, Any]] = {}
        for scale, unit in enumerate(UNITS):
            tensor = logits[scale].reshape(len(durations), -1, 2)[batch_index].detach().cpu()
            nsegs = max(int(samples / (0.02 * SAMPLE_RATE) / (2 ** scale)), 1)
            if tensor.shape[0] < nsegs or tensor.shape[-1] != 2:
                raise ValueError(f"native scale {scale} output shape is incompatible")
            values = tensor[:nsegs, :].tolist()
            scales[f"scale_{scale}_{unit:.2f}s"] = {
                "scale_index": scale,
                "unit_sec": unit,
                "native_times_sec": [[index * unit, (index + 1) * unit] for index in range(nsegs)],
                "native_class_scores": values,
                "class_order": ["spoof", "bonafide"],
                "output_shape": [nsegs, 2],
            }
        utterance = logits[-1].reshape(len(durations), 2)[batch_index].detach().cpu().tolist()
        output.append(
            {
                "scales": scales,
                "utterance_class_scores": utterance,
                "utterance_class_order": ["spoof", "bonafide"],
            }
        )
    return output


def _native_is_finite(native: dict[str, Any]) -> bool:
    try:
        return all(
            math.isfinite(float(value))
            for scale in native["scales"].values()
            for row in scale["native_class_scores"]
            for value in row
        ) and all(math.isfinite(float(value)) for value in native["utterance_class_scores"])
    except (KeyError, TypeError, ValueError):
        return False


def _append(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _terminal(row: dict[str, Any], status: str, started: float, failure: str | None, attempt: int) -> dict[str, Any]:
    return {
        "case_id": row["case_id"],
        "case_index": row["case_index"],
        "invocation_id": INVOCATION_ID,
        "attempt": attempt,
        "terminal_status": status,
        "failure": failure,
        "runtime_sec": time.perf_counter() - started,
        "timestamp_utc": utc_now(),
    }


def _raw_record(
    row: dict[str, Any],
    status: str,
    failure: str | None,
    attempt: int,
    retry_count: int,
    audio_hash: str | None,
    native: dict[str, Any] | None,
    runtime_sec: float,
    peak_vram_bytes: int,
) -> dict[str, Any]:
    return {
        "case_id": row["case_id"],
        "case_index": row["case_index"],
        "model_id": MODEL_ID,
        "authorization_id": AUTHORIZATION_ID,
        "dataset_id": "PartialEdit_v1.1_E1",
        "checkpoint_archive_sha256": CHECKPOINT_ARCHIVE_SHA256,
        "input_audio_sha256": audio_hash,
        "sample_rate": SAMPLE_RATE,
        "duration_sec": None if native is None else row["samples"] / SAMPLE_RATE,
        "native_outputs": native,
        "raw_output_shapes": {} if native is None else {
            key: value["output_shape"] for key, value in native["scales"].items()
        } | {"utterance_class_scores": [2]},
        "raw_output_sha256": None if native is None else canonical_hash(native),
        "runtime_sec": runtime_sec,
        "peak_vram_bytes": peak_vram_bytes,
        "attempt": attempt,
        "retry_count": retry_count,
        "status": status,
        "terminal": True,
        "failure": failure,
    }


def _record_terminal(
    row: dict[str, Any],
    *,
    status: str,
    failure: str | None,
    attempt: int,
    audio_hash: str | None,
    native: dict[str, Any] | None,
    started: float,
    torch: Any,
) -> None:
    runtime = time.perf_counter() - started
    peak = int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0
    raw = _raw_record(row, status, failure, attempt, max(attempt - 1, 0), audio_hash, native, runtime, peak)
    _append(RAW_JSONL, raw)
    _append(
        MANIFEST_JSONL,
        {
            "case_id": row["case_id"],
            "case_index": row["case_index"],
            "status": status,
            "raw_output_sha256": raw["raw_output_sha256"],
            "attempt": attempt,
            "failure": failure,
        },
    )
    _append(LEDGER_JSONL, _terminal(row, "VALID" if native is not None else "FAILED", started, failure, attempt))


def _existing_case_state(namespace: Path) -> tuple[set[str], int, int]:
    if not LEDGER_JSONL.exists():
        return set(), 0, 0
    ids: set[str] = set()
    valid = failed = 0
    with LEDGER_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            case_id = record["case_id"]
            if case_id in ids:
                raise RuntimeError("duplicate terminal record in existing ledger")
            ids.add(case_id)
            if record.get("terminal_status") == "VALID":
                valid += 1
            elif record.get("terminal_status") == "FAILED":
                failed += 1
            else:
                raise RuntimeError("invalid terminal status in existing ledger")
    if not RAW_JSONL.exists():
        raise RuntimeError("existing terminal ledger has no raw-output ledger")
    raw_ids: set[str] = set()
    with RAW_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            case_id = json.loads(line)["case_id"]
            if case_id in raw_ids:
                raise RuntimeError("duplicate raw output record in existing namespace")
            raw_ids.add(case_id)
    if raw_ids != ids:
        raise RuntimeError("raw-output and terminal ledgers are not one-to-one")
    return ids, valid, failed


def _write_run_manifest(identity: dict[str, Any], status: str, planned: int, terminal: int, valid: int, failed: int, runtime_sec: float, strict: dict[str, int]) -> None:
    payload = {
        "schema_version": "phase3t_raw_manifest_v1",
        "status": status,
        "authorization_id": AUTHORIZATION_ID,
        "authorization_base_commit": BASE_COMMIT,
        **identity,
        "data_source": "PartialEdit_v1.1_E1",
        "case_population": "all valid E1 cases",
        "case_order": "official CSV E1 order",
        "planned": planned,
        "terminal": terminal,
        "valid": valid,
        "failed": failed,
        "missing": planned - terminal,
        "model_id": MODEL_ID,
        "model_repository_commit": MODEL_REPOSITORY_COMMIT,
        "checkpoint_archive_sha256": CHECKPOINT_ARCHIVE_SHA256,
        "dataset_csv_sha256": DATASET_CSV_SHA256,
        "scales_expected": 6,
        "scales_preserved": "6/6" if status == "COMPLETE" else "PENDING",
        "strict_load_missing": strict["missing"],
        "strict_load_unexpected": strict["unexpected"],
        "scientific_metrics_computed": 0,
        "gt_accessed": "NO",
        "result_based_scale_selections": 0,
        "result_based_case_exclusions": 0,
        "raw_output_path": str(RAW_JSONL).replace("\\", "/"),
        "ledger_path": str(LEDGER_JSONL).replace("\\", "/"),
        "attempts_path": str(ATTEMPTS_JSONL).replace("\\", "/"),
        "retry_ledger_path": str(RETRY_JSONL).replace("\\", "/"),
        "manifest_jsonl_path": str(MANIFEST_JSONL).replace("\\", "/"),
        "runtime_sec": runtime_sec,
        "updated_utc": utc_now(),
    }
    write_json_atomic(RUN_MANIFEST, payload)


def _is_oom(exc: BaseException) -> bool:
    return "out of memory" in str(exc).lower()


def _failure_for_exception(exc: BaseException) -> tuple[str, str]:
    if _is_oom(exc):
        return "CUDA_OOM", "CUDA_OOM"
    if isinstance(exc, FloatingPointError):
        return "NONFINITE_OUTPUT", "NONFINITE_OUTPUT"
    if isinstance(exc, ValueError):
        return "INVALID_OUTPUT", "INVALID_OUTPUT_SHAPE"
    if isinstance(exc, OSError):
        return "INFRASTRUCTURE_FAILURE", "SERIALIZATION_FAILURE"
    return "MODEL_INFERENCE_FAILURE", "MODEL_INFERENCE_FAILURE"


def _cleanup_cuda(torch: Any, *objects: Any) -> None:
    for obj in objects:
        del obj
    gc.collect()
    try:
        torch.cuda.empty_cache()
    except Exception:
        pass


def _infer_batch(model: Any, loaded: list[dict[str, Any]], attempt: int, torch: Any) -> tuple[list[dict[str, Any]] | None, BaseException | None]:
    for row in loaded:
        _append(
            ATTEMPTS_JSONL,
            {
                "authorization_id": AUTHORIZATION_ID,
                "case_id": row["case_id"],
                "case_index": row["case_index"],
                "attempt": attempt,
                "retry_count": max(attempt - 1, 0),
                "status": "STARTED",
                "timestamp_utc": utc_now(),
            },
        )
    batch = logits = None
    started = time.perf_counter()
    try:
        batch = _padded([row["waveform"] for row in loaded], torch).to("cuda")
        with torch.inference_mode():
            logits, _ = model(batch)
        native = _native_outputs(logits, [row["samples"] for row in loaded], torch)
        if len(native) != len(loaded):
            raise ValueError("batch output length mismatch")
        if not all(_native_is_finite(item) for item in native):
            raise FloatingPointError("nonfinite native output")
        runtime = time.perf_counter() - started
        for row, item in zip(loaded, native):
            row["native_runtime_sec"] = runtime
            row["native"] = item
        _cleanup_cuda(torch, logits, batch)
        return native, None
    except BaseException as exc:
        _cleanup_cuda(torch, logits, batch)
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return None, exc


def _run(batch_size: int, resume: bool, recover_stale_lock: bool) -> int:
    torch, identity = _environment_gate()
    import torchaudio

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if not CHECKPOINT_ARCHIVE.is_file() or sha256_file(CHECKPOINT_ARCHIVE) != CHECKPOINT_ARCHIVE_SHA256:
        raise RuntimeError("authorized checkpoint archive missing or hash mismatch")
    if not CHECKPOINT_PATH.is_file() or not SSL_PATH.is_file():
        raise RuntimeError("authorized model materialization is incomplete")
    cases = read_case_order()

    if NAMESPACE.exists() and not resume:
        raise NamespaceOwnershipError("dedicated namespace already exists; explicit resume is required")
    if resume:
        assert_resume_manifest(NAMESPACE, identity)
        completed, valid, failed = _existing_case_state(NAMESPACE)
    else:
        completed, valid, failed = set(), 0, 0

    lock = acquire_namespace_lock(
        NAMESPACE,
        identity,
        resume=resume,
        recover_stale=recover_stale_lock,
    )
    started_run = time.perf_counter()
    strict = {"missing": 0, "unexpected": 0}
    model = None
    current_batch_size = batch_size
    try:
        model, strict = _load_model(torch, torch.device("cuda"))
        _write_run_manifest(identity, "RUNNING", len(cases), len(completed), valid, failed, 0.0, strict)
        index = 0
        while index < len(cases):
            window = cases[index:index + current_batch_size]
            index += len(window)
            pending = [row for row in window if row["case_id"] not in completed]
            if not pending:
                continue

            loaded: list[dict[str, Any]] = []
            for row in pending:
                load_started = time.perf_counter()
                try:
                    waveform, samples, audio_hash = _load_audio(row, torchaudio)
                    loaded.append({**row, "waveform": waveform, "samples": samples, "audio_hash": audio_hash})
                except Exception:
                    _record_terminal(
                        row,
                        status="AUDIO_LOAD_FAILURE",
                        failure="AUDIO_LOAD_FAILURE",
                        attempt=1,
                        audio_hash=None,
                        native=None,
                        started=load_started,
                        torch=torch,
                    )
                    completed.add(row["case_id"])
                    failed += 1
            if not loaded:
                continue

            native, error = _infer_batch(model, loaded, 1, torch)
            if error is not None and _is_oom(error) and len(loaded) > 1 and current_batch_size > 1:
                for row in loaded:
                    _append(
                        RETRY_JSONL,
                        {
                            "attempt_id": f"{INVOCATION_ID}-{row['case_index']}-batch-reduction",
                            "case_id": row["case_id"],
                            "case_index": row["case_index"],
                            "attempt_type": "batch_size_reduction",
                            "from_batch_size": current_batch_size,
                            "to_batch_size": 1,
                            "retry_attempt": 2,
                            "failure": "CUDA_OOM",
                            "retry_reason": "predeclared infrastructure policy; batch-size only",
                            "authorization_id": AUTHORIZATION_ID,
                        },
                    )
                current_batch_size = 1
                for row in loaded:
                    one_native, one_error = _infer_batch(model, [row], 2, torch)
                    if one_error is not None:
                        status, failure = _failure_for_exception(one_error)
                        _record_terminal(
                            row, status=status, failure=failure, attempt=2,
                            audio_hash=row["audio_hash"], native=None,
                            started=time.perf_counter(), torch=torch,
                        )
                        failed += 1
                    else:
                        row["native"] = one_native[0]
                        _record_terminal(
                            row, status="VALID_INFERENCE", failure=None, attempt=2,
                            audio_hash=row["audio_hash"], native=row["native"],
                            started=time.perf_counter(), torch=torch,
                        )
                        valid += 1
                    completed.add(row["case_id"])
                continue

            if error is not None:
                status, failure = _failure_for_exception(error)
                for row in loaded:
                    _record_terminal(
                        row, status=status, failure=failure, attempt=1,
                        audio_hash=row["audio_hash"], native=None,
                        started=time.perf_counter(), torch=torch,
                    )
                    completed.add(row["case_id"])
                    failed += 1
                continue

            assert native is not None
            for row, item in zip(loaded, native):
                _record_terminal(
                    row, status="VALID_INFERENCE", failure=None, attempt=1,
                    audio_hash=row["audio_hash"], native=item,
                    started=time.perf_counter(), torch=torch,
                )
                completed.add(row["case_id"])
                valid += 1
            terminal = len(completed)
            if terminal % 100 == 0 or terminal == len(cases):
                print(json.dumps({"invocation": INVOCATION_ID, "terminal": terminal, "planned": len(cases), "valid": valid, "failed": failed, "scales_preserved": "6/6", "scientific_metrics_computed": 0, "gt_accessed": "NO"}, sort_keys=True), flush=True)
            _write_run_manifest(identity, "RUNNING", len(cases), terminal, valid, failed, time.perf_counter() - started_run, strict)

        terminal = len(completed)
        status = "COMPLETE" if terminal == len(cases) and terminal == valid + failed else "INCOMPLETE"
        _write_run_manifest(identity, status, len(cases), terminal, valid, failed, time.perf_counter() - started_run, strict)
        if status != "COMPLETE":
            raise RuntimeError("RAW_OUTPUT_COMPLETENESS=FAIL")
        release_namespace_lock(
            lock,
            identity,
            status="COMPLETED",
            updates={
                "terminal": terminal,
                "valid": valid,
                "failed": failed,
                "planned": len(cases),
                "completed_manifest": str(RUN_MANIFEST).replace("\\", "/"),
            },
        )
        print(json.dumps({"status": status, "planned": len(cases), "terminal": terminal, "valid": valid, "failed": failed, "missing": len(cases) - terminal, "scales_preserved": "6/6", "scientific_metrics_computed": 0, "gt_accessed": "NO", "runtime_sec": time.perf_counter() - started_run}, sort_keys=True), flush=True)
        return 0
    except BaseException as exc:
        try:
            release_namespace_lock(
                lock,
                identity,
                status="ABORTED",
                updates={"abort_type": type(exc).__name__, "abort_reason": str(exc)[:500]},
            )
        except Exception:
            pass
        raise
    finally:
        if model is not None:
            del model
        gc.collect()
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


def _preflight() -> int:
    torch, identity = _environment_gate()
    import torchaudio

    if not CHECKPOINT_ARCHIVE.is_file() or sha256_file(CHECKPOINT_ARCHIVE) != CHECKPOINT_ARCHIVE_SHA256:
        raise RuntimeError("authorized checkpoint archive missing or hash mismatch")
    if not CHECKPOINT_PATH.is_file() or not SSL_PATH.is_file():
        raise RuntimeError("authorized model materialization is incomplete")
    case = read_case_order()[0]
    waveform, samples, audio_hash = _load_audio(case, torchaudio)
    model, strict = _load_model(torch, torch.device("cuda"))
    try:
        with torch.inference_mode():
            logits, _ = model(_padded([waveform], torch).cuda())
        native = _native_outputs(logits, [samples], torch)[0]
        if len(native["scales"]) != 6 or not _native_is_finite(native):
            raise RuntimeError("technical preflight output contract failed")
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()
    print(json.dumps({"preflight": "PASS", "invocation": INVOCATION_ID, "case_index": 0, "input_audio_sha256_present": bool(audio_hash), "strict_load": strict, "authorized_executable": identity["authorized_executable"], "python": identity["python_version"], "torch": identity["torch_version"], "fairseq": identity["fairseq_version"], "gpu": identity["gpu_name"], "scales": 6, "scientific_metrics_computed": 0, "gt_accessed": "NO"}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--recover-stale-lock", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        return _preflight()
    return _run(args.batch_size, args.resume, args.recover_stale_lock)


if __name__ == "__main__":
    raise SystemExit(main())

