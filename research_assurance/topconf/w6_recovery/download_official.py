"""Resumable downloader for explicitly authorized first-party artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests


def download(url: str, dest: Path, expected_size: int | None) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    existing = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={existing}-"} if existing else {}
    started = time.time()
    with requests.get(url, headers=headers, stream=True, timeout=(30, 120), allow_redirects=True) as r:
        if existing and r.status_code == 200:
            existing = 0
            part.unlink(missing_ok=True)
            r.close()
            return download(url, dest, expected_size)
        r.raise_for_status()
        mode = "ab" if existing else "wb"
        with part.open(mode) as f:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    size = part.stat().st_size
    complete = expected_size is None or size == expected_size
    if complete:
        os.replace(part, dest)
    h = hashlib.sha256()
    with (dest if complete else part).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return {
        "url": url,
        "destination": str(dest),
        "size": size,
        "expected_size": expected_size,
        "complete": complete,
        "sha256": h.hexdigest().upper(),
        "elapsed_seconds": round(time.time() - started, 2),
        "status_code": r.status_code,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--size", type=int, required=True)
    p.add_argument("--manifest", required=True)
    a = p.parse_args()
    try:
        result = download(a.url, Path(a.dest), a.size)
    except Exception as exc:
        result = {"url": a.url, "destination": a.dest, "complete": False, "error": repr(exc)}
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return 1
    Path(a.manifest).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
