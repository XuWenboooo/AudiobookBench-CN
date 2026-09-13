# Phase3T MultiReso Resume Identity Reconciliation v1

Status: **INFRASTRUCTURE-ONLY / NO SCIENTIFIC STATE CHANGE**

The first r2 execution wrote its run identity at commit
`8da8714a0785f5bfeead08599211cba9c4a53bd3`. A later commit added only
preserved provenance for an old hidden writer; it did not change the runner,
model, dataset, checkpoint, case order, output semantics, or protocol. The
prior manifest and lock are retained as `*.pre-resume-identity-8da8714.*`
evidence before the same invocation resumes under the current branch HEAD.

```text
PRIOR_RUN_IDENTITY_COMMIT = 8da8714a0785f5bfeead08599211cba9c4a53bd3
CURRENT_BRANCH = topconf-phase3t-multireso-worker-r2
RUNNER_CODE_CHANGED = NO
PROVENANCE_DOCUMENT_ONLY = YES
INVOCATION = PHASE3T_MRM_FULL_E1_002
NAMESPACE = results/topconf_phase3t/multireso_worker_02
RESUME_FROM_TERMINAL = 2840
SCIENTIFIC_OUTCOMES_USED = NO
```

This reconciliation preserves the previous lock/manifest files and changes
only the repository identity metadata needed for the strict same-invocation
resume gate. It does not alter any raw output or terminal record.

