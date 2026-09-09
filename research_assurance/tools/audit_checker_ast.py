#!/usr/bin/env python3
"""AST audit for the Week2A gate checker and its test files.

Confirms that none of the checked Python files import torch / speechbrain /
CosyVoice, and that none contain audio-generation / A2-metric calls. Emits a
machine-readable JSON report. Pure stdlib (ast, json, pathlib).

Run:
  python research_assurance/tools/audit_checker_ast.py
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_DIR = HERE.parent

TARGETS = [
    "tools/week2a_gate_check.py",
    "tools/test_registry_integrity.py",
    "tools/test_week2a_gate_check.py",
]
FORBIDDEN = {"torch", "speechbrain", "cosyvoice"}
# Names that would imply the checker actually generates audio or runs metrics.
AUDIO_GEN_CALLS = {"generate_audio", "synthesize", "tts", "run_metrics", "run_a2_metrics"}


def analyze(relpath: str):
    src = (REGISTRY_DIR / relpath).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    forbidden_found = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
                if any(seg.lower() in FORBIDDEN for seg in n.name.lower().split(".")):
                    forbidden_found.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append(mod)
            if any(seg.lower() in FORBIDDEN for seg in mod.lower().split(".")):
                forbidden_found.append(mod)
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                calls.append(f.id)
            elif isinstance(f, ast.Attribute):
                calls.append(f.attr)
    return {
        "file": relpath,
        "imports": sorted(set(imports)),
        "forbidden_imports": sorted(set(forbidden_found)),
        "call_names": sorted(set(calls)),
        "audio_generation_calls": sorted(set(calls) & AUDIO_GEN_CALLS),
        "ok": (not forbidden_found) and (not (set(calls) & AUDIO_GEN_CALLS)),
    }


reports = [analyze(t) for t in TARGETS]
overall_ok = all(r["ok"] for r in reports)
out = {
    "audit": "checker_ast",
    "forbidden_modules": sorted(FORBIDDEN),
    "audio_gen_call_names": sorted(AUDIO_GEN_CALLS),
    "files": reports,
    "overall_ok": overall_ok,
}
(REGISTRY_DIR / "week2a_checker_ast_audit.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("AST audit written: research_assurance/week2a_checker_ast_audit.json (overall_ok=%s)" % overall_ok)
for r in reports:
    print("  %-44s ok=%s forbidden=%s" % (r["file"], r["ok"], r["forbidden_imports"]))
sys.exit(0 if overall_ok else 1)
