# W7 P4 final human approval packet v1

Status: `PROPOSED_NOT_HUMAN_APPROVED`. This packet is pre-inference and outcome-blind. It does not authorize W7.

Proposed package SHA256: `512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117`
Existing deterministic case-map SHA256: `8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9`

Each family has exactly one recommended Candidate A. Recommendation basis is canonicality, reproducibility, source fidelity, and minimal discretionary choice only. No metric, detector, localizer, gap expectation, or Level-2 outcome was used.

## M1 — conventional_tts_replacement
- Candidate: A
- Implementation: `VITS official single-speaker TTS`
- Parameter set: `VITS_LJS_CANONICAL_V1`
- Bundle hash: `B20CB1B8D4B428C3BDD420041ABA3A2231D3D99C51CF31FFD9D010DCE3E02C03`
- Scientific effect: text-conditioned waveform generation replacing the frozen target span
- Human choice: `APPROVE_A` or `REJECT_AND_STOP`

## M2 — cross_speaker_boundary_control
- Candidate: A
- Implementation: `AudiobookBench deterministic waveform control adapter`
- Parameter set: `CROSS_SPEAKER_BOUNDARY_CANONICAL_V1`
- Bundle hash: `331F4A484A79E2C19FE856A954576F8C68FBE3CECEBB2C31EC8C85ED00CB8CDF`
- Scientific effect: cross-speaker waveform replacement at the frozen target interval with deterministic boundary crossfades
- Human choice: `APPROVE_A` or `REJECT_AND_STOP`

## M3 — neural_speech_editing_infilling
- Candidate: A
- Implementation: `VoiceCraft official neural codec language model`
- Parameter set: `VOICECRAFT_GIGA830M_CANONICAL_V1`
- Bundle hash: `121656A1688F5A4DBBFCBE6B1575DA44E9BA962FAF510E6846CA9D818B5EA803`
- Scientific effect: neural codec-token infilling/editing of the frozen target span conditioned on surrounding speech and transcript
- Human choice: `APPROVE_A` or `REJECT_AND_STOP`

## M4 — same_speaker_splice_crossfade_control
- Candidate: A
- Implementation: `AudiobookBench deterministic waveform control adapter`
- Parameter set: `SAME_SPEAKER_SPLICE_CROSSFADE_CANONICAL_V1`
- Bundle hash: `ABBAC07B1B9721C906BE148FE086D381624B011581A3EB3CEEADE1892474EE6D`
- Scientific effect: same-speaker waveform substitution using a deterministic context window and 400-sample boundary crossfades
- Human choice: `APPROVE_A` or `REJECT_AND_STOP`

## M5 — voice_conditioned_tts_vc_replacement
- Candidate: A
- Implementation: `YourTTS official zero-shot TTS/voice-conversion implementation`
- Parameter set: `YOURTTS_CANONICAL_V1`
- Bundle hash: `2E609C86419FF923519D90809240BFB2BE315D790DC2E23E96619D92360FEB5C`
- Scientific effect: voice-conditioned waveform generation replacing the frozen target span while conditioning on a distinct deterministic speaker reference
- Human choice: `APPROVE_A` or `REJECT_AND_STOP`

Implementation bindings are complete for all five proposed bundles. No final executable configuration is emitted; after human approval, the bundle must be materialized into the execution config and independently revalidated.

W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
OUTCOME_GUIDED_SELECTION = NO

Codex approval text is intentionally not included as an executed action. Human approval remains required.
