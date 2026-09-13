# WEEK5_EXP3_PROTOCOL

**Stage:** `WEEK5_EXP3_GENERATOR_DIVERSE_REPRESENTATION_LEARNING`  
**Research status:** `QUALIFICATION_ONLY`

## Frozen scope

Exp3 reuses the Exp2 generator-OOD population and all temporal features without changing scale, hop, alignment, edge handling, regions, cases, or split. `EXP2_OOD_POPULATION == EXP3_OOD_POPULATION` is required and checked by parent-manifest SHA-256.

The three frozen folds are: Fold A train controlled_splice+F5 / OOD CosyVoice2; Fold B train controlled_splice+CosyVoice2 / OOD F5; Fold C train F5+CosyVoice2 / OOD controlled_splice. The OOD generator is excluded from training, dev model selection, architecture selection, feature selection, and threshold selection.

## Fixed models

R0 is Exp2 B4-full, reproduced with the frozen deterministic linear baseline. R1/R2/R3 use one fixed small head: B4 input -> Linear(32) -> ReLU -> Linear(8) representation -> Linear(1) classifier. Training uses Adam, lr=0.001, weight decay=0.0001, 60 epochs, batch size 96, seed `20260917`, CPU deterministic mode. R1 is generator-balanced case-aware ERM. R2 adds supervised contrastive loss (temperature 0.20, weight 0.25) using same-label cross-generator positives and different-label negatives. R3 adds group-robust classification: the mean per-generator loss is reweighted toward the current worst group with weight 0.50. `R2_NO_GENERATOR_BALANCING` removes only the generator balancing while retaining the fixed R2 architecture/objective.

Generator-balanced case-aware sampling gives each generator equal mass and each case equal mass within generator; rows are sampled without changing labels or population. Generator ID is never an inference feature. Boundary/core are subgroup diagnostics only; the primary binary label remains attack-related versus clean.

## Evaluation and gates

Primary metrics are mean and worst generator-OOD AUROC/AUPRC, plus all/boundary/core per fold and in-domain metrics. Case-level bootstrap is N=2000, seed `20260917`, percentile 95% CI. The generator probe is a secondary diagnostic trained on frozen representations.

`STRONG_GO` requires positive mean OOD delta, non-decreasing worst OOD, at least 2/3 fold improvements, controlled-splice recovery, no material fold collapse, and broadly preserved in-domain performance. `WEAK_GO` requires mean improvement and controlled-splice recovery with one unstable fold or uncertainty overlap. If controlled-splice remains substantially degraded or worst-generator performance worsens, the gate is `NO_GO`. No outcome-driven changes are permitted after the first run; bugs require an invalidation/revision record before rerun.
