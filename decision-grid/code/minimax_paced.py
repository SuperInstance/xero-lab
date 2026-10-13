#!/usr/bin/env python3
"""PACED re-run of the SMALL tier (MiniMax-Text-01) — closes the first
run's 429 deficit. Doctrine from RESULTS.md finding #7: batch pacing is
a gate too. Rules enforced here:
  * ONE call in flight at a time (concurrency 1 <= 2), sequential batches.
  * 2s pacing sleep between successful batches.
  * HTTP 429 -> exponential backoff (20s, 45s, 90s); if a batch still
    429s after the ladder, the WHOLE run halts (exit 3) and reports.
  * Other errors / unparseable output -> one retry after 5s, then the
    batch is marked MISSING; >=3 such batches also halts the run.
  * Every invocation is logged to data/minimax_calls_rerun.log.
Resumable: a repo counts as done only with a non-MISSING value in
small_<CELL>.jsonl. After each cell, the file is normalized to exactly
one line per repo (sample order; subsample order for the REF cells).

Usage: minimax_paced.py FAM TRAP PILLAR DISP
       minimax_paced.py SUBSTANCE COLLISION VAGUE   (119-repo REF subsample)
Prompts for the original four cells are copied verbatim from
minimax_run.py so the re-run is measured against identical standards.
"""
import json, re, subprocess, sys, os, time, datetime

CHAT = "/home/hatch/workspace/skills/minimax/bin/chat.py"
DATA = "/home/hatch/workspace/xero-decision-grid/data"
BATCH = 16
PACE_S = 2.0
BACKOFF_429 = [20, 45, 90]
CALLLOG = open(f"{DATA}/minimax_calls_rerun.log", "a")
SUMMARY_PATH = f"{DATA}/rerun_summary.json"

def ts():
    return datetime.datetime.now().isoformat(timespec="seconds")

def log_call(cell, batch_no, attempt, result):
    CALLLOG.write(f"{ts()} cell={cell} batch={batch_no} attempt={attempt} result={result}\n")
    CALLLOG.flush()

sample = [json.loads(l) for l in open(f"{DATA}/sample.jsonl")]
big_names = [json.loads(l)["name"] for l in open(f"{DATA}/big_labels.jsonl")]
by_name = {r["name"]: r for r in sample}
src = [json.loads(l) for l in open("/home/hatch/workspace/xero-research/superinstance/.scratch/all-repos.jsonl")]
def tok(n): return re.split(r"[-_.]", n.lower())[0]
from collections import Counter
cnt = Counter(tok(r["name"]) for r in src)
FAMS = sorted(t for t, n in cnt.items() if n >= 12)

def load_done(cell):
    """name -> value for non-MISSING entries (later lines win)."""
    p = f"{DATA}/small_{cell}.jsonl"
    d = {}
    if os.path.exists(p):
        for l in open(p):
            o = json.loads(l)
            if o["v"] != "MISSING":
                d[o["name"]] = o["v"]
    return d

def normalize(cell, universe):
    d = load_done(cell)
    p = f"{DATA}/small_{cell}.jsonl"
    with open(p, "w") as f:
        for name in universe:
            f.write(json.dumps({"name": name, "v": d.get(name, "MISSING")}) + "\n")
    return d

SYS = {
"FAM": "You classify GitHub repos into survey families. Reply ONLY with a JSON array, one object per repo: {\"name\": <name>, \"v\": <family>}. No prose.",
"TRAP": "You audit repo names. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"TRUST\" or \"SUSPECT\"}. No prose.",
"PILLAR": "You tag repos with zero-program pillars. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": [<pillar>, ...]} (empty list if none). No prose.",
"DISP": "You assign survey dispositions. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"DEEP\" or \"COLLAPSE\" or \"TAIL\"}. No prose.",
"SUBSTANCE": "You audit repos for substance. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"STUB\" or \"SUBSTANTIVE\"}. No prose.",
"COLLISION": "You audit repo names for collisions with famous things. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"YES\" or \"NO\"}. No prose.",
"VAGUE": "You audit repo names for vagueness. Reply ONLY with a JSON array: {\"name\": <name>, \"v\": \"YES\" or \"NO\"}. No prose.",
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
    if cell == "SUBSTANCE":
        return ("Judge each repo's substance from its name and description. "
                "STUB = placeholder, empty shell, scaffold or test repo, or a "
                "content-free experiment: little or no real implementation or ideas. "
                "SUBSTANTIVE = carries real implementation, a real pattern, or "
                f"substantive content a survey would learn from.\n{body}")
    if cell == "COLLISION":
        return ("Judge ONLY the repo's name (use the description just to know what the "
                "repo actually is). COLLISION (YES) = the name is, or contains, a famous "
                "word, product, project, scientific field, brand, or concept from OUTSIDE "
                "this program, such that a reader would first think of that famous thing "
                "(e.g. a name built on a well-known cryptography field, a famous software "
                "product, or a famous fictional concept). NO = the name is original or "
                f"generic program vocabulary with no famous external referent.\n{body}")
    if cell == "VAGUE":
        return ("Judge ONLY the repo's name, ignoring what the description says it does. "
                "VAGUE (YES) = from the name alone you could not tell what the repo "
                "actually does: the words are generic, abstract, or poetic, with no "
                "concrete referent for the content. NO = the name concretely signals "
                f"its content (a technology, domain, artifact, or function is named).\n{body}")
    raise ValueError(cell)

def parse_arr(txt):
    m = re.search(r"\[.*\]", txt, re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

class Halt(Exception):
    pass

stats = {"calls": 0, "http429": 0, "retries": 0, "error_batches": 0, "cells": {}}

def call_batch(cell, batch_no, system, prompt, names):
    """One batch with the pacing/backoff doctrine. Returns parsed array
    or None (batch unrecoverable but not a 429 halt). Raises Halt."""
    attempt = 0
    backoff_i = 0
    retried_other = False
    while True:
        attempt += 1
        stats["calls"] += 1
        if attempt > 1: stats["retries"] += 1
        r = subprocess.run(["python3", CHAT, prompt, "--system", system,
                            "--max-tokens", "1400"],
                           capture_output=True, text=True, timeout=300)
        err = (r.stderr or "").strip()
        if r.returncode != 0 and "429" in err:
            stats["http429"] += 1
            log_call(cell, batch_no, attempt, "http429")
            print(f"  !! 429 on {cell} batch {batch_no} (attempt {attempt})", flush=True)
            if backoff_i < len(BACKOFF_429):
                wait = BACKOFF_429[backoff_i]; backoff_i += 1
                print(f"     backing off {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise Halt(f"HTTP 429 persisted after backoff ladder on {cell} batch {batch_no}")
        if r.returncode != 0:
            log_call(cell, batch_no, attempt, f"error: {err[:120]}")
            if not retried_other:
                retried_other = True
                time.sleep(5)
                continue
            return None
        arr = parse_arr(r.stdout)
        if arr is None:
            log_call(cell, batch_no, attempt, "parsefail")
            if not retried_other:
                retried_other = True
                time.sleep(5)
                continue
            return None
        got = sum(1 for o in arr if isinstance(o, dict) and o.get("name") in names)
        log_call(cell, batch_no, attempt, f"ok {got}/{len(names)}")
        return arr

def run_cell(cell):
    if cell in ("SUBSTANCE", "COLLISION", "VAGUE"):
        universe = big_names
    else:
        universe = [r["name"] for r in sample]
    done = load_done(cell)
    todo = [by_name[n] for n in universe if n not in done]
    print(f"{cell}: {len(done)} done, {len(todo)} to go", flush=True)
    aux = {}
    if cell == "DISP":
        aux = {"FAM": load_done("FAM"), "PILLAR": load_done("PILLAR")}
    out = open(f"{DATA}/small_{cell}.jsonl", "a")
    nb = (len(todo) + BATCH - 1) // BATCH
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        bno = i // BATCH + 1
        names = [r["name"] for r in batch]
        arr = call_batch(cell, bno, SYS[cell], prompt_for(cell, batch, aux), names)
        got = {}
        if arr:
            for o in arr:
                if isinstance(o, dict) and o.get("name") in names:
                    got[o["name"]] = o.get("v")
        if arr is None:
            stats["error_batches"] += 1
            print(f"  batch {bno}/{nb}: FAILED (marked MISSING)", flush=True)
            if stats["error_batches"] >= 3:
                out.close()
                raise Halt(f"3 failed batches — systemic problem, last on {cell} batch {bno}")
        for r in batch:
            v = got.get(r["name"], "MISSING")
            out.write(json.dumps({"name": r["name"], "v": v}) + "\n")
        out.flush()
        print(f"  batch {bno}/{nb}: {len(got)}/{len(batch)} parsed", flush=True)
        if i + BATCH < len(todo):
            time.sleep(PACE_S)
    out.close()
    d = normalize(cell, universe)
    stats["cells"][cell] = {"answered": len(d), "of": len(universe)}
    print(f"{cell} complete: {len(d)}/{len(universe)} answered", flush=True)
    json.dump(stats, open(SUMMARY_PATH, "w"), indent=1)

def main():
    cells = sys.argv[1:]
    if not cells:
        print("usage: minimax_paced.py CELL [CELL...]"); sys.exit(2)
    try:
        for cell in cells:
            run_cell(cell)
    except Halt as h:
        json.dump(stats, open(SUMMARY_PATH, "w"), indent=1)
        print(f"HALT: {h}", flush=True)
        print("SUMMARY:", json.dumps(stats), flush=True)
        sys.exit(3)
    print("ALL CELLS DONE. SUMMARY:", json.dumps(stats), flush=True)

main()
