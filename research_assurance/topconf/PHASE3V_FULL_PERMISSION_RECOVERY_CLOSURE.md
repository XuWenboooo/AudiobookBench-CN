# Phase 3V Full-Permission Second-Baseline Recovery Closure

Status: **IN PROGRESS — AUTHORIZATION FROZEN**

```text
PHASE3V_AUTHORIZATION = P3V-2026-09-13-01
BASE_COMMIT = b6f80771544881e98269980efbbc176401a55e99
ORIGINAL_PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE
PHASE3V_CLOSURE = IN_PROGRESS
READY_FOR_PHASE3T_CONTROLLED_REPRODUCTION_REVIEW = NO
PHASE3T_EXECUTION_AUTHORIZED = NO
READY_FOR_PHASE4_REVIEW = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

This is append-only. All historical blocked closures remain authoritative.

## Initial gate state

```text
SCHANNEL_ERROR = CRYPT_E_NO_REVOCATION_CHECK (0x80092012), curl 8.21.0 Schannel
SCHANNEL_ROOT_CAUSE = PENDING_ALTERNATE_SECURE_TRANSPORT_DIAGNOSIS
DOWNLOAD_TRANSPORTS_ATTEMPTED = prior Phase3U single Schannel attempt only; Phase3V attempts pending
HUGGINGFACE_HUB_STATUS = NOT_YET_INSTALLED
GIT_LFS_STATUS = NOT_REQUIRED_YET
MULTIRESO_SIMPLE_CHECKPOINT_MATERIALIZATION = PENDING
MULTIRESO_SIMPLE_CHECKPOINT_LOAD = NOT_AUTHORIZED_UNTIL_HASH_PASS
MULTIRESO_SIMPLE_SMOKE = NOT_AUTHORIZED_UNTIL_LOAD_PASS
BASELINE_PATH_1 = CFPRF VERIFIED
BASELINE_PATH_2 = NOT_ESTABLISHED
EXTERNAL_BASELINE_PATHS = 1
FULL_AUDIO_EXTERNAL_DATASETS = 1
FULL_AUDIO_PARSER_VALIDATED = 1
SCIENTIFIC_METRICS_COMPUTED = 0
SCIENTIFIC_OUTCOMES_PRODUCED = 0
RESULT_BASED_SELECTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
RETRAINING_SUBAUTHORIZATION_CREATED = NO
RETRAINING_INVOKED = NO
```

## Phase3V exit gate

`PHASE3V_CLOSURE = PASS` requires a secure official/author-linked source,
complete nonzero archive, expected filename/size, SHA256, archive integrity,
repository/license provenance, isolated environment, documented-compatible
checkpoint load, deterministic bounded GPU smoke, finite temporal output, and
feasible raw schema mapping. It permits only a Phase3T review; it never
authorizes Phase3T execution or Phase4.

## Final Phase3V closure (append-only)

```text
BRANCH = topconf-dl-robustness
LOCAL_HEAD = pending_commit_after_this_closure
REMOTE_HEAD = 2e197be (before this closure commit)
WORKING_TREE = pending_commit_after_this_closure
PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE
PHASE3V_AUTHORIZATION = P3V-2026-09-13-01
PHASE3V_AUTHORIZATION_SHA256 = 36D6C6D84752CF5A7E0575C546D3EF070FE3389EC2ABC6D1D6B3D21BE15B8DFC
SCHANNEL_ERROR = CRYPT_E_NO_REVOCATION_CHECK (0x80092012) from prior curl 8.21.0; Phase3V official curl 8.22.0 via proxy remained curl 60 with verify results 35/53
SCHANNEL_ROOT_CAUSE = pre-existing local WinINET proxy/MITM path plus unavailable revocation/unsupported local certificate validation on the LibreSSL curl path; direct public route timed out; no TLS verification bypass used
DOWNLOAD_TRANSPORTS_ATTEMPTED = official curl 8.22.0 --ca-native via 127.0.0.1:17890 (failed verification); requests+certifi verify=true HEAD (failed issuer verification); Windows Invoke-WebRequest HEAD (200, then stopped partial at 127957617 bytes); Windows BITS official HF resolve URL (complete and verified); Windows BITS official fairseq wav2vec URL (complete and verified)
OFFICIAL_CURL_INSTALLED = YES
OFFICIAL_CURL_VERSION = curl 8.22.0 x86_64-w64-mingw32
OFFICIAL_CURL_TLS_BACKEND = LibreSSL 4.3.2; native CA diagnostic attempted; no --insecure/-k
HUGGINGFACE_HUB_STATUS = NOT_INVOKED; requests/certifi diagnostic only; no insecure verify setting
GIT_LFS_STATUS = git-lfs 3.7.1 available; not required for the author-linked release archive
MULTIRESO_SIMPLE_REPO_COMMIT = 0f69db3a2d654de47822d951fe6ad256bbaac9ba
MULTIRESO_SIMPLE_LICENSE = root MIT; partialspoof-metrics submodule terms tracked separately
MULTIRESO_SIMPLE_CHECKPOINT_SOURCE = https://huggingface.co/hieuthi/MultiResoModel-Simple-ckpts
MULTIRESO_SIMPLE_CHECKPOINT_REVISION = 31fd984c53a95e428551f13c4d95645b3cb8c885
MULTIRESO_SIMPLE_CHECKPOINT_FILENAME = baseline-ps-e55.tgz
MULTIRESO_SIMPLE_CHECKPOINT_SIZE = 3701009843 bytes
MULTIRESO_SIMPLE_CHECKPOINT_SHA256 = 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32
MULTIRESO_SIMPLE_CHECKPOINT_IDENTITY = author-repository-linked public unofficial reimplementation run; not original-paper exact checkpoint
MULTIRESO_SIMPLE_ENVIRONMENT = isolated Python 3.10.11; torch 1.13.1+cu117; torchaudio 0.13.1+cu117; fairseq 0.12.2; compatibility NumPy 1.23.5/SciPy 1.9.3/scikit-learn 1.1.3/numba 0.56.4; CUDA RTX 4060 Laptop GPU
MULTIRESO_SIMPLE_CHECKPOINT_LOAD = PASS; strict=True; missing=0; unexpected=0; dtype=float32; GPU move PASS
MULTIRESO_SIMPLE_SMOKE = PASS; exactly 3 deterministic E1 samples; no GT; forward 3.5845 s; peak VRAM 1872419840 bytes; all outputs finite
MULTIRESO_SIMPLE_TEMPORAL_OUTPUT = six raw repository units: 20/40/80/160/320/640 ms; two-class temporal arrays preserved; no normalization
MULTIRESO_SIMPLE_SCHEMA_MAPPING = frame_times=[i*unit,min((i+1)*unit,audio_duration)]; frame_scores=raw class-1 value; no calibration/smoothing/threshold
BASELINE_PATH_1 = CFPRF
BASELINE_PATH_2 = MultiResoModel-Simple
EXTERNAL_BASELINE_PATHS = 2
REPLACEMENT_SEARCH_INVOKED = NO
REPLACEMENT_CANDIDATES = none; authorized MultiResoModel-Simple path recovered
RETRAINING_SUBAUTHORIZATION_CREATED = NO
RETRAINING_INVOKED = NO
FULL_AUDIO_EXTERNAL_DATASETS = 1
FULL_AUDIO_PARSER_VALIDATED = 1
GPU_ENVIRONMENT = PASS; existing CFPRF environment unchanged
SCIENTIFIC_METRICS_COMPUTED = 0
SCIENTIFIC_OUTCOMES_PRODUCED = 0
RESULT_BASED_SELECTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
TESTS = python -m pytest tests/topconf -q: 26 passed; git diff --check: PASS; manifest JSON parse: PASS
PHASE3V_CLOSURE = PASS
REMAINING_BLOCKERS = Phase3T controlled reproduction review is not executed or authorized; Phase4, RQ1/RQ2/RQ3, and confirmatory execution remain closed
COMMITS = pending_commit_after_this_closure
PUSH_STATUS = pending
READY_FOR_PHASE3T_CONTROLLED_REPRODUCTION_REVIEW = YES
PHASE3T_EXECUTION_AUTHORIZED = NO
READY_FOR_PHASE4_REVIEW = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

The PASS is limited to a provenance-verified functional second baseline path
and the authorized bounded smoke. It does not claim reproduction of the
original MultiResoModel paper checkpoint or any scientific result.

## Post-commit finalization ledger (append-only)

```text
EVIDENCE_COMMIT = c17e7f1
EVIDENCE_COMMIT_PUSH_STATUS = PUSHED to origin/topconf-dl-robustness
FINAL_CLOSURE_LEDGER = this append-only record is included in the next commit and will be pushed immediately
```
