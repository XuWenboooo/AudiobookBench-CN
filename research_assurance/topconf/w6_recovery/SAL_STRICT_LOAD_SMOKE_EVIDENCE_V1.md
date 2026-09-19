# SAL strict-load and temporal smoke evidence v1

Audit date: `2026-09-19`

The official SAL source at commit `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485`
was loaded with the official model class and the official HF WavLM checkpoint
at revision `d9ab313d86a8b00a6345419721389d8b4eabe992`.

The HF file is a Lightning checkpoint containing the full upstream WavLM
state. A deterministic wrapper was generated only to place those unchanged
embedded tensors in the fairseq container expected by the official s3prl
loader. The embedded WavLM state matched the official s3prl WavLM-Large
implementation with `strict=True`; the complete SAL network then matched the
official checkpoint state dictionary with `strict=True`.

```text
OFFICIAL_SAL_SOURCE_SHA256 = 30504CF6B3B95C5062FE2DD1D6DDC0F605376E744E25B42E201F752D4033B22A
OFFICIAL_SAL_WAVLM_SIZE = 4037013806
OFFICIAL_SAL_WAVLM_SHA256 = FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F
SAL_STRICT_LOAD = PASS
SAL_SYNTHETIC_INPUT = B=1, 16000 samples, 16 kHz
SAL_OUTPUT_SHAPES = (1, 6, 8), (1, 6, 2)
SAL_OUTPUT_FINITE = PASS
SAL_TEMPORAL_OUTPUT = PASS
SCIENTIFIC_INFERENCE = NO
OUTCOME_GUIDED_SELECTION = NO
```

The official W2V2 checkpoint remains separately unverified and is not used for
the qualification decision. The WavLM checkpoint is sufficient to identify
one SAL localizer instance and one segment-aware localization paradigm.
