"""Small-range transport and synthetic writer diagnostics for W6 recovery."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

def get_range(url: str, start: int, end: int) -> tuple[bytes, dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix="topconf_range_") as directory:
        body_path = Path(directory) / "body.bin"
        header_path = Path(directory) / "headers.txt"
        command = [
            "curl.exe", "--ssl-no-revoke", "--fail", "--silent", "--show-error",
            "--location", "--max-time", "60", "--range", f"{start}-{end}",
            "--dump-header", str(header_path), "--output", str(body_path), url,
        ]
        subprocess.run(command, check=True, timeout=75)
        body = body_path.read_bytes()
        blocks = header_path.read_text(encoding="iso-8859-1").split("\r\n\r\n")
        header_block = next((block for block in reversed(blocks) if "HTTP/" in block), "")
        status_line = header_block.splitlines()[0] if header_block else ""
        header_map = {}
        for line in header_block.splitlines()[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                header_map[key.lower()] = value.strip()
    validate_range_contract(status_line, header_map, body, start, end)
    expected_range = header_map.get("content-range", "")
    return body, {
        "status": "206",
        "content_length": header_map.get("content-length", ""),
        "content_range": expected_range,
        "accept_ranges": header_map.get("accept-ranges", ""),
        "etag": header_map.get("etag", ""),
        "last_modified": header_map.get("last-modified", ""),
    }


def validate_range_contract(
    status_line: str, headers: dict[str, str], body: bytes, start: int, end: int
) -> None:
    expected_range = headers.get("content-range", "")
    expected = f"bytes {start}-{end}/"
    if " 206 " not in status_line or not expected_range.startswith(expected):
        raise AssertionError(
            f"range contract failed: status={status_line!r} "
            f"content-range={expected_range!r}"
        )
    total = int(expected_range.rsplit("/", 1)[1])
    if expected_range != f"bytes {start}-{end}/{total}":
        raise AssertionError(f"unexpected returned range: {expected_range!r}")
    if len(body) != end - start + 1:
        raise AssertionError(f"short/extra body: {len(body)} != {end - start + 1}")


def deterministic_range_test(url: str) -> dict[str, object]:
    full, headers = get_range(url, 0, 65_535)
    repeat, repeat_headers = get_range(url, 0, 65_535)
    left, _ = get_range(url, 0, 32_767)
    right, _ = get_range(url, 32_768, 65_535)
    return {
        "range_contract": headers,
        "repeat_same_bytes": full == repeat,
        "repeat_sha256": hashlib.sha256(repeat).hexdigest().upper(),
        "first_sha256": hashlib.sha256(full).hexdigest().upper(),
        "adjacent_concat_equals_full": left + right == full,
        "repeat_headers": repeat_headers,
    }


def synthetic_parallel_writer_test() -> dict[str, object]:
    size = 2 * 1024 * 1024
    source = bytes((i * 37 + 11) % 256 for i in range(size))
    chunk = 64 * 1024
    ranges = [(s, min(size - 1, s + chunk - 1)) for s in range(0, size, chunk)]
    with tempfile.TemporaryDirectory(prefix="topconf_transport_") as directory:
        source_path = Path(directory) / "source.bin"
        reconstructed = Path(directory) / "reconstructed.bin"
        source_path.write_bytes(source)
        with reconstructed.open("wb") as handle:
            handle.truncate(size)

        def write_range(bounds: tuple[int, int]) -> int:
            start, end = bounds
            payload = source[start : end + 1]
            for attempt in range(2):
                with reconstructed.open("r+b", buffering=0) as handle:
                    handle.seek(start)
                    midpoint = len(payload) // 2 if attempt == 0 else len(payload)
                    handle.write(payload[:midpoint])
                    if midpoint != len(payload):
                        # Simulated interrupted worker; retry must overwrite, not append.
                        continue
                    return len(payload)
            with reconstructed.open("r+b", buffering=0) as handle:
                handle.seek(start)
                handle.write(payload)
            return len(payload)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            completed = list(pool.map(write_range, reversed(ranges)))
        actual = reconstructed.read_bytes()
    return {
        "fixture_bytes": size,
        "ranges": len(ranges),
        "out_of_order": True,
        "simulated_interruption_and_retry": True,
        "source_sha256": hashlib.sha256(source).hexdigest().upper(),
        "reconstructed_sha256": hashlib.sha256(actual).hexdigest().upper(),
        "hash_match": source == actual and sum(completed) == size,
    }


def main() -> None:
    url = os.environ.get(
        "TOPCONF_DIAGNOSTIC_URL",
        "https://zenodo.org/records/17929533/files/English.zip",
    )
    report = {
        "url": url,
        "range_test": deterministic_range_test(url),
        "synthetic_parallel_writer_test": synthetic_parallel_writer_test(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
