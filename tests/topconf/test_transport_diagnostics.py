from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).parents[2]
    / "research_assurance"
    / "topconf"
    / "w6_recovery"
    / "transport_diagnostics.py"
)
SPEC = importlib.util.spec_from_file_location("transport_diagnostics", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_synthetic_parallel_writer_is_hash_exact() -> None:
    result = MODULE.synthetic_parallel_writer_test()
    assert result["hash_match"] is True
    assert result["source_sha256"] == result["reconstructed_sha256"]


def test_range_contract_accepts_exact_206() -> None:
    MODULE.validate_range_contract(
        "HTTP/1.1 206 Partial Content",
        {"content-range": "bytes 0-3/10"},
        b"abcd",
        0,
        3,
    )


@pytest.mark.parametrize(
    "status,headers,body",
    [
        ("HTTP/1.1 200 OK", {"content-range": "bytes 0-3/10"}, b"abcd"),
        ("HTTP/1.1 206 Partial Content", {"content-range": "bytes 1-4/10"}, b"abcd"),
        ("HTTP/1.1 206 Partial Content", {"content-range": "bytes 0-3/10"}, b"abc"),
    ],
)
def test_range_contract_rejects_invalid_response(
    status: str, headers: dict[str, str], body: bytes
) -> None:
    with pytest.raises(AssertionError):
        MODULE.validate_range_contract(status, headers, body, 0, 3)
