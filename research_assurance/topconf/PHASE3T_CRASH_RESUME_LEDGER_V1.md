# Phase3T Crash Resume Ledger V1

Status: **COMPLETE — RECOVERY DID NOT RERUN COMPLETED CASES**

This ledger records crash/session recovery only. It is not a scientific retry
ledger and does not replace either model's append-only attempt ledger.

| Model / invocation | Previous state | Recovered progress | Resume action | Result |
|---|---|---|---|---|
| CFPRF mainline authorized namespace | `results/topconf_phase3t/cfprf`; a persisted standalone invocation ID was unavailable | 42,471 terminal records after the resume chain; 42,455 valid and 16 retained model failures | Authorized runner form: `F:/项目/申请实验室  TTS项目/envs/topconf-phase3s-cfprf-py310/Scripts/python.exe experiments/topconf_phase3t/run_cfprf.py --manifest results/topconf_phase3t/case_manifest.tsv --output-dir results/topconf_phase3t/cfprf --device cuda`; existing terminal IDs were skipped | Complete; no completed raw case rerun or overwritten |
| MultiReso mainline partial | `results/topconf_phase3t/multireso`; 7,810 cases | Terminated duplicate execution | No resume; namespace classified superseded and preserved | Excluded from formal output |
| MultiReso worker-01 partial | `multireso_worker_01`; 7,880 cases | Schema-invalid partial without authorized utterance output | No resume; namespace classified superseded and preserved | Excluded from formal output |
| MultiReso `PHASE3T_MRM_FULL_E1_002` worker-r2 | `multireso_worker_02`; exclusive owner lock and handoff | 42,471 terminal; 42,438 valid and 33 retained audio-load failures; 6/6 scales | Worker resumed only unfinished cases under the exclusive namespace lock; mainline performed read-only handoff verification and did not rerun MultiReso | Formal output complete and ingested read-only |

```text
CRASH_RESUME_IS_SCIENTIFIC_RETRY = NO
RAW_OUTPUT_OVERWRITE = NO
COMPLETED_CASES_RERUN = 0
NEW_MAINLINE_INFERENCE_PID_AFTER_RECOVERY = NONE
NEW_MULTIRESo_MAINLINE_INFERENCE = NO
```

The formal MultiReso handoff is
`PHASE3T_MULTIRRESO_WORKER_HANDOFF_V1.md`; its raw, case-ledger,
output-manifest, retry-ledger, backfill-report, and run-manifest hashes are
recorded in `PHASE3T_CRASH_RECOVERY_AUDIT_V1.md` and the final raw-output
manifest.
