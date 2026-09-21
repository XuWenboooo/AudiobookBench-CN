# W7 protocol pre-execution correction audit v1

Audit date: `2026-09-21`  
Decision: `PASS`

The old frozen protocol is preserved unchanged at
`W7_PILOT_PROTOCOL_V1.md` with SHA-256
`0d386e3461afeaa5a2dce361a8d7ebca58f5816f111827322576297774a51d3c`.
It is superseded only because its Gate 1 text was omitted. The corrected
protocol is `W7_PILOT_PROTOCOL_V1_1.md` with SHA-256
`ad2c318085e66796f822134259e207c74a1a01a691adf7e1d77d4fb1242b1c80`.

## Pre-existing Gate 1 evidence

The criterion predates this correction and was present before any W7
scientific inference in:

- `w7_preparation/W7_PILOT_PROTOCOL_DRAFT_V1.md`, section 11;
- `TOPCONF_RESEARCH_PREREGISTRATION_V1.md`, which requires at least three
  distinct localization paradigms and two independent distributions;
- `W7_PROTOCOL_CONSISTENCY_AUDIT_V2.json/.md`, which records the same Gate 1
  definition as semantically equivalent;
- `W7_RECONCILIATION_FINAL_AUDIT_V2.md`, which records the same pre-outcome
  gate.

The restored exact criterion is:

```text
GAP_OBSERVED_IN >= 3 DISTINCT localization paradigms
AND
GAP_OBSERVED_IN >= 2 external distributions
```

## Semantic diff

| Field | Result |
|---|---|
| Gate 1 | PASS: restores pre-existing exact threshold text |
| Whether-A | UNCHANGED |
| Whether-B | UNCHANGED |
| Where | UNCHANGED |
| Models/localizers | UNCHANGED |
| External distributions | UNCHANGED |
| `clean` | UNCHANGED |
| `mechanism_shift` | UNCHANGED |
| `codec` | UNCHANGED |
| `resampling` | UNCHANGED |
| Metrics | UNCHANGED |
| Aggregation | UNCHANGED |
| Bootstrap/statistics | UNCHANGED |
| Failure policy | UNCHANGED |

`ONLY_SCIENTIFIC_TEXTUAL_CHANGE = explicit restoration of pre-existing Gate 1 threshold`.
No inference, prediction, metric, outcome, Level-2 access, or authorization
record update occurred. Refreeze state is `W7_PROTOCOL_FROZEN = YES` with
`W7_SCIENTIFIC_INFERENCES_AT_REFREEZE = 0`.
