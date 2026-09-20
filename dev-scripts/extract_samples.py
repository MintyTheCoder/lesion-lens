import base64, json
from pathlib import Path

cache_dir = Path("backend/app/fixtures/demo_cache")
out_dir = Path("frontend/public/samples")
out_dir.mkdir(exist_ok=True)

for f in cache_dir.glob("*.json"):
    data = json.loads(f.read_text())
    data_url = data["image"]["data_url"]
    header, b64 = data_url.split(",", 1)
    raw = base64.b64decode(b64)
    out_path = out_dir / f"{f.stem}.png"
    out_path.write_bytes(raw)
    print(f.stem, "->", out_path, len(raw), "bytes")