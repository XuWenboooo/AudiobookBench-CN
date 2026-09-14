# Phase 4 Reconciliation Ledger v1

Status: **COMPLETE — MANUAL CONTENT RECONCILIATION**  
Ledger date: **2026-09-14**

This append-oriented ledger records what was adopted from the two frozen
parallel branches. Branches remain intact at their recorded tips. No branch
was merged, rebased, reset, or bulk cherry-picked.

| Entry | Source branch / commit | Adopted content | Integration method | Conflict resolution / reason | Result |
|---:|---|---|---|---|---|
| 1 | `topconf-rq1-prefreeze @ 82e6fd2` | context audit, Phase4 handoff, dependency matrix | content review | corrected historical Phase3R labels to Phase3T and preserved non-authorizing boundary | `PHASE4_REVIEWED` |
| 2 | `topconf-rq1-prefreeze @ 82e6fd2` | population, GT, failure, mechanism, transformation drafts | manual rewrite into final preregistration | fixed only by capability-independent semantics and feasibility; no pilot/Phase3T outcome used | `ACCEPT_WITH_UPDATE` |
| 3 | `topconf-rq1-prefreeze @ 82e6fd2` | metric hierarchy, LD candidate, Whether-A | manual rewrite into dossier/preregistration | selected native 20 ms common frame and normalized mean by task semantics and native support | `ACCEPT_WITH_UPDATE` |
| 4 | `topconf-rq1-prefreeze @ 82e6fd2` | Whether-B candidate audit | manual blocker record | public source candidate lacks locally verified checkpoint hash, license chain, and runtime smoke | `BLOCKER_RETAINED` |
| 5 | `topconf-rq1-prefreeze @ 82e6fd2` | claim safety, prior-art matrix, novelty log | provenance-only citation | retained bounded wording; no “first” or exhaustive-negative claim | `BACKGROUND_ONLY` |
| 6 | `topconf-rq1-prefreeze @ 82e6fd2` | synthetic statistical simulation | reviewed synthetic design input | fixed 400/120/4 planning band; simulation is not power and does not pick from observed results | `SYNTHETIC_ONLY` |
| 7 | `topconf-phase4-reconcile-prep @ 4e173b4` | reconciliation map, conflict forecast, quality audit, runbook | manual content audit | used as review scaffolding; no automatic merge or overwrite of authority files | `AUDIT_COMPLETE` |
| 8 | `topconf-phase4-reconcile-prep @ 4e173b4` | LD, gap, mechanism, transformation, metric, statistics, Whether memos | manual integration | resolved candidate language into versioned freeze fields and explicit NOT_ESTIMABLE rules | `ACCEPT_WITH_UPDATE` |
| 9 | `topconf-phase4-reconcile-prep @ 4e173b4` | Level-2 governance module, fixtures, CLI concepts | manual implementation and tests | extended exact-once, unknown-case, freeze-before-reveal, checkpoint, metric, and threshold gates | `ACCEPT_WITH_UPDATE` |
| 10 | `topconf-phase4-reconcile-prep @ 4e173b4` | paper skeleton | no integration | publication claims are downstream and would create scope drift | `REJECT` |
| 11 | mainline `17b6419` | Phase3T authority and raw manifest | read-only verification | kept all authority paths untouched; outcome firewall prohibits selection use | `ACCEPT_AS_PROVENANCE` |

## Integrity counters

```text
BLIND_MERGES = 0
BLIND_BULK_CHERRY_PICKS = 0
SOURCE_BRANCHES_REWRITTEN = 0
PHASE3T_AUTHORITY_FILES_OVERWRITTEN = 0
RESULT_BASED_BASELINE_SELECTIONS = 0
RESULT_BASED_METRIC_SELECTIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_HEAD_SELECTIONS = 0
RESULT_BASED_TRANSFORMATION_SELECTIONS = 0
RESULT_BASED_MECHANISM_SELECTIONS = 0
RESULT_BASED_THRESHOLD_SELECTIONS = 0
RESULT_BASED_SAMPLE_SIZE_ADJUSTMENTS = 0
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
```

## Provenance verification

The two source branch tips, their common base, and the mainline head were
resolved from local Git refs on 2026-09-14. The source-side hash ledgers were
read but not regenerated. Phase3T raw-output hashes remain in
`PHASE3T_RAW_OUTPUT_MANIFEST_V1.json`; no raw result was copied into a new
Phase4 result namespace.

The ledger is complete as a reconciliation record. It does not by itself
resolve the Whether-B checkpoint/licensing blocker and does not authorize any
future Level-2 run.
