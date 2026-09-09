from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
from pathlib import Path

import pytest
import yaml

from audiobookbench.data.construct_longform import load_longform_manifest, validate_longform_lineage
from audiobookbench.data.expanded_pilot import (
    build_text_overlap_audit,
    inventory_aishell3,
    select_expanded_speakers,
    text_overlap_counts,
    validate_expanded_source_catalog,
)
from audiobookbench.security.manipulation_dataset import A0, A1
from audiobookbench.security.paired_manipulation import (
    build_paired_diagnostics,
    load_paired_attack_manifest,
    validate_paired_attack_manifest,
    verify_paired_waveforms,
)


REPOSITORY = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((REPOSITORY / "configs/day45_expanded_paired.yaml").read_text(encoding="utf-8"))
DATASET_ROOT = Path(CONFIG["dataset_root"])


def _csv(relative: str) -> list[dict[str, str]]:
    with (REPOSITORY / relative).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def test_expanded_split_is_deterministic_disjoint_and_has_twelve_speakers() -> None:
    sources = _csv("data/manifests/day45_source_audio.csv")
    validate_expanded_source_catalog(sources)
    by_split = {
        split: sorted({row["speaker"] for row in sources if row["split"] == split})
        for split in ("train", "val", "test")
    }
    assert by_split == {
        "train": ["SSB0005", "SSB0009", "SSB0011", "SSB0261", "SSB0309", "SSB0393"],
        "val": ["SSB0073", "SSB0197", "SSB0434"],
        "test": ["SSB0139", "SSB0342", "SSB1100"],
    }
    assert len(set().union(*map(set, by_split.values()))) == 12
    assert all(len(by_split[split]) >= 3 for split in by_split)
    assert not (set(by_split["train"]) & set(by_split["val"]))
    assert not (set(by_split["train"]) & set(by_split["test"]))
    assert not (set(by_split["val"]) & set(by_split["test"]))
    assert Counter(row["speaker"] for row in sources) == Counter({speaker: 40 for speakers in by_split.values() for speaker in speakers})
    recomputed = select_expanded_speakers(
        inventory_aishell3(DATASET_ROOT), CONFIG["expanded_pilot"]["split_slots"], minimum_rows=40,
    )
    assert recomputed == by_split


def test_expanded_text_overlap_audit_is_reproducible() -> None:
    sources = _csv("data/manifests/day45_source_audio.csv")
    expected = build_text_overlap_audit(sources)
    actual = _csv("data/reports/day45_text_overlap_audit.csv")
    assert [{key: str(value) for key, value in row.items()} for row in expected] == actual
    assert text_overlap_counts(actual) == {
        "train_val": 0, "train_test": 0, "val_test": 0, "train_val_test": 0,
    }


def test_expanded_longform_has_twenty_four_traceable_clean_sequences() -> None:
    sources = _csv("data/manifests/day45_source_audio.csv")
    source_by_id = {row["sample_id"]: row for row in sources}
    lineage = load_longform_manifest(REPOSITORY / "data/manifests/day45_longform_manifest.csv")
    validate_longform_lineage(lineage, source_sample_ids=set(source_by_id), check_audio=True)
    sequence_ids = {row["sequence_id"] for row in lineage}
    assert len(sequence_ids) == 24
    assert Counter(row["speaker"] for row in {seq: next(item for item in lineage if item["sequence_id"] == seq) for seq in sequence_ids}.values()) == Counter({speaker: 2 for speaker in {row["speaker"] for row in sources}})
    assert all(row["sequence_id"].startswith("day45_") for row in lineage)
    for row in lineage:
        source = source_by_id[row["source_sample_id"]]
        assert (row["speaker"], row["split"]) == (source["speaker"], source["split"])
        assert row["longform_type"] == "constructed"


def test_paired_manifest_controls_target_donor_and_split() -> None:
    attacks = load_paired_attack_manifest(REPOSITORY / "data/manifests/day45_attack_manifest.csv")
    lineage = load_longform_manifest(REPOSITORY / "data/manifests/day45_longform_manifest.csv")
    validate_paired_attack_manifest(attacks)
    pairs: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attacks:
        pairs[row["paired_case_id"]].append(row)
    assert len(pairs) == 23
    assert Counter((row["split"], row["attack_type"]) for row in attacks) == Counter({
        ("train", A0): 11, ("train", A1): 11,
        ("val", A0): 6, ("val", A1): 6,
        ("test", A0): 6, ("test", A1): 6,
    })
    lineage_by_target = {
        (row["sequence_id"], row["source_sample_id"]): row for row in lineage
    }
    for case in pairs.values():
        assert len(case) == 2 and {row["attack_type"] for row in case} == {A0, A1}
        for field in (
            "clean_sequence_id", "target_start_sample", "target_end_sample",
            "donor_source_sample_id", "donor_start_sample", "donor_end_sample",
        ):
            assert case[0][field] == case[1][field]
        row = case[0]
        assert row["split"] == row["donor_split"]
        assert row["target_speaker"] != row["donor_speaker"]
        target = lineage_by_target[(row["clean_sequence_id"], row["target_source_sample_id"])]
        source_start = round(float(target["sequence_start"]) * int(row["sample_rate"]))
        source_end = round(float(target["sequence_end"]) * int(row["sample_rate"]))
        assert int(row["target_start_sample"]) - source_start >= 8000
        assert source_end - int(row["target_end_sample"]) >= 8000
        assert float(row["target_start"]) == int(row["target_start_sample"]) / int(row["sample_rate"])
        assert float(row["target_end"]) == int(row["target_end_sample"]) / int(row["sample_rate"])


def test_balanced_donor_usage_and_repeat_cap() -> None:
    attacks = [row for row in load_paired_attack_manifest(REPOSITORY / "data/manifests/day45_attack_manifest.csv") if row["attack_type"] == A0]
    usage = Counter((row["split"], row["donor_speaker"]) for row in attacks)
    assert usage == Counter({
        ("train", "SSB0005"): 2, ("train", "SSB0009"): 2,
        ("train", "SSB0011"): 2, ("train", "SSB0261"): 2,
        ("train", "SSB0309"): 2, ("train", "SSB0393"): 1,
        ("val", "SSB0073"): 2, ("val", "SSB0197"): 2, ("val", "SSB0434"): 2,
        ("test", "SSB0139"): 2, ("test", "SSB0342"): 2, ("test", "SSB1100"): 2,
    })
    assert max(Counter(row["donor_source_sample_id"] for row in attacks).values()) == 1
    assert all(int(row["donor_usage_count"]) == 1 for row in attacks)


def test_all_paired_waveforms_pass_actual_sample_verification() -> None:
    attacks = load_paired_attack_manifest(REPOSITORY / "data/manifests/day45_attack_manifest.csv")
    sources = _csv("data/manifests/day45_source_audio.csv")
    results = verify_paired_waveforms(attacks, sources, dataset_root=DATASET_ROOT)
    assert len(results) == 46
    assert all(all(row[field] for field in (
        "duration_equal", "sample_rate_equal", "channel_equal", "finite",
        "outside_equal", "inside_changed", "core_matches_donor",
    )) for row in results)


def test_paired_diagnostics_and_regeneration_records_match() -> None:
    attacks = load_paired_attack_manifest(REPOSITORY / "data/manifests/day45_attack_manifest.csv")
    expected = build_paired_diagnostics(attacks)
    actual = _csv("data/generated/day45_paired/metadata/paired_diagnostics.csv")
    assert len(expected) == len(actual) == 23
    for left, right in zip(expected, actual):
        assert left["paired_case_id"] == right["paired_case_id"]
        for field in (
            "a0_boundary_jump_total", "a1_boundary_jump_total",
            "boundary_jump_difference_a1_minus_a0", "a0_local_rms_discontinuity",
            "a1_local_rms_discontinuity", "rms_difference_a1_minus_a0",
        ):
            assert float(left[field]) == pytest.approx(float(right[field]), abs=1e-15)
    reproducibility = _csv("data/generated/day45_paired/metadata/reproducibility.csv")
    assert len(reproducibility) == 8
    assert all(row["match"].lower() == "true" for row in reproducibility)


def test_protected_prior_artifacts_and_raw_sources_are_unchanged() -> None:
    protected = _csv("data/generated/day45_paired/metadata/protected_artifact_hashes.csv")
    assert protected and {row["artifact_group"] for row in protected} == {"day3", "day35", "day4"}
    for row in protected:
        actual = hashlib.sha256((REPOSITORY / row["path"]).read_bytes()).hexdigest().upper()
        assert row["unchanged"].lower() == "true"
        assert actual == row["sha256_before"] == row["sha256_after"]
    sources = _csv("data/generated/day45_paired/metadata/source_input_hashes.csv")
    assert len(sources) == 480
    for row in sources:
        actual = hashlib.sha256((DATASET_ROOT / row["audio_relpath"]).read_bytes()).hexdigest().upper()
        assert row["unchanged"].lower() == "true"
        assert actual == row["sha256_before"] == row["sha256_after"]
