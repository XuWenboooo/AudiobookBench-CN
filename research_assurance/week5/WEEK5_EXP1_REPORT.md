# WEEK5_EXP1_REPORT

`WEEK5_EXP1_STATUS = PASS (qualification-only)`

The fixed Week5 Exp1 pipeline completed after protocol, manifest, TEST_ONLY tests, fail-closed guard, frozen B1 reproduction, B2 qualification, ablation, and case-level bootstrap. This report is not a final-test or paper-generalization claim.

```text
WEEK4_VALIDATION_DATA_USED = NO
WEEK4_HELDOUT_DATA_USED = NO
WEEK4_H4_USED = NO

QUALIFICATION_CASES = 69
TRAIN_CASES = 39
DEV_CASES = 18
QUALIFICATION_TEST_CASES = 12
SPEAKER_DISJOINT = YES
EXP1_QUALIFICATION_SEED = 20260915

B1_ALL_AUROC = 0.668570
B1_ALL_AUPRC = 0.205134
B1_BOUNDARY_AUROC = 0.501380
B1_CORE_AUROC = 0.897605

B2_ALL_AUROC = 0.716351
B2_ALL_AUPRC = 0.327744
B2_BOUNDARY_AUROC = 0.535374
B2_CORE_AUROC = 0.961123

DELTA_ALL_AUROC = +0.047780
DELTA_BOUNDARY_AUROC = +0.033994
DELTA_CORE_AUROC = +0.063518
DELTA_ALL_AUPRC = +0.122610
DELTA_BOUNDARY_AUPRC = +0.007373
DELTA_CORE_AUPRC = +0.261882

GENERATOR_SPECIFIC_RESULTS = controlled_splice and F5 reported separately; CosyVoice score evidence missing
GENERATOR_OOD_RESULTS = NOT_REPORTABLE_FOR_STRONG_CLAIM
BOOTSTRAP = N=2000, seed=20260915, case_id unit, finite=2000; AUROC-delta CIs:
  all [-0.042948, 0.059323]
  boundary [-0.087902, 0.034225]
  core [0.002238, 0.130932]
ABLATION = B2a/B2b/B2-full all improve aggregate AUROC over B1; full: 0.716351, B2a: 0.713788, B2b: 0.718242

WEEK5_BOUNDARY_AWARE_DIRECTION = WEAK_GO
RECOMMENDED_WEEK5_EXP2 = multi-scale + core/context branch, with a separately authorized population and generator-OOD qualification
```

## Generator-specific directional results

On the fixed qualification-test speaker split, controlled splice B1/B2-full AUROC was 0.883217/0.950643 for ALL, 0.922991/0.975074 for BOUNDARY, and 0.895433/0.960485 for CORE. F5 B1/B2-full AUROC was 0.513544/0.542340 for ALL and BOUNDARY. F5 CORE was not computable because the qualification-test subset had no positive strict-core windows. CosyVoice2 has successful Week2 waveforms and GT sidecars, but no reusable B1b/S2 score artifact was found in the read-only audit; it was not silently scored or claimed.

The weak-go decision is directional: boundary and overall AUROC increase in the available aggregate and controlled-splice evidence, while the case-level CIs include zero for overall and boundary deltas, and F5 evidence is small/limited. Therefore this result supports pursuing boundary-aware features in Exp2, not a claim of robust cross-generator generalization.

## Integrity record

- Regions are derived from frozen sample-first GT overlap; no waveform re-detection is used.
- GT fields are excluded from model inputs.
- The four required model variants are persisted in `results/week5_exp1/feature_manifest.json` and metrics.
- TEST_ONLY suite: 5 passed, including region semantics, leakage guard, feature determinism, and split determinism.
