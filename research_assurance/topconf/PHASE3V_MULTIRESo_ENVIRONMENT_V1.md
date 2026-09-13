# Phase3V MultiResoModel-Simple environment record

Environment path: `F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310`

Bootstrap: Python 3.10.11 from `F:/项目/申请实验室/python.exe`.

The repository requested NumPy 1.21.6, but its available Windows binary was
not compatible with the selected SciPy/scikit-learn wheels. The isolated
runtime therefore uses the compatibility set below; this is a dependency/API
compatibility adjustment only.

```text
pip==23.3.2
setuptools==69.5.1
torch==1.13.1+cu117
torchaudio==0.13.1+cu117
fairseq==0.12.2
librosa==0.9.1
numpy==1.23.5
scipy==1.9.3
scikit-learn==1.1.3
numba==0.56.4
llvmlite==0.39.1
soundfile==0.11.0
audioread==3.0.1
matplotlib==3.5.3
toml==0.10.2
omegaconf==2.0.6
hydra-core==1.0.7
requests==2.34.2
certifi==2026.7.22
urllib3==2.7.0
```

Import check passed for NumPy, SciPy, scikit-learn, numba, librosa, torch,
torchaudio, fairseq; CUDA reported `NVIDIA GeForce RTX 4060 Laptop GPU`.
The existing CFPRF environment was not modified.
