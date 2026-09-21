# SAL frozen checkpoint identity v1

Audit date: `2026-09-21`
Scope: checkpoint identity recovery only. This record contains no W7 case,
audio, prediction, metric, or Level-2 outcome.

```text
SAL_CHECKPOINT_ADJUDICATION = HISTORICAL_EXACT_ARTIFACT_RECOVERED_COPY_ONLY
SAL_CHECKPOINT_IDENTITY = PASS
EXPECTED_BYTES = 4037013806
EXPECTED_SHA256 = FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F
CURRENT_BYTES = 4037013806
CURRENT_SHA256 = FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F
HASH_MATCH = YES
SCIENTIFIC_INFERENCE = NO
```

## Identity chain

| Field | Bound value |
| --- | --- |
| official source repository | `https://github.com/SentryMao/SAL` at `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` |
| official checkpoint location | `https://huggingface.co/MaoYC/SAL/resolve/d9ab313d86a8b00a6345419721389d8b4eabe992/SAL_WavLM.ckpt` |
| checkpoint name | `SAL_WavLM.ckpt` |
| frozen identity | 4,037,013,806 bytes; SHA-256 `FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F` |
| historical candidate | `.../w6_recovery/artifacts/SAL_WavLM.ckpt.part`; it had the exact frozen size and SHA-256 despite the incomplete-name suffix |
| recovery action | copy-only to `G:/AudiobookBench-CN/external_data/topconf_phase3_cache/checkpoints/SAL/SAL_WavLM.ckpt`; no download, conversion, or overwrite |
| current logical path | `F:/项目/申请实验室  TTS项目/topconf_phase3_cache/checkpoints/SAL/SAL_WavLM.ckpt` (the migrated F-path resolves to the controlled G cache) |

The historical `SAL_STRICT_LOAD_SMOKE_EVIDENCE_V1.md` records strict matching
of this same SHA-256 through the official SAL model and a zero-waveform
synthetic smoke. The active runtime has PyTorch and fairseq but lacks the
source-required `s3prl==0.4.18`; therefore this audit does **not** relabel a
partial WavLM-wrapper attempt as a new complete SAL strict-load result. The
exact byte identity makes the prior strict-load evidence applicable to the
recovered artifact; it does not create a scientific inference.

## Rejection rule

Any different size or SHA-256 is `FAIL`; a filename match, a Drive/HF link, or
historical prose without this exact digest is insufficient. This recovered
artifact remains subject to the independent W7 rights and mechanism gates.
