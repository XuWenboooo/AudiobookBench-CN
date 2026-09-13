# Week 1–5 Pilot Evidence Register

This register is an archival, claim-bounded index. Week 1–5 material is
historical pilot or qualification evidence; none is a confirmatory result for
the next research phase. Primary artifact paths are repository-relative unless
the entry explicitly identifies the isolated Week5 worktree.

## E-W1-CONTROLLED-SPLICE

Evidence ID: `E-W1-CONTROLLED-SPLICE`
Week / Experiment: Week 1 controlled splice and canonical localization baseline
Scientific Question: What temporal speaker-consistency and localization signals appear under the frozen constructed splice protocol?
Population: 12 speakers; 23 paired targets; 23 A0/A1 pairs; 23 C0A/C0B controls
Protocol Status: FROZEN_HISTORICAL_PILOT_COMPLETE
Outcome Observed: Day6A negative; Day6B B1 signal; Day6C control and speech-active audits
Primary Result: Frozen B1b/S2 test AUROC was 0.901421/0.896658 for A0/A1; the result is a bounded temporal ranking signal.
Allowed Interpretation: The tested ECAPA-based signal is informative under the named constructed protocol and claim boundary.
Forbidden Interpretation: Universal TTS/deepfake detection, native-audiobook generalization, deployment readiness, or pure speaker-identity causality.
Top-Conference Role: Historical motivation and baseline context only.
Primary Artifact Paths: `WEEK1_FREEZE.md`; `WEEK1_REPORT.md`; `results/week1/hashes.json`; `results/week1/metrics_summary.csv`
Commit: `9e67ba880c674884ddf1818e3f2e95f735100b9f` (initial public release); the freeze itself records no original canonical Git commit.
SHA256 / provenance: `WEEK1_FREEZE.md` = `BF9EBF086A2D99E46A2C93A95C9F8F4DFA38D32C83A63AE55C96858E4B378105`; 696-entry chain in `results/week1/hashes.json`; ECAPA checkpoint hash is recorded in the freeze.
Final Status: ARCHIVED_PILOT_ONLY

## E-W2-COSYVOICE2

Evidence ID: `E-W2-COSYVOICE2`
Week / Experiment: Week 2 CosyVoice2 mechanism-shift pilot
Scientific Question: Does the frozen Week1 signal transfer to same-text, voice-conditioned whole-utterance TTS replacement?
Population: 23 realized cases across 12 speakers; 11 train, 6 validation, 6 test
Protocol Status: FROZEN_HISTORICAL_PILOT_COMPLETE; original Day13 decision gate remains formally unresolvable and on HOLD
Outcome Observed: The tested B1b/S2 transfer was not comparable to the Week1 result; Day12 mechanism evidence was correlational and diagnostic.
Primary Result: Original full-GT test B1b/S2 AUROC was `0.5215332008687215`; the bounded transfer stress-test conclusion is preserved.
Allowed Interpretation: The named frozen baseline did not retain comparable transfer under the tested A2 condition.
Forbidden Interpretation: TTS is undetectable, B1 is useless, generic deepfake detection failed, or the result establishes causation.
Top-Conference Role: Historical motivation and pilot stress-test context only.
Primary Artifact Paths: `research_assurance/WEEK2_SCIENTIFIC_CLOSURE.md`; `results/day10`; `results/day11`; `results/day12`
Commit: `9e67ba880c674884ddf1818e3f2e95f735100b9f`
SHA256 / provenance: `research_assurance/WEEK2_SCIENTIFIC_CLOSURE.md` = `EC5B0121570E4679272763BD14E08EDE18D47B49455CA8062AF7E861961EAFB3`; source provenance and limits are stated in the closure record.
Final Status: ARCHIVED_PILOT_ONLY

## E-W3-F5

Evidence ID: `E-W3-F5`
Week / Experiment: Week 3 Stage-A F5 clean rerun
Scientific Question: Do the frozen F5 protocol and B1b/S2 estimands reproduce the predeclared full, boundary/core, and blend-exclusion evidence?
Population: 23/23 verified clean-rerun cases
Protocol Status: SCIENTIFICALLY_COMPLETE; integrity re-execution of frozen protocol
Outcome Observed: H1/H2/H3 were independently recomputable within the frozen claim boundary.
Primary Result: The final closure record reports PASS with no scientific-output mutation or historical copy-forward.
Allowed Interpretation: Week3 closed for the tested frozen F5 condition and estimands.
Forbidden Interpretation: Universal F5 robustness, general TTS/deepfake detection, or deployment readiness.
Top-Conference Role: Historical pilot evidence and motivation only.
Primary Artifact Paths: `research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md`; `results/week3_stage_a_f5`; `results/week3_evaluation_repro_runs`
Commit: `bd7bb098167d7006ac88d633fed33e6674ac1cee`
SHA256 / provenance: closure record = `24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C`; clean-run identity and F5 provenance are recorded in the closure record.
Final Status: ARCHIVED_PILOT_ONLY; `WEEK3_SCIENTIFIC_CLOSURE = PASS`

## E-W3-BOUNDARY-CORE

Evidence ID: `E-W3-BOUNDARY-CORE`
Week / Experiment: Week 3 boundary/core decomposition
Scientific Question: Is the tested F5 response stronger around manipulated boundaries than in manipulated core regions?
Population: The same frozen 23-case Stage-A F5 population
Protocol Status: FROZEN_SECONDARY_DECOMPOSITION; not a new population
Outcome Observed: Boundary response exceeded core response under the named frozen F5 condition.
Primary Result: The result is a scoped boundary/core asymmetry in the tested condition.
Allowed Interpretation: “Under the frozen F5 condition, detector response was stronger around manipulated boundaries than in manipulated core regions.”
Forbidden Interpretation: “Partial deepfake localizers generally depend on boundary artifacts.”
Top-Conference Role: Pilot motivation for a prospective robustness-decoupling question.
Primary Artifact Paths: `research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md`; Week3 Stage-A result manifests and evaluation outputs
Commit: `bd7bb098167d7006ac88d633fed33e6674ac1cee`
SHA256 / provenance: closure record = `24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C`.
Final Status: ARCHIVED_SCOPED_PILOT_EVIDENCE

## E-W4-ADAPTIVE-REDTEAM

Evidence ID: `E-W4-ADAPTIVE-REDTEAM`
Week / Experiment: Week 4 Validation01 and Held-out01 adaptive red-team protocol
Scientific Question: Under the preregistered adaptive protocol, is primary H4 reportable after strict terminal-case accounting?
Population: Validation 12 cases; Held-out 12 cases; no replacement, dropping, fallback parent, or query transfer
Protocol Status: EXECUTION_COMPLETE; frozen scientific closure PASS
Outcome Observed: Validation 7 winners/5 no-valid-parent; Held-out 10 winners/2 no-valid-parent; zero other failures
Primary Result: Primary H4 is `NOT_REPORTABLE` because strict 12/12 winner eligibility was not met.
Allowed Interpretation: “The preregistered held-out adaptive protocol completed with 10/12 valid adaptive winners and 2/12 terminal NO_VALID_ADAPTIVE_PARENT cases; under the frozen strict reportability rule, primary H4 was therefore not reportable.”
Forbidden Interpretation: The attack failed; adaptive attacks do not affect localization; or a counterfactual H4 value after excluding the two cases.
Top-Conference Role: Historical pilot boundary and governance evidence only; not a confirmatory H4 result.
Primary Artifact Paths: `research_assurance/WEEK4_VALIDATION_01_REPORT.md`; `research_assurance/WEEK4_HELDOUT_01_FINAL_REPORT.md`; `research_assurance/WEEK4_HELDOUT_01_POSTRUN_INTEGRITY_REVIEW.md`; `results/week4_adaptive_redteam_runs/week4_validation_01`; `results/week4_adaptive_redteam_runs/week4_heldout_01`
Commit: execution bound to `68ce71e8e87a93c4ae653c7ae5f554521086e5bf`; evidence preserved locally in `7a1ccddda86681d87f725d6b56b8722eadf372fd`.
SHA256 / provenance: Held-out final report = `5953C6B438B69A148AE3C4997B4802572F11BFD1087172F6380B74768CE839F9`; postrun review = `AFB1307D4D90DC0BF7793BB8E2A2276B834322290F99970A47A115CDDE91B477`; A0 freeze = `365BEEDA158A93B4F458687AE2C4CA1887B0849E1F467041F316CB3EFF3666BA`; source manifest = `5B47CE12D68AF1EC376C7747AC2334C28D374E361A40E265C3B276B25F5711A5`; authorization = `299631FF47E80937AFEE362FA8A10B61278DAF2CE03CDB542F615FBF4A7B6F79`.
Final Status: ARCHIVED_PILOT_ONLY; NOT_REPORTABLE is a valid frozen-protocol terminal state, not an infrastructure failure.

## E-W5-EXP1

Evidence ID: `E-W5-EXP1`
Week / Experiment: Week 5 Exp1 boundary/core recoverability qualification
Scientific Question: Does the fixed qualification feature family improve scoped boundary/core localization?
Population: 69 qualification cases; 12 qualification-test cases
Protocol Status: QUALIFICATION_ONLY; isolated Week5 branch/worktree
Outcome Observed: Boundary-aware direction was `WEAK_GO`; generator-OOD strong claim was not reportable.
Primary Result: Qualification evidence supported pursuing Exp2, not robust cross-generator generalization.
Allowed Interpretation: A scoped qualification signal under the fixed population and available generators.
Forbidden Interpretation: Confirmatory superiority or robust OOD generalization.
Top-Conference Role: Pilot motivation only.
Primary Artifact Paths: isolated `AudiobookBench-CN-Week5/research_assurance/week5/WEEK5_EXP1_REPORT.md`; branch `week5-defender-recovery`
Commit: `d758eccf492a681e08e4faad591fde583f358769` for the preserved Exp1–Exp4 history
SHA256 / provenance: report = `24AEEF52E59E6E550E987E8A335730F42E0FB6EFD4A86820EE3362A97786FC0B`; isolated worktree only.
Final Status: ARCHIVED_PILOT_ONLY; `WEAK_GO`

## E-W5-EXP2

Evidence ID: `E-W5-EXP2`
Week / Experiment: Week 5 Exp2 multiscale core/context and generator-OOD qualification
Scientific Question: Does multiscale context improve core localization and transfer across generators?
Population: 92 qualification cases; 16 qualification-test cases; 3 OOD folds
Protocol Status: QUALIFICATION_ONLY; isolated Week5 branch/worktree
Outcome Observed: `WEAK_GO`; controlled-splice OOD degradation was retained and generator-OOD transfer was mixed.
Primary Result: Aggregate/boundary gains were directional; core gain and transfer remained limited.
Allowed Interpretation: Scoped qualification evidence motivating a new question.
Forbidden Interpretation: Robust cross-generator recovery or final-test confirmation.
Top-Conference Role: Pilot motivation only.
Primary Artifact Paths: isolated `AudiobookBench-CN-Week5/research_assurance/week5/WEEK5_EXP2_REPORT.md`; branch `week5-defender-recovery`
Commit: `d758eccf492a681e08e4faad591fde583f358769`
SHA256 / provenance: report = `D2564076B4043AE01CB203D607B6EFA2E0EB1C62584BB0C331389542DA739FA0`; isolated worktree only.
Final Status: ARCHIVED_PILOT_ONLY; `WEAK_GO`

## E-W5-EXP3

Evidence ID: `E-W5-EXP3`
Week / Experiment: Week 5 Exp3 generator-diverse representation qualification
Scientific Question: Can the tested representation-learning heads improve mean/worst generator-OOD localization?
Population: 92 qualification cases; 3 OOD folds
Protocol Status: QUALIFICATION_ONLY; scientific gate `NO_GO`
Outcome Observed: No improvement in mean OOD, worst-generator OOD, or controlled-splice recovery.
Primary Result: The current small-head representation-learning design degraded relative to the frozen Exp2 baseline.
Allowed Interpretation: Negative qualification result for the tested design.
Forbidden Interpretation: Generator-diverse representation learning is impossible.
Top-Conference Role: Pilot negative result; informs a separately preregistered question.
Primary Artifact Paths: isolated `AudiobookBench-CN-Week5/research_assurance/week5/WEEK5_EXP3_REPORT.md`; branch `week5-defender-recovery`
Commit: `d758eccf492a681e08e4faad591fde583f358769`
SHA256 / provenance: report = `7EDB8578F60B2B33373A2EAEDECC408E975DDCBB49023967FE356064CCD195BE`; isolated worktree only.
Final Status: ARCHIVED_PILOT_ONLY; `NO_GO`

## E-W5-EXP4

Evidence ID: `E-W5-EXP4`
Week / Experiment: Week 5 Exp4 frozen SSL/Chinese HuBERT representation qualification
Scientific Question: Does the tested frozen Chinese HuBERT replacement recover OOD or controlled-splice localization?
Population: 92 qualification cases; 3 OOD folds
Protocol Status: QUALIFICATION_ONLY; frozen SSL gate `NO_GO`
Outcome Observed: No mean/worst OOD improvement; controlled-splice OOD decreased.
Primary Result: The tested frozen Chinese HuBERT representation did not improve under the unchanged temporal contract.
Allowed Interpretation: Scoped non-improvement of the tested frozen Chinese HuBERT representation.
Forbidden Interpretation: SSL representations cannot solve the problem.
Top-Conference Role: Pilot negative result and motivation only.
Primary Artifact Paths: isolated `AudiobookBench-CN-Week5/research_assurance/week5/WEEK5_EXP4_REPORT.md`; branch `week5-defender-recovery`
Commit: no committed Exp4 report in the branch tip; the preserved branch tip is `d758eccf492a681e08e4faad591fde583f358769`.
SHA256 / provenance: report = `1C561800291DE7E3C91170AD00D90E6E07E985BA03BFE3DE9F7B46AAF01DAD77`; isolated, untracked worktree material.
Final Status: ARCHIVED_PILOT_ONLY; `NO_GO`

## E-W5-EXP5

Evidence ID: `E-W5-EXP5`
Week / Experiment: Week 5 Exp5 learned temporal encoder qualification
Scientific Question: Does the tested ECAPA-based temporal encoder improve generator-OOD localization?
Population: 92 qualification cases; 3 OOD folds
Protocol Status: QUALIFICATION_ONLY; main branch does not accept this isolated worktree material
Outcome Observed: No mean/worst OOD improvement and no controlled-splice recovery.
Primary Result: The tested ECAPA-based temporal encoder did not improve over the frozen Exp2 baseline.
Allowed Interpretation: Scoped non-improvement of the tested frozen ECAPA-based temporal encoder.
Forbidden Interpretation: Temporal modeling does not work.
Top-Conference Role: Pilot negative result only; no Exp6 or Exp7 is authorized by this register.
Primary Artifact Paths: isolated `AudiobookBench-CN-Week5/research_assurance/week5/WEEK5_EXP5_REPORT.md`
Commit: NONE; file is untracked in the isolated Week5 worktree.
SHA256 / provenance: report = `DEAE614DA4AC3D1463BB634B324FB2FDBAAB15C448F906E3CB6574EDB81E52F0`; not imported into the authoritative main archive.
Final Status: ARCHIVED_AS_UNCOMMITTED_PILOT_RECORD; `NO_GO`

## Archival boundary

The isolated Week5 worktree is not the authoritative Week4 input and is not
modified by this archive operation. Its untracked Exp5/Exp6 materials are not
promoted to committed confirmatory evidence. Week5 Exp6 and Exp7 therefore do
not enter the evidence register as accepted experiments.
