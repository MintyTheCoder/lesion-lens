import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.pipeline import run_pipeline
from backend.app.services import gemini

REPO_ROOT = Path(__file__).resolve().parents[1]
test_dir = REPO_ROOT / "data/processed/ms3seg_dataset/test"
candidates = sorted(test_dir.glob("*.png"))

MIN_CONFIDENCE = 0.55

best = None
for p in candidates:
    b = p.read_bytes()
    result = run_pipeline(b)
    n = len(result.lesions)
    if 3 <= n <= 5 and all(l.confidence >= MIN_CONFIDENCE for l in result.lesions):
        patterns = {l.pattern for l in result.lesions}
        mixed = len(patterns) > 1
        confidences = [round(l.confidence, 2) for l in result.lesions]
        print(f"candidate: {p.name} — {n} lesions, mixed={mixed}, confidences={confidences}")
        # prefer mixed, then prefer closer to 4
        score = (mixed, -abs(n - 4))
        if best is None or score > best[0]:
            best = (score, p, b, result)

if best is None:
    print("No slice with exactly 4 lesions found.")
else:
    _, p, b, result = best
    print(f"\nPICKED: {p} — 4 lesions")
    result.summary = gemini.summarize(result)
    (REPO_ROOT / "frontend/public/plate/hero-slice.png").write_bytes(b)
    (REPO_ROOT / "frontend/src/mocks/hero.json").write_text(result.model_dump_json(indent=2))
    print("Overwrote hero-slice.png and hero.json.")