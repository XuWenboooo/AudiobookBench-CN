# TopConf RQ1 Confirmatory Preregistration v1

Status: **DESIGN FROZEN FOR REVIEW / EXECUTION NOT AUTHORIZED**
Protocol ID: `P4-RQ1-DESIGN-20260914-01`
Freeze date: **2026-09-14**

This is the outcome-blind RQ1 Level-2 design produced by Phase4 human
reconciliation. It is not a model, data-generation, inference, evaluation,
bootstrap, attack, or mitigation authorization. The current record is blocked
from authorization because the independent Whether-B checkpoint/license/runtime
contract is not complete.

## 1. Question and hypotheses

In long-form Mandarin speech partial-deepfake localization, when manipulation
mechanism or bounded realistic media transformation shifts, do coarse fake
detection and temporal localization show a systematic robustness gap?

`H1` is the frozen Detection–Localization Gap Gate: in at least three distinct
localization paradigms and two independent source distributions, localization
degradation must be measurable while the frozen detection-retention constraint
is met. `H2` tests fixed mechanism heterogeneity, `H3` fixed transformation
heterogeneity, and `H4` compares Whether-A with an independently qualified
Whether-B. H2–H4 are secondary and Holm-adjusted within their declared family.

The project codename is AudiobookBench-CN; the scientific task is long-form
Mandarin speech. Week1–5 is historical pilot context only. Phase3T is Level-1
external functional validation only.

## 2. Frozen models and output contracts

The two verified functional localization baselines are CFPRF at official commit
`358a901ead8a7d84dac979c3d626e34ef82c2854` and MultiResoModel-Simple at
`0f69db3a2d654de47822d951fe6ad256bbaac9ba`. Their checkpoint and environment
identities are frozen in `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`
and the Phase3T provenance register.

CFPRF primary output is native FDN segment score on 20 ms support; FDN boundary
and PRN/proposal outputs are retained as secondary native outputs.
MultiReso primary common output is its native 0.02 s scale. All six native
scales (`0.02/0.04/0.08/0.16/0.32/0.64 s`) are retained and reported; no best
scale or head is selected.

The current verified core has two paradigms. No positive H1 claim is allowed
unless a third distinct paradigm passes an independent capability/provenance
gate before authorization. Adding a third paradigm after outcomes is forbidden.

## 3. Whether definitions

Whether-A is the duration-weighted mean of the finite native higher-is-better
spoof score across supports. For the 20 ms common support this is the ordinary
mean. Invalid, empty, non-finite, out-of-duration, or semantically ambiguous
output is `NOT_ESTIMABLE`.

Whether-A thresholding uses only a speaker/source-disjoint Level-1 calibration
split and a target FPR of `0.05`, with a deterministic empirical quantile and
fixed tie rule. Level-2 threshold optimization is prohibited.

Whether-B is an independent frozen utterance detector, never a pooling of a
localization map. The audited Codecfake W2V2+AASIST candidate is not currently
qualified because its checkpoint SHA256, explicit license chain, and local
runtime smoke are incomplete. Whether-B is therefore a frozen requirement but
an unresolved blocker; it is not substituted by CFPRF or MultiReso.

## 4. Where metrics and LD@DR95

The primary Where metric is frame-level AUPRC on native common 20 ms supports,
with a positive frame defined by at least 0.5 support overlap with the private
edited interval. Secondary metrics are native frame AUROC/AUPRC at all
MultiReso scales, CFPRF boundary diagnostics, native proposal AP/F1 where
supported, and fixed descriptive RangeEER/event/boundary measures. They cannot
be promoted after observation.

For each model, distribution, and predeclared condition, `r` is the paired
reference: the clean-media version of the same mechanism for transformation
comparisons, or the clean same-source splice/crossfade control for mechanism
comparisons. Let `D` be the mean Whether-A spoof score and `L` the mean primary
frame AUPRC over paired source units:

```text
DR_c = D_c / D_r
LR_c = L_c / L_r
F_0.95 = {c : DR_c >= 0.95}
LD@DR95 = 1 - mean_{c in F_0.95}(LR_c)
```

Higher `LD@DR95` means greater localization degradation at retained detection.
The condition aggregation is equal-weight over the declared
mechanism × transformation × distribution grid. `NOT_ESTIMABLE` is returned
for non-finite/non-positive references, empty feasible sets, one-class/empty
support, incompatible pairing, or undefined aggregation. Undefined values are
never zero-filled or silently removed.

## 5. Gap criterion

H1 passes only when all six paradigm × distribution cells are estimable, each
has at least one condition in `F_0.95`, each point estimate is at least `0.10`,
each two-sided 95% CI lower bound is above `0.00`, and every failure/quality
gate is reconciled. The `0.10` materiality value is a fixed ten-percentage-point
loss in localization retention, chosen as an operational design threshold and
not tuned to any project outcome. Failure is `NO_GO / NOT_ESTIMABLE`.

## 6. Population, pairing, and freshness

The frozen design targets two independent, rights-cleared long-form Mandarin
source pools, 200 primary sources and 60 speakers per pool, 400 sources and
120 speakers total. Each source has four balanced manipulation variants plus a
clean paired counterpart; this is 1,600 manipulated variants before fixed
transformation branches. A predeclared 40-source reserve is hashed before any
model output and can be used only for the fixed `SOURCE_INVALID` rule.

Source/session/speaker identities are disjoint across development,
calibration, and held-out evaluation. Target spans are sampled by a fixed
speech-bearing placement rule, with fixed duration bounds and no label-,
score-, quality-, or visualization-driven selection. The private freshness
manifest must prove that no case or lineage belongs to Week1–5 pilot data,
Phase3T PartialEdit v1.1 E1, or any development/model/metric/threshold
selection set. The design manifest is intentionally not materialized in
Phase4.

The paired unit is the same source, speaker, surrounding context, target text
where feasible, and target position across mechanisms. A voice-conditioned
reference is a separate same-speaker utterance/text selected by a deterministic
predeclared rule and is generator input only.

## 7. Fixed mechanisms and transformations

Primary mechanisms are: (1) same-speaker splice/crossfade control, with
cross-speaker splice as a separately flagged boundary/speaker-shift control;
(2) conventional TTS replacement; (3) voice-conditioned TTS/VC replacement;
and (4) neural speech editing/infilling. Codec-consistent/mismatched paths and
multiple edited regions are secondary controls.

Each is paired and generated with fixed text, span, generator/version,
reference rule, sample rate, codec path, seed, and quality gates.

The one-step transformation cells are Opus 64 kbps re-encoding at 16 kHz;
16→8→16 kHz resampling with fixed anti-aliasing; deterministic 4 kHz
low-pass bandwidth limitation; additive noise at 20 dB SNR from a declared
fixed family; fixed held-out RIR with RT60 target 0.3 s; and −6 dB gain with
peak guard. There is no transformation chain/severity search or
outcome-dependent omission.

## 8. Statistical analysis

The primary inference unit is paired source. Source-condition rows are not
independent frame observations. The primary uncertainty procedure is 2,000
paired-source percentile bootstrap resamples, retaining all mechanism and
transformation rows for each sampled source and recomputing the feasible set.
A 2,000-replicate hierarchical speaker→source bootstrap is a predeclared
sensitivity analysis. The seed is `20260914` with deterministic child seeds
from protocol/distribution/source/mechanism/transformation/model identity.

The single primary H1 is the frozen gap gate. H2–H4 and their fixed secondary
metrics use Holm adjustment within each declared family at two-sided alpha
`0.05`. There is no significance-based stopping rule; the run stops only after
the complete frozen population/condition grid and every terminal ledger row are
processed.

## 9. Blinding, failures, and namespace

Private generation and GT use `gen/<invocation_id>/` and `gt/<case_id_hash>/`;
the model-facing view uses `infer/<invocation_id>/` and contains only opaque
case IDs, authorized audio identities, durations, and protocol metadata. Raw
predictions use `pred/<invocation_id>/<model_id>/`; the joined evaluator uses
`eval/<invocation_id>/` only after the reveal gate. Mechanical separation is
possible for a single operator, but independent human custody is not claimed.

Every planned model × case × condition invocation has exactly one terminal
state: `SCIENTIFIC_VALID_CASE`, `SOURCE_INVALID`, `REFERENCE_INVALID`,
`GENERATION_FAILURE`, `QUALITY_GATE_FAILURE`, `MODEL_LOAD_FAILURE`,
`INFERENCE_FAILURE`, `INVALID_OUTPUT`, `GT_INVALID`, or
`INFRASTRUCTURE_FAILURE`. Planned, terminal, valid, and failure denominators
are all reported. At most one registered deterministic retry is allowed for a
predeclared transient infrastructure/invalid-output failure, with the same
lineage. No retry follows a valid score, no retry is result-driven, and no case
is silently dropped or replaced.

The fresh outcome namespace is
`results/topconf_level2_rq1_v1/<invocation_id>/`; it cannot overwrite
`results/topconf_phase3t/` or historical pilot paths. The namespace requires
one invocation, one owner, one authorization hash, and one protocol/dataset
identity.

## 10. Authorization status

```text
PROTOCOL_FROZEN = YES
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RQ2_ATTACK_INVOKED = NO
RQ3_MITIGATION_INVOKED = NO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```

Authorization remains a separate human decision after the Whether-B blocker,
third-paradigm claim requirement, materialized freshness proof, and any
model-specific environment gates are resolved.
