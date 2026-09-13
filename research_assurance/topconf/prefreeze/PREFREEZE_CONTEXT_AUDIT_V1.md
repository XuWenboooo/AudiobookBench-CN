# RQ1 Parallel Pre-Freeze Context Audit v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

Audit date: **2026-09-13**
Parallel lane: `TOPCONF_PARALLEL_LANE_RQ1_PREFREEZE`
Fixed base: `origin/topconf-dl-robustness` at `2fe5641274b232a5535df6b36314e665a12c043e`
Scientific runs invoked: **NO**

## Scope and invariants

This audit was performed from the committed repository state in the isolated
`topconf-rq1-prefreeze` worktree. It does not read uncommitted Phase 3R
outputs, does not access Level-2 outcomes, and does not alter Phase 1--3R
authority files. Every conclusion in this directory is a candidate for human
reconciliation only.

The following invariants remain explicit:

```text
WEEK1_5_RESEARCH_PHASE = ARCHIVED
WEEK1_5_NEW_EXPERIMENTS_ALLOWED = NO
WEEK1_5_DATA_ROLE = PILOT_ONLY
WEEK1_5_CONFIRMATORY_USE = PROHIBITED
PHASE4_STARTED = NO
LEVEL2_OUTCOMES_ACCESSED = NO
CONFIRMATORY_EXECUTION_AUTHORIZED = NO
SCIENTIFIC_RUNS_INVOKED = NO
```

## Current research questions

| Question | Committed context | Pre-freeze interpretation |
|---|---|---|
| RQ1 | Under manipulation-mechanism shift and realistic media transformations, do utterance-level detection and temporal localization degrade at different rates? | The estimand is a paired detection-retention versus localization-retention comparison. `LD@DR95` is a recommended candidate, not frozen. |
| RQ2 | Can a bounded black-box adversary preserve coarse detection while degrading localization under preservation and budget constraints? | Attack conjunction and success rule remain TBD and are not prepared as an executable run. |
| RQ3 | Which controlled interventions explain the gap, and can unreliable localization be detected or mitigated? | Controlled intervention and reliability analysis; no post-hoc cue mining. |

## Decisions already present in committed drafts

These are protocol-hardened candidates, not authorization:

- Level 0/1/2 and H-PILOT/C-TRAIN/C-DEV/C-HELDOUT/EXT-BASELINE separation.
- `LD@DR95` as the recommended RQ1 gap candidate, with higher-is-better
  direction conversion and explicit `NOT_ESTIMABLE` for an empty feasible set.
- Whether-A is derived from a localizer using one fixed pooling rule; Whether-B
  is an independent frozen utterance detector whose score is not computed from
  the localization map.
- Where can be represented at frame, event, proposal, and boundary levels;
  the primary level is not frozen.
- Candidate detection metrics include AUROC, AUPRC, EER and fixed-FPR
  retention; candidate localization metrics include frame scores, event/proposal
  AP/F1, boundary errors, and RangeEER.
- Thresholds must be official, Level-1-calibrated, or a frozen target-FPR/EER
  rule; Level-2 threshold optimization is prohibited.
- Paired source/case units, fail-closed missingness, explicit terminal states,
  and no silent dropping or replacement.
- A gap gate requiring stability across at least three distinct localization
  paradigms and two independent distributions, subject to final review.

## Still-open decisions

The following remain `TBD_BEFORE_AUTHORIZATION` or require a new versioned
review:

1. The exact Level-2 population and sampling frame, including prevalence.
2. The common-core model/paradigm set and compatible output semantics.
3. The primary Where level, metric, temporal resolution, and direction.
4. The primary detection-retention definition among ratio, paired correctness,
   and fixed-threshold alternatives.
5. The final Whether-A rule and whether an independent Whether-B is available.
6. Mechanism and transformation counts, strengths, budgets, and stopping rules.
7. Reference selection, quality gates, retry eligibility, and no-valid-parent
   adjudication.
8. Statistical resampling count, uncertainty model, multiplicity family, and
   stopping rule.
9. Compute feasibility for every selected external checkpoint and legal release
   status for third-party artifacts.

## Phase3R-dependent versus independent work

| Item | Classification in this lane | Reason / handoff condition |
|---|---|---|
| Core baseline set | **PHASE3R-DEPENDENT** | Phase 3R reproduction, output contracts, checkpoint identity, and availability can change the compatible core. |
| Common-core Where metric | **PHASE3R-DEPENDENT** | Native temporal resolution and output semantics must be known for every retained paradigm. |
| Whether-A final form | **INDEPENDENT CANDIDATE, NOT FROZEN** | Formal pooling analysis can be done now; final choice must be recorded in authorization and cannot use outcome comparisons. |
| Whether-B role | **PHASE3R-DEPENDENT** | Candidate provenance can be audited now, but final inclusion depends on independent checkpoint and Mandarin/general-speech compatibility. |
| External reproduction role | **PHASE3R-DEPENDENT** | It depends on committed reproduction availability and rights, not on this lane's literature assessment. |
| Mechanism taxonomy | **INDEPENDENT CANDIDATE** | Can be selected by identifiability, paired-control feasibility, modern relevance, and reproducibility. |
| Transformation taxonomy | **INDEPENDENT CANDIDATE** | Can be reduced to a small interpretable matrix without observed outcomes. |
| Level-2 population bands | **INDEPENDENT CANDIDATE, NOT FROZEN** | Candidate ranges and trade-offs are design work; final population must be approved after capability review. |
| Sample-size bands | **INDEPENDENT SYNTHETIC SENSITIVITY** | Simulations map design sensitivity only; they do not optimize to pilot or Phase3R effects. |
| Thresholds | **PHASE3R/PROTOCOL-DEPENDENT** | Need final model output contracts and an authorized calibration rule. |
| GPU environment | **PARTLY INDEPENDENT** | Host inspection is complete; full reproduction feasibility remains checkpoint- and dependency-dependent. |
| Artifact validator | **INDEPENDENT TOOLING** | It validates provenance/governance completeness and never evaluates scientific direction or magnitude. |

## Potential conflicts and degrees of freedom

- Existing `EXTERNAL_BASELINE_MATRIX_V1.md`, `MODEL_CAPABILITY_MATRIX_V1.md`,
  and the Phase 3R records contain source-level candidates but not a final
  common core. This lane adds no edits to those files.
- `LD@DR95` has multiple valid detection-retention operationalizations and
  several localization aggregations. Selecting among them after observing
  results would be metric drift.
- A mechanism taxonomy can accidentally confound mechanism with boundary
  smoothness, codec path, text, speaker, or target duration. Paired
  counterfactuals and explicit transformation cells are therefore required.
- Long-form and Mandarin are deployment/regime choices, not novelty claims.
- A single-person workflow can provide mechanical blinding, but cannot claim
  independent human custody. The limitation is retained explicitly.
- Real checkpoints may be unavailable, licensed restrictively, trained on
  language or domains mismatched to Mandarin, or incompatible with a common
  output contract. Such rows stay conditional or blocked.

## Read-only context evidence

The audit read the following committed files in full: `PROJECT_STRUCTURE.md`,
`TOPCONF_RESEARCH_PREREGISTRATION_V1.md`, `NOVELTY_LEDGER_V1.md`,
`THREAT_MODEL_V1.md`, `EXTERNAL_BASELINE_MATRIX_V1.md`,
`DATA_CLASSIFICATION_AND_LEAKAGE_POLICY_V1.md`,
`CONFIRMATORY_PROTOCOL_SKELETON_V1.md`, `OPEN_SCIENCE_MANIFEST_V1.md`,
`PROTOCOL_CONSISTENCY_REVIEW_V1.md`, `LD_DR95_FORMAL_REVIEW_V1.md`,
`PHASE2_INFRASTRUCTURE_READINESS_V1.md`, `PHASE2_5_CLOSURE_V1.md`, and
`MODEL_CAPABILITY_MATRIX_V1.md`. Phase 3/3R documents were treated as
committed read-only context only.

## Negative boundary

No model inference, benchmark, generation, attack, defense, real-data
bootstrap, Level-2 population construction, or result-based selection was
performed. No field in this audit authorizes Phase 4 or confirmatory execution.
