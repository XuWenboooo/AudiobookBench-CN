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

## Corrected worker continuation

At 2026-09-13T21:40:45+08:00, the worker owner started a new, separately
identified invocation after the old partial namespace had been stopped and
preserved. The serialization fix adds the authorized native utterance output,
uses the canonical E1 case identifiers/order, adds a terminal attempt ledger,
and uses the memory-safe strict checkpoint loader. Its technical preflight
passed without accessing GT or computing scientific metrics.

```text
CORRECTED_WORKER_INVOCATION_ID=PHASE3T_MRM_FULL_E1_002
CORRECTED_WORKER_NAMESPACE=results/topconf_phase3t/multireso_worker_02
CORRECTED_WORKER_COMMIT=c7f0283
CORRECTED_WORKER_PREFLIGHT=PASS
CORRECTED_WORKER_SCIENTIFIC_METRICS_COMPUTED=0
CORRECTED_WORKER_GT_ACCESSED=NO
MAINLINE_MRM_FULL_INFERENCE_AFTER_STOP=NO
```

## Worker resume accounting

The corrected worker process exited after writing 21,588 raw terminal records
(21,549 valid and 39 audio-load failures). A read-only audit found exactly one
raw record without its terminal ledger line; that line was appended to the
ledger using the already-written failure record, without changing the raw
output. The 39 affected files were subsequently readable, so the event is
classified as transient I/O and retained in the failure accounting.

The authorized worker resumed in the same `multireso_worker_02` namespace.
Resume skips every case already represented by the reconciled terminal ledger;
it does not rerun or overwrite completed raw records. This continuation is a
bounded execution recovery, not a new scientific invocation or an ownership
change.

```text
WORKER_E1_002_INITIAL_RAW_TERMINAL=21588
WORKER_E1_002_INITIAL_VALID=21549
WORKER_E1_002_INITIAL_AUDIO_LOAD_FAILURE=39
WORKER_E1_002_ORPHAN_RAW_LEDGER_LINES_REPAIRED=1
WORKER_E1_002_RESUME_NAMESPACE_REUSED=YES
WORKER_E1_002_COMPLETED_CASES_RERUN=0
WORKER_E1_002_SCIENTIFIC_OUTCOMES_INSPECTED=NO
```

## Final MultiReso owner selection

Read-only audit found a second parallel-worker worktree created for
integrity-controlled continuation:

```text
WORKER_R2_WORKTREE=F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2
WORKER_R2_BRANCH=topconf-phase3t-multireso-worker-r2
WORKER_R2_COMMIT=a210287b0473b628b8ba4b85f9658fbc10f0d832
WORKER_R2_NAMESPACE=results/topconf_phase3t/multireso_worker_02
WORKER_R2_OWNER_LOCK=phase3t_namespace_owner_v1; exclusive writer
WORKER_R2_RAW_TERMINAL_AT_AUDIT=8047
WORKER_R2_LEDGER_TERMINAL_AT_AUDIT=8047
WORKER_R2_RAW_DUPLICATES_AT_AUDIT=0
WORKER_R2_LEDGER_DUPLICATES_AT_AUDIT=0
WORKER_R2_RAW_LEDGER_SET_MISMATCH_AT_AUDIT=0
WORKER_R2_SCHEMA=six temporal scales plus native utterance output
WORKER_R2_GT_ACCESSED=NO
WORKER_R2_SCIENTIFIC_METRICS_COMPUTED=0
```

The final MultiReso owner is the r2 parallel worker. This decision uses only
completed-count, exclusive-writer integrity, schema compliance, and frozen
authorization provenance. No score, metric, ranking, threshold, or other
scientific outcome was inspected. The original `multireso_worker_02`
namespace in the first worker worktree remains preserved as a superseded
partial execution artifact and must not be ingested or resumed as a second
writer. The r2 worker must finish and provide
`PHASE3T_MULTIRRESO_WORKER_HANDOFF_V1.md` before mainline ingestion.

```text
FINAL_MULTIRESO_EXECUTION_OWNER=PARALLEL_WORKER_R2
FINAL_MULTIRESO_OWNER_DECISION_BASIS=COUNT_INTEGRITY_AUTHORIZATION_ONLY
SCIENTIFIC_OUTCOMES_USED_FOR_FINAL_OWNER_DECISION=NO
SECOND_ACTIVE_MULTIRESO_WRITER=NO
```

## Final worker handoff and mainline read-only verification

At `2026-09-14T01:05:10+08:00`, the selected r2 worker had completed the
authorized full E1 population and released its namespace lock. Mainline read
the handoff file from the worker worktree and verified its status and the
reported output hashes. The handoff itself is committed and pushed on the r2
branch.

```text
HANDOFF_FILE=F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/PHASE3T_MULTIRRESO_WORKER_HANDOFF_V1.md
HANDOFF_FILE_SHA256=2005CE7AB93347FD15A0A5D556AD9C28A457E81F20A50FA7F599214F7C46B60A
HANDOFF_STATUS=READY_FOR_MAINLINE_READ_ONLY_INGESTION
WORKER_R2_FINAL_EXECUTION_COMMIT=418593d2c9f0c90f7c663fa001fa15f8839bde7f
WORKER_R2_CURRENT_HEAD=ebad7eac879cd4ae14c7cbb14bf0900101720e0f
WORKER_R2_FINAL_NAMESPACE_STATUS=COMPLETE
WORKER_R2_PLANNED=42471
WORKER_R2_TERMINAL=42471
WORKER_R2_VALID=42438
WORKER_R2_FAILED=33
WORKER_R2_MISSING=0
WORKER_R2_FAILURE_CLASS=AUDIO_LOAD_FAILURE
WORKER_R2_SCALES=6/6
WORKER_R2_GT_ACCESSED=NO
WORKER_R2_SCIENTIFIC_METRICS_COMPUTED=0
WORKER_R2_RAW_SHA256=00E502AA418DC1279AE19F72E48E1617A4BCF56014307FE6E0BC666736E37925
WORKER_R2_CASE_LEDGER_SHA256=24FAE99EEE5BE1E3CDE8D912AE8EF4C12DF6423A7705599F4C7C26DA97EA5733
WORKER_R2_OUTPUT_MANIFEST_JSONL_SHA256=4A606CA23126AF50CDDF3ACA1AABA536BB03B96DDF4C962DA924080034F521AC
WORKER_R2_ATTEMPTS_SHA256=D1C66CCF73538ECD810F56ABDD29402D85A38CA5A22323D83EED17869FCA204E
WORKER_R2_RETRY_LEDGER_SHA256=87D9A2B86FBBCA61FFBCEC5788E3B205B0509D150F8A1D896EB0CF1EADC9F3AD
WORKER_R2_RUN_MANIFEST_SHA256=0EE148D1305675369D7B8772BD37A2C39E769A4C0CA8A9D335756A6DC6BB2333
WORKER_R2_T2_VALIDATION=PASS
WORKER_R2_T2_VALIDATION_SHA256=BC87402447FEFDEF7DF1360B76B5910C4BFEF9A2580D7AA24F142BC7B4899054
WORKER_R2_ATTEMPT_BACKFILL_REPORT_SHA256=ADAD92B6AE8B54D8C96C0D8EF2A84058D6FFFD38802374A6E6EED09211638B22
WORKER_R2_RUN_RUNTIME_SEC=4815.7775395
WORKER_R2_PEAK_VRAM_BYTES=2474151424
```

The raw, terminal case ledger, and output-manifest JSONL each contain 42,471
unique records with continuous official case indices and zero set mismatch.
The attempts history contains 42,482 append-only records, including seven
retained duplicate attempt-start keys from earlier infrastructure restarts;
all 42,471 terminal attempts are represented, and four attempt-2 records match
the four retry-ledger entries. The 33 audio-load attempt-start rows missing
from the worker's original append-only attempts file were backfilled without
changing raw or the terminal case ledger. The exact before/after attempts
hashes and case IDs are preserved in the backfill report.

Mainline does not use the worker's per-record `runtime_sec` fields because the
worker instrumentation started that timer immediately before terminal
serialization. The run-level manifest runtime is retained as the authoritative
execution runtime; this metadata defect does not alter native outputs,
completeness, failure accounting, or the authorized evaluation boundary.

The formal MultiReso owner is now locked to `PARALLEL_WORKER_R2`. The old
worker namespace and the terminated mainline MultiReso partial remain preserved
for provenance only. Mainline may ingest only the handoff namespace by
read-only verification; it must not rerun MultiReso or use any partial output.
