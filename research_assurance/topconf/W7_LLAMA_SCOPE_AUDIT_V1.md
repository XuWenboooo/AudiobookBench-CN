# LlamaPartialSpoof frozen scope audit v1

Decision: `LLAMA_REQUIRED_SCOPE_MATERIALIZED = YES`.

The frozen W7 distribution identity is `LlamaPartialSpoof`, version `1.0.b`,
official split `R01TTS.0.b`, Zenodo record `14214149`. The scope is the
official `R01TTS.0.b` package only, as recorded in the W7 execution manifest,
distribution acceptance evidence, and case manifest. It is not the entire
Zenodo record and not a locally selected subset.

The G: physical target now contains, by copy-only migration:

| File | Size | SHA-256 / official identity |
|---|---:|---|
| `R01TTS.0.b.tgz` | 12,791,859,200 | MD5 `a4de860a845816fa65785dddd7849700`; SHA-256 `d2afa57c0cd2a9426ca35d0ace66e40ae68cdb383214c8057a9cd87564196175` |
| `label_R01TTS.0.b.txt` | 14,217,170 | `d0a9b856b3cf7ba09fbbe21507a1224e86aefc85a1893af25736d87454f28e80` |
| `LICENSE.txt` | 18,657 | `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411` |
| `metadata_crossfade.csv` | 1,707,038 | `1a5cb2c9f615d1fe08a05ef6e5e58e496c62bb2576186d3510f4f11587b508fd` |
| `README.txt` | 1,183 | `10b1ba0d567689891615c5745ce408fbf6236f5bab51bf3b19d332553549fa06` |

The package contains 64,388 WAV members and the official label file contains
64,388 unique GT rows. Missing audio, missing GT, duplicate IDs, and
audio/GT identity mismatches are all zero. The scope therefore does not
require migration of unused official `R01TTS.0.a` assets.

The F-path aliases and G physical target are treated as one canonical asset
identity; duplicate discovery is prohibited. No data transformation,
re-encoding, renaming, or scientific selection occurred during migration.
