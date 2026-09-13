"""CLI helpers for synthetic-only Phase-4 Level-2 governance rehearsal."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from audiobookbench.topconf.level2.governance import (Level2ValidationError, build_blinded_manifest, canonical_sha256, validate_failure_ledger, validate_level2_manifest, validate_namespace, validate_retry_ledger, validate_reveal_gate)

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
def dump(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def require_synthetic(payload):
    if payload.get("data_source") != "SYNTHETIC_GOVERNANCE_DRY_RUN": raise Level2ValidationError("synthetic governance input required")

def split(manifest, seed, proportions):
    require_synthetic(manifest); validate_level2_manifest(manifest)
    labels = ["train", "dev", "test"]
    if len(proportions) != 3 or sum(proportions) != 100: raise Level2ValidationError("split proportions must total 100")
    sources = {r["source_id"]: r for r in manifest["sources"]}; by_speaker = {}
    for source in sources.values(): by_speaker.setdefault(source["speaker_id"], []).append(source["source_id"])
    for speaker, ids in by_speaker.items():
        bucket = int(canonical_sha256({"speaker": speaker, "seed": seed})[:8], 16) % 100
        total = 0
        for label, cut in zip(labels, proportions):
            total += cut
            if bucket < total: chosen = label; break
        for variant in manifest["variants"]:
            if variant["source_id"] in ids: variant["_assigned_split"] = chosen
    manifest["splits"] = [{"case_id": v["case_id"], "split": v.pop("_assigned_split"), "seed": seed} for v in manifest["variants"]]
    validate_level2_manifest(manifest); return manifest

def authorization_template(args):
    fields = {"protocol_commit": args.protocol_commit, "dataset_hash": args.dataset_hash, "model_set": args.model_set, "checkpoint_hashes": args.checkpoint_hashes, "metrics": args.metrics, "threshold_policy": args.threshold_policy, "seed": args.seed, "namespace": args.namespace}
    missing = [key for key, value in fields.items() if value in (None, "")]
    return {"schema_version": "topconf.rq1.authorization-template.v1", "status": "TEMPLATE_ONLY_NON_AUTHORIZING", "valid": not missing, "missing_required_fields": missing, "fields": fields}

def main(kind: str) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--registry", type=Path); parser.add_argument("--seed", type=int, default=20260913); parser.add_argument("--proportions", default="70,15,15")
    parser.add_argument("--authorization", type=Path); parser.add_argument("--inference", type=Path); parser.add_argument("--protocol-hash"); parser.add_argument("--dataset-hash")
    parser.add_argument("--protocol-commit"); parser.add_argument("--model-set"); parser.add_argument("--checkpoint-hashes"); parser.add_argument("--metrics"); parser.add_argument("--threshold-policy"); parser.add_argument("--namespace")
    args = parser.parse_args()
    try:
        if kind == "auth":
            payload = authorization_template(args); print(json.dumps(payload, indent=2, sort_keys=True)); return 0 if payload["valid"] else 1
        if kind == "namespace":
            payload = load(args.manifest); registry = load(args.registry) if args.registry else []
            validate_namespace(payload, registry); print("PASS: namespace is unused and bound"); return 0
        if kind == "reveal":
            if not all((args.authorization, args.inference, args.protocol_hash, args.dataset_hash)): raise Level2ValidationError("authorization, inference, protocol hash and dataset hash required")
            auth, inference = load(args.authorization), load(args.inference); validate_reveal_gate(auth, inference, args.protocol_hash, args.dataset_hash)
            manifest = load(args.manifest); require_synthetic(manifest); payload = {"schema_version":"topconf.level2.revealed-gt.v1", "status":"SYNTHETIC_GOVERNANCE_DRY_RUN_ONLY", "ground_truth":manifest["ground_truth"]}; dump(args.output, payload); print("PASS: synthetic GT reveal gate"); return 0
        manifest = load(args.manifest)
        if kind == "validate": validate_level2_manifest(manifest); print("PASS: synthetic Level-2 leakage and GT contract"); return 0
        if kind == "split": dump(args.output, split(manifest, args.seed, [int(x) for x in args.proportions.split(",")])); print("PASS: synthetic speaker/source-disjoint split"); return 0
        if kind == "blind": dump(args.output, build_blinded_manifest(manifest)); print("PASS: blinded synthetic inference manifest"); return 0
        if kind == "ledger":
            validate_failure_ledger(manifest["failure_ledger"]); validate_retry_ledger(manifest.get("retry_ledger", []), manifest["failure_ledger"]); print("PASS: failure and retry ledger"); return 0
    except (OSError, ValueError, Level2ValidationError) as exc:
        print(f"FAIL: {exc}"); return 1
    raise AssertionError(kind)

