#!/usr/bin/env python3
"""Stratified sample of SuperInstance repos for the decision-grid PoC.
GOLD family = survey's programmatic clustering: first name-token family
(split on [-_.]) if that family has >=12 members across the account, else OTHER.
"""
import json, re, random
from collections import Counter, defaultdict

SRC = "/home/hatch/workspace/xero-research/superinstance/.scratch/all-repos.jsonl"
OUT = "/home/hatch/workspace/xero-decision-grid/data/sample.jsonl"
random.seed(20261013)

rows = [json.loads(l) for l in open(SRC) if l.strip()]
def tok(n): return re.split(r"[-_.]", n.lower())[0]
cnt = Counter(tok(r["name"]) for r in rows)
BIG = {t for t, n in cnt.items() if n >= 12}
def gold(r): 
    t = tok(r["name"]); return t if t in BIG else "OTHER"

for r in rows:
    r["gold_family"] = gold(r)
    r["stratum"] = None

pools = defaultdict(list)
for r in rows:
    if r["fork"]:
        pools["fork"].append(r)
    elif not r.get("d"):
        pools["nodesc"].append(r)
    elif r["gold_family"] != "OTHER":
        pools["bigfam"].append(r)
    else:
        pools["tail"].append(r)

want = {"bigfam": 160, "tail": 128, "nodesc": 48, "fork": 48}
sample = []
for k, n in want.items():
    picked = random.sample(pools[k], n)
    for r in picked: r["stratum"] = k
    sample += picked
    print(k, "pool", len(pools[k]), "-> picked", n)

SPOTLIGHT = ["zero-knowledge","zero-poc","git.pp-ng","quilt-matrix","cellforge",
             "fleet-triage","xero","xero-lab","question-tree","jev-semantic",
             "constraint-theory-core","exocortex-core"]
byname = {r["name"]: r for r in rows}
have = {r["name"] for r in sample}
for name in SPOTLIGHT:
    if name in byname and name not in have:
        r = dict(byname[name]); r["stratum"] = "spotlight"
        sample.append(r)
print("total sample:", len(sample))

FIELDS = ["name","d","l","fork","gold_family","stratum"]
with open(OUT, "w") as f:
    for r in sample:
        f.write(json.dumps({k: r.get(k) for k in FIELDS}) + "\n")
print("wrote", OUT)
