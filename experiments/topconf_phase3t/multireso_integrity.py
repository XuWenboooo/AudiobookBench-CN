"""Execution-integrity guards for the Phase3T MultiReso worker.

This module intentionally has no model, dataset, target, score, or metric
logic.  It only owns the single-writer namespace contract and the small amount
of identity bookkeeping needed to make a resumable infrastructure run safe.
"""
from __future__ import annotations

import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


LOCK_NAME = "worker_owner_lock.json"
COMPLETED_STATUSES = {"COMPLETED"}
IDENTITY_FIELDS = (
    "invocation_id",
    "namespace",
    "branch",
    "repository_commit",
    "authorized_executable",
    "python_version",
    "torch_version",
    "fairseq_version",
    "cuda_available",
    "gpu_name",
)


class NamespaceOwnershipError(RuntimeError):
    """Raised when a namespace cannot be safely acquired or resumed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value)))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NamespaceOwnershipError(f"cannot read integrity record: {path}") from exc
    if not isinstance(value, dict):
        raise NamespaceOwnershipError(f"integrity record is not an object: {path}")
    return value


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _same_identity_value(field: str, expected: Any, actual: Any) -> bool:
    if field == "authorized_executable":
        return normalize_path(str(expected)) == normalize_path(str(actual))
    return expected == actual


def identity_mismatches(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> dict[str, tuple[Any, Any]]:
    mismatches: dict[str, tuple[Any, Any]] = {}
    for field in IDENTITY_FIELDS:
        if field in expected and field in actual and not _same_identity_value(field, expected[field], actual[field]):
            mismatches[field] = (expected[field], actual[field])
    return mismatches


def _default_process_probe(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _stale_lock_path(lock_path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = lock_path.with_name(f"{lock_path.name}.stale-{stamp}-{os.getpid()}")
    suffix = 0
    while candidate.exists():
        suffix += 1
        candidate = lock_path.with_name(f"{lock_path.name}.stale-{stamp}-{os.getpid()}-{suffix}")
    return candidate


def acquire_namespace_lock(
    namespace: Path,
    identity: Mapping[str, Any],
    *,
    resume: bool = False,
    recover_stale: bool = False,
    process_probe: Callable[[int], bool] | None = None,
) -> Path:
    """Acquire the namespace lock with atomic create and identity checks.

    A stale lock is never silently removed.  Recovery requires both the
    explicit ``resume`` and ``recover_stale`` controls, and the old lock is
    renamed to a preserved evidence file before a new lock is created.
    """

    if "invocation_id" not in identity or "namespace" not in identity:
        raise NamespaceOwnershipError("lock identity must include invocation_id and namespace")
    namespace.mkdir(parents=True, exist_ok=True)
    lock_path = namespace / LOCK_NAME
    probe = process_probe or _default_process_probe

    if lock_path.exists():
        old = read_json(lock_path)
        mismatches = identity_mismatches(identity, old)
        if mismatches:
            fields = ", ".join(sorted(mismatches))
            raise NamespaceOwnershipError(f"namespace identity mismatch: {fields}")
        if old.get("status") in COMPLETED_STATUSES:
            raise NamespaceOwnershipError("completed namespace reuse is forbidden")
        try:
            old_pid = int(old.get("pid", 0))
        except (TypeError, ValueError):
            old_pid = 0
        if probe(old_pid):
            raise NamespaceOwnershipError(f"active namespace writer exists: pid={old_pid}")
        if not (resume and recover_stale):
            raise NamespaceOwnershipError("stale namespace lock detected; explicit resume recovery is required")
        stale_path = _stale_lock_path(lock_path)
        try:
            lock_path.rename(stale_path)
        except FileExistsError:
            raise NamespaceOwnershipError("could not preserve stale namespace lock")

    payload = dict(identity)
    payload.update(
        {
            "pid": os.getpid(),
            "host": platform.node(),
            "started_utc": utc_now(),
            "status": "RUNNING",
            "lock_schema": "phase3t_namespace_owner_v1",
        }
    )
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        descriptor = os.open(str(lock_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise NamespaceOwnershipError("another writer won the namespace lock race") from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return lock_path


def release_namespace_lock(
    lock_path: Path,
    identity: Mapping[str, Any],
    *,
    status: str,
    updates: Mapping[str, Any] | None = None,
) -> None:
    """Close the lock while preserving completion or abort evidence."""

    current = read_json(lock_path)
    mismatches = identity_mismatches(identity, current)
    if mismatches:
        fields = ", ".join(sorted(mismatches))
        raise NamespaceOwnershipError(f"cannot release lock with identity mismatch: {fields}")
    if int(current.get("pid", -1)) != os.getpid():
        raise NamespaceOwnershipError("only the owning process may release the namespace lock")
    current["status"] = status
    current["released_utc"] = utc_now()
    if updates:
        current.update(dict(updates))
    write_json_atomic(lock_path, current)


def assert_resume_manifest(namespace: Path, identity: Mapping[str, Any]) -> dict[str, Any]:
    """Require a non-complete run manifest with the same invocation identity."""

    manifest_path = namespace / "MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json"
    if not manifest_path.exists():
        raise NamespaceOwnershipError("resume requested without a run manifest")
    manifest = read_json(manifest_path)
    mismatches = identity_mismatches(identity, manifest)
    if mismatches:
        fields = ", ".join(sorted(mismatches))
        raise NamespaceOwnershipError(f"resume manifest identity mismatch: {fields}")
    if manifest.get("status") == "COMPLETE":
        raise NamespaceOwnershipError("completed namespace reuse is forbidden")
    return manifest

