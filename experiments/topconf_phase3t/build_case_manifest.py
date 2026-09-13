from __future__ import annotations

import argparse
from pathlib import Path

from common import materialize_manifest_rows, sha256_file, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the frozen audio-only PartialEdit E1 case manifest")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--audio-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = materialize_manifest_rows(args.csv, args.audio_root)
    write_manifest(args.output, rows)
    print(f"MANIFEST_CASES={len(rows)}")
    print(f"MANIFEST_SHA256={sha256_file(args.output)}")


if __name__ == "__main__":
    main()

