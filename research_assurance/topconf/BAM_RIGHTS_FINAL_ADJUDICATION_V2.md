# BAM rights final adjudication v2

Audit date: `2026-09-21`  
Classification is split into checkpoint supply, local evaluation, and
redistribution. The checkpoint bytes are not included in Git.

```text
CHECKPOINT_OFFICIALLY_PROVIDED_FOR_EVALUATION = YES
LOCAL_RESEARCH_EVALUATION_SUPPORTED_BY_OFFICIAL_SOURCE = YES
CHECKPOINT_REDISTRIBUTION_LICENSE = NOT_ESTABLISHED
DO_NOT_REDISTRIBUTE_CHECKPOINT = YES
BAM_RIGHTS_GATE_REQUIREMENT = official author provenance + explicit intended evaluation support + no redistribution; an open redistribution license is not required for this local-use gate
BAM_RIGHTS_GATE = PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS
BAM_RIGHTS = PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS
```

## Evidence and boundary

The pinned official README explicitly says that the authors provide the model
checkpoint, links the exact author-hosted Drive object, supplies a test-only
evaluation command using that checkpoint, and requests citation for code and
results. This closes the frozen local-evaluation gate under the current
pre-execution authorization.

The same evidence does not grant redistribution. The Zenodo CC BY record is
scoped to the released source archive, not the 1,353,631,994-byte checkpoint.
The checkpoint remains local-use-only and must not be committed, uploaded,
packaged, or redistributed.

This is a pre-inference rights classification. It does not authorize W7
execution and does not alter the scientific population, metrics, or protocol.
