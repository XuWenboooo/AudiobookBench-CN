# Phase 4.6 Validation Record v1

Review date: **2026-09-15**  
Branch: `topconf-dl-robustness`  
Scope: metadata, identity, lineage, and fail-closed governance only

## Evidence inputs

```text
AISHELL1_FULL_AUDIT = F:\项目\申请实验室  TTS项目\datasets\AISHELL-1\aishell1_feasibility_full.json
AISHELL1_FULL_AUDIT_SHA256 = E20DA0D9C1281AD87C6FD36B079B70004C49F81CAF2ED79EC421380BA0E198A3
AISHELL1_AUDIO_ARCHIVE_SHA256 = A4A0313CDE0A933E0E01A451F77DE0A23D6C942F4694AF5BB7F40B9DC38143FE
AISHELL1_RESOURCE_ARCHIVE_SHA256 = 1A6749854456E9402BC7295767937367AFED1327799A5E1DF0ED64BAA5F77409
AISHELL3_AUDIO_ARCHIVE_SHA256 = BE2507D431AD59419EC871E60674CAEDB2B585F84FFA01FE359784686DB0E0CC
LEVEL2_POPULATION_V2_FILE_SHA256 = ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
LEVEL2_POPULATION_V2_INTERNAL_IDENTITY_SHA256 = FCFFEEC32F4CAB32DA53BFAD06C0BBBC6F1354AA87277DCE1B1A4EA8E6F90674
LEVEL2_FRESHNESS_V2_FILE_SHA256 = BFD62914A0580FD96AFF1F2847727F016E0BE554AB4A9E3CDC4E418E26B94420
``` 

The official AISHELL-1 authority is [OpenSLR SLR33](https://www.openslr.org/33/).
The candidate was selected after the official archive and supplementary
metadata were acquired and verified; no model or outcome was consulted.

## Validator outcomes

| Check | Result | Meaning |
|---|---|---|
| AISHELL-1 full WAV/transcript audit | PASS | 141,925 valid headers; 2,761 duration-eligible / 300 speakers; 2,750 transcript-complete retained candidates; 11 eligible WAVs excluded for missing transcript |
| V2 population validator | PASS | 400 primary sources, 120 speakers, 2 pools, 40 reserve, 1,600 cases, 400 per mechanism, no speaker split leakage |
| V2 freshness validator | `INSUFFICIENT_EVIDENCE`, exit 2 | `WEEK1_PILOT` and other historical exclusion sets remain incomplete; no freshness PASS claim |
| V1 population validator | FAIL closed | Preserved blocked template is not materialized |
| V1 freshness validator | `INSUFFICIENT_EVIDENCE`, exit 2 | Preserved V1 remains blocked |
| Synthetic Phase4 governance dry run | PASS | Blinding, namespace, failure accounting, retry ledger, threshold, bootstrap, and reveal-gate rehearsal only |
| `python -m pytest tests/topconf -q` | PASS | 58 passed |
| V2 generator reproducibility | PASS | Regeneration produced the same internal population identity hash |

## Authorization firewall

```text
SOURCE_CORPUS_IDENTITY_FROZEN = NO
AMENDMENT_REQUIRED = NO
MODEL_INFERENCE_RUNS = 0
CFPRF_INFERENCE_RUNS = 0
MULTIRESO_INFERENCE_RUNS = 0
AASIST_LEVEL2_INFERENCE_RUNS = 0
SCIENTIFIC_OUTCOMES_COMPUTED = NO
LD_DR95_COMPUTED = NO
RQ1_RQ2_RQ3_OUTCOMES_CHANGED = NO
RESULT_BASED_SELECTION = NO
GT_REVEALED = NO
FINAL_AUTHORIZATION_DECISION = NO_GO
```

V2 is a materialized metadata candidate, not an authorization. The current
blocker is historical freshness and unresolved physical cross-corpus speaker
identity—not source capacity, cardinality, or the frozen scientific design.
