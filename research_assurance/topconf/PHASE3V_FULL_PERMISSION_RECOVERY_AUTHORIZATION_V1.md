# Phase 3V Full-Permission Second-Baseline Recovery Authorization v1

Status: **FROZEN — SECURE INFRASTRUCTURE RECOVERY ONLY**

This append-only authorization follows the blocked Phase3U closure. It does
not alter the Phase3, Phase3R, Phase3S, or Phase3U historical closures and does
not authorize Phase3T full reproduction, Phase 4, RQ1/RQ2/RQ3, metrics,
ranking, or confirmatory analysis.

```text
PHASE3V_AUTHORIZATION_ID = P3V-2026-09-13-01
BASE_COMMIT = b6f80771544881e98269980efbbc176401a55e99
BRANCH = topconf-dl-robustness
ORIGINAL_PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE

AUTHORIZED_OBJECTIVE = establish one secure, provenance-verified MultiResoModel-Simple baseline path
AUTHORIZED_REPOSITORY = https://github.com/hieuthi/MultiResoModel-Simple.git
AUTHORIZED_REPO_COMMIT = 0f69db3a2d654de47822d951fe6ad256bbaac9ba
AUTHORIZED_BASELINE = MultiResoModel-Simple; unofficial open reimplementation; not original Zhang et al. checkpoint
AUTHORIZED_LICENSE = root MIT; submodule terms tracked separately
AUTHORIZED_CHECKPOINT_SOURCE = https://huggingface.co/hieuthi/MultiResoModel-Simple-ckpts
AUTHORIZED_CHECKPOINT_REVISION = 31fd984c53a95e428551f13c4d95645b3cb8c885
AUTHORIZED_CHECKPOINT_FILENAME = baseline-ps-e55.tgz
AUTHORIZED_CHECKPOINT_EXPECTED_SIZE = 3701009843 bytes
AUTHORIZED_CHECKPOINT_EXPECTED_LFS_SHA256 = 0c394f03558ecdd7a6b81bf6c0fd8ee642c5937ba22cc852f58ae4e7dc480e32

AUTHORIZED_SECURE_TRANSPORTS = official curl.se build with verified checksum; huggingface_hub; Git/Git LFS; Python requests/urllib with TLS verify=true; browser-compatible official URL; per-command Schannel best-effort only after safer transports fail
PROHIBITED_TRANSPORTS = curl -k; curl --insecure; requests verify=False; HF_HUB_DISABLE_SSL_VERIFY; global revocation disable; unknown roots; mirrors; unverified executables
AUTHORIZED_TRANSPORT_POLICY = switch only among official-source secure mechanisms; record each attempt; stop after complete verified archive
AUTHORIZED_DOWNLOAD_BUDGET = bounded secure recovery attempts, one per distinct mechanism; no brute-force retry loop; no duplicate content after checksum PASS

AUTHORIZED_TOOLS_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-tools-py310
AUTHORIZED_TOOLS_PYTHON = 3.10.11 from F:/项目/申请实验室/python.exe
AUTHORIZED_MODEL_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310 if load dependencies require isolation
CFPRF_ENVIRONMENT_POLICY = do not modify topconf-phase3s-cfprf-py310
SYSTEM_PYTHON_POLICY = do not modify system Python or primary project environment

AUTHORIZED_LOAD_SCOPE = archive integrity, inner checkpoint identity, documented model load, GPU load
AUTHORIZED_DATASET = PartialEdit v1.1 E1 only
AUTHORIZED_SMOKE_CASES = at most 3 deterministic manifest-order first-N cases, frozen before execution; no GT access
AUTHORIZED_OUTPUT_NAMESPACE = results/topconf/reproduction_recovery/PartialEdit_E1/MultiResoModel-Simple/phase3v_smoke
AUTHORIZED_SCHEMA_CHECK = raw temporal output to frame_times/frame_scores only; no calibration, smoothing, thresholding, or metric

FAILURE_ACCOUNTING = source, revision, filename, method, TLS backend, start/end, status, bytes, expected/actual size, hash, and failure category
RETRY_POLICY = no insecure retry; no unbounded retry; alternate secure mechanism must be explicitly recorded
CODE_FIX_POLICY = dependency/path/device/API compatibility only; preserve architecture, weights, score definition, aggregation, and temporal semantics
RETRAINING = not authorized in this baseline recovery; requires separate subauthorization
RESULT_BASED_SELECTIONS = 0
SCIENTIFIC_METRICS = 0

PROHIBITED_ACTIONS = Phase3T execution; Phase4; RQ1/RQ2/RQ3; full split inference; metrics; ranking; model selection by result; training/retraining; GT edits; changing historical closures; paid compute
PHASE3T_EXECUTION_AUTHORIZED = NO
READY_FOR_PHASE4_REVIEW = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

The only success claim permitted by this authorization is a verified
functional baseline path. It must remain explicitly distinguished from an
original-paper checkpoint reproduction.
