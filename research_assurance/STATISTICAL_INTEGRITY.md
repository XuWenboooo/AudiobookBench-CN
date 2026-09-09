# Statistical Integrity Audit — Week 1

Scope: how uncertainty, dependence, prevalence and wording are handled
across the frozen Week-1 artifacts. No new statistical test was designed or
added to the scientific conclusions; recommendations are marked FUTURE WORK.

## 1. Bootstrap unit

- Case-level (paired_case_id) resampling, 2000 resamples, seed 20260905;
  documented in configs and CSVs; window-level bootstrap never used.
- Verified: `bootstrap_ci.csv` records unit/resamples/seed;
  `test_bootstrap_unit_is_case_not_window` and determinism tests exist.
- **PASS.**

## 2. Overlapping-window dependence

- S1: 1.0 s window / 0.25 s hop ⇒ up to 75 % audio shared between adjacent
  windows; S2: 50 % shared. Window counts (17,342 + 35,826 from Day 6A) are
  therefore NOT independent samples, and no report treats them as such for
  uncertainty: all CIs are case-level. Pooled-window AUROC is reported as a
  descriptive ranking metric only.
- Residual exposure: point estimates (AUROC/AUPRC/F1) are still computed on
  correlated windows; this is standard for detection-style evaluation but
  should be stated in the paper's evaluation section. **PASS with wording
  requirement.**

## 3. Sample size

- 23 paired cases; 6 val / 6 test. CIs are wide (e.g. S1 B1a test AUROC CI
  [0.723, 0.917]) and are reported wherever a key claim is made. Claims are
  bounded accordingly. **PASS.**

## 4. CI interpretation

- Percentile CIs from case resampling; a CI is an uncertainty statement
  about the case-sampling distribution, not a hypothesis test. Reports use
  CI language only; no p-values anywhere in Week 1. **PASS.**

## 5. Significance wording

- Sweep across WEEK1_REPORT, WEEK1_FREEZE, DAY6A/6B/6C reports,
  claims.md, limitations.md, retrospective: the corrected phrasing
  "every observed AUROC is below 0.5 / no significance test was performed"
  is in place; no "significant(ly)" used as a statistical claim anywhere.
  The single use of "significantly" in the corpus is in a non-statistical
  sense ("decisively the easiest") in DAY6C §10 prose — flagged as a paper
  wording caution: avoid the word entirely. **PASS with wording caution.**

## 6. Multiple metrics / multiple comparisons

- Many slices (scale × ablation × GT × variant × split) are reported
  without multiplicity adjustment. Because Week 1 makes no per-slice
  significance claims, no correction is required; any future hypothesis
  testing (e.g. A0 vs A1) must pre-register the comparison set.
  **FUTURE WORK.**

## 7. Undefined metrics and NaN handling

- NaN is used for undefined slices (single-class AUROC, empty core
  coverage at S2/0.75s, all-NaN feature windows). NaN is never rendered as
  0 and never imputed in bootstrap (recorded as NaN, e.g. the S2 C0B−A1
  contrast). **PASS.**

## 8. Prevalence shift and conditional evaluation

- Masked evaluation conditions on a smaller population (original
  prevalence 0.052 → masked 0.074 at S1/A0/test); AUPRC is
  prevalence-sensitive, so masked-vs-original AUPRC differences are partly
  population effects. The reports enforce the
  "conditional-on-speech-active" framing and pair masked with unmasked.
  Population audit quantifies retention by class and tier. **PASS.**

## 9. Observed-difference vs significant-difference sweep

- Grep across all Week-1 documents for "significant": only negations
  ("no significance test") and one non-statistical prose use (noted above).
  Day 6C duration-tier comparisons explicitly avoid significance claims
  ("no statistical-significance claim is made"). **PASS.**

## 10. Recommendations (FUTURE WORK — not added to conclusions)

1. Pre-registered paired tests (e.g. paired bootstrap over case-level
   AUROC differences A1 vs A0) if variant contrasts are ever claimed.
2. Matched-population reporting companion for conditional evaluation
   (report metrics on the same retained window set for original scores).
3. Interval-level localization metrics (IoU-based) to complement
   window AUROC/AUPRC.
4. Multiplicity policy if the paper reports a large metric grid.
