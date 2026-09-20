# W6 external-distribution recovery baseline v1

Baseline frozen: `2026-09-20`  
Purpose: external-distribution recovery only; no W7 scientific inference.

```text
BRANCH = topconf-dl-robustness
BASELINE_HEAD = 3f67838c7f598c4f7eddad882b5057f82c169bd3
REMOTE_HEAD = 3f67838c7f598c4f7eddad882b5057f82c169bd3
LOCAL_REMOTE_SYNC = YES
WORKTREE_CLEAN = NO (untracked recovery cache/source/download scripts only)

LOCALIZER_GATE = PASS
READY_LOCALIZERS = 4
DISTINCT_LOCALIZATION_PARADIGMS = 4
PARADIGMS = CFPRF, MultiReso, SAL, BAM

READY_EXTERNAL_DISTRIBUTIONS = 1
PARTIALEDIT = READY
PARTIALSPOOF = NOT_READY; official archive/audio scan pass, but two eval IDs lack audio and matching GT
HAD = NOT_READY; official-size transfer had MD5 and ZIP integrity failure
HQ_MPSD = NOT_READY; official English transfer had MD5 and ZIP central-directory failure
LLAMA_PARTIALSPOOF = NOT_READY; local audio not materialized
MIST = NOT_READY; rights gate unresolved

W6_GATE = BLOCKED
W7_PROTOCOL_FROZEN = NO
W7_EXECUTED = NO
LEVEL2_OUTCOMES_ACCESSED = NO
W7_SCIENTIFIC_INFERENCES = 0
SCIENTIFIC_OUTCOME_FIELDS = NOT_MEASURED
RESULT_BASED_MODEL_SELECTIONS = 0
RESULT_BASED_DATASET_SELECTIONS = 0
RESULT_BASED_METRIC_CHANGES = 0
```

The untracked recovery assets are retained outside Git staging. No archive,
audio, checkpoint, or extraction directory is part of this baseline commit.
