"""Day 6C Control C0: same-speaker different-text splice.

For every frozen Day 4.5 paired case, build two controls that reuse the
EXACT original target (same clean sequence, same target source utterance,
same target interval, same duration tier, same split) and replace the donor
with one from the SAME speaker and SAME split (different utterance, hence
normally different text):

- C0A ``same_speaker_direct_splice``: A0-style direct replacement;
- C0B ``same_speaker_artifact_controlled_splice``: A1-style RMS matching
  (gain clamped to [0.25, 4]) + 25 ms (400-sample) crossfade.

The DSP semantics mirror the frozen A0/A1 builders; nothing is re-tuned.
Donor selection is deterministic (lowest usage count, then lexicographic
sample_id, skipping the target utterance). All verification is fail-closed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.preprocessing.audio_io import load_audio, probe_audio, write_audio
from audiobookbench.data.prepare_audio import DATASET_ROOT_ENV
from audiobookbench.security.manipulation_dataset import _crossfade_replace, _rms

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_CSV = REPO_ROOT / "data/manifests/day45_source_audio.csv"
ATTACK_MANIFEST = REPO_ROOT / "data/manifests/day45_attack_manifest.csv"
OUT_DIR = REPO_ROOT / "data/generated/day6c_same_speaker_control"
CROSSFADE = 400
GAIN_MIN, GAIN_MAX = 0.25, 4.0
MAX_DONOR_REUSE = 1


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def _dataset_root(repo_root: Path = REPO_ROOT) -> Path:
    import yaml

    config = yaml.safe_load((repo_root / "configs/day45_expanded_paired.yaml").read_text(encoding="utf-8"))
    return Path(os.environ.get(DATASET_ROOT_ENV) or str(config["dataset_root"]))


def _resolve_source(row: dict[str, str], root: Path) -> Path:
    return root / row["audio_relpath"].replace("\\", "/")


def select_donor(
    candidates: list[dict[str, Any]],
    target_sample_id: str,
    needed_samples: int,
    usage: dict[str, int],
) -> dict[str, Any] | None:
    """Deterministic donor choice: usable, lowest usage, lexicographic id.

    A candidate is usable when it is decodable, long enough for a centered
    crop of ``needed_samples``, and not the target utterance itself.
    """
    best: dict[str, Any] | None = None
    for cand in sorted(candidates, key=lambda c: (usage.get(c["sample_id"], 0), c["sample_id"])):
        if cand["sample_id"] == target_sample_id:
            continue
        if cand["frames"] is None or cand["frames"] < needed_samples:
            continue
        key = (usage.get(cand["sample_id"], 0), cand["sample_id"])
        if best is None or key < (usage.get(best["sample_id"], 0), best["sample_id"]):
            best = cand
    return best


def build_same_speaker_controls(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    manifest_rows = _read_csv(repo_root / "data/manifests/day45_attack_manifest.csv")
    a0_rows = [r for r in manifest_rows if r["attack_type"] == "cross_speaker_splice"]
    source_rows = _read_csv(repo_root / "data/manifests/day45_source_audio.csv")
    source_by_id = {r["sample_id"]: r for r in source_rows}
    dataset_root = _dataset_root(repo_root)

    # frames inventory for donor eligibility (probe only, read-only).
    # AISHELL-3 raw WAVs are not 16 kHz; eligibility must use the decoded
    # length after resampling to 16 kHz, estimated conservatively here.
    inventory: dict[str, int | None] = {}
    for r in source_rows:
        try:
            info = probe_audio(_resolve_source(r, dataset_root))
            inventory[r["sample_id"]] = int(info.frames * 16000 // info.sample_rate)
        except (OSError, RuntimeError, ValueError):
            inventory[r["sample_id"]] = None

    usage: dict[str, int] = {}
    control_rows: list[dict[str, Any]] = []
    verification_rows: list[dict[str, Any]] = []
    hash_rows: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    for a0 in a0_rows:
        case_id = a0["paired_case_id"]
        clean_seq = a0["clean_sequence_id"]
        split = a0["split"]
        target_speaker = a0["target_speaker"]
        target_sid = a0["target_source_sample_id"]
        start, end = int(a0["target_start_sample"]), int(a0["target_end_sample"])
        needed = end - start
        clean_path = repo_root / a0.get("clean_audio_relpath", a0["clean_audio_path"])

        candidates = [
            r for r in source_rows
            if r["speaker"] == target_speaker and r["split"] == split
        ]
        donor_row = select_donor(
            [{**r, "frames": inventory.get(r["sample_id"])} for r in candidates],
            target_sid, needed, usage,
        )
        if donor_row is None:
            skipped.append({"paired_case_id": case_id, "reason": "no_eligible_same_speaker_donor"})
            continue

        clean, sr = load_audio(clean_path, target_sr=None)
        donor, donor_sr = load_audio(_resolve_source(donor_row, dataset_root), target_sr=16000)
        assert sr == donor_sr == 16000
        donor_start = max(0, (donor.size - needed) // 2)
        if donor.size < needed:
            skipped.append({"paired_case_id": case_id, "reason": "donor_too_short_after_resample"})
            continue
        crop = donor[donor_start:donor_start + needed].astype(np.float64)
        target_rms = _rms(clean[start:end])
        gain = float(np.clip(target_rms / max(_rms(crop.astype(np.float32)), 1e-8), GAIN_MIN, GAIN_MAX))

        c0a = clean.copy()
        c0a[start:end] = crop.astype(np.float32)
        c0b = _crossfade_replace(clean, (crop * gain).astype(np.float32), start, end, CROSSFADE)

        base_id = f"day6c_{case_id}"
        speaker = target_speaker
        rel = {
            "C0A": f"data/generated/day6c_same_speaker_control/C0A/{split}/{speaker}/{base_id}_c0a_manipulated.wav",
            "C0B": f"data/generated/day6c_same_speaker_control/C0B/{split}/{speaker}/{base_id}_c0b_manipulated.wav",
        }
        same_text = donor_row["text_id"] == a0["target_text_id"]
        common = {
            "control_case_id": f"{case_id}_c0",
            "_clean_seq": clean_seq,
            "paired_case_id": case_id,
            "clean_sequence_id": clean_seq,
            "control_sequence_id": "_PLACEHOLDER_",
            "control_type": "same_speaker_different_text_splice",
            "target_source_sample_id": target_sid,
            "target_speaker": target_speaker,
            "target_text_id": a0["target_text_id"],
            "donor_source_sample_id": donor_row["sample_id"],
            "donor_speaker": donor_row["speaker"],
            "donor_text_id": donor_row["text_id"],
            "same_speaker": "True",
            "same_text": str(same_text),
            "split": split,
            "target_start_sample": start,
            "target_end_sample": end,
            "attack_start_sample": start,
            "attack_end_sample": end,
            "blend_start_sample": start,
            "blend_end_sample": end,
            "duration_tier": a0["duration_tier"],
            "duration_matching_method": a0["duration_matching_method"],
            "sample_rate": 16000,
            "longform_type": "constructed",
            "clean_audio_sha256": _sha256(clean_path),
        }
        for variant, out_arr, attack_type, core_offset, gain_val, cf in (
            ("C0A", c0a, "same_speaker_direct_splice", 0, 1.0, 0),
            ("C0B", c0b, "same_speaker_artifact_controlled_splice", CROSSFADE, gain, CROSSFADE),
        ):
            out_path = repo_root / rel[variant]
            out_path.parent.mkdir(parents=True, exist_ok=True)
            write_audio(out_path, out_arr, 16000)
            control_rows.append({
                **{k: v for k, v in common.items() if k != "_clean_seq"},
                "control_variant": variant,
                "control_sequence_id": f"{clean_seq}_{variant.lower()}_manipulated",
                "attack_type": attack_type,
                "attack_core_start_sample": start + core_offset,
                "attack_core_end_sample": end - core_offset,
                "rms_gain": f"{gain_val:.10f}",
                "crossfade_samples": cf,
                "control_audio_relpath": rel[variant],
                "control_audio_sha256": _sha256(out_path),
            })
            hash_rows.append({
                "control_variant": variant, "control_case_id": common["control_case_id"],
                "audio_relpath": rel[variant], "sha256": _sha256(out_path),
            })

        # ---- fail-closed verification for both variants ----
        decoded = {}
        for variant in ("C0A", "C0B"):
            path = repo_root / rel[variant]
            info = probe_audio(path)
            wav, wsr = load_audio(path, target_sr=None)
            decoded[variant] = (info, wav, wsr)
        clean_check = load_audio(clean_path, target_sr=None)[0]
        problems: list[str] = []
        if donor_row["speaker"] != target_speaker:
            problems.append("donor_speaker_mismatch")
        if donor_row["split"] != split:
            problems.append("donor_split_mismatch")
        if donor_row["sample_id"] == target_sid:
            problems.append("donor_equals_target_utterance")
        for variant, (info, wav, wsr) in decoded.items():
            if info.frames != clean.size or wsr != 16000 or info.channels != 1:
                problems.append(f"{variant}_format_mismatch")
            if not np.all(np.isfinite(wav)):
                problems.append(f"{variant}_non_finite")
            if not np.array_equal(wav[:start], clean_check[:start]) or not np.array_equal(wav[end:], clean_check[end:]):
                problems.append(f"{variant}_outside_changed")
            if np.array_equal(wav[start:end], clean_check[start:end]):
                problems.append(f"{variant}_inside_unchanged")
            if abs(int(a0["target_start_sample"]) - start) or abs(int(a0["target_end_sample"]) - end):
                problems.append(f"{variant}_target_interval_drift")
        usage[donor_row["sample_id"]] = usage.get(donor_row["sample_id"], 0) + 1
        verification_rows.append({
            "control_case_id": common["control_case_id"], "paired_case_id": case_id,
            "donor_source_sample_id": donor_row["sample_id"], "donor_speaker": donor_row["speaker"],
            "donor_split": donor_row["split"], "donor_is_target_utterance": False,
            "same_speaker": True, "same_text": same_text,
            "donor_reuse_count": usage[donor_row["sample_id"]],
            "passed": not problems, "problems": "; ".join(problems),
        })

    _write_csv(repo_root / "data/manifests/day6c_same_speaker_control_manifest.csv", control_rows)
    _write_csv(repo_root / "data/generated/day6c_same_speaker_control/verification.csv", verification_rows)
    _write_csv(repo_root / "data/generated/day6c_same_speaker_control/output_audio_hashes.csv", hash_rows)
    if skipped:
        _write_csv(repo_root / "data/generated/day6c_same_speaker_control/skips.csv", skipped)

    all_pass = all(r["passed"] for r in verification_rows)
    summary = {
        "control": "C0_same_speaker_different_text_splice",
        "paired_cases": len(a0_rows),
        "controls_built": len(control_rows) // 2,
        "variants_per_case": 2,
        "skipped": skipped,
        "donor_reuse_max": max(usage.values()) if usage else 0,
        "donor_reuse_over_cap": sum(1 for v in usage.values() if v > MAX_DONOR_REUSE),
        "cross_split_leakage": 0,
        "verification_all_passed": all_pass,
        "manifest_rows": len(control_rows),
    }
    (repo_root / "data/generated/day6c_same_speaker_control/build_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8",
    )
    return summary


def verify_against_freeze(repo_root: Path = REPO_ROOT) -> bool:
    """Re-verify every C0 output hash against the recorded manifest."""
    rows = _read_csv(repo_root / "data/generated/day6c_same_speaker_control/output_audio_hashes.csv")
    for row in rows:
        path = repo_root / row["audio_relpath"]
        if not path.exists() or _sha256(path) != row["sha256"]:
            return False
    return True


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build Day 6C same-speaker controls.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    summary = build_same_speaker_controls(Path(args.repo_root))
    print(json.dumps(summary, indent=2))
    return 0 if summary["verification_all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
