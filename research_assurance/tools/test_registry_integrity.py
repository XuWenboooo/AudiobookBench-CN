#!/usr/bin/env python3
"""Registry integrity tests for the Week2A machine-readable registries.

Read-only: loads YAML and asserts structural invariants. Exits non-zero if any
check fails.

ISSUE H (FINAL CHECKER SEMANTIC FIX): PyYAML missing must NOT silently pass
CI. In the default mode a missing dependency is a hard failure (exit 2). Pass
`--allow-skip` to explicitly opt out (exit 0). The decision logic is exposed as
`decide_exit(has_yaml, argv)` so it can be unit-tested without uninstalling
PyYAML.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_DIR = HERE.parent

try:
    import yaml
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False


def decide_exit(has_yaml, argv):
    """Return the exit code the CI should use for the dependency situation.

    - no yaml and no --allow-skip  -> 2  (strict: refusing to pass silently)
    - no yaml and --allow-skip     -> 0  (explicit opt-out)
    - yaml present                  -> None (run the full suite)
    """
    if not has_yaml and "--allow-skip" not in argv:
        return 2
    if not has_yaml:
        return 0
    return None


def load(name):
    return yaml.safe_load((REGISTRY_DIR / name).read_text(encoding="utf-8"))


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    decision = decide_exit(HAVE_YAML, argv)
    if decision is not None:
        if decision == 2:
            print("ERROR: PyYAML unavailable and --allow-skip not given; refusing to "
                  "pass CI silently. Install PyYAML or run with --allow-skip.")
        else:
            print("SKIP: PyYAML unavailable; registry integrity not evaluated (--allow-skip).")
        return decision

    results = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        results.append((name, ok, detail))
        flag = "PASS" if ok else "FAIL"
        extra = (" -- " + detail) if (detail and not ok) else ""
        print("%-42s %s%s" % (name, flag, extra))

    # -------------------------------------------------------------------
    # Failure registry
    # -------------------------------------------------------------------
    fr = load("week2a_failure_registry.yaml")
    classes = fr.get("failure_classes", [])
    check("failure_count_17", len(classes) == 17, "got %d" % len(classes))

    ALLOWED_FAILURE_KEYS = {
        "name", "trigger", "severity", "retain_row", "retain_waveform",
        "retry_allowed", "amendment_required", "blocks_pilot", "blocks_claim",
        "status_effect", "source", "required_before_gate",
    }
    unexpected = [(c.get("name"), sorted(set(c.keys()) - ALLOWED_FAILURE_KEYS))
                  for c in classes if set(c.keys()) - ALLOWED_FAILURE_KEYS]
    check("failure_no_unexpected_keys", not unexpected, str(unexpected))

    check("failure_trigger_is_str", all(isinstance(c.get("trigger"), str) for c in classes))

    se = Counter(c["status_effect"] for c in classes)
    check("failure_hard_15", se.get("HARD_FAILURE") == 15, "counts=%s" % dict(se))
    check("failure_qa_1", se.get("QA_FLAG") == 1, "counts=%s" % dict(se))
    check("failure_detlim_1", se.get("DETERMINISM_LIMITATION") == 1, "counts=%s" % dict(se))

    byname = {c["name"]: c for c in classes}
    check("rms_match_fail_qa_flag", byname["RMS_MATCH_FAIL"]["status_effect"] == "QA_FLAG")
    check("rms_match_fail_not_block_claim", byname["RMS_MATCH_FAIL"]["blocks_claim"] is False)
    check("determinism_limitation",
          byname["DETERMINISM_MISMATCH"]["status_effect"] == "DETERMINISM_LIMITATION")

    counts = fr.get("counts", {})
    check("counts_block_matches",
          counts.get("total") == 17 and counts.get("HARD_FAILURE") == 15
          and counts.get("QA_FLAG") == 1 and counts.get("DETERMINISM_LIMITATION") == 1,
          str(counts))
    check("qa_flag_only_classes", fr.get("qa_flag_only_classes") == ["RMS_MATCH_FAIL"])
    check("determinism_limitation_classes",
          fr.get("determinism_limitation_classes") == ["DETERMINISM_MISMATCH"])

    # -------------------------------------------------------------------
    # Test registry
    # -------------------------------------------------------------------
    tr = load("week2a_test_registry.yaml")
    tests = tr.get("tests", [])
    check("test_count_21", len(tests) == 21, "got %d" % len(tests))
    ids = [t["test_id"] for t in tests]
    check("test_unique_ids", len(set(ids)) == 21, "unique=%d" % len(set(ids)))
    byn = {t["test_id"]: t for t in tests}

    check("test_phases_are_lists", all(isinstance(t.get("phases"), list) for t in tests))
    check("t01_dual_phase",
          byn["T01"]["phases"] == ["PHASE_A_PRE_A2_UNIT", "PHASE_B_FIXTURE_MANIFEST"],
          str(byn["T01"]["phases"]))
    check("t10_single_phase_list", byn["T10"]["phases"] == ["PHASE_B_FIXTURE_MANIFEST"],
          str(byn["T10"]["phases"]))
    obligations = sum(len(t.get("phases") or []) for t in tests)
    check("phase_obligations_gt_21", obligations > 21, "obligations=%d" % obligations)

    # T19 required_before_gate (ISSUE D): satisfied by Day12, must not block Day11.
    check("t19_required_before_day12",
          byn["T19"].get("required_before_gate") == ["DAY12_ANALYSIS_GATE"],
          str(byn["T19"].get("required_before_gate")))

    # -------------------------------------------------------------------
    # Leakage registry (14 vectors; 4 covered by report/validator checks only)
    # -------------------------------------------------------------------
    lr = load("week2a_leakage_registry.yaml")
    vectors = lr.get("vectors", [])
    check("leakage_count_14", len(vectors) == 14, "got %d" % len(vectors))
    REPORT_CHECKS = {"denominator_report_check", "zone_statistics_report_check",
                     "trim_margin_validator_check", "format_sr_validator_check"}
    non_pytest = []
    for v in vectors:
        rt = v.get("required_test")
        vals = rt if isinstance(rt, list) else [rt]
        if any(x in REPORT_CHECKS for x in vals):
            non_pytest.append(v["id"])
    check("leakage_4_report_validator_only",
          set(non_pytest) == {"L7", "L9", "L10", "L13"}, "got=%s" % sorted(non_pytest))

    # -------------------------------------------------------------------
    # Gate registry (7 gates, each with evidence_search)
    # -------------------------------------------------------------------
    gr = load("week2a_gate_registry.yaml")
    gates = gr.get("gates", {})
    check("gate_count_7", len(gates) == 7, "got %d" % len(gates))
    for gk in gates:
        check("gate_%s_has_evidence_search" % gk, "evidence_search" in gates[gk], gk)

    failed = [r for r in results if not r[1]]
    print("\n%d checks: %d passed, %d failed" % (len(results), len(results) - len(failed), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
