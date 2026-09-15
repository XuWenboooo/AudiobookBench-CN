# Phase 4 Human Reconciliation and Confirmatory Design Freeze Closure

Status: **PASS — DESIGN FIELDS FROZEN, READY FOR AUTHORIZATION REVIEW**
Closure date: **2026-09-14**
Phase4 base head: `17b6419e4ee185a7029034776034235bcf17eac7`

## Closure decision

Content-level reconciliation is complete. The RQ1 Level-2 design fields are
frozen in the reviewed preregistration and decision dossier. The independent
Whether-B gate is now satisfied by the official AASIST repository/checkpoint
provenance and a deterministic synthetic capability smoke; no localizer-derived
score is substituted. A third-paradigm requirement remains the predeclared H1
claim gate, not something to solve by adding a model after outcomes.

```text
PHASE4_CLOSURE = PASS
PHASE4_RECONCILIATION = COMPLETE
READY_FOR_RQ1_CONFIRMATORY_AUTHORIZATION_REVIEW = YES
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```

## Required final report fields

```text
BRANCH = topconf-dl-robustness
PHASE4_BASE_HEAD = 17b6419e4ee185a7029034776034235bcf17eac7 (pre-freeze anchor)
WORKING_TREE_AT_AUDIT = clean before Phase4 additions
REMOTE_SYNC_AT_AUDIT = origin/topconf-dl-robustness matched 69dca09 at AASIST freeze audit

PHASE3T_CLOSURE_VERIFIED = PASS
RQ1_PREFREEZE_BRANCH = topconf-rq1-prefreeze
RQ1_PREFREEZE_HEAD = 82e6fd2c63c3afd2ad374f8cb4cc785f496822af
RQ1_PREFREEZE_AUDIT = COMPLETE / FROZEN_FOR_RECONCILIATION
RECONCILE_PREP_BRANCH = topconf-phase4-reconcile-prep
RECONCILE_PREP_HEAD = 4e173b43950b5bc1985ed228c965513816740711
RECONCILE_PREP_AUDIT = COMPLETE / FROZEN_FOR_RECONCILIATION
BLIND_MERGES = 0

RECONCILIATION_MATRIX = PHASE4_RECONCILIATION_MATRIX_V1.md
RECONCILIATION_LEDGER = PHASE4_RECONCILIATION_LEDGER_V1.md
PHASE3T_OUTCOME_FIREWALL = PASS; design selection prohibited

BASELINE_SET = CFPRF + MultiResoModel-Simple verified functional core;
  third paradigm required for positive six-cell H1 claim
CFPRF_OUTPUT_POLICY = native FDN 20ms primary; boundary/PRN retained secondary
MULTIRESO_SCALE_POLICY = fixed native 0.02s common scale + all six secondary;
  result-based scale selection = NO
WHETHER_A = duration-weighted mean native higher-is-better spoof score;
  Level-1 calibration target FPR 0.05
WHETHER_A_FREEZE = FROZEN
WHETHER_B = official AASIST independent utterance detector
WHETHER_B_REPOSITORY_COMMIT = a04c9863f63d44471dde8a6abcb3b082b07cd1d1
WHETHER_B_CHECKPOINT = models/weights/AASIST.pth;
  SHA256 51D2D9CF0738172F61E2A384EC50A54A55363240F67C971ED55A92435BC1A1C0
WHETHER_B_FREEZE = FROZEN_FOR_AUTHORIZATION_REVIEW
PRIMARY_WHERE_METRIC = native common 20ms frame AUPRC
SECONDARY_WHERE_METRICS = frame AUROC/AUPRC at all native scales;
  native boundary/proposal/event diagnostics when compatible
LD_DR95_DEFINITION = 1 - mean(L_c/L_r for cells with D_c/D_r >= 0.95),
  higher-is-better utilities, paired source condition aggregation,
  NOT_ESTIMABLE on invalid/empty/incompatible cells
GAP_CRITERION = >=3 paradigms x 2 independent distributions; all six cells
  estimable, each LD point estimate >=0.10 and 95% CI lower >0.00

RQ1_MECHANISMS = splice/crossfade control; conventional TTS;
  voice-conditioned TTS/VC; neural edit/infilling
TRANSFORMATION_SET = Opus 64kbps; 16-8-16k resampling; 4kHz low-pass;
  20dB SNR noise; RT60 0.3s reverb; -6dB gain
LEVEL2_POPULATION = 2 independent Mandarin long-form source pools;
  400 sources, 120 speakers, 4 balanced mechanisms, 40 fixed reserve
LEVEL2_FRESHNESS_POLICY = design manifest excludes Week1-5 and Phase3T E1;
  materialized proof required before authorization
SAMPLE_SIZE = 400 sources / 120 speakers / 4 mechanisms + 40 reserve
STATISTICAL_UNIT = paired source, with speaker clustering sensitivity
BOOTSTRAP = 2,000 paired-source primary + 2,000 hierarchical speaker->source
  sensitivity; seed 20260914; percentile 95% CI
MULTIPLICITY_POLICY = H1 single primary; Holm within locked H2-H4 families;
  exploratory native diagnostics cannot rescue H1
THRESHOLD_POLICY = official/frozen Level-1 calibration/fixed-FPR only;
  target FPR 0.05; no Level-2 test optimization
BLINDING = separate gen/gt/infer/pred/eval namespaces; mechanical single-user
  separation; no independent custody claim
GT_ISOLATION = inference-safe view excludes labels, spans, mechanisms,
  source/session linkage and failure outcomes
FAILURE_ACCOUNTING = exact one terminal per planned model/case/condition;
  known/missing/duplicate cases fail closed
RETRY_POLICY = at most one registered deterministic infrastructure or invalid-
  output retry with same lineage; no result-driven retry
NAMESPACE_POLICY = one invocation/owner/namespace; new
  results/topconf_level2_rq1_v1/ namespace; never overwrite Phase3T

CONFIRMATORY_PREREGISTRATION = TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md
RQ1_AUTHORIZATION_ARTIFACT = RQ1_CONFIRMATORY_EXECUTION_AUTHORIZATION_V1.md
AUTHORIZATION_STATUS = READY_FOR_FINAL_REVIEW / NOT_AUTHORIZED
LEVEL2_SYNTHETIC_DRY_RUN = PASS
FAIL_CLOSED_TESTS = PASS; 11 governance tests including all requested cases
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RESULT_BASED_DESIGN_CHANGES = 0
TESTS = python -m pytest tests/topconf -q (44 passed)
GIT_DIFF_CHECK = PASS

BLOCKERS = none for Phase4 design freeze; authorization still requires
  preauthorized third-paradigm disposition, materialized freshness proof, and
  model-specific preflight
COMMITS = 9691e92 (governance); 72409df (reconciliation/design freeze);
  c3dc854 (dry-run hardening and formatting); 2797bf0 (initial closure audit);
  69dca09 (AASIST capability freeze and PASS closure)
PUSH_STATUS = PUSHED to origin/topconf-dl-robustness
```

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Phase3T closure verified | PASS | authoritative closure, crash audit, resume ledger, raw manifest |
| Parallel branch audit | PASS | matrix and ledger; both tips remain intact |
| Outcome firewall | PASS | `PHASE4_OUTCOME_FIREWALL_V1.md` |
| Baseline/output/scale policies | PASS | decision dossier; no score-driven selection |
| Whether-A | PASS | fixed pooling, direction, calibration, failure behavior |
| Whether-B | PASS | official AASIST exact checkpoint/license/runtime capability record |
| Where / LD@DR95 / gap gate | PASS | fixed native common metric and `NOT_ESTIMABLE` rules |
| Mechanisms / transformations | PASS | fixed paired taxonomy and bounded one-step matrix |
| Population / sample size / statistics | PASS AS DESIGN | materialization is future and separately gated |
| Thresholds / blinding / GT isolation | PASS AS DESIGN | preregistration and synthetic governance contract |
| Failure / retry / namespace | PASS | strict code gates and tests |
| Synthetic Level-2 dry run | PASS | `PHASE4_SYNTHETIC_DRY_RUN_RESULT_V1.json` |
| Real Level-2 outcomes accessed | PASS | none accessed |
| RQ1 authorization readiness artifact | PASS AS READINESS | `RQ1_CONFIRMATORY_EXECUTION_AUTHORIZATION_V1.md`; all remaining preflight fields are explicit |
| Phase4 closure | PASS | all design-freeze gates pass; authorization remains separate |

This is the safe stopping point. The design is ready for a separate human
authorization review, but no confirmatory execution may start from this
closure and no automatic action converts readiness into authorization.

## Historical blocker resolution

The earlier Phase4 record was intentionally preserved as a historical state:

```text
PREVIOUS_PHASE4_CLOSURE = BLOCKED
PREVIOUS_BLOCKER = WHETHER_B_CHECKPOINT_LICENSE_RUNTIME_PROVENANCE
PREVIOUS_CANDIDATE = Codecfake W2V2+AASIST; checkpoint not locally hashed,
  explicit root license chain incomplete, and runtime capability smoke absent
NEW_EVIDENCE = official AASIST repository commit
  a04c9863f63d44471dde8a6abcb3b082b07cd1d1; MIT LICENSE hash
  B7290F12E8346F663833EC1C4F9964A84C74CD091DB042B3CD680548BDD18A3F;
  AASIST.pth hash
  51D2D9CF0738172F61E2A384EC50A54A55363240F67C971ED55A92435BC1A1C0;
  strict load and deterministic finite synthetic forward PASS
RESOLUTION_COMMIT = 69dca0964c5b6865289420dae8cfb8bc15b153d9
RESOLUTION_DATE = 2026-09-14
CURRENT_PHASE4_CLOSURE = PASS
```

The resolution is a provenance/capability result only. It does not imply
Whether-B performance, Mandarin transfer performance, a positive gap claim,
or authorization to execute Level 2.
