# Model Capability Matrix v1

Status: **PRE-RUN CONTRACT / CAPABILITIES ARE NOT RESULTS**

The unified evaluator accepts only finite, provenance-tagged outputs. A model
is not forced into a metric family that its native output cannot support.

| Model | Native output expected from source | Unified contract mapping | RangeEER eligibility | Gate status |
|---|---|---|---|---|
| Internal B1b | utterance score | utterance detection metrics; frame/event/proposal only if a separately authorized native output exists | no unless range scores and compatible GT are emitted | internal artifact available; no Phase 3 run |
| Internal B4 | local/frame score | frame metrics, event/proposal/boundary where timestamps are explicit; utterance aggregation must be declared | yes only with compatible frame/range score and PartialSpoof GT | internal artifact available; no Phase 3 run |
| CFPRF | detector score plus refined proposals, per official repository | native official metrics first; unified utterance/frame/event/proposal fields when contract is satisfied | conditional on interval/range output and validated GT | checkpoint load blocked |
| SAL | frame/localization output, default granularity documented by source | native evaluator plus frame/event/boundary fields when output is finite and aligned | conditional on range-compatible output | checkpoint unavailable |
| BAM | frame-level localization output | native evaluator plus frame/event/boundary fields when output contract is verified | conditional; no forced conversion | rights unresolved |
| TRACE | trajectory-based detection/localization concept | stretch only; no adapter or output contract claimed | not eligible until official output and provenance are verified | reimplementation required |

Common checks: sample identity, split identity, time units, monotonic support,
finite scores, output granularity, checkpoint hash, and failure class. The
matrix does not authorize tuning or any confirmatory comparison.
