"""Week-1 frozen-chain verification and representative core reproduction.

This entry never regenerates the research dataset and never overwrites Day
3--Day 6C results. ``--verify-only`` hashes frozen artifacts. The
``--reproduce-core`` mode also reruns representative Day 5, 6A, 6B and 6C
links, writing C0 reconstruction only into an automatically removed temp dir.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify_frozen_hashes(repo_root: Path) -> dict[str, Any]:
    expected: list[tuple[str, Path, str]] = []
    protected = _read_csv(repo_root / "data/generated/day45_paired/metadata/protected_artifact_hashes.csv")
    for row in protected:
        expected.append((row["artifact_group"], repo_root / row["path"], row["sha256_before"]))
    for row in _read_csv(repo_root / "data/generated/day45_paired/metadata/output_audio_hashes.csv"):
        expected.append(("day45_outputs", repo_root / row["audio_relpath"], row["sha256"]))

    cfg = yaml.safe_load((repo_root / "configs/day45_expanded_paired.yaml").read_text(encoding="utf-8"))
    dataset_root = Path(os.environ.get("AUDIOBOOKBENCH_DATASET_ROOT") or cfg["dataset_root"])
    for row in _read_csv(repo_root / "data/generated/day45_paired/metadata/source_input_hashes.csv"):
        relative = Path(*row["audio_relpath"].replace("\\", "/").split("/"))
        expected.append(("day45_raw_sources", dataset_root / relative, row["sha256_before"]))

    records = (
        ("day5", repo_root / "results/day6a/day5_output_hashes.json", "hashes"),
        ("day6a", repo_root / "results/day6b/day6a_frozen_record.json", "hashes"),
        ("day6b", repo_root / "results/day6c/day6b_freeze_record.json", "hashes"),
        ("day6c", repo_root / "results/day6c/day6c_final_hashes.json", None),
    )
    for group, record_path, key in records:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        hashes = payload[key] if key else payload
        expected.extend((group, repo_root / relative, digest) for relative, digest in hashes.items())
    for row in _read_csv(repo_root / "data/generated/day6c_same_speaker_control/output_audio_hashes.csv"):
        expected.append(("day6c_c0_audio", repo_root / row["audio_relpath"], row["sha256"]))

    missing, mismatches, groups = [], [], Counter()
    for group, path, digest in expected:
        groups[group] += 1
        if not path.is_file():
            missing.append(str(path))
        elif _sha256(path) != digest.upper():
            mismatches.append(str(path))
    return {"passed": not missing and not mismatches, "checked": len(expected),
            "groups": dict(sorted(groups.items())), "missing": missing, "mismatches": mismatches}


def reproduce_day5(repo_root: Path) -> dict[str, Any]:
    from audiobookbench.preprocessing.audio_io import load_audio
    from audiobookbench.temporal.day5_pipeline import _load_records
    from audiobookbench.temporal.frame_features import F0_BACKEND_PARSELMOUTH, extract_frame_features
    from audiobookbench.temporal.grid import TemporalGrid

    records, _ = _load_records(repo_root)
    record = sorted((r for r in records if r["variant"] == "clean"), key=lambda r: r["record_id"])[0]
    waveform, sr = load_audio(repo_root / record["audio_relpath"], target_sr=None)
    features = extract_frame_features(waveform, TemporalGrid(sample_rate=sr))
    saved = [r for r in _read_csv(repo_root / "results/day5_validation/day5_frame_metadata_clean.csv")
             if r["record_id"] == record["record_id"]]
    frozen = {name: np.asarray([float(r[name]) for r in saved])
              for name in ("energy", "log_energy", "rms", "f0_hz")}
    tolerances = {"energy": 6e-9, "log_energy": 6e-7, "rms": 6e-9, "f0_hz": 6e-5}
    errors: dict[str, float] = {}
    passed = len(saved) == len(features["energy"]) and features["f0_backend"] == F0_BACKEND_PARSELMOUTH
    for name, old in frozen.items():
        new = np.asarray(features[name], dtype=np.float64)
        finite = np.isfinite(new) & np.isfinite(old)
        error = float(np.max(np.abs(new[finite] - old[finite]))) if finite.any() else 0.0
        errors[name] = error
        passed = passed and np.array_equal(np.isnan(new), np.isnan(old)) and error <= tolerances[name]
    return {"passed": bool(passed), "record_id": record["record_id"], "frames": len(saved),
            "backend": features["f0_backend"], "max_abs_error": errors}


def reproduce_day6a(repo_root: Path, scale_name: str) -> dict[str, Any]:
    from audiobookbench.evaluation.day6a_localization import evaluate_windows
    from audiobookbench.temporal.aggregation import AggregationScale
    from audiobookbench.temporal.day6a_pipeline import _to_float, aggregate_record_windows, load_config, load_day5_frames
    from audiobookbench.temporal.day6a_scoring import combine_scores, compute_reference, feature_zscore_matrix
    from audiobookbench.temporal.grid import TemporalGrid

    config, grid = load_config(repo_root), TemporalGrid()
    scale = AggregationScale.from_config(next(e for e in config["aggregation"]["scales"] if e["name"] == scale_name), grid.hop_length)
    records, definitions = load_day5_frames(repo_root), config["window_features"]
    names, windows, gts = list(definitions), {}, {}
    for rid, record in records.items():
        windows[rid], gts[rid] = aggregate_record_windows(
            record, scale, grid, definitions, float(config["gt_projection"]["label_threshold"]))
    train_clean = [rid for rid, r in records.items() if r["variant"] == "clean" and r["split"] == "train"]
    source = {name: np.asarray([_to_float(row[name]) for rid in train_clean for row in windows[rid]]) for name in names}
    reference = compute_reference(source, names, eps=float(config["reference"]["eps"]))
    scores = {}
    for rid, rows in windows.items():
        z = feature_zscore_matrix({name: np.asarray([_to_float(r[name]) for r in rows]) for name in names},
                                  reference, names, cap=float(config["reference"]["z_cap"]))
        scores[rid] = combine_scores(z, config["feature_channels"], config["ablations"]["ALL"],
                                     min_valid_features=int(config["anomaly"]["min_valid_features"]))["combined"]
    stored = json.loads((repo_root / "results/day6a/metrics.json").read_text(encoding="utf-8"))
    details, passed = {}, True
    for variant in ("a0", "a1"):
        ys, ss = [], []
        for rid, rec in records.items():
            if rec["variant"] == variant and rec["split"] == "test":
                ys.extend(bool(row["is_attack_window"]) for row in gts[rid]); ss.extend(scores[rid])
        actual = evaluate_windows(np.asarray(ys), np.asarray(ss), np.nan)["auroc"]
        expected = float(stored[f"{scale_name}|ALL|full|{variant}|test"]["auroc"])
        details[variant] = {"auroc": actual, "frozen_auroc": expected}
        passed = passed and abs(actual - expected) < 1e-12 and actual < 0.5
    return {"passed": bool(passed), "reference_source": "TRAIN_CLEAN_ONLY", "scale": scale_name, "results": details}


def reproduce_day6b(repo_root: Path, scale_name: str) -> dict[str, Any]:
    from audiobookbench.evaluation.day6a_localization import auroc
    from audiobookbench.preprocessing.audio_io import load_audio
    from audiobookbench.temporal.day6b_embed import SpeakerBackend, SpeakerWindowScale, build_speaker_windows, load_config, load_records
    from audiobookbench.temporal.day6b_pipeline import load_embeddings
    from audiobookbench.temporal.day6b_scoring import b1_scores, project_ground_truth_speaker

    config, records = load_config(repo_root), load_records(repo_root)
    scale = SpeakerWindowScale.from_config(next(e for e in config["speaker_temporal_grid"]["scales"] if e["name"] == scale_name))
    representative = sorted(records)[0]
    waveform, _ = load_audio(records[representative]["audio_path"], target_sr=None)
    first = build_speaker_windows(waveform.size, scale)[0]
    fresh = SpeakerBackend().embed_windows(waveform, [(first["sample_start"], first["sample_end"])])[0]
    cached = load_embeddings(repo_root, scale_name, representative)[0]
    cosine = float(np.dot(fresh, cached) / max(np.linalg.norm(fresh) * np.linalg.norm(cached), 1e-12))
    stored = json.loads((repo_root / "results/day6b/metrics.json").read_text(encoding="utf-8"))
    details, passed = {}, cosine > 0.999
    for variant in ("a0", "a1"):
        ys, ss = [], []
        for rid, rec in records.items():
            if rec["variant"] != variant or rec["split"] != "test":
                continue
            emb = load_embeddings(repo_root, scale_name, rid)
            wins = build_speaker_windows(scale.window_samples + (len(emb) - 1) * scale.hop_samples, scale)
            row = rec["manifest_row"]
            intervals = {
                "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
                "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
                "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
                "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
            }
            ys.extend(bool(r["is_attack_window"]) for r in project_ground_truth_speaker(wins, intervals, 0.5))
            ss.extend(b1_scores(emb, trimmed=True))
        actual = auroc(np.asarray(ys), np.asarray(ss))
        expected = float(stored[f"{scale_name}|B1b|full|{variant}|test"]["auroc"])
        details[variant] = {"auroc": actual, "frozen_auroc": expected}
        passed = passed and abs(actual - expected) < 1e-12
    return {"passed": bool(passed), "scale": scale_name, "representative_record": representative,
            "fresh_vs_cached_cosine": cosine, "results": details}


def reproduce_day6c_c0(repo_root: Path, temporary: Path) -> dict[str, Any]:
    from audiobookbench.preprocessing.audio_io import load_audio, write_audio
    from audiobookbench.security.day6c_same_speaker import CROSSFADE, GAIN_MAX, GAIN_MIN, _crossfade_replace, _rms

    rows = _read_csv(repo_root / "data/manifests/day6c_same_speaker_control_manifest.csv")
    case_id = sorted({r["paired_case_id"] for r in rows})[0]
    pair = {r["control_variant"]: r for r in rows if r["paired_case_id"] == case_id}
    a0 = next(r for r in _read_csv(repo_root / "data/manifests/day45_attack_manifest.csv")
              if r["paired_case_id"] == case_id and r["attack_type"] == "cross_speaker_splice")
    sources = {r["sample_id"]: r for r in _read_csv(repo_root / "data/manifests/day45_source_audio.csv")}
    cfg = yaml.safe_load((repo_root / "configs/day45_expanded_paired.yaml").read_text(encoding="utf-8"))
    dataset_root = Path(os.environ.get("AUDIOBOOKBENCH_DATASET_ROOT") or cfg["dataset_root"])
    clean, _ = load_audio(repo_root / a0["clean_audio_relpath"], target_sr=None)
    donor_row = sources[pair["C0A"]["donor_source_sample_id"]]
    donor_path = dataset_root / Path(*donor_row["audio_relpath"].replace("\\", "/").split("/"))
    donor, _ = load_audio(donor_path, target_sr=16000)
    start, end = int(a0["target_start_sample"]), int(a0["target_end_sample"]); needed = end - start
    crop = donor[max(0, (donor.size - needed) // 2):][:needed].astype(np.float64)
    gain = float(np.clip(_rms(clean[start:end]) / max(_rms(crop.astype(np.float32)), 1e-8), GAIN_MIN, GAIN_MAX))
    rebuilt = {"C0A": clean.copy(), "C0B": _crossfade_replace(clean, (crop * gain).astype(np.float32), start, end, CROSSFADE)}
    rebuilt["C0A"][start:end] = crop.astype(np.float32)
    details, passed = {}, True
    for variant, waveform in rebuilt.items():
        out = temporary / f"{case_id}_{variant}.wav"; write_audio(out, waveform, 16000)
        digest, expected = _sha256(out), pair[variant]["control_audio_sha256"]
        details[variant] = {"sha256": digest, "frozen_sha256": expected}; passed = passed and digest == expected
    lineage_ok = (pair["C0A"]["target_speaker"] == pair["C0A"]["donor_speaker"]
                  and pair["C0A"]["split"] == donor_row["split"]
                  and pair["C0A"]["target_source_sample_id"] != donor_row["sample_id"])
    return {"passed": bool(passed and lineage_ok), "paired_case_id": case_id,
            "lineage_ok": lineage_ok, "waveforms": details}


def reproduce_day6c_mask(repo_root: Path, scale_name: str) -> dict[str, Any]:
    from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, build_speaker_windows, load_config, load_records
    from audiobookbench.temporal.day6b_pipeline import load_embeddings
    from audiobookbench.temporal.day6b_scoring import project_ground_truth_speaker
    from audiobookbench.temporal.day6c_pipeline import SPEECH_ACTIVE_THRESHOLD, speech_active_fractions

    config, records = load_config(repo_root), load_records(repo_root)
    scale = SpeakerWindowScale.from_config(next(e for e in config["speaker_temporal_grid"]["scales"] if e["name"] == scale_name))
    fractions = speech_active_fractions(repo_root, scale)
    orig_pos = orig_neg = kept_pos = kept_neg = 0
    for rid, rec in records.items():
        if rec["variant"] != "a0" or rec["split"] != "test":
            continue
        emb = load_embeddings(repo_root, scale_name, rid)
        wins = build_speaker_windows(scale.window_samples + (len(emb) - 1) * scale.hop_samples, scale)
        row = rec["manifest_row"]
        intervals = {
            "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
            "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
            "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
            "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
        }
        pos = np.asarray([r["is_attack_window"] for r in project_ground_truth_speaker(wins, intervals, 0.5)], dtype=bool)
        keep = fractions[rid][:len(pos)] >= SPEECH_ACTIVE_THRESHOLD
        orig_pos += int(pos.sum()); orig_neg += int((~pos).sum())
        kept_pos += int((pos & keep).sum()); kept_neg += int((~pos & keep).sum())
    frozen = next(r for r in _read_csv(repo_root / "results/day6c/speech_mask_population_audit.csv")
                  if r["scale"] == scale_name and r["variant"] == "a0" and r["split"] == "test" and r["gt"] == "full")
    actual = {"original_positives": orig_pos, "original_negatives": orig_neg,
              "positive_retention": kept_pos / orig_pos, "negative_retention": kept_neg / orig_neg}
    passed = (orig_pos == int(frozen["original_positives"]) and orig_neg == int(frozen["original_negatives"])
              and abs(actual["positive_retention"] - float(frozen["positive_retention"])) < 1e-6
              and abs(actual["negative_retention"] - float(frozen["negative_retention"])) < 1e-6)
    return {"passed": bool(passed), "scale": scale_name, "slice": "a0/test/full", **actual}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify or reproduce the frozen Week-1 experiment chain.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-only", action="store_true")
    modes.add_argument("--reproduce-core", action="store_true")
    parser.add_argument("--config", default="configs/week1.yaml")
    parser.add_argument("--log", default=None, help="Optional JSON log path; omitted means stdout only.")
    args = parser.parse_args(argv)
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    result: dict[str, Any] = {"protocol": config["protocol"],
                              "mode": "reproduce-core" if args.reproduce_core else "verify-only"}
    result["hashes"] = verify_frozen_hashes(REPO_ROOT)
    if args.reproduce_core:
        with tempfile.TemporaryDirectory(prefix="audiobookbench_week1_") as temporary:
            result["day5"] = reproduce_day5(REPO_ROOT)
            result["day6a"] = reproduce_day6a(REPO_ROOT, config["reproduction"]["day6a_scale"])
            result["day6b"] = reproduce_day6b(REPO_ROOT, config["reproduction"]["day6b_scale"])
            result["day6c_c0"] = reproduce_day6c_c0(REPO_ROOT, Path(temporary))
            result["day6c_speech_mask"] = reproduce_day6c_mask(REPO_ROOT, config["reproduction"]["day6c_scale"])
    result["passed"] = all(value.get("passed", True) for value in result.values() if isinstance(value, dict))
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.log:
        log_path = Path(args.log)
        if not log_path.is_absolute():
            log_path = REPO_ROOT / log_path
        log_path.parent.mkdir(parents=True, exist_ok=True); log_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
