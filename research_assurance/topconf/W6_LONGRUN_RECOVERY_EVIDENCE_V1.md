# TOPCONF-W6 Long-Run Recovery Evidence v1

Audit date: `2026-09-19`  
Mode: `FULL-CANDIDATE-PARALLEL-RECOVERY / NO-W7-SCIENTIFIC-INFERENCE`

## 1. Identity and frozen baseline

```text
CURRENT_STAGE = TOPCONF-W6
W7_SCIENTIFIC_PILOT_STARTED = NO
RECOVERY_WORKTREE = topconf-dl-robustness
RECOVERY_HEAD_AT_EVIDENCE_UPDATE = 4af8088b1673174c0b1af195171806b4b2e26d0f
REMOTE_HEAD_AT_EVIDENCE_UPDATE = 4af8088b1673174c0b1af195171806b4b2e26d0f
WORKTREE_STATE = AHEAD_BY_2; RECOVERY_ARTIFACTS_UNTRACKED
```

The Phase4.9R invariants are carried forward and were not edited:

```text
V3_POPULATION_SHA256 = AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4
V5_FRESHNESS_SHA256 = 6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E
V5_FRESHNESS_STATUS = PASS
V5_FRESHNESS_PATH = PATH_B_PROSPECTIVE_PROJECT_ENTRY
V3_CONFIRMATORY_OUTCOMES_ACCESSED = NO
PHASE4_9R_REOPENED = NO
```

No Level-2 outcome, RQ2/RQ3 analysis, Phase4.10 action, W7 population
inference, metric, or result table was accessed or computed in this audit.

## 2. Recovery inventory and integrity evidence

| Candidate | Official identity | Materialized evidence | Integrity / load status | Decision |
|---|---|---|---|---|
| PartialEdit v1.1 E1 | Zenodo `18829689` | 42,471 WAV; official temporal GT and split binding | no missing/extra/duplicate; adapter/evaluator previously PASS | READY external distribution |
| PartialSpoof v1.2 eval | Zenodo `5766198`; official MD5 `79c7c834d0d9979ecd374a98a059ea19` | full archive size `5,803,817,500` and MD5 PASS; isolated extraction; 71,237 WAV all decode at 16 kHz mono | official `eval.lst` has 71,239 IDs; `CON_E_0034982` and `CON_E_0058039` have no audio or matching GT; adapter fail-closed | NOT_READY |
| SAL | GitHub `SentryMao/SAL`, commit `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485`; HF `MaoYC/SAL`, revision `d9ab313d86a8b00a6345419721389d8b4eabe992` | official source SHA256 `30504CF6B3B95C5062FE2DD1D6DDC0F605376E744E25B42E201F752D4033B22A`; official WavLM file size/hash closed; deterministic wrapper preserves embedded tensors | official WavLM state strict-matched, complete SAL state strict-matched, synthetic temporal smoke and adapter PASS | READY localizer / P5 |
| BAM | GitHub `media-sec-lab/BAM`, commit `55f3fb9e3b4dd6281597b86d7712fb23454179f6`; official Drive checkpoint `1eL3Ca27hEruI20lkoqkQEnZlb2GzTyHT`; Zenodo `12747417` | source SHA256 `86E3B131017AB711489B452B24A6F7CB1D4A4418450644147BD032A2E2FB13D6`; checkpoint ZIP SHA256 `5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1`; CC BY 4.0 | complete official BAM strict load, synthetic temporal smoke, and adapter PASS after deterministic wrapper | READY localizer / P4 |
| TRACE | paper/source inventory | no verified official implementation/checkpoint/output contract | provenance gate fails | BLOCKED |
| HAD | Zenodo `10377492` | official-size `HAD.zip` download completed (`8,073,665,280` bytes), but MD5 `6fd23321b03abef5dac6ba7c26c3196d` mismatches official `4daef62a7cf20c71b052635c968ece1c`; ZIP central directory opens but streaming CRC/decompression fails | archive integrity, GT binding, and adapter closure absent; fail-closed | BLOCKED fallback |
| HQ-MPSD English | Zenodo `17929533`, official `English.zip` | official-size `3,204,831,988` bytes reached, but MD5 `0d007ce820e7a7d3300f72662447668b` mismatches official `c89346355d9afb0ba8dca4247c35dbe6`; ZIP central directory unreadable | audio/GT/schema adapter closure absent; repeated incomplete/reset Range transfers | BLOCKED fallback |
| MIST | HF `tung2308/MIST_SpeechInpaintingDataset`, fixed revision `b1abbd16329bf1421d204af01c7b5939f128cd8a` | official metadata/card only; no full download | Research-Only rights gate and local integrity/adapter gate fail closed | BLOCKED fallback |
| LlamaPartialSpoof | official HF/project metadata | labels and license metadata cached; audio not materialized | no local audio/adapter closure | BLOCKED fallback |

The recovery did not select a source or model using performance, validation
metrics, or any scientific outcome.

### B1b promotion audit

The historical B1b control remains `PILOT_ONLY`. Its project-local ECAPA
artifact and historical runtime are not an externally bound localizer
checkpoint, and no arbitrary external-distribution adapter is frozen. No new
training was run or authorized. Promotion would require a new adapter and
authorization, so B1b is not counted as a fourth paradigm.

## 3. Localizer and paradigm accounting

```text
READY_LOCALIZERS = 4 (CFPRF, MultiResoModel-Simple, SAL-WavLM, BAM)
PILOT_ONLY_LOCALIZERS = 1 (B1b; no replacement training or promotion)
NEW_STRICTLY_READY_LOCALIZERS = 2 (SAL-WavLM, BAM)
DISTINCT_LOCALIZATION_PARADIGMS = 4
READY_EXTERNAL_DISTRIBUTIONS = 1; PartialSpoof blocked by two official list/audio identity mismatches
```

The three ready paradigms are `P2_FRAME_PLUS_PROPOSAL_REFINEMENT`,
`P3_MULTI_RESOLUTION_FRAME`, and `P5_SEGMENT_AWARE_SEQUENCE`. SAL is counted
because its source/checkpoint/strict-load/temporal-adapter evidence is closed;
BAM is not counted merely because its
papers, source repositories, or checkpoint files exist. A checkpoint is not a
ready paradigm without official source identity, strict load, synthetic smoke,
temporal output contract, and the frozen adapter.

## 4. Whether / evaluator / preflight gates

```text
WHETHER_A = existing bounded capability smoke; no new scientific inference
WHETHER_B = capability-only; no outcome-based comparison
TEMPORAL_OUTPUT_CONTRACT = PASS for the two existing ready localizers only
EVALUATOR_NAMESPACE = frozen; no metric definition changed
MODEL_PREFLIGHT = PASS for all four ready localizers (CFPRF, MultiResoModel-Simple, SAL-WavLM, BAM)
GT_BINDING = PASS for PartialEdit E1; PENDING for PartialSpoof until archive closure
TESTS = last verified 91 passed; rerun after this evidence patch
GIT_SYNC = synchronized at evidence-update baseline; verify after commit/push
```

## 5. Gate decision

```text
W6_GATE = BLOCKED
W7_PROTOCOL_FROZEN = NO
W7_FORMAL_PILOT_READY = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
RESULT_BASED_MODEL_SELECTIONS = 0
RESULT_BASED_DATASET_SELECTIONS = 0
RESULT_BASED_METRIC_CHANGES = 0
```

The W7 entry condition is not met: the audit has only two distinct ready
localization paradigms and one ready external distribution. The minimum
remaining recovery is (a) close PartialSpoof archive size/MD5/audio/GT/adapter,
(b) resolve an official reproducible base-checkpoint path for at least one of
SAL or BAM and pass strict load/smoke/adapter, and (c) obtain a fourth
distinct paradigm with the same evidence standard. If these gates close, the
next action is only to freeze `W7_PILOT_PROTOCOL_V1.md` and stop; it is not to
run W7 scientific inference.

## 6. Validation and handoff

The current evidence is intentionally an honest blocked closure, not a
scientific failure. Required final validation before commit/push is:

1. rerun `tests/topconf` and `git diff --check`;
2. record final PartialSpoof transfer state and MD5 if it closes;
3. preserve the Phase4.9R hashes and no-outcome firewall;
4. commit the evidence and recovery artifacts separately; and
5. push or explicitly report `READY_BUT_UNSYNCED` if the remote remains behind.
