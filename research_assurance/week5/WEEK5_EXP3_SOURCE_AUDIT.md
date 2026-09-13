# WEEK5_EXP3_SOURCE_AUDIT

Status: `READ_ONLY_AUDIT_COMPLETE`

```text
EXP2_STATUS = PASS
EXP2_POPULATION_REPRODUCIBLE = YES (92 cases; deterministic Exp2 manifest)
EXP2_FEATURES_REPRODUCIBLE = YES (frozen feature_manifest.json)
EXP2_OOD_FOLDS_REPRODUCIBLE = YES (three explicit folds)
COSYVOICE2_REQUALIFICATION_PROVENANCE_VALID = YES (23/23 score rows; frozen Week2 waveforms)
WEEK4_LEAKAGE = NONE
```

Exp3 inherits the Exp2 population and identity exactly. No Week4 Validation, Held-out, H4, adaptive winner, waveform, or score is read. Temporal scale search is closed: SHORT/MEDIUM/LONG, canonical medium center, 250 ms hop, and the Exp2 B4 feature contract are unchanged.

The representation input is the frozen Exp2 B4 feature vector. The ECAPA backbone remains frozen and is not fine-tuned; no generator identity is supplied to inference-time models. Generator identity is used only for training balance, contrastive pair construction, group-robust optimization, and the diagnostic probe.
