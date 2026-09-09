# Day12 preregistration source-semantics adjudication

Date: 2026-09-06  
Status: **HOLD — source classification resolved; T19 semantics underspecified**

No Day12 similarity, correlation, bootstrap, or scientific result was computed
or observed during this adjudication. The review was limited to the authoritative
Week2A preregistration, Day9 preregistration, Day12 preregistration, and the test,
finding, and gate registries.

## Cosine source classification

**DERIVED_VARIABLE_NOT_YET_MATERIALIZED**

The frozen documents specify a Day12 analysis variable, not a requirement that
its numeric values already exist as a Day9 output artifact:

- `WEEK2_A2_PREREGISTRATION_REPORT.md:3-5` identifies the preregistration as a
  pure design/audit performed before A2 artifacts existed. Its Day9 summary at
  lines 9-15 requires the generation pipeline, validators, smoke cases, and
  transition evidence; it does not require materialized ECAPA cosine values.
- `WEEK2_DAY9_PREREG.md:19-33` enumerates Day9 outputs without an ECAPA cosine
  table or mandatory cosine-valued sidecar field. Lines 90-94 classify low
  speaker similarity as a retained QA flag and prohibit quality filtering.
- `WEEK2_DAY12_MECHANISM_PREREG.md:21-28` places the per-case
  target-real↔synthetic cosine inside Day12 P1 and defines it as the synthetic
  core region versus the real target utterance embedding. Lines 62-63 name the
  sidecar field, while lines 78-81 freeze the extractor/variable and population;
  they do not state that the numeric value must have been computed during Day9.
- `week2a_gate_registry.yaml:57-66` requires the P1 association and Day12
  diagnostic outputs for the Day12 gate, not for the Day9 gate.

Accordingly, the absent `target_synthetic_ecapa_cosine` column is a
preregistered derived variable not yet materialized. Day12 may compute it from
the immutable Day10 waveforms with the frozen extractor. This is not a protocol
amendment and must not be described as reconstruction of a historical Day9
artifact. Before execution, the mechanical specification must pin the exact
real-target path/whole-utterance rule, synthetic core half-open bounds, ECAPA
function and code revision, 16-kHz preprocessing, cosine formula, the 23 case
IDs, and the Day12 output schema/path.

The target-real semantics are sufficiently frozen as the real target utterance;
the synthetic semantics are sufficiently frozen as the strict synthetic core.
The supplied frozen implementation identity—SpeechBrain 1.1.1,
`speechbrain/spkrec-ecapa-voxceleb`, offline CPU, 16 kHz, 192-D—is sufficiently
specific, subject to recording the exact callable/code revision in the
pre-execution mechanical freeze.

## Reference cosine

The reference↔synthetic cosine is required as **D2 DIAGNOSTIC ONLY**, not as part
of the primary P1 relationship. This follows from
`WEEK2_DAY12_MECHANISM_PREREG.md:48-55` and the Day12 gate requirement that D1-D4
be reported (`week2a_gate_registry.yaml:58`). It must remain outside detector
inputs and must not be promoted, filtered on, or substituted for P1.

## T19 adjudication

T19 is required before `DAY12_ANALYSIS_GATE` by
`week2a_test_registry.yaml:331-350`. The registry freezes only the qualitative
assertion that a “pause-feature shift between removed-real and
inserted-synthetic is reported as DIAGNOSTIC.” It does not define:

- the pause/silence feature and threshold;
- the exact removed-real and inserted-synthetic sample regions;
- the case-level aggregation or comparison statistic;
- the required output schema/path;
- a mechanical PASS/FAIL condition beyond producing an unspecified report.

No registered implementation exists. Therefore T19 is **UNDERSPECIFIED**, not
merely an engineering implementation gap. Inventing these choices now would
redesign T19, which this adjudication is not authorized to do.

## Decision

- Cosine materialization requires protocol amendment: **NO**.
- Scientific ambiguity in the primary cosine source: **NO**.
- Day12 execution contract can be frozen now: **NO**, solely because T19 remains
  semantically underspecified and separately blocks the Day12 gate.

