# Day 3 Data Freeze

Freeze timestamp: `2026-09-04T21:28:04+08:00`  
Git commit: `NOT AVAILABLE` (the canonical repository has no `.git` metadata)

## Frozen Files (SHA256)

| File | SHA256 |
|---|---|
| `configs/day3_aishell3_pilot.yaml` | `5ABBF04AD741500D314EEA0EF4285C97EF0A538C0E9416A587F9933D3D49C36E` |
| `data/manifests/source_audio.csv` | `6F6D165B020416DA3153DC4D129E06998ED0A193C88C932C5CDF03B72E04A596` |
| `data/manifests/week1_manifest.csv` | `B1D77517031AAB2D02D29A7978CE3FA44097E23E9CC69095786D4746179C7264` |
| `DAY3_REAL_DATA_REPORT.md` | `A567BA2BD85ACD8401A7E5B7C733969E57792FC96832A270D100BF4DC67B426E` |

These hashes describe the Day 3 files before any Day 3.5 work. Day 3.5 uses
new files and optional extension fields; it does not rewrite these frozen
artifacts.

## Frozen Dataset Summary

- Source samples: 200
- Segments: 217
- Speakers: 5
- Source split counts: train=120, val=40, test=40
- Segment split counts: train=135, val=42, test=40
- Target sample rate: 16,000 Hz
- Fixed window: 5.0 s
- Minimum tail: 1.0 s; a shorter final tail is merged
- Energy-VAD threshold ratio: 0.25 (sanity diagnostic only)

## Pilot Selection Rule

Five speakers were selected deterministically from speakers with at least 40
valid WAV/transcript/metadata rows. The four gender/accent combinations use the
lexicographically first eligible speaker; the fifth speaker is the
lexicographically first eligible age-group-C speaker not already selected.
Within each selected speaker, utterances are sorted by utterance ID and the
first 40 are used. No random seed applies and no waveform or model outcome was
used for selection.

Selected speakers: `SSB0005`, `SSB0009`, `SSB0011`, `SSB0073`, `SSB0139`.

Pilot splits are speaker-disjoint: the first three listed speakers are train,
`SSB0073` is val, and `SSB0139` is test.
