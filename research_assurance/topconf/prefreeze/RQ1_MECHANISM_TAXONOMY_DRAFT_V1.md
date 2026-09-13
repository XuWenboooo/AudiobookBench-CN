# RQ1 Manipulation-Mechanism Taxonomy Draft v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

This taxonomy is a design aid. It does not select a mechanism from pilot or
Phase3R outcomes and does not authorize generation. Mechanisms should be
selected only after considering scientific identifiability, paired-control
feasibility, modern relevance, and resource reproducibility.

| Mechanism | Definition | Realism | Boundary behavior | Core behavior | Paired-counterfactual feasibility | Semantic control | Speaker control | Implementation availability | Known confounds | Literature precedent | Candidate role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Classical cut/paste splice | Replace a source interval with separately rendered or sourced speech and concatenate | Low to medium; common baseline threat | Often exposes discontinuity unless aligned | Region may be acoustically consistent internally but not with context | High: same source/target/reference can be reused | High with transcript-driven replacement | High if source-conditioned or same-speaker material | High; standard audio tooling | Boundary artifact, gain, duration, phase, resampling | PartialSpoof, HAD, ADD partial-fake line | Candidate baseline/control |
| Crossfade splice | Cut/paste with predefined overlap and fade-in/out window | Medium | Boundary artifact reduced but fade may become a cue | Same as splice plus mixing envelope | High; fade parameters can be fixed across mechanisms | High | High | High | Fade length, energy normalization, phase, unintended smearing | HAD/partial-fake practice and speech editing studies | Candidate controlled comparator |
| TTS replacement | Generate target text with a TTS system and replace the target interval | Medium to high depending on conditioning | May show prosodic/timbre mismatch | Synthetic segment artifacts can dominate | Medium to high if target text/position are shared | High | Medium unless speaker-conditioned | High to medium | Generator signature, text length, duration, speaker mismatch | PartialSpoof/HAD and partial-fake literature | Candidate mechanism |
| Voice-conditioned TTS replacement | TTS/VC generation conditioned on a reference from the source speaker | High for speaker-preserving threat model | Boundary and prosodic continuity depend on conditioner | Core artifacts may be speaker-conditioned and subtle | High when reference policy is fixed before seeing quality | High | High in principle | Medium; checkpoint and licensing vary | Reference selection, leakage, speaker similarity, content length | HAD, LlamaPartialSpoof, PartialEdit-related generation | Candidate mechanism |
| Neural speech editing / infilling | Regenerate a masked target span conditioned on surrounding audio and target text | High and modern | Designed to reduce boundary discontinuity | Tests content-edited region under contextual conditioning | High if same source, text, position, and edit request are paired | High | High | Medium; model and alignment dependencies | Codec path, post-processing, alignment, changed context outside target | SINE, PartialEdit, VoiceCraft, VoiceNoNG | Candidate primary modern arm |
| Codec-consistent editing | Editing and retained audio share the same declared neural-codec path or compatible post-processing | High for codec-native deployment | Boundary may be codec-consistent | Core may contain codec artifacts shared by real/resynth conditions | Medium; requires explicit clean/resynth control | High | High | Medium to low | Resynthesis of comparator, codec identity, bitrate, hidden post-processing | PartialEdit, SINE, VoiceNoNG | Candidate nested condition |
| Codec-mismatched editing | Edited region and comparator/retained audio traverse intentionally different codec paths | Deployment-relevant but can be artificial | Codec discontinuity can dominate boundary | Core confounded by codec mismatch if not controlled | High as a stress control, not necessarily primary | High | High | Medium | Codec mismatch, sample-rate conversion, bandwidth and phase | PartialEdit codec discussion and robustness literature | Candidate diagnostic/stress arm |
| Multiple edited regions | Two or more non-overlapping edited spans with count and positions declared in advance | High for disinformation/content manipulation | Multiple boundary opportunities and interaction | Tests distributed core evidence and aggregation | Medium to high; paired placements can be identical | High | High | Medium | Region count, prevalence, overlap, duration, aggregation bias | MIST, SpeechSplice, PartialSpoof multi-region variants | Candidate secondary arm |

## Candidate selection guardrails

- Keep a small set with orthogonal mechanisms rather than a search over
  generators, prompts, and post-processing.
- For every retained mechanism, predeclare source, target text, target position,
  duration policy, reference policy, sample rate, codec path, and quality gate.
- Treat splice/crossfade primarily as controls for boundary dependence; do not
  infer that they represent all real-world edits.
- Treat codec-consistent/mismatched as orthogonal recording/transformation
  factors where possible, not as interchangeable “mechanisms.”
- Any failed generation or quality gate remains in the failure ledger and is not
  silently replaced.
