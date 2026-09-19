import json
import random
import shutil
from pathlib import Path

for name in ["ms3seg_dataset", "mslesseg_dataset"]:
    src = Path(f"data/processed/{name}/test")
    dst = Path(f"data/processed/{name}/test_subset")
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    coco = json.loads((src / "_annotations.coco.json").read_text())
    sample = random.sample(coco["images"], min(10, len(coco["images"])))
    keep_ids = {img["id"] for img in sample}

    coco["images"] = [i for i in coco["images"] if i["id"] in keep_ids]
    coco["annotations"] = [a for a in coco["annotations"] if a["image_id"] in keep_ids]

    for img in coco["images"]:
        shutil.copy(src / img["file_name"], dst / img["file_name"])

    (dst / "_annotations.coco.json").write_text(json.dumps(coco))
    n = len(coco["images"])
    print(f"{name}: wrote {n} images to {dst}")