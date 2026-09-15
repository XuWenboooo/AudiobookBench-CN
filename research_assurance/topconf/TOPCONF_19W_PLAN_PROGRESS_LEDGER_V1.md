# TOPCONF 19-Week Plan Progress Ledger v1

Audit date: `2026-09-15`  
Authoritative plan: `F:/项目/申请实验室  TTS项目/计划表/Top-Conference Confirmatory Phase — 19周逐日实验计划.md`  
Branch: `topconf-dl-robustness`  
Local/remote head at audit: `71d4a2d5094a4635a9a0d00b17aba7a9c9eda931` / same  
Scope: W1–W6 only; no W7 scientific inference.

## Status policy

- `COMPLETE`: the plan deliverable and its required gate evidence are present;
  a related artifact alone is insufficient.
- `PARTIAL`: material progress exists, but at least one named deliverable or
  gate field is absent or not frozen.
- `BLOCKED`: a required gate cannot pass with the presently authorized assets.
- `SUPERSEDED_WITH_JUSTIFICATION`: a later frozen artifact replaces the
  earlier draft without changing the scientific core; the historical artifact
  remains preserved.
- `NOT_STARTED`: no qualifying evidence was found.

## Audited ledger

| Week | Plan requirement | Status | Evidence / commit / hash where applicable | Tests and scientific state |
|---|---|---|---|---|
| W1 | Close Week1–5 pilot, audit Week4, freeze novelty and the reset boundary | `PARTIAL` | `WEEK1_FREEZE.md` SHA256 `A0C55C52DD3FADC50F2EF253DB7E65CAFF7BCD198DEEC8A8B940914904708D06`; `research_assurance/archive/PILOT_EVIDENCE_REGISTER.md` SHA256 `531D7EE0BCA425E76255EA55E82C6B9CB5B55EAEF6014959AE3A1E51D5781017`; `research_assurance/topconf/NOVELTY_LEDGER_V1.md` SHA256 `AE03DB388D254F29E79D5D88A33C4E7F5BBC932DCBF32D70DEC44740472B0E2B`; Week4 closure and post-run audit are present. | Historical tests and reports exist. The exact `TOPCONF_PILOT_INVENTORY.md` and `TOPCONF_RESEARCH_RESET_V1.md` names are absent; all historical outputs remain pilot/historical and were not promoted. |
| W2 | Freeze RQ1–RQ3, Whether definitions, Where, threat model, metrics and stop gates | `SUPERSEDED_WITH_JUSTIFICATION` | Draft `TOPCONF_RESEARCH_PREREGISTRATION_V1.md` remains preserved (SHA256 `75C28DF08B4923E3684C8A835773FF3A7305E0C264052715D59D758512647910`). It was superseded for the active design by `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md` SHA256 `91BB6BE78BFBFF948C7B2559AFDC7ED6F3A87BA116BDC59807D1194B15BB115C`, commit `69dca0964c5b6865289420dae8cfb8bc15b153d9`; the Phase4.9R amendment is prospective only. | Design fields, pooling, thresholds, metrics, gap gate and prohibition rules are frozen for review. This is not execution authorization; no confirmatory outcomes were accessed. |
| W3 | Build unified Whether–Where evaluator, detection/frame/event/RangeEER metrics, time alignment and synthetic fixtures | `PARTIAL` | Evaluator package under `src/audiobookbench/topconf/evaluation/`, schemas and external parsers; evaluator code last bound by commit `bf66933347889b7f0acaa12ba2681470151b9d59`; current topconf test suite is 91 passing. | Detection, frame, event/proposal, RangeEER, gap and robustness modules are present and tested. An exact named `TOPCONF_UNIFIED_EVALUATOR_V1` freeze manifest was not found; no W7 or confirmatory model output was produced. |
| W4 | Establish at least two external partial-deepfake distributions with audio, temporal GT, license and adapters | `PARTIAL` | PartialEdit v1.1 E1 is fully materialized and audited; PartialSpoof v1.2 official eval recovery is in progress as a bounded, non-scientific resource action. `DATASET_PROVENANCE_REGISTER_V1.md`, `DATASET_ADAPTERS_V1.md`, and current `W7_DISTRIBUTION_MATRIX_V1.md` bind the evidence. | PartialEdit parser/audio/GT checks pass. PartialSpoof labels/VAD/protocols pass, but the original local audio file was a 499,712-byte placeholder; no W7 run started. Final W4 status is conditioned on recovery hash, extraction and integrity checks. |
| W5 | Reproduce B1b/B4, BAM and CFPRF; record exact source/checkpoint and unified compatibility | `PARTIAL` | CFPRF official repository commit `358a901ead8a7d84dac979c3d626e34ef82c2854`, strict checkpoint evidence and Phase3T terminal artifacts; `PHASE3T_CONTROLLED_REPRODUCTION_CLOSURE.md`, closure commit `17b6419e4ee185a7029034776034235bcf17eac7`. BAM rights/checkpoint are unresolved; B1b/B4 are historical internal baselines, not external reproduction. | CFPRF: 42,471 terminal, 42,455 valid, 16 failures, missing/orphan 0; adapter and evaluator checks pass. B1b is pilot-only; B4 is diagnostic-only; BAM is blocked. No result-based selection. |
| W6 | Add SAL/TRACE and complete a frozen matrix with at least four distinct localization paradigms | `BLOCKED` | `W6_LOCALIZER_REPRODUCTION_INVENTORY_V1.md`, `LOCALIZER_PARADIGM_MATRIX_V1.md`, and `W6_RESOURCE_GAP_ANALYSIS_V1.md` below. Verified functional paradigms are currently CFPRF and MultiResoModel-Simple only. | MultiReso has 42,471 terminal, 42,438 valid, 33 audio-load failures, six scales, strict load and smoke pass, but is an author-linked public reimplementation rather than the original-paper checkpoint. SAL lacks a verified checkpoint; BAM rights are unresolved; TRACE lacks a verified official audio-localization code/checkpoint. W6 gate is blocked and W7 science is prohibited. |

## Preservation and no-outcome audit

```text
PHASE4_9R_PRESERVED = YES
V3_CONFIRMATORY_OUTCOMES_ACCESSED = NO
V3_POPULATION_SHA256 = AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4
V5_FRESHNESS_STATUS = PASS; PATH_B_PROSPECTIVE_PROJECT_ENTRY
V5_FRESHNESS_SHA256 = 6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E
PHASE4_9R_REOPENED = NO
RQ2_ATTACK_RUNS = 0
RQ3_RUNS = 0
FINAL_CONFIRMATORY_RUNS = 0
RESULT_BASED_MODEL_SELECTIONS = 0
RESULT_BASED_DATASET_SELECTIONS = 0
RESULT_BASED_METRIC_CHANGES = 0
```

The ledger is a progress audit, not a claim that W1–W6 gates passed. The
authoritative stop decision is in `TOPCONF_W6_CLOSURE_V1.md`.
