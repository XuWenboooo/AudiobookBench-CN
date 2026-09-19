# PartialSpoof v1.2 integrity and adapter audit v1

Audit date: `2026-09-19`

## Official archive identity

```text
SOURCE = https://zenodo.org/records/5766198
FILE = database_eval.tar.gz
EXPECTED_SIZE_BYTES = 5803817500
OBSERVED_SIZE_BYTES = 5803817500
EXPECTED_MD5 = 79c7c834d0d9979ecd374a98a059ea19
OBSERVED_MD5 = 79c7c834d0d9979ecd374a98a059ea19
ARCHIVE_INTEGRITY = PASS
ISOLATED_EXTRACTION = PASS
```

## Audio and identity audit

The extracted official archive contains 71,237 WAV files. A full WAV-header
scan found zero decode errors, all files at 16 kHz and one channel, positive
durations from 0.4815625 s to 18.200125 s, and no duplicate stems.

The archive's own `database/eval/eval.lst` contains 71,239 unique non-empty
identifiers. Two identifiers have no corresponding audio path in the same
official archive:

```text
CON_E_0034982
CON_E_0058039
```

The two identifiers also do not occur in the materialized official segment
label/VAD metadata. There are no extra WAV stems relative to the list.

```text
WAV_COUNT = 71237
EVAL_LIST_COUNT = 71239
MISSING_AUDIO_FOR_LIST_ENTRIES = 2
EXTRA_AUDIO = 0
DUPLICATE_AUDIO_STEMS = 0
DECODEABILITY = PASS_FOR_ALL_71237
SAMPLE_RATE = 16000_FOR_ALL_71237
CHANNELS = 1_FOR_ALL_71237
DURATION_SANITY = PASS_FOR_ALL_71237
GT_BINDING = FAIL_CLOSED_UNTIL_TWO_ENTRY_MISMATCH_IS_RECONCILED
ADAPTER = NOT_READY
W7_DISTRIBUTION_READY = NO
```

The MD5 match proves that this is the official archive, not that the archive
is internally complete for the frozen adapter. No entries were silently
dropped and no GT was synthesized.
