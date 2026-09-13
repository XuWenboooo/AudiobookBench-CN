# Phase3T MultiReso worker handoff V1

HANDOFF_STATUS = READY_FOR_MAINLINE_READ_ONLY_INGESTION
AUTHORIZATION_ID = P3T-2026-09-13-01
INVOCATION_ID = PHASE3T_MRM_FULL_E1_002
MODEL_ID = MultiResoModel-Simple
EXECUTION_OWNER = PARALLEL_WORKER_R2
NAMESPACE_OWNER_LOCK = phase3t_namespace_owner_v1; exclusive writer

## Execution identity

WORKER_WORKTREE = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2`
WORKER_BRANCH = `topconf-phase3t-multireso-worker-r2`
EXECUTION_CODE_COMMIT = `418593d2c9f0c90f7c663fa001fa15f8839bde7f`
POSTRUN_REPAIR_UTILITY_COMMIT = `ebad7eac879cd4ae14c7cbb14bf0900101720e0f`
CURRENT_BRANCH_HEAD = `ebad7eac879cd4ae14c7cbb14bf0900101720e0f`
AUTHORIZED_EXECUTABLE = `F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310/Scripts/python.exe`
PYTHON = `3.10.11`
TORCH = `1.13.1+cu117`
FAIRSEQ = `0.12.2`
GPU = `NVIDIA GeForce RTX 4060 Laptop GPU`
HOST = `ROG-Zephyrus-G16`

The worker resumed only after the infrastructure-only manifest serialization and
resume-identity reconciliation.  The model repository identity remained the
authorized `0f69db3a2d654de47822d951fe6ad256bbaac9ba`; the execution commit is
the commit recorded by the completed run manifest.  No mainline MultiReso
partial output was resumed or ingested.

## Frozen output locations and hashes

NAMESPACE = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02`
RAW = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/multireso_raw_v1.jsonl`
RAW_SHA256 = `00E502AA418DC1279AE19F72E48E1617A4BCF56014307FE6E0BC666736E37925`
CASE_LEDGER = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/multireso_case_ledger_v1.jsonl`
CASE_LEDGER_SHA256 = `24FAE99EEE5BE1E3CDE8D912AE8EF4C12DF6423A7705599F4C7C26DA97EA5733`
OUTPUT_MANIFEST_JSONL = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/multireso_output_manifest_v1.jsonl`
OUTPUT_MANIFEST_JSONL_SHA256 = `4A606CA23126AF50CDDF3ACA1AABA536BB03B96DDF4C962DA924080034F521AC`
ATTEMPTS = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/multireso_attempts_v1.jsonl`
ATTEMPTS_SHA256 = `D1C66CCF73538ECD810F56ABDD29402D85A38CA5A22323D83EED17869FCA204E`
RETRY_LEDGER = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/multireso_retry_ledger_v1.jsonl`
RETRY_LEDGER_SHA256 = `87D9A2B86FBBCA61FFBCEC5788E3B205B0509D150F8A1D896EB0CF1EADC9F3AD`
RUN_MANIFEST = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json`
RUN_MANIFEST_SHA256 = `0EE148D1305675369D7B8772BD37A2C39E769A4C0CA8A9D335756A6DC6BB2333`
ATTEMPT_BACKFILL_REPORT = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02/MULTIRESO_ATTEMPT_LEDGER_BACKFILL_V1.json`
ATTEMPT_BACKFILL_REPORT_SHA256 = `ADAD92B6AE8B54D8C96C0D8EF2A84058D6FFFD38802374A6E6EED09211638B22`
MAINLINE_T2_VALIDATION = `F:/项目/申请实验室  TTS项目/AudiobookBench-CN-topconf-dl-robustness/results/topconf_phase3t/multireso_r2_validation.json`
MAINLINE_T2_VALIDATION_SHA256 = `BC87402447FEFDEF7DF1360B76B5910C4BFEF9A2580D7AA24F142BC7B4899054`

## Completion and integrity

PLANNED_CASES = 42471
TERMINAL_CASES = 42471
VALID_CASES = 42438
FAILED_CASES = 33
MISSING_CASES = 0
FAILURE_CLASS = `AUDIO_LOAD_FAILURE` (33)
RETRY_COUNT_FROM_RAW = 4
RETRY_LEDGER_RECORDS = 4
RUN_MANIFEST_STATUS = COMPLETE
SCALES_EXPECTED = 6
SCALES_PRESERVED = 6/6
GT_ACCESSED = NO
SCIENTIFIC_METRICS_COMPUTED = 0
RESULT_BASED_CASE_EXCLUSIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0

Mainline T2 validation is PASS: raw completeness PASS, failure accounting
PASS, no GT-like keys, and all per-record native-output hashes match after
case-normalizing the hexadecimal representation.  Raw case IDs are unique and
case_index is continuous; case ledger and output manifest are each 42,471
records with the same set and order as raw.

The attempts history contains 42,482 records: 42,475 unique case-attempt keys,
four attempt=2 records matching the four raw retry_count=1 cases, and seven
duplicate attempt=1 start keys retained as historical restart evidence.  The
terminal attempt for every raw record is represented.  The 33 missing
audio-load attempt-start rows were added append-only by
`PHASE3T_MRM_ATTEMPT_LEDGER_BACKFILL_V1`; raw and case ledger were not
modified.  Before/after attempts hashes and the exact added case IDs are in the
backfill report above.

## Authorized data and model materialization

DATASET = `PartialEdit_v1.1_E1`
DATASET_CSV_SHA256 = `ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC`
CASE_ORDER = official CSV E1 order
AUDIO_ROOT = `F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/materialized/E1`
CHECKPOINT_ARCHIVE_SHA256 = `0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32`
MODEL_REPOSITORY_COMMIT = `0f69db3a2d654de47822d951fe6ad256bbaac9ba`
STRICT_LOAD_MISSING = 0
STRICT_LOAD_UNEXPECTED = 0

## Runtime note

RUN_LEVEL_RUNTIME_SEC = 4815.7775395
PEAK_VRAM_MAX_BYTES = 2474151424

The worker's per-record raw `runtime_sec` field was populated from a timestamp
started immediately before terminal serialization, so it is not a trustworthy
per-case wall-clock measurement; the frozen raw values are preserved unchanged
and are not used for scientific evaluation.  The completed run manifest's
run-level runtime above is the authoritative runtime record.  This is a
metadata instrumentation limitation, not a native-output or completeness
failure.

## Ingestion boundary

Mainline may read-only verify the paths and hashes above, validate the raw with
the authorized Phase3T validator, and ingest this namespace as the formal
MultiReso output.  Mainline must not rerun MultiReso, inspect GT before T4, use
the old worker namespace, use the terminated mainline partial, or select a
scale/model from outcomes.  This handoff contains no metrics or GT outcomes.
