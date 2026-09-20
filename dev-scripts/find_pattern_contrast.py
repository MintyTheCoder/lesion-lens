import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.pipeline import run_pipeline
from backend.app.services import gemini
from backend.app.services.inference import save_to_demo_cache

REPO_ROOT = Path(__file__).resolve().parents[1]
test_dir = REPO_ROOT / "data/processed/ms3seg_dataset/test"
candidates = sorted(test_dir.glob("*.png")) + sorted(test_dir.glob("*.jpg"))

print(f"Found {len(candidates)} candidate files in {test_dir}")

best = None  # (p, b, result, atypical_count) among mixed slices
match = None

for p in candidates:
    b = p.read_bytes()
    result = run_pipeline(b)
    if not result.lesions:
        continue
    patterns = [l.pattern for l in result.lesions]
    typical_count = patterns.count("ms_typical")
    atypical_count = patterns.count("atypical")
    print(f"{p.name}: {len(result.lesions)} lesions, {typical_count} typical / {atypical_count} atypical")
    if typical_count >= 1 and atypical_count >= 1:
        # prefer a denser, more convincing mix
        if best is None or len(result.lesions) > len(best[2].lesions):
            best = (p, b, result, atypical_count)

if best:
    p, b, result, ac = best
    print(f"MATCH: {p} — {len(result.lesions)} lesions, mixed pattern")
    result.summary = gemini.summarize(result)
    save_to_demo_cache(b, result)
    (REPO_ROOT / "frontend/public/samples/pattern-contrast.png").write_bytes(b)
    print("Cached (with summary) and copied — overwrote pattern-contrast.png.")
else:
    print("No slice with both ms_typical and atypical lesions found.")