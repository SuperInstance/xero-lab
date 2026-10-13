#!/usr/bin/env python3
"""SMALL tier decider: MiniMax-Text-01 via the minimax skill CLI.
Usage: minimax_run.py FAM|TRAP|PILLAR|DISP
Batches of 16 repos per call; strict JSON out; resumable (skips batches
already present in the per-cell output file). DISP reads this decider's
own FAM/PILLAR outputs (grid chaining)."""
import json, re, subprocess, sys, os
from collections import Counter
from pathlib import Path

# The MiniMax chat CLI is an external tool (a script called as
# `chat.py PROMPT --system SYS --max-tokens N`, printing the reply).
# It is only invoked for cells not already answered in data/.
CHAT = os.environ.get("MINIMAX_CHAT")
DATA = Path(__file__).resolve().parents[1] / "data"
CELL = sys.argv[1]
BATCH = 16

sample = [json.loads(l) for l in open(f"{DATA}/sample.jsonl")]
def tok(n): return re.split(r"[-_.]", n.lower())[0]
def _fams():
    """Families with >=12 members account-wide: counted from the full
    enumeration when XERO_ENUMERATION points at it, else the committed
    sample's GOLD families (the same set for the sampled repos)."""
    enum = os.environ.get("XERO_ENUMERATION")
    if enum:
        src = [json.loads(l) for l in open(enum)]
        cnt = Counter(tok(r["name"]) for r in src)
        return sorted(t for t, n in cnt.items() if n >= 12)
    return sorted({r["gold_family"] for r in sample if r["gold_family"] != "OTHER"})
FAMS = _fams()

def load_cell(cell):
    p = f"{DATA}/small_{cell}.jsonl"
    d = {}
    if os.path.exists(p):
        for l in open(p):
            o = json.loads(l); d[o["name"]] = o["v"]
    return d

def call(system, prompt, maxtok=1400):
    r = subprocess.run(["python3", CHAT, prompt, "--system", system,
                        "--max-tokens", str(maxtok)],
                       capture_output=True, text=True, timeout=300)
    return r.stdout

def parse_arr(txt):
    m = re.search(r"\[.*\]", txt, re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

SYS = {
"FAM": "You classify GitHub repos into survey families. Reply ONLY with a JSON array, one object per repo: {\"name\": <name>, \"v\": <family>}. No prose.",
"TRAP": "You audit repo names. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"TRUST\" or \"SUSPECT\"}. No prose.",
"PILLAR": "You tag repos with zero-program pillars. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": [<pillar>, ...]} (empty list if none). No prose.",
"DISP": "You assign survey dispositions. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"DEEP\" or \"COLLAPSE\" or \"TAIL\"}. No prose.",
}

def brief(r):
    d = (r.get("d") or "(no description)")[:220]
    return f"- name: {r['name']} | lang: {r.get('l') or '-'} | fork: {r['fork']} | desc: {d}"

def prompt_for(cell, batch, aux):
    lines = [brief(r) for r in batch]
    body = "\n".join(lines)
    if cell == "FAM":
        return (f"Families: {', '.join(FAMS)}, OTHER.\n"
                f"Assign each repo its family from its name and description. "
                f"Use OTHER if it belongs to no listed family.\n{body}")
    if cell == "TRAP":
        return ("Decide whether each repo's NAME is a reliable guide to its content, "
                "judging from the description. TRUST = name honestly signals content. "
                "SUSPECT = name is misleading, a famous-word collision, or promises "
                f"something the description does not support.\n{body}")
    if cell == "PILLAR":
        return ("Pillars: agent-as-files (agent is a set of files/git repo), "
                "two-logs (state log + contract ledger, append-only records), "
                "gates-deadbands (gates, thresholds, alarms, watches), "
                "memory-grid (memory as addressed files/rooms/tiles/index), "
                "interface-data-logic (chat interfaces, bridges, rendering, protocols), "
                "deployment (hardware, edge, microcontrollers, workers), "
                "pyramid-orchestration (fleets, multi-agent coordination, tiered models), "
                "walkthroughs-skills (skills, curricula, learned procedures), "
                "calculator-maker (building tools/compilers that build other things). "
                f"Tag each repo with up to 2 pillars it genuinely touches, else empty list.\n{body}")
    if cell == "DISP":
        extra = []
        for r in batch:
            extra.append(f"  grid cells for {r['name']}: FAM={aux['FAM'].get(r['name'])} PILLAR={aux['PILLAR'].get(r['name'])}")
        return ("Dispositions: DEEP = deserves individual deep reading in a survey of the "
                "zero-agent program; COLLAPSE = adequately represented by its family line; "
                "TAIL = one-off, note in aggregate only. Use the repo data AND the grid's "
                f"own FAM/PILLAR cells.\n{body}\n" + "\n".join(extra))

def main():
    aux = {}
    if CELL == "DISP":
        aux = {"FAM": load_cell("FAM"), "PILLAR": load_cell("PILLAR")}
    done = load_cell(CELL)
    todo = [r for r in sample if r["name"] not in done]
    print(f"{CELL}: {len(done)} done, {len(todo)} to go", flush=True)
    if todo and not (CHAT and os.path.exists(CHAT)):
        sys.exit(f"error: {len(todo)} repos still need MiniMax calls but no "
                 "MiniMax chat CLI was found. Point MINIMAX_CHAT at one:\n"
                 "  MINIMAX_CHAT=/path/to/chat.py python3 code/minimax_run.py "
                 f"{CELL}\n(The committed data/small_*.jsonl already cover "
                 "the sample; scoring and finalize run without it.)")
    out = open(f"{DATA}/small_{CELL}.jsonl", "a")
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        names = [r["name"] for r in batch]
        arr = None
        for attempt in range(2):
            txt = call(SYS[CELL], prompt_for(CELL, batch, aux))
            arr = parse_arr(txt)
            if arr: break
        got = {}
        if arr:
            for o in arr:
                if isinstance(o, dict) and o.get("name") in names:
                    got[o["name"]] = o.get("v")
        for r in batch:
            v = got.get(r["name"], "MISSING")
            out.write(json.dumps({"name": r["name"], "v": v}) + "\n")
        out.flush()
        print(f"  batch {i//BATCH+1}: {len(got)}/{len(batch)} parsed", flush=True)
    out.close()
    print(f"{CELL} complete")

main()
