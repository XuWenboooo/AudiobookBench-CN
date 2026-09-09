# THREAT_MODEL.md

Status: draft template. Fill this after Day 1 audit.

## 1. Research Motivation

Long-form generative speech may contain localized synthetic manipulation that is not well captured by utterance-level scalar evaluation or global fake/real classification.

## 2. Security Problem

Given a long-form speech sample, detect whether a local segment has been synthetically manipulated, localize the suspicious region, and estimate which temporal segment is responsible for abnormal behavior.

## 3. Attacker Capability v0

Attacker can:

- replace local segment;
- switch TTS generator;
- switch speaker / apply voice conversion;
- insert or splice synthetic audio;
- apply codec, noise, resampling, or volume changes.

Attacker initially cannot:

- modify detector internals;
- access hidden test data;
- directly optimize through evaluator.

Adaptive attacker is reserved for Week 5.

## 4. Defender Output

- global manipulation score;
- segment-level anomaly score;
- localized suspicious interval;
- optional responsibility score;
- uncertainty / reject flag.

## 5. What Not To Claim Yet

- real speaker identity drift;
- human-perceived abnormality;
- universal unseen-generator robustness;
- adaptive robustness;
- causal attribution.
