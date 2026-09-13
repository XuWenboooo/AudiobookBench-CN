# Whether-A Pre-Freeze Review v1

Status: **DRAFT / CANDIDATE / NON-AUTHORIZING**

Whether-A is the utterance-level decision derived from a localization system.
This review uses formal reasoning, synthetic examples, and output-contract
constraints only. No project model was run and no real benchmark was compared.

## Candidate pooling rules

| Rule | Low-prevalence sensitivity | Outlier sensitivity | Temporal-resolution dependence | Cross-model comparability | Calibration | Candidate status |
|---|---|---|---|---|---|---|
| `mean_pool` | May dilute a short fake region | Low to medium | Relatively stable but depends on frame support | Good if masks/resolution are aligned | Needs a fixed calibration rule | Candidate |
| `max_pool` | High sensitivity to a short strong region | High; one spike can dominate | High; finer grids create more opportunities for maxima | Poorer without resolution normalization | Often poorly calibrated | Alternative/diagnostic |
| `top_k_mean` | Tunable compromise for sparse regions | Medium; depends on `k` and score count | High unless `k` is defined by duration/quantile | Conditional on a common support rule | Needs fixed `k`/quantile calibration | Alternative |
| Model-native utterance score | May reflect trained semantics | Unknown and model-specific | Depends on native architecture | Low unless contract is standardized | Potentially best native calibration | Alternative when explicitly documented |
| Predefined model-specific aggregation | Can preserve each model’s intended output | Depends on rule | Explicit but heterogeneous | Lowest; requires a common reporting layer | Must be separately calibrated | Diagnostic/conditional |

## Synthetic reasoning

For a map with one short high score and a long low-score background, `max_pool`
can detect the short event while `mean_pool` can suppress it. If the short score
is a spurious boundary spike, the ordering reverses scientifically: `max_pool`
can reward a shortcut. `top_k_mean` interpolates between these cases but adds a
prevalence/temporal-resolution parameter. These examples show sensitivity and
failure modes; they do not identify a best rule for the real models.

## Candidate procedure

Before authorization, choose at most one primary rule using only:

- the semantic meaning of an utterance-level “contains manipulation” decision;
- low-prevalence behavior;
- temporal-resolution and support normalization;
- cross-model comparability;
- calibration stability under a predeclared Level-1 rule.

Do not run models and choose the pooling rule by AUROC, gap magnitude, or any
other Level-2/Phase3R outcome. If evidence is insufficient, record
`RECOMMENDATION = CANDIDATE ONLY` and make the rule non-primary.
