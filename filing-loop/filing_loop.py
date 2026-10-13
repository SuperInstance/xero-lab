#!/usr/bin/env python3
"""
filing_loop.py — chat-to-git filing loop prototype (Xero memory ladder, rung 2)

The design (from the 2026-10-10 zero-agent ramble, notes §12:48):
  - Chat DEPOSITS utterances into a folder (toss).
  - Files REFINE themselves: when the inbox file passes a size gate it
    cascade-splits — first into daily archive files, then (if a single
    day is still too big) into per-topic files inside that day.
  - During idle churn, a topic pass builds topic VIEWS + an index over
    the archive (the "better-than-that filing system").
  - Every action CHECKS IN to git. The git log is the ledger.

Split policy = gates: a size gate (bytes) and a time gate (the date in
each entry's timestamp). Topic assignment here is a deterministic
keyword heuristic — the honest stub where an LLM iteration-box pass
slots in later. Views are regenerated wholesale on each refine, so
refine is idempotent.

Store layout (a git repo):
  inbox/<chat>/current.md            deposits append here
  archive/<chat>/YYYY-MM-DD.md       split level 1: daily files
  archive/<chat>/YYYY-MM-DD/<topic>.md   split level 2: huge days, by topic
  topics/<chat>/<topic>.md           refine views (generated, not source)
  topics/<chat>/INDEX.md

Entry format (one utterance):
  ## 2026-10-12T14:03:52-08:00 — telegram
  <text>

Config (env): FILING_SPLIT_BYTES (default 60000 ≈ 20 "pages"),
              FILING_TOPIC_K    (default 8 topics per chat)
Usage:
  filing_loop.py init   <store>
  filing_loop.py deposit <store> <chat> <text> [--ts ISO] [--source NAME]
  filing_loop.py refine <store> [chat]
  filing_loop.py status <store>
"""
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

SPLIT_BYTES = int(os.environ.get("FILING_SPLIT_BYTES", "60000"))
TOPIC_K = int(os.environ.get("FILING_TOPIC_K", "8"))

HEADER_RE = re.compile(r"^## (\S+) — (.*)$")
WORD_RE = re.compile(r"[a-z][a-z0-9\-]{2,}")
STOPWORDS = set(
    "the a an and or of to in on for with is are was were be been it its "
    "this that these those i you he she we they my his her our their me "
    "him us them do does did can could will would should may might not "
    "no yes if then than so as at by from into about over under again "
    "just like get got one two all any out up down off too very".split()
)


# ---------- git ----------

def git(store, *args, check=True):
    return subprocess.run(
        ["git", "-C", store, *args], capture_output=True, text=True, check=check
    )


def git_commit(store, message):
    """Commit whatever changed; return True if a commit was made."""
    if not git(store, "status", "--porcelain").stdout.strip():
        return False
    git(store, "add", "-A")
    git(store, "commit", "-q", "-m", message)
    return True


def init_store(store):
    """Create the store if needed. Returns True if it was created."""
    os.makedirs(store, exist_ok=True)
    if not os.path.isdir(os.path.join(store, ".git")):
        git(store, "init", "-q", "-b", "main")
        git(store, "config", "user.name", "filing-loop")
        git(store, "config", "user.email", "filing-loop@local")
        with open(os.path.join(store, "README.md"), "w") as f:
            f.write("# filing-loop store\n\nChat deposits, filed by the loop. "
                    "The git log is the ledger.\n")
        git_commit(store, "init: filing-loop store")
        return True
    return False


# ---------- entries ----------

def parse_entries(text):
    """Split file text into [(timestamp, source, body), ...]."""
    entries, cur = [], None
    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m:
            if cur:
                entries.append(cur)
            cur = [m.group(1), m.group(2), []]
        elif cur is not None:
            cur[2].append(line)
    if cur:
        entries.append(cur)
    return [(ts, src, "\n".join(body).strip()) for ts, src, body in entries]


def render_entry(ts, source, body):
    return f"## {ts} — {source}\n{body.strip()}\n\n"


def read_entries(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return parse_entries(f.read())


def append_entries(path, entries):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        for ts, src, body in entries:
            f.write(render_entry(ts, src, body))


# ---------- topics (deterministic heuristic stub) ----------

def top_keywords(texts, k):
    counts = Counter()
    for t in texts:
        counts.update(w for w in WORD_RE.findall(t.lower()) if w not in STOPWORDS)
    return [w for w, _ in counts.most_common(k)]


def primary_topic(body, topics):
    words = Counter(w for w in WORD_RE.findall(body.lower()))
    best, best_n = "misc", 0
    for t in topics:
        if words.get(t, 0) > best_n:
            best, best_n = t, words[t]
    return best


# ---------- deposit ----------

def deposit(store, chat, text, ts=None, source="chat"):
    if ts is None:
        ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    cur = os.path.join(store, "inbox", chat, "current.md")
    append_entries(cur, [(ts, source, text)])
    git_commit(store, f"deposit: {chat} {ts}")
    cascade_split(store, chat)


# ---------- cascade split ----------

def cascade_split(store, chat):
    """Level 1: inbox file over the size gate -> daily archive files.
    Level 2: a daily file still over the gate -> per-topic files in that day."""
    cur = os.path.join(store, "inbox", chat, "current.md")
    if not os.path.exists(cur) or os.path.getsize(cur) <= SPLIT_BYTES:
        return
    entries = read_entries(cur)
    by_day = defaultdict(list)
    for e in entries:
        by_day[e[0][:10]].append(e)
    for day, day_entries in sorted(by_day.items()):
        append_entries(os.path.join(store, "archive", chat, f"{day}.md"), day_entries)
    with open(cur, "w"):
        pass  # inbox drained
    git_commit(store, f"split L1: {chat} -> {len(by_day)} daily file(s)")

    # level 2: any daily file still over the gate splits by topic
    for day in sorted(by_day):
        day_file = os.path.join(store, "archive", chat, f"{day}.md")
        if os.path.getsize(day_file) <= SPLIT_BYTES:
            continue
        day_entries = read_entries(day_file)
        topics = top_keywords([b for _, _, b in day_entries], TOPIC_K)
        by_topic = defaultdict(list)
        for e in day_entries:
            by_topic[primary_topic(e[2], topics)].append(e)
        day_dir = os.path.join(store, "archive", chat, day)
        for topic, t_entries in sorted(by_topic.items()):
            append_entries(os.path.join(day_dir, f"{topic}.md"), t_entries)
        os.remove(day_file)
        git_commit(store, f"split L2: {chat} {day} -> {len(by_topic)} topic file(s)")


# ---------- refine (idle churn): topic views + index ----------

def all_source_entries(store, chat):
    """Entries from inbox + archive (never from generated topic views)."""
    entries = read_entries(os.path.join(store, "inbox", chat, "current.md"))
    arch = os.path.join(store, "archive", chat)
    if os.path.isdir(arch):
        for name in sorted(os.listdir(arch)):
            p = os.path.join(arch, name)
            if os.path.isfile(p) and name.endswith(".md"):
                entries += read_entries(p)
            elif os.path.isdir(p):
                for sub in sorted(os.listdir(p)):
                    if sub.endswith(".md"):
                        entries += read_entries(os.path.join(p, sub))
    return entries


def refine(store, chat):
    """Rebuild topic views for one chat. Returns entries processed."""
    entries = all_source_entries(store, chat)
    if not entries:
        return 0
    topics = top_keywords([b for _, _, b in entries], TOPIC_K)
    tdir = os.path.join(store, "topics", chat)
    os.makedirs(tdir, exist_ok=True)
    index = [f"# topics — {chat}\n",
             f"{len(entries)} entries, {len(topics)} topics. "
             "Generated by refine; regenerate freely.\n"]
    for topic in topics:
        hits = [e for e in entries if topic in WORD_RE.findall(e[2].lower())]
        with open(os.path.join(tdir, f"{topic}.md"), "w") as f:
            f.write(f"# {topic} — {chat}\n\n")
            for ts, src, body in hits:
                f.write(render_entry(ts, src, body))
        index.append(f"- [{topic}]({topic}.md) — {len(hits)} entries")
    with open(os.path.join(tdir, "INDEX.md"), "w") as f:
        f.write("\n".join(index) + "\n")
    git_commit(store, f"refine: {chat} topics ({', '.join(topics)})")
    return len(entries)


# ---------- status ----------

def status(store):
    chats = set()
    for sub in ("inbox", "archive", "topics"):
        d = os.path.join(store, sub)
        if os.path.isdir(d):
            chats.update(os.listdir(d))
    for chat in sorted(chats):
        n = len(all_source_entries(store, chat))
        arch = os.path.join(store, "archive", chat)
        nfiles = 0
        if os.path.isdir(arch):
            for root, _, files in os.walk(arch):
                nfiles += sum(1 for f in files if f.endswith(".md"))
        tdir = os.path.join(store, "topics", chat)
        ntopics = 0
        if os.path.isdir(tdir):
            ntopics = sum(1 for f in os.listdir(tdir)
                          if f.endswith(".md") and f != "INDEX.md")
        print(f"{chat}: {n} entries, {nfiles} archive file(s), {ntopics} topic view(s)")
    log = git(store, "log", "--oneline").stdout.strip().splitlines()
    print(f"git: {len(log)} commits (the ledger)")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, store = argv[1], argv[2]
    created = init_store(store)
    if cmd == "init":
        print(f"✅ init: store ready at {store} "
              f"({'new git store created' if created else 'already initialized'})")
    elif cmd == "deposit":
        ts, source = None, "chat"
        rest = argv[5:]
        for i, a in enumerate(rest):
            if a == "--ts":
                ts = rest[i + 1]
            if a == "--source":
                source = rest[i + 1]
        deposit(store, argv[3], argv[4], ts=ts, source=source)
        n = len(all_source_entries(store, argv[3]))
        commits = len(git(store, "log", "--oneline").stdout.strip().splitlines())
        print(f"✅ deposit: {argv[3]}: {n} entries in store, "
              f"{commits} commits (the ledger)")
    elif cmd == "refine":
        chats = [argv[3]] if len(argv) > 3 else sorted(
            os.listdir(os.path.join(store, "inbox")))
        total = 0
        for c in chats:
            total += refine(store, c)
        print(f"✅ refine: {total} entries -> topic views for "
              f"{len(chats)} chat(s)")
    elif cmd == "status":
        status(store)
    else:
        print(f"unknown command: {cmd}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
