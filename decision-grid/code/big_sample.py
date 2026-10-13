#!/usr/bin/env python3
import json, random
from pathlib import Path
random.seed(777)
DATA = Path(__file__).resolve().parents[1] / "data"
sample = [json.loads(l) for l in open(f"{DATA}/sample.jsonl")]
spot = [r for r in sample if r["stratum"] == "spotlight"]
rest = [r for r in sample if r["stratum"] != "spotlight"]
by = {}
for r in rest: by.setdefault(r["stratum"], []).append(r)
quota = {"bigfam": 44, "tail": 36, "nodesc": 14, "fork": 14}
picked = list(spot)
for k, n in quota.items():
    picked += random.sample(by[k], n)
print("big subsample:", len(picked), "| spotlight:", len(spot))
with open(f"{DATA}/big_sample.jsonl", "w") as f:
    for r in picked: f.write(json.dumps(r) + "\n")
