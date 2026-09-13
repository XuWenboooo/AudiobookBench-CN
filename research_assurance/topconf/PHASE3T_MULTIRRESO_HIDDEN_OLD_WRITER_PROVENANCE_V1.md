# Phase3T Hidden Old MultiReso Writer Provenance v1

Status: **SUPERSEDED_INFRASTRUCTURE_ATTEMPT / PRESERVED / NOT FOR SCIENCE**

During the integrity recovery, a separate old-worktree writer was found by
its imported-module command form rather than the script-path form. It was
stopped only after its provenance was captured. Its artifacts remain in the
old worktree and were not read for scientific content.

```text
OLD_HIDDEN_PARENT_PID = 21844
OLD_HIDDEN_PID = 42136
OLD_HIDDEN_PARENT_START = 2026-09-13T22:32:48+08:00
OLD_HIDDEN_START = 2026-09-13T22:32:48+08:00
OLD_HIDDEN_PARENT_EXECUTABLE = F:\项目\申请实验室  TTS项目\envs\topconf-phase3v-multireso-py310\Scripts\python.exe
OLD_HIDDEN_EXECUTABLE = F:\项目\申请实验室\python.exe
OLD_HIDDEN_COMMAND = "F:\项目\申请实验室\python.exe" -u -c "from experiments.topconf_phase3t.run_multireso_worker import main; raise SystemExit(main())" --batch-size 4 --resume --recover-stale-lock
OLD_HIDDEN_NAMESPACE = old-worktree MultiReso namespace; preserved in place
STOP_ACTION = safe process stop after provenance capture; no resume
OUTPUTS_USED_FOR_SCIENCE = NO
```

