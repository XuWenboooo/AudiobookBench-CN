"""Fail-closed resumable downloader + integrity verifier for the HAD.zip artifact.

Replacement for `download_had_verified.py`. The v1 script assembled 512 MB
ranges onto a pre-truncated sparse file via `curl.exe -k ... --output -` and
recorded an MD5 mismatch at the correct total size. This version differs in
four ways that matter for a provenance-bound artifact:

1. TLS verification stays ON (v1 passed `-k`, which disables certificate
   validation for an 8 GB integrity-critical transfer).
2. Resume is delegated to HTTP Range against the *existing* partial file,
   with the 200-vs-206 response handled explicitly (v1 pre-truncated the
   file to the full size before writing any bytes, so a range that silently
   returned a full-body 200 could not be detected by length alone).
3. Disk space is checked before a single byte is fetched. On 2026-09-19
   `F:` had ~3.5 GB free against an 8.07 GB artifact.
4. A matching MD5 is not accepted as sufficient. The container is opened and
   every member CRC is verified, because the failure mode observed was a
   valid central directory over a corrupt payload.

Nothing here is executed automatically, and no scientific artifact is read or
produced. This script only moves and verifies bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

import requests

URL = "https://zenodo.org/records/10377492/files/HAD.zip"
OFFICIAL_SIZE = 8_073_665_280
OFFICIAL_MD5 = "4daef62a7cf20c71b052635c968ece1c"
CHUNK = 8 * 1024 * 1024
DEFAULT_ATTEMPTS = 5
# Zenodo has been observed returning `retry-after: 60` with a 60-request
# window. Back off on the server's terms rather than a fixed sleep.
DEFAULT_BACKOFF = 30.0


class IntegrityFailure(RuntimeError):
    """Raised when an artifact fails a check. Always fails closed."""


def _free_bytes(path: Path) -> int:
    anchor = path
    while not anchor.exists() and anchor != anchor.parent:
        anchor = anchor.parent
    return shutil.disk_usage(anchor).free


def check_disk_space(dest: Path, needed: int, headroom: int) -> None:
    free = _free_bytes(dest)
    if free < needed + headroom:
        raise IntegrityFailure(
            f"insufficient space on {dest.drive or dest.anchor}: "
            f"free={free:,} needed={needed:,} headroom={headroom:,} "
            f"shortfall={needed + headroom - free:,}"
        )


def _retry_after(response: requests.Response, default: float) -> float:
    raw = response.headers.get("Retry-After")
    if raw is None:
        return default
    try:
        return max(float(raw), 0.0)
    except ValueError:
        return default


def download(url: str, part: Path, expected_size: int) -> None:
    """Fetch `url` into `part`, resuming from whatever is already there."""
    part.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, DEFAULT_ATTEMPTS + 1):
        existing = part.stat().st_size if part.exists() else 0
        if existing > expected_size:
            raise IntegrityFailure(
                f"{part.name} is larger than the official size: "
                f"{existing:,} > {expected_size:,}; refusing to resume"
            )
        if existing == expected_size:
            print(f"[resume] {part.name} already at full size {existing:,}")
            return

        headers = {"Range": f"bytes={existing}-"} if existing else {}
        mode = "ab" if existing else "wb"
        started = time.time()
        try:
            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=(30, 180),
                allow_redirects=True,
            ) as response:
                if existing and response.status_code == 200:
                    # Server ignored our Range and is resending the whole body.
                    # Appending would duplicate bytes while still reaching the
                    # correct total length -- the exact v1 failure shape.
                    print("[resume] server ignored Range (200); restarting from 0")
                    response.close()
                    part.unlink(missing_ok=True)
                    continue
                response.raise_for_status()
                if existing and response.status_code != 206:
                    raise IntegrityFailure(
                        f"expected 206 for a ranged resume, got "
                        f"{response.status_code}"
                    )
                with part.open(mode) as handle:
                    for block in response.iter_content(chunk_size=CHUNK):
                        if block:
                            handle.write(block)
        except (requests.RequestException, IntegrityFailure) as exc:
            if attempt == DEFAULT_ATTEMPTS:
                raise IntegrityFailure(
                    f"download failed after {DEFAULT_ATTEMPTS} attempts: {exc}"
                ) from exc
            delay = DEFAULT_BACKOFF * attempt
            print(f"[retry {attempt}/{DEFAULT_ATTEMPTS}] {exc}; sleeping {delay:.0f}s")
            time.sleep(delay)
            continue

        wrote = part.stat().st_size - existing
        rate = wrote / max(time.time() - started, 1e-6) / 1e6
        print(
            f"[range] +{wrote:,} bytes ({rate:.1f} MB/s) "
            f"-> {part.stat().st_size:,}/{expected_size:,}"
        )

    final = part.stat().st_size
    if final != expected_size:
        raise IntegrityFailure(
            f"size mismatch after download: {final:,} != {expected_size:,}"
        )


def _digest(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
    return digest.hexdigest()


def verify(path: Path, expected_size: int, expected_md5: str) -> dict:
    """Verify size, official MD5, SHA-256, and ZIP member CRCs. Fail closed."""
    size = path.stat().st_size
    if size != expected_size:
        raise IntegrityFailure(f"size {size:,} != official {expected_size:,}")

    print("[verify] computing MD5 ...")
    md5 = _digest(path, "md5")
    if md5 != expected_md5:
        raise IntegrityFailure(f"MD5 {md5} != official {expected_md5}")

    print("[verify] computing SHA-256 ...")
    sha256 = _digest(path, "sha256")

    print("[verify] opening ZIP container and checking every member CRC ...")
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise IntegrityFailure(f"ZIP member failed CRC: {bad}")
            members = len(archive.infolist())
    except zipfile.BadZipFile as exc:
        raise IntegrityFailure(f"not a readable ZIP container: {exc}") from exc

    return {
        "size": size,
        "md5": md5,
        "sha256": sha256.upper(),
        "zip_members": members,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, help="final .zip path")
    parser.add_argument("--url", default=URL)
    parser.add_argument("--size", type=int, default=OFFICIAL_SIZE)
    parser.add_argument("--md5", default=OFFICIAL_MD5)
    parser.add_argument(
        "--headroom",
        type=int,
        default=2 * 1024**3,
        help="free space to leave after the download (default 2 GiB)",
    )
    parser.add_argument("--report", help="write a JSON verification report here")
    parser.add_argument(
        "--check-space-only",
        action="store_true",
        help="report free space and exit without downloading",
    )
    args = parser.parse_args()

    dest = Path(args.dest).resolve()
    part = dest.with_suffix(dest.suffix + ".part")

    try:
        check_disk_space(dest, args.size, args.headroom)
    except IntegrityFailure as exc:
        print(f"SPACE_FAIL {exc}", file=sys.stderr)
        return 2

    if args.check_space_only:
        print(f"SPACE_OK free={_free_bytes(dest):,} needed={args.size:,}")
        return 0

    try:
        download(args.url, part, args.size)
        result = verify(part, args.size, args.md5)
    except IntegrityFailure as exc:
        # The partial file is deliberately left in place so the failure can be
        # inspected. Removing it is a human decision, never this script's.
        print(f"VERIFY_FAIL {exc}", file=sys.stderr)
        return 1

    os.replace(part, dest)
    report = {"url": args.url, "destination": str(dest), **result}
    print(json.dumps(report, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"VERIFIED {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
