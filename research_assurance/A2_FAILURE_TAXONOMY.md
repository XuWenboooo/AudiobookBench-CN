# A2 Failure Taxonomy (machine-readable, pre-registered)

Frozen before any A2 generation. These classes are **pipeline/QA failures
only**: none of them is defined by, or may be inferred from, a detector or
diagnostic score. Every planned case retains its manifest row regardless of
class (`failure_rows_retained: true`).

Common columns for every class:
`trigger`, `severity`, `retain_row`, `retain_waveform`, `retry_allowed`,
`protocol_amendment_required`, `blocks_pilot`, `blocks_publication_claim`.

`retain_waveform = RETAIN` means the written file stays in the tree as
evidence; `DISCARD` means the file must not be treated as a formal
artifact (row still retained); `N/A` = nothing was written.

| Class | Trigger | Sev. | Retain row | Retain waveform | Retry | Amend. req. | Blocks pilot | Blocks claim |
|---|---|---|---|---|---|---|---|---|
| BACKEND_LOAD_FAIL | generator/runtime fails to import or initialize | CRITICAL | YES | N/A | 1 infrastructure retry | only if env fix needs new dependency versions | YES until fixed | YES (no A2 claims) |
| CHECKPOINT_MISMATCH | checkpoint/component SHA-256 ≠ recorded provenance | CRITICAL | YES | N/A | NO | YES (provenance amendment) | YES | YES |
| REFERENCE_INVALID | reference missing, wrong speaker/split, duration outside 3–8 s, or overlaps any target utterance | CRITICAL | YES | N/A | NO | YES (reference rule change) | YES for that speaker's planned cases | YES |
| TEXT_MISMATCH | transcript absent, non-NFC-fixable, whitespace-invalid, or TTS input hash ≠ source text hash | CRITICAL | YES | N/A | NO | YES | YES | YES |
| EMPTY_OUTPUT | generator returns zero-length audio | HIGH | YES | DISCARD | 1 infrastructure retry | NO | case counts as failed | partial (denominator disclosure) |
| NONFINITE_OUTPUT | NaN/Inf in generator or post-DSP samples | HIGH | YES | DISCARD | 1 infrastructure retry | NO | case counts as failed | partial |
| NO_ACTIVE_SPEECH | no frame > −45 dBFSFS after resample (trim rule finds nothing) | HIGH | YES | DISCARD | 1 infrastructure retry | NO | case counts as failed | partial |
| TRIM_COLLAPSE | edge trim removes > 90 % of samples (active speech collapses) | HIGH | YES | RETAIN (evidence) | NO | NO | case counts as failed | partial |
| INSUFFICIENT_SYNTHETIC_CORE | post-trim N_syn ≤ 800 samples (core would be empty under 2×400 crossfade rule) | HIGH | YES | RETAIN | NO | NO | case counts as failed | partial |
| RMS_MATCH_FAIL | gain clamped at 0.25/4.0 AND post-gain speech RMS still > 6 dB from reference (recorded; not a quality filter) | LOW (QA flag) | YES | RETAIN | NO | NO | NO | NO |
| PEAK_SAFE_FAIL | peak-safety reduction cannot bring |peak| < 0.999 | HIGH | YES | DISCARD | NO | NO | case counts as failed | partial |
| SERIALIZATION_MISMATCH | serialized-decoded length/channels/SR ≠ in-memory final | HIGH | YES | DISCARD | 1 infrastructure retry | only if library version change required | YES until fixed | YES |
| OFFLINE_RELOAD_FAIL | offline reload of the cached generator env fails after cache freeze | CRITICAL | YES | N/A | NO | YES | YES | YES |
| DETERMINISM_MISMATCH | identical inputs/seed produce different outputs across the recorded determinism probe | MEDIUM | YES | RETAIN (both) | NO | NO (disclose limitation) | NO | partial (determinism caveat in claims) |
| TIMELINE_INCONSISTENCY | suffix-shift lineage check fails (post-attack interval mapping ≠ clean + delta) | CRITICAL | YES | RETAIN (evidence) | NO | NO (generator bug) | YES | YES |
| GT_OUT_OF_RANGE | any GT bound < 0, ≥ final length, or seconds inconsistent | CRITICAL | YES | RETAIN (evidence) | NO | NO | YES | YES |
| SUFFIX_MISMATCH | downstream suffix not bit-equal to clean + delta | CRITICAL | YES | RETAIN (evidence) | NO | NO | YES | YES |

## Cross-references to the frozen config

- `crossfade_interval_too_short` (config hard-failure) maps to
  INSUFFICIENT_SYNTHETIC_CORE.
- `no_speech_detected` maps to NO_ACTIVE_SPEECH; `empty_audio` to
  EMPTY_OUTPUT; `nonfinite_audio` to NONFINITE_OUTPUT;
  `duration_ratio_out_of_bounds` maps to TRIM_COLLAPSE-or-
  INSUFFICIENT_SYNTHETIC_CORE depending on trim evidence; the remaining
  config hard reasons map 1:1 (lineage_failure → REFERENCE_INVALID or
  TEXT_MISMATCH by evidence; exact_input_text_failure → TEXT_MISMATCH;
  waveform_or_gt_verification_failure → TIMELINE/GT/SUFFIX classes;
  serialization_mismatch → SERIALIZATION_MISMATCH).

## Explicitly NOT failure classes

- High ASR CER (diagnostic QA flag only; ASR never defines GT).
- Low reference↔synthetic ECAPA cosine (diagnostic QA flag only).
- Low/any B0/B1/B2/B4 score (detector output; forbidden as a failure
  criterion by the frozen detector denylist).
- Audible-artifact or unusual-prosody judgment (retained as QA flags).

## Denominator rule

Every split/speaker report of A2 results must state
`planned = 23 (11/6/6)`, `succeeded`, `failed_by_class`. Claims are
conditioned on the realized denominator; a pilot with > 3 failed cases
must report per-class counts before any performance number.
