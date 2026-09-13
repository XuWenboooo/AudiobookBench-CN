# Phase 3T Controlled External Reproduction Authorization v1

Status: **FROZEN — LEVEL-1 EXTERNAL FUNCTIONAL REPRODUCTION ONLY**

This authorization follows the Phase3V functional second-baseline recovery.
It authorizes a complete external functional run on PartialEdit v1.1 E1; it
does not authorize Phase4, RQ1 confirmatory execution, attack/defense tuning,
model selection, or confirmatory claims.

```text
AUTHORIZATION_ID = P3T-2026-09-13-01
BASE_COMMIT = 62994f0982149583a86533b20648dae07a789fa7
BRANCH = topconf-dl-robustness
PARALLEL_BRANCH_POLICY = topconf-rq1-prefreeze and topconf-phase4-reconcile-prep frozen for reconciliation; no merge/cherry-pick/rebase

DATA_ROLE = LEVEL_1_EXTERNAL_REPRODUCTION_AND_COMPATIBILITY
PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE
PHASE3V_CLOSURE = PASS

DATASET = PartialEdit v1.1 E1 (VoiceCraft)
DATASET_VERSION = 1.1
DATASET_ARCHIVE = E1.tar.gz
DATASET_ARCHIVE_MD5 = 1f489d2ff488ddd6c9b655127725af2f
DATASET_ARCHIVE_SHA256 = f4bb1a632eed8ddc66bb9285de8b4bc07192d0539385efe9afc9ea04aef3ddcb
DATASET_MANIFEST = research_assurance/topconf/EXTERNAL_DATASET_LOCAL_MANIFEST_V1.json
DATASET_MANIFEST_SHA256 = E397A2B601B6D297AE21A511589817B6EEC5D30A68007CC0260F374A724BA58A
DATASET_CSV = PartialEdit_E1E2.csv (E1 rows only)
DATASET_CSV_SHA256 = ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC
CASE_POPULATION = all valid E1 cases; expected 42471
CASE_ORDER = rows whose path begins E1/ in official CSV order, without sorting or score/GT selection
DATASET_AUDIO_ROOT = F:/项目/申请实验室  TTS项目/topconf_phase3_cache/PartialEdit_v1.1/materialized/E1
FULL_AUDIO_PARSER_VALIDATED = PASS; 42471/42471; zero missing/duplicate/extra; mono 16 kHz PCM16

BASELINE_1_IDENTITY = CFPRF official repository commit 358a901ead8a7d84dac979c3d626e34ef82c2854; external localization baseline
BASELINE_1_LICENSE = MIT
BASELINE_1_CHECKPOINTS = 1FDN_PS.pth SHA256 5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267; 2PRN_PS.pth SHA256 88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36; XLSR SHA256 B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9
BASELINE_1_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3s-cfprf-py310; Python 3.10.11; torch 2.2.2+cu121; fairseq 1.0.0a0 editable; RTX 4060; do not modify
BASELINE_1_NATIVE_OUTPUTS = FDN segment scores, FDN boundary scores, PRN verification scores, PRN regression outputs, coarse/verification/refined native proposals; preserve all class columns

BASELINE_2_IDENTITY = MultiResoModel-Simple repository commit 0f69db3a2d654de47822d951fe6ad256bbaac9ba; public unofficial reimplementation, not original Zhang et al. exact checkpoint
BASELINE_2_LICENSE = root MIT; partialspoof-metrics submodule terms tracked separately
BASELINE_2_CHECKPOINT = baseline-ps-e55.tgz SHA256 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32
BASELINE_2_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310; Python 3.10.11; torch 1.13.1+cu117; torchaudio 0.13.1+cu117; fairseq 0.12.2; RTX 4060
BASELINE_2_NATIVE_OUTPUTS = all six native temporal scales 0.02/0.04/0.08/0.16/0.32/0.64 seconds plus native utterance two-class output; preserve both class columns

STAGE_ORDER = T1 inference only; T2 raw-output validation; T3 canonical adapter mapping; T4 preauthorized Level-1 diagnostics; T5 closure
INFERENCE_COMMANDS = experiments/topconf_phase3t/run_cfprf.py and experiments/topconf_phase3t/run_multireso.py with direct frozen environment Python paths and this authorization ID
RAW_OUTPUT_NAMESPACE = results/topconf_phase3t/
RAW_OUTPUT_SCHEMA = phase3t_raw_v1 JSONL; one record per case and model; case_id, model_id, checkpoint hash, input audio SHA256, sample_rate, duration, native raw outputs, shapes, raw_output_sha256, runtime, attempt, retry_count, terminal status, failure
RAW_OUTPUT_MANIFEST = one append-only manifest JSONL per model plus one raw-output JSONL per model; no derived-only replacement and no silent omission
ADAPTER_VERSION = phase3t_adapter_v1
CANONICAL_SCHEMA = case_id, frame_times, frame_scores; native class-0 spoof score is mapped without calibration; native class columns remain in raw output
MULTIRESO_SCALE_POLICY = map and report all six scales independently; no primary/best scale selection
CFPRF_HEAD_POLICY = preserve and map all native FDN/PRN outputs; no primary/best head selection

GT_ACCESS_BY_MODEL = NO
GT_ACCESS_STAGE = evaluation only, after T1/T2/T3 completeness gates
GT_INPUT_TO_RUNNER = audio path and required model metadata only; no target_start, target_end, fake label, mechanism outcome, or edited-region fields
METRIC_POLICY = preauthorize frame AUROC and frame AUPRC as descriptive Level-1 diagnostics only, using edited-region target and native class-0 spoof score; report every authorized scale/head artifact without winner claims
THRESHOLD_POLICY = no threshold-based primary decision; no calibration, threshold, ranking, or selection
RANGEEER = NOT_PREAUTHORIZED_THIS_RUN
LD_DR95 = NO
WHETHER_A = DEFERRED
WHETHER_B = NOT_RUN
RQ1 = NOT_RUN; E1 functional validation is not a mechanism-shift experiment
PHASE4 = NOT_STARTED

FAILURE_ACCOUNTING = exactly one terminal record for every planned case per baseline; VALID_INFERENCE, AUDIO_LOAD_FAILURE, MODEL_INFERENCE_FAILURE, CUDA_OOM, INVALID_OUTPUT, NONFINITE_OUTPUT, or INFRASTRUCTURE_FAILURE
RETRY_POLICY = at most one retry per case only for classified transient file-read/CUDA infrastructure failure; no retry for score, metric, GT, or output-shape reasons; every attempt recorded
OOM_POLICY = reduce batch size only, preserving per-case waveform/model semantics; no waveform crop/window/scale change; batch-size amendment requires new commit before affected rerun
CODE_FIX_POLICY = only path/device/dtype/serialization/API compatibility; stop affected model, document, patch, test, commit, create new invocation namespace, and restart affected model from clean authorized state; semantic fix stops Phase3T
SEED_POLICY = seed 1234; canonical CSV order; deterministic per-case RNG reset for model execution; no score-driven ordering
STOP_CONDITIONS = stop before metrics on raw incompleteness, duplicate IDs, missing terminal states, semantic adapter failure, GT leakage, or any unauthorized model/output transformation; resource failures are fully accounted and do not trigger model substitution
RESULT_BASED_SUBSTITUTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_HEAD_SELECTIONS = 0

PRE_RUN_TEST = python -m pytest tests/topconf -q
POST_RUN_TESTS = adapter tests, raw-output validator, unified evaluator end-to-end, python -m pytest tests/topconf -q, git diff --check
FULL_SPLIT_COMPLETENESS_GATE = planned cases = terminal cases = 42471 for each baseline; every valid case has raw output or a classified terminal failure; no duplicate IDs
PHASE3T_EXIT = PASS only if both full runs complete or are fully accounted, raw completeness/failure accounting pass, both adapters pass, unified evaluator end-to-end passes, and all result-based counters remain zero
PHASE3T_EXECUTION_AUTHORIZED = YES after this authorization commit only
READY_FOR_PHASE4_HUMAN_RECONCILIATION = NO until Phase3T closure
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

The only permitted scientific interpretation is Level-1 external functional
reproduction/compatibility. It must remain distinct from original-paper
reproduction and from confirmatory robustness evidence.
