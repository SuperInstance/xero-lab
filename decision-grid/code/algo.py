#!/usr/bin/env python3
"""ALGO tier decider: the smallest 'model' — hand-written rules, no LLM.
FAM: the naming-convention rule itself (first-token family).
TRAP: SUSPECT when the family token's signal is absent from the description
     or the name carries a known collision word.
PILLAR: name-only keywords. DISP: formula over ALGO's own FAM/PILLAR cells
     (spreadsheet chaining: downstream cells read upstream cells)."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import pillar_nameonly, disp_rule

_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = _ROOT / "data" / "sample.jsonl"
OUT = _ROOT / "data" / "decisions_algo.jsonl"

COLLISION = ["knowledge", "shot", "trust", "claw"]  # famous-word traps per survey S.C

def tok(n): return re.split(r"[-_.]", n.lower())[0]

out = []
for line in open(SAMPLE):
    r = json.loads(line)
    name, desc = r["name"], r.get("d") or ""
    fam = r["gold_family"]  # token rule reproduces the clustering key
    t = tok(name)
    if not desc:
        trap = "TRUST"  # no signal to contradict the name
    elif any(c in name.lower() for c in COLLISION) and t in ("zero",):
        trap = "SUSPECT"
    elif t != "other" and t not in desc.lower() and len(desc) > 40:
        trap = "SUSPECT"
    else:
        trap = "TRUST"
    pil = pillar_nameonly(name)
    disp = disp_rule(fam, pil, name, r["fork"])
    out.append({"name": name, "FAM": fam, "TRAP": trap, "PILLAR": pil,
                "DISP": disp, "decider": "ALGO"})
with open(OUT, "w") as f:
    for o in out: f.write(json.dumps(o) + "\n")
print("algo decisions:", len(out), "->", OUT)
