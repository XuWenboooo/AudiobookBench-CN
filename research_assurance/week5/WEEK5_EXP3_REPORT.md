# WEEK5_EXP3_REPORT

```text
WEEK5_EXP3_STATUS = PASS (qualification-only execution; scientific gate NO_GO)
WEEK4_VALIDATION_DATA_USED = NO
WEEK4_HELDOUT_DATA_USED = NO
WEEK4_H4_USED = NO

EXP2_POPULATION_REUSED = YES (byte-identical parent SHA256)
EXP2_B4_REPRODUCED = YES (R0 metrics exactly match Exp2 B4)
GENERATOR_ID_USED_AT_INFERENCE = NO
OOD_FOLDS = 3

R0_MEAN_OOD_AUROC = 0.673565
R0_WORST_OOD_AUROC = 0.448061
R1_MEAN_OOD_AUROC = 0.427830
R1_WORST_OOD_AUROC = 0.174379
R2_MEAN_OOD_AUROC = 0.427471
R2_WORST_OOD_AUROC = 0.174251
R3_MEAN_OOD_AUROC = 0.427628
R3_WORST_OOD_AUROC = 0.174611

BEST_MODEL = R0 (Exp2 B4 baseline)
DELTA_MEAN_OOD_AUROC_VS_R0 = R1 -0.245735; R2 -0.246093; R3 -0.245937
DELTA_WORST_OOD_AUROC_VS_R0 = R1 -0.273683; R2 -0.273811; R3 -0.273450

COSYVOICE2_OOD_DELTA = R3 -0.276037
F5_OOD_DELTA = R3 -0.188322
CONTROLLED_SPLICE_OOD_DELTA = R3 -0.273450
CONTROLLED_SPLICE_RECOVERY = NO

IN_DOMAIN_ALL_AUROC_DELTA = R3-R0 -0.362163
BOUNDARY_AUROC_DELTA = R3-R0 -0.287129
CORE_AUROC_DELTA = R3-R0 -0.792083

GENERATOR_PROBE_R0 = 0.503476
GENERATOR_PROBE_R1 = 0.509434
GENERATOR_PROBE_R2 = 0.509434
GENERATOR_PROBE_R3 = 0.509434

BALANCED_SAMPLING_HELPED = NO CLEAR EVIDENCE
CONTRASTIVE_REPRESENTATION_HELPED = NO
GROUP_ROBUST_OBJECTIVE_HELPED = NO

BOOTSTRAP = 3 folds, N=2000/fold/model, seed=20260917, case-level; finite=2000/2000 for every reported fold/model
TESTS = 16 passed

DOES_GENERATOR_DIVERSE_REPRESENTATION_IMPROVE_MEAN_OOD = NO
DOES_IT_IMPROVE_WORST_GENERATOR_OOD = NO
DOES_IT_RECOVER_CONTROLLED_SPLICE = NO

WEEK5_GENERATOR_DIVERSE_REPRESENTATION_DIRECTION = NO_GO
RECOMMENDED_WEEK5_EXP4 = stronger frozen SSL speech representation or a learned temporal encoder; do not add more temporal scales
```

## Interpretation

The Exp2 B4 baseline was reproduced exactly as R0. All learned representation heads (R1/R2/R3) substantially reduced in-domain and generator-OOD localization performance. The worst-generator score fell from R0's `0.448061` to `0.174611` at best, and controlled-splice OOD was not recovered. Contrastive and group-robust objectives did not rescue the collapse; the generator probe also did not show a meaningful reduction in generator information.

This is a negative qualification result for the current small-head representation-learning design. It does not prove that generator-diverse representation learning is impossible, and it is not a production or universal-detector claim. The frozen Exp2 temporal-scale route should not be expanded by adding more scales. A future Exp4 should first improve the frozen speech representation or use a separately justified learned temporal encoder.

## Integrity

- Exp3 manifest is byte-identical to the Exp2 population; parent SHA-256 is recorded in `results/week5_exp3/provenance.json`.
- All three OOD generators are excluded from their respective fold training populations.
- Generator ID is used only for balancing, contrastive construction, robust weighting, and diagnostics—not inference.
- ECAPA remains frozen and is not fine-tuned.
- Week4 Validation/Held-out/H4 artifacts were not read or used.
