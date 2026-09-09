# Day 6B Pre-Check Report

Date: 2026-09-05
Nature: lightweight self-check (Day 5 / 6A were implemented in this same
workspace; this is explicitly **not** an independent audit).

## 1. Verdict

**DAY 6B PRECHECK = PASS.** No frozen-data drift detected; Day 6B work may
start once a real speaker-embedding backend is unlocked (any backend failure
leads to DAY 6B = BLOCKED, never to synthetic substitutes).

## 2. Checklist

| # | Item | Result |
|---|---|---|
| 1 | pytest full suite | **105 passed**, 0 failed (62 s) |
| 2 | Day 3 / 3.5 / 4 / 4.5 hashes | unchanged (70 output + 39 protected + 480 source re-verified) |
| 3 | Day 5 outputs | unchanged vs `results/day6a/day5_output_hashes.json` (13 files) |
| 4 | Day 6A frozen outputs | unchanged; 16 files hashed into `results/day6b/day6a_frozen_record.json` for end-of-day re-verification |
| 5 | random / fake speaker embedding | none exists — Day 5/6A record embedding as BLOCKED; no embedding code path was ever fabricated |
| 6 | test leakage | none observed: Day 6A reference is train-clean-only (unit-tested), thresholds train-only (unit-tested) |
| 7 | private agent paths in formal code | none: `src/**` contains no user/machine-specific absolute paths (dataset root lives in configs and is bypassed by the portable `audio_relpath` mechanism) |
| 8 | Day 6A negative result | untouched; will only receive claim-wording corrections, no numeric changes |

## 3. Backend plan (recorded before any localization result)

Primary: SpeechBrain ECAPA-TDNN (`speechbrain/spkrec-ecapa-voxceleb`,
pretrained on VoxCeleb, inference-only, 16 kHz input, 192-d embeddings) on
CPU-only PyTorch inside the managed isolated venv.
Fallback: Resemblyzer (256-d LSTM) if torch/speechbrain is not installable.
If neither installs reliably: **DAY 6B = BLOCKED** for the speaker track.
No random/synthetic/MFCC-substitute embedding is permitted under any
circumstance.
