# WEEK 2 — DAY 10 FROZEN PILOT PRE-REGISTRATION (A2 23-case pilot)

Status: PRE-REGISTERED. Day 10 executes the frozen pilot exactly as
recorded here; any deviation requires an amendment record before running.

## 1. Planned case count and distribution (frozen in the corrected config)

- **23 planned cases**, one A2-V generation per case (`generations_per_case: 1`).
- Inheritance from Week 1 lineage only: `paired_case_id`,
  `target_source_sample_id`, target speaker, split, clean sequence id
  (11 train / 6 val / 6 test; 12 speakers 6/3/3; 23 unique transcripts).
- The one Week-1 clean sequence without a frozen paired target stays
  excluded (preserves pre-outcome target selection).
- Week-1 interval fields (target/attack bounds, duration tiers 0.75/1.5/2.5,
  donor crops) are **forbidden** as A2 bounds or duration metadata.
- Feasibility was pre-audited: 23 unique lineage rows, 23 unique complete
  transcripts, valid 3–8 s reference candidate for every speaker
  (pre-implementation audit §8). Day 10 does not re-litigate the plan.

## 2. Speaker / split distribution

Exactly the Week-1 distribution carried through lineage: train 11 cases
(6 speakers), val 6 (3 speakers), test 6 (3 speakers). No re-balancing, no
speaker swaps, no split changes — outcome-independent by construction.

## 3. Case retention policy

- Every planned row is retained whatever happens (success or any failure
  class from `A2_FAILURE_TAXONOMY.md`).
- No substitution, no re-donation, no re-texting, no quality-based retry
  (best-of-n and quality-driven retry are forbidden by config).
- Infrastructure retry: max 1, identical inputs/seed/environment, both
  attempts logged.
- Realized denominators (planned/succeeded/failed per class, per split,
  per speaker) are mandatory in every report.

## 4. Generation order (deterministic)

- Order: ascending `paired_case_id` (one-based index feeds the seed rule
  `generation_seed = 20260905 + index`).
- The order is fixed before Day 10 and independent of any outcome.
- Failures do not reorder or skip; the pipeline continues to the next case
  and the failed row is retained.

## 5. Determinism

- One seed per case per the frozen rule; identical inputs must reproduce
  identical outputs (determinism probe recorded at Day 9).
- The single permitted infrastructure retry reuses the identical seed.
- If `DETERMINISM_MISMATCH` occurs, it is disclosed and the pilot proceeds
  on recorded outputs (no silent re-rolls, no seed shopping).

## 6. Hash freeze

At Day-10 close, before any evaluation:

1. SHA-256 of every A2 output WAV + the serialized sidecar
   (`day10_output_hashes.json`);
2. SHA-256 of the generator checkpoint/components + pipeline code snapshot
   (completing the `TO_BE_VERIFIED_BEFORE_IMPLEMENTATION` fields);
3. SHA-256 of the frozen reference audio per speaker;
4. a fresh Week-1 `--verify-only` run (696/696) to prove no back-contamination;
5. the Day-10 freeze record appended to the week1/hash chain as a new
   additive record (no existing hash edited).

## 7. No-score-based filtering (restated as a hard rule)

Day-10 freeze happens **before** any detector or diagnostic score exists
for the pilot outputs. ASR CER, ECAPA similarities and B-scores are
computed later (Day 11/12), are DIAGNOSTIC ONLY, and can never: exclude a
case, trigger regeneration, reorder the pilot, or select a subset for
analysis. The only post-freeze per-case state transitions are failure-class
assignments already defined in the taxonomy.

## 8. Plan-sanity review (no execution)

The 23-case plan is reasonable against the existing lineage: exactly one
frozen paired target per case; 23 unique complete source utterances with
exact transcripts; every speaker has a frozen 3–8 s reference candidate;
speaker/split coverage mirrors Week 1 exactly. Natural whole-utterance
durations (≈3–10 s typical for AISHELL-3) give substantially more
synthetic core per case than the Week-1 0.75–2.5 s crops, so the S2
strict-core unmeasurability problem of Week 1 is not expected here — but
that is an expectation, not a result.

## 9. Forbidden in Day 10

Running evaluation on unfrozen outputs; generating extra/best-of-n cases;
touching Week-1 artifacts; editing transcripts/intervals; excluding or
substituting cases; tuning anything.
