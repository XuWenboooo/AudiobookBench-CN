# Phase 4.9R prospective freshness-policy clarification v1

Status: `PROSPECTIVE_GOVERNANCE_CLARIFICATION / COMMITTED_BEFORE_VALIDATOR_REPAIR`

This document resolves the policy question identified by the independent Phase
4.9 audit before any alternative freshness validator is run on the real V3
population. It does not change the scientific protocol core, the V3
population, source pools, sample sizes, mechanisms, transformations, metrics,
thresholds, Whether rules, or statistics.

## Governance binding

```text
AMENDMENT_TYPE = PROSPECTIVE_GOVERNANCE_CLARIFICATION
TRIGGER = FROZEN_POLICY_AMBIGUITY_IDENTIFIED_BY_INDEPENDENT_AUDIT
SCIENTIFIC_OUTCOMES_USED = NO
LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
POPULATION_CHANGED = NO
SCIENTIFIC_DESIGN_CHANGED = NO
GOVERNANCE_POLICY_CLARIFIED = YES
EFFECTIVE_SCOPE = PROSPECTIVE_FRESHNESS_DECISIONS_ONLY
```

The clarification answers:

> How should post-freeze project-entry evidence interact with historical
> exclusion completeness under the frozen freshness objective?

It does not answer “how can we make AliMeeting pass?” and it creates no
corpus-specific exception. The same rules apply to every candidate corpus and
pool.

## Objective preserved

The freshness objective remains unchanged: Level-2 confirmatory assets must not
have participated in forming the hypothesis, model choice, metric choice,
threshold, Whether rule, or any other confirmatory design decision. A missing
historical record is never converted to “fresh” by assumption. A post-freeze
entry path is allowed only because positive provenance evidence establishes
that the candidate asset could not have participated in earlier project
decisions within the audited project boundary.

The policy remains fail-closed for critical identity, lineage, overlap, and
provenance contradictions.

## Two legal evidence paths

### Path A — Historical Exclusion Proof

Path A applies when a corpus or asset existed in the project before the
relevant design freeze, when project-entry timing cannot be strongly
established, or when the candidate does not qualify for Path B.

For every historical universe that is `DIRECTLY_RELEVANT` or
`POTENTIALLY_RELEVANT` to a candidate pool, the required case/source/speaker/
lineage exclusion evidence must be `COMPLETE` or
`COMPLETE_EXCLUSION_EMPTY`; comparisons must be known; and the case, source,
lineage, and declared speaker-overlap policies must pass. A critical
`UNKNOWN` relevance classification is insufficient evidence, even when the
observed comparison count is zero.

An `IRRELEVANT_BY_CORPUS_IDENTITY` classification may discharge a universe
only when the corpus identity and the classification evidence are explicit,
the classification is not based on an incomplete alias search, and no
contradictory prior-use or overlap evidence exists.

### Path B — Prospective Project-Entry Proof

Path B applies to a candidate pool only when its assets can be strongly
demonstrated to have first entered the scientific project after the relevant
design freeze. Path B is an evidence route, not an assumption that incomplete
history is harmless.

A Path-B record is `STRONG` only when all of the following checks are present,
positive, and bound to the same candidate corpus/archive identity:

```text
UNIQUE_CORPUS_ARCHIVE_IDENTITY
OFFICIAL_SOURCE_PROVENANCE
ARCHIVE_OR_FILE_HASH
FIRST_GIT_REFERENCE
FIRST_MANIFEST_REFERENCE
FIRST_PROJECT_USE_REFERENCE
REPOSITORY_WIDE_HISTORICAL_SEARCH
ALIAS_PATH_ARCHIVE_SEARCH
NO_PRIOR_SCIENTIFIC_PROJECT_USAGE
ACQUISITION_PROJECT_ENTRY_TIMING
ASSET_LINEAGE_BOUND_TO_ARCHIVE_IDENTITY
```

No single filesystem creation time, mtime, ctime, copy time, or archive member
timestamp can satisfy the strong gate. Filesystem timing is supporting
evidence only. The primary evidence is the combination of Git history,
project manifests, project-use logs, provenance records, exact corpus/archive
identity, hashes/version binding, and documented alias/path/archive-name
coverage.

For a Path-B candidate pool, a historical universe may be classified
`IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY` when the strong record proves
that the bound asset could not have participated in earlier project decisions.
That classification may discharge `PARTIAL` or `UNKNOWN` completeness for that
pool/universe. It does not discharge a direct overlap, a provenance
contradiction, verified prior use, or an `UNKNOWN` identity that prevents
binding the candidate asset to the proof.

The validator must evaluate this classification per candidate pool and per
historical universe. It must not use a global “any universe is PARTIAL” rule
when every affected candidate/universe relationship is explicitly irrelevant
under Path B. It must also not grant Path B because a corpus name merely
appears after the freeze.

## Historical-universe relevance classes

The machine-readable field `historical_universe_relevance` maps each candidate
`pool_id` to each required V3 universe. The only permitted values are:

```text
DIRECTLY_RELEVANT
POTENTIALLY_RELEVANT
IRRELEVANT_BY_CORPUS_IDENTITY
IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY
UNKNOWN
```

Decision rules:

| Classification | Required evidence consequence |
|---|---|
| `DIRECTLY_RELEVANT` | Path A; universe complete, comparisons known, and identity/lineage policy passes. |
| `POTENTIALLY_RELEVANT` | Path A; universe complete, comparisons known, and identity/lineage policy passes. |
| `IRRELEVANT_BY_CORPUS_IDENTITY` | Explicit corpus identity proof and no contradiction; no completeness shortcut from an unproven classification. |
| `IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY` | Path B strong gate, no prior use, bound lineage, no contradiction; incomplete unrelated history may be discharged. |
| `UNKNOWN` | `INSUFFICIENT_EVIDENCE`; never treated as zero or irrelevant. |

If any pool has a critical `UNKNOWN` classification, the result is
`INSUFFICIENT_EVIDENCE`. If a universe is relevant to any pool and is not
complete, the result is `INSUFFICIENT_EVIDENCE` unless a separate explicit
Path-B classification for that same pool/universe satisfies the strong gate.

## Verdict precedence

The validator must apply this order, before checking a declared verdict:

```text
1. VERIFIED_PRIOR_USAGE_OR_PROHIBITED_OVERLAP
   -> FAIL

2. PROVENANCE_CONTRADICTION_OR_CRITICAL_IDENTITY_LINEAGE_CONFLICT
   -> FAIL

3. STRONG_PATH_B_FOR_EVERY_CANDIDATE_POOL
   + no prior scientific use
   + no contradiction
   + every required universe is explicitly irrelevant by corpus identity or
     strong post-freeze entry for that pool
   -> PASS

4. PATH_A
   + every relevant universe is COMPLETE or COMPLETE_EXCLUSION_EMPTY
   + all comparisons are known
   + no prohibited overlap
   -> PASS

5. Any critical evidence missing, unknown, incomplete, or unbound
   -> INSUFFICIENT_EVIDENCE
```

`FAIL_PRIOR_USAGE_FOUND` or an equivalent verified prior scientific-use
finding has highest priority over every other proof path. It must produce
`FAIL`, even when all historical universes are complete, even when they are
partial or unknown, and even when a post-freeze claim is also present.

A project-entry proof that conflicts with Git, manifest, log, provenance, or
identity evidence is `PROVENANCE_CONTRADICTION` and produces `FAIL`; it must
never be converted to `PASS` by Path B.

## Required V3 freshness-manifest fields

The V3 population file remains byte-identical. A new freshness manifest may
carry these policy fields without changing the population:

```json
{
  "freshness_policy_id": "PHASE4_9R_FRESHNESS_POLICY_CLARIFICATION_V1",
  "freshness_evidence_path": "PATH_A_HISTORICAL_EXCLUSION | PATH_B_PROSPECTIVE_PROJECT_ENTRY | MIXED",
  "historical_universe_relevance": {
    "<pool_id>": {
      "<V3_UNIVERSE>": "<relevance class>"
    }
  },
  "corpus_isolation": [
    {
      "pool_id": "<pool_id>",
      "path": "PATH_A_HISTORICAL_EXCLUSION | PATH_B_PROSPECTIVE_PROJECT_ENTRY",
      "proof_strength": "STRONG | NOT_STRONG",
      "prior_use_status": "NO_PRIOR_PROJECT_USAGE_FOUND | FAIL_PRIOR_USAGE_FOUND | UNKNOWN",
      "project_entry_after_freeze": true,
      "proof_checks": ["...all eleven checks for STRONG..."],
      "asset_lineage_binding": "BOUND | UNBOUND",
      "channel_semantics": {
        "channel_type": "...",
        "audio_rendering": "...",
        "far_field_8ch_included": false
      }
    }
  ]
}
```

The validator may accept legacy V3/V4 manifests under the original global
fail-closed rule, but a manifest claiming the clarified Path-B semantics must
carry and satisfy the fields above. A missing policy field is not permission
to infer Path B.

For the existing AliMeeting V3 population, the frozen channel semantics are
`NEAR_FIELD_PARTICIPANT_HEADSET`, `MONO`, 16 kHz PCM, and
`far_field_8ch_included = false`. This records the existing selection; it does
not reopen input-mode selection or alter V3.

## Scientific-design invariants

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

The amendment is prospective governance clarification only. It must be
committed before the production validator repair and before any real V3
freshness rerun. V4 remains an immutable historical record; V5 is the only
manifest produced by the reconciled validator.
