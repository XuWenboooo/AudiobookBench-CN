# TopConf RQ1 confirmatory preregistration amendment v1

Status: `PROSPECTIVE_GOVERNANCE_CLARIFICATION / SCIENTIFIC_CORE_UNCHANGED`

## Parent binding

```text
PARENT_PREREGISTRATION = TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md
PARENT_PREREGISTRATION_SHA256 = 91BB6BE78BFBFF948C7B2559AFDC7ED6F3A87BA116BDC59807D1194B15BB115C
TRIGGER = FROZEN_POLICY_AMBIGUITY_IDENTIFIED_BY_INDEPENDENT_AUDIT
AMENDMENT_TYPE = PROSPECTIVE_GOVERNANCE_CLARIFICATION
POLICY_SOURCE = PHASE4_9R_FRESHNESS_POLICY_CLARIFICATION_V1.md
```

This amendment is part of the preregistration provenance chain and must not
overwrite the parent preregistration. It clarifies only freshness-proof
semantics that the parent text left unresolved. It is effective for future
freshness decisions and is not an outcome-driven reinterpretation.

## Clarified freshness rule

The confirmatory freshness objective remains that Level-2 assets must not have
participated in hypothesis, model, metric, threshold, Whether-rule, or other
confirmatory design decisions. Two evidence paths are legal:

1. `PATH_A_HISTORICAL_EXCLUSION`: relevant historical case/source/speaker/
   lineage universes must be complete and comparison-known.
2. `PATH_B_PROSPECTIVE_PROJECT_ENTRY`: a candidate pool may use a strong,
   positively bound post-freeze project-entry proof when the proof establishes
   that the asset could not have participated in earlier project decisions.

Path B requires a unique corpus/archive identity, official provenance, exact
hash/version binding, first Git/manifest/project-use references, repository-
wide history search, alias/path/archive-name coverage, no prior scientific
project usage, post-freeze timing support, and asset-lineage binding. A single
filesystem timestamp is never sufficient.

Relevance is evaluated per candidate pool and per required historical
universe. `DIRECTLY_RELEVANT` and `POTENTIALLY_RELEVANT` require Path A.
`IRRELEVANT_BY_CORPUS_IDENTITY` requires explicit identity evidence.
`IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY` requires the complete Path-B
strong gate. `UNKNOWN` is fail-closed `INSUFFICIENT_EVIDENCE`.

## Verdict precedence

The following precedence is binding:

```text
VERIFIED_PRIOR_USAGE_FOUND or PROHIBITED_OVERLAP
  -> FAIL
PROVENANCE_CONTRADICTION or CRITICAL_IDENTITY_LINEAGE_CONFLICT
  -> FAIL
STRONG_PATH_B for every candidate pool, no prior use, no contradiction,
and every required universe explicitly irrelevant for that pool
  -> PASS
Otherwise, complete relevant historical proof under Path A
  -> PASS
Critical missing/unknown/incomplete/unbound evidence
  -> INSUFFICIENT_EVIDENCE
```

`FAIL_PRIOR_USAGE_FOUND` therefore cannot be bypassed by `PARTIAL`, `UNKNOWN`,
zero observed overlap, or a post-freeze project-entry claim.

## AliMeeting channel-semantic binding

The existing V3 selection remains bound to the near-field participant-headset
speaker recording, rendered as mono 16 kHz PCM. AliMeeting far-field 8-channel
audio is excluded. This field freezes machine-readable interpretation of the
existing V3 artifact; it does not change the selected distribution or input
mode.

## Scientific core invariants

```text
HYPOTHESIS_CHANGED = NO
PRIMARY_ENDPOINT_CHANGED = NO
METRIC_CHANGED = NO
SAMPLE_SIZE_CHANGED = NO
POPULATION_CHANGED = NO
MODEL_CHANGED = NO
MECHANISMS_CHANGED = NO
TRANSFORMATIONS_CHANGED = NO
STATISTICS_CHANGED = NO
WHETHER_RULE_CHANGED = NO
```

```text
SCIENTIFIC_OUTCOMES_USED = NO
LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
RESULT_BASED_DESIGN_CHANGES = 0
```

The amendment must precede the production validator patch. It does not
authorize Level-2 inference, evaluation, RQ1 execution, RQ2, or RQ3.
