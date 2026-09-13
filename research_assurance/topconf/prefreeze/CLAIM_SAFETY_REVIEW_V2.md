# Candidate Claim Safety Review v2

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Search date: **2026-09-13**

## Classification

| Candidate claim | Classification | Evidence boundary | Safe pre-freeze wording | Forbidden wording |
|---|---|---|---|---|
| Detection--Localization Robustness Gap | **NO_DIRECT_EQUIVALENT_FOUND** | Primary sources reviewed separately study partial localization, boundary reliance, OOD/cross-dataset behavior, or detection robustness. None reviewed uses the exact retained-detection-constrained paired estimand across paradigms/distributions. | “No directly equivalent formulation was identified in the primary sources reviewed as of 2026-09-13.” | first, first-ever, unprecedented, no prior work |
| Detection-preserving black-box localization suppression | **INSUFFICIENT_EVIDENCE** | Generic black-box/transfer attacks target utterance detectors; localization papers do not establish the preservation/degradation conjunction. | “We propose to evaluate a bounded black-box objective that preserves a predeclared detection criterion while testing temporal localization.” | first, universally effective, practical attack proven |
| Paired mechanism-controlled robustness study | **PARTIAL_OVERLAP** | Paired source design is common in editing/data papers, while robustness studies often compare datasets or transformations. The exact mechanism-controlled pairing is not established as a field-wide novelty. | “A paired mechanism-controlled design is a methodological choice intended to reduce confounding.” | novel design, unprecedented control |
| Cross-paradigm Whether-vs-Where measurement | **NO_DIRECT_EQUIVALENT_FOUND** | Reviewed sources report utterance and local outputs, but do not define a common paired retention curve with an independent Whether-B arm as the central estimand. | “The protocol makes Whether and Where separable reporting axes.” | first unified framework |
| Localization reliability monitor / abstention | **INSUFFICIENT_EVIDENCE** | No direct equivalence was verified in the partial speech sources reviewed; general selective prediction is a broad adjacent area and is not a direct precedent audit. | “Reliability monitoring and abstention are candidate mitigations for later evaluation.” | novel reliability monitor, solved uncertainty |

## Explicit non-novel components

The following are useful design choices or deployment regimes but are not
novelty claims by themselves: partial deepfake localization; Mandarin/Chinese
partial spoof; long-form speech; boundary-aware or multi-scale modeling; SSL
backbones; modern TTS; neural editing; generator OOD; codec robustness; generic
black-box attack; generic robustness testing; event/proposal metrics; paired
source sampling; and abstention as a generic concept.

## Claim discipline

1. Every future claim must carry a source, checked date, and scope boundary.
2. “No directly equivalent formulation was identified” describes this search,
   not the entire literature.
3. New papers appearing after 2026-09-13 or inaccessible sources may change the
   classification; an update must be versioned and remains non-confirmatory.
4. No historical pilot, Phase 3/3R result, or synthetic simulation output may
   be used to upgrade a novelty classification.
