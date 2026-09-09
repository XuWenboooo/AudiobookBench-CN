# WEEK 2 — DAY 12 MECHANISM ANALYSIS PRE-REGISTRATION

Frozen before any A2 metric or diagnostic exists. Nothing here may be
added, re-weighted, or reinterpreted after results are seen. The three
tiers are exhaustive: an analysis not listed here is not part of Day 12.

## 0. Core question (verbatim, frozen)

> **Does B1 localization weaken as synthetic speaker similarity to the
> target increases?**

Interpretation guard: any observed association is **correlational**. The
generator, the text and the speaker are entangled in a 23-case pilot; no
causal language is permitted in either direction (neither "similarity
causes detectability loss" nor "independence proves robustness").

## 1. Pre-registered analysis tiers

### PRIMARY (required for the Day-12 conclusion)

- **P1. Similarity–localization association.** Per-case
  `target↔synthetic ECAPA cosine` (Day-9 QA diagnostic, computed on the
  synthetic core region vs the real target utterance embedding) versus
  per-case B1b localization (case AUROC, case AUPRC on GT-full, S1 and
  S2). Reported as: per-case scatter (frozen figure), Spearman rank
  correlation with case-level bootstrap 95 % CI (2000 resamples, seed
  20260905), and a median split (high/low similarity halves) with per-group
  metrics. No linear-model fit, no p-value thresholding.
- **P2. B1 behavior on A2 vs Week-1 anchors.** A2 B1b window AUROC/AUPRC/F1
  (original AND conditional-on-speech-active) at S1/S2, compared
  descriptively against the frozen Week-1 A0/A1 and C0 anchors. This is a
  bounded-transfer statement, not a significance claim.

### SECONDARY (reported, not headline)

- **S1.** B2 adjacent/symmetric on A2 (does the change-point view behave
  differently for natural-duration same-text replacement?).
- **S2.** Zone statistics: core/boundary/outside mean B1b anomaly (does
  the signal enter the whole-utterance core, or stay at the crossfades?).
- **S3.** Duration-ratio descriptive analysis: `N_syn/N_real` distribution
  per split; its (correlational) association with B1 anomaly — diagnostic
  for the duration-shortcut risk, never a filter.
- **S4.** Speech-active retention on A2 (positive/negative, per tier-free
  population) with the frozen 0.5 mask.
- **S5.** Peak-error distribution on A2 (manipulated-timeline definition).

### DIAGNOSTIC ONLY (QA context; never performance claims)

- **D1.** ASR CER distribution (pre-frozen ASR backend or explicit
  omission); correlation with P1 is itself diagnostic — CER must not
  become a filter or a claimed mediator without a dedicated experiment.
- **D2.** Reference↔synthetic cosine (conditioning quality of the voice
  prompt, distinct from P1's target↔synthetic).
- **D3.** Generation failure classes and realized denominators.
- **D4.** Raw-output QA flags (audible artifacts, unusual prosody) as
  recorded at generation time.

## 2. The nine pre-frozen diagnostic variables

| # | Variable | Tier | Definition source |
|---|---|---|---|
| 1 | target real ↔ synthetic ECAPA cosine | PRIMARY (P1) | sidecar `target_synthetic_ecapa_cosine` |
| 2 | reference ↔ synthetic ECAPA cosine | DIAGNOSTIC (D2) | sidecar `reference_synthetic_ecapa_cosine` |
| 3 | ASR CER | DIAGNOSTIC (D1) | sidecar `asr_cer` (ASR defines nothing) |
| 4 | synthetic/real duration ratio | SECONDARY (S3) | sidecar `duration_ratio` |
| 5 | B1 full/core/boundary/outside scores | PRIMARY (P2) / SECONDARY (S2) | day6c evaluation code path |
| 6 | peak localization error | SECONDARY (S5) | manipulated-timeline definition |
| 7 | speech-active positive/negative retention | SECONDARY (S4) | frozen 0.5 mask |
| 8 | generation failure class | DIAGNOSTIC (D3) | A2_FAILURE_TAXONOMY |
| 9 | case split / speaker | DIAGNOSTIC (context) | lineage |

## 3. Pre-registered interpretation rules for the core question

- "B1 localization weakens" = lower case AUROC/AUPRC in the
  high-similarity half AND negative Spearman association with CIs
  excluding zero. Anything weaker is reported as "no clear association
  observed in this pilot".
- The similarity variable is the Day-9 QA cosine (frozen extractor), not
  any post-hoc alternative embedding.
- Outcomes are reported for ALL 23 planned cases' realized denominators,
  including failures (which cap the analyzable set).

## 4. Forbidden after seeing results

- Adding a new metric, embedding, similarity measure, or aggregation
  because it looks better.
- Changing the protocol, mask threshold, grids, or trim ratio.
- Filtering cases by similarity, CER, duration ratio, or B1 score.
- Promoting a DIAGNOSTIC variable into PRIMARY/SECONDARY.
- Causal wording in either direction.
- Reporting only the favorable scale/tier.
