# Phase4.9 fresh Pool-A candidate matrix v1

Review date: **2026-09-15**  
Protocol: P4-RQ1-DESIGN-20260914-01  
Decision boundary: **before V3 materialization and before any Level-2 model run**

| Candidate | Official source | License / derivative compatibility | Mandarin / capacity evidence | Speaker / lineage metadata | Prior project usage | Download reproducibility | Decision |
|---|---|---|---|---|---|---|---|
| **AliMeeting SLR119** | [OpenSLR SLR119](https://www.openslr.org/119/) | CC BY-SA 4.0; adaptation is permitted with attribution/share-alike compliance | 118.75 h; 15–30 min meetings; Test+Eval acquired; 1,721 eligible TextGrid intervals / 76 eligible speakers; 1,679 intervals across top 60 | Near-field speaker WAVs, meeting IDs, TextGrids, exact interval offsets; parent recording lineage retained | NONE_FOUND in pre-selection project/repository/ref/worktree scan | Test: 9,555,497,666 bytes, SHA-256 42407625B774A44FE34F2F25CA99116F090BEC901F5AB81196B89F683A8B7BFA; Eval: 3,673,718,355 bytes, SHA-256 DC47343B2474B5EBCF458927E878155F6DDEB59C85E685B3645C32A1F9578D92 | **SELECTED** |
| MAGICDATA SLR68 | [OpenSLR SLR68](https://www.openslr.org/68/) | CC BY-NC-ND 4.0; official usage instruction forbids modification, format conversion, and secondary development | Metadata reports 1,080 speakers / 755 h; local dev+test audit: 1,279 eligible files / 62 speakers | Metadata present; corpus provider distinct | NONE_FOUND in pre-selection scan | Dev/test obtained and hashed; audit artifacts retained locally | **REJECTED_LICENSE** |
| WenetSpeech SLR121 | [OpenSLR SLR121](https://www.openslr.org/121/) | CC BY 4.0 is derivative-compatible, but official acquisition requires a form/password | 10,000+ h reported; speaker-level eligibility and exact capacity not established | Speaker identity/long-form segment metadata not established locally | NONE_FOUND in pre-selection scan | No local archive; password-gated acquisition | **DEFERRED_INSUFFICIENT_PROVENANCE/CAPACITY** |
| AISHELL-3 | [OpenSLR SLR93](https://www.openslr.org/93/) / local archive | Apache-2.0 metadata, but project historical use is verified | Local audit: 532 eligible files / 112 speakers | Historical lineage and prohibited speakers verified | FOUND | Local archive hash preserved | **RETIRED_HISTORICAL_CONTAMINATION** |
| AISHELL-1 | [OpenSLR SLR33](https://www.openslr.org/33/) | Apache License 2.0 | Local audit: 2,750 transcript-complete eligible files / 300 speakers | Retained frozen Pool B; separate official resource | Post-freeze acquisition proof already recorded | Full archive and resource hashes preserved | **RETAIN_POOL_B** |

## Selection rule

Only AliMeeting is selected for final Pool A. The selection is pre-outcome and
metadata-only:

1. use the acquired Test and Eval near-field recordings and matching TextGrid
   speaker tiers;
2. retain non-empty intervals in the inclusive 8–30 second, 16 kHz,
   mono, PCM16 filter;
3. rank speakers by eligible-interval count descending, then speaker ID
   ascending;
4. take the top 60 speakers;
5. select 200 primary intervals by speaker-block round-robin, then 20 unused
   reserve intervals by speaker/meeting/interval order.

The frozen selection snapshot is
C749F4A8BAA9B1EF5BC70D6D028E58B825FADFA30E6657B1DAE5AA38CECC4C2E.

No quality, difficulty, transcript content, detector score, model output, or
scientific outcome participates in this decision.

