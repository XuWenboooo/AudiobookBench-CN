# HQ-MPSD English integrity and adapter audit v1

Audit date: `2026-09-20`  
Source: official Zenodo record `17929533`, file `English.zip`  
License recorded by the official API: `CC BY 4.0`

## Transfer and integrity

```text
OFFICIAL_SIZE = 3,204,831,988
OFFICIAL_MD5 = c89346355d9afb0ba8dca4247c35dbe6
LOCAL_SIZE = 3,204,831,988
LOCAL_MD5 = 0d007ce820e7a7d3300f72662447668b
SIZE_CHECK = PASS
MD5_CHECK = FAIL
ZIP_CONTAINER = FAIL (BadZipFile: central directory not readable)
```

The official endpoint returned valid small `206` range responses, but larger
range transfers repeatedly ended in incomplete reads or connection resets.
The full-size local file is therefore not an accepted archive. It is not
extracted, and no audio or frame-label adapter is promoted from it.

```text
AUDIO_GT_BINDING = NOT_AUDITED
ADAPTER = NOT_READY
READY_FOR_W7 = NO
OUTCOME_GUIDED = NO
```
