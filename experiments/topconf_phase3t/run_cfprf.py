from __future__ import annotations

import argparse
import gc
import json
import sys
import time
import types
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


MODEL_ID = "CFPRF"
CFPRF_ROOT = Path(r"G:/项目/申请实验室  TTS项目/topconf_phase3_cache/repos/CFPRF")
XLSR_PATH = Path(r"G:/项目/申请实验室  TTS项目/topconf_phase3_cache/checkpoints/CFPRF/pretrain_models/xlsr2_300m.pt")
FDN_PATH = Path(r"G:/项目/申请实验室  TTS项目/topconf_phase3_cache/checkpoints/CFPRF/1FDN_PS.pth")
PRN_PATH = Path(r"G:/项目/申请实验室  TTS项目/topconf_phase3_cache/checkpoints/CFPRF/2PRN_PS.pth")
CHECKPOINT_HASHES = {
    "fdn": "5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267",
    "prn": "88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36",
    "xlsr": "B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9",
}


def _load_models(device: Any):
    """Load the official CFPRF modules without importing its GT dataloader."""

    sys.path.insert(0, str(CFPRF_ROOT))
    import torch
    import torch.nn as nn
    from fairseq.models.wav2vec.wav2vec2 import Wav2Vec2Config, Wav2Vec2Model
    import models.FDN as fdn_module
    import models.PRN as prn_module

    class AbsoluteASRModel(nn.Module):
        def __init__(self):
            super().__init__()
            # The verified FDN checkpoint contains the complete ``asr.model``
            # state. Build the exact XLSR architecture from its frozen config
            # rather than loading a second 1.27 GB copy of the same weights.
            cfg = Wav2Vec2Config(
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
            self.model = Wav2Vec2Model.build_model(cfg)

        def forward(self, x):
            return self.model(x, mask=False, features_only=True)["x"]

    # The official FDN constructor uses a repository-relative XLSR path. This
    # path-only override leaves the architecture and checkpoint semantics
    # unchanged while keeping the runner independent of the GT dataloader.
    fdn_module.ASRModel = AbsoluteASRModel
    # Keep the FDN post-ASR stack on CPU and place only the embedded XLSR
    # encoder on CUDA. This is an infrastructure-compatible placement: all
    # model layers, dtypes, weights, and score semantics remain unchanged,
    # while the verified 8 GiB GPU can execute the full split reliably.
    fdn = fdn_module.CFPRF_FDN(seq_len=1070, gmlp_layers=1)
    fdn.load_state_dict(torch.load(str(FDN_PATH), map_location="cpu", mmap=True, weights_only=True), strict=True, assign=True)
    prn = prn_module.CFPRF_PRN(device=torch.device("cpu"))
    prn.load_state_dict(torch.load(str(PRN_PATH), map_location="cpu", mmap=True, weights_only=True), strict=True, assign=True)
    fdn.PE_T.encoding = fdn.PE_T.encoding.cpu()
    if device.type == "cuda":
        fdn.asr.model.to(device)

        def hybrid_forward(self, x):
            gpu_x = x.to(device=device, dtype=torch.float32)
            return self.model(gpu_x, mask=False, features_only=True)["x"].cpu()

        fdn.asr.forward = types.MethodType(hybrid_forward, fdn.asr)
    fdn.eval()
    prn.eval()
    return fdn, prn, fdn_module, prn_module


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
    if "shape" in message or "proposal" in message or "index" in message:
        return "INVALID_OUTPUT", False
    return "MODEL_INFERENCE_FAILURE", False


def _proposal_outputs(seg_scores: np.ndarray, emb_t: Any, fdn: Any, prn: Any, tool: Any, torch: Any, device: Any) -> dict[str, Any]:
    """Run native CFPRF proposal decoding without any target input."""

    seg_scores = np.asarray(seg_scores, dtype=np.float32)
    boundary_scores = None
    coarse = tool.segscore2proposal(seg_scores, cp_fun=tool.proposal_func, rso=20)[1]
    coarse = np.asarray(coarse, dtype=np.float32).reshape(-1, 3)
    coarse_seconds = tool.frame2second_proposal(coarse, rso=20) if coarse.size else []
    native: dict[str, Any] = {
        "fdn_coarse_proposals": coarse_seconds,
        "prn_input_coarse_proposals": coarse_seconds,
        "prn_verification_scores": [],
        "prn_regression_outputs": [],
        "prn_scored_coarse_proposals": [],
        "prn_verification_proposals": [],
        "prn_refined_proposals": [],
    }
    if not coarse.size:
        return native

    cp_list = [coarse]
    with torch.no_grad():
        ver_score, reg_pred, _, prn_cp_list = prn(emb_t, cp_list, 20)
    ver_np = ver_score.detach().cpu().numpy().reshape(-1, 1).astype(np.float32)
    reg_np = reg_pred.detach().cpu().numpy().reshape(-1, 2).astype(np.float32)
    scored = np.asarray(prn_cp_list[0], dtype=np.float32).reshape(-1, 3)
    native["prn_verification_scores"] = ver_np
    native["prn_regression_outputs"] = reg_np
    native["prn_scored_coarse_proposals"] = tool.frame2second_proposal(scored, rso=20)

    ver_label_pred = (ver_np.reshape(-1) > 0.5).astype(np.int64)
    cp_ver_list = tool.decoder_ver(prn_cp_list, ver_label_pred)
    native["prn_verification_proposals"] = tool.frame2second_proposal(cp_ver_list[0], rso=20) if cp_ver_list[0].size else []

    sampled_pos_inds = np.where(ver_label_pred == 1)[0]
    prn_cp_flatten = np.concatenate([arr for arr in prn_cp_list if arr.size > 0]).reshape(-1, 3)
    lengths = prn_cp_flatten[sampled_pos_inds][:, 2] - prn_cp_flatten[sampled_pos_inds][:, 1] if sampled_pos_inds.size else np.array([])
    short_inds = np.where(lengths < 2)[0]
    fp_pred_list: list[np.ndarray] = [np.array([])]
    fp_short_list: list[np.ndarray] = [np.array([])]
    if short_inds.size > 0:
        sampled_pos_short_inds = sampled_pos_inds[short_inds]
        sampled_pos_inds = np.delete(sampled_pos_inds, short_inds)
        short_label_pred = np.zeros(len(ver_label_pred))
        short_label_pred[sampled_pos_short_inds] = 1
        fp_short_list = tool.decoder_ver(prn_cp_list, short_label_pred)
    if sampled_pos_inds.size > 0:
        pos_label_pred = np.zeros(len(ver_label_pred))
        pos_label_pred[sampled_pos_inds] = 1
        fp_pred_flatten = tool.decoder_reg(prn_cp_flatten, reg_np)
        fp_pred_flatten[fp_pred_flatten[:, 2] == 0] = prn_cp_flatten[fp_pred_flatten[:, 2] == 0]
        fp_pred_list = tool.decoder_ver2(fp_pred_flatten, pos_label_pred, cp_list)
    fp_short = fp_short_list[0] if fp_short_list else np.array([])
    fp_pred = fp_pred_list[0] if fp_pred_list else np.array([])
    if fp_short.size == 0:
        combined = fp_pred
    elif fp_pred.size == 0:
        combined = fp_short
    else:
        combined = tool.vstack_twolist(fp_short, fp_pred)
    native["prn_refined_proposals"] = tool.frame2second_proposal(combined, rso=20) if np.asarray(combined).size else []
    return native


def _run_one(case: dict[str, Any], fdn: Any, prn: Any, tool: Any, torch: Any, sf: Any, device: Any) -> dict[str, Any]:
    path = Path(case["audio_path"])
    audio_bytes_hash = sha256_file(path)
    waveform, sample_rate = sf.read(path, dtype="float32", always_2d=False)
    waveform = np.asarray(waveform)
    if waveform.ndim == 2:
        if waveform.shape[1] != 1:
            raise ValueError("audio must be mono")
        waveform = waveform[:, 0]
    if waveform.ndim != 1 or waveform.size == 0:
        raise ValueError("audio must be a non-empty 1-D waveform")
    if int(sample_rate) != 16_000:
        raise ValueError(f"sample rate is {sample_rate}, expected 16000")
    duration = float(waveform.size / int(sample_rate))
    # The hybrid runner's FDN stack is CPU-resident; its patched ASR wrapper
    # performs the sole CPU->CUDA transfer when CUDA is available.
    x = torch.from_numpy(waveform).reshape(1, -1).to(dtype=torch.float32)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    with torch.no_grad():
        seg_scores, boundary_scores, emb_t, f_ba = fdn(x)
    elapsed = time.perf_counter() - started
    seg = seg_scores[0].detach().cpu().numpy().astype(np.float32)
    boundary = boundary_scores[0].detach().cpu().numpy().astype(np.float32)
    native = {
        "fdn_segment_scores": seg,
        "fdn_boundary_scores": boundary,
        "fdn_segment_class_order": ["spoof", "bonafide"],
    }
    native.update(_proposal_outputs(seg, emb_t, fdn, prn, tool, torch, device))
    assert_finite_tree(native)
    raw_hash = sha256_json(to_jsonable(native))
    peak = int(torch.cuda.max_memory_allocated(device)) if device.type == "cuda" else 0
    return {
        "case_id": case["case_id"],
        "case_index": case["case_index"],
        "model_id": MODEL_ID,
        "authorization_id": AUTHORIZATION_ID,
        "dataset_id": DATASET_ID,
        "checkpoint_hashes": CHECKPOINT_HASHES,
        "input_audio_sha256": audio_bytes_hash,
        "sample_rate": int(sample_rate),
        "duration_sec": duration,
        "native_outputs": native,
        "raw_output_shapes": {
            "fdn_segment_scores": list(seg.shape),
            "fdn_boundary_scores": list(boundary.shape),
            "emb_T": list(emb_t.shape),
            "F_BA": list(f_ba.shape),
        },
        "raw_output_sha256": raw_hash,
        "runtime_sec": float(elapsed),
        "peak_vram_bytes": peak,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase3T CFPRF audio-only full-split runner")
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
        "checkpoint_hashes": CHECKPOINT_HASHES,
        "seed": SEED,
        "gt_access_by_model": False,
        "raw_schema": "phase3t_raw_v1",
        "command": "experiments/topconf_phase3t/run_cfprf.py",
    }
    if meta_path.exists():
        if json.loads(meta_path.read_text(encoding="utf-8")) != metadata:
            raise RuntimeError("existing CFPRF run metadata differs; refusing to overwrite namespace")
    else:
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    seed_everything(SEED)
    import soundfile as sf
    import torch

    device = torch.device(args.device if args.device == "cuda" and torch.cuda.is_available() else "cpu")
    fdn, prn, _, _ = _load_models(device)
    sys.path.insert(0, str(CFPRF_ROOT))
    from libs import tool

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
                record = _run_one(case, fdn, prn, tool, torch, sf, device)
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
                    "checkpoint_hashes": CHECKPOINT_HASHES,
                    "input_audio_sha256": None,
                    "sample_rate": None,
                    "duration_sec": None,
                    "native_outputs": None,
                    "raw_output_shapes": None,
                    "raw_output_sha256": None,
                    "runtime_sec": float(time.perf_counter() - attempt_started),
                    "peak_vram_bytes": int(torch.cuda.max_memory_allocated(device)) if device.type == "cuda" else 0,
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
    del fdn, prn
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
