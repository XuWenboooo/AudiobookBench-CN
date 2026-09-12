# Week4 authorization supersession record

Date: 2026-09-12  
Scope: forensic preservation before any execution-critical implementation change.

## Preserved artifact

The authorization originally issued at
`results/week4_adaptive_redteam/authorization.json` was copied byte-for-byte
before any runtime-dispatcher implementation work to:

`results/week4_adaptive_redteam/authorization_history/authorization_AFA6BA2CC68556B832FA7C11CBAF0BF1AF1FE56B4DDB844FBA8F82FC5F7F3B48.json`

```text
OLD_AUTHORIZATION_SHA256 = AFA6BA2CC68556B832FA7C11CBAF0BF1AF1FE56B4DDB844FBA8F82FC5F7F3B48
ARCHIVED_COPY_SHA256 = AFA6BA2CC68556B832FA7C11CBAF0BF1AF1FE56B4DDB844FBA8F82FC5F7F3B48
ARCHIVED_COPY_BYTE_IDENTICAL = YES

OLD_AUTHORIZATION_USED_FOR_SCIENTIFIC_EXECUTION = NO
OLD_AUTHORIZATION_F5_INVOKED = NO
OLD_AUTHORIZATION_D0_INVOKED = NO
OLD_AUTHORIZATION_WEEK4_RESULT_OBSERVED = NO

SUPERSESSION_REASON = PRE_EXECUTION_RUNTIME_DISPATCHER_INCOMPLETE
```

## Current status

The old authorization remains forensic evidence and must not be used for
scientific execution. It is not yet labelled
`SUPERSEDED_BEFORE_SCIENTIFIC_EXECUTION`, because that terminal label is
permitted only after a complete runtime dispatcher, deterministic execution
source manifest, synthetic end-to-end closure, and replacement authorization
exist.

```text
OLD_AUTHORIZATION_STATUS = FORENSICALLY_PRESERVED_NONEXECUTABLE_PENDING_SUPERSESSION
```

No frozen scientific artifact was changed by this preservation step.
