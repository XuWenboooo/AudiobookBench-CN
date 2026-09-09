# WEEK 2 — A2 PRE-REGISTRATION REPORT

Date: 2026-09-05. Pure design/audit task: no dependency installed, no model
downloaded, no TTS generated, no A2 smoke or metric executed, no Day-8
artifact touched, no Week-1 frozen artifact modified.

## 1. Day9 readiness requirements (WEEK2_DAY9_PREREG.md)

Day 9 implements the formal generation pipeline, the additive sidecar
validator, the fail-closed waveform/GT verification suite, and at most 3
official smoke cases (first sorted paired_case_id per split). Smoke→official
transition requires: all `TO_BE_VERIFIED_BEFORE_IMPLEMENTATION` config
fields recorded; 3/3 smoke pass; validator committed with tests; fresh
Week-1 verify-only 696/696. Failure rows are always retained; quality
(outcome) filtering is forbidden; the only retry is the 1-shot
infrastructure retry with an identical seed.

## 2. Day10 freeze requirements (WEEK2_DAY10_FROZEN_PILOT_PREREG.md)

23 planned cases (11/6/6; 12 speakers 6/3/3), one generation each, ordered
by ascending paired_case_id with the frozen seed rule
(20260905 + index). At close: output/checkpoint/reference/pipeline hashes
frozen; fresh Week-1 verify-only 696/696; no score-based filtering; no
substitution; realized denominators (planned/succeeded/failed-by-class)
mandatory in every later report.

## 3. Day11 evaluation invariants (WEEK2_DAY11_EVAL_DRY_AUDIT.md)

Reusable unchanged: B1a/B1b/B2 (sequence-local, duration-agnostic), B0
(grid reprojected on the manipulated timeline), B4 as DIAGNOSTIC on
recomputed frames. **B3 is forbidden for primary A2 evaluation** (dual
timeline + suffix shift break the same-grid premise; clean-embedding
interpolation is banned). Eight new tests required before any A2 metric:
dual-timeline GT, variable-length windows, unequal-count case grouping,
mask alignment, B3 denial, figure time-axis convention (manipulated
timeline; clean trajectory cut at attack start), detector input denylist,
threshold-reuse freeze. Interpretation caveat: Week-1-frozen thresholds are
reused, so AUPRC is the primary threshold-free comparison.

## 4. Day12 pre-registered analyses (WEEK2_DAY12_MECHANISM_PREREG.md)

Core question frozen: *does B1 localization weaken as synthetic speaker
similarity to the target increases?* Nine diagnostic variables; three
exhaustive tiers: PRIMARY (P1 similarity↔localization association with
case-level bootstrap CIs; P2 A2-vs-Week-1-anchor descriptive comparison),
SECONDARY (B2 on A2; zone statistics; duration-ratio diagnostics; mask
retention; peak error), DIAGNOSTIC (CER, reference↔synthetic cosine,
failure classes, context). Correlation ≠ causality is binding; post-hoc
metric addition, protocol change, and any similarity/score-based case
filtering are forbidden.

## 5. Day13 decision tree (WEEK2_DAY13_DECISION_TREE.md)

Four frozen branches — A: B1 strong on A2; B: B1 near chance; C:
performance tracks speaker similarity continuously; D: boundary-artifact
dominated — each with supported/forbidden interpretations and priority
shifts (second generator, channel, short-attack, native long-form, paper
framing). Mixed outcomes report the intersection of allowed
interpretations. Negative results are framed as boundary-mapping findings
with full provenance.

## 6. Failure taxonomy (A2_FAILURE_TAXONOMY.md)

17 machine-readable classes (BACKEND_LOAD_FAIL … SUFFIX_MISMATCH), each
with trigger/severity/retention/retry/amendment/blocks. Detector-score-
based failures are explicitly prohibited. Denominator rule: every report
states planned 23 (11/6/6) vs realized, per class; > 3 failed cases forces
per-class disclosure before performance numbers.

## 7. Claim gates (WEEK2_PUBLICATION_CLAIM_GATE.md)

E-class ladder (E1 generation → E2 original evaluation → E3 conditional →
E4 mechanism → E5 scenario → E6 second generator, absent in 2A). First-use
permissions: "TTS replacement"/"synthetic speech"/"voice-conditioned
replacement" at E1; "same-text TTS localization signal" only at E2+E5∈{A}
or {C graded}; "deepfake detection", "robust", "generalize",
"deployment-ready", "native audiobook", "speaker causality",
"statistically significant" remain forbidden in Week 2A regardless of
outcome. A pre-written maximal claim template (Scenario A, all qualifiers)
is included.

## 8. Leakage risks (WEEK2_A2_LEAKAGE_SHORTCUT_AUDIT.md)

14 audited vectors: reference audio/embedding, speaker ID, paired-clean
(B3), test-threshold tuning, generator metadata, failure-code skew,
duration-delta shortcut, crossfade, trim edges, silence, constructed-
boundary interaction, sample-rate/codec, file-naming. Each has a current
mitigation (mostly frozen config/contract), a required pre-result test,
and an explicit remaining gap. New required null control: B1 on the
pre-attack clean-prefix windows of A2 manipulated sequences must match
clean behavior (no timeline-shift artifact).

## 9. Protocol amendment triggers

An amendment record (before the affected run) is REQUIRED for: any config
`TO_BE_VERIFIED_BEFORE_IMPLEMENTATION` resolution affecting semantics;
reference-rule changes; crossfade/DSP changes; threshold source changes;
mask changes; tier/interval changes; any new analysis tier. Everything
else is fixed.

## 10. Contradiction scan

Read against WEEK1_FREEZE/REPORT/RETROSPECTIVE, the research-assurance
suite, and the corrected A2 config: **no protocol contradiction found.**
The v1.1 correction already resolved the interval/transcript conflict
(whole-utterance unit; Week-1 bounds forbidden); the config's 23-case plan
matches the lineage (23 unique target sources, 23 transcripts, references
available for all 12 speakers); the detector denylist matches Week-1
leakage tests; the speech-mask and bootstrap parameters match the Day-6C
frozen values (0.5 / 20260905 / 2000 / case unit).

## 11. Final gate

**PREREGISTRATION GATE = PASS.**

Meaning: the boundaries of all subsequent A2 work (generation, freezing,
evaluation, mechanism analysis, decision rules, claim gates, leakage
controls) are now pre-defined and testable. Meaning NOT: Day 8 is ready,
A2 is implemented, A2 will succeed, or a paper is ready.

## 12. Hold conditions (would flip the gate to HOLD)

Any of: a protocol amendment introduced after seeing A2 outputs; a missing
failure-taxonomy class discovered during generation without pre-registration;
evaluation code touching the detector denylist; threshold or population
changes without an amendment.
