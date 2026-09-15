# Phase4.9 new Pool-A selection record v1

Status: **SELECTED_PRE_OUTCOME**

Selected corpus: **AliMeeting SLR119**  
Pool ID: SOURCE_POOL_A_ALIMEETING_SLR119  
Selection snapshot SHA-256: C749F4A8BAA9B1EF5BC70D6D028E58B825FADFA30E6657B1DAE5AA38CECC4C2E  
Pre-selection HEAD: 110e2b91c04625898b955c0d0dfcfccfe04515cb

## Selection was frozen before V3

The selection is based only on official corpus identity, license, archive
integrity, audio headers, TextGrid interval bounds, transcript presence, and
speaker/meeting metadata. It was made before any V3 population, segment
materialization, model inference, metric calculation, or scientific outcome.

The eligible inventory is 1,721 intervals from 76 speakers. The fixed
metadata-only rule selected the 60 highest-count speakers, 200 primary
intervals by speaker-block round-robin, and 20 unused reserve intervals in
speaker/meeting/interval order. The top 60 contain 1,679 eligible intervals;
the least represented selected speaker has six.

## Why this corpus

AliMeeting is a distinct official OpenSLR resource (SLR119), provided by
Alibaba Group under CC BY-SA 4.0. The public Test and Eval resources provide
near-field speaker recordings and matching TextGrids. Deterministic extraction
of a TextGrid interval into a PCM16 WAV preserves the parent recording hash,
meeting, speaker, and exact frame offsets, and is compatible with the
derivative-use terms subject to attribution/share-alike compliance.

MAGICDATA SLR68 was audited but rejected before selection because its official
usage instruction forbids modification, format conversion, and secondary
development. WenetSpeech was not selected because speaker-level capacity and
reproducible local acquisition were not established. No candidate was selected
from detector scores, quality scores, difficulty, or outcomes.

## Commit boundary

This record, the candidate matrix, project-entry proof, source-pool proof, and
AISHELL-3 retirement record are committed as the **selection commit**. The V3
population creation commit must be a strict descendant of that commit. No V3
artifact exists at the selection boundary.

## Firewall

MODEL_INFERENCE_RUNS = 0  
SCIENTIFIC_OUTCOMES_ACCESSED = NO  
RQ2_ATTACK_INVOKED = NO  
RQ3_MITIGATION_INVOKED = NO  
RESULT_BASED_SELECTION = NO

