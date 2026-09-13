# WEEK5_EXP1_SOURCE_AUDIT

Status: READ_ONLY_AUDIT_COMPLETE
Protocol namespace: `WEEK5_EXP1_QUALIFICATION_ONLY`

## Scope and isolation

- `WEEK4_USED = NO`
- Week4 Validation, Held-out, H4 outputs, authorization, runner, config and governance artifacts were not opened by the Exp1 audit.
- All Exp1 outputs use the `week5` / `week5_exp1` namespace.

## Availability

| Source | Available | Evidence | Notes |
|---|---:|---|---|
| Week1 scientific outputs | YES | `WEEK1_REPORT.md`, `WEEK1_FREEZE.md`, `results/day6b/` | Frozen B1b/S2 score and embedding evidence |
| Week2 CosyVoice2 outputs | YES | `results/day10/` | 23 successful generation sidecars and waveforms; no reusable detector score timeline found |
| Week3 clean corrective F5 outputs | YES | `results/week3_stage_a_f5_runs/clean_rerun_20260907_01/` | 23 successful sidecars and score evidence in the separate evaluation-repro evidence timeline |
| B1b implementation | YES | `src/audiobookbench/temporal/day6b_scoring.py` | `robust_prototype`, `b1_scores`; frozen trim ratio 0.20 |
| S2 implementation | YES | `src/audiobookbench/temporal/day6b_embed.py` | `S2_1500ms_250ms`, 24,000-sample window, 4,000-sample hop |
| Sample-first GT | YES | `results/day6b/speaker_scores.csv`; Week2/3 sidecars | Existing overlap columns plus explicit attack/core/blend sample bounds |
| ECAPA score evidence | YES | `results/day6b/speaker_scores.csv`; F5 `window_timeline.jsonl` | Week1 S2 scores and Week3 F5 score timeline |
| ECAPA embedding evidence | YES | `results/day6b/embeddings/`, `embedding_manifest.csv`, `embedding_backend.json` | Frozen SpeechBrain ECAPA-TDNN evidence |
| AISHELL-3 identities | YES | Week1/Week2/Week3 manifests and sidecars | Source and reference identities are recorded; raw source remains read-only |

## Qualification limitation

The Week2 CosyVoice waveform population is available, but the read-only audit found no reusable CosyVoice B1b/S2 score artifact. Exp1 therefore does not invent or silently reconstruct a historical CosyVoice score claim. The executable qualification population is built from controlled splice and F5 score evidence; CosyVoice remains an explicitly recorded `SCORE_EVIDENCE_MISSING` mechanism unless a separately authorized score extraction is added.

## Required fields

```text
WEEK1_AVAILABLE = YES
WEEK2_AVAILABLE = YES (waveform/GT; score evidence missing)
WEEK3_AVAILABLE = YES
WEEK4_USED = NO
B1B_IMPLEMENTATION_FOUND = YES
S2_IMPLEMENTATION_FOUND = YES
SAMPLE_FIRST_GT_FOUND = YES
REUSABLE_SCORE_EVIDENCE = YES (Week1 controlled splice, Week3 F5)
REUSABLE_WAVEFORM_EVIDENCE = YES (Week1–3; Week2 CosyVoice included)
REUSABLE_EMBEDDING_EVIDENCE = YES (Week1 ECAPA cache)
```
