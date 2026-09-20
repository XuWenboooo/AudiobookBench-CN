# Segment-Aware Learning (SAL) for Localizing Speech Deepfakes

## 📌 Introduction

This is the **official implementation** of [our paper](https://arxiv.org/abs/2601.21925):

```bibtex
Localizing Speech Deepfakes Beyond Transitions via Segment-Aware Learning
Yuchen Mao, Wen Huang, Yanmin Qian
Accepted by ICASSP 2026
```

---

### 🔍 Motivation

Detecting **partially spoofed speech** is highly challenging:  
- Existing approaches often rely on **transition artifacts** at real-fake boundaries.  
- These models **overfit to transitions**, ignoring **intrinsic segment content**.  

**SAL** addresses this by explicitly modeling **frame-level information within segments** rather than only their boundaries.

---

### 🛠️ Key Contributions

- **Segment Positional Labeling (SPL):**  
  Fine-grained supervision that encodes **relative frame positions** within segments (Start, Middle, End, Unit).

- **Cross-Segment Mixing (CSM):**  
  A data augmentation strategy that generates diverse segment combinations, **breaking shortcut reliance** on transitions.

- **Consistent performance gains** across multiple benchmarks:  
  PartialSpoof (PS), Half-truth Audio Detection (HAD), and LlamaPartialSpoof (LPS).

---

## ⚙️ Installation

```bash
conda create -n sal python=3.10 -y
conda activate sal
pip install -r requirements.txt
````

Dependencies:

* `lightning` (PyTorch Lightning 2.x)
* `hydra` for configuration management
* See `requirements.txt` for the full list.

---

## 📂 Project Structure

```
src/
  data/               # Dataset interfaces and loaders
  evaluator/          # Evaluators and metrics
  models/             # Model definitions and feature extraction
  trainers/           # Training utilities
  utils/              # Common utilities & wrappers
  train.py            # Training entry point
  eval.py             # Evaluation entry point
configs/              # Hydra configs (model, data, trainer, experiments)
scripts/              # Visualization & analysis scripts
```

---

## 📊 Data Preparation

* **Primary dataset:** [PartialSpoof (PS)](https://github.com/nii-yamagishilab/PartialSpoof)
* **Additional datasets:** [HAD](https://zenodo.org/records/10377492), [LlamaPartialSpoof (LPS)](https://github.com/hieuthi/LlamaPartialSpoof)

Notes:

1. Labels stored as `.npy` dictionaries keyed by `utt id`.
2. Default resolution: **160 ms**.

   * Training: \~4s segments
   * Testing: full utterances
3. Modify dataset paths in `configs/data/`.

---

## 🚀 Training

Minimal run:

```bash
python src/train.py
```

With a specific experiment:

```bash
python src/train.py experiment=SAL_WavLM_HAD
```

Hydra overrides:

* `data=...` → select dataset
* `model=...` → switch model configs
* `trainer.*` → set Lightning params (devices, precision, logging, etc.)

---

## 🧪 Evaluation

Evaluate a trained checkpoint:

```bash
python src/eval.py data=partialspoof model=SAL_WavLM \
  ckpt_path=/your/path/to/checkpoint.ckpt
```

Metrics:

* **Equal Error Rate (EER, ↓)**
* **F1-score (↑)**

---

## 🎨 Visualization

### Grad-CAM Visualization

Use the Grad-CAM visualization script:
```bash
python scripts/visualize/gradcam.py \
    --audio_path /path/to/audio.wav \
    --labels_path /path/to/labels.npy \
    --sample_id your_sample_id \
    --ckpt /path/to/xlsr2_300m.pt \
    --model_ckpt /path/to/model_checkpoints/last.ckpt \
    --model_type your_model_type(ssl_seq or ssl_seq_8labels_2loss) \
    --ssl_mode your_ssl_mode(s3prl or s3prl_weighted) \
    --device cuda \
    --output_path /path/to/your_output_path.png \
    --show
```

### Part Error Analysis

```bash
python scripts/visualize/part_error.py \
  --file /path/to/sal/result.txt \
  --out plots/pair_error_rates.png
```


## 📈 Results

| Train / Test |     PS → PS      |    HAD → HAD     |     PS → LPS     |
| :--- |:----------------:|:----------------:|:----------------:|
| **System (Front-end)** | **EER ↓ / F1 ↑** | **EER ↓ / F1 ↑** | **EER ↓ / F1 ↑** |
| SAL (W2V2-XLSR) |   3.32 / 96.84   |   0.05 / 99.99   |  35.52 / 55.30   |
| SAL (WavLM) |   3.00 / 97.09   |   0.05 / 99.99   |   36.60 /56.09   |


## 📝 Cite
If you find this work useful in your research, please consider citing:

```bibtex
@inproceedings{mao2026localizing,
  title={Localizing Speech Deepfakes Beyond Transitions via Segment-Aware Learning},
  author={Mao, Yuchen and Huang, Wen and Qian, Yanmin},
  booktitle={ICASSP 2026 - 2026 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  year={2026},
  organization={IEEE},
}
```

## 🙏 Acknowledgments

We gratefully acknowledge the following open-source projects and prior works that this repository builds upon:

- **RawBoost**: Original RawBoost project for anti-spoofing: https://github.com/TakHemlata/RawBoost-antispoofing
- **BAM**: Base dataset reference: https://github.com/media-sec-lab/BAM/tree/master
- **Lightning-Hydra-Template**: Original PyTorch Lightning + Hydra project template: https://github.com/ashleve/lightning-hydra-template
