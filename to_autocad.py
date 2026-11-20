"""Load the generated DXF sheets into the running AutoCAD and save them as DWG.

The DXF is the source of truth (see plan_dxf.py for why the drawings are not
built over COM). AutoCAD reads DXF natively, so this is a load + SaveAs rather
than a re-draw, which keeps layers, lineweights, hatches and dimensions intact.
"""
import os
import ezdxf
import pythoncom
import win32com.client as w

OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
SHEETS = ["A-101_GF_TECH", "A-102_FF_TECH", "A-111_GF_PRES", "A-112_FF_PRES"]

pythoncom.CoInitialize()

for name in SHEETS:
    dxf = os.path.join(OUT, name + ".dxf")
    dwg = os.path.join(OUT, name + ".dwg")

    # expected content, read straight from the DXF
    src = ezdxf.readfile(dxf)
    want_ents = len(list(src.modelspace()))
    want_layers = len([l.dxf.name for l in src.layers])

    # Re-acquire each pass: closing a document invalidates the cached proxy.
    app = w.GetActiveObject("AutoCAD.Application")
    for i in range(app.Documents.Count - 1, -1, -1):
        d = app.Documents.Item(i)
        if os.path.basename(dwg).lower() == str(d.Name).lower():
            d.Close(False)

    app = w.GetActiveObject("AutoCAD.Application")
    doc = app.Documents.Open(dxf)
    got_ents = int(doc.ModelSpace.Count)
    got_layers = int(doc.Layers.Count)

    doc.SaveAs(dwg)                     # rebinds the document to the .dwg
    doc.SetVariable("LWDISPLAY", 1)     # show lineweights on screen
    try:
        app.ZoomExtents()
    except Exception:
        pass

    ok = "OK " if got_ents == want_ents else "DIFF"
    print(f"{ok} {name:18s} entities {got_ents:4d}/{want_ents:<4d} "
          f"layers {got_layers:2d}/{want_layers:<2d} -> {os.path.basename(dwg)}")

app = w.GetActiveObject("AutoCAD.Application")
print("\nopen documents now:", app.Documents.Count)
