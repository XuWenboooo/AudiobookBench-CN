# Phase3T MultiReso Worker-02 Epoch 1 Assessment Correction v1

Status: **INFRASTRUCTURE-ONLY / CURRENT r2 OUTPUTS RETAINED**

An interim conservative assessment treated PID 4764 as a possible second
writer for the r2 directory. Subsequent process provenance showed that PID
4764 was a child of the old-worktree supervisor whose script and output root
were `AudiobookBench-CN-phase3t-multireso-worker`, separate from the r2
worktree. The r2 execution process was PID 42112, and its output files have
equal raw/terminal/manifest case-ID sets with zero duplicate IDs through
6,711 terminal records. The conservative assessment is retained under
`results/topconf_phase3t/worker_02_recovery_evidence/` as evidence, but is not
treated as a live namespace marker.

```text
R2_INVOCATION = PHASE3T_MRM_FULL_E1_002
R2_NAMESPACE = results/topconf_phase3t/multireso_worker_02
R2_WRITER = PID 42112; authorized r2 process
R2_TERMINAL = 6711
R2_VALID = 6678
R2_FAILURES = 33 AUDIO_LOAD_FAILURE
R2_DUPLICATE_CASE_IDS = 0
R2_RAW_LEDGER_SET_DIFF = 0
OLD_SUPERVISOR_OUTPUT_ROOT = AudiobookBench-CN-phase3t-multireso-worker\results\topconf_phase3t\multireso_worker_02
OLD_SUPERVISOR_WRITER_PID = 4764
CURRENT_OLD_SUPERVISOR_STATUS = stopped
SCIENTIFIC_OUTCOMES_USED = NO
PROTOCOL_CHANGED = NO
```

The r2 process stopped on a Windows manifest file-lock error; its raw and
terminal records remain structurally consistent. Resume may continue only
after the r2 namespace lock is reacquired and the old supervisor remains
stopped.

