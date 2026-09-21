# W7 protocol consistency audit v2

Audit date: `2026-09-21`
Mainline: `W7_PILOT_PROTOCOL_V1.md` at `ec4bf9f`
Preparation source: `w7_preparation/W7_PILOT_PROTOCOL_DRAFT_V1.md` at
`35e0c6e`
Scope: semantic comparison only; no inference, metric, bootstrap, or Level-2
access.

The comparison found no scientific conflict. The concise mainline protocol
and the preparation draft resolve to the same four conditions, two Whether
definitions, common/native Where handling, fail-closed failure policy, fixed
FPR rule, paired-source/bootstrap plan, seed `20260914`, two-sided percentile
95% CI, and Gate 1 definition. The preparation branch is more explicit for
case identity and resampling; the inherited confirmatory design is more
explicit for the fixed mechanism grid and aggregation provenance. These are
precision additions, not changes to populations, estimands, or outcomes.

| Field | Result |
|---|---|
| Whether-A / Whether-B | `SEMANTICALLY_EQUIVALENT` |
| Where | `PREPARATION_MORE_EXPLICIT` |
| Conditions | `SEMANTICALLY_EQUIVALENT` |
| Identity/source binding | `PREPARATION_MORE_EXPLICIT` |
| Mechanism | `MAINLINE_MORE_EXPLICIT` |
| Codec | `SEMANTICALLY_EQUIVALENT` |
| Resampling | `PREPARATION_MORE_EXPLICIT` |
| Failure | `SEMANTICALLY_EQUIVALENT` |
| Metrics / fixed FPR | `SEMANTICALLY_EQUIVALENT` |
| Aggregation | `MAINLINE_MORE_EXPLICIT` |
| Bootstrap / seed / CI | `SEMANTICALLY_EQUIVALENT` |
| Gate 1 | `SEMANTICALLY_EQUIVALENT` |

The preparation draft's `W6_GATE = BLOCKED` text is a stale branch snapshot,
not a conflict in the Gate 1 definition. It is not carried into reconciled
state. `RESAMPLING_PROTOCOL_INCOMPLETE = NO`.

```text
MAINLINE_SIDE_PROTOCOL_CONSISTENCY = PASS
PROTOCOL_CONFLICTS = 0
W7_PROTOCOL_FROZEN = YES (mainline frozen document)
W7_FORMAL_PILOT_AUTHORIZED = NO
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
```
