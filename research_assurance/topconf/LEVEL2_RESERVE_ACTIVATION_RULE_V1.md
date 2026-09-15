# Level-2 reserve activation rule v1

**Status:** `PROSPECTIVE_RULE_CREATED_BEFORE_ACTIVATION`
**Purpose:** one-time, outcome-independent remediation of verified historical
freshness contamination in the frozen V2 candidate

## Pre-existing rule audit

Phase4 and the V2 manifest predeclared 40 reserve records, 20 per source pool,
and limited their use to a deterministic `SOURCE_INVALID` rule. They did not
freeze a complete activation ordering for a freshness-contamination amendment.
Therefore:

```text
RESERVE_POOL_DEFINED = YES
RESERVE_ORDER_DEFINED = PARTIAL
RESERVE_ACTIVATION_RULE_DEFINED = PARTIAL
RESERVE_RULE_PREEXISTING = NO_FOR_THIS_TRIGGER_AND_ORDER
RESERVE_RULE_AMENDMENT_REQUIRED = YES
AMENDMENT_KIND = PROSPECTIVE_GOVERNANCE_ONLY
SCIENTIFIC_DESIGN_CHANGED = NO
```

The only amendment trigger allowed in this record is the already verified
Phase4.7 freshness contamination. Detector/localizer scores, model behavior,
quality preference, difficulty, expected direction, and any scientific result
are not eligible triggers.

## One-time activation rule

1. The candidate universe is exactly the 40 records in
   `LEVEL2_RQ1_POPULATION_MANIFEST_V2.json.reserve_records`. No new corpus scan,
   manual listening choice, score-ranked candidate, or expanded reserve is
   permitted.
2. Activation is within the original source pool only. An AISHELL-3 primary
   source can be replaced only by a clean eligible AISHELL-3 reserve; an
   AISHELL-1 primary source can be replaced only by a clean eligible AISHELL-1
   reserve. Cross-pool substitution is not permitted by the frozen two-pool
   design.
3. A reserve is eligible only if its frozen metadata already satisfies the
   duration, audio-integrity, transcript, source-lineage, speaker-metadata,
   corpus, and pool requirements, and it is absent from every verified case,
   source, speaker, and lineage exclusion identity. An excluded speaker makes
   all records from that speaker ineligible.
4. Within each pool, scan the predeclared records in the canonical ascending
   tuple `(corpus_id, speaker_id, utterance_id, source_id,
   source_audio_sha256, parent_asset_id)`. `reserve_rank` is the one-based rank
   in this full predeclared order; skipped records are not renumbered.
5. Assign the first eligible reserve to the first contaminated primary source
   in ascending old `source_id` order, then continue in that fixed order. The
   ledger must record the old source, old cases, reserve rank, new source, new
   cases, and the rule ID before any model output.
6. A replacement regenerates the complete four-case mechanism group from the
   frozen source-dependent seed function. It cannot retain the old source's
   seed, case ID, lineage, or speaker identity. Pairing, mechanism balance,
   transform balance, split assignment, and source-pool counts must be
   revalidated.
7. If the clean same-pool reserve count is smaller than the number of
   contaminated primary sources, activation stops before any partial
   replacement. The closure is
   `BLOCKED_INSUFFICIENT_CLEAN_RESERVE`; no cross-pool fallback, population
   expansion, or second replacement cycle is allowed.

```text
ACTIVATION_TRIGGER = FRESHNESS_CONTAMINATION
ACTIVATION_IS_RESULT_INDEPENDENT = YES
ACTIVATION_IS_ONE_TIME = YES
POOL_SUBSTITUTION = FORBIDDEN
MANUAL_SELECTION = FORBIDDEN
SCORE_SELECTION = FORBIDDEN
QUALITY_SELECTION = FORBIDDEN
```
