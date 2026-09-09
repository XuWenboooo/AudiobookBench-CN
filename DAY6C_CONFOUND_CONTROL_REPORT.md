# Day 6C Confound-Control Report

Date: 2026-09-05
Config: reuses the frozen `configs/day6b_speaker_consistency.yaml`; the two
new pre-declared constants of today (speech-mask threshold 0.5, seed
20260905) were frozen before any Day 6C result was observed.
Scope: confound isolation for the Day 6B speaker-consistency signal. No
supervised model, no hyperparameter sweep, no test tuning, no A0/A1
regeneration, no A2 TTS, no Day 7 work. Every frozen artifact was verified
unchanged before and after.

## 1. Executive Summary

Day 6C answers five pre-registered questions about the Day 6B signal using
four controls: C0 (same-speaker different-text splice, 23 cases × C0A/C0B =
46 new verified WAVs), C1 (label-agnostic speech-active masking), C2
(duration stratification), C3 (case-level evaluation with global top-1 peak
error) and C4 (clean transition audit).

**Headline (pre-registered interpretation CASE A):**

1. The B1 signal is **primarily driven by speaker change**: cross-speaker
   core anomaly (A0 0.729 / A1 0.732) exceeds same-speaker C0 core anomaly
   (0.366 / 0.366) in **23/23 cases**, with case-level bootstrap CIs far
   from zero (A0−C0A −0.363 [−0.413, −0.308]).
2. Same-speaker replacement produces **no usable residual localization**
   (C0 window AUROC 0.31–0.38, below 0.5).
3. The label-agnostic speech-active mask (threshold 0.5, 69 % windows
   retained) **removes most outside false positives**: masked test metrics
   (S2, A0) AUROC 0.972 / AUPRC 0.744 / F1 0.657 (from 0.901 / 0.454 /
   0.506); S1 AUPRC rises 0.170 → 0.773.
4. Clean-sequence top peaks lie **at utterance transitions** (144/144 top-3
   peaks within 2 s of the nearest utterance boundary; median 0.09 s) —
   the outside-FP mechanism is now identified.
5. Duration stratification: 2.5 s attacks are by far the easiest
   (S2 AUROC 0.965, AUPRC 0.74, F1 0.79); 0.75 s attacks are hard in
   *precision* (AUPRC 0.12); 1.5 s has the lowest AUROC (0.78–0.80).

**DAY 6C GATE = PASS** (all 17 requirements, §23).

## 2. Day6B Freeze

`DAY6B_FREEZE.md` + `results/day6c/day6b_freeze_record.json`: SHA256 of all
Day 6B outputs, configs, reports and the four ECAPA checkpoints, frozen at
2026-09-05T12:04:22 with pytest 130. Re-verified unchanged after all Day 6C
work (`test_day6b_freeze_hashes_verify`, `run_summary.day6b_freeze_unchanged
= true`). Day 6A outputs and all earlier hashes likewise unchanged. The
AISHELL-3 raw corpus re-verified unchanged (480 source hashes).

## 3. Research Questions

Q1–Q5 as stated in the protocol; each answered in §6/§8/§10/§12/§13 and
summarized in §20. Additional question Q6 (S1/S2 resolution trade-off) in
§11.

## 4. Same-Speaker C0 Protocol

For every frozen paired case the original target was reused verbatim (same
clean sequence, same target utterance, same `target_start/end_sample`, same
duration tier, same split); only the donor changed:

- donor speaker == target speaker; donor split == target split;
- donor utterance != target utterance (hence text differs in all cases;
  `same_text = false` for 46/46 rows);
- deterministic selection: lowest usage count, then lexicographic
  `sample_id`, skipping the target utterance, requiring a 16 kHz-decoded
  length ≥ target length (raw-WAV frames converted to 16 kHz estimates);
- **C0A** `same_speaker_direct_splice`: A0-style direct replacement;
- **C0B** `same_speaker_artifact_controlled_splice`: A1-style RMS matching
  (gain = target_rms/donor_rms clamped [0.25, 4]) + the same 400-sample
  crossfade; identical boundary semantics.

No target interval was modified to gain samples; zero cases were skipped.
Donor reuse max = 1 (cap respected); cross-split leakage = 0.

## 5. C0 Integrity

Fail-closed verification (`c0_waveform_verification.csv`, all 23 PASS):
duration == clean duration; 16 kHz mono; finite; samples outside the target
interval exactly unchanged; inside changed; target interval identical to the
original paired case; donor speaker/split/utterance checks; clean WAV and
AISHELL-3 untouched. Output hashes recorded
(`c0_output_hashes.csv`) and re-verified after the reproducibility rerun.
C0 embeddings: 5,742 (S1) + 5,650 (S2) windows with the frozen ECAPA.

## 6. Cross-Speaker vs Same-Speaker Results

Per-case core anomaly (B1b, mean over cases; test+val+train pooled per
case, S1):

| | core anomaly | boundary | outside | case AUROC (test) |
|---|---:|---:|---:|---:|
| A0 (cross) | 0.729 | — | — | 0.856 |
| C0A (same) | 0.366 | — | — | — |
| A1 (cross) | 0.732 | — | — | 0.850 |
| C0B (same) | 0.366 | — | — | — |

C0 localization metrics (window-level, test, full GT, B1b): AUROC 0.377
(S1) / 0.323 (S2) — **below 0.5**, i.e. no residual usable signal.

## 7. Speaker-Change Contribution (pre-registered interpretation)

**CASE A applies.** The cross-vs-same difference is +0.36 core anomaly with
23/23 case-level agreement and bootstrap CIs excluding zero. Within this
pilot, speaker change accounts for the largest identified share of the B1
core anomaly, and a same-speaker utterance replacement does not trigger B1
(0/23 cases above the cross-speaker level). More cautiously: this
establishes the signal's *specificity to speaker change* on this
constructed pilot; it does not measure how much non-speaker factors
(text difficulty, phonetic distance between the specific utterance pairs,
local channel variation) would contribute in other pairings, because C0
controls the speaker factor only and each C0 uses one particular donor
utterance per case.

## 8. Speech-Active Masking (C1)

Pre-frozen rule: a speaker window enters the masked evaluation iff its
speech-active fraction (1 − pause fraction over covered 25 ms/10 ms Day-5
rule frames; for C0 controls the identical −45 dBFS rule on their own
waveform) ≥ **0.5**. The mask never reads attack GT, intervals or variant
labels (unit-tested). Retained windows: S1 69.9 %, S2 68.7 %.

## 9. Original vs Masked Localization

Test, full GT, B1b:

| Variant | Scale | ORIGINAL auc/ap/f1 | MASKED auc/ap/f1 |
|---|---|---|---|
| A0 | S1 | 0.831 / 0.170 / 0.242 | **0.955 / 0.773 / 0.694** |
| A1 | S1 | 0.830 / 0.170 / 0.249 | **0.959 / 0.787 / 0.722** |
| A0 | S2 | 0.901 / 0.454 / 0.506 | **0.972 / 0.744 / 0.657** |
| A1 | S2 | 0.897 / 0.491 / 0.519 | **0.969 / 0.727 / 0.667** |
| C0A | S1 | 0.376 / 0.039 / 0.099 | 0.521 / 0.074 / 0.109 |
| C0B | S1 | 0.367 / 0.038 / 0.097 | 0.519 / 0.073 / 0.134 |
| C0A | S2 | 0.323 / 0.036 / 0.101 | 0.443 / 0.067 / 0.143 |

Answers, stated carefully: the masked numbers are
**conditional-on-speech-active evaluation** — they describe the same B1
scores restricted to windows retained by the label-agnostic mask, on a
different (smaller, more positive-weighted) window population; they are not
the score of a different detector and the AUPRC increase must not be read
in isolation as "the detector improved". What the comparison does show:
(a) negative-window retention ~0.67 versus positive-window retention
0.974–1.00 on test full-GT (0.933–1.00 across all split/GT slices;
population audit, `speech_mask_population_audit.csv`), i.e. the
mask removes mostly non-attack windows; (b) masked C0 controls remain at
chance (no artificial separability introduced); (c) per-tier fixed-threshold
FP/min (test): 2.0–2.5 at 0.75 s and 2.5 s tiers, 0.0 at the 1.5 s tier.
**Both original and masked are reported side by side everywhere**; the
original numbers remain the unmasked deployable reference.

## 10. Attack-Duration Stratification (C2)

Test, B1b, S2 (full GT; case counts 8/8/7 as frozen):

| Tier | Variant | AUROC | AUPRC | F1 |
|---|---|---:|---:|---:|
| 0.75 s | A0 / A1 | 0.877 / 0.891 | 0.124 / 0.125 | 0.11 / 0.13 |
| 1.5 s | A0 / A1 | 0.801 / 0.777 | 0.121 / 0.105 | 0.00 / 0.00 |
| 2.5 s | A0 / A1 | 0.964 / 0.965 | 0.660 / 0.739 | 0.79 / 0.79 |

2.5 s attacks are decisively the easiest. 0.75 s is hard in precision (few
positive windows, extreme class imbalance), while 1.5 s shows the lowest
AUROC — no statistical-significance claim is made (no test performed).

## 11. Temporal Resolution Analysis

S2 (1.5 s window): window/attack duration ratio = 2.0 at 0.75 s — and the
median number of windows with core-overlap ≥ 0.5 is **0** for 0.75 s cases
(the 0.5 s strict core cannot dominate a 1.5 s window). S1 (1.0 s): ratio
1.33, core-positive windows median 3. Trade-off: longer windows stabilize
the speaker embedding (higher AUROC) but cannot resolve sub-window cores —
the S2 core-GT numbers for 0.75 s are structurally unmeasurable under the
majority rule. This is a grid limitation, not a detector property.

## 12. Case-Level Evaluation (C3)

Per-case window AUROC/AUPRC (test, S2, B1b): median case AUROC 0.898 (A0) /
0.907 (A1); median case AUPRC 0.162 / 0.150. The case-level story is
consistent with window-level AUROC (every case separates above 0.5), while
case-level precision remains modest — consistent with the §9 mask findings.

## 13. Peak Localization Error

Global top-1 peak (unmasked B1b, S2, test): median error **5.44 s**
(IQR 1.16–9.56). With unmasked outside false positives dominating the argmax
(§14), the global peak frequently lands far from the core — this metric must
be read together with the masked metrics (§9), which remove most of those
peaks' causes. Top-k was not used (default per protocol).

## 14. Clean Transition Audit (C4)

Top-3 B1b peaks per clean sequence (24 sequences, 144 peaks, deterministic
descending-anomaly/tie-by-time rule), distance to the nearest utterance
boundary from the frozen Day 4.5 lineage (already in seconds):

- mean **0.15 s**, median **0.09 s**, IQR 0.04–0.13 s;
- 140/144 peaks within 1 s, **144/144 within 2 s**.

**The clean-sequence false-positive mechanism is now identified: high B1
anomaly on clean sequences occurs almost exactly at constructed utterance
boundaries** (natural prosodic/lexical transitions between different
utterances of the same speaker), not inside steady speech. This is
error analysis only; no test anomaly was deleted on this basis, and only
the label-agnostic C1 mask is allowed to change evaluation eligibility.

## 15. Bootstrap Uncertainty

Case-level (paired_case_id) resampling, 2 000 resamples, seed 20260905:

| Contrast (core anomaly, B1b) | n | mean Δ | 95 % CI |
|---|---:|---:|---|
| C0A − A0 (S1) | 23 | −0.363 | [−0.413, −0.308] |
| C0B − A1 (S1) | 23 | −0.366 | [−0.415, −0.314] |
| C0A − A0 (S2) | 23 | −0.382 | [−0.438, −0.329] |
| C0B − A1 (S2) | 23 | NaN* | — |

Integrity note (Day 6C correction): the quantity was always computed as
*C0 minus cross* (negative when the speaker change dominates); the earlier
contrast labels (`A0_vs_C0A`) read as the reverse difference. The labels
were corrected to `C0A_minus_A0` / `C0B_minus_A1`; the underlying anomaly
values, deltas and CI numbers are unchanged (label bug, not a calculation
bug).

*C0B S2 deltas contain NaN entries because some 0.75 s cases have zero
core-eligible windows at S2 (§11); recorded as NaN, not imputed.

## 16. Failure Cases

22 deterministic rows (`failure_cases.csv`): same-speaker high anomaly (6),
cross-speaker low case AUROC (6), high outside FP (6), worst peak error (4).
All retained; nothing deleted.

## 17. Figures

`results/day6c/figures/`, deterministic selection rules in code: Figure A
(clean/A0/A1/C0A/C0B B1b on one case), Figure B (original vs masked),
Figure C (0.75 s case), Figure D (2.5 s case), Figure E (clean
highest-anomaly case). Success and failure cases both appear.

Integrity fix (Day 6C correction): the GT bands were originally drawn on a
window-index x axis while the trajectories used seconds, misplacing the
bands (visible on Figure A as GT blocks near 52–58 on the index axis).
All five figures were re-rendered with bands on the same seconds time axis
as the trajectories; Figure A was visually verified against the manifest
(paircase_0001 GT 13.75–14.50 s = 220056/232056 samples at 16 kHz). A
full GT-axis audit (start ≥ 0, end ≤ waveform duration, overlap with the
speaker-grid time range, plotted target == manifest) covering all 92
intervals × 2 scales = 184 checks passed with zero problems
(`gt_axis_audit.json`). The bug was figure-only; metrics and GT projection
were never affected (they derive from sample bounds, not from plots).

## 18. Reproducibility

Full independent rerun (C0 WAV regeneration + full pipeline): the five core
outputs (`speaker_scores_c0.csv`, `cross_vs_same_speaker.csv`,
`case_level_metrics.csv`, `bootstrap_ci.csv`, `clean_transition_audit.csv`)
are **byte-identical** across runs (sha256 match). ECAPA inference remains
bit-identical on CPU. Two pipeline bugs found during development (a
tuple-vs-string dict key check in C4; lineage-second units) were fixed
before the recorded runs; both fixes are in the committed code and covered
by tests.

## 19. Tests

`tests/test_day6c_controls.py`: **29 new tests**, all old tests retained.
Full suite: **159 passed, 0 failed** (130 + 29). Coverage maps to the 30
required points, including freeze verification, ECAPA checkpoint hash
recording, C0 donor integrity (same speaker/split, different utterance,
target reuse, deterministic capped selection, no skips), waveform integrity
(duration/format/finite/outside-unchanged/inside-changed), C0A direct-splice
and C0B RMS+crossfade reconstruction against the recorded gain, leakage
zero, Day 6B config/scale/trim immutability, mask label-agnosticism and
determinism, original/masked window-population consistency, tier
immutability and counts, case grouping, bootstrap unit/seed/determinism,
peak-error definition, clean top-3 determinism, and all frozen-artifact
protections (Day 6B, Day 6A, Day 5, raw AISHELL-3).

## 20. Claim Audit — Answers to the Ten Questions

- **Q1** Cross-speaker core anomaly (0.729/0.732) is substantially higher
  than same-speaker C0 (0.366/0.366): 23/23 cases, CIs exclude zero. → YES.
- **Q2** Same-speaker residual: none usable (C0 window AUROC 0.32–0.38,
  masked ≤ 0.52); same-speaker replacement does not trigger B1.
- **Q3** YES — outside FPs are overwhelmingly utterance-transition windows
  (C4: median 0.09 s to the nearest boundary); masking removes them.
- **Q4** Masked vs original (test, full): S1 A0 0.83→0.955 / 0.17→0.773 /
  0.24→0.694; S2 A0 0.901→0.972 / 0.454→0.744 / 0.506→0.657. Core signal
  preserved; masked C0 stays at chance.
- **Q5** 2.5 s easiest (AUPRC 0.66–0.74, F1 0.79); 0.75 s hard in precision
  (AUPRC 0.12); 1.5 s lowest AUROC (0.78–0.80). No significance claims.
- **Q6** S2 stabilizes embeddings but cannot half-cover a 0.5 s core
  (core-positive median 0 at 0.75 s); S1 retains core coverage (median 3).
- **Q7** Consistent direction (case AUROC median ≈ 0.90), but case-level
  AUPRC (≈ 0.15) confirms window AUROC alone overstates precision.
- **Q8** Global top-1 peak error median 5.44 s (IQR 1.2–9.6) unmasked —
  dominated by outside FPs; the masked evaluation is the actionable variant.
- **Q9** YES — 97 % of clean top peaks within 1 s of an utterance boundary.
- **Q10** Safest claim after Day 6C (see §23 statement below).

## 21. Research Integrity

Day 6C is a confound-control study, not a new benchmark. Constructed
long-form ≠ native audiobook. C0 controls the speaker-change factor but not
the text/content factor (C0 is not TTS; A2 remains PENDING). The speech
mask is label-agnostic and pre-frozen. ECAPA is VoxCeleb-pretrained, not
Mandarin-specific. B1 measures speaker-representation consistency, not pure
speaker identity. High AUROC ≠ high-precision localization; AUPRC/F1/peak
error must be read together. Val/test have 6 cases each; window
observations are correlated; the case-level bootstrap is the primary
uncertainty analysis. Findings apply to the cross-speaker splice threat
model only. B4's negative (Day 6B) still means only that the tested
log-energy transient cue does not explain the signal.

## 22. Limitations

C0 donors come from the same constructed protocol, so same-speaker
"recording context" variation is narrower than a real-world spoofed-insert
scenario. The speech mask threshold (0.5) is one point, not a curve — no
sweep was permitted. Peak error is defined on the unmasked score. S2 core
metrics for 0.75 s attacks are structurally limited by the window rule.
One bootstrap contrast is NaN for that reason (recorded, not imputed).
All findings are on the 23-case paired pilot.

## 23. Day6C Gate

| # | Requirement | Status |
|---|---|---|
| 1 | Day 6B frozen | PASS |
| 2 | C0 generated correctly | PASS (23 cases × 2, 0 skips) |
| 3 | C0 waveform verification | PASS (fail-closed) |
| 4 | same-speaker donor integrity | PASS |
| 5 | cross-split leakage = 0 | PASS |
| 6 | cross-vs-same comparison | PASS |
| 7 | speech-active mask | PASS |
| 8 | original + masked both reported | PASS |
| 9 | duration stratification | PASS |
| 10 | case-level evaluation | PASS |
| 11 | peak-error completed | PASS |
| 12 | clean-transition audit | PASS |
| 13 | paired-case bootstrap | PASS |
| 14 | failure cases retained | PASS |
| 15 | reproducibility | PASS (byte-identical rerun) |
| 16 | pytest all pass | PASS (159) |
| 17 | previous frozen artifacts unchanged | PASS |

**DAY 6C CONFOUND-CONTROL GATE = PASS.**

**Safest post-Day 6C claim:**

> "On this constructed cross-speaker-splice pilot, the B1
> speaker-representation inconsistency signal shows specificity to speaker
> change: same-speaker different-utterance splices do not trigger it
> (23/23 cases; case-level bootstrap CIs exclude zero). Under a
> label-agnostic, pre-frozen speech-active mask — which retains 96–100 % of
> attack windows while removing about a third of non-attack windows — the
> conditional-on-speech-active test evaluation reaches AUROC 0.97 / AUPRC
> 0.74 (S2). Clean-sequence high-anomaly peaks occur almost exclusively at
> constructed utterance boundaries, which identifies the dominant
> false-positive source. Remaining limits: case-level precision, short
> attacks (0.75 s) where core coverage is structurally limited at S2, and
> generalization beyond this pilot and this threat model."

## 24. Implications for Next Stage

(Not implemented.)

1. Fold the speech-active mask into the standing evaluation protocol (it is
   label-agnostic and already frozen).
2. A2 same-text TTS replacement is now the single most informative missing
   control: C0 shows the pipeline is specific to speaker change, but text
   confound can only be closed with same-text synthesis.
3. Boundary/transition-aware scoring (down-weighting detected utterance
   transitions instead of masking windows) could combine the mask benefit
   with finer temporal resolution.
4. For 0.75 s attacks, only S1 can measure core localization; a multi-scale
   (S1+S2) fusion under the same non-trained rules is the natural next
   question.
