"""Import the villa STEP model into AutoCAD as native 3D solids.

The first attempt produced 0 solids. STEP import runs asynchronously through
AcTranslators.exe, so a fixed sleep is unreliable — poll the entity count
instead, and quote the path (it contains spaces via OneDrive).
"""

import os
import time

import pythoncom
import win32com.client as w

pythoncom.CoInitialize()

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
STEP = os.path.join(OUT, "villa.step")
DWG = os.path.join(OUT, "VILLA_3D_MODEL.dwg")


def app():
    return w.GetActiveObject("AutoCAD.Application")


def count(doc):
    try:
        return int(doc.ModelSpace.Count)
    except Exception:
        return -1


if __name__ == "__main__":
    a = app()
    # close any stale copy so SaveAs can overwrite
    for i in range(a.Documents.Count - 1, -1, -1):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == os.path.basename(DWG).lower():
            d.Close(False)

    a = app()
    a.Documents.Add()
    doc = a.ActiveDocument
    doc.SetVariable("INSUNITS", 4)
    doc.SetVariable("FILEDIA", 0)
    before = count(doc)
    print(f"fresh drawing: {before} entities")

    # quote the path; OneDrive puts spaces in it
    doc.SendCommand(f'_.IMPORT\n"{STEP}"\n')
    print("IMPORT issued, polling...")

    t0 = time.time()
    last = before
    stable = 0
    while time.time() - t0 < 420:
        time.sleep(10)
        try:
            a = app()
            doc = a.ActiveDocument
            n = count(doc)
        except Exception:
            continue
        if n > last:
            print(f"  {time.time() - t0:5.0f}s  {n} entities")
            last, stable = n, 0
        elif n > before:
            stable += 1
            if stable >= 3:          # count settled -> import finished
                break

    a = app()
    doc = a.ActiveDocument
    total = count(doc)
    solids = 0
    try:
        solids = sum(1 for e in doc.ModelSpace
                     if str(e.ObjectName).endswith("3dSolid")
                     or str(e.EntityName) == "AcDb3dSolid")
    except Exception as exc:
        print("  count failed:", str(exc)[:60])

    print(f"\nresult: {total} entities, {solids} 3D solids")
    if total > 0:
        try:
            doc.SaveAs(DWG)
            doc.SetVariable("FILEDIA", 1)
            a.ZoomExtents()
            print("saved:", DWG)
        except Exception as exc:
            print("save failed:", str(exc)[:80])
    else:
        print("IMPORT produced nothing — STEP import may be unavailable in this "
              "vertical, or the translator failed silently.")
        try:
            doc.SetVariable("FILEDIA", 1)
        except Exception:
            pass
