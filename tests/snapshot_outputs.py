"""Summarise a deliverables folder so two runs can be compared exactly.

    python tests\\snapshot_outputs.py OUT_DIR --out snap.json
    python tests\\snapshot_outputs.py --diff A.json B.json

The regression gate for generalising the builders: the CURRENT villa's
outputs must not change. Per DXF: entity count by (layer, type), text
strings (sorted), extents rounded to 0.1 mm. Per glTF group: groups.json
bounds and the .glb byte size. Per PNG: pixel size only (antialiasing is
not a design change). Title-block dates are dropped (they come from file
times).
"""
from __future__ import annotations

import json
import os
import re
import sys

DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def dxf_summary(path):
    import ezdxf
    doc = ezdxf.readfile(path)
    counts, texts = {}, []
    xs, ys = [], []
    for e in doc.modelspace():
        k = f"{e.dxf.layer}|{e.dxftype()}"
        counts[k] = counts.get(k, 0) + 1
        if e.dxftype() in ("TEXT", "MTEXT"):
            t = e.dxf.text if e.dxftype() == "TEXT" else e.text
            texts.append(DATE.sub("<date>", t))
    for lay in doc.layouts:
        if lay.name == "Model":
            continue
        for e in lay:
            k = f"PS:{lay.name}|{e.dxf.layer}|{e.dxftype()}"
            counts[k] = counts.get(k, 0) + 1
            if e.dxftype() in ("TEXT", "MTEXT"):
                t = e.dxf.text if e.dxftype() == "TEXT" else e.text
                texts.append(DATE.sub("<date>", t))
    try:
        from ezdxf import bbox
        ext = bbox.extents(doc.modelspace(), fast=True)
        extents = [round(v, 1) for v in (*ext.extmin[:2], *ext.extmax[:2])] if ext.has_data else None
    except Exception:          # noqa: BLE001
        extents = None
    return {"counts": counts, "texts": sorted(texts), "extents": extents}


def snapshot(root):
    out = {}
    for dp, _dn, fns in os.walk(root):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            low = fn.lower()
            try:
                if low.endswith(".dxf"):
                    out[rel] = dxf_summary(p)
                elif low == "groups.json":
                    g = json.load(open(p))
                    out[rel] = {k: [round(v, 1) for v in b] for k, b in g.items()}
                elif low.endswith(".glb"):
                    out[rel] = {"bytes": os.path.getsize(p)}
                elif low.endswith(".png"):
                    from PIL import Image
                    out[rel] = {"size": list(Image.open(p).size)}
            except Exception as exc:  # noqa: BLE001
                out[rel] = {"error": str(exc)[:200]}
    return out


def diff(a, b):
    bad = []
    for k in sorted(set(a) | set(b)):
        if k not in a:
            bad.append(f"NEW      {k}")
        elif k not in b:
            bad.append(f"MISSING  {k}")
        elif a[k] != b[k]:
            da, db = a[k], b[k]
            if isinstance(da, dict) and isinstance(db, dict):
                for kk in sorted(set(da) | set(db)):
                    if da.get(kk) != db.get(kk):
                        va, vb = da.get(kk), db.get(kk)
                        if isinstance(va, dict) and isinstance(vb, dict):
                            ch = [f"{x}: {va.get(x)} -> {vb.get(x)}"
                                  for x in sorted(set(va) | set(vb)) if va.get(x) != vb.get(x)]
                            bad.append(f"CHANGED  {k} [{kk}] " + "; ".join(ch[:8]))
                        else:
                            bad.append(f"CHANGED  {k} [{kk}] {str(va)[:120]} -> {str(vb)[:120]}")
            else:
                bad.append(f"CHANGED  {k}")
    return bad


if __name__ == "__main__":
    if sys.argv[1] == "--diff":
        a = json.load(open(sys.argv[2], encoding="utf-8-sig"))
        b = json.load(open(sys.argv[3], encoding="utf-8-sig"))
        d = diff(a, b)
        print("\n".join(d) if d else "IDENTICAL")
        sys.exit(1 if d else 0)
    if len(sys.argv) > 3 and sys.argv[2] == "--out":
        with open(sys.argv[3], "w", encoding="utf-8") as fh:
            json.dump(snapshot(sys.argv[1]), fh, indent=1, sort_keys=True)
    else:
        json.dump(snapshot(sys.argv[1]), sys.stdout, indent=1, sort_keys=True)
