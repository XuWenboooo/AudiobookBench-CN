# Day 6B Claim Addendum (wording only; no numeric change)

Date: 2026-09-05, issued before any Day 6C experiment.

## 1. The safest current claim

> **"B1 provides a strong temporal speaker-representation inconsistency
> signal."**

This is the supported statement. It is **not** supported to claim that
"a high-precision deployable localizer is solved."

Reasons:

- Window-level AUPRC (test 0.17–0.18 at S1) and localization F1
  (0.24–0.28) remain far below the AUROC, because outside windows
  (false positives) are frequent in absolute terms.
- Case counts are small (6 test cases); CIs are wide.
- High AUROC under heavy class imbalance does not imply usable precision.

## 2. Scope of the B4 negative result

The B4 boundary-transient diagnostic was one specific cue: the maximum
adjacent-frame log-energy step inside each speaker window. Its null result
(test AUROC 0.36–0.37) supports only:

> "The tested energy-transient cue does not explain the B1 result."

It does **not** support:

> "All possible splice/boundary artifacts have been ruled out."

Other artifact families (click/phase discontinuities, spectral-edge
artifacts, room-tone differences between donor and target recording
contexts, codec-level mismatch) were not tested and remain open. Day 6C's
C0 (same-speaker splice), C1 (speech-active masking) and C4 (clean
transition audit) are the next confound analyses, not a completion of the
shortcut audit.

## 3. Status unchanged

All Day 6B numbers, configs, thresholds, embeddings and outputs remain
frozen (see `DAY6B_FREEZE.md`). This addendum changes interpretation
wording only.
