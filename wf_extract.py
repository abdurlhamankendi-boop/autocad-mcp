"""Pull one lens's findings and verdicts out of the workflow journal.

The journal sits past MAX_PATH, so the extended-length prefix is required or
open() reports the file does not exist.
"""

import json
import os
import sys

sys_stdout_reconfigured = True

LONG = "\\\\?\\"
BASE = os.path.join(
    LONG + os.path.expanduser("~"), ".claude", "projects",
    "C--Users-lsire-AppData-Roaming-Claude-scratch-workspaces-"
    "436da4c5-e448-4522-8504-fb3dec3718e9-"
    "f86423bb-0f28-4bea-a1b5-a2b812363194-scratch-2026-09-06-5fc263",
    "0a85fa68-f6c3-4f8e-a777-5f0d403d4c58", "subagents", "workflows",
    "wf_a96d3cea-feb")


def main(want):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ev = []
    with open(os.path.join(BASE, "journal.jsonl"), encoding="utf-8",
              errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    ev.append(json.loads(line))
                except Exception:
                    pass

    for e in ev:
        if str(e.get("type")) != "result":
            continue
        r = e.get("result")
        if not isinstance(r, dict) or "findings" not in r:
            continue
        for f in r["findings"]:
            cat = str(f.get("category", "")).lower()
            nm = str(f.get("name", ""))
            if want.lower() in cat or want.lower() in nm.lower():
                print(f"\n### {nm}")
                print(f"  url      {f.get('url', '-')}")
                print(f"  cost     {f.get('cost', '-')}")
                print(f"  licence  {str(f.get('licence', '-'))[:220]}")
                print(f"  formats  {str(f.get('formats', '-'))[:160]}")
                print(f"  quality  {str(f.get('quality', '-'))[:300]}")
                print(f"  why      {str(f.get('why', '-'))[:400]}")
                print(f"  conf     {f.get('confidence')}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "block")
