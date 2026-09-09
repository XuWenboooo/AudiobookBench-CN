"""Deterministic AISHELL-3 expanded-pilot selection for Day 4.5.

Selection uses only corpus identity, transcript availability, metadata, and
lexicographic IDs. It must not inspect waveform quality or model outcomes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from pathlib import Path
from typing import Any, Iterable, Mapping
import unicodedata


EXPANDED_SOURCE_COLUMNS = [
    "audio_path", "sample_id", "pair_id", "source_sample_id", "source_type",
    "generator", "generator_family", "speaker", "text_id", "is_manipulated",
    "attack_type", "attack_start", "attack_end", "attack_generator",
    "source_generator", "replacement_speaker", "split", "dataset",
    "original_partition", "selection_rank", "age_group", "gender", "accent",
    "transcript_zh", "transcript_pinyin", "transcript_source", "audio_relpath",
]

TEXT_AUDIT_COLUMNS = [
    "normalized_text", "train_count", "val_count", "test_count", "split_count",
    "train_sample_ids", "val_sample_ids", "test_sample_ids",
]


class ExpandedPilotError(ValueError):
    """Raised when expanded-pilot selection or lineage is invalid."""


def normalize_chinese_text(value: Any) -> str:
    """Apply the frozen Day 3.5 exact-text normalization."""
    return unicodedata.normalize("NFC", str(value).strip())


def load_speaker_metadata(dataset_root: str | Path) -> dict[str, dict[str, str]]:
    path = Path(dataset_root) / "raw" / "spk-info.txt"
    metadata: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ExpandedPilotError(f"invalid speaker metadata row: {line!r}")
        speaker, age_group, gender, accent = parts
        if speaker in metadata:
            raise ExpandedPilotError(f"duplicate speaker metadata: {speaker}")
        metadata[speaker] = {
            "age_group": age_group,
            "gender": gender,
            "accent": accent,
        }
    return metadata


def _load_transcripts(path: Path) -> dict[str, tuple[str, str]]:
    transcripts: dict[str, tuple[str, str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            filename, annotated = line.split("\t", 1)
        except ValueError as exc:
            raise ExpandedPilotError(f"invalid content row {path}:{line_number}") from exc
        tokens = annotated.split()
        if not tokens or len(tokens) % 2:
            raise ExpandedPilotError(f"invalid character/pinyin pairs {path}:{line_number}")
        sample_id = Path(filename).stem
        value = ("".join(tokens[0::2]), " ".join(tokens[1::2]))
        if sample_id in transcripts and transcripts[sample_id] != value:
            raise ExpandedPilotError(f"conflicting transcript for {sample_id}")
        transcripts[sample_id] = value
    return transcripts


def inventory_aishell3(dataset_root: str | Path) -> list[dict[str, str]]:
    """Return traceable WAV/transcript/metadata rows without decoding audio."""
    root = Path(dataset_root).resolve()
    metadata = load_speaker_metadata(root)
    inventory: list[dict[str, str]] = []
    seen: set[str] = set()
    for partition in ("train", "test"):
        transcript_path = root / "raw" / partition / "content.txt"
        transcripts = _load_transcripts(transcript_path)
        wav_root = root / "raw" / partition / "wav"
        for path in sorted(wav_root.glob("*/*.wav"), key=lambda item: item.as_posix()):
            sample_id = path.stem
            speaker = path.parent.name
            if sample_id in seen:
                raise ExpandedPilotError(f"duplicate WAV sample_id across partitions: {sample_id}")
            if speaker not in metadata or sample_id not in transcripts:
                continue
            seen.add(sample_id)
            transcript_zh, transcript_pinyin = transcripts[sample_id]
            inventory.append({
                "sample_id": sample_id,
                "speaker": speaker,
                "original_partition": partition,
                "audio_path": str(path.resolve()),
                "audio_relpath": path.resolve().relative_to(root).as_posix(),
                "transcript_zh": transcript_zh,
                "transcript_pinyin": transcript_pinyin,
                "transcript_source": str(transcript_path.resolve()),
                **metadata[speaker],
            })
    return sorted(inventory, key=lambda row: (row["speaker"], row["sample_id"]))


def select_expanded_speakers(
    inventory: Iterable[Mapping[str, Any]],
    split_slots: Mapping[str, Iterable[Mapping[str, Any]]],
    *,
    minimum_rows: int = 40,
) -> dict[str, list[str]]:
    """Resolve exact anchors and metadata slots deterministically."""
    rows = [dict(row) for row in inventory]
    by_speaker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_speaker[str(row["speaker"])].append(row)
    eligible = {speaker for speaker, group in by_speaker.items() if len(group) >= minimum_rows}
    selected: set[str] = set()
    result: dict[str, list[str]] = {}
    for split in ("train", "val", "test"):
        resolved: list[str] = []
        for slot in split_slots.get(split, []):
            slot = dict(slot)
            exact = str(slot.get("speaker_id", "")).strip()
            if exact:
                candidates = [exact] if exact in eligible and exact not in selected else []
            else:
                required = {
                    key: str(slot[key]) for key in ("age_group", "gender", "accent")
                    if key in slot
                }
                candidates = sorted(
                    speaker for speaker in eligible - selected
                    if all(str(by_speaker[speaker][0].get(key, "")) == value for key, value in required.items())
                )
            if not candidates:
                raise ExpandedPilotError(f"no eligible speaker for split={split}, slot={slot}")
            chosen = candidates[0]
            selected.add(chosen)
            resolved.append(chosen)
        result[split] = resolved
    return result


def build_expanded_source_catalog(
    inventory: Iterable[Mapping[str, Any]],
    split_speakers: Mapping[str, Iterable[str]],
    *,
    utterances_per_speaker: int = 40,
) -> list[dict[str, Any]]:
    rows = [dict(row) for row in inventory]
    by_speaker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_speaker[str(row["speaker"])].append(row)
    speaker_to_split: dict[str, str] = {}
    for split, speakers in split_speakers.items():
        for speaker in speakers:
            if speaker in speaker_to_split:
                raise ExpandedPilotError(f"speaker crosses splits: {speaker}")
            speaker_to_split[str(speaker)] = str(split)

    catalog: list[dict[str, Any]] = []
    for speaker, split in sorted(speaker_to_split.items(), key=lambda item: (item[1], item[0])):
        selected = sorted(by_speaker.get(speaker, []), key=lambda row: str(row["sample_id"]))[:utterances_per_speaker]
        if len(selected) != utterances_per_speaker:
            raise ExpandedPilotError(f"speaker {speaker} has only {len(selected)} valid rows")
        for rank, source in enumerate(selected):
            sample_id = str(source["sample_id"])
            catalog.append({
                "audio_path": source["audio_path"],
                "sample_id": sample_id,
                "pair_id": f"aishell3_pair_{sample_id}",
                "source_sample_id": sample_id,
                "source_type": "natural",
                "generator": "human",
                "generator_family": "human",
                "speaker": speaker,
                "text_id": f"aishell3_text_{sample_id}",
                "is_manipulated": False,
                "attack_type": "",
                "attack_start": "",
                "attack_end": "",
                "attack_generator": "",
                "source_generator": "human",
                "replacement_speaker": "",
                "split": split,
                "dataset": "AISHELL-3",
                "original_partition": source["original_partition"],
                "selection_rank": rank,
                "age_group": source["age_group"],
                "gender": source["gender"],
                "accent": source["accent"],
                "transcript_zh": source["transcript_zh"],
                "transcript_pinyin": source["transcript_pinyin"],
                "transcript_source": source["transcript_source"],
                "audio_relpath": source["audio_relpath"],
            })
    validate_expanded_source_catalog(catalog)
    return catalog


def validate_expanded_source_catalog(records: Iterable[Mapping[str, Any]]) -> None:
    rows = [dict(row) for row in records]
    if not rows:
        raise ExpandedPilotError("expanded source catalog must not be empty")
    sample_ids = [str(row.get("sample_id", "")) for row in rows]
    if len(sample_ids) != len(set(sample_ids)):
        raise ExpandedPilotError("expanded source sample_id must be unique")
    speaker_splits: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        missing = [column for column in EXPANDED_SOURCE_COLUMNS if column not in row]
        if missing:
            raise ExpandedPilotError(f"expanded source row missing columns: {missing}")
        if not Path(str(row["audio_path"])).is_file() or not str(row["transcript_zh"]):
            raise ExpandedPilotError(f"missing WAV or transcript: {row.get('sample_id')}")
        if str(row["source_sample_id"]) != str(row["sample_id"]):
            raise ExpandedPilotError("clean source must self-reference source_sample_id")
        if str(row["source_type"]) != "natural" or str(row["is_manipulated"]).lower() not in {"false", "0"}:
            raise ExpandedPilotError("expanded source catalog accepts clean natural rows only")
        speaker_splits[str(row["speaker"])].add(str(row["split"]))
    if any(len(splits) != 1 for splits in speaker_splits.values()):
        raise ExpandedPilotError("expanded pilot speakers must be split-disjoint")


def build_text_overlap_audit(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in records:
        text = normalize_chinese_text(row["transcript_zh"])
        grouped[text][str(row["split"])].append(str(row["sample_id"]))
    output = []
    for text, splits in sorted(grouped.items()):
        output.append({
            "normalized_text": text,
            "train_count": len(splits["train"]),
            "val_count": len(splits["val"]),
            "test_count": len(splits["test"]),
            "split_count": sum(bool(splits[name]) for name in ("train", "val", "test")),
            "train_sample_ids": ";".join(sorted(splits["train"])),
            "val_sample_ids": ";".join(sorted(splits["val"])),
            "test_sample_ids": ";".join(sorted(splits["test"])),
        })
    return output


def text_overlap_counts(audit_rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    rows = list(audit_rows)
    return {
        "train_val": sum(int(row["train_count"]) > 0 and int(row["val_count"]) > 0 for row in rows),
        "train_test": sum(int(row["train_count"]) > 0 and int(row["test_count"]) > 0 for row in rows),
        "val_test": sum(int(row["val_count"]) > 0 and int(row["test_count"]) > 0 for row in rows),
        "train_val_test": sum(all(int(row[f"{split}_count"]) > 0 for split in ("train", "val", "test")) for row in rows),
    }


def save_expanded_source_catalog(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    rows = [dict(row) for row in records]
    validate_expanded_source_catalog(rows)
    _save_csv(rows, path, EXPANDED_SOURCE_COLUMNS)


def save_text_overlap_audit(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    _save_csv([dict(row) for row in records], path, TEXT_AUDIT_COLUMNS)


def _save_csv(rows: list[dict[str, Any]], path: str | Path, columns: list[str]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
