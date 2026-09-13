from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.week4_authorization import CANONICAL_SOURCES, sha256_file
from audiobookbench.security.week4_execution import SAMPLE_RATE, execute_protocol
from audiobookbench.security.week4_final_evaluator import evaluate_committed_held_out
from audiobookbench.security.week4_post_validation_freeze import PostValidationFreezeError, build_freeze_record
from audiobookbench.security.week4_adaptive import FrozenAttackSpec


ROOT = Path(__file__).resolve().parents[1]


class FakeD0:
    def embed_windows(self, waveform, windows):
        rows = []
        for index, (lo, hi) in enumerate(windows):
            row = np.zeros(192, dtype=np.float32)
            row[index % 192] = 1.0
            row[(index + 1) % 192] = float(np.mean(waveform[lo:hi]))
            rows.append(row)
        return np.asarray(rows, dtype=np.float32)


def cases():
    return [
        {"case_id": f"week4_case_{index:04d}", "split": "dev" if index <= 24 else "validation" if index <= 36 else "held_out", "source_text_exact": "源文本", "reference_text_exact": "参考文本"}
        for index in range(1, 49)
    ]


def source_hashes():
    return {name: sha256_file(path) for name, path in CANONICAL_SOURCES.items()}


def run_stage(tmp_path: Path, stage: str, *, no_parent: set[str] | None = None):
    no_parent = no_parent or set()
    spec = FrozenAttackSpec.from_path(ROOT / "configs/week4_adaptive_red_team.yaml")
    metadata = {"authorization_source_sha256": source_hashes(), "invocation_id": f"TEST_ONLY_{stage}"}
    return execute_protocol(
        cases=cases(), spec=spec, runtime_root=tmp_path / stage, stage=stage, metadata=metadata,
        f5_generator=lambda case, _seed: (np.full(21200 if case["case_id"] in no_parent else 32000, 0.2, dtype=np.float32), SAMPLE_RATE),
        source_loader=lambda case: np.full(38336 if case["case_id"] in no_parent else 64000, 0.1, dtype=np.float32),
        d0_backend=FakeD0(),
    )


def test_only_stage_scopes_freeze_and_reportable_h4(tmp_path: Path):
    validation = run_stage(tmp_path, "validation")
    assert validation["stage"] == "VALIDATION"
    assert len(validation["per_case"]) == 12 and validation["accounting"]["VALIDATION_PLANNED"] == 12
    freeze = build_freeze_record(tmp_path / "validation", tmp_path / "freeze.md")
    assert freeze["terminal_cases"] == 12
    heldout = run_stage(tmp_path, "held_out")
    assert heldout["stage"] == "HELD_OUT" and "final" not in heldout
    result = evaluate_committed_held_out(tmp_path / "held_out", tmp_path / "h4.json")
    assert result["PRIMARY_H4"] == "REPORTABLE"
    assert result["paired_bootstrap"]["auroc"]["requested"] == 2000
    assert result["paired_bootstrap"]["auroc"]["finite"] >= 1900


def test_only_validation_no_parent_still_freezes(tmp_path: Path):
    result = run_stage(tmp_path, "validation", no_parent={"week4_case_0025"})
    assert result["per_case"]["week4_case_0025"]["adaptive_case_status"] == "NO_VALID_ADAPTIVE_PARENT"
    assert build_freeze_record(tmp_path / "validation", tmp_path / "freeze.md")["terminal_cases"] == 12


def test_only_heldout_no_parent_is_not_reportable(tmp_path: Path):
    run_stage(tmp_path, "held_out", no_parent={"week4_case_0037"})
    assert evaluate_committed_held_out(tmp_path / "held_out") == {
        "PRIMARY_H4": "NOT_REPORTABLE", "reason": "HELD_OUT_NOT_12_OF_12_PAIRED_COMPLETE"
    }


def test_only_validation_integrity_or_hash_mutation_blocks_freeze(tmp_path: Path):
    run_stage(tmp_path, "validation")
    ledger = tmp_path / "validation/accounting/candidate_ledger.jsonl"
    ledger.write_text(ledger.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
    with pytest.raises(PostValidationFreezeError, match="ledger integrity"):
        build_freeze_record(tmp_path / "validation", tmp_path / "freeze.md")
    clean = tmp_path / "clean"
    run_stage(clean, "validation")
    metadata = clean / "validation/run_metadata.json"
    text = metadata.read_text(encoding="utf-8").replace('"canonical_config": "', '"canonical_config": "0', 1)
    metadata.write_text(text, encoding="utf-8")
    with pytest.raises(PostValidationFreezeError, match="source hashes"):
        build_freeze_record(clean / "validation", clean / "freeze.md")
