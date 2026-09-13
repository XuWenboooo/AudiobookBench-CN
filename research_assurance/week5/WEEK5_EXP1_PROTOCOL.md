# Week5 Exp1 Protocol

**Stage:** `WEEK5_EXP1_BOUNDARY_CORE_RECOVERABILITY_QUALIFICATION`  
**Population:** `WEEK5_EXP1_QUALIFICATION_ONLY`  
**Question:** Can explicit temporal boundary/core features recover localization performance lost by frozen B1b across synthetic mechanisms?

This is an engineering-scientific qualification, not a final-test or SOTA claim. Week4 is completely out of scope. The fail-closed guard rejects paths containing `week4_validation`, `held_out`, `week4_adaptive_redteam_runs/.../week4_validation`, or any `*held*` path.

## Frozen design

- Inputs are historical Week1–3 score evidence only; no Week4 output is read.
- S2 is 1.5 s windows with 250 ms hop. B1b is the frozen sequence-local trimmed prototype score (`trim_ratio=0.20`). No retraining or threshold tuning is performed for B1.
- Region labels are derived only from sample-first GT overlap: `CLEAN` has zero attack overlap; `CORE` has at least 50% overlap with strict core and no blend overlap; `BOUNDARY` is attack/blend overlap not classified as core. Labels never enter feature construction.
- Features are fixed before execution: `b1b_score`, left/right one-step deltas, absolute local gradient, neighbor mean/std/min/max, and center-minus-neighbor-mean contrast. Missing edge neighbors use NaN and are excluded by the classifier's finite-row mask.
- B2 is logistic regression with fixed solver settings and no outcome-driven tuning. Ablations are B1, B2a (B1 + derivatives), B2b (B1 + neighborhood statistics), and B2-full (all features).
- Case split is deterministic with seed `20260915`, speaker-disjoint, and source-utterance-disjoint where identities are available. The unit for bootstrap is `case_id`, N=2000, percentile 95% CI.
- Primary metrics are AUROC and AUPRC for ALL_ATTACK vs CLEAN, BOUNDARY vs CLEAN, and CORE vs CLEAN. Generator-specific and leave-one-mechanism-out directional results are reported only when computable.

## Decision gate

`STRONG_GO` requires ALL-AUROC improvement on at least two mechanisms, consistent boundary direction, no obvious generator-OOD collapse, and no single-speaker/case explanation. `WEAK_GO` is boundary improvement with unstable overall/core results. Otherwise the result is `NO_GO` or `INCONCLUSIVE` when evidence is insufficient.

## Execution order

1. Source audit; 2. protocol and manifest; 3. TEST_ONLY unit tests; 4. leakage guard; 5. frozen B1 reproduction; 6. B2 qualification. Any implementation bug stops execution and creates a new revision; numbers are never used to alter the split, regions, features, labels, or metrics.
