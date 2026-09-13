# WEEK5_EXP2_REPORT

```text
WEEK5_EXP2_STATUS = PASS (qualification-only)
WEEK4_VALIDATION_DATA_USED = NO
WEEK4_HELDOUT_DATA_USED = NO
WEEK4_H4_USED = NO

EXP1_REPRODUCED = YES (artifact audit; frozen B1b/B2 scorer retained)
EXP2_PROTOCOL_FROZEN = YES
EXP2_POPULATION_FROZEN = YES
COSYVOICE2_PROVENANCE_STATUS = IN_SCOPE_REQUALIFICATION; 23/23 frozen waveforms scored

TOTAL_CASES = 92
TRAIN_CASES = 52
DEV_CASES = 24
QUALIFICATION_TEST_CASES = 16

GENERATOR_OOD_FOLDS = 3 valid folds

B1_ALL_AUROC = 0.641303
B1_BOUNDARY_AUROC = 0.595171
B1_CORE_AUROC = 0.905627

B2_ALL_AUROC = 0.694313
B2_BOUNDARY_AUROC = 0.657724
B2_CORE_AUROC = 0.903958

B3_SHORT_ALL_AUROC = 0.693867
B3_MEDIUM_ALL_AUROC = 0.718725
B3_LONG_ALL_AUROC = 0.759455
B3_MS_ALL_AUROC = 0.786120

B4_ALL_AUROC = 0.786143
B4_BOUNDARY_AUROC = 0.763277
B4_CORE_AUROC = 0.917158

DELTA_B4_VS_B2_ALL = +0.091830
DELTA_B4_VS_B2_BOUNDARY = +0.105553
DELTA_B4_VS_B2_CORE = +0.013200

DELTA_B4_VS_B1_ALL = +0.144840
DELTA_B4_VS_B1_CORE = +0.011531

GENERATOR_SPECIFIC_RESULTS = persisted in generator_metrics.json
GENERATOR_OOD_RESULTS = persisted in generator_ood_metrics.json
GENERATOR_OOD_DELTA_AUROC = Fold A +0.247568; Fold B +0.209894; Fold C -0.358137 (B4 minus B1)

B2_CAPACITY_MATCHED_CONTROL = 0.693154 ALL AUROC; below B4, supporting information gain beyond dimension alone

BOOTSTRAP = N=2000, seed=20260916, case_id unit; all/boundary/core finite = 2000/2000/1998; B4-minus-B2 AUROC CIs:
  all [0.039735, 0.137476]
  boundary [0.046513, 0.154563]
  core [-0.056981, 0.059595]
TESTS = 11 Week5 tests passed; JSON artifacts and score provenance validated

DOES_MULTISCALE_CONTEXT_RECOVER_CORE_LOCALIZATION = YES (directional; small main-population gain, CI includes zero)
DOES_RECOVERY_TRANSFER_TO_GENERATOR_OOD = INCONCLUSIVE

WEEK5_MULTISCALE_DIRECTION = WEAK_GO
RECOMMENDED_WEEK5_EXP3 = GENERATOR_DIVERSE_REPRESENTATION_LEARNING
```

## Interpretation

Multi-scale context improves the aggregate and boundary metrics beyond Exp1 B2, with B3_MS/B4-full outperforming the single-scale ladder and the capacity-matched control. The core gain is positive but modest and its case-level interval includes zero. This is directional qualification evidence, not proof of robust core recovery.

Generator-OOD transfer is mixed. Fold A (OOD CosyVoice2) and Fold B (OOD F5) improve over B1, while Fold C (OOD controlled_splice) collapses below B1 and B2. The required three folds are reported, but the mixed result does not support a strong transfer claim. Exp3 should therefore move toward generator-diverse representation learning rather than adding more temporal scales.

## Integrity and provenance

- CosyVoice2 was requalified from frozen Week2 waveform and GT artifacts only; no audio was regenerated.
- Sample-first GT region semantics remain unchanged from Exp1.
- All scale features use the canonical medium center, fixed radii, and deterministic NaN edge padding.
- The Week4 guard is fail-closed, and all final Week4 usage fields are `NO`.
- All artifacts are qualification-only and must not be presented as final SOTA, production detection, or definitive cross-generator generalization.
