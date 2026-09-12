# Week4 execution-governance amendment V2

## Status and provenance

```text
AMENDMENT_STATUS = FROZEN_AFTER_PARTIAL_DEV_OBSERVATION_BEFORE_VALIDATION
PRIOR_DEV_OUTCOMES_OBSERVED = YES
PRIOR_VALIDATION_OUTCOMES_OBSERVED = NO
PRIOR_HELD_OUT_OUTCOMES_OBSERVED = NO
PRIOR_H4_OUTCOME_OBSERVED = NO

EXECUTION_GOVERNANCE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION = YES
ATTACK_METHOD_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION = NO
OBJECTIVE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION = NO
SEARCH_PROPOSAL_RULE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION = NO
H4_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION = NO
HELDOUT_OBSERVED_BEFORE_AMENDMENT = NO
```

This amendment was frozen after the consumed
`week4_dev_integrity_reexecution_02` DEV execution exposed
`NO_VALID_ADAPTIVE_PARENT` at case 0004.  It is not a prospective
before-all-Week4-outcomes preregistration.  Its post-observation provenance is
a permanent limitation for any future report or paper.

## Scope

The amendment separates two independent findings:

```text
NO_VALID_ADAPTIVE_PARENT = FROZEN_EXECUTION_GOVERNANCE_UNDERSPECIFIED
CANDIDATE_WAVEFORM_SHA_MISMATCH = EVIDENCE_CANONICALIZATION_IMPLEMENTATION_DEFECT
```

The first is not a detector failure, waveform failure, candidate-invalid
failure, or simple implementation typo.  The second is corrected by one
canonical evidence representation and is not a scientific-method amendment.

The following remain byte-level or semantic scientific freezes:

- H4, its primary and companion estimands, 48/24/12/12 population, generator,
  F5 parameters and seeds;
- insertion position and waveform construction, A_STATIC, A0 grids, D0/B1b,
  S2, J, score direction, GT projection, held-out evaluator, and bootstrap;
- generation-0 proposals, mutation after a valid parent exists, and the
  40-query maximum.

```text
ATTACK_METHOD_CHANGED = NO
OBJECTIVE_CHANGED = NO
SEARCH_PROPOSAL_RULE_CHANGED = NO
H4_CHANGED = NO
POPULATION_CHANGED = NO
SCIENTIFIC_ATTACK_AND_ESTIMAND_SPEC_CHANGED = NO
EXECUTION_GOVERNANCE_AMENDED = YES
```

## Frozen no-valid-parent rule

For every case, execute the eight frozen generation-0 adaptive proposals.
When at least one has a finite J with
`objective_status=DEFINED` and `valid_for_winner=true`, continue the existing
frozen A0 search unchanged.  Parent selection remains: lowest finite objective,
then lower `query_index`, then lexical `candidate_id`.

When all eight generation-0 candidates complete D0 successfully with
`objective_status=OBJECTIVE_UNDEFINED`, do not create a fallback parent.  In
particular, a lexical, random, raw-B1b, first-candidate, static-candidate, or
manual parent is prohibited.  The case records:

```text
ADAPTIVE_CASE_STATUS = NO_VALID_ADAPTIVE_PARENT
ADAPTIVE_SEARCH_TERMINAL = YES
ADAPTIVE_D0_QUERIES_CONSUMED = 8
ADAPTIVE_WINNER = NONE
REMAINING_32_QUERIES = NOT_EXECUTED_STRUCTURALLY_UNAVAILABLE
```

This is structural termination due to absence of a defined parent, not an
early-stopping optimization, retry budget, or transferable query allocation.
It depends only on whether any generation-0 objective is defined, never on an
objective magnitude.

```text
NO_VALID_PARENT_TERMINATES_CASE = YES
NO_VALID_PARENT_TERMINATES_STAGE = NO
CASE_TERMINAL != RUN_TERMINAL
```

Whole-run termination remains reserved for authorization, source identity,
ledger integrity, implementation-hash, actual-versus-accounted-D0, scientific
mutation, or unrecoverable frozen-policy infrastructure failures.

## Split and denominator governance

All 24 DEV cases must reach either `DEV_CASE_COMPLETE_WITH_WINNER` or
`DEV_CASE_TERMINAL_NO_VALID_ADAPTIVE_PARENT`.  No replacement or denominator
drop is allowed.  Validation likewise retains and discloses every terminal
no-parent case and continues all 12 cases without changing A0.

Held-out likewise attempts all 12 cases.  If any held-out case has no adaptive
winner, including `NO_VALID_ADAPTIVE_PARENT`, then:

```text
PRIMARY_H4 = NOT_REPORTABLE
REASON = HELD_OUT_NOT_12_OF_12_PAIRED_COMPLETE
```

The runner must still complete remaining held-out cases for failure accounting.
It must not replace or drop the case, substitute static, choose an arbitrary
adaptive candidate, change J, or rerun seeking a winner.

## Canonical waveform evidence hash

The sole candidate waveform hash is
`canonical_waveform_sha256(waveform)` over:

```python
np.ascontiguousarray(waveform, dtype=np.float32).tobytes(order="C")
```

It is used identically by the candidate ledger, sidecar, and their evidence
consistency check.  Score-vector hashing remains distinct: C-contiguous
`float64` raw score bytes.  This repairs evidence canonicalization only; it
does not alter the float32 scientific candidate waveform.

## Applicability

This amendment does not make reexecution 02 admissible, resumable, or an input
to any later execution.  A future execution requires separately hash-bound
authorization and an unused namespace.
