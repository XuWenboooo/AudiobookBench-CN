# W7 Pilot Protocol Draft v1

```text
STATUS = DRAFT_NOT_FROZEN
CURRENT_STAGE = TOPCONF-W7-PREPARATION-SIDEBRANCH
W7_PROTOCOL_FROZEN = NO
W7_FORMAL_PILOT_AUTHORIZED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
```

This is an outcome-blind preparation draft. It brings the W7 scientific
definitions to a final-review shape but does not authorize generation,
inference, evaluation or bootstrap. The current W6 gate remains blocked until
at least two independent external distributions pass the same acceptance
harness and a human authorization decision is recorded.

The inherited definitions are taken from
`TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`,
`W7_WHETHER_READINESS_V1.md`, `W7_EXECUTION_NAMESPACE_PLAN_V1.md` and
`W7_GT_AND_IDENTITY_BINDING_V1.json`. This draft does not rewrite those frozen
scientific choices.

## 1. Scientific conditions

The only W7 condition IDs are `clean`, `mechanism_shift`, `codec`, and
`resampling`. Each condition is paired to the same source/case identity and is
evaluated under the fixed model, localizer, distribution and case contract.

### `clean`

- Purpose: paired reference condition for detection retention and localization.
- Input transformation: none beyond the authorized source/manipulation
  construction.
- Allowed parameter space: the frozen case construction and source identity;
  no quality- or score-driven selection.
- Forbidden post-hoc tuning: model, threshold, pooling, case, source, or
  failure-rule changes after observing any W7 output.
- Case identity: the same `distribution_id`, `source_id`,
  `manipulation_id`, model and localizer lineage is retained.
- GT preservation: the clean paired reference must retain the predeclared
  source/target position and its evaluation-only GT binding.
- Failure handling: terminal failure is retained in the ledger and is not
  silently converted to a score.

### `mechanism_shift`

- Purpose: test the predeclared robustness change across the fixed mechanism
  grid, not to search for a mechanism that produces a desired gap.
- Input transformation: one of the existing frozen mechanism relations:
  same-speaker splice/crossfade control, cross-speaker boundary control,
  conventional TTS replacement, voice-conditioned TTS/VC replacement, or
  neural speech editing/infilling.
- Allowed parameter space: only the mechanism/version/reference/span/sample
  rate/codec/seed fields frozen for the case manifest.
- Forbidden post-hoc tuning: no new mechanism, dropped mechanism, altered
  reference rule, severity search, or outcome-guided retry.
- Case identity and GT preservation: source, target text/position, edited
  interval and GT identity remain paired; mechanism identity changes only in
  the declared `manipulation_id`.
- Failure handling: the declared terminal failure taxonomy applies.

`UNRESOLVED_PRE_FREEZE_ITEM`: the exact operational parameter values for any
mechanism cell not already present in the materialized W7 case manifest must be
written into that manifest before the first scientific inference.

### `codec`

- Purpose: test the predeclared codec transformation without changing the
  underlying case or GT.
- Input transformation: one-step Opus 64 kbps re-encoding at 16 kHz, as
  inherited from the design freeze.
- Allowed parameter space: exactly the declared codec path; no bitrate,
  codec, decoder, or severity search.
- Forbidden post-hoc tuning: no choosing the codec after seeing scores and no
  dropping a case because a codec branch is inconvenient.
- Case identity/GT: audio identity records the transformed input while source,
  manipulation and GT identities remain linked to the paired case.
- Failure handling: codec/decode/duration mismatch is an explicit terminal
  failure, never an imputed score.

### `resampling`

- Purpose: test the predeclared sample-rate transformation with identity and
  temporal support preserved.
- Input transformation: 16 kHz → 8 kHz → 16 kHz with a fixed anti-aliasing
  path.
- Allowed parameter space: the declared one-step path only.
- Forbidden post-hoc tuning: no filter, rate, chain, or severity selection
  after outcome observation.
- Case identity/GT: the exact transformed audio hash is bound to the same
  source/manipulation/condition case; GT interval seconds are unchanged.
- Failure handling: sample-count, duration, timestamp or decode mismatch is a
  terminal integrity failure.

`UNRESOLVED_PRE_FREEZE_ITEM`: the exact anti-aliasing implementation identity
and hash must be recorded before inference; this draft does not invent one.

## 2. Whether-A

Whether-A is detection derived from the localization score map.

- Input: finite native higher-is-better spoof scores on the model's temporal
  supports, joined to the inference-safe case after terminal output.
- Output: one utterance/case score per valid case.
- Score semantics: duration-weighted mean over finite native supports; on the
  common 20 ms support this is the ordinary mean. Higher means more spoof-like.
- Label semantics: case is positive when the authorized manipulated case is
  present and negative for the paired clean/control label defined by the case
  manifest.
- Aggregation: model × distribution × condition aggregation follows the frozen
  paired-source design; no test-set threshold or pooling optimization.
- Valid-case rule: non-empty, finite, in-duration and semantically
  unambiguous supports are required; otherwise `NOT_ESTIMABLE`.
- Failure rule: invalid, empty, non-finite, out-of-duration or ambiguous
  output is fail-closed and remains in the terminal ledger.
- Expected metric interface: AUROC, AUPRC, EER, fixed-FPR metrics and
  decision retention, with the fixed Level-1 target FPR `0.05` empirical
  quantile and tie rule.

## 3. Whether-B

Whether-B is independent of the localization map.

- Input: mono 16 kHz, 64,600-sample utterance input to the official frozen
  AASIST detector.
- Output: utterance-level softmax class-0 spoof score.
- Score semantics: higher class-0 score means more spoof-like; official mapping
  is `0=spoof`, `1=bonafide`.
- Label semantics: the same authorized case label as Whether-A, joined only on
  the canonical case identity.
- Aggregation: case-level and declared distribution/condition aggregation;
  no test-set recalibration.
- Valid-case rule: exact input length, finite deterministic two-class output,
  and strict checkpoint identity.
- Failure rule: load, shape, nonfinite or identity failure is terminal and
  cannot be replaced by a localization score.
- Expected metric interface: AUROC/AUPRC/EER and the same fixed-FPR/retention
  interface where the paired data support it.

## 4. Where

- Temporal score semantics: higher frame/segment/proposal score means more
  spoof-like; all native model outputs remain available for secondary reports.
- Canonical timeline: common 20 ms half-open supports `[start, end)`; native
  MultiReso scales and 160 ms BAM/SAL outputs retain their native resolution
  and are mapped explicitly, never silently clipped.
- Frame/sample/segment conversion: the generic adapter emits seconds with
  explicit half-open boundaries; sample indices use `start/rate` and
  `end/rate`; frame supports use their declared duration.
- Event conversion: proposals are scored and matched with the existing
  evaluator's IoU/AP/F1 contract; no event threshold is chosen from W7 output.
- GT normalization: only official/authorized temporal GT may be normalized;
  the adapter rejects malformed, out-of-range, ambiguous or empty positive
  labels.
- Case validity: a case is valid only when audio, GT, duration, identity and
  model output contracts all pass.
- Failure propagation: every invalid or missing output has an explicit
  terminal category and cannot be silently removed.

## 5. Canonical case identity

Every Whether and Where row is keyed by the stable tuple:

```text
distribution_id
source_id
manipulation_id
condition_id
model_id
whether_definition
localizer_id
adapter_version
ground_truth_identity
audio_identity
```

The opaque `case_id` is derived from this predeclared identity record. A case
cannot be joined on filename proximity, score order or array position. The
inference view excludes GT payload and outcome fields; the evaluation view
joins GT only after terminal raw output.

`UNRESOLVED_PRE_FREEZE_ITEM`: the final case-manifest hash and source-pool
identity binding must be materialized before human freeze.

## 6. Namespace ownership

```text
raw source namespace       = source/<distribution_id>/<source_id>/
generated asset namespace  = gen/<invocation_id>/<case_id_hash>/
scientific case namespace  = manifests/<distribution_id>/<version>/
prediction namespace       = pred/<invocation_id>/<model_id>/
metric namespace            = eval/<invocation_id>/
bootstrap namespace         = bootstrap/<invocation_id>/<analysis_id>/
artifact namespace          = results/topconf/w7_pilot/<invocation_id>/
```

One invocation owns one model × distribution × condition × owner lineage.
Distribution, manipulation, model and invocation IDs must be collision-free.
Historical pilot, Phase3T, and confirmatory namespaces are read-only and
cannot be reused. A duplicate case is a fail-closed identity error, not a
second observation.

## 7. Failure propagation

The terminal categories are `SOURCE_INVALID`, `REFERENCE_INVALID`,
`GENERATION_FAILURE`, `QUALITY_GATE_FAILURE`, `MODEL_LOAD_FAILURE`,
`INFERENCE_FAILURE`, `INVALID_OUTPUT`, `GT_INVALID`, and
`INFRASTRUCTURE_FAILURE`, with a predeclared single retry only where the
frozen protocol permits it. The following all fail closed: checkpoint load,
audio load, missing/invalid GT, adapter failure, model inference failure,
NaN, Inf, empty output, timestamp mismatch, duration mismatch, unsupported
representation, and identity ambiguity. No case is dropped, replaced,
imputed, or reclassified after outcome observation.

## 8. Detection metrics

The declared interface includes AUROC, AUPRC, EER, TPR at the frozen fixed-FPR
point, and decision retention. Whether-A uses the inherited Level-1 target FPR
`0.05` rule. No W7 test-set threshold optimization is allowed.

`UNRESOLVED_PRE_FREEZE_ITEM`: any metric-specific minimum-valid-case threshold
not already present in the frozen design must be explicitly recorded before
authorization; no favorable threshold is inferred here.

## 9. Localization metrics

The primary Where metric is frame AUPRC on common 20 ms supports with positive
support overlap at least `0.5`. Secondary outputs include frame AUROC/AUPRC at
native MultiReso scales, RangeEER, event AP/mAP, event F1 and boundary error.
The evaluator's existing event IoU points (`0.50`, `0.75`, `0.95`) remain
descriptive unless explicitly promoted before freeze.

- canonical temporal resolution: common 20 ms for the primary comparison;
  native resolutions are retained as secondary;
- aggregation: paired source first, then the predeclared equal-weight
  mechanism × transformation × distribution grid;
- macro/micro policy: source/case is the statistical unit; frame rows are not
  independent scientific units;
- invalid-case rule: `NOT_ESTIMABLE` on missing/empty/nonfinite/incompatible
  support, never zero-filled.

`UNRESOLVED_PRE_FREEZE_ITEM`: final report labels for any unsupported native
  event/boundary output must be fixed in the model adapter manifest.

## 10. Statistical analysis

- Bootstrap unit: paired source; all mechanism/transformation rows for a
  sampled source travel together.
- Paired structure: clean/reference and shifted condition rows remain paired by
  source, target context and authorized case identity.
- Resampling identity: deterministic child seeds derive from protocol,
  distribution, source, mechanism, transformation and model identity.
- CI target: two-sided percentile 95% CI for the declared estimand.
- Seed policy: primary seed `20260914`, with the frozen child-seed derivation.
- Minimum valid cases: the frozen source/population and terminal ledger must be
  complete; any additional minimum not already frozen is
  `UNRESOLVED_PRE_FREEZE_ITEM`.
- Failure condition: empty feasible `F_0.95`, nonfinite/nonpositive paired
  references, one-class support, incompatible pairing or unresolved quality
  gate yields `NOT_ESTIMABLE`, not an inferred zero.

The primary `LD@DR95` definition and 2,000-replicate paired bootstrap are
copied from the current outcome-blind design. No bootstrap is run in this
preparation branch.

## 11. Gate 1

```text
GAP_OBSERVED_IN >= 3 localization paradigms
AND
GAP_OBSERVED_IN >= 2 external distributions
```

Otherwise `PRIMARY_GAP_HYPOTHESIS = WEAK / NO_GO`. The gate cannot be lowered,
and no W7 result can alter its definition. The current state is
`W6_GATE = BLOCKED`, `READY_EXTERNAL_DISTRIBUTIONS = 1`, and no gap is
observed or measured.

## 12. Anti-outcome-seeking invariant

After the first scientific inference, it is prohibited to add or remove a
model or dataset to pursue a gap; modify a metric, threshold, aggregation,
bootstrap unit, gap definition or paradigm definition; or drop an unfavorable
case. This preparation branch also makes no such choice. Synthetic fixtures
are software tests only.

## 13. Authorization boundary

The final human decision must separately verify the second external
distribution, final case/provenance hashes, model preflight, namespace,
license and adapter evidence. Until then this document remains
`DRAFT_NOT_FROZEN`; it creates no W7 run, no Level-2 access and no scientific
outcome.
