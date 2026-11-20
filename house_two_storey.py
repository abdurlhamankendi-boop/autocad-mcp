"""
Two-storey dwelling: 2D plan set (ground + first) and a 3D solid model.

Millimetres, drawn 1:1 in model space. Plans plot 1:100 @ A3.
Each output goes into its own new drawing, so nothing already open is touched.

Run:  python house_two_storey.py
"""

import math
import os

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

pythoncom.CoInitialize()
APP = w.GetActiveObject("AutoCAD.Application")

OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- constants
W, H = 12000.0, 9000.0        # envelope
EXT, INT = 200.0, 100.0       # wall thicknesses
CH_G, CH_F = 2700.0, 2600.0   # clear ceiling heights, ground / first
SLAB = 250.0                  # floor slab

LAYERS = {
    "A-WALL": 7, "A-WALL-PATT": 8, "A-DOOR": 3, "A-GLAZ": 4,
    "A-STRS": 5, "A-ANNO-TEXT": 2, "A-ANNO-DIMS": 1,
    "A-ANNO-TTLB": 7, "A-ANNO-NORT": 6, "A-SLAB": 8, "A-ROOF": 33,
}


def P(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x), float(y), float(z)])


def arr(v):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(i) for i in v])


def disp(objs):
    """AppendOuterLoop and friends reject plain lists -- they need VT_DISPATCH."""
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(objs))


def spans(a, b, openings):
    """Split the run a..b around `openings` [(s, e), ...]; returns solid pieces."""
    out, cur = [], a
    for s, e in sorted(openings):
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < b:
        out.append((cur, b))
    return out


class Sheet:
    """One drawing plus the helpers used to populate it."""

    def __init__(self, title):
        # Documents.Add() sometimes hands back a late-bound proxy with no type
        # information, so every attribute access on it raises
        # "AttributeError: Add.<name>". Re-fetching the new document through
        # ActiveDocument returns a properly resolved object.
        APP.Documents.Add()
        self.doc = APP.ActiveDocument
        self.ms = self.doc.ModelSpace
        self.title = title
        for name, color in LAYERS.items():
            self.doc.Layers.Add(name).Color = color
        for var, val in (("DIMTXT", 250.0), ("DIMASZ", 150.0), ("DIMEXE", 100.0),
                         ("DIMEXO", 150.0), ("DIMDEC", 0), ("DIMTIH", 0)):
            try:
                self.doc.SetVariable(var, val)
            except Exception:
                pass

    # -- 2D primitives ---------------------------------------------------
    def rect(self, x1, y1, x2, y2, layer, poche=False):
        pl = self.ms.AddLightWeightPolyline(arr([x1, y1, x2, y1, x2, y2, x1, y2]))
        pl.Closed = True
        pl.Layer = layer
        if poche:
            try:
                h = self.ms.AddHatch(0, "SOLID", True)
                h.AppendOuterLoop(disp([pl]))
                h.Evaluate()
                h.Layer = "A-WALL-PATT"
            except Exception:
                pass
        return pl

    def line(self, x1, y1, x2, y2, layer):
        ln = self.ms.AddLine(P(x1, y1), P(x2, y2))
        ln.Layer = layer
        return ln

    def text(self, s, x, y, h, layer, centre=False):
        t = self.ms.AddText(s, P(x, y), h)
        t.Layer = layer
        if centre:
            try:
                t.Alignment = 1
                t.TextAlignmentPoint = P(x, y)
            except Exception:
                pass
        return t

    def door(self, hx, hy, width, facing, hinge="left"):
        a = math.radians(facing)
        self.line(hx, hy, hx + width * math.cos(a), hy + width * math.sin(a), "A-DOOR")
        sweep = math.radians(-90 if hinge == "left" else 90)
        arc = self.ms.AddArc(P(hx, hy), width, min(a, a + sweep), max(a, a + sweep))
        arc.Layer = "A-DOOR"

    def window(self, x1, y1, x2, y2, horizontal=True):
        if horizontal:
            for f in (0.0, 0.5, 1.0):
                y = y1 + (y2 - y1) * f
                self.line(x1, y, x2, y, "A-GLAZ")
            self.line(x1, y1, x1, y2, "A-GLAZ")
            self.line(x2, y1, x2, y2, "A-GLAZ")
        else:
            for f in (0.0, 0.5, 1.0):
                x = x1 + (x2 - x1) * f
                self.line(x, y1, x, y2, "A-GLAZ")
            self.line(x1, y1, x2, y1, "A-GLAZ")
            self.line(x1, y2, x2, y2, "A-GLAZ")

    def stair(self, x1, y1, x2, y2, treads, up_text="UP"):
        """Straight flight drawn as tread lines with a direction arrow."""
        self.rect(x1, y1, x2, y2, "A-STRS")
        depth = (y2 - y1) / treads
        for i in range(1, treads):
            self.line(x1, y1 + i * depth, x2, y1 + i * depth, "A-STRS")
        cx = (x1 + x2) / 2
        self.line(cx, y1 + depth * 0.5, cx, y2 - depth * 0.5, "A-STRS")
        head = y2 - depth * 0.5
        self.line(cx, head, cx - 120, head - 200, "A-STRS")
        self.line(cx, head, cx + 120, head - 200, "A-STRS")
        self.text(up_text, x2 + 150, (y1 + y2) / 2, 200, "A-ANNO-TEXT")

    def dim_h(self, x1, x2, y, offset):
        d = self.ms.AddDimRotated(P(x1, y), P(x2, y), P((x1 + x2) / 2, y - offset), 0.0)
        d.Layer = "A-ANNO-DIMS"

    def dim_v(self, y1, y2, x, offset):
        d = self.ms.AddDimRotated(P(x, y1), P(x, y2), P(x - offset, (y1 + y2) / 2),
                                  math.radians(90))
        d.Layer = "A-ANNO-DIMS"

    def north_arrow(self, nx=13800.0, ny=8000.0, r=500.0):
        c = self.ms.AddCircle(P(nx, ny), r)
        c.Layer = "A-ANNO-NORT"
        tip = self.ms.AddLightWeightPolyline(
            arr([nx, ny + r, nx - r * .35, ny - r * .5, nx, ny - r * .2,
                 nx + r * .35, ny - r * .5]))
        tip.Closed = True
        tip.Layer = "A-ANNO-NORT"
        self.text("N", nx, ny + r + 200, 300, "A-ANNO-NORT", centre=True)

    def title_block(self, sheet_no, sheet_name, gia=None, scale="1:100 @ A3"):
        x, y, bw, bh = 0.0, -4400.0, 15000.0, 2400.0
        self.rect(x, y, x + bw, y + bh, "A-ANNO-TTLB")
        self.line(x, y + 1600, x + bw, y + 1600, "A-ANNO-TTLB")
        self.line(x + 9000, y, x + 9000, y + 1600, "A-ANNO-TTLB")
        self.line(x + 12000, y, x + 12000, y + 1600, "A-ANNO-TTLB")
        self.text("TWO-STOREY RESIDENTIAL DWELLING", x + 300, y + 1900, 450,
                  "A-ANNO-TTLB")
        self.text(sheet_name, x + 300, y + 1000, 280, "A-ANNO-TTLB")
        self.text("ALL DIMENSIONS IN MILLIMETRES. DO NOT SCALE FROM DRAWING.",
                  x + 300, y + 500, 200, "A-ANNO-TTLB")
        if gia is not None:
            self.text(f"GROSS INTERNAL AREA: {gia:.2f} m2", x + 300, y + 150, 200,
                      "A-ANNO-TTLB")
        self.text(f"SCALE  {scale}", x + 9300, y + 1000, 250, "A-ANNO-TTLB")
        self.text("DATE   2026-09-06", x + 9300, y + 500, 250, "A-ANNO-TTLB")
        self.text(f"DWG    {sheet_no}", x + 12300, y + 1000, 250, "A-ANNO-TTLB")
        self.text("REV    A", x + 12300, y + 500, 250, "A-ANNO-TTLB")

    # -- 3D primitives ---------------------------------------------------
    def box(self, x1, y1, x2, y2, z0, z1, layer):
        cx, cy, cz = (x1 + x2) / 2, (y1 + y2) / 2, (z0 + z1) / 2
        b = self.ms.AddBox(P(cx, cy, cz), abs(x2 - x1), abs(y2 - y1), abs(z1 - z0))
        b.Layer = layer
        return b

    def save_and_plot(self, basename):
        dwg = os.path.join(OUT, basename + ".dwg")
        pdf = os.path.join(OUT, basename + ".pdf")
        self.doc.SaveAs(dwg)
        lay = self.doc.ActiveLayout
        try:
            # Order matters. RefreshPlotDeviceInfo() resets media/scale/type to
            # the device defaults, so it must run straight after ConfigName --
            # calling it last silently discards everything set before it, which
            # leaves PlotType on acDisplay and plots the current screen view.
            lay.ConfigName = "DWG To PDF.pc3"
            lay.RefreshPlotDeviceInfo()
            lay.CanonicalMediaName = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
            lay.PlotType = 1            # acExtents
            lay.UseStandardScale = True
            lay.StandardScale = 0       # acScaleToFit
            lay.CenterPlot = True
            lay.PlotRotation = 0        # media is already 420 x 297 landscape
            if str(lay.CanonicalMediaName).upper().find("A3") < 0:
                print("   media did not stick:", lay.CanonicalMediaName)
        except Exception as exc:
            print("   layout warning:", exc)
        self.doc.SetVariable("BACKGROUNDPLOT", 0)
        try:
            self.doc.Plot.PlotToFile(pdf, "DWG To PDF.pc3")
        except Exception as exc:
            print("   plot failed:", exc)
        APP.ZoomExtents()
        return dwg, pdf, os.path.exists(pdf)


# ============================================================ FLOOR DATA
# Central hall/stair spine runs north-south at x 5200..7200.
HALL_W1, HALL_W2 = 5200.0, 7200.0
STAIR = (5400.0, 4000.0, 6300.0, 7250.0)   # 900 wide, 13 treads

GROUND = {
    "name": "GROUND FLOOR PLAN",
    "sheet": "A-101",
    # exterior openings, per face
    "south_open": [(5500, 6500), (1200, 3400), (8200, 10200)],   # door + 2 windows
    "north_open": [(1500, 3500), (8500, 10500)],
    "west_open":  [(1500, 3500), (5800, 7800)],
    "east_open":  [(900, 2900), (6200, 8000)],
    # windows only (the door is drawn separately)
    "south_win":  [(1200, 3400), (8200, 10200)],
    "north_win":  [(1500, 3500), (8500, 10500)],
    "west_win":   [(1500, 3500), (5800, 7800)],
    "east_win":   [(900, 2900), (6200, 8000)],
    "partitions": [
        (HALL_W1, EXT, HALL_W1 + INT, H - EXT),      # hall west wall
        (HALL_W2, EXT, HALL_W2 + INT, H - EXT),      # hall east wall
        (EXT, 5000, HALL_W1, 5100),                  # living | kitchen
        (HALL_W2 + INT, 4000, W - EXT, 4100),        # study | wc
        (HALL_W2 + INT, 5600, W - EXT, 5700),        # wc | utility
    ],
    "part_open": [
        (HALL_W1, 1800, HALL_W1 + INT, 2700),        # living -> hall
        (HALL_W1, 6200, HALL_W1 + INT, 7100),        # kitchen -> hall
        (HALL_W2, 1500, HALL_W2 + INT, 2400),        # hall -> study
        (HALL_W2, 4500, HALL_W2 + INT, 5300),        # hall -> wc
        (HALL_W2, 6600, HALL_W2 + INT, 7500),        # hall -> utility
    ],
    "doors": [
        (5500, EXT, 1000, 90),        # entrance
        (1800, 5000, 900, 90),        # living/kitchen
        (HALL_W1 + INT, 1800, 900, 0),
        (HALL_W1 + INT, 6200, 900, 0),
        (HALL_W2, 1500, 900, 180),
        (HALL_W2, 4500, 800, 180),
        (HALL_W2, 6600, 900, 180),
    ],
    "rooms": [
        ("LIVING",        2700, 2600, 5.00 * 4.80),
        ("KITCHEN/DINING", 2700, 6900, 5.00 * 3.70),
        ("HALL",          6200, 2000, 2.00 * 8.60),
        ("STUDY",         9500, 2100, 4.60 * 3.80),
        ("WC",            9500, 4850, 4.60 * 1.50),
        ("UTILITY",       9500, 7250, 4.60 * 3.10),
    ],
    "stair_text": "UP",
}

FIRST = {
    "name": "FIRST FLOOR PLAN",
    "sheet": "A-102",
    "south_open": [(1200, 3400), (8200, 10200)],
    "north_open": [(1500, 3500), (8500, 10500)],
    "west_open":  [(1500, 3500), (5800, 7800)],
    "east_open":  [(900, 2900), (6200, 8000)],
    "south_win":  [(1200, 3400), (8200, 10200)],
    "north_win":  [(1500, 3500), (8500, 10500)],
    "west_win":   [(1500, 3500), (5800, 7800)],
    "east_win":   [(900, 2900), (6200, 8000)],
    "partitions": [
        (HALL_W1, EXT, HALL_W1 + INT, H - EXT),
        (HALL_W2, EXT, HALL_W2 + INT, H - EXT),
        (EXT, 4400, HALL_W1, 4500),                  # bed2 | bed1
        (HALL_W2 + INT, 4000, W - EXT, 4100),        # bed3 | bath
        (HALL_W2 + INT, 6000, W - EXT, 6100),        # bath | bed4
    ],
    "part_open": [
        (HALL_W1, 2000, HALL_W1 + INT, 2900),
        (HALL_W1, 6000, HALL_W1 + INT, 6900),
        (HALL_W2, 1500, HALL_W2 + INT, 2400),
        (HALL_W2, 4600, HALL_W2 + INT, 5400),
        (HALL_W2, 6800, HALL_W2 + INT, 7700),
    ],
    "doors": [
        (2000, 4400, 900, 90),
        (HALL_W1 + INT, 2000, 900, 0),
        (HALL_W1 + INT, 6000, 900, 0),
        (HALL_W2, 1500, 900, 180),
        (HALL_W2, 4600, 800, 180),
        (HALL_W2, 6800, 900, 180),
    ],
    "rooms": [
        ("BEDROOM 2",   2700, 2200, 5.00 * 4.20),
        ("BEDROOM 1",   2700, 6800, 5.00 * 4.30),
        ("LANDING",     6200, 2200, 2.00 * 8.60),
        ("BEDROOM 3",   9500, 2100, 4.60 * 3.80),
        ("BATHROOM",    9500, 5050, 4.60 * 1.90),
        ("BEDROOM 4",   9500, 7400, 4.60 * 2.70),
    ],
    "stair_text": "DN",
}


def build_walls(sh, spec, poche=True):
    """Exterior + internal walls with their openings. Returns wall rects."""
    rects = []
    for x1, x2 in spans(0, W, spec["south_open"]):
        rects.append(sh.rect(x1, 0, x2, EXT, "A-WALL", poche))
    for x1, x2 in spans(0, W, spec["north_open"]):
        rects.append(sh.rect(x1, H - EXT, x2, H, "A-WALL", poche))
    for y1, y2 in spans(0, H, spec["west_open"]):
        rects.append(sh.rect(0, y1, EXT, y2, "A-WALL", poche))
    for y1, y2 in spans(0, H, spec["east_open"]):
        rects.append(sh.rect(W - EXT, y1, W, y2, "A-WALL", poche))

    for (px1, py1, px2, py2) in spec["partitions"]:
        vertical = (px2 - px1) < (py2 - py1)
        opens = []
        for (ox1, oy1, ox2, oy2) in spec["part_open"]:
            if vertical and abs(ox1 - px1) < 1 and py1 <= oy1 <= py2:
                opens.append((oy1, oy2))
            elif not vertical and abs(oy1 - py1) < 1 and px1 <= ox1 <= px2:
                opens.append((ox1, ox2))
        if vertical:
            for a, b in spans(py1, py2, opens):
                rects.append(sh.rect(px1, a, px2, b, "A-WALL", poche))
        else:
            for a, b in spans(px1, px2, opens):
                rects.append(sh.rect(a, py1, b, py2, "A-WALL", poche))
    return rects


def draw_plan(spec):
    sh = Sheet(spec["name"])
    build_walls(sh, spec, poche=True)

    for (hx, hy, wd, facing) in spec["doors"]:
        sh.door(hx, hy, wd, facing)

    for x1, x2 in spec["south_win"]:
        sh.window(x1, 0, x2, EXT)
    for x1, x2 in spec["north_win"]:
        sh.window(x1, H - EXT, x2, H)
    for y1, y2 in spec["west_win"]:
        sh.window(0, y1, EXT, y2, horizontal=False)
    for y1, y2 in spec["east_win"]:
        sh.window(W - EXT, y1, W, y2, horizontal=False)

    sh.stair(*STAIR, treads=13, up_text=spec["stair_text"])

    gia = 0.0
    for name, cx, cy, area in spec["rooms"]:
        sh.text(name, cx, cy, 300, "A-ANNO-TEXT", centre=True)
        sh.text(f"{area:.2f} m2", cx, cy - 450, 200, "A-ANNO-TEXT", centre=True)
        gia += area

    for a, b in [(0, HALL_W1), (HALL_W1, HALL_W2 + INT), (HALL_W2 + INT, W)]:
        sh.dim_h(a, b, 0, 900)
    sh.dim_h(0, W, 0, 1900)
    for a, b in [(0, H / 2), (H / 2, H)]:
        sh.dim_v(a, b, 0, 900)
    sh.dim_v(0, H, 0, 1900)

    sh.north_arrow()
    sh.title_block(spec["sheet"], spec["name"], gia)
    return sh, gia


def draw_model_3d():
    """Solid model: slabs, both storeys of walls, and a hipped-ish roof mass."""
    sh = Sheet("3D MODEL")
    z = 0.0
    sh.box(0, 0, W, H, z - SLAB, z, "A-SLAB")                       # ground slab

    for spec, base, ch in ((GROUND, 0.0, CH_G), (FIRST, CH_G + SLAB, CH_F)):
        if base > 0:
            sh.box(0, 0, W, H, base - SLAB, base, "A-SLAB")         # upper slab
        for x1, x2 in spans(0, W, spec["south_open"]):
            sh.box(x1, 0, x2, EXT, base, base + ch, "A-WALL")
        for x1, x2 in spans(0, W, spec["north_open"]):
            sh.box(x1, H - EXT, x2, H, base, base + ch, "A-WALL")
        for y1, y2 in spans(0, H, spec["west_open"]):
            sh.box(0, y1, EXT, y2, base, base + ch, "A-WALL")
        for y1, y2 in spans(0, H, spec["east_open"]):
            sh.box(W - EXT, y1, W, y2, base, base + ch, "A-WALL")
        # lintels over the openings so the model reads as a solid shell
        for x1, x2 in spec["south_open"]:
            sh.box(x1, 0, x2, EXT, base + 2100, base + ch, "A-WALL")
        for x1, x2 in spec["north_open"]:
            sh.box(x1, H - EXT, x2, H, base + 2100, base + ch, "A-WALL")
        for y1, y2 in spec["west_open"]:
            sh.box(0, y1, EXT, y2, base + 2100, base + ch, "A-WALL")
        for y1, y2 in spec["east_open"]:
            sh.box(W - EXT, y1, W, y2, base + 2100, base + ch, "A-WALL")
        # internal partitions, full height
        for (px1, py1, px2, py2) in spec["partitions"]:
            sh.box(px1, py1, px2, py2, base, base + ch, "A-WALL")

    roof_base = CH_G + SLAB + CH_F
    sh.box(-300, -300, W + 300, H + 300, roof_base, roof_base + SLAB, "A-ROOF")
    sh.box(1500, 1500, W - 1500, H - 1500, roof_base + SLAB,
           roof_base + SLAB + 1200, "A-ROOF")

    sh.title_block("A-201", "3D MODEL - SOUTH WEST ISOMETRIC", scale="NTS")
    # Set the isometric view through the viewport object rather than
    # SendCommand -- SendCommand re-enters AutoCAD and invalidates the COM
    # document proxy, which made the following SaveAs fail with
    # "Add.ActiveLayout".
    try:
        vp = sh.doc.ActiveViewport
        vp.Direction = P(-1, -1, 1)
        sh.doc.ActiveViewport = vp
    except Exception as exc:
        print("   view warning:", exc)
    return sh


def close_generated():
    """AutoCAD cannot overwrite a drawing it still has open, so close any
    previously generated sheet. User drawings are never touched."""
    marker = OUT.lower()
    for i in range(APP.Documents.Count - 1, -1, -1):
        d = APP.Documents.Item(i)
        if marker in str(d.FullName).lower():
            d.Close(False)


if __name__ == "__main__":
    close_generated()
    results = []
    for spec in (GROUND, FIRST):
        sh, gia = draw_plan(spec)
        dwg, pdf, ok = sh.save_and_plot(f"{spec['sheet']}_{spec['name'].replace(' ', '_')}")
        print(f"{spec['sheet']}  entities={sh.ms.Count:4d}  GIA={gia:6.2f} m2  pdf={ok}")
        results.append((spec["sheet"], pdf, ok))

    sh3 = draw_model_3d()
    dwg, pdf, ok = sh3.save_and_plot("A-201_3D_Model")
    solids = sum(1 for e in sh3.ms if str(e.EntityName) == "AcDb3dSolid")
    print(f"A-201  entities={sh3.ms.Count:4d}  solids={solids}  pdf={ok}")
    results.append(("A-201", pdf, ok))

    print("\noutput folder:", OUT)
    for s, p, ok in results:
        print(f"  {s}  {'OK ' if ok else 'FAIL'}  {os.path.basename(p)}")
