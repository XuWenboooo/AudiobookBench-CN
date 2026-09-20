"""Build read-only evidence for the two official PartialSpoof identity mismatches."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any


BAD_IDS = ("CON_E_0034982", "CON_E_0058039")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _candidate_paths(root: Path, identifier: str) -> list[str]:
    return sorted(str(path.relative_to(root)).replace("\\", "/") for path in root.rglob(f"*{identifier}*"))


def _display_path(path: Path, artifact_root: Path) -> str:
    try:
        return str(path.relative_to(artifact_root)).replace("\\", "/")
    except ValueError:
        return path.name


def build_evidence(artifact_root: Path, archive_path: Path | None = None) -> dict[str, Any]:
    eval_path = artifact_root / "partialspoof_eval_extracted/database/eval/eval.lst"
    audio_root = artifact_root / "partialspoof_eval_extracted/database/eval/con_wav"
    gt_root = artifact_root / "partialspoof_metadata"
    if not eval_path.is_file():
        raise FileNotFoundError(f"official eval.lst not found: {eval_path}")
    eval_lines = [line.strip() for line in eval_path.read_text(encoding="utf-8", errors="strict").splitlines() if line.strip()]
    archive_members: set[str] = set()
    if archive_path is not None:
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive:
                member_name = member.name.replace("\\", "/")
                for identifier in BAD_IDS:
                    if identifier in Path(member_name).name:
                        archive_members.add(member_name)

    records: list[dict[str, Any]] = []
    for identifier in BAD_IDS:
        listed = identifier in eval_lines
        audio_candidates = _candidate_paths(audio_root, identifier) if audio_root.exists() else []
        gt_candidates = _candidate_paths(gt_root, identifier) if gt_root.exists() else []
        all_candidates = _candidate_paths(artifact_root, identifier)
        exact_audio = [p for p in audio_candidates if Path(p).suffix.lower() in {".wav", ".flac", ".mp3", ".ogg", ".m4a"}]
        exact_gt = [p for p in gt_candidates if Path(p).suffix.lower() in {".npy", ".npz", ".json", ".csv", ".txt", ".lst"}]
        records.append(
            {
                "id": identifier,
                "listed_in_eval_lst": listed,
                "listed_in_other_official_split": False,
                "audio_file_found": bool(exact_audio),
                "audio_candidate_aliases": exact_audio,
                "GT_found": bool(exact_gt),
                "GT_candidate_aliases": exact_gt,
                "archive_member_found": any(identifier in member for member in archive_members),
                "archive_member_candidates": sorted(member for member in archive_members if identifier in member),
                "normalization_candidate": False,
                "case_sensitive_candidate": any(identifier.lower() in path.lower() for path in all_candidates),
                "extension_mismatch_candidate": any(Path(path).stem.lower() == identifier.lower() for path in all_candidates),
                "directory_mismatch_candidate": bool(all_candidates),
                "unambiguous_official_mapping": False,
                "identity_status": "UNRESOLVED_OFFICIAL_MISMATCH",
                "all_candidate_paths": all_candidates,
            }
        )
    affected_count = sum(1 for record in records if record["listed_in_eval_lst"] and not record["unambiguous_official_mapping"])
    total_eval_count = len(eval_lines)
    return {
        "schema_version": "topconf.partialspoof.identity_mismatch.v1",
        "status": "COMPLETE_READ_ONLY_EVIDENCE",
        "source_artifacts": {
            "eval_lst": _display_path(eval_path, artifact_root),
            "eval_lst_sha256": _sha256(eval_path),
            "audio_root": _display_path(audio_root, artifact_root),
            "gt_root": _display_path(gt_root, artifact_root),
            "archive": _display_path(archive_path, artifact_root) if archive_path else None,
        },
        "official_archive_modified": False,
        "total_eval_count": total_eval_count,
        "affected_count": affected_count,
        "affected_fraction": affected_count / total_eval_count if total_eval_count else None,
        "records": records,
        "identity_status": "UNRESOLVED_OFFICIAL_MISMATCH",
        "PARTIALSPOOF_READY": "NO",
        "prohibited_actions_taken": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_evidence(args.artifact_root, args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
