# Phase 4.7 historical exclusion and freshness proof

**Date:** 2026-09-15
**Decision:** `FAIL` / `NO_GO`
**Scope:** historical data-use reconstruction and frozen-`V2` freshness only

## 1. Scope and freeze binding

This audit starts from topconf commit `45b95dd224f7172a41dccaa4663fd9c8256b62b7`.
It keeps the Phase 4.6 V2 population unchanged and does not select a replacement
population. No Level-2 or CFPRF/MultiReso/AASIST inference, scientific metric,
LD@DR95 estimate, or RQ1/RQ2/RQ3 outcome was accessed.

The frozen V2 population remains:

```text
population file: LEVEL2_RQ1_POPULATION_MANIFEST_V2.json
file SHA256: ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
internal manifest SHA256: FCFFEEC32F4CAB32DA53BFAD06C0BBBC6F1354AA87277DCE1B1A4EA8E6F90674
sources: 400; speakers: 120; cases: 1600; reserves: 40
population validation: PASS
file unchanged during reconstruction: YES
```

## 2. Historical coverage

The audit materializes `HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json` across Week1–5,
Phase3/3R/3S/3U/3V/3T, the Whether-B capability smoke, metric and threshold
development, model selection, debugging, manual inspection, visualization, and
scientific selection. It searches current files, deleted Git history, all refs in
the main and Week5 repositories, and the listed topconf worktrees. The method and
scope are recorded in `HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json`.

Observed identity coverage is intentionally typed rather than converted to
false zero-overlap claims:

| Stage | Observed cases | Observed sources | Observed speakers | Identity status |
|---|---:|---:|---:|---|
| Week1 | 217 | 200 | 5 | case/source/lineage partial |
| Week2 | 23 | 35 IDs | 12 | case complete; source/lineage partial |
| Week3 | 23 | 35 IDs | 12 | case complete; source/lineage partial |
| Week4 | 48 | 96 IDs | 48 | case/source/lineage partial |
| Week5 qualification | 92 unique IDs across six manifests | unknown | 12 | case partial; source/lineage unknown |
| Phase3/3R/3S/3U/3V | not materialized | unknown | unknown | unknown |
| Phase3T PartialEdit E1 | 42,471 | 42,471 path-derived records | 109 path-derived | case complete; source/lineage partial |
| Whether-B | 0 real records | 0 | 0 | complete empty exclusion |
| metric/threshold/model/debug/manual/visualization/selection | not materialized | unknown | unknown | unknown |

Unknown and partial dimensions remain evidence gaps. They are never interpreted
as proof of non-use.

## 3. V3 comparison result

`LEVEL2_FRESHNESS_MANIFEST_V3.json` was validated against the four separate
historical universes. The validator recomputes the comparisons from the records;
declared counts are not trusted without recomputation.

```text
case_id_overlap_count:              0
case_lineage_overlap_count:        20
source_overlap_count:               5
lineage_overlap_count:              5
speaker_overlap_count:              23
prohibited_speaker_overlap_count:   2
unknown_case_comparisons:         780
unknown_source_comparisons:       195
unknown_lineage_comparisons:      195
freshness_verdict:                FAIL
```

The five verified AISHELL-3 source/lineage overlaps are:

| Frozen source | Frozen speaker | Historical stage | Historical source | Audio SHA256 |
|---|---|---|---|---|
| `AISHELL3-SRC-0001` | `AISHELL3_SSB0005` | Week1 | `SSB00050001` | `BB61E8E29F25FA6AD9702EB42BE6FD81B82E7A55DF4066E6AFDE21DADAF8B927` |
| `AISHELL3-SRC-0036` | `AISHELL3_SSB1203` | Week4 | `SSB12030001` | `8B89A052DD76790E282EA045E23E5192DE0A94F9FC465F2C65375DB2D9575CB6` |
| `AISHELL3-SRC-0061` | `AISHELL3_SSB0005` | Week1 | `SSB00050007` | `F7C2E359847AF780EBFEA6D06A170D38AC5D4CD5E91B51B7CD98216A11D32BC0` |
| `AISHELL3-SRC-0121` | `AISHELL3_SSB0005` | Week1 | `SSB00050022` | `30BBFE43D675533FA5FA023920197E9CC176592D4DDAE45F55765B3C9AAF0E75` |
| `AISHELL3-SRC-0181` | `AISHELL3_SSB0005` | Week1 | `SSB00050027` | `781DA576104AB7E62E823E739C38DBADBB87BBD114C17A82FC85777BCE2A3E55` |

The V2 case IDs are new, but case-ID novelty does not defeat source/lineage
identity. The 5 source lineages expand to 20 V2 cases. The historical speaker
intersection contains 23 AISHELL-3 speaker keys; the two speakers with direct
source/lineage overlap, and therefore prohibited under the locked policy, are
`AISHELL3:SSB0005` and `AISHELL3:SSB1203`.

## 4. Corpus isolation

AISHELL-3 is `FAIL_PRIOR_USAGE_FOUND` because the five direct hashed overlaps
are in retained Week1/Week4 evidence. AISHELL-1 is
`PASS_POST_FREEZE_ACQUISITION`: the project-entry proof records no prior project
reference in the searched Git histories and records the post-freeze acquisition
evidence. This status does not repair the independent AISHELL-3 overlap.

## 5. Reproducible artifacts

The closure is represented by:

```text
HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json
HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json
HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json
HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json
HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json
HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json
AISHELL1_PROJECT_ENTRY_PROOF_V1.json
LEVEL2_FRESHNESS_MANIFEST_V3.json
```

The four historical universes are marked `PARTIAL` where identity is not
complete. The V3 validator therefore fails closed on both confirmed prohibited
overlap and unresolved historical comparisons.

## 6. Authorization conclusion

Phase 4.7 closes the reconstruction task with a reproducible `FAIL`. It does
not authorize Level-2 execution. `LEVEL2_RQ1_POPULATION_MANIFEST_V2.json` is
left byte-for-byte unchanged, no new population is selected, and no Level-2
inference namespace or outcome is created.
