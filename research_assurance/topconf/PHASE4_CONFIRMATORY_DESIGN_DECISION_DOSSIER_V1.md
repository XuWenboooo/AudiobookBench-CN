# Phase 4 Confirmatory Design Decision Dossier v1

Status: **DESIGN FIELDS FROZEN / PHASE4 CLOSURE BLOCKED ON WHETHER-B**  
Decision ID: `P4-RQ1-DESIGN-20260914-01`  
Decision date: **2026-09-14**  
Scope: **RQ1 Level-2 design only; no execution authority**

This dossier is the content-level resolution of the two frozen parallel lanes
after the authoritative Phase3T capability audit. It freezes every decision
that can be frozen without observing Level-2 outcomes. It does not authorize
population materialization, model loading, inference, evaluation, bootstrap,
RQ2 attack work, or RQ3 mitigation work.

## 1. Research question and claim boundary

RQ1 is:

> In long-form Mandarin speech partial-deepfake localization, when the
> manipulation mechanism or a bounded realistic media transformation shifts,
> do coarse fake detection and temporal localization show a systematic
> Detection–Localization Robustness Gap (robustness decoupling)?

“AudiobookBench-CN” is retained as the engineering codename. The scientific
regime is long-form Mandarin speech, not a claim that audiobook recordings are
the whole task. Week1–5 artifacts are pilot context only; Phase3T is Level-1
external functional validation only.

No directly equivalent formulation was identified in the primary sources
reviewed as of 2026-09-13. This is a bounded search statement, not a first-ever
claim and not evidence from a project result.

## 2. Baseline and capability policy

The frozen functional core is:

| Baseline | Frozen identity | Primary common output | Native outputs retained |
|---|---|---|---|
| CFPRF | official repository commit `358a901ead8a7d84dac979c3d626e34ef82c2854`; MIT; FDN `5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267`; PRN `88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36`; XLS-R `B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9` | FDN segment score at native 20 ms | FDN boundary scores and all PRN verification/regression/proposal fields |
| MultiResoModel-Simple | repository commit `0f69db3a2d654de47822d951fe6ad256bbaac9ba`; root MIT; archive `0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32`; inner checkpoint `5B753752F7C25370C6ABF973F69F58E100DAD4B5D3EA035872335358A876FDD1`; SSL checkpoint `4E1B1AE691F26947FBF0B709FF1DD5F2F16CB586161CC3E9461E35BCD9CB5F75` | native `0.02 s` scale | all six native scales: `0.02/0.04/0.08/0.16/0.32/0.64 s`, both class columns |

The two baselines are retained because their functional contracts were
completed and accounted for in Phase3T, not because of their diagnostic
performance. Internal B4, SAL, BAM, and TRACE are not silently promoted. A
positive gap claim requires at least three distinct localization paradigms;
the current two-baseline core therefore cannot by itself satisfy that claim
gate. A third paradigm may be added only by a capability/provenance amendment
before authorization, never by Level-2 performance selection.

### CFPRF head policy

`CFPRF_FDN_20ms` is the primary common temporal representation because FDN is
the model’s native segment detector and has the explicitly aligned 20 ms
support. Boundary scores and PRN/refined proposals remain secondary native
reports. No FDN/PRN/boundary/frame/proposal head was selected using Phase3T
metrics.

### MultiReso scale policy

`MRM_0.02` is the fixed common representation because it is the native scale
shared with CFPRF’s 20 ms FDN support. This is a contract intersection rule,
not a performance choice. All six scales must be retained and reported in
secondary sensitivity tables; there is no best-scale choice and no scale
averaging that can hide a scale. The policy is:

```text
MULTIRESO_SCALE_POLICY = FIXED_NATIVE_COMMON_20MS_PLUS_ALL_SCALE_REPORTING
RESULT_BASED_SCALE_SELECTION = NO
```

## 3. Whether-A and Whether-B

### Whether-A — frozen

Whether-A is derived from the selected localization output and is not a second
model. For each valid native support `j`, let `s_j` be the higher-is-better
native spoof score (class-0 spoof score after the fixed adapter contract).
The primary utterance score is the duration-weighted mean:

```text
WhetherA_score = sum_j duration(support_j) * s_j / sum_j duration(support_j)
```

For the 20 ms common representation this is the ordinary mean. Supports must
be finite, positive, monotonic, non-overlapping, and within the waveform
duration; the adapter may not clip or invent support. The score direction is
higher = more likely fake. Non-finite, empty, unsupported, or semantically
ambiguous outputs are `NOT_ESTIMABLE`, never zero-imputed.

The binary threshold is not optimized on Level 2. It is frozen from a
speaker/source-disjoint Level-1 calibration split at target FPR `0.05`, using
a deterministic empirical quantile and a fixed tie rule. The calibration
split, code commit, threshold, and hash must be recorded before any Level-2
reveal. AUROC/AUPRC and score-retention analyses remain threshold-free.

```text
WHETHER_A = DURATION_WEIGHTED_MEAN_NATIVE_SPOOF_SCORE
WHETHER_A_FREEZE = FROZEN
WHETHER_A_THRESHOLD_SOURCE = LEVEL1_CALIBRATION_TARGET_FPR_0.05
WHETHER_A_MISSING_OUTPUT = NOT_ESTIMABLE
```

`max_pool` and `top_k_mean` are not alternate primary analyses. They may appear
only as clearly labelled exploratory diagnostics after the confirmatory lock.

### Whether-B — explicit blocker

Whether-B must be a strong, independent, frozen utterance-level detector whose
score is not computed from a localizer. The preferred audit candidate is
Codecfake W2V2+AASIST at official commit
`72c32e2840eef95fbeade349425fa9c5391fa11e`, with a 16 kHz input contract and
the repository-provided checkpoint path
`pretrained_model/codec_w2v2aasist/anti-spoofing_feat_model.pt`.

The candidate cannot be frozen in this Phase4 record because the checkpoint
could not be materialized and independently hashed in the authorized local
environment, the repository has no explicit root code-license file in the
audited commit, the dataset is CC BY-NC-ND 4.0, and the official script
requires a separately provisioned XLS-R path and CUDA execution. AASIST and
SSL alternatives likewise lack a locally pinned checkpoint hash and complete
Mandarin/runtime compatibility record.

```text
WHETHER_B = INDEPENDENT_DETECTOR_REQUIRED_BUT_NOT_INCLUDED
WHETHER_B_CHECKPOINT = NOT_MATERIALIZED / SHA256_NOT_VERIFIED
WHETHER_B_FREEZE = BLOCKED_ON_CHECKPOINT_LICENSE_RUNTIME_PROVENANCE
WHETHER_B_FALLBACK = DO_NOT_DERIVE_FROM_LOCALIZER; REPORT_LIMITATION
```

This is a genuine blocker, not a reason to substitute a localizer-derived
score. A separate versioned provenance amendment must pass before
`RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED` can become `YES`.

## 4. Where hierarchy and common metric

The primary common Where estimand is frame-level AUPRC on the fixed native
20 ms support. A frame is positive when at least `0.5` of its support overlaps
the predeclared edited interval. No model is forced into a level unsupported
by its native output.

```text
PRIMARY_WHERE_METRIC = FRAME_AUPRC_NATIVE_COMMON_20MS
PRIMARY_REPRESENTATIONS = CFPRF_FDN_20ms; MRM_0.02
SECONDARY_WHERE_METRICS = native frame AUROC; MRM all six scale AUPRC/AUROC;
  CFPRF boundary error/boundary F1; native proposal AP/F1 when contract-valid
DIAGNOSTIC_ONLY = RangeEER; event/proposal/boundary alternatives;
  threshold-free and thresholded descriptive curves
```

Secondary metrics are reported with their native support, label convention,
and compatibility status. They cannot replace the primary endpoint after
outcomes are seen.

## 5. LD@DR95 definition

The reference is paired within source, speaker, target text, and target
position. For a mechanism-shift comparison, the reference is the fixed
same-source splice/crossfade control under the clean media condition. For a
media-transformation comparison, the reference is the same mechanism under
the clean media condition. Each comparison uses the same model, distribution,
source unit, and primary Where representation.

For a model/distribution/condition cell, let:

```text
D0 = mean higher-is-better Whether-A score on the paired reference condition
Dc = mean higher-is-better Whether-A score on the shifted condition c
L0 = mean primary frame-AUPRC on the paired reference condition
Lc = mean primary frame-AUPRC on the shifted condition c
DR_c = Dc / D0
LR_c = Lc / L0
F_0.95 = {c : DR_c >= 0.95}
LD@DR95 = 1 - mean_{c in F_0.95}(LR_c)
```

The final condition aggregation is equal-weight over the predeclared
mechanism × transformation × distribution cells. Source-level means are
computed before condition aggregation. The primary sign is higher positive
`LD@DR95` = larger localization degradation while detection retention remains
at least 95% of the paired reference.

`NOT_ESTIMABLE` is mandatory for a non-finite or non-positive `D0`/`L0`, an
empty feasible set, one-class or empty support, incompatible paired support,
undefined condition aggregation, or any unresolved output contract. No
undefined cell may be dropped, zero-filled, or replaced by a different
condition. Planned, terminal, valid, and failure counts accompany every
estimand.

The primary uncertainty interval is a two-sided percentile 95% interval from
`2,000` paired-source bootstrap resamples. Each resample retains every
mechanism/transformation row for a sampled source and recomputes the complete
feasible set. A `2,000` replicate hierarchical speaker→source bootstrap is a
predeclared sensitivity analysis. A row bootstrap is diagnostic only.

## 6. Detection–Localization Gap Gate

The gap claim is allowed only if all of the following were predeclared and
estimable:

1. at least three distinct localization paradigms and two independent source
   distributions are available, yielding six paradigm × distribution cells;
2. every cell has at least one condition in `F_0.95` and a complete paired
   source ledger;
3. in every one of the six cells, the point estimate satisfies
   `LD@DR95 >= 0.10` (a fixed ten-percentage-point loss in localization
   retention) and the two-sided 95% CI lower bound is above `0.00`;
4. all planned failures, invalid cases, and quality gates are reported, with no
   result-driven model, cell, threshold, or condition removal.

Failure of any item means `GAP_CLAIM = NO_GO / NOT_ESTIMABLE`, not a rescue by
adding a model or selecting a metric after inspection. The current two-model
Phase3T capability core is explicitly insufficient for a positive six-cell
claim until a third paradigm is independently verified before authorization.

## 7. RQ1 stages and fixed mechanism taxonomy

```text
STAGE_A = manipulation-mechanism shift
STAGE_B = bounded realistic media transformations
STAGE_C = adaptive detection-preserving localization attack interface only;
          not executed in Phase4 and not part of this RQ1 freeze
```

The four balanced primary mechanism families are:

1. same-speaker splice/crossfade control, with cross-speaker splice retained as
   a separately flagged boundary/speaker-shift control;
2. conventional TTS target replacement with fixed text and position;
3. voice-conditioned TTS/VC replacement with a deterministic, separately
   authorized reference-utterance rule;
4. neural speech editing/infilling conditioned on surrounding context and
   target text.

Mechanism identity, generator/version/checkpoint, reference, text, position,
sample rate, codec path, seed, and quality outcome are manifest fields. The
primary mechanism set is fixed for identifiability, paired feasibility,
modern relevance, and reproducibility. Codec-consistent/mismatched paths and
multiple edited regions are secondary controls, not interchangeable primary
mechanisms.

## 8. Fixed transformation set

Each transformation is a one-step condition applied independently to the same
paired audio. No chain search, severity search, or outcome-dependent omission
is allowed.

| ID | Fixed condition | Parameter / implementation rule |
|---|---|---|
| `codec_opus_64k` | Opus re-encoding | 16 kHz, 64 kbps, deterministic encoder settings |
| `resample_8k_roundtrip` | resample and restore | 16→8→16 kHz, fixed anti-aliasing filter |
| `bandwidth_4k` | bandwidth limitation | deterministic 4 kHz low-pass, no clipping |
| `noise_20db` | additive noise | fixed declared noise family at 20 dB SNR; seed from manifest |
| `reverb_rt60_0p3` | reverberation | fixed held-out RIR family, RT60 target 0.3 s |
| `gain_minus6db` | level change | −6 dB gain with peak guard and no clipping |

Quality gates are finite audio, duration/alignment preservation, no clipping,
predeclared intelligibility/speaker checks, and parameter realization. A
failed gate is a terminal failure, not a reason to search another strength.

## 9. Fresh Level-2 population and sample size

The population design is frozen but not materialized by Phase4:

```text
POPULATION_ID = TOPCONF_RQ1_LEVEL2_FRESH_V1
REGIME = long-form Mandarin speech
INDEPENDENT_DISTRIBUTIONS = 2 source pools, 200 primary sources each
SPEAKERS = 120 total, 60 per source pool, speaker-disjoint across splits/pools
PRIMARY_SOURCES = 400
PRIMARY_MECHANISMS = 4 balanced mechanisms per source
MANIPULATED_VARIANTS = 1,600 before transform branches
PREDECLARED_SOURCE_RESERVE = 40, selected and hashed before any model output
TARGET_DURATION = 8–30 s source segments with multiple valid target positions
```

The source pools must be independently rights-cleared, Mandarin, long-form
speech distributions with source/session/speaker metadata. The exact pool
identities and hashes are fields in the pre-run freshness manifest and must be
filled before authorization; no Phase3T E1 row may be reused. The reserve is
used only by a deterministic source-invalid rule recorded before inference;
there is no replacement for a bad score or quality preference.

Sampling is speaker-disjoint across `C-TRAIN`, `C-DEV`, `C-CALIBRATION`, and
`C-HELDOUT`; source and session families may not cross a held-out boundary.
Target positions are selected by a frozen speech-bearing-span rule, not by
labels, detector scores, visualization, or quality outcomes. Each manipulated
variant retains a clean paired counterpart and a private target interval.

The planning choice is the middle synthetic sensitivity band `400 sources /
120 speakers / 4 mechanisms`. It is a planning design, not a power claim and
not an update from Phase3T metrics. No sample-size expansion is permitted
after Level-2 outcomes are visible.

## 10. Statistical hierarchy and multiplicity

The single primary hypothesis is the six-cell Detection–Localization Gap Gate
using the frozen `LD@DR95`. Predeclared secondary families are:

```text
H2 = mechanism heterogeneity in LD@DR95
H3 = transformation-stratum differences in LD@DR95
H4 = Whether-A versus independent Whether-B detection-retention sensitivity
```

H2–H4 and secondary native metrics use Holm adjustment within their respective
locked family at two-sided alpha `0.05`. Exploratory native-scale, event,
proposal, boundary, and pooling diagnostics are labelled exploratory and are
not used to rescue H1. There is no significance-based stopping rule.

The statistical unit is the paired source. Speaker is a clustering/sensitivity
dimension, never a reason to treat frame rows as independent observations.
The fixed seed policy is `20260914` with deterministic child seeds derived
from the hash of `(protocol, distribution, source, mechanism, transform,
model)`. The bootstrap order and number are fixed above.

## 11. Thresholds, blinding, GT isolation, and failures

Threshold sources are only `OFFICIAL_FIXED_THRESHOLD`, `LEVEL1_CALIBRATION`,
or `FROZEN_FIXED_FPR`. No Level-2 test-set threshold, calibration, model
selection, reference selection, or pooling selection is permitted.

The namespaces are:

```text
gen/<invocation_id>/       private generation manifest and output hashes
gt/<case_id_hash>/         private labels and target spans
infer/<invocation_id>/     public model-facing manifest, no GT
pred/<invocation_id>/<m>/  raw model outputs, no GT
eval/<invocation_id>/      joined evaluation package after reveal gate
```

Case IDs are random non-semantic identifiers. The inference runner receives
only authorized audio identity/path, duration, model metadata, and protocol
hash. A separate evaluator joins predictions and private GT only after the
freeze, completion, namespace, hash, and terminal-ledger gates pass. This is
mechanical separation in a single-person workflow; it is not independent human
custody.

Every planned `model × case × condition` invocation has exactly one terminal
state: `SCIENTIFIC_VALID_CASE`, `SOURCE_INVALID`, `REFERENCE_INVALID`,
`GENERATION_FAILURE`, `QUALITY_GATE_FAILURE`, `MODEL_LOAD_FAILURE`,
`INFERENCE_FAILURE`, `INVALID_OUTPUT`, `GT_INVALID`, or
`INFRASTRUCTURE_FAILURE`. Planned, terminal, valid, and failure denominators
are all reported. Missing/unknown/duplicate rows block closure.

At most one deterministic retry is allowed for a predeclared transient
infrastructure or invalid-output failure, using the same source, configuration,
model, target, and namespace lineage. Retries require registration and the
authorization hash, remain in the append-only ledger, and are forbidden after
a valid result or for a better observed score. GT incidents invalidate the
affected scope; they are not repaired by silent replacement.

Future output ownership is one invocation, one owner, one namespace under
`results/topconf_level2_rq1_v1/`. It must never overwrite
`results/topconf_phase3t/` or any pilot path.

## 12. Stopping rule and authorization boundary

The future run stops only after the complete frozen population, all declared
conditions, all selected model invocations, and all terminal ledger rows have
been processed or explicitly failed. It never stops when significant, positive,
or computationally convenient.

Phase4 freezes the design but creates no execution authorization. The separate
authorization template must be completed only after the Whether-B provenance
blocker and any third-paradigm gap-claim requirement are resolved by a new
human review.

```text
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```
