# Phase 4.9 historical-universe relevance matrix v1

This matrix is an independent, read-only-first audit artifact. It records whether each historical exclusion universe is directly relevant to the newly selected Pool A (AliMeeting SLR119) and Pool B (AISHELL-1 SLR33) population. A zero direct match is not treated as a freshness pass when the corresponding universe is incomplete.

## Evidence basis

- Audit base: `110e2b91c04625898b955c0d0dfcfccfe04515cb` (`origin/topconf-dl-robustness`).
- Current Phase 4.9 evidence was inspected read-only from the separate local worktree `AudiobookBench-CN-topconf-dl-robustness`; its unpushed commits were not copied into this audit branch.
- Pool A entry proof: `research_assurance/topconf/LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json`.
- Pool B entry proof: `research_assurance/topconf/AISHELL1_PROJECT_ENTRY_PROOF_V1.json`.
- Historical stage index: `research_assurance/topconf/HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json`.
- Case/source/speaker/lineage universes: `HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json`, `HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json`, `HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json`, and `HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json`.
- Direct-match method: compare Pool A/B corpus, source IDs, speaker IDs, session IDs, parent/source hashes, and lineage IDs against every materialized historical record; separately inspect alias/history searches. Direct-match count was zero for all explicitly grouped records, but unresolved projections remain in Week 5 and Phase 3-family stages.

## Matrix

| Historical universe / stage | Historical identity in the evidence | AliMeeting relevance | AISHELL-1 relevance | Direct comparison result | Completeness / audit consequence |
|---|---|---|---|---|---|
| Week 1 pilot | AISHELL-3; 217 cases, 200 sources, 5 speakers | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | 0 direct Pool A/B source, speaker, session, hash, and lineage matches | Case/source/lineage `PARTIAL`; identified corpus does not match, but incomplete exclusion is not a freshness PASS by itself. |
| Week 2 pilot | AISHELL-3; 23 cases, 35 sources, 12 speakers | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | 0 direct matches | Case `COMPLETE`; source/lineage `PARTIAL`; source/lineage incompleteness remains a conservative block. |
| Week 3 pilot | AISHELL-3; 23 cases, 23 sources, 12 speakers | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | 0 direct matches | Case `COMPLETE`; source/lineage `PARTIAL`; no freshness PASS from identity mismatch alone. |
| Week 4 pilot | AISHELL-3; 48 cases, 96 sources, 48 speakers | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | 0 direct matches | Case/source/lineage `PARTIAL`; incomplete universe remains unresolved. |
| Week 5 qualification | AISHELL-3 is named, but qualification records and source/lineage projections are incomplete; 92 cases, 12 speakers, unresolved source count | `POTENTIALLY_RELEVANT_UNRESOLVED_PROJECTION` for the unresolved portion; identified AISHELL-3 rows are corpus-irrelevant | `POTENTIALLY_RELEVANT_UNRESOLVED_PROJECTION` for the unresolved portion; identified AISHELL-3 rows are corpus-irrelevant | 0 direct matches in the keyed records; unresolved projections prevent a complete comparison | Case `PARTIAL`; source/lineage `UNKNOWN`; do not convert the identified AISHELL-3 label into a complete exclusion proof. |
| Phase 3 / 3R / 3S / 3U / 3V | No complete dataset/source identity; stage index records no known IDs and marks case/source/lineage `UNKNOWN` | `UNKNOWN_UNRESOLVED_HISTORY` | `UNKNOWN_UNRESOLVED_HISTORY` | No reliable direct comparison possible | `UNKNOWN` in the historical universe. This is the clearest unresolved historical relevance, independent of the zero keyed-match result. |
| Phase3T PartialEdit v1.1 E1 | Explicitly named `PartialEdit_v1.1_E1`; 42,471 cases/sources, 109 speakers | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | `IRRELEVANT_BY_CORPUS_IDENTITY` for identified records | 0 direct Pool A/B matches | Case `COMPLETE`; source/lineage `PARTIAL`; E1 is explicitly excluded, but incomplete source/lineage records are not a complete freshness proof. |
| Whether-B capability smoke | Synthetic sinusoid; no real dataset IDs; explicit empty exclusion universe | `IRRELEVANT_BY_PROJECT_ENTRY_TIME_AND_EMPTY_UNIVERSE` | `IRRELEVANT_BY_PROJECT_ENTRY_TIME_AND_EMPTY_UNIVERSE` | 0; no real source identity exists to match | `COMPLETE_EXCLUSION_EMPTY`; no model or scientific outcome was used. |
| Metric development / threshold calibration / model selection / adapter debugging / manual inspection / pilot visualization / scientific selection | Stage index has no complete dataset/ID ledger for these selection-relevant activities | `UNKNOWN_UNRESOLVED_HISTORY` | `UNKNOWN_UNRESOLVED_HISTORY` | No reliable direct comparison possible from the available ledger | `UNKNOWN`; the frozen policy names these selection sets, so the absence of a complete ledger cannot be silently treated as irrelevant. |

## Interpretation

1. The explicit corpus labels and keyed identity comparisons show no direct Pool A/B overlap in the records that are actually keyed.
2. Week 5 and the Phase 3-family/selection-relevant stages remain relevant as unresolved history because the exclusion ledgers are `PARTIAL` or `UNKNOWN`; this is not a claim that overlap exists.
3. The Pool A and Pool B project-entry proofs provide a separate prospective boundary claim: both selected archives were acquired/materialized after the stated freeze boundary, with exact archive hashes and no prior project reference found by the recorded alias/history searches. The frozen design documents do not explicitly say that this prospective proof may replace incomplete historical universes. The matrix therefore does not authorize a PASS.
