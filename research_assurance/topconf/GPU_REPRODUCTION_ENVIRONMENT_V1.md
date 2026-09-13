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
