# Numeric Traceability Audit — Week 1

Chain convention: CLAIM → REPORT → TABLE (metrics_summary.csv) → CSV/JSON
(frozen artifact) → CONFIG → CODE → HASH/FREEZE.

Method: programmatic comparison of stored artifact values against report
values (tolerance 5e-4 = half-ulp of 3-dp reporting); Week-1
`metrics_summary.csv` additionally cross-checked against upstream artifacts
at 5e-7 tolerance. Raw comparison data: `research_assurance/_audit_data.json`.

## 1. Trace table (28 entries)

| Claim | Frozen artifact | Stored value | Report value | Status |
|---|---|---:|---:|---|
| Day6A 250ms A0 AUROC | results/day6a/metrics.json | 0.331217 | 0.331 | ROUNDING ✓ |
| Day6A 250ms A1 AUROC | results/day6a/metrics.json | 0.349672 | 0.350 | ROUNDING ✓ |
| Day6A 100ms A0/A1 AUROC | results/day6a/metrics.json | 0.379082/0.377993 | 0.379/0.378 | ROUNDING ✓ |
| Day6A 500ms A0/A1 AUROC | results/day6a/metrics.json | 0.324153/0.345763 | 0.324/0.346 | ROUNDING ✓ |
| Day6B S2 B1b A0 AUROC | results/day6b/metrics.json | 0.901421 | 0.901 | ROUNDING ✓ |
| Day6B S2 B1b A1 AUROC | results/day6b/metrics.json | 0.896658 | 0.897 | ROUNDING ✓ |
| Day6B S2 B1b A0 AUPRC | results/day6b/metrics.json | 0.453843 | 0.454 | ROUNDING ✓ |
| Day6B S2 B1b A1 AUPRC | results/day6b/metrics.json | 0.491193 | 0.491 | ROUNDING ✓ |
| Day6B S1 B1b A0/A1 AUROC | results/day6b/metrics.json | 0.830741/0.830439 | 0.831/0.830 | ROUNDING ✓ |
| B3 ORACLE S1 A0 AUROC | results/day6b/metrics.json | 0.995734 | ≈0.996 | ROUNDING ✓ |
| B4 S1 A0 AUROC | results/day6b/metrics.json | 0.370932 | 0.371 | ROUNDING ✓ |
| C0A S1 test AUROC | original_vs_masked_metrics.csv | 0.376199 | 0.376 | ROUNDING ✓ |
| C0B S1 test AUROC | original_vs_masked_metrics.csv | 0.366609 | 0.367 | ROUNDING ✓ |
| C0A S2 test AUROC | original_vs_masked_metrics.csv | 0.323319 | 0.323 | ROUNDING ✓ |
| C0B S2 test AUROC | original_vs_masked_metrics.csv | 0.306531 | 0.307 | ROUNDING ✓ |
| cross core anomaly A0 (S1 mean) | cross_vs_same_speaker.csv | 0.729014 | 0.729 | ROUNDING ✓ |
| cross core anomaly A1 | cross_vs_same_speaker.csv | 0.731642 | 0.732 | ROUNDING ✓ |
| same core anomaly C0A/C0B | cross_vs_same_speaker.csv | 0.365902/0.365906 | 0.366/0.366 | ROUNDING ✓ |
| masked S2 A0 AUROC (conditional) | original_vs_masked_metrics.csv | 0.972403 | 0.972 | ROUNDING ✓ |
| masked S2 A0 AUPRC (conditional) | original_vs_masked_metrics.csv | 0.743715 | 0.744 | ROUNDING ✓ |
| case AUROC median (S2 A0 test) | case_level_metrics.csv | 0.897727 | 0.898 | ROUNDING ✓ |
| peak error median (S2 A0 test) | case_level_metrics.csv | 5.4375 | 5.44 | ROUNDING ✓ (2-dp) |
| bootstrap C0A−A0 mean | bootstrap_ci.csv | −0.363112 | −0.363 | ROUNDING ✓ |
| speech-mask positive retention min/max | speech_mask_population_audit.csv | 0.933333/1.0 | 0.933/1.00 | ROUNDING ✓ |
| **C4 median boundary distance** | clean_transition_audit.csv | **0.093375** | **0.094** | **LOW INCONSISTENCY** |
| C4 within-1s | clean_transition_audit.csv | 0.972222 | 0.972 (97.2%) | ROUNDING ✓ |
| metrics_summary cross-check (Day6A/6B rows) | results/week1/metrics_summary.csv | identical at 5e-7 | — | EXACT ✓ |

## 2. Rounding policy application

- `0.901421 → 0.901`: ROUNDING.
- `5.4375 → 5.44`: ROUNDING (2-dp convention, half-up).
- `0.093375 → 0.094`: **LOW INCONSISTENCY.** Standard 3-dp rounding yields
  0.093; the reports (WEEK1_REPORT §10, WEEK1_FREEZE, retrospective) print
  0.094. Deviation 0.0006 s — no scientific consequence, no downstream
  dependency — recorded here, **not auto-corrected** per the audit contract.
  Recommended wording for the paper: "≈0.09 s" or "0.093 s".

## 3. Config → code → freeze anchors

- Day6A config: `configs/day6a_localization_baseline.yaml` (frozen copy in
  results/day6a/config.yaml; equality unit-tested).
- Day6B config: `configs/day6b_speaker_consistency.yaml` (hash-frozen in
  `results/day6c/day6b_freeze_record.json`; verified by
  `test_day6b_freeze_hashes_verify`).
- Day6C config: `configs/day6c_confound_controls.yaml` (executed-values
  record; unit-tested) + inherited `day6b` values.
- Week1 entry: `experiments/week1_baseline/run.py` + `configs/week1.yaml`;
  `results/week1/hashes.json` = 696-entry frozen chain (verify-only PASS:
  0 missing / 0 mismatch, re-executed during this audit).

## 4. Verdict

**Numeric traceability: PASS.** 28/28 entries trace; 26 exact/standard
rounding, 1 acceptable 2-dp rounding, 1 LOW cosmetic rounding deviation
(0.094 vs 0.093 s) recorded and not corrected. Zero true inconsistencies.
