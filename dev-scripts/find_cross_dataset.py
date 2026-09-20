import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.pipeline import run_pipeline
from backend.app.services.inference import save_to_demo_cache

REPO_ROOT = Path(__file__).resolve().parents[1]
test_dir = REPO_ROOT / "data/processed/mslesseg_dataset/test"
candidates = sorted(test_dir.glob("*.png")) + sorted(test_dir.glob("*.jpg"))

print(f"Found {len(candidates)} candidate files in {test_dir}")

match = None
for p in candidates:
    b = p.read_bytes()
    result = run_pipeline(b)
    print(f"{p.name}: {len(result.lesions)} lesions")
    if len(result.lesions) >= 1:
        match = (p, b, result)
        break

if match:
    p, b, result = match
    print(f"MATCH: {p} — {len(result.lesions)} lesions")
    save_to_demo_cache(b, result)
    (REPO_ROOT / "frontend/public/samples/cross-dataset.png").write_bytes(b)
    print("Cached and copied.")
else:
    print("Zero detections across every file — check confidence threshold, preprocessing, or that this folder is actually skull-stripped/preprocessed the model expects.")