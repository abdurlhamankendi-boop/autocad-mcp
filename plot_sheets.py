"""Plot the current DWG sheets (blocks included) to A3 landscape PDF."""
import os, time, pythoncom, win32com.client as w
pythoncom.CoInitialize()
OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
MEDIA = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
SHEETS = ["A-101_GF_TECH", "A-102_FF_TECH", "A-111_GF_PRES", "A-112_FF_PRES"]

def busy(e):
    t = str(e).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t

def plot(name):
    dwg = os.path.join(OUT, name + ".dwg")
    pdf = os.path.join(OUT, name + ".pdf")
    app = w.GetActiveObject("AutoCAD.Application")
    doc = None
    for i in range(app.Documents.Count):
        d = app.Documents.Item(i)
        if str(d.Name).lower() == os.path.basename(dwg).lower():
            doc = d; break
    if doc is None:
        doc = app.Documents.Open(dwg)
    doc.Activate()
    app.ZoomExtents()
    lay = doc.ActiveLayout
    lay.ConfigName = "DWG To PDF.pc3"
    lay.RefreshPlotDeviceInfo()          # resets media/scale -> must precede them
    lay.CanonicalMediaName = MEDIA
    lay.PlotType = 1                     # acExtents
    lay.UseStandardScale = True
    lay.StandardScale = 0                # acScaleToFit
    lay.CenterPlot = True
    lay.PlotRotation = 0
    # Apply the plot style table. Without it the ACI colours print literally --
    # pale yellow room names, near-invisible light-grey furniture. The CTB maps
    # every colour to black at its assigned lineweight, which is the whole
    # point of the hierarchy.
    try:
        lay.StyleSheet = "PLAN-MONO.ctb"
    except Exception as exc:
        print("   stylesheet warning:", str(exc)[:60])
    doc.SetVariable("BACKGROUNDPLOT", 0)
    doc.Plot.PlotToFile(pdf, "DWG To PDF.pc3")
    return pdf, str(lay.StyleSheet)

for n in SHEETS:
    for _ in range(8):
        try:
            pdf, media = plot(n)
            print(f"{n:16s} OK  ctb={media:22s} {os.path.getsize(pdf)//1024} KB")
            break
        except Exception as exc:
            if not busy(exc):
                print(f"{n:16s} ERROR {str(exc)[:80]}"); break
            time.sleep(2.5)
