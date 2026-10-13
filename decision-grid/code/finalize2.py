#!/usr/bin/env python3
"""Re-run finalize: rebuild the sheet with the COMPLETED SMALL tier and
the closed staircases, and recompute economics.
Staffing policy (run-1 policy, updated by re-run measurements + Jev):
  FAM    ALGO token-family / SMALL tail-OTHER / BIG fused-name watch
         (Jev rerun: zero 0.44 on tail staffing — standing caution, logged)
  TRAP   BIG verdicts on the labeled subsample; WATCH flags elsewhere
         (Jev choice: keep_big_watch 0.66)
  PILLAR ALGO everywhere — staffing CONFIRMED by the re-run (ALGO fidelity
         to REF 65.6% exact vs SMALL 33.6%); SMALL tags are candidates
         (Jev pos 0.77)
  DISP   formula over ALGO cells; pillar-bearing tail/fork escalate
         (SUBSTANCE cell not adopted — Jev pos 0.74)
Units (same proxy as run 1): ALGO=0.001, SMALL=1, BIG=25, Jev=2/gated cell.
Also regenerates data/decisions_small.jsonl from the completed cell files."""
import json, sys, csv, re, os
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import pillar_silver, disp_rule

D = Path(__file__).resolve().parents[1] / "data"
sample = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/sample.jsonl")}
algo = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/decisions_algo.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/big_labels.jsonl")}
jevres = {(r["cell"], r["name"]): r for r in json.load(open(f"{D}/jev_instance_results.json"))}
def load_small(cell):
    d = {}
    try:
        for l in open(f"{D}/small_{cell}.jsonl"):
            o = json.loads(l)
            if o["v"] != "MISSING": d[o["name"]] = o["v"]
    except FileNotFoundError: pass
    return d
small = {c: load_small(c) for c in ["FAM", "TRAP", "PILLAR", "DISP"]}
def _bigtokens():
    """First-token families with >=12 members account-wide. Counted from
    the full enumeration when XERO_ENUMERATION points at it; otherwise
    the committed sample's GOLD families — the same set for the repos
    this sheet covers (their gold_family was computed from that count)."""
    enum = os.environ.get("XERO_ENUMERATION")
    if enum:
        src = [json.loads(l) for l in open(enum)]
        cnt = Counter(re.split(r"[-_.]", r["name"].lower())[0] for r in src)
        return {t for t, n in cnt.items() if n >= 12}
    return {r["gold_family"] for r in sample.values() if r["gold_family"] != "OTHER"}
BIGTOKENS = _bigtokens()
def fused(name):
    n = name.lower()
    if re.split(r"[-_.]", n)[0] in BIGTOKENS: return False
    return any(n.startswith(t) and len(n) > len(t) for t in BIGTOKENS)

def fmt(v):
    if isinstance(v, list): return "+".join(v) if v else "NONE"
    return str(v)

# ---- regenerate the merged SMALL decisions file (full coverage now) ----
with open(f"{D}/decisions_small.jsonl", "w") as f:
    for name in sample:
        f.write(json.dumps({"name": name,
                            "FAM": small["FAM"].get(name), "TRAP": small["TRAP"].get(name),
                            "PILLAR": small["PILLAR"].get(name), "DISP": small["DISP"].get(name),
                            "decider": "SMALL(minimax-text-01); paced re-run 2026-10-13 — full coverage, zero 429s"}) + "\n")

rows = []
for name, r in sample.items():
    silv = pillar_silver(name, r.get("d"))
    silv_disp = disp_rule(r["gold_family"], silv, name, r["fork"])
    for cell in ["FAM", "TRAP", "PILLAR", "DISP"]:
        if cell == "FAM": std_name, std_val = "GOLD", r["gold_family"]
        elif cell == "PILLAR": std_name, std_val = "SILVER", silv
        elif cell == "DISP": std_name, std_val = "SILVER", silv_disp
        else: std_name, std_val = ("REF", big[name]["TRAP"]) if name in big else ("none", None)
        algo_v = algo[name][cell]
        small_v = small[cell].get(name, "MISSING")
        big_v = big[name][cell] if name in big else ""
        gate = jevres.get((cell, name))
        gate_s = f"{gate['band']} p={gate['p']}" if gate else ""
        # staircase staffing (closed by the re-run)
        if cell == "FAM":
            if fused(name) and name in big: tier, staffed = "BIG(watch: fused name)", big[name]["FAM"]
            elif r["gold_family"] != "OTHER": tier, staffed = "ALGO", algo_v
            elif isinstance(small_v, str) and small_v != "MISSING": tier, staffed = "SMALL", small_v
            else: tier, staffed = "ALGO(fallback)", algo_v
        elif cell == "TRAP":
            if name in big: tier, staffed = "BIG", big[name]["TRAP"]
            else: tier, staffed = "WATCH(algo flag only)", algo_v
        elif cell == "PILLAR":
            tier, staffed = "ALGO(confirmed)", algo_v
        else:
            esc = bool(silv) and r["stratum"] in ("tail", "fork")
            if esc and name in big: tier, staffed = "BIG(escalated)", big[name]["DISP"]
            elif esc: tier, staffed = "FORMULA+flag", algo_v
            else: tier, staffed = "FORMULA(algo cells)", algo_v
        if gate:  # run-1 instance gates still override where they sat
            staffed = gate["ref"] if gate["band"] != "pos" else gate["small"]
            tier = f"JEV-GATED({tier})"
        correct = ""
        if std_val is not None:
            correct = (fmt(staffed) == fmt(std_val)) if cell in ("PILLAR",) else (staffed == std_val)
        rows.append({"repo": name, "stratum": r["stratum"], "cell": cell,
                     "standard": std_name, "standard_value": fmt(std_val) if std_val is not None else "",
                     "algo": fmt(algo_v), "small": fmt(small_v), "big": fmt(big_v) if big_v != "" else "",
                     "jev_gate": gate_s, "staffed_tier": tier,
                     "staffed_decision": fmt(staffed), "staffed_correct": correct})
with open(f"{D}/sheet.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(f"{D}/sheet.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("sheet rows:", len(rows))

U = {"ALGO": 0.001, "SMALL": 1, "BIG": 25, "JEV": 2}
n = len(sample)
all_big = 4 * n * U["BIG"]
staffed = Counter(); cost = 0.0
for r in rows:
    t = r["staffed_tier"]
    base = ("BIG" if t.startswith("BIG") else "SMALL" if t.startswith("SMALL")
            else "JEV" if t.startswith("JEV-GATED") else "ALGO")
    staffed[base] += 1
    cost += U["BIG"] if t.startswith("BIG") else U["SMALL"] if t.startswith("SMALL") else U["ALGO"]
    if r["jev_gate"]: cost += U["JEV"]
print("staffed cells by tier:", dict(staffed))
print(f"all-BIG cost for 395x4 grid: {all_big:.0f} units | staffed grid: {cost:.1f} units "
      f"({100*cost/all_big:.1f}% of all-BIG)")
for cell in ["FAM", "TRAP", "PILLAR", "DISP"]:
    cr = [r for r in rows if r["cell"] == cell and r["staffed_correct"] != ""]
    ok = sum(1 for r in cr if r["staffed_correct"] is True)
    print(f"staffed {cell}: correct {ok}/{len(cr)} vs its standard")
json.dump({"all_big": all_big, "staffed_cost": cost, "staffed_by_tier": dict(staffed),
           "note": "re-run (paced) finalize2.py, 2026-10-13"},
          open(f"{D}/economics.json", "w"), indent=1)
