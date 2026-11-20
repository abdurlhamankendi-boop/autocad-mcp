"""Load each generated DXF into AutoCAD, insert the real ACA content blocks,
and save as DWG.

AutoCAD returns RPC_E_CALL_REJECTED (-2147418111) whenever it is mid-operation.
Retrying individual calls turns into whack-a-mole because any one of them can
fail, so the whole per-sheet job is retried instead -- it reopens the DXF from
scratch each time, which makes it safely repeatable.
"""

import math
import os
import sys
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import furniture_layout as fl

pythoncom.CoInitialize()

OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
SCALE = 25.4                      # ACA "Metric" content is authored in inches
FIXTURES = {"wc", "basin", "bath"}
SHEETS = [("A-101_GF_TECH", "ground"), ("A-102_FF_TECH", "first"),
          ("A-111_GF_PRES", "ground"), ("A-112_FF_PRES", "first")]


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def do_sheet(sheet, floor):
    dxf = os.path.join(OUT, sheet + ".dxf")
    dwg = os.path.join(OUT, sheet + ".dwg")
    app = w.GetActiveObject("AutoCAD.Application")

    for i in range(app.Documents.Count - 1, -1, -1):
        d = app.Documents.Item(i)
        if str(d.Name).lower() in (os.path.basename(dwg).lower(),
                                   os.path.basename(dxf).lower()):
            d.Close(False)

    doc = app.Documents.Open(dxf)
    doc.SetVariable("INSUNITS", 4)
    ms = doc.ModelSpace
    before = int(ms.Count)

    placed, failed = 0, []
    for key, x, y, rot in (fl.GROUND if floor == "ground" else fl.FIRST):
        meta = fl.CATALOG.get(key)
        if not meta or "path" not in meta:
            failed.append(key)
            continue
        ix, iy = fl.insert_point(key, x, y, rot)
        ref = ms.InsertBlock(pt(ix, iy), meta["path"],
                             SCALE, SCALE, SCALE, math.radians(rot))
        ref.Layer = "A-FLOR-FIXT" if key in FIXTURES else "A-FURN"
        placed += 1

    after = int(ms.Count)
    doc.SaveAs(dwg)
    doc.SetVariable("LWDISPLAY", 1)
    return before, after, placed, failed


for sheet, floor in SHEETS:
    last = None
    for _ in range(6):
        try:
            before, after, placed, failed = do_sheet(sheet, floor)
            print(f"{sheet:16s} {before:4d} -> {after:4d} entities   "
                  f"blocks placed {placed}"
                  + (f"   FAILED {failed}" if failed else ""))
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                print(f"{sheet:16s} ERROR {str(exc)[:90]}")
                break
            time.sleep(2.5)
    if last is not None and busy(last):
        print(f"{sheet:16s} gave up: AutoCAD stayed busy")

time.sleep(1.0)
app = w.GetActiveObject("AutoCAD.Application")
names = [str(b.Name) for b in app.ActiveDocument.Blocks
         if not str(b.Name).startswith("*")]
print(f"\nblock definitions in last sheet: {len(names)}")
print("  " + ", ".join(sorted(names)[:12]))
