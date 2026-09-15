# W7 Execution Namespace Plan v1

Status: `FROZEN PRE-RUN PLAN / FORMAL PILOT NOT AUTHORIZED`  
Audit date: `2026-09-15`

This plan defines a future append-only namespace. It does not create a run or
permit scientific inference.

## Root and ownership

```text
W7_ROOT = results/topconf/w7_pilot/
ONE_INVOCATION = one model x one dataset x one condition x one owner
OWNER_REGISTRY = manifests/w7_owner_registry_v1.json
RAW_POLICY = append-only; never overwrite or share raw files
CONFIRMATORY_NAMESPACE = results/topconf_level2_rq1_v1/ (not used by W7)
V3_CONFIRMATORY_OUTCOMES_ACCESSED = NO
```

## Required per-run fields

Every invocation must carry unique values for:

```text
run_id, invocation_id, owner_id, model_id, model_commit, checkpoint_id,
dataset_id, dataset_version, dataset_manifest_sha256, case_manifest_sha256,
condition_id, transform_id, seed, runtime_environment_id, raw_output_path,
attempt_ledger_path, failure_ledger_path, evaluator_version
```

## Planned layout

```text
results/topconf/w7_pilot/
  manifests/
    w7_owner_registry_v1.json
    w7_case_manifest_<dataset_id>_<version>.jsonl
  raw/<model_id>/<dataset_id>/<condition_id>/<invocation_id>/raw.jsonl
  attempts/<model_id>/<dataset_id>/<condition_id>/<invocation_id>.jsonl
  failures/<model_id>/<dataset_id>/<condition_id>/<invocation_id>.jsonl
  eval/<model_id>/<dataset_id>/<condition_id>/<invocation_id>/canonical.jsonl
  summaries/<invocation_id>.json
```

The model-facing input contains only authorized audio identity, opaque case
ID, duration and condition metadata. Ground-truth files are held under a
separate evaluation-only binding and are joined only after raw inference is
terminal. No model process may read GT, label, mechanism or failure outcome.

## Conditions and stop rules

Only `clean`, `mechanism_shift`, `codec`, and `resampling` may be used by W7.
Adaptive attack, query search, result-guided retry, and confirmatory V3 access
are prohibited. Every planned unit receives exactly one terminal state; invalid
or failed rows are retained and excluded only by the frozen fail-closed rule.
