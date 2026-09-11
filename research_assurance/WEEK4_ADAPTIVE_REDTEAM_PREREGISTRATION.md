# AudiobookBench-CN — Week4 adaptive red-team preregistration

Date: 2026-09-11
Status: `PREREGISTRATION_STATUS = FROZEN_BEFORE_FORMAL_EXECUTION`

`H4_SCIENTIFIC_RESULT_OBSERVED = NO`
`FORMAL_WEEK4_EXECUTION = NOT STARTED`

Canonical config SHA-256: `1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D`.

This is the sole scientific source of truth for Week4.  It is prospective and
does not reopen Week3, reinterpret Week1–3 results, or authorize any generation,
adaptive search, validation run, held-out run, or H4 result computation.

## 1. Question and fixed systems

Primary question: under a frozen detector D0, fixed population, fixed black-box
query budget, and predefined waveform-validity constraints, does a bounded
adaptive attacker reduce temporal localization performance more than the static
comparator?

- Defender `D0`: frozen `B1b` on `S2_1500ms_250ms` (1500 ms window, 250 ms hop).
  No detector training, fine-tuning, checkpoint change, threshold tuning, score
  normalization, score direction, window, or stride change is allowed.
- Generator `G0`: `F5-TTS v1 Base`, source commit
  `82fc4fe622fe36047d1dff99b550e6018181ea11`, model revision
  `84e5a410d9cead4de2f847e7c9369a6440bdfaca`.
- Week4 has an independent namespace, authorization, accounting and evidence.
  Week3 waveforms may not be copied forward.

## 2. Population and governance

The target population is 48 speaker-disjoint cases: DEV 24, VALIDATION 12, and
HELD_OUT 12.  Selection seed is `20260912`; each case uses same-speaker,
different-utterance, different-text source/reference material and retains an
exclusion ledger plus input hashes.  Week1–3 scientific speakers are excluded.
If that exclusion prevents a valid 48-case population, execution stops and the
available population is reported; the rule may not be relaxed.

The repository currently contains only a candidate-population builder.  No real
population has been selected or finalized.  It never imports or invokes D0.

DEV permits engineering debugging and the already-frozen search mechanics.
VALIDATION may use only the frozen choices below; after it completes,
`A0_FROZEN = YES`.  HELD_OUT may run only the same frozen A0, never a tuning
phase.  Once held-out D0 output is observed, no bounds, objective, search, seed,
validity rule, query budget, hyperparameter, or primary metric may change.

## 3. Static comparator and insertion rule

`A_STATIC` is the sole deterministic comparator:

- insertion position: middle of the source active interval, rounded down;
- mono 16 kHz construction, no channel post-processing;
- 400-sample linear insertion crossfade and 0.0 dB synthetic gain;
- sample-first deterministic ground truth.

Insertion position is not an adaptive dimension.

## 4. A0 attack space and validity

`A0 = ADAPTIVE_BOUNDED_POSTPROCESSING_CONTROLLER`.  It does not train a new
TTS model.  The only adaptive factors are:

| Parameter | Meaning / unit | Grid | Default | Deterministic operation |
| --- | --- | --- | --- | --- |
| `insertion_crossfade_samples` | boundary blend duration, samples at 16 kHz | 160–400, step 80 | 400 | linear insertion crossfade; integer grid and sample-first GT |
| `synthetic_gain_db` | local synthetic-region gain, dB | -3.0–3.0, step 0.5 | 0.0 | multiply synthetic region before crossfade; finite peak must not exceed 0.999 |

Every candidate must be mono, 16 kHz, finite, free of NaN/Inf, natural-duration
without crop/pad/time-stretch, and preserve text/content, generator-output,
source/reference identities.  Only the two listed transformations are allowed.
Invalid candidates retain parameters and failure reason in the ledger, never
become winners, and do not justify changing the grid.

## 5. Query budget and deterministic adaptive algorithm

`MAX_ADAPTIVE_D0_QUERIES_PER_CASE = 40`.  Every actual D0 invocation counts,
including a failed invocation.  A pre-invocation invalid waveform does not count.
Crash/restart loads the hash-chained candidate ledger and cannot reset the
budget.  Query 41, hidden diagnostic calls, and manual extra calls fail closed.
`A_STATIC` has exactly one separately-accounted D0 evaluation per case and does
not consume the 40 adaptive queries.

A0 uses a fixed 8-candidate × 5-generation search (40 queries):

- seed: `20260913`, derived per case with SHA-256 and NumPy PCG64;
- generation 0: seeded grid proposals without replacement;
- generations 1–4: one-step symmetric mutation from the valid candidate with
  lowest objective, then lowest query index as tie-break;
- mutation scale: one parameter-grid step; clipping is to frozen grid bounds;
- duplicates: lexicographically first unseen grid point; exhausted grid stops
  fail-closed; no early stopping;
- same config, case, seed and ledger history produce exactly one next proposal.

The next proposal therefore depends on earlier D0 outcomes after generation 0;
this is an adaptive black-box controller, not best-of-N generation.

## 6. Objective, hypothesis, estimands and uncertainty

Higher D0 scores mean more anomalous.  The candidate-level attacker objective is

`J = mean(score in FULL_ATTACK) - mean(score in OUTSIDE_CLEAN)`.

A0 minimizes `J`; D0 score direction itself is never inverted or normalized.

H4: with frozen D0, the same held-out population, the fixed 40-query budget and
these validity constraints, A0 reduces temporal localization performance versus
A_STATIC.

Primary estimand:

`DELTA_ADAPTIVE_AUROC = AUROC_STATIC - AUROC_ADAPTIVE`.

Companion estimand:

`DELTA_ADAPTIVE_AUPRC = AUPRC_STATIC - AUPRC_ADAPTIVE`.

Positive values favor H4; null and negative values remain valid outcomes.  The
case-level paired bootstrap uses identical resampled paired-case IDs for both
conditions, `N=2000`, seed `20260911`, 95% percentile CI, and at least 1900
finite draws.

## 7. Failure/retry policy and authorization

Failure classes are `infrastructure_transient`, `infrastructure_terminal`,
`candidate_invalid`, `authorization_failure`, `query_budget_violation`,
`data_identity_failure`, `detector_runtime_failure`, and
`ledger_integrity_failure`.  Only a transient failure before D0 invocation may
retry; all other listed failures are non-retryable.  A failed invoked D0 query
still consumes budget and is ledgered.

The future formal path requires a valid active Week4 authorization bound to the
canonical config hash and A0 freeze hash before waveform construction or detector
runtime.  This document creates no authorization.  CLI may provide only config,
authorization and runtime paths; scientific flags are not CLI inputs.

## 8. Canonical executable binding

The canonical executable specification is
`configs/week4_adaptive_red_team.yaml`; its JSON Schema is
`configs/week4_adaptive_red_team.schema.json`.  The controller,
candidate-population builder and synthetic tests must conform to this document.
Any modification after a held-out outcome requires a separately preregistered
study, not an amendment to Week4 v0.
