"""Fail-closed, outcome-blind acceptance of external distribution manifests.

The validator checks identity, temporal-GT structure and manifest integrity. It
does not open a model, score audio, infer labels, or decide scientific
eligibility. ``ready_candidate`` is only a mechanical candidate status; the
project's provenance and human authorization gates remain binding.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


ACCEPTANCE_VALIDATOR_VERSION = "topconf.w7.distribution_acceptance.v1"
SUPPORTED_AUDIO_EXTENSIONS = frozenset({".wav", ".flac", ".mp3", ".ogg", ".m4a"})
SUPPORTED_GT_TYPES = frozenset(
    {
        "intervals_sec",
        "segment_labels",
        "frame_labels",
        "binary_frame_vector",
        "sample_index_intervals",
        "json_interval_list",
        "csv_interval_list",
        "manifest_segment_table",
    }
)


def _empty_report(distribution_id: str = "UNKNOWN", split: str = "UNKNOWN") -> dict[str, Any]:
    return {
        "schema_version": "topconf.w7.distribution_acceptance_result.v1",
        "distribution_identity": {"distribution_id": distribution_id, "split": split},
        "validator_version": ACCEPTANCE_VALIDATOR_VERSION,
        "audio_count": 0,
        "gt_count": 0,
        "matched_count": 0,
        "missing_audio_ids": [],
        "missing_gt_ids": [],
        "duplicate_audio_ids": [],
        "duplicate_gt_ids": [],
        "invalid_intervals": [],
        "duration_mismatches": [],
        "identity_ambiguities": [],
        "split_conflicts": [],
        "manifest_errors": [],
        "unsupported_gt_representations": [],
        "unsupported_audio_extensions": [],
        "frame_count_mismatches": [],
        "sample_count_mismatches": [],
        "unexpected_duplicate_source_mappings": [],
        "unreadable_audio_metadata": [],
        "empty_manipulated_regions": [],
        "audio_identity_pass": False,
        "gt_identity_pass": False,
        "gt_integrity_pass": False,
        "duration_integrity_pass": False,
        "split_integrity_pass": False,
        "license_status": "UNKNOWN",
        "provenance_status": "UNKNOWN",
        "ready_candidate": False,
        "failure_reasons": [],
    }


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _as_key(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _append_unique(values: list[Any], value: Any) -> None:
    if value not in values:
        values.append(value)


def _interval_error(report: dict[str, Any], row_id: str, detail: str) -> None:
    report["invalid_intervals"].append({"audio_id": row_id, "detail": detail})


def _validate_gt_payload(
    report: dict[str, Any], row: Mapping[str, Any], audio_id: str, duration: float, sample_rate: float
) -> None:
    representation = _as_key(row.get("gt_representation_type"))
    if representation not in SUPPORTED_GT_TYPES:
        _append_unique(report["unsupported_gt_representations"], representation or "MISSING")
        return
    payload = row.get("gt_payload")
    if not isinstance(payload, Mapping):
        report["manifest_errors"].append({"audio_id": audio_id, "detail": "gt_payload must be an object"})
        return

    intervals: list[tuple[float, float]] = []
    if representation in {"intervals_sec", "json_interval_list", "csv_interval_list"}:
        raw_intervals = payload.get("intervals")
        if not isinstance(raw_intervals, list):
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "intervals must be a list"})
            return
        for item in raw_intervals:
            if not isinstance(item, Mapping) or "start_sec" not in item or "end_sec" not in item:
                _interval_error(report, audio_id, "malformed interval")
                continue
            start, end = item.get("start_sec"), item.get("end_sec")
            if not _finite(start) or not _finite(end):
                _interval_error(report, audio_id, "NaN or Inf timestamp")
                continue
            start, end = float(start), float(end)
            if start < 0 or end < 0:
                _interval_error(report, audio_id, "negative timestamp")
            elif start >= end:
                _interval_error(report, audio_id, "start must be less than end")
            elif end > duration:
                _interval_error(report, audio_id, "end exceeds audio duration")
            else:
                intervals.append((start, end))
    elif representation in {"segment_labels", "manifest_segment_table"}:
        segments = payload.get("segments")
        if not isinstance(segments, list):
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "segments must be a list"})
            return
        for item in segments:
            if not isinstance(item, Mapping) or not {"start_sec", "end_sec", "label"}.issubset(item):
                _interval_error(report, audio_id, "malformed segment label")
                continue
            start, end, label = item.get("start_sec"), item.get("end_sec"), item.get("label")
            if label not in (0, 1, False, True):
                _interval_error(report, audio_id, "segment label must be binary")
                continue
            if not _finite(start) or not _finite(end):
                _interval_error(report, audio_id, "NaN or Inf timestamp")
                continue
            start, end = float(start), float(end)
            if start < 0 or end < 0 or start >= end or end > duration:
                _interval_error(report, audio_id, "segment interval outside duration")
            elif bool(label):
                intervals.append((start, end))
    elif representation in {"frame_labels", "binary_frame_vector"}:
        labels = payload.get("labels")
        frame_duration = payload.get("frame_duration_sec")
        if not isinstance(labels, list) or not _finite(frame_duration) or float(frame_duration) <= 0:
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "malformed frame label payload"})
            return
        expected_count = payload.get("frame_count")
        if expected_count is not None and expected_count != len(labels):
            report["frame_count_mismatches"].append({"audio_id": audio_id, "expected": expected_count, "actual": len(labels)})
        if payload.get("duration_sec") is not None and (
            not _finite(payload["duration_sec"]) or abs(float(payload["duration_sec"]) - duration) > 1e-6
        ):
            report["duration_mismatches"].append({"audio_id": audio_id, "field": "gt.duration_sec"})
        for index, label in enumerate(labels):
            if label not in (0, 1, False, True):
                _interval_error(report, audio_id, "frame label must be binary")
                continue
            if bool(label):
                start = index * float(frame_duration)
                end = (index + 1) * float(frame_duration)
                if start < 0 or end > duration + 1e-6:
                    _interval_error(report, audio_id, "frame support exceeds duration")
                else:
                    intervals.append((start, min(end, duration)))
        if len(labels) and abs(len(labels) * float(frame_duration) - duration) > 1e-6:
            report["frame_count_mismatches"].append({"audio_id": audio_id, "expected_duration": duration, "actual_duration": len(labels) * float(frame_duration)})
    elif representation == "sample_index_intervals":
        if not _finite(payload.get("sample_rate")) or float(payload["sample_rate"]) <= 0:
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "sample-index GT needs positive sample_rate"})
            return
        gt_rate = float(payload["sample_rate"])
        if abs(gt_rate - sample_rate) > 1e-9:
            report["sample_count_mismatches"].append({"audio_id": audio_id, "detail": "GT/audio sample-rate mismatch"})
        raw_intervals = payload.get("intervals")
        if not isinstance(raw_intervals, list):
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "sample intervals must be a list"})
            return
        max_sample = int(round(duration * gt_rate))
        for item in raw_intervals:
            if not isinstance(item, Mapping) or not isinstance(item.get("start_sample"), int) or not isinstance(item.get("end_sample"), int):
                _interval_error(report, audio_id, "malformed sample-index interval")
                continue
            start_sample, end_sample = item["start_sample"], item["end_sample"]
            if start_sample < 0 or end_sample < 0 or start_sample >= end_sample or end_sample > max_sample:
                _interval_error(report, audio_id, "sample-index interval out of range")
            else:
                intervals.append((start_sample / gt_rate, end_sample / gt_rate))

    if not intervals:
        report["empty_manipulated_regions"].append(audio_id)


def validate_distribution_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one canonical manifest and return a deterministic JSON report."""

    if not isinstance(manifest, Mapping):
        report = _empty_report()
        report["manifest_errors"].append({"detail": "manifest root must be an object"})
        report["failure_reasons"].append("manifest_parsing_failure")
        return report

    distribution_id = _as_key(manifest.get("distribution_id")) or "UNKNOWN"
    split = _as_key(manifest.get("split")) or "UNKNOWN"
    report = _empty_report(distribution_id, split)
    rows = manifest.get("records")
    if not isinstance(rows, list):
        report["manifest_errors"].append({"detail": "records must be a list"})
        report["failure_reasons"].append("manifest_parsing_failure")
        return report

    audio_ids: list[str] = []
    gt_ids: list[str] = []
    audio_to_gt: dict[str, set[str]] = defaultdict(set)
    gt_to_audio: dict[str, set[str]] = defaultdict(set)
    source_to_audio: dict[str, set[str]] = defaultdict(set)
    declared_audio_ids = {str(value) for value in manifest.get("declared_audio_ids", []) if str(value)}
    declared_gt_ids = {str(value) for value in manifest.get("declared_gt_ids", []) if str(value)}
    top_license = manifest.get("license_status", "UNKNOWN")
    top_provenance = manifest.get("provenance_status", "UNKNOWN")
    license_statuses = [str(top_license).upper()]
    provenance_statuses = [str(top_provenance).upper()]

    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            report["manifest_errors"].append({"row": row_number, "detail": "record must be an object"})
            continue
        audio_id = _as_key(row.get("audio_id"))
        gt_id = _as_key(row.get("gt_id"))
        if audio_id:
            audio_ids.append(audio_id)
        if gt_id:
            gt_ids.append(gt_id)
        audio_present = row.get("audio_present", bool(row.get("audio_path")))
        gt_present = row.get("gt_present", row.get("gt_payload") is not None)
        if not audio_id or not audio_present:
            _append_unique(report["missing_audio_ids"], audio_id or f"<row:{row_number}>")
        if not gt_id or not gt_present:
            _append_unique(report["missing_gt_ids"], gt_id or f"<row:{row_number}>")
        if audio_id and gt_id:
            audio_to_gt[audio_id].add(gt_id)
            gt_to_audio[gt_id].add(audio_id)

        audio_path = _as_key(row.get("audio_path"))
        suffix = Path(audio_path).suffix.lower()
        if not suffix or suffix not in SUPPORTED_AUDIO_EXTENSIONS:
            _append_unique(report["unsupported_audio_extensions"], suffix or "MISSING")
        metadata = row.get("audio_metadata", {})
        if isinstance(metadata, Mapping) and metadata.get("readable") is False:
            _append_unique(report["unreadable_audio_metadata"], audio_id or f"<row:{row_number}>")

        duration = row.get("duration")
        sample_rate = row.get("sample_rate")
        if not _finite(duration) or float(duration) <= 0:
            report["duration_mismatches"].append({"audio_id": audio_id or f"<row:{row_number}>", "detail": "duration <= 0 or invalid"})
            duration_value = 0.0
        else:
            duration_value = float(duration)
        if not _finite(sample_rate) or float(sample_rate) <= 0:
            report["manifest_errors"].append({"audio_id": audio_id, "detail": "sample_rate must be positive"})
            sample_rate_value = 1.0
        else:
            sample_rate_value = float(sample_rate)
        if isinstance(metadata, Mapping) and metadata.get("duration_sec") is not None:
            if not _finite(metadata["duration_sec"]) or abs(float(metadata["duration_sec"]) - duration_value) > 1e-6:
                report["duration_mismatches"].append({"audio_id": audio_id, "field": "audio_metadata.duration_sec"})
        if isinstance(metadata, Mapping) and metadata.get("sample_count") is not None and duration_value > 0:
            if not isinstance(metadata["sample_count"], int) or metadata["sample_count"] != round(duration_value * sample_rate_value):
                report["sample_count_mismatches"].append({"audio_id": audio_id, "expected": round(duration_value * sample_rate_value), "actual": metadata.get("sample_count")})

        source_identity = row.get("source_identity")
        if not source_identity:
            report["identity_ambiguities"].append({"audio_id": audio_id, "detail": "missing source identity"})
        else:
            source_key = json.dumps(source_identity, sort_keys=True, ensure_ascii=False)
            if audio_id:
                source_to_audio[source_key].add(audio_id)
        candidates = row.get("identity_candidates")
        if row.get("identity_ambiguous") is True or (candidates is not None and len(candidates) != 1):
            report["identity_ambiguities"].append({"audio_id": audio_id, "detail": "identity candidate set is not singleton"})

        row_split = _as_key(row.get("split"))
        if row_split and row_split != split:
            report["split_conflicts"].append({"audio_id": audio_id, "expected": split, "actual": row_split})
        if row.get("conflicting_splits"):
            report["split_conflicts"].append({"audio_id": audio_id, "detail": "case appears in conflicting split"})
        if isinstance(row.get("license_provenance"), Mapping):
            license_statuses.append(str(row["license_provenance"].get("license_status", "UNKNOWN")).upper())
            provenance_statuses.append(str(row["license_provenance"].get("provenance_status", "UNKNOWN")).upper())
        else:
            license_statuses.append("UNKNOWN")
            provenance_statuses.append("UNKNOWN")

        _validate_gt_payload(report, row, audio_id or f"<row:{row_number}>", duration_value, sample_rate_value)

    report["audio_count"] = len(audio_ids)
    report["gt_count"] = len(gt_ids)
    report["duplicate_audio_ids"] = sorted(value for value, count in Counter(audio_ids).items() if count > 1)
    report["duplicate_gt_ids"] = sorted(value for value, count in Counter(gt_ids).items() if count > 1)
    report["missing_audio_ids"] = sorted(set(report["missing_audio_ids"]) | (declared_audio_ids - set(audio_ids)))
    report["missing_gt_ids"] = sorted(set(report["missing_gt_ids"]) | (declared_gt_ids - set(gt_ids)))
    report["unexpected_duplicate_source_mappings"] = sorted(
        source_key for source_key, mapped in source_to_audio.items() if len(mapped) > 1
    )
    for audio_id, mapped_gt in audio_to_gt.items():
        if len(mapped_gt) > 1:
            report["identity_ambiguities"].append({"audio_id": audio_id, "detail": "audio maps to multiple GT IDs"})
    for gt_id, mapped_audio in gt_to_audio.items():
        if len(mapped_audio) > 1:
            report["identity_ambiguities"].append({"gt_id": gt_id, "detail": "GT maps to multiple audio IDs"})
    report["matched_count"] = sum(
        1 for audio_id, mapped_gt in audio_to_gt.items() if audio_id not in report["missing_audio_ids"] and len(mapped_gt) == 1
    )

    report["license_status"] = "PASS" if all(value == "PASS" for value in license_statuses) else ("FAIL" if "FAIL" in license_statuses else "UNKNOWN")
    report["provenance_status"] = "PASS" if all(value == "PASS" for value in provenance_statuses) else ("FAIL" if "FAIL" in provenance_statuses else "UNKNOWN")
    report["audio_identity_pass"] = not any(
        (report[key] for key in ("missing_audio_ids", "duplicate_audio_ids", "unsupported_audio_extensions", "unreadable_audio_metadata"))
    ) and not report["identity_ambiguities"]
    report["gt_identity_pass"] = not any(
        (report[key] for key in ("missing_gt_ids", "duplicate_gt_ids", "unsupported_gt_representations"))
    ) and not report["identity_ambiguities"]
    report["gt_integrity_pass"] = not any(
        (report[key] for key in ("invalid_intervals", "empty_manipulated_regions", "frame_count_mismatches", "sample_count_mismatches", "manifest_errors"))
    )
    report["duration_integrity_pass"] = not report["duration_mismatches"]
    report["split_integrity_pass"] = not report["split_conflicts"] and not report["unexpected_duplicate_source_mappings"]
    failure_fields = (
        "missing_audio_ids", "missing_gt_ids", "duplicate_audio_ids", "duplicate_gt_ids",
        "invalid_intervals", "duration_mismatches", "identity_ambiguities", "split_conflicts",
        "manifest_errors", "unsupported_gt_representations", "unsupported_audio_extensions",
        "frame_count_mismatches", "sample_count_mismatches", "unexpected_duplicate_source_mappings",
        "unreadable_audio_metadata", "empty_manipulated_regions",
    )
    report["failure_reasons"] = [field for field in failure_fields if report[field]]
    report["ready_candidate"] = bool(
        rows
        and report["audio_identity_pass"]
        and report["gt_identity_pass"]
        and report["gt_integrity_pass"]
        and report["duration_integrity_pass"]
        and report["split_integrity_pass"]
        and report["license_status"] == "PASS"
        and report["provenance_status"] == "PASS"
    )
    return report


def validate_distribution_file(path: str | Path) -> dict[str, Any]:
    """Read and validate a JSON manifest; parse failures become a failed report."""

    path = Path(path)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = _empty_report()
        report["manifest_errors"].append({"path": str(path), "detail": str(exc)})
        report["failure_reasons"].append("manifest_parsing_failure")
        return report
    return validate_distribution_manifest(manifest)
