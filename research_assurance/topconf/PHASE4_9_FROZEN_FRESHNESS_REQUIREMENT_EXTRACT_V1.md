# Phase 4.9 Frozen Freshness Requirement Extract v1

This is a read-only extraction of repository text. It does not resolve
ambiguity, add an exception, or reinterpret a policy in favor of PASS.

## Frozen population and source reuse

- The design freezes two independently rights-cleared, long-form Mandarin
  source pools, 200 primary sources and 60 speakers per pool, 400 sources and
  120 speakers total, four balanced mechanisms per source, and a 40-source
  reserve selected before model output. Source: `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`,
  §9 “Fresh Level-2 population and sample size”.
- Exact pool identities and hashes must be filled before authorization, and no
  Phase3T E1 row may be reused. Source: the same dossier, §9.
- The private freshness manifest must prove that no case or lineage belongs to
  Week1–5 pilot data, Phase3T PartialEdit v1.1 E1, or any development/model/
  metric/threshold selection set. Source: `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`,
  §6 “Population, pairing, and freshness”.

## Speaker, session, and lineage rules

- Sampling is speaker-disjoint across `C-TRAIN`, `C-DEV`, `C-CALIBRATION`, and
  `C-HELDOUT`; source and session families may not cross a held-out boundary.
  Source: `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`, §9.
- Source/session/speaker identities are disjoint across development,
  calibration, and held-out evaluation. Source: `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`,
  §6.
- Target positions are selected by a fixed speech-bearing placement rule, not
  labels, detector scores, visualization, or quality outcomes. Source: the
  dossier, §9, and the preregistration, §6.
- The paired unit is the same source, speaker, surrounding context, target text
  where feasible, and target position across mechanisms; a voice-conditioned
  reference is a separate same-speaker utterance/text selected by a deterministic
  predeclared rule and is generator input only. Source: the preregistration, §6.

## Freshness and historical exclusion

- The source pools must be independently rights-cleared Mandarin long-form
  distributions with source/session/speaker metadata. Source: the dossier, §9.
- The private freshness manifest is a prerequisite to authorization and must
  carry exact pool identities and hashes. Source: the dossier, §9.
- Missing, unknown, or duplicate rows block closure. Source: the dossier, §11
  “Blinding, failures, and namespace”.
- The historical reconstruction retains directly observed identities and
  represents unresolved history as `PARTIAL` or `UNKNOWN`; an apparent zero
  cannot be treated as proof of non-use. Source: `PHASE4_7_HISTORICAL_EXCLUSION_AND_FRESHNESS_CLOSURE.md`,
  §Outcome and §Freshness validator.

## Post-freeze acquisition and project-entry semantics

- The selected-corpus project-entry proof records the Test/Eval archives and
  extracted segments as acquired after the 2026-09-14 protocol freeze, and
  explicitly states that filesystem presence is not treated as evidence of
  prior scientific use. Source: `LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json`,
  `protocol_freeze`, `acquisition`, and `local_existence_is_not_usage`.
- The retained AISHELL-1 project-entry proof records no prior project reference
  in the searched evidence, while explicitly limiting that statement because
  the historical universe is incomplete. Source: `AISHELL1_PROJECT_ENTRY_PROOF_V1.json`,
  `search_result`, `interpretation`, and `limitations`.
- The frozen policy text does not state that post-freeze acquisition by itself
  replaces a complete historical exclusion universe. This is recorded as
  `POSSIBLE_POLICY_AMBIGUITY`, not resolved on the mainline.

## Critical unknown handling and result states

- The frozen design says missing/unknown/duplicate rows block closure. Source:
  `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`, §11.
- The production freshness implementation returns `PASS`, `FAIL`, or
  `INSUFFICIENT_EVIDENCE`, and states that missing historical identity is never
  converted into zero overlap. Source: `src/audiobookbench/topconf/level2/materialization.py`,
  `validate_level2_freshness_v3` docstring and body.
- The implementation checks the four referenced universes, requires evidence
  sources for non-empty-exclusion statuses, recomputes the declared overlap
  counts, fails on prohibited case/source/lineage overlap, and applies the
  declared speaker policy. Source: the same function.
- When no prohibited overlap is found but any completeness value is `PARTIAL`
  or `UNKNOWN`, the implementation returns `INSUFFICIENT_EVIDENCE`. Source:
  `src/audiobookbench/topconf/level2/materialization.py`, the conditional after
  `unknown_total`.

## Authorization boundary

- Phase4 freezes the design but creates no execution authorization; separate
  human review remains required after materialized freshness proof, the
  third-paradigm claim gate, and model-specific preflight checks. Source:
  `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`, §12.
- The preregistration records `PROTOCOL_FROZEN = YES` while
  `RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO` and
  `RQ1_CONFIRMATORY_EXECUTION_STARTED = NO`. Source:
  `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`, §10.

