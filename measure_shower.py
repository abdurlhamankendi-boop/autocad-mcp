"""Measure the ACA shower blocks and add them to the block catalogue.

The en-suite check needs a shower, and the catalogue had none. ACA metric
content is authored in inches, so insert at 1, read the extents, and record
the plan size in mm (x 25.4) with the insertion offset -- exactly how
measure_blocks.py measured the rest. Done in a scratch drawing that is
closed without saving, and tracked by name.
"""

import json
import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

CAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block_catalog.json")
ROOT = r"C:\ProgramData\Autodesk\ACA 2027\enu\AEC Content\Metric\Design\Bathroom\Shower"
BLOCKS = {"shower": "3D Shower.dwg", "shower_seat": "3D Shower - And Seat.dwg"}
SCALE = 25.4

pythoncom.CoInitialize()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x), float(y), float(z)])


def main():
    a = w.dynamic.Dispatch(w.GetActiveObject("AutoCAD.Application"))
    before = {a.Documents.Item(i).Name for i in range(a.Documents.Count)}
    a.Documents.Add()
    doc = next(a.Documents.Item(i) for i in range(a.Documents.Count)
               if a.Documents.Item(i).Name not in before)
    name = doc.Name
    cat = json.load(open(CAT))
    try:
        for key, fn in BLOCKS.items():
            path = os.path.join(ROOT, fn)
            ref = doc.ModelSpace.InsertBlock(pt(0, 0), path, 1.0, 1.0, 1.0, 0.0)
            lo, hi = ref.GetBoundingBox()
            # Most ACA "Metric" 2D content is drawn in inches, but these 3D
            # showers came back 900 units wide -- millimetres. x25.4 made a
            # 22.9 m shower. Decide the unit from the magnitude, per block.
            raw = max(hi[0] - lo[0], hi[1] - lo[1])
            s = 1.0 if raw > 200 else SCALE
            wd, dp = (hi[0] - lo[0]) * s, (hi[1] - lo[1]) * s
            cat[key] = {"path": path, "scale": s, "w": round(wd, 1),
                        "d": round(dp, 1), "offx": round(lo[0] * s, 1),
                        "offy": round(lo[1] * s, 1)}
            print(f"  {key:12s} {wd:7.1f} x {dp:7.1f} mm   unit x{s:g}   offset "
                  f"({lo[0] * s:.0f}, {lo[1] * s:.0f})   {fn}")
            ref.Delete()
    finally:
        for i in range(a.Documents.Count):
            d = a.Documents.Item(i)
            if d.Name == name:
                d.Close(False)
                break
    json.dump(cat, open(CAT, "w"), indent=1)
    print(f"catalogue now holds {len(cat)} blocks")


if __name__ == "__main__":
    for attempt in range(5):
        try:
            main()
            break
        except Exception as exc:
            t = str(exc).lower()
            if "rejected" in t or "-2147418111" in t or isinstance(exc, AttributeError):
                print(f"  AutoCAD busy, retrying ({attempt + 1})")
                time.sleep(5)
                continue
            raise
