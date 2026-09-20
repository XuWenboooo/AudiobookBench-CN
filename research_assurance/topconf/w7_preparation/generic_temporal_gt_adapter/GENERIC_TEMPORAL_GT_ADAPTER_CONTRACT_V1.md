# Generic Temporal GT Adapter Contract v1

Status: `SKELETON FOR W7 PREPARATION / NOT AN EXECUTION AUTHORIZATION`

The adapter is shared by HQ-MPSD, HAD and future external distributions. It
does not read or alter any active download/archive state. A distribution is
not ready merely because an adapter can parse a fixture; source, rights,
identity and integrity gates remain independent.

## Canonical case

Every emitted case contains `distribution_id`, `split`, `audio_id`, relative
`audio_path`, positive `duration_sec`, integer `sample_rate`, original GT
representation type, canonical manipulated intervals, source identity,
manipulation identity, metadata and the fixed adapter version
`topconf.w7.generic_temporal_gt_adapter.v1`.

The canonical interval convention is half-open `[start_sec, end_sec)` with
`0 <= start < end <= duration`. No clipping, padding, interpolation, label
invention or opportunistic filename normalization is permitted.

## Supported synthetic forms

The preparation adapter supports:

1. start/end interval labels (`intervals_sec`, including JSON/CSV interval-list
   aliases);
2. segment labels (`segment_labels` / `manifest_segment_table`);
3. binary frame vectors (`frame_labels` / `binary_frame_vector`) with an
   explicit frame duration and exact duration agreement;
4. sample-index intervals with explicit sample rate and exclusive end index.

Conversions are deterministic: frame `i` maps to
`[i * frame_duration, (i + 1) * frame_duration)`, and sample indices map to
`[start / sample_rate, end / sample_rate)`. Any mismatch is an explicit
structured error.

## Required interface

Future distribution adapters must expose:

```text
discover()
parse_manifest()
resolve_audio()
parse_gt()
normalize_gt()
validate_case()
emit_canonical_case()
```

`validate_case()` must call identity, duration and GT-range validation before
emission. `TemporalGTAdapterError.code` is the machine-readable failure class.
The adapter never suppresses an invalid case; the acceptance harness retains
the failure and marks the distribution candidate not ready.
