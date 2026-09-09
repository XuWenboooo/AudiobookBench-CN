# Research Roadmap Rebaseline

Date: 2026-09-06

Status: forward-looking planning record. It does not alter frozen scientific artifacts, preregistrations, metrics, hash manifests, or claim gates.

## Program continuity

The high-level program remains **Trustworthy Temporal Analysis of Long-form Generative Speech**. Its security arc remains temporal forensic signal, stronger controlled manipulation, transfer/generalization, localization/traceback, attribution/responsibility, and then open-world or adaptive robustness. This rebaseline changes experimental sequencing, not the program.

| Stage | Scientific role | Status | Boundary |
| --- | --- | --- | --- |
| Week 1 | Signal discovery under controlled cross-speaker natural-speech splicing | CLOSED | A temporal speaker-consistency localization signal was observed; different-text/realization confounding remains. |
| Week 2 | Controlled transfer stress test under same-text, voice-conditioned, whole-utterance TTS replacement | SCIENTIFICALLY COMPLETE | A frozen outcome-blind transfer test was completed; it is not judged by whether it produced a successful TTS detector. |
| Original Day 13 | Original preregistered scenario decision tree | HOLD — FORMALLY UNRESOLVABLE UNDER ORIGINAL PREREGISTRATION | Partially operationalized B/D predicates must not be repaired after results. This does not invalidate Week 2. |
| Week 3 | New second-generator replication plus predefined mechanism decomposition | PROTOCOL REVIEW ONLY | It is a new study and cannot retrospectively classify original Day 13. |
| Week 4+ | Open-world, adaptive, attribution, and broader extensions | NOT ENTERED | No automatic progression. |

## Week 2 role

Week 2 asked whether the frozen Week 1 temporal speaker-consistency signal retained comparable performance under same-text, voice-conditioned, whole-source-utterance CosyVoice2-0.5B replacement with natural synthetic duration. Its primary evidence is the Day 10 frozen A2 dataset and Day 11 frozen detector evaluation. Day 12 is secondary mechanism evidence; D2, T19, generation QA, runtime, and provenance remain diagnostics rather than headline scientific claims.

Week 2 is scientifically complete because the planned, frozen, outcome-blind transfer test was completed with retained denominators and no A2-specific detector tuning. Its bounded conclusion is that the strong Week 1 signal did not directly retain comparable localization performance in the tested A2 condition. Day 12 did not show a consistent monotonic global ECAPA similarity explanation for that degradation. These facts do not imply that TTS is undetectable, that B1 is useless, or that generic deepfake detection is supported.

## Week 3 redesign

Week 3 is a forward-looking study with three objectives: (1) replicate the transfer stress test with a scientifically distinct, voice-conditioned second TTS generator; (2) estimate where residual localization signal occurs using predefined continuous quantities for strict synthetic core, blend/crossfade, and outside/clean-background zones; and (3) determine, within the new study's defined population and protocol, whether the transfer pattern is specific to one tested backend or is reproduced across two tested backends.

Week 3 must prefer continuous estimates such as `AUROC_full`, `AUROC_core`, `AUROC_blend_excluded`, `delta_boundary_core`, and `delta_full_core` over natural-language binary predicates. Any categorical decision rule must be frozen before Week 3 outputs or scores are observed.

## Case strategy recommendation

**Recommended strategy: STAGED_A_THEN_B.**

- **Stage A:** use the same frozen 23 source/reference pairs with the second generator to control source/reference composition. Any comparison against already-observed CosyVoice2 outcomes is explicitly **POST-HOC / EXPLORATORY** and cannot repair Day 13.
- **Stage B:** create a larger independent confirmatory population, freezing its sample size, split allocation, seed, and reference policy before output generation. Report Stages A and B separately unless a pooling rule is preregistered before either has new results.

This recommendation follows pairing efficiency and the existing 23-case, 6-test-case limitation, not expected detector outcomes.

## Second-generator eligibility

No generator is selected here. A candidate must support exact same-text synthesis and target-speaker conditioning; permit compatible frozen-style reference selection; have identifiable license, provenance, revision, and component hashes; allow detector leakage prevention; be practically executable; and be scientifically distinct from CosyVoice2. Selection may not use expected detectability or detector scores. AISHELL-3 training independence remains **UNKNOWN** unless official evidence establishes it.

## Persistent claim boundary and entry condition

Two tested generators would still not establish universal TTS detection, deepfake detection, adaptive robustness, native-audiobook generalization, speaker causality, unseen-generator generalization, or deployment readiness. Week 3 remains in protocol review until a prospective preregistration freezes its generator, populations, estimands, zone mapping, split policy, uncertainty procedure, multiple-primary handling, and claim boundary. This roadmap authorizes no experiment.
