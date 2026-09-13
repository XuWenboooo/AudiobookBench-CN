# Phase3T MultiReso Worker-02 Epoch 1 Supersession v1

Status: **INFRASTRUCTURE-ONLY / SUPERSEDED BEFORE SCIENCE**

The first r2 worker-02 epoch reached 6,711 terminal records, with 6,678 valid
and 33 audio-load infrastructure failures. Its raw, terminal, and per-case
manifest files had equal case-ID sets and zero duplicate IDs at archival. It
is nevertheless ineligible for Phase3T because separate processes wrote the
same namespace during the recovery window: PID 42112 and PID 4764 (each with
an authorized venv parent but a child executable path outside the frozen
invocation identity).

```text
SUPERSEDED_INVOCATION = PHASE3T_MRM_FULL_E1_002
SUPERSEDED_NAMESPACE = results/topconf_phase3t/multireso_worker_02
SUPERSEDED_EPOCH = r2-mixed-writer-1
SUPERSEDED_TERMINAL = 6711
SUPERSEDED_VALID = 6678
SUPERSEDED_FAILURES = 33 AUDIO_LOAD_FAILURE
SUPERSEDED_RAW_LEDGER_DUPLICATES = 0
SUPERSEDED_RAW_LEDGER_SET_DIFF = 0
SUPERSEDED_OUTPUTS_USED_FOR_SCIENCE = NO
ARCHIVE_NAMESPACE = results/topconf_phase3t/multireso_worker_02_superseded_epoch1_20260913
CLEAN_EPOCH_INVOCATION = PHASE3T_MRM_FULL_E1_002
CLEAN_EPOCH_START = first authorized E1 case; full planned population 42471
PROTOCOL_CHANGED = NO
GT_ACCESS = NO
SCIENTIFIC_METRICS_COMPUTED = 0
```

The archive move preserves every file from the mixed-writer epoch. The clean
epoch is created only after the archive is complete and is protected by the
atomic namespace owner lock.

