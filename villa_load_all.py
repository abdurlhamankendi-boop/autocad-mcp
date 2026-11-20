"""Wait for AutoCAD to finish starting, then load the whole villa: every 2D
view as DWG, plus the 3D solid model imported from STEP.

AutoCAD takes a while to start and rejects COM calls until it is ready, so the
first job is to poll rather than assume.
"""

import os
import time

import pythoncom
import win32com.client as w

pythoncom.CoInitialize()

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
SHEETS_2D = [
    "A-201_GROUND_FLOOR_PLAN", "A-202_FIRST_FLOOR_PLAN",
    "VILLA_PLAN_BASEMENT", "VILLA_PLAN_ROOF",
    "VILLA_ELEV_S", "VILLA_ELEV_N", "VILLA_ELEV_E", "VILLA_ELEV_W",
    "VILLA_SECTION_AA",
    "VILLA_VIEW_AERIAL_SW", "VILLA_VIEW_POOL_EYE", "VILLA_VIEW_AERIAL_NE",
]
STEP = os.path.join(OUT, "villa.step")


def busy(exc):
    t = str(exc).lower()
    return ("rejected" in t or "-2147418111" in t or "busy" in t
            or "unavailable" in t or "-2147221021" in t)


def wait_for_autocad(timeout=300):
    """AutoCAD refuses COM until the editor is up. Poll rather than assume."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            app = w.GetActiveObject("AutoCAD.Application")
            _ = app.Documents.Count          # forces a real call
            print(f"  AutoCAD ready after {time.time() - t0:.0f}s")
            return app
        except Exception:
            time.sleep(5)
    raise RuntimeError(f"AutoCAD did not become available within {timeout}s")


def load_2d(name):
    src = os.path.join(OUT, name + ".dxf")
    dwg = os.path.join(OUT, name + ".dwg")
    app = w.GetActiveObject("AutoCAD.Application")
    for i in range(app.Documents.Count - 1, -1, -1):
        d = app.Documents.Item(i)
        if str(d.Name).lower() in (os.path.basename(dwg).lower(),
                                   os.path.basename(src).lower()):
            d.Close(False)
    doc = app.Documents.Open(src)
    n = int(doc.ModelSpace.Count)
    doc.SaveAs(dwg)
    doc.SetVariable("LWDISPLAY", 1)
    doc.SetVariable("INSUNITS", 4)
    return n


def import_step():
    """Bring the 3D solid model in. FILEDIA=0 stops the file dialog blocking."""
    app = w.GetActiveObject("AutoCAD.Application")
    app.Documents.Add()
    doc = app.ActiveDocument
    doc.SetVariable("INSUNITS", 4)
    doc.SetVariable("FILEDIA", 0)
    doc.SendCommand(f'_.IMPORT\n{STEP}\n')
    return doc


if __name__ == "__main__":
    print("waiting for AutoCAD...")
    wait_for_autocad()

    ok = 0
    for name in SHEETS_2D:
        if not os.path.exists(os.path.join(OUT, name + ".dxf")):
            print(f"  MISSING {name}")
            continue
        last = None
        for _ in range(6):
            try:
                n = load_2d(name)
                print(f"  OK   {name:30s} {n:4d} entities")
                ok += 1
                last = None
                break
            except Exception as exc:
                last = exc
                if not busy(exc):
                    print(f"  ERR  {name:30s} {str(exc)[:60]}")
                    break
                time.sleep(3)
        if last is not None and busy(last):
            print(f"  BUSY {name}")

    print("")
    print("importing 3D solid model from STEP (this takes a while)...")
    try:
        import_step()
        time.sleep(45)                       # STEP import runs asynchronously
        app = w.GetActiveObject("AutoCAD.Application")
        doc = app.ActiveDocument
        solids = sum(1 for e in doc.ModelSpace
                     if str(e.EntityName) == "AcDb3dSolid")
        total = int(doc.ModelSpace.Count)
        dwg3 = os.path.join(OUT, "VILLA_3D_MODEL.dwg")
        doc.SaveAs(dwg3)
        doc.SetVariable("FILEDIA", 1)
        print(f"  3D model: {total} entities, {solids} solids -> "
              f"{os.path.basename(dwg3)}")
    except Exception as exc:
        print("  STEP import failed:", str(exc)[:100])

    app = w.GetActiveObject("AutoCAD.Application")
    print("")
    print(f"{ok}/{len(SHEETS_2D)} 2D views loaded; "
          f"{app.Documents.Count} documents open")
