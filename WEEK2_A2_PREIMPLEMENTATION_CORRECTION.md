# Week 2A A2 Pre-Implementation Semantic Correction

Correction date: 2026-09-05  
Supersedes protocol wording: `week2a-a2-v1.0`  
Corrected protocol: `week2a-a2-v1.1-corrected`  
Protocol-design gate: **PASS**  
Implementation readiness: **HOLD**

## 1. Scope

This is a protocol-only semantic correction. Week 2 implementation remains paused. No TTS software or dependency was installed, no checkpoint was downloaded, no audio was synthesized, no detector was trained, and no Week 2B work was started.

No Week 1 frozen artifact is modified. The correction changes only:

- `WEEK2_A2_PROTOCOL_DESIGN.md`;
- `THREAT_MODEL_WEEK2_DRAFT.md`;
- `configs/week2a_a2_protocol_draft.yaml`;
- this correction record.

## 2. Conflict Audit

The scientific conflict is real **if** “reuse the Week 1 exact target interval” is combined with “synthesize the complete AISHELL-3 utterance transcript.” Week 1 paired targets are 0.75/1.5/2.5 s waveform crops inside source utterances. Those crops have source-utterance lineage, but no word/character alignment that supplies an exact transcript for the crop. Sending the complete transcript to TTS and calling the complete generated sentence a strict same-text replacement of the short crop would therefore be false.

The v1.0 files had already partially avoided the error: they stated that `target_source_sample_id` should identify and replace a complete source utterance and that the old crop was not the A2 duration. However, the terms “reuse paired targets” and “paired target selection” did not make the lineage/interval distinction sufficiently fail-closed, and no correction record prohibited copying the old sample bounds. The conflict was therefore a genuine semantic risk before implementation even though the v1.0 duration formula itself used whole-utterance bounds.

## 3. Corrected Primary A2 Unit

PRIMARY remains `A2-V`: same-input-text, target-speaker-conditioned, whole-source-utterance TTS replacement.

Week 1 contributes only deterministic identifiers:

- `paired_case_id`;
- `target_source_sample_id`;
- target speaker and split;
- clean sequence ID.

For each of the 23 cases, A2 joins `target_source_sample_id` to the corresponding row of `data/manifests/day45_longform_manifest.csv`. It materializes `c0=round(sequence_start*16000)` and `c1=round(sequence_end*16000)`, validates those bounds against sequence construction and decoded source length, and makes the integers authoritative. The A2 clean source interval is that complete source-utterance interval. Its transcript is the complete `transcript_zh` for the same source sample.

The following Week 1 values are forbidden as A2 bounds or duration metadata:

- `target_start_sample` / `target_end_sample`;
- `attack_start_sample` / `attack_end_sample` from the A0/A1 row;
- `duration_tier` = 0.75/1.5/2.5 s;
- donor crop start/end.

The old tiers remain Week 1 A0/A1 metadata only. Short-attack temporal resolution is an independent Priority 2 experiment, not an A2 duration stratum.

## 4. Natural-Duration Reconstruction

Let the complete real source utterance occupy clean samples `[c0,c1)`, with `N_real=c1-c0`. Let the final post-trim, post-resample and post-gain synthetic sentence contain `N_syn` samples. A2 keeps `N_syn`; it does not stretch, crop or pad to `N_real` or to a Week 1 tier.

After the fixed edge crossfade, the replacement still has `N_syn` samples. The manipulated sequence length changes by:

`duration_delta_samples = N_syn - N_real`.

Every clean interval before `c0` is unchanged. Every original clean utterance/gap after `c1` maps to manipulated samples by adding this delta. Both clean and manipulated start/end samples are mandatory lineage fields. No sample-wise clean/manipulated alignment is assumed after the attack.

## 5. Crossfade Re-Review

The v1.0 default `crossfade_samples=0` is corrected to a fixed 25 ms = 400 samples **per edge** at 16 kHz.

Reason: Week 1 established that constructed transitions/boundaries account for many outside false positives. An unblended hard splice would leave a controllable boundary discontinuity confounded with the synthetic-speech condition. Applying the already established A1 artifact-control principle is therefore more defensible for the primary A2 pilot.

The crossfade does not modify context outside the full A2 replacement. It blends:

- the first 400 scaled synthetic samples with the first 400 samples of the removed complete real source utterance;
- the last 400 scaled synthetic samples with the last 400 samples of the removed complete real source utterance.

The same linear A1 weights are frozen. Require `800 < min(N_real,N_syn)`; otherwise retain `crossfade_interval_too_short` as a hard generation failure. Crossfade is not claimed to produce perceptual realism, and its envelope remains a mandatory shortcut diagnostic.

## 6. Corrected Sample-First GT

All intervals are zero-based half-open sample ranges at 16 kHz:

```text
attack_start_sample      = c0
attack_end_sample        = c0 + N_syn
attack_core_start_sample = c0 + 400
attack_core_end_sample   = c0 + N_syn - 400

left_blend  = [attack_start_sample, attack_core_start_sample)
strict_core = [attack_core_start_sample, attack_core_end_sample)
right_blend = [attack_core_end_sample, attack_end_sample)
full_attack = [attack_start_sample, attack_end_sample)
```

The full attack contains both blend zones. Strict core excludes them. For compatibility with Week 1, `blend_start/end` span the complete changed region; explicit `blend_in_*` and `blend_out_*` fields identify the two mixture zones. Seconds are always derived as sample index divided by 16000.

Waveform verification must check unchanged prefix, suffix equality under the exact duration shift, synthetic-only core equality, exact reconstruction of both blend zones, final length and sample/second consistency.

## 7. Corrected Manifest/Config Semantics

The corrected config now explicitly records:

- fields inherited from Week 1 as lineage only;
- Week 1 interval/duration fields forbidden for A2;
- complete-source-utterance bounds as the only A2 source interval;
- natural post-trim synthetic duration;
- 400-sample-per-edge linear crossfade and anchor semantics;
- full/core/blend-in/blend-out sample fields;
- dual timelines and suffix delta;
- the separate Priority 2 status of short-duration attacks.

The Day 2 schema and Week 1 manifests are not edited. The A2 additive sidecar validator remains an implementation prerequisite.

## 8. Integrity Checks

The pre-correction read-only audit confirmed:

- 23 unique Week 1 `paired_case_id`/target-source lineage cases;
- every target source ID maps uniquely to a complete long-form source row;
- 12 frozen speakers and 23 unique complete transcripts;
- a valid deterministic 3–8 s reference candidate for every speaker;
- 696/696 Week 1 frozen hashes passing with zero missing/mismatch before correction.

These facts validate selection feasibility only. They do not constitute TTS implementation or synthetic-audio QA.

## 9. Gate Decision

**PROTOCOL SEMANTIC CORRECTION = PASS.** The primary attack unit, text unit, source interval, duration reconstruction, dual timeline and crossfade GT now agree.

**IMPLEMENTATION READINESS = HOLD.** Implementation remains paused by instruction and because generator license chain, immutable checkpoint/component hashes, local hardware/Windows feasibility, offline caching, determinism, final resampler/serialization versions, A2 manifest validator, dummy-array crossfade/dual-timeline tests, detector denylist and optional ASR diagnostic freeze are not yet complete.
