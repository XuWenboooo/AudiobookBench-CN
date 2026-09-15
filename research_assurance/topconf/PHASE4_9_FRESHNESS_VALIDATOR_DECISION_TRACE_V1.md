# Phase 4.9 Freshness Validator Decision Trace v1

This is a logic trace of the existing production validator. The production
validator was not modified and the real V4 manifest was not rerun under an
alternative rule.

## Inputs

```text
population = LEVEL2_RQ1_POPULATION_MANIFEST_V3.json
population.materialized = true
population.status = MATERIALIZED
population.result_based_selection = false
freshness = LEVEL2_FRESHNESS_MANIFEST_V4.json
freshness.schema_version = topconf.level2.freshness.v3
freshness.freshness_verdict = INSUFFICIENT_EVIDENCE
historical universes supplied = four referenced JSON files
speaker_overlap_policy = ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT
```

The CLI path is `tools/topconf/validate_level2_freshness.py`. For a V3 schema
it resolves `universe_references`, loads the referenced files, and calls
`validate_level2_freshness` from
`src/audiobookbench/topconf/level2/materialization.py`. The V3 dispatch reaches
`validate_level2_freshness_v3`.

## Completeness fields

| Universe | Manifest status | Records | Evidence source present |
|---|---|---:|---|
| `CASE_EXCLUSION` | `PARTIAL` | 43,311 | yes |
| `SOURCE_EXCLUSION` | `PARTIAL` | 317 | yes |
| `SPEAKER_USAGE` | `PARTIAL` | 169 | yes |
| `LINEAGE_EXCLUSION` | `PARTIAL` | 317 | yes |

## Conditions evaluated

1. Population is materialized and has status `MATERIALIZED`: satisfied.
2. Freshness schema is `topconf.level2.freshness.v3`: satisfied.
3. Result-based selection is false: satisfied.
4. All four referenced universes are present and parseable: satisfied.
5. Each universe has a recognized completeness status and evidence source:
   satisfied; all four statuses are `PARTIAL`.
6. Corpus-isolation records are present with accepted statuses and evidence:
   satisfied for AliMeeting and retained AISHELL-1 post-freeze project-entry
   records.
7. Declared overlap counts equal recomputed counts: satisfied. All observed
   case, case-lineage, source, lineage, speaker, and prohibited-speaker counts
   are zero; unknown comparison counts are also zero.
8. The declared speaker policy permits historical speaker reuse only when the
   prohibited-speaker/lineage condition is disjoint: satisfied; prohibited
   speaker overlap is zero.

## Condition causing `INSUFFICIENT_EVIDENCE`

The production branch after the overlap checks is equivalent to:

```text
if prohibited_overlap:
    status = FAIL
elif unknown_total or any(completeness in {PARTIAL, UNKNOWN}):
    status = INSUFFICIENT_EVIDENCE
else:
    status = PASS
```

Here `prohibited_overlap = false`, `unknown_total = 0`, and
`any(completeness in {PARTIAL, UNKNOWN}) = true` because all four completeness
values are `PARTIAL`. Therefore the validator returns
`INSUFFICIENT_EVIDENCE`. The declared V4 verdict matches that result.

Exact implementation reference: `src/audiobookbench/topconf/level2/materialization.py`,
`validate_level2_freshness_v3`, especially the completeness loop and the
conditional following `unknown_total`.

## Mainline interpretation

This trace does not decide whether the branch implements the frozen policy
correctly. That is the independent auditor’s task. The mainline records:

```text
PRODUCTION_VALIDATOR_MODIFIED = NO
REAL_V4_ALTERNATIVE_RULE_RERUN = NO
V4_REPORTED_STATUS = INSUFFICIENT_EVIDENCE
V4_DECISION = STOP_AFTER_ONE_V3_AND_ONE_V4_AUDIT / NO_GO
```

