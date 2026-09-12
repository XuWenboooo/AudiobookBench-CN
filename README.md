# AudiobookBench-CN

**A research benchmark for temporal security, forensics, and responsible
evaluation of long-form generative speech.**

AudiobookBench-CN studies whether reliability and security failures that emerge
over time in long-form text-to-speech can be measured, localized, and evaluated
under a frozen, auditable protocol.

## Project status

| Item | Current state |
|---|---|
| Engineering foundation | **Week 1–2 complete** |
| Current milestone | **Week 4 — runtime execution contract incomplete; scientific execution blocked** |
| Clean-rerun engineering controls | **Verified** |
| Active Week4 formal execution authorization | **Historical preflight artifact preserved; not executable pending reauthorization** |
| Week4 formal F5 generation / D0 search / H4 result | **Not started** |

```mermaid
flowchart LR
  W1["✓ Week 1\nFoundation"] -->
  W2["✓ Week 2\nProtocol"] -->
  W3["✓ Week 3\nScientific closure"] -->
  W4["● Week 4\nRuntime contract blocker"] -->
  N["○ Next\nFreeze execution specification"]

  classDef complete fill:#198754,color:#fff,stroke:#146c43;
  classDef current fill:#0d6efd,color:#fff,stroke:#0a58ca;
  classDef next fill:#f8f9fa,color:#343a40,stroke:#6c757d;
  class W1,W2,W3 complete;
  class W4 current;
  class N next;
```

Week 3 is scientifically complete within the frozen claim boundary. The clean
run is an integrity reexecution of the frozen protocol; the earlier Week 3
execution remains forensic-only. See
[the readiness record](research_assurance/WEEK3_CLEAN_RERUN_READINESS.md) and
[the final closure record](research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md).

Week 4 has a frozen adaptive red-team preregistration and finalized 48-case
speaker-disjoint population manifest. Its earlier authorization passed a
zero-side-effect preflight, but was preserved as non-executable historical
evidence after the runtime-contract review found missing frozen execution
semantics. F5 generation, D0 queries, validation/held-out runs, and H4 remain
unstarted. See the [runtime blocker](research_assurance/WEEK4_RUNTIME_DISPATCHER_BLOCKER.md),
[authorization supersession record](research_assurance/WEEK4_AUTHORIZATION_SUPERSESSION.md),
and [preregistration](research_assurance/WEEK4_ADAPTIVE_REDTEAM_PREREGISTRATION.md).

## What is in this repository?

| Area | Contents |
|---|---|
| `src/audiobookbench/` | Data preparation, temporal features, security controls, evaluators, and statistics |
| `experiments/` | Reproducible entry points for the research workflow |
| `configs/` | Versioned protocols, schemas, and frozen experiment configurations |
| `tests/` | Unit, security-contract, and orchestration tests |
| `research_assurance/` | Audits, claim boundaries, integrity decisions, and protocol evidence |
| `docs/` | Research plans and project documentation |
| `data/manifests/` | Versioned metadata manifests and public schema examples — not audio/source data |

## How the evaluation is designed

```mermaid
flowchart LR
  A["Source audio"] --> B["Lineage & validation"]
  B --> C["Frozen evaluation"]
  C --> D["Auditable claim"]
```

Each scientific claim is gated by provenance, validator, and accounting checks.
Synthetic fixtures are used only for software tests and never as formal
research evidence.

## Quick start

```bash
git clone https://github.com/XuWenboooo/AudiobookBench-CN.git
cd AudiobookBench-CN
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -e .
pip install -r requirements.txt
pytest tests/test_manifest.py tests/test_portability.py -q
```

To use real data or model assets, obtain them directly from their original
licensors, configure paths for your own environment, and read the relevant
protocol and assurance documents before running a workflow.

## Reproducibility and data policy

- Audio, source datasets, generated results, model checkpoints, and local
  environments are deliberately excluded from this public release.
- Third-party model repositories are not bundled; obtain them independently
  and comply with their respective licenses.
- Some historical frozen records retain original local paths so their recorded
  hashes remain auditable. They are not portable runtime settings.
- The repository is released under the [MIT License](LICENSE).

## Citation and contact

This is an active research repository. Please cite the repository URL and the
specific protocol or assurance record used in your work. A formal citation
record will be added when the benchmark reaches scientific closure.
