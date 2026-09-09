"""Fail-closed validation of sample-first Week3 zone provenance."""
from __future__ import annotations

from typing import Any

ZONES = ("FULL_ATTACK", "STRICT_CORE", "BOUNDARY_BLEND", "OUTSIDE_CLEAN")

def verify_sample_first_gt(row: dict[str, Any], gt_rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = ("attack_start_sample", "attack_end_sample", "attack_core_start_sample", "attack_core_end_sample",
                "blend_in_start_sample", "blend_in_end_sample", "blend_out_start_sample", "blend_out_end_sample")
    if any(row.get(k) in (None, "") for k in required):
        raise ValueError("sample-first GT bounds missing")
    if not gt_rows:
        raise ValueError("sample-first GT projection is empty")
    if any("window_index" not in item or "zone" not in item for item in gt_rows):
        raise ValueError("GT rows lack deterministic window/zone membership")
    allowed = {"core", "boundary", "outside"}
    if any(item["zone"] not in allowed for item in gt_rows):
        raise ValueError("invalid GT zone")
    zone_map = {"STRICT_CORE": "core", "BOUNDARY_BLEND": "boundary", "OUTSIDE_CLEAN": "outside"}
    return {"status": "PASS", "zones": {name: sum((item["is_attack_window"] if name == "FULL_ATTACK" else item["zone"] == zone_map[name]) for item in gt_rows) for name in ZONES}, "sample_authoritative": True}
