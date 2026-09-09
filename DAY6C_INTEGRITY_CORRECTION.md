# Day 6C Integrity Correction Record

Date: 2026-09-05 (post-Day 6C correction pass; no new experiments, no data
changes, no threshold changes, no next-stage work).

## 1. Bootstrap contrast direction audit → LABEL BUG (fixed)

- Audit: the quantity has always been computed as `delta = C0_anomaly −
  cross_anomaly` (`delta_core_c0a_minus_a0` in `cross_vs_same_speaker.csv`),
  and the bootstrap means are the resampled means of that same delta.
- Finding: the numbers are correct and directionally consistent
  (negative = cross-speaker anomaly higher than same-speaker), but the
  contrast labels (`A0_vs_C0A`, `A1_vs_C0B`) read as the reverse
  difference. The Day 6C report §15 had additionally mislabeled the table
  rows as "A0 − C0A".
- Classification: **label/sign-presentation bug, not a calculation bug.**
- Fix: contrast identifiers renamed to `C0A_minus_A0` / `C0B_minus_A1`;
  `bootstrap_ci.csv` regenerated; report §15 corrected with an explicit
  note; report §23 claim re-expressed in the corrected direction.
- Raw anomaly data untouched (no value was changed to match expectations).
- Bootstrap and all related tests re-run after the fix.

## 2. Figure GT time-axis audit → FIGURE-ONLY UNIT BUG (fixed)

- Audit of every Day 6C figure: the GT bands were drawn with
  `fill_between(range(n_windows), …)` — a **window-index x axis** — while
  the trajectories plot seconds. On Figure A (≈122 windows over ≈31 s of
  trajectory) this displaced the bands far to the right (user-observed
  "52–58" position). Classification: **figure-only unit bug**.
- GT pipeline audit (`gt_axis_audit.json`): all 92 manipulated/C0 records
  × 2 scales = **184 target intervals** checked — start ≥ 0, end ≤ waveform
  duration, interval overlaps the speaker-grid time range, plotted target
  verbatim == manifest `target_start/end_sample / 16000`. **184/184 PASS,
  zero problems.** Metrics and GT projection were never affected (they
  derive from sample bounds, not plots).
- Fix: `bands()` now takes the same seconds time axis as the trajectories;
  all five figures re-rendered; Figure A visually verified against
  paircase_0001 (GT 13.75–14.50 s = samples 220056–232056 ✓).

## 3. Speech-active masking population audit (added)

New artifact `speech_mask_population_audit.csv` (36 rows), computed with
the frozen mask (0.5) and the frozen train-only thresholds — no threshold
was changed:

| Quantity | Result (S1/S2) |
|---|---|
| positive-window retention (full GT, test) | 1.000 (A0 S1/S2); 0.974 (A1 S1/S2) |
| GT-full positive retention (all splits) | 0.947–1.00 |
| GT-core positive retention (all splits) | 0.933–1.00 |
| negative-window retention | ≈ 0.67 (about one third of non-attack windows removed) |
| original prevalence → masked prevalence (S1 A0 test, full) | 0.052 → 0.075 |
| per-tier FP/min at fixed train threshold (S2, test) | 0.75 s: 2.46/1.97; 1.5 s: 0.0/0.0; 2.5 s: 2.07/2.07 |

Interpretation guard: the mask changes the *evaluation population*;
masked metrics are conditional-on-speech-active and are never to be read
as a detector improvement on its own.

## 4. Frozen-parameter config

`configs/day6c_confound_controls.yaml` records (without modification) the
executed parameters: mask threshold 0.5, bootstrap seed 20260905 /
2000 resamples / case unit with direction-explicit contrasts, C0 donor
rule, duration tiers, figure selection rules, inherited S1/S2 values.
Unit-tested (`test_day6c_confound_config_freezes_executed_values`).

## 5. Report updates

`DAY6C_CONFOUND_CONTROL_REPORT.md` updated: §7 more cautious
cross-speaker-contribution wording; §9 masked metrics re-expressed as
conditional-on-speech-active with the population audit; §15 contrast
labels corrected with an integrity note; §17 figure bug disclosure and
GT-axis audit; §23 safest claim rewritten (masked evaluation explicitly
conditional; specificity-to-speaker-change claim kept; pilot-scope and
precision limits kept). No Day 6A/6B numbers touched.

## 6. Verification after corrections

- Full pytest: **163 passed / 0 failed** (159 + 4 new integrity tests:
  bootstrap label direction, GT-axis audit, population-audit presence and
  retention bounds, frozen-config values).
- Day 6B / Day 6A / Day 5 / AISHELL-3 hashes: unchanged.
- Final Day 6C artifact hashes re-recorded below (post-correction).

## 7. Final Day 6C artifact hashes (post-correction)

Recorded in `results/day6c/day6c_final_hashes.json` (SHA256, uppercase),
covering: `bootstrap_ci.csv`, `cross_vs_same_speaker.csv`,
`case_level_metrics.csv`, `clean_transition_audit.csv`,
`speech_mask_population_audit.csv`, `gt_axis_audit.json`,
`original_vs_masked_metrics.csv`, `duration_stratified_metrics.csv`,
`duration_resolution_audit.csv`, `failure_cases.csv`, `config.yaml`,
`configs/day6c_confound_controls.yaml`, and the five figures.

## 8. Outcome

All three audits closed. Two presentation bugs fixed (bootstrap contrast
labels; figure GT-band axis), zero scientific-value changes; one new audit
artifact (population); one frozen config; report wording tightened.
**Day 6C Gate remains PASS with the corrections applied.**
