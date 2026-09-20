# TOPCONF-W6_RECOVERY Closure v1

Audit date: `2026-09-20` (long-run evidence supersedes the 2026-09-18 transfer-attempt notes)

```text
BASELINE_HEAD = 4af8088b1673174c0b1af195171806b4b2e26d0f
RECOVERY_MODE = ALL_REGISTERED_CANDIDATES_PARALLEL_RECOVERY
TOTAL_LOCALIZER_CANDIDATES = 7
SUCCESSFULLY_REPRODUCED = 4
READY_LOCALIZERS = 4
DISTINCT_LOCALIZATION_PARADIGMS = 4
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

W6 remains blocked because only one external distribution is fully ready,
below the target of 2. The recovery run reached four distinct ready
localization paradigms and attempted every registered distribution candidate;
it did not stop after the first two ready paradigms and did not use outcome
guided selection.

## Failed candidates / exact remaining blockers

- BAM: official source and Drive checkpoint are materialized and hashed;
  Zenodo `12747417` records CC BY 4.0. Strict load, temporal smoke, and
  adapter contract all pass.
- SAL: official source and HF WavLM checkpoint are materialized; embedded
  WavLM state was deterministically wrapped without changing tensors, then
  strict-loaded through the official SAL model and passed temporal smoke and
  adapter checks. W2V2 is not needed for the WavLM qualification.
- TRACE: no verified official audio-localization implementation, checkpoint, or
  output contract.
- LlamaPartialSpoof: official clone failed to connect; local audio absent and
  no W7 adapter/integrity proof.
- PartialSpoof: official 5.8 GB eval archive size and MD5 pass, but two IDs in
  the official eval list have no audio or matching GT; adapter remains
  fail-closed.
- HAD: official-size archive transfer completed, but official MD5 mismatched (`6fd23321b03abef5dac6ba7c26c3196d` vs `4daef62a7cf20c71b052635c968ece1c`) and ZIP streaming integrity failed; rights/GT/adapter remain unresolved.
- MIST: rights, local integrity, and adapter remain unresolved.
- HQ-MPSD: official Zenodo `17929533` English pack reached the advertised
  `3,204,831,988` bytes, but local MD5 `0d007ce820e7a7d3300f72662447668b`
  mismatched official `c89346355d9afb0ba8dca4247c35dbe6`; ZIP central
  directory was unreadable after incomplete/reset Range transfers.

## Next authorized action

Retry official-source/checkpoint recovery when network and transfer permissions
are available, preserving the same frozen candidate universe and no-outcome
firewall. After recovery, re-run only source/checkpoint/integrity/preflight
audits and regenerate the matrices. Do not run W7 scientific inference,
Level-2 inference, RQ2/RQ3, or any metric calculation.
