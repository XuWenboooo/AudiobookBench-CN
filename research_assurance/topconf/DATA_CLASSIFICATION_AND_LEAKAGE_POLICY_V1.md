# Data Classification and Leakage Policy v1

Status: **DRAFT / REQUIRED BEFORE DATA FREEZE**

## Classification

| Class | Description | Allowed use |
|---|---|---|
| H-PILOT | Week1–5 historical artifacts and observations | pilot context and audit only |
| C-TRAIN | confirmatory-phase development data | development only |
| C-DEV | confirmatory validation data | protocol-approved tuning only |
| C-HELDOUT | confirmatory held-out data and labels | locked evaluation only |
| EXT-BASELINE | externally sourced baseline artifacts | comparison subject to license/provenance |

## Rules

1. H-PILOT must never be merged into the confirmatory population without an explicitly approved new protocol.
2. C-HELDOUT labels, identifiers, and derived scores must not enter tuning, prompt selection, threshold selection, or model selection.
3. Every derived artifact records source class, transformation, code version, and operator/date.
4. Any suspected leakage pauses the run and creates an incident record; it is not silently repaired.
5. Access to held-out material is least-privilege and logged.
