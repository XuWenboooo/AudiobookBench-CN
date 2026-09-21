# W7 P4 final human decision table v1

| Decision | Family | Candidate | Implementation | Key scientific parameters | Provenance | Human choice |
|---|---|---|---|---|---|---|
| M1 | `conventional_tts_replacement` | A | `VITS official single-speaker TTS` | `VITS_LJS_CANONICAL_V1` | 2e561ba58618d021b5b8323d3765880f7e0ecfdb | APPROVE_A / REJECT_AND_STOP |
| M2 | `cross_speaker_boundary_control` | A | `AudiobookBench deterministic waveform control adapter` | `CROSS_SPEAKER_BOUNDARY_CANONICAL_V1` | 1955c8e4637c9cd00625809fda0adfa1d8f0f28b | APPROVE_A / REJECT_AND_STOP |
| M3 | `neural_speech_editing_infilling` | A | `VoiceCraft official neural codec language model` | `VOICECRAFT_GIGA830M_CANONICAL_V1` | f0a7a971363905883a21c466a3aa4ea2d4c0b690 | APPROVE_A / REJECT_AND_STOP |
| M4 | `same_speaker_splice_crossfade_control` | A | `AudiobookBench deterministic waveform control adapter` | `SAME_SPEAKER_SPLICE_CROSSFADE_CANONICAL_V1` | 1955c8e4637c9cd00625809fda0adfa1d8f0f28b | APPROVE_A / REJECT_AND_STOP |
| M5 | `voice_conditioned_tts_vc_replacement` | A | `YourTTS official zero-shot TTS/voice-conversion implementation` | `YOURTTS_CANONICAL_V1` | 23904e6b7158d42cacf2a94dba0791ef69f1e2a9; c7cca4135db0c108a30ba8fd6a437fb63a5ecc12 | APPROVE_A / REJECT_AND_STOP |

All five rows are complete Candidate A bundles. Human choice is intentionally blank beyond the allowed action vocabulary; Codex has not approved any candidate.
