"""Day 6B speaker-embedding extraction over the frozen Day 4.5 waveforms.

Backend: SpeechBrain ECAPA-TDNN (``speechbrain/spkrec-ecapa-voxceleb``),
pretrained on VoxCeleb, inference-only, 16 kHz input, 192-d embeddings,
loaded offline from the local copy under ``pretrained/``.

Temporal grids are frozen in ``configs/day6b_speaker_consistency.yaml``
(S1: 1.0 s window / 0.25 s hop; S2: 1.5 s / 0.25 s) and are independent of
the Day 5 measurement grid. Extraction is label-agnostic: no attack ground
truth is read here, and windows are never adjusted using GT.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.preprocessing.audio_io import load_audio
from audiobookbench.temporal.grid import TemporalGrid

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "configs/day6b_speaker_consistency.yaml"
SAVEDIR = REPO_ROOT / "pretrained/spkrec-ecapa-voxceleb"

EMBEDDING_DIM = 192
SAMPLE_RATE = 16000
BATCH = 64


def _ensure_torch_amp_compatibility(torch: Any) -> None:
    """Bridge SpeechBrain 1.1's CPU decorator onto torch 2.3.

    SpeechBrain 1.1.1 uses ``torch.amp.custom_fwd(..., device_type="cpu")``.
    That generic API is unavailable in the Day 8 Windows overlay's fixed
    torch 2.3.1, even though Day 6B invokes the encoder on CPU with autocast
    disabled.  For that exact no-autocast CPU path the decorator is a no-op;
    retain torch's native CUDA implementation if it is ever requested.
    """
    if hasattr(torch.amp, "custom_fwd"):
        return

    def compat_custom_fwd(fwd=None, *, device_type: str, cast_inputs=None):
        if device_type == "cuda":
            return torch.cuda.amp.custom_fwd(fwd, cast_inputs=cast_inputs)
        if fwd is None:
            return lambda func: func
        return fwd

    torch.amp.custom_fwd = compat_custom_fwd


class SpeakerBackend:
    """Lazy offline loader for the frozen ECAPA-TDNN backend."""

    def __init__(self) -> None:
        self._enc = None

    def load(self) -> Any:
        if self._enc is None:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            import torch

            _ensure_torch_amp_compatibility(torch)
            from speechbrain.inference.speaker import EncoderClassifier

            torch.set_num_threads(max(1, os.cpu_count() or 4))
            if not (SAVEDIR / "hyperparams.yaml").exists():
                raise RuntimeError(
                    f"local ECAPA model missing under {SAVEDIR}; run the "
                    "Day 6B model setup before extraction"
                )
            self._enc = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir=str(SAVEDIR),
                run_opts={"device": "cpu"},
            )
        return self._enc

    def embed_windows(self, waveform: np.ndarray, windows: list[tuple[int, int]]) -> np.ndarray:
        """Embed complete windows; returns ``(n_windows, 192)`` float32."""
        import torch

        enc = self.load()
        out = np.empty((len(windows), EMBEDDING_DIM), dtype=np.float32)
        with torch.no_grad():
            for start in range(0, len(windows), BATCH):
                chunk = windows[start:start + BATCH]
                batch = torch.stack(
                    [torch.tensor(np.asarray(waveform[lo:hi], dtype=np.float32)) for lo, hi in chunk]
                )
                emb = enc.encode_batch(batch).squeeze(1).cpu().numpy()
                out[start:start + len(chunk)] = emb
        return out


class SpeakerWindowScale:
    """One frozen speaker temporal scale (window/hop in samples)."""

    def __init__(self, name: str, window_samples: int, hop_samples: int) -> None:
        if window_samples <= 0 or hop_samples <= 0:
            raise ValueError("window_samples and hop_samples must be positive")
        if hop_samples > window_samples:
            raise ValueError("hop_samples must not exceed window_samples")
        self.name = name
        self.window_samples = window_samples
        self.hop_samples = hop_samples

    @classmethod
    def from_config(cls, entry: dict[str, Any]) -> "SpeakerWindowScale":
        window_ms, hop_ms = int(entry["window_ms"]), int(entry["hop_ms"])
        if window_ms % 250 != 0 or hop_ms % 250 != 0:
            raise ValueError("Day 6B windows/hops must be multiples of 250 ms")
        return cls(
            name=str(entry["name"]),
            window_samples=window_ms * SAMPLE_RATE // 1000,
            hop_samples=hop_ms * SAMPLE_RATE // 1000,
        )

    def window_count(self, num_samples: int) -> int:
        if num_samples < self.window_samples:
            return 0
        return 1 + (num_samples - self.window_samples) // self.hop_samples

    def bounds(self, index: int) -> tuple[int, int]:
        if index < 0:
            raise ValueError("index must be non-negative")
        start = index * self.hop_samples
        return start, start + self.window_samples


def build_speaker_windows(
    num_samples: int, scale: SpeakerWindowScale, grid: TemporalGrid | None = None
) -> list[dict[str, Any]]:
    """Window metadata rows: sample bounds + exact seconds (samples / 16000)."""
    sr = SAMPLE_RATE
    rows = []
    for index in range(scale.window_count(num_samples)):
        lo, hi = scale.bounds(index)
        center = (lo + hi) // 2
        rows.append(
            {
                "window_index": index,
                "sample_start": lo,
                "sample_end": hi,
                "time_start": lo / sr,
                "time_center": center / sr,
                "time_end": hi / sr,
            }
        )
    return rows


def load_config(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    import yaml

    return yaml.safe_load((repo_root / "configs/day6b_speaker_consistency.yaml").read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_records(repo_root: Path = REPO_ROOT) -> dict[str, dict[str, Any]]:
    """Identity + audio path for all 70 records (clean from hashes CSV)."""
    hash_rows = _read_csv(repo_root / "data/generated/day45_paired/metadata/output_audio_hashes.csv")
    manifest = _read_csv(repo_root / "data/manifests/day45_attack_manifest.csv")
    by_record = {row["manipulated_sequence_id"]: row for row in manifest}
    records: dict[str, dict[str, Any]] = {}
    for row in hash_rows:
        rid = row["artifact_id"]
        variant = "clean" if row["artifact_type"] == "clean" else None
        if variant is None:
            continue
        records[rid] = {
            "record_id": rid,
            "variant": "clean",
            "paired_case_id": "",
            "split": _split_of(rid),
            "speaker": _speaker_of(rid),
            "audio_path": str(repo_root / row["audio_relpath"]),
        }
    for row in manifest:
        records[row["manipulated_sequence_id"]] = {
            "record_id": row["manipulated_sequence_id"],
            "variant": "a0" if row["attack_type"] == "cross_speaker_splice" else "a1",
            "paired_case_id": row["paired_case_id"],
            "split": row["split"],
            "speaker": _speaker_of(row["clean_sequence_id"]),
            # The absolute field is retained for lineage, but formal reads
            # must prefer the portable repository-relative path.
            "audio_path": str(
                repo_root
                / row.get("manipulated_audio_relpath", row["manipulated_audio_path"])
            ),
            "manifest_row": row,
        }
    return records


def _split_of(sequence_id: str) -> str:
    body = sequence_id[len("day45_"):] if sequence_id.startswith("day45_") else sequence_id
    parts = body.split("_")
    return parts[0] if parts and parts[0] in {"train", "val", "test"} else "unknown"


def _speaker_of(sequence_id: str) -> str:
    body = sequence_id[len("day45_"):] if sequence_id.startswith("day45_") else sequence_id
    parts = body.split("_")
    return parts[1] if len(parts) >= 2 and parts[0] in {"train", "val", "test"} else "unknown"


def extract_all(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Extract and persist temporal embeddings for all 70 records, both scales."""
    config = load_config(repo_root)
    out_dir = repo_root / "results/day6b/embeddings"
    out_dir.mkdir(parents=True, exist_ok=True)
    backend = SpeakerBackend()
    backend.load()
    manifest_rows: list[dict[str, Any]] = []
    records = load_records(repo_root)
    scales = [SpeakerWindowScale.from_config(e) for e in config["speaker_temporal_grid"]["scales"]]
    counts: dict[str, int] = {}
    for record in records.values():
        waveform, sr = load_audio(record["audio_path"], target_sr=None)
        assert sr == SAMPLE_RATE, f"unexpected sample rate {sr} for {record['record_id']}"
        for scale in scales:
            windows = build_speaker_windows(waveform.size, scale)
            spans = [(w["sample_start"], w["sample_end"]) for w in windows]
            emb = backend.embed_windows(waveform, spans)
            if emb.shape != (len(windows), EMBEDDING_DIM):
                raise AssertionError(f"embedding shape mismatch for {record['record_id']}")
            np.save(out_dir / f"{scale.name}__{record['record_id']}.npy", emb)
            counts[scale.name] = counts.get(scale.name, 0) + len(windows)
            base = {
                "scale": scale.name,
                "record_id": record["record_id"],
                "variant": record["variant"],
                "paired_case_id": record["paired_case_id"],
                "split": record["split"],
                "speaker": record["speaker"],
            }
            for w in windows:
                row = dict(base)
                row.update({k: w[k] for k in (
                    "window_index", "sample_start", "sample_end",
                    "time_start", "time_center", "time_end")})
                row["embedding_file"] = f"{scale.name}__{record['record_id']}.npy"
                row["embedding_index"] = w["window_index"]
                manifest_rows.append(row)

    manifest_path = repo_root / "results/day6b/embedding_manifest.csv"
    columns = [
        "scale", "record_id", "variant", "paired_case_id", "split", "speaker",
        "window_index", "embedding_index", "sample_start", "sample_end",
        "time_start", "time_center", "time_end", "embedding_file",
    ]
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(manifest_rows)

    summary = {
        "extraction": "day6b_speaker_embeddings",
        "backend": {
            "package": "speechbrain", "version": "1.1.1", "model": "speechbrain/spkrec-ecapa-voxceleb",
            "dim": EMBEDDING_DIM, "sample_rate": SAMPLE_RATE, "device": "cpu",
        },
        "records": len(records),
        "windows_per_scale": counts,
        "windows_total": sum(counts.values()),
        "label_agnostic": True,
    }
    (repo_root / "results/day6b/embedding_backend.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Extract Day 6B speaker embeddings.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    print(json.dumps(extract_all(Path(args.repo_root)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
