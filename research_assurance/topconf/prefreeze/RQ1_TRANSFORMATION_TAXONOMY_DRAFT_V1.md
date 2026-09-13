# RQ1 Media-Transformation Taxonomy Draft v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

This is a candidate interpretable matrix, not a combinatorial search. Final
strengths, ordering, and inclusion require human review and a versioned
authorization. The matrix should remain small enough that every cell has a
provenance record and an independently checked quality gate.

| Transformation | Deployment relevance | Candidate parameter range (not frozen) | Existing robustness precedent | Quality risk | Semantic risk | Speaker risk | Compute cost | Candidate role |
|---|---|---|---|---|---|---|---|---|
| Codec compression | Streaming, storage, social-media export | MP3/AAC/Opus at a few declared rates; exact rates TBD | ASVspoof channel/codec tracks; Proteus | High at low rates | Medium if artifacts mask consonants | Low to medium | Low to medium | Primary candidate |
| Resampling | Upload/download and legacy pipelines | 8/16/24 kHz paths with explicit anti-aliasing; TBD | Common anti-spoofing preprocessing and dataset variance | Medium | Medium if aliasing | Low | Low | Primary candidate |
| Additive noise | Mobile, room, street and production environments | SNR bands with named noise sources; TBD | ADD and anti-spoofing augmentation literature | Medium to high | High at low SNR | Low | Low | Primary candidate |
| Reverberation | Rooms, halls, far-field capture | RT60/room families; TBD | ADD/noisy-reverberant robustness work | Medium | Medium | Low | Low to medium | Primary candidate |
| Dynamic-range compression | Broadcast, podcast, mobile post-processing | Ratio/attack/release bands; TBD | Proteus and common audio post-processing | Low to medium | Low | Low | Low | Secondary candidate |
| Bandwidth limitation | Telephony, narrowband devices | 3.4/7/8 kHz-style limits; exact filter TBD | ASVspoof and telephony robustness literature | Medium | Medium | Low | Low | Secondary candidate |
| Telephony / VoIP simulation | Calls, conferencing, social voice channels | G.711/Opus/packet-loss profile; TBD | Proteus explicitly includes VoIP simulation | Medium to high | Medium | Low | Medium | Primary candidate if reproducible |
| Gain | Microphone distance, normalization, playback level | Fixed dB bands with peak guard; TBD | Generic pipeline control | Low if clipped-free | Low | Low | Low | Control / nuisance factor |
| Channel filtering | Microphone, room, equalization, device response | Named low/high-pass or measured impulse family; TBD | Channel-variation robustness literature | Medium | Medium | Medium | Low | Secondary candidate |

## Matrix-size guardrail

The pre-freeze recommendation is a small orthogonal matrix: one or two
strengths per selected transformation, with a fixed order or one-step
application unless a chained condition is explicitly justified. Do not create a
search space such as `1000 transforms x 20 strengths x 50 codecs`. If a later
study needs breadth, it must be a separately authorized robustness study with
its own correction and budget.

## Quality gates to predeclare later

Every transformation must be checked for finite audio, duration/alignment
preservation, clipping, intelligibility, speaker identity, and the intended
parameter realization. A failed quality gate is an explicit terminal state, not
an exclusion.
