# Threat Model Week 2 Draft

Status: design-frozen Week 2A corrected draft; does not replace `THREAT_MODEL.md`  
Protocol reference: `WEEK2_A2_PROTOCOL_DESIGN.md` (`week2a-a2-v1.1-corrected`)  
Implementation readiness: **HOLD**

## Security question

Given a constructed long-form sequence containing one whole-utterance, same-input-text, target-speaker-conditioned synthetic replacement, can a reference-free non-trained temporal baseline localize the actual synthetic interval?

The experiment tests the named construction and generator, not generic “deepfake detection.” A null localization result is valid evidence.

## Attacker capability

The attacker can:

- identify one frozen complete source utterance and know its exact catalog transcript;
- access one other 3–8 s utterance plus exact transcript from the same target speaker and split;
- use a fixed pretrained Chinese voice-conditioned/zero-shot TTS generator;
- generate the same exact input text with a pre-recorded seed/config;
- deterministically resample to mono 16 kHz, trim edge silence under the frozen rule, and apply one bounded active-speech-RMS gain;
- apply one fixed 25 ms (400-sample) linear crossfade at each edge using the removed real source utterance's edge samples as anchors;
- replace the complete real utterance with natural-duration synthetic speech and shift the downstream timeline.

The attacker cannot in this protocol:

- use the target utterance or clean long-form occurrence as reference audio;
- choose targets, references, seeds or generations after hearing outputs or seeing QA/detector results;
- perform best-of-N generation or quality-driven retry;
- crop/pad to the old interval, time-stretch, pitch-shift, denoise, dereverberate, EQ, compress, limit, use a lossy codec, or alter the frozen crossfade;
- access detector internals/scores or optimize adaptively against them.

One identical retry is allowed only after a logged infrastructure interruption with no valid output.

## Generator knowledge

The Week 2A detector is generator-agnostic in its inputs and parameters. The report names the generator for scientific provenance; no generator label reaches the detector and no A2 threshold is trained. The candidate is the CosyVoice family (`CosyVoice2-0.5B`), pending immutable revision, license-chain, environment and hardware verification.

The pilot is a one-generator tested setting, not an unseen-generator experiment. Pretrained training corpora may overlap AISHELL-3 speakers or text; strict independence is unknown unless documentary evidence proves otherwise.

## Speaker reference access

Reference audio is an attack-construction capability, not defender enrollment. It is deterministically selected once per target speaker from the frozen source catalog: same speaker/split; different utterance and text from all that speaker's A2 targets; absent from the attacked clean sequences; 3–8 s; lexicographically/selection-rank first after fixed filters. It may be reused for the speaker's two cases. Failures are retained if no reference qualifies.

The detector must not receive the reference path, waveform, embedding, transcript, speaker ID, reuse count, or reference-to-synthetic similarity.

## Text knowledge and same-text guarantee

The attacker knows `source_text_exact`. The adapter sends an exactly identical Unicode string after verifying, not applying, NFC and edge-whitespace conditions. Punctuation, full-width characters, numerals, English letters, spaces, polyphonic characters and erhua remain unchanged. The exact UTF-8 strings and SHA-256 hashes are stored. Generator-internal text normalization is recorded separately.

Input identity is ground-truth lineage. Spoken identity is audited diagnostically with a pre-frozen ASR if available and never defines GT or post-hoc inclusion.

## Replacement interval and temporal ground truth

The source unit is the complete target utterance identified by each frozen Week 1 paired-case lineage record. The old paired row supplies deterministic case/source lineage only. Its `target_start/end`, `attack_start/end`, 0.75/1.5/2.5 s tier and donor crop are not inherited. A2 joins `target_source_sample_id` to the long-form lineage, materializes `c0=round(sequence_start*16000)` and `c1=round(sequence_end*16000)`, validates those integer bounds, and uses the complete source interval `[c0,c1)`.

If final synthetic length is `N_syn`, the attacker emits:

`clean[:c0] + crossfade_25ms(synthetic[:N_syn], clean[c0:c1] edges) + clean[c1:]`.

The sample-first fields are:

```text
attack_start_sample      = c0
attack_end_sample        = c0 + N_syn
attack_core_start_sample = c0 + 400
attack_core_end_sample   = c0 + N_syn - 400
```

The full attack `[attack_start_sample,attack_end_sample)` contains both 400-sample blend zones. Strict core `[attack_core_start_sample,attack_core_end_sample)` excludes them. The input must satisfy `800 < min(N_syn,c1-c0)`. `duration_delta_samples = N_syn-(c1-c0)`, and downstream clean lineage shifts by exactly that delta. Samples are authoritative; seconds equal sample index divided by 16000. The original clean interval and every clean/manipulated lineage interval are both stored.

No sample-wise alignment is assumed after the attack. Same-grid B3 is prohibited.

## DSP capabilities and channel assumptions

The analysis channel is mono 16 kHz. The generator may emit another rate/channel only if a single deterministic, frozen conversion supports it. Edge silence uses 25 ms/10 ms frames, `-45 dBFS`, and a 50 ms retained margin. Active-speech RMS is matched to the original target with requested gain clamped to `[0.25,4.0]` and a further scalar peak-safe bound below `0.999`.

A fixed 25 ms linear crossfade is applied inside the full replacement at each edge, following the A1 artifact-control principle. It mixes the first/last 400 scaled synthetic samples with the first/last 400 removed clean source-utterance samples; it does not alter samples outside the full attack. This reduces an avoidable hard-splice confound after Week 1 identified boundary/transition false positives, but it does not establish perceptual realism and can itself be a signature. No codec/noise/channel robustness is tested. Resampling, trim, gain, duration, crossfade-envelope and boundary statistics are recorded as shortcut diagnostics.

## Detector knowledge and output

The primary detector sees only the suspect waveform. It has no transcript, speaker metadata/enrollment, reference, clean counterpart, generator metadata, QA/ASR outcome, split-dependent tuning signal, or attack interval.

It produces window anomaly scores and localization metrics using frozen Week 1 Day 5 features, B0, B1a, B1b and B2. B4 is diagnostic only. B3 is disabled. Week 1 thresholds, windows, prototype trimming, GT projection and speech-active mask are reused without A2 tuning.

## Known versus unseen generator distinction

- Week 2A: one-family pilot, provenance known to the evaluator but unused by the detector; pipeline/GT/interpretability gate.
- Week 2B: separately pre-registered multi-generator known-setting evaluation.
- Week 2C: generators A/B available for development or thresholding; held-out family C first accessed for unseen-generator evaluation.

Checkpoint variants from one family must be labeled separately and are not automatically independent generator families.

## Out of scope and claim boundary

Out of scope are generic voice, voice conversion, duration-normalized attacks, multiple simultaneous replacements, adaptive attacks, detector-aware generation, codec/noise/channel perturbation, supervised training, human perceptual testing, native audiobooks and unseen generators.

At most, Week 2A can establish signal or failure for the tested same-text target-speaker-conditioned CosyVoice replacement protocol on constructed AISHELL-3 long forms. It cannot establish universal synthetic-speech, voice-cloning, deepfake, adaptive, unseen-generator, native-audiobook or deployment robustness.

## Principal risks

The largest leakage risk is accidental defender access to attack-side reference/enrollment information. The largest shortcut risk is a boundary/silence envelope induced by deterministic trim adjacent to constructed gaps. Both require fail-closed audits before formal scoring.
