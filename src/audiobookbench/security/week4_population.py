"""Outcome-blind deterministic candidate-population construction for Week4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


TOTAL_TARGET, DEV_TARGET, VALIDATION_TARGET, HELD_OUT_TARGET = 48, 24, 12, 12
REQUIRED_FIELDS = ("speaker", "source_speaker", "reference_speaker", "source_sample_id", "reference_sample_id", "source_text_sha256", "reference_text_sha256", "source_audio_sha256", "reference_audio_sha256", "same_speaker", "different_utterance", "different_text", "eligible")


class PopulationContractError(ValueError):
    pass


def _rank(seed: int, row: Mapping[str, Any]) -> str:
    payload = f"{seed}|{row['speaker']}|{row['source_sample_id']}|{row['reference_sample_id']}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_candidate_population(rows: Iterable[Mapping[str, Any]], *, selection_seed: int, prior_week_speakers: set[str]) -> dict[str, Any]:
    """Create a candidate-only manifest without importing or calling a detector."""
    if not isinstance(selection_seed, int) or isinstance(selection_seed, bool):
        raise PopulationContractError("selection seed must be an integer")
    exclusions: list[dict[str, str]] = []; by_speaker: dict[str, list[dict[str, Any]]] = {}
    for raw in rows:
        row = dict(raw); missing = [field for field in REQUIRED_FIELDS if field not in row]; label = str(row.get("source_sample_id", "unknown"))
        if missing:
            exclusions.append({"source_sample_id": label, "reason": f"missing:{','.join(missing)}"}); continue
        speaker = str(row["speaker"])
        if not row["eligible"] or not row["same_speaker"] or str(row["source_speaker"]) != speaker or str(row["reference_speaker"]) != speaker:
            exclusions.append({"source_sample_id": label, "reason": "same_speaker_eligibility_failed"}); continue
        if not row["different_utterance"] or not row["different_text"]:
            exclusions.append({"source_sample_id": label, "reason": "reference_independence_failed"}); continue
        if speaker in prior_week_speakers:
            exclusions.append({"source_sample_id": label, "reason": "prior_week_speaker_overlap"}); continue
        if any(not isinstance(row[field], str) or not row[field] for field in ("source_text_sha256", "reference_text_sha256", "source_audio_sha256", "reference_audio_sha256")):
            exclusions.append({"source_sample_id": label, "reason": "identity_hash_missing"}); continue
        by_speaker.setdefault(speaker, []).append(row)
    representatives = []
    for speaker, candidates in by_speaker.items():
        selected = min(candidates, key=lambda row: (_rank(selection_seed, row), str(row["source_sample_id"])))
        representatives.append(selected)
        for unselected in candidates:
            if unselected is not selected:
                exclusions.append({"source_sample_id": str(unselected["source_sample_id"]), "reason": "speaker_representative_not_selected"})
    selected_rows = sorted(representatives, key=lambda row: (_rank(selection_seed, row), str(row["speaker"])))[:TOTAL_TARGET]
    if len(selected_rows) < TOTAL_TARGET:
        return {"status": "INSUFFICIENT_ELIGIBLE_SPEAKER_DISJOINT_CANDIDATES", "selection_seed": selection_seed, "selected_cases": [], "exclusions": exclusions, "eligible_unique_speakers": len(representatives), "target_cases": TOTAL_TARGET}
    cases = []
    for index, row in enumerate(selected_rows):
        split = "dev" if index < DEV_TARGET else "validation" if index < DEV_TARGET + VALIDATION_TARGET else "held_out"
        cases.append({"case_id": f"week4_case_{index + 1:04d}", "speaker_id": row["speaker"], "speaker": row["speaker"], "source_speaker": row["source_speaker"], "reference_speaker": row["reference_speaker"], "source_sample_id": row["source_sample_id"], "reference_sample_id": row["reference_sample_id"], "source_path": row.get("source_path"), "reference_path": row.get("reference_path"), "source_audio_sha256": row["source_audio_sha256"], "reference_audio_sha256": row["reference_audio_sha256"], "source_text_exact": row.get("source_text_exact"), "reference_text_exact": row.get("reference_text_exact"), "source_text_sha256": row["source_text_sha256"], "reference_text_sha256": row["reference_text_sha256"], "split": split, "selection_reason": "deterministic_seeded_speaker_disjoint_selection", "eligibility_decision": "PASS", "exclusion_reason": None, "prior_week_overlap": False, "selection_seed": selection_seed, "selection_rank": _rank(selection_seed, row)})
    return {"status": "CANDIDATE_POPULATION_REQUIRES_INDEPENDENT_ELIGIBILITY_REVIEW", "selection_seed": selection_seed, "target_cases": TOTAL_TARGET, "selected_cases": cases, "exclusions": exclusions, "eligible_unique_speakers": len(representatives), "split_counts": {"dev": DEV_TARGET, "validation": VALIDATION_TARGET, "held_out": HELD_OUT_TARGET}}


def write_candidate_population_manifest(manifest: Mapping[str, Any], path: Path) -> None:
    """Persist a candidate manifest only; callers choose a TEST_ONLY/output path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(manifest), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def build_aishell3_train_candidate_population(aishell_root: Path, *, selection_seed: int, prior_week_speakers: set[str]) -> dict[str, Any]:
    """Build the real candidate population from AISHELL-3 with read-only access.

    The function reads train audio and the official character/pinyin content
    file, hashes inputs in memory, and never calls a detector or writes under
    ``aishell_root``.  It returns a final manifest only after all 48 checks pass.
    """
    aishell_root = Path(aishell_root)
    content: dict[str, str] = {}
    for partition in ("train", "test"):
        content_path = aishell_root / "raw" / partition / "content.txt"
        if not content_path.is_file():
            raise PopulationContractError(f"AISHELL-3 content file missing: {content_path}")
        for line in content_path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            tokens = parts[1].split()
            text = "".join(tokens[0::2])
            content[Path(parts[0]).stem] = text
    rows: list[dict[str, Any]] = []
    train_root = aishell_root / "raw" / "train" / "wav"
    for speaker_dir in sorted((path for path in train_root.iterdir() if path.is_dir()), key=lambda path: path.name):
        files = sorted(speaker_dir.glob("*.wav"), key=lambda path: path.name)
        pair: tuple[Path, Path] | None = None
        for index, source in enumerate(files):
            for reference in files[index + 1:]:
                if source.stem in content and reference.stem in content and content[source.stem] != content[reference.stem]:
                    pair = source, reference
                    break
            if pair is not None:
                break
        if pair is None:
            continue
        source, reference = pair
        text_hash = lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest().upper()
        rows.append({"speaker": speaker_dir.name, "source_speaker": speaker_dir.name, "reference_speaker": speaker_dir.name, "source_sample_id": source.stem, "reference_sample_id": reference.stem, "source_path": str(source), "reference_path": str(reference), "source_text_exact": content[source.stem], "reference_text_exact": content[reference.stem], "source_text_sha256": text_hash(content[source.stem]), "reference_text_sha256": text_hash(content[reference.stem]), "source_audio_sha256": hashlib.sha256(source.read_bytes()).hexdigest().upper(), "reference_audio_sha256": hashlib.sha256(reference.read_bytes()).hexdigest().upper(), "same_speaker": True, "different_utterance": source.stem != reference.stem, "different_text": content[source.stem] != content[reference.stem], "eligible": True})
    manifest = build_candidate_population(rows, selection_seed=selection_seed, prior_week_speakers=prior_week_speakers)
    if len(manifest.get("selected_cases", [])) != TOTAL_TARGET or manifest.get("split_counts") != {"dev": DEV_TARGET, "validation": VALIDATION_TARGET, "held_out": HELD_OUT_TARGET}:
        raise PopulationContractError("frozen 48/24/12/12 population could not be finalized")
    manifest["status"] = "FINALIZED"
    manifest["aishell3_root"] = str(aishell_root)
    manifest["builder"] = "build_aishell3_train_candidate_population"
    manifest["d0_invoked"] = False
    manifest["selected_without_d0"] = True
    manifest["d0_outcome_inspected"] = False
    manifest["candidate_pool_count"] = manifest["eligible_unique_speakers"] + len([row for row in manifest["exclusions"] if row["reason"] == "prior_week_speaker_overlap"])
    manifest["candidate_pair_count"] = manifest["candidate_pool_count"]
    manifest["prior_week_speaker_count"] = len([row for row in manifest["exclusions"] if row["reason"] == "prior_week_speaker_overlap"])
    manifest["eligible_after_prior_exclusion"] = manifest["eligible_unique_speakers"]
    manifest["final_case_count"] = len(manifest["selected_cases"])
    return manifest
