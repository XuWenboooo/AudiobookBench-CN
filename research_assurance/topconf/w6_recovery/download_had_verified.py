from __future__ import annotations

import hashlib
import os
import subprocess
import sys


URL = "https://zenodo.org/records/10377492/files/HAD.zip"
OUTPUT = os.path.join(
    os.path.dirname(__file__), "artifacts", "HAD.zip.part"
)
SIZE = 8_073_665_280
EXPECTED_MD5 = "4daef62a7cf20c71b052635c968ece1c"
CHUNK = 8 * 1024 * 1024
RANGE_SIZE = 512 * 1024 * 1024


def fetch_range(start: int, end: int) -> None:
    expected = end - start + 1
    header_path = OUTPUT + ".headers"
    command = [
        "curl.exe",
        "-k",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--retry",
        "3",
        "--retry-all-errors",
        "--connect-timeout",
        "30",
        "--max-time",
        "3600",
        "--range",
        f"{start}-{end}",
        "--dump-header",
        header_path,
        "--output",
        "-",
        URL,
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    written = 0
    with open(OUTPUT, "r+b", buffering=0) as target:
        target.seek(start)
        while written < expected:
            block = process.stdout.read(min(CHUNK, expected - written))
            if not block:
                break
            target.write(block)
            written += len(block)
    extra = process.stdout.read(1)
    return_code = process.wait()
    headers = open(header_path, encoding="ascii", errors="replace").read()
    expected_range = f"content-range: bytes {start}-{end}/{SIZE}"
    if return_code != 0:
        raise RuntimeError(f"curl failed for {start}-{end}: exit={return_code}")
    if expected_range not in headers.lower():
        raise RuntimeError(f"unexpected response headers for {start}-{end}: {headers!r}")
    if written != expected or extra:
        raise RuntimeError(f"wrong response length for {start}-{end}: {written}/{expected}")
    print(f"RANGE_DONE {start} {end} {written}", flush=True)


def main() -> int:
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "ab") as target:
        target.truncate(SIZE)
    for start in range(0, SIZE, RANGE_SIZE):
        fetch_range(start, min(SIZE - 1, start + RANGE_SIZE - 1))
    digest = hashlib.md5()
    with open(OUTPUT, "rb", buffering=0) as source:
        while block := source.read(CHUNK):
            digest.update(block)
    actual = digest.hexdigest()
    print(f"MD5 {actual}", flush=True)
    if actual != EXPECTED_MD5:
        raise RuntimeError(f"MD5 mismatch: {actual} != {EXPECTED_MD5}")
    print(f"VERIFIED {SIZE}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
