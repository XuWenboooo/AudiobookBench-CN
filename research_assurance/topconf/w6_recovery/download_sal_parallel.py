from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
from download_official import download

ROOT = Path(__file__).resolve().parent / "artifacts"
REV = "d9ab313d86a8b00a6345419721389d8b4eabe992"
ITEMS = [
    ("SAL_W2V2.ckpt", 3357802496),
    ("SAL_WavLM.ckpt", 4037013806),
]

def one(item):
    name, size = item
    result = download(
        f"https://huggingface.co/MaoYC/SAL/resolve/{REV}/{name}",
        ROOT / name,
        size,
    )
    (ROOT / f"{name}.manifest.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result

if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(one, item) for item in ITEMS]
        for f in as_completed(futures):
            print(json.dumps(f.result()), flush=True)
