from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from audiobookbench.week5.exp2 import run
if __name__=="__main__":
    import json
    print(json.dumps(run(Path(__file__).resolve().parents[2]),ensure_ascii=False,indent=2))
