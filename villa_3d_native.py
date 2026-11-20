"""Build the villa as NATIVE AutoCAD 3D solids.

AutoCAD's STEP import produced nothing, so instead of importing we replay the
geometry we already own. build123d does the 2D boolean it is good at (offsetting
the comb footprint to get a correct wall ring with no doubled junctions);
AutoCAD does the extrude and the 3D booleans, giving real AcDb3dSolid entities.

Documents are tracked BY NAME throughout. SendCommand and long operations
invalidate COM proxies, and trusting ActiveDocument after one of those is how
the first-floor plan got overwritten.
"""

import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_3d as v3

pythoncom.CoInitialize()

OUT = v3.OUT
DWG = os.path.join(OUT, "VILLA_3D_MODEL.dwg")


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def dbl(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])


def objs(items):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(items))


def boundary_rings(rects, inset):
    """Outer and inner boundary vertex lists for a comb footprint, via
    build123d. Offsetting the MERGED face is what avoids the doubled wall at
    every wing/bar junction."""
    from build123d import Rectangle, Pos, offset, Kind
    fp = None
    for x0, y0, x1, y1 in rects:
        r = Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)
        fp = r if fp is None else fp + r
    inner = offset(fp, -inset, kind=Kind.INTERSECTION)

    def ring(face_sketch):
        f = face_sketch.faces()[0]
        return [(v.X, v.Y) for v in f.outer_wire().vertices()]
    return ring(fp), ring(inner)


def ordered(vs):
    """Vertices come back unordered; walk them by angle about the centroid.
    Safe here because both boundaries are convex-ish comb outlines traced in
    one loop."""
    cx = sum(v[0] for v in vs) / len(vs)
    cy = sum(v[1] for v in vs) / len(vs)
    import math
    return sorted(vs, key=lambda v: math.atan2(v[1] - cy, v[0] - cx))


def region_from(ms, pts):
    flat = []
    for x, y in pts:
        flat += [x, y]
    pl = ms.AddLightWeightPolyline(dbl(flat))
    pl.Closed = True
    regs = ms.AddRegion(objs([pl]))
    return regs[0]


def prism(ms, rects, inset, z0, z1):
    """Wall ring between z0 and z1 as one solid."""
    outer, inner = boundary_rings(rects, inset)
    ro = region_from(ms, ordered(outer))
    ri = region_from(ms, ordered(inner))
    so = ms.AddExtrudedSolid(ro, z1 - z0, 0.0)
    si = ms.AddExtrudedSolid(ri, z1 - z0, 0.0)
    so.Move(pt(0, 0, 0), pt(0, 0, z0))
    si.Move(pt(0, 0, 0), pt(0, 0, z0))
    so.Boolean(2, si)                      # 2 = acSubtraction
    return so


def box(ms, x0, y0, z0, x1, y1, z1):
    return ms.AddBox(pt((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                     abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def get_doc(app, name):
    for i in range(app.Documents.Count):
        d = app.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def run():
    app = w.GetActiveObject("AutoCAD.Application")
    old = get_doc(app, os.path.basename(DWG))
    if old is not None:
        old.Close(False)

    app = w.GetActiveObject("AutoCAD.Application")
    app.Documents.Add()
    doc = app.ActiveDocument
    created_name = str(doc.Name)          # remember it; never trust ActiveDocument later
    doc.SetVariable("INSUNITS", 4)
    ms = doc.ModelSpace
    t0 = time.perf_counter()

    solids, voids = [], []

    # ---- envelopes -----------------------------------------------------
    GF_FOOT = ((v3.HX0, v3.NB_Y0, v3.HX1, v3.NB_Y1),
               (v3.WW_X0, v3.WG_Y0, v3.WW_X1, v3.WG_Y1),
               (v3.EW_X0, v3.WG_Y0, v3.EW_X1, v3.WG_Y1),
               (v3.LV_X0, v3.WG_Y0, v3.LV_X1, v3.WG_Y1))
    FF_FOOT = ((v3.HX0, v3.NB_Y0, v3.HX1, v3.NB_Y1),
               (v3.WW_X0, v3.WG_Y0, v3.WW_X1, v3.WG_Y1),
               (v3.EW_X0, v3.WG_Y0, v3.EW_X1, v3.WG_Y1))
    solids.append(prism(ms, GF_FOOT, v3.WALL, v3.GF, v3.GF + v3.GF_CH))
    solids.append(prism(ms, FF_FOOT, v3.WALL, v3.FF, v3.RF))
    print(f"  envelopes  {time.perf_counter() - t0:.1f}s")

    # ---- slabs, roof, parapet, pavilion --------------------------------
    for x0, y0, x1, y1 in GF_FOOT:
        solids.append(box(ms, x0, y0, v3.GF - v3.SLAB, x1, y1, v3.GF))
    for x0, y0, x1, y1 in FF_FOOT:
        solids.append(box(ms, x0, y0, v3.GF + v3.GF_CH, x1, y1, v3.FF))
    solids.append(box(ms, v3.HX0, v3.WG_Y0 - v3.CANT, v3.RF,
                      v3.HX1, v3.NB_Y1, v3.RF + v3.SLAB))
    solids.append(box(ms, v3.PV[0], v3.PV[1], v3.RF + v3.SLAB,
                      v3.PV[2], v3.PV[3], v3.RF + v3.SLAB + v3.PAV_CH))
    voids.append(box(ms, v3.PV[0] + 250, v3.PV[1] + 250, v3.RF + v3.SLAB,
                     v3.PV[2] - 250, v3.PV[3] - 250, v3.RF + v3.SLAB + v3.PAV_CH))

    # ---- cantilever ----------------------------------------------------
    solids.append(box(ms, v3.LV_X0, v3.WG_Y0 - v3.CANT, v3.GF + v3.GF_CH,
                      v3.LV_X1, v3.WG_Y0, v3.RF + v3.SLAB))

    # ---- pool, basin, rill ---------------------------------------------
    solids.append(box(ms, v3.POOL_X0 - 400, v3.POOL_Y0 - 400, v3.POOL_FL - 400,
                      v3.POOL_X1 + 400, v3.POOL_Y1 + 400, v3.POOL_TW))
    voids.append(box(ms, v3.POOL_X0, v3.POOL_Y0, v3.POOL_FL,
                     v3.POOL_X1, v3.POOL_Y1, v3.POOL_TW + 100))
    voids.append(box(ms, v3.POOL_X0 - 400, v3.POOL_Y0 - 1400, -v3.BASIN_D,
                     v3.POOL_X1 + 400, v3.POOL_Y0 - 400, v3.POOL_TW - 60))

    # ---- boundary wall + gates -----------------------------------------
    BW, BH = 350.0, 2400.0
    for x0, y0, x1, y1 in ((0, 0, v3.PLOT_W, BW),
                           (0, v3.PLOT_D - BW, v3.PLOT_W, v3.PLOT_D),
                           (0, 0, BW, v3.PLOT_D),
                           (v3.PLOT_W - BW, 0, v3.PLOT_W, v3.PLOT_D)):
        solids.append(box(ms, x0, y0, 0, x1, y1, BH))
    voids.append(box(ms, 3800, v3.PLOT_D - BW - 200, 0, 8300, v3.PLOT_D + 200, BH))
    voids.append(box(ms, 15400, v3.PLOT_D - BW - 200, 0, 16600, v3.PLOT_D + 200, 2200))

    # ---- west brise-soleil ---------------------------------------------
    for i in range(9):
        yy = v3.WG_Y0 + 300 + i * 600
        solids.append(box(ms, v3.HX0 - 700, yy, v3.GF,
                          v3.HX0 - 250, yy + 180, v3.RF))

    print(f"  {len(solids)} solids, {len(voids)} voids created  "
          f"{time.perf_counter() - t0:.1f}s")

    base = solids[0]
    for s in solids[1:]:
        base.Boolean(0, s)                 # 0 = acUnion
    for v in voids:
        base.Boolean(2, v)                 # 2 = acSubtraction
    print(f"  booleans done  {time.perf_counter() - t0:.1f}s")

    app = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(app, created_name)       # by NAME, never ActiveDocument
    n3d = sum(1 for e in doc.ModelSpace if str(e.ObjectName) == "AcDb3dSolid")
    total = int(doc.ModelSpace.Count)
    doc.SaveAs(DWG)
    try:
        vp = doc.ActiveViewport
        vp.Direction = pt(-1, -1, 1)
        doc.ActiveViewport = vp
        doc.SendCommand("_.VSCURRENT\n_Shaded\n_.ZOOM\n_E\n")
    except Exception as exc:
        print("  view warning:", str(exc)[:60])
    print(f"\n{total} entities, {n3d} 3D solids -> {os.path.basename(DWG)}")


if __name__ == "__main__":
    last = None
    for attempt in range(8):
        try:
            run()
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy, retrying ({attempt + 1})...")
            time.sleep(4)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
