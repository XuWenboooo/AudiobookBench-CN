"""Week3 F5 runner.

Scientific execution is deliberately locked in this infrastructure turn. The
engineering-only mode validates the already frozen disposable fixture.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from audiobookbench.security.week3_f5_stage_a import BASE_SEED, generation_seed, sha256_file
from audiobookbench.security.week3_f5_stage_a import (
    InferenceSettings, build_f5_api, build_success_sidecar, construct_replacement, infer_once,
)
from audiobookbench.preprocessing.audio_io import write_audio
from audiobookbench.security.week3_accounting import classify_failure, append_attempt, final_accounting_rows, write_cases_csv
from audiobookbench.security.week3_authorization import validate_authorization_artifact
from audiobookbench.security.week3_pipeline import run_formal_generation, FUTURE_AUTH_REL

PLANNED = REPO / "data/manifests/week2a_a2_planned_manifest.csv"
FIXTURE = REPO / "results/week3_engineering_qualification/f5_tts_v1_base/smoke/engineering_smoke_16k.wav"
FIXTURE_META = REPO / "results/week3_engineering_qualification/f5_tts_v1_base/qualification.json"
CONFIG = REPO / "configs/week3_stage_a_f5.yaml"
AUTHORIZATION = REPO / FUTURE_AUTH_REL

def load_frozen_config() -> dict[str, object]:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if config.get("protocol") != "WEEK3_STAGE_A_F5" or config.get("scientific_execution_enabled") is not False:
        raise RuntimeError("Week3 config is not the frozen fail-closed config")
    if int(config.get("planned_cases", 0)) != 23 or int(config.get("generation_seed_base", 0)) != BASE_SEED:
        raise RuntimeError("frozen population or seed policy mismatch")
    f5 = config.get("f5", {})
    expected = {"model": "F5TTS_v1_Base", "device": "cpu", "ode_method": "euler",
                "use_ema": True, "target_rms": 0.1, "cross_fade_duration": 0.15,
                "sway_sampling_coef": -1, "cfg_strength": 2, "nfe_step": 32,
                "speed": 1.0, "fix_duration": None, "remove_silence": False}
    if any(f5.get(k) != v for k, v in expected.items()):
        raise RuntimeError("frozen F5 inference settings mismatch")
    return config

def validate_frozen_assets(config: dict[str, object]) -> dict[str, object]:
    f5 = config["f5"]
    assets = {"ckpt": REPO / f5["ckpt_file"], "vocab": REPO / f5["vocab_file"], "vocoder": REPO / f5["vocoder_local_path"]}
    missing = [name for name, path in assets.items() if not path.exists()]
    if missing:
        raise RuntimeError(f"frozen F5 asset missing: {missing}")
    # A vocoder is a directory; its full-tree digest is represented by the
    # qualification manifest and checked as a presence/provenance boundary.
    return {name: str(path) for name, path in assets.items()}

def load_planned() -> list[dict[str, str]]:
    with PLANNED.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: r["paired_case_id"])
    if len(rows) != 23:
        raise RuntimeError(f"planned population must contain 23 rows, got {len(rows)}")
    for index, row in enumerate(rows):
        if row["paired_case_id"] != f"paircase_{index + 1:04d}":
            raise RuntimeError("case order is not the frozen ascending order")
        # The legacy manifest seed is historical metadata. Week3 uses the
        # amended zero-based seed policy and never inherits that field.
    return rows

def engineering_only_report() -> dict[str, object]:
    if not FIXTURE.exists() or not FIXTURE_META.exists():
        raise RuntimeError("frozen engineering-only F5 fixture evidence is missing")
    meta = json.loads(FIXTURE_META.read_text(encoding="utf-8"))
    if not meta.get("smoke", {}).get("engineering_only") or meta.get("scientific_execution"):
        raise RuntimeError("fixture is not explicitly engineering-only")
    return {
        "status": "PASS",
        "engineering_only": True,
        "excluded_from_scientific_population": True,
        "fixture": "AISHELL3_ENGINEERING_ONLY_SSB0005_0001_REF_0014",
        "waveform": str(FIXTURE.relative_to(REPO)),
        "sha256": sha256_file(FIXTURE),
        "scientific_generation": False,
    }

def run_case(*, api, case: dict[str, str], zero_based_index: int, clean_path: Path,
             settings: InferenceSettings, output_root: Path, checkpoint_sha256: str,
             vocab_sha256: str, vocoder_sha256: str, repo_commit: str,
             model_revision: str, repo_source: Path | None = None) -> dict[str, object]:
    """Low-level case execution; authorization is owned by the formal runner."""
    seed = generation_seed(zero_based_index)
    raw, native_sr, _ = infer_once(api, ref_file=Path(case["reference_audio_path"]),
                                   ref_text=case["reference_text_exact"],
                                   gen_text=case["source_text_exact"], seed=seed, settings=settings)
    case_dir = output_root / "cases" / case["paired_case_id"]
    raw_path = case_dir / "raw_native.wav"; standardized_path = case_dir / "waveform_16k.wav"
    write_audio(raw_path, raw, native_sr)
    final_wave, trim, gain, layout, _serialization, _ = construct_replacement(
        clean_path, raw, native_sr,
        start=int(case["clean_source_utterance_start_sample"]),
        end=int(case["clean_source_utterance_end_sample"]), out_path=standardized_path)
    row = build_success_sidecar(case, index=zero_based_index, seed=seed,
        raw_path=raw_path, standardized_path=standardized_path, raw_sr=native_sr,
        raw_wave=raw, final_wave=final_wave, trim=trim, gain=gain, layout=layout,
        attempts=1, repo_commit=repo_commit, model_revision=model_revision,
        checkpoint_sha256=checkpoint_sha256, vocab_sha256=vocab_sha256,
        vocoder_sha256=vocoder_sha256, reference_preprocessing="official_f5_preprocess_ref_audio_text")
    return row

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engineering-only", action="store_true")
    parser.add_argument("--stage-a", action="store_true", help="reserved; never enabled in this handoff")
    args = parser.parse_args()
    if args.stage_a:
        try:
            result = run_formal_generation(REPO)
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    if not args.engineering_only:
        raise SystemExit("select --engineering-only; formal 23-case generation is locked")
    config = load_frozen_config()
    validate_frozen_assets(config)
    load_planned()
    report = engineering_only_report()
    out = REPO / "results/week3_stage_a_f5/engineering_only_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
