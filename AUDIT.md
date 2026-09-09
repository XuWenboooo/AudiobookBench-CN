# AUDIT.md — Day 1 Project Audit

Date: 2026-09-04  
Project: AudiobookBench-CN  
Priority: Liu Zheli track first; Qin Yong track second.

## 0. Audit Summary

This repository is a useful Week 1 starter scaffold, not yet a research-ready benchmark. The new `src/audiobookbench/` package contains real structural components for manifest loading, audio I/O, fixed-window segmentation, segment replacement, simple anomaly scoring, basic metrics, and bootstrap CI. However, the current repository does **not** yet contain real audio, a real Week 1 manifest, a production VAD, a real F0 extractor, a configured speaker embedding backend, true detection/localization experiments, or formal open-world/adaptive attack evaluation.

The `legacy/audiobookbench_landing/` scripts should remain legacy. They contain synthetic simulations, random feature generation, missing scripts, and over-strong claims such as `VALIDATED`; they should not be used as formal evidence for the Liu Zheli security/forensics track or Qin Yong evaluation track.

## 1. Repository Inventory

| Path | Purpose | Status | Decision |
|---|---|---|---|
| `README.md` | High-level project description and Week 1 target. | Accurate as a starter statement; no overclaim detected. | KEEP |
| `THREAT_MODEL.md` | Draft threat-model template. | Useful but incomplete; Day 1 requires a fuller `THREAT_MODEL_v0.md`. | KEEP + EXPAND |
| `DATASET_CARD.md` | Dataset-card template and required manifest fields. | Good schema starter; not filled with real data. | KEEP + EXPAND |
| `DAY1_CODEX_RUNBOOK.md` | Day 1 execution instructions. | Aligned with current task. Mentions `THREAT_MODEL.md`, while user asked for `THREAT_MODEL_v0.md`; both should coexist. | KEEP |
| `pyproject.toml` | Package metadata and setuptools config. | Valid minimal config. Tests require either install or `PYTHONPATH=src`. | KEEP |
| `requirements.txt` | Runtime/test dependencies. | Minimal dependencies listed. No pinned versions. | KEEP + REFINE LATER |
| `configs/week1.yaml` | Week 1 baseline config. | Points to missing `data/manifests/week1_manifest.csv`. | KEEP |
| `docs/*.md` | Historical 8-week plans. | Useful context; not executable source. | KEEP AS DOCS |
| `data/raw/.gitkeep` | Placeholder for raw audio. | No actual data yet. | KEEP |
| `data/natural_control/.gitkeep` | Placeholder for human/natural control audio. | No actual data yet. | KEEP |
| `data/manipulated/.gitkeep` | Placeholder for manipulated audio. | No actual data yet. | KEEP |
| `data/manifests/.gitkeep` | Placeholder for manifests. | No Week 1 manifest yet. | KEEP |
| `results/security/.gitkeep` | Placeholder for security results. | No real results yet. | KEEP |
| `results/evaluation/.gitkeep` | Placeholder for evaluation-track results. | No real results yet. | KEEP |
| `src/audiobookbench/preprocessing/audio_io.py` | Load, write, and resample audio. | Real implementation using `soundfile` and `scipy.signal.resample_poly`. | KEEP |
| `src/audiobookbench/preprocessing/segment.py` | Fixed windows and simple energy VAD. | Fixed windows usable; VAD is explicitly a sanity baseline, not production. | KEEP + REWRITE VAD LATER |
| `src/audiobookbench/features/prosody.py` | Basic energy/ZCR/duration features with placeholder F0/speech-rate fields. | Real energy/ZCR; F0, voiced ratio, speech rate, pause ratio are `NaN` placeholders. | KEEP + REWRITE/EXTEND |
| `src/audiobookbench/evaluators/speaker.py` | Speaker evaluator abstraction and cosine distance. | Correctly refuses formal speaker embeddings until backend configured. | KEEP + ADD BACKENDS |
| `src/audiobookbench/security/manipulation.py` | Segment replacement and segment-level attack labels. | Real minimal manipulation implementation. Needs audio-boundary smoothing and metadata integration later. | KEEP |
| `src/audiobookbench/security/anomaly.py` | Z-score anomaly score. | Real baseline. Not enough for final claims. | KEEP |
| `src/audiobookbench/temporal/trajectory.py` | Delta and trajectory summaries. | Real lightweight utility. Needs more trajectory/failure metrics later. | KEEP |
| `src/audiobookbench/evaluation/metrics.py` | Binary F1 and interval IoU. | Real minimal metrics. Needs AUROC/AUPRC/localization metrics later. | KEEP |
| `src/audiobookbench/statistics/bootstrap.py` | Bootstrap CI. | Real implementation. | KEEP |
| `src/audiobookbench/utils/manifest.py` | Manifest required columns and read/write helpers. | Real implementation. Missing several fields from `DATASET_CARD.md`. | KEEP + ALIGN SCHEMA |
| `experiments/security_track/exp01_week1_baseline/run.py` | Loads manifest and writes summary/preview. | Scaffold only; no feature extraction or detection/localization yet. | REWRITE/EXTEND |
| `experiments/evaluation_track/exp01_natural_control/` | Empty placeholder. | No implementation. | REWRITE |
| `tests/test_manifest.py` | Manifest roundtrip test. | Passes with `PYTHONPATH=src`. | KEEP |
| `tests/test_manipulation.py` | Replacement and overlap-label tests. | Passes with `PYTHONPATH=src`. | KEEP |
| `tests/test_metrics.py` | F1 and IoU tests. | Passes with `PYTHONPATH=src`. | KEEP |
| `legacy/audiobookbench_landing/run_all_optimizations.py` | Old one-click orchestration. | References missing scripts and overclaims generated outputs. | LEGACY |
| `legacy/audiobookbench_landing/build_natural_contrast.py` | Old natural contrast extraction. | Uses lexical heuristics and fallback duplicated handcrafted text. | LEGACY |
| `legacy/audiobookbench_landing/emotion_trajectory_dtw.py` | Old simulated emotion trajectory DTW. | Uses random simulated trajectories and writes `status: VALIDATED`. | LEGACY / DO NOT USE FOR CLAIMS |
| `legacy/audiobookbench_landing/probe_attribution_v3.py` | Old synthetic generator attribution probe. | Uses random prototypes/features and simulated codec perturbations. | LEGACY / DO NOT USE FOR CLAIMS |
| `legacy/audiobookbench_landing/README_使用指南.md` | Old suite readme. | Claims missing modules and Nankai-inspired components that are not present. | LEGACY |
| `__pycache__/`, `.pytest_cache/` | Generated cache files included in zip. | Should not be distributed in final source package. | DELETE-CANDIDATE |

## 2. Real Implementation vs Placeholder / Demo

### Real starter implementations

- `load_audio`, `write_audio`, and `resample_audio` exist.
- Fixed-window segmentation exists.
- Segment replacement with exact start/end seconds exists.
- Segment overlap labels for attack intervals exist.
- Manifest read/write helpers exist.
- Z-score anomaly scoring exists.
- Binary F1 and interval IoU exist.
- Bootstrap CI exists.

### Placeholders or incomplete parts

- No real dataset is included.
- No `data/manifests/week1_manifest.csv` exists.
- `experiments/security_track/exp01_week1_baseline/run.py` only loads manifest and writes a summary; it does not extract features or detect/localize manipulation.
- No production VAD exists; `simple_energy_vad` is only a sanity baseline.
- No real F0 extractor exists; `f0_mean`, `f0_std`, and `pitch_range` are `NaN` placeholders.
- No speech-rate or pause extractor exists; those fields are `NaN` placeholders.
- No speaker embedding backend is configured; `NotConfiguredSpeakerEvaluator` deliberately raises an error.
- No multi-evaluator agreement, uncertainty, calibration, or human-alignment implementation exists.
- No adaptive evasion, attribution, responsibility score, or counterfactual forensics implementation exists.

## 3. Synthetic / Mock / Random / Demo Code

### Legacy scripts

- `legacy/audiobookbench_landing/emotion_trajectory_dtw.py` simulates frame-level emotion trajectories with `np.random.randint` and `np.random.normal`, then writes `status: VALIDATED`. This is not real validation.
- `legacy/audiobookbench_landing/probe_attribution_v3.py` generates random class prototypes, random text biases, random train/holdout features, and random codec perturbations. It is a simulation, not real TTS generator attribution.
- `legacy/audiobookbench_landing/build_natural_contrast.py` can fall back to duplicated handcrafted sentences if source text is missing. This can be useful for smoke tests but not for formal data claims.

### Current `src/` package

- Current unit tests use tiny synthetic arrays. This is acceptable for tests and does not constitute research evidence.
- `bootstrap.py` uses random resampling with a fixed seed; this is valid statistical computation, not fake data.

## 4. README / Code Mismatch

| Claim / expectation | Current support | Assessment |
|---|---|---|
| Week 1 target includes controlled localized manipulation. | `replace_segment` exists, but no end-to-end dataset generation script yet. | Partially supported. |
| Week 1 target includes temporal feature extraction. | Basic prosody placeholder and trajectory utilities exist. | Partially supported. |
| Week 1 target includes segment-level anomaly score. | `zscore_anomaly` exists, but baseline run does not compute it from features. | Partially supported. |
| Week 1 deliverable includes `results/security/week1/segment_scores.csv`. | Current baseline writes only `metrics.json` and `manifest_preview.csv`. | Mismatch. |
| `DATASET_CARD.md` requires `generator_family`, `attack_generator`, `replacement_speaker`. | `REQUIRED_COLUMNS` in `manifest.py` does not include these fields. | Schema mismatch. |
| `DAY1_CODEX_RUNBOOK.md` asks for `THREAT_MODEL.md`; current user workflow asks for `THREAT_MODEL_v0.md`. | Existing `THREAT_MODEL.md` is a template. | Need v0 copy/expansion. |

## 5. Missing Imports / Scripts / Dependencies

### Import/package issue

Running `python -m pytest -q` from repository root failed with:

```text
ModuleNotFoundError: No module named 'audiobookbench'
```

The tests pass when using:

```bash
PYTHONPATH=src python -m pytest -q
```

Result:

```text
5 passed
```

Day 2 should add one of the following:

- editable install instruction: `pip install -e .`; or
- pytest config with `pythonpath = ["src"]`; or
- a `conftest.py` path setup, though packaging config is cleaner.

### Missing scripts

- No script creates `data/manifests/week1_manifest.csv`.
- No script builds clean/manipulated pairs from real audio.
- No script extracts temporal features per segment.
- No script computes segment-level anomaly scores against attack labels.
- No script generates the required Week 1 timeline figure.
- `legacy/run_all_optimizations.py` references missing legacy scripts:
  - `f0_vad_calibrator.py`
  - `speaker_drift_evaluator.py`
  - `nankai_prosody_engine.py`
  - `latex_table_formatter.py`

### Dependency notes

- `soundfile` may require system-level `libsndfile` depending on platform.
- `scikit-learn` is listed but currently not used by baseline code.
- No speaker model dependency is configured.
- No robust F0/VAD backend dependency is configured.

## 6. Hard-coded Results / Fake Validation / Overclaims

- Current `src/` package does not appear to hard-code research results.
- `experiments/security_track/exp01_week1_baseline/run.py` writes a clear note that feature extraction must be added before claiming results.
- Legacy `emotion_trajectory_dtw.py` writes `status: VALIDATED` despite using simulated data. This must not be used in formal claims.
- Legacy README claims an integrated seven-task pipeline and multiple output files, but several scripts are absent. This is an overclaim relative to available code.

## 7. Data Leakage Risks

Current repository does not yet implement train/test splits beyond manifest loading, so leakage is not currently occurring in executable experiments. However, the following risks must be controlled before Week 4:

1. **Clean/manipulated pair leakage**: a clean sample and its manipulated counterpart must not appear across train/test in a way that allows shortcut learning.
2. **Speaker leakage**: if the goal is cross-speaker generalization, the same speaker cannot appear in both train and test.
3. **Text leakage**: if the goal is unseen text, the same text/book/chapter cannot leak into train and test.
4. **Generator leakage**: leave-one-generator-out must be controlled at the generator level, not row level.
5. **Attack-boundary artifact**: bad splicing may create trivial boundary clicks that make localization easy but scientifically meaningless.
6. **Channel shortcut**: if replacement segments have different codec/sample rate/noise floor, detector may learn channel mismatch rather than manipulation.
7. **Random split inside scripts**: all splits must be controlled by manifest fields, not ad hoc `train_test_split` calls.

## 8. Capability Checklist

| Capability | Current support | Notes |
|---|---:|---|
| Real audio loading | Partial | `load_audio` exists; no real audio included. |
| Audio writing | Yes | `write_audio` exists. |
| Resampling | Yes | `resample_audio` exists. |
| VAD | Partial | Simple energy VAD only; sanity baseline. |
| Segmentation | Partial | Fixed windows only; no VAD-aware or sentence-level segmentation. |
| Speaker embedding | No | Interface exists, backend deliberately not configured. |
| Speaker distance | Yes | Cosine and representation distance exist. |
| F0 | No | Placeholder NaN fields only. |
| Energy | Yes | Basic frame-energy features exist. |
| Pause ratio | No | Placeholder NaN field only. |
| Speech rate | No | Placeholder NaN field only. |
| Segment-level metadata | Partial | Manifest schema exists, but no manifest generation. |
| `attack_start` / `attack_end` | Partial | Manipulation record and labels exist; not integrated into generated manifest. |
| Detection | Partial | Z-score utility exists; no end-to-end detector. |
| Localization | Partial | Segment labels and interval IoU exist; no localization pipeline. |
| Unseen-generator protocol | No | Not implemented. |
| Adaptive evasion | No | Reserved for Week 5. |
| Attribution / responsibility | No | Not implemented. |
| Human validation | No | Not implemented. |
| Uncertainty / reject option | No | Not implemented. |

## 9. Module Decisions

### KEEP

- `src/audiobookbench/preprocessing/audio_io.py`
- `src/audiobookbench/preprocessing/segment.py` as a sanity baseline
- `src/audiobookbench/security/manipulation.py`
- `src/audiobookbench/security/anomaly.py`
- `src/audiobookbench/temporal/trajectory.py`
- `src/audiobookbench/evaluation/metrics.py`
- `src/audiobookbench/statistics/bootstrap.py`
- `src/audiobookbench/utils/manifest.py`
- `tests/`
- `configs/week1.yaml`
- root-level planning docs

### REWRITE / EXTEND

- `experiments/security_track/exp01_week1_baseline/run.py`: extend from manifest preview to real feature extraction + segment anomaly + metrics.
- `src/audiobookbench/features/prosody.py`: add real F0, voiced ratio, pause ratio, and speech-rate extraction.
- `src/audiobookbench/preprocessing/segment.py`: add VAD-aware segmentation and audio slicing helpers.
- `src/audiobookbench/utils/manifest.py`: align required columns with `DATASET_CARD.md`.
- Add scripts for dataset preparation, manipulation generation, feature extraction, and figure generation.

### LEGACY

- Entire `legacy/audiobookbench_landing/` directory.

### DELETE-CANDIDATE

- `__pycache__/`
- `.pytest_cache/`
- any future generated results that are not reproducible from config + manifest.

## 10. Day 2 Recommended Actions

1. Add packaging/test configuration so `python -m pytest` works without manually setting `PYTHONPATH`.
2. Align manifest schema with `DATASET_CARD.md`.
3. Add `src/audiobookbench/preprocessing/slicing.py` or equivalent helper to cut audio by segment intervals.
4. Add `src/audiobookbench/security/dataset.py` to create clean/manipulated pairs and write attack metadata.
5. Extend Week 1 experiment script to:
   - read real audio;
   - segment audio;
   - compute basic energy/ZCR features;
   - compute segment labels from `attack_start`/`attack_end`;
   - compute anomaly scores;
   - write `segment_scores.csv` and `metrics.json`.
6. Add tests for manifest schema, attack metadata integrity, and segment-time alignment.
7. Do not add adaptive attacks, attribution, or large models on Day 2.

## 11. Day 1 Completion Status

Day 1 audit is complete.

Created/updated by this audit:

- `AUDIT.md`
- `THREAT_MODEL_v0.md`

Main risks:

1. No real audio or Week 1 manifest exists yet.
2. F0, pause ratio, speech rate, and speaker embedding are placeholders or unconfigured.
3. Current baseline does not yet perform detection/localization.
4. Legacy scripts contain random simulations and overclaims; they must remain legacy.
5. Tests require `PYTHONPATH=src` unless package is installed or pytest config is added.
