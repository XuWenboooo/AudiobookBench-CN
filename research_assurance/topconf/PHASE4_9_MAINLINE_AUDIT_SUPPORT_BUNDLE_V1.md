# Phase 4.9 Mainline Audit Support Bundle v1

Date: 2026-09-15  
Mainline branch: `topconf-dl-robustness`  
Mainline HEAD: `ad44f6b29db1930e039c57f8b5412854e8349e3f`  
Remote-tracking HEAD at bundle preparation: `110e2b91c04625898b955c0d0dfcfccfe04515cb`  
Independent audit worktree: `AudiobookBench-CN-topconf-phase4-9-freshness-audit`  
Independent audit branch: `topconf-phase4-9-freshness-audit`  
Independent audit status at preparation: active; no verdict yet

## Frozen mainline state

```text
V3_POPULATION_MODIFIED = NO
NEW_CORPUS_SEARCH = NO
NEW_POOL_A_SELECTION = NO
LEVEL2_MODEL_INFERENCE = NO
SCIENTIFIC_METRICS_COMPUTED = 0
LD_DR95_COMPUTED = NO
RQ1_STARTED = NO
RQ2_STARTED = NO
RQ3_STARTED = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
PRODUCTION_VALIDATOR_MODIFIED = NO
READY_FOR_INDEPENDENT_AUDIT_RECONCILIATION = YES
```

The mainline treats `LEVEL2_RQ1_POPULATION_MANIFEST_V3.json` as
`AUDIT-FROZEN`. No V4/V5 population is materialized, no candidate corpus is
searched, and the independent audit branch is not modified, merged, or
cherry-picked.

## Required evidence index

### Protocol and design

- `research_assurance/topconf/PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`
- `research_assurance/topconf/TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`
- `research_assurance/topconf/PHASE4_HUMAN_RECONCILIATION_AND_DESIGN_FREEZE_CLOSURE.md`
- `research_assurance/topconf/PHASE4_RECONCILIATION_MATRIX_V1.md`
- `research_assurance/topconf/PHASE4_RECONCILIATION_LEDGER_V1.md`
- `research_assurance/topconf/PHASE4_OUTCOME_FIREWALL_V1.md`
- `research_assurance/topconf/RQ1_CONFIRMATORY_EXECUTION_AUTHORIZATION_V1.md`

### Phase closures

- `research_assurance/topconf/PHASE4_5_LEVEL2_POPULATION_AND_FRESHNESS_CLOSURE.md`
- `research_assurance/topconf/PHASE4_6_SOURCE_POOL_RECOVERY_CLOSURE.md`
- `research_assurance/topconf/PHASE4_7_HISTORICAL_EXCLUSION_AND_FRESHNESS_CLOSURE.md`
- `research_assurance/topconf/PHASE4_8_LEVEL2_POPULATION_REMATERIALIZATION_CLOSURE.md`
- `research_assurance/topconf/PHASE4_9_FRESH_POOL_A_REPLACEMENT_CLOSURE.md`

### Population and freshness

- `research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V2.json` — preserved rejected V2
- `research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V3.json` — frozen structural V3
- `research_assurance/topconf/LEVEL2_RQ1_INFERENCE_MANIFEST_V3.json` — model-facing, no outcomes
- `research_assurance/topconf/LEVEL2_RQ1_EVALUATION_MANIFEST_V3.json` — private GT view, no predictions
- `research_assurance/topconf/LEVEL2_FRESHNESS_MANIFEST_V1.json`
- `research_assurance/topconf/LEVEL2_FRESHNESS_MANIFEST_V2.json`
- `research_assurance/topconf/LEVEL2_FRESHNESS_MANIFEST_V3.json` — preserved Phase 4.7 result
- `research_assurance/topconf/LEVEL2_FRESHNESS_MANIFEST_V4.json` — one frozen V4 audit, insufficient
- `research_assurance/topconf/LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json`
- `research_assurance/topconf/LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json`

### Historical exclusion universes

- `research_assurance/topconf/HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json`
- `research_assurance/topconf/HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json`
- `research_assurance/topconf/HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json`
- `research_assurance/topconf/HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json`
- `research_assurance/topconf/HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json`
- `research_assurance/topconf/HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json`
- `research_assurance/topconf/PHASE4_7_HISTORICAL_FRESHNESS_PROOF_V1.md`

### Corpus provenance and independence

- `research_assurance/topconf/LEVEL2_NEW_POOL_A_SELECTION_RECORD_V1.md`
- `research_assurance/topconf/LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json`
- `research_assurance/topconf/LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json`
- `research_assurance/topconf/AISHELL1_PROJECT_ENTRY_PROOF_V1.json`
- `research_assurance/topconf/AISHELL1_SOURCE_POOL_FEASIBILITY_V1.json`
- `research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V3.json`
- `research_assurance/topconf/PHASE4_9_ALIMEETING_PROVENANCE_BUNDLE_V1.json`
- `research_assurance/topconf/PHASE4_9_AISHELL1_PROVENANCE_BUNDLE_V1.json`

### Validators and relevant tests

- `src/audiobookbench/topconf/level2/materialization.py`
- `tools/topconf/validate_level2_freshness.py`
- `tools/topconf/validate_level2_population.py`
- `tools/topconf/audit_alimeeting_test.py`
- `tools/topconf/materialize_level2_population_v3_alimeeting.py` — provenance only; not rerun in this hold
- `tests/topconf/test_level2_freshness_v3.py`
- `tests/topconf/test_level2_materialization.py`
- `tests/topconf/test_phase4_8_rematerialization.py`
- `tests/topconf/test_phase4_9_closure.py`

### Audit interpretation and handoff

- `research_assurance/topconf/PHASE4_9_FROZEN_FRESHNESS_REQUIREMENT_EXTRACT_V1.md`
- `research_assurance/topconf/PHASE4_9_FRESHNESS_VALIDATOR_DECISION_TRACE_V1.md`
- `research_assurance/topconf/PHASE4_9_INDEPENDENT_AUDIT_HANDOFF_V1.md`
- `research_assurance/topconf/PHASE4_9_AUDIT_SUPPORT_SHA256SUMS_V1.txt`

## Historical stage status snapshot

This table is copied from `HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json`; it does
not upgrade or downgrade the recorded statuses.

| Stage | Case | Source | Lineage |
|---|---|---|---|
| Week1 pilot | PARTIAL | PARTIAL | PARTIAL |
| Week2 pilot | COMPLETE | PARTIAL | PARTIAL |
| Week3 pilot | COMPLETE | PARTIAL | PARTIAL |
| Week4 pilot | PARTIAL | PARTIAL | PARTIAL |
| Week5 qualification | PARTIAL | UNKNOWN | UNKNOWN |
| Phase3 / 3R / 3S / 3U / 3V | UNKNOWN | UNKNOWN | UNKNOWN |
| Phase3T PartialEdit E1 | COMPLETE | PARTIAL | PARTIAL |
| Whether-B capability smoke | COMPLETE_EXCLUSION_EMPTY | COMPLETE_EXCLUSION_EMPTY | COMPLETE_EXCLUSION_EMPTY |
| Metric development | UNKNOWN | UNKNOWN | UNKNOWN |
| Threshold calibration | UNKNOWN | UNKNOWN | UNKNOWN |
| Model selection | UNKNOWN | UNKNOWN | UNKNOWN |
| Adapter debugging | UNKNOWN | UNKNOWN | UNKNOWN |
| Manual inspection | UNKNOWN | UNKNOWN | UNKNOWN |
| Pilot visualization | UNKNOWN | UNKNOWN | UNKNOWN |
| Scientific selection | UNKNOWN | UNKNOWN | UNKNOWN |

Universe-level status remains: case `PARTIAL_RECONSTRUCTION_WITH_PHASE3T_CASE_COMPLETENESS`,
source `PARTIAL_RECONSTRUCTION_WITH_DIRECT_HASHED_SOURCES`, speaker
`PARTIAL_RECONSTRUCTION`, and lineage
`PARTIAL_RECONSTRUCTION_WITH_SOURCE_AUDIO_HASH_LINEAGE`.

## Questions reserved for the independent auditor

The mainline records, but does not answer, the distinction between:

1. whether the historical record is globally complete; and
2. whether AliMeeting/AISHELL-1 freshness can be independently proven despite
   unrelated historical incompleteness.

The auditor must return exactly one of:
`TRUE_EVIDENCE_GAP`, `VALIDATOR_OVERCONSTRAINT`,
`FROZEN_POLICY_AMBIGUITY`, or `ADDITIONAL_NON_FRESHNESS_BLOCKER`.

