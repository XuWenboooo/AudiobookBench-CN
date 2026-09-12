# Week4 prospective execution supplement v1

Status: `SUPPLEMENT_STATUS = FROZEN_BEFORE_ANY_WEEK4_SCIENTIFIC_OUTCOME`  
Protocol: the original Week4 preregistration plus this supplement are the sole
canonical scientific protocol for Week4 v0.  This document changes neither H4,
the 48-case population, the 24/12/12 splits, A_STATIC/A0, attack bounds, the
40-query budget, the 8x5 search, nor the bootstrap.

`REAL_F5_GENERATION = NOT STARTED`; `REAL_D0_QUERY = NOT STARTED`;
`H4_RESULT_OBSERVED = NO` at the time this supplement was frozen.

## Generator and inputs

Each case uses `F5TTS_v1_Base` on CPU with Euler ODE, EMA enabled,
`target_rms=0.1`, `internal_cross_fade_duration=0.15`,
`sway_sampling_coef=-1`, `cfg_strength=2`, `nfe_step=32`, `speed=1.0`,
`fix_duration=null`, and `remove_silence=false`.  The source commit is
`82fc4fe622fe36047d1dff99b550e6018181ea11`; model revision is
`84e5a410d9cead4de2f847e7c9369a6440bdfaca`.

The four required local assets are frozen as checkpoint
`670900FD14E6C458B95DA6E9ED317CDB20DBAF7A1C02AC06A05475A9D32B6A38`, vocab
`2A05F992E00AF9B0BD3800A8D23E78D520DBD705284ED2EEDB5F4BD29398FA3C`, vocoder
config `DA9033922F969A47F0C160010226919E59F27761FD5066F3828D46DE6650B0FC`,
and vocoder model `97EC976AD1FD67A33AB2682D29C0AC7DF85234FAE875AEFCC5FB215681A91B2A`.

For every case, `reference_path/reference_text_exact/source_text_exact` are the
frozen manifest values, non-empty and never ASR-filled or rewritten.  Exactly
one base synthetic is generated per case; A_STATIC and every A0 candidate are
derived from it.  Cases are ascending by `case_id`; their seeds are
`20260914 + zero_based_case_index` (0001 = 20260914, 0048 = 20260961), and an
infrastructure retry retains its original seed.

Native synthetic audio is retained with its native sample rate, then converted
to mono 16 kHz.  It alone receives edge trimming: 400-sample frames, 160-sample
hop, active iff `20*log10(max(rms,1e-12)) > -45`, retaining at most 800 samples
outside the first/last active frames.  No activity is invalid; no crop,
time-stretch, or padding is permitted.

## Construction and ground truth

Source audio is deterministically mono-resampled to 16 kHz and finite, after
its frozen file hash is checked.  Its active interval uses the same 400/160/-45
rule without edge retention.  With `[a,b)` that interval,
`p=floor((a+b)/2)`.  For crossfade `f` and gain `g`, use
`s=synthetic_trimmed*10^(g/20)`, rejecting a non-finite value, a peak above
0.999, `p<f`, `len(source)-p<f`, or `len(s)<=2f` before D0.

`alpha_in[k]=(k+1)/(f+1)` and `alpha_out[k]=(f-k)/(f+1)`, for `k=0..f-1`.
The output is exactly
`source[:p-f] + source[p-f:p]*(1-alpha_in)+s[:f]*alpha_in + s[f:n-f] +
s[n-f:]*alpha_out+source[p:p+f]*(1-alpha_out) + source[p+f:]`.
There is no deletion/replacement, normalization, channel matching, crop, pad,
or time stretch.  A_STATIC is `(f=400,g=0)`; A0 has only the frozen grids.

Sample-first GT is saved per candidate: attack `[p-f, p+n-f)`, strict core
`[p,p+n-2f)`, and blend `[p-f,p) U [p+n-2f,p+n-f)`.  GT is never inferred from
audio content.

## D0, objective, and final evaluation

D0 is offline CPU SpeechBrain 1.1.1 ECAPA (`speechbrain/spkrec-ecapa-voxceleb`),
at `pretrained/spkrec-ecapa-voxceleb`, 16 kHz and 192 dimensions.  Its asset
manifest is canonical and hash-bound; no network replacement is allowed.
S2 uses complete 24,000-sample windows with a 4,000-sample hop.  B1b is the
frozen reference-free normalized-centroid, stable 20% trim implementation.

Each D0 call preserves a C-contiguous float64 score vector, raw-byte SHA-256,
window table, case/candidate identity, and waveform SHA-256.  A window is
FULL_ATTACK at overlap >= 0.5 and OUTSIDE_CLEAN at overlap == 0.  The adaptive
objective is `J=mean(FULL_ATTACK)-mean(OUTSIDE_CLEAN)`; a missing/non-finite
side is `OBJECTIVE_UNDEFINED`, cannot win, but an already invoked D0 call counts.
The winner is minimum finite J, then lower query index, then lexical candidate
ID.

Only the 12 held-out cases enter final metrics.  The final evaluator reads
committed static/winner vectors and GT without D0, requires all 12 paired cases,
labels every FULL_ATTACK window positive and every other window negative, and
concatenates ascending case IDs.  AUROC/AUPRC use the frozen Day6A semantics.
Deltas are static minus adaptive.  Paired bootstrap resamples the same 12 case
IDs for both conditions (N=2000, seed=20260911, percentile 95%, at least 1900
finite replicates); otherwise that CI is not reportable.

## Governance

The machine-readable companion is `configs/week4_execution_supplement_v1.yaml`
and must validate against its schema.  A new authorization binds the original
preregistration, adaptive config, population, this document, companion config,
D0 asset manifest, and execution-source manifest.  Earlier unused
authorizations remain forensic history with
`SUPERSEDED_BEFORE_SCIENTIFIC_EXECUTION`.  Runtime is permitted only after this
supplement, TEST_ONLY E2E, and both manifests validate.  This supplement itself
does not authorize or perform scientific execution.
