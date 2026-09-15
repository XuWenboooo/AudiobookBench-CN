# Phase 4.9 Independent Audit Handoff v1

## Mainline identity

```text
MAINLINE_BRANCH = topconf-dl-robustness
MAINLINE_HEAD = ad44f6b29db1930e039c57f8b5412854e8349e3f
REMOTE_HEAD_AT_HANDOFF = 110e2b91c04625898b955c0d0dfcfccfe04515cb
WORKTREE = clean
V3_POPULATION_MODIFIED = NO
```

The candidate-selection commit is
`3fa5ce5984c01f1feb75f931c0c00c57c0f00872`; the V3/V4 artifact commit is
`a242295444e1f2cdf78c1d8d3a2a662a111d6fd0`; the Phase4.9 closure commit is
`ad44f6b29db1930e039c57f8b5412854e8349e3f`. No reset, rebase, amend of old
scientific commits, or force push was used.

## Frozen artifacts

```text
V3_POPULATION_MANIFEST = research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V3.json
V3_POPULATION_INTERNAL_MANIFEST_SHA256 = 89834D9F85603727EE5E6F482C9BAC9832283EAF1902976FD31975AF61FCE78B
V3_POPULATION_FILE_SHA256 = AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4
V4_FRESHNESS_MANIFEST = research_assurance/topconf/LEVEL2_FRESHNESS_MANIFEST_V4.json
V4_FRESHNESS_INTERNAL_MANIFEST_SHA256 = 973002F7112B1A51F803C24817321BC2CF23BD814B1DBD673F6BFA85DA6FC4C6
V4_FRESHNESS_FILE_SHA256 = 9DFAEB6A699F7463914F6A91047A8A638C68C3C6439FD874616D3F2E5FF6D1F3
V4_FRESHNESS_STATUS = INSUFFICIENT_EVIDENCE
V4_FAILURE_REASON = all four historical exclusion universes remain PARTIAL; zero observed overlap cannot authorize PASS
```

## Frozen policy files

- `research_assurance/topconf/PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`
- `research_assurance/topconf/TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`
- `research_assurance/topconf/PHASE4_HUMAN_RECONCILIATION_AND_DESIGN_FREEZE_CLOSURE.md`
- `research_assurance/topconf/PHASE4_7_HISTORICAL_EXCLUSION_AND_FRESHNESS_CLOSURE.md`
- `research_assurance/topconf/PHASE4_9_FROZEN_FRESHNESS_REQUIREMENT_EXTRACT_V1.md`

## Historical universe files

- `HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json` — `PARTIAL`, 43,311 records
- `HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json` — `PARTIAL`, 317 records
- `HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json` — `PARTIAL`, 169 records
- `HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json` — `PARTIAL`, 317 records
- `HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json` — 19 stages, explicit PARTIAL/UNKNOWN statuses
- `HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json` — audited search/evidence index

## Corpus provenance

```text
ALIMEETING_PROVENANCE = PHASE4_9_ALIMEETING_PROVENANCE_BUNDLE_V1.json
AISHELL1_PROVENANCE = PHASE4_9_AISHELL1_PROVENANCE_BUNDLE_V1.json
SOURCE_POOL_INDEPENDENCE = LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json
ALIMEETING_SOURCE_MODE = near-field speaker recording, mono channel, TextGrid speaker-tier boundary; far package used for TextGrid only
ALIMEETING_SOURCE_MODE_FROZEN = YES
ALIMEETING_DISTRIBUTION_COMPATIBILITY = AMBIGUOUS_PENDING_INDEPENDENT_AUDIT
```

The selected AliMeeting primary/reserve rows are 200/20 across 60 speakers
and 20 meetings. A read-only TextGrid comparison found other-speaker interval
overlap in 175 of 220 Pool-A rows; this was not filtered after selection and is
presented as a source-semantics question for the auditor.

## Validator trace and known blocker

```text
VALIDATOR_PATH = tools/topconf/validate_level2_freshness.py
VALIDATOR_IMPLEMENTATION = src/audiobookbench/topconf/level2/materialization.py::validate_level2_freshness_v3
VALIDATOR_DECISION_TRACE = PHASE4_9_FRESHNESS_VALIDATOR_DECISION_TRACE_V1.md
KNOWN_BLOCKER = incomplete historical exclusion universes cause fail-closed INSUFFICIENT_EVIDENCE
```

The mainline has not modified the production validator, rerun real V4 under an
alternative rule, or created a V5 manifest. The auditor must distinguish the
global-completeness question from the corpus-specific freshness question and
return exactly one allowed verdict:

```text
TRUE_EVIDENCE_GAP
VALIDATOR_OVERCONSTRAINT
FROZEN_POLICY_AMBIGUITY
ADDITIONAL_NON_FRESHNESS_BLOCKER
```

## Firewall state

```text
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
SCIENTIFIC_METRICS_COMPUTED = 0
LD_DR95_COMPUTED = NO
RQ1_STARTED = NO
RQ2_STARTED = NO
RQ3_STARTED = NO
```

## Requested audit output

Please bind the verdict to the audit base commit and report:

```text
INDEPENDENT_AUDIT_BRANCH
INDEPENDENT_AUDIT_HEAD
AUDIT_VERDICT
AUDIT_BASE_COMMIT
POLICY_CITATIONS
EXACT_VALIDATOR_LOGIC_IF_OVERCONSTRAINT
AUDIT_REPORT_SHA256
SCIENTIFIC_PROTOCOL_CHANGED = NO/YES
POPULATION_CHANGED = NO/YES
OUTCOMES_ACCESSED = NO/YES
```

