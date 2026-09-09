# A2 Sidecar Contract Audit (pre-registered field contract)

The A2 sidecar is an **additive** manifest (Day-2 schema untouched). One
row per planned case per generation attempt; failed rows retained.
Access classes: REQUIRED (validator fail-closed), OPTIONAL (recommended),
DIAGNOSTIC ONLY (analysis/QA; never a detector input, never a filter),
FORBIDDEN TO DETECTOR (must never reach the evaluation input path).

## 1. Case identity

| Field | Class |
|---|---|
| protocol_version | REQUIRED |
| paired_case_id | REQUIRED |
| attack_id | REQUIRED |
| attack_type (= same_text_tts_replacement) | REQUIRED |
| split | REQUIRED |
| generation_status / generation_failure_reason | REQUIRED |
| generation_attempt_count | REQUIRED |

## 2. Source utterance & clean timeline

| Field | Class |
|---|---|
| source_sample_id (= target_source_sample_id lineage) | REQUIRED |
| clean_sequence_id | REQUIRED |
| clean_timeline_start_sample / clean_timeline_end_sample (= c0/c1) | REQUIRED |
| source_real_num_samples / source_real_duration | REQUIRED |
| source_text_exact + source_text_sha256 | REQUIRED |
| transcript lineage (longform row reference) | REQUIRED |
| duration_ratio | REQUIRED |
| duration_delta_samples | REQUIRED |

## 3. Manipulated timeline

| Field | Class |
|---|---|
| manipulated_sequence_id / manipulated_audio_relpath | REQUIRED |
| manipulated_timeline_start_sample / manipulated_timeline_end_sample | REQUIRED |
| final_synthetic_num_samples / synthetic_duration | REQUIRED |
| pretrim_num_samples / pretrim_duration / posttrim_num_samples /
  posttrim_duration / leading_trim_samples / trailing_trim_samples | REQUIRED |
| generator_output_sample_rate / channels | REQUIRED |

## 4. Speaker & reference (construction-side)

| Field | Class |
|---|---|
| target_speaker | REQUIRED (lineage/audit) — **FORBIDDEN TO DETECTOR** |
| replacement_speaker (= target_speaker_conditioning_intent_only) | REQUIRED |
| reference_audio_path / reference_sample_id / reference_speaker | REQUIRED — **FORBIDDEN TO DETECTOR** |
| reference_text_exact / reference_text_sha256 / reference_audio_sha256 / reference_preprocessing | REQUIRED — **FORBIDDEN TO DETECTOR** |
| reference↔synthetic ECAPA cosine | DIAGNOSTIC ONLY |

## 5. Text lineage

| Field | Class |
|---|---|
| normalized_for_tts / tts_input_text + tts_input_text_sha256 | REQUIRED |
| text_normalization (= identity after NFC/edge validation) | REQUIRED |
| same_text_exact / same_text_semantic | REQUIRED |

## 6. Generator & runtime provenance

| Field | Class |
|---|---|
| attack_generator / attack_generator_family / generator_role / tts_mode / voice_conditioned / speaker_match_intent | REQUIRED |
| generator_version / code_revision / checkpoint_revision / checkpoint_sha256 / config_sha256 / frontend / vocoder / training_data_provenance | REQUIRED (values may be `TO_BE_VERIFIED…` only before Day 9 close) |
| generation_seed | REQUIRED |
| runtime (python/torch/speechbrain/serialization versions) | REQUIRED |
| hardware (cpu/gpu model, thread count) | REQUIRED |
| repo state identifier (hash chain reference; git hash if available) | REQUIRED |
| input/output audio SHA-256 | REQUIRED |
| resampler algorithm+version | REQUIRED |

## 7. DSP

| Field | Class |
|---|---|
| rms_reference / rms_gain_requested / rms_gain_clamped / rms_gain_peak_safe / rms_gain | REQUIRED |
| peak max abs (post-gain) | REQUIRED |
| crossfade_samples / crossfade formula anchor fields | REQUIRED |

## 8. GT (dual timeline)

| Field | Class |
|---|---|
| attack_start/end_sample, attack_core_start/end_sample, blend_start/end_sample, blend_in_start/end_sample, blend_out_start/end_sample | REQUIRED |
| attack_start/end (seconds) | REQUIRED |
| prefix/suffix/core/blend verification verdicts | REQUIRED |

## 9. QA / diagnostics

| Field | Class |
|---|---|
| qa_flags (high_asr_cer, low_speaker_similarity, audible_artifact, unusual_prosody, low_detector_score) | DIAGNOSTIC ONLY |
| asr_backend / asr_transcript / asr_cer | DIAGNOSTIC ONLY |
| reference_synthetic_ecapa_cosine | DIAGNOSTIC ONLY |
| target_synthetic_ecapa_cosine | DIAGNOSTIC ONLY |
| raw generator output path (pre-DSP) | OPTIONAL (recommended; large-file registry entry) |
| wall-clock time, host load | OPTIONAL |

## 10. FORBIDDEN TO DETECTOR (evaluation input path)

The following sidecar fields must never be reachable by B0/B1a/B1b/B2/B4
at scoring time (enforced by an input-path unit test on the evaluation
loader): reference audio/embedding/path, target or reference speaker ID,
clean original waveform/path, transcript/text IDs, generator identity or
any provenance metadata, ASR/QA outcomes, all GT interval fields, split
labels (scoring is split-agnostic; split is used only for reporting).

## 11. Validator rules

- A row is VALID iff every REQUIRED field is present, hash-evidenced, and
  internally consistent (e.g. `attack_end = c0 + N_syn`;
  `core = attack ± 400`; `delta = N_syn − N_real`;
  `tts_input_text_sha256 == source_text_sha256`).
- Failed rows are VALID rows with `generation_status = failure`.
- No field may be back-filled after Day-10 freeze except via an amendment
  record.
