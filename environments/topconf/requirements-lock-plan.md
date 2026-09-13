# Requirements lock plan

Status: **TBD_BEFORE_AUTHORIZATION / TEMPLATE ONLY**

1. Record the selected model repository commit and checkpoint SHA256.
2. Export a clean environment specification without modifying the existing
   project environment.
3. Pin Python, PyTorch, CUDA, torchaudio/fairseq/Lightning/Hydra versions only
   after reading the selected model's official instructions.
4. Run import and load-only tests on synthetic audio, recording hardware and
   software metadata. Do not run a real research dataset during this check.
5. Capture a lockfile plus hashes for all project scripts, configuration,
   manifests, and reports.
6. Re-run the same test on the declared execution host before human approval.

The current host cannot provide a CUDA-enabled PyTorch smoke test because its
installed torch package is `2.14.0+cpu`.
