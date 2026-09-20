# LlamaPartialSpoof distribution readiness

Status: **READY = YES**

The official Zenodo record [14214149](https://zenodo.org/records/14214149), version `1.0.b`, defines `R01TTS.0.b` as an official package of partially fake speech created with cut/paste or overlap/add. The package is not a locally selected subset. The record and the bundled README identify the corresponding label file, audio identity rule, temporal label format, and CC BY 4.0 license.

## Evidence

- Archive: `R01TTS.0.b.tgz`; official URL is the Zenodo API content endpoint.
- Expected and observed size: `12,791,859,200` bytes.
- Expected and observed MD5: `a4de860a845816fa65785dddd7849700`.
- The file extension says `.tgz`, but the verified payload is an uncompressed tar; all `64,389` members were enumerated successfully, including one directory and `64,388` WAV members.
- The official label file has `64,388` unique IDs and `464,714` temporal segments. Its schema and interval audit passed; the `122` zero-length bonafide markers are explicit no-ops under the official SAL parser semantics, while zero-length spoof intervals remain invalid.
- Every audio member decoded as 16-kHz mono WAV. All `64,388` audio IDs matched the `64,388` GT IDs one-to-one. No missing, extra, duplicate, corrupt, or duration-misaligned case was found.
- The official SAL `llama_partialspoof.py` parser was inspected for adapter compatibility. It consumes the same label grammar and writes spoof intervals while initializing bonafide labels, so the deterministic zero-length bonafide no-op is consistent with the published adapter. No case was manually repaired or dropped.

The full machine-readable evidence is in [`LLAMA_PARTIALSPOOF_DISTRIBUTION_READINESS_V1.json`](LLAMA_PARTIALSPOOF_DISTRIBUTION_READINESS_V1.json).

This closes LlamaPartialSpoof as the second verified external distribution. No W7 inference, Level-2 outcome, or outcome-guided selection was performed.
