#!/usr/bin/env python3
"""Week2A dry-run gate checker (READ-ONLY).

Standard library only (PyYAML required at runtime). Never imports torch,
speechbrain or CosyVoice. Never generates audio, never runs A2 metrics, never
modifies repository artifacts; writes a file only when --write-report is given.

Corrective patch — FINAL CHECKER SEMANTIC FIX (WEEK2A GATE CHECKER FINAL
CORRECTIVE PATCH). This file addresses the independent-review HOLD item
"Gate Checker Semantic Correctness":

  ISSUE A  FAIL/ERROR/SKIPPED/unknown must NOT be read as PASS. A phase is
           PASS only when every required obligation is IMPLEMENTED_PASS. The
           checker is fail-closed (everything else -> HOLD/BLOCKED, never PASS).
  ISSUE B  Downstream gates consume the LIVE evaluated status of their upstream
           gate (dependency injection), never the static `status:` string in
           week2a_gate_registry.yaml. The YAML status is DECLARED/EXPECTED only.
  ISSUE C  Day13 prerequisite is DAY12_ANALYSIS_GATE (reason BLOCKED_BY_DAY12);
           Day12 prerequisite is DAY11_METRIC_GATE (reason BLOCKED_BY_DAY11);
           Day11<-Day10, Day10<-Day9, Day9<-Day8.
  ISSUE D  T19 (silence distribution shift report) is satisfied by the Day12
           DIAGNOSTIC report, so it must NOT block DAY11_METRIC_GATE. Excluded
           via `required_before_gate` in the test registry.
  ISSUE E  Evidence PRESENCE alone can never yield a gate PASS. Each gate also
           performs minimal CONTENT validation (presence + content).
  ISSUE F  Fresh Week1 rehash must parse rehash_result.json content
           (status/exit_code/missing/mismatch/matched), not just file existence.
  ISSUE G  Single-gate CLI (--gate dayN) computes its full dependency closure
           lazily; never KeyError.
  ISSUE H  (covered in the test files) PyYAML missing must not silently pass CI.

FINAL CLOSURE PATCH (FIX 1-3 + LOW) — engineering-only hardening that changes
NO scientific / protocol / registry semantics:

  FIX 1   Day9 requires three INDEPENDENT execution-result evidence classes
          (sidecar validator execution PASS, waveform/GT verifier execution
          PASS, official smoke 3/3/0). Source-file presence is recorded as
          informational/non-blocking only (IMPLEMENTATION_PRESENT !=
          VALIDATOR_EXECUTION_PASS). Execution-result artifact names are an
          ENGINEERING_EVIDENCE_ONLY checker contract (added here, not in the
          protocol, because no canonical names are defined in
          WEEK2_DAY9_PREREG.md / A2_SIDECAR_CONTRACT.md).
  FIX 2   Fresh Week1 rehash requires the FULL contract (status, exit_code,
          matched, missing, mismatch all PRESENT) with status=PASS,
          exit_code=0, missing=0, mismatch=0, matched=696 (canonical Week1
          696/696). A bare {"status":"PASS"} must NOT yield REHASH_PASS.
  FIX 3   PyYAML missing => CLI fail-closed (non-zero exit, default 2);
          --allow-missing-yaml explicit opt-out still refuses any gate PASS.
  LOW     Day10 failed_by_class values must be non-negative ints.

Usage:
  python research_assurance/tools/week2a_gate_check.py --gate day8
  python research_assurance/tools/week2a_gate_check.py --all
  python ... --all --write-report research_assurance/week2a_gate_dryrun_v3.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_DIR = HERE.parent
REPO_ROOT = REGISTRY_DIR.parent

# Status vocabulary. Lower rank = "better". Anything not PASS/HOLD is blocking
# or missing; the checker is fail-closed.
RANK = {"PASS": 0, "NOT_APPLICABLE": 1, "HOLD": 2, "BLOCKED": 3, "MISSING_EVIDENCE": 3}

# Canonical successful test result. Only this value clears a phase/obligation.
SUCCESS = "IMPLEMENTED_PASS"

GATE_ORDER = ["day8", "day9", "day10", "day11", "day12", "day13", "claim"]

# Tests that are explicitly NOT testable as PASS (fail-closed on unknown status).
NON_PASS_STATUSES = ("FAIL", "ERROR", "SKIPPED", "NOT_RUN")

# ---------------------------------------------------------------------------
# FIX 1: Day9 execution-result evidence contract (ENGINEERING_EVIDENCE_ONLY).
# No canonical execution-result artifact names are defined in
# WEEK2_DAY9_PREREG.md / A2_SIDECAR_CONTRACT.md, so these checker-level names
# are ADDED here and explicitly labelled. They do NOT alter the scientific
# Day9 gate meaning; they only let the checker locate the EXECUTION proof
# (source-file existence alone is IMPLEMENTATION_PRESENT, never PASS).
DAY9_SIDECAR_VALIDATOR_RESULT = "results/day9/sidecar_validator_result.json"
DAY9_WAVEFORM_GT_VERIFIER_RESULT = "results/day9/waveform_gt_verifier_result.json"
DAY9_OFFICIAL_SMOKE_RESULT = "results/day9/smoke.json"

# Canonical Week1 verify contract (WEEK2_DAY9_PREREG.md §4: 696/696).
CANONICAL_WEEK1_EXPECTED = 696

# CLAIM-GATE MICRO FIX / LOW 1: explicit sentinel returned by
# count_to_be_verified() when the protocol config is absent or unreadable.
# Returning 0 would fake "all placeholders resolved".
CONFIG_MISSING_SENTINEL = "CONFIG_MISSING"


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------
def load_yaml(path: Path):
    try:
        import yaml
    except Exception:
        return None, "PyYAML unavailable (registry not evaluated)"
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, "YAML parse error: %s" % exc


def yaml_available():
    """FIX 3: cheap, import-only probe used by the fail-closed CLI gatekeeper."""
    try:
        import yaml  # noqa: F401
        return True
    except Exception:
        return False


def exists_evidence(rel: str):
    p = REPO_ROOT / rel
    return p.exists(), ("present: %s" % rel) if p.exists() else ("missing: %s" % rel)


# ---------------------------------------------------------------------------
# ISSUE 3: config_flag regex (split into a pure parser for unit testing).
# ---------------------------------------------------------------------------
def parse_config_flag(text: str, name: str):
    """Return the value after `name:` (a non-space token), or 'NOT_FOUND'."""
    m = re.search(r"^\s*%s:\s*(\S+)" % re.escape(name), text, re.M)
    return m.group(1) if m else "NOT_FOUND"


def config_flag(name: str):
    p = REPO_ROOT / "configs/week2a_a2_protocol_draft.yaml"
    if not p.exists():
        return "NOT_FOUND"
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return "NOT_FOUND"
    return parse_config_flag(text, name)


def count_to_be_verified():
    """LOW 1: never return 0 when the config is absent/unreadable — that would
    fake "all TO_BE_VERIFIED placeholders resolved". Returns the explicit
    CONFIG_MISSING sentinel instead (rules then HOLD, fail-closed)."""
    p = REPO_ROOT / "configs/week2a_a2_protocol_draft.yaml"
    if not p.exists():
        return CONFIG_MISSING_SENTINEL
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return CONFIG_MISSING_SENTINEL
    return len(re.findall(r"TO_BE_VERIFIED", text))


def config_placeholders_resolved(n):
    """SENTINEL CRASH FIX: PASS only when the count is a real int == 0.
    CONFIG_MISSING (or any non-int value) must HOLD — never crash, never PASS."""
    return isinstance(n, int) and not isinstance(n, bool) and n == 0


# ---------------------------------------------------------------------------
# Test registry access (with optional injection for tests).
# ---------------------------------------------------------------------------
INJECTED_TESTS = None  # dict tid -> {result_status, phases, required_before_gate}


def set_test_injection(inj):
    global INJECTED_TESTS
    INJECTED_TESTS = inj


def test_statuses():
    if INJECTED_TESTS is not None:
        return {tid: (m["result_status"], m.get("phases")) for tid, m in INJECTED_TESTS.items()}, None
    doc, err = load_yaml(REGISTRY_DIR / "week2a_test_registry.yaml")
    if doc is None:
        return {}, err
    return {t["test_id"]: (t.get("result_status"), t.get("phases")) for t in doc.get("tests", [])}, None


def test_meta():
    """Full per-test metadata (incl. required_before_gate)."""
    if INJECTED_TESTS is not None:
        return {tid: m for tid, m in INJECTED_TESTS.items()}
    doc, err = load_yaml(REGISTRY_DIR / "week2a_test_registry.yaml")
    if doc is None:
        return {}
    return {t["test_id"]: t for t in doc.get("tests", [])}


def required_tests_for_gate(gate_key):
    """Return test_ids whose `required_before_gate` includes `gate_key`.

    BUG 2: used so Day12 explicitly enforces every test that must be satisfied
    BEFORE the DAY12_ANALYSIS_GATE (e.g. T19, which is allowed to slip past
    Day11 but must be IMPLEMENTED_PASS before Day12)."""
    meta = test_meta()
    return [tid for tid, m in meta.items()
            if gate_key in (m.get("required_before_gate") or [])]


def finding_statuses():
    doc, err = load_yaml(REGISTRY_DIR / "week2a_findings_registry.yaml")
    if doc is None:
        return {}, err
    return {f["id"]: (f.get("severity"), f.get("status")) for f in doc.get("findings", [])}, None


def gate_registry():
    doc, err = load_yaml(REGISTRY_DIR / "week2a_gate_registry.yaml")
    if doc is None:
        return {}, err
    return doc.get("gates", {}), None


def rule(rid, source, evidence, status, blocking=True):
    return {"rule": rid, "source": source, "evidence": evidence,
            "status": status, "blocking": blocking}


def worst(rules):
    status = "PASS"
    for r in rules:
        # BUG 1 fix: declared/expected status rules carry blocking=False so they
        # are informational only and never participate in Gate aggregation.
        if r.get("blocking", True) is False:
            continue
        if RANK.get(r["status"], 2) > RANK.get(status, 2):
            status = r["status"]
    return status


# ---------------------------------------------------------------------------
# ISSUE A: phase / obligation success logic (fail-closed).
# ---------------------------------------------------------------------------
def phase_obligations_pass(test_ids, exclude=None):
    """A phase is PASS only when EVERY required obligation is IMPLEMENTED_PASS.

    FAIL / ERROR / SKIPPED / NOT_RUN / unknown status => NOT PASS (fail-closed).
    """
    exclude = set(exclude or [])
    ids = [t for t in test_ids if t not in exclude]
    if not ids:
        return "NOT_APPLICABLE"
    statuses = [test_status_for(t) for t in ids]
    if all(s == SUCCESS for s in statuses):
        return "PASS"
    if any(s in ("FAIL", "ERROR") for s in statuses):
        return "BLOCKED"
    if any(s in ("SKIPPED", "NOT_RUN") for s in statuses):
        return "HOLD"
    # Unknown status => HOLD (never PASS). Fail-closed.
    return "HOLD"


def test_status_for(tid):
    tests, _ = test_statuses()
    return (tests.get(tid) or ("NOT_RUN", []))[0]


def phase_rule_status(phase, gate="DAY11_METRIC_GATE"):
    """Return (status, relevant_ids) for a phase, EXCLUDING tests whose
    required_before_gate does not include `gate` (ISSUE D: T19 excluded from
    DAY11_METRIC_GATE, still classified under PHASE_C)."""
    tests, _ = test_statuses()
    meta = test_meta()
    ids = [k for k, (_, phs) in tests.items() if phase in (phs or [])]
    relevant = []
    for tid in ids:
        rbg = (meta.get(tid) or {}).get("required_before_gate") or []
        if rbg and gate not in rbg:
            continue
        relevant.append(tid)
    return phase_obligations_pass(relevant), relevant


# ---------------------------------------------------------------------------
# ISSUE 8 / F: Week1 hash status — two distinct facts, fresh rehash content-checked.
# ---------------------------------------------------------------------------
def fresh_rehash_status():
    """FIX 2: parse results/week1/rehash_result.json CONTENT with the full
    contract. A bare {"status":"PASS"} is NOT sufficient. Required fields must
    all be PRESENT (no default-to-0/None), and the canonical Week1 verify
    contract requires matched == 696 (WEEK2_DAY9_PREREG.md §4 "696/696").
    Returns (state, detail)."""
    path = REPO_ROOT / "results/week1/rehash_result.json"
    if not path.exists():
        return "NOT_PERFORMED", "missing results/week1/rehash_result.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return "INVALID_REHASH_EVIDENCE", "malformed json: %s" % exc
    if not isinstance(data, dict):
        return "INVALID_REHASH_EVIDENCE", "rehash_result.json not a JSON object"
    # Status is checked FIRST (preserves the status=FAIL -> REHASH_FAIL meaning)
    # but the full field contract is enforced once status==PASS.
    if "status" not in data:
        return "INVALID_REHASH_EVIDENCE", "missing required field: status"
    if data["status"] != "PASS":
        return "REHASH_FAIL", "status=%s (need PASS)" % data["status"]
    # FIX 2: every required field must be PRESENT (never defaulted to 0/None).
    required = ["exit_code", "matched", "missing", "mismatch"]
    absent = [k for k in required if k not in data]
    if absent:
        return "INVALID_REHASH_EVIDENCE", "missing required fields: %s" % ",".join(absent)
    if data["exit_code"] != 0:
        return "REHASH_FAIL", "exit_code=%s (need 0)" % data["exit_code"]
    if data["missing"] != 0:
        return "REHASH_FAIL", "missing=%s (need 0)" % data["missing"]
    if data["mismatch"] != 0:
        return "REHASH_FAIL", "mismatch=%s (need 0)" % data["mismatch"]
    # Canonical Week1 verify contract: 696/696.
    if data.get("expected") is not None and data["expected"] != CANONICAL_WEEK1_EXPECTED:
        return "REHASH_FAIL", "expected=%s (canonical Week1 contract=%d)" % (
            data["expected"], CANONICAL_WEEK1_EXPECTED)
    if data["matched"] != CANONICAL_WEEK1_EXPECTED:
        return "REHASH_FAIL", "matched=%s (canonical Week1 contract=%d)" % (
            data["matched"], CANONICAL_WEEK1_EXPECTED)
    return "REHASH_PASS", ("content validated (status=PASS, exit_code=0, "
                            "missing/mismatch=0, matched=%d)" % CANONICAL_WEEK1_EXPECTED)


def week1_hash_status():
    out = {"declared_status": "MISSING", "fresh_rehash": "NOT_PERFORMED", "detail": ""}
    p = REPO_ROOT / "results/week1/hashes.json"
    if not p.exists():
        out["detail"] = "missing results/week1/hashes.json"
        return out
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        out["detail"] = "unreadable: %s" % exc
        return out
    out["declared_status"] = data.get("status")
    state, detail = fresh_rehash_status()
    out["fresh_rehash"] = state
    out["detail"] = "declared=%s; fresh_rehash=%s (%s)" % (out["declared_status"], state, detail)
    return out


# ---------------------------------------------------------------------------
# ISSUE 4 / E: evidence presence + minimal content validation.
# ---------------------------------------------------------------------------
def resolve_evidence_presence(gate_key):
    gates, _ = gate_registry()
    patterns = (gates.get(gate_key) or {}).get("evidence_search") or []
    found = 0
    parts = []
    files = []
    for pat in patterns:
        try:
            hits = sorted(REPO_ROOT.glob(pat))
        except Exception:
            hits = []
        if hits:
            found += 1
            files.extend(hits)
            parts.append("present: %s" % hits[0].relative_to(REPO_ROOT))
        else:
            parts.append("missing: %s" % pat)
    return found, len(patterns), files, "; ".join(parts)


def _json_first(files):
    for f in files:
        if f.suffix == ".json":
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def _some_parseable(files, exts):
    for f in files:
        if f.suffix not in exts:
            continue
        try:
            txt = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if not txt.strip():
            continue
        if f.suffix == ".json":
            try:
                json.loads(txt)
            except Exception:
                continue
        return True, "parseable %s" % f.name
    return False, "no parseable artifact among %d files" % len(files)


def validate_smoke_payload(data):
    """Validate the official Day9 smoke payload: planned=3, passed=3, failed=0.
    LOW 2: the `failed` field must be EXPLICITLY present and == 0 (a missing
    `failed` must never be treated as 0)."""
    if not isinstance(data, dict):
        return False, "smoke payload not a dict"
    planned = data.get("planned")
    passed = data.get("passed")
    if planned != 3:
        return False, "planned=%s (need 3)" % planned
    if passed != 3:
        return False, "passed=%s (need 3)" % passed
    if "failed" not in data:
        return False, "missing failed field (must be explicitly 0)"
    failed = data.get("failed")
    if failed != 0:
        return False, "failed=%s (need 0)" % failed
    return True, "official smoke 3/3/0 validated"


def validate_day9_smoke(files):
    """Back-compat: validate the first parseable smoke json among `files`."""
    data = _json_first(files)
    if data is None:
        return False, "no parseable smoke json"
    return validate_smoke_payload(data)


def _glob_any(pattern):
    """Return (found_bool, hits) for a single REPO_ROOT-relative glob pattern."""
    try:
        hits = sorted(REPO_ROOT.glob(pattern))
    except Exception:
        return False, []
    return bool(hits), hits


def validate_day9_execution_result(rel_path, label):
    """FIX 1: validate a Day9 execution-result artifact (ENGINEERING_EVIDENCE_ONLY).

    Presence of source code is NOT sufficient; the EXECUTION result must be
    present and PASS. Returns (ok, note, status) where status is the rule
    status (PASS / MISSING_EVIDENCE / HOLD)."""
    p = REPO_ROOT / rel_path
    if not p.exists():
        return False, "%s result artifact missing (%s)" % (label, rel_path), "MISSING_EVIDENCE"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, "%s result malformed json: %s" % (label, exc), "MISSING_EVIDENCE"
    if not isinstance(data, dict):
        return False, "%s result not a JSON object" % label, "MISSING_EVIDENCE"
    status = data.get("status")
    if status != "PASS":
        return False, "%s status=%s (need PASS)" % (label, status), "HOLD"
    failed = data.get("failed", 0)
    if failed not in (0, None):
        return False, "%s failed=%s (need 0)" % (label, failed), "HOLD"
    errors = data.get("errors", 0)
    # Canonical validators serialize their zero-error collection as ``[]``.
    # Accept that schema-equivalent empty collection while still rejecting any
    # non-empty collection or non-zero scalar.
    if errors not in (0, None, []):
        return False, "%s errors=%s (need 0)" % (label, errors), "HOLD"
    return True, "%s execution result PASS (status=PASS, failed/errors=0)" % label, "PASS"


def _day9_smoke_result():
    """MICRO-CLOSURE: read ONLY the canonical official smoke artifact
    (DAY9_OFFICIAL_SMOKE_RESULT = results/day9/smoke.json). No directory scan;
    unrelated JSON files under results/day9 can never satisfy the smoke."""
    p = REPO_ROOT / DAY9_OFFICIAL_SMOKE_RESULT
    if not p.exists():
        return False, "missing %s" % DAY9_OFFICIAL_SMOKE_RESULT
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, "smoke json malformed: %s" % exc
    return validate_smoke_payload(data)


def validate_day10_pilot(files):
    for f in files:
        if f.name == "day10_output_hashes.json":
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception as exc:
                return False, "hash json malformed: %s" % exc
            if d.get("planned") != 23:
                return False, "planned=%s (need 23)" % d.get("planned")
            # BUG 3B: exact split validation (no set() dedup that lets a missing
            # key slip through). Allow list / string / explicit dict forms.
            split = d.get("split")
            ok_split = (
                split == [11, 6, 6]
                or split == "11/6/6"
                or (isinstance(split, dict)
                    and split.get("train") == 11
                    and split.get("val") == 6
                    and split.get("test") == 6)
            )
            if not ok_split:
                return False, "split=%s (need exactly 11/6/6)" % split
            # BUG 3A: BOTH fields are mandatory (was `and`, must be `or`).
            if "succeeded" not in d or "failed_by_class" not in d:
                return False, "missing succeeded and/or failed_by_class"
            succeeded = d.get("succeeded")
            failed_by_class = d.get("failed_by_class")
            # MICRO-CLOSURE: succeeded must be a real non-negative int
            # (booleans are ints in Python but are NOT valid counts).
            if (not isinstance(succeeded, int) or isinstance(succeeded, bool)
                    or succeeded < 0):
                return False, "succeeded=%s (need non-negative int)" % succeeded
            if not isinstance(failed_by_class, dict):
                return False, "failed_by_class=%s (need dict)" % type(failed_by_class).__name__
            # LOW fix: each value must be a non-negative int (rejects
            # {"A": 2, "B": -1} or non-integer counts). Booleans excluded.
            if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0
                       for v in failed_by_class.values()):
                return False, "failed_by_class has non-integer or negative value: %s" % failed_by_class
            if sum(failed_by_class.values()) + succeeded != 23:
                return False, "denominator sum=%d (failed_by_class %d + succeeded %d != 23)" % (
                    sum(failed_by_class.values()) + succeeded,
                    sum(failed_by_class.values()), succeeded)
            return True, "23-case pilot 11/6/6 validated"
    return False, "no day10_output_hashes.json"


def _validate_content(gate_key, files, upstream):
    upstream = upstream or {}
    if gate_key == "DAY9_GATE":
        return validate_day9_smoke(files)
    if gate_key == "DAY10_GATE":
        return validate_day10_pilot(files)
    if gate_key == "DAY11_METRIC_GATE":
        ok, note = _some_parseable(files, (".csv", ".json"))
        return ok, note or "day11 tables present"
    if gate_key in ("DAY12_ANALYSIS_GATE", "DAY13_DECISION_GATE"):
        ok, note = _some_parseable(files, (".csv", ".md"))
        return ok, note or "analysis artifact present"
    if gate_key == "WEEK2A_CLAIM_GATE":
        d10 = upstream.get("day10")
        d11 = upstream.get("day11")
        d12 = upstream.get("day12")
        d13 = upstream.get("day13")
        if not all(s == "PASS" for s in (d10, d11, d12, d13)):
            return False, "prerequisite gates not all PASS (day10=%s day11=%s day12=%s day13=%s)" % (
                d10, d11, d12, d13)
        ok, note = _some_parseable(files, (".csv", ".md"))
        return ok, note or "claim artifacts present"
    return True, "no content contract defined"


def evidence_rule_status(gate_key, upstream):
    """ISSUE E: presence alone never yields PASS. Requires presence complete AND
    minimal content validation (or upstream gate prereq, for claim)."""
    found, total, files, pres_note = resolve_evidence_presence(gate_key)
    if found == 0:
        return "MISSING_EVIDENCE", "%s resolved 0/%d" % (gate_key, total)
    if found < total:
        return "HOLD", "%s presence %d/%d (content not checked)" % (gate_key, found, total)
    ok, cnote = _validate_content(gate_key, files, upstream)
    if not ok:
        return "HOLD", "%s presence ok; content invalid: %s" % (gate_key, cnote)
    return "PASS", "%s presence+content valid: %s" % (gate_key, cnote)


# Back-compat helper used by the dynamic-evidence test; presence only.
def resolve_evidence_for_gate(gate_key: str, label: str):
    found, total, _, parts = resolve_evidence_presence(gate_key)
    # MICRO-CLOSURE: zero configured patterns is a contract failure, never a
    # PASS (found == total == 0 must NOT yield PASS).
    if total == 0:
        return "MISSING_EVIDENCE", "%s resolved %d/%d (no evidence_search patterns): %s" % (
            label, found, total, parts)
    if found == total:
        status = "PASS"
    elif found == 0:
        status = "MISSING_EVIDENCE"
    else:
        status = "HOLD"
    return status, "%s resolved %d/%d: %s" % (label, found, total, parts)


# ---------------------------------------------------------------------------
# Evaluation with dependency injection (ISSUE B) + lazy closure (ISSUE G).
# ---------------------------------------------------------------------------
def evaluate(gate: str, upstream=None):
    upstream = dict(upstream or {})

    # FIX 3: fail-closed guard. Without PyYAML the registry cannot be loaded,
    # so every gate is reported as MISSING_EVIDENCE (never PASS).
    if not yaml_available():
        return [rule("YAML_UNAVAILABLE", "import yaml",
                     "PyYAML missing; registry gates not evaluable (fail-closed)",
                     "MISSING_EVIDENCE")], "MISSING_EVIDENCE"

    def live(pred):
        """Lazily compute a predecessor gate and cache its status in `upstream`.
        This realizes the live-upstream dependency chain without reading the
        static YAML `status:` field."""
        if pred not in upstream:
            _, st = evaluate(pred, upstream)
            upstream[pred] = st
        return upstream[pred]

    rules = []

    def add(rid, source, evidence, status, blocking=True):
        rules.append(rule(rid, source, evidence, status, blocking))

    if gate == "day8":
        declared = (gate_registry()[0].get("DAY8_GATE") or {}).get("status", "UNKNOWN")
        ok, ev = exists_evidence("DAY8_PRECHECK.md")
        add("DAY8_PRECHECK_PRESENT", "WEEK2_A2_PREREGISTRATION_REPORT.md / DAY8 owner", ev,
            "PASS" if ok else "HOLD")
        for flag in ("complete_license_chain_checked", "windows_feasibility_verified",
                     "hardware_requirement_verified", "offline_cache_verified", "determinism_verified"):
            v = config_flag(flag)
            add("DAY8_%s" % flag.upper(), "configs/week2a_a2_protocol_draft.yaml", "%s=%s" % (flag, v),
                "PASS" if v == "true" else "HOLD")
        n = count_to_be_verified()
        add("DAY8_PROVENANCE_FIELDS_RESOLVED", "configs/week2a_a2_protocol_draft.yaml",
            "TO_BE_VERIFIED occurrences=%s" % n,
            "PASS" if config_placeholders_resolved(n) else "HOLD")
        # BUG 1: the YAML `status:` of DAY8_GATE is DECLARED/EXPECTED only. It
        # is recorded as informational (blocking=False) and must NEVER push the
        # live Day8 Gate into HOLD when all real evidence passes.
        add("DAY8_REGISTRY_DECLARED_STATUS", "research_assurance/week2a_gate_registry.yaml",
            "declared_status=%s (DECLARED/EXPECTED, non-blocking)" % declared,
            "PASS", blocking=False)
        return rules, worst(rules)

    if gate == "day9":
        # ISSUE B: consume LIVE day8 result, not YAML DAY8_GATE.status.
        d8 = live("day8")
        add("DAY8_GATE_STATE", "live upstream (DAY8 actual evaluate)", "DAY8_GATE=%s" % (d8 or "UNKNOWN"),
            "PASS" if d8 == "PASS" else "BLOCKED")
        whs = week1_hash_status()
        add("WEEK1_HASH_REGISTRY_DECLARED", "results/week1/hashes.json",
            "declared_status=%s" % whs["declared_status"],
            "PASS" if whs["declared_status"] == "PASS" else "HOLD")
        add("WEEK1_HASH_FRESH_REHASH", "results/week1/rehash_result.json (optional independent rehash)",
            "fresh_rehash=%s" % whs["fresh_rehash"],
            "PASS" if whs["fresh_rehash"] == "REHASH_PASS" else "HOLD")
        n = count_to_be_verified()
        add("A2_CONFIG_PLACEHOLDERS_RESOLVED", "configs/week2a_a2_protocol_draft.yaml",
            "TO_BE_VERIFIED=%s" % n,
            "PASS" if config_placeholders_resolved(n) else "HOLD")
        # FIX 1: source implementation PRESENCE is informational only and never
        # yields PASS (IMPLEMENTATION_PRESENT != VALIDATOR_EXECUTION_PASS).
        ok_src_v, _ = _glob_any("src/**/a2_sidecar_validator*.py")
        add("SIDECAR_VALIDATOR_IMPLEMENTATION_PRESENT",
            "ENGINEERING_EVIDENCE_ONLY: src/**/a2_sidecar_validator*.py",
            "present" if ok_src_v else "absent",
            "PASS" if ok_src_v else "MISSING_EVIDENCE", blocking=False)
        ok_src_w, _ = _glob_any("src/**/a2_waveform_gt_verifier*.py")
        add("WAVEFORM_GT_VERIFIER_IMPLEMENTATION_PRESENT",
            "ENGINEERING_EVIDENCE_ONLY: src/**/a2_waveform_gt_verifier*.py",
            "present" if ok_src_w else "absent",
            "PASS" if ok_src_w else "MISSING_EVIDENCE", blocking=False)
        # FIX 1: three INDEPENDENT execution-result evidence classes (blocking).
        ok_sv, note_sv, st_sv = validate_day9_execution_result(
            DAY9_SIDECAR_VALIDATOR_RESULT, "SIDECAR_VALIDATOR")
        add("SIDECAR_VALIDATOR_EXECUTION_RESULT",
            "ENGINEERING_EVIDENCE_ONLY: " + DAY9_SIDECAR_VALIDATOR_RESULT, note_sv, st_sv)
        ok_wv, note_wv, st_wv = validate_day9_execution_result(
            DAY9_WAVEFORM_GT_VERIFIER_RESULT, "WAVEFORM_GT_VERIFIER")
        add("WAVEFORM_GT_VERIFIER_EXECUTION_RESULT",
            "ENGINEERING_EVIDENCE_ONLY: " + DAY9_WAVEFORM_GT_VERIFIER_RESULT, note_wv, st_wv)
        ok_smoke, note_smoke = _day9_smoke_result()
        add("OFFICIAL_SMOKE_3_3_0", DAY9_OFFICIAL_SMOKE_RESULT + " (official 3/3/0)",
            note_smoke, "PASS" if ok_smoke else "MISSING_EVIDENCE")
        # Legacy consolidated rule (kept for ISSUE B test compatibility): PASS
        # only when all three execution-evidence classes pass.
        consolidated = (st_sv == "PASS" and st_wv == "PASS" and ok_smoke)
        add("A2_SIDECAR_VALIDATOR_AND_SMOKE",
            "FIX1 consolidated: sidecar_exec AND waveform_exec AND smoke 3/3/0",
            "sidecar_exec=%s waveform_exec=%s smoke=%s" % (st_sv == "PASS", st_wv == "PASS", ok_smoke),
            "PASS" if consolidated else "MISSING_EVIDENCE")
        return rules, worst(rules)

    if gate == "day10":
        d9 = live("day9")
        add("DAY9_GATE_STATE", "live upstream (DAY9 actual evaluate)", "DAY9_GATE=%s" % (d9 or "UNKNOWN"),
            "PASS" if d9 == "PASS" else "BLOCKED")
        st, ev = evidence_rule_status("DAY10_GATE", upstream)
        add("A2_PILOT_OUTPUTS_AND_DENOMINATOR", "week2a_gate_registry.yaml#DAY10_GATE (presence+content)", ev, st)
        return rules, worst(rules)

    if gate == "day11":
        d10 = live("day10")
        add("DAY10_GATE_STATE", "live upstream (DAY10 actual evaluate)", "DAY10_GATE=%s" % (d10 or "UNKNOWN"),
            "PASS" if d10 == "PASS" else "BLOCKED")
        # ISSUE A + D: phase PASS only on IMPLEMENTED_PASS; T19 excluded from Day11.
        tests, terr = test_statuses()
        if tests:
            for phase in ("PHASE_A_PRE_A2_UNIT", "PHASE_B_FIXTURE_MANIFEST", "PHASE_C_POST_A2_DATA"):
                st, ids = phase_rule_status(phase)
                sts = {t: test_status_for(t) for t in ids}
                add("TESTS_%s" % phase, "week2a_test_registry.yaml (required_before_gate aware)",
                    "%d obligations [%s]; statuses=%s" % (len(ids), ",".join(ids), sts), st)
        else:
            add("TEST_REGISTRY_LOADED", "week2a_test_registry.yaml", terr or "empty", "HOLD")
        finds, _ = finding_statuses()
        p0 = [k for k, (sev, _) in finds.items() if sev == "HIGH"]
        unresolved = [k for k in p0 if finds[k][1] != "RESOLVED"]
        add("P0_FINDINGS_RESOLVED", "week2a_findings_registry.yaml",
            "HIGH findings=%s unresolved=%s" % (sorted(p0), sorted(unresolved)),
            "PASS" if not unresolved else "HOLD")
        ok, ev = exists_evidence("results/day6b/metrics_by_split.csv")
        add("FROZEN_THRESHOLD_SOURCE_PRESENT", "results/day6b/metrics_by_split.csv", ev,
            "PASS" if ok else "MISSING_EVIDENCE")
        st9 = test_status_for("T09")
        add("TEST_A2_THRESHOLD_REUSE_FROZEN", "week2a_test_registry.yaml",
            "T09 result_status=%s" % st9, "PASS" if st9 == SUCCESS else "HOLD")
        st8 = test_status_for("T08")
        add("DETECTOR_DENYLIST_TEST", "week2a_test_registry.yaml",
            "T08 result_status=%s" % st8, "PASS" if st8 == SUCCESS else "HOLD")
        st, ev = evidence_rule_status("DAY11_METRIC_GATE", upstream)
        add("A2_METRIC_INPUTS_AND_TABLES", "week2a_gate_registry.yaml#DAY11_METRIC_GATE (presence+content)", ev, st)
        return rules, worst(rules)

    if gate in ("day12", "day13"):
        prev = "DAY11_METRIC_GATE" if gate == "day12" else "DAY12_ANALYSIS_GATE"
        # ISSUE C: live predecessor (day11 for day12, day12 for day13).
        prev_status = live("day11" if gate == "day12" else "day12")
        add("%s_STATE" % prev, "live upstream (%s actual evaluate)" % prev,
            "%s=%s" % (prev, prev_status or "UNKNOWN"),
            "PASS" if prev_status == "PASS" else "BLOCKED")
        # BUG 2: Day12 must explicitly enforce every test required before the
        # DAY12_ANALYSIS_GATE (T19 silence-distribution-shift report). T19 is
        # excluded from Day11 but cannot slip past Day12.
        if gate == "day12":
            req_t = required_tests_for_gate("DAY12_ANALYSIS_GATE")
            if req_t:
                sts = [test_status_for(t) for t in req_t]
                if all(s == SUCCESS for s in sts):
                    tst = "PASS"
                elif any(s in ("FAIL", "ERROR") for s in sts):
                    tst = "BLOCKED"
                else:  # SKIPPED / NOT_RUN / unknown => HOLD (fail-closed)
                    tst = "HOLD"
                add("TESTS_REQUIRED_BEFORE_DAY12",
                    "week2a_test_registry.yaml#required_before_gate[DAY12_ANALYSIS_GATE]",
                    "tests=%s statuses=%s" % (req_t, dict(zip(req_t, sts))), tst)
        docname = "WEEK2_DAY12_MECHANISM_PREREG.md" if gate == "day12" else "WEEK2_DAY13_DECISION_TREE.md"
        ok, ev = exists_evidence("research_assurance/" + docname)
        add("PREREGISTRATION_DOCUMENT_PRESENT", "research_assurance/", ev, "PASS" if ok else "MISSING_EVIDENCE")
        gk = "DAY12_ANALYSIS_GATE" if gate == "day12" else "DAY13_DECISION_GATE"
        st, ev = evidence_rule_status(gk, upstream)
        add("A2_OUTPUT_AVAILABLE", "week2a_gate_registry.yaml#%s (presence+content)" % gk, ev, st)
        return rules, worst(rules)

    if gate == "claim":
        doc, err = load_yaml(REGISTRY_DIR / "week2a_claim_registry.yaml")
        if doc is None:
            add("CLAIM_REGISTRY_LOADED", "week2a_claim_registry.yaml", err or "empty", "HOLD")
            return rules, worst(rules)
        add("CLAIM_REGISTRY_LOADED", "week2a_claim_registry.yaml",
            "terms=%d evidence_classes=%d" % (len(doc.get("terms", [])), len(doc.get("evidence_classes", {}))),
            "PASS")
        e6 = str(doc.get("evidence_classes", {}).get("E6", ""))
        # CLAIM-GATE MICRO FIX: E6 explicitly declared NOT AVAILABLE is
        # informational (blocking=False) so it can never drag the E1-E5 claim
        # gate down to NOT_APPLICABLE. If E6 should apply but is unsatisfied
        # (any other E6 text), the rule stays blocking HOLD (fail-closed).
        e6_not_available = "NOT AVAILABLE" in e6.upper()
        add("E6_SECOND_GENERATOR", "week2a_claim_registry.yaml", "E6=%s" % e6[:60],
            "NOT_APPLICABLE" if e6_not_available else "HOLD",
            blocking=not e6_not_available)
        # ISSUE 21: artifact existence alone cannot satisfy the claim gate.
        st, ev = evidence_rule_status("WEEK2A_CLAIM_GATE", upstream)
        add("A2_E1_E5_PRESENT", "week2a_gate_registry.yaml#WEEK2A_CLAIM_GATE (presence+content+prereq gates)", ev, st)
        return rules, worst(rules)

    return rules, "NOT_APPLICABLE"


def block_reason_for(gate, upstream):
    """ISSUE C / 9: specific, live-derived block reasons."""
    if gate == "day9":
        return "BLOCKED_BY_DAY8" if upstream.get("day8") != "PASS" else None
    if gate == "day10":
        return "BLOCKED_BY_DAY9" if upstream.get("day9") != "PASS" else None
    if gate == "day11":
        return "BLOCKED_BY_DAY10" if upstream.get("day10") != "PASS" else None
    if gate == "day12":
        return "BLOCKED_BY_DAY11" if upstream.get("day11") != "PASS" else None
    if gate == "day13":
        return "BLOCKED_BY_DAY12" if upstream.get("day12") != "PASS" else None
    if gate == "claim":
        return "NO_A2_CLAIMS_YET" if upstream.get("claim") != "PASS" else None
    return None


# ---------------------------------------------------------------------------
# ISSUE 5 / C: status propagation derived purely from live evaluated statuses.
# ---------------------------------------------------------------------------
def derive_propagation(statuses: dict):
    d8 = statuses.get("day8")
    d9 = statuses.get("day9")
    d10 = statuses.get("day10")
    d11 = statuses.get("day11")
    d12 = statuses.get("day12")
    d13 = statuses.get("day13")
    cl = statuses.get("claim")
    return {
        "week1": "PASS", "protocol": "PASS", "preregistration": "PASS", "static_compatibility": "PASS",
        "day8": d8,
        "day9": "BLOCKED_BY_DAY8" if d8 != "PASS" else d9,
        "day10": "BLOCKED_BY_DAY9" if d9 != "PASS" else d10,
        "day11": "BLOCKED_BY_DAY10" if d10 != "PASS" else d11,
        "day12": "BLOCKED_BY_DAY11" if d11 != "PASS" else d12,
        "day13": "BLOCKED_BY_DAY12" if d12 != "PASS" else d13,
        "week2a_claims": "NO_A2_CLAIMS_YET" if cl != "PASS" else cl,
    }


def require_yaml_or_exit(allow_skip=False):
    """FIX 3: fail-closed gatekeeper. PyYAML is required to evaluate registry
    gates. If it is unavailable the CLI must NOT silently succeed; it exits
    non-zero (2) unless the operator explicitly opts out with
    --allow-missing-yaml (opt-out still refuses to declare any gate PASS)."""
    if yaml_available():
        return 0
    if allow_skip:
        sys.stderr.write(
            "WARNING: PyYAML unavailable; --allow-missing-yaml set; registry "
            "gates cannot be validated and are reported as MISSING_EVIDENCE "
            "(never PASS).\n")
        return 0
    sys.stderr.write(
        "ERROR: PyYAML is required to evaluate registry gates.\n"
        "Install PyYAML, or pass --allow-missing-yaml to opt out (opt-out "
        "still refuses to declare any gate PASS).\n")
    return 2


def main(argv=None):
    parser = argparse.ArgumentParser(description="Week2A dry-run gate checker (read-only).")
    parser.add_argument("--gate", choices=GATE_ORDER)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write-report", default=None)
    parser.add_argument("--allow-missing-yaml", action="store_true",
                        help="FIX 3: explicitly opt out of the PyYAML requirement "
                             "(registry gates reported as MISSING_EVIDENCE, never PASS)")
    args = parser.parse_args(argv)

    # FIX 3: fail-closed on missing PyYAML (default non-zero exit code 2).
    rc = require_yaml_or_exit(allow_skip=args.allow_missing_yaml)
    if rc != 0:
        return rc

    if args.gate:
        idx = GATE_ORDER.index(args.gate)
        closure = GATE_ORDER[: idx + 1]
    else:
        closure = list(GATE_ORDER)

    report = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "repo_root": str(REPO_ROOT),
              "registry_dir": str(REGISTRY_DIR),
              "gates": {}}

    # ISSUE G / B: sequential live evaluation; each gate lazily computes its
    # upstream predecessors into the shared `upstream` context.
    upstream = {}
    for gate in closure:
        rules, status = evaluate(gate, upstream)
        upstream[gate] = status
        reason = block_reason_for(gate, upstream)
        print("=" * 72)
        print("GATE: %s" % gate.upper())
        for r in rules:
            print("RULE:     %s" % r["rule"])
            print("SOURCE:   %s" % r["source"])
            print("EVIDENCE: %s" % r["evidence"])
            print("STATUS:   %s" % r["status"])
            print("-" * 72)
        print("GATE %s = %s%s" % (gate.upper(), status, (" (%s)" % reason) if reason else ""))
        report["gates"][gate] = {"status": status, "rules": rules, "block_reason": reason}

    report["status_propagation"] = derive_propagation(upstream)

    if args.write_report:
        out = REPO_ROOT / args.write_report if not Path(args.write_report).is_absolute() else Path(args.write_report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("report written: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
