# W6 transport diagnostics v1

Audit date: `2026-09-20`  
Diagnostic file: official HQ-MPSD English asset
`https://zenodo.org/records/17929533/files/English.zip`

## Small official Range contract

The verified diagnostic path used Windows `curl.exe` with Schannel
certificate validation retained (`--ssl-no-revoke` only avoids an unavailable
revocation lookup). It requested `bytes=0-65535` twice and two adjacent
halves (`0-32767`, `32768-65535`). Both full-range requests returned:

```text
HTTP status = 206
Accept-Ranges = bytes
Content-Length = 65536
Content-Range = bytes 0-65535/3204831988
```

```text
RANGE_REPEAT_SAME_BYTES = YES
RANGE_SHA256 = E6959E13EDDD5C7C3FBC6F20BD6DC364BA40B5AF48EA3C209A91127CC1B9828A
ADJACENT_CONCAT_EQUALS_FULL = YES
```

The same test through Python `requests` separately produced
`SSL_UNEXPECTED_EOF`; that path is not used for acceptance-critical transfer.
The curl path proves only small-range determinism, not full-archive
reliability. Previous large-range transfers still produced incomplete reads,
connection resets, MD5 mismatches, or unreadable ZIPs.

## Synthetic parallel writer

```text
FIXTURE_BYTES = 2097152
RANGES = 32
WORKERS = 4
OUT_OF_ORDER = YES
INTERRUPTION_RETRY = YES
SOURCE_SHA256 = A095CB3EC83A81EE83E4F38668EB366AEFEF7E5F70160A044994CEC435295F4C
RECONSTRUCTED_SHA256 = A095CB3EC83A81EE83E4F38668EB366AEFEF7E5F70160A044994CEC435295F4C
PARALLEL_WRITE_TEST = PASS
```

The synthetic test uses independent file handles and explicit offsets; it
simulates an interrupted first write and verifies retry overwrite semantics.

## Storage

```text
FILESYSTEM = NTFS
FREE_BYTES_AT_AUDIT = 27278213120
STORAGE_CHECK = PASS_FOR_SMALL_DIAGNOSTICS
```

Conclusion: `TRANSPORT_PATH = SMALL_RANGE_VERIFIED_BUT_LARGE_TRANSFER_UNRELIABLE`.
The result is insufficient to authorize another blind multi-gigabyte archive
materialization; any future attempt must preserve per-range evidence and
re-verify size, official hash, ZIP structure, and CRC before acceptance.
