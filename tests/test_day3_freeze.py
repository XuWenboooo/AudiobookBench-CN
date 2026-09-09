from __future__ import annotations

import hashlib
from pathlib import Path


EXPECTED_DAY3_SHA256 = {
    "configs/day3_aishell3_pilot.yaml": "5ABBF04AD741500D314EEA0EF4285C97EF0A538C0E9416A587F9933D3D49C36E",
    "data/manifests/source_audio.csv": "6F6D165B020416DA3153DC4D129E06998ED0A193C88C932C5CDF03B72E04A596",
    "data/manifests/week1_manifest.csv": "B1D77517031AAB2D02D29A7978CE3FA44097E23E9CC69095786D4746179C7264",
    "DAY3_REAL_DATA_REPORT.md": "A567BA2BD85ACD8401A7E5B7C733969E57792FC96832A270D100BF4DC67B426E",
}


def test_day3_frozen_hashes_still_match() -> None:
    repository = Path(__file__).resolve().parents[1]
    actual = {
        relative: hashlib.sha256((repository / relative).read_bytes()).hexdigest().upper()
        for relative in EXPECTED_DAY3_SHA256
    }
    assert actual == EXPECTED_DAY3_SHA256
