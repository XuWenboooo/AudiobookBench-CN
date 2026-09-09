# Day 1 Codex Runbook — Liu Zheli Priority

## Model policy

| Task | Preferred model | Reasoning effort |
|---|---|---|
| File audit | GPT-5.6 Terra | high |
| Import/dependency check | GPT-5.6 Terra | medium/high |
| Threat model design | GPT-5.6 Sol | high |
| If Sol unavailable | GPT-5.6 Terra | xhigh |
| Formatting / small edits | Luna or Terra | low/medium |

Codex cannot reliably switch models by itself inside a task. If the next task requires Sol, it should stop and ask the user to restart with:

```powershell
codex -m gpt-5.6-sol
```

## Day 1 goal

Create exactly:

```text
AUDIT.md
THREAT_MODEL.md
```

Do not refactor, train models, or implement new features on Day 1.

## Task A — AUDIT.md

Scan the repository and identify:

1. all files and their purposes;
2. synthetic/mock/random/demo code;
3. README/code mismatch;
4. missing imports, scripts, or dependencies;
5. hard-coded results or overclaims;
6. data leakage risks;
7. whether real audio loading, VAD, segmentation, speaker embedding, F0, energy, pause, speech rate, segment metadata, and attack timestamps are implemented;
8. mark each module as KEEP / REWRITE / LEGACY / DELETE-CANDIDATE.

## Task B — THREAT_MODEL.md

Prioritize Liu Zheli direction:

- AI security
- open-world robustness
- attack-defense
- attribution
- forensics

Secondary Qin Yong layer:

- temporal responsible evaluation
- evaluator reliability
- human alignment
- uncertainty

Threat model must include attacker capabilities, defender goals, manipulation types, known/unseen generator settings, cross-attack setting, channel-shift setting, adaptive attacker reserved for Week 5, metrics, risks, and what not to claim yet.
