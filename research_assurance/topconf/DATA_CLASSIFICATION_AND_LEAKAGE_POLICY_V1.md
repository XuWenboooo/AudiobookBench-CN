# Data Classification and Leakage Policy v1 (Protocol-Hardening Draft)

Status: **DRAFT / REQUIRED BEFORE DATA FREEZE**

## Classification

| Class | Description | Allowed use |
|---|---|---|
| H-PILOT | Week1–5 historical artifacts and observations | pilot context and audit only |
| C-TRAIN | confirmatory-phase development data | development only |
| C-DEV | confirmatory validation data | protocol-approved tuning only |
| C-HELDOUT | confirmatory held-out data and labels | locked evaluation only |
| EXT-BASELINE | externally sourced baseline artifacts | comparison subject to license/provenance |

The canonical phase labels are:

| Level | Meaning | Rule |
|---|---|---|
| Level 0 | historical pilot | Week1–5 only; hypothesis generation, debugging, sanity checks, visualization, and regression testing; never confirmatory tuning or claims |
| Level 1 | development | implementation debugging, attack development, calibration, threshold setting, and dry runs only |
| Level 2 | confirmatory | fresh, outcome-uninspected, untuned data opened only after protocol freeze |

## Rules

1. H-PILOT must never be merged into the confirmatory population without an explicitly approved new protocol.
2. C-HELDOUT labels, identifiers, and derived scores must not enter tuning, prompt selection, threshold selection, or model selection.
3. Every derived artifact records source class, transformation, code version, and operator/date.
4. Any suspected leakage pauses the run and creates an incident record; it is not silently repaired.
5. Access to held-out material is least-privilege and logged.

## Level 2 fail-closed procedure

The custodian, permitted operators, and point at which ground truth becomes
visible are `TBD_BEFORE_AUTHORIZATION`. Before that point only identifiers and
authorized inputs may be accessed. Accidental leakage includes any label,
identifier, score, visualization, aggregate, or failure outcome reaching
model/threshold/attack selection. A suspected leak pauses the run, preserves
the evidence, opens an incident record, and invalidates the affected
confirmatory set unless an independently approved replacement protocol exists.
No replacement, deletion, retry, or fallback parent is allowed silently.
