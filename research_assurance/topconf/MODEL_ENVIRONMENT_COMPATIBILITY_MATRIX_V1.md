# Model and Environment Compatibility Matrix v1

Status: **INITIAL PHASE 3S AUDIT**

| Model / path | Official identity | Python / runtime evidence | GPU status | Checkpoint / rights | Phase 3S disposition |
|---|---|---|---|---|---|
| CFPRF | official repo `358a901ead8a7d84dac979c3d626e34ef82c2854` | source README recommends Python 3.8+, NumPy 1.23.5, PyTorch 1.8.1+cu111; existing Python 3.10 CPU fairseq path imports | new isolated CUDA path pending | FDN/PRN/XLSR hashes verified; MIT code | primary GPU environment candidate |
| PartialSpoof MultiReso | official repo `847347aaec6f65c3c6d2f17c63515b826b94feb3` | official script/source route audited; runtime load not reached | pending | official Zenodo 6674660 route; one bounded curl returned HTTP 504/0 bytes | not materialized; remains conditional |
| SAL | official repo `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | Python 3.10/Lightning/Hydra documented in prior audit | not evaluated | no official checkpoint found | deferred |
| BAM | official repo `55f3fb9e3b4dd6281597b86d7712fb23454179f6` / current rights audit | README path inspected | not evaluated | repository license unresolved; no release asset | blocked rights |
| TRACE | official paper reviewed; matching runnable audio artifact unverified | unknown | unknown | provenance/checkpoint unresolved | stretch only; no implementation |

## Compatibility rules

The CFPRF row is a compatibility target, not a claim of successful Phase 3S
execution. Exact installed versions, `pip freeze`, CUDA smoke, fairseq import,
and XLSR load must be appended from the isolated environment's command output.
No result or reported score may influence a candidate's inclusion.

## Append-only Phase3V compatibility result

| Model / path | Official identity | Python / runtime evidence | GPU status | Checkpoint / rights | Phase3V disposition |
|---|---|---|---|---|---|
| MultiResoModel-Simple | author repository `0f69db3a2d654de47822d951fe6ad256bbaac9ba`; unofficial reimplementation | isolated Python 3.10.11; torch 1.13.1+cu117; torchaudio 0.13.1+cu117; fairseq 0.12.2; compatibility NumPy 1.23.5/SciPy 1.9.3/scikit-learn 1.1.3/numba 0.56.4 | RTX 4060 Laptop GPU; strict load and 3-sample finite forward pass | HF revision and SHA256 recorded in `PHASE3V_CHECKPOINT_MANIFEST_V1.json`; root MIT | `FUNCTIONAL_BASELINE_PATH_PASS; PHASE3T_REVIEW_ONLY` |

## Append-only Phase3S result

PartialEdit v1.1 E1 now has a verified full-audio materialization and parser
pass. MultiReso was not materialized after its single authorized official
transport returned HTTP 504. Therefore the matrix still exposes only one
verified external baseline path (CFPRF infrastructure-only); no replacement
baseline was selected.
