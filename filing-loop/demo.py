#!/usr/bin/env python3
"""
demo.py — end-to-end demo of the filing loop with synthetic chat deposits.

Sets a small split gate (1000 bytes) so the cascade visibly triggers:
L1 (inbox -> daily files) and L2 (a huge day -> per-topic files).
Deposits 35 utterances across 2 chats, 3 days, 3 themes, then refines
and verifies that no entry was lost.
"""
import os
import sys

os.environ["FILING_SPLIT_BYTES"] = "1000"  # before importing filing_loop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_loop as fl

STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store")

AUTOPILOT = [
    "autopilot yaw test in heavy seas: the compass swings but the deadband holds",
    "compass deviation on this heading is two degrees, note it in the logbook",
    "the steering rams answer slower in cold oil, widen the gate a little",
    "deadband question: how far off course before the autopilot corrects",
    "heavy seas again, the compass card hunts, time delay saves the rams",
]
XERO = [
    "xero clone for the uno board: build in git, sync the winning commits down",
    "telegram injection for the zero agent, memory files ride the prompt",
    "the zero agent is just files, any harness can crank the same files",
    "uno pin idea: click to talk, the agent answers locally or reaches out",
    "agent contracts are algorithms, log the transaction not the voltage",
]
BOAT = [
    "invoice for the brandons job goes out monday, jim has the hours",
    "mouse the dog rode the skiff to the harbor, sitka sun for once",
    "harbor fuel dock opens early, top up before the weekend fleet",
    "sitka tide table says low water at six, plan the haul around it",
    "the invoice total changed, brandons added the mailbox migration",
]
BURST = [  # day-3 burst for telegram-main: forces the L2 topic split
    "autopilot compass deadband rams seas yaw logbook heading oil gate",
    "xero uno clone telegram injection agent files harness commits sync",
    "autopilot deadband again: compass swing, rams lag, seas building",
    "xero agent memory: telegram deposits become files, files become xero",
    "compass card sticky at north, check the compass fluid this week",
    "uno redshirt build: xero on the metal, telegram stays in the cloud",
    "rams chatter at the gate edge, deadband or worn seals, watch it",
    "telegram bot cannot read its own history, injection is the memory",
    "seas forecast heavy friday, autopilot sea trial waits for monday",
    "clone the xero repo, the uno board syncs at the dock on wifi",
]


def ts(day, i):
    return f"2026-10-{day}T{8 + i:02d}:15:00-08:00"


def run():
    fl.init_store(STORE)
    plan = []
    for i in range(5):
        plan.append(("telegram-main", ts(10, i), AUTOPILOT[i], "telegram"))
        plan.append(("zero-lab", ts(10, i), XERO[i], "telegram"))
    for i in range(5):
        plan.append(("telegram-main", ts(11, i), BOAT[i], "telegram"))
        plan.append(("zero-lab", ts(11, i), AUTOPILOT[i], "telegram"))
    for i, text in enumerate(BURST):
        plan.append(("telegram-main", ts(12, i), text, "telegram"))
    for i in range(5):
        plan.append(("zero-lab", ts(12, i), BOAT[i], "telegram"))

    for chat, when, text, source in plan:
        fl.deposit(STORE, chat, text, ts=when, source=source)
    print(f"deposited {len(plan)} utterances")

    for chat in ("telegram-main", "zero-lab"):
        fl.refine(STORE, chat)
    print("refined both chats\n")

    # verification: every deposited entry still exists exactly once in sources
    total = sum(len(fl.all_source_entries(STORE, c))
                for c in ("telegram-main", "zero-lab"))
    print(f"verify: {total} source entries on disk, {len(plan)} deposited",
          "-> OK" if total == len(plan) else "-> MISMATCH")
    fl.status(STORE)


if __name__ == "__main__":
    run()
