# Day 8 A2 readiness report

Date: 2026-09-06  
Status: **PASS**

## Scope and outcome

This is a Day 8 readiness check only.  No formal 23-case A2 generation, Day 9
official smoke, A2 metric, detector training, case selection, or dataset write
was performed.  AISHELL-3 remained read-only.

The local Windows environment and the non-TTS readiness layer are usable.  The
official checkpoint is complete and its manifest is verified.  Local and
true-offline model initialization passed after minimal Windows-only loader
compatibility work.  The final CPU-only closure for frozen `paircase_0007`
completed whole-utterance generation, construction, serialization, sidecar
write, and independent mechanical QA.  Day 8 passes; no later-stage work was
entered.

## Upstream requirements versus the Windows/Python 3.12 overlay

| Item | Upstream / protocol requirement | This host's result |
| --- | --- | --- |
| Source | `FunAudioLLM/CosyVoice`, code recorded by the overlay as revision `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc` | `third_party/CosyVoice` is present.  It has no `.git` metadata, so the recorded revision cannot be independently re-derived from this checkout. |
| Code licence | CosyVoice source licence | `third_party/CosyVoice/LICENSE` is Apache-2.0. |
| Checkpoint | Official Hugging Face repository `https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B`, immutable revision `eec1ae6c79877dbd9379285cf8789c9e0879293d` | The Hub API confirmed the public repository, exact revision, and model-card licence `Apache-2.0`.  The project-controlled destination is `pretrained/cosyvoice2-0.5b/eec1ae6c79877dbd9379285cf8789c9e0879293d/`. |
| Runtime | Upstream requirements plus the repository's documented compatibility overlay | Python 3.12.9, torch 2.3.1+cu121, torchaudio 2.3.1+cu121, speechbrain 1.1.1. |
| Windows compatibility overlay | `requirements-cosyvoice-win312.txt` retains torch/torchaudio 2.3.1 and updates the grpc/protobuf pins for CPython 3.12 | Installed and importable.  A small CPU-only SpeechBrain/torch-2.3 AMP compatibility bridge was added in `day6b_embed.py`; it does not alter TTS, data, frozen waveforms, or scientific outputs. |
| Hardware | CUDA-capable inference host | CUDA available: NVIDIA GeForce RTX 4060 Laptop GPU. |

## Review and checkpoint-acquisition record

- Third-party review: PASS; Week2A registry track:
  `INDEPENDENTLY_VERIFIED_CLOSED` (checker 123/123; registry 29/29).
- Before acquisition, the offline reload correctly failed with `RuntimeError:
  local checkpoint absent`; no network access was attempted in that test.
- On 2026-09-06T02:19:41Z, the authorized acquisition used only the official
  Hugging Face source at the frozen revision and only the Day 8 inference
  assets: `CosyVoice-BlankEN/*`, `campplus.onnx`, `cosyvoice2.yaml`, `flow.pt`,
  `hift.pt`, `llm.pt`, and `speech_tokenizer_v2.onnx`.
- Eleven of twelve required assets completed in the project destination.  The
  required `llm.pt` normal HTTPS transfer terminated with `IncompleteRead` after
  71,444,480 bytes of the advertised 2,023,316,821-byte file.  A subsequent
  official Hugging Face Xet retry made no data progress and was stopped.  No
  mirror, repack, or alternative model was used.
- Diagnosis found a WinINET proxy / direct-socket split.  Using the existing
  explicit local proxy, the official Hugging Face exact-revision URL recovered
  **only** `llm.pt` with resume support; no existing asset was deleted or
  re-fetched.  The final file is 2,023,316,821 bytes and SHA-256 is
  `b144ef55b51ce8cfb79a73c90dbba0bdaba4e451c0ebcfab20f769264f84a608`.
- `results/day8/checkpoint_hashes.json` records the complete 12/12 official
  asset set and hashes.  Its recorded SHA is the full canonical value above;
  the earlier shortened display typo was not present in the manifest or this
  report, so no record correction was needed.

## Regression and integrity evidence

- Initial full pytest failures were:
  - `tests/test_day6b_speaker.py::test_embeddings_are_finite_and_dimension_is_fixed`
  - `tests/test_day6b_speaker.py::test_repeated_input_is_stable`
- Both had the same environment-compatibility root cause: SpeechBrain 1.1.1
  calls `torch.amp.custom_fwd(..., device_type="cpu")`, which torch 2.3.1 does
  not expose.  The Day 6B backend is CPU inference with autocast disabled; the
  compatibility bridge preserves that no-autocast behavior and delegates CUDA
  calls to torch's native legacy decorator.
- Re-running those two tests: PASS (2/2).
- Full regression after the minimal compatibility fix: PASS (188 passed, 1
  skipped; 12 non-failing third-party warnings).
- Fresh Week 1 verification: PASS — checked 696, missing 0, mismatches 0.

## Loader, offline reload, and disposable smoke

- A Step-0 review of `experiments/day8_a2_readiness/smoke.py` found no
  scientific or protocol-semantic change: it retains whole-utterance
  replacement, submitted raw exact strings with `text_frontend=False`, the
  frozen voice reference, natural generated duration (no stretch/crop/pad),
  16-kHz mono serialization, 400-sample crossfade, dual timelines,
  sample-first ground truth, and `smoke_only=true`.
- Initial local loader diagnostics exposed only infrastructure issues: missing
  `openai-whisper==20231117`, a local Matcha-TTS submodule absent from
  `PYTHONPATH`, and HyperPyYAML collapsing the canonical Windows workspace's
  double space.  The first was installed at the upstream fixed version (without
  rebuilding the venv or changing torch); Matcha-TTS was exposed from the
  already checked-in CosyVoice source; a temporary `R:` mapping avoided the
  Windows path parsing defect and was removed afterwards.
- A local `AutoModel` probe then passed from the frozen local source,
  `R:\\third_party\\CosyVoice`, and local checkpoint,
  `R:\\pretrained\\cosyvoice2-0.5b\\eec1ae6c79877dbd9379285cf8789c9e0879293d`, on
  the NVIDIA GeForce RTX 4060 Laptop GPU.  The GPU could not complete a fresh
  full load on its 8-GB memory (CUDA OOM), so the true offline and disposable
  runs were explicitly CPU-only; no model, source revision, or generation
  setting changed.
- `smoke.py` received only loader/provenance safeguards: the checked-in Matcha
  path is added, `.cache` temporary files are excluded from checkpoint hashing,
  and the unused optional WeText normalizer is disabled before local-only model
  construction.  Frozen smoke calls use `text_frontend=False`, so this cannot
  alter submitted text behavior; it prevents WeText from attempting its separate
  ModelScope asset.
- True offline reload command: `CUDA_VISIBLE_DEVICES=''`, `HF_HUB_OFFLINE=1`,
  `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_XET=1`, and
  `MODELSCOPE_OFFLINE=1`, followed by
  `python experiments/day8_a2_readiness/smoke.py --offline-load-only` from the
  temporary mapped local path.  Result: **PASS**; sample rate 24,000; the audit
  at `results/day8/offline_cache_audit.json` records local-only initialization
  and no permitted network fetch.
- The first CPU-only disposable wrapper for frozen `paircase_0007` exited after
  model initialization without a Python traceback.  Windows Error Reporting
  recorded `APPCRASH` in `c10.dll`, exception `0xc0000005`; no artifact was
  emitted by that failed attempt.
- The authorized final CPU closure then ran the same frozen `paircase_0007`,
  same transcript, target reference, seed, source, model, checkpoint, and
  offline settings.  It emitted
  `results/day8/smoke/paircase_0007_smoke.wav`, `smoke_manifest.csv`, waveform
  verification, output hash, summary, and determinism audit.  The wrapper used
  the already captured two-run CPU bit-identical result rather than generating a
  further redundant raw waveform for determinism alone.
- Final mechanical QA PASS: the WAV is readable, finite, mono, 16 kHz,
  non-empty, and unclipped (peak 0.4455872); its canonical SHA-256 is
  `456144C10EBA4377561812AD88BA9E5822DFCD0DB3E2CC404C5EC6F13D04B5B1`.
  `validate_a2_sidecar_row` passes.  Exact source/tts string and hashes match
  frozen `paircase_0007`; reference sample, target speaker, checkpoint
  manifest, and `smoke_only=true` match lineage records.  Sample-first GT and
  derived durations pass.  Attack `[217285, 252085)`, strict core
  `[217685, 251685)`, and both 400-sample blend intervals pass.  After PCM16
  roundtrip, prefix and suffix mapping errors are both 0.0.  The smoke code has
  no detector invocation; the detector denylist safe-payload audit passes, so
  no attack-side reference or speaker information enters detector-facing input.

## Scientific limitation retained

AISHELL-3 training-data independence remains **UNKNOWN**.  No evidence was
obtained that the candidate generator was trained independently of AISHELL-3;
this report makes no PASS claim about that condition.

## Native `c10.dll` crash isolation

- The original one-case disposable smoke command was CPU-only and local-only:
  from the temporary `R:` mapping it set `CUDA_VISIBLE_DEVICES=''`,
  `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_XET=1`, and
  `MODELSCOPE_OFFLINE=1`, then ran
  `python experiments/day8_a2_readiness/smoke.py` for frozen `paircase_0007`.
  Windows Error Reporting recorded two `python.exe` APPCRASH records for
  `c10.dll`, exception `0xc0000005`; the protected WER minidump was not
  readable without installing a debugger.
- Preservation record: Python 3.12.9; torch 2.3.1+cu121; torchaudio
  2.3.1+cu121; `torch.version.cuda` 12.1; speechbrain 1.1.1; GPU NVIDIA GeForce
  RTX 4060 Laptop GPU; driver 610.62; recorded CosyVoice source revision
  `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`; checkpoint revision
  `eec1ae6c79877dbd9379285cf8789c9e0879293d`.
- `python -m torch.utils.collect_env` was captured.  Small deterministic CPU
  tensor operations PASS.  Small CUDA allocation, transfer, matrix multiply,
  synchronization, and return-to-CPU operations PASS with
  `CUDA_LAUNCH_BLOCKING=1`.  The full GPU CosyVoice path cannot currently load
  within the 8-GB card (CUDA OOM during weight loading), so no GPU paircase
  inference was run.
- Read-only ABI/DLL checks found the active Python, torch, and torchaudio under
  `.venv-cosyvoice`; `c10.dll`, `torch_cpu.dll`, and `torch_cuda.dll` are in
  that venv's `torch\\lib`.  PATH contains the base Python location but no torch
  or CUDA runtime directory, and the installed Microsoft VC++ x64 runtime is
  14.51.36247.  No duplicate-torch or PATH conflict was identified.
- A CPU-only, network-disabled diagnostic with `PYTHONFAULTHANDLER=1` used the
  same `paircase_0007`, frozen transcript/reference, and generation seed.  It
  reached and passed all staged points: model load, exact-text preparation,
  prompt/speaker processing, TTS generator creation, and first waveform chunk.
  Two complete raw generations each returned 76,800 finite samples and were
  bit-identical (`max_abs=0.0`).  It wrote no waveform, sidecar, or formal A2
  artifact.  Thus the prior native failure was not reproduced in controlled CPU
  inference and is not localized to text, prompt, LLM, flow, or vocoder core
  execution.
- The pinned source README specifies Python 3.10.  This host has Python 3.12
  and 3.14 only, and has no `uv` runtime manager; no separate Python 3.10
  environment was created or altered.  The upstream-like runtime A/B is
  therefore NOT RUN, rather than guessed or substituted with a different
  runtime.

## Release decision

**DAY8 = PASS.**  Checkpoint provenance (12/12 and complete hash manifest),
local loader, true offline reload, the frozen CPU full-wrapper smoke, exact
text, waveform/GT/dual-timeline QA, prefix/suffix mapping, and detector
separation all pass without a protocol-semantic change.  GPU full-model
inference remains infeasible on the 8-GB card (CUDA OOM), and the earlier
`c10.dll` event remains NON_REPRODUCED with unknown root cause; these are
recorded limitations, not Day 8 blockers for the verified CPU path.  AISHELL-3
training independence remains UNKNOWN.  Day 9 is not entered; no A2 metrics or
scientific claims were added.
