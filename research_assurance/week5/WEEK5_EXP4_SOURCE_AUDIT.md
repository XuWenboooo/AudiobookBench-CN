# WEEK5_EXP4_SOURCE_AUDIT

Status: `READ_ONLY_AUDIT_COMPLETE`

```text
EXP2_POPULATION_REPRODUCIBLE = YES
EXP2_OOD_FOLDS_REPRODUCIBLE = YES (3 explicit folds)
EXP2_B4_REPRODUCIBLE = YES (Exp3 R0 exactly matched Exp2 B4)
EXP3_NO_GO_REPRODUCIBLE = YES (metrics artifact; all learned heads below R0)
WEEK4_LEAKAGE = NONE
```

Exp4 reuses the byte-identical Exp2 population, including speaker identities, case identities and generator-OOD fold membership. Exp2 SHORT/MEDIUM/LONG, 250 ms hop, canonical medium center, edge handling and region semantics are inherited without search.

## Frozen representation candidates

| ID | Representation | Status | Provenance |
|---|---|---|---|
| E0 | SpeechBrain ECAPA-TDNN `spkrec-ecapa-voxceleb` | AVAILABLE | `pretrained/spkrec-ecapa-voxceleb`; existing Week1 frozen backend |
| E1 | Chinese HuBERT base | AVAILABLE | `results/week3_engineering_qualification/gpt_sovits_v3/assets/chinese-hubert-base/pytorch_model.bin`; local offline asset |

No additional candidate was included because no other local SSL asset had equally clear, stable offline loading provenance in the audit. E1 uses the last hidden layer, mean pooling, per-vector L2 normalization, and the fixed audio-to-SSL frame interval alignment described in the frozen protocol. Both backbones are frozen.

## CosyVoice2 and Week4

CosyVoice2 score provenance is inherited from the validated Week2 requalification in `results/week5_exp2/cosyvoice2_scores.jsonl`. Week4 Validation, Held-out, H4, adaptive-winner, waveform and score artifacts were not read or used.
