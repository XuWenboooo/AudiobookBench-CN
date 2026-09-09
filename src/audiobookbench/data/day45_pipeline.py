"""Orchestrate the deterministic Day 4.5 expanded paired-attack build."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from audiobookbench.data.construct_longform import construct_longform_sequences, save_longform_manifest
from audiobookbench.data.expanded_pilot import (
    build_expanded_source_catalog,
    build_text_overlap_audit,
    inventory_aishell3,
    save_expanded_source_catalog,
    save_text_overlap_audit,
    select_expanded_speakers,
    text_overlap_counts,
)
from audiobookbench.security.paired_manipulation import (
    build_paired_attacks,
    build_paired_diagnostics,
    save_diagnostics,
    save_paired_attack_manifest,
    save_skips,
    save_verification,
    verify_paired_waveforms,
)


HASH_COLUMNS = ["artifact_group", "path", "sha256_before", "sha256_after", "unchanged"]
SOURCE_HASH_COLUMNS = ["sample_id", "audio_relpath", "sha256_before", "sha256_after", "unchanged"]
OUTPUT_HASH_COLUMNS = ["artifact_type", "artifact_id", "audio_relpath", "sha256"]
REPRODUCIBILITY_COLUMNS = ["component", "match", "detail"]


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def _destination(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def protected_artifact_paths(repository_root: str | Path) -> list[tuple[str, Path]]:
    root = Path(repository_root).resolve()
    explicit = {
        "day3": [
            "configs/day3_aishell3_pilot.yaml", "data/manifests/source_audio.csv",
            "data/manifests/week1_manifest.csv", "DAY3_REAL_DATA_REPORT.md",
        ],
        "day35": [
            "configs/day35_constructed_longform.yaml", "data/manifests/day35_source_audio_portable.csv",
            "data/manifests/day35_longform_manifest.csv", "DAY35_LONGFORM_PROTOCOL_REPORT.md",
        ],
        "day4": [
            "configs/day4_manipulation_v2.yaml", "data/manifests/day4_attack_manifest.csv",
            "DAY4_MANIPULATION_REPORT.md", "src/audiobookbench/security/manipulation_dataset.py",
            "tests/test_day3_freeze.py", "tests/test_day4_manipulation.py",
        ],
    }
    output: list[tuple[str, Path]] = []
    for group, paths in explicit.items():
        output.extend((group, root / path) for path in paths)
    output.extend(("day35", path) for path in sorted((root / "data/constructed_longform/day35_smoke").rglob("*.wav")))
    output.extend(("day4", path) for path in sorted((root / "data/generated/day4_v2").rglob("*")) if path.is_file())
    return output


def run_day45_pipeline(
    config_path: str | Path,
    *,
    repository_root: str | Path,
    protect_existing: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    dataset_root = Path(config["dataset_root"]).resolve()
    outputs = config["outputs"]
    metadata_root = _destination(root, outputs["metadata_directory"])
    metadata_root.mkdir(parents=True, exist_ok=True)

    protected = protected_artifact_paths(root) if protect_existing else []
    protected_before = {(group, path): _sha256(path) for group, path in protected}

    inventory = inventory_aishell3(dataset_root)
    pilot = config["expanded_pilot"]
    split_speakers = select_expanded_speakers(
        inventory, pilot["split_slots"],
        minimum_rows=int(pilot["eligibility"]["minimum_valid_wav_transcript_metadata_rows"]),
    )
    sources = build_expanded_source_catalog(
        inventory, split_speakers,
        utterances_per_speaker=int(pilot["utterances_per_speaker"]),
    )
    source_hash_before = {str(row["sample_id"]): _sha256(row["audio_path"]) for row in sources}
    save_expanded_source_catalog(sources, _destination(root, outputs["source_catalog"]))
    audit = build_text_overlap_audit(sources)
    save_text_overlap_audit(audit, _destination(root, outputs["text_overlap_audit"]))

    longform = config["constructed_longform"]
    lineage = construct_longform_sequences(
        sources,
        dataset_root=dataset_root,
        repository_root=root,
        output_directory=outputs["clean_audio_directory"],
        target_sr=int(longform["target_sample_rate"]),
        gap_seconds=float(longform["gap_seconds"]),
        min_duration=float(longform["target_duration_seconds"]["minimum"]),
        preferred_duration=float(longform["target_duration_seconds"]["preferred"]),
        max_duration=float(longform["target_duration_seconds"]["maximum"]),
        min_utterances=int(longform["utterances_per_sequence"]["minimum"]),
        max_utterances=int(longform["utterances_per_sequence"]["maximum"]),
        sequences_per_speaker=int(longform["sequences_per_speaker"]),
        sequence_id_prefix=str(longform["sequence_id_prefix"]),
    )
    save_longform_manifest(lineage, _destination(root, outputs["longform_manifest"]))

    attack = config["paired_attacks"]
    attacks, skips = build_paired_attacks(
        lineage, sources,
        dataset_root=dataset_root,
        repository_root=root,
        a0_directory=outputs["A0_directory"],
        a1_directory=outputs["A1_directory"],
        duration_tiers=tuple(float(value) for value in attack["duration_tiers_seconds"]),
        margin_seconds=float(attack["internal_margin_seconds"]),
        sample_rate=int(longform["target_sample_rate"]),
        crossfade_seconds=float(attack["crossfade_seconds"]),
        rms_epsilon=float(attack["rms_epsilon"]),
        rms_gain_min=float(attack["rms_gain_min"]),
        rms_gain_max=float(attack["rms_gain_max"]),
        donor_repeat_cap=int(attack["donor_utterance_repeat_cap"]),
    )
    save_paired_attack_manifest(attacks, _destination(root, outputs["attack_manifest"]))
    save_skips(skips, _destination(root, outputs["skip_manifest"]))
    verification = verify_paired_waveforms(attacks, sources, dataset_root=dataset_root)
    save_verification(verification, _destination(root, outputs["waveform_verification"]))
    diagnostics = build_paired_diagnostics(attacks)
    save_diagnostics(diagnostics, _destination(root, outputs["paired_diagnostics"]))

    source_hash_rows = []
    for row in sources:
        sample_id = str(row["sample_id"])
        after = _sha256(row["audio_path"])
        source_hash_rows.append({
            "sample_id": sample_id, "audio_relpath": row["audio_relpath"],
            "sha256_before": source_hash_before[sample_id], "sha256_after": after,
            "unchanged": source_hash_before[sample_id] == after,
        })
    _save_csv(source_hash_rows, metadata_root / "source_input_hashes.csv", SOURCE_HASH_COLUMNS)

    clean_seen: set[str] = set()
    output_hash_rows = []
    for row in lineage:
        sequence_id = str(row["sequence_id"])
        if sequence_id not in clean_seen:
            clean_seen.add(sequence_id)
            output_hash_rows.append({
                "artifact_type": "clean", "artifact_id": sequence_id,
                "audio_relpath": row["sequence_audio_relpath"],
                "sha256": _sha256(row["sequence_audio_path"]),
            })
    for row in attacks:
        output_hash_rows.append({
            "artifact_type": str(row["attack_type"]), "artifact_id": row["attack_id"],
            "audio_relpath": row["manipulated_audio_relpath"],
            "sha256": _sha256(row["manipulated_audio_path"]),
        })
    _save_csv(output_hash_rows, metadata_root / "output_audio_hashes.csv", OUTPUT_HASH_COLUMNS)

    protected_rows = []
    for group, path in protected:
        before = protected_before[(group, path)]
        after = _sha256(path)
        protected_rows.append({
            "artifact_group": group, "path": path.relative_to(root).as_posix(),
            "sha256_before": before, "sha256_after": after, "unchanged": before == after,
        })
    if protect_existing:
        _save_csv(protected_rows, metadata_root / "protected_artifact_hashes.csv", HASH_COLUMNS)
        if not all(row["unchanged"] for row in protected_rows):
            raise RuntimeError("protected Day 3/3.5/4 artifact changed during Day 4.5 build")
    if not all(row["unchanged"] for row in source_hash_rows):
        raise RuntimeError("raw AISHELL-3 source changed during Day 4.5 build")

    return {
        "split_speakers": split_speakers,
        "sources": sources,
        "text_overlap": text_overlap_counts(audit),
        "lineage": lineage,
        "attacks": attacks,
        "skips": skips,
        "verification": verification,
        "diagnostics": diagnostics,
        "protected": protected_rows,
    }


def verify_day45_reproducibility(
    config_path: str | Path,
    *,
    canonical_root: str | Path,
    regeneration_root: str | Path,
) -> list[dict[str, Any]]:
    """Regenerate independently and compare portable manifests, skips, and WAV hashes."""
    canonical = Path(canonical_root).resolve()
    regenerated = Path(regeneration_root).resolve()
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    run_day45_pipeline(config_path, repository_root=regenerated, protect_existing=False)
    outputs = config["outputs"]
    components = [
        ("source_catalog", outputs["source_catalog"], set()),
        ("text_overlap_audit", outputs["text_overlap_audit"], set()),
        ("longform_manifest", outputs["longform_manifest"], {"sequence_audio_path"}),
        ("attack_manifest", outputs["attack_manifest"], {"clean_audio_path", "manipulated_audio_path"}),
        ("skip_manifest", outputs["skip_manifest"], set()),
        ("paired_diagnostics", outputs["paired_diagnostics"], set()),
        ("waveform_verification", outputs["waveform_verification"], set()),
        ("output_audio_hashes", str(Path(outputs["metadata_directory"]) / "output_audio_hashes.csv"), set()),
    ]
    results = []
    for name, relative, ignored in components:
        left = _normalized_csv(canonical / relative, ignored)
        right = _normalized_csv(regenerated / relative, ignored)
        match = left == right
        results.append({
            "component": name, "match": match,
            "detail": f"canonical_rows={len(left)} regenerated_rows={len(right)}",
        })
    return results


def save_reproducibility(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    _save_csv(records, path, REPRODUCIBILITY_COLUMNS)


def _normalized_csv(path: Path, ignored: set[str]) -> list[tuple[tuple[str, str], ...]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    return [tuple((key, value) for key, value in row.items() if key not in ignored) for row in rows]


def _save_csv(rows: Iterable[Mapping[str, Any]], path: str | Path, columns: list[str]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Day 4.5 expanded paired-attack pilot")
    parser.add_argument("--config", default="configs/day45_expanded_paired.yaml")
    parser.add_argument("--repository-root", default=".")
    args = parser.parse_args()
    result = run_day45_pipeline(args.config, repository_root=args.repository_root)
    sequences = {row["sequence_id"] for row in result["lineage"]}
    cases = {row["paired_case_id"] for row in result["attacks"]}
    print(
        f"Day45 speakers={sum(map(len, result['split_speakers'].values()))} "
        f"sources={len(result['sources'])} sequences={len(sequences)} "
        f"paired_cases={len(cases)} attacks={len(result['attacks'])} skips={len(result['skips'])}"
    )


if __name__ == "__main__":
    main()
