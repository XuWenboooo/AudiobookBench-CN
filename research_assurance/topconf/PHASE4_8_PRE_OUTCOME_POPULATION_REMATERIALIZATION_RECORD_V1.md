# Phase 4.8 pre-outcome population rematerialization record

**Date:** 2026-09-15
**Status:** `BLOCKED_INSUFFICIENT_CLEAN_RESERVE`
**Amendment type:** prospective governance rule for one contamination-remediation attempt

## Trigger and pre-outcome firewall

```text
TRIGGER = FRESHNESS_CONTAMINATION
REAL_LEVEL2_OUTCOMES_ACCESSED_BEFORE_AMENDMENT = NO
MODEL_INFERENCE_RUNS_BEFORE_AMENDMENT = 0
SCIENTIFIC_RESULTS_USED_FOR_REPLACEMENT = NO
RESULT_BASED_DESIGN_CHANGES = 0
```

The trigger is the verified Phase4.7 historical freshness contamination only.
No detector score, localizer score, difficulty, expected hypothesis direction,
quality preference, or model behavior entered the decision.

## Parent population disposition

The parent is the immutable Phase4.6 V2 metadata-only candidate:

```text
LEVEL2_POPULATION_V2_STATUS = REJECTED_FOR_CONFIRMATORY_EXECUTION
REASON = VERIFIED_FRESHNESS_CONTAMINATION
PARENT_POPULATION = LEVEL2_RQ1_POPULATION_MANIFEST_V2.json
PARENT_POPULATION_SHA256 = ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
V2_PRIMARY_SOURCES = 400
V2_SPEAKERS = 120
V2_CASES = 1600
V2_RESERVE_RECORDS = 40
V2_MODIFIED = NO
```

V2 remains a valid historical audit artifact and is not overwritten, edited,
partially deleted, or defended as confirmatory data.

## Frozen design boundary

The following remain inherited without change: 400 primary sources, 120
speakers, two independent 200-source pools, the predeclared 40-record reserve,
four balanced mechanisms, 1,600 cases, paired/counterfactual structure,
transformations, Whether-A/Whether-B policy, metrics, LD@DR95, gap criterion,
sample-size rationale, statistical unit, bootstrap, multiplicity, threshold
policy, failure accounting, retry policy, and stopping rule.

Only the contaminated source/speaker membership was eligible for consideration.

## Contamination exclusion

Phase4.7 directly verified five AISHELL-3 audio/source/lineage overlaps. Under
the frozen speaker policy, all V2 membership of the two implicated speakers is
excluded:

```text
DIRECT_VERIFIED_OVERLAP_SOURCES = 5
PROHIBITED_SPEAKERS = 2
EXCLUDED_PRIMARY_SOURCES = 7
EXCLUDED_CASES = 28
EXCLUDED_POOL = SOURCE_POOL_A_AISHELL3
```

The complete machine-readable set is
`LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json`. It records the five
historical evidence matches, both prohibited speakers, all seven affected V2
sources, all 28 derived cases, source hashes, parent lineage IDs, and the
reason for exclusion.

## Reserve activation audit

The pre-existing protocol defined reserve quantity and the `SOURCE_INVALID`
purpose, but not a complete activation order for this freshness-contamination
trigger. `LEVEL2_RESERVE_ACTIVATION_RULE_V1.md` therefore records one
outcome-independent canonical order and explicitly forbids cross-pool
substitution, manual choice, score choice, quality choice, and a second cycle.

The frozen reserve audit found:

```text
REQUIRED_SAME_POOL_REPLACEMENTS = 7
SOURCE_POOL_A_RESERVE_RECORDS = 20
SOURCE_POOL_A_CLEAN_RESERVE_RECORDS = 0
SOURCE_POOL_B_CLEAN_RESERVE_RECORDS = 20
CROSS_POOL_SUBSTITUTION = FORBIDDEN
ACTIVATED_RESERVES = 0
```

All 20 Pool A reserve records are from the prohibited speaker
`AISHELL3_SSB0005`. Pool B records cannot replace Pool A records without
changing the frozen independent-pool allocation.

## Terminal decision

The replacement ledger contains one row for each of the seven excluded primary
sources, with complete old case membership and null replacement fields. Since
the clean same-pool reserve is insufficient, no partial replacement is
permitted. No V3 population or V4 freshness manifest is created in this
attempt.

```text
PHASE4_8_CLOSURE = BLOCKED_INSUFFICIENT_CLEAN_RESERVE
LEVEL2_RQ1_POPULATION_MANIFEST_V3 = NOT_CREATED
LEVEL2_FRESHNESS_MANIFEST_V4 = NOT_CREATED
INFERENCE_MANIFEST_V2 = NOT_CREATED
EVALUATION_MANIFEST_V2 = NOT_CREATED
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
```
