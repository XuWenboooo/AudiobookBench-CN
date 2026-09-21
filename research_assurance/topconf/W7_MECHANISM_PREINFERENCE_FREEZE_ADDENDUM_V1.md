# W7 mechanism pre-inference freeze addendum v1

Status: `PRE_INFERENCE_SPECIFICATION_COMPLETION / INCOMPLETE_P4_FAIL_CLOSED`

This addendum was created before any W7 scientific inference. It records the human-authorized deterministic M1 assignment rule and seed rule, but it does not invent missing implementation or parameter values.

```text
W7_SCIENTIFIC_INFERENCES_AT_FREEZE = 0
LEVEL2_OUTCOMES_ACCESSED_AT_FREEZE = NO
FORMAL_OUTCOME_ABSENCE = PASS
PRE_INFERENCE_SPECIFICATION_COMPLETION = YES
ASSIGNMENT_SALT = W7_MECHANISM_ASSIGNMENT_V1
MECHANISM_CASE_MAP_COUNT = 106859
MECHANISM_MAP_DETERMINISM = PASS_GENERATOR_CANONICAL_BYTES
P4_COUNT = 35
MECHANISM_FREEZE = INCOMPLETE
W7_EXECUTION_AUTHORIZATION = NO
```

M1 maps each case to the lexicographically sorted eligible family list using the frozen SHA-256 rule. No pre-W7 evidence excludes a family, so all five families are eligible for every logical case. M2 uses fixed 16 kHz/seed/quality/failure policies but leaves the seven family-specific P4 fields unresolved for every family: implementation, version, parameter set, reference rule, target-span rule, codec path, and parameters. M3 validates identity, determinism, source/GT linkage, no timestamps/absolute paths, no outcomes, and no Level-2 access.

Because P4 remains nonzero, no complete executable config hash exists, no final map is claimed, and no four-localizer runner dry-run is authorized. A separate human decision is required for each P4 field class before a new re-authorization request.
