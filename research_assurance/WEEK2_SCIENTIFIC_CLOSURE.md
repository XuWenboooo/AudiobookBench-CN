# Week 2 Scientific Closure

Date: 2026-09-06

Status: closure interpretation of frozen evidence. This document does not modify Week 2 inputs, outputs, hashes, original preregistrations, or Day 13.

## Primary question

Does the frozen Week 1 temporal speaker-consistency localization signal retain comparable performance under same-text, voice-conditioned, whole-source-utterance TTS replacement with natural synthetic duration?

## Design rationale and frozen population

The A2 manipulation was designed to control the major Week 1 lexical and phonetic-realization confound: it uses the exact source text with a voice-conditioned replacement of the complete source utterance. The frozen CosyVoice2-0.5B A2 population contains 23 realized cases across 12 speakers: 11 train, 6 validation, and 6 test. There was no case replacement and no A2-specific detector tuning.

## Frozen primary evidence

The primary scientific evidence is the Day 10 frozen A2 dataset together with the Day 11 frozen evaluation of Week 1 detector definitions and thresholds. For example, B1b/S2 on the original full-GT test population had AUROC `0.5215332008687215` and case-level AUROC CI `[0.4324439189701658, 0.6055668227537886]`.

The bounded conclusion is that the strong Week 1 localization signal did not retain comparable transfer under the tested same-text, voice-conditioned A2 condition. This is not a statement that TTS is undetectable, that B1 is useless, that the A2 implementation is necessarily incorrect, or that generic deepfake detection has failed.

## Frozen secondary evidence

Day 12 P1 compared target-real to synthetic-core ECAPA similarity with B1b case-level AUROC and AUPRC at co-primary S1 and S2. All four case-bootstrap intervals include zero. The frozen interpretation is that these analyses do not show a consistent monotonic relationship between this global ECAPA similarity quantity and B1b localization performance. The Day 11 degradation cannot currently be attributed to that simple mechanism. This is correlational evidence only and does not establish causation.

## Diagnostics and non-headline evidence

D2 reference-to-synthetic cosine, T19 silence-distribution reporting, generation QA, runtime behavior, provenance, and checkpoint evidence remain diagnostic or engineering context. They must not be promoted into primary scientific claims or used to select cases, methods, or interpretations.

## Limitations

- 23 total cases and 6 test cases;
- one tested generator;
- constructed long-form material;
- mono 16 kHz standardized condition;
- AISHELL-3 training independence is UNKNOWN; and
- similarity associations do not identify causal speaker mechanisms.

## Claim boundary

Week 2 does not support universal TTS detection, deepfake detection, adaptive robustness, native-audiobook generalization, speaker causality, unseen-generator generalization, or deployment readiness. Its bounded result concerns the named frozen baseline, tested immutable checkpoint, and constructed protocol.

## Original Day 13 limitation

Original Day 13 remains **FORMALLY UNRESOLVABLE UNDER ORIGINAL PREREGISTRATION** and its gate remains HOLD. Its Scenario B/D predicates required decision definitions that were only partially operationalized; those definitions must not be supplied after Day 11/Day 12 results were observed. This is a preregistration and experiment-design limitation, not evidence for or against any scenario, and it does not invalidate the frozen Week 2 primary or secondary results.

## Closure statement

Week 2 is **SCIENTIFICALLY COMPLETE** despite original Day 13 being formally unresolvable: a clean, frozen, outcome-blind transfer stress test was completed with its primary and secondary results preserved and bounded. Any subsequent zone or generator work belongs to a newly prospective study, not to a retroactive repair of Week 2.
