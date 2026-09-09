"""Fixture-only tests for the frozen Day12 full execution entry."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from experiments.day12_mechanism import run as day12


class _FakeBackend:
    """Deterministic 192-D fixture backend; never loads the real ECAPA model."""

    def embed_windows(self, waveform: np.ndarray, windows: list[tuple[int, int]]) -> np.ndarray:
        value = float(np.mean(waveform))
        vector = np.zeros((len(windows), 192), dtype=np.float32)
        vector[:, 0] = value + 0.1
        vector[:, 1] = 1.0 - value
        vector[:, 2] = value * value + 0.01
        return vector


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fixture_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path
    wave_dir = root / "fixture_waves"
    wave_dir.mkdir()
    splits = ["train"] * 11 + ["val"] * 6 + ["test"] * 6
    sidecar: list[dict[str, object]] = []
    metrics: list[dict[str, object]] = []
    output_hashes: list[dict[str, object]] = []
    audio: dict[str, np.ndarray] = {}
    for index, split in enumerate(splits, start=1):
        case_id = f"paircase_{index:04d}"
        real = wave_dir / f"real_{index}.wav"
        manip = wave_dir / f"manip_{index}.wav"
        reference = wave_dir / f"reference_{index}.wav"
        for path in (real, manip, reference):
            path.write_bytes(f"fixture-{path.name}".encode("ascii"))
        audio[str(real)] = np.full(800, index / 100.0, dtype=np.float32)
        manipulated = np.full(1000, 0.02, dtype=np.float32)
        manipulated[100:900] = 0.5 - index / 100.0
        audio[str(manip)] = manipulated
        audio[str(reference)] = np.full(800, 0.2 + index / 1000.0, dtype=np.float32)
        sidecar.append({
            "paired_case_id": case_id, "split": split, "generation_status": "success",
            "source_audio_path": str(real), "manipulated_audio_path": str(manip),
            "reference_audio_path": str(reference), "reference_sample_id": f"reference_{index}",
            "source_real_num_samples": 800, "attack_start_sample": 100, "attack_end_sample": 900,
            "attack_core_start_sample": 200, "attack_core_end_sample": 800,
            "final_synthetic_num_samples": 800, "source_sample_id": f"source_{index}",
            "target_speaker": f"speaker_{index}",
        })
        output_hashes.append({"paired_case_id": case_id, "bytes": manip.stat().st_size, "sha256": _hash(manip)})
        for scale in ("S1_1000ms_250ms", "S2_1500ms_250ms"):
            metrics.append({"case_id": case_id, "split": split, "method": "B1b", "gt": "full", "scale": scale,
                            "auroc": index / 25.0, "auprc": (24 - index) / 25.0})
    _write_csv(root / "results/day10/a2_sidecar.csv", sidecar)
    (root / "results/day10/day10_output_hashes.json").write_text(json.dumps({
        "planned": 23, "succeeded": 23, "failed_by_class": {}, "output_hashes": output_hashes,
    }), encoding="utf-8")
    metrics_path = root / "results/day11/case_level_metrics.csv"
    _write_csv(metrics_path, metrics)
    (root / "results/day11/day11_output_hashes.json").write_text(json.dumps({
        "files": [{"path": "results/day11/case_level_metrics.csv", "bytes": metrics_path.stat().st_size,
                   "sha256": _hash(metrics_path)}],
    }), encoding="utf-8")

    def fixture_loader(path: str, target_sr: int | None):
        assert target_sr == 16000
        return audio[path].copy(), 16000

    monkeypatch.setattr(day12, "load_audio", fixture_loader)
    monkeypatch.setattr(day12, "SpeakerBackend", _FakeBackend)
    return root


def test_full_cli_dispatch_writes_all_canonical_fixture_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_repo(tmp_path, monkeypatch)
    assert day12.main(["--repo-root", str(root), "--full"]) == 0
    output = root / "results/day12"
    names = {path.name for path in output.iterdir()}
    assert names == {
        "per_case_similarity.csv", "p1_association.csv", "p1_bootstrap_ci.csv",
        "d2_reference_synthetic_cosine.csv", "t19_silence_distribution_shift.csv",
        "t19_silence_distribution_shift_report.md", "execution_record.json", "day12_output_hashes.json",
    }


def test_full_entry_hash_failure_stops_before_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_repo(tmp_path, monkeypatch)
    target = next((root / "fixture_waves").glob("manip_*.wav"))
    target.write_bytes(b"corrupted")
    with pytest.raises(day12.FullDay12IntegrityError, match="waveform hash mismatch"):
        day12.run_full(root)
    assert not (root / "results/day12").exists()


def test_full_entry_preserves_23_case_merge_and_co_primary_outcomes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_repo(tmp_path, monkeypatch)
    day12.run_full(root)
    p1 = list(csv.DictReader((root / "results/day12/per_case_similarity.csv").open(encoding="utf-8")))
    associations = list(csv.DictReader((root / "results/day12/p1_association.csv").open(encoding="utf-8")))
    assert len(p1) == 23 and len({row["paired_case_id"] for row in p1}) == 23
    assert Counter(row["split"] for row in p1) == Counter({"train": 11, "val": 6, "test": 6})
    assert {(row["scale"], row["outcome"]) for row in associations} == {
        ("S1", "AUROC"), ("S1", "AUPRC"), ("S2", "AUROC"), ("S2", "AUPRC"),
    }
    assert all(row["statistic"] == "Spearman" and row["n_cases"] == "23" for row in associations)


def test_case_level_spearman_bootstrap_is_seed_deterministic_and_paired() -> None:
    p1 = [{"paired_case_id": f"paircase_{i:04d}", "target_synthetic_ecapa_cosine": i / 30.0} for i in range(1, 24)]
    metrics = {scale: {row["paired_case_id"]: {"auroc": index / 25.0, "auprc": (24 - index) / 25.0}
                       for index, row in enumerate(p1, start=1)} for scale in ("S1", "S2")}
    first = day12.association_and_bootstrap(p1, metrics, resamples=40, seed=20260905)
    second = day12.association_and_bootstrap(p1, metrics, resamples=40, seed=20260905)
    assert first == second
    assert len(first[0]) == len(first[1]) == 4
    assert all(row["n_cases"] == 23 and row["bootstrap_count"] == 40 for row in first[1])


def test_d2_is_separate_diagnostic_and_t19_is_integrated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_repo(tmp_path, monkeypatch)
    day12.run_full(root)
    d2 = list(csv.DictReader((root / "results/day12/d2_reference_synthetic_cosine.csv").open(encoding="utf-8")))
    t19 = list(csv.DictReader((root / "results/day12/t19_silence_distribution_shift.csv").open(encoding="utf-8")))
    assert len(d2) == len(t19) == 23
    assert {row["diagnostic_label"] for row in d2} == {"DIAGNOSTIC_ONLY"}
    assert {row["diagnostic_label"] for row in t19} == {"DIAGNOSTIC_ONLY"}
    assert "DIAGNOSTIC ONLY" in (root / "results/day12/t19_silence_distribution_shift_report.md").read_text(encoding="utf-8")


def test_full_entry_output_hash_manifest_covers_canonical_nonself_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_repo(tmp_path, monkeypatch)
    day12.run_full(root)
    manifest = json.loads((root / "results/day12/day12_output_hashes.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 7
    for item in manifest["files"]:
        path = root / item["path"]
        assert path.is_file() and path.stat().st_size == item["bytes"] and _hash(path) == item["sha256"]

