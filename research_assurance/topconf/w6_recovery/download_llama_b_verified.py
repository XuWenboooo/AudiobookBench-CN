"""Verified multi-range recovery for the official LlamaPartialSpoof .b package."""
from __future__ import annotations

import concurrent.futures
import hashlib
import subprocess
import tempfile
from pathlib import Path

URL = "https://zenodo.org/api/records/14214149/files/R01TTS.0.b.tgz/content"
SIZE = 12_791_859_200
MD5 = "a4de860a845816fa65785dddd7849700"
OUT = Path(__file__).parent / "recovery_cache" / "llama_v1.0.b" / "R01TTS.0.b.tgz.part"
RANGE = 64 * 1024 * 1024
BLOCK = 8 * 1024 * 1024
WORKERS = 4


def fetch(bounds: tuple[int, int]) -> str:
    start, end = bounds
    expected = end - start + 1
    for attempt in range(1, 11):
        with tempfile.TemporaryDirectory(prefix="topconf_llama_curl_") as d:
            header_path = Path(d) / "headers.txt"
            process = subprocess.Popen(
                [
                    "curl.exe", "--ssl-no-revoke", "--fail", "--silent", "--show-error",
                    "--location", "--max-time", "600", "--range", f"{start}-{end}",
                    "--dump-header", str(header_path), "--output", "-", URL,
                ],
                stdout=subprocess.PIPE,
            )
            written = 0
            with OUT.open("r+b", buffering=0) as target:
                target.seek(start)
                while written < expected:
                    block = process.stdout.read(min(BLOCK, expected - written))
                    if not block:
                        break
                    target.write(block)
                    written += len(block)
            extra = process.stdout.read(1)
            return_code = process.wait()
            blocks = header_path.read_text(encoding="iso-8859-1").split("\r\n\r\n")
            header_block = next((x for x in reversed(blocks) if "HTTP/" in x), "")
            header_map = {}
            for line in header_block.splitlines()[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    header_map[key.lower()] = value.strip()
            expected_range = f"bytes {start}-{end}/{SIZE}"
            if (
                return_code == 0
                and written == expected
                and not extra
                and " 206 " in (header_block.splitlines()[0] if header_block else "")
                and header_map.get("content-range") == expected_range
            ):
                return f"RANGE_DONE {start} {end} {written} attempt={attempt}"
        if attempt < 10:
            continue
    raise RuntimeError(f"range failed after 10 attempts: {start}-{end}")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("ab") as handle:
        handle.truncate(SIZE)
    bounds = [(s, min(SIZE - 1, s + RANGE - 1)) for s in range(0, SIZE, RANGE)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch, item) for item in bounds]
        for future in concurrent.futures.as_completed(futures):
            print(future.result(), flush=True)
    digest = hashlib.md5()
    with OUT.open("rb", buffering=0) as handle:
        while block := handle.read(BLOCK):
            digest.update(block)
    actual = digest.hexdigest()
    print(f"MD5 {actual}", flush=True)
    if actual != MD5:
        raise SystemExit(f"MD5 mismatch: {actual} != {MD5}")
    print(f"SIZE {OUT.stat().st_size}", flush=True)


if __name__ == "__main__":
    main()
