from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping

import numpy as np

from audiobookbench.data.manifest import (
    ALLOWED_SOURCE_TYPES,
    ALLOWED_SPLITS,
    ManifestValidationError,
    normalize_bool,
    save_manifest,
    validate_manifest,
)
from audiobookbench.preprocessing.audio_io import load_audio, probe_audio
from audiobookbench.preprocessing.segment import fixed_windows, slice_segment, voiced_ratio


SOURCE_CATALOG_COLUMNS = [
    "audio_path",
    "sample_id",
    "pair_id",
    "source_sample_id",
    "source_type",
    "generator",
    "generator_family",
    "speaker",
    "text_id",
    "is_manipulated",
    "attack_type",
    "attack_start",
    "attack_end",
    "attack_generator",
    "source_generator",
    "replacement_speaker",
    "split",
]

_SOURCE_REQUIRED_NON_EMPTY = {
    "audio_path",
    "sample_id",
    "pair_id",
    "source_sample_id",
    "source_type",
    "generator",
    "generator_family",
    "speaker",
    "text_id",
    "is_manipulated",
    "split",
}

DATASET_ROOT_ENV = "AUDIOBOOKBENCH_DATASET_ROOT"


def _portable_relpath(value: Any) -> Path:
    """Convert POSIX- or Windows-style relative text to a local Path safely."""
    text = str(value).strip().replace("\\", "/")
    posix_path = PurePosixPath(text)
    windows_path = PureWindowsPath(text)
    if not text or posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        raise ValueError(f"audio_relpath must be relative, got {value!r}")
    if ".." in posix_path.parts:
        raise ValueError(f"audio_relpath must not escape dataset_root, got {value!r}")
    return Path(*posix_path.parts)


def resolve_audio_path(
    record: Mapping[str, Any],
    *,
    dataset_root: str | Path | None = None,
) -> Path:
    """Resolve portable ``audio_relpath`` while preserving legacy audio_path.

    When a dataset root and ``audio_relpath`` are both available, the portable
    path takes precedence. Otherwise the existing ``audio_path`` behavior is
    unchanged. The root can be supplied by API/CLI or by
    ``AUDIOBOOKBENCH_DATASET_ROOT``.
    """
    root_value = dataset_root or os.environ.get(DATASET_ROOT_ENV)
    relpath = str(record.get("audio_relpath", "")).strip()
    if root_value is not None and relpath:
        return Path(root_value).expanduser() / _portable_relpath(relpath)

    audio_path = Path(str(record.get("audio_path", "")).strip()).expanduser()
    if root_value is not None and not audio_path.is_absolute():
        return Path(root_value).expanduser() / _portable_relpath(audio_path)
    return audio_path


def load_source_catalog(path: str | Path) -> list[dict[str, str]]:
    """Load file-level metadata for real audio ingestion.

    The source catalog is intentionally separate from the canonical segment manifest:
    Day 3 turns one file-level catalog row into one or more segment-level rows.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Source audio catalog not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
    validate_source_catalog(rows)
    return rows


def validate_source_catalog(records: Iterable[Mapping[str, Any]]) -> None:
    rows = list(records)
    if not rows:
        raise ManifestValidationError("source audio catalog must contain at least one row")

    seen_sample_ids: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        missing = [field for field in SOURCE_CATALOG_COLUMNS if field not in row]
        if missing:
            raise ManifestValidationError(f"source catalog row {idx} missing columns: {missing}")
        empty = [field for field in _SOURCE_REQUIRED_NON_EMPTY if str(row.get(field, "")).strip() == ""]
        if empty:
            raise ManifestValidationError(f"source catalog row {idx} has empty required fields: {sorted(empty)}")

        sample_id = str(row["sample_id"]).strip()
        if sample_id in seen_sample_ids:
            raise ManifestValidationError(f"source catalog sample_id must be unique, duplicate={sample_id!r}")
        seen_sample_ids.add(sample_id)

        source_type = str(row["source_type"]).strip().lower()
        if source_type not in ALLOWED_SOURCE_TYPES:
            raise ManifestValidationError(
                f"source catalog row {idx} source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}"
            )
        split = str(row["split"]).strip().lower()
        if split not in ALLOWED_SPLITS:
            raise ManifestValidationError(
                f"source catalog row {idx} split must be one of {sorted(ALLOWED_SPLITS)}"
            )

        is_manipulated = normalize_bool(row["is_manipulated"], row_index=idx)
        if is_manipulated:
            raise ManifestValidationError(
                "Day 3 real-audio ingestion accepts clean source rows only. "
                "Manipulated audio is introduced in Day 4."
            )
        source_sample_id = str(row["source_sample_id"]).strip()
        if source_sample_id != sample_id:
            raise ManifestValidationError(
                f"source catalog row {idx} clean source must self-reference source_sample_id == sample_id"
            )


def _rms(audio: np.ndarray) -> float:
    waveform = np.asarray(audio, dtype=np.float32)
    return float(np.sqrt(np.mean(waveform**2))) if waveform.size else 0.0


def _peak(audio: np.ndarray) -> float:
    waveform = np.asarray(audio, dtype=np.float32)
    return float(np.max(np.abs(waveform))) if waveform.size else 0.0


def build_segment_manifest(
    source_records: Iterable[Mapping[str, Any]],
    *,
    target_sr: int = 16000,
    window_seconds: float = 5.0,
    min_tail_seconds: float = 1.0,
    vad_threshold_ratio: float = 0.25,
    dataset_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Convert clean real-audio source records into the canonical segment manifest."""
    source_rows = [dict(row) for row in source_records]
    validate_source_catalog(source_rows)
    if target_sr <= 0:
        raise ValueError("target_sr must be > 0")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")

    manifest_rows: list[dict[str, Any]] = []
    for row in source_rows:
        path = resolve_audio_path(row, dataset_root=dataset_root)
        info = probe_audio(path)
        audio, sr = load_audio(path, target_sr=target_sr)
        duration = float(len(audio) / sr)
        segments = fixed_windows(
            duration,
            window_seconds=window_seconds,
            min_tail_seconds=min_tail_seconds,
        )
        if not segments:
            raise ValueError(f"No valid segments produced for audio: {path}")

        sample_id = str(row["sample_id"]).strip()
        for segment in segments:
            chunk = slice_segment(audio, sr, segment)
            manifest_rows.append(
                {
                    "audio_path": str(path),
                    "sample_id": sample_id,
                    "pair_id": str(row["pair_id"]).strip(),
                    "source_sample_id": str(row["source_sample_id"]).strip(),
                    "source_type": str(row["source_type"]).strip().lower(),
                    "generator": str(row["generator"]).strip(),
                    "generator_family": str(row["generator_family"]).strip(),
                    "speaker": str(row["speaker"]).strip(),
                    "text_id": str(row["text_id"]).strip(),
                    "duration": duration,
                    "sample_rate": sr,
                    "segment_id": f"{sample_id}_seg{segment.index:04d}",
                    "segment_start": segment.start,
                    "segment_end": segment.end,
                    "position": segment.index,
                    "is_manipulated": False,
                    "attack_type": "",
                    "attack_start": "",
                    "attack_end": "",
                    "attack_generator": "",
                    "source_generator": str(row.get("source_generator") or row["generator"]).strip(),
                    "replacement_speaker": "",
                    "split": str(row["split"]).strip().lower(),
                    "audio_relpath": str(row.get("audio_relpath", "")).replace("\\", "/"),
                    # Extra Day-3 diagnostic columns. They are allowed by save_manifest().
                    "original_sample_rate": info.sample_rate,
                    "original_channels": info.channels,
                    "segment_duration": segment.duration,
                    "vad_voiced_ratio": voiced_ratio(
                        chunk,
                        sr,
                        threshold_ratio=vad_threshold_ratio,
                    ),
                    "rms": _rms(chunk),
                    "peak": _peak(chunk),
                }
            )

    validate_manifest(manifest_rows)
    return manifest_rows


def prepare_real_audio_manifest(
    catalog_path: str | Path,
    output_path: str | Path,
    *,
    target_sr: int = 16000,
    window_seconds: float = 5.0,
    min_tail_seconds: float = 1.0,
    vad_threshold_ratio: float = 0.25,
    dataset_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    source_records = load_source_catalog(catalog_path)
    manifest_rows = build_segment_manifest(
        source_records,
        target_sr=target_sr,
        window_seconds=window_seconds,
        min_tail_seconds=min_tail_seconds,
        vad_threshold_ratio=vad_threshold_ratio,
        dataset_root=dataset_root,
    )
    save_manifest(manifest_rows, output_path)
    return manifest_rows


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a validated segment-level manifest from clean real audio."
    )
    parser.add_argument("--catalog", required=True, help="File-level source catalog CSV")
    parser.add_argument("--output", required=True, help="Output canonical segment manifest CSV")
    parser.add_argument("--target-sr", type=int, default=16000)
    parser.add_argument("--window-seconds", type=float, default=5.0)
    parser.add_argument("--min-tail-seconds", type=float, default=1.0)
    parser.add_argument("--vad-threshold-ratio", type=float, default=0.25)
    parser.add_argument(
        "--dataset-root",
        default=None,
        help=f"Root joined with audio_relpath (or use {DATASET_ROOT_ENV})",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    rows = prepare_real_audio_manifest(
        args.catalog,
        args.output,
        target_sr=args.target_sr,
        window_seconds=args.window_seconds,
        min_tail_seconds=args.min_tail_seconds,
        vad_threshold_ratio=args.vad_threshold_ratio,
        dataset_root=args.dataset_root,
    )
    sample_ids = sorted({str(row["sample_id"]) for row in rows})
    print(
        f"Prepared {len(rows)} segments from {len(sample_ids)} audio files -> {args.output}"
    )


if __name__ == "__main__":
    main()
