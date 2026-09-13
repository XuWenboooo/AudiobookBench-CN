# Phase 3U Second Baseline Authorization v1

Status: **FROZEN — FUNCTIONAL BASELINE PATH ONLY; NO SCIENTIFIC REPRODUCTION**

This is a new append-only authorization after the blocked Phase3S closure. It
does not modify the original Phase3, Phase3R, or Phase3S closures and does not
authorize Phase3T full reproduction, Phase 4, metric computation, ranking, or
RQ1/RQ2/RQ3.

```text
PHASE3U_AUTHORIZATION_ID = P3U-2026-09-13-01
BASE_COMMIT = b661b7b1f3bea8e523cd24d0c447af2bc4ba16e0
ORIGINAL_PHASE3_CLOSURE = BLOCKED
PHASE3R_RECOVERY_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE

AUTHORIZED_BASELINE = MultiResoModel-Simple
BASELINE_ROLE = REPRODUCIBLE_EXTERNAL_BASELINE; NOT_ORIGINAL_OFFICIAL_MULTIRESo_CHECKPOINT
AUTHORIZED_REPOSITORY = https://github.com/hieuthi/MultiResoModel-Simple.git
AUTHORIZED_REPO_COMMIT = 0f69db3a2d654de47822d951fe6ad256bbaac9ba
AUTHORIZED_LICENSE = repository MIT; external submodule terms separately tracked
AUTHORIZED_LICENSE_SHA256 = ED42AB78ED79E83DB342D3044031362896BDF838D8712746B9613B37321C19C0
AUTHORIZED_REQUIREMENTS_SHA256 = F41617E6E49951BBA9ECDD75941D1DA08C00EDC234815D5238694CAA52EF7A7B
AUTHORIZED_SUBMODULE = hieuthi/partialspoof-metrics at 4fc9b8852d9cebca2686b99cd4d98f95a808c161; MIT notices in source files; no standalone LICENSE file

AUTHORIZED_CHECKPOINT_SOURCE = https://huggingface.co/hieuthi/MultiResoModel-Simple-ckpts
AUTHORIZED_CHECKPOINT_REVISION = 31fd984c53a95e428551f13c4d95645b3cb8c885
AUTHORIZED_CHECKPOINT_FILENAME = baseline-ps-e55.tgz
AUTHORIZED_CHECKPOINT_URL = https://huggingface.co/hieuthi/MultiResoModel-Simple-ckpts/resolve/31fd984c53a95e428551f13c4d95645b3cb8c885/baseline-ps-e55.tgz
AUTHORIZED_CHECKPOINT_EXPECTED_SIZE = 3701009843 bytes
AUTHORIZED_CHECKPOINT_EXPECTED_LFS_SHA256 = 0c394f03558ecdd7a6b81bf6c0fd8ee642c5937ba22cc852f58ae4e7dc480e32
AUTHORIZED_CHECKPOINT_EXPECTED_INNER = exp/baseline/55.pth
CHECKPOINT_PROVENANCE = AUTHOR_REPOSITORY_LINKED_PUBLIC_CHECKPOINT
CHECKPOINT_IDENTITY = PUBLIC_REIMPLEMENTATION_RUN; NOT_PAPER_EXACT_CHECKPOINT

AUTHORIZED_DOWNLOAD_COUNT = 1 complete official Hugging Face transport; no retry or mirror
AUTHORIZED_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3u-multireso-py310
AUTHORIZED_PYTHON = 3.10.11 from F:/项目/申请实验室/python.exe
AUTHORIZED_RUNTIME_TARGET = PyTorch 1.13.1+cu117; torchaudio 0.13.1+cu117; fairseq 0.12.2; requirements.txt baseline
CFPRF_ENVIRONMENT_POLICY = do not modify topconf-phase3s-cfprf-py310

AUTHORIZED_LOAD_TEST = checkpoint archive integrity, inner checkpoint identity, documented model load, and GPU load only
AUTHORIZED_SMOKE_SCOPE = at most 3 deterministic PartialEdit v1.1 E1 WAVs; no GT-based selection
AUTHORIZED_SMOKE_CASES = E1/p225/p225_001_edited_partial_16k.wav; E1/p225/p225_002_edited_partial_16k.wav; E1/p225/p225_003_edited_partial_16k.wav
AUTHORIZED_DATASET = PartialEdit v1.1 E1 only
AUTHORIZED_OUTPUT_NAMESPACE = results/topconf/reproduction_recovery/PartialEdit_E1/MultiResoModel-Simple/phase3u_smoke

FAILURE_ACCOUNTING = record source, revision, filename, expected/actual size, hash, transport, timestamps, load semantics, and failure category
RETRY_POLICY = one bounded checkpoint transport only; no retry, mirror, or result-driven checkpoint shopping
CODE_FIX_POLICY = only path/dependency compatibility fixes required to execute the documented load/smoke; preserve model architecture and output semantics; record every fix
RESULT_BASED_SELECTIONS = 0

PROHIBITED_ACTIONS = Phase3T full reproduction; Phase 4; RQ1/RQ2/RQ3; full split inference; metric computation; ranking; threshold/calibration/smoothing; training/retraining; GT edits; unofficial artifacts; paid compute; modification of historical closures; modification of CFPRF environment
REAUTHORIZATION_REQUIRED_FOR = any second checkpoint; new dataset; more than 3 samples; full inference; evaluator changes; scientific metrics; any transport beyond the single authorized download
PHASE3T_EXECUTION_AUTHORIZED = NO
READY_FOR_PHASE4_REVIEW = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

The candidate is explicitly a public reimplementation baseline. It may become
a verified functional path only after provenance, checkpoint hash, isolated
environment, load, and deterministic smoke gates all pass.
