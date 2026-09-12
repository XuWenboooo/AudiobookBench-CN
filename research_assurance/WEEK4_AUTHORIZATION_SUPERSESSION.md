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
scientific execution. A replacement authorization now binds the frozen
execution supplement, D0 asset manifest, and execution-source manifest after
TEST_ONLY end-to-end closure.

```text
OLD_AUTHORIZATION_STATUS = SUPERSEDED_BEFORE_SCIENTIFIC_EXECUTION
```

No frozen scientific artifact was changed by this preservation step.
