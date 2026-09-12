# Week4 DEV integrity reexecution 01 invalidation

Run: `week4_dev_integrity_reexecution_01`  
Namespace: `results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_01`

```text
RUN_STATUS = INVALIDATED_BY_EXECUTION_IMPLEMENTATION_INTEGRITY_DEFECT
RESUMABLE = NO
SCIENTIFIC_EVIDENCE_ADMISSIBLE = NO

REAL_DEV_OUTCOME_OBSERVED = YES
REAL_F5_CASES = 4
REAL_SCORE_VECTOR_EVIDENCE = PRESENT (123 retained sidecars)
VALIDATION_OBSERVED = NO
HELD_OUT_OBSERVED = NO
H4_OBSERVED = NO

DEFECT_1 = DUPLICATE_UNACCOUNTED_D0
DEFECT_2 = OBJECTIVE_UNDEFINED_MISCLASSIFIED
DEFECT_3 = METADATA_FINALIZATION
```

The namespace is permanently forensic-only.  Its `run_metadata.json`,
`accounting/f5_attempt_ledger.jsonl`, `accounting/candidate_ledger.jsonl`,
waveforms, sidecars, and selections must not be modified, deleted, resumed,
or copied into any future formal output namespace.

At invalidation, the retained key-file SHA-256 values are:

| Artifact | SHA-256 |
| --- | --- |
| `run_metadata.json` | `F35E31805869DC14F0AB6C380852F50C6B608E72A18677856AD3C227471F3622` |
| `accounting/f5_attempt_ledger.jsonl` | `98FD6C145AD32A536190D3476AFDD5FCFDAED266B28589516B008699BB652E96` |
| `accounting/candidate_ledger.jsonl` | `CAE1C58DE6CAEB67F5C7F5CD7062E110A3C3F394BD59E82A92058681C4C3E03B` |

The previous authorization used to start this run is consumed by the
invalidated partial DEV execution.  Its historical status is:

```text
CONSUMED_BY_INVALIDATED_PARTIAL_DEV_EXECUTION
```

It is neither unused nor superseded before scientific execution.

## Reexecution admissibility

The frozen preregistration, canonical config, 48-case population, execution
supplement, D0 asset manifest, F5 settings, seed rule, attack bounds,
objective formula, search rule, query budget, GT construction, and evaluator
were rechecked without modification.  The required correction is solely an
execution implementation repair.

```text
CLEAN_DEV_REEXECUTION_ADMISSIBLE = YES
REEXECUTION_CLASSIFICATION = INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL_AFTER_INVALID_IMPLEMENTATION
SCIENTIFIC_PROTOCOL_CHANGED_AFTER_DEV_OBSERVATION = NO
EXECUTION_IMPLEMENTATION_CHANGED_AFTER_DEV_OBSERVATION = YES
IMPLEMENTATION_CHANGE_CLASS = CORRECTIVE_IMPLEMENTATION_INTEGRITY_REPAIR
```
