from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from common import (
    ALLOWED_TERMINAL_STATUSES,
    AUTHORIZATION_ID,
    DATASET_ID,
    SEED,
    append_jsonl,
    assert_finite_tree,
    attempt_counts,
    existing_terminal_ids,
    read_case_manifest,
    seed_everything,
    sha256_file,
    sha256_json,
    to_jsonable,
)


MODEL_ID = "MultiResoModel-Simple"
MODEL_ROOT = Path(r"G:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/MultiResoModel-Simple-schannel")
SSL_PATH = MODEL_ROOT / "pretrained" / "w2v_large_lv_fsh_swbd_cv_fixed.pt"
MODEL_CHECKPOINT = MODEL_ROOT / "materialized" / "baseline-ps-e55" / "exp" / "baseline" / "55.pth"
CHECKPOINT_SHA256 = "5B753752F7C25370C6ABF973F69F58E100DAD4B5D3EA035872335358A876FDD1"
SSL_SHA256 = "4E1B1AE691F26947FBF0B709FF1DD5F2F16CB586161CC3E9461E35BCD9CB5F75"
UNITS = (0.02, 0.04, 0.08, 0.16, 0.32, 0.64)


def _build_meta(torch: Any, builder):
    """Build a module with PyTorch 1.13-compatible meta-like factories."""

    # ``with torch.device('meta')`` was added after the frozen torch 1.13
    # environment. Redirect the no-device tensor factories just while the
    # architecture is built; checkpoint tensors are assigned afterward.
    import importlib

    originals = {name: getattr(torch, name) for name in ("empty", "zeros", "ones", "full")}
    weight_norm_module = importlib.import_module("torch.nn.utils.weight_norm")
    original_compute_weight = weight_norm_module.WeightNorm.compute_weight
    wav2vec_module = importlib.import_module("fairseq.models.wav2vec.wav2vec2")
    original_init_bert_params = wav2vec_module.init_bert_params

    def meta_factory(original):
        def factory(*args, **kwargs):
            if kwargs.get("device") is None:
                kwargs["device"] = "meta"
            return original(*args, **kwargs)

        return factory

    try:
        for name, original in originals.items():
            setattr(torch, name, meta_factory(original))
        # PyTorch 1.13's weight_norm computes a derived parameter through an
        # operator without a Meta kernel. Keep its exact g/v parameters and
        # forward hook, but defer that derived computation until real tensors
        # are assigned and the model executes.
        weight_norm_module.WeightNorm.compute_weight = lambda self, module: module.weight_v.data
        # The frozen fairseq constructor applies a CPU random initializer
        # which attempts to copy data out of Meta tensors.
        wav2vec_module.init_bert_params = lambda module: None
        return builder()
    finally:
        for name, original in originals.items():
            setattr(torch, name, original)
        weight_norm_module.WeightNorm.compute_weight = original_compute_weight
        wav2vec_module.init_bert_params = original_init_bert_params


def _load_model(device: Any):
    """Build the model using the verified fairseq-compatible SSL lifecycle."""

    import torch
    import torch.nn as nn
    import fairseq
    from fairseq.models.wav2vec.wav2vec2 import Wav2Vec2Config, Wav2Vec2Model

    sys.path.insert(0, str(MODEL_ROOT))
    import modules.multiresomodel as multireso_module

    ssl_cfg = Wav2Vec2Config(
        _name="wav2vec2",
        extractor_mode="layer_norm",
        encoder_layers=24,
        encoder_embed_dim=1024,
        encoder_ffn_embed_dim=4096,
        encoder_attention_heads=16,
        activation_fn="gelu",
        dropout=0.0,
        attention_dropout=0.0,
        activation_dropout=0.0,
        encoder_layerdrop=0.0,
        dropout_input=0.0,
        dropout_features=0.0,
        final_dim=768,
        layer_norm_first=True,
        conv_feature_layers="[(512, 10, 5)] + [(512, 3, 2)] * 4 + [(512,2,2)] + [(512,2,2)]",
        conv_bias=True,
        logit_temp=0.1,
        quantize_targets=True,
        quantize_input=False,
        same_quantizer=False,
        target_glu=False,
        feature_grad_mult=1.0,
        quantizer_depth=1,
        quantizer_factor=3,
        latent_vars=320,
        latent_groups=2,
        latent_dim=0,
        mask_length=10,
        mask_prob=0.65,
        mask_selection="static",
        mask_other=0.0,
        no_mask_overlap=False,
        mask_min_space=1,
        mask_channel_length=10,
        mask_channel_prob=0.0,
        mask_channel_before=False,
        mask_channel_selection="static",
        mask_channel_other=0.0,
        no_mask_channel_overlap=False,
        mask_channel_min_space=1,
        num_negatives=100,
        negatives_from_everywhere=False,
        cross_sample_negatives=0,
        codebook_negatives=0,
        conv_pos=128,
        conv_pos_groups=16,
        latent_temp=(2.0, 0.1, 0.999995),
    )

    # Construct the architecture on meta so the 4.19 GB checkpoint can be
    # read once and assigned directly to model parameters without a second
    # full-sized initialized model in CPU memory.
    fresh_ssl = _build_meta(torch, lambda: Wav2Vec2Model.build_model(ssl_cfg))

    class LifecycleCompatibleSSL(nn.Module):
        def __init__(self, ssl_path: str = "unused", ssl_dim: int = 1024, device: str = "cuda"):
            super().__init__()
            self.model = fresh_ssl
            self.device = device
            self.out_dim = ssl_dim

        def extract_layers_feat(self, input_data):
            # This mirrors the official reimplementation, including its train
            # mode and layer-result transpose, while avoiding a second SSL load.
            if next(self.model.parameters()).device != input_data.device or next(self.model.parameters()).dtype != input_data.dtype:
                self.model.to(input_data.device, dtype=input_data.dtype)
            self.model.train()
            input_tmp = input_data[:, 0, :] if input_data.ndim == 3 else input_data
            results = self.model(input_tmp, mask=False, features_only=True)
            return [hidden[2].transpose(0, 1) for hidden in results["layer_results"]]

        def extract_feat(self, input_data):
            if next(self.model.parameters()).device != input_data.device or next(self.model.parameters()).dtype != input_data.dtype:
                self.model.to(input_data.device, dtype=input_data.dtype)
            self.model.train()
            input_tmp = input_data[:, 0, :] if input_data.ndim == 3 else input_data
            return self.model(input_tmp, mask=False, features_only=True)["x"]

    multireso_module.SSLModel = LifecycleCompatibleSSL
    model = _build_meta(torch, lambda: multireso_module.MultiResoModel(
            num_scales=6,
            include_utt=True,
            use_mask=True,
            ssl_dim=1024,
            ssl_path=str(SSL_PATH),
            ssl_tuning=True,
            device="meta",
        ))
    checkpoint = torch.load(str(MODEL_CHECKPOINT), map_location="cpu")
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
        expected_shape = tuple(model.state_dict()[key].shape)
        if tuple(tensor.shape) != expected_shape:
            raise RuntimeError(f"shape mismatch for {key}: {tuple(tensor.shape)} != {expected_shape}")
        assign_tensor(model, key, tensor)
    del state, checkpoint
    gc.collect()
    model.device = str(device)
    return model.to(device), torch


def _classify_failure(exc: BaseException) -> tuple[str, bool]:
    message = str(exc).lower()
    if "out of memory" in message:
        return "CUDA_OOM", False
    if isinstance(exc, (OSError, IOError)):
        return "AUDIO_LOAD_FAILURE", True
    if "cuda" in message or "cudnn" in message:
        return "INFRASTRUCTURE_FAILURE", True
    if "non-finite" in message or "nan" in message or "inf" in message:
        return "NONFINITE_OUTPUT", False
    if "shape" in message or "size" in message:
        return "INVALID_OUTPUT", False
    return "MODEL_INFERENCE_FAILURE", False


def _run_one(case: dict[str, Any], model: Any, torch: Any, torchaudio: Any, device: Any) -> dict[str, Any]:
    path = Path(case["audio_path"])
    audio_hash = sha256_file(path)
    waveform, sample_rate = torchaudio.load(str(path))
    if waveform.ndim != 2 or waveform.shape[0] != 1:
        raise ValueError("audio must be mono")
    if int(sample_rate) != 16_000:
        raise ValueError(f"sample rate is {sample_rate}, expected 16000")
    original_samples = int(waveform.shape[-1])
    if original_samples <= 0:
        raise ValueError("audio must be non-empty")
    target_size = max(original_samples + int(0.005 * 16_000), int(0.645 * 16_000))
    if original_samples < target_size:
        waveform = torch.nn.functional.pad(waveform, (0, target_size - original_samples), value=0)
    else:
        waveform = waveform[..., :target_size]
    duration = float(original_samples / int(sample_rate))
    x = waveform.unsqueeze(0).to(device=device, dtype=torch.float32)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    with torch.no_grad():
        logits, _ = model(x)
    elapsed = time.perf_counter() - started

    scales: dict[str, Any] = {}
    for scale_index, unit in enumerate(UNITS):
        full_scores = logits[scale_index].reshape(1, -1, 2)
        nsegs = max(int(original_samples / (0.02 * 16_000) / (2**scale_index)), 1)
        scores = full_scores[0, :nsegs, :].detach().cpu().numpy().astype(np.float32)
        supports = np.asarray([[i * unit, (i + 1) * unit] for i in range(nsegs)], dtype=np.float64)
        scales[f"scale_{scale_index}_{unit:.2f}s"] = {
            "scale_index": scale_index,
            "unit_sec": unit,
            "native_times_sec": supports,
            "native_class_scores": scores,
            "class_order": ["spoof", "bonafide"],
            "output_shape": list(scores.shape),
        }
    utterance = logits[-1].reshape(1, 2)[0].detach().cpu().numpy().astype(np.float32)
    native = {
        "scales": scales,
        "utterance_class_scores": utterance,
        "utterance_class_order": ["spoof", "bonafide"],
    }
    assert_finite_tree(native)
    return {
        "case_id": case["case_id"],
        "case_index": case["case_index"],
        "model_id": MODEL_ID,
        "authorization_id": AUTHORIZATION_ID,
        "dataset_id": DATASET_ID,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "ssl_checkpoint_sha256": SSL_SHA256,
        "input_audio_sha256": audio_hash,
        "sample_rate": int(sample_rate),
        "duration_sec": duration,
        "native_outputs": native,
        "raw_output_shapes": {
            key: value["output_shape"] for key, value in scales.items()
        } | {"utterance_class_scores": list(utterance.shape)},
        "raw_output_sha256": sha256_json(to_jsonable(native)),
        "runtime_sec": float(elapsed),
        "peak_vram_bytes": int(torch.cuda.max_memory_allocated(device)) if torch.cuda.is_available() else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase3T MultiResoModel-Simple audio-only full-split runner")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--limit", type=int, default=None, help="test-only prefix limit; never use for the authorized run")
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / "raw.jsonl"
    attempts_path = output / "attempts.jsonl"
    meta_path = output / "run_metadata.json"
    metadata = {
        "authorization_id": AUTHORIZATION_ID,
        "dataset_id": DATASET_ID,
        "model_id": MODEL_ID,
        "manifest_sha256": sha256_file(args.manifest),
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "ssl_checkpoint_sha256": SSL_SHA256,
        "units_sec": list(UNITS),
        "seed": SEED,
        "gt_access_by_model": False,
        "raw_schema": "phase3t_raw_v1",
        "command": "experiments/topconf_phase3t/run_multireso.py",
    }
    if meta_path.exists():
        if json.loads(meta_path.read_text(encoding="utf-8")) != metadata:
            raise RuntimeError("existing MultiReso run metadata differs; refusing to overwrite namespace")
    else:
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    seed_everything(SEED)
    import torch
    import torchaudio

    device = torch.device(args.device if args.device == "cuda" and torch.cuda.is_available() else "cpu")
    model, torch = _load_model(device)
    model.eval()
    done = existing_terminal_ids(raw_path)
    counts = attempt_counts(attempts_path)
    processed = 0
    started_all = time.perf_counter()
    for case in read_case_manifest(args.manifest):
        if args.limit is not None and processed >= args.limit:
            break
        processed += 1
        case_id = case["case_id"]
        if case_id in done:
            continue
        previous = counts.get(case_id, 0)
        while True:
            attempt = previous + 1
            if attempt > 2:
                raise RuntimeError(f"retry budget exhausted without terminal output for {case_id}")
            seed_everything(SEED + int(case["case_index"]))
            attempt_started = time.perf_counter()
            append_jsonl(attempts_path, {
                "authorization_id": AUTHORIZATION_ID,
                "model_id": MODEL_ID,
                "case_id": case_id,
                "case_index": case["case_index"],
                "attempt": attempt,
                "retry_count": attempt - 1,
                "status": "STARTED",
            })
            try:
                record = _run_one(case, model, torch, torchaudio, device)
                record.update({"attempt": attempt, "retry_count": attempt - 1, "terminal": True, "status": "VALID_INFERENCE", "failure": None})
                append_jsonl(attempts_path, {"authorization_id": AUTHORIZATION_ID, "model_id": MODEL_ID, "case_id": case_id, "case_index": case["case_index"], "attempt": attempt, "retry_count": attempt - 1, "status": "VALID_INFERENCE", "elapsed_sec": time.perf_counter() - attempt_started})
                append_jsonl(raw_path, record)
                done.add(case_id)
                break
            except Exception as exc:
                status, retryable = _classify_failure(exc)
                if status not in ALLOWED_TERMINAL_STATUSES:
                    status = "MODEL_INFERENCE_FAILURE"
                failure = f"{type(exc).__name__}: {exc}"
                append_jsonl(attempts_path, {"authorization_id": AUTHORIZATION_ID, "model_id": MODEL_ID, "case_id": case_id, "case_index": case["case_index"], "attempt": attempt, "retry_count": attempt - 1, "status": status, "failure": failure, "elapsed_sec": time.perf_counter() - attempt_started})
                previous = attempt
                if retryable and attempt < 2:
                    continue
                append_jsonl(raw_path, {
                    "case_id": case_id,
                    "case_index": case["case_index"],
                    "model_id": MODEL_ID,
                    "authorization_id": AUTHORIZATION_ID,
                    "dataset_id": DATASET_ID,
                    "checkpoint_sha256": CHECKPOINT_SHA256,
                    "ssl_checkpoint_sha256": SSL_SHA256,
                    "input_audio_sha256": None,
                    "sample_rate": None,
                    "duration_sec": None,
                    "native_outputs": None,
                    "raw_output_shapes": None,
                    "raw_output_sha256": None,
                    "runtime_sec": float(time.perf_counter() - attempt_started),
                    "peak_vram_bytes": int(torch.cuda.max_memory_allocated(device)) if torch.cuda.is_available() else 0,
                    "attempt": attempt,
                    "retry_count": attempt - 1,
                    "terminal": True,
                    "status": status,
                    "failure": failure,
                })
                done.add(case_id)
                break
        if len(done) % 100 == 0:
            print(f"PROGRESS model={MODEL_ID} terminal={len(done)} elapsed_sec={time.perf_counter() - started_all:.1f}", flush=True)
    print(f"COMPLETE model={MODEL_ID} terminal={len(done)} elapsed_sec={time.perf_counter() - started_all:.1f}", flush=True)
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
