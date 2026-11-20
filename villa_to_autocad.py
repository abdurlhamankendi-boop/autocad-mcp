"""Load the derived villa DXFs into the running AutoCAD and save them as DWG.

Same whole-job retry as insert_blocks.py: AutoCAD returns RPC_E_CALL_REJECTED
whenever it is mid-operation, and retrying individual calls is whack-a-mole
because any one of them can fail.
"""

import os
import time

import ezdxf
import pythoncom
import win32com.client as w

pythoncom.CoInitialize()

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
ORDER = [
    "VILLA_VIEW_AERIAL_SW", "VILLA_VIEW_POOL_EYE", "VILLA_VIEW_AERIAL_NE",
    "VILLA_PLAN_BASEMENT", "VILLA_PLAN_GF", "VILLA_PLAN_FF", "VILLA_PLAN_ROOF",
    "VILLA_SECTION_AA",
    "VILLA_ELEV_S", "VILLA_ELEV_N", "VILLA_ELEV_E", "VILLA_ELEV_W",
]


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def load(name):
    dxf = os.path.join(OUT, name + ".dxf")
    dwg = os.path.join(OUT, name + ".dwg")

    want = len(list(ezdxf.readfile(dxf).modelspace()))

    app = w.GetActiveObject("AutoCAD.Application")
    for i in range(app.Documents.Count - 1, -1, -1):
        d = app.Documents.Item(i)
        if str(d.Name).lower() in (os.path.basename(dwg).lower(),
                                   os.path.basename(dxf).lower()):
            d.Close(False)

    doc = app.Documents.Open(dxf)
    got = int(doc.ModelSpace.Count)
    doc.SaveAs(dwg)
    doc.SetVariable("LWDISPLAY", 1)     # show the lineweight hierarchy on screen
    doc.SetVariable("INSUNITS", 4)      # millimetres
    return got, want


if __name__ == "__main__":
    ok = 0
    for name in ORDER:
        if not os.path.exists(os.path.join(OUT, name + ".dxf")):
            print(f"{name:22s} MISSING")
            continue
        last = None
        for _ in range(6):
            try:
                got, want = load(name)
                flag = "OK " if got == want else "DIFF"
                print(f"{flag} {name:22s} {got:4d}/{want:<4d} entities")
                ok += 1
                last = None
                break
            except Exception as exc:
                last = exc
                if not busy(exc):
                    print(f"ERR {name:22s} {str(exc)[:70]}")
                    break
                time.sleep(2.5)
        if last is not None and busy(last):
            print(f"BUSY {name:22s} AutoCAD stayed busy")

    time.sleep(1.0)
    app = w.GetActiveObject("AutoCAD.Application")
    # bring the aerial to the front so there is something to look at
    for i in range(app.Documents.Count):
        d = app.Documents.Item(i)
        if str(d.Name).upper() == "VILLA_VIEW_AERIAL_SW.DWG":
            d.Activate()
            time.sleep(0.8)
            app.ZoomExtents()
            break
    print(f"\n{ok}/{len(ORDER)} loaded; {app.Documents.Count} documents open")
