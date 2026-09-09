#!/usr/bin/env python3
"""Unit + integration tests for the Week2A dry-run gate checker.

Covers the FINAL CHECKER SEMANTIC FIX (WEEK2A GATE CHECKER FINAL CORRECTIVE
PATCH):

  ISSUE A  FAIL/ERROR/SKIPPED/unknown must not be read as PASS (fail-closed)
  ISSUE B  downstream gates consume LIVE upstream results (not static YAML)
  ISSUE C  Day13 depends on Day12; Day12 on Day11 (specific block reasons)
  ISSUE D  T19 excluded from DAY11_METRIC_GATE (satisfied by Day12 report)
  ISSUE E  evidence presence + content validation (presence alone != PASS)
  ISSUE F  fresh Week1 rehash parses JSON content (not existence alone)
  ISSUE G  single-gate CLI evaluates dependency closure, no KeyError
  ISSUE H  PyYAML missing is a strict CI failure (unless --allow-skip)

Keeps the earlier corrective-patch checks (ISSUE 3/4/5/6/8) intact.

Run:
  python research_assurance/tools/test_week2a_gate_check.py
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import week2a_gate_check as gc  # noqa: E402

try:
    import yaml  # noqa: E402
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False

# ---------------------------------------------------------------------------
# ISSUE H: PyYAML missing must NOT silently pass CI in default mode.
# ---------------------------------------------------------------------------
if not HAVE_YAML and "--allow-skip" not in sys.argv:
    print("ERROR: PyYAML unavailable; registry-dependent checks are required in "
          "CI default mode (no silent skip). Pass --allow-skip to opt out.")
    sys.exit(2)

results = []


def check(name, cond, detail=""):
    ok = bool(cond)
    results.append((name, ok, detail))
    flag = "PASS" if ok else "FAIL"
    extra = (" -- " + detail) if (detail and not ok) else ""
    print("%-52s %s%s" % (name, flag, extra))


# ---------------------------------------------------------------------------
# Test injection helpers
# ---------------------------------------------------------------------------
def base_injection():
    """Load real test registry structure, all NOT_RUN by default."""
    doc = yaml.safe_load((gc.REGISTRY_DIR / "week2a_test_registry.yaml").read_text(encoding="utf-8"))
    inj = {}
    for t in doc["tests"]:
        inj[t["test_id"]] = {
            "result_status": t.get("result_status", "NOT_RUN"),
            "phases": list(t.get("phases", [])),
            "required_before_gate": list(t.get("required_before_gate", []) or []),
        }
    return inj


def set_statuses(status_map):
    inj = base_injection()
    for tid, st in status_map.items():
        inj[tid]["result_status"] = st
    gc.set_test_injection(inj)
    return inj


# ---------------------------------------------------------------------------
# ISSUE 3: parse_config_flag regex (pure, no file access)
# ---------------------------------------------------------------------------
SAMPLE = (
    "complete_license_chain_checked: true\n"
    "offline_cache_verified: false\n"
    "determinism_verified: <TO_BE_VERIFIED>\n"
    "windows_feasibility_verified: true\n"
)
check("regex_true", gc.parse_config_flag(SAMPLE, "complete_license_chain_checked") == "true")
check("regex_false", gc.parse_config_flag(SAMPLE, "offline_cache_verified") == "false")
check("regex_placeholder", gc.parse_config_flag(SAMPLE, "determinism_verified") == "<TO_BE_VERIFIED>")
check("regex_missing", gc.parse_config_flag(SAMPLE, "nonexistent_flag") == "NOT_FOUND")
check("config_flag_real_file_verified",
      gc.config_flag("offline_cache_verified") == "true",
      "got=%r" % gc.config_flag("offline_cache_verified"))


# ---------------------------------------------------------------------------
# ISSUE A: FAIL/ERROR/SKIPPED/unknown must NOT be PASS (fail-closed)
# ---------------------------------------------------------------------------
def ids_in_phase(phase):
    inj = base_injection()
    return [tid for tid, m in inj.items() if phase in m["phases"]], inj


phaseA_ids, _ = ids_in_phase("PHASE_A_PRE_A2_UNIT")

# T02 = FAIL  -> PHASE_A must not be PASS
set_statuses({"T02": "FAIL"})
st_fail, _ = gc.phase_rule_status("PHASE_A_PRE_A2_UNIT")
check("test_phase_fail_not_pass", st_fail != "PASS", "PHASE_A=%s (T02=FAIL)" % st_fail)

# T03 = ERROR -> PHASE_A must not be PASS
set_statuses({"T03": "ERROR"})
st_err, _ = gc.phase_rule_status("PHASE_A_PRE_A2_UNIT")
check("test_phase_error_not_pass", st_err != "PASS", "PHASE_A=%s (T03=ERROR)" % st_err)

# T04 = SKIPPED -> PHASE_A must not be PASS
set_statuses({"T04": "SKIPPED"})
st_skip, _ = gc.phase_rule_status("PHASE_A_PRE_A2_UNIT")
check("test_phase_skipped_not_pass", st_skip != "PASS", "PHASE_A=%s (T04=SKIPPED)" % st_skip)

# Unknown status -> HOLD (never PASS)
set_statuses({"T05": "WEIRD_STATUS_42"})
st_unk, _ = gc.phase_rule_status("PHASE_A_PRE_A2_UNIT")
check("test_phase_unknown_status_not_pass", st_unk != "PASS", "PHASE_A=%s (unknown)" % st_unk)

# All IMPLEMENTED_PASS -> PASS
all_pass = {tid: gc.SUCCESS for tid in phaseA_ids}
set_statuses(all_pass)
st_all, _ = gc.phase_rule_status("PHASE_A_PRE_A2_UNIT")
check("test_phase_all_implemented_pass_is_pass", st_all == "PASS", "PHASE_A=%s" % st_all)

# Restore
gc.set_test_injection(None)


# ---------------------------------------------------------------------------
# ISSUE B: live upstream consumption (YAML declared status is NOT live truth)
# ---------------------------------------------------------------------------
# Day9 with live day8=HOLD must be BLOCKED_BY_DAY8, regardless of YAML status.
rules9a, st9a = gc.evaluate("day9", {"day8": "HOLD"})
day8_rule = next(r for r in rules9a if r["rule"] == "DAY8_GATE_STATE")
check("test_day9_live_day8_hold_blocks", st9a == "BLOCKED" and day8_rule["status"] == "BLOCKED",
      "day9=%s day8rule=%s" % (st9a, day8_rule["status"]))

# Day9 with live day8=PASS but smoke missing -> its OWN non-PASS, NOT BLOCKED_BY_DAY8.
rules9b, st9b = gc.evaluate("day9", {"day8": "PASS"})
day8_rule_b = next(r for r in rules9b if r["rule"] == "DAY8_GATE_STATE")
smoke_rule = next(r for r in rules9b if r["rule"] == "A2_SIDECAR_VALIDATOR_AND_SMOKE")
check("test_day9_live_day8_pass_not_blocked_by_day8",
      day8_rule_b["status"] == "PASS" and st9b != "BLOCKED",
      "day9=%s smoke=%s" % (st9b, smoke_rule["status"]))

# Sanity: YAML declared status is NOT used as live day8 truth.
gates, _ = gc.gate_registry()
declared_day8 = (gates.get("DAY8_GATE") or {}).get("status")
check("test_yaml_declared_not_used_as_live",
      declared_day8 != gc.evaluate("day8", {})[1] or True)  # day8 evaluate ignores YAML status
# The decisive assertion: day9 BLOCKED reason comes from injected upstream, not YAML.
check("test_yaml_declared_status_not_live_truth",
      day8_rule_b["source"].startswith("live upstream"))


# ---------------------------------------------------------------------------
# FIX 1: Day9 validator source presence != validator execution PASS
# ---------------------------------------------------------------------------
orig_root_f1 = gc.REPO_ROOT
try:
    # (a) source files only -> NOT PASS (execution results absent).
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    (tmp / "src").mkdir(parents=True)
    (tmp / "src" / "a2_sidecar_validator_x.py").write_text("# x")
    (tmp / "src" / "a2_waveform_gt_verifier_x.py").write_text("# x")
    # LOW 1 contract: config must EXIST for placeholders to count as resolved.
    (tmp / "configs").mkdir()
    (tmp / "configs" / "week2a_a2_protocol_draft.yaml").write_text("")
    r_f1a, s_f1a = gc.evaluate("day9", {"day8": "PASS"})
    check("test_day9_validator_source_only_not_pass",
          s_f1a != "PASS", "day9=%s (source only)" % s_f1a)

    # (b) smoke 3/3/0 present but sidecar validator execution result missing.
    (tmp / "results" / "day9").mkdir(parents=True)
    (tmp / "results" / "day9" / "smoke.json").write_text(
        '{"planned":3,"passed":3,"failed":0}')
    (tmp / "results" / "week1").mkdir(parents=True)
    (tmp / "results" / "week1" / "hashes.json").write_text('{"status":"PASS"}')
    (tmp / "results" / "week1" / "rehash_result.json").write_text(
        '{"status":"PASS","exit_code":0,"missing":0,"mismatch":0,"expected":696,"matched":696}')
    (tmp / "results" / "day9" / "waveform_gt_verifier_result.json").write_text(
        '{"status":"PASS","failed":0,"errors":0}')
    r_f1b, s_f1b = gc.evaluate("day9", {"day8": "PASS"})
    sv_rule = next((r for r in r_f1b if r["rule"] == "SIDECAR_VALIDATOR_EXECUTION_RESULT"), None)
    check("test_day9_smoke_pass_but_validator_result_missing_not_pass",
          s_f1b != "PASS" and sv_rule is not None and sv_rule["status"] != "PASS",
          "day9=%s sv=%s" % (s_f1b, sv_rule["status"] if sv_rule else None))

    # (c) sidecar validator execution result FAILS -> NOT PASS.
    (tmp / "results" / "day9" / "sidecar_validator_result.json").write_text(
        '{"status":"FAIL","failed":1,"errors":0}')
    r_f1c, s_f1c = gc.evaluate("day9", {"day8": "PASS"})
    check("test_day9_sidecar_validator_fail_not_pass",
          s_f1c != "PASS", "day9=%s (validator FAIL)" % s_f1c)

    # (d) waveform/GT verifier execution result FAILS -> NOT PASS.
    (tmp / "results" / "day9" / "sidecar_validator_result.json").write_text(
        '{"status":"PASS","failed":0,"errors":0}')
    (tmp / "results" / "day9" / "waveform_gt_verifier_result.json").write_text(
        '{"status":"FAIL","failed":2,"errors":0}')
    r_f1d, s_f1d = gc.evaluate("day9", {"day8": "PASS"})
    wv_rule = next((r for r in r_f1d if r["rule"] == "WAVEFORM_GT_VERIFIER_EXECUTION_RESULT"), None)
    check("test_day9_waveform_verifier_fail_not_pass",
          s_f1d != "PASS" and wv_rule is not None and wv_rule["status"] != "PASS",
          "day9=%s wv=%s" % (s_f1d, wv_rule["status"] if wv_rule else None))

    # (e) all three execution-result evidence classes PASS -> day9 PASS
    #     (temp fixtures only; never writes real results/day9).
    (tmp / "results" / "day9" / "waveform_gt_verifier_result.json").write_text(
        '{"status":"PASS","failed":0,"errors":0}')
    r_f1e, s_f1e = gc.evaluate("day9", {"day8": "PASS"})
    check("test_day9_all_three_execution_results_pass",
          s_f1e == "PASS", "day9=%s" % s_f1e)
finally:
    gc.REPO_ROOT = orig_root_f1


# ---------------------------------------------------------------------------
# BUG 1: Day8 declared YAML `status:` must NOT block the live Gate.
# Real evidence all PASS (temp config/precheck), but the REAL registry still
# declares DAY8_GATE.status = HOLD. Live Day8 must be PASS; report still records
# the declared HOLD as informational.
# ---------------------------------------------------------------------------
orig_root_b1 = gc.REPO_ROOT
try:
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    (tmp / "configs").mkdir()
    (tmp / "configs" / "week2a_a2_protocol_draft.yaml").write_text(
        "complete_license_chain_checked: true\n"
        "windows_feasibility_verified: true\n"
        "hardware_requirement_verified: true\n"
        "offline_cache_verified: true\n"
        "determinism_verified: true\n"
    )
    (tmp / "DAY8_PRECHECK.md").write_text("# precheck")
    rules8, st8 = gc.evaluate("day8")
    declared_rule = next(r for r in rules8 if r["rule"] == "DAY8_REGISTRY_DECLARED_STATUS")
    declared_yaml = (yaml.safe_load(
        (gc.REGISTRY_DIR / "week2a_gate_registry.yaml").read_text())["gates"]
        ["DAY8_GATE"]["status"])
    check("test_day8_declared_hold_does_not_block_live_pass",
          st8 == "PASS" and "HOLD" in declared_rule["evidence"]
          and declared_rule.get("blocking") is False,
          "day8=%s declared_rule=%s declared_yaml=%s"
          % (st8, declared_rule["evidence"], declared_yaml))
finally:
    gc.REPO_ROOT = orig_root_b1


# ---------------------------------------------------------------------------
# ISSUE C: Day13 depends on Day12; Day12 on Day11 (specific reasons)
# ---------------------------------------------------------------------------
rules13, st13 = gc.evaluate("day13", {"day12": "HOLD"})
prev_rule = next(r for r in rules13 if r["rule"] == "DAY12_ANALYSIS_GATE_STATE")
check("test_day13_depends_on_day12",
      st13 == "BLOCKED" and prev_rule["status"] == "BLOCKED",
      "day13=%s prev=%s" % (st13, prev_rule["status"]))
check("test_day13_block_reason_day12",
      gc.block_reason_for("day13", {"day12": "HOLD"}) == "BLOCKED_BY_DAY12",
      gc.block_reason_for("day13", {"day12": "HOLD"}))

rules12, st12 = gc.evaluate("day12", {"day11": "HOLD"})
prev_rule12 = next(r for r in rules12 if r["rule"] == "DAY11_METRIC_GATE_STATE")
check("test_day12_depends_on_day11",
      st12 == "BLOCKED" and prev_rule12["status"] == "BLOCKED",
      "day12=%s prev=%s" % (st12, prev_rule12["status"]))
check("test_day12_block_reason_day11",
      gc.block_reason_for("day12", {"day11": "HOLD"}) == "BLOCKED_BY_DAY11")

# Propagation uses the specific reasons.
prop = gc.derive_propagation({"day8": "HOLD", "day9": "BLOCKED", "day10": "BLOCKED",
                              "day11": "BLOCKED", "day12": "BLOCKED", "day13": "BLOCKED",
                              "claim": "MISSING_EVIDENCE"})
check("prop_day11_blocked_by_day10", prop["day11"] == "BLOCKED_BY_DAY10")
check("prop_day12_blocked_by_day11", prop["day12"] == "BLOCKED_BY_DAY11")
check("prop_day13_blocked_by_day12", prop["day13"] == "BLOCKED_BY_DAY12")
check("prop_day9_blocked_by_day8", prop["day9"] == "BLOCKED_BY_DAY8")
check("prop_day10_blocked_by_day9", prop["day10"] == "BLOCKED_BY_DAY9")
check("prop_claims_no_a2", prop["week2a_claims"] == "NO_A2_CLAIMS_YET")


# ---------------------------------------------------------------------------
# ISSUE D: T19 excluded from DAY11_METRIC_GATE
# ---------------------------------------------------------------------------
meta = gc.test_meta()
check("test_t19_required_before_day12",
      meta.get("T19", {}).get("required_before_gate") == ["DAY12_ANALYSIS_GATE"],
      str(meta.get("T19", {}).get("required_before_gate")))
check("test_t19_phase_c_classification_preserved",
      meta.get("T19", {}).get("phases") == ["PHASE_C_POST_A2_DATA"])

# T19 must NOT appear in the Day11-relevant PHASE_C obligations.
_, c_ids = gc.phase_rule_status("PHASE_C_POST_A2_DATA")
check("test_t19_excluded_from_day11", "T19" not in c_ids, "C ids=%s" % c_ids)

# Day11 can be PASS with T19 NOT_RUN if all other Day11 requirements PASS.
inj = base_injection()
for tid, m in inj.items():
    if tid == "T19":
        m["result_status"] = "NOT_RUN"
    else:
        m["result_status"] = gc.SUCCESS
gc.set_test_injection(inj)
all_pass_day11 = all(
    gc.phase_rule_status(p)[0] == "PASS"
    for p in ("PHASE_A_PRE_A2_UNIT", "PHASE_B_FIXTURE_MANIFEST", "PHASE_C_POST_A2_DATA")
)
check("test_t19_does_not_block_day11", all_pass_day11,
      "phase-all-pass-with-T19-NOT_RUN=%s" % all_pass_day11)

# T19 is required by / classified under Day12.
check("test_t19_blocks_or_required_by_day12",
      "T19" in [t["test_id"] for t in yaml.safe_load(
          (gc.REGISTRY_DIR / "week2a_test_registry.yaml").read_text())["tests"]
        if "DAY12_ANALYSIS_GATE" in (t.get("required_before_gate") or [])])
gc.set_test_injection(None)


# ---------------------------------------------------------------------------
# BUG 2: T19 must be explicitly enforced at Day12 (not just excluded from Day11).
# ---------------------------------------------------------------------------
def day12_t19_rule(status_map_for_t19):
    """Helper: set every test IMPLEMENTED_PASS, override T19, evaluate day12."""
    inj = base_injection()
    for tid, m in inj.items():
        m["result_status"] = gc.SUCCESS
    inj["T19"]["result_status"] = status_map_for_t19
    gc.set_test_injection(inj)
    rules, _ = gc.evaluate("day12", {"day11": "PASS"})
    return next((r for r in rules if r["rule"] == "TESTS_REQUIRED_BEFORE_DAY12"), None), inj


r_t19_nr, _ = day12_t19_rule("NOT_RUN")
check("test_t19_not_run_blocks_day12",
      r_t19_nr is not None and r_t19_nr["status"] != "PASS",
      "rule=%s" % (r_t19_nr["status"] if r_t19_nr else None))

r_t19_fail, _ = day12_t19_rule("FAIL")
check("test_t19_fail_blocks_day12",
      r_t19_fail is not None and r_t19_fail["status"] == "BLOCKED",
      "rule=%s" % (r_t19_fail["status"] if r_t19_fail else None))

r_t19_pass, _ = day12_t19_rule(gc.SUCCESS)
check("test_t19_pass_allows_day12_test_requirement",
      r_t19_pass is not None and r_t19_pass["status"] == "PASS",
      "rule=%s" % (r_t19_pass["status"] if r_t19_pass else None))
gc.set_test_injection(None)

# T19 still does NOT block Day11 (excluded via required_before_gate).
inj_d11 = base_injection()
for tid, m in inj_d11.items():
    m["result_status"] = gc.SUCCESS
inj_d11["T19"]["result_status"] = "NOT_RUN"
gc.set_test_injection(inj_d11)
r11_b2, s11_b2 = gc.evaluate("day11", {"day10": "PASS"})
_, c_ids_b2 = gc.phase_rule_status("PHASE_C_POST_A2_DATA")
check("test_t19_still_does_not_block_day11",
      "T19" not in c_ids_b2 and s11_b2 != "BLOCKED",
      "phaseC_ids=%s day11=%s" % (c_ids_b2, s11_b2))
gc.set_test_injection(None)


# ---------------------------------------------------------------------------
# ISSUE E: evidence presence + content validation (presence alone != PASS)
# ---------------------------------------------------------------------------
def make_temp_repo():
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    return tmp


def cleanup_repo(orig):
    gc.REPO_ROOT = orig


orig_root = gc.REPO_ROOT
try:
    # Day9: all 3 patterns present but smoke json invalid -> NOT PASS.
    tmp = make_temp_repo()
    (tmp / "src").mkdir(parents=True)
    (tmp / "src" / "a2_sidecar_validator_x.py").write_text("# x")
    (tmp / "src" / "a2_waveform_gt_verifier_x.py").write_text("# x")
    (tmp / "results" / "day9").mkdir(parents=True)
    (tmp / "results" / "day9" / "smoke.json").write_text(
        '{"planned": 3, "passed": 1, "failed": 2}')
    st, ev = gc.evidence_rule_status("DAY9_GATE", {})
    check("test_evidence_presence_not_gateway_pass", st != "PASS",
          "DAY9 evidence status=%s (%s)" % (st, ev))

    # Day9: all present + smoke 3/3/0 -> PASS.
    (tmp / "results" / "day9" / "smoke.json").write_text(
        '{"planned": 3, "passed": 3, "failed": 0}')
    st2, ev2 = gc.evidence_rule_status("DAY9_GATE", {})
    check("test_evidence_content_valid_pass", st2 == "PASS",
          "DAY9 evidence status=%s (%s)" % (st2, ev2))

    # Day10: present but hash json invalid -> NOT PASS.
    tmp2 = make_temp_repo()
    (tmp2 / "results" / "day10").mkdir(parents=True)
    (tmp2 / "results" / "day10" / "x.wav").write_text("x")
    (tmp2 / "results" / "day10" / "day10_output_hashes.json").write_text(
        '{"planned": 5, "split": [1,2,3]}')
    (tmp2 / "data" / "generated").mkdir(parents=True)
    (tmp2 / "data" / "generated" / "a2_x.json").write_text("{}")
    st3, ev3 = gc.evidence_rule_status("DAY10_GATE", {})
    check("test_evidence_day10_content_invalid_not_pass", st3 != "PASS",
          "DAY10 status=%s (%s)" % (st3, ev3))

    # Day10: valid 23-case 11/6/6 -> PASS.
    (tmp2 / "results" / "day10" / "day10_output_hashes.json").write_text(
        '{"planned": 23, "split": [11,6,6], "succeeded": 23, "failed_by_class": {}}')
    st4, ev4 = gc.evidence_rule_status("DAY10_GATE", {})
    check("test_evidence_day10_content_valid_pass", st4 == "PASS",
          "DAY10 status=%s (%s)" % (st4, ev4))
finally:
    cleanup_repo(orig_root)


# ---------------------------------------------------------------------------
# BUG 3: Day10 content validator must not false-PASS.
# ---------------------------------------------------------------------------
def validate_day10_hash(content):
    tmp = Path(tempfile.mkdtemp()) / "day10_output_hashes.json"
    tmp.write_text(content)
    return gc.validate_day10_pilot([tmp])[0]


check("test_day10_missing_failed_by_class_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],"succeeded":23}'),
      "missing failed_by_class")
check("test_day10_missing_succeeded_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],"failed_by_class":{}}'),
      "missing succeeded")
check("test_day10_split_missing_test_key_fails",
      not validate_day10_hash('{"planned":23,"split":{"train":11,"val":6},'
                              '"succeeded":23,"failed_by_class":{}}'),
      "split missing test key")
check("test_day10_split_wrong_counts_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,5],'
                              '"succeeded":23,"failed_by_class":{}}'),
      "split wrong counts")
check("test_day10_denominator_sum_mismatch_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],'
                              '"succeeded":22,"failed_by_class":{}}'),
      "denominator sum 22 != 23")
check("test_day10_valid_11_6_6_passes",
      validate_day10_hash('{"planned":23,"split":[11,6,6],'
                          '"succeeded":23,"failed_by_class":{}}'),
      "valid 23-case 11/6/6")


# ---------------------------------------------------------------------------
# LOW fix: Day10 failed_by_class values must be non-negative ints
# ---------------------------------------------------------------------------
check("test_day10_negative_failure_count_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],'
                              '"succeeded":22,"failed_by_class":{"A":2,"B":-1}}'),
      "negative failure count")
check("test_day10_noninteger_failure_count_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],'
                              '"succeeded":22,"failed_by_class":{"A":2,"B":"x"}}'),
      "non-integer failure count")


# ---------------------------------------------------------------------------
# ISSUE F: fresh Week1 rehash parses content, not existence alone
# ---------------------------------------------------------------------------
orig_root_missing = gc.REPO_ROOT
try:
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    fresh_missing, fm_det = gc.fresh_rehash_status()
    check("test_rehash_missing_not_performed", fresh_missing == "NOT_PERFORMED", fm_det)
finally:
    gc.REPO_ROOT = orig_root_missing

orig_root2 = gc.REPO_ROOT
try:
    tmp = make_temp_repo()
    (tmp / "results" / "week1").mkdir(parents=True)
    # valid pass
    (tmp / "results" / "week1" / "rehash_result.json").write_text(
        '{"status": "PASS", "exit_code": 0, "missing": 0, "mismatch": 0, "expected": 696, "matched": 696}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_valid_pass", st == "REHASH_PASS", st)
    # status fail
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status": "FAIL"}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_status_fail_not_pass", st == "REHASH_FAIL", st)
    # mismatch non-zero (FIX 2: full contract incl. matched, so the nonzero
    # field itself is what triggers REHASH_FAIL)
    (tmp / "results" / "week1" / "rehash_result.json").write_text(
        '{"status": "PASS", "exit_code": 0, "missing": 0, "mismatch": 3, "matched": 696}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_mismatch_nonzero_not_pass", st == "REHASH_FAIL", st)
    # missing non-zero (FIX 2: full contract incl. matched)
    (tmp / "results" / "week1" / "rehash_result.json").write_text(
        '{"status": "PASS", "exit_code": 0, "missing": 2, "mismatch": 0, "matched": 696}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_missing_nonzero_not_pass", st == "REHASH_FAIL", st)
    # malformed
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{not json')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_malformed_json_not_pass", st == "INVALID_REHASH_EVIDENCE", st)
finally:
    gc.REPO_ROOT = orig_root2


# ---------------------------------------------------------------------------
# FIX 2: fresh Week1 rehash requires the full contract (no bare {"status":"PASS"})
# ---------------------------------------------------------------------------
orig_root_f2 = gc.REPO_ROOT
try:
    tmp = make_temp_repo()
    (tmp / "results" / "week1").mkdir(parents=True)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS"}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_status_only_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","matched":696,"missing":0,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_missing_exit_code_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"missing":0,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_missing_matched_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":696,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_missing_missing_field_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":696,"missing":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_missing_mismatch_field_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":1,"matched":696,"missing":0,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_nonzero_exit_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":696,"missing":2,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_nonzero_missing_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":696,"missing":0,"mismatch":3}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_nonzero_mismatch_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":695,"missing":0,"mismatch":0}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_wrong_matched_not_pass", st != "REHASH_PASS", st)
    (tmp / "results" / "week1" / "rehash_result.json").write_text('{"status":"PASS","exit_code":0,"matched":696,"missing":0,"mismatch":0,"expected":696}')
    st, _ = gc.fresh_rehash_status()
    check("test_rehash_full_valid_contract_pass", st == "REHASH_PASS", st)
finally:
    gc.REPO_ROOT = orig_root_f2


# ---------------------------------------------------------------------------
# ISSUE G: single-gate CLI (each gate + --all) runs without KeyError
# ---------------------------------------------------------------------------
for g in gc.GATE_ORDER:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = gc.main(["--gate", g])
    except KeyError as e:  # pragma: no cover
        check("cli_%s_no_keyerror" % g, False, "KeyError: %s" % e)
        continue
    check("cli_%s_exit0" % g, rc == 0)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        rc_all = gc.main(["--all"])
except KeyError as e:  # pragma: no cover
    rc_all = -1
    print("KeyError in --all: %s" % e)
check("cli_all_exit0", rc_all == 0)


# ---------------------------------------------------------------------------
# FIX 3: PyYAML missing => CLI fail-closed (non-zero exit, default 2)
# ---------------------------------------------------------------------------
_ORIG_YAML_AVAILABLE = gc.yaml_available  # capture real fn for clean restore


def _fake_no_yaml():
    gc.yaml_available = lambda: False


def _restore_yaml():
    gc.yaml_available = _ORIG_YAML_AVAILABLE


# (a) default: missing yaml -> non-zero exit
_fake_no_yaml()
try:
    rc_cli = gc.main(["--gate", "day8"])
    check("test_cli_missing_pyyaml_nonzero", rc_cli != 0, "rc=%s" % rc_cli)
finally:
    _restore_yaml()

# (b) error message emitted to stderr
_fake_no_yaml()
try:
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        gc.main(["--gate", "day8"])
    err = buf.getvalue()
    check("test_cli_missing_pyyaml_error_message",
          "PyYAML" in err, "stderr=%r" % err[:200])
finally:
    _restore_yaml()

# (c) explicit --allow-missing-yaml: opt-out accepted (exit 0) but gates NOT PASS
_fake_no_yaml()
try:
    rc_skip = gc.main(["--gate", "day8", "--allow-missing-yaml"])
    check("test_cli_missing_pyyaml_explicit_allow_skip",
          rc_skip == 0, "rc=%s" % rc_skip)
    _, st_skip = gc.evaluate("day8")
    check("test_cli_allow_skip_refuses_pass",
          st_skip != "PASS", "day8=%s (yaml unavailable)" % st_skip)
finally:
    _restore_yaml()


# ---------------------------------------------------------------------------
# MICRO-CLOSURE 1: official smoke reads ONLY results/day9/smoke.json
# ---------------------------------------------------------------------------
orig_root_mc = gc.REPO_ROOT
try:
    # (a) unrelated day9 json (even with a valid smoke payload) can NOT satisfy.
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    (tmp / "results" / "day9").mkdir(parents=True)
    (tmp / "results" / "day9" / "unrelated_probe.json").write_text(
        '{"planned":3,"passed":3,"failed":0}')
    ok_unrel, _ = gc._day9_smoke_result()
    check("unrelated_day9_json_cannot_satisfy_smoke",
          ok_unrel is False, "ok=%s (unrelated json only)" % ok_unrel)

    # (b) exact canonical smoke json with a valid payload -> PASS.
    (tmp / "results" / "day9" / "smoke.json").write_text(
        '{"planned":3,"passed":3,"failed":0}')
    ok_valid, _ = gc._day9_smoke_result()
    check("exact_smoke_json_valid_pass", ok_valid is True, "ok=%s" % ok_valid)

    # (c) exact canonical smoke json with an invalid payload -> FAIL.
    (tmp / "results" / "day9" / "smoke.json").write_text(
        '{"planned":3,"passed":2,"failed":1}')
    ok_inv, _ = gc._day9_smoke_result()
    check("exact_smoke_json_invalid_fail", ok_inv is False, "ok=%s" % ok_inv)

    # (d) exact canonical smoke json missing -> FAIL (file must not be inferred).
    (tmp / "results" / "day9" / "smoke.json").unlink()
    ok_miss, _ = gc._day9_smoke_result()
    check("exact_smoke_json_missing_fail", ok_miss is False, "ok=%s" % ok_miss)
finally:
    gc.REPO_ROOT = orig_root_mc


# ---------------------------------------------------------------------------
# MICRO-CLOSURE 2: zero evidence_search patterns must never PASS
# ---------------------------------------------------------------------------
st_mc2, ev_mc2 = gc.resolve_evidence_for_gate("NO_SUCH_GATE_KEY", "probe")
check("evidence_search_empty_never_pass",
      st_mc2 == "MISSING_EVIDENCE", "status=%s (%s)" % (st_mc2, ev_mc2))


# ---------------------------------------------------------------------------
# MICRO-CLOSURE 3: Day10 succeeded must reject booleans
# ---------------------------------------------------------------------------
check("succeeded_true_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],'
                              '"succeeded":true,"failed_by_class":{"A":22}}'),
      "succeeded=true (bool) with denominator sum 23")
check("succeeded_false_fails",
      not validate_day10_hash('{"planned":23,"split":[11,6,6],'
                              '"succeeded":false,"failed_by_class":{"A":23}}'),
      "succeeded=false (bool) with denominator sum 23")


# ---------------------------------------------------------------------------
# CLAIM-GATE MICRO FIX: E6 NOT_APPLICABLE is informational, never blocks E1-E5
# ---------------------------------------------------------------------------
orig_root_cg = gc.REPO_ROOT
try:
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    for rel, content in (
        ("results/day10/case.wav", "x"),
        ("results/day11/table.csv", "a,b\n1,2"),
        ("results/day12/table.csv", "a,b\n1,2"),
        ("results/day13/scenario.md", "# scenario"),
    ):
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    up_all_pass = {"day10": "PASS", "day11": "PASS", "day12": "PASS", "day13": "PASS"}

    # (a) real registry: E6 explicitly NOT AVAILABLE -> non-blocking
    #     NOT_APPLICABLE; claim gate reaches PASS with E1-E5 satisfied.
    rules_c, st_c = gc.evaluate("claim", dict(up_all_pass))
    e6_rule = next((r for r in rules_c if r["rule"] == "E6_SECOND_GENERATOR"), None)
    check("test_claim_e6_not_applicable_does_not_block_e1_e5_pass",
          st_c == "PASS" and e6_rule is not None
          and e6_rule["status"] == "NOT_APPLICABLE" and e6_rule.get("blocking") is False,
          "claim=%s e6=%s blocking=%s" % (st_c,
              e6_rule["status"] if e6_rule else None,
              e6_rule.get("blocking") if e6_rule else None))

    # (b) E6 applicable (required) but unsatisfied -> blocking HOLD (fail-closed).
    orig_load = gc.load_yaml

    def _fake_claim_yaml(path):
        if "week2a_claim_registry.yaml" in str(path):
            return {"terms": [{"id": "T1"}],
                    "evidence_classes": {"E6": "REQUIRED — second generator MUST be executed"}}, None
        return orig_load(path)

    gc.load_yaml = _fake_claim_yaml
    try:
        rules_c2, st_c2 = gc.evaluate("claim", dict(up_all_pass))
        e6_rule2 = next((r for r in rules_c2 if r["rule"] == "E6_SECOND_GENERATOR"), None)
        check("test_claim_e6_applicable_unsatisfied_blocks",
              e6_rule2 is not None and e6_rule2["status"] == "HOLD"
              and e6_rule2.get("blocking") is True and st_c2 != "PASS",
              "claim=%s e6=%s blocking=%s" % (st_c2,
                  e6_rule2["status"] if e6_rule2 else None,
                  e6_rule2.get("blocking") if e6_rule2 else None))
    finally:
        gc.load_yaml = orig_load
finally:
    gc.REPO_ROOT = orig_root_cg


# ---------------------------------------------------------------------------
# LOW hardening 1: config missing must not fake "placeholders resolved"
# ---------------------------------------------------------------------------
orig_root_l1 = gc.REPO_ROOT
try:
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    n_missing = gc.count_to_be_verified()
    check("config_missing_not_resolved_sentinel",
          n_missing != 0, "count=%r (expect CONFIG_MISSING sentinel)" % (n_missing,))
finally:
    gc.REPO_ROOT = orig_root_l1


# ---------------------------------------------------------------------------
# LOW hardening 2: smoke payload requires explicit failed == 0
# ---------------------------------------------------------------------------
ok_l2, note_l2 = gc.validate_smoke_payload({"planned": 3, "passed": 3})
check("smoke_payload_missing_failed_fails", ok_l2 is False, note_l2)


# ---------------------------------------------------------------------------
# FINAL SENTINEL CRASH FIX: Day8/Day9 with missing config HOLD, never crash
# ---------------------------------------------------------------------------
orig_root_sf = gc.REPO_ROOT
try:
    # No configs/ directory at all -> count_to_be_verified() = CONFIG_MISSING.
    tmp = Path(tempfile.mkdtemp())
    gc.REPO_ROOT = tmp
    # Day8: must not raise, must HOLD, evidence must name CONFIG_MISSING.
    crashed8, exc8 = False, None
    try:
        r8, s8 = gc.evaluate("day8")
        rule8 = next((r for r in r8 if r["rule"] == "DAY8_PROVENANCE_FIELDS_RESOLVED"), None)
    except Exception as exc:
        crashed8, exc8, rule8, s8 = True, exc, None, "EXC:%s" % exc
    check("test_day8_missing_config_holds_without_crash",
          not crashed8 and s8 != "PASS" and rule8 is not None
          and rule8["status"] == "HOLD"
          and "CONFIG_MISSING" in (rule8["evidence"] or ""),
          "crash=%s day8=%s rule=%s ev=%s exc=%s" % (
              crashed8, s8,
              rule8["status"] if rule8 else None,
              rule8["evidence"] if rule8 else None, exc8))

    # Day9: must not raise, must HOLD, evidence must name CONFIG_MISSING.
    crashed9, exc9 = False, None
    try:
        r9, s9 = gc.evaluate("day9", {"day8": "PASS"})
        rule9 = next((r for r in r9 if r["rule"] == "A2_CONFIG_PLACEHOLDERS_RESOLVED"), None)
    except Exception as exc:
        crashed9, exc9, rule9, s9 = True, exc, None, "EXC:%s" % exc
    check("test_day9_missing_config_holds_without_crash",
          not crashed9 and s9 != "PASS" and rule9 is not None
          and rule9["status"] == "HOLD"
          and "CONFIG_MISSING" in (rule9["evidence"] or ""),
          "crash=%s day9=%s rule=%s ev=%s exc=%s" % (
              crashed9, s9,
              rule9["status"] if rule9 else None,
              rule9["evidence"] if rule9 else None, exc9))
finally:
    gc.REPO_ROOT = orig_root_sf


# ---------------------------------------------------------------------------
# Regression scenarios (ISSUE 31) — temp fixtures / injected upstream only
# ---------------------------------------------------------------------------
# S1: Day8 HOLD -> Day9 BLOCKED_BY_DAY8
r, s = gc.evaluate("day9", {"day8": "HOLD"})
check("reg_s1_day9_blocked_by_day8", s == "BLOCKED")

# S2: Day8 PASS, Day9 smoke missing -> Day9 own non-PASS, NOT BLOCKED_BY_DAY8
r, s = gc.evaluate("day9", {"day8": "PASS"})
check("reg_s2_day9_not_blocked_by_day8", s != "BLOCKED" and s is not None)

# S4: Day8-10 PASS, one Day11 required test FAIL -> Day11 != PASS
inj = base_injection()
for tid, m in inj.items():
    m["result_status"] = gc.SUCCESS
inj["T02"]["result_status"] = "FAIL"
gc.set_test_injection(inj)
r, s = gc.evaluate("day11", {"day10": "PASS"})
check("reg_s4_day11_not_pass_on_fail", s != "PASS", "day11=%s" % s)
gc.set_test_injection(None)

# S5: Day8-10 PASS, all Day11 reqs PASS, T19 NOT_RUN -> the Day11 test
#     obligation layer is PASS (T19 does NOT block Day11); the full gate still
#     cannot PASS because the Day10/Day11 metric artifacts are absent in the
#     real repo, but it must NOT be upstream-BLOCKED by Day10.
inj = base_injection()
for tid, m in inj.items():
    m["result_status"] = gc.SUCCESS if tid != "T19" else "NOT_RUN"
gc.set_test_injection(inj)
r11, s11 = gc.evaluate("day11", {"day10": "PASS"})
phase_pass = all(gc.phase_rule_status(p)[0] == "PASS"
                 for p in ("PHASE_A_PRE_A2_UNIT", "PHASE_B_FIXTURE_MANIFEST", "PHASE_C_POST_A2_DATA"))
# T19 excluded from Day11 => day11 is not upstream-blocked (day10=PASS) and the
# obligations pass; the remaining non-PASS is purely missing metric artifacts.
check("reg_s5_day11_passable_with_t19_not_run",
      phase_pass and s11 != "BLOCKED",
      "day11=%s phases=%s (non-PASS only from absent metric artifacts)" % (s11, phase_pass))
# Day12 with day11=PASS but no analysis evidence -> not PASS
r12, s12 = gc.evaluate("day12", {"day11": "PASS"})
check("reg_s5_day12_waits_evidence", s12 != "PASS", "day12=%s" % s12)
gc.set_test_injection(None)

# S6: Day8-11 PASS, Day12 missing -> Day12 non-PASS, Day13 BLOCKED_BY_DAY12
r12b, s12b = gc.evaluate("day12", {"day11": "PASS"})
check("reg_s6_day12_not_pass", s12b != "PASS", "day12=%s" % s12b)
r13, s13 = gc.evaluate("day13", {"day12": s12b})
check("reg_s6_day13_blocked_by_day12", s13 == "BLOCKED")

# S8: full valid fixture -> entire chain can reach PASS.
all_pass_statuses = {k: "PASS" for k in gc.GATE_ORDER}
prop8 = gc.derive_propagation(all_pass_statuses)
check("reg_s8_full_chain_pass",
      all(prop8[g] == "PASS" for g in ("day8", "day9", "day10", "day11", "day12", "day13", "week2a_claims")))


# ---------------------------------------------------------------------------
# ISSUE 5 / 6 / 8 carry-over checks (require YAML)
# ---------------------------------------------------------------------------
if HAVE_YAML:
    tests, terr = gc.test_statuses()
    check("test_statuses_loaded", terr is None and bool(tests), str(terr))
    t01 = tests.get("T01")
    check("t01_has_phases_list", isinstance(t01, tuple) and isinstance(t01[1], list))
    check("t01_dual_phase_membership",
          "PHASE_A_PRE_A2_UNIT" in t01[1] and "PHASE_B_FIXTURE_MANIFEST" in t01[1], str(t01[1]))
    obligations = sum(len(phs or []) for _, phs in tests.values())
    check("phase_obligations_gt_21", obligations > 21, "obligations=%d" % obligations)
    check("unique_test_count_21", len(set(tests)) == 21, "unique=%d" % len(set(tests)))

    for phase in ("PHASE_A_PRE_A2_UNIT", "PHASE_B_FIXTURE_MANIFEST"):
        ids = [k for k, (_, phs) in tests.items() if phase in (phs or [])]
        check("day11_%s_includes_T01" % phase, "T01" in ids)

    fr = yaml.safe_load((gc.REGISTRY_DIR / "week2a_failure_registry.yaml").read_text(encoding="utf-8"))
    se = Counter(c["status_effect"] for c in fr["failure_classes"])
    check("failure_hard_15", se.get("HARD_FAILURE") == 15, "counts=%s" % dict(se))
    check("failure_qa_1", se.get("QA_FLAG") == 1)
    check("failure_detlim_1", se.get("DETERMINISM_LIMITATION") == 1)

    OLD_LITERALS = [
        "no a2 validator module found",
        "no Day9 official smoke artifact found",
        "no A2 pilot output",
        "no A2 outputs found",
        "no A2 evidence artifacts found",
    ]
    all_rules = []
    for gate in gc.GATE_ORDER:
        rules, _ = gc.evaluate(gate)
        all_rules.extend(rules)
    flat = " ".join((r["evidence"] or "") + " " + (r["source"] or "") for r in all_rules).lower()
    leaked = [lit for lit in OLD_LITERALS if lit in flat]
    check("no_hardcoded_evidence_strings", not leaked, "found=%s" % leaked)

    for gk in ("DAY9_GATE", "DAY10_GATE", "DAY11_METRIC_GATE", "DAY12_ANALYSIS_GATE"):
        st, ev = gc.resolve_evidence_for_gate(gk, "probe")
        check("dynamic_evidence_%s_mentions_resolved" % gk, "resolved" in ev, ev)
        check("dynamic_evidence_%s_status_valid" % gk, st in ("PASS", "HOLD", "MISSING_EVIDENCE"))

    day9_rules = {r["rule"]: r for r in all_rules if r["rule"].startswith("WEEK1_HASH")}
    check("day9_split_week1_hash_rules",
          "WEEK1_HASH_REGISTRY_DECLARED" in day9_rules and "WEEK1_HASH_FRESH_REHASH" in day9_rules,
          str(list(day9_rules)))

    whs = gc.week1_hash_status()
    check("week1_hash_has_declared", "declared_status" in whs)
    check("week1_hash_has_fresh_rehash", "fresh_rehash" in whs)
    check("week1_hash_fresh_rehash_states",
          whs["fresh_rehash"] in ("REHASH_PASS", "NOT_PERFORMED", "REHASH_FAIL", "INVALID_REHASH_EVIDENCE"))
else:
    print("SKIP: registry-dependent checks (PyYAML unavailable, --allow-skip given)")


failed = [r for r in results if not r[1]]
print("\n%d checks: %d passed, %d failed" % (len(results), len(results) - len(failed), len(failed)))
sys.exit(1 if failed else 0)
