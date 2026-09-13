# Phase 2 Infrastructure Readiness v1

Status: **CONDITIONAL PASS FOR PHASE 3 PLANNING / CONFIRMATORY EXECUTION NO**

## Readiness ledger

| Requirement | Status | Evidence |
|---|---|---|
| Unified prediction schema | READY | `src/audiobookbench/topconf/schemas.py` |
| Whether-A pooling interface | READY / NOT FROZEN | `evaluation/detection.py` |
| Whether-B adapter interface | READY / NO MODEL RUN | `models/base.py` |
| Frame/event/proposal/boundary metrics | READY for supported metrics | corresponding evaluation modules and synthetic tests |
| RangeEER | READY / REFERENCE FORMULA VALIDATED | `evaluation/range_eer.py` and synthetic reference tests; official implementation metadata recorded in Phase 2.5 closure |
| LD@DR95 formal review | REVIEWED CANDIDATE | `LD_DR95_FORMAL_REVIEW_V1.md`; preregistration decision pending |
| External dataset adapters | READY metadata-only | `DATASET_ADAPTERS_V1.md`, `datasets/base.py`; PartialSpoof v1.2 and PartialEdit v1.1 targeted |
| Baseline provenance | CORE CANDIDATES VERIFIED at source level | `EXTERNAL_BASELINE_MATRIX_V1.md`; no baseline executed |
| Synthetic edge-case tests | PASS | `tests/topconf/` |

## Integrity and blockers

No training, inference, scientific benchmark, bootstrap, attack, defense,
confirmatory-data access, or scientific outcome was performed. Phase 3 remains
conditional on local license/GT/hash verification, RangeEER reference
comparison, and preregistration decisions. Confirmatory execution remains
blocked by all unresolved `TBD_BEFORE_AUTHORIZATION` fields.

## Hash policy

SHA256 values for critical source/test files in this draft:

| Path | SHA256 |
|---|---|
| `src/audiobookbench/topconf/__init__.py` | `2DC2C10DDB222D74E0247E41125FF7529AAF8434057DAF223C2476AF88C1885D` |
| `src/audiobookbench/topconf/schemas.py` | `BCA6DF95F1812CC52990BF396C044C8FFA5FC08083B09647CD2E7180335D653E` |
| `src/audiobookbench/topconf/evaluation/detection.py` | `EDE04B19A004C9DE5EC5B1876CB3BF8D65504D746C73F2B68A453E6AE128A0AB` |
| `src/audiobookbench/topconf/evaluation/frame_localization.py` | `EA61EA2DD7DD6077136B088BBF75DAF6EA329705EF83BCEE88EA646E2582A342` |
| `src/audiobookbench/topconf/evaluation/event_localization.py` | `C29805D38402AF55016C339A9A540FA2588CE241698711BF5CD81DFE5BA8AE58` |
| `src/audiobookbench/topconf/evaluation/proposal_localization.py` | `787F206F9451D0CCBC79D7A1C2CDE6E112CFF7F1E3EEF4F1079855752EFAE583` |
| `src/audiobookbench/topconf/evaluation/boundary.py` | `BDB4798386BDE963EDF580FF2F1C8BA2E6CE93AF01375A8F844A905B4F19703F` |
| `src/audiobookbench/topconf/evaluation/range_eer.py` | `A99A8E6CBF869E5591AF9BBD1B33A245E02B9A7892A1E32363A07A4261C578FB` |
| `src/audiobookbench/topconf/evaluation/robustness.py` | `06B9604F820BCD429879CC6B4D2526966A3F6F3CE007C241AD20D7D891F1198B` |
| `src/audiobookbench/topconf/evaluation/gap_metrics.py` | `D030BB55123F0A30A0A1F44C2DA0E75785BCAB5E8BEA78087BFF9B7D7ADE9B1B` |
| `src/audiobookbench/topconf/evaluation/validation.py` | `2C79137A624CCABCF427B7DBE674E84FE3ECEEF2F40E7BB5C4D5ADAE022A0855` |
| `src/audiobookbench/topconf/datasets/base.py` | `DA4722AF9A5AF5D14F7F60C0FC5EA3642FA65AE9E01CBD79D8B79E6DCED69AF7` |
| `src/audiobookbench/topconf/models/base.py` | `B365C90E00E7462D3CCF4A05CFBC40C4D55128E6A23ADABDC6F22F616995D08B` |
| `tests/topconf/test_schema_validation.py` | `399FF5B3E9DAC1F8D3519D424875089DEA4F1BDBE21474E1EAFC164998973FC8` |
| `tests/topconf/test_detection_metrics.py` | `0983650044BBA19860A3BDA2FE1538A552E47DDBC863368EE43B110B581D1FE8` |
| `tests/topconf/test_localization_metrics.py` | `8F7A1451A5AE3A77153F587B6D9823EEC4D39F320C96CAF67237E61BE615C607` |
| `tests/topconf/test_gap_metrics.py` | `02D46EF37D2DAB56AB5F1D73EB62780D81FF0287E0BE2738F22C2E9CF195BE6E` |
| `tests/topconf/test_range_eer.py` | `C4E5B6E7ADBA8704C73B3882AFB5666C8DF57F9D4CD155F9718490188475713E` |
| `tests/topconf/test_reference_metrics.py` | `48F9B295F432AF85908CA8D26AFD252070705F7F7EBE273C9F27664FAA5C8EFE` |
