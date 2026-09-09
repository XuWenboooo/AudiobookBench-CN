# Dependency / Environment Audit — Week 1 (read-only)

No package was installed, upgraded, or removed during this audit.

## 1. Week-1 runtime chain (verified installed versions, managed venv)

| Package | Installed | Used by | Recorded in |
|---|---|---|---|
| Python | 3.13.12 (managed) | whole chain | WEEK1_FREEZE / day6b records |
| numpy | 2.5.2 | features/aggregation/scoring | requirements.txt |
| scipy | 1.18.1 | resampling | requirements.txt |
| soundfile | 0.14.0 | audio IO (PCM16 outputs) | requirements.txt |
| praat-parselmouth | 0.4.7 | Praat F0 (primary backend) | requirements.txt |
| pyyaml | 6.0.3 | frozen configs | requirements.txt |
| scikit-learn | 1.9.0 | AUROC/AUPRC | requirements.txt |
| matplotlib | 3.11.1 | figures | requirements.txt |
| torch | 2.14.0+cpu | ECAPA inference | requirements-speaker.txt (documented, not pinned) |
| torchaudio | 2.11.0 | speechbrain transitively | requirements-speaker.txt |
| speechbrain | 1.1.1 | ECAPA wrapper | requirements-speaker.txt (pinned) |

## 2. Model provenance

- Model: `speechbrain/spkrec-ecapa-voxceleb` (VoxCeleb-pretrained,
  inference-only; the speaker encoder is never trained in Week 1).
- Checkpoint SHA-256 (embedding_model.ckpt, 83,316,686 B):
  `0575CB64845E6B9A10DB9BCB74D5AC32B326B8DC90352671D345E2EE3D0126A2`
  (pinned in WEEK1_FREEZE and day6b_freeze_record.json).
- Local offline copy under `pretrained/spkrec-ecapa-voxceleb/`;
  `HF_HUB_OFFLINE=1` at load time; no runtime network dependency.
- Expected input 16 kHz; output 192-d.

## 3. Cross-version stability evidence

- Day 6B/6C execution: torch 2.14.0+cpu (recorded).
- Independent Week-1 audit: torch 2.13.0+cpu / Python 3.14 — representative
  fresh-vs-cached ECAPA embedding cosine 0.99999988; B1 AUROC reproduced
  exactly from cached embeddings (WEEK1_FREEZE, limitations.md).
- Residual risk: torch is deliberately unpinned in
  `requirements-speaker.txt`; a future torch major bump is not guaranteed
  bit-identical. Mitigation: the frozen embeddings (results/day6b,
  results/day6c) decouple evaluation from re-inference.

## 4. Requirements files

- `requirements.txt`: Week-1 core scientific stack (unpinned).
- `requirements-speaker.txt`: speechbrain==1.1.1 pinned; torch documented
  (2.14.0+cpu) with install command; explicitly notes no agent-private
  path is a runtime dependency.
- Day-8 (CosyVoice) environment: **WORK IN PROGRESS — OWNED BY DAY8
  CODEX**. Not audited, not touched (see scope note below).

## 5. Findings

| # | Finding | Severity |
|---|---|---|
| 1 | requirements.txt versions unpinned (numpy 2.x, sklearn 1.9 are recent majors; future majors may break) | LOW–MEDIUM |
| 2 | torch documented-not-pinned | LOW (mitigated by frozen embeddings) |
| 3 | Windows-specific notes (symlinks, proxy) recorded but no POSIX smoke test yet | LOW–MEDIUM |
| 4 | ECAPA checkpoint hash-pinned and offline — no finding | — |

**Dependency audit: PASS** (for Week-1 purposes; pinning is a
recommendation, not a blocker).
