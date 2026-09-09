# Week3 Stage-A Second-Generator Selection Record

Date: 2026-09-06

This record completes only the frozen deterministic selection step. It authorizes no Stage-A case generation, detector scoring, B1b, H1/H2/H3, ECAPA, B4, CER, or other scientific execution. A separate Stage-A execution authorization remains required.

## Mechanical completion gate

The authoritative qualification matrix has been checked against the frozen selection contract.

| Check | Result |
|---|---|
| All four candidate qualification states are terminal | `YES` |
| Qualification coverage | `ALL_SURVIVING_CANDIDATES` |
| Unresolved mandatory eligibility field | `NO` |
| External blockers | `NONE` |
| Scientific result used during qualification or selection | `NO` |
| Confirmatory 23-case member used in qualification | `NO` |
| Engineering fixture | `AISHELL3_ENGINEERING_ONLY_SSB0005_0001_REF_0014` |
| Engineering fixture excluded from scientific population | `YES` |
| `READY_FOR_DETERMINISTIC_TIE_BREAK` | `YES` |

The prior `NO` readiness value was stale after Fish Speech S2 reached a terminal dynamic result. This reconciliation does not alter any historical qualification evidence or failure.

## Terminal qualification states

| Candidate | Qualification state | Selection state | Preserved disposition |
|---|---|---|---|
| OpenVoice V2 | `STATIC_FAIL` | `NOT_ELIGIBLE` | The official V2 checkpoint URL returned HTTP 404; no deterministic official acquisition path remained. |
| GPT-SoVITS V3 | `FULLY_INELIGIBLE` | `NOT_ELIGIBLE` | The frozen official Mandarin path could not obtain the required G2PWModel_1.1 asset; engineering smoke failed before waveform emission. |
| F5-TTS v1 Base | `FULLY_ELIGIBLE` | `SELECTED` | All mandatory static and dynamic qualification evidence passed. |
| Fish Speech S2 | `FULLY_INELIGIBLE` | `NOT_ELIGIBLE` | The official CPU load path ended with native access violation `0xC0000005`; 8-GB GPU is not supported. |

The qualification state remains distinct from the selection state: F5-TTS v1 Base remains `FULLY_ELIGIBLE` in the qualification matrix and is `SELECTED` here as the tie-break winner. The other three candidates and their evidence are retained unchanged in the qualification report and matrix.

## Frozen deterministic tie-break

- fully eligible candidates: `F5-TTS v1 Base`
- eligible-set size: `1`
- deterministic tie-break executed: `YES`
- selected second generator: `F5-TTS v1 Base`
- selection reason: the frozen matrix has exactly one `FULLY_ELIGIBLE` candidate. The contract therefore selects that sole candidate without an additional comparison.
- selection used scientific outcome: `NO`

No audio quality, CER, ECAPA, detector output, detectability, localization metric, subjective preference, expected scientific result, or unfrozen runtime preference was considered.

## Selected-generator provenance freeze

| Field | Frozen value |
|---|---|
| Canonical generator | `F5-TTS v1 Base` |
| Provider | `SWivid` |
| Official repository | `https://github.com/SWivid/F5-TTS` |
| Repository commit | `82fc4fe622fe36047d1dff99b550e6018181ea11` |
| Official model ID | `SWivid/F5-TTS` |
| Exact model revision | `84e5a410d9cead4de2f847e7c9369a6440bdfaca` |
| Generation topology | `END_TO_END_REFERENCE_CONDITIONED` |
| Code license | `MIT` |
| Model/checkpoint license | `CC-BY-NC-4.0` (`LICENSE_PASS` for the intended academic research use) |
| Auxiliary-component license | `CC-BY-NC-4.0_PER_OFFICIAL_MODEL_REPOSITORY` (`LICENSE_PASS`) |
| Validated environment | `results/week3_engineering_qualification/f5_tts_v1_base/env` |
| Python/runtime | Windows CPU environment; Python `3.12.9`; PyTorch `2.2.2+cpu` |
| Validated execution path | CPU local load and true offline reload, followed by the engineering-only Mandarin smoke and 16-kHz mono serialization |
| CPU feasibility | `PASS` |
| RTX 4060 Laptop 8-GB feasibility | `NOT_RUN` (not required because the permitted CPU path passed) |
| AISHELL-3 training independence | `UNKNOWN` |

### Frozen assets and hashes

| Official asset | Revision | SHA256 |
|---|---|---|
| `F5TTS_v1_Base/model_1250000.safetensors` | `84e5a410d9cead4de2f847e7c9369a6440bdfaca` | `670900FD14E6C458B95DA6E9ED317CDB20DBAF7A1C02AC06A05475A9D32B6A38` |
| `F5TTS_v1_Base/vocab.txt` | `84e5a410d9cead4de2f847e7c9369a6440bdfaca` | `2A05F992E00AF9B0BD3800A8D23E78D520DBD705284ED2EEDB5F4BD29398FA3C` |
| `charactr/vocos-mel-24khz/config.yaml` | `0feb3fdd929bcd6649e0e7c5a688cf7dd012ef21` | `DA9033922F969A47F0C160010226919E59F27761FD5066F3828D46DE6650B0FC` |
| `charactr/vocos-mel-24khz/pytorch_model.bin` | `0feb3fdd929bcd6649e0e7c5a688cf7dd012ef21` | `97EC976AD1FD67A33AB2682D29C0AC7DF85234FAE875AEFCC5FB215681A91B2A` |

## Evidence freeze

- qualification matrix: `results/week3_engineering_qualification/qualification_matrix.json`
- static provenance and license preflight: `results/week3_engineering_qualification/static_preflight.json`
- F5 qualification, assets, local/offline load, smoke, and waveform QA: `results/week3_engineering_qualification/f5_tts_v1_base/qualification.json`
- native smoke output: `results/week3_engineering_qualification/f5_tts_v1_base/smoke/engineering_smoke.wav`
- true-offline smoke output: `results/week3_engineering_qualification/f5_tts_v1_base/smoke/engineering_smoke_offline.wav`
- standardized 16-kHz mono output: `results/week3_engineering_qualification/f5_tts_v1_base/smoke/engineering_smoke_16k.wav`
- historical qualification report: `research_assurance/WEEK3_ENGINEERING_QUALIFICATION_REPORT.md`

The standardized engineering-only waveform has SHA256 `82552566C1D2340A8BC28E08BE45E186D8D4C3E09E3B0DB8C631DCEA9F9B8B51`; its recorded QA is finite, readable, mono, 16 kHz, non-empty, and without unexpected clipping. It is not a Stage-A case or scientific result.

## Status and strict stop

- current final selection: `F5-TTS v1 Base`
- selection status: `SELECTED`
- `NO_ELIGIBLE_GENERATOR`: `NOT_APPLICABLE`
- selected provenance frozen: `YES`
- 23-case Stage-A generation executed: `NO`
- scientific metric executed: `NO`
- Week3 Stage-A scientific execution entered: `NO`
- `READY_FOR_STAGE_A_READINESS_REVIEW`: `YES` (readiness review only; not execution authorization)

The frozen H1/H2/H3, 23-case population and split semantics, bootstrap, zones, detector, B1b/S2, and GT semantics are unchanged.
