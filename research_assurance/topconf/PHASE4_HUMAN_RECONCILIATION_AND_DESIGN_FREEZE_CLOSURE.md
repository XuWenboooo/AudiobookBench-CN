# Phase 4 Human Reconciliation and Confirmatory Design Freeze Closure

Status: **BLOCKED — DESIGN FIELDS FROZEN, AUTHORIZATION NOT READY**
Closure date: **2026-09-14**
Phase4 base head: `17b6419e4ee185a7029034776034235bcf17eac7`

## Closure decision

Content-level reconciliation is complete. The RQ1 Level-2 design fields are
frozen in the reviewed preregistration and decision dossier, but Phase4 cannot
close PASS because Whether-B does not yet have a locally verified checkpoint
SHA256, complete license/provenance chain, and runtime capability smoke. The
official Codecfake candidate is retained as a blocker; no localizer-derived
score is substituted. A third-paradigm requirement is also retained as the
predeclared H1 claim gate, not solved by adding a model after outcomes.

```text
PHASE4_CLOSURE = BLOCKED
PHASE4_RECONCILIATION = COMPLETE
READY_FOR_RQ1_CONFIRMATORY_AUTHORIZATION_REVIEW = NO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```

## Required final report fields

```text
BRANCH = topconf-dl-robustness
PHASE4_BASE_HEAD = 17b6419e4ee185a7029034776034235bcf17eac7
WORKING_TREE_AT_AUDIT = clean before Phase4 additions
REMOTE_SYNC_AT_AUDIT = origin/topconf-dl-robustness matched 17b6419

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
WHETHER_B = independent detector required; Codecfake candidate not included
WHETHER_B_CHECKPOINT = NOT_MATERIALIZED / SHA256_NOT_VERIFIED
WHETHER_B_FREEZE = BLOCKED_ON_CHECKPOINT_LICENSE_RUNTIME_PROVENANCE
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
LEVEL2_SYNTHETIC_DRY_RUN = PASS
FAIL_CLOSED_TESTS = PASS; 11 governance tests including all requested cases
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RESULT_BASED_DESIGN_CHANGES = 0
TESTS = python -m pytest tests/topconf -q (44 passed at closure preparation)
GIT_DIFF_CHECK = PENDING_FINAL_COMMIT_CHECK

BLOCKERS = Whether-B checkpoint/license/runtime provenance; positive H1 claim
  also requires preauthorized third paradigm and materialized freshness proof
COMMITS = Phase4 reconciliation, governance, metric/design freeze, and closure
  commits recorded in Git history
PUSH_STATUS = pending final reviewed push
```

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Phase3T closure verified | PASS | authoritative closure, crash audit, resume ledger, raw manifest |
| Parallel branch audit | PASS | matrix and ledger; both tips remain intact |
| Outcome firewall | PASS | `PHASE4_OUTCOME_FIREWALL_V1.md` |
| Baseline/output/scale policies | PASS | decision dossier; no score-driven selection |
| Whether-A | PASS | fixed pooling, direction, calibration, failure behavior |
| Whether-B | BLOCKED | exact checkpoint hash/license/runtime chain not verified |
| Where / LD@DR95 / gap gate | PASS | fixed native common metric and `NOT_ESTIMABLE` rules |
| Mechanisms / transformations | PASS | fixed paired taxonomy and bounded one-step matrix |
| Population / sample size / statistics | PASS AS DESIGN | materialization is future and separately gated |
| Thresholds / blinding / GT isolation | PASS AS DESIGN | preregistration and synthetic governance contract |
| Failure / retry / namespace | PASS | strict code gates and tests |
| Synthetic Level-2 dry run | PASS | `PHASE4_SYNTHETIC_DRY_RUN_RESULT_V1.json` |
| Real Level-2 outcomes accessed | PASS | none accessed |
| Phase4 closure | BLOCKED | Whether-B blocker remains |

This is the safe stopping point. No confirmatory execution may start from this
closure, and no automatic action should convert the blocker into an
authorization.
