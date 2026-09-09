# Paper Traceability Matrix — Week 1

Each future-paper claim mapped to its complete evidence chain.

## Claim 1 — The real-audio pipeline is reproducible

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §12; WEEK1_FREEZE "Hash and reproduction status" |
| Metrics | results/week1/reproduction_manifest.json; run.log |
| Config | configs/week1.yaml |
| Code | experiments/week1_baseline/run.py (--verify-only / --reproduce-core) |
| Figure | — (process claim) |
| Freeze/hash | results/week1/hashes.json (696 entries; 0 missing/0 mismatch re-verified in this audit) |

## Claim 2 — B0 (global scalar anomaly) fails on this pilot

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §7; DAY6A_NONTRAINED_LOCALIZATION_REPORT §6–§7, §20 |
| Metrics | results/day6a/metrics.json; results/week1/metrics_summary.csv (Day6A rows) |
| Config | configs/day6a_localization_baseline.yaml |
| Code | src/audiobookbench/temporal/aggregation.py, day6a_scoring.py, day6a_pipeline.py |
| Figure | results/week1/figures/01_day6a_negative_example.png |
| Freeze/hash | day5_output_hashes.json; day6a hashes in week1 chain |

Boundary wording: "the tested generic global scalar robust-z anomaly";
every observed AUROC < 0.5; no significance claim.

## Claim 3 — B1 provides a strong cross-speaker temporal signal

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §8; DAY6B report §7; DAY6B_CLAIM_ADDENDUM §1 |
| Metrics | results/day6b/metrics.json (S2 B1b rows); metrics_summary.csv |
| Config | configs/day6b_speaker_consistency.yaml (frozen grids/trim/threshold) |
| Code | day6b_embed.py, day6b_scoring.py, day6b_pipeline.py |
| Figure | results/week1/figures/02_day6b_speaker_signal_example.png |
| Freeze/hash | day6b_freeze_record.json; week1 chain (Day6B 15) |

Boundary: strong ranking; AUPRC/F1 quoted; NOT high-precision deployable.

## Claim 4 — C0 same-speaker control (specificity)

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §9; DAY6C report §6–§7 |
| Metrics | cross_vs_same_speaker.csv; original_vs_masked_metrics.csv (C0 rows); case_level_metrics.csv |
| Config | configs/day6c_confound_controls.yaml (donor rule) |
| Code | security/day6c_same_speaker.py |
| Figure | results/week1/figures/03_day6c_cross_vs_same_control.png |
| Freeze/hash | C0 audio hashes (46) in week1 chain; c0_output_hashes.csv |

Boundary: text not controlled; specificity claim pilot-scoped.

## Claim 5 — Utterance-transition mechanism for outside FPs

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §10; DAY6C report §14 |
| Metrics | clean_transition_audit.csv (144 rows) |
| Config | figure/top-3 rule in configs/day6c_confound_controls.yaml |
| Code | day6c_pipeline.py (C4 section) |
| Figure | results/week1/figures/04 (masked comparison), 05 (limitation) |
| Freeze/hash | clean_transition_audit.csv in day6c_final_hashes.json |

Boundary: "a large fraction", not "all"; error-analysis-only.

## Claim 6 — Conditional-on-speech-active result

| Layer | Artifact |
|---|---|
| Report | WEEK1_REPORT §9; DAY6C report §8–§9 |
| Metrics | original_vs_masked_metrics.csv (masked rows); speech_mask_population_audit.csv (corrected) |
| Config | mask threshold 0.5 in day6c_confound_controls.yaml |
| Code | day6c_pipeline.py (speech_active_fractions + population audit) |
| Figure | results/week1/figures/04_original_vs_speech_active.png |
| Freeze/hash | corrected CSV hash 9886F17E… in week1 chain |

Boundary: conditional population; must pair with unmasked; not a detector
improvement on its own.

## Cross-cutting integrity artifacts

- Day 6B freeze: results/day6c/day6b_freeze_record.json + DAY6B_FREEZE.md
- Day 6C corrections: DAY6C_INTEGRITY_CORRECTION.md (all three historical
  corrections RESOLVED; current artifacts verified)
- Independent audit: CODEX_INDEPENDENT_AUDIT_DAY5_DAY6C.md
- Continuity review: AGENT_WEEK1_CONTINUITY_REVIEW.md
- Week-1 chain: results/week1/hashes.json (696)
