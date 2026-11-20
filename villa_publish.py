"""Load the villa sheets into AutoCAD, save as DWG, and plot to A3 PDF.

Whole-job retry: AutoCAD returns RPC_E_CALL_REJECTED whenever it is busy, and
retrying individual calls is whack-a-mole.
"""

import os
import time

import ezdxf
import pythoncom
import win32com.client as w

pythoncom.CoInitialize()

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
MEDIA = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
SHEETS = ["A-201_GROUND_FLOOR_PLAN", "A-202_FIRST_FLOOR_PLAN"]


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def publish(name):
    dxf = os.path.join(OUT, name + ".dxf")
    dwg = os.path.join(OUT, name + ".dwg")
    pdf = os.path.join(OUT, name + ".pdf")
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
    doc.SetVariable("LWDISPLAY", 1)
    doc.SetVariable("INSUNITS", 4)
    doc.Activate()
    app.ZoomExtents()

    lay = doc.ActiveLayout
    lay.ConfigName = "DWG To PDF.pc3"
    lay.RefreshPlotDeviceInfo()      # resets media/scale -> must precede them
    lay.CanonicalMediaName = MEDIA
    lay.PlotType = 1                 # acExtents
    lay.UseStandardScale = True
    lay.StandardScale = 0            # acScaleToFit
    lay.CenterPlot = True
    lay.PlotRotation = 0
    doc.SetVariable("BACKGROUNDPLOT", 0)
    doc.Plot.PlotToFile(pdf, "DWG To PDF.pc3")
    return got, want, os.path.getsize(pdf) // 1024


if __name__ == "__main__":
    for name in SHEETS:
        last = None
        for _ in range(6):
            try:
                got, want, kb = publish(name)
                flag = "OK " if got == want else "DIFF"
                print(f"{flag} {name:32s} {got:4d}/{want:<4d} entities   "
                      f"PDF {kb} KB")
                last = None
                break
            except Exception as exc:
                last = exc
                if not busy(exc):
                    print(f"ERR {name:32s} {str(exc)[:70]}")
                    break
                time.sleep(2.5)
        if last is not None and busy(last):
            print(f"BUSY {name:32s} AutoCAD stayed busy")
