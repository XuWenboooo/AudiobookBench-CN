# Week4 scaffold alignment audit

Date: 2026-09-11
Scope: code/configuration review and TEST_ONLY validation only.  No F5
generation, D0 scientific query, validation/held-out result, H4 result, or
Week4 authorization was created.

## Repository and Week3 integrity

- Branch/starting HEAD: `main` / `bd7bb098167d7006ac88d633fed33e6674ac1cee`.
- Week4 scaffold was untracked before this alignment work.
- Week3 closure SHA-256 matched
  `24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C` before
  edits and is protected by a TEST_ONLY immutability check.
- Week4's frozen config remains byte-identical and binds only its historical
  base field; the formal runner independently derives a unique
  `results/week4_adaptive_redteam_runs/<invocation_id>` namespace, rejects
  existing namespaces, and accepts no Week1–3 output path.
- The finalized AISHELL-3-derived population is independently recorded in
  `WEEK4_POPULATION_FREEZE.md`; no Week4 formal results directory exists.

## Post-alignment review matrix

| Review question | Verdict | Evidence |
| --- | --- | --- |
| Controller is adaptive | PASS | deterministic generations 1–4 select/mutate from lowest prior D0 objective |
| Later candidates depend on earlier scores | PASS | synthetic history-dependence test |
| Counter persists across restart | PASS | ledger is re-read before every budget decision |
| Query 41 fails closed | PASS | 40-query synthetic test |
| Ledger is append-only and retains all candidates | PASS | contiguous JSONL hash chain, unique ID, tamper test |
| Invalid candidates are retained and cannot win | PASS | invalid rows have reason and are excluded from elite selection |
| Static/adaptive accounting is separate | PASS | one A_STATIC query is distinct from 40 adaptive D0 queries |
| Held-out tuning fails closed | PASS | `tuning` is rejected only for held-out; frozen A0 execution remains permitted |
| A0/config freeze is enforced | PASS | spec hash + A0 freeze hash bind authorization; manual proposal change rejects |
| Authorization precedes detector/runtime | PASS | gate runs before waveform/detector call and sentinel detector remains uncalled |
| CLI/schema cannot override science | PASS | strict schema plus path-only CLI; unknown scientific flags reject |
| Score direction is frozen | PASS | `higher_is_more_anomalous` is a schema and spec constant |
| Bootstrap is paired by case | PASS | Week4-only utility fixes paired-case unit, N=2000, seed and finite threshold |
| Week3 namespace is protected | PASS | independent output root, no execution entry point, closure hash test |
| Real 48-case population is frozen without D0 | PASS | canonical manifest, 149-pair pool, 12 prior exclusions, 24/12/12 split |
| Formal authorization binds current evidence and F5 assets | PASS | canonical schema/validator and read-only preflight tests |

## Environment regression disposition

`NON_BLOCKING_PREEXISTING_ENVIRONMENT_ERRORS = YES` for the three base-Python
Day6B errors.  Exact failing tests were `test_real_pretrained_backend_loads`,
`test_embeddings_are_finite_and_dimension_is_fixed`, and
`test_repeated_input_is_stable`; all fail because base Python has no `torch`.
The offline formal F5 environment has `torch 2.2.2+cpu` and passed the complete
Day6B module: `25 passed, 1 Windows symlink warning`.  This has no Week4
dependency-path overlap, so no unrelated production change was made.

## Result

The scaffold is aligned to the canonical preregistration for independent
readiness review.  This audit is not an execution authorization.
