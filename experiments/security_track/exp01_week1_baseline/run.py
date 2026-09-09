from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from audiobookbench.data.manifest import load_manifest, validate_manifest


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def main() -> None:
    cfg_path = Path("configs/week1.yaml")
    if not cfg_path.exists():
        raise FileNotFoundError("configs/week1.yaml not found. Run from repository root.")

    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    manifest_path = Path(cfg["manifest_path"])
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"{manifest_path} not found. Create a real-audio manifest before running Week 1 baseline. "
            "Use data/manifests/example_manifest.csv only for schema smoke tests, not research claims."
        )

    records = load_manifest(manifest_path)
    validate_manifest(records)

    out = Path(cfg["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    sample_ids = {str(row["sample_id"]) for row in records}
    summary = {
        "n_rows": len(records),
        "n_samples": len(sample_ids),
        "n_manipulated_rows": sum(_as_bool(row["is_manipulated"]) for row in records),
        "note": "Baseline scaffold loaded and validated the manifest. Add feature extraction before claiming results.",
    }
    (out / "metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    preview_path = out / "manifest_preview.csv"
    fieldnames = list(records[0].keys()) if records else []
    with preview_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records[:50])

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
