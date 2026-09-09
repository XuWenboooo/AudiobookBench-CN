"""Day 5 engineering pipeline: temporal grid, frame features, validation, figures.

Read-only over all frozen Day 4.5 artifacts. Outputs:

- results/day5_validation/day5_precheck.json
- results/day5_validation/day5_frame_metadata_clean.csv / _a0.csv / _a1.csv
- results/day5_validation/day5_sequence_summary.csv
- results/day5_validation/day5_record_validation.csv
- results/day5_validation/day5_pair_alignment.csv
- results/day5_debug_figures/day5_debug_<case>.png (5 sampled pairs, fixed seed)

No model is trained, no detector/classifier/localization/AUROC/EER computation
is performed anywhere in this pipeline.
"""
from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from audiobookbench.preprocessing.audio_io import load_audio, probe_audio
from audiobookbench.security.day5_precheck import (
    REPO_ROOT,
    OUTPUT_HASH_CSV,
    ATTACK_MANIFEST_CSV,
    run_day5_precheck,
    save_precheck_report,
)
from audiobookbench.temporal.day5_figures import plot_pair_trajectories
from audiobookbench.temporal.day5_validation import (
    interval_label,
    overlap_flags,
    validate_pair_alignment,
    validate_record_frames,
    validate_ground_truth_intervals,
)
from audiobookbench.temporal.frame_features import (
    EMBEDDING_REASON,
    EMBEDDING_STATUS,
    extract_frame_features,
    sequence_summary,
)
from audiobookbench.temporal.grid import TemporalGrid, frame_record, overlap_fraction

RESULTS_DIR = REPO_ROOT / "results/day5_validation"
FIGURES_DIR = REPO_ROOT / "results/day5_debug_figures"
FIGURE_SEED = 20260904
FIGURE_CASE_COUNT = 5

VARIANT_BY_ATTACK_TYPE = {
    "cross_speaker_splice": "a0",
    "artifact_controlled_cross_speaker_splice": "a1",
}

FRAME_METADATA_COLUMNS = [
    "record_id", "variant", "paired_case_id", "split", "speaker",
    "frame_index", "frame_start_sample", "frame_end_sample", "frame_center_sample",
    "t_start", "t_center", "t_end",
    "energy", "log_energy", "rms", "f0_hz", "voiced_ratio", "pause_ratio",
    "overlap_target", "in_target", "overlap_attack", "in_attack",
    "overlap_core", "in_core", "overlap_blend", "in_blend",
]

SEQUENCE_SUMMARY_COLUMNS = [
    "record_id", "variant", "paired_case_id", "split", "speaker",
    "num_samples", "duration_s", "frame_count",
    "voiced_ratio", "pause_ratio", "f0_mean", "f0_std",
    "energy_mean", "rms_mean", "f0_backend",
    "probe_frames", "probe_sample_rate", "probe_channels", "probe_duration",
    "duration_match", "gt_intervals_valid", "passed", "problems",
]

PAIR_ALIGNMENT_COLUMNS = ["paired_case_id", "clean_sequence_id", "problems", "passed"]

RECORD_VALIDATION_COLUMNS = [
    "record_id", "variant", "num_samples", "expected_frame_count",
    "metadata_frame_count", "waveform_finite", "features_finite", "passed", "problems",
]


def _parse_sequence_identity(sequence_id: str) -> tuple[str, str]:
    """Extract ``(split, speaker)`` from a ``day45_<split>_<speaker>_seqNNN`` id."""
    body = sequence_id[len("day45_"):] if sequence_id.startswith("day45_") else sequence_id
    parts = body.split("_")
    if len(parts) >= 2 and parts[0] in {"train", "val", "test"}:
        return parts[0], parts[1]
    return "unknown", "unknown"


def _load_records(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    hash_rows = _read_csv(repo_root, OUTPUT_HASH_CSV)
    manifest_rows = _read_csv(repo_root, ATTACK_MANIFEST_CSV)
    clean_records = [
        {
            "record_id": row["artifact_id"],
            "variant": "clean",
            "paired_case_id": "",
            "audio_relpath": row["audio_relpath"],
        }
        for row in hash_rows
        if row["artifact_type"] == "clean"
    ]
    manipulated_records = [
        {
            "record_id": row["manipulated_sequence_id"],
            "variant": VARIANT_BY_ATTACK_TYPE[str(row["attack_type"])],
            "paired_case_id": row["paired_case_id"],
            "split": row["split"],
            "clean_sequence_id": row["clean_sequence_id"],
            "manifest_row": row,
            # Prefer the repository-relative field so a frozen manifest can
            # move between machines without retaining its creator's drive.
            "audio_path": str(
                repo_root
                / row.get("manipulated_audio_relpath", row["manipulated_audio_path"])
            ),
        }
        for row in manifest_rows
    ]
    records = clean_records + manipulated_records
    return records, manifest_rows


def _read_csv(repo_root: Path, relative: str) -> list[dict[str, str]]:
    with (repo_root / relative).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _intervals_from_manifest(row: Mapping[str, str]) -> dict[str, tuple[int, int]]:
    return {
        "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
        "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
    }


def _seconds_from_manifest(row: Mapping[str, str]) -> dict[str, tuple[float, float]]:
    return {
        "target": (float(row["target_start"]), float(row["target_end"])),
        "attack": (float(row["attack_start"]), float(row["attack_end"])),
        "core": (float(row["attack_core_start"]), float(row["attack_core_end"])),
        "blend": (float(row["blend_start"]), float(row["blend_end"])),
    }


def run_day5(repo_root: Path = REPO_ROOT, *, sample_rate: int = 16000) -> dict[str, Any]:
    grid = TemporalGrid(sample_rate=sample_rate)
    results_dir = repo_root / "results/day5_validation"
    figures_dir = repo_root / "results/day5_debug_figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    precheck = run_day5_precheck(repo_root)
    save_precheck_report(precheck, results_dir / "day5_precheck.json")

    records, manifest_rows = _load_records(repo_root)
    manifest_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in manifest_rows:
        manifest_by_case[row["paired_case_id"]].append(row)

    selected_cases = _sample_cases(manifest_by_case)
    selected_case_ids = {case for case, _, _ in selected_cases}
    selected_clean_ids = {
        manifest_by_case[case][0]["clean_sequence_id"] for case in selected_case_ids
    }
    clean_to_case: dict[str, str] = {}
    for case_id, case_rows in manifest_by_case.items():
        clean_to_case[case_rows[0]["clean_sequence_id"]] = case_id

    writers: dict[str, csv.DictWriter] = {}
    files: dict[str, Any] = {}
    for variant in ("clean", "a0", "a1"):
        handle = (results_dir / f"day5_frame_metadata_{variant}.csv").open("w", encoding="utf-8", newline="")
        writer = csv.DictWriter(handle, fieldnames=FRAME_METADATA_COLUMNS)
        writer.writeheader()
        writers[variant] = writer
        files[variant] = handle

    sequence_rows: list[dict[str, Any]] = []
    record_validation_rows: list[dict[str, Any]] = []
    decoded_info: dict[str, tuple[int, int]] = {}
    kept_rows: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    f0_backend_counts: dict[str, int] = defaultdict(int)

    for record in records:
        record_id = record["record_id"]
        variant = record["variant"]
        path = (
            repo_root / record["audio_relpath"] if variant == "clean" else Path(record["audio_path"])
        )
        info = probe_audio(path)
        waveform, sr = load_audio(path, target_sr=None)
        decoded_info[record_id] = (int(waveform.size), int(sr))

        base_identity = {
            "record_id": record_id,
            "variant": variant,
            "paired_case_id": record.get("paired_case_id", ""),
            "split": record.get("split") or _parse_sequence_identity(record_id)[0],
            "speaker": (
                _parse_sequence_identity(str(record.get("clean_sequence_id", record_id)))[1]
            ),
        }

        features = extract_frame_features(waveform, grid)
        f0_backend_counts[str(features["f0_backend"])] += 1

        intervals = (
            _intervals_from_manifest(record["manifest_row"]) if variant != "clean" else {}
        )
        rows: list[dict[str, Any]] = []
        for index in range(grid.frame_count(waveform.size)):
            row = frame_record(grid, index, base_identity)
            row["energy"] = f"{features['energy'][index]:.8f}"
            row["log_energy"] = f"{features['log_energy'][index]:.6f}"
            row["rms"] = f"{features['rms'][index]:.8f}"
            row["f0_hz"] = f"{features['f0_hz'][index]:.4f}" if np.isfinite(features["f0_hz"][index]) else "nan"
            row["voiced_ratio"] = f"{features['voiced_ratio'][index]:.1f}"
            row["pause_ratio"] = f"{features['pause_ratio'][index]:.1f}"
            if intervals:
                start, end = grid.frame_bounds(index)
                overlaps = overlap_flags(start, end, intervals)
                for name, fraction in overlaps.items():
                    row[f"overlap_{name}"] = f"{fraction:.6f}"
                    row[f"in_{name}"] = interval_label(fraction)
            else:
                for name in ("target", "attack", "core", "blend"):
                    row[f"overlap_{name}"] = "0.000000"
                    row[f"in_{name}"] = "none"
            rows.append(row)
        writers[variant].writerows(rows)

        if variant == "clean" and record_id in selected_clean_ids:
            case_id = clean_to_case.get(record_id, "")
            if case_id in selected_case_ids:
                kept_rows[case_id]["clean"] = rows
        if variant != "clean" and record["paired_case_id"] in selected_case_ids:
            kept_rows[record["paired_case_id"]][variant] = rows

        validation = validate_record_frames(waveform, grid, rows, features)
        gt_problems: list[str] = []
        if variant != "clean":
            gt_problems = validate_ground_truth_intervals(record["manifest_row"], int(waveform.size), sr)
        record_validation_rows.append({
            "record_id": record_id,
            "variant": variant,
            "num_samples": validation["num_samples"],
            "expected_frame_count": validation["expected_frame_count"],
            "metadata_frame_count": validation["metadata_frame_count"],
            "waveform_finite": validation["waveform_finite"],
            "features_finite": validation["features_finite"],
            "passed": validation["passed"] and not gt_problems,
            "problems": "; ".join(validation["problems"] + gt_problems),
        })

        duration_match = (
            info.frames == waveform.size
            and info.sample_rate == sr == sample_rate
            and info.channels == 1
        )
        summary = sequence_summary(features, grid)
        sequence_rows.append({
            "record_id": record_id,
            "variant": variant,
            "paired_case_id": record.get("paired_case_id", ""),
            "split": base_identity["split"],
            "speaker": base_identity["speaker"],
            "num_samples": int(waveform.size),
            "duration_s": f"{waveform.size / sr:.6f}",
            "frame_count": summary["frame_count"],
            "voiced_ratio": f"{summary['voiced_ratio']:.6f}",
            "pause_ratio": f"{summary['pause_ratio']:.6f}",
            "f0_mean": f"{summary['f0_mean']:.4f}" if np.isfinite(summary["f0_mean"]) else "nan",
            "f0_std": f"{summary['f0_std']:.4f}" if np.isfinite(summary["f0_std"]) else "nan",
            "energy_mean": f"{summary['energy_mean']:.8f}",
            "rms_mean": f"{summary['rms_mean']:.8f}",
            "f0_backend": features["f0_backend"],
            "probe_frames": info.frames,
            "probe_sample_rate": info.sample_rate,
            "probe_channels": info.channels,
            "probe_duration": f"{info.duration:.6f}",
            "duration_match": duration_match,
            "gt_intervals_valid": not gt_problems if variant != "clean" else True,
            "passed": duration_match and validation["passed"] and not gt_problems,
            "problems": "; ".join(validation["problems"] + gt_problems),
        })

    for handle in files.values():
        handle.close()

    pair_alignment_rows = []
    for case_id, case_rows in sorted(manifest_by_case.items()):
        clean_id = case_rows[0]["clean_sequence_id"]
        decoded_subset = dict(decoded_info)
        alignment = validate_pair_alignment({"clean_sequence_id": clean_id}, case_rows, decoded_subset)
        pair_alignment_rows.append({
            "paired_case_id": alignment["paired_case_id"],
            "clean_sequence_id": alignment["clean_sequence_id"],
            "problems": "; ".join(alignment["problems"]),
            "passed": alignment["passed"],
        })

    figure_paths = _render_figures(grid, selected_cases, kept_rows, figures_dir)

    _write_csv(results_dir / "day5_sequence_summary.csv", sequence_rows, SEQUENCE_SUMMARY_COLUMNS)
    _write_csv(results_dir / "day5_record_validation.csv", record_validation_rows, RECORD_VALIDATION_COLUMNS)
    _write_csv(results_dir / "day5_pair_alignment.csv", pair_alignment_rows, PAIR_ALIGNMENT_COLUMNS)

    summary = {
        "pipeline": "day5_temporal_signals",
        "grid": {
            "frame_length": grid.frame_length,
            "hop_length": grid.hop_length,
            "sample_rate": grid.sample_rate,
            "frame_seconds": grid.frame_length / grid.sample_rate,
            "hop_seconds": grid.hop_length / grid.sample_rate,
        },
        "records": {
            "clean": sum(1 for r in records if r["variant"] == "clean"),
            "a0": sum(1 for r in records if r["variant"] == "a0"),
            "a1": sum(1 for r in records if r["variant"] == "a1"),
            "total": len(records),
        },
        "total_frames": sum(int(row["frame_count"]) for row in sequence_rows),
        "f0_backend_usage": dict(f0_backend_counts),
        "speaker_embedding_status": EMBEDDING_STATUS,
        "speaker_embedding_reason": EMBEDDING_REASON,
        "records_passed": sum(1 for row in sequence_rows if row["passed"]),
        "records_failed": [row["record_id"] for row in sequence_rows if not row["passed"]],
        "pairs_aligned": sum(1 for row in pair_alignment_rows if row["passed"]),
        "pairs_total": len(pair_alignment_rows),
        "precheck_all_passed": precheck["all_passed"],
        "figures": [str(p) for p in figure_paths],
    }
    (results_dir / "day5_pipeline_summary.json").write_text(
        json_dumps(summary), encoding="utf-8",
    )
    return summary


def _sample_cases(
    manifest_by_case: Mapping[str, list[dict[str, str]]],
) -> list[tuple[str, str, dict[str, tuple[float, float]]]]:
    """Deterministically sample debug cases: (case_id, split, gt_seconds)."""
    rng = random.Random(FIGURE_SEED)
    case_ids = sorted(manifest_by_case)
    chosen = sorted(rng.sample(case_ids, min(FIGURE_CASE_COUNT, len(case_ids))))
    out = []
    for case_id in chosen:
        rows = manifest_by_case[case_id]
        out.append((case_id, rows[0]["split"], _seconds_from_manifest(rows[0])))
    return out


def _render_figures(
    grid: TemporalGrid,
    selected_cases: list[tuple[str, str, dict[str, tuple[float, float]]]],
    kept_rows: Mapping[str, Mapping[str, list[dict[str, Any]]]],
    figures_dir: Path,
) -> list[Path]:
    paths: list[Path] = []
    for case_id, split, gt_seconds in selected_cases:
        rows_for_case = kept_rows.get(case_id, {})
        if not {"clean", "a0", "a1"} <= set(rows_for_case):
            continue
        out_path = figures_dir / f"day5_debug_{case_id}.png"
        paths.append(plot_pair_trajectories(
            grid,
            rows_for_case["clean"],
            rows_for_case["a0"],
            rows_for_case["a1"],
            gt_seconds,
            case_id,
            split,
            out_path,
        ))
    return paths


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Day 5 temporal-signal pipeline.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    summary = run_day5(Path(args.repo_root))
    print(json_dumps(summary))
    return 0 if summary["records_failed"] == [] and summary["pairs_aligned"] == summary["pairs_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
