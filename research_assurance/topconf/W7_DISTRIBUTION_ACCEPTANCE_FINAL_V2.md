# W7 distribution acceptance final v2

Audit date: `2026-09-21`
Scope: re-read-only acceptance reconciliation; no model inference, score,
metric, bootstrap, or result-based selection.

## Accepted W7 inputs

| Distribution | Version / split | Audio / GT evidence | Adapter / identity | Decision |
|---|---|---|---|---|
| PartialEdit | `v1.1 / E1` | 42,471 WAV; official temporal GT; 16 kHz mono PCM; no missing/orphan | PASS | `READY` |
| LlamaPartialSpoof | `1.0.b / R01TTS.0.b` | 64,388 WAV members; 64,388 GT rows; archive MD5 `a4de860a845816fa65785dddd7849700`; audio/GT identity PASS; decode/duration PASS | official SAL parser compatibility PASS | `READY` |

The Llama archive remains on the external data volume and is referenced by its
official record and verified integrity evidence; it is not copied into the
repository. The readiness evidence is record-level and pre-execution only.

## Explicitly blocked candidates

`PartialSpoof_v1.2_eval` remains `NOT_READY` because official IDs
`CON_E_0034982` and `CON_E_0058039` lack the required audio/GT identity.
`HAD` and `HQ-MPSD_English` remain `NOT_READY` because the official archive
integrity/ZIP checks did not pass. `MIST` remains `NOT_READY` because rights
are unresolved. None is silently substituted or selected by outcome.

## Gate and evidence boundary

```text
READY_EXTERNAL_DISTRIBUTIONS = 2
DISTINCT_LOCALIZATION_PARADIGMS = 4
GATE_1_DEFINITION = >=3 paradigms AND >=2 external distributions
W6_GATE = PASS
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
ALL_W7_METRICS = NOT_MEASURED
```

`W7_DISTRIBUTION_ACCEPTANCE_FINAL_V2 = PASS_FOR_PREPARATION_ONLY`.
