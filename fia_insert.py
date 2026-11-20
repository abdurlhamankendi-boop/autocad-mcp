"""Copy FIA block definitions into the villa sheets and place them.

Not via -WBLOCK: that prompts for a block name on the command line, where a
SPACE is Enter, so "PNL 15C Bed Plan" can never be entered. CopyObjects moves
the definition between databases directly, with no parsing in the way.

Placement is measure-scale-move, same as the ACA blocks: insert at 1, read the
bounding box, scale uniformly, then move onto the footprint the plan demands.
"""

import json
import math
import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

BLOCKS = r"C:\Users\lsire\OneDrive\Desktop\Villa\blocks"
PACKS = ("Furniture-pack-2-and-3__FIA_Furniture_Cad_Blocks_02.dwg",
         "Furniture-pack-2-and-3__FIA_Furniture_Cad_Blocks_03.dwg")

pythoncom.CoInitialize()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def objs(items):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(items))


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def get_doc(a, name):
    for i in range(a.Documents.Count):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def find_block(doc, name):
    for i in range(doc.Blocks.Count):
        b = doc.Blocks.Item(i)
        if str(b.Name) == name:
            return b
    return None


def copy_definition(src_doc, dst_doc, name):
    """Copy one block definition from src into dst. Returns True if present."""
    if find_block(dst_doc, name) is not None:
        return True
    src = find_block(src_doc, name)
    if src is None:
        return False
    ents = [e for e in src]
    if not ents:
        return False
    dst_blk = find_block(dst_doc, name)
    if dst_blk is None:
        dst_blk = dst_doc.Blocks.Add(pt(0, 0), name)
    src_doc.CopyObjects(objs(ents), dst_blk)
    return True


def place(doc, name, fp, rot=0.0, layer="A-FURN"):
    """Insert by NAME (the definition is already in this drawing), then scale
    and move onto the target footprint."""
    ms = doc.ModelSpace
    ref = ms.InsertBlock(pt(0, 0), name, 1.0, 1.0, 1.0, math.radians(rot))
    lo, hi = ref.GetBoundingBox()
    aw, ad = hi[0] - lo[0], hi[1] - lo[1]
    ew, ed = fp[2] - fp[0], fp[3] - fp[1]
    if aw > 1e-6 and ad > 1e-6:
        k = min(ew / aw, ed / ad)
        if abs(k - 1.0) > 1e-4:
            ref.ScaleEntity(pt(0, 0), k)
    lo, hi = ref.GetBoundingBox()
    ref.Move(pt(lo[0], lo[1]), pt(fp[0], fp[1]))
    ref.Layer = layer
    return ref


def close_packs():
    """The pack drawings were only needed as a source. 25 open documents is
    what made AutoCAD start refusing COM calls."""
    a = w.GetActiveObject("AutoCAD.Application")
    closed = []
    for i in range(a.Documents.Count - 1, -1, -1):
        try:
            d = a.Documents.Item(i)
            p = str(d.Path or "")
            if p.lower().startswith(BLOCKS.lower()):
                n = str(d.Name)
                d.Close(False)
                closed.append(n)
        except Exception:
            pass
    return closed


if __name__ == "__main__":
    for attempt in range(8):
        try:
            c = close_packs()
            a = w.GetActiveObject("AutoCAD.Application")
            print(f"closed {len(c)} block-pack document(s); "
                  f"{a.Documents.Count} still open")
            break
        except Exception as exc:
            if not busy(exc):
                raise
            print(f"  busy, retrying ({attempt + 1})...")
            time.sleep(8)
