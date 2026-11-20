"""
Generate a presentation-grade residential floor plan in the running AutoCAD.

Units are millimetres, drawn 1:1 in model space (plot at 1:100 on A3).
Creates its own new drawing, so nothing already open is touched.
"""

import math

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

pythoncom.CoInitialize()
app = w.GetActiveObject("AutoCAD.Application")
doc = app.Documents.Add()
ms = doc.ModelSpace
print("drawing:", doc.Name)


def P(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x), float(y), float(z)])


def arr(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])


# ---------------------------------------------------------------- layers
LAYERS = {
    "A-WALL":      7,   # walls               white
    "A-WALL-PATT": 8,   # wall poche          dark grey
    "A-DOOR":      3,   # doors               green
    "A-GLAZ":      4,   # windows             cyan
    "A-ANNO-TEXT": 2,   # room names          yellow
    "A-ANNO-DIMS": 1,   # dimensions          red
    "A-ANNO-TTLB": 7,   # title block         white
    "A-ANNO-NORT": 6,   # north arrow         magenta
}
for name, color in LAYERS.items():
    lyr = doc.Layers.Add(name)
    lyr.Color = color

# text + dimension styles sized for 1:100 on A3
try:
    dimstyle = doc.DimStyles.Add("PLAN-100")
    doc.ActiveDimStyle = dimstyle
    doc.SetVariable("DIMTXT", 250.0)     # text height
    doc.SetVariable("DIMASZ", 150.0)     # arrow size
    doc.SetVariable("DIMEXE", 100.0)     # extension beyond dim line
    doc.SetVariable("DIMEXO", 150.0)     # extension line offset
    doc.SetVariable("DIMDEC", 0)         # whole millimetres
    doc.SetVariable("DIMTIH", 0)         # text aligned with dim line
except Exception as exc:
    print("dimstyle warning:", exc)


def rect(x1, y1, x2, y2, layer):
    """Closed rectangle as a lightweight polyline."""
    pl = ms.AddLightWeightPolyline(arr([x1, y1, x2, y1, x2, y2, x1, y2]))
    pl.Closed = True
    pl.Layer = layer
    return pl


def line(x1, y1, x2, y2, layer):
    ln = ms.AddLine(P(x1, y1), P(x2, y2))
    ln.Layer = layer
    return ln


def text(s, x, y, h, layer, align_centre=False):
    t = ms.AddText(s, P(x, y), h)
    t.Layer = layer
    if align_centre:
        try:
            t.Alignment = 1          # acAlignmentCenter
            t.TextAlignmentPoint = P(x, y)
        except Exception:
            pass
    return t


# ============================================================ GEOMETRY
# Envelope 12000 x 9000, exterior wall 200, partitions 100.
W, H, EXT, INT = 12000.0, 9000.0, 200.0, 100.0

walls = []

# ---- exterior walls, broken for the front door and windows -------------
# bottom (south) --------------------------------------------------------
for x1, x2 in [(0, 1500), (3500, 5200), (6200, 7000), (8500, W)]:
    walls.append(rect(x1, 0, x2, EXT, "A-WALL"))
# top (north) -----------------------------------------------------------
for x1, x2 in [(0, 1000), (3000, 5000), (7000, 9000), (11000, W)]:
    walls.append(rect(x1, H - EXT, x2, H, "A-WALL"))
# left (west) -----------------------------------------------------------
for y1, y2 in [(0, 1500), (3500, H)]:
    walls.append(rect(0, y1, EXT, y2, "A-WALL"))
# right (east) ----------------------------------------------------------
for y1, y2 in [(0, 3000), (4500, H)]:
    walls.append(rect(W - EXT, y1, W, y2, "A-WALL"))

# ---- corridor walls, broken for six internal doors ---------------------
HALL_S, HALL_N = 5000.0, 6100.0          # corridor 5100 -> 6100 clear
for x1, x2 in [(EXT, 2000), (2900, 6500), (7400, 10000), (10900, W - EXT)]:
    walls.append(rect(x1, HALL_S, x2, HALL_S + INT, "A-WALL"))
for x1, x2 in [(EXT, 1500), (2400, 5500), (6400, 9500), (10400, W - EXT)]:
    walls.append(rect(x1, HALL_N, x2, HALL_N + INT, "A-WALL"))

# ---- partitions --------------------------------------------------------
walls.append(rect(5500, EXT, 5600, HALL_S, "A-WALL"))            # living|kitchen
walls.append(rect(9000, EXT, 9100, HALL_S, "A-WALL"))            # kitchen|bath
walls.append(rect(4200, HALL_N + INT, 4300, H - EXT, "A-WALL"))  # bed1|bed2
walls.append(rect(8000, HALL_N + INT, 8100, H - EXT, "A-WALL"))  # bed2|bed3

# ---- wall poche --------------------------------------------------------
hatched = 0
for pl in walls:
    try:
        h = ms.AddHatch(0, "SOLID", True)
        # AppendOuterLoop rejects a plain Python list ("Invalid object array");
        # it needs an explicit VT_ARRAY|VT_DISPATCH variant.
        h.AppendOuterLoop(VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [pl]))
        h.Evaluate()
        h.Layer = "A-WALL-PATT"
        hatched += 1
    except Exception:
        pass
print(f"walls: {len(walls)}  poche: {hatched}")


# ---- doors: leaf + 90 degree swing arc ---------------------------------
def door(hx, hy, width, facing, hinge="left"):
    """Door in a wall opening. `facing` is the swing direction in degrees
    (0 = east, 90 = north). Draws the leaf and its quarter-circle arc."""
    a = math.radians(facing)
    lx, ly = hx + width * math.cos(a), hy + width * math.sin(a)
    line(hx, hy, lx, ly, "A-DOOR")
    sweep = math.radians(-90 if hinge == "left" else 90)
    arc = ms.AddArc(P(hx, hy), width,
                    min(a, a + sweep), max(a, a + sweep))
    arc.Layer = "A-DOOR"


door(5200, EXT, 1000, 90)                 # front entrance, swings in
door(2000, HALL_S, 900, 90)               # living  -> hall
door(6500, HALL_S, 900, 90)               # kitchen -> hall
door(10000, HALL_S, 900, 90)              # bath    -> hall
door(1500, HALL_N + INT, 900, 90)         # hall -> bed 1
door(5500, HALL_N + INT, 900, 90)         # hall -> bed 2
door(9500, HALL_N + INT, 900, 90)         # hall -> bed 3


# ---- windows: three lines across the opening ---------------------------
def window(x1, y1, x2, y2, horizontal=True):
    if horizontal:
        for f in (0.0, 0.5, 1.0):
            y = y1 + (y2 - y1) * f
            line(x1, y, x2, y, "A-GLAZ")
        line(x1, y1, x1, y2, "A-GLAZ")
        line(x2, y1, x2, y2, "A-GLAZ")
    else:
        for f in (0.0, 0.5, 1.0):
            x = x1 + (x2 - x1) * f
            line(x, y1, x, y2, "A-GLAZ")
        line(x1, y1, x2, y1, "A-GLAZ")
        line(x1, y2, x2, y2, "A-GLAZ")


window(1500, 0, 3500, EXT)                    # living, south
window(7000, 0, 8500, EXT)                    # kitchen, south
window(1000, H - EXT, 3000, H)                # bed 1, north
window(5000, H - EXT, 7000, H)                # bed 2, north
window(9000, H - EXT, 11000, H)               # bed 3, north
window(0, 1500, EXT, 3500, horizontal=False)  # living, west
window(W - EXT, 3000, W, 4500, horizontal=False)  # bath, east

# ---- room labels with areas -------------------------------------------
ROOMS = [
    ("LIVING",     2850, 2600, 5.30 * 4.80),
    ("KITCHEN",    7300, 2600, 3.40 * 4.80),
    ("BATH",      10450, 2600, 2.70 * 4.80),
    ("HALL",       6000, 5500, 11.60 * 1.00),
    ("BEDROOM 1",  2200, 7500, 4.00 * 2.60),
    ("BEDROOM 2",  6150, 7500, 3.70 * 2.60),
    ("BEDROOM 3", 10000, 7500, 3.70 * 2.60),
]
for name, x, y, area in ROOMS:
    text(name, x, y, 300, "A-ANNO-TEXT", align_centre=True)
    text(f"{area:.2f} m2", x, y - 450, 200, "A-ANNO-TEXT", align_centre=True)


# ---- dimensions --------------------------------------------------------
def dim_h(x1, x2, y, offset):
    d = ms.AddDimRotated(P(x1, y), P(x2, y), P((x1 + x2) / 2, y - offset), 0.0)
    d.Layer = "A-ANNO-DIMS"


def dim_v(y1, y2, x, offset):
    d = ms.AddDimRotated(P(x, y1), P(x, y2), P(x - offset, (y1 + y2) / 2),
                         math.radians(90))
    d.Layer = "A-ANNO-DIMS"


# room-level string along the south face, then the overall below it
for x1, x2 in [(0, 5500), (5500, 9000), (9000, W)]:
    dim_h(x1, x2, 0, 900)
dim_h(0, W, 0, 1900)
# west face
for y1, y2 in [(0, HALL_S), (HALL_S, HALL_N + INT), (HALL_N + INT, H)]:
    dim_v(y1, y2, 0, 900)
dim_v(0, H, 0, 1900)

# ---- north arrow -------------------------------------------------------
NX, NY, NR = 13500.0, 8000.0, 500.0
c = ms.AddCircle(P(NX, NY), NR)
c.Layer = "A-ANNO-NORT"
tip = ms.AddLightWeightPolyline(
    arr([NX, NY + NR, NX - NR * 0.35, NY - NR * 0.5, NX, NY - NR * 0.2,
         NX + NR * 0.35, NY - NR * 0.5]))
tip.Closed = True
tip.Layer = "A-ANNO-NORT"
text("N", NX, NY + NR + 200, 300, "A-ANNO-NORT", align_centre=True)

# ---- title block -------------------------------------------------------
TB_X, TB_Y, TB_W, TB_H = 0.0, -4200.0, 15000.0, 2400.0
rect(TB_X, TB_Y, TB_X + TB_W, TB_Y + TB_H, "A-ANNO-TTLB")
line(TB_X, TB_Y + 1600, TB_X + TB_W, TB_Y + 1600, "A-ANNO-TTLB")
line(TB_X + 9000, TB_Y, TB_X + 9000, TB_Y + 1600, "A-ANNO-TTLB")
line(TB_X + 12000, TB_Y, TB_X + 12000, TB_Y + 1600, "A-ANNO-TTLB")

text("RESIDENTIAL FLOOR PLAN - THREE BEDROOM DWELLING",
     TB_X + 300, TB_Y + 1900, 450, "A-ANNO-TTLB")
text("GROUND FLOOR / GENERAL ARRANGEMENT",
     TB_X + 300, TB_Y + 1000, 280, "A-ANNO-TTLB")
text("ALL DIMENSIONS IN MILLIMETRES. DO NOT SCALE FROM DRAWING.",
     TB_X + 300, TB_Y + 500, 200, "A-ANNO-TTLB")
text("SCALE  1:100 @ A3", TB_X + 9300, TB_Y + 1000, 250, "A-ANNO-TTLB")
text("DATE   2026-09-06", TB_X + 9300, TB_Y + 500, 250, "A-ANNO-TTLB")
text("DWG    A-101", TB_X + 12300, TB_Y + 1000, 250, "A-ANNO-TTLB")
text("REV    A", TB_X + 12300, TB_Y + 500, 250, "A-ANNO-TTLB")

# gross internal area
gia = sum(r[3] for r in ROOMS)
text(f"GROSS INTERNAL AREA (ROOMS): {gia:.2f} m2",
     TB_X + 300, TB_Y + 150, 200, "A-ANNO-TTLB")

app.ZoomExtents()
print(f"entities: {ms.Count}")
print(f"GIA: {gia:.2f} m2")
