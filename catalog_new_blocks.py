"""Enumerate and MEASURE every block definition in the downloaded libraries.

A block's name tells you nothing about its size, and these packs ship in both
metric and imperial. Extents are measured from the block definition's own
entities, so what goes in the catalogue is what will actually be drawn.
"""

import json
import os
import time

import pythoncom
import win32com.client as w

BLOCKS = r"C:\Users\lsire\OneDrive\Desktop\Villa\blocks"
OUT = os.path.join(BLOCKS, "measured_blocks.json")

pythoncom.CoInitialize()


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def get_doc(a, name):
    for i in range(a.Documents.Count):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def measure_block(blk):
    """Union of the bounding boxes of the block definition's own entities."""
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    n = 0
    for e in blk:
        try:
            a, b = e.GetBoundingBox()
        except Exception:
            continue
        for i in range(3):
            lo[i] = min(lo[i], a[i])
            hi[i] = max(hi[i], b[i])
        n += 1
    if n == 0 or lo[0] == float("inf"):
        return None
    return {"w": hi[0] - lo[0], "d": hi[1] - lo[1], "h": hi[2] - lo[2],
            "minx": lo[0], "miny": lo[1], "entities": n}


def scan(path):
    a = w.GetActiveObject("AutoCAD.Application")
    name = os.path.basename(path)
    doc = get_doc(a, name)
    if doc is None:
        a.Documents.Open(path)
        doc = get_doc(a, name)
    if doc is None:
        return None, []

    out = []
    for i in range(doc.Blocks.Count):
        blk = doc.Blocks.Item(i)
        bn = str(blk.Name)
        if bn.startswith("*") or bn.lower() in ("model_space", "paper_space"):
            continue
        m = measure_block(blk)
        if not m or m["w"] <= 0 or m["d"] <= 0:
            continue
        out.append({"block": bn, "file": name, **{k: round(v, 1)
                                                  for k, v in m.items()}})
    try:
        doc.Close(False)
    except Exception:
        pass
    return name, out


def run(state):
    """Resume-capable: a busy AutoCAD used to send this back to file one, so
    it re-measured the same three libraries forever and never reached the
    rest."""
    files = sorted(f for f in os.listdir(BLOCKS)
                   if f.lower().endswith(".dwg") and os.path.getsize(
                       os.path.join(BLOCKS, f)) > 1024)
    allblocks = state["blocks"]
    for f in files:
        if f in state["done"]:
            continue
        try:
            name, blocks = scan(os.path.join(BLOCKS, f))
        except Exception as exc:
            if busy(exc):
                raise
            print(f"  {f[:52]:52s} failed: {str(exc)[:40]}")
            continue
        print(f"  {f[:52]:52s} {len(blocks):>4} block definitions")
        allblocks += blocks
        state["done"].add(f)
        json.dump(allblocks, open(OUT, "w"), indent=1)
    json.dump(allblocks, open(OUT, "w"), indent=1)
    print(f"\n{len(allblocks)} measured block definitions -> "
          f"{os.path.basename(OUT)}")
    return allblocks


if __name__ == "__main__":
    last = None
    state = {"done": set(), "blocks": []}
    for attempt in range(12):
        try:
            run(state)
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy after {len(state['done'])} file(s), "
                  f"resuming ({attempt + 1})...")
            time.sleep(10)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
