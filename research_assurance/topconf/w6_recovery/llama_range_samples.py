"""Deterministic multi-position Range test for the official Llama archive."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

URL = "https://zenodo.org/api/records/14214149/files/R01TTS.0.b.tgz/content"
TOTAL = 12_791_859_200
SAMPLE = 1 * 1024 * 1024


def fetch(start: int, end: int) -> tuple[bytes, dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix="topconf_llama_range_") as d:
        body = Path(d) / "body"
        headers = Path(d) / "headers"
        subprocess.run(
            [
                "curl.exe", "--ssl-no-revoke", "--fail", "--silent", "--show-error",
                "--location", "--max-time", "120", "--range", f"{start}-{end}",
                "--dump-header", str(headers), "--output", str(body), URL,
            ],
            check=True,
            timeout=135,
        )
        blocks = headers.read_text(encoding="iso-8859-1").split("\r\n\r\n")
        block = next((x for x in reversed(blocks) if "HTTP/" in x), "")
        status = block.splitlines()[0] if block else ""
        parsed = {}
        for line in block.splitlines()[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                parsed[k.lower()] = v.strip()
        payload = body.read_bytes()
    expected = f"bytes {start}-{end}/{TOTAL}"
    if " 206 " not in status or parsed.get("content-range") != expected:
        raise RuntimeError(f"bad range response: {status!r} {parsed!r}")
    if len(payload) != SAMPLE:
        raise RuntimeError(f"bad range length {len(payload)} != {SAMPLE}")
    return payload, parsed


def main() -> None:
    positions = [0, TOTAL // 4, TOTAL // 2, (TOTAL * 3) // 4, TOTAL - SAMPLE]
    records = []
    for start in positions:
        start = (start // SAMPLE) * SAMPLE
        end = start + SAMPLE - 1
        first, headers = fetch(start, end)
        second, second_headers = fetch(start, end)
        digest = hashlib.sha256(first).hexdigest().upper()
        records.append(
            {
                "start": start,
                "end": end,
                "length": len(first),
                "sha256": digest,
                "repeat_same_bytes": first == second,
                "same_content_range": headers.get("content-range")
                == second_headers.get("content-range"),
                "content_range": headers.get("content-range"),
            }
        )
    print(json.dumps({"url": URL, "total": TOTAL, "sample_bytes": SAMPLE, "samples": records}, indent=2))


if __name__ == "__main__":
    main()
