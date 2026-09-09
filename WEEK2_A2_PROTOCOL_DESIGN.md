# Week 2A A2 Same-Text TTS Replacement Protocol

Status: **DESIGN FROZEN**  
Protocol version: `week2a-a2-v1.1-corrected`  
Design date: 2026-09-05  
Week 2A protocol-design gate: **PASS**

Pre-implementation semantic correction: `WEEK2_A2_PREIMPLEMENTATION_CORRECTION.md`  
Implementation readiness: **HOLD**

This document freezes the design only. It does not authorize an unrecorded generator, checkpoint, text frontend, reference rule, retry, DSP variant, or detector change. No TTS package or checkpoint was installed or downloaded, no synthetic audio was generated, and no detector was trained during Week 2A.

## 1. Scientific Motivation

Week 2 asks whether a reference-free temporal detector can localize a bounded synthetic replacement when linguistic content is held fixed as tightly as the generator interface permits. The objective is mechanism discovery, not a required positive detection result.

Pre-registered questions are:

1. Does the frozen Week 1 B1 speaker-representation inconsistency score retain localization signal on same-text synthetic replacement?
2. Does target-speaker conditioning reduce B1 relative to cross-speaker A0/A1?
3. Do the frozen Day 5 temporal/prosodic measurements provide signal not present in B1?
4. Does a generator create a distinctive temporal signature? Week 2A can answer this only for one tested family.
5. Does signal generalize to an unseen generator? This is reserved for Week 2C and is not a Week 2A claim.

## 2. Gap Left by Week 1

Week 1 froze cross-speaker, different-utterance, different-text A0/A1 attacks and same-speaker, different-utterance, different-text C0 controls. C0 showed that merely changing utterance/text did not create useful positive B1 localization, but it did not isolate synthetic generation while preserving the target transcript. A2 supplies that missing condition.

The Week 1 long forms remain constructed sequences, so A2 still does not establish native audiobook behavior. The 24 clean sequences, 12 speakers, 23 reusable paired-case lineage records, and all Week 1 artifacts remain unchanged.

Semantic correction v1.1 makes one distinction normative: a Week 1 0.75/1.5/2.5 s crop is waveform-only and has no separately annotated complete transcript, so it cannot be the strict same-text synthesis unit. A2 may reuse its `paired_case_id` and `target_source_sample_id` to make selection deterministic, but A2 derives new bounds from the complete source-utterance lineage row. It never reuses the Week 1 crop bounds or duration tier.

## 3. Threat Model

The primary attacker knows the exact transcript and complete real source-utterance interval to replace, has one other recording and its transcript from the same target speaker, and can run a fixed pretrained voice-conditioned TTS generator. The attacker may trim generator-added edge silence, resample to 16 kHz mono, apply one global RMS gain, and apply the fixed 25 ms linear edge crossfade defined in Section 12. The attacker does not time-stretch, denoise, encode with a lossy codec, optimize against the detector, use detector scores to select generations, or change samples outside the full replacement interval.

The detector receives only the manipulated suspect sequence. The TTS reference is attack-construction input and is never detector input. The detector receives no speaker ID, enrollment audio, clean original, generator label, transcript, attack interval, or generation-QA result. B3 is excluded from the primary experiment because it requires the clean original.

The generator is known only in the descriptive sense that the reported pilot names it. No generator-specific detector training or threshold fitting is permitted. Full details are also recorded in `THREAT_MODEL_WEEK2_DRAFT.md`.

## 4. A2 Definition

`A2` remains the schema name `same_text_tts_replacement`. The primary pilot subtype is:

- `A2-V`: whole-utterance, exact-input-text, target-speaker-conditioned TTS replacement;
- `tts_mode = zero_shot_voice_conditioned` only if the selected implementation demonstrably exposes that mode;
- `speaker_match_intent = target_conditioned_not_verified_identity`.

The protocol does not rename every A2 case “voice cloning,” “deepfake,” or “speaker replacement.” Those descriptions may be used only where the selected model and measured conditioning justify them. `A2-G`, a fixed generic synthetic voice, remains a future control because it would leave a large speaker-change confound and would mainly extend the Week 1 mismatch condition.

## 5. Generic vs Voice-Conditioned TTS

| Property | A2-G generic voice | A2-V target-speaker conditioned |
|---|---|---|
| Engineering complexity | Lower | Higher |
| Same-input-text control | Yes | Yes |
| Speaker mismatch control | Poor | Stronger but imperfect |
| Relevance to impersonation | Limited | Direct, given attacker reference access |
| Reference/leakage risk | None | Must be explicitly controlled |
| Interpretation of B1 | Likely dominated by speaker change | Tests whether B1 survives attempted speaker matching |

**Decision:** Week 2A uses only A2-V. A2-G is useful later as a mechanistic positive control, but adding it now would double conditions without closing the central scientific gap.

## 6. Selected Pilot Condition

The primary condition is `A2-V / CosyVoice2-0.5B candidate / complete-source-utterance / natural-duration / silence-trimmed / active-speech-RMS-matched / fixed-25ms-linear-crossfade`.

The first generator family is **CosyVoice**, with the official `CosyVoice2-0.5B` checkpoint as the pre-implementation candidate. Official materials explicitly document Chinese zero-shot usage, a 0.5B checkpoint, and Apache-2.0 licensing. The exact repository commit, model revision, complete component licenses, checkpoint files and SHA-256 hashes, CUDA/CPU requirements, output sample rate, deterministic behavior, Windows feasibility, and training-corpus relation to AISHELL-3 are **TO BE VERIFIED BEFORE IMPLEMENTATION**. A failure of any hard check reopens generator selection before any sample is generated; it does not permit silent substitution.

F5-TTS is the second-family candidate for a later phase: its official interface accepts reference audio/text and generated text and supports Chinese/English, but the official pretrained weights are CC-BY-NC due to Emilia. It is not part of this pilot. The repository currently contains no approved Chinese TTS checkpoint; the existing `pretrained` material is not treated as an A2 generator.

Selection evidence (accessed 2026-09-05):

- CosyVoice official repository/model documentation: <https://github.com/FunAudioLLM/CosyVoice> and <https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B>
- F5-TTS official repository/model card: <https://github.com/SWivid/F5-TTS> and <https://huggingface.co/SWivid/F5-TTS>

## 7. Same-Text Semantics

The authoritative source is the `transcript_zh` string joined from `data/manifests/day45_source_audio.csv` by `target_source_sample_id`. The pilot uses an identity text policy:

1. `source_text_exact` preserves the source manifest string unchanged.
2. The string must be non-empty, valid Unicode, already NFC, and have no leading/trailing whitespace. Failure is retained; the string is not repaired.
3. `normalized_for_tts` and `tts_input_text` must be code-point identical to `source_text_exact`.
4. Chinese/full-width punctuation, Arabic numerals, English letters, case, spaces, and all other visible characters are preserved and sent as-is. No punctuation insertion/removal, number expansion, letter transliteration, pinyin substitution, or whitespace collapse is allowed in the adapter.
5. `text_normalization = identity_after_nfc_and_edge_whitespace_validation`.
6. `same_text_exact = true` only when exact code-point equality holds and the UTF-8 SHA-256 hashes are equal. Every primary case requires this.
7. `same_text_semantic = true` follows from exact equality for the primary pilot; it is not inferred from an ASR transcript.
8. `text_id` remains the AISHELL-3 target `text_id`; a separate `tts_text_id` may identify the generation request.

The generator's internal frontend may still normalize numbers, punctuation, English, polyphonic characters, or erhua. Its frontend name/version/config must be recorded. Such internal behavior is a generator property, not permission to alter the manifest input. Pronunciation ambiguity and ASR CER are QA diagnostics. Phoneme or pinyin overrides would define a different future condition.

Hashes are computed over the exact UTF-8 bytes without an added newline. “Input same-text” is ground truth about request lineage; “spoken-content match” is a diagnostic and must not be conflated with it.

## 8. Speaker Reference Protocol

One reference utterance is selected once per target speaker and reused for that speaker's cases. It must:

- come from the frozen Week 1 source catalog and the same speaker and split;
- have a different `source_sample_id` and `text_id` from every target it conditions;
- not occur in either attacked clean sequence for that speaker;
- have decoded duration in `[3.0, 8.0]` seconds, finite non-empty audio, and an exact catalog transcript;
- be chosen by ascending `selection_rank`, then `sample_id`, after applying only these pre-frozen eligibility rules.

If no utterance qualifies, all planned cases for that speaker are retained as failed with `no_eligible_reference`; no speaker or target is substituted. Reference audio stays read-only. Any generator-required resampling/channel conversion is deterministic and recorded, but no denoise, loudness normalization, voice conversion, or content editing is allowed. The reference file, transcript, hashes, original format, preprocessing, and reuse count are recorded.

A read-only eligibility audit on 2026-09-05 resolved the frozen references below; durations are decoded source-WAV durations. Implementation must reproduce this table exactly before generation:

| Speaker | Reference sample | Duration (s) |
|---|---|---:|
| SSB0005 | SSB00050014 | 7.377 |
| SSB0009 | SSB00090015 | 5.072 |
| SSB0011 | SSB00110018 | 3.803 |
| SSB0073 | SSB00730017 | 3.243 |
| SSB0139 | SSB01390022 | 3.136 |
| SSB0197 | SSB01970016 | 5.627 |
| SSB0261 | SSB02610029 | 4.359 |
| SSB0309 | SSB03090014 | 4.323 |
| SSB0342 | SSB03420018 | 6.176 |
| SSB0393 | SSB03930020 | 3.346 |
| SSB0434 | SSB04340024 | 3.529 |
| SSB1100 | SSB11000026 | 4.640 |

Reference access is an attacker capability. The detector remains reference-free and enrollment-free. The target utterance itself, its clean long-form occurrence, and val/test detector information are forbidden as prompt audio.

## 9. Generator Selection Criteria

Before generation, a candidate must pass: Mandarin and exact text-input support; explicit voice conditioning/zero-shot mode; usable research license for code, weights, frontend, vocoder and dependencies; immutable version/revision and checkpoint hashes; offline cached inference after authorized acquisition; deterministic seed/config capture or documented nondeterminism; supported local hardware; and a successful Windows smoke test or a frozen isolated execution environment.

The following comparison is a selection record, not an experimental result:

| Criterion | CosyVoice family | F5-TTS family |
|---|---|---|
| Mandarin | Explicit official support | Chinese/English official weights |
| Voice conditioning | Explicit zero-shot path | Reference audio/text interface |
| Published pilot-sized model | 0.5B CosyVoice2 | 0.3B F5-TTS base |
| Reported weight license | Apache-2.0 model page | CC-BY-NC-4.0 model card |
| Windows feasibility | Not established by reviewed official instructions | PyTorch install paths exist; end-to-end Windows still unverified |
| Training-data/AISHELL-3 independence | Unknown | Emilia reported; AISHELL-3 overlap still not proven absent |
| Determinism | Must be measured | Must be measured |

No claim of strict generator training-data independence is permitted without documentary evidence. Unknown contamination is a recorded limitation.

## 10. Pilot Data Selection

The pilot reuses every frozen Week 1 `paired_case_id` exactly once **as case lineage only**: select the A0 row of each case from `data/manifests/day45_attack_manifest.csv`, use it to identify `target_source_sample_id`, target speaker, split and clean sequence, then join that source ID to `data/manifests/day45_longform_manifest.csv`. A2 replaces the **entire source utterance** at that long-form row's `sequence_start/sequence_end` bounds. At implementation preflight, materialize `c0=round(sequence_start*16000)` and `c1=round(sequence_end*16000)` once, validate them against sequence construction and decoded source length, and treat those integer bounds—not the floating values—as authoritative.

The Week 1 `target_start_sample`, `target_end_sample`, `attack_start_sample`, `attack_end_sample`, `duration_tier`, donor crop, and 0.75/1.5/2.5 s length are explicitly **not inherited**. They only identify the older local A0/A1 construction and must be rejected if copied into an A2 request or manifest. Thus Week 1 contributes deterministic speaker/case/source selection, not the A2 attack interval.

Frozen planned count:

- 12 speakers: train/val/test = 6/3/3;
- 23 unique target texts and 23 A2-V cases: train/val/test = 11/6/6;
- one A2-V generation request per case;
- the same 23 clean counterparts; no new clean audio construction.

Targets are not replaced after listening, QA, ASR, detector scoring, or generation failure. The one Week 1 clean sequence without a paired lineage row remains out of the A2 pilot. The old short-duration tiers describe A0/A1 crops only and are not A2 attack-duration tiers. Short-attack temporal resolution remains an independent Priority 2 protocol and is not tested by this whole-utterance A2 pilot.

## 11. Duration-Mismatch Policy

Three candidate policies were reviewed:

| Policy | Validity | GT/comparability | Shortcut risk |
|---|---|---|---|
| P1 natural synthetic duration, shift suffix | Preserves generated timing/prosody | Requires dual timelines; not clean-grid aligned | Lowest artificial DSP risk |
| P2 crop/pad to old interval | Can truncate speech or label padding as attack | Same total length but ambiguous content/GT | Padding/truncation shortcut |
| P3 time-stretch to real duration | Alters generator output and prosody | Same grid and convenient pairing | Strong stretch/pitch/tempo shortcut |

**PRIMARY = P1.** Let the clean whole-source-utterance interval be `[c0, c1)` and the final post-trim/post-resample/post-gain synthetic waveform contain `N_syn` samples. After the fixed in-interval edge crossfade, the replacement still contains exactly `N_syn` samples. The manipulated sequence is `clean[:c0] + crossfaded_synthetic + clean[c1:]`; its length changes by `delta = N_syn - (c1 - c0)`. All downstream source/gap intervals shift by exactly `delta`. No time stretch, speed change, crop-to-fit, or pad-to-fit is permitted.

P2 and P3 require separately named future conditions and cannot be mixed into primary results. Natural-duration changes mean clean and manipulated waveforms are not sample-aligned after the attack; B3 same-grid comparison is invalid.

## 12. Silence and DSP Policy

Generator output is first decoded in float form and audited. Edge silence is handled deterministically using the already frozen Day 5 pause threshold: 25 ms frames, 10 ms hop, active when frame level is greater than `-45 dBFS`. Keep from 50 ms before the first active frame to 50 ms after the last active frame, clipped to available samples. No active frame is `no_speech_detected`. Record pre-trim and post-trim samples/durations and leading/trailing samples removed. The clean target is not trimmed.

The final A2 waveform is standardized to mono 16 kHz with one frozen, versioned deterministic resampler. Resampling occurs before silence measurement and gain measurement. Match the synthetic active-speech RMS to the complete clean source utterance's active-speech RMS under the same `-45 dBFS` rule. Clamp requested gain to `[0.25, 4.0]`, then reduce it further only if necessary to keep absolute peak below `0.999`; record requested, clamped, peak-safe, and final gains. This is one scalar multiply, not compression or limiting.

`crossfade_samples = 400` **per edge** (25 ms at 16 kHz) for the primary condition, following the Week 1 A1 artifact-control principle. Week 1 found that constructed transitions/boundaries create many outside false positives; a hard unblended A2 splice would unnecessarily entangle a generator signal with an avoidable boundary discontinuity. This choice is a control, not evidence that the output is perceptually natural or harder to detect.

Let `L=400`, clean complete-source interval `[c0,c1)`, source length `N_real=c1-c0`, and scaled synthetic samples `s[0:N_syn]`. Require `2L < min(N_real,N_syn)` or retain a hard failure. The two linear blends use the same weight convention as A1:

```text
alpha_in[i]  = (i + 1) / (L + 1),           i = 0..L-1
alpha_out[i] = (L - i) / (L + 1),           i = 0..L-1
left[i]  = clean[c0+i]       * (1-alpha_in[i])  + s[i]             * alpha_in[i]
right[i] = clean[c1-L+i]     * (1-alpha_out[i]) + s[N_syn-L+i]     * alpha_out[i]
core     = s[L:N_syn-L]
```

Concatenating `left + core + right` preserves the natural synthetic length `N_syn`; samples before `c0` and the shifted clean suffix beginning at original `c1` are untouched. The use of removed clean target edge samples as blend anchors must be explicit in lineage. Boundary jumps, B4 and edge envelopes remain mandatory shortcut diagnostics because crossfade can itself be a signature.

No loudness (LUFS) matching, peak normalization beyond the peak-safe scalar bound, denoise, dereverberation, EQ, codec, time stretch, pitch shift, prosody instruction, post-generation silence insertion, or selective normalization is allowed. Final serialization format and library version must be frozen before implementation (preferred: mono 16 kHz PCM WAV), and sample counts are taken from the serialized-decoded result before crossfade reconstruction.

## 13. Ground-Truth Semantics

A2 full ground truth is the half-open interval occupied by the actual final crossfaded synthetic replacement in the manipulated sequence. It includes both edge blends. Strict-core ground truth excludes both blends:

```text
attack_start_sample = clean target utterance start sample
attack_end_sample   = attack_start_sample + final synthetic sample count
attack interval     = [attack_start_sample, attack_end_sample)
attack_core_start_sample = attack_start_sample + 400
attack_core_end_sample   = attack_end_sample - 400
left blend zone     = [attack_start_sample, attack_core_start_sample)
right blend zone    = [attack_core_end_sample, attack_end_sample)
seconds             = sample index / 16000
```

For compatibility with Week 1 semantics, `blend_start_sample = attack_start_sample` and `blend_end_sample = attack_end_sample` span the complete changed region, while explicit `blend_in_start/end_sample` and `blend_out_start/end_sample` identify the two actual mixture zones. The original complete real interval `[clean_timeline_start_sample, clean_timeline_end_sample)` is retained separately. Every source utterance and gap gets clean and manipulated timeline bounds. Prefix intervals are unchanged; suffix intervals shift by `duration_delta_samples = N_syn-N_real`. GT must never use the old short Week 1 interval or the original real duration as `attack_end`, unless synthetic duration happens to equal it.

Waveform verification must prove prefix bit equality through `attack_start_sample`, suffix equality under the exact offset `delta`, exact final length, strict-core equality to scaled synthetic samples, exact reconstruction of both blends from the frozen formula and clean target edge anchors, valid bounds, and seconds/sample consistency. AISHELL-3 source files remain read-only.

## 14. Manifest Extension

The extension is **designed in `configs/week2a_a2_protocol_draft.yaml`; implementation validation is pending**. It is additive and must not edit or reinterpret the frozen Day 2 schema. A2 uses a sidecar attack/lineage manifest joined by `sample_id`, `pair_id`, `paired_case_id`, and `source_sample_id`.

Day 2 semantics remain:

- `source_type = natural`, because the base long form is natural;
- `generator = human`, `generator_family = human`, and `source_generator = human` describe the base source;
- `is_manipulated = true`, `attack_type = same_text_tts_replacement`;
- `attack_generator` and new `attack_generator_family` identify the synthetic replacement;
- `replacement_speaker = target_speaker` expresses conditioning intent only; `speaker_match_intent` prevents it being misread as verified identity.

Required A2 fields include generator code/model/frontend/vocoder versions and hashes; text strings and hashes; reference provenance; clean/manipulated sample timelines; pre/post-trim and source/synthetic durations; duration ratio/delta; DSP parameters; sample-first GT; generation status/failure; seed/attempt; ASR and acoustic QA diagnostics; and split. Empty values are allowed only where status makes a field inapplicable, and failures remain rows.

The minimum named extension is: `attack_type`, `source_type`, `attack_generator`, `attack_generator_family`, `generator_family`, `generator_version`, `generator_code_revision`, `generator_checkpoint_sha256`, `tts_mode`, `voice_conditioned`, `reference_audio_path`, `reference_sample_id`, `reference_speaker`, `source_text_exact`, `normalized_for_tts`, `tts_input_text`, `text_normalization`, `same_text_exact`, `same_text_semantic`, `source_text_sha256`, `tts_input_text_sha256`, `synthetic_duration`, `source_real_duration`, `duration_ratio`, `pretrim_duration`, `posttrim_duration`, `rms_gain`, `crossfade_samples`, `attack_start_sample`, `attack_end_sample`, `attack_core_start_sample`, `attack_core_end_sample`, `blend_start_sample`, `blend_end_sample`, `blend_in_start_sample`, `blend_in_end_sample`, `blend_out_start_sample`, `blend_out_end_sample`, `clean_timeline_start_sample`, `clean_timeline_end_sample`, `manipulated_timeline_start_sample`, `manipulated_timeline_end_sample`, `generation_status`, `generation_failure_reason`, `generation_seed`, and `split`. The YAML schema inventory adds the component hashes, sample counts, preprocessing, QA and diagnostic fields needed for reproducibility.

## 15. Generation QA

QA is run before detector scoring and without access to detector outputs:

- lineage: target, clean sequence, split, speaker, reference and text joins are unique and valid;
- text: exact equality, NFC/edge-whitespace validation, and matching UTF-8 SHA-256;
- generator: immutable code revision, checkpoint/component hashes, config hash, seed and frontend recorded;
- raw audio: decodable, non-empty, finite, expected channel/sample-rate handling, and no NaN/Inf;
- post-DSP audio: mono 16 kHz, finite, non-empty, peak `< 0.999`, no clipped samples, exact saved/decoded length;
- duration: record raw, post-trim and source durations and their ratio; ratios outside `[0.25, 4.0]` are hard generation failures;
- silence/activity: active frames must exist; trim bounds and removed samples are recorded;
- splice integrity: prefix/suffix equality, strict synthetic core, exact two-edge crossfade reconstruction, timeline shift and full/core GT checks must pass;
- content: one pre-frozen offline Mandarin ASR backend may report normalized CER and decoded transcript as **diagnostic only**; ASR model/version/hash and its evaluation-only normalization must be frozen before generation;
- speaker: reference-to-synthetic and target-to-synthetic ECAPA cosine may be reported as attack QA diagnostic but is never a selection filter or detector input.

ASR cannot define GT. No case is removed solely for high CER, low speaker cosine, poor MOS, unusual prosody, or detector behavior. These cases are reported and may be stratified only as explicitly diagnostic analyses.

## 16. Failure Handling

All 23 planned rows are retained. Hard failures are: generator crash; unreadable/empty/non-finite output; no active speech; source/reference/text lineage failure; exact-input-text failure; unsupported sample-rate/channel conversion; post-DSP clipping/non-finite audio; duration ratio outside `[0.25, 4.0]`; serialization mismatch; or prefix/suffix/GT verification failure.

Use `generation_status = success|failed` and a controlled `generation_failure_reason`. A failed case has no formal attack waveform and is excluded from waveform metrics only because no valid waveform exists; every report must show planned, successful, failed, and reason counts by split/speaker. It is never replaced with another target, text, speaker, reference, seed, or generator.

One retry is allowed only for a documented infrastructure interruption that produced no valid model output. It must use the identical environment, inputs, config and seed; both attempts are logged. Quality-driven resampling, best-of-N generation and manual regeneration are forbidden.

High ASR CER, low speaker similarity, audible artifacts, or poor detector score are retained successful cases if hard integrity checks pass. Unexpected but valid output is scientific evidence about the tested generator.

## 17. Evaluation Protocol

Primary evaluation scores all successful A2-V manipulated sequences with frozen Week 1 definitions. No A2 output may change a feature, grid, trim ratio, GT projection threshold, speech-active threshold, decision threshold, or case selection.

Report by split and pooled only where labeled:

- A2 localization AUROC, AUPRC and F1 on full GT (including blends) and strict-core GT (excluding 400 samples per edge);
- B1 core, blend/boundary and outside anomaly distributions, keeping waveform blend zones distinct from window-overlap boundary labels;
- case-level AUROC/AUPRC/F1 with the number of measurable cases;
- global top-1 peak localization error in seconds;
- original-population and conditional-on-speech-active results side by side, including positive/negative retention;
- planned/success/failure denominators;
- descriptive A2 versus clean false-positive behavior;
- descriptive, duration/occupancy-aware A2 versus matched Week 1 A0/A1 magnitude comparisons.

Apply the frozen Week 1 B0 and B1 train-derived thresholds from their recorded artifacts; do not fit thresholds on A2 train, val or test. Threshold-free metrics are still reported. Bootstrap, if used, resamples `paired_case_id` rather than windows, uses the frozen Week 1 seed/resample count, and discloses that test contains only six planned cases.

A limited claim that a baseline has localization signal requires directionally favorable test AUROC versus 0.5, AUPRC versus attack prevalence, case-level behavior, outside-anomaly audit, and case-bootstrap uncertainty; preferably the relevant CI excludes its null. Failure to meet this criterion is reported as negative/inconclusive, not repaired. Even a positive result supports only this generator/protocol.

## 18. Existing Baselines to Reuse

- Day 5 temporal features on the unchanged 25 ms/10 ms frame grid;
- B0 robust global-scalar anomaly at frozen 100/250/500 ms scales and ablations;
- B1a and B1b on the frozen S1/S2 ECAPA grids, with B1b trim ratio 0.20;
- B2 adjacent/symmetric speaker change;
- B4 energy-transient score as `DIAGNOSTIC ONLY`;
- frozen Day 6C speech-active conditional evaluation (`>= 0.5`) alongside the full population.

B1 stays reference-free. B3 is **forbidden in the primary pilot** because natural-duration replacement removes same-grid pairing after the attack. No interpolation, dynamic time warping, normalized-time embedding comparison, or hidden clean alignment is allowed. Any future lineage-aware B3 must be separately pre-registered and marked `ORACLE / DIAGNOSTIC`.

No supervised classifier, detector retraining, new embedding model, threshold search, window search, feature selection, or test tuning is permitted.

## 19. Leakage Analysis

The largest leakage risk is confusing attack-side target-speaker reference access with detector-side enrollment. The construction code may read the reference; feature/scoring code must not receive its path, embedding, speaker ID, transcript, QA similarity, or generator metadata. Separate process inputs and a fail-closed column denylist are required.

Other controls are: speaker-disjoint Week 1 splits remain frozen; target/reference selection never observes generation or detector outcomes; val/test text or waveform cannot fit thresholds; ASR is diagnostic only; clean originals are verification inputs but not primary detector inputs; and generator training-data contamination is recorded as unknown unless proven otherwise.

## 20. Shortcut Analysis

The largest shortcut risk is a deterministic splice-boundary/silence-envelope cue caused by trimming synthetic edges and placing the result beside the constructed 0.3 s gaps. The primary protocol therefore uses complete utterances, a fixed 25 ms A1-style crossfade, a fixed non-metric-tuned trimming rule, and mandatory boundary-jump/B4, edge-silence, duration-ratio, crossfade-envelope, and clean-transition audits. Crossfade reduces a hard discontinuity confound but is not assumed to eliminate boundary shortcuts.

Potential shortcuts also include resampler or codec fingerprints, time-stretch artifacts, gain/clipping, generator-specific sample rate, leading/trailing silence, frontend pronunciation failures, fixed voice mismatch, and duration changes. Controls are one recorded resampler, no lossy codec, no stretch, scalar gain only, peak-safe no-clipping, target-speaker conditioning, exact text lineage, and stratified diagnostic reporting. One generator cannot distinguish “synthetic speech” from “this generator.”

## 21. Claim Boundaries

If positive, Week 2A may support only: “Under the tested constructed AISHELL-3 long-form protocol, selected same-text, target-speaker-conditioned replacements from the recorded CosyVoice checkpoint exhibit localization signal for the named frozen baseline(s).”

It cannot support general deepfake detection, universal TTS detection, unseen-generator robustness, generic voice-cloning robustness, adaptive robustness, native audiobook robustness, human perceptual realism, deployment readiness, strict generator training-data independence, or causal separation of all speaker/channel/prosody factors. If B1 is near chance, the correct conclusion is that B1 failed under this A2 condition while the protocol may still pass.

## 22. Pilot Gate

The implementation pilot gate is based on correctness and interpretability, never an AUROC target. It passes only if:

1. all 23 planned rows and all failures are accounted for;
2. exact text and reference lineage validate;
3. generator/checkpoint/environment provenance is immutable and complete;
4. final waveforms, DSP, dual timelines and sample-index GT validate;
5. detector/reference separation is audited;
6. frozen baselines and thresholds run without A2 tuning;
7. original and speech-active populations, failure denominators, shortcut diagnostics and claim limits are reported.

A B1 AUROC near 0.5 does not fail this gate. A silent protocol deviation, target replacement, invalid GT, detector leakage, or selective failure deletion does.

**WEEK2A PROTOCOL DESIGN GATE = PASS. IMPLEMENTATION READINESS = HOLD.** The corrected semantics are frozen, but implementation remains paused until every hard preflight item is resolved and readiness is explicitly changed by a later review. This does not mean TTS has run or passed.

## 23. Expansion to Multi-Generator

Week 2B may add at least one second generator family in a named known-generator setting with the same frozen targets, references, text semantics, natural-duration policy, QA and GT. It must not retroactively alter Week 2A.

Week 2C may pre-register generators A/B for any development or threshold fitting and hold generator C completely unseen until final evaluation. Family, checkpoint and vocoder must be represented separately because two checkpoints from one family are not necessarily two independent generators. Thresholding by A2 generator is prohibited unless explicitly scoped as known-generator evaluation. No Week 2B/C implementation occurs in this stage.

## 24. Risks

- CosyVoice2 local Windows support, memory/compute and deterministic inference are not yet verified.
- The complete license chain and exact model revision/hash are not yet captured.
- Pretrained training data may contain AISHELL-3 speakers or text; absence cannot currently be claimed.
- Target-speaker conditioning may be weak or may transfer reference channel characteristics.
- Identity input text does not guarantee identity spoken content; ASR itself is fallible.
- Natural duration weakens direct clean-grid and A0/A1 comparability.
- Silence trimming/RMS matching can themselves become cues despite fixed rules.
- Six planned val and six planned test cases give wide case-level uncertainty.
- Constructed gaps and utterance boundaries remain a major non-native confound.

## 25. Implementation Plan

Implementation must occur only in a later explicitly authorized stage after readiness changes from HOLD:

1. Resolve every hard readiness item and record immutable generator/environment provenance.
2. Materialize and freeze the 23-row selection/reference request manifest without running TTS.
3. Validate text, reference, split and clean-timeline lineage.
4. Run a non-experimental one-case engineering smoke test only after explicit implementation authorization; freeze observed I/O handling before formal generation.
5. Generate exactly one output per planned case under the frozen seed rule and retain failures.
6. Apply the frozen trim/resample/gain chain, reconstruct dual timelines, and fail closed on verification.
7. Run frozen Day 5/B0/B1/B2 and diagnostic B4, then report all denominators and claim limits.

### A2_IMPLEMENTATION_READINESS_CHECKLIST

- [ ] Generator code, model weights, frontend, vocoder and dependency licenses checked.
- [ ] Mandarin and exact text-input behavior verified on the selected immutable version.
- [ ] Exact repository commit, model revision, checkpoint/component SHA-256 and provenance recorded.
- [ ] Possible AISHELL-3 training-data contamination investigated and remaining uncertainty disclosed.
- [ ] CPU/GPU/VRAM/RAM/runtime requirements measured; Windows or isolated runtime smoke-tested.
- [ ] Offline cache layout and no-network formal inference verified.
- [ ] Seed behavior and repeat-run determinism measured; nondeterminism policy frozen.
- [x] Reference selection/access protocol frozen.
- [x] Text normalization, equality and hashing protocol frozen.
- [x] Sample selection frozen at 23 Week 1 paired-case/source lineage records; old local bounds are forbidden.
- [x] Failure/one-retry policy frozen.
- [x] Natural-duration reconstruction policy frozen.
- [x] Silence rule frozen.
- [x] DSP rule frozen, including 400-sample-per-edge linear crossfade; final serialization library/version remains to record.
- [ ] A2 sidecar manifest validator implemented and validated without changing Day 2 semantics.
- [ ] Dual-timeline and sample-index GT implementation tested on synthetic dummy arrays only.
- [ ] Detector input denylist proves no reference/enrollment/generator/ASR/clean leakage.
- [ ] ASR diagnostic backend/version/hash and CER normalization frozen, or ASR explicitly omitted.
- [ ] Week 1 696-hash verification passes immediately before implementation.
- [x] Week 1 artifacts untouched during protocol design.

Unchecked items are **TO BE VERIFIED BEFORE FORMAL GENERATION**. They do not change the frozen scientific choices; a hard failure requires an amended, versioned protocol before any formal output.
