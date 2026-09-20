"""Parallel, provenance-bound HAD archive recovery with independent writers."""
from __future__ import annotations

import concurrent.futures
import hashlib
import os
import zipfile
from pathlib import Path

import requests

URL = "https://zenodo.org/records/10377492/files/HAD.zip"
SIZE = 8_073_665_280
MD5 = "4daef62a7cf20c71b052635c968ece1c"
OUT = Path(__file__).parent / "artifacts" / "HAD.zip.part"
RANGE = 64 * 1024 * 1024
BLOCK = 8 * 1024 * 1024
WORKERS = 4


def fetch(bounds: tuple[int, int]) -> str:
    start, end = bounds
    expected = end - start + 1
    headers = {"Range": f"bytes={start}-{end}", "Accept-Encoding": "identity"}
    last_error: Exception | None = None
    for attempt in range(1, 9):
        try:
            with requests.get(URL, headers=headers, stream=True, timeout=(30, 180)) as r:
                r.raise_for_status()
                content_range = r.headers.get("Content-Range", "")
                expected_range = f"bytes {start}-{end}/{SIZE}"
                if r.status_code != 206 or content_range != expected_range:
                    raise RuntimeError(
                        f"range {start}-{end}: status={r.status_code} "
                        f"content-range={content_range!r}"
                    )
                written = 0
                # Every worker owns a separate handle; no seek/write races.
                with OUT.open("r+b", buffering=0) as target:
                    target.seek(start)
                    for block in r.iter_content(chunk_size=BLOCK):
                        if block:
                            if written + len(block) > expected:
                                raise RuntimeError("response exceeded requested range")
                            target.write(block)
                            written += len(block)
                if written != expected:
                    raise RuntimeError(f"short range {written}/{expected}")
                return f"RANGE_DONE {start} {end} {written}"
        except Exception as exc:  # retry transient transport failures only
            last_error = exc
            if attempt < 8:
                continue
    raise RuntimeError(str(last_error))


def digest(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb", buffering=0) as f:
        while block := f.read(BLOCK):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("ab") as f:
        f.truncate(SIZE)
    bounds = [(s, min(SIZE - 1, s + RANGE - 1)) for s in range(0, SIZE, RANGE)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch, item) for item in bounds]
        for future in concurrent.futures.as_completed(futures):
            print(future.result(), flush=True)
    actual = digest(OUT)
    print(f"MD5 {actual}", flush=True)
    if actual != MD5:
        raise SystemExit(f"MD5 mismatch: {actual} != {MD5}")
    with zipfile.ZipFile(OUT) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise SystemExit(f"ZIP CRC failure: {bad}")
        print(f"ZIP_OK members={len(archive.infolist())}", flush=True)


if __name__ == "__main__":
    main()
