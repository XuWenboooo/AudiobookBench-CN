# THREAT_MODEL_v0.md — Day 1 Threat Model

Project: AudiobookBench-CN  
Primary target: Liu Zheli / AI Security / Forensics  
Secondary target: Qin Yong / Temporal Responsible Evaluation of TTS  
Status: v0 research framing. Not yet validated by experiments.

## 1. Research Motivation

Long-form generative speech creates security risks that are not well captured by ordinary utterance-level quality metrics or global fake/real classification. A long audiobook-like recording may be mostly benign while only a short region is synthetically replaced, generator-switched, voice-converted, spliced, or otherwise manipulated. A global classifier may say the entire sample is fake or real, but this does not answer the security-forensics question: **where did the abnormal segment occur, and which temporal evidence supports that decision?**

The Liu Zheli-priority framing is therefore:

> Given long-form generative speech, detect localized manipulation, localize suspicious temporal regions, estimate segment responsibility, and evaluate whether the method generalizes under unseen generators, unseen attacks, channel shifts, and adaptive evasion.

The Qin Yong-secondary framing is:

> The temporal signals used for security must themselves be evaluated responsibly: speaker/prosody metrics should be checked against natural speech controls, multiple evaluators, human judgment where feasible, and uncertainty/reject behavior.

## 2. Security Problem

Input:

```text
Long-form speech sample x(t)
```

Possible status:

```text
clean
manipulated with one or more localized suspicious intervals
```

Desired outputs:

```text
global manipulation score
segment-level anomaly score A(t)
localized suspicious interval(s)
optional segment responsibility score R(t)
uncertainty / reject flag
```

The project must not stop at global classification. The minimum security upgrade is:

```text
Detection → Localization
```

The stronger Week 6 goal is:

```text
Detection → Localization → Responsibility / Forensics
```

## 3. Attacker Capability

### 3.1 Initial Attacker — Week 1 to Week 4

The initial attacker can:

- replace a local segment of a long-form sample;
- switch from one TTS generator to another;
- replace the speaker or use voice conversion;
- insert a synthetic segment;
- splice two audio sources;
- apply codec, noise, resampling, or volume changes.

The initial attacker cannot:

- modify detector internals;
- directly access hidden test data;
- directly optimize through the evaluator;
- know all validation/test split details.

### 3.2 Adaptive Attacker — Reserved for Week 5

The adaptive attacker may know that the defender uses temporal speaker/prosody signals. The attacker can attempt to evade by:

- selecting replacement segments with similar speaker representation;
- selecting replacement segments with similar F0 / energy / speech-rate statistics;
- smoothing splice boundaries;
- applying feature-aware candidate search;
- minimizing a known anomaly score over candidate fake segments.

The adaptive setting must not be claimed until actually implemented and tested.

## 4. Defender Knowledge and Goal

The defender knows:

- the general threat model;
- the training generator set in known-generator experiments;
- the available clean/manipulated training data;
- the segment-level labels for supervised training/evaluation.

The defender may not know:

- the unseen test generator;
- the unseen attack strategy;
- the exact manipulated interval in test samples;
- whether channel conditions changed.

The defender aims to output:

1. **Global detection**: whether the long-form sample is manipulated.
2. **Segment localization**: where suspicious intervals occur.
3. **Responsibility evidence**: which segment contributes most to abnormal temporal behavior.
4. **Uncertainty/reject flag**: when evaluator disagreement or OOD conditions make confident claims unsafe.

## 5. Manipulation Types v0

Minimum v0 manipulation set:

1. **Localized TTS Segment Replacement**
   - Replace a time interval with generated audio from a different TTS source.

2. **Speaker / Voice Replacement**
   - Replace a region with audio from another speaker or voice-converted speech.

3. **Generator Switching**
   - Keep content similar but switch the generation system for a local region.

4. **Synthetic Splice / Insertion**
   - Insert or splice synthetic audio into an otherwise clean long-form sample.

Future extensions:

- boundary-smoothed splice;
- pitch/energy-matched replacement;
- duration-matched replacement;
- adversarial candidate-selection attack.

## 6. Evaluation Protocol

### 6.1 Clean / Manipulated Pairing

Every manipulated sample should have a paired clean source:

```text
sample_001_clean.wav
sample_001_attack.wav
```

The pair must share the same base audio except for the attack interval whenever possible.

### 6.2 Required Attack Metadata

Each manipulated sample must record:

```text
sample_id
source_audio_path
manipulated_audio_path
attack_type
attack_start
attack_end
source_generator
attack_generator
source_speaker
replacement_speaker
segment_length
channel_condition
split
```

### 6.3 Segment-Level Labels

For each segment `[segment_start, segment_end)`:

```text
label = 1 if segment overlaps [attack_start, attack_end)
label = 0 otherwise
```

### 6.4 Known-Generator Setting

Train and test generators may overlap:

```text
Train: Generator A + B
Test : Generator A + B
```

This is only a baseline and must not be used to claim open-world robustness.

### 6.5 Unseen-Generator Setting

Leave-one-generator-out:

```text
Train: Generator A + B
Test : Generator C
```

This is a primary Liu Zheli-relevant setting because it tests open-world generalization.

### 6.6 Cross-Attack Setting

Train on one manipulation type and test on another:

```text
Train: TTS segment replacement
Test : VC replacement / splice / generator switching
```

### 6.7 Channel-Shift Setting

Test robustness under:

- MP3 / AAC or other codec changes;
- additive noise;
- reverberation;
- resampling;
- volume changes.

## 7. Metrics

### 7.1 Global Detection

- AUROC
- AUPRC
- F1
- false positive rate
- false negative rate

### 7.2 Segment Localization

- segment-level AUROC
- segment-level AUPRC
- localization F1
- temporal IoU
- false alarm duration
- missed attack duration

### 7.3 Forensics / Responsibility

- segment responsibility ranking
- top-k localization hit
- counterfactual removal effect
- responsibility concentration inside ground-truth attack interval

### 7.4 Open-world Robustness

Report degradation from IID to OOD:

```text
Performance_IID → Performance_unseen_generator
Performance_IID → Performance_unseen_attack
Performance_clean_channel → Performance_channel_shift
```

### 7.5 Evaluator Validity — Qin Yong Secondary Layer

- multi-evaluator agreement
- natural-speech control gap
- human-alignment check
- evaluator disagreement rate
- uncertainty / reject rate
- calibration error if probabilities are produced

## 8. Temporal Signals

Initial signals:

- speaker representation distance trajectory;
- energy trajectory;
- zero-crossing / simple acoustic trajectory;
- F0 trajectory after a real F0 extractor is added;
- pause ratio after VAD/silence estimation is added;
- speech rate after transcript/text alignment or reliable proxy is added.

Current code status:

- energy and ZCR are implemented as basic sanity features;
- F0, pause ratio, voiced ratio, and speech rate are placeholders;
- speaker embedding backend is not configured.

Therefore, Week 1 claims must be limited to pipeline readiness and basic temporal-signal sanity unless real features and data are added.

## 9. Risks and Confounds

1. **Speaker shortcut**: detector may learn speaker ID rather than manipulation.
2. **Text shortcut**: detector may learn repeated text or chapter identity.
3. **Generator shortcut**: detector may simply recognize generator identity rather than local manipulation.
4. **Channel artifact**: replacement audio may have different codec, noise floor, or sample rate.
5. **Splice boundary artifact**: abrupt clicks or discontinuities may make localization trivial.
6. **VAD error**: poor VAD may create false pause/prosody abnormalities.
7. **Segmentation error**: attack intervals may not align with segment windows.
8. **Phonetic-content artifact**: speaker/prosody metrics can vary due to content rather than manipulation.
9. **Single-evaluator artifact**: one speaker embedding model may produce false drift.
10. **Overclaiming identity drift**: speaker representation drift is not automatically human-perceived identity drift.
11. **Adaptive weakness**: a non-adaptive detector may fail once attacker matches the monitored features.

## 10. What Not to Claim Yet

Do not claim:

- real speaker identity drift;
- human-perceived abnormality;
- universal unseen-generator robustness;
- robustness to adaptive attacks;
- causal attribution;
- publication-level benchmark completeness;
- that F0/prosody metrics are valid before real extraction and human/evaluator checks;
- that legacy simulation results validate the new project.

## 11. Day 2 Implementation Plan

Day 2 should stay narrow and implement only the minimum path toward a real Week 1 baseline.

Recommended files to create or modify:

```text
pyproject.toml or pytest config
src/audiobookbench/utils/manifest.py
src/audiobookbench/preprocessing/slicing.py
src/audiobookbench/security/dataset.py
src/audiobookbench/features/extract.py
experiments/security_track/exp01_week1_baseline/run.py
tests/test_schema.py
tests/test_slicing.py
tests/test_week1_baseline.py
```

Day 2 priorities:

1. Make tests runnable with `python -m pytest` from repo root.
2. Align manifest schema with `DATASET_CARD.md`.
3. Add real audio slicing helpers.
4. Add a controlled manipulation dataset builder.
5. Extend baseline to output:

```text
results/security/week1/metrics.json
results/security/week1/segment_scores.csv
results/security/week1/manifest_preview.csv
```

6. Add tests for attack timestamp integrity and segment-label correctness.

Day 2 should not add:

- adaptive attacks;
- attribution / responsibility;
- large speaker models;
- large-scale experiments;
- fake data to make results look good.

## 12. Day 1 Status

Day 1 threat model v0 is complete as a research framing document. It is not an experimental result and should be revised after real data and the first manipulation baseline are implemented.
