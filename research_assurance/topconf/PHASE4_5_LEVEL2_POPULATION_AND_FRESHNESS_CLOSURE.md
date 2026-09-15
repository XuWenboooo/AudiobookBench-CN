# Phase 4.5 Level-2 Population and Freshness Closure v1

Status: **BLOCKED — POPULATION MATERIALIZATION / FRESHNESS EVIDENCE INSUFFICIENT**  
Review date: **2026-09-15**  
Review base: `6e7a0957809472a8189514781414b47cc4f494f8`

## Decision

Phase 4.5 did not silently alter the frozen Phase4 design. A read-only audit of
the local resources found no materialized Level-2 case population that can
support the frozen two-pool, 400-source, 120-speaker design.

```text
PHASE3T_CLOSURE = PASS
PHASE4_CLOSURE = PASS
PHASE4_5_CLOSURE = BLOCKED_POPULATION_MATERIALIZATION
POPULATION_MATERIALIZATION = FAIL
LEVEL2_FRESHNESS = INSUFFICIENT_EVIDENCE
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
RESULT_BASED_DESIGN_CHANGES = 0
```

## Frozen target and observed resource boundary

```text
FROZEN_PRIMARY_SOURCES = 400
FROZEN_SPEAKERS = 120
FROZEN_INDEPENDENT_SOURCE_POOLS = 2
FROZEN_SOURCES_PER_POOL = 200
FROZEN_SPEAKERS_PER_POOL = 60
FROZEN_MECHANISMS_PER_SOURCE = 4
FROZEN_RESERVE_SOURCES = 40
FROZEN_DURATION_SEC = 8..30

AISHELL3_RAW_WAV_FILES = 88035
AISHELL3_RAW_SPEAKERS = 218
AISHELL3_ELIGIBLE_8_30_FILES = 532
AISHELL3_ELIGIBLE_8_30_SPEAKERS = 112
AISHELL3_TRAIN_TEST_SPEAKERS = 174 / 214
AISHELL3_TRAIN_ONLY_TEST_ONLY_SHARED = 4 / 44 / 170
```

The duration audit used the local RIFF PCM header metadata only. The resource
is a single AISHELL-3 corpus and is already part of the historical Week1–5
lineage. The local worktree contains no fresh Level-2 case manifest. The local
PartialEdit E1 audio is the excluded Phase3T Level-1 population, not a second
fresh source pool.

## Materialization and freshness artifacts

| Artifact | State | Meaning |
|---|---|---|
| `LEVEL2_RQ1_POPULATION_MANIFEST_V1.json` | blocked, `materialized=false` | explicit failed materialization attempt; no population claim |
| `LEVEL2_EXCLUSION_UNIVERSE_V1.json` | incomplete | hashes and known inventory are recorded; complete cross-dimensional historical identities are not available |
| `LEVEL2_FRESHNESS_MANIFEST_V1.json` | `INSUFFICIENT_EVIDENCE` | no case-level freshness claim |
| `LEVEL2_RQ1_INFERENCE_MANIFEST_V1.json` | not materialized | empty model-facing template; no cases |
| `LEVEL2_RQ1_EVALUATION_MANIFEST_V1.json` | not materialized | empty private-evaluation template; no GT |
| `RQ1_*_FAILURE_LEDGER_V1.json` | not started | templates only; no fake execution rows |

The exclusion universe records the exact available artifact hashes and marks
each missing identity projection as incomplete. The AASIST capability smoke is
explicitly represented with `source_ids=[]` because it used a deterministic
synthetic sinusoid and loaded no dataset source.

## Why authorization remains NO_GO

The missing evidence is not a model or metric issue. The current resources
fail the frozen cardinality/pool gate before any generation can be authorized:

1. only one local source corpus is available for this review;
2. only 112 corpus speakers have an 8–30 second source, below the frozen 120;
3. AISHELL-3 train/test speaker partitions share 170 speakers, so those
   partitions cannot be asserted as two independent speaker pools;
4. no case-level source/reference/generator/seed binding exists; and
5. the complete historical pilot, Phase3T, and selection-data exclusion
   universe is not materialized with all required lineage dimensions.

Creating 400 rows from the available corpus, reusing Phase3T E1, or treating
the example/template files as fresh metadata would be a protocol change or a
false freshness claim. None was done.

## Validator and test evidence

`tools/topconf/audit_level2_resource_capacity.py` reproduces the capacity
counts from read-only WAV headers. `src/audiobookbench/topconf/level2/materialization.py` provides fail-closed
checks for population cardinality, two-pool speaker allocation, case ordering,
mechanism balance, pair integrity, metadata/hash binding, seed uniqueness,
inference GT isolation, evaluation runner separation, and cross-dimensional
freshness. The new synthetic corruption tests cover duplicate/missing/extra
cases, speaker and mechanism imbalance, seed reuse, missing lineage, tampered
audio identity, prohibited lineage overlap, incomplete freshness evidence, and
GT leakage. They do not read audio or invoke a model.

```text
TESTS = 58 passed
MODEL_INFERENCE_RUNS = 0
SCIENTIFIC_SCORES = 0
```

## Re-open condition

Phase 4.5 may be reopened only after a separately supplied, rights-cleared
source inventory can satisfy the frozen two-pool cardinality and duration
requirements, and the full exclusion universe can be materialized with
case/source/speaker/session/utterance/reference/text/parent lineage hashes.
That future review must create a new population manifest and a new
authorization review; this blocked artifact is not an authorization.
