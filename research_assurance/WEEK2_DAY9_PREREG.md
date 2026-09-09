# WEEK 2 — DAY 9 PRE-REGISTRATION (A2 Generation Pipeline + Official Smoke)

Status: PRE-REGISTERED before any Day-9 implementation. This document
freezes what Day 9 may and may not do. It does not authorize generation
beyond the smoke/preflight cases defined here, and it does not modify the
frozen A2 protocol (`configs/week2a_a2_protocol_draft.yaml`,
`week2a-a2-v1.1-corrected`).

## 1. Inputs (all pre-existing; Day 9 creates no new data source)

- `configs/week2a_a2_protocol_draft.yaml` (v1.1-corrected, design-frozen).
- `data/manifests/day45_attack_manifest.csv` (lineage only:
  `paired_case_id`, `target_source_sample_id`, target speaker, split,
  clean sequence).
- `data/manifests/day45_longform_manifest.csv`
  (`sequence_start`/`sequence_end` → materialized whole-utterance bounds
  `c0`/`c1`).
- `data/manifests/day45_source_audio.csv` + AISHELL-3 raw audio (read-only)
  for the 12 frozen speaker references (`frozen_reference_sample_by_speaker`)
  and for target source utterances.
- `transcript_zh` for the 23 target source utterances (exact text, NFC,
  no normalization rewrite).
- CosyVoice2-0.5B code + checkpoint — **only after** every
  `TO_BE_VERIFIED_BEFORE_IMPLEMENTATION` field in the config is resolved
  and the checkpoint/component hashes are recorded.

## 2. Outputs

1. The formal A2 generation pipeline (one deterministic function:
   case lineage → reference + text + generator → trim → resample → RMS
   match → peak-safe gain → 400-sample dual crossfade → dual-timeline
   assembly → serialization → sidecar row).
2. The additive A2 sidecar validator (every REQUIRED field of
   `A2_SIDECAR_CONTRACT.md`, including dual timelines, suffix delta and
   full/core/blend-in/blend-out GT).
3. Waveform/GT verification suite (prefix bit-equality, suffix equality
   under the exact `duration_delta_samples`, synthetic-only core equality,
   both blend zones reconstructed from the frozen formula, final length,
   half-open bounds, seconds consistency).
4. **A small number of official smoke/preflight cases** (see §4).

## 3. Allowed actions

- Implement and unit-test the pipeline on **synthetic dummy arrays** (no
  TTS): crossfade formula, dual-timeline assembly, suffix-shift GT, trim
  rule, RMS/peak-safe gain, serialization round-trip.
- Run official smoke cases (§4) once the generator environment passes its
  own preflight (license chain, checkpoint hashes, offline cache,
  determinism probe, Windows smoke).
- Record every attempt (including failures) in the sidecar with
  `generation_status` / `generation_failure_reason`.

## 4. Smoke-to-official transition

Official smoke = at most 3 cases, chosen deterministically before any
generation: the first sorted `paired_case_id` in train, in val, in test.
Smoke succeeds iff: pipeline runs end-to-end; sidecar passes the validator;
waveform/GT verification passes; duration ratio within [0.25, 4.0]; no
detenctor/diagnostic score is examined for the decision.

**Transition rule**: official 23-case generation is authorized only when
(a) all config `TO_BE_VERIFIED_BEFORE_IMPLEMENTATION` fields are recorded;
(b) smoke passes on all 3 cases; (c) the sidecar validator is committed
with tests; (d) a fresh `--verify-only` Week-1 run is 696/696. Any smoke
failure is a Day-9 blocker to fix in the pipeline (not in the protocol).

## 5. Manifest requirements

- Every planned case keeps its manifest row **even on hard failure**
  (`failure_rows_retained: true`); failed rows carry
  `generation_status=failure` + machine-readable
  `generation_failure_reason` from the A2 failure taxonomy; no row is
  deleted or replaced.
- Success rows carry the full REQUIRED sidecar field set.
- `formal_generation_allowed` flips to true in the config **only** via an
  explicit amendment record after §4 conditions are met.

## 6. GT verification (Day-9 code must implement, Day-10 runs it)

Exactly the eight checks listed in the protocol's
`timeline_and_gt.verification` (prefix/suffix/core/blends/length/bounds/
seconds). All are fail-closed: any failure sets
`waveform_or_gt_verification_failure` and retains the row as failed.

## 7. Failure retention

No case may be dropped, re-donored, re-texted, or regenerated for quality
reasons. The ONLY permitted retry is the protocol's infrastructure retry
(max 1, identical inputs/seed/environment, both attempts logged, only when
no valid model output exists). Quality flags (high ASR CER, low speaker
similarity, audible artifacts, unusual prosody, low detector score) are
retained as QA flags — **never** as exclusion criteria.

## 8. Determinism rules

- `generation_seed = base_seed + one-based sorted paired_case_index`
  (frozen rule).
- best_of_n forbidden; sampling parameters recorded; generator determinism
  probe executed and recorded before official generation.
- Infrastructure retry must reuse the identical seed.
- If the generator proves non-deterministic across identical runs, that is
  `DETERMINISM_MISMATCH` — recorded; pilot proceeds with per-case recorded
  seeds and the limitation is disclosed (no silent re-rolls).

## 9. Forbidden in Day 9

Installing/checking out anything beyond the Day-8-owned environment without
an amendment; touching Week-1 frozen artifacts; generating beyond smoke;
running detector/diagnostic scores on smoke output for any accept/reject
decision; ASR-based filtering; similarity-based filtering; editing
transcripts; altering intervals; deleting failed rows.
