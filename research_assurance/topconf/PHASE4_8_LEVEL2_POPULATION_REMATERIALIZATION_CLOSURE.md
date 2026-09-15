# Phase 4.8 Level-2 population rematerialization closure

```text
PHASE = PHASE4_8_PROSPECTIVE_LEVEL2_POPULATION_REMATERIALIZATION
DATE = 2026-09-15
PHASE4_8_STATUS = BLOCKED
PHASE4_8_CLOSURE = BLOCKED_INSUFFICIENT_CLEAN_RESERVE
FINAL_AUTHORIZATION_DECISION = NO_GO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```

## Closure decision

The single authorized prospective remediation attempt was performed from the
frozen V2 population and frozen Phase4.7 historical evidence. It stopped before
partial activation because the seven affected primary sources are all in
`SOURCE_POOL_A_AISHELL3`, while the 20 predeclared Pool A reserve records are
all from the prohibited speaker `AISHELL3_SSB0005`. The clean same-pool reserve
capacity is therefore zero for seven required replacements.

Cross-pool use of the 20 clean Pool B reserve records would change the frozen
two-pool allocation and is not permitted. No new candidate scan, source
re-ranking, listening choice, score choice, or second replacement cycle was
performed.

## Frozen V2 and contamination disposition

```text
V2_STATUS = REJECTED_FOR_CONFIRMATORY_EXECUTION
V2_REASON = VERIFIED_FRESHNESS_CONTAMINATION
V2_POPULATION_SHA256 = ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
V2_PRIMARY_SOURCES = 400
V2_SPEAKERS = 120
V2_CASES = 1600
V2_RESERVES = 40
V2_CHANGED = NO

VERIFIED_DIRECT_OVERLAP_SOURCES = 5
PROHIBITED_SPEAKERS = 2
EXCLUDED_PRIMARY_SOURCES = 7
EXCLUDED_CASES = 28
```

The two machine-readable artifacts are
`LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json` and
`LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json`. The ledger has seven complete
old-membership rows, zero activated reserves, and no replacement population.

## Reserve and eligibility result

```text
RESERVE_RULE_PREEXISTING = NO_FOR_THIS_TRIGGER_AND_ORDER
RESERVE_RULE_AMENDMENT_REQUIRED = YES
RESERVE_ACTIVATION_RULE = LEVEL2_RESERVE_ACTIVATION_RULE_V1
REQUIRED_REPLACEMENTS = 7
POOL_A_RESERVES = 20
POOL_A_CLEAN_RESERVES = 0
POOL_B_CLEAN_RESERVES = 20
ACTIVATED_RESERVES = 0
CROSS_POOL_SUBSTITUTION = FORBIDDEN
```

The population validator independently returns PASS for the frozen V2 parent.
The Phase4.8 rematerialization validator returns the terminal status
`BLOCKED_INSUFFICIENT_CLEAN_RESERVE`; it does not interpret the blocker as a
passing V3.

## No downstream scientific artifacts

Because a clean same-pool replacement set does not exist, the following are
intentionally not generated:

```text
LEVEL2_RQ1_POPULATION_MANIFEST_V3.json = NOT_CREATED
LEVEL2_FRESHNESS_MANIFEST_V4.json = NOT_CREATED
LEVEL2_RQ1_INFERENCE_MANIFEST_V2.json = NOT_CREATED
LEVEL2_RQ1_EVALUATION_MANIFEST_V2.json = NOT_CREATED
```

No CFPRF, MultiReso, or AASIST inference was run. No scientific score,
localization metric, LD@DR95, RQ1/RQ2/RQ3 outcome, or result-based design
change was accessed or created.

## Tests and governance

The fail-closed test suite covers retained contamination, prohibited speakers,
same-lineage/new-case identity, non-reserve replacement, reserve-ordering
violation, source/speaker/case count drift, pool allocation, pair integrity,
and GT leakage. The synthetic governance pipeline remains required to pass.

This is a terminal Phase4.8 blocker. It must not be followed by repeated
replacement-and-audit cycles. Any future attempt requires a separately reviewed
prospective amendment that supplies a clean same-pool candidate universe.
