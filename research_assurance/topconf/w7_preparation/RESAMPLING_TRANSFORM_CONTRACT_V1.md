# W7 Resampling Transform Identity Contract v1

Status: `DRAFT_READY_TO_FREEZE` / synthetic validation only

The declared transform is 16 kHz → 8 kHz → 16 kHz using
`scipy.signal.resample_poly`, the project runtime identity `scipy==1.18.0`,
polyphase FIR filtering, anti-aliasing enabled, explicit Kaiser window
`beta=5.0`, `padtype=constant`, `cval=0.0`, and no hidden library defaults.

The transform is mono-only, casts to float32 after each leg, performs no
normalization, and uses the library's documented ceil output-length rule.
The transform ID and SHA-256 configuration hash are written to the case
manifest. Runtime version mismatch is a fail-closed environment error; no
alternate library or backend is substituted.

Temporal GT represented in seconds keeps the same half-open seconds interval.
Sample-index or frame-index GT must first be converted by the frozen GT
adapter using the declared source rate and then be applied in canonical
seconds. Model output cannot repair or move a boundary.

The synthetic validation covers repeated-array determinism, finite output,
expected length/duration tolerance, stable transform identity and valid GT
interval support. It does not read or process any W7 real sample.
