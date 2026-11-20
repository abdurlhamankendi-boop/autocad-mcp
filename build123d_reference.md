# build123d 0.11.1 — working reference for architectural modelling

Everything below was **executed** against the installed package:

```
python:     C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe   (3.13.15, win-amd64)
build123d:  0.11.1  -> ...\Python313\Lib\site-packages\build123d\__init__.py
ezdxf:      1.4.4
kernel:     OpenCASCADE via OCP
```

Benchmarks were measured on this machine (Windows 11, Python 3.13). Timings are `min` of the runs shown.

---

## 0. Imports — three names you need are NOT exported by `import *`

`build123d.__all__` has 200 entries. These are **missing** from it and must be imported explicitly:

| Name | Import from | Needed for |
|---|---|---|
| `Drawing` | `build123d.exporters` | HLR projection / elevations |
| `ColorIndex` | `build123d.exporters` | DXF + SVG layer colours |
| `SkipClean` | `build123d.topology` | disabling `clean()` in operator code |
| `Shape`, `Mixin1D`, `GroupBy` | `build123d.topology` | type checks / annotations |

```python
from build123d import *                                   # 200 names
from build123d.exporters import Drawing, ColorIndex       # NOT in __all__
from build123d.topology import SkipClean                  # NOT in __all__
```

`ExportSVG`, `ExportDXF`, `LineType`, `DotLength`, `Export2D`, `Unit`, `ShapeList`,
`TechnicalDrawing`, `Draft` **are** in `__all__`.

> Cosmetic noise: importing build123d prints `'name' table stringOffset incorrect. Expected: 222; Actual: 224`
> once (fontTools scanning a system font while `FontManager` builds its cache). Harmless; it goes to stdout.

---

## 1. Algebra mode basics

Algebra mode = plain Python objects and operators. No `with BuildPart()` context needed.
`Box`, `Cylinder`, … return a `Part` (which subclasses `Compound`, which subclasses `Shape`).

### Verified

```python
from build123d import *

b = Box(1000, 800, 600, align=(Align.MIN, Align.MIN, Align.MIN))
# -> type Box, isinstance(b, Part) == True, volume 480000000.0
#    bbox: 0<=x<=1000, 0<=y<=800, 0<=z<=600

Pos(100, 200, 300)          # Location: (position=(100,200,300), orientation=(0,0,0))
Rot(0, 0, 45)               # Rotation: (position=(0,0,0), orientation=(0,0,45))
Pos(100, 200, 300) * Rot(0, 0, 45)   # Location: pos=(100,200,300), ori=(0,0,45)

moved   = Pos(100, 0, 0) * b          # bbox 100..1100 in x  (returns a NEW object)
rotated = Rot(0, 0, 30) * b           # rotates about the world origin, not the shape
onplane = Plane.XZ * Box(10, 10, 10)  # place a solid on a plane
```

`Pos`/`Rot`/`Plane` **left-multiply** the shape. `shape * location` is not the placement operator —
always write `Pos(...) * shape`.

### Booleans

| Operator | Meaning | Verified result |
|---|---|---|
| `a + b` | fuse | `1000×800×600` + a `200³` box beside it → volume `4.88e8`, 1 solid |
| `a - b` | cut | `480e6 − 48e6 = 432000000.0`, 1 solid, 12 faces |
| `a & b` | common | half-overlap of two `1000×800×600` → `240000000.0` |
| `a += b`, `-=`, `&=` | in-place | works |

Method forms exist and are faster in bulk: `a.fuse(*others)`, `a.cut(*others)`, `a.intersect(other)`.

### Minimal hollow box — runs

```python
from build123d import *

outer  = Box(1000, 800, 600, align=(Align.MIN, Align.MIN, Align.MIN))
inner  = Pos(200, 200, 200) * Box(600, 400, 200, align=(Align.MIN, Align.MIN, Align.MIN))
hollow = outer - inner

print(hollow.volume)          # 432000000.0   (= 480e6 - 48e6)
print(len(hollow.solids()))   # 1
print(len(hollow.faces()))    # 12
print(hollow.is_valid)        # True     <-- PROPERTY, not a method
```

### `offset()` on a solid does **not** shell it by default

```python
offset(Box(1000, 800, 600), amount=-25)          # -> volume 391875000.0 == 950*750*550
```
That is a **shrunken solid**, not a shell. To get a shell you must pass `openings=[face]`.
For buildings, do not use `offset` on solids at all — subtract an inner extrusion (§2).

### Planes available

`Plane.XY, YZ, ZX, XZ, YX, ZY, front, back, left, right, top, bottom`, plus
`Plane(origin=…, x_dir=…, z_dir=…)`, `Plane(face)`, `Plane.XY.offset(1200)`,
`Plane.XY.rotated((0,0,45))`, `Plane.XY.to_local_coords(shape)` / `.from_local_coords(...)`.

---

## 2. Walls from a footprint — which approach is most robust

Four approaches were built and timed on an 8 m × 6 m room, 250 mm walls, 3 m high:

| # | Approach | Time | Result |
|---|---|---|---|
| **A2** | **sketch boolean, then one `extrude`** | **1.4 ms** | ✅ correct, fastest |
| A | two `extrude`s, then 3D subtract | 8.2 ms | ✅ correct, 6× slower |
| C2 | `offset(face, -t)` in sketch space, then extrude | 4.7 ms | ✅ correct, best for non-rectangular footprints |
| B | `trace(polyline, line_width=t)` then extrude | 4.0 ms | ✅ works but walls are **centred on the polyline** |
| C | `offset(wire, side=Side.LEFT/RIGHT)` | — | ❌ **raises `IndexError`** on closed wires (bug) |

### Winner: build the wall *face*, then extrude once

```python
from build123d import *

WALL, H = 250.0, 3000.0

outer = Rectangle(8000, 6000, align=(Align.MIN, Align.MIN))            # Sketch on Plane.XY
inner = Pos(WALL, WALL) * Rectangle(8000 - 2*WALL, 6000 - 2*WALL,
                                    align=(Align.MIN, Align.MIN))
ring  = outer - inner                     # Sketch boolean -> 1 annular face
walls = extrude(ring, H)                  # -> Part, volume 20 250 000 000.0
```

For a non-rectangular footprint, use `offset()` **on the face** (this one works fine):

```python
outer = Rectangle(8000, 6000, align=(Align.MIN, Align.MIN))
inner = offset(outer, amount=-WALL, kind=Kind.INTERSECTION)   # Sketch, area 41 250 000.0
walls = extrude(outer - inner, H)                             # volume 20 250 000 000.0
```
Use `Kind.INTERSECTION` for building corners (mitred). `Kind.ARC` (the default) rounds them.

`trace()` centres the band on the polyline — handy if your footprint is a wall **centreline**:

```python
centre = Polyline((0,0), (8000,0), (8000,6000), (0,6000), close=True)   # -> a Curve
walls  = extrude(trace(centre, line_width=WALL), H)   # outer footprint becomes 8250 × 6250
```

### ❌ Broken: `offset()` on a closed wire

```python
w = Wire(Polyline((0,0),(8000,0),(8000,6000),(0,6000), close=True).edges())
offset(w, amount=125, side=Side.LEFT,  kind=Kind.INTERSECTION, closed=True)
# IndexError: list index out of range   (topology/one_d.py:1226, offset_2d)
offset(w, amount=125, side=Side.RIGHT, ...)   # same IndexError
offset(w, amount=125, side=Side.BOTH,  ...)   # returns a Curve, 4 edges, 1 wire
```
Only `Side.BOTH` survives. Do wall offsetting on **faces**, not wires.

### Closed room shell with door + window openings — runs

```python
from build123d import *

WALL, H = 250.0, 3000.0
outer = Rectangle(8000, 6000, align=(Align.MIN, Align.MIN))
inner = Pos(WALL, WALL) * Rectangle(8000 - 2*WALL, 6000 - 2*WALL, align=(Align.MIN, Align.MIN))
shell = extrude(outer - inner, H)

door = Pos(2000,  -50,   0) * Box(1000, WALL+100, 2100, align=(Align.MIN,)*3)
win1 = Pos(5000,  -50, 900) * Box(1500, WALL+100, 1400, align=(Align.MIN,)*3)
win2 = Pos( -50, 2000, 900) * Box(WALL+100, 1500, 1400, align=(Align.MIN,)*3)

# BATCH the cut: one boolean instead of three  (10.9 ms vs 19.6 ms here, and the gap
# widens hugely at building scale - see §6)
room = shell - (Part() + [door, win1, win2])

print(room.volume)        # 18675000000.0
print(len(room.solids())) # 1
print(len(room.faces()))  # 21
print(room.is_valid, room.is_manifold)   # True True
```

**Coplanar cutters are safe** in this OCCT build — the `±50 mm` overshoot above is optional:

```python
wall  = Box(4000, 250, 3000, align=(Align.MIN,)*3)
exact = Pos(1000, 0, 900) * Box(1200, 250, 1400, align=(Align.MIN,)*3)   # exactly flush
over  = Pos(1000,-1, 900) * Box(1200, 252, 1400, align=(Align.MIN,)*3)
# both -> volume 2580000000.0, 10 faces, 1 solid, valid, manifold. 6.0 ms / 4.3 ms.
```
Overshoot still costs nothing and protects you from accumulated float error, so keep it as a habit.

---

## 3. Sectioning to 2D

### `section()` signature and return type

```python
section(obj: Part | None = None,
        section_by: Plane | Iterable[Plane] = Plane.XZ,
        height: float = 0.0,
        clean: bool = True,
        mode: Mode = Mode.PRIVATE) -> Sketch
```

* Returns a **`Sketch`** (`Sketch → Compound → Mixin3D → Shape`) containing the **cut faces**,
  positioned **in 3D on the cutting plane** (not flattened).
* `height` offsets the plane along its **`z_dir`**.
* Internally: builds a `Face.make_rect(2*max_size, …)` on the plane and calls `obj.intersect(face)`.
* Multiple planes at once: pass a list; results are merged into one `Sketch`.
* Empty result → an **empty `Sketch`**, not `None`; `.area == 0.0`, `.bounding_box()` is degenerate.

### Floor plan at Z = 1200 — runs

```python
from build123d import *

plan = section(model, Plane.XY, height=1200)    # 16 ms on a 77-face two-storey villa
# equivalent, and clearer:
plan = section(model, Plane.XY.offset(1200))
plan = section(model, Plane(origin=(0, 0, 1200), z_dir=(0, 0, 1)))

print(type(plan).__name__)          # Sketch
print(len(plan.faces()))            # 6      <- cut faces (poché regions)
print(len(plan.edges()))            # 36
print(len(plan.wires()))            # 6
print(plan.area / 1e6, "m2")        # 7.636
print(plan.bounding_box())          # z is 1200..1200  <-- NOT flat!
```

### Getting the edges out

```python
edges = plan.edges()                                  # ShapeList[Edge], 36
loops = [w for f in plan.faces() for w in f.wires()]  # closed loops, 6
big   = plan.faces().sort_by(SortBy.AREA)[-1]
big.outer_wire().edges()                              # 14 edges
big.inner_wires()                                     # holes; a column in a room shows up here
curve = Curve() + plan.edges()                        # Curve (a Compound) — feeds the exporters
```
Holes really do survive: `section(Box(2000,2000,3000) - Cylinder(400,4000), Plane.XY)` gives one
face with a 4-edge outer wire and **1 inner wire**.

### ⚠️ `Plane.XZ.z_dir` is `(0, −1, 0)` — `height` goes the "wrong" way

```python
section(model, Plane.XZ, height= 4000)   # 0 faces, area 0.0     <-- empty, silently
section(model, Plane.XZ, height=-4000)   # 1 face,  area 9.47 m2, y = 4000
```
Always prefer an explicit plane for building sections:

```python
sec = section(model, Plane(origin=(0, 4000, 0), z_dir=(0, 1, 0)))   # 1 face, 9.47 m2
```

### Vertical section, flattened onto the XY plane for 2D output

Put the plane's **origin on the cut** so `to_local_coords` lands the result on `z = 0`,
and give an explicit `x_dir` so you control which way is "right" in the drawing:

```python
p        = Plane(origin=(4500, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
sec      = section(model, p)                    # lives at x = 4500 in 3D
sec_flat = p.to_local_coords(sec)               # bbox 0..8000 (world Y) × 0..6200 (world Z), z = 0
```
Without an explicit `x_dir`, build123d picks one for you and you get e.g. `y = −8000..0`.

### Flattening a plan

DXF discards Z and **warns**, so translate first:

```python
plan_flat = Pos(0, 0, -1200) * plan        # bbox z: 0.0 .. 0.0
```

### `split()` — the other half of the story

```python
lower = split(model, bisect_by=Plane.XY.offset(1200), keep=Keep.BOTTOM)   # -> Part, 25.1 m3, 19 ms
both  = split(model, bisect_by=Plane.XY.offset(1200), keep=Keep.BOTH)     # -> Part with 2 solids
# Keep: ALL, BOTTOM, BOTH, INSIDE, OUTSIDE, TOP
```
Use `split` when you want the **cut model** (e.g. a cutaway view or "what's below the cut plane"),
`section` when you want the **cut face**.

---

## 4. Projection with hidden-line removal

Two APIs, both wrapping `HLRBRep_Algo` + `HLRAlgo_Projector`. They give the same geometry;
they differ in how you aim the camera and what they return.

| | `Drawing` | `Shape.project_to_viewport` |
|---|---|---|
| import | `from build123d.exporters import Drawing` | method on any `Shape` |
| camera | `look_from` is a **direction** | `viewport_origin` is a **point** |
| aim point | `look_at` (default `shape.center()`) | `look_at` (default `shape.center()`) |
| returns | `.visible_lines` / `.hidden_lines` → `Compound` | `(ShapeList[Edge], ShapeList[Edge])` |
| hidden lines | `with_hidden=True/False` | always both |
| perspective | `focus=<float>` | `focus=<float>` |

Both collect `VCompound + Rg1LineVCompound + OutLineVCompound` as visible and
`HCompound + OutLineHCompound (+ Rg1LineHCompound)` as hidden, then run
`BRepLib.BuildCurves3d_s` (without which OCCT segfaults).

**Output frame:** edges land on the **global `z = 0` plane**, in the projector's own 2D frame,
centred on `look_at`. Verified: `min/max` of every visible edge centre `Z` = `0.0 / 0.0`.

### `Drawing` — the one to use for elevations

```python
from build123d import *
from build123d.exporters import Drawing

d = Drawing(model, look_from=(0, -1, 0), look_up=(0, 0, 1), with_hidden=True)
print(type(d.visible_lines).__name__, len(d.visible_lines.edges()))   # Compound 36
print(type(d.hidden_lines).__name__,  len(d.hidden_lines.edges()))    # Compound 118
print(d.visible_lines.bounding_box())   # x span 10000.0, y span 6200.0 -> true size
```
Measured on the villa: `Drawing(...)` took **0.007–0.010 s**.

### Verified view table (a 77-face two-storey villa, 10 m × 8 m × 6.2 m)

| `look_from` | `look_up` | reads as | visible edges | projected size |
|---|---|---|---|---|
| `(0,-1,0)` | `(0,0,1)` | south elevation | 36 | 10000 × 6200 |
| `(0, 1,0)` | `(0,0,1)` | north elevation | 4 | 10000 × 6200 |
| `(-1,0,0)` | `(0,0,1)` | west elevation | 24 | 8000 × 6200 |
| `( 1,0,0)` | `(0,0,1)` | east elevation | 4 | 8000 × 6200 |
| `(0,0,1)` | `(0,1,0)` | roof plan | 4 | 10000 × 8000 |
| `(1,-1,1)` | `(0,0,1)` | iso | 70 | 12728 × 12411 |

**Orientation is architecturally correct — no mirroring bugs.** Verified with an asymmetric
marker at the `+X +Y` corner:

| `look_from` | projected x | projected y |
|---|---|---|
| `(0,-1,0)` | `+(X − look_at.X)` | `Z − look_at.Z` |
| `(0, 1,0)` | `−(X − look_at.X)` | `Z − look_at.Z` |
| `( 1,0,0)` | `+(Y − look_at.Y)` | `Z − look_at.Z` |
| `(-1,0,0)` | `−(Y − look_at.Y)` | `Z − look_at.Z` |
| `(0,0,1)` up `(0,1,0)` | `X − look_at.X` | `Y − look_at.Y` |

i.e. looking north puts east on the right, looking south puts east on the left. Exactly right.

### Restoring true heights (and a sheet layout) — runs

```python
def elevation(model, look_from, origin=(0, 0), with_hidden=True):
    """(visible, hidden) as 2D Compounds on z=0.
       x = view-local horizontal (centred on model.center()), y = TRUE world Z."""
    look_at = model.center()
    d = Drawing(model, look_from=look_from, look_up=(0, 0, 1), with_hidden=with_hidden)
    place = Pos(origin[0], origin[1] + look_at.Z, 0)
    return place * d.visible_lines, place * d.hidden_lines

vis, hid = elevation(model, (0, -1, 0))
vis.bounding_box()          # y: 0.0 .. 6000.0  <- real building heights
# window sill/head Y values recovered exactly: [0, 900, 2300, 6000]

sheet_v, sheet_h = Curve(), Curve()
for i, lf in enumerate([(0,-1,0), (1,0,0), (0,1,0), (-1,0,0)]):
    v, h = elevation(model, lf, origin=(i * 12000, 0))
    sheet_v += v.edges();  sheet_h += h.edges()
# sheet bbox x: -5006 .. 40050, y: 0 .. 6000
```

### `project_to_viewport` — when you want `ShapeList[Edge]`

```python
c = model.center()
vis, hid = model.project_to_viewport(
    viewport_origin=(c.X, c.Y - 1e6, c.Z),   # a POINT far away on the view axis
    viewport_up=(0, 0, 1),
    look_at=c)
# -> ShapeList[Edge] 36 visible / 118 hidden, size 10000.0 × 6200.0
```
🪤 If `viewport_origin` is not collinear with `look_at` along the view axis you silently get a
**skewed** view: `viewport_origin=(0, -50000, 0)` with `look_at=(5000,4000,3100)` gave
`10706 × 6696` instead of `10000 × 6200` and 95 "visible" edges instead of 36.

Perspective: `model.project_to_viewport((0, -30000, 5000), focus=30000)` → 97 visible edges.

For a plan the top-down projection *does* line up with world coordinates after a shift
(verified — see §9 `plan_at`):

```python
c = lower.center()
vis, _ = lower.project_to_viewport(viewport_origin=(c.X, c.Y, c.Z + 1e6),
                                   viewport_up=(0, 1, 0), look_at=(c.X, c.Y, c.Z))
vis = ShapeList(e.moved(Location((c.X, c.Y, 0))) for e in vis)
# bbox now 0..10000 × 0..8000, matching the plan section exactly
```

### `ExportSVG` / `ExportDXF` do **not** do HLR themselves

They are pure 2D writers: `add_shape()` just walks `shape.edges()` and drops Z.
You must run `Drawing` / `project_to_viewport` first, then hand the two edge sets to two layers.

```python
from build123d.exporters import Drawing, ColorIndex

d = Drawing(model, look_from=(0, -1, 0), look_up=(0, 0, 1), with_hidden=True)

svg = ExportSVG(scale=1/50, margin=5, unit=Unit.MM, line_weight=0.25)
svg.add_layer("visible", line_weight=0.35, line_color=ColorIndex.BLACK)
svg.add_layer("hidden",  line_weight=0.18, line_color=ColorIndex.LIGHT_GRAY,
              line_type=LineType.ISO_DOT)
svg.add_shape(d.visible_lines, layer="visible")
svg.add_shape(d.hidden_lines,  layer="hidden")
svg.write("elevation_front.svg")          # 13 510 bytes
```

---

## 5. `ExportDXF` — exact usage

### Constructor

```python
ExportDXF(version: str = ezdxf.DXF2013,          # "AC1027"; AC1009=R12, AC1032=2018
          unit: Unit = Unit.MM,                  # MC | MM | CM | M | IN | FT  (others raise ValueError)
          color: ColorIndex | None = None,       # default for layer "0"
          line_weight: float | None = None,      # mm; stored as round(lw*100)
          line_type: LineType | None = None)
```
`ezdxf.DXF2013 == "AC1027"`, `ezdxf.DXF2018 == "AC1032"`, `ezdxf.DXF12 == "AC1009"`.
Metric units get a linetype pattern scale of `2.54`; imperial `1`.

### `add_layer`

```python
add_layer(name: str, *,
          color: ColorIndex | None = None,
          line_weight: float | None = None,      # mm
          line_type: LineType | None = None) -> Self     # chainable
```
`ColorIndex`: `RED=1, YELLOW=2, GREEN=3, CYAN=4, BLUE=5, MAGENTA=6, BLACK=7, GRAY=8, LIGHT_GRAY=9`.
**There is no `WHITE`.**
`LineType`: ANSI family (`CONTINUOUS, BORDER, CENTER, DASHDOT, DASHED, DIVIDE, DOT, HIDDEN,
PHANTOM` each ×1/×.5/×2) plus the ISO family
(`ISO_DASH, ISO_DOT, ISO_LONG_DASH_DOT, ISO_DASH_SPACE, ISO_LONG_DASH_DOUBLE_DOT, …`).
Linetype definitions are added to the document lazily on first use.

### `add_shape` / `write`

```python
add_shape(shape: Shape | Iterable[Shape], layer: str = "") -> Self
write(file_name: PathLike | str | bytes | BytesIO, ascii_format: bool = True)
```
`write()` calls `ezdxf.zoom.extents(modelspace)` first, so the DXF opens zoomed to the drawing.

Accepted `shape` (all verified to produce the same 36 LINEs from one plan section):

| passed | entities |
|---|---|
| `Sketch` | 36 |
| `Compound(plan.faces())` | 36 |
| `Curve() + plan.edges()` | 36 |
| `ShapeList[Edge]` (`plan.edges()`) | 36 |
| a single `Face` | 6 |
| a single `Wire` | 6 |
| a **3D `Part`** | 228 — garbage, plus a warning |

Edges become `LINE`, `CIRCLE`, `ELLIPSE`, `SPLINE` depending on `GeomType`.

### Working two-layer plan export — runs

```python
import ezdxf
from build123d import *
from build123d.exporters import ColorIndex

Z = 1200.0
plan_flat = Pos(0, 0, -Z) * section(model, Plane.XY, height=Z)   # MUST be on z = 0

below = split(model, bisect_by=Plane.XY.offset(Z), keep=Keep.BOTTOM)
c = below.center()
beyond, _ = below.project_to_viewport(viewport_origin=(c.X, c.Y, 100000),
                                      viewport_up=(0, 1, 0))

dxf = ExportDXF(version=ezdxf.DXF2013, unit=Unit.MM,
                color=ColorIndex.BLACK, line_weight=0.25,
                line_type=LineType.CONTINUOUS)
dxf.add_layer("A-WALL",   color=ColorIndex.BLACK, line_weight=0.50)
dxf.add_layer("A-GLAZ",   color=ColorIndex.CYAN,  line_weight=0.18)
dxf.add_layer("A-BEYOND", color=ColorIndex.GRAY,  line_weight=0.13,
              line_type=LineType.ISO_DASH)
dxf.add_layer("A-GRID",   color=ColorIndex.RED,   line_type=LineType.ISO_LONG_DASH_DOT) \
   .add_layer("A-ANNO",   color=ColorIndex.GREEN)

dxf.add_shape(plan_flat, layer="A-WALL")
dxf.add_shape(beyond,    layer="A-BEYOND")
dxf.add_shape([Edge.make_line((-1000, 4000, 0), (11000, 4000, 0)),
               Edge.make_line(( 5000,-1000, 0), ( 5000, 9000, 0))], layer="A-GRID")
dxf.add_shape(Edge.make_circle(300, Plane.XY), layer="A-GLAZ")

dxf.write("plan_L0.dxf")                       # 34 777 bytes (ASCII)
dxf.write("plan_L0_bin.dxf", ascii_format=False)   # 24 005 bytes
```

Read back with ezdxf, verified:

```
dxfversion: AC1027   $INSUNITS: 4 (= mm)
layers:  ['0', 'A-ANNO', 'A-BEYOND', 'A-GLAZ', 'A-GRID', 'A-WALL', 'Defpoints']
entities: {'LINE': 86, 'CIRCLE': 1}
per layer: {'A-BEYOND': 48, 'A-WALL': 36, 'A-GRID': 2, 'A-GLAZ': 1}
```

`BytesIO` works too: `buf = BytesIO(); exp.write(buf)` → 19 525 bytes.

### `ExportSVG`

```python
ExportSVG(unit=Unit.MM, scale=1, margin=0, fit_to_stroke=True, precision=6,
          fill_color=None, line_color=ColorIndex.BLACK, line_weight=0.09,
          line_type=LineType.CONTINUOUS, dot_length=DotLength.INKSCAPE_COMPAT)
add_layer(name, *, fill_color=None, line_color=ColorIndex.BLACK,
          line_weight=0.09, line_type=LineType.CONTINUOUS) -> Self
add_shape(shape, layer="", reverse_wires=False)
write(path | BytesIO)
```
Unlike DXF, SVG **has a scale** and **can fill faces** — ideal for poché:

```python
svg = ExportSVG(unit=Unit.MM, scale=1/100, margin=10)
svg.add_layer("cut",    fill_color=ColorIndex.GRAY, line_color=ColorIndex.BLACK, line_weight=0.5)
svg.add_layer("beyond", line_color=ColorIndex.LIGHT_GRAY, line_weight=0.13,
              line_type=LineType.ISO_DASH)
svg.add_shape(plan_flat, layer="cut")
svg.write("plan_L0.svg")
```
produces (verified header):
```xml
<svg width="120.5mm" height="100.5mm" viewBox="-1025.0 -9025.0 12050.0 10050.0" ...>
  <g transform="scale(1,-1)" stroke-linecap="round">
    <g fill="rgb(128,128,128)" stroke="rgb(0,0,0)" stroke-width="50.0" id="cut">
```
Note the `scale(1,-1)` flip: SVG output is Y-up like the model. `stroke-width` is in **model units**
(0.5 mm × 100 = 50), so line weights come out right only at the declared `scale`.
Use `reverse_wires=True` if inner wires fill solid instead of punching holes.

### Round-trip

```python
imported = import_dxf("plan_L0.dxf")     # -> ShapeList, 87 edges (86 LINE + 1 CIRCLE)
```

---

## 6. Performance

Measured on this machine. 80 boxes of 1000 × 1000 × 3000 in a 10 × 8 grid.

### Union of 80 solids

| strategy | disjoint (1100 pitch) | overlapping (900 pitch) |
|---|---|---|
| `acc += box` in a loop | **1.701 s** | 0.541 s |
| `acc += box` inside `SkipClean()` | 0.915 s | 2.346 s ⚠️ |
| `Part() + [list_of_80]` | **0.040 s** | **0.359 s** |
| `boxes[0].fuse(*boxes[1:]).clean()` | 0.056 s | 0.361 s |
| `boxes[0].fuse(*boxes[1:])` no clean | 0.041 s | 0.359 s |

**Batching is 42× faster for disjoint solids and 1.5× for overlapping ones.**
`SkipClean` helps only when the result stays disjoint; on overlapping geometry it
*hurts* badly (638 faces carried forward instead of 6).

### 80 openings cut from one wall slab

| strategy | time |
|---|---|
| `acc -= cutter` in a loop | 2.096 s |
| `slab - (Part() + cutters)` | **0.184 s** |
| `slab.cut(*cutters).clean()` | **0.154 s** |

**~13× faster batched.**

### Realistic building scale

A two-storey villa — 10 m × 8 m, 250 mm external walls, an internal partition per floor,
10 window openings, a door, two slabs and a roof (final solid: 77 faces, 96 m³):

| step | time |
|---|---|
| full model build (≈20 boolean ops) | **0.147 s** |
| `section(v, Plane.XY, height=1200)` | **0.013 s** |
| `project_to_viewport` front, 36 vis / 118 hid | **0.007 s** |
| **full pipeline**: model + 2 plans + 4 elevations + 1 section + DXF + SVG + STEP + STL | **0.39 s** |

### Rules of thumb

* Booleans are **not** the bottleneck at villa scale — a whole house is sub-second.
* Always accumulate cutters/adders in a list and do **one** boolean.
  `wall - (Part() + openings)` not `for o in openings: wall -= o`.
* Keep each storey / element group as a separate `Part` and only fuse when you must.
  A `Compound` of many solids is fine for sectioning, HLR and export.
* If you go past ~500 solids, batch **and** avoid `clean()` on intermediates.

---

## 7. Gotchas

### Units — build123d is **unitless**; everything is mm by convention

```python
MM, CM, M, IN, FT = 1, 10, 1000, 25.4, 304.79999999999995
```
These are plain multipliers (`3 * M == 3000`). Nothing in the kernel knows about units.
`Unit.MM` etc. exist **only** for the exporters (they set `$INSUNITS` in DXF and the
`mm`/`in` suffix in SVG). `Unit.MC | MM | CM | M | IN | FT` — anything else raises
`ValueError: unit ... not supported`.

Work in **millimetres**. `304.79999999999995` for `FT` is a reminder not to build in feet.

### Tolerance

```python
TOLERANCE   = 1e-06     # build123d's geometric tolerance
TOL         = 0.01      # used for comparisons/rounding in some helpers
TOL_DIGITS  = 6
```
Empirically, a gap between two solids is closed by `fuse` up to about `1e-6`:

| gap (mm) | result of `slab + wall` |
|---|---|
| 0 | 1 solid, 8 faces |
| 1e-7 | 1 solid, 8 faces |
| 1e-6 | 1 solid, 8 faces |
| 1e-4 | **2 solids**, 12 faces |
| 1e-3, 0.01 | 2 solids |

So round your dimensions to a sane grid. Anything above ~1e-4 mm is a real gap.

### Empty shapes

```python
r = Box(1,1,1) & Pos(100,0,0) * Box(1,1,1)     # disjoint intersection
bool(r)        # False       <-- __bool__ is `_wrapped is not None`
r._wrapped     # None
r.wrapped      # AssertionError !!
r.volume       # 0
len(r.solids())# 0
Part().center()# AssertionError
```
**Test emptiness with `if shape:` — never with `shape.wrapped`.**

An empty **`section()`** is different: it returns a `Sketch` whose `_wrapped` is a valid but empty
compound, so `bool()` is `True` and `.area == 0.0`. Check `len(sk.faces())` there.

### `is_valid` is a property, not a method

```python
room.is_valid       # True         (calling room.is_valid() -> TypeError: 'bool' object is not callable)
room.is_manifold    # True         (property too)
```

### `Compound` vs `Part` for export

* `Part`, `Sketch`, `Curve` are all `Compound` subclasses; the 2D exporters accept **any** `Shape`
  and simply iterate `shape.edges()`. Type does **not** matter for DXF/SVG.
* What matters is **dimensionality and Z**: passing a 3D `Part` to `ExportDXF` emits every edge
  in the model, flattened — 228 nonsense lines plus
  `WARNING, exporting non-planar shape to 2D format. 444 points found outside the XY plane.`
  **Always `section()` or `Drawing()` first.**
* `Pos(0, 0, -z) * plan` before DXF, or you get the same warning (72 points, in the plan test).
  The check is `abs(z) > 1e-6` per point in `_convert_point`.
* `Part() + [a, b, c]` returns a **`Compound`**, not a `Part`. Re-wrap if you care:
  `Part(compound.wrapped)`.
* For STEP, `Compound(children=[...])` preserves `label` and `color` per child:
  ```python
  p = Box(10,10,10); p.label = "wall_01"; p.color = Color("saddlebrown")
  grp = Compound(children=[p]); grp.label = "storey_0"
  export_step(grp, "labels.step")
  back = import_step("labels.step")
  back.label            # 'storey_0'
  [c.label for c in back.children]   # ['wall_01']
  ```

### Exceptions you will actually hit

| call | exception |
|---|---|
| `Box(0, 1, 1)` | `Standard_DomainError` (bare message) |
| `extrude(sketch, 0)` | `Standard_ConstructionError: BRepSweep_Translation::Constructor` |
| `Part() - Box(1,1,1)` | `ValueError: Cannot subtract shape from empty compound` |
| `Part().center()` | `AssertionError` (bare) |
| `shape.wrapped` on an empty shape | `AssertionError` (bare) |
| `make_face(Polyline((0,0),(10,0),(10,10)))` | `ValueError: Face can only be created with closed wires` |
| `offset(Rectangle(100,100), amount=-60)` | `RuntimeError: Unexpected result type` (collapsed) |
| `Wire([disconnected edges])` | `ValueError: Edges are disconnected` |
| `fillet(Box(10,10,10).edges(), 6)` | `ValueError: Failed creating a fillet with radius of 6 … use max_fillet()` |
| `section(None, Plane.XY)` | `ValueError: No object to section` |
| `offset(closed_wire, side=Side.LEFT)` | `IndexError: list index out of range` — package bug |
| `room.is_valid()` | `TypeError: 'bool' object is not callable` |
| `Box(1,1,1) - Pos(100,0,0)*Box(1,1,1)` | **no exception** — returns the original |

Wrap OCCT calls generously: several failures surface as bare `Standard_*` / `AssertionError`
with no message.

### Selectors — the workhorses for buildings

```python
faces = model.faces()                                       # ShapeList
faces.filter_by(Axis.Z)                                     # faces whose normal ∥ Z   -> 30
faces.filter_by(Plane.XY)                                   # faces lying in/parallel to XY -> 30
faces.filter_by(lambda f: abs(f.normal_at().Z) < 1e-6)      # all vertical faces      -> 47
faces.filter_by(lambda f: abs(f.normal_at().Y + 1) < 1e-6)  # south-facing            -> 13
faces.sort_by(SortBy.AREA)[-1]                              # biggest face            -> 80 m2
faces.group_by(Axis.Z)                                      # buckets by height       -> 31
model.edges().filter_by(GeomType.LINE)                      # -> 228
```
`SortBy`: `LENGTH, RADIUS, AREA, VOLUME, DISTANCE`.
`Align`: `MIN, CENTER, MAX, NONE`. `Kind`: `ARC, INTERSECTION, TANGENT`.
`Side`: `LEFT, RIGHT, BOTH`. `Keep`: `ALL, BOTTOM, BOTH, INSIDE, OUTSIDE, TOP`.
`Mode`: `ADD, SUBTRACT, INTERSECT, REPLACE, PRIVATE`. `Until`: `NEXT, LAST, PREVIOUS, FIRST`.

### Misc

* `Pos(...) * shape` returns a **new** shape; the original is untouched. `copy.copy` /
  `copy.deepcopy` both work. `shape.moved(loc)` returns new; `shape.move(loc)` mutates.
* `Location((1000,0,0), (0,0,30))` → `.position`, `.orientation` (extrinsic XYZ degrees),
  `.inverse()`.
* `Plane * Location` composes: `Plane.XZ * Location((0,0,500))` → `Location(pos=(0,-500,0), ori=(90,0,0))`.
* `Plane(face)` builds a plane from any planar face.
* Annotation objects exist and produce **`Sketch`** (filled text/arrow outlines, no DXF `TEXT`
  entities): `Draft(font_size=…, unit=Unit.MM, decimal_precision=2)`, `DimensionLine(path, draft, …)`,
  `ExtensionLine(border, offset, draft, …)`, `TechnicalDrawing(page_size=PageSize.A1, drawing_scale=…)`,
  `Text(txt, font_size, …)`. `PageSize`: `A0…A10, LETTER, LEGAL, LEDGER`.
  Exported to DXF they become polylines/splines — fine for plotting, not editable as text in AutoCAD.
  If you need real AutoCAD `TEXT`/`MTEXT`/`DIMENSION`, post-process the DXF with `ezdxf` directly.

---

## 8. Cheat sheet

```python
from build123d import *
from build123d.exporters import Drawing, ColorIndex
from build123d.topology import SkipClean

# --- model
walls  = extrude(Rectangle(8000,6000, align=(Align.MIN,)*2)
                 - offset(Rectangle(8000,6000, align=(Align.MIN,)*2), -250, kind=Kind.INTERSECTION),
                 3000)
walls -= (Part() + [Pos(2000,-50,0) * Box(1000, 350, 2100, align=(Align.MIN,)*3)])

# --- plan
plan = Pos(0,0,-1200) * section(walls, Plane.XY, height=1200)     # Sketch on z=0

# --- vertical section
p    = Plane(origin=(4000,0,0), x_dir=(0,1,0), z_dir=(1,0,0))
sec  = p.to_local_coords(section(walls, p))                       # Sketch on z=0

# --- elevation with hidden lines
d    = Drawing(walls, look_from=(0,-1,0), look_up=(0,0,1), with_hidden=True)
elev = Pos(0, walls.center().Z, 0) * d.visible_lines               # true heights
hidn = Pos(0, walls.center().Z, 0) * d.hidden_lines

# --- DXF
dxf = ExportDXF(unit=Unit.MM, version="AC1027")
dxf.add_layer("A-WALL", color=ColorIndex.BLACK, line_weight=0.5)
dxf.add_layer("A-HIDN", color=ColorIndex.GRAY,  line_weight=0.13, line_type=LineType.HIDDEN)
dxf.add_shape(plan, layer="A-WALL")
dxf.add_shape(hidn, layer="A-HIDN")
dxf.write("out.dxf")

# --- 3D
export_step(walls, "out.step");  export_stl(walls, "out.stl")
```

---

## 9. Full verified pipeline

Ran end to end in **0.39 s**, producing
`plan_L0/L1.{dxf,svg}`, `elev_{N,S,E,W}.dxf`, `section_AA.dxf`, `villa.step`, `villa.stl`.

```python
"""3D villa -> plans, sections, elevations -> DXF + SVG."""
import os, time
from build123d import *
from build123d.exporters import Drawing, ColorIndex

OUT = "./out/"; os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- the model
W, D, T, TI, FH, SLAB = 10000.0, 8000.0, 250.0, 120.0, 3000.0, 200.0

def storey(z0):
    outer = Rectangle(W, D, align=(Align.MIN, Align.MIN))
    inner = offset(outer, amount=-T, kind=Kind.INTERSECTION)
    walls = extrude(outer - inner, FH - SLAB)
    walls += extrude(Pos(W/2 - TI/2, T) * Rectangle(TI, D - 2*T, align=(Align.MIN, Align.MIN)),
                     FH - SLAB)
    slab = extrude(outer, SLAB)
    return Pos(0, 0, z0) * (walls.moved(Location((0, 0, SLAB))) + slab)

def openings(z0):
    cut = Part()
    for x in (1500, 4000, 7000):
        cut += Pos(x, -50, z0 + SLAB + 900) * Box(1600, T + 100, 1400, align=(Align.MIN,)*3)
    for y in (1500, 4500):
        cut += Pos(-50, y, z0 + SLAB + 900) * Box(T + 100, 1400, 1400, align=(Align.MIN,)*3)
    cut += Pos(W/2 - TI/2 - 25, 2500, z0 + SLAB) * Box(TI + 50, 900, 2100, align=(Align.MIN,)*3)
    return cut

def build_villa():
    v  = storey(0) + storey(FH)
    v -= openings(0)                                          # batched cut per storey
    v -= openings(FH)
    v -= Pos(4500, -50, SLAB) * Box(1100, T + 100, 2200, align=(Align.MIN,)*3)
    v += Pos(0, 0, 2*FH) * extrude(Rectangle(W, D, align=(Align.MIN, Align.MIN)), SLAB)
    return v

t0 = time.perf_counter()
model = build_villa()          # 0.147 s -> 96.0 m3, 1 solid, 77 faces, valid, manifold

# ---------------------------------------------------------------- helpers
def plan_at(model, z):
    """(cut Sketch, beyond edges) both on Z = 0 and in true world XY."""
    cut_flat = Pos(0, 0, -z) * section(model, Plane.XY, height=z)
    lower = split(model, bisect_by=Plane.XY.offset(z), keep=Keep.BOTTOM)
    c = lower.center()
    vis, _ = lower.project_to_viewport(viewport_origin=(c.X, c.Y, c.Z + 1e6),
                                       viewport_up=(0, 1, 0), look_at=(c.X, c.Y, c.Z))
    return cut_flat, ShapeList(e.moved(Location((c.X, c.Y, 0))) for e in vis)

def elevation(model, direction, up=(0, 0, 1)):
    d = Drawing(model, look_from=direction, look_up=up, with_hidden=True)
    return d.visible_lines, d.hidden_lines

def vertical_section(model, origin, x_dir, z_dir):
    p = Plane(origin=origin, x_dir=x_dir, z_dir=z_dir)
    return p.to_local_coords(section(model, p))

# ---------------------------------------------------------------- plans
for lvl, z in [("L0", 1200), ("L1", FH + 1200)]:
    cut, bey = plan_at(model, z)                       # 6 cut faces, 48/49 beyond edges
    d = ExportDXF(unit=Unit.MM, version="AC1027")
    d.add_layer("A-WALL",   color=ColorIndex.BLACK, line_weight=0.50)
    d.add_layer("A-BEYOND", color=ColorIndex.GRAY,  line_weight=0.13,
                line_type=LineType.ISO_DASH)
    d.add_shape(cut, layer="A-WALL")
    d.add_shape(bey, layer="A-BEYOND")
    d.write(OUT + f"plan_{lvl}.dxf")

    s = ExportSVG(unit=Unit.MM, scale=1/100, margin=10)
    s.add_layer("cut",    fill_color=ColorIndex.GRAY, line_color=ColorIndex.BLACK, line_weight=0.5)
    s.add_layer("beyond", line_color=ColorIndex.LIGHT_GRAY, line_weight=0.13,
                line_type=LineType.ISO_DASH)
    s.add_shape(cut, layer="cut");  s.add_shape(bey, layer="beyond")
    s.write(OUT + f"plan_{lvl}.svg")

# ---------------------------------------------------------------- elevations
for name, dirn in [("N", (0,1,0)), ("S", (0,-1,0)), ("E", (1,0,0)), ("W", (-1,0,0))]:
    vis, hid = elevation(model, dirn)     # S: 36 vis/118 hid, W: 24/132, N & E: 4/148
    d = ExportDXF(unit=Unit.MM)
    d.add_layer("A-ELEV", color=ColorIndex.BLACK, line_weight=0.35)
    d.add_layer("A-HIDN", color=ColorIndex.GRAY,  line_weight=0.13, line_type=LineType.HIDDEN)
    d.add_shape(vis, layer="A-ELEV");  d.add_shape(hid, layer="A-HIDN")
    d.write(OUT + f"elev_{name}.dxf")

# ---------------------------------------------------------------- section A-A
sec = vertical_section(model, origin=(4500, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
d = ExportDXF(unit=Unit.MM)
d.add_layer("A-SECT", color=ColorIndex.BLACK, line_weight=0.60)
d.add_shape(sec, layer="A-SECT")
d.write(OUT + "section_AA.dxf")     # bbox 0..8000 x 0..6200, z = 0

export_step(model, OUT + "villa.step")
export_stl(model,  OUT + "villa.stl")
print(f"TOTAL {time.perf_counter()-t0:.2f}s")      # TOTAL 0.39s
```

**Caveat on the "beyond" layer:** projecting everything below the cut plane straight down
reproduces the cut outline itself (the wall tops at the cut plane are the top-most visible
surfaces). For a real floor plan, project **only** the objects you want shown dashed
(sills, stairs, counters, overhangs) rather than the whole lower half.
