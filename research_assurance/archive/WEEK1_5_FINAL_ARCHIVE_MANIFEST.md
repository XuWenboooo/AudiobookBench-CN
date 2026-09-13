# Week 1–5 Final Archive Manifest

Archive timestamp: `2026-09-13` (Asia/Shanghai)
Repository: `F:\项目\申请实验室  TTS项目\AudiobookBench-CN`
Authoritative branch: `main`
Local HEAD before archive commit: `7a1ccddda86681d87f725d6b56b8722eadf372fd`
Remote `origin/main` at archive start: `68ce71e8e87a93c4ae653c7ae5f554521086e5bf`
Remote sync: pending because the remote was not reachable during the archive operation.
Archive commit: recorded in the final handoff output; this manifest is intentionally not self-hashed.

```text
WEEK1_5_RESEARCH_PHASE = ARCHIVED
WEEK1_5_NEW_EXPERIMENTS_ALLOWED = NO
WEEK1_5_DATA_ROLE = PILOT_ONLY
WEEK1_5_CONFIRMATORY_USE = PROHIBITED
WEEK4_SCIENTIFIC_CLOSURE = PASS
WEEK4_PRIMARY_H4 = NOT_REPORTABLE
WEEK5_EXP6 = CANCELLED_UNEXECUTED
WEEK5_EXP7 = NOT_AUTHORIZED
TOPCONF_CONFIRMATORY_PHASE = SEPARATE_RESEARCH_PHASE
```

## Phase status

- Week1: controlled splice / canonical localization baseline archived as pilot evidence; freeze and 696-entry hash chain retained.
- Week2: CosyVoice2 mechanism-shift pilot scientifically complete with bounded transfer and diagnostic interpretation; original Day13 gate remains HOLD.
- Week3: F5 clean rerun and boundary/core decomposition scientifically complete within the frozen claim boundary.
- Week4: Validation01 and Held-out01 execution complete; scientific closure PASS; primary H4 not reportable under the strict 12/12 winner rule; no rerun authorized.
- Week5 Exp1: `WEAK_GO`, qualification-only.
- Week5 Exp2: `WEAK_GO`, qualification-only; controlled-splice OOD degradation preserved.
- Week5 Exp3: `NO_GO`, qualification-only.
- Week5 Exp4: `NO_GO`, qualification-only; scoped to the tested frozen Chinese HuBERT representation.
- Week5 Exp5: `NO_GO`, qualification-only; scoped to the tested ECAPA-based temporal encoder. The report remains isolated and uncommitted.
- Week5 Exp6: `CANCELLED_UNEXECUTED` for the authoritative archive; no accepted Exp6 result is imported. An isolated worktree contains later untracked material that is explicitly outside this archive and is not treated as accepted evidence.
- Week5 Exp7: `NOT_DESIGNED` and `NOT_AUTHORIZED`; no implementation or execution is part of this archive.

## Provenance and artifact anchors

| Phase | Primary anchor | Commit | SHA256 / status |
| --- | --- | --- | --- |
| Week1 | `WEEK1_FREEZE.md`, `results/week1/hashes.json` | `9e67ba880c674884ddf1818e3f2e95f735100b9f`; original freeze says no canonical Git commit | Freeze `BF9EBF086A2D99E46A2C93A95C9F8F4DFA38D32C83A63AE55C96858E4B378105`; chain 696 entries |
| Week2 | `research_assurance/WEEK2_SCIENTIFIC_CLOSURE.md` | `9e67ba880c674884ddf1818e3f2e95f735100b9f` | `EC5B0121570E4679272763BD14E08EDE18D47B49455CA8062AF7E861961EAFB3` |
| Week3 | `research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md` | `bd7bb098167d7006ac88d633fed33e6674ac1cee` | `24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C` |
| Week4 Validation | `research_assurance/WEEK4_VALIDATION_01_REPORT.md` | execution `68ce71e…`; evidence local in `7a1ccdd…` | `CF39B878971EBC8B89ADE234E51F52CBD4B1679F5A252D31570861FEB2B870D3` |
| Week4 Held-out | `research_assurance/WEEK4_HELDOUT_01_FINAL_REPORT.md`, postrun review | execution `68ce71e…`; evidence local in `7a1ccdd…` | report `5953C6B438B69A148AE3C4997B4802572F11BFD1087172F6380B74768CE839F9`; review `AFB1307D4D90DC0BF7793BB8E2A2276B834322290F99970A47A115CDDE91B477` |
| Week4 freeze | `research_assurance/WEEK4_POST_VALIDATION_A0_FREEZE.md` | `68ce71e…` | `365BEEDA158A93B4F458687AE2C4CA1887B0849E1F467041F316CB3EFF3666BA` |
| Week4 source manifest | `research_assurance/WEEK4_EXECUTION_SOURCE_MANIFEST.json` | `68ce71e…` | `5B47CE12D68AF1EC376C7747AC2334C28D374E361A40E265C3B276B25F5711A5` |
| Week5 | isolated `AudiobookBench-CN-Week5` worktree | branch tip `d758eccf492a681e08e4faad591fde583f358769` | Exp1–Exp3 report hashes are listed in the evidence register; Exp4/Exp5 are isolated uncommitted records |

## Scientific boundaries

Historical results remain forensic/pilot-only. The two Week4 no-parent cases
must remain in the denominator and must not be replaced, regenerated, rerun,
or converted into parents. Week4 primary H4 cannot be reported from the
10-winner subset. No new F5, detector, evaluator, bootstrap, Held-out, or
Week5 Exp6/Exp7 execution is authorized by this archive.

## Remote and integrity limitations

The main worktree was clean before the archive. The archive commit is local;
remote synchronization is pending if the network remains unavailable. The
isolated Week5 worktree is intentionally not cleaned, staged, or modified.
