from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable, Iterator

import numpy as np


AUTHORIZATION_ID = "P3T-2026-09-13-01"
EXPECTED_CASES = 42_471
DATASET_ID = "PartialEdit_v1.1_E1"
SAMPLE_RATE = 16_000
SEED = 1234
ALLOWED_TERMINAL_STATUSES = {
    "VALID_INFERENCE",
    "AUDIO_LOAD_FAILURE",
    "MODEL_INFERENCE_FAILURE",
    "CUDA_OOM",
    "INVALID_OUTPUT",
    "NONFINITE_OUTPUT",
    "INFRASTRUCTURE_FAILURE",
}
FORBIDDEN_GT_KEYS = {
    "target_start",
    "target_end",
    "fake_label",
    "mechanism_outcome",
    "edited_regions",
    "ground_truth_intervals",
    "gt",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def to_jsonable(value: Any) -> Any:
    """Convert tensor/NumPy values without lossy score selection."""

    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return to_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if hasattr(value, "detach") and hasattr(value, "cpu"):
        return to_jsonable(value.detach().cpu().numpy())
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite value cannot be serialized")
        return value
    if isinstance(value, (int, str, bool)) or value is None:
        return value
    raise TypeError(f"unsupported JSON value: {type(value)!r}")


def assert_finite_tree(value: Any, *, path: str = "value") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert_finite_tree(item, path=f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_finite_tree(item, path=f"{path}[{index}]")
        return
    if isinstance(value, np.ndarray):
        if not np.isfinite(value).all():
            raise ValueError(f"non-finite array at {path}")
        return
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite value at {path}")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass


def read_case_manifest(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\r\n").split("\t")
        expected = ["case_index", "case_id", "audio_relpath", "audio_path"]
        if header != expected:
            raise ValueError(f"manifest header must be {expected!r}, got {header!r}")
        for line_number, line in enumerate(handle, start=2):
            fields = line.rstrip("\r\n").split("\t")
            if len(fields) != 4:
                raise ValueError(f"manifest line {line_number}: expected 4 fields")
            try:
                case_index = int(fields[0])
            except ValueError as exc:
                raise ValueError(f"manifest line {line_number}: invalid case_index") from exc
            if case_index < 0 or not fields[1] or not fields[2] or not fields[3]:
                raise ValueError(f"manifest line {line_number}: empty or invalid case field")
            yield {
                "case_index": case_index,
                "case_id": fields[1],
                "audio_relpath": fields[2],
                "audio_path": fields[3],
            }


def materialize_manifest_rows(csv_path: str | Path, audio_root: str | Path) -> list[dict[str, Any]]:
    """Build an audio-only E1 manifest while ignoring all annotation columns."""

    import csv

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    root = Path(audio_root).resolve()
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        for row_number, row in enumerate(csv.reader(handle), start=1):
            if not row or all(not field.strip() for field in row):
                continue
            rel = row[0].strip().replace("\\", "/")
            if not rel.startswith("E1/"):
                continue
            if not rel or rel in seen or Path(rel).is_absolute():
                raise ValueError(f"CSV row {row_number}: invalid/duplicate E1 path {rel!r}")
            # The frozen manifest keeps the official ``E1/...`` identifier,
            # while the materialized root itself is the E1 directory.
            rel_under_root = rel[3:] if root.name.lower() == "e1" else rel
            candidate = (root / Path(rel_under_root)).resolve()
            if root not in candidate.parents:
                raise ValueError(f"CSV row {row_number}: path escapes E1 root")
            if not candidate.is_file():
                raise FileNotFoundError(candidate)
            seen.add(rel)
            rows.append(
                {
                    "case_index": len(rows),
                    "case_id": rel,
                    "audio_relpath": rel,
                    "audio_path": str(candidate),
                }
            )
    if len(rows) != EXPECTED_CASES:
        raise ValueError(f"expected {EXPECTED_CASES} E1 rows, found {len(rows)}")
    return rows


def write_manifest(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    path = Path(path)
    lines = ["case_index\tcase_id\taudio_relpath\taudio_path"]
    for row in rows:
        lines.append("\t".join(str(row[key]) for key in ("case_index", "case_id", "audio_relpath", "audio_path")))
    content = "\n".join(lines) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise FileExistsError(f"refusing to overwrite a different manifest: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            yield value


def append_jsonl(path: str | Path, value: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(to_jsonable(value)) + "\n")
        handle.flush()


def existing_terminal_ids(path: str | Path) -> set[str]:
    ids: set[str] = set()
    if not Path(path).exists():
        return ids
    for record in read_jsonl(path):
        case_id = record.get("case_id")
        if not isinstance(case_id, str) or case_id in ids:
            raise ValueError(f"duplicate or invalid terminal case_id in {path}: {case_id!r}")
        if record.get("terminal") is not True:
            raise ValueError(f"non-terminal record in terminal raw output: {case_id!r}")
        ids.add(case_id)
    return ids


def attempt_counts(path: str | Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not Path(path).exists():
        return counts
    for record in read_jsonl(path):
        case_id = record.get("case_id")
        attempt = record.get("attempt")
        if not isinstance(case_id, str) or not isinstance(attempt, int) or attempt < 1:
            raise ValueError(f"invalid attempt record in {path}")
        counts[case_id] = max(counts.get(case_id, 0), attempt)
    return counts


def forbidden_keys(value: Any, *, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in FORBIDDEN_GT_KEYS:
                found.append(f"{path}.{key}" if path else str(key))
            found.extend(forbidden_keys(item, path=f"{path}.{key}" if path else str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(forbidden_keys(item, path=f"{path}[{index}]"))
    return found
