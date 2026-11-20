"""
Two-storey dwelling - drawing set generator.

Outputs, all A3 landscape:
    A-101 / A-102   engineering plans   dimensioned, furnished, title block
    A-111 / A-112   client plans        furnished, areas, no dimension clutter
    A-201           3D solid model

Millimetres, 1:1 in model space, plotted 1:100.

Room areas and label positions are COMPUTED from the room rectangles rather
than hand-entered, so they cannot drift out of step with the geometry.
"""

import math
import os

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

pythoncom.CoInitialize()
# Late binding (a bare GetActiveObject) hands back dynamic proxies whose type
# info goes stale after Documents.Add()/Close(), producing errors like
# "AttributeError: <unknown>.ModelSpace" partway through a run. Building the
# typelib wrappers first makes GetActiveObject return a typed AcadApplication.
# AutoCAD is a single-instance server, so this attaches rather than launching.
w.gencache.EnsureDispatch("AutoCAD.Application")
APP = w.GetActiveObject("AutoCAD.Application")

OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
os.makedirs(OUT, exist_ok=True)

W, H = 12000.0, 9000.0
EXT, INT = 200.0, 100.0
CH_G, CH_F, SLAB = 2700.0, 2600.0, 250.0
HW1, HW2 = 5200.0, 7200.0          # hall walls (100 thick, so clear 5300..7200)
STAIR = (5400.0, 4000.0, 6300.0, 7250.0)

# AutoCAD's txt font renders roughly 0.8 * height per character. Used to keep
# title-block strings inside their columns instead of overprinting the next one.
CHAR_W = 0.8

LAYERS = {
    "A-WALL": 7, "A-WALL-PATT": 8, "A-DOOR": 3, "A-GLAZ": 4, "A-STRS": 5,
    "A-FURN": 32, "A-FURN-SANR": 130, "A-ANNO-TEXT": 2, "A-ANNO-DIMS": 1,
    "A-ANNO-TTLB": 7, "A-ANNO-NORT": 6, "A-SLAB": 8, "A-ROOF": 33,
}


def P(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x), float(y), float(z)])


def arr(v):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(i) for i in v])


def disp(objs):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(objs))


def spans(a, b, openings):
    out, cur = [], a
    for s, e in sorted(openings):
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < b:
        out.append((cur, b))
    return out


def text_w(s, h):
    return len(s) * h * CHAR_W


class Sheet:
    def __init__(self):
        self.doc = APP.Documents.Add()
        self.ms = self.doc.ModelSpace
        for name, color in LAYERS.items():
            self.doc.Layers.Add(name).Color = color

    # ---- 2D primitives -------------------------------------------------
    def rect(self, x1, y1, x2, y2, layer, poche=False):
        pl = self.ms.AddLightWeightPolyline(arr([x1, y1, x2, y1, x2, y2, x1, y2]))
        pl.Closed = True
        pl.Layer = layer
        if poche:
            try:
                h = self.ms.AddHatch(0, "SOLID", True)
                h.AppendOuterLoop(disp([pl]))   # a plain list is rejected
                h.Evaluate()
                h.Layer = "A-WALL-PATT"
            except Exception:
                pass
        return pl

    def line(self, x1, y1, x2, y2, layer):
        ln = self.ms.AddLine(P(x1, y1), P(x2, y2))
        ln.Layer = layer
        return ln

    def circle(self, cx, cy, r, layer):
        c = self.ms.AddCircle(P(cx, cy), r)
        c.Layer = layer
        return c

    def arc(self, cx, cy, r, a0, a1, layer):
        a = self.ms.AddArc(P(cx, cy), r, math.radians(a0), math.radians(a1))
        a.Layer = layer
        return a

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

    def bbox(self, ent):
        lo, hi = ent.GetBoundingBox()
        return (lo[0], lo[1], hi[0], hi[1])

    def fit_text(self, s, x, y, h, layer, max_w, centre=False):
        """Draw text, then shrink it until its REAL bounding box fits max_w.
        Rendered width depends on the text style, so estimating characters
        times height overruns and overprints the next column."""
        t = self.text(s, x, y, h, layer, centre)
        for _ in range(14):
            x0, _y0, x1, _y1 = self.bbox(t)
            if (x1 - x0) <= max_w or h <= 90:
                break
            h *= 0.90
            t.Height = h
        return t

    def door(self, hx, hy, width, facing, hinge="left"):
        a = math.radians(facing)
        self.line(hx, hy, hx + width * math.cos(a), hy + width * math.sin(a), "A-DOOR")
        sweep = math.radians(-90 if hinge == "left" else 90)
        self.arc(hx, hy, width, math.degrees(min(a, a + sweep)),
                 math.degrees(max(a, a + sweep)), "A-DOOR")

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

    def stair(self, treads=13, up_text="UP"):
        x1, y1, x2, y2 = STAIR
        self.rect(x1, y1, x2, y2, "A-STRS")
        d = (y2 - y1) / treads
        for i in range(1, treads):
            self.line(x1, y1 + i * d, x2, y1 + i * d, "A-STRS")
        cx = (x1 + x2) / 2
        self.line(cx, y1 + d * .5, cx, y2 - d * .5, "A-STRS")
        head = y2 - d * .5
        self.line(cx, head, cx - 120, head - 200, "A-STRS")
        self.line(cx, head, cx + 120, head - 200, "A-STRS")
        self.text(up_text, x2 + 120, (y1 + y2) / 2, 180, "A-ANNO-TEXT")

    # ---- dimensions ----------------------------------------------------
    def _style_dim(self, d):
        """New dimensions inherit the ACTIVE DIM STYLE (ISO-25, 2.5mm text),
        not the DIM* system variables -- at 1:100 that is invisible. Set the
        sizes on the entity so they override the style."""
        d.Layer = "A-ANNO-DIMS"
        for prop, val in (("TextHeight", 250.0), ("ArrowheadSize", 150.0),
                          ("ExtensionLineExtend", 100.0),
                          ("ExtensionLineOffset", 150.0)):
            try:
                setattr(d, prop, val)
            except Exception:
                pass
        try:
            d.PrimaryUnitsPrecision = 0
        except Exception:
            pass

    def dim_h(self, x1, x2, y, off):
        self._style_dim(self.ms.AddDimRotated(P(x1, y), P(x2, y),
                                              P((x1 + x2) / 2, y - off), 0.0))

    def dim_v(self, y1, y2, x, off):
        self._style_dim(self.ms.AddDimRotated(P(x, y1), P(x, y2),
                                              P(x - off, (y1 + y2) / 2),
                                              math.radians(90)))

    # ---- sheet furniture -----------------------------------------------
    def north_arrow(self, nx=13600.0, ny=7800.0, r=450.0):
        self.circle(nx, ny, r, "A-ANNO-NORT")
        t = self.ms.AddLightWeightPolyline(
            arr([nx, ny + r, nx - r * .35, ny - r * .5, nx, ny - r * .2,
                 nx + r * .35, ny - r * .5]))
        t.Closed = True
        t.Layer = "A-ANNO-NORT"
        self.text("N", nx, ny + r + 180, 260, "A-ANNO-NORT", centre=True)

    def title_block(self, sheet_no, sheet_name, gia, scale="1:100 @ A3"):
        """Three columns with the text sized to fit. Earlier versions used
        250-450mm text in 3000mm columns, which overran and overprinted."""
        X, Y, BW, BH = 0.0, -4600.0, 15000.0, 2600.0
        C1, C2 = 8000.0, 11400.0
        self.rect(X, Y, X + BW, Y + BH, "A-ANNO-TTLB")
        self.line(X, Y + 1700, X + BW, Y + 1700, "A-ANNO-TTLB")
        for cx in (C1, C2):
            self.line(X + cx, Y, X + cx, Y + 1700, "A-ANNO-TTLB")

        self.fit_text("TWO-STOREY RESIDENTIAL DWELLING", X + 250, Y + 2000, 380,
                      "A-ANNO-TTLB", BW - 500)
        self.fit_text(sheet_name, X + 250, Y + 1150, 260, "A-ANNO-TTLB", C1 - 500)
        self.fit_text("ALL DIMENSIONS IN MILLIMETRES. DO NOT SCALE FROM DRAWING.",
                      X + 250, Y + 700, 150, "A-ANNO-TTLB", C1 - 500)
        self.fit_text(f"GROSS INTERNAL AREA  {gia:.2f} m2", X + 250, Y + 300, 150,
                      "A-ANNO-TTLB", C1 - 500)

        fields = [(C1, C2 - C1, [f"SCALE  {scale}", "DATE   2026-09-06"]),
                  (C2, BW - C2, [f"DWG    {sheet_no}", "REV    A"])]
        for cx, width, rows in fields:
            for i, s in enumerate(rows):
                self.fit_text(s, X + cx + 250, Y + 1150 - i * 600, 200,
                              "A-ANNO-TTLB", width - 500)

    # ---- 3D ------------------------------------------------------------
    def box(self, x1, y1, x2, y2, z0, z1, layer):
        b = self.ms.AddBox(P((x1 + x2) / 2, (y1 + y2) / 2, (z0 + z1) / 2),
                           abs(x2 - x1), abs(y2 - y1), abs(z1 - z0))
        b.Layer = layer
        return b

    # ---- output --------------------------------------------------------
    def save_and_plot(self, basename):
        dwg = os.path.join(OUT, basename + ".dwg")
        pdf = os.path.join(OUT, basename + ".pdf")
        self.doc.SaveAs(dwg)
        # Plot settings apply to the ACTIVE document; configuring a background
        # one silently plots the wrong view. Zoom too, so that even if PlotType
        # falls back to acDisplay the fallback frames the whole drawing.
        self.doc.Activate()
        APP.ZoomExtents()
        lay = self.doc.ActiveLayout
        try:
            # RefreshPlotDeviceInfo() resets media/scale/type to device
            # defaults, so it must run right after ConfigName -- calling it
            # last silently reverts PlotType to acDisplay and plots the screen.
            lay.ConfigName = "DWG To PDF.pc3"
            lay.RefreshPlotDeviceInfo()
            lay.CanonicalMediaName = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
            lay.PlotType = 1
            lay.UseStandardScale = True
            lay.StandardScale = 0
            lay.CenterPlot = True
            lay.PlotRotation = 0
        except Exception as exc:
            print("   layout warning:", exc)
        self.doc.SetVariable("BACKGROUNDPLOT", 0)
        try:
            self.doc.Plot.PlotToFile(pdf, "DWG To PDF.pc3")
        except Exception as exc:
            print("   plot failed:", exc)
        return pdf, os.path.exists(pdf)


# ==================================================== ROOMS (x1,y1,x2,y2)
# Clear internal rectangles. Areas and label anchors derive from these.
GROUND_ROOMS = [
    ("LIVING",         200,  200, HW1,   5000),
    ("KITCHEN/DINING", 200, 5100, HW1,   8800),
    ("HALL",       HW1 + INT,  200, HW2,  8800),
    ("STUDY",      HW2 + INT,  200, 11800, 4000),
    ("WC",         HW2 + INT, 4100, 11800, 5600),
    ("UTILITY",    HW2 + INT, 5700, 11800, 8800),
]
FIRST_ROOMS = [
    ("BEDROOM 2",      200,  200, HW1,   4400),
    ("BEDROOM 1",      200, 4500, HW1,   8800),
    ("LANDING",    HW1 + INT,  200, HW2,  8800),
    ("BEDROOM 3",  HW2 + INT,  200, 11800, 4000),
    ("BATHROOM",   HW2 + INT, 4100, 11800, 6000),
    ("BEDROOM 4",  HW2 + INT, 6100, 11800, 8800),
]

GROUND = {
    "sheet": "A-101", "client_sheet": "A-111", "name": "GROUND FLOOR PLAN",
    "south_open": [(1200, 3400), (5500, 6500), (8200, 10200)],
    "north_open": [(1500, 3500), (8500, 10500)],
    "west_open":  [(1500, 3500), (5800, 7800)],
    "east_open":  [(900, 2900), (6200, 8000)],
    "south_win":  [(1200, 3400), (8200, 10200)],
    "north_win":  [(1500, 3500), (8500, 10500)],
    "west_win":   [(1500, 3500), (5800, 7800)],
    "east_win":   [(900, 2900), (6200, 8000)],
    "partitions": [
        (HW1, EXT, HW1 + INT, H - EXT),
        (HW2, EXT, HW2 + INT, H - EXT),
        (EXT, 5000, HW1, 5100),
        (HW2 + INT, 4000, W - EXT, 4100),
        (HW2 + INT, 5600, W - EXT, 5700),
    ],
    "part_open": [
        (HW1, 1800, HW1 + INT, 2700),
        (HW1, 6200, HW1 + INT, 7100),
        (HW2, 1500, HW2 + INT, 2400),
        (HW2, 4500, HW2 + INT, 5300),
        (HW2, 6600, HW2 + INT, 7500),
    ],
    "doors": [
        (5500, EXT, 1000, 90), (1800, 5000, 900, 90),
        (HW1 + INT, 1800, 900, 0), (HW1 + INT, 6200, 900, 0),
        (HW2, 1500, 900, 180), (HW2, 4500, 800, 180), (HW2, 6600, 900, 180),
    ],
    "rooms": GROUND_ROOMS, "stair_text": "UP",
}

FIRST = {
    "sheet": "A-102", "client_sheet": "A-112", "name": "FIRST FLOOR PLAN",
    "south_open": [(1200, 3400), (8200, 10200)],
    "north_open": [(1500, 3500), (8500, 10500)],
    "west_open":  [(1500, 3500), (5800, 7800)],
    "east_open":  [(900, 2900), (6200, 8000)],
    "south_win":  [(1200, 3400), (8200, 10200)],
    "north_win":  [(1500, 3500), (8500, 10500)],
    "west_win":   [(1500, 3500), (5800, 7800)],
    "east_win":   [(900, 2900), (6200, 8000)],
    "partitions": [
        (HW1, EXT, HW1 + INT, H - EXT),
        (HW2, EXT, HW2 + INT, H - EXT),
        (EXT, 4400, HW1, 4500),
        (HW2 + INT, 4000, W - EXT, 4100),
        (HW2 + INT, 6000, W - EXT, 6100),
    ],
    "part_open": [
        (HW1, 2000, HW1 + INT, 2900),
        (HW1, 6000, HW1 + INT, 6900),
        (HW2, 1500, HW2 + INT, 2400),
        (HW2, 4600, HW2 + INT, 5400),
        (HW2, 6800, HW2 + INT, 7700),
    ],
    "doors": [
        (2000, 4400, 900, 90),
        (HW1 + INT, 2000, 900, 0), (HW1 + INT, 6000, 900, 0),
        (HW2, 1500, 900, 180), (HW2, 4600, 800, 180), (HW2, 6800, 900, 180),
    ],
    "rooms": FIRST_ROOMS, "stair_text": "DN",
}


# ==================================================== FURNITURE
def furnish(sh, which):
    """2D furniture symbols. F = generic outline, S = sanitaryware."""
    F, S = "A-FURN", "A-FURN-SANR"
    R = sh.rect
    C = sh.circle

    def bed(x, y, wd, ln, label=None):
        R(x, y, x + wd, y + ln, F)
        R(x, y + ln - 400, x + wd, y + ln, F)          # pillow band
        sh.line(x, y + ln - 700, x + wd, y + ln - 700, F)

    def table(cx, cy, wd, dp, seats=0):
        R(cx - wd / 2, cy - dp / 2, cx + wd / 2, cy + dp / 2, F)
        for i in range(seats // 2):
            step = wd / (seats // 2 + 1)
            x = cx - wd / 2 + step * (i + 1)
            R(x - 200, cy + dp / 2 + 80, x + 200, cy + dp / 2 + 480, F)
            R(x - 200, cy - dp / 2 - 480, x + 200, cy - dp / 2 - 80, F)

    if which == "ground":
        # LIVING 200..5200 x 200..5000
        R(600, 400, 3000, 1300, F)                      # sofa
        R(600, 400, 3000, 700, F)                       # sofa back
        R(3400, 400, 4400, 1300, F)                     # armchair
        table(1800, 2100, 1400, 800)                    # coffee table
        R(600, 3600, 2600, 4000, F)                     # tv unit
        # KITCHEN/DINING 200..5200 x 5100..8800
        R(300, 8200, 4200, 8800, F)                     # counter run
        R(1100, 8350, 1700, 8700, S)                    # sink
        C(2500, 8500, 220, F)                           # hob
        C(3050, 8500, 220, F)
        R(4300, 8100, 5100, 8800, F)                    # fridge
        table(2300, 6300, 1800, 1000, seats=6)          # dining
        # STUDY 7300..11800 x 200..4000
        R(7600, 400, 9400, 1100, F)                     # desk
        R(8300, 1200, 8900, 1700, F)                    # chair
        R(11100, 500, 11700, 3600, F)                   # shelving
        # WC 7300..11800 x 4100..5600
        R(7600, 4300, 8200, 4900, S)                    # wc pan
        R(8500, 4300, 9200, 4700, S)                    # basin
        # UTILITY 7300..11800 x 5700..8800
        R(7500, 8100, 11600, 8700, F)                   # counter
        R(7700, 8150, 8400, 8650, F)                    # washer
        R(8600, 8150, 9300, 8650, F)                    # dryer
    else:
        # BEDROOM 2 200..5200 x 200..4400
        bed(1600, 300, 1500, 2000)                      # double
        R(1100, 300, 1500, 800, F)                      # bedside
        R(3300, 300, 3700, 800, F)
        R(400, 3400, 2400, 4000, F)                     # wardrobe
        # BEDROOM 1 200..5200 x 4500..8800  (master)
        bed(1500, 6400, 1600, 2100)
        R(1000, 6400, 1400, 6900, F)
        R(3200, 6400, 3600, 6900, F)
        R(400, 4700, 2600, 5300, F)                     # wardrobe
        R(3600, 4700, 5000, 5600, F)                    # dresser
        # BEDROOM 3 7300..11800 x 200..4000
        bed(8200, 400, 1000, 1900)                      # single
        R(10600, 400, 11700, 1000, F)                   # wardrobe
        R(7500, 3300, 9300, 3900, F)                    # desk
        # BATHROOM 7300..11800 x 4100..6000
        R(7500, 4300, 9200, 5000, S)                    # bath
        R(9500, 4300, 10100, 4900, S)                   # wc
        R(10400, 4300, 11100, 4700, S)                  # basin
        # BEDROOM 4 7300..11800 x 6100..8800
        bed(8000, 6400, 1000, 1900)
        R(10500, 6300, 11700, 6900, F)                  # wardrobe


# ==================================================== BUILD
def build_walls(sh, spec, poche=True):
    for x1, x2 in spans(0, W, spec["south_open"]):
        sh.rect(x1, 0, x2, EXT, "A-WALL", poche)
    for x1, x2 in spans(0, W, spec["north_open"]):
        sh.rect(x1, H - EXT, x2, H, "A-WALL", poche)
    for y1, y2 in spans(0, H, spec["west_open"]):
        sh.rect(0, y1, EXT, y2, "A-WALL", poche)
    for y1, y2 in spans(0, H, spec["east_open"]):
        sh.rect(W - EXT, y1, W, y2, "A-WALL", poche)

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
                sh.rect(px1, a, px2, b, "A-WALL", poche)
        else:
            for a, b in spans(px1, px2, opens):
                sh.rect(a, py1, b, py2, "A-WALL", poche)


OBSTACLE_LAYERS = ("A-FURN", "A-FURN-SANR", "A-STRS", "A-DOOR", "A-GLAZ")


def collect_obstacles(sh):
    """Real bounding boxes of everything a label must not land on."""
    out = []
    for e in sh.ms:
        if str(e.Layer) in OBSTACLE_LAYERS:
            try:
                lo, hi = e.GetBoundingBox()
                out.append((lo[0], lo[1], hi[0], hi[1]))
            except Exception:
                pass
    return out


def _overlap(a, b, pad=150.0):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or
                a[3] + pad < b[1] or b[3] + pad < a[1])


def _place_label(name, area_txt, x1, y1, x2, y2, obs, h=280.0):
    """Search the room for a spot where the two-line label clears every
    obstacle, preferring positions near the centroid. Labels used to be
    pinned to the centroid, which is exactly where the furniture sits."""
    wd = max(len(name), len(area_txt)) * h * 0.95
    cx0, cy0 = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    best = None
    for fy in (0.50, 0.32, 0.68, 0.20, 0.80, 0.12, 0.88):
        for fx in (0.50, 0.32, 0.68, 0.22, 0.78):
            cx = x1 + (x2 - x1) * fx
            cy = y1 + (y2 - y1) * fy
            box = (cx - wd / 2, cy - 560, cx + wd / 2, cy + h)
            if (box[0] < x1 + 120 or box[2] > x2 - 120 or
                    box[1] < y1 + 120 or box[3] > y2 - 120):
                continue
            hits = sum(1 for o in obs if _overlap(box, o))
            score = (hits, (cx - cx0) ** 2 + (cy - cy0) ** 2)
            if best is None or score < best[0]:
                best = (score, cx, cy)
    if best is None:
        return cx0, cy0, h
    return best[1], best[2], h


def label_rooms(sh, spec, obs):
    gia = 0.0
    for name, x1, y1, x2, y2 in spec["rooms"]:
        area = (x2 - x1) * (y2 - y1) / 1e6
        gia += area
        atxt = f"{area:.2f} m2"
        cx, cy, h = _place_label(name, atxt, x1, y1, x2, y2, obs)
        room_w = (x2 - x1) - 300
        lbl = sh.fit_text(name, cx, cy, h, "A-ANNO-TEXT", room_w, centre=True)
        sh.fit_text(atxt, cx, cy - 430, 190, "A-ANNO-TEXT", room_w, centre=True)
        # the placed label is itself an obstacle for the next room's search
        try:
            obs.append(sh.bbox(lbl))
        except Exception:
            pass
    return gia


def draw_plan(spec, client=False):
    sh = Sheet()
    build_walls(sh, spec, poche=True)
    for (hx, hy, wd, fa) in spec["doors"]:
        sh.door(hx, hy, wd, fa)
    for x1, x2 in spec["south_win"]:
        sh.window(x1, 0, x2, EXT)
    for x1, x2 in spec["north_win"]:
        sh.window(x1, H - EXT, x2, H)
    for y1, y2 in spec["west_win"]:
        sh.window(0, y1, EXT, y2, horizontal=False)
    for y1, y2 in spec["east_win"]:
        sh.window(W - EXT, y1, W, y2, horizontal=False)
    sh.stair(up_text=spec["stair_text"])
    furnish(sh, "ground" if spec["sheet"] == "A-101" else "first")
    # labels are placed after the furniture so they can avoid it
    gia = label_rooms(sh, spec, collect_obstacles(sh))

    if not client:
        for a, b in [(0, HW1), (HW1, HW2 + INT), (HW2 + INT, W)]:
            sh.dim_h(a, b, 0, 1000)
        sh.dim_h(0, W, 0, 2100)
        for a, b in [(0, H / 2), (H / 2, H)]:
            sh.dim_v(a, b, 0, 1000)
        sh.dim_v(0, H, 0, 2100)

    sh.north_arrow()
    sh.title_block(spec["client_sheet"] if client else spec["sheet"],
                   spec["name"] + (" - PRESENTATION" if client else ""), gia)
    return sh, gia


def draw_model_3d():
    sh = Sheet()
    sh.box(0, 0, W, H, -SLAB, 0, "A-SLAB")
    for spec, base, ch in ((GROUND, 0.0, CH_G), (FIRST, CH_G + SLAB, CH_F)):
        if base > 0:
            sh.box(0, 0, W, H, base - SLAB, base, "A-SLAB")
        for x1, x2 in spans(0, W, spec["south_open"]):
            sh.box(x1, 0, x2, EXT, base, base + ch, "A-WALL")
        for x1, x2 in spans(0, W, spec["north_open"]):
            sh.box(x1, H - EXT, x2, H, base, base + ch, "A-WALL")
        for y1, y2 in spans(0, H, spec["west_open"]):
            sh.box(0, y1, EXT, y2, base, base + ch, "A-WALL")
        for y1, y2 in spans(0, H, spec["east_open"]):
            sh.box(W - EXT, y1, W, y2, base, base + ch, "A-WALL")
        for x1, x2 in spec["south_open"]:
            sh.box(x1, 0, x2, EXT, base + 2100, base + ch, "A-WALL")
        for x1, x2 in spec["north_open"]:
            sh.box(x1, H - EXT, x2, H, base + 2100, base + ch, "A-WALL")
        for y1, y2 in spec["west_open"]:
            sh.box(0, y1, EXT, y2, base + 2100, base + ch, "A-WALL")
        for y1, y2 in spec["east_open"]:
            sh.box(W - EXT, y1, W, y2, base + 2100, base + ch, "A-WALL")
        for (px1, py1, px2, py2) in spec["partitions"]:
            sh.box(px1, py1, px2, py2, base, base + ch, "A-WALL")

    rb = CH_G + SLAB + CH_F
    sh.box(-300, -300, W + 300, H + 300, rb, rb + SLAB, "A-ROOF")
    sh.box(1500, 1500, W - 1500, H - 1500, rb + SLAB, rb + SLAB + 1200, "A-ROOF")
    sh.title_block("A-201", "3D MODEL - SOUTH WEST ISOMETRIC",
                   sum((r[3] - r[1]) * (r[4] - r[2]) for r in GROUND_ROOMS) / 1e6,
                   scale="NTS")
    try:
        vp = sh.doc.ActiveViewport
        vp.Direction = P(-1, -1, 1)
        sh.doc.ActiveViewport = vp
    except Exception as exc:
        print("   view warning:", exc)
    return sh


def close_generated():
    for i in range(APP.Documents.Count - 1, -1, -1):
        d = APP.Documents.Item(i)
        if OUT.lower() in str(d.FullName).lower():
            d.Close(False)


if __name__ == "__main__":
    close_generated()
    done = []
    for spec in (GROUND, FIRST):
        for client in (False, True):
            sh, gia = draw_plan(spec, client)
            no = spec["client_sheet"] if client else spec["sheet"]
            tag = "CLIENT" if client else "ENGINEERING"
            pdf, ok = sh.save_and_plot(f"{no}_{spec['name'].replace(' ', '_')}"
                                       + ("_CLIENT" if client else ""))
            print(f"{no}  {tag:11s} entities={sh.ms.Count:4d}  GIA={gia:6.2f} m2  pdf={ok}")
            done.append((no, ok))
    sh3 = draw_model_3d()
    pdf, ok = sh3.save_and_plot("A-201_3D_Model")
    solids = sum(1 for e in sh3.ms if str(e.EntityName) == "AcDb3dSolid")
    print(f"A-201  3D          entities={sh3.ms.Count:4d}  solids={solids}   pdf={ok}")
    done.append(("A-201", ok))
    print("\n", OUT)
    for n, ok in done:
        print(f"  {n}  {'OK' if ok else 'FAIL'}")
