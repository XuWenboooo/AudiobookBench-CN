# Compute and Reproducibility Readiness v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Inspection date: **2026-09-13**
Inspection scope: host metadata and tool availability only; no scientific run.

## Observed host

| Field | Observation | Readiness interpretation |
|---|---|---|
| OS | Windows 11 Home Chinese, 64-bit, build `10.0.26200` | Native Windows workflow available. |
| CPU | Intel Core Ultra 9 185H, 16 cores / 22 logical processors | Suitable for metadata, schema, synthetic simulation, and small CPU checks. |
| RAM | 33,733,144,576 bytes (~31.4 GiB) | Adequate for tooling; large model/data loads remain workload-dependent. |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 8,188 MiB reported, driver 610.62 | Hardware exists. |
| CUDA toolkit / PyTorch | Python 3.12.9; `torch 2.14.0+cpu`; `torch.cuda.is_available() = False`; `torch.version.cuda = None` | Current Python environment cannot use the GPU through PyTorch. Full reproduction is not ready. |
| `nvidia-smi` | `C:\Windows\System32\nvidia-smi.exe` | Driver is visible to the host. |
| Disk F: | 308,374,663,168 bytes total; 170,055,913,472 bytes free (~158.4 GiB) | Enough for small artifacts; not a guarantee for full datasets/checkpoints. |
| WSL | `wsl --status` returned installation/help text rather than a verified distro/runtime status | WSL availability is **NOT_VERIFIED**; do not assume Linux compatibility. |
| Docker | `docker` command not found | Docker tier unavailable on this host. |

The CPU and disk values were obtained with read-only Windows system queries.
No cloud resource, paid resource, private-data upload, dataset download, or
checkpoint download was performed.

## Candidate compute tiers

| Tier | Examples | Current status |
|---|---|---|
| `CPU_ONLY_TASKS` | Documentation, manifests, validators, unit tests, synthetic statistics, hashes | READY |
| `SMALL_GPU_TASKS` | Load-only checkpoint checks, tiny synthetic tensor smoke tests | BLOCKED in current Python because PyTorch is CPU-only; host GPU exists |
| `FULL_REPRODUCTION_GPU_TASKS` | External model reproduction and cross-dataset output materialization | NOT READY; requires CUDA-enabled environment, exact dependencies, checkpoints, and rights |
| `CONFIRMATORY_GENERATION_GPU_TASKS` | Level-2 generation or confirmatory inference | NOT AUTHORIZED and additionally not ready on this environment |

## Reproducibility requirements still open

- Pin a supported Python/PyTorch/CUDA combination per external model rather than
  overwriting the current environment.
- Preserve exact repository commits and checkpoint SHA256 values.
- Verify Windows versus WSL/Linux path, audio codec, and multiprocessing behavior.
- Record peak VRAM/RAM, disk footprint, command lines, stdout/stderr, and seed
  after an authorized load-only test.
- Keep third-party checkpoints and datasets outside the Git-tracked artifact
  namespace unless redistribution is explicitly allowed.
