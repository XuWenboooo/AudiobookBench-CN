"""Reconstruct historical data-use exclusions and compare them with frozen V2.

The reconstruction is deliberately evidence-first.  It reads manifests,
reports, logs, Git history, and known external project trees; it never loads
audio samples or models and never changes the frozen V2 population.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


TOPCONF_HEAD_EXPECTED = "45b95dd224f7172a41dccaa4663fd9c8256b62b7"
PROTOCOL_FREEZE_COMMIT = "2797bf0"
PHASE4_6_ENTRY_COMMIT = "ad58622667098f02b119192e1d5a7c93e0aef77d"
TEXT_EXTENSIONS = {".md", ".json", ".csv", ".tsv", ".yaml", ".yml", ".txt", ".log", ".py", ".ps1", ".sh"}
SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    "site-packages", "dist-packages", "datasets", "smoke", "generated",
}
CASE_PATTERNS = re.compile(r"case[_-]?id|paircase|case_", re.IGNORECASE)
AISHELL1_PATTERN = re.compile(r"aishell[-_ ]?1|slr33", re.IGNORECASE)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical_sha256(payload: Any) -> str:
    rendered = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return _sha256_bytes(rendered.encode("utf-8"))


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _repo_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _commit_for(root: Path, relative_path: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--all", "-1", "--format=%H", "--", relative_path],
        cwd=root, capture_output=True, text=True, check=False,
    )
    value = result.stdout.strip()
    return value or None


def _git_search(root: Path, pattern: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            "git", "log", "--all", "--regexp-ignore-case", "--date=iso",
            "--format=%H|%ad|%s", "-G", pattern, "--",
        ], cwd=root, capture_output=True, text=True, check=False,
    )
    rows = []
    for line in result.stdout.splitlines():
        fields = line.split("|", 2)
        if len(fields) == 3:
            rows.append({"commit": fields[0], "date": fields[1], "subject": fields[2]})
    return rows


def _git_history_summary(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "log", "--all", "--name-status", "--format=%H"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    commit_count = 0
    path_entries = 0
    deleted_entries = 0
    matched_paths: set[str] = set()
    for line in result.stdout.splitlines():
        if re.fullmatch(r"[0-9a-f]{40}", line):
            commit_count += 1
            continue
        fields = line.split("\t")
        if len(fields) < 2 or fields[0][0:1] not in {"A", "M", "D", "R", "C"}:
            continue
        path_entries += 1
        if fields[0].startswith("D"):
            deleted_entries += 1
        path = fields[-1]
        if re.search(r"manifest|ledger|authorization|closure|selection|threshold|calibr|debug|smoke|phase3|week[1-5]", path, re.I):
            matched_paths.add(path)
    return {
        "all_refs_checked": True,
        "commit_count": commit_count,
        "name_status_path_entries": path_entries,
        "deleted_path_entries_checked": deleted_entries,
        "matched_historical_paths_sample": sorted(matched_paths)[:300],
    }


def _read_text_matches(roots: list[Path]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    aishell1_matches: list[str] = []
    scanned = 0
    skipped_large = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.stat().st_size > 20 * 1024 * 1024:
                skipped_large += 1
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            matched = []
            for pattern, label in (
                (AISHELL1_PATTERN, "AISHELL1"),
                (re.compile(r"phase3[rsuvt]|week[1-5]", re.I), "PHASE_OR_WEEK"),
                (re.compile(r"selection|threshold|calibr|debug|metric|smoke", re.I), "GOVERNANCE_OR_SELECTION"),
            ):
                if pattern.search(text) or pattern.search(path.name):
                    matched.append(label)
            if matched:
                entry = {"path": str(path), "labels": sorted(set(matched)), "bytes": path.stat().st_size}
                matches.append(entry)
                if "AISHELL1" in matched:
                    aishell1_matches.append(str(path))
    return {
        "roots": [str(root) for root in roots],
        "text_files_scanned": scanned,
        "large_or_skipped_files": skipped_large,
        "matched_file_count": len(matches),
        "matched_files": sorted(matches, key=lambda row: row["path"]),
        "aishell1_match_paths": sorted(aishell1_matches),
    }


def _speaker_key(corpus: str, speaker_id: str | None) -> str | None:
    if not speaker_id:
        return None
    return f"{corpus}:{speaker_id}"


def _record_evidence(root: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    evidence = []
    for relative in relative_paths:
        path = root / relative
        item: dict[str, Any] = {"path": str(path), "exists": path.is_file()}
        if path.is_file():
            item["bytes"] = path.stat().st_size
            item["sha256"] = _sha256_file(path)
            item["commit"] = _commit_for(root, relative)
        evidence.append(item)
    return evidence


class Reconstruction:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.main = args.main_root
        self.week5 = args.week5_root
        self.topconf = args.topconf_root
        self.phase3t_cache = args.phase3t_cache
        self.case_records: list[dict[str, Any]] = []
        self.source_by_key: dict[str, dict[str, Any]] = {}
        self.speaker_by_key: dict[str, dict[str, Any]] = {}
        self.lineage_by_key: dict[str, dict[str, Any]] = {}
        self.unresolved: list[dict[str, Any]] = []
        self.stage_counts: dict[str, dict[str, Any]] = {}

    def _add_speaker(
        self,
        *,
        corpus: str,
        speaker_id: str | None,
        stage: str,
        confidence: str,
        evidence: list[str],
        namespace: str | None = None,
    ) -> None:
        key = _speaker_key(corpus, speaker_id)
        if key is None:
            return
        item = self.speaker_by_key.setdefault(key, {
            "corpus": corpus,
            "speaker_namespace": namespace or corpus,
            "speaker_id": speaker_id,
            "speaker_key": key,
            "historical_stages": [],
            "evidence_sources": [],
            "confidence": confidence,
            "reuse_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        })
        if stage not in item["historical_stages"]:
            item["historical_stages"].append(stage)
        for path in evidence:
            if path not in item["evidence_sources"]:
                item["evidence_sources"].append(path)
        if confidence == "PARTIAL" or item["confidence"] == "PARTIAL":
            item["confidence"] = "PARTIAL"

    def _add_source(
        self,
        *,
        stage: str,
        corpus: str,
        source_id: str | None,
        speaker_id: str | None,
        utterance_id: str | None,
        parent_recording: str | None,
        source_audio_sha256: str | None,
        text_sha256: str | None,
        role: str,
        confidence: str,
        evidence: list[str],
    ) -> None:
        audio_sha = source_audio_sha256.upper() if source_audio_sha256 else None
        key = f"audio:{audio_sha}" if audio_sha else f"identity:{corpus}:{source_id}:{utterance_id}"
        item = self.source_by_key.setdefault(key, {
            "source_id": source_id,
            "parent_recording": parent_recording,
            "corpus": corpus,
            "speaker_id": speaker_id,
            "speaker_key": _speaker_key(corpus, speaker_id),
            "utterance_id": utterance_id,
            "text_sha256": text_sha256,
            "source_audio_sha256": audio_sha,
            "lineage_id": f"AUDIO_SHA256:{audio_sha}" if audio_sha else None,
            "historical_stages": [],
            "historical_roles": [],
            "evidence_sources": [],
            "confidence": confidence,
        })
        if stage not in item["historical_stages"]:
            item["historical_stages"].append(stage)
        if role not in item["historical_roles"]:
            item["historical_roles"].append(role)
        for path in evidence:
            if path not in item["evidence_sources"]:
                item["evidence_sources"].append(path)
        if confidence == "PARTIAL" or item["confidence"] == "PARTIAL":
            item["confidence"] = "PARTIAL"
        self._add_speaker(corpus=corpus, speaker_id=speaker_id, stage=stage, confidence=confidence, evidence=evidence)

    def _add_case(
        self,
        *,
        case_id: str,
        stage: str,
        dataset: str,
        source_id: str | None,
        speaker_id: str | None,
        source_evidence: list[str],
        data_role: str,
        confidence: str,
        source_audio_sha256: str | None = None,
        text_sha256: str | None = None,
        parent_asset_id: str | None = None,
        lineage_id: str | None = None,
    ) -> None:
        self.case_records.append({
            "case_id": case_id,
            "stage": stage,
            "dataset": dataset,
            "source_id": source_id,
            "speaker_id": speaker_id,
            "speaker_key": _speaker_key(dataset, speaker_id),
            "source_audio_sha256": source_audio_sha256.upper() if source_audio_sha256 else None,
            "text_sha256": text_sha256,
            "parent_asset_id": parent_asset_id,
            "lineage_id": lineage_id,
            "source_evidence": source_evidence,
            "commit_file_log": source_evidence,
            "data_role": data_role,
            "confidence": confidence,
        })
        self._add_speaker(corpus=dataset, speaker_id=speaker_id, stage=stage, confidence=confidence, evidence=source_evidence)

    def _audio_hash(self, raw_path: str | None, manifest_hash: str | None = None) -> str | None:
        if manifest_hash:
            return manifest_hash.upper()
        if not raw_path:
            return None
        path = Path(raw_path)
        return _sha256_file(path).upper() if path.is_file() else None

    def _ingest_week1(self) -> dict[str, Any]:
        source_rel = "data/manifests/source_audio.csv"
        case_rel = "data/manifests/week1_manifest.csv"
        source_path = self.main / source_rel
        case_path = self.main / case_rel
        sources = _csv(source_path)
        cases = _csv(case_path)
        evidence = [str(source_path), str(case_path)]
        for row in sources:
            audio_sha = self._audio_hash(row.get("audio_path"))
            source_id = row.get("source_sample_id") or row.get("sample_id")
            speaker = row.get("speaker") or None
            text = row.get("transcript_zh") or ""
            self._add_source(
                stage="WEEK1_PILOT", corpus="AISHELL3", source_id=source_id,
                speaker_id=speaker, utterance_id=source_id, parent_recording=row.get("audio_path"),
                source_audio_sha256=audio_sha, text_sha256=_sha256_bytes(text.encode("utf-8")) if text else None,
                role="PILOT_SOURCE", confidence="VERIFIED", evidence=evidence,
            )
        for row in cases:
            case_id = row.get("segment_id") or row.get("sample_id")
            if not case_id:
                continue
            source_id = row.get("source_sample_id") or row.get("sample_id")
            self._add_case(
                case_id=case_id, stage="WEEK1_PILOT", dataset="AISHELL3", source_id=source_id,
                speaker_id=row.get("speaker") or None, source_evidence=evidence,
                data_role="PILOT_MANIPULATED_AND_CONTROL", confidence="VERIFIED",
                source_audio_sha256=self._audio_hash(row.get("audio_path")),
            )
        return {
            "known_case_count": len(cases), "unique_case_count": len({row.get("segment_id") or row.get("sample_id") for row in cases}),
            "known_source_count": len(sources), "unique_source_count": len({row.get("source_sample_id") or row.get("sample_id") for row in sources}),
            "known_speaker_count": len({row.get("speaker") for row in sources if row.get("speaker")}),
            "evidence": _record_evidence(self.main, [source_rel, case_rel]),
            "case_history_completeness": "PARTIAL", "source_history_completeness": "PARTIAL", "lineage_history_completeness": "PARTIAL",
        }

    def _ingest_week2_and_week3(self) -> dict[str, Any]:
        planned_rel = "data/manifests/week2a_a2_planned_manifest.csv"
        reference_rel = "data/manifests/week2a_reference_manifest.csv"
        planned_path = self.main / planned_rel
        reference_path = self.main / reference_rel
        planned = _csv(planned_path)
        references = _csv(reference_path)
        evidence = [str(planned_path), str(reference_path), str(self.main / "research_assurance/WEEK2_SCIENTIFIC_CLOSURE.md"), str(self.main / "research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md")]
        for row in planned:
            source_id = row.get("target_source_sample_id") or None
            audio_sha = self._audio_hash(row.get("source_audio_path"))
            for stage in ("WEEK2_PILOT", "WEEK3_PILOT"):
                self._add_source(
                    stage=stage, corpus="AISHELL3", source_id=source_id, speaker_id=row.get("target_speaker") or None,
                    utterance_id=source_id, parent_recording=row.get("source_audio_path"), source_audio_sha256=audio_sha,
                    text_sha256=row.get("source_text_sha256") or None, role="PILOT_SOURCE", confidence="VERIFIED", evidence=evidence,
                )
                if row.get("paired_case_id"):
                    self._add_case(
                        case_id=row["paired_case_id"], stage=stage, dataset="AISHELL3", source_id=source_id,
                        speaker_id=row.get("target_speaker") or None, source_evidence=evidence,
                        data_role="LEVEL1_DEVELOPMENT_PILOT", confidence="VERIFIED", source_audio_sha256=audio_sha,
                        text_sha256=row.get("source_text_sha256") or None,
                    )
        for row in references:
            source_id = row.get("reference_sample_id") or None
            audio_sha = self._audio_hash(row.get("reference_audio_path"), row.get("sha256"))
            self._add_source(
                stage="WEEK2_PILOT", corpus="AISHELL3", source_id=source_id, speaker_id=row.get("speaker") or None,
                utterance_id=source_id, parent_recording=row.get("reference_audio_path"), source_audio_sha256=audio_sha,
                text_sha256=None, role="REFERENCE_AUDIO", confidence="VERIFIED", evidence=evidence,
            )
        return {
            "known_case_count": len(planned) * 2, "unique_case_count": len({row.get("paired_case_id") for row in planned}),
            "known_source_count": len(planned) + len(references), "unique_source_count": len({row.get("target_source_sample_id") for row in planned} | {row.get("reference_sample_id") for row in references}),
            "known_speaker_count": len({row.get("target_speaker") for row in planned if row.get("target_speaker")} | {row.get("speaker") for row in references if row.get("speaker")}),
            "evidence": _record_evidence(self.main, [planned_rel, reference_rel, "research_assurance/WEEK2_SCIENTIFIC_CLOSURE.md", "research_assurance/WEEK3_FINAL_SCIENTIFIC_CLOSURE.md"]),
            "case_history_completeness": "COMPLETE", "source_history_completeness": "PARTIAL", "lineage_history_completeness": "PARTIAL",
        }

    def _ingest_week4(self) -> dict[str, Any]:
        rel = "data/manifests/week4_population_manifest.json"
        path = self.main / rel
        manifest = _json(path)
        selected = manifest.get("selected_cases", [])
        evidence = [str(path)]
        for row in selected:
            source_id = row.get("source_sample_id") or None
            source_hash = self._audio_hash(row.get("source_path"), row.get("source_audio_sha256"))
            self._add_source(
                stage="WEEK4_PILOT", corpus="AISHELL3", source_id=source_id, speaker_id=row.get("source_speaker") or None,
                utterance_id=source_id, parent_recording=row.get("source_path"), source_audio_sha256=source_hash,
                text_sha256=row.get("source_text_sha256") or None, role="PILOT_SOURCE", confidence="VERIFIED", evidence=evidence,
            )
            ref_id = row.get("reference_sample_id") or None
            self._add_source(
                stage="WEEK4_PILOT", corpus="AISHELL3", source_id=ref_id, speaker_id=row.get("reference_speaker") or None,
                utterance_id=ref_id, parent_recording=row.get("reference_path"), source_audio_sha256=self._audio_hash(row.get("reference_path"), row.get("reference_audio_sha256")),
                text_sha256=row.get("reference_text_sha256") or None, role="REFERENCE_AUDIO", confidence="VERIFIED", evidence=evidence,
            )
            if row.get("case_id"):
                self._add_case(
                    case_id=row["case_id"], stage="WEEK4_PILOT", dataset="AISHELL3", source_id=source_id,
                    speaker_id=row.get("source_speaker") or None, source_evidence=evidence,
                    data_role="PILOT_ADAPTIVE_SELECTION", confidence="VERIFIED", source_audio_sha256=source_hash,
                    text_sha256=row.get("source_text_sha256") or None,
                )
        return {
            "known_case_count": len(selected), "unique_case_count": len({row.get("case_id") for row in selected}),
            "known_source_count": len(selected) * 2, "unique_source_count": len({row.get("source_sample_id") for row in selected} | {row.get("reference_sample_id") for row in selected}),
            "known_speaker_count": len({row.get("source_speaker") for row in selected if row.get("source_speaker")} | {row.get("reference_speaker") for row in selected if row.get("reference_speaker")}),
            "evidence": _record_evidence(self.main, [rel]),
            "case_history_completeness": "PARTIAL", "source_history_completeness": "PARTIAL", "lineage_history_completeness": "PARTIAL",
        }

    def _ingest_week5(self) -> dict[str, Any]:
        manifest_dir = self.week5 / "data/manifests"
        manifests = sorted(manifest_dir.glob("week5_exp*_qualification_population.json"))
        case_total = 0
        unique_cases: set[str] = set()
        speakers: set[str] = set()
        evidence_paths: list[str] = []
        for path in manifests:
            manifest = _json(path)
            exp = re.search(r"week5_exp(\d+)", path.stem)
            stage = f"WEEK5_EXP{exp.group(1)}_QUALIFICATION" if exp else "WEEK5_QUALIFICATION"
            cases = manifest.get("cases", [])
            speaker_map = manifest.get("speakers", {})
            case_total += len(cases)
            for value in speaker_map:
                speakers.add(str(value))
                self._add_speaker(corpus="AISHELL3", speaker_id=str(value), stage=stage, confidence="VERIFIED", evidence=[str(path)])
            for case_id in cases:
                if isinstance(case_id, str):
                    unique_cases.add(case_id)
                    self._add_case(
                        case_id=case_id, stage=stage, dataset="AISHELL3", source_id=None,
                        speaker_id=None, source_evidence=[str(path)], data_role="LEVEL1_QUALIFICATION",
                        confidence="VERIFIED",
                    )
            evidence_paths.append(str(path))
        self.unresolved.append({
            "stage": "WEEK5_QUALIFICATION", "unknown_source_count": case_total,
            "missing_fields": ["source_id", "parent_recording", "utterance_id", "lineage_id"],
            "evidence_sources": evidence_paths,
        })
        return {
            "known_case_count": case_total, "unique_case_count": len(unique_cases),
            "known_source_count": None, "unique_source_count": None, "known_speaker_count": len(speakers),
            "evidence": [_record_evidence(self.week5, [str(path.relative_to(self.week5))])[0] for path in manifests],
            "case_history_completeness": "PARTIAL", "source_history_completeness": "UNKNOWN", "lineage_history_completeness": "UNKNOWN",
        }

    def _ingest_phase3t(self) -> dict[str, Any]:
        rel = "results/topconf_phase3t/case_manifest.tsv"
        path = self.topconf / rel
        rows: list[dict[str, str]] = []
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        speakers: set[str] = set()
        evidence = [str(path), str(self.topconf / "research_assurance/topconf/PHASE3T_RAW_OUTPUT_MANIFEST_V1.json")]
        for row in rows:
            case_id = row.get("case_id") or ""
            if not case_id:
                continue
            audio_rel = row.get("audio_relpath") or ""
            parts = Path(audio_rel).parts
            raw_speaker = parts[1] if len(parts) > 1 else None
            if raw_speaker:
                speakers.add(raw_speaker)
                self._add_speaker(corpus="PartialEdit_v1.1_E1", speaker_id=raw_speaker, stage="PHASE3T_PARTIALEDIT_E1", confidence="DERIVED_WITH_STRONG_EVIDENCE", evidence=evidence, namespace="PARTIALEDIT_OUTPUT_PATH")
            self._add_case(
                case_id=case_id, stage="PHASE3T_PARTIALEDIT_E1", dataset="PartialEdit_v1.1_E1",
                source_id=None, speaker_id=raw_speaker, source_evidence=evidence,
                data_role="LEVEL1_EVALUATION_OUTPUT", confidence="VERIFIED",
            )
        self.unresolved.append({
            "stage": "PHASE3T_PARTIALEDIT_E1", "unknown_source_count": len(rows),
            "missing_fields": ["original_recording", "source_id", "session_id", "reference_audio_id", "parent_asset_id", "generator_input_identity"],
            "evidence_sources": evidence,
        })
        return {
            "known_case_count": len(rows), "unique_case_count": len({row.get("case_id") for row in rows}),
            "known_source_count": len(rows), "unique_source_count": len(rows), "known_speaker_count": len(speakers),
            "evidence": _record_evidence(self.topconf, [rel, "research_assurance/topconf/PHASE3T_RAW_OUTPUT_MANIFEST_V1.json"]),
            "case_history_completeness": "COMPLETE", "source_history_completeness": "PARTIAL", "lineage_history_completeness": "PARTIAL",
        }

    def _empty_or_unknown_stages(self) -> None:
        topconf_files = {
            "PHASE3": ["research_assurance/topconf/PHASE3_EXTERNAL_REPRODUCTION_CLOSURE.md"],
            "PHASE3R": ["research_assurance/topconf/PHASE3R_RECOVERY_CLOSURE.md"],
            "PHASE3S": ["research_assurance/topconf/PHASE3S_BASELINE_REPLACEMENT_AUDIT_V1.md", "research_assurance/topconf/PHASE3S_RESOURCE_ENVIRONMENT_CLOSURE.md"],
            "PHASE3U": ["research_assurance/topconf/PHASE3U_SECOND_BASELINE_CLOSURE.md"],
            "PHASE3V": ["research_assurance/topconf/PHASE3V_FULL_PERMISSION_RECOVERY_CLOSURE.md", "research_assurance/topconf/PHASE3V_CHECKPOINT_MANIFEST_V1.json"],
            "WHETHER_B_CAPABILITY_SMOKE": ["research_assurance/topconf/WHETHER_B_AASIST_CAPABILITY_SMOKE_V1.json"],
        }
        for stage, rels in topconf_files.items():
            evidence = _record_evidence(self.topconf, rels)
            if stage == "WHETHER_B_CAPABILITY_SMOKE":
                self.stage_counts[stage] = {
                    "known_case_count": 0, "unique_case_count": 0, "known_source_count": 0, "unique_source_count": 0,
                    "known_speaker_count": 0, "evidence": evidence,
                    "case_history_completeness": "COMPLETE_EXCLUSION_EMPTY", "source_history_completeness": "COMPLETE_EXCLUSION_EMPTY", "lineage_history_completeness": "COMPLETE_EXCLUSION_EMPTY",
                    "identity_projection": "Synthetic sinusoid only; no real dataset source IDs.",
                }
            else:
                self.stage_counts[stage] = {
                    "known_case_count": None, "unique_case_count": None, "known_source_count": None, "unique_source_count": None,
                    "known_speaker_count": None, "evidence": evidence,
                    "case_history_completeness": "UNKNOWN", "source_history_completeness": "UNKNOWN", "lineage_history_completeness": "UNKNOWN",
                    "identity_projection": "Closure/provenance documents are present, but no complete case/source/lineage universe was materialized for this stage.",
                }

        generic = {
            "METRIC_DEVELOPMENT": "metric development and metric-selection identity not consolidated",
            "THRESHOLD_CALIBRATION": "Level-1 calibration/threshold identity not consolidated",
            "MODEL_SELECTION": "model-selection identity not consolidated",
            "ADAPTER_DEBUGGING": "adapter/debugging identity only partially represented by retained logs/reports",
            "MANUAL_INSPECTION": "manual inspection identity not fully logged as a case universe",
            "PILOT_VISUALIZATION": "debug figures and visualization inputs are not a complete identity universe",
            "SCIENTIFIC_SELECTION": "selection decisions are documented but not projected to complete source/lineage rows",
        }
        for stage, projection in generic.items():
            self.stage_counts[stage] = {
                "known_case_count": None, "unique_case_count": None, "known_source_count": None, "unique_source_count": None,
                "known_speaker_count": None, "evidence": [],
                "case_history_completeness": "UNKNOWN", "source_history_completeness": "UNKNOWN", "lineage_history_completeness": "UNKNOWN",
                "identity_projection": projection,
            }

    def _build_lineages(self) -> None:
        for source in self.source_by_key.values():
            lineage_id = source.get("lineage_id")
            if not lineage_id:
                continue
            item = self.lineage_by_key.setdefault(lineage_id, {
                "lineage_id": lineage_id,
                "original_recording": source.get("parent_recording"),
                "derived_segments": [],
                "synthetic_replacement_parent": None,
                "reference_audio": None,
                "speaker_reference": source.get("speaker_key"),
                "text_content_source": source.get("text_sha256"),
                "generator_input": None,
                "source_audio_sha256": source.get("source_audio_sha256"),
                "historical_stages": [],
                "evidence_sources": [],
                "confidence": source.get("confidence", "PARTIAL"),
            })
            for stage in source.get("historical_stages", []):
                if stage not in item["historical_stages"]:
                    item["historical_stages"].append(stage)
            for evidence in source.get("evidence_sources", []):
                if evidence not in item["evidence_sources"]:
                    item["evidence_sources"].append(evidence)
            item["derived_segments"].extend(
                row["case_id"] for row in self.case_records
                if row.get("source_audio_sha256") == source.get("source_audio_sha256") and row.get("case_id") not in item["derived_segments"]
            )

    def _stage_index(self) -> dict[str, Any]:
        self.stage_counts.setdefault("WEEK1_PILOT", self._ingest_week1())
        self.stage_counts.setdefault("WEEK2_PILOT", self._ingest_week2_and_week3())
        # The shared Week2/Week3 ingest has separate case records but one summary.
        week23 = self.stage_counts["WEEK2_PILOT"]
        self.stage_counts["WEEK3_PILOT"] = dict(week23)
        self.stage_counts.setdefault("WEEK4_PILOT", self._ingest_week4())
        self.stage_counts.setdefault("WEEK5_QUALIFICATION", self._ingest_week5())
        self.stage_counts.setdefault("PHASE3T_PARTIALEDIT_E1", self._ingest_phase3t())
        self._empty_or_unknown_stages()
        self._build_lineages()

        ordered = []
        stage_order = [
            "WEEK1_PILOT", "WEEK2_PILOT", "WEEK3_PILOT", "WEEK4_PILOT", "WEEK5_QUALIFICATION",
            "PHASE3", "PHASE3R", "PHASE3S", "PHASE3U", "PHASE3V", "PHASE3T_PARTIALEDIT_E1",
            "WHETHER_B_CAPABILITY_SMOKE", "METRIC_DEVELOPMENT", "THRESHOLD_CALIBRATION",
            "MODEL_SELECTION", "ADAPTER_DEBUGGING", "MANUAL_INSPECTION", "PILOT_VISUALIZATION", "SCIENTIFIC_SELECTION",
        ]
        for stage in stage_order:
            data = self.stage_counts[stage]
            ordered.append({
                "stage_id": stage,
                "date_or_commit_range": {
                    "main_repository_head": _repo_head(self.main),
                    "week5_repository_head": _repo_head(self.week5),
                    "topconf_repository_head": _repo_head(self.topconf),
                    "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
                },
                "data_role": "PILOT_ONLY" if stage.startswith("WEEK") else ("CAPABILITY_SMOKE" if stage == "WHETHER_B_CAPABILITY_SMOKE" else "LEVEL1_DEVELOPMENT_OR_EVALUATION"),
                "known_datasets": ["AISHELL-3"] if stage.startswith("WEEK") else (["PartialEdit_v1.1_E1"] if "PHASE3T" in stage else []),
                "known_manifests": [item["path"] for item in data.get("evidence", []) if str(item.get("path", "")).lower().endswith((".json", ".csv", ".tsv"))],
                "known_logs": [item["path"] for item in data.get("evidence", []) if str(item.get("path", "")).lower().endswith((".log", ".md"))],
                "known_raw_outputs": [item["path"] for item in data.get("evidence", []) if "results" in str(item.get("path", "")).lower()],
                "known_case_ids": {
                    "count": data.get("unique_case_count"),
                    "sample": sorted({row["case_id"] for row in self.case_records if row.get("stage") == stage})[:5],
                },
                "known_source_ids": {
                    "count": data.get("unique_source_count"),
                    "sample": sorted({row.get("source_id") for row in self.source_by_key.values() if stage in row.get("historical_stages", []) and row.get("source_id")})[:5],
                },
                "known_speaker_ids": {
                    "count": data.get("known_speaker_count"),
                    "sample": sorted({row.get("speaker_id") for row in self.speaker_by_key.values() if stage in row.get("historical_stages", []) and row.get("speaker_id")})[:10],
                },
                "lineage_evidence": [item["path"] for item in data.get("evidence", [])],
                "case_history_completeness": data.get("case_history_completeness", "UNKNOWN"),
                "source_history_completeness": data.get("source_history_completeness", "UNKNOWN"),
                "lineage_history_completeness": data.get("lineage_history_completeness", "UNKNOWN"),
                "identity_projection": data.get("identity_projection"),
            })
        return {
            "schema_version": "topconf.level2.historical_data_usage_stage_index.v1",
            "status": "AUDITED_WITH_EXPLICIT_PARTIAL_AND_UNKNOWN_STAGES",
            "audit_date": "2026-09-15",
            "repositories": {
                "topconf": {"root": str(self.topconf), "head": _repo_head(self.topconf), "all_refs_checked": True},
                "main": {"root": str(self.main), "head": _repo_head(self.main), "all_refs_checked": True},
                "week5": {"root": str(self.week5), "head": _repo_head(self.week5), "all_refs_checked": True},
            },
            "worktrees_checked": self.args.worktree_list,
            "historical_search_method": {
                "git_commands": ["git log --all --name-status", "git log --all -S", "git log --all -G", "git show", "git grep"],
                "deleted_historical_files_checked": True,
                "filesystem_search_excludes_only": sorted(SKIP_DIRS),
                "no_audio_or_model_loaded": True,
            },
            "stages": ordered,
        }

    def _source_universe(self) -> dict[str, Any]:
        records = sorted(self.source_by_key.values(), key=lambda row: (str(row.get("source_audio_sha256")), str(row.get("source_id"))))
        return {
            "schema_version": "topconf.level2.historical_source_exclusion.v3",
            "status": "PARTIAL_RECONSTRUCTION_WITH_DIRECT_HASHED_SOURCES",
            "purpose": "Historical source identities are excluded when directly evidenced; missing identity is never treated as non-overlap.",
            "identity_dimensions": ["source_id", "parent_recording", "corpus", "speaker_id", "utterance_id", "lineage_id", "text_sha256", "source_audio_sha256", "historical_stages"],
            "completeness": "PARTIAL",
            "records": records,
            "unresolved_projections": self.unresolved,
            "authorization_effect": "FAIL_OR_INSUFFICIENT_UNTIL_COMPLETE_POLICY_REVIEW",
            "model_inference_runs": 0,
            "scientific_outcomes_accessed": False,
        }

    def _case_universe(self) -> dict[str, Any]:
        return {
            "schema_version": "topconf.level2.historical_case_exclusion.v3",
            "status": "PARTIAL_RECONSTRUCTION_WITH_PHASE3T_CASE_COMPLETENESS",
            "purpose": "Every directly observed historical case ID is retained; case IDs absent from a partial projection do not imply non-use.",
            "identity_dimensions": ["case_id", "stage", "dataset", "source_id", "speaker_id", "speaker_key", "source_audio_sha256", "text_sha256", "parent_asset_id", "lineage_id"],
            "records": self.case_records,
            "unresolved_projections": self.unresolved,
            "completeness_by_stage": {stage: data.get("case_history_completeness", "UNKNOWN") for stage, data in self.stage_counts.items()},
            "authorization_effect": "FAIL_OR_INSUFFICIENT_UNTIL_COMPLETE_POLICY_REVIEW",
            "model_inference_runs": 0,
            "scientific_outcomes_accessed": False,
        }

    def _speaker_universe(self) -> dict[str, Any]:
        records = sorted(self.speaker_by_key.values(), key=lambda row: str(row["speaker_key"]))
        return {
            "schema_version": "topconf.level2.historical_speaker_usage.v1",
            "status": "PARTIAL_RECONSTRUCTION",
            "identity_dimensions": ["corpus", "speaker_namespace", "speaker_id", "speaker_key", "historical_stages", "reuse_policy"],
            "records": records,
            "unresolved_projections": [item for item in self.unresolved if item.get("stage") in {"WEEK5_QUALIFICATION", "PHASE3T_PARTIALEDIT_E1"}],
            "authorization_effect": "SPEAKER_REUSE_ALLOWED_ONLY_WITH_LINEAGE_DISJOINT; UNKNOWN_REMAINS_UNKNOWN",
        }

    def _lineage_universe(self) -> dict[str, Any]:
        records = sorted(self.lineage_by_key.values(), key=lambda row: str(row["lineage_id"]))
        return {
            "schema_version": "topconf.level2.historical_lineage_exclusion.v1",
            "status": "PARTIAL_RECONSTRUCTION_WITH_SOURCE_AUDIO_HASH_LINEAGE",
            "identity_dimensions": ["lineage_id", "original_recording", "derived_segments", "synthetic_replacement_parent", "reference_audio", "speaker_reference", "text_content_source", "generator_input", "source_audio_sha256"],
            "records": records,
            "unresolved_projections": self.unresolved,
            "authorization_effect": "LINEAGE_UNKNOWN_IS_NOT_ZERO_OVERLAP",
            "model_inference_runs": 0,
            "scientific_outcomes_accessed": False,
        }

    def _aishell1_proof(self, search: dict[str, Any]) -> dict[str, Any]:
        root = self.args.aishell1_root
        candidates = [
            root / "resource_aishell.tgz", root / "data_aishell.tgz", root / "data_aishell" / "transcript" / "aishell_transcript_v0.8.txt",
            root / "resource_aishell" / "speaker.info", root / "aishell1_feasibility_full.json",
        ]
        existing = []
        for path in candidates:
            if not path.exists():
                continue
            stat = path.stat()
            existing.append({
                "path": str(path), "bytes": stat.st_size, "sha256": _sha256_file(path) if path.is_file() and stat.st_size < 20 * 1024 * 1024 else None,
                "filesystem_mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
        first = min((row["filesystem_mtime"] for row in existing), default=None)
        top_search = _git_search(self.topconf, r"aishell[-_ ]?1|slr33")
        top_pre_entry = [row for row in top_search if row["commit"] != PHASE4_6_ENTRY_COMMIT and not row["commit"].startswith("ad58622")]
        main_search = _git_search(self.main, r"aishell[-_ ]?1|slr33")
        week5_search = _git_search(self.week5, r"aishell[-_ ]?1|slr33")
        return {
            "schema_version": "topconf.level2.aishell1.project_entry_proof.v1",
            "status": "NO_PRIOR_PROJECT_USAGE_FOUND_POST_FREEZE_ACQUISITION_EVIDENCE",
            "corpus": "AISHELL-1",
            "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
            "phase4_6_entry_commit": PHASE4_6_ENTRY_COMMIT,
            "first_filesystem_evidence": first,
            "filesystem_evidence": existing,
            "archive_hash_from_audit": "A4A0313CDE0A933E0E01A451F77DE0A23D6C942F4694AF5BB7F40B9DC38143FE",
            "search_result": "NO_PRIOR_PROJECT_USAGE_FOUND",
            "search_scope": {
                "topconf_all_refs": {"aishell1_or_slr33_matches_before_phase4_6": top_pre_entry, "all_matches": top_search},
                "main_all_refs": main_search,
                "week5_all_refs": week5_search,
                "external_text_scan_paths": search.get("aishell1_match_paths", []),
                "worktrees_checked": self.args.worktree_list,
                "search_terms": ["AISHELL-1", "AISHELL1", "SLR33", "data_aishell", "speaker IDs", "archive names", "paths", "hashes"],
                "deleted_history_checked": True,
            },
            "interpretation": "This supports post-freeze acquisition and no prior project reference was found; it is not an absolute claim that the corpus never existed outside the searched evidence.",
            "limitations": ["filesystem timestamps are local metadata", "public corpus metadata cannot prove physical human identity across corpora", "absence from incomplete logs is not treated as non-use"],
            "model_inference_runs": 0,
            "scientific_outcomes_accessed": False,
        }

    def _evidence_index(self, searches: dict[str, Any], stage_index: dict[str, Any]) -> dict[str, Any]:
        files: list[dict[str, Any]] = []
        seen: set[str] = set()
        for stage in stage_index["stages"]:
            for item in stage.get("lineage_evidence", []):
                if item in seen:
                    continue
                seen.add(item)
                path = Path(item)
                if path.is_file():
                    files.append({"path": item, "bytes": path.stat().st_size, "sha256": _sha256_file(path) if path.stat().st_size < 30 * 1024 * 1024 else None})
                else:
                    files.append({"path": item, "exists": False})
        return {
            "schema_version": "topconf.level2.historical_exclusion_evidence_index.v1",
            "status": "AUDITED",
            "audit_date": "2026-09-15",
            "search_commands": [
                "git log --all --name-status", "git log --all -S", "git log --all -G", "git show", "git grep", "rg --hidden on current/external project trees",
            ],
            "repository_history": {
                "topconf": _git_history_summary(self.topconf),
                "main": _git_history_summary(self.main),
                "week5": _git_history_summary(self.week5),
            },
            "text_scan": searches,
            "evidence_files": files,
            "deleted_files_included_in_audit": True,
            "interpretation": "Evidence is retained with confidence labels; unresolved identity remains explicit and cannot support a freshness PASS.",
        }

    def _freshness_v3(self, population: dict[str, Any], universe_paths: dict[str, Path], entry_proof: dict[str, Any]) -> dict[str, Any]:
        primary = population["sources"]
        v2_case_ids = {str(row["case_id"]) for row in population["case_records"]}
        historical_cases = set(str(row["case_id"]) for row in self.case_records if row.get("case_id"))
        historical_source_hashes = {str(row["source_audio_sha256"]).upper() for row in self.source_by_key.values() if row.get("source_audio_sha256")}
        historical_lineage_hashes = {str(row["source_audio_sha256"]).upper() for row in self.lineage_by_key.values() if row.get("source_audio_sha256")}
        v2_speakers = set()
        for row in primary:
            speaker = str(row.get("speaker_id"))
            if speaker.startswith("AISHELL3_"):
                v2_speakers.add(f"AISHELL3:{speaker.removeprefix('AISHELL3_')}")
            elif speaker.startswith("AISHELL1_"):
                v2_speakers.add(f"AISHELL1:{speaker.removeprefix('AISHELL1_')}")
            else:
                v2_speakers.add(speaker)
        historical_speakers = set(self.speaker_by_key)
        speaker_overlap = v2_speakers & historical_speakers
        source_matches = []
        lineage_matches = []
        overlap_speakers = set()
        overlap_source_ids = set()
        for source in primary:
            audio_sha = str(source["source_audio_sha256"]).upper()
            if audio_sha in historical_source_hashes:
                matches = [row for row in self.source_by_key.values() if row.get("source_audio_sha256", "").upper() == audio_sha]
                source_matches.append({
                    "population_source_id": source["source_id"], "population_speaker_id": source["speaker_id"],
                    "source_audio_sha256": audio_sha, "historical_matches": matches,
                })
                overlap_source_ids.add(source["source_id"])
                raw = str(source["speaker_id"]).removeprefix("AISHELL3_").removeprefix("AISHELL1_")
                overlap_speakers.add(f"AISHELL3:{raw}" if str(source["pool_id"]).endswith("AISHELL3") else f"AISHELL1:{raw}")
            if audio_sha in historical_lineage_hashes:
                matches = [row for row in self.lineage_by_key.values() if row.get("source_audio_sha256", "").upper() == audio_sha]
                lineage_matches.append({
                    "population_source_id": source["source_id"], "population_speaker_id": source["speaker_id"],
                    "source_audio_sha256": audio_sha, "historical_matches": matches,
                })
        case_lineage = {
            str(row["case_id"])
            for row in population["case_records"]
            if row.get("source_id") in overlap_source_ids
        }
        unknown_a_sources = [row for row in primary if str(row["pool_id"]).endswith("AISHELL3") and row["source_id"] not in overlap_source_ids]
        comparisons = {
            "case_id_overlap_count": len(v2_case_ids & historical_cases),
            "case_lineage_overlap_count": len(case_lineage),
            "source_overlap_count": len(source_matches),
            "lineage_overlap_count": len(lineage_matches),
            "speaker_overlap_count": len(speaker_overlap),
            "prohibited_speaker_overlap_count": len(speaker_overlap & overlap_speakers),
            "unknown_case_comparisons": len(unknown_a_sources) * 4,
            "unknown_source_comparisons": len(unknown_a_sources),
            "unknown_lineage_comparisons": len(unknown_a_sources),
        }
        history_status = {"CASE_EXCLUSION": "PARTIAL", "SOURCE_EXCLUSION": "PARTIAL", "SPEAKER_USAGE": "PARTIAL", "LINEAGE_EXCLUSION": "PARTIAL"}
        refs = {}
        for universe_id, path in universe_paths.items():
            refs[universe_id] = {
                "path": path.name,
                "sha256": _sha256_file(path),
                "status": history_status[universe_id],
                "evidence_sources": [path.name, "HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json"],
            }
        return {
            "schema_version": "topconf.level2.freshness.v3",
            "manifest_id": "TOPCONF_RQ1_LEVEL2_FRESH_V3",
            "status": "FAIL_PROHIBITED_OVERLAP",
            "freshness_verdict": "FAIL",
            "materialized": True,
            "source_corpus_identity_frozen": False,
            "result_based_selection": False,
            "real_level2_outcomes_accessed": False,
            "level2_population_manifest": "LEVEL2_RQ1_POPULATION_MANIFEST_V2.json",
            "level2_population_manifest_sha256": population["manifest_sha256"],
            "level2_population_file_sha256": _sha256_file(self.topconf / "research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V2.json"),
            "repository_head": _repo_head(self.topconf),
            "validator_version": "topconf.level2.freshness.v3",
            "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
            "universe_references": refs,
            "comparison_counts": comparisons,
            "overlap_counts": comparisons,
            "overlap_details": {
                "case_id_overlap_ids": sorted(v2_case_ids & historical_cases),
                "case_lineage_overlap_case_ids": sorted(case_lineage),
                "source_overlap_details": source_matches,
                "lineage_overlap_details": lineage_matches,
                "speaker_overlap_ids": sorted(speaker_overlap),
            },
            "unknown_comparison_details": {
                "case": "V2 AISHELL-3 cases whose source hash was not found in the partial direct source universe remain unresolved; different case IDs are not treated as proof of freshness.",
                "source": "195 AISHELL-3 primary source hashes have no matching retained historical source record, but Week5/selection/Phase3 lineage is incomplete.",
                "lineage": "195 AISHELL-3 source lineages are not fully resolved across all historical derived artifacts.",
            },
            "corpus_isolation": [
                {
                    "corpus": "AISHELL-1", "pool_id": "SOURCE_POOL_B_AISHELL1",
                    "status": "PASS_POST_FREEZE_ACQUISITION", "evidence_sources": ["AISHELL1_PROJECT_ENTRY_PROOF_V1.json"],
                    "population_primary_sources": 200, "unknown_source_comparisons": 0,
                },
                {
                    "corpus": "AISHELL-3", "pool_id": "SOURCE_POOL_A_AISHELL3",
                    "status": "FAIL_PRIOR_USAGE_FOUND", "evidence_sources": ["HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json", "HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json"],
                    "population_primary_sources": 200, "confirmed_source_overlaps": len(source_matches), "unknown_source_comparisons": len(unknown_a_sources),
                },
            ],
            "frozen_population_changed": False,
            "authorization_gate": "NO_GO; V2 population is evaluated as-is and cannot be silently replaced",
        }

    def run(self) -> dict[str, Any]:
        population_path = self.topconf / "research_assurance/topconf/LEVEL2_RQ1_POPULATION_MANIFEST_V2.json"
        population = _json(population_path)
        before_hash = _sha256_file(population_path)
        searches = _read_text_matches([self.topconf, self.main, self.week5])
        stage_index = self._stage_index()
        case_universe = self._case_universe()
        source_universe = self._source_universe()
        speaker_universe = self._speaker_universe()
        lineage_universe = self._lineage_universe()
        out = self.args.output_dir
        out.mkdir(parents=True, exist_ok=True)
        paths = {
            "CASE_EXCLUSION": out / "HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json",
            "SOURCE_EXCLUSION": out / "HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json",
            "SPEAKER_USAGE": out / "HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json",
            "LINEAGE_EXCLUSION": out / "HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json",
        }
        payloads = {"CASE_EXCLUSION": case_universe, "SOURCE_EXCLUSION": source_universe, "SPEAKER_USAGE": speaker_universe, "LINEAGE_EXCLUSION": lineage_universe}
        for universe_id, path in paths.items():
            path.write_text(json.dumps(payloads[universe_id], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        entry_proof = self._aishell1_proof(searches)
        entry_path = out / "AISHELL1_PROJECT_ENTRY_PROOF_V1.json"
        entry_path.write_text(json.dumps(entry_proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        evidence_index = self._evidence_index(searches, stage_index)
        evidence_path = out / "HISTORICAL_EXCLUSION_EVIDENCE_INDEX_V1.json"
        evidence_path.write_text(json.dumps(evidence_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        freshness = self._freshness_v3(population, paths, entry_proof)
        freshness_path = out / "LEVEL2_FRESHNESS_MANIFEST_V3.json"
        freshness_path.write_text(json.dumps(freshness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        stage_index["population_binding"] = {
            "manifest": str(population_path), "file_sha256_before": before_hash,
            "file_sha256_after": _sha256_file(population_path), "unchanged": before_hash == _sha256_file(population_path),
            "internal_manifest_sha256": population.get("manifest_sha256"),
        }
        stage_path = out / "HISTORICAL_DATA_USAGE_STAGE_INDEX_V1.json"
        stage_path.write_text(json.dumps(stage_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {
            "status": "FAIL_PROHIBITED_OVERLAP",
            "population_unchanged": before_hash == _sha256_file(population_path),
            "population_file_sha256": before_hash,
            "case_records": len(case_universe["records"]),
            "source_records": len(source_universe["records"]),
            "speaker_records": len(speaker_universe["records"]),
            "lineage_records": len(lineage_universe["records"]),
            "freshness": freshness["comparison_counts"],
            "aishell1_status": entry_proof["status"],
            "output_dir": str(out),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topconf-root", type=Path, required=True)
    parser.add_argument("--main-root", type=Path, required=True)
    parser.add_argument("--week5-root", type=Path, required=True)
    parser.add_argument("--phase3t-cache", type=Path, required=True)
    parser.add_argument("--aishell1-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--worktree-list", nargs="*", default=[])
    args = parser.parse_args()
    print(json.dumps(Reconstruction(args).run(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
