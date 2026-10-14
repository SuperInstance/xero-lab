#!/usr/bin/env python3
"""turn.py — build one character's prompt for a beat and take the turn.

Usage: turn.py CHAR TAG INSTRUCTION_FILE

Assembles: sheet + life + in-game log + the shared scene so far +
this beat's instruction. Hands the call to crank.py (pacing gate,
backoff, hard stop). Raw post lands in posts/TAG-CHAR.md.
"""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.join(BASE, "campaign")
NAMES = {"tobin": "Tobin Marlow", "marta": "Marta Venn", "pell": "Pell Sutter"}


def read(path):
    with open(path) as f:
        return f.read().strip()


def main():
    char, tag, instr_file = sys.argv[1], sys.argv[2], sys.argv[3]
    name = NAMES[char]
    cdir = os.path.join(CAMP, "characters", char)
    prompt = f"""You are {name}. Below is everything you are and everything that has happened so far. Stay inside it.

=== YOUR SHEET ===
{read(os.path.join(cdir, "sheet.md"))}

=== YOUR LIFE SO FAR ===
{read(os.path.join(cdir, "life.md"))}

=== YOUR IN-GAME LOG (your memory of the game) ===
{read(os.path.join(cdir, "log.md"))}

=== THE SCENE SO FAR (the GM's posts and everyone's posts, in order) ===
{read(os.path.join(CAMP, "scene.md"))}

=== NOW ===
{read(instr_file)}

Post as {name}, first person, in your own voice. About 120 words at most.
Say what you perceive — what you notice and what you make of it — and what
you attempt to do. End on your attempt; the Game Master resolves what
happens. Speak only for yourself. Do not narrate other characters'
actions, and do not invent facts about the wider world — radio calls,
other boats, official word, the weather already turned — that the GM
hasn't given you. If you need to know something, try to learn it inside
the scene, from the people and things in front of you. Write only your
post: no title, no word count, no notes to the GM."""
    os.makedirs(os.path.join(BASE, "posts"), exist_ok=True)
    prompt_path = os.path.join(BASE, "posts", f"{tag}-{char}-prompt.md")
    out_path = os.path.join(BASE, "posts", f"{tag}-{char}.md")
    with open(prompt_path, "w") as f:
        f.write(prompt)
    return subprocess.call(
        ["python3", os.path.join(BASE, "crank.py"), char,
         f"turn-{tag}", prompt_path, out_path, "--max-tokens", "600"])


if __name__ == "__main__":
    sys.exit(main())
