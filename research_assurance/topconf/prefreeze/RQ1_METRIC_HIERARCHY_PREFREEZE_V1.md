# RQ1 Metric Hierarchy Pre-Freeze Review v1

Status: **DRAFT / RECOMMENDED_CANDIDATE / NON-AUTHORIZING**

This review is based on formal metric semantics and the committed
`LD_DR95_FORMAL_REVIEW_V1.md`; it does not inspect Phase3R scientific outputs.
Labels below mean `RECOMMENDED_CANDIDATE`, `ALTERNATIVE`, or
`DEPENDENCY_ON_PHASE3R`, never frozen primary endpoints.

## Detection candidates

| Metric | Candidate use | Strength | Limitation / dependency |
|---|---|---|---|
| AUROC | Secondary or broad discrimination summary | Threshold-free and common | Can hide low-prevalence operating behavior and does not directly define retention. |
| AUPRC | Secondary when spoof prevalence is low | Sensitive to positive prevalence and useful for rare partial edits | Prevalence-dependent and less cross-study comparable without a declared population. |
| EER / RangeEER | Diagnostic or native-dataset-compatible metric | Familiar in anti-spoofing; RangeEER models temporal ranges | Threshold convention, range definition, temporal resolution, and official implementation must be compatible. |
| TPR at fixed FPR / decision retention | Detection-retention candidate | Operationally interpretable | FPR/threshold must be frozen; empty or one-class cases fail closed. |
| Correct-after-given-correct | Detection-retention alternative | Paired and operational | Undefined if no clean-correct cases; requires paired decisions. |

## Where candidates

| Level | Candidate metrics | Strength | Limitation |
|---|---|---|---|
| Frame | AUPRC, AUROC, frame F1, RangeEER | Uses native dense maps and fine temporal detail | Resolution-dependent, highly correlated frames, boundary shortcut risk. |
| Event | F1/AP at declared IoU, onset/offset error | Directly reflects recovered manipulated intervals | Requires proposal extraction and a fixed threshold/matching rule. |
| Proposal | AP/mAP at declared IoU | Compatible with proposal models such as CFPRF | Not native for all frame localizers; mapping can add degrees of freedom. |
| Boundary | Onset/offset error, boundary F1 | Directly diagnoses transition reliance | Can reward a boundary-only system while ignoring manipulated interiors. |

## LD@DR95 candidate

For higher-is-better scores, the formal candidate is:

```text
LD@DR95 = 1 - mean(localization_retention_c)
           over conditions with detection_retention_c >= 0.95
```

It requires a declared detection-retention option, clean reference score,
condition grid, statistical unit, and missingness rule. The feasible set and
`NOT_ESTIMABLE` behavior must be reported. Lower-is-better error metrics must
be transformed by an approved utility or remain secondary; raw AUROC/mAP and
raw EER/boundary error must not be subtracted.

## Common-core compatibility review

The common-core candidate must be the intersection of finite, aligned native
outputs across the retained paradigms. A model cannot be forced into frame,
event, proposal, or RangeEER metrics its output contract does not support.
Phase3R may change which paradigms/checkpoints are actually available, so the
common core remains `DEPENDENCY_ON_PHASE3R`.

## Candidate hierarchy for human review

1. `RECOMMENDED_CANDIDATE`: one paired LD@DR95 definition on the largest
   verified common Where level, with the primary score direction explicit.
2. `ALTERNATIVE`: a fixed-threshold detection-retention constraint or a
   sample-conditional paired estimand if the common output contract requires it.
3. `SECONDARY`: detection AUROC/AUPRC/EER, frame AUPRC/RangeEER, event/proposal
   AP/F1, and boundary diagnostics, each with declared compatibility.

No metric is formally frozen here.
