from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from audiobookbench.security.week3_evaluation_repro import run_formal_repair


if __name__ == "__main__":
    print(json.dumps(run_formal_repair(Path(__file__).resolve().parents[2]), ensure_ascii=False, indent=2))
