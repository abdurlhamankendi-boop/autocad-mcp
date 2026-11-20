"""Re-plot generated DWGs to A3 landscape PDF, verifying each setting sticks."""
import os, pythoncom, win32com.client as w
pythoncom.CoInitialize()
app = w.GetActiveObject("AutoCAD.Application")
OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
MEDIA = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"

for i in range(app.Documents.Count - 1, -1, -1):
    d = app.Documents.Item(i)
    if OUT.lower() in str(d.FullName).lower():
        d.Close(False)

for f in sorted(os.listdir(OUT)):
    if not f.endswith(".dwg"):
        continue
    # Closing a document invalidates the cached Documents proxy
    # ("AttributeError: <unknown>.Open"), so re-acquire it each pass.
    app = w.GetActiveObject("AutoCAD.Application")
    doc = app.Documents.Open(os.path.join(OUT, f))
    doc.Activate()
    app.ZoomExtents()                     # make acDisplay a safe fallback too
    lay = doc.ActiveLayout
    lay.ConfigName = "DWG To PDF.pc3"
    lay.RefreshPlotDeviceInfo()
    lay.CanonicalMediaName = MEDIA
    lay.PlotType = 1                      # acExtents
    lay.UseStandardScale = True
    lay.StandardScale = 0                 # acScaleToFit
    lay.CenterPlot = True
    lay.PlotRotation = 0
    lay.RefreshPlotDeviceInfo()           # commit
    # read back what actually took
    got = (str(lay.CanonicalMediaName), int(lay.PlotType),
           bool(lay.UseStandardScale), int(lay.StandardScale),
           int(lay.PlotRotation))
    doc.SetVariable("BACKGROUNDPLOT", 0)
    pdf = os.path.join(OUT, f[:-4] + ".pdf")
    try:
        doc.Plot.PlotToFile(pdf, "DWG To PDF.pc3")
        ok = True
    except Exception as e:
        ok = False
        print("   plot error:", e)
    print(f"{f[:34]:36s} media={got[0][:28]:30s} type={got[1]} std={got[2]}/{got[3]} rot={got[4]} ok={ok}")
    doc.Close(False)
