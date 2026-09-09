# Week 3 Stage-A Preregistration Draft — Prospective Second-Generator Follow-up

Date: 2026-09-06

Status: **STAGE-A PROTOCOL FROZEN FOR GENERATOR-SELECTION REVIEW ONLY.** This document authorizes neither candidate selection nor model download, audio generation, detector scoring, B4 execution, ECAPA execution, or any analysis of the existing CosyVoice2 cases. It is a new prospective study and cannot repair original Day 13.

## 1. Study structure

**Stage A** is a **PROSPECTIVE CONFIRMATORY PAIRED SECOND-GENERATOR FOLLOW-UP**. It applies one as-yet-unselected, eligible, non-CosyVoice voice-conditioned TTS generator to the exact frozen 23 Day10 source/reference pairs. The second-generator outcomes are prospective. CosyVoice2 outcomes are already observed and serve only as a fixed historical benchmark; no comparison with them is an independent-population replication.

**Stage B** is a **FUTURE INDEPENDENT CONFIRMATORY STUDY**. It is not automatically entered and has no trigger in this protocol. It requires a separately completed preregistration before any Stage-B data are selected or generated. Stage-A results may motivate a future Stage-B question, but may not retrospectively modify Stage-A hypotheses, estimands, metrics, regions, generator, detector, statistical contract, or interpretation. Stage B is therefore `DEFERRED_WITH_VALID_SEPARATE_PREREG` and is not a Stage-A readiness blocker.

## 2. Analysis hierarchy

Every Stage-A analysis has exactly one role:

| Role | Analyses |
| --- | --- |
| PRIMARY | H1 second-generator transfer estimates; H2 core-versus-boundary score decomposition; H3 full-versus-core blend-exclusion effect. |
| SECONDARY | Fixed historical paired descriptive contrasts between new second-generator case metrics and already-observed CosyVoice2 case metrics. |
| DIAGNOSTIC_ONLY | B4 energy-transient reporting, if executed after separate engineering readiness; it cannot control a gate, endpoint, case inclusion, generator selection, or claim. |
| EXPLORATORY_ONLY | Any Week3 ECAPA analysis and every new analysis of existing CosyVoice2 zone data. These cannot define thresholds, select a generator, or change confirmatory interpretation. |

No diagnostic or exploratory result may be promoted after observation.

## 3. Generator eligibility and deterministic selection contract

No generator is selected by this document. Selection state is fail-closed but does not treat unperformed dynamic qualification as a static failure. The permitted candidate states are:

- `STATIC_FAIL`: a mandatory failure is established before dynamic execution, including `LICENSE_FAIL`, unsupported scientific semantics, or no deterministic official acquisition path;
- `READINESS_PENDING`: no known mandatory failure, but one or more mandatory criteria remain unverified;
- `FULLY_ELIGIBLE`: every mandatory criterion has PASS evidence;
- `FULLY_INELIGIBLE`: the static contract passed, but dynamic mandatory qualification later fails, such as no permitted execution backend, offline reload failure, engineering-only smoke failure, or mechanical waveform failure;
- `SELECTED`: the deterministic tie-break winner among `FULLY_ELIGIBLE` candidates.

The selection pipeline is frozen as `STATIC SCREEN -> ENGINEERING QUALIFICATION -> FULL ELIGIBILITY MATRIX -> DETERMINISTIC TIE-BREAK -> FINAL SELECTION`. No candidate may be marked `FULLY_ELIGIBLE` or `SELECTED` before mandatory engineering qualification is complete.

The qualification order is frozen for every candidate: resolve and record the exact immutable upstream revision; record provider, URL, model ID, and metadata provenance; enumerate statically identifiable mandatory components; complete authoritative license preflight; acquire binaries only after all currently known mandatory components are `LICENSE_PASS`; permit only official-path dynamic asset discovery; license and hash every newly discovered mandatory asset before use; then run local load, offline reload, hardware checks, engineering-only smoke, and mechanical waveform QA. Mutable `main`, `HEAD`, and `latest` downloads are forbidden. If an official publisher exposes only a mutable archive URL, record `upstream_immutable_revision=UNAVAILABLE`, official URL, provider, acquisition timestamp, SHA256, and complete local inventory.

A candidate is eligible only if all mandatory criteria below are documented before formal Stage-A generation:

1. an official, publicly identifiable model or repository exists;
2. it supports target-speaker or voice-conditioned synthesis from reference audio;
3. Mandarin/Chinese exact same-text synthesis is usable under the existing exact-text policy;
4. whole-source-utterance generation with natural synthetic duration is possible;
5. model/checkpoint revision and required component hashes can be frozen;
6. an official research-compatible license is identifiable;
7. local/offline reproducibility can be documented;
8. detector-side access to reference audio, speaker identity, text, generator internals, QA, and metadata can be prevented;
9. it is not a CosyVoice/CosyVoice2 checkpoint, derivative, fine-tune, or member of the same documented model lineage; and
10. it passes the engineering-feasibility gate below without changing A2 scientific semantics.

The engineering-feasibility gate means: the official/local checkpoint is obtainable; the immutable revision can be recorded; one fixed disposable engineering smoke completes using the unchanged same-text/reference, natural-duration, 16-kHz, crossfade, and dual-timeline semantics; and required inference completes on CPU or the available 8-GB GPU without a semantic modification. Runtime speed is not a ranking criterion.

Engineering qualification is restricted to checkpoint acquisition, dependency/runtime closure, local loading, offline loading, CPU/available-8-GB-GPU feasibility, one disposable engineering smoke, and mechanical waveform integrity. It must not inspect B1b scores, H1/H2/H3, ECAPA similarity, detectability, scientific localization, subjective preference, or comparative audio quality.

Dynamic qualification may discover only additional mandatory official files required by the already-frozen official inference path. It may not substitute unofficial assets, switch vocoders/frontends, change model lineage, alter reference/text semantics, change generation topology, or redesign inference. Each discovered official asset requires source provenance, revision or archive evidence, SHA256, and `LICENSE_PASS` before use.

Every candidate surviving the static screen receives the same qualification procedure. The frozen contract contains no sequential short-circuit rule: all surviving candidates must be qualified so that the objective compatibility-burden tie-break remains comparable. A candidate with unresolved license evidence remains `READINESS_PENDING`; final eligibility requires an explicit license PASS/FAIL determination for the intended academic research use.

Before large checkpoint acquisition, every statically identifiable mandatory code, checkpoint, vocoder, tokenizer, frontend, and auxiliary component must reach `LICENSE_PASS`. Metadata-only revision and manifest resolution is allowed before that preflight when required to identify the component set. `LICENSE_FAIL` immediately yields `STATIC_FAIL` and dynamic status `NOT_RUN_DUE_TO_MANDATORY_FAIL`.

If more than one candidate passes all mandatory criteria, select the candidate by this frozen order: (a) explicit official documentation of Chinese voice conditioning; (b) documented local/offline reproducibility; (c) ascending count of non-semantic environment-compatibility actions required from a fixed checklist of installation, model-cache, runtime, and device prerequisites; then (d) ascending canonical model ID under Unicode code-point ordering. Detector score, audio quality, ECAPA similarity, CER, subjective preference, and expected detectability are prohibited tie-break inputs.

AISHELL-3 training independence remains **UNKNOWN** unless official documentation establishes otherwise.

## 4. Population, construction, and split semantics

Stage A has exactly 23 planned cases: the same frozen Day10 source/reference pairs and IDs, with the inherited provenance labels train=11, val=6, and test=6. There is no case replacement, source replacement, reference replacement, or transcript change. Cases are processed in ascending `paired_case_id` order with generation seed `20260905 + zero-based_case_index`; a backend that cannot accept and record this deterministic seed policy is ineligible. The source/reference provenance, exact transcript policy, whole-source-utterance unit, natural synthetic duration, mono 16-kHz serialization, 400-sample crossfade, sample-first dual timeline, and detector denylist are reused unchanged. The generator backend is the only intended manipulation change.

The **primary Stage-A analysis population is all successful new second-generator cases**. The inherited train/val/test labels are retained only for provenance and stratified descriptive reporting. They are not used for fitting, threshold selection, generator selection, region selection, detector selection, or parameter tuning. Existing Week1 thresholds and B1b detector settings are inherited unchanged. No authoritative existing protocol requires a test-only Stage-A headline, so this all-case primary population does not conflict with the frozen Week2 protocol.

The source/reference provenance also carries the descriptive `generation_topology` field (for example, `END_TO_END_REFERENCE_CONDITIONED` or `TTS_PLUS_VOICE_CONVERSION`). This field is lineage metadata only; it is not an outcome-dependent eligibility criterion or tie-break input.

## 5. Failure and missingness policy

Planned denominator is 23. Each planned case terminates as `SUCCESS` or an unchanged Week2 A2 hard-failure class. At most one same-case infrastructure retry is permitted only for a clearly transient non-semantic failure; text, source, reference, seed, model revision, and settings remain identical, and both attempts are recorded. No failed case is replaced.

The primary scientific analysis set is the **SUCCESSFUL-GENERATION ANALYSIS SET**. Every result reports planned=23, successful count, failure count, and failure classes. If fewer than 23 cases succeed, the achieved denominator and missingness limitation are reported; an exact paired 23-case follow-up is not claimed. No failure count defines a scientific performance threshold or triggers an outcome-driven rerun.

## 6. Primary detector, shared score representation, and regions

The primary detector is frozen **B1b** at frozen **S2_1500ms_250ms**. It uses the inherited reference-free sequence-local robust-prototype score and unchanged Week1 threshold provenance. Primary metrics are threshold-free AUROC and AUPRC; F1 is not a primary endpoint.

All regions are sample-first half-open intervals on the manipulated timeline:

- `FULL_ATTACK = [attack_start_sample, attack_end_sample)`;
- `STRICT_CORE = [attack_core_start_sample, attack_core_end_sample)`;
- `BOUNDARY_BLEND = FULL_ATTACK minus STRICT_CORE`, namely `[attack_start_sample, attack_core_start_sample)` union `[attack_core_end_sample, attack_end_sample)`;
- `OUTSIDE_CLEAN = [0, attack_start_sample)` union `[attack_end_sample, manipulated_num_samples)`.

The existing frozen speaker-window GT projection remains the sole score-window mapping: majority label threshold 0.5; `core` when `core_overlap_ratio >= 0.5`; `boundary` when not core and the window overlaps `FULL_ATTACK`; otherwise `outside`. No seconds-based, center-based, or post-hoc zone rule is introduced. Existing valid-score and speech-mask semantics are retained unchanged.

At S2, a 400-sample blend edge is smaller than one half-window. Consequently, a standalone `AUROC_boundary` positive class is not a stable endpoint under the inherited majority-label representation and is not computed. The frozen continuous boundary alternative is the case-level score contrast in H2 below.

## 7. H1 — primary transfer estimands

For the all-successful Stage-A population, report the co-primary estimates `AUROC_full` and `AUPRC_full`. `full` uses the inherited `is_attack_window` labels. Each point estimate is computed by concatenating valid B1b/S2 score-label pairs across the successful cases; uncertainty is the case bootstrap specified below. Strict-core AUROC/AUPRC are H3 quantities, not additional H1 endpoints.

The secondary fixed historical comparison uses the same `paired_case_id` values that are successful in Stage A and available in frozen Week2 case metrics. For each retained pair, calculate the new-minus-historical full-GT case AUROC and AUPRC under matching B1b/S2 definitions; report their paired case-bootstrap mean differences and CIs. This comparison is descriptive secondary evidence only. No binary rule defines “replication,” “recovery,” “similarity,” or “success.”

## 8. H2 — primary core-versus-boundary decomposition

For every successful case, calculate the arithmetic mean of finite B1b/S2 scores in each inherited speaker-window zone: `mean_score_core`, `mean_score_boundary`, and `mean_score_outside`. The primary H2 estimand is `DELTA_BOUNDARY_CORE = mean_score_boundary - mean_score_core`. Its point estimate is the arithmetic mean of computable case-level differences. `mean_score_outside` is reported as a required contextual primary decomposition quantity but is not substituted into another contrast after observation.

Every output reports planned, successful, computable, and unavailable case counts for every zone quantity. A case with no finite score in a required zone is retained in the generation denominator, marked unavailable for that contrast with its reason, and never replaced. No term such as “boundary fires,” “flat,” or “substantially above” controls a decision.

## 9. H3 — primary blend-exclusion effect

From the same valid B1b/S2 score timeline, calculate `AUROC_full`, `AUPRC_full`, `AUROC_core`, and `AUPRC_core` under the inherited full/core labels. The co-primary continuous H3 effects are `DELTA_FULL_CORE_AUROC = AUROC_full - AUROC_core` and `DELTA_FULL_CORE_AUPRC = AUPRC_full - AUPRC_core`. Each is estimated on the all-successful population and receives the paired case-bootstrap uncertainty specified below. No magnitude threshold defines whether blend exclusion “erases” a signal.

## 10. B4 and ECAPA roles

**B4 is DIAGNOSTIC_ONLY.** Its magnitude cannot determine Stage-A PASS/HOLD, H1/H2/H3, generator selection, case inclusion, or a claim gate.

**ECAPA similarity is EXPLORATORY_ONLY.** Week2 Day12 did not show a consistent monotonic global ECAPA-similarity mechanism. It cannot become a Stage-A primary hypothesis or define an endpoint, threshold, generator choice, case filter, or confirmatory interpretation.

## 11. Statistical contract and multiplicity

The inferential unit is `paired_case_id`; windows and frames are never independent inferential units. Every primary estimate uses a 95% percentile case-bootstrap CI with `N=2000` and seed `20260905`.

- For H1 and H3, resample successful case IDs with replacement, carrying each case's complete valid score/label arrays together; concatenate sampled arrays before calculating AUROC/AUPRC and the named delta.
- For H2 and secondary historical effects, resample case IDs with replacement while carrying each case's complete required zone values or paired historical/new values together; calculate the mean case-level contrast in each replicate.
- Undefined statistics are never replaced by zero. Record valid and undefined replicate counts. Compute a CI only from finite valid replicates when at least 1900 of 2000 (95%) are finite. Otherwise record `CI=NOT_REPORTABLE`, preserve all cases, and flag the affected scientific estimate without rerunning for a preferable result.

This is an **ESTIMATION-FIRST** design. H1, H2, and H3 are co-primary estimand families; every named endpoint and CI is reported, with no result-dependent selection, p-value declaration, or categorical global success/failure gate.

## 12. Claim boundary

Allowed reporting is bounded to the named second generator, immutable revision, frozen construction, realized denominator, and listed estimates/CIs. If the second-generator estimates are low, report that bounded observation without universal-failure language. If fixed historical paired estimates differ, report the named new-minus-historical difference and CI without a formal “substantial” rule. If `DELTA_BOUNDARY_CORE` is positive, report that direction and CI without claiming a causal boundary mechanism.

Regardless of outcome, Stage A does not establish universal TTS detection, deepfake detection, adaptive robustness, native-audiobook generalization, speaker causality, unseen-generator generalization, or deployment readiness. Two tested generators do not equal universal generalization.

## 13. Execution boundary

Before Stage-A execution, record the selected candidate's eligibility evidence, tie-break result, immutable provenance, and engineering-feasibility evidence. Then obtain a separate execution authorization. No result-dependent protocol change is permitted after candidate selection or after any Stage-A output, score, or QA observation.
