# GPU Reproduction Environment v1

Status: **PENDING — ISOLATED ENVIRONMENT NOT YET CREATED**

This manifest is append-only. It records the Phase 3S environment separately
from the existing primary Python 3.12 environment.

## Authorized target

```text
ENVIRONMENT_NAME = topconf-phase3s-cfprf-py310
ENVIRONMENT_PATH = F:\\项目\\申请实验室  TTS项目\\envs\\topconf-phase3s-cfprf-py310
PYTHON_BOOTSTRAP = F:\\项目\\申请实验室\\python.exe
PYTHON_TARGET = 3.10.11
PYTORCH_TARGET = 2.2.2+cu121 candidate (official PyTorch CUDA wheel index)
FAIRSEQ_SOURCE = F:\\项目\\申请实验室  TTS项目\\topconf_phase3_cache\\fairseq-a54021305d6b3c4c5959ac9395135f63202db8f1
FAIRSEQ_IDENTITY = a54021305d6b3c4c5959ac9395135f63202db8f1; source archive SHA256 D70577F2D00E066C2EF14F6519623B90FFACB94E07C56F5406BA425C2BF8A85A
CFPRF_SOURCE = official CFPRF commit 358a901ead8a7d84dac979c3d626e34ef82c2854
```

## Initial status

```text
OS = Windows (native)
GPU = NVIDIA GeForce RTX 4060 Laptop GPU (known visible before Phase3S)
GPU_VRAM = 8188 MiB reported
DRIVER = 610.62 reported
CUDA = 12.1 reported by existing primary environment
SYSTEM_PYTHON_CHANGED = NO
PRIMARY_ENVIRONMENT_CHANGED = NO
GPU_ENVIRONMENT_SMOKE = NOT_RUN
FAIRSEQ_IMPORT = NOT_RUN_IN_PHASE3S_ENVIRONMENT
XLSR_CHECKPOINT_LOAD = NOT_RUN_IN_PHASE3S_ENVIRONMENT
PIP_FREEZE = PENDING_ENVIRONMENT_CREATION
```

No model inference is authorized from this manifest until the environment is
created, its complete dependency manifest is captured, and the Phase 3S
authorization remains applicable.

## Append-only execution record

Recorded after isolated environment creation on `2026-09-13`:

```text
ENVIRONMENT_CREATION = PASS
SYSTEM_PYTHON_CHANGED = NO
PRIMARY_ENVIRONMENT_CHANGED = NO
LEGACY_PYTHON = 3.10.11
PYTORCH_VERSION = 2.2.2+cu121
TORCHAUDIO_VERSION = 2.2.2+cu121
TORCHVISION_VERSION = 0.17.2+cu121
NUMPY_VERSION = 1.23.5
FAIRSEQ_VERSION = 1.0.0a0 (editable source)
HYDRA_VERSION = 1.0.7
OMEGACONF_VERSION = 2.0.6

GPU = NVIDIA GeForce RTX 4060 Laptop GPU
GPU_VRAM = 8585216000 bytes reported by PyTorch (8188 MiB class)
CUDA = 12.1
CUDA_VISIBLE = YES
CUDA_TENSOR_ALLOCATION = PASS
CUDA_SMALL_MATMUL = PASS (4x4, finite, sum 64.0)
FAIRSEQ_IMPORT = PASS
XLSR_CHECKPOINT_LOAD = PASS (317390592 parameters, moved to cuda:0)
CFPRF_FDN_CHECKPOINT_LOAD = PASS (0 missing, 0 unexpected, cuda:0)
CFPRF_PRN_CHECKPOINT_LOAD = PASS (0 missing, 0 unexpected, cuda:0)
CFPRF_LOAD_PEAK_ALLOCATED = 2566092800 bytes
GPU_AUDIO_SMOKE = VALIDLY_DEFERRED_NO_FULL_AUDIO_DATASET
PIP_FREEZE = PHASE3S_GPU_PIP_FREEZE_V1.txt
```

The checkpoint checks were load-only. No audio forward, metric, ranking, or
scientific outcome was produced.
