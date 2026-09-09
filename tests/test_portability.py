from __future__ import annotations

from pathlib import Path

from audiobookbench.data.prepare_audio import DATASET_ROOT_ENV, resolve_audio_path
from audiobookbench.security.day5_precheck import _dataset_root as day5_dataset_root
from audiobookbench.security.day6c_same_speaker import _dataset_root as day6c_dataset_root
from audiobookbench.temporal.day6b_embed import load_records


def test_relative_path_resolution_prefers_dataset_root(tmp_path: Path) -> None:
    record = {
        "audio_path": r"F:\old-machine\AISHELL-3\raw\train\wav\SSB0005\a.wav",
        "audio_relpath": "raw/train/wav/SSB0005/a.wav",
    }
    expected = tmp_path / "raw" / "train" / "wav" / "SSB0005" / "a.wav"
    assert resolve_audio_path(record, dataset_root=tmp_path) == expected


def test_windows_style_relative_path_is_portable(tmp_path: Path) -> None:
    record = {
        "audio_path": "unused.wav",
        "audio_relpath": r"raw\test\wav\SSB0139\b.wav",
    }
    expected = tmp_path / "raw" / "test" / "wav" / "SSB0139" / "b.wav"
    assert resolve_audio_path(record, dataset_root=tmp_path) == expected


def test_legacy_absolute_audio_path_remains_supported(tmp_path: Path) -> None:
    absolute = tmp_path / "legacy.wav"
    assert resolve_audio_path({"audio_path": str(absolute)}) == absolute


def test_dataset_root_environment_variable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(DATASET_ROOT_ENV, str(tmp_path))
    record = {"audio_path": "legacy.wav", "audio_relpath": "raw/legacy.wav"}
    assert resolve_audio_path(record) == tmp_path / "raw" / "legacy.wav"


def test_research_prechecks_honor_dataset_root_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(DATASET_ROOT_ENV, str(tmp_path))
    repository = Path(__file__).resolve().parents[1]
    assert day5_dataset_root(repository) == tmp_path
    assert day6c_dataset_root(repository) == tmp_path


def test_day6b_records_prefer_repository_relative_attack_paths() -> None:
    repository = Path(__file__).resolve().parents[1]
    manipulated = [record for record in load_records(repository).values() if record["variant"] != "clean"]
    assert manipulated
    assert all(Path(record["audio_path"]).is_relative_to(repository) for record in manipulated)
