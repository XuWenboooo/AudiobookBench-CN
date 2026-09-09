# Week2A Registry Consistency Audit

Checks performed against the machine-readable registries and their Markdown
sources. CORRECTIVE NOTE: this audit doc and two derived docs
(`A2_STATUS_MODEL.md`, `WEEK2A_VERIFICATION_MATRIX.md`) were corrected by the
WEEK2A registry corrective patch — failure-count 14→15 (ISSUE 1) and leakage
coverage reworded to *enforcement obligations* (ISSUE 7). Registry semantics
and the source taxonomy are unchanged.

## 1. Count consistency

| Collection | Expected | Registry | Status |
|---|---:|---:|---|
| Findings (F-ids) | 17 | 17 | PASS |
| Required tests | 21 | 21 | PASS |
| Failure classes | 17 | 17 | PASS |
| Leakage vectors | 14 | 14 | PASS |
| Day13 scenarios | 4 | 4 | PASS |
| Gates | 7 | 7 | PASS |
| Claim terms | 16 | 16 | PASS |
| Matrix rows | 92 | 92 | PASS |

## 2. Coverage checks

- Every F-id maps to at least one test: PASS (F11/F12/F13/F15/F16/F17 map to
  their locking tests; F1-F10, F14 map to dedicated tests).
- Every HIGH finding (F1, F4, F5) is gate-blocking (DAY11_METRIC_GATE): PASS.
- Every leakage vector has an ENFORCEMENT OBLIGATION (pytest test-id, report-check, validator-check, or gate-check): 14/14 PASS. Note: only 10/14 have dedicated pytest test-ids; L7/L9/L10/L13 are covered by REPORT_CHECK/VALIDATOR_CHECK obligations (denominator_report_check, zone_statistics_report_check, trim_margin_validator_check, format_sr_validator_check), not machine tests.
- Every hard failure class has an explicit status effect: PASS (HARD_FAILURE,
  except RMS_MATCH_FAIL=QA_FLAG and DETERMINISM_MISMATCH=DETERMINISM_LIMITATION
  as required).
- No QA flag is mapped to a hard failure: PASS (RMS_MATCH_FAIL explicitly QA_FLAG).
- Every claim term has an evidence gate: PASS (16/16).
- Every gate has an evidence source: PASS (registry + dry-run JSON).
- Every test has an execution phase: PASS (21/21).
- Every registry rule traces to a Markdown source: PASS (source_file recorded
  per item in the CSV).

## 3. Documentation inconsistencies found (2)

### DI-1 — Finding severity summary count
- SOURCE: A2_STATIC_COMPATIBILITY_AUDIT.md summary section ("3/7/7").
- CONFLICT: per-finding severities recount to 3 HIGH / 8 MEDIUM / 6 LOW-SAFE.
- CANONICAL INTERPRETATION: NORMALIZED_COUNT = 3 HIGH / 8 MEDIUM / 6 LOW-SAFE /
  17 total.
- REASON: F2 was labelled MEDIUM-HIGH, F9/F10 LOW-MEDIUM; the registry collapses
  both to MEDIUM, and the six SAFE-with-tests items (F11-F13, F15-F17) belong to
  the LOW/SAFE bucket. The underlying findings are unchanged.
- CLASSIFICATION: **DOCUMENTATION_NORMALIZATION_ONLY** (not a protocol
  amendment). Source document left untouched as instructed.

### DI-2 — Test type / phase taxonomy
- SOURCE: A2_REQUIRED_TEST_MAP.md notes ("#1-13 unit, #14-21 DATA").
- CONFLICT: the unit/DATA split does not express that test #1 has both a unit
  and a fixture/integration portion, and that #10 needs only a manifest fixture.
- CANONICAL INTERPRETATION: PHASE_A_PRE_A2_UNIT / PHASE_B_FIXTURE_MANIFEST /
  PHASE_C_POST_A2_DATA, with T01 split across A (unit) and B (fixture).
- REASON: executes-before-A2-output is the property that matters for scheduling;
  it differs from the source's unit/integration phrasing.
- CLASSIFICATION: **DOCUMENTATION_NORMALIZATION_ONLY**. Original provenance kept
  in the registry (`sources`) and in the CSV notes.

## 4. Dry-run verification

`python research_assurance/tools/week2a_gate_check.py --all --write-report
research_assurance/week2a_gate_dryrun.json`

- DAY8 = HOLD (36 evaluated rules; config placeholders TO_BE_VERIFIED=10;
  DAY8_PRECHECK.md absent)
- DAY9 = BLOCKED (BLOCKED_BY_DAY8)
- DAY10 = BLOCKED (BLOCKED_BY_DAY9)
- DAY11 = BLOCKED (BLOCKED_BY_DAY10; all tests NOT_RUN; P0 findings
  unresolved) — reason corrected from BLOCKED_BY_A2_OUTPUT to BLOCKED_BY_DAY10
  by the final checker semantic fix (ISSUE 9/10).
- DAY12 = BLOCKED (BLOCKED_BY_DAY11), DAY13 = BLOCKED (BLOCKED_BY_DAY12) —
  Day13 prerequisite is DAY12_ANALYSIS_GATE, not Day11 (ISSUE C); reasons
  corrected from the generic BLOCKED_BY_A2_OUTPUT.
- CLAIM = MISSING_EVIDENCE (NO_A2_CLAIMS_YET; E6 NOT_APPLICABLE)
- Status propagation: matches the expected dependency graph with live-upstream,
  specific block reasons (see `week2a_gate_dryrun_v3.json`).

Checker dependency hygiene: imports are argparse, json, re, sys, datetime,
pathlib, plus optional PyYAML with a clear fallback message; no torch,
speechbrain or CosyVoice import: PASS.

## 5. Result

**CORRECTIVE PATCH STATUS = READY_FOR_INDEPENDENT_REVIEW** (the checker author
must not self-declare PASS; the final gate is judged by the independent model).

The structural registry-consistency checks (counts, coverage, provenance, the
two documentation-normalization items) remain intact, and the dry-run now
propagates the correct HOLD/BLOCKED states with live-upstream, specific block
reasons. READY_FOR_INDEPENDENT_REVIEW does not mean Day8 is ready, A2 is
implemented, A2 is tested, or a paper is ready.

## 6. Final checker semantic fix (WEEK2A GATE CHECKER FINAL CORRECTIVE PATCH)

The independent-review HOLD item "Gate Checker Semantic Correctness" is remediated
by `tools/week2a_gate_check.py` (and `tools/test_week2a_gate_check.py`). Issues
addressed:

- A — FAIL/ERROR/SKIPPED/unknown are fail-closed; a phase is PASS only when every
  required obligation is `IMPLEMENTED_PASS`.
- B — downstream gates consume the **live evaluated** upstream status via
  dependency injection; the static YAML `status:` field is DECLARED/EXPECTED
  only and is never used as the live truth.
- C — Day13 depends on DAY12_ANALYSIS_GATE (reason BLOCKED_BY_DAY12); Day12 on
  DAY11_METRIC_GATE (BLOCKED_BY_DAY11); Day11←Day10, Day10←Day9, Day9←Day8.
- D — T19 (`test_a2_silence_distribution_shift_report`) carries
  `required_before_gate: [DAY12_ANALYSIS_GATE]` and is excluded from
  DAY11_METRIC_GATE obligations (still classified under PHASE_C).
- E — evidence PRESENCE alone never yields a gate PASS; each gate also runs
  minimal CONTENT validation (Day9 smoke 3/3/0, Day10 pilot 23-case 11/6/6, etc.).
- F — fresh Week1 rehash parses `rehash_result.json` content
  (status/exit_code/missing/mismatch/matched), not just file existence.
- G — single-gate CLI (`--gate dayN`) lazily evaluates its dependency closure;
  never KeyError.
- H — PyYAML missing is a strict CI failure (`test_registry_integrity.py`
  `decide_exit` returns 2; `--allow-skip` opts out) and `test_week2a_gate_check.py`
  refuses to silently pass.

Verification:

- `python research_assurance/tools/test_registry_integrity.py` → 29/29 PASS
- `python research_assurance/tools/test_week2a_gate_check.py` → 78/78 PASS
- `python research_assurance/tools/week2a_gate_check.py --all
  --write-report research_assurance/week2a_gate_dryrun_v3.json`
- AST audit (`tools/audit_checker_ast.py`): no torch / speechbrain / CosyVoice
  imports in the checker or either test file.

## FINAL CLOSURE PATCH (FIX 1-3 + LOW) — engineering-only, no semantics change

Checker-level hardening applied to `tools/week2a_gate_check.py` and
`tools/test_week2a_gate_check.py` ONLY. No scientific protocol, no gate
registry semantics, no Week1/Day8 artifacts were touched.

- FIX 1 — Day9: source implementation presence
  (`SIDECAR_VALIDATOR_IMPLEMENTATION_PRESENT`,
  `WAVEFORM_GT_VERIFIER_IMPLEMENTATION_PRESENT`) is recorded as
  informational/non-blocking ONLY (`blocking=False`). Real Day9 evidence
  requires three INDEPENDENT execution-result classes (all blocking):
  `SIDECAR_VALIDATOR_EXECUTION_RESULT`,
  `WAVEFORM_GT_VERIFIER_EXECUTION_RESULT`, `OFFICIAL_SMOKE_3_3_0`.
  Execution-result JSON must have `status == "PASS"` and, when present,
  `failed == 0` and `errors == 0`. The artifact paths
  (`results/day9/sidecar_validator_result.json`,
  `results/day9/waveform_gt_verifier_result.json`,
  `results/day9/smoke.json`) are an ENGINEERING_EVIDENCE_ONLY checker
  contract — no canonical names existed in WEEK2_DAY9_PREREG.md /
  A2_SIDECAR_CONTRACT.md, and no scientific document was modified.
- FIX 2 — fresh Week1 rehash requires the FULL contract: `status`,
  `exit_code`, `matched`, `missing`, `mismatch` all PRESENT (never
  defaulted to 0/None), `status == "PASS"`, `exit_code == 0`,
  `missing == 0`, `mismatch == 0`, `matched == 696` (canonical Week1
  696/696). A bare `{"status":"PASS"}` now yields
  `INVALID_REHASH_EVIDENCE`, never `REHASH_PASS`.
- FIX 3 — PyYAML missing => CLI fail-closed: stderr ERROR, exit code 2 by
  default; `--allow-missing-yaml` is an explicit opt-out that still refuses
  any gate PASS (all gates reported MISSING_EVIDENCE).
- LOW — Day10 `failed_by_class` values must each be a non-negative int
  (rejects `{"A": 2, "B": -1}` and non-integer counts).

Verification (after this patch):

- `test_week2a_gate_check.py` → 110/110 PASS (incl. 5 Day9
  execution-result tests, 10 strict-rehash tests, 3 PyYAML-CLI tests,
  2 Day10 failure-count tests; all prior fixes still green)
- `test_registry_integrity.py` → 29/29 PASS
- `week2a_gate_check.py --all` and all 7 single-gate CLIs → exit 0
- AST audit → no torch / speechbrain / CosyVoice
- Real repo state unchanged: Day8 HOLD; Day9-DAY13 blocked by their live
  upstream; Claim NO_A2_CLAIMS_YET; fresh Week1 rehash NOT_PERFORMED
  (no fake `results/day9` or `results/week1/rehash_result.json` created).

Status: SELF-TESTED ONLY — AWAITING INDEPENDENT REVIEW.
