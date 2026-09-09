"""Frozen Day12 mechanism-analysis entry points (T19-only and full modes)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from audiobookbench.preprocessing.audio_io import load_audio
from audiobookbench.temporal.day6b_embed import EMBEDDING_DIM, SpeakerBackend
from audiobookbench.temporal.day6b_scoring import cosine_to
from audiobookbench.temporal.frame_features import frame_energies, pause_indicator
from audiobookbench.temporal.grid import TemporalGrid


DAY10_SIDECAR = REPO_ROOT / "results/day10/a2_sidecar.csv"
DAY12_DIR = REPO_ROOT / "results/day12"
T19_CSV = DAY12_DIR / "t19_silence_distribution_shift.csv"
T19_REPORT = DAY12_DIR / "t19_silence_distribution_shift_report.md"
P1_SIMILARITY_CSV = DAY12_DIR / "per_case_similarity.csv"
P1_ASSOCIATION_CSV = DAY12_DIR / "p1_association.csv"
P1_BOOTSTRAP_CSV = DAY12_DIR / "p1_bootstrap_ci.csv"
D2_CSV = DAY12_DIR / "d2_reference_synthetic_cosine.csv"
EXECUTION_RECORD = DAY12_DIR / "execution_record.json"
OUTPUT_HASHES = DAY12_DIR / "day12_output_hashes.json"
SAMPLE_RATE = 16000
FRAME_MS = 25
HOP_MS = 10
PAUSE_THRESHOLD_DBFS = -45.0
SUCCESS = "success"
FROZEN_SPLIT_COUNTS = {"train": 11, "val": 6, "test": 6}

AudioLoader = Callable[[str, int | None], tuple[np.ndarray, int]]


class T19IntegrityError(ValueError):
    """Raised when frozen provenance or a required signal is invalid."""


class FullDay12IntegrityError(RuntimeError):
    """Raised before output writing when a frozen full-Day12 input is invalid."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _integer(row: dict[str, str], field: str) -> int:
    try:
        value = int(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise T19IntegrityError(f"{row.get('paired_case_id', '<unknown>')}: invalid {field}") from exc
    return value


def pause_fraction(waveform: np.ndarray) -> tuple[float, int]:
    """Return the frozen Day5 pause fraction over complete 25-ms frames only."""
    signal = np.asarray(waveform, dtype=np.float32)
    if signal.ndim != 1 or signal.size == 0 or not np.isfinite(signal).all():
        raise T19IntegrityError("waveform must be non-empty, mono, and finite")
    grid = TemporalGrid()
    rms = np.asarray(frame_energies(signal, grid)["rms"], dtype=np.float64)
    if rms.size == 0 or not np.isfinite(rms).all():
        raise T19IntegrityError("region has no finite complete Day5 frames")
    indicators = pause_indicator(rms, threshold_db=PAUSE_THRESHOLD_DBFS)
    value = float(np.mean(indicators))
    if not np.isfinite(value):
        raise T19IntegrityError("pause fraction is non-finite")
    return value, int(indicators.size)


def _load_region(
    path: str,
    start: int,
    end: int,
    loader: AudioLoader,
    case_id: str,
    label: str,
    *,
    require_complete_waveform: bool = False,
) -> tuple[np.ndarray, int]:
    waveform, sample_rate = loader(path, SAMPLE_RATE)
    waveform = np.asarray(waveform, dtype=np.float32)
    if sample_rate != SAMPLE_RATE:
        raise T19IntegrityError(f"{case_id}: {label} sample rate is not {SAMPLE_RATE}")
    if waveform.ndim != 1 or not np.isfinite(waveform).all():
        raise T19IntegrityError(f"{case_id}: {label} waveform is not finite mono audio")
    if start < 0 or end <= start or end > waveform.size:
        raise T19IntegrityError(f"{case_id}: invalid {label} region [{start}, {end})")
    if require_complete_waveform and start == 0 and end != waveform.size:
        raise T19IntegrityError(f"{case_id}: {label} does not equal the complete source utterance")
    return waveform[start:end], sample_rate


def _validate_sidecar_row(row: dict[str, str]) -> None:
    case_id = row.get("paired_case_id", "<unknown>")
    required = (
        "paired_case_id", "split", "generation_status", "source_audio_path",
        "manipulated_audio_path", "source_real_num_samples", "attack_start_sample",
        "attack_end_sample", "final_synthetic_num_samples", "source_sample_id",
        "target_speaker",
    )
    missing = [name for name in required if not row.get(name)]
    if missing:
        raise T19IntegrityError(f"{case_id}: missing provenance fields {missing}")
    if row["split"] not in FROZEN_SPLIT_COUNTS:
        raise T19IntegrityError(f"{case_id}: invalid split {row['split']!r}")
    source_end = _integer(row, "source_real_num_samples")
    attack_start = _integer(row, "attack_start_sample")
    attack_end = _integer(row, "attack_end_sample")
    synthetic_n = _integer(row, "final_synthetic_num_samples")
    if source_end <= 0 or attack_start < 0 or attack_end - attack_start != synthetic_n:
        raise T19IntegrityError(f"{case_id}: inconsistent frozen region provenance")


def build_t19_rows(
    sidecar_rows: Iterable[dict[str, str]],
    *,
    loader: AudioLoader = load_audio,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Materialize only the T19 per-success-case diagnostic rows.

    Failed sidecar rows are returned separately so the caller can retain them in
    denominators without attempting to read a nonexistent waveform.
    """
    rows = list(sidecar_rows)
    case_ids = [row.get("paired_case_id", "") for row in rows]
    if not rows or "" in case_ids or len(case_ids) != len(set(case_ids)):
        raise T19IntegrityError("sidecar must contain unique non-empty paired_case_id values")
    for row in rows:
        _validate_sidecar_row(row)

    output: list[dict[str, Any]] = []
    unavailable: list[dict[str, str]] = []
    for row in rows:
        if row["generation_status"].lower() != SUCCESS:
            unavailable.append(row)
            continue
        case_id = row["paired_case_id"]
        real_end = _integer(row, "source_real_num_samples")
        attack_start = _integer(row, "attack_start_sample")
        attack_end = _integer(row, "attack_end_sample")
        real, sample_rate = _load_region(
            row["source_audio_path"], 0, real_end, loader, case_id, "removed-real",
            require_complete_waveform=True,
        )
        inserted, _ = _load_region(
            row["manipulated_audio_path"], attack_start, attack_end, loader, case_id, "inserted-synthetic"
        )
        real_pause, real_frames = pause_fraction(real)
        synthetic_pause, synthetic_frames = pause_fraction(inserted)
        delta = synthetic_pause - real_pause
        if not np.isfinite(delta):
            raise T19IntegrityError(f"{case_id}: pause delta is non-finite")
        output.append(
            {
                "paired_case_id": case_id,
                "split": row["split"],
                "source_sample_id": row["source_sample_id"],
                "speaker": row["target_speaker"],
                "real_region_start_sample": 0,
                "real_region_end_sample": real_end,
                "synthetic_region_start_sample": attack_start,
                "synthetic_region_end_sample": attack_end,
                "real_pause_fraction": real_pause,
                "synthetic_pause_fraction": synthetic_pause,
                "delta_pause_fraction": delta,
                "real_frame_count": real_frames,
                "synthetic_frame_count": synthetic_frames,
                "sample_rate": sample_rate,
                "frame_ms": FRAME_MS,
                "hop_ms": HOP_MS,
                "pause_threshold_dbfs": PAUSE_THRESHOLD_DBFS,
                "status": "PASS",
                "provenance_valid": True,
                "diagnostic_label": "DIAGNOSTIC_ONLY",
            }
        )
    return output, unavailable


def summarize_t19(
    computed_rows: list[dict[str, Any]],
    all_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Descriptive, case-level T19 summaries without an inferential test."""
    expected = Counter(row["split"] for row in all_rows)
    summaries: list[dict[str, Any]] = []
    for split in ("all", "train", "val", "test"):
        all_subset = all_rows if split == "all" else [row for row in all_rows if row["split"] == split]
        values = computed_rows if split == "all" else [row for row in computed_rows if row["split"] == split]
        if not values:
            raise T19IntegrityError(f"{split}: no computable successful cases")
        def aggregate(field: str, method: Callable[[np.ndarray], float]) -> float:
            data = np.asarray([row[field] for row in values], dtype=np.float64)
            value = float(method(data))
            if not np.isfinite(value):
                raise T19IntegrityError(f"{split}: non-finite {field} summary")
            return value
        summaries.append(
            {
                "population": split,
                "n_realized": len(all_subset),
                "n_computable": len(values),
                "n_unavailable": len(all_subset) - len(values),
                "real_pause_fraction_mean": aggregate("real_pause_fraction", np.mean),
                "real_pause_fraction_median": aggregate("real_pause_fraction", np.median),
                "synthetic_pause_fraction_mean": aggregate("synthetic_pause_fraction", np.mean),
                "synthetic_pause_fraction_median": aggregate("synthetic_pause_fraction", np.median),
                "delta_pause_fraction_mean": aggregate("delta_pause_fraction", np.mean),
                "delta_pause_fraction_median": aggregate("delta_pause_fraction", np.median),
                "diagnostic_label": "DIAGNOSTIC_ONLY",
                "status": "PASS",
            }
        )
    if expected != Counter(FROZEN_SPLIT_COUNTS):
        raise T19IntegrityError(f"frozen split accounting mismatch: {dict(expected)}")
    return summaries


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise T19IntegrityError(f"cannot write empty {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_t19_report(summaries: list[dict[str, Any]]) -> str:
    """Render a diagnostic-only report; its numerical contents are descriptive."""
    lines = [
        "# Day12 T19 silence-distribution-shift diagnostic",
        "",
        "**DIAGNOSTIC ONLY.** This report is not a detector-performance claim,",
        "does not change P1/D2, and contains no inferential test or threshold.",
        "",
        "| Population | Realized | Computable | Unavailable | Real pause mean | Inserted pause mean | Delta mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            "| {population} | {n_realized} | {n_computable} | {n_unavailable} | "
            "{real_pause_fraction_mean:.6f} | {synthetic_pause_fraction_mean:.6f} | "
            "{delta_pause_fraction_mean:.6f} |".format(**row)
        )
    return "\n".join(lines) + "\n"


def run_t19(
    repo_root: Path = REPO_ROOT,
    *,
    sidecar_path: Path | None = None,
    output_csv: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Any]:
    """Execute the frozen T19 diagnostic and write its two canonical outputs."""
    root = Path(repo_root)
    sidecar = Path(sidecar_path) if sidecar_path is not None else root / "results/day10/a2_sidecar.csv"
    output = Path(output_csv) if output_csv is not None else root / "results/day12/t19_silence_distribution_shift.csv"
    report = Path(report_path) if report_path is not None else root / "results/day12/t19_silence_distribution_shift_report.md"
    all_rows = _read_csv(sidecar)
    computed, unavailable = build_t19_rows(all_rows)
    summaries = summarize_t19(computed, all_rows)
    _write_csv(output, computed)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_t19_report(summaries), encoding="utf-8")
    return {
        "status": "PASS",
        "diagnostic_label": "DIAGNOSTIC_ONLY",
        "sidecar": str(sidecar),
        "output_csv": str(output),
        "report": str(report),
        "n_realized": len(all_rows),
        "n_computable": len(computed),
        "n_unavailable": len(unavailable),
        "split_counts": dict(Counter(row["split"] for row in all_rows)),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _verify_hashed_files(root: Path, manifest_path: Path, *, required_path: str) -> dict[str, Any]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        items = manifest["files"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise FullDay12IntegrityError(f"invalid frozen manifest: {manifest_path}") from exc
    paths = {str(item.get("path")): item for item in items if isinstance(item, dict)}
    if required_path not in paths:
        raise FullDay12IntegrityError(f"frozen manifest lacks {required_path}")
    for relative, item in paths.items():
        path = root / relative
        if not path.is_file() or path.stat().st_size != int(item.get("bytes", -1)) or _sha256(path) != item.get("sha256"):
            raise FullDay12IntegrityError(f"frozen input hash mismatch: {relative}")
    return manifest


def verify_day10_inputs(root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Fail-closed verification of the frozen Day10 sidecar and waveform hashes."""
    freeze_path = root / "results/day10/day10_output_hashes.json"
    sidecar_path = root / "results/day10/a2_sidecar.csv"
    try:
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        sidecar = _read_csv(sidecar_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise FullDay12IntegrityError("Day10 frozen input is unreadable") from exc
    if freeze.get("planned") != 23 or freeze.get("succeeded") != 23 or freeze.get("failed_by_class") not in ({}, None):
        raise FullDay12IntegrityError("Day10 denominator is not frozen 23/23")
    case_ids = [row.get("paired_case_id", "") for row in sidecar]
    if len(sidecar) != 23 or "" in case_ids or len(set(case_ids)) != 23:
        raise FullDay12IntegrityError("Day10 case population is not 23 unique cases")
    if {row.get("generation_status") for row in sidecar} != {SUCCESS}:
        raise FullDay12IntegrityError("Day10 population is not all retained successful cases")
    splits = Counter(row.get("split") for row in sidecar)
    if splits != Counter(FROZEN_SPLIT_COUNTS):
        raise FullDay12IntegrityError(f"Day10 split mismatch: {dict(splits)}")
    frozen = {str(item.get("paired_case_id")): item for item in freeze.get("output_hashes", []) if isinstance(item, dict)}
    if set(frozen) != set(case_ids):
        raise FullDay12IntegrityError("Day10 waveform-hash case set mismatch")
    for row in sidecar:
        item = frozen[row["paired_case_id"]]
        path = Path(row["manipulated_audio_path"])
        if not path.is_file() or path.stat().st_size != int(item.get("bytes", -1)) or _sha256(path) != item.get("sha256"):
            raise FullDay12IntegrityError(f"Day10 waveform hash mismatch: {row['paired_case_id']}")
        _validate_sidecar_row(row)
        core_start, core_end = _integer(row, "attack_core_start_sample"), _integer(row, "attack_core_end_sample")
        attack_start, attack_end = _integer(row, "attack_start_sample"), _integer(row, "attack_end_sample")
        if not attack_start < core_start < core_end < attack_end:
            raise FullDay12IntegrityError(f"invalid strict-core bounds: {row['paired_case_id']}")
    return sidecar, freeze


def verify_day11_inputs(root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Verify every declared Day11 frozen file before reading B1b case metrics."""
    manifest_path = root / "results/day11/day11_output_hashes.json"
    manifest = _verify_hashed_files(root, manifest_path, required_path="results/day11/case_level_metrics.csv")
    try:
        return _read_csv(root / "results/day11/case_level_metrics.csv"), manifest
    except OSError as exc:
        raise FullDay12IntegrityError("Day11 case-level metrics are unreadable") from exc


def _frozen_b1b_metrics(
    metric_rows: Iterable[dict[str, str]], sidecar_rows: Iterable[dict[str, str]]
) -> dict[str, dict[str, dict[str, float]]]:
    """Read, never recompute, the two co-primary B1b full-GT outcomes."""
    expected_ids = {row["paired_case_id"] for row in sidecar_rows}
    expected_split = {row["paired_case_id"]: row["split"] for row in sidecar_rows}
    result: dict[str, dict[str, dict[str, float]]] = {"S1": {}, "S2": {}}
    scale_map = {"S1_1000ms_250ms": "S1", "S2_1500ms_250ms": "S2"}
    for row in metric_rows:
        if row.get("method") != "B1b" or row.get("gt") != "full" or row.get("scale") not in scale_map:
            continue
        case_id = row.get("case_id", "")
        scale = scale_map[row["scale"]]
        if case_id in result[scale]:
            raise FullDay12IntegrityError(f"duplicate Day11 B1b case metric: {scale}/{case_id}")
        try:
            auroc, auprc = float(row["auroc"]), float(row["auprc"])
        except (KeyError, ValueError) as exc:
            raise FullDay12IntegrityError(f"invalid Day11 B1b case metric: {scale}/{case_id}") from exc
        if case_id not in expected_ids or row.get("split") != expected_split[case_id] or not np.isfinite([auroc, auprc]).all():
            raise FullDay12IntegrityError(f"invalid Day11 B1b provenance: {scale}/{case_id}")
        result[scale][case_id] = {"auroc": auroc, "auprc": auprc}
    for scale, cases in result.items():
        if set(cases) != expected_ids:
            raise FullDay12IntegrityError(f"missing Day11 B1b full-GT metrics for {scale}")
    return result


def _embed_one(backend: SpeakerBackend, waveform: np.ndarray, label: str) -> np.ndarray:
    signal = np.asarray(waveform, dtype=np.float32)
    if signal.ndim != 1 or signal.size == 0 or not np.isfinite(signal).all():
        raise FullDay12IntegrityError(f"invalid {label} waveform")
    embedding = np.asarray(backend.embed_windows(signal, [(0, signal.size)]), dtype=np.float64)
    if embedding.shape != (1, EMBEDDING_DIM) or not np.isfinite(embedding).all():
        raise FullDay12IntegrityError(f"invalid {label} ECAPA embedding")
    return embedding[0]


def _cosine(left: np.ndarray, right: np.ndarray, label: str) -> float:
    value = float(cosine_to(np.asarray(left, dtype=np.float64)[None, :], np.asarray(right, dtype=np.float64))[0])
    if not np.isfinite(value):
        raise FullDay12IntegrityError(f"non-finite {label} cosine")
    return value


def _load_full_source(row: dict[str, str], loader: AudioLoader) -> np.ndarray:
    case_id, source_n = row["paired_case_id"], _integer(row, "source_real_num_samples")
    waveform, sr = loader(row["source_audio_path"], SAMPLE_RATE)
    signal = np.asarray(waveform, dtype=np.float32)
    if sr != SAMPLE_RATE or signal.ndim != 1 or signal.size != source_n or not np.isfinite(signal).all():
        raise FullDay12IntegrityError(f"invalid complete target-real waveform: {case_id}")
    return signal


def _load_manipulated_core(row: dict[str, str], loader: AudioLoader) -> np.ndarray:
    case_id = row["paired_case_id"]
    waveform, sr = loader(row["manipulated_audio_path"], SAMPLE_RATE)
    signal = np.asarray(waveform, dtype=np.float32)
    start, end = _integer(row, "attack_core_start_sample"), _integer(row, "attack_core_end_sample")
    if sr != SAMPLE_RATE or signal.ndim != 1 or not np.isfinite(signal).all() or start < 0 or end <= start or end > signal.size:
        raise FullDay12IntegrityError(f"invalid strict synthetic core: {case_id}")
    return signal[start:end]


def _load_reference(row: dict[str, str], loader: AudioLoader) -> np.ndarray:
    case_id = row["paired_case_id"]
    path = row.get("reference_audio_path", "")
    if not path:
        raise FullDay12IntegrityError(f"D2_REFERENCE_RESOLUTION_FAIL: {case_id}")
    waveform, sr = loader(path, SAMPLE_RATE)
    signal = np.asarray(waveform, dtype=np.float32)
    if sr != SAMPLE_RATE or signal.ndim != 1 or signal.size == 0 or not np.isfinite(signal).all():
        raise FullDay12IntegrityError(f"D2_REFERENCE_RESOLUTION_FAIL: {case_id}")
    return signal


def materialize_similarity_rows(
    sidecar_rows: Iterable[dict[str, str]], *, backend: SpeakerBackend | None = None,
    loader: AudioLoader = load_audio,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Materialize frozen P1 and D2 cosines without reading detector scores."""
    rows = list(sidecar_rows)
    extractor = backend or SpeakerBackend()
    p1_rows: list[dict[str, Any]] = []
    d2_rows: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item["paired_case_id"]):
        target = _embed_one(extractor, _load_full_source(row, loader), "target-real")
        # The strict core is the frozen pure-synthetic representation for both
        # P1 and D2; T19 separately uses the full inserted replacement.
        core = _embed_one(extractor, _load_manipulated_core(row, loader), "synthetic-core")
        p1 = _cosine(target, core, "P1")
        reference = _embed_one(extractor, _load_reference(row, loader), "reference")
        d2 = _cosine(reference, core, "D2")
        base = {
            "paired_case_id": row["paired_case_id"], "split": row["split"],
            "source_sample_id": row["source_sample_id"], "target_speaker": row["target_speaker"],
            "reference_sample_id": row.get("reference_sample_id", ""),
            "synthetic_core_start_sample": _integer(row, "attack_core_start_sample"),
            "synthetic_core_end_sample": _integer(row, "attack_core_end_sample"),
            "sample_rate": SAMPLE_RATE, "ecapa_model": "speechbrain/spkrec-ecapa-voxceleb",
            "ecapa_embedding_dim": EMBEDDING_DIM, "ecapa_device": "cpu",
        }
        p1_rows.append({**base, "target_synthetic_ecapa_cosine": p1, "status": "PASS"})
        d2_rows.append({**base, "reference_synthetic_ecapa_cosine": d2,
                        "diagnostic_label": "DIAGNOSTIC_ONLY", "status": "PASS"})
    if len(p1_rows) != 23 or {row["paired_case_id"] for row in p1_rows} != {row["paired_case_id"] for row in rows}:
        raise FullDay12IntegrityError("P1 similarity case accounting failure")
    return p1_rows, d2_rows


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import spearmanr
    result = spearmanr(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64))
    value = float(result.statistic)
    if not np.isfinite(value):
        raise FullDay12IntegrityError("undefined point-estimate Spearman rho")
    return value


def association_and_bootstrap(
    p1_rows: list[dict[str, Any]], metrics: dict[str, dict[str, dict[str, float]]],
    *, resamples: int = 2000, seed: int = 20260905,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Four co-primary, case-resampled Spearman analyses; no scale selection."""
    ids = [row["paired_case_id"] for row in sorted(p1_rows, key=lambda item: item["paired_case_id"])]
    cosine = np.asarray([row["target_synthetic_ecapa_cosine"] for row in sorted(p1_rows, key=lambda item: item["paired_case_id"])], dtype=np.float64)
    if len(ids) != 23 or not np.isfinite(cosine).all():
        raise FullDay12IntegrityError("invalid P1 association population")
    associations: list[dict[str, Any]] = []
    bootstrap: list[dict[str, Any]] = []
    for scale in ("S1", "S2"):
        for outcome, metric_key in (("AUROC", "auroc"), ("AUPRC", "auprc")):
            values = np.asarray([metrics[scale][case_id][metric_key] for case_id in ids], dtype=np.float64)
            if not np.isfinite(values).all():
                raise FullDay12IntegrityError(f"non-finite frozen {scale} {outcome} metrics")
            rho = _spearman(cosine, values)
            associations.append({"scale": scale, "outcome": outcome, "statistic": "Spearman", "rho": rho,
                                 "n_cases": len(ids), "case_unit": "paired_case_id", "status": "PASS"})
            rng = np.random.default_rng(seed)
            replicas: list[float] = []
            undefined = 0
            for _ in range(resamples):
                indices = rng.integers(0, len(ids), size=len(ids))
                try:
                    replica = _spearman(cosine[indices], values[indices])
                except FullDay12IntegrityError:
                    undefined += 1
                    continue
                replicas.append(replica)
            finite = np.asarray(replicas, dtype=np.float64)
            if finite.size == 0:
                lo = hi = float("nan")
            else:
                lo, hi = (float(value) for value in np.quantile(finite, [0.025, 0.975]))
            bootstrap.append({"scale": scale, "outcome": outcome, "statistic": "Spearman", "rho": rho,
                              "n_cases": len(ids), "bootstrap_count": resamples, "seed": seed,
                              "ci_lower": lo, "ci_upper": hi, "valid_replicates": int(finite.size),
                              "undefined_replicates": undefined, "case_unit": "paired_case_id", "status": "PASS"})
    return associations, bootstrap


def _ensure_fresh_output_dir(output_dir: Path) -> None:
    canonical = (P1_SIMILARITY_CSV.name, P1_ASSOCIATION_CSV.name, P1_BOOTSTRAP_CSV.name, D2_CSV.name,
                 T19_CSV.name, T19_REPORT.name, EXECUTION_RECORD.name, OUTPUT_HASHES.name)
    if output_dir.exists() and any((output_dir / name).exists() for name in canonical):
        raise FullDay12IntegrityError("refusing to overwrite existing Day12 canonical outputs")


def _write_output_hashes(output_dir: Path) -> dict[str, Any]:
    paths = [output_dir / name for name in (
        P1_SIMILARITY_CSV.name, P1_ASSOCIATION_CSV.name, P1_BOOTSTRAP_CSV.name, D2_CSV.name,
        T19_CSV.name, T19_REPORT.name, EXECUTION_RECORD.name,
    )]
    if not all(path.is_file() for path in paths):
        raise FullDay12IntegrityError("canonical Day12 output missing before hash freeze")
    manifest = {"artifact_type": "day12_frozen_mechanism_analysis", "files": [
        {"path": str(path.relative_to(output_dir.parents[1])).replace("\\", "/"),
         "bytes": path.stat().st_size, "sha256": _sha256(path)} for path in paths
    ]}
    _write_json(output_dir / OUTPUT_HASHES.name, manifest)
    return manifest


def run_full(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Run the complete frozen Day12 analysis; intended only for Luna's real run."""
    root = Path(repo_root)
    output_dir = root / "results/day12"
    _ensure_fresh_output_dir(output_dir)
    sidecar_rows, day10_freeze = verify_day10_inputs(root)
    metric_rows, day11_freeze = verify_day11_inputs(root)
    metrics = _frozen_b1b_metrics(metric_rows, sidecar_rows)
    # Execute T19 in memory first so any later fail-closed error leaves no
    # partial canonical scientific artifact tree.
    t19_rows, t19_unavailable = build_t19_rows(sidecar_rows, loader=load_audio)
    t19_summary = summarize_t19(t19_rows, sidecar_rows)
    if len(t19_rows) != 23 or t19_unavailable:
        raise FullDay12IntegrityError("T19 accounting failure")
    p1_rows, d2_rows = materialize_similarity_rows(sidecar_rows, loader=load_audio)
    associations, bootstrap = association_and_bootstrap(p1_rows, metrics)
    output_dir.mkdir(parents=True, exist_ok=False)
    _write_csv(output_dir / P1_SIMILARITY_CSV.name, p1_rows)
    _write_csv(output_dir / P1_ASSOCIATION_CSV.name, associations)
    _write_csv(output_dir / P1_BOOTSTRAP_CSV.name, bootstrap)
    _write_csv(output_dir / D2_CSV.name, d2_rows)
    _write_csv(output_dir / T19_CSV.name, t19_rows)
    (output_dir / T19_REPORT.name).write_text(render_t19_report(t19_summary), encoding="utf-8")
    record = {
        "status": "PASS", "execution": "frozen_day12_full", "day10_freeze_sha256": _sha256(root / "results/day10/day10_output_hashes.json"),
        "day11_freeze_sha256": _sha256(root / "results/day11/day11_output_hashes.json"),
        "cases": 23, "split": dict(Counter(row["split"] for row in sidecar_rows)),
        "p1": {"definition": "target-real_full_vs_synthetic_strict_core", "case_unit": "paired_case_id"},
        "co_primary": {"scales": ["S1", "S2"], "outcomes": ["AUROC", "AUPRC"], "statistic": "Spearman"},
        "bootstrap": {"resamples": 2000, "seed": 20260905, "unit": "paired_case_id"},
        "d2": "DIAGNOSTIC_ONLY", "t19": "DIAGNOSTIC_ONLY", "day13_entered": False,
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(output_dir / EXECUTION_RECORD.name, record)
    manifest = _write_output_hashes(output_dir)
    return {"status": "PASS", "day10_freeze": day10_freeze, "day11_freeze": day11_freeze,
            "t19_rows": len(t19_rows), "p1_cases": len(p1_rows), "associations": len(associations),
            "bootstrap_rows": len(bootstrap), "output_hashes": manifest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run frozen Day12 T19-only or complete analysis modes.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--t19-only", action="store_true", help="run only the frozen T19 diagnostic")
    mode.add_argument("--full", action="store_true", help="run the complete frozen Day12 analysis")
    parser.add_argument("--sidecar")
    parser.add_argument("--output-csv")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    if args.full:
        if args.sidecar or args.output_csv or args.report:
            parser.error("--full uses only frozen canonical inputs and outputs")
        result = run_full(Path(args.repo_root))
    else:
        result = run_t19(
            Path(args.repo_root),
            sidecar_path=Path(args.sidecar) if args.sidecar else None,
            output_csv=Path(args.output_csv) if args.output_csv else None,
            report_path=Path(args.report) if args.report else None,
        )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
