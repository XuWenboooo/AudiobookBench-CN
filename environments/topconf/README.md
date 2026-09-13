# TopConf Reproducibility Environment Templates

Status: **TEMPLATE ONLY / NON-AUTHORIZING**

These files describe a future environment without changing or replacing the
current host environment. They are not a Phase 4 authorization and do not
download packages, checkpoints, or data.

The host audit found a CPU-only PyTorch build despite an NVIDIA RTX 4060 Laptop
GPU. A future reproduction environment must be created separately, tested with
a load-only smoke test, and pinned to the exact external model requirements.

Use a project-specific environment name and keep model-specific legacy stacks
isolated. Do not use this template to run a confirmatory dataset.
