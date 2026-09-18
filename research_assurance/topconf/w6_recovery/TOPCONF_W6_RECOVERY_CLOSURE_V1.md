# TOPCONF-W6_RECOVERY Closure v1

Audit date: `2026-09-18`

```text
BASELINE_HEAD = 09f06a8dba5717e46a9d5a7084ac61834db85b34
RECOVERY_MODE = ALL_REGISTERED_CANDIDATES_ATTEMPTED
TOTAL_LOCALIZER_CANDIDATES = 7
SUCCESSFULLY_REPRODUCED = 2
READY_LOCALIZERS = 2
DISTINCT_LOCALIZATION_PARADIGMS = 2
TOTAL_EXTERNAL_CANDIDATES = 6
READY_EXTERNAL_DISTRIBUTIONS = 1
BLOCKED_EXTERNAL_DISTRIBUTIONS = 5
MODEL_PREFLIGHT = PASS_FOR_ALL_READY_LOCALIZERS; OVERALL_W6_SET_INCOMPLETE
W6_GATE = BLOCKED
W7_PROTOCOL_FROZEN = NO
W7_FORMAL_PILOT_READY_FOR_HUMAN_REVIEW = NO
LEVEL2_OUTCOMES_ACCESSED = NO
W7_SCIENTIFIC_INFERENCES = 0
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
RESULT_BASED_MODEL_SELECTIONS = 0
RESULT_BASED_DATASET_SELECTIONS = 0
RESULT_BASED_METRIC_CHANGES = 0
```

## Decision

W6 remains blocked because the formulation-based paradigm count is 2, below
the frozen target of 4, and only one external distribution is fully ready,
below the target of 2. The recovery run attempted every registered candidate;
it did not stop after the first two ready paradigms and did not use outcome
guided selection.

## Failed candidates / exact remaining blockers

- BAM: official clone failed with an HTTP/2 framing error; checkpoint rights and
  hash remain unresolved.
- SAL: official clone failed with a connection reset; checkpoint unavailable.
- TRACE: no verified official audio-localization implementation, checkpoint, or
  output contract.
- LlamaPartialSpoof: official clone failed to connect; local audio absent and
  no W7 adapter/integrity proof.
- PartialSpoof: official 5.8 GB eval archive is not locally materialized; the
  current session could not query the existing system BITS job because of
  `E_ACCESSDENIED`.
- HAD: archive, rights, temporal-GT binding, and adapter remain unresolved.
- MIST: rights, local integrity, and adapter remain unresolved.
- HQ-MPSD: not an authoritative official distribution.

## Next authorized action

Retry official-source/checkpoint recovery when network and transfer permissions
are available, preserving the same frozen candidate universe and no-outcome
firewall. After recovery, re-run only source/checkpoint/integrity/preflight
audits and regenerate the matrices. Do not run W7 scientific inference,
Level-2 inference, RQ2/RQ3, or any metric calculation.
