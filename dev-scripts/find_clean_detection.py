import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.pipeline import run_pipeline
from backend.app.services.inference import save_to_demo_cache

REPO_ROOT = Path(__file__).resolve().parents[1]
test_dir = REPO_ROOT / "data/processed/ms3seg_dataset/test"
candidates = sorted(test_dir.glob("*.png")) + sorted(test_dir.glob("*.jpg"))

print(f"Found {len(candidates)} candidate files in {test_dir}")

best = None  # (p, b, result, atypical_count)
match = None

for p in candidates:
    b = p.read_bytes()
    result = run_pipeline(b)
    if not result.lesions:
        continue
    patterns = [l.pattern for l in result.lesions]
    atypical_count = patterns.count("atypical")
    print(f"{p.name}: {len(result.lesions)} lesions, {atypical_count} atypical")
    if atypical_count == 0:
        match = (p, b, result)
        break
    if best is None or atypical_count < best[3]:
        best = (p, b, result, atypical_count)

if match:
    p, b, result = match
    print(f"MATCH: {p} — {len(result.lesions)} lesions, all ms_typical")
    save_to_demo_cache(b, result)
    (REPO_ROOT / "frontend/public/samples/clean-detection.png").write_bytes(b)
    print("Cached and copied.")
elif best:
    p, b, result, ac = best
    print(f"No perfect match. Closest: {p} with {ac} atypical lesion(s) out of {len(result.lesions)}.")
else:
    print("Zero files produced any lesion detections at all — check confidence threshold or the folder path/extension.")