from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from experiments.topconf_phase3t.multireso_integrity import (
    NamespaceOwnershipError,
    acquire_namespace_lock,
    release_namespace_lock,
)


def _identity(namespace: Path, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "invocation_id": "PHASE3T_MRM_FULL_E1_002",
        "namespace": "results/topconf_phase3t/multireso_worker_02",
        "branch": "topconf-phase3t-multireso-worker-r2",
        "repository_commit": "ee8d3a157dd329116e5ea8607a14446f90f26e8d",
        "authorized_executable": r"F:\envs\topconf-phase3v-multireso-py310\Scripts\python.exe",
        "python_version": "3.10.11",
        "torch_version": "1.13.1+cu117",
        "fairseq_version": "0.12.2",
        "cuda_available": True,
        "gpu_name": "NVIDIA GeForce RTX 4060 Laptop GPU",
    }
    value.update(overrides)
    return value


def test_second_writer_is_rejected(tmp_path: Path) -> None:
    namespace = tmp_path / "worker"
    identity = _identity(namespace)
    acquire_namespace_lock(namespace, identity, process_probe=lambda pid: pid == os.getpid())
    with pytest.raises(NamespaceOwnershipError, match="active namespace writer"):
        acquire_namespace_lock(namespace, identity, process_probe=lambda pid: pid == os.getpid())


def test_stale_lock_requires_explicit_recovery_and_is_preserved(tmp_path: Path) -> None:
    namespace = tmp_path / "worker"
    identity = _identity(namespace)
    namespace.mkdir()
    lock = namespace / "worker_owner_lock.json"
    lock.write_text(json.dumps({**identity, "pid": 999999, "status": "RUNNING"}), encoding="utf-8")
    with pytest.raises(NamespaceOwnershipError, match="stale namespace lock"):
        acquire_namespace_lock(namespace, identity, process_probe=lambda pid: False)
    new_lock = acquire_namespace_lock(namespace, identity, resume=True, recover_stale=True, process_probe=lambda pid: False)
    assert new_lock.exists()
    assert list(namespace.glob("worker_owner_lock.json.stale-*"))


def test_wrong_invocation_and_environment_are_rejected(tmp_path: Path) -> None:
    namespace = tmp_path / "worker"
    identity = _identity(namespace)
    namespace.mkdir()
    (namespace / "worker_owner_lock.json").write_text(
        json.dumps({**identity, "invocation_id": "PHASE3T_MRM_FULL_E1_001", "pid": 999999, "status": "RUNNING"}),
        encoding="utf-8",
    )
    with pytest.raises(NamespaceOwnershipError, match="identity mismatch"):
        acquire_namespace_lock(namespace, identity, resume=True, recover_stale=True, process_probe=lambda pid: False)

    (namespace / "worker_owner_lock.json").write_text(
        json.dumps({**identity, "authorized_executable": r"F:\wrong\python.exe", "pid": 999999, "status": "RUNNING"}),
        encoding="utf-8",
    )
    with pytest.raises(NamespaceOwnershipError, match="identity mismatch"):
        acquire_namespace_lock(namespace, identity, resume=True, recover_stale=True, process_probe=lambda pid: False)


def test_completed_namespace_cannot_be_reused(tmp_path: Path) -> None:
    namespace = tmp_path / "worker"
    identity = _identity(namespace)
    lock = acquire_namespace_lock(namespace, identity, process_probe=lambda pid: pid == os.getpid())
    release_namespace_lock(lock, identity, status="COMPLETED", updates={"terminal": 42471})
    with pytest.raises(NamespaceOwnershipError, match="completed namespace reuse"):
        acquire_namespace_lock(namespace, identity, resume=True, recover_stale=True, process_probe=lambda pid: False)

