# WEEK5_EXP2_PROTOCOL

**Stage:** `WEEK5_EXP2_MULTISCALE_CORE_CONTEXT_AND_GENERATOR_OOD_QUALIFICATION`  
**Population:** `WEEK5_EXP2_QUALIFICATION_ONLY`

## Frozen questions and design

Exp2 tests whether aligned short/medium/long temporal context improves core localization beyond Exp1 B2-full and transfers across generators. It is qualification evidence, not a final-test, SOTA, production, or definitive generalization claim.

Scales are fixed before qualification: `SHORT_WINDOW_SAMPLES=8000` (~0.5 s), `MEDIUM_WINDOW_SAMPLES=24000` (1.5 s), `LONG_WINDOW_SAMPLES=64000` (4.0 s), with canonical `HOP_SAMPLES=4000` (250 ms). Every scale is represented around the same medium-window center. Centers use the medium window start plus half its width; short/long context is a fixed neighborhood of the medium score trajectory. Edge windows use NaN padding, and models use deterministic finite-value imputation. No GT enters feature construction.

The model ladder is frozen: B1, Exp1 B2-full, B3_SHORT, B3_MEDIUM, B3_LONG, B3_MS, B4_FULL, and B2_CAPACITY_MATCHED_CONTROL. All models use the same deterministic logistic-regression implementation and fixed speaker-disjoint split with seed `20260916`.

Regions remain exactly Exp1: `CLEAN`, `BOUNDARY`, `CORE`, `ALL_ATTACK`, derived from sample-first GT overlap and never re-detected from waveform or score.

## Generator-OOD folds

Three folds are frozen when all three mechanisms have valid score evidence:

```text
FOLD_A: train controlled_splice + F5; OOD CosyVoice2
FOLD_B: train controlled_splice + CosyVoice2; OOD F5
FOLD_C: train F5 + CosyVoice2; OOD controlled_splice
```

For each fold, the OOD generator is absent from training. Speaker and source/reference utterance identities are checked for split separation where possible.

## Features and metrics

Each scale has center score, context mean/std/min/max, left/right context means, left-right difference, center-context difference, gradient, and range. Cross-scale features are the three score differences and two absolute disagreements. B4 adds these to the frozen Exp1 B2 features. The anti-capacity control uses the same feature dimension as B4 but only deterministic redundant transforms of Exp1 features.

Every model reports AUROC/AUPRC for ALL, BOUNDARY, and CORE. Case-level bootstrap is fixed at N=2000, seed=20260916, percentile 95% CI; no window-level bootstrap.

## Gate and stop rule

`STRONG_GO` requires B4 > B2 for ALL and CORE, improvements over B1 in at least two generator conditions, positive OOD delta in at least two valid folds, stable case bootstrap direction, and no single-case/speaker dominance. `WEAK_GO` is clear core improvement with unstable OOD. `NO_GO` is B4 approximately equal to B2 or consistently harmful OOD. If an implementation bug occurs, execution stops and a revision record is required before rerun. Scales, features, seed, regions, cases, and metrics cannot be changed after first qualification execution.
