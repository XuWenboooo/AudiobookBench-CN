"""Feasibility audit for an official LlamaPartialSpoof label package."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEGMENT = re.compile(r"^(?P<start>\d+(?:\.\d+)?)-(?P<end>\d+(?:\.\d+)?)-(?P<label>bonafide|spoof)$")


def audit(path: Path) -> dict[str, object]:
    ids: set[str] = set()
    rows = 0
    segments = 0
    labels = {"bonafide": 0, "spoof": 0}
    zero_length_bonafide = 0
    errors: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        rows += 1
        fields = raw.split()
        if len(fields) < 4:
            errors.append(f"line {line_number}: too few fields")
            continue
        case_id, duration_text, utterance_label, *raw_segments = fields
        if case_id in ids:
            errors.append(f"line {line_number}: duplicate id {case_id}")
        ids.add(case_id)
        try:
            duration = float(duration_text)
        except ValueError:
            errors.append(f"line {line_number}: invalid duration")
            continue
        if duration <= 0 or utterance_label not in labels:
            errors.append(f"line {line_number}: invalid utterance label/duration")
        previous_end = 0.0
        for token in raw_segments:
            match = SEGMENT.match(token)
            if match is None:
                errors.append(f"line {line_number}: invalid segment {token}")
                continue
            start = float(match.group("start"))
            end = float(match.group("end"))
            label = match.group("label")
            if start < 0 or end < start or end > duration + 1e-4 or start < previous_end - 1e-4:
                errors.append(f"line {line_number}: invalid interval {token}")
            elif end == start:
                if label != "bonafide":
                    errors.append(f"line {line_number}: zero-length spoof interval {token}")
                else:
                    zero_length_bonafide += 1
            previous_end = end
            labels[label] += 1
            segments += 1
    return {
        "label_file": str(path),
        "rows": rows,
        "unique_ids": len(ids),
        "segments": segments,
        "segment_labels": labels,
        "zero_length_bonafide_noop": zero_length_bonafide,
        "schema_and_temporal_gt": "PASS" if not errors else "FAIL",
        "errors": errors[:20],
        "error_count": len(errors),
        "audio_identity": "PENDING_OFFICIAL_ARCHIVE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("label_file", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.label_file), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
