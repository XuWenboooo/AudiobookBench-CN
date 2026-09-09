# Week3 Stage-A Second-Generator Dynamic Engineering Qualification

Date: 2026-09-06

This report covers engineering qualification only. It does not select a final generator, apply the deterministic tie-break, enter the 23-case Stage-A experiment, or run scientific metrics.

## Engineering-only fixture

- `engineering_fixture_id`: `AISHELL3_ENGINEERING_ONLY_SSB0005_0001_REF_0014`
- source: `datasets/AISHELL-3/raw/train/wav/SSB0005/SSB00050001.wav`
- source text: `广州女大学生登山失联四天警方找到疑似女尸`
- reference: `datasets/AISHELL-3/raw/train/wav/SSB0005/SSB00050014.wav`
- reference text: `将于十一月二十一日早七点在东方明珠塔下跑起`
- same speaker: `SSB0005`
- `engineering_only=true`
- `excluded_from_scientific_population=true`
- `smoke_only=true`

## Qualification order

Immutable revision and metadata are recorded before binary acquisition. All statically identifiable mandatory components require authoritative `LICENSE_PASS` before acquisition or execution. Dynamic discovery is limited to additional official files required by the frozen official inference path; every such file requires provenance, revision/archive evidence, SHA256, and license closure before use.

## Candidate results

| Candidate | State | Static license preflight | Local load | Offline reload | CPU | GPU 8GB | Smoke | Waveform QA |
|---|---|---|---|---|---|---|---|---|
| OpenVoice V2 | `STATIC_FAIL` | `LICENSE_PASS` | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` |
| GPT-SoVITS V3 | `FULLY_INELIGIBLE` | `LICENSE_PASS` | `PASS` | `PASS` | `FAIL` (required Mandarin path) | `NOT_RUN` | `FAIL` (G2PW unavailable) | `NOT_RUN` |
| F5-TTS v1 Base | `FULLY_ELIGIBLE` | `LICENSE_PASS` | `PASS` | `PASS` | `PASS` | `NOT_RUN` | `PASS` | `PASS` |
| Fish Speech S2 | `FULLY_INELIGIBLE` | `LICENSE_PASS` | `FAIL` (native 0xC0000005) | `NOT_RUN` | `FAIL` | `NOT_SUPPORTED` | `NOT_RUN` | `NOT_RUN` |

OpenVoice V2 is `STATIC_FAIL`: the recorded official V2 checkpoint URL returned HTTP 404, so no deterministic official acquisition path remained under the frozen rules. Dynamic qualification was not run.

GPT-SoVITS V3 reached `FULLY_INELIGIBLE` after local/offline initialization succeeded but the official frozen Mandarin path required G2PWModel_1.1, whose frozen official URL and official CDN variant both returned HTTP 404. No mirror or substitution was used, and the required engineering smoke therefore failed before waveform emission. F5-TTS v1 Base reached `FULLY_ELIGIBLE` on CPU: all frozen model/vocoder assets were acquired and hashed, local and true-offline reload passed, the engineering-only Mandarin smoke emitted a finite mono waveform, and mechanical waveform QA passed after the required 16 kHz mono PCM serialization. Fish Speech S2 official acquisition is now complete, including both sharded safetensors, codec, tokenizer, configuration, and license files, all hashed against the frozen revision. The official CPU load path then terminated with Windows native access violation `0xC0000005` during sharded safetensors loading; a bounded bfloat16 default-dtype compatibility attempt terminated in the same load phase. With 8 GB GPU officially unsupported and no permitted CPU path, Fish is `FULLY_INELIGIBLE`. No mirror or substitution was used.

No final generator is selected. No scientific result has been observed. The deterministic tie-break is not ready.

## Scope and stop conditions

- Confirmatory 23-case member used: `NO`.
- Scientific metric, ECAPA, CER, and subjective/comparative evaluation: `NO`.
- Week3 Stage-A scientific generation entered: `NO`.
- Model lineage, reference/text semantics, and generation topology were not changed.
- Stop: Fish Speech S2 reached a terminal dynamic failure. No deterministic tie-break is run.

## Evidence locations

Candidate-specific evidence belongs under `results/week3_engineering_qualification/<candidate>/`. The final matrix is `results/week3_engineering_qualification/qualification_matrix.json`.

## Frozen completion gate

- qualification coverage: `ALL_SURVIVING_CANDIDATES`
- license closure: `PASS` for all acquired mandatory components
- provenance closure: `PASS`
- asset/hash closure: `PASS` for Fish official inventory and all acquired assets
- environment qualification: `COMPLETE` through terminal Fish local-load result
- offline qualification: `INCOMPLETE` (Fish load failed before offline reload)
- hardware qualification: `COMPLETE` (Fish CPU `FAIL`; 8GB GPU `NOT_SUPPORTED`)
- engineering smoke qualification: `INCOMPLETE` (Fish not run)
- mechanical waveform QA: `INCOMPLETE` (Fish not run after load failure)
- scientific metric executed: `NO`
- ECAPA executed: `NO`
- CER executed: `NO`
- confirmatory 23-case member used: `NO`
- final generator selected: `NO`
- deterministic tie-break executed: `NO`
- Week3 Stage-A scientific generation entered: `NO`
- READY_FOR_DETERMINISTIC_TIE_BREAK: `YES` (post-qualification reconciliation below)

## Post-qualification gate reconciliation

This addendum records only the subsequent mechanical completion-gate reconciliation and does not modify any candidate's historical engineering evidence or failure.

- all four qualification states are terminal: `YES`
- qualification coverage: `ALL_SURVIVING_CANDIDATES`
- unresolved mandatory eligibility fields: `NO`
- external blockers: `NONE`
- scientific result used during qualification: `NO`
- confirmatory 23-case member used: `NO`
- `READY_FOR_DETERMINISTIC_TIE_BREAK`: `YES`

The former `NO` readiness state was stale once Fish Speech S2 had a terminal dynamic result. The deterministic selection outcome and selected-generator provenance are recorded separately in `research_assurance/WEEK3_SECOND_GENERATOR_SELECTION_STATUS.md`; this engineering report continues to preserve the original qualification results.
