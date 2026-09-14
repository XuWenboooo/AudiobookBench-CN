# Phase 4 Reconciliation Matrix v1

Status: **COMPLETE — CONTENT-LEVEL REVIEW / BLIND MERGES = 0**  
Reconciliation date: **2026-09-14**

## Frozen inputs

```text
MAINLINE_BRANCH = topconf-dl-robustness
MAINLINE_HEAD_AT_REVIEW = 17b6419e4ee185a7029034776034235bcf17eac7
COMMON_BASE = 2fe5641274b232a5535df6b36314e665a12c043e
BRANCH_A = topconf-rq1-prefreeze @ 82e6fd2c63c3afd2ad374f8cb4cc785f496822af
BRANCH_B = topconf-phase4-reconcile-prep @ 4e173b43950b5bc1985ed228c965513816740711
BLIND_MERGES = 0
BLIND_BULK_CHERRY_PICKS = 0
```

`ACCEPT_WITH_UPDATE` means the content was manually reconciled into a new
Phase4 artifact or tool. `ACCEPT_AS_PROVENANCE` means it remains evidence of
the frozen branch state. `SUPERSEDED` means a stricter mainline artifact
replaces the candidate wording. No source branch was merged or rewritten.

## Branch A — `topconf-rq1-prefreeze`

| Source file | Purpose | Mainline equivalent / action | Status | Rationale |
|---|---|---|---|---|
| `PREFREEZE_CONTEXT_AUDIT_V1.md` | boundary and dependency audit | this matrix, outcome firewall, decision dossier | ACCEPT_WITH_UPDATE | Phase3T is the actual dependency; historical Phase3R wording is corrected. |
| `PHASE4_PREFREEZE_HANDOFF_V1.md` | non-authorizing handoff | closure and ledger | ACCEPT_AS_PROVENANCE | Correct boundary; all candidate labels are superseded by reviewed decisions. |
| `PHASE4_DECISION_DEPENDENCY_MATRIX_V1.md` | decision blockers | decision dossier | ACCEPT_WITH_UPDATE | Retains candidate-vs-freeze distinction and records the Whether-B blocker. |
| `RQ1_LEVEL2_POPULATION_DRAFT_V1.md` | fresh population and paired units | preregistration and freshness manifest | ACCEPT_WITH_UPDATE | Fixed to 400/120/4 design with no E1 reuse or result-driven replacement. |
| `RQ1_GT_BLINDING_AND_LEAKAGE_DRAFT_V1.md` | GT separation | preregistration and governance code | ACCEPT_WITH_UPDATE | Mechanical separation retained; single-human custody limitation retained. |
| `RQ1_FAILURE_ACCOUNTING_DRAFT_V1.md` | terminal states and retries | preregistration and governance code | ACCEPT_WITH_UPDATE | Converted to executable exact-once/known-case fail-closed gates. |
| `RQ1_MECHANISM_TAXONOMY_DRAFT_V1.md` | manipulation families | preregistration | ACCEPT_WITH_UPDATE | Four fixed families; codec is a transformation/control, not an outcome-selected mechanism. |
| `RQ1_TRANSFORMATION_TAXONOMY_DRAFT_V1.md` | realistic media shifts | preregistration | ACCEPT_WITH_UPDATE | Six bounded one-step cells with fixed parameters and no severity search. |
| `RQ1_METRIC_HIERARCHY_PREFREEZE_V1.md` | candidate Where/metric hierarchy | decision dossier and preregistration | ACCEPT_WITH_UPDATE | Frame-AUPRC at native common 20 ms is fixed; native alternatives remain secondary. |
| `RQ1_STATISTICAL_SIMULATION_REPORT_V1.md` | synthetic planning sensitivity | decision dossier and synthetic result | ACCEPT_WITH_UPDATE | Used only to justify a declared planning band and sensitivity, never power or effects. |
| `WHETHER_A_PREFREEZE_REVIEW_V1.md` | pooling comparison | decision dossier and preregistration | ACCEPT_WITH_UPDATE | Normalized mean is fixed from semantics/support normalization, not performance. |
| `WHETHER_B_CANDIDATE_AUDIT_V1.md` | independent-detector audit | decision dossier | ACCEPT_WITH_UPDATE | Codecfake remains a candidate; absent checkpoint hash/license/runtime prevents freeze. |
| `CLAIM_SAFETY_REVIEW_V2.md` | claim boundary | claim-evidence map | ACCEPT_AS_PROVENANCE | Bounded wording is retained; no novelty result is asserted. |
| `CLOSEST_PRIOR_ART_MATRIX_V2.md` | source-backed prior art | claim-evidence map | ACCEPT_AS_PROVENANCE | Background only; dated search is not treated as exhaustive. |
| `NOVELTY_SEARCH_LOG_V2.md` | search trace | claim-evidence map | ACCEPT_AS_PROVENANCE | Search limitations remain explicit. |
| `COMPUTE_REPRODUCIBILITY_READINESS_V1.md` | host and environment audit | dossier / authorization template | ACCEPT_WITH_UPDATE | Full confirmatory environment remains a pre-authorization gate. |
| `PREFREEZE_SHA256SUMS_V1.txt` | frozen branch hashes | reconciliation ledger | ACCEPT_AS_PROVENANCE | Verified as frozen provenance; not regenerated in Branch A. |
| `tools/topconf/simulate_rq1_statistics.py` and its test | synthetic statistics | Phase4 dry-run tooling | ACCEPT_WITH_UPDATE | Reused conceptually; no real-data path is added. |
| `tools/topconf/validate_research_assurance.py` and its test | generic metadata audit | strict Level-2 governance module | SUPERSEDED | New module covers the required fail-closed cases without scientific fields. |
| `environments/topconf/*` | environment templates | dossier / authorization template | ACCEPT_WITH_UPDATE | Templates remain non-executable until a future authorization. |

## Branch B — `topconf-phase4-reconcile-prep`

| Source file / group | Purpose | Mainline equivalent / action | Status | Rationale |
|---|---|---|---|---|
| `reconciliation_prep/PHASE4_HUMAN_RECONCILIATION_RUNBOOK_V1.md` | review sequence | this matrix and ledger | ACCEPT_AS_PROVENANCE | Sequence was followed; runbook itself grants no authority. |
| `reconciliation_prep/PHASE4_RECONCILIATION_MAP_V1.md` | destination map | this matrix | ACCEPT_WITH_UPDATE | Converted from candidate map to per-file dispositions. |
| `reconciliation_prep/PHASE4_DECISION_DOSSIER_V1.md` | candidate decisions | final decision dossier | ACCEPT_WITH_UPDATE | Candidates are resolved where safe; unresolved Whether-B is explicit. |
| `reconciliation_prep/PHASE4_MERGE_CONFLICT_FORECAST_V1.md` | static conflict forecast | ledger | ACCEPT_AS_PROVENANCE | No merge was attempted; mainline authority files were preserved. |
| `reconciliation_prep/PREFREEZE_INTEGRATION_PLAN_V1.md` | proposed cherry-pick plan | ledger | SUPERSEDED | Content was audited and manually integrated; no blind cherry-pick occurred. |
| `reconciliation_prep/PREFREEZE_QUALITY_AUDIT_V1.md` | quality review | this matrix / firewall | ACCEPT_WITH_UPDATE | Its warnings are reflected in blocker and limitation fields. |
| `reconciliation_prep/LD_DR95_IMPLEMENTATION_SPEC_DRAFT_V1.md` | metric implementation candidate | final dossier / preregistration | ACCEPT_WITH_UPDATE | Direction, feasibility, pairing, and NOT_ESTIMABLE rules are frozen. |
| `reconciliation_prep/RQ1_GAP_GATE_SPEC_DRAFT_V1.md` | gap claim gate | final dossier / claim map | ACCEPT_WITH_UPDATE | Three paradigms/two distributions and a fixed materiality rule are frozen. |
| `reconciliation_prep/RQ1_MECHANISM_PHASE4_DECISION_MEMO_V1.md` | mechanism decision aid | preregistration | ACCEPT_WITH_UPDATE | Four families selected by identifiability and reproducibility. |
| `reconciliation_prep/RQ1_TRANSFORMATION_PHASE4_DECISION_MEMO_V1.md` | transform aid | preregistration | ACCEPT_WITH_UPDATE | Fixed matrix and quality gates are frozen. |
| `reconciliation_prep/RQ1_METRIC_PHASE4_DECISION_MEMO_V1.md` | metric decision aid | final dossier / preregistration | ACCEPT_WITH_UPDATE | 20 ms frame-AUPRC is the common primary Where. |
| `reconciliation_prep/RQ1_STATISTICAL_DECISION_MEMO_V1.md` | bootstrap/sample aid | final dossier / preregistration | ACCEPT_WITH_UPDATE | 400/120/4 and 2,000 paired-source resamples fixed. |
| `reconciliation_prep/WHETHER_A_PHASE4_DECISION_MEMO_V1.md` | Whether-A aid | final dossier / preregistration | ACCEPT_WITH_UPDATE | Normalized mean rule fixed; max/top-k are non-primary diagnostics. |
| `reconciliation_prep/WHETHER_B_PHASE4_DECISION_MEMO_V1.md` | Whether-B aid | final dossier | ACCEPT_WITH_UPDATE | Independent detector gate retained; no opaque fallback. |
| `reconciliation_prep/PHASE3T_TO_PHASE4_REVIEW_CHECKLIST_V1.md` | future checklist | firewall and closure | ACCEPT_WITH_UPDATE | Phase3T PASS facts are verified; third-paradigm claim gate remains. |
| `reconciliation_prep/PHASE3T_CONTROLLED_REPRODUCTION_HANDOFF_TEMPLATE.md` | future handoff fields | authorization template | ACCEPT_AS_PROVENANCE | Fields are retained for future runs, not used as evidence now. |
| `reconciliation_prep/SYNTHETIC_GOVERNANCE_DRY_RUN_V1.md` | rehearsal scope | dry-run result and tests | ACCEPT_WITH_UPDATE | Expanded to adapter/evaluator/bootstrap and all requested failure modes. |
| `src/audiobookbench/topconf/level2/*` | metadata governance code | same path in mainline | ACCEPT_WITH_UPDATE | Strict fail-closed implementation added manually; no audio/model imports. |
| `tests/topconf/fixtures/level2_*` and `test_level2_governance.py` | governance fixtures/tests | same path in mainline | ACCEPT_WITH_UPDATE | Eleven required fail-closed behaviors are tested. |
| `tools/topconf/*level2*`, `run_phase4_synthetic_dry_run.py` | split/blind/reveal/ledger helpers | same path in mainline | ACCEPT_WITH_UPDATE | Synthetic-only CLI and dry-run path added; no real Level-2 acceptance. |
| `paper/*` skeleton | future publication framing | none in Phase4 freeze | REJECT | No paper claim or venue-readiness artifact is needed to freeze the protocol. |

## Mainline authority files

| Mainline source | Disposition |
|---|---|
| `PHASE3T_CONTROLLED_REPRODUCTION_AUTHORIZATION_V1.md` | ACCEPT_AS_PROVENANCE; unchanged |
| `PHASE3T_CONTROLLED_REPRODUCTION_CLOSURE.md` | ACCEPT_AS_PROVENANCE; append-only authority unchanged except its prior finalization record |
| `PHASE3T_CRASH_RECOVERY_AUDIT_V1.md` | ACCEPT_AS_PROVENANCE; unchanged |
| `PHASE3T_CRASH_RESUME_LEDGER_V1.md` | ACCEPT_AS_PROVENANCE; unchanged |
| `PHASE3T_RAW_OUTPUT_MANIFEST_V1.json` | ACCEPT_AS_PROVENANCE; unchanged |
| `BASELINE_PROVENANCE_REGISTER_V2.md` and dataset manifest | ACCEPT_AS_PROVENANCE; no outcome-driven edits |
| existing evaluator/adapters/tests | ACCEPT_AS_BASELINE; regression coverage preserved |

No disposition above authorizes data materialization, checkpoint loading, or
scientific inference. The unresolved Whether-B row is intentionally visible
and is the only current Phase4 closure blocker recorded in the ledger.
