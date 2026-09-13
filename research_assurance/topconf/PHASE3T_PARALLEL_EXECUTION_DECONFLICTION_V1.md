# Phase3T Parallel Execution Deconfliction Record V1

This is an append-only research-assurance record. It documents an execution
ownership correction and does not contain scientific outcomes or score-based
comparisons.

## Immediate correction report

```text
AUTHORIZATION_ID=P3T-2026-09-13-01
DETECTED_AT=2026-09-13T21:32:00.9206761+08:00 Asia/Shanghai

MAINLINE_MRM_INVOCATION_STARTED=YES
MAINLINE_MRM_INVOCATION=experiments/topconf_phase3t/run_multireso.py --manifest results/topconf_phase3t/case_manifest.tsv --output-dir results/topconf_phase3t/multireso
MAINLINE_MRM_NAMESPACE=results/topconf_phase3t/multireso
MAINLINE_MRM_CASES_COMPLETED=7810
MAINLINE_MRM_TERMINATION=TERMINATED_EXECUTION_DECONFLICTION
MAINLINE_MRM_FORMAL_PHASE3T_USE=NO

WORKER_MRM_INVOCATION_STARTED=YES
WORKER_MRM_INVOCATION=PHASE3T_MRM_FULL_E1_001
WORKER_MRM_BRANCH=topconf-phase3t-multireso-worker
WORKER_MRM_COMMIT=3c749ceeb0e079874091a72d37dc546794540a52
WORKER_MRM_NAMESPACE=results/topconf_phase3t/multireso_worker_01
WORKER_MRM_CASES_COMPLETED=7880
WORKER_MRM_STATUS=PARTIAL_AND_SCHEMA_INVALID_FOR_PHASE3T

MULTIRESO_EXECUTION_OWNER=PARALLEL_WORKER
DUPLICATE_EXECUTION_STOPPED=YES
SCIENTIFIC_OUTCOMES_USED_FOR_OWNER_DECISION=NO
CFPRF_MAINLINE_STATUS=CONTINUE
PHASE3T_CONTINUES=YES
```

## Reason for the duplicate invocation

The controlled Phase3T authorization was operationalized in two execution
contexts before the ownership boundary was made explicit: the mainline
worktree started a full MultiReso E1 invocation while the designated parallel
worker was also running. This is an execution-control conflict, not a
scientific decision or a result comparison.

The mainline process and the old worker process were stopped after the
conflict was detected. No model score, metric, ranking, threshold, case
selection, or other scientific outcome was inspected for ownership selection.

## Ownership and artifact policy

The corrected ownership is:

```text
MAINLINE_OWNER=CFPRF full E1 inference + controller + worker ingestion + unified evaluator + Level-1 diagnostics + closure
PARALLEL_WORKER_OWNER=MultiResoModel-Simple full E1 inference only
MULTIRESO_EXECUTION_OWNER=PARALLEL_WORKER
OWNER_DECISION_BASIS=compute de-duplication, completed-count/integrity/provenance checks, and authorization compliance only
OWNER_DECISION_SCORES_OR_OUTCOMES=NOT_USED
```

Both partial namespaces are preserved in place. The mainline namespace is
superseded as a duplicate execution and is not to be resumed, reused, or
treated as formal Phase3T scientific output. The worker namespace is also not
yet a formal output: its current raw schema preserves six temporal scales but
does not preserve the authorized utterance-level native output. It therefore
requires a corrected, separately identified worker invocation and a complete
handoff before ingestion.

```text
MAINLINE_PARTIAL_RAW_SHA256=2279A5A6144D917FBC9D03201FF42A7A693AB0B3B64B0E0D74894A0DE4F0ECE8
MAINLINE_PARTIAL_ATTEMPTS_SHA256=40514808429D4A22EA047764BF5C2ED3CC537E58EF77E90822972CDAF015CB06
WORKER_OLD_PARTIAL_RAW_SHA256=B263934794B011A6271CDD1F11C1659E74906AC1CB0A53926E78D8141708938C
WORKER_OLD_PARTIAL_LEDGER_SHA256=22202D926366CCC5B2D21F1C211F65C5540219062588C453DD9A37DF8B6303E3
ARTIFACT_DELETION=NO
```

## Required continuation

The mainline continues CFPRF only. The parallel worker may produce a new
MultiReso invocation only under the frozen authorization, with a new namespace
and corrected raw-output schema that includes all six temporal scales and the
native utterance output. The mainline must wait for
`PHASE3T_MULTIRRESO_WORKER_HANDOFF_V1.md`, then perform read-only provenance,
manifest, hash, completeness, failure-ledger, and schema checks before
ingesting the existing worker output. A passing handoff must not trigger a
mainline MultiReso rerun.

No metrics, evaluator output, result-based case exclusion, scale selection, or
other scientific outcome is authorized by this record. Phase3T remains active
under the original authorization and this ownership amendment.
