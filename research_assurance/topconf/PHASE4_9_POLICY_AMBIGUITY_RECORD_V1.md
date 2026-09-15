# Phase 4.9 Frozen-Policy Ambiguity Record v1

Date: 2026-09-15
Status: **CLOSED FOR THIS REVIEW / NO_GO / DO NOT AUTHORIZE**

## Independent audit binding

```text
AUDIT_VERDICT = FROZEN_POLICY_AMBIGUITY
AUDIT_BRANCH = topconf-phase4-9-freshness-audit
AUDIT_HEAD = 58e036d
AUDIT_BASE_COMMIT = 110e2b91c04625898b955c0d0dfcfccfe04515cb
AUDIT_INTEGRATED_MAINLINE_COMMIT = 19bfaeb6062ba4417975b1215fa0b5395b17e0ff
AUDIT_REPORT = PHASE4_9_INDEPENDENT_FRESHNESS_SEMANTICS_AUDIT_V1.md
AUDIT_MATRIX = PHASE4_9_HISTORICAL_UNIVERSE_RELEVANCE_MATRIX_V1.md
AUDIT_SYNTHETIC_TESTS = tests/topconf/test_phase4_9_freshness_semantics_audit.py
```

The mainline reviewed the audit commit with `git show` and `git diff` before
integration. It contains only the audit report, historical-relevance matrix,
and diagnostic tests. No population, protocol, production validator, dataset,
model output, or scientific result was integrated.

## Ambiguous frozen-policy clause

The frozen design requires a materialized freshness proof before authorization
and names the historical sets that must not contribute cases or lineages. It
does not explicitly answer either of these questions:

1. Must every historical case/source/speaker/lineage exclusion universe be
   globally `COMPLETE` before any corpus can pass freshness?
2. Can a cryptographically bound, post-freeze project-entry proof for a new
   corpus discharge an incomplete historical universe when the available keyed
   records are corpus-irrelevant and show zero direct overlap?

The selected AliMeeting and retained AISHELL-1 proofs provide exact archive
identities, post-freeze project-boundary evidence, and negative project-history
searches. The frozen policy does not state that these proofs are an authorized
substitute for unresolved historical ledgers. The absence of that statement is
the ambiguity; it is not interpreted as permission on the mainline.

The audit also identified a related policy/implementation boundary: an
isolation record with `FAIL_PRIOR_USAGE_FOUND` is currently accepted as a
structurally valid status by the production validator, and a complete,
zero-overlap synthetic case can return `PASS`. A future governance amendment
must explicitly make confirmed prior use a hard `FAIL`; this record does not
patch the validator.

## Competing interpretations

| Interpretation | Freshness consequence | Mainline disposition |
|---|---|---|
| Strict historical completeness | Every required universe must be complete; V4 `INSUFFICIENT_EVIDENCE` is correct and remains `NO_GO`. | Not changed; remains valid under the current conservative reading. |
| Prospective boundary exception | A post-freeze, exact project-entry proof may discharge an unrelated incomplete universe after corpus-level relevance checks. | Plausible but not written in the frozen policy; requires a prospective amendment before use. |
| Automatic post-freeze freshness | Post-freeze acquisition alone automatically substitutes for historical exclusion. | Unsupported by the frozen text; rejected. |
| Prior-use status as non-blocking metadata | `FAIL_PRIOR_USAGE_FOUND` can coexist with PASS if no keyed overlap is found. | Unsafe; must not be adopted. |

These alternatives have different false-freshness and auditability implications.
The mainline must not choose among them by editing V3, changing the validator,
or observing Level-2 outcomes.

## Scientific and governance consequences

- Under the strict reading, the V4 `INSUFFICIENT_EVIDENCE` result blocks
  confirmatory authorization, so no Level-2 scientific result can be claimed.
- Under a future boundary-exception reading, the exact scope of the exception,
  required relevant universes, prior-use failure semantics, and machine-readable
  channel identity would become prospective governance fields. This could
  change authorization eligibility without changing the frozen V3 population;
  it must not be introduced retroactively after outcomes.
- Treating `FAIL_PRIOR_USAGE_FOUND` as non-blocking would create a false-freshness
  risk and is not an acceptable shortcut.
- The AliMeeting source-mode audit itself was `PASS`: V3 uses near-field mono
  speaker recordings and not far-field eight-channel audio. That compatibility
  result does not resolve the historical-policy ambiguity.

## Required next action and stop state

```text
REQUIRED_NEXT_ACTION = separate prospective governance amendment
AMENDMENT_MUST_DEFINE =
  post-freeze project-entry substitution rule;
  mandatory historical universes and relevance scope;
  FAIL_PRIOR_USAGE_FOUND => FAIL;
  machine-readable AliMeeting near-field participant-headset mono semantics
PRODUCTION_VALIDATOR_MODIFIED = NO
V3_POPULATION_MODIFIED = NO
NEW_CORPUS_SEARCH = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
SCIENTIFIC_METRICS_COMPUTED = 0
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
RQ2_STARTED = NO
RQ3_STARTED = NO
READY_FOR_RQ1_FINAL_AUTHORIZATION_REVIEW = NO
```

No V5 freshness manifest, validator patch, population change, or confirmatory
run is permitted from this record. Any continuation requires the prospective
governance amendment and a new explicit review.
