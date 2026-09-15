# Phase 4.9 independent freshness-semantics audit v1

## Scope and independence

This is an independent, read-only-first audit of the Detection–Localization Robustness TopConf Phase 4.9 freshness closure. No Level2 model, CFPRF, MultiReso, AASIST, score, metric, threshold, scientific outcome, or confirmatory inference was run or inspected. No population, source pool, protocol, authorization, or production validator was changed.

The audit branch was created from the latest fetched remote stable commit, not from the local unpushed Phase 4.9 worktree:

```text
AUDIT_BRANCH = topconf-phase4-9-freshness-audit
AUDIT_BASE_COMMIT = 110e2b91c04625898b955c0d0dfcfccfe04515cb
AUDIT_BASE_REF = origin/topconf-dl-robustness
UNPUSHED_PHASE4_9_EVIDENCE_READ_ONLY = 3fa5ce5984c01f1feb75f931c0c00c57c0f00872,
  a242295444e1f2cdf78c1d8d3a2a662a111d6fd0,
  ad44f6b29db1930e039c57f8b5412854e8349e3f
```

The unpushed Phase 4.9 evidence was inspected from its existing local worktree only; it was not copied into the audit branch. The audit branch contains this report, the historical-relevance matrix, and diagnostic tests that exercise the existing validator without changing it.

At branch creation, `origin/topconf-dl-robustness` resolved to the audit base above. During this audit the source branch advanced to `1942746` and now contains the previously local Phase 4.9 commits plus three support commits. The audit branch was intentionally not rebased onto those source commits, preserving the physical separation and the base that was locked when the audit began.

## Required verdict fields

```text
FROZEN_FRESHNESS_REQUIREMENT =
  Two independent rights-cleared long-form Mandarin source pools;
  disjoint source/session/speaker identities across development,
  calibration, and heldout; private freshness manifest must prove no
  case or lineage belongs to Week 1–5 pilot data, Phase3T PartialEdit
  v1.1 E1, or any development/model/metric/threshold selection set;
  materialized proof is required before authorization.

POST_FREEZE_PROJECT_ENTRY_PROOF_ALLOWED = AMBIGUOUS
ALIMEETING_FIRST_PROJECT_REFERENCE = 3fa5ce5984c01f1feb75f931c0c00c57c0f00872
ALIMEETING_PROJECT_ENTRY_PROOF = STRONG_WITH_PROJECT_BOUNDARY_LIMITATIONS
AISHELL1_FIRST_PROJECT_REFERENCE = ad58622667098f02b119192e1d5a7c93e0aef77d
  (the exact Phase 4.6 entry commit recorded in the proof; see note below)
AISHELL1_PROJECT_ENTRY_PROOF = STRONG_WITH_PROJECT_BOUNDARY_LIMITATIONS
HISTORICAL_UNIVERSE_RELEVANCE =
  Explicitly keyed records have zero direct Pool A/B matches;
  Week 5, Phase 3-family, and selection-relevant ledgers retain
  PARTIAL/UNKNOWN projections and therefore remain unresolved.
VALIDATOR_IMPLEMENTATION_MATCHES_POLICY = NO_DETERMINATION_UNDER_FROZEN_TEXT
VALIDATOR_OVERCONSTRAINT = NOT_ESTABLISHED
ALIMEETING_DISTRIBUTION_COMPATIBILITY = PASS
ALIMEETING_CHANNEL_POLICY =
  V3 binds Pool A to near-field participant-headset speaker recordings
  rendered as mono 16 kHz PCM; AliMeeting far-field 8-channel audio is
  not used. The binding is explicit in paths, selection rule, and format,
  but no normalized channel_type/channel_semantics field is frozen.
CONFIRMATORY_CRITICAL_AMBIGUITY = YES
V3_POPULATION_MODIFIED = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
AUDIT_VERDICT = FROZEN_POLICY_AMBIGUITY
REQUIRED_NEXT_ACTION =
  DO NOT AUTHORIZE. Adopt a separate prospective governance amendment
  that explicitly defines whether a cryptographically bound post-freeze
  project-entry proof can satisfy the historical freshness requirement,
  and freezes channel semantics plus prior-use-failure handling. Then
  re-run the freshness validation under that amended rule; do not loosen
  the production validator based on this audit alone.
```

Note on the AISHELL-1 commit identifier: the project-entry proof records the exact Phase 4.6 entry commit. The audit’s history scan identifies the first exact AISHELL-1/SLR33 project reference as the Phase 4.6 entry, while generic `data_aishell` matches in the initial repository history refer to AISHELL-3 and are not treated as AISHELL-1 references.

## Frozen policy reconstruction

The controlling design text was read from the remote-stable audit base:

- `research_assurance/topconf/PHASE4_HUMAN_RECONCILIATION_AND_DESIGN_FREEZE_CLOSURE.md`: Level2 targets two independent Mandarin long-form source pools; the freshness policy excludes Week 1–5 and Phase3T E1, requires materialized proof before authorization, and provides no automatic authorization from non-results artifacts.
- `research_assurance/topconf/TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`: the two pools must be rights-cleared and long-form Mandarin; source/session/speaker identities must be disjoint across development/calibration/heldout; a private freshness manifest must prove no case or lineage belongs to the named historical or selection sets.
- `research_assurance/topconf/PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`: exact pool identities and hashes are pre-run freshness-manifest fields; no Phase3T E1 row may be reused. It does not state that all historical universes must be `COMPLETE`, and it does not state that post-freeze project-entry evidence is an authorized substitute for unresolved historical ledgers.
- `research_assurance/topconf/PHASE4_6_SOURCE_POOL_RECOVERY_CLOSURE.md`: exact corpus identity was not frozen by Phase 4.6; the implementation required a sufficiently complete historical exclusion record and passing validators. This is implementation/closure evidence, not an unambiguous prospective amendment to the confirmatory preregistration.

The literal policy therefore supports “freshness proof before authorization,” but leaves the semantics of a new corpus acquired after the freeze boundary under-specified. Treating that route as automatically allowed would add a governance interpretation; treating it as automatically forbidden would also add a governance interpretation. This is why the verdict is `FROZEN_POLICY_AMBIGUITY`, not a silent PASS and not a validator patch.

## Project-entry and identity audit

### Pool A: AliMeeting SLR119

The entry proof selects AliMeeting SLR119, provided by Alibaba, with CC BY-SA 4.0 licensing and Mandarin meeting speech. It binds the selected material to `Test_Ali` and `Eval_Ali` archive identities:

| Artifact | Size | SHA-256 | Entry evidence |
|---|---:|---|---|
| `Test_Ali.tar.gz` | 9,555,497,666 bytes | `42407625B774A44FE34F2F25CA99116F090BEC901F5AB81196B89F683A8B7BFA` | `acquired_after_freeze = true` |
| `Eval_Ali.tar.gz` | 3,673,718,355 bytes | `DC47343B2474B5EBCF458927E878155F6DDEB59C85E685B3645C32A1F9578D92` | `acquired_after_freeze = true` |
| Selection snapshot | — | `C749F4A8BAA9B1EF5BC70D6D028E58B825FADFA30E6657B1DAE5AA38CECC4C2E` | model-free selection snapshot |

The independent filesystem check reproduced both archive hashes. The local archive/directory creation timestamps are 2026-09-15, after the recorded 2026-09-14 protocol freeze. This is evidence of project-local entry timing, not evidence that the public corpus never existed elsewhere.

The alias/history search covers `AliMeeting`, `M2MeT`, `SLR119`, `Train_Ali`, `Eval_Ali`, `Test_Ali`, `alimeeting`, and the OSS AliMeeting path across the current project, Week 5, TopConf, Phase3T preparation/worker/r2, Phase4 reconciliation, and RQ1 pre-freeze worktrees. It reports no pre-Phase-4.9 project-tree or all-ref history matches and records `deleted_history_checked = true`. The first exact project reference is the unpushed selection commit `3fa5ce5...`.

The proof is `STRONG_WITH_PROJECT_BOUNDARY_LIMITATIONS`: exact archive identity, post-freeze local entry evidence, model-free selection evidence, source/session/speaker fields, and broad alias/history search are present. Limitations are explicit: there is no independent custody receipt or public corpus-version identifier, and absence from project history is not proof about external copies.

### Pool B: AISHELL-1 SLR33

The entry proof selects AISHELL-1 SLR33 as the retained independent Pool B. It records the official corpus/license identity, the exact archive hashes, no prior project usage in the searched project evidence, and post-freeze acquisition evidence:

| Artifact | SHA-256 | Entry evidence |
|---|---|---|
| `data_aishell.tgz` | `A4A0313CDE0A933E0E01A451F77DE0A23D6C942F4694AF5BB7F40B9DC38143FE` | post-freeze local archive evidence |
| `resource_aishell.tgz` | `1A6749854456E9402BC7295767937367AFED1327799A5E1DF0ED64BAA5F77409` | post-freeze local archive evidence |

The independent filesystem check reproduced both hashes. The dataset directory and archives were created on 2026-09-15, after the recorded Phase 4 freeze boundary. Embedded member timestamps from the public tar archive are 2017 metadata and are not treated as project-use timestamps.

The proof searches exact AISHELL-1 aliases (`AISHELL-1`, `AISHELL1`, `SLR33`, `data_aishell`, `speaker IDs`, archive names and paths), relevant worktrees, Git history, deleted history, and external-text evidence. It finds no prior project usage; the first exact project reference is the Phase 4.6 entry commit recorded by the proof. The generic `data_aishell` substring in older history is AISHELL-3 and does not identify AISHELL-1.

The proof is `STRONG_WITH_PROJECT_BOUNDARY_LIMITATIONS`: exact archive identity and broad negative-history evidence are present, but the proof correctly does not claim that AISHELL-1 never existed outside the searched project evidence or that filesystem timestamps are independent custody records.

### Distribution, channel, session, and speaker semantics

The official AliMeeting distribution describes both far-field 8-channel microphone-array recordings and near-field participant headset recordings. The V3 materializer selects `Test_Ali_near`/`Eval_Ali_near`, requires mono 16 kHz PCM, and retains the parent recording path, meeting/session ID, speaker ID, frame offsets, parent hash, and lineage ID. The selected set contains 200 Pool-A sources, 60 speakers, and 20 meetings; the split construction is session-blocked, no meeting or speaker crosses a split, and the selected Pool-A speakers do not span multiple selected meetings.

Therefore `ALIMEETING_DISTRIBUTION_COMPATIBILITY = PASS`: the selected near-field speaker track is a long-form Mandarin source with the required source/session/speaker metadata, and the frozen design does not prohibit meeting overlap. `ALIMEETING_CHANNEL_POLICY` is nevertheless not fully machine-readable: the manifest has `channels = 1`, a near-field parent path, and a near-field selection rule, but no normalized `channel_type` or `channel_semantics` field. The far-field 8-channel track is not included in the selected audio. This is recorded as `CONFIRMATORY_CRITICAL_AMBIGUITY = YES`; it is not evidence of distribution incompatibility.

The public dataset references used for this identity check are [OpenSLR 119 AliMeeting](https://www.openslr.org/119/) and [OpenSLR 33 AISHELL-1](https://www.openslr.org/33/). No scientific result or model behavior was used in this compatibility assessment.

## Historical relevance and freshness

The full stage-by-stage matrix is in `PHASE4_9_HISTORICAL_UNIVERSE_RELEVANCE_MATRIX_V1.md`. The decisive result is:

- Explicitly identified AISHELL-3 and PartialEdit E1 records have zero direct Pool A/B identity matches and are corpus-irrelevant for those identified rows.
- Week 5 retains unresolved source/lineage projections, and Phase 3-family plus metric/threshold/model/adapter/manual/scientific-selection stages are not complete identity ledgers. They are therefore `POTENTIALLY_RELEVANT_UNRESOLVED_PROJECTION` or `UNKNOWN_UNRESOLVED_HISTORY`, not a freshness PASS.
- The Phase 4.9 V4 manifest has all four required historical universes (`CASE_EXCLUSION`, `SOURCE_EXCLUSION`, `SPEAKER_USAGE`, `LINEAGE_EXCLUSION`) at `PARTIAL`, with zero recorded comparison counts and zero unknown counts in the materialized comparison output. Zero is not sufficient when the universes themselves are incomplete.
- The two corpus-isolation records are `PASS_POST_FREEZE_ACQUISITION` and `NO_PRIOR_PROJECT_USAGE_FOUND` as appropriate to the entry proofs. The current validator does not use these isolation statuses to override incomplete historical-universe status.

This supports a precise conclusion: current evidence establishes no direct overlap in the searched/keyed records and strong project-boundary entry evidence for both pools, but it does not establish that the frozen confirmatory policy authorizes the post-freeze route to discharge unresolved historical completeness.

## Validator semantics audit

The production implementation inspected was `src/audiobookbench/topconf/level2/materialization.py`, function `validate_level2_freshness_v3`. It:

1. Requires all four universe references.
2. Requires each universe to expose status, evidence source, and records.
3. Checks corpus-isolation status values, including `PASS_POST_FREEZE_ACQUISITION`, `NO_PRIOR_PROJECT_USAGE_FOUND`, and `FAIL_PRIOR_USAGE_FOUND`, but accepts all three as structurally valid.
4. Compares source/speaker/session/hash/lineage identities and rejects prohibited overlap.
5. Returns `INSUFFICIENT_EVIDENCE` if any universe has unknown comparisons or if any completeness value is `PARTIAL` or `UNKNOWN`; otherwise it returns `PASS`.

The exact overconstraint candidate is the global gate equivalent to:

```python
elif unknown_total or any(
    value in {"PARTIAL", "UNKNOWN"} for value in completeness.values()
):
    status = verdict = "INSUFFICIENT_EVIDENCE"
```

That gate ignores whether the incomplete universe is relevant to a corpus acquired after the freeze boundary. However, the frozen policy does not explicitly define post-freeze project-entry proof as a substitute, so this audit cannot label the gate a confirmed `VALIDATOR_OVERCONSTRAINT` without first making a governance decision.

The exact underconstraint is also material: `FAIL_PRIOR_USAGE_FOUND` is admitted as an allowed isolation status, and no later decision branch converts it to `FAIL`. A synthetic complete-zero-overlap case with `FAIL_PRIOR_USAGE_FOUND` therefore returns `PASS` today. This is unsafe to “fix” by merely loosening the global completeness gate; prior-use failure must be made a hard failure in any future governance-approved validator change.

The audit’s diagnostic tests capture both observations:

| Synthetic condition | Current validator output | Conditional policy implication if a prospective route is explicitly adopted |
|---|---|---|
| Post-freeze entry, unrelated historical universe `PARTIAL` | `INSUFFICIENT_EVIDENCE` | Candidate `PASS` only if governance explicitly allows entry proof to discharge that universe |
| Pre-freeze/no entry proof, historical universe `PARTIAL` | `INSUFFICIENT_EVIDENCE` | `INSUFFICIENT_EVIDENCE` |
| Confirmed prior-use failure, all universes complete/zero overlap | `PASS` | Must be `FAIL` |
| Post-freeze entry, all universes complete/zero overlap | `PASS` | `PASS` |

No production code was changed. The tests are diagnostic and do not assert a new protocol result.

## Structural and protocol checks

- V3 population structure: `PASS` for the requested shape as materialized in the inspected evidence: 400 sources, 120 speakers, two pools, 200 sources/60 speakers per pool, and 40 reserve sources are recorded; source/session/speaker/parent-hash/offset/lineage fields are present.
- Freshness status: `INSUFFICIENT_EVIDENCE` in V4; all four historical universes remain `PARTIAL`; authorization remains `NO_GO`.
- Distribution: `PASS` for AliMeeting near-field compatibility; no far-field channel was silently substituted.
- V3 population modification in this audit: `NO`.
- Real Level2 outcomes accessed: `NO`.
- Model inference runs: `0`.
- Scientific metrics/results: `0`.

## Final verdict

```text
AUDIT_VERDICT = FROZEN_POLICY_AMBIGUITY
```

The audit does not authorize Phase 4.9 or any Level2 confirmatory run. The evidence is sufficient to reject a silent freshness PASS, but insufficient to decide whether the current `PARTIAL/UNKNOWN` gate is an overconstraint because the frozen policy never explicitly settles the prospective post-freeze project-entry route or normalized channel semantics.

Required next action: create and approve a separate prospective governance amendment. It must explicitly state (a) whether exact post-freeze project-entry proof can replace an incomplete historical exclusion universe, (b) which historical universes remain mandatory regardless of project-entry time, (c) that `FAIL_PRIOR_USAGE_FOUND` is a hard failure, and (d) the frozen machine-readable AliMeeting channel semantics (`near_field participant-headset mono`, with far-field 8-channel audio excluded). Only after that amendment should the validator be changed, if needed, and the freshness audit rerun.
