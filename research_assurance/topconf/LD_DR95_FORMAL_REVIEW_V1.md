# LD@DR95 Formal Review v1

Status: **REVIEWED CANDIDATE / NOT PREREGISTRATION-LOCKED**

## Notation and direction handling

Let (D_0) and (L_0) be the clean reference detection and localization
scores, and (D_c), (L_c) the scores for a paired condition (c). This
review only permits higher-is-better scores after explicit direction
conversion. For an error metric such as EER or boundary error, define a
predeclared bounded utility or report it separately; never divide or subtract
raw lower-is-better values against AUROC/mAP.

## Detection retention candidates

| Option | Definition | Strength | Failure mode |
|---|---|---|---|
| A | (D_c/D_0) | compact and curve-friendly | invalid for lower-is-better metrics and unstable near zero |
| B | (P(\text{after correct}\mid\text{before correct})) | directly operational and threshold-aware | requires paired decisions and can be undefined when no clean-correct cases exist |
| C | fixed threshold/fixed-FPR detection constraint | preserves an operational decision rule | threshold/FPR choice must be frozen and can yield an empty feasible set |

Recommended infrastructure representation: store all three when inputs permit,
but choose exactly one primary definition before preregistration lock. The
current implementation uses Option A only for a higher-is-better synthetic
curve and does not select a confirmatory threshold.

## Localization candidates

For a higher-is-better primary localization score, define localization
retention (R^L_c=L_c/L_0), requiring (L_0>0). For lower-is-better errors,
use an explicitly approved transformed utility or keep them secondary; do not
mix directions in a single arithmetic aggregate.

## Candidate LD@DR95 definition

Let (F_{.95}=\{c: R^D_c\ge .95\}). The recommended candidate is:

```text
LD@DR95 = 1 - mean_{c in F_.95}(R^L_c)
```

This is a condition-level, paired, macro-average estimand. It reports the
number of feasible conditions and is **NOT_ESTIMABLE** when (F_{.95}) is
empty. It is never replaced with zero.

## Alternatives and decision boundary

- Worst-case: (1-min_{c\in F_{.95}}R^L_c); security-relevant but high variance.
- AUC-under-budget: integrate localization retention over a frozen condition
  strength/budget grid while requiring detection feasibility; needs a frozen
  grid and normalization.
- Sample-conditional: compute retained correctness and localization loss per
  case, then aggregate; operationally meaningful but requires a case-level
  localization estimand and missingness rule.
- Condition-level median/trimmed mean: robust descriptive sensitivity only,
  not primary unless locked in advance.

Known failure modes: clean localization score zero, one-class detection,
empty feasible set, incomparable condition grids, lower-is-better metrics,
post-hoc choice of pooling/threshold, and aggregation over frames instead of
the predeclared statistical unit. All must fail closed or be reported as
not-estimable.
