# Day 11 frozen A2 detector evaluation

Date: 2026-09-06  
Status: **PASS** (frozen evaluation and live Week2A gate cleared)

## Frozen inputs and configuration

The Day10 freeze was verified before scoring: 23/23 Day10 WAV hashes matched
`results/day10/day10_output_hashes.json`, and the sidecar case set was unchanged.
The evaluation retained train/val/test = 11/6/6 and all 23 cases. The A2
manipulated/output timeline and sample-first attack/core/blend bounds were used;
no rounded-seconds GT or Week1 short-duration boundaries were substituted.

Primary methods were the frozen Week1 B0, B1a, B1b, and B2 definitions. B0
recomputed the frozen 25-ms/10-ms feature grid on A2 waveforms with a
train-clean-only robust reference. B1a/B1b/B2 used the frozen offline ECAPA
backend and S1/S2 grids on suspect waveforms only. No enrollment, reference
audio/embedding, clean-original, text, generator metadata, or GT was passed to
detector scoring. B3 was excluded from primary results; B4 was not run.

All thresholds came from the frozen Week1 train-F1 rows recorded in
`results/day11/threshold_provenance.csv`; `a2_tuning=False` for every method.
No A2 threshold, score polarity, grid, model, or aggregation was tuned.

## Primary test results (GT full)

| Method / scale | AUROC | AUPRC | F1 |
| --- | ---: | ---: | ---: |
| B0 / 100 ms | 0.3807 | 0.0656 | 0.1634 |
| B0 / 250 ms | 0.3818 | 0.0655 | 0.1611 |
| B0 / 500 ms | 0.3653 | 0.0668 | 0.1554 |
| B1a / S1 | 0.4543 | 0.0781 | 0.0127 |
| B1b / S1 | 0.4675 | 0.0798 | 0.0208 |
| B2 adjacent / S1 | 0.4017 | 0.0724 | 0.1551 |
| B2 symmetric / S1 | 0.3541 | 0.0680 | 0.1375 |
| B1a / S2 | 0.5276 | 0.0934 | 0.0233 |
| B1b / S2 | 0.5215 | 0.0921 | 0.0000 |
| B2 adjacent / S2 | 0.4138 | 0.0747 | 0.1717 |
| B2 symmetric / S2 | 0.3834 | 0.0719 | 0.1581 |

The complete train/val/test, full/core, raw-window timeline, and case-level
tables are in `results/day11/metrics_by_split.csv`,
`results/day11/score_timeline.csv`, `results/day11/gt_timeline.csv`, and
`results/day11/case_level_metrics.csv`.

Uncertainty is case-level only: `results/day11/case_bootstrap_ci.csv` uses
2000 resamples, seed 20260905, and unit `paired_case_id` (11 train cases and
6 val/test cases). Windows were never treated as independent bootstrap units.

## Integrity, tests, and limitations

- Day10 freeze verification: PASS; 23 cases retained, no replacement.
- Detector leakage: PASS; B0/B1a/B1b/B2 received suspect waveform-derived
  inputs only.
- Timeline/GT integrity: PASS; variable-length output timelines, full/core/
  blend zones, and sample-first bounds were preserved.
- Relevant tests: **68 passed, 1 warning** (`test_day11_a2_evaluation.py`,
  `test_day6b_speaker.py`, `test_day8_a2_readiness.py`).
- Day11 output hashes are frozen in `results/day11/day11_output_hashes.json`.
- Limitations remain: 23 total cases, 6 test cases, constructed long-form,
  one TTS generator, standardized 16-kHz audio, AISHELL-3 training
  independence UNKNOWN, and GPU 8-GB OOM (irrelevant because CPU was used).

Live-gate reconciliation registered the existing Day8–Day10 evidence, added the
missing Day8 precheck record, and corrected only the Day9 verifier's empty-list
error representation (`errors: []`). The executed Day11 test evidence now
closes T01–T18/T20/T21; T19 remains deferred to Day12 as specified. Findings
F1/F4/F5 are resolved by the tested reporting clip, frozen-threshold provenance,
and explicit B3 exclusion. No Day11 scientific result file was changed and no
metric was recomputed.

The metrics are evaluation evidence for this frozen A2 construction, generator,
dataset, and detector family only. They do not establish universal detection,
deepfake detection, causality, robustness, or deployment readiness. Day12's
ECAPA–B1b association analysis was not run.

**DAY11 = PASS.** Day12 has not been entered; no method retuning or claims
beyond the preregistration were added.
