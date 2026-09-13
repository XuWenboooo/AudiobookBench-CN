# WEEK5_EXP2_SOURCE_AUDIT

Status: `READ_ONLY_AUDIT_COMPLETE`

## Exp1 verification

| Check | Result | Evidence |
|---|---|---|
| `EXP1_STATUS` | PASS | `results/week5_exp1/metrics.json` |
| `EXP1_B1_REPRODUCIBLE` | YES | Exp1 metrics, feature manifest and frozen `src/audiobookbench/temporal/day6b_scoring.py` |
| `EXP1_B2_REPRODUCIBLE` | YES | Exp1 metrics and deterministic runner |
| `EXP1_SPLIT_DETERMINISTIC` | YES | `data/manifests/week5_exp1_qualification_population.json`, 5 passing tests |
| `EXP1_WEEK4_LEAKAGE` | NONE | Exp1 metrics and fail-closed guard |

## CosyVoice2 provenance

```text
COSYVOICE2_SOURCE_AUDIO_AVAILABLE = YES
COSYVOICE2_SYNTHETIC_AUDIO_AVAILABLE = YES (23/23 successful frozen waveforms)
COSYVOICE2_GT_AVAILABLE = YES (23/23 waveform/sidecar GT verification)
COSYVOICE2_CASE_IDENTITY_AVAILABLE = YES
COSYVOICE2_B1B_SCORE_REPRODUCIBLE = YES
```

The score requalification uses only the existing Week2 waveform, source identity, and sample-first sidecar GT. It does not regenerate CosyVoice2 audio, change the generator, change labels, or tune B1b. A representative score extraction was executed successfully with the frozen ECAPA backend; the full extraction is persisted as a Week5 provenance artifact.

## Week4 isolation

Week4 Validation/Held-out/H4 scientific artifacts were not opened or used. Week4 paths are rejected by the Exp2 guard before any input is accepted.
