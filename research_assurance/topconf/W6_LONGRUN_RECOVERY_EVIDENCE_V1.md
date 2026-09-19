# TOPCONF-W6 Long-Run Recovery Evidence v1

Audit date: `2026-09-19`  
Mode: `FULL-CANDIDATE-PARALLEL-RECOVERY / NO-W7-SCIENTIFIC-INFERENCE`

## 1. Identity and frozen baseline

```text
CURRENT_STAGE = TOPCONF-W6
W7_SCIENTIFIC_PILOT_STARTED = NO
RECOVERY_WORKTREE = topconf-dl-robustness
RECOVERY_HEAD = 5f4cc4393e76b019a2506a45f55c41323d4a3ab0
REMOTE_HEAD_AT_AUDIT = 764e9f9650ffcf948d4d98534122ed3f7e2f116
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
| PartialSpoof v1.2 eval | Zenodo `5766198`; official MD5 `79c7c834d0d9979ecd374a98a059ea19` | resumable `.part` transfer in progress; smaller official protocol/VAD/segment-label/README files MD5-verified | full archive not yet closed; no extraction or promotion | NOT_READY |
| SAL | GitHub `SentryMao/SAL`, commit `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485`; HF `MaoYC/SAL`, revision `d9ab313d86a8b00a6345419721389d8b4eabe992` | official source SHA256 `30504CF6B3B95C5062FE2DD1D6DDC0F605376E744E25B42E201F752D4033B22A`; WavLM and W2V2 files are present at official byte sizes; WavLM Lightning container reads | official source contract is temporal; strict construction stops because the source expects an external s3prl/fairseq base checkpoint, while the HF file is a Lightning checkpoint; W2V2 container verification remains pending after re-download closure | NOT_READY localizer |
| BAM | GitHub `media-sec-lab/BAM`, commit `55f3fb9e3b4dd6281597b86d7712fb23454179f6`; official Drive checkpoint `1eL3Ca27hEruI20lkoqkQEnZlb2GzTyHT` | source SHA256 `86E3B131017AB711489B452B24A6F7CB1D4A4418450644147BD032A2E2FB13D6`; checkpoint ZIP SHA256 `5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1`; extracted `model.ckpt` and hparams | checkpoint container reads; official strict load stops at the source-required external `wavlm_local` base checkpoint path; repository rights remain unresolved | NOT_READY localizer |
| TRACE | paper/source inventory | no verified official implementation/checkpoint/output contract | provenance gate fails | BLOCKED |
| HAD | Zenodo `10377492` | official record known; archive not materialized | rights/GT/adapter closure absent | BLOCKED fallback |
| HQ-MPSD | Zenodo `17929533` | official record identified; language archive not materialized | audio/GT/schema adapter closure absent | BLOCKED fallback |
| MIST | HF `tung2308/MIST_SpeechInpaintingDataset`, fixed revision `b1abbd16329bf1421d204af01c7b5939f128cd8a` | official metadata/card only; no full download | Research-Only rights gate and local integrity/adapter gate fail closed | BLOCKED fallback |
| LlamaPartialSpoof | official HF/project metadata | labels and license metadata cached; audio not materialized | no local audio/adapter closure | BLOCKED fallback |

The recovery did not select a source or model using performance, validation
metrics, or any scientific outcome.

## 3. Localizer and paradigm accounting

```text
READY_LOCALIZERS = 2 (CFPRF, MultiResoModel-Simple)
PILOT_ONLY_LOCALIZERS = 1 (B1b; no replacement training or promotion)
NEW_STRICTLY_READY_LOCALIZERS = 0 (SAL and BAM blocked at reproducibility gates)
DISTINCT_LOCALIZATION_PARADIGMS = 2
READY_EXTERNAL_DISTRIBUTIONS = 1
```

The two ready paradigms remain `P2_FRAME_PLUS_PROPOSAL_REFINEMENT` and
`P3_MULTI_RESOLUTION_FRAME`. SAL and BAM are not counted merely because their
papers, source repositories, or checkpoint files exist. A checkpoint is not a
ready paradigm without official source identity, strict load, synthetic smoke,
temporal output contract, and the frozen adapter.

## 4. Whether / evaluator / preflight gates

```text
WHETHER_A = existing bounded capability smoke; no new scientific inference
WHETHER_B = capability-only; no outcome-based comparison
TEMPORAL_OUTPUT_CONTRACT = PASS for the two existing ready localizers only
EVALUATOR_NAMESPACE = frozen; no metric definition changed
MODEL_PREFLIGHT = PASS for existing ready localizers; NOT_RUN/PENDING for SAL/BAM
GT_BINDING = PASS for PartialEdit E1; PENDING for PartialSpoof until archive closure
TESTS = pending final closure rerun
GIT_SYNC = NOT_SYNCED (local ahead of remote by 2 commits)
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

