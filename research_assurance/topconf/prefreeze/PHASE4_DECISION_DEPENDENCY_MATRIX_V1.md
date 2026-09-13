# Phase 4 Decision Dependency Matrix v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

This matrix identifies what can be prepared now and what must wait for Phase3R
and human reconciliation. “Yes” means a candidate can be documented now, not
that it is authorized or frozen.

| Decision | Can freeze before Phase3R? | Depends on Phase3R field | Current candidate | Alternative | Risk if frozen too early | Required evidence |
|---|---|---|---|---|---|---|
| Core baselines | **NO** | Reproduction availability, output contracts, licenses, checkpoint identity | BAM/CFPRF/SAL plus internal candidates are source-level candidates | Reduce to verified paradigms or add a compatible independent paradigm | Missing/unequal paradigms or forced output conversions | Committed reproduction and source-level provenance review |
| External distributions | **NO** | Dataset/local-GT materialization and external reproduction status | PartialSpoof v1.2, PartialEdit v1.1 and additional OOD candidates | Use a smaller rights-cleared set | Distribution/rights mismatch or leakage | Dataset identity, version, rights, parser/hash verification |
| Whether-A | **CANDIDATE ONLY** | Final localizer output semantics and calibration rule | One predeclared mean/max/top-k choice selected by formal criteria | Non-primary native aggregation | Post-hoc pooling and calibration drift | Formal review, synthetic examples, Level-1 calibration rule |
| Whether-B | **NO** | Frozen checkpoint and independent compatibility | Codecfake W2V2+AASIST; AASIST; SSL detector conditional shortlist | State limitation if no candidate passes | False causal decoupling claim or opaque detector | Checkpoint hash, architecture/training-data/license audit |
| Primary Where metric | **NO** | Common native temporal resolution/output | LD@DR95 over a verified common Where score | Fixed-threshold sample-conditional alternative | Forced mapping or incomparable scales | Contract matrix, metric review, compatible GT |
| LD@DR95 | **CANDIDATE ONLY** | Primary detection-retention option and common Where score | Higher-is-better retention with explicit empty-set `NOT_ESTIMABLE` | Correct-after-correct or fixed-FPR constraint | Undefined or direction-mixed estimand | Formal review and predeclared condition grid |
| Sample size | **CANDIDATE BANDS ONLY** | Final model count, mechanism count, compute and failure budget | Low 300/100; target 400/120; stretch 500/150+ | Recompute synthetic sensitivity grid | Treating planning band as power guarantee | Synthetic-only simulation plus resource and attrition plan |
| Mechanisms | **YES AS TAXONOMY; NO AS FINAL SET** | Availability and paired quality for selected generators | Splice, crossfade, TTS/voice-conditioned, neural edit, codec controls | Multi-region secondary arm | Confounding mechanism with boundary/codec artifacts | Paired counterfactual feasibility and QC plan |
| Transformations | **YES AS SMALL CANDIDATE MATRIX** | Final deployment and quality constraints | Codec, resampling, noise, reverb, VoIP plus secondary controls | Fewer orthogonal cells | Combinatorial search and multiple-testing drift | Fixed matrix, parameter bounds, quality gates |
| Bootstrap | **YES AS STATISTICAL CANDIDATE; NO FINAL N** | Final statistical unit and missingness policy | Paired-source plus cluster sensitivity | Hierarchical speaker→case primary if justified | Underestimated uncertainty from speaker dependence | Synthetic coverage/width simulation and protocol review |
| Thresholds | **NO** | Model outputs and authorized calibration split | Official/Level-1/fixed-FPR rule | Non-primary threshold-free metrics | Test-set optimization and leakage | Frozen calibration manifest and audit log |
| GPU environment | **NO for full reproduction** | CUDA-enabled torch, external dependencies, checkpoint loads | CPU tooling ready; GPU hardware exists but current torch is CPU-only | Separate pinned WSL/Linux environment | Partial or irreproducible runs | Load-only smoke test and peak-resource logs |

## Current stop interpretation

The matrix supports preparation and human reconciliation only. It does not
create `RQ1_EXECUTION_AUTHORIZATION`, `PHASE4_FINAL_FREEZE`, or any equivalent
record. Any row classified `NO` or `CANDIDATE ONLY` remains non-authorizing.
