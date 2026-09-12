# Week4 runtime-dispatcher closure blocker

Date: 2026-09-12  
Status: `BLOCKER = FROZEN_EXECUTION_CONTRACT_INCOMPLETE`

The requested real Week4 dispatcher cannot be implemented faithfully from the
current frozen scientific artifacts without adding scientific choices that are
not frozen by the Week4 preregistration or canonical config.

## Missing frozen execution semantics

1. **F5 inference contract.** Week4 freezes the F5 identity and revision, but
   not its inference settings or a Week4 seed rule (for example ODE method,
   EMA, RMS target, CFG, NFE steps, speed, silence policy, and per-case seed).
   The Week3 values are specific to the Week3 protocol and cannot be silently
   inherited because Week4 declares itself the sole scientific source of truth.
2. **D0 implementation identity and score-vector contract.** `B1b` and the
   `S2_1500ms_250ms` window identify a method, but no Week4-bound ECAPA/model
   asset, prototype/trimming inputs, waveform-to-score-vector adapter, or
   scalar objective projection is frozen.
3. **Source active interval and sample-first ground truth.** Week4 fixes the
   insertion rule as the middle of the source active interval, but the 48-case
   manifest contains no active-interval boundaries. It also contains no
   deterministic GT construction inputs. Inventing interval detection or
   treating the full file as active would alter the experimental construction.
4. **Final evaluator definition.** The primary/companion estimands name AUROC
   and AUPRC deltas, but the frozen Week4 artifacts do not bind the final
   evaluator implementation, score/label construction, or a complete-case
   inclusion rule needed to compute them after held-out completion.

## Evidence

- `configs/week4_adaptive_red_team.yaml` contains the fixed high-level method,
  A_STATIC and A0 bounds/search, but none of the missing execution fields.
- `data/manifests/week4_population_manifest.json` case rows contain only
  identities, texts, hashes, splits, and eligibility fields; they contain no
  active interval, GT, detector, or F5-inference fields.
- `research_assurance/WEEK4_ADAPTIVE_REDTEAM_PREREGISTRATION.md` calls itself
  the sole scientific source of truth, so different Week3 protocol settings
  are not an admissible implicit default.

## Safe disposition

```text
REAL_RUNTIME_DISPATCHER_IMPLEMENTED = NO
SYNTHETIC_END_TO_END_EXECUTION = NOT_STARTED
NEW_ACTIVE_EXECUTION_AUTHORIZATION = NOT_ISSUED
READY_FOR_WEEK4_DEV_EXECUTION = NO

REAL_F5_GENERATION = NOT STARTED
REAL_D0_QUERY = NOT STARTED
DEV_SCIENTIFIC_RUN = NOT STARTED
VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO
```

Resolution requires a separately approved, prospective Week4 execution
specification/amendment that freezes these missing choices and is then bound to
a new execution-source manifest and authorization. The existing authorization
is retained only as historical evidence and must not be used for scientific
execution.
