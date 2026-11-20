"""Read a workflow journal and say what actually ran.

The journal path runs past Windows' 260-character MAX_PATH, so it is invisible
to open() without the extended-length prefix -- the same trap that made
save_findings.py silently find nothing.
"""

import collections
import json
import os
import sys

LONG = "\\\\?\\"
BASE = os.path.join(
    LONG + os.path.expanduser("~"), ".claude", "projects",
    "C--Users-lsire-AppData-Roaming-Claude-scratch-workspaces-"
    "436da4c5-e448-4522-8504-fb3dec3718e9-"
    "f86423bb-0f28-4bea-a1b5-a2b812363194-scratch-2026-09-06-5fc263",
    "0a85fa68-f6c3-4f8e-a777-5f0d403d4c58", "subagents", "workflows")


def main(run=None):
    runs = [d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d))]
    run = run or sorted(runs)[-1]
    d = os.path.join(BASE, run)
    jp = os.path.join(d, "journal.jsonl")
    print(f"run: {run}")

    events = []
    with open(jp, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                pass

    kinds = collections.Counter(str(e.get("type")) for e in events)
    print("event types:", dict(kinds))

    by_label = {}
    for e in events:
        lab = e.get("label") or e.get("agentLabel") or e.get("name") or "?"
        rec = by_label.setdefault(lab, {"start": 0, "result": 0, "cached": 0})
        t = str(e.get("type"))
        if "start" in t:
            rec["start"] += 1
        if "result" in t:
            rec["result"] += 1
        if e.get("cached") or e.get("fromCache"):
            rec["cached"] += 1

    done = sum(1 for v in by_label.values() if v["result"])
    cached = sum(1 for v in by_label.values() if v["cached"])
    print(f"\nlabels seen: {len(by_label)}   with a result: {done}   "
          f"flagged cached: {cached}\n")
    for k in sorted(by_label):
        v = by_label[k]
        mark = "cached" if v["cached"] else ("done" if v["result"] else "running")
        print(f"  [{mark:7s}] {k[:66]}")

    # agent transcript files are the ground truth for how many actually ran
    files = [f for f in os.listdir(d) if f.startswith("agent-")
             and f.endswith(".jsonl")]
    print(f"\nagent transcript files on disk: {len(files)}")
    import time
    now = time.time()
    fresh = [f for f in files
             if now - os.path.getmtime(os.path.join(d, f)) < 3600]
    print(f"touched in the last hour (this resume): {len(fresh)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
