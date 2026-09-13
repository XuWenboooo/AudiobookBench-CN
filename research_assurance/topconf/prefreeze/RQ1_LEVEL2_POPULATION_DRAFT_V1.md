# RQ1 Level-2 Population Design Draft v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

Level 2 is a fresh outcome-blind confirmatory regime, not a novelty claim. This
document designs candidate bands only; it does not create, download, inspect,
or materialize a Level-2 population.

## Candidate population bands

| Band | Source recordings | Speakers | Mechanisms | Approx. variants before failures | Trade-off |
|---|---:|---:|---:|---:|---|
| Low-budget candidate | 300 | 100 | 3 | ~900--1,200 | Lower compute and annotation burden; less speaker and mechanism coverage. |
| Target candidate | 400 | 120 | 4 | ~1,600--2,000 | Better balance for paired mechanism and transformation cells; still feasible for a single-lab workflow. |
| Stretch candidate | 500 | 150+ | 4 | ~2,000--2,500 | Stronger speaker/distribution coverage but higher generation, QC, storage, and failure-accounting cost. |

These numbers are planning bands, not a final sample size or power claim. The
final band must be selected before any outcome is inspected and must remain
compatible with available paradigms, rights, and compute.

## Source and speaker design

- Use long-form Mandarin speech with source recordings long enough to contain
  multiple plausible target positions; record source duration and session ID.
- Prefer a broad speaker pool with speaker-disjoint splits. Report gender or
  other demographic balance only when available, legally appropriate, and
  scientifically justified; do not infer identity from metadata.
- Include multiple recording conditions and sessions where rights permit, while
  keeping source identity, session, and recording channel in the manifest.
- Keep an utterance/session structure that permits repeated paired edits without
  reusing the same target content in multiple roles unintentionally.

## Target placement and linguistic diversity

- Sample target regions by a frozen placement rule over speech-bearing portions,
  not by visualizing labels or detector scores.
- Predeclare duration bands and the relation between target duration and total
  duration. Keep the same target position and text across paired mechanisms
  whenever feasible.
- Cover lexical, phonetic, prosodic, and syntactic contexts relevant to Mandarin
  without making language or long-form status a novelty claim.
- Preserve an untouched clean counterpart for every source and a manifest of
  the exact target span; source and target text must be versioned.

## Splits and reference policy

- Speaker-disjoint train/dev/calibration/test splits are the default candidate.
- Source- and session-disjoint test material are preferred when the source
  corpus contains repeated recordings. No source family may cross a held-out
  boundary through near-duplicate audio.
- References for voice-conditioned generation must come from a separately
  authorized reference pool, use the same speaker where feasible, and be a
  different utterance/text from the target source. Reference identity and hash
  belong in the private manifest.
- Do not choose a “best” reference using Level-2 quality, detector, localizer,
  or failure outcomes. A deterministic predeclared rule is required.
- The reference is generator input only and is not detector input.

## Paired counterfactual unit

The preferred unit is:

```text
same source + same speaker + same linguistic context + same target position
+ same target text where feasible + different declared mechanism
```

This reduces speaker, content, location, duration, and source-quality
confounding. When a mechanism cannot preserve one field, the deviation and
its reason must be recorded rather than silently creating an unmatched pair.
