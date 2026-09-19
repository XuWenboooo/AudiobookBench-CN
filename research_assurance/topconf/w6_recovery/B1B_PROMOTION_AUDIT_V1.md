# B1b promotion audit v1

Audit date: `2026-09-19`

## Identity and scope

B1b is the repository-local historical ECAPA sequence-local baseline defined
by the frozen earlier protocol. Its pretrained ECAPA artifact and historical
CPU runtime are already bound by the earlier project evidence. This audit does
not rerun the historical experiment, inspect outcome values, or train a new
checkpoint.

## Promotion gates

| Gate | Evidence | Status |
|---|---|---|
| external/public source identity | no current external repository/checkpoint identity for the B1b wrapper | FAIL |
| arbitrary external-distribution audio adapter | no frozen PartialSpoof/PartialEdit adapter for B1b's internal sequence-local construction | FAIL |
| temporal output contract | historical fixed-window/window-frame anomaly score only | INCOMPLETE |
| strict checkpoint identity | project-local historical ECAPA artifact, not a new external localizer checkpoint | HISTORICAL_ONLY |
| no replacement training | no new training requested or run | PASS |
| outcome-blind promotion | no score/metric used for this decision | PASS |

```text
B1B_PROMOTION_ALLOWED = NO
B1B_NEW_TRAINING_REQUIRED = YES_IF_PROMOTED
B1B_ADAPTER = NOT_FROZEN_FOR_EXTERNAL_DISTRIBUTIONS
B1B_PREFLIGHT = HISTORICAL_ONLY
B1B_W7_ELIGIBLE = NO
```

B1b therefore remains a historical control and is not counted as a fourth
localization paradigm. Promoting it would require a new external-data adapter
and a new authorization decision, not merely relabeling the historical
artifact.
