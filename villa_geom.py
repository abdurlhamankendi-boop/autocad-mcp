"""
Builder-side geometry, computed from villa_design -- one answer, every builder.

villa_design.py is the design as DATA and belongs to the designers. It already
derives the house (fabric, outline, envelope, opening heights, fins, external
steps, probes). What it does not say is how a builder turns the newer parts of
that language into solids and sheets, and each builder used to answer that for
itself, with its own constants:

  * floors that are not the stacked house -- the annex ("AX", a single storey
    standing on the plot) and a roof pavilion ("RF") -- need walls, a floor
    slab, a roof slab and a parapet like the house, at their own LEVEL/CEIL;
  * every opening is cut at V.opening_z(); a window or a sliding door (SLIDE)
    is glazed, an external hinged door gets a leaf;
  * shading is V.SHADES boxes plus V.fins() -- never a loop in a builder (the
    west brise-soleil was `range(9)` in two builders and checked by nothing);
  * a title block prints numbers computed here, never typed ("VALIDATED 0 FATAL
    / 0 MAJOR" sat on every sheet while the validator reported 5 and 22);
  * the integration data (PROJECT_STATE s12): a part may be a y-z PROFILE
    (is_profile -- the sloping pool floor), the basin grate (grate_boxes),
    the glass guards (guard_boxes, guards_on), the gates (gates, gate_cuts)
    and the stair's real risers (stair_risers) -- one reading, every builder.

Nothing in here is a design decision. The few constants are modelling or
drawing conventions (glass thickness, frame section, parapet band), not
dimensions of the house.
"""

from __future__ import annotations

import datetime
import os

from shapely.geometry import Polygon, box as _box
from shapely.ops import unary_union

import villa_design as V

# ------------------------------------------------------------------ output
# A PROJECT design (projects\<name>\villa_design.py, run through
# run_project.py) names its own folder with OUT_NAME, so a run that forgets
# VILLA_OUT still cannot overwrite the villa's issued drawings.
DEFAULT_OUT = (os.path.join(r"C:\Users\lsire\OneDrive\Desktop", V.OUT_NAME)
               if getattr(V, "OUT_NAME", None) else r"C:\Users\lsire\OneDrive\Desktop\Villa")


def out_dir(*sub):
    """The deliverables folder (plus `sub`), created if missing.

    VILLA_OUT redirects the whole set -- sheets, manifest, render groups -- so
    a test or a dry run never overwrites the issued drawings. Unset, it is the
    Villa folder on the desktop, as it always was (a project's own folder
    when its design names one)."""
    base = os.environ.get("VILLA_OUT") or DEFAULT_OUT
    path = os.path.join(base, *sub)
    os.makedirs(path, exist_ok=True)
    return path


# ------------------------------------------------------------------ floors
# The house proper, stacked by V.envelope() (or V.massing()). A design with a
# basement stacks it too: STACKED = ("B1", "GF", "FF"); BELOW_GRADE_FLOORS
# names the storeys under the ground (no parapet, no base, no setback, drawn
# in section under the ground line); GROUND_FLOOR is the storey the garden,
# the forecourt and the front door are at.
STACKED = tuple(getattr(V, "STACKED", ("GF", "FF")))
BELOW_GRADE = tuple(getattr(V, "BELOW_GRADE_FLOORS", ()))
GROUND_FLOOR = getattr(V, "GROUND_FLOOR", "GF")

# Which plan sheet draws a floor that has no sheet of its own. The annex stands
# at ground level beside the house, so it belongs on the ground-floor sheets
# (A-102 / A-102P) and on the site plan.
SHEET_OF = dict(getattr(V, "SHEET_OF", {"AX": "GF"}))


def plan_sheets():
    """[(floor, sheet number, title or None)] -- every plan sheet, one table
    for every builder (villa_cad, villa_colour with a P suffix, villa_load,
    villa_verify, villa_show, the MCP server). A design may declare
    PLAN_SHEETS; the villa's default is A-102 GF, A-103 FF, and A-104 for a
    roof pavilion only when the roof has rooms. The title is None where the
    builder keeps its own wording."""
    if getattr(V, "PLAN_SHEETS", None):
        return [(f, n, t) for f, n, t in V.PLAN_SHEETS if f in V.floors()]
    out = [("GF", "A-102", None), ("FF", "A-103", None)]
    if "RF" in V.floors():
        out.append(("RF", "A-104", None))
    return out


def massing():
    """The design's own building groups (V.massing(): {group: [(op, part)]},
    openings already cut), or None -- the builders then stack the villa's
    envelope() the way they always have."""
    return V.massing() if hasattr(V, "massing") else None


def landscape_parts():
    """The design's own landscape groups (V.landscape_parts(): {group:
    [part]}), or None -- the builders then lay villa_colour's surfaces on
    the villa's terrain slab and raised garden."""
    return V.landscape_parts() if hasattr(V, "landscape_parts") else None


def poly_parts(part):
    """(polygon, z0, z1) for a poly part {'poly': g, 'z': (z0, z1)}, else None."""
    if isinstance(part, dict) and "poly" in part:
        return part["poly"], part["z"][0], part["z"][1]
    return None


def standalone_floors():
    """Floors built as their own single-storey volume -- the annex, a roof
    pavilion -- rather than inside the stacked house."""
    return [f for f in V.floors() if f not in STACKED]


def sheet_floors(sheet):
    """Floors drawn on the plan sheet for `sheet`, the sheet's own floor first."""
    return [sheet] + [f for f in V.floors()
                      if f != sheet and SHEET_OF.get(f) == sheet]


def ground_floors():
    """Floors that stand on the ground: what a site plan shows as buildings."""
    g = GROUND_FLOOR
    return [f for f in V.floors() if f == g or SHEET_OF.get(f) == g]


def footprint():
    """Every building on the plot at ground level, outside faces (house + annex)."""
    return unary_union([V.outline(f) for f in ground_floors()])


def annex_footprint():
    """Ground-standing buildings other than the house (the annex), or empty."""
    fls = [f for f in ground_floors() if f != "GF"]
    if not fls:
        return Polygon()
    return unary_union([V.outline(f) for f in fls])


# ---------------------------------------------------------------- openings
GLASS_T, REVEAL = 30.0, 60.0    # pane thickness; glass held back from reveal
FRAME_W, FRAME_D = 60.0, 80.0   # bronze frame section: face width, depth


def cut_box(o):
    """The void an opening cuts, (x0, y0, z0, x1, y1, z1): through the whole
    wall, at the height villa_design gives it. A SLIDE is cut like a door --
    floor to head -- because V.opening_z says so, not because a builder does."""
    x0, y0, x1, y1 = V.void_rect(o).bounds
    z0, z1 = V.opening_z(o)
    return (x0, y0, z0, x1, y1, z1)


def _centred(o, a0, a1, z0, z1, t):
    """A slab of thickness t on the wall's centre line, spanning a0..a1 along
    the opening and z0..z1 in height."""
    x0, y0, _, x1, y1, _ = cut_box(o)
    if o[2] == "h":
        c = (y0 + y1) / 2
        return (a0, c - t / 2, z0, a1, c + t / 2, z1)
    c = (x0 + x1) / 2
    return (c - t / 2, a0, z0, c + t / 2, a1, z1)


def _span(o):
    x0, y0, z0, x1, y1, z1 = cut_box(o)
    return ((x0, x1) if o[2] == "h" else (y0, y1)), z0, z1


def infill(o):
    """What fills an opening, as (what, box):
      'glass' -- a window, or a sliding door: a SLIDE is a full-height pane,
                 not a door leaf;
      'leaf'  -- an external hinged door;
    None for an internal door or a plain opening."""
    kind, rb = o[1], o[8]
    (a0, a1), z0, z1 = _span(o)
    if kind in (V.WIN, V.SLIDE):
        return "glass", _centred(o, a0 + REVEAL, a1 - REVEAL,
                                 z0 + REVEAL, z1 - REVEAL, GLASS_T)
    if kind == V.DOOR and rb is None:
        return "leaf", _centred(o, a0 + REVEAL, a1 - REVEAL,
                                z0, z1 - REVEAL, GLASS_T)
    return None


def frame(o):
    """Bronze frame of a glazed opening as (outer, hole, stiles): the section
    is `outer` less `hole`, plus `stiles` -- a sliding door's meeting stile,
    where its two leaves overlap. None for anything that is not glazed."""
    if o[1] not in (V.WIN, V.SLIDE):
        return None
    (a0, a1), lo, hi = _span(o)
    FR, D = FRAME_W, FRAME_D
    outer = _centred(o, a0, a1, lo, hi, D)
    hole = _centred(o, a0 + FR, a1 - FR, lo + FR, hi - FR, 2 * D)
    stiles = []
    if o[1] == V.SLIDE:
        m = (a0 + a1) / 2
        stiles.append(_centred(o, m - FR / 2, m + FR / 2, lo + FR, hi - FR, D))
    return outer, hole, stiles


# ----------------------------------------------------------------- shading
def _as_box(s):
    """(x0, y0, x1, y1, z0, z1) -- villa_design's order -- or a dict with those
    keys, to a builder box (x0, y0, z0, x1, y1, z1)."""
    if isinstance(s, dict):
        x0, y0, x1, y1, z0, z1 = (s[k] for k in ("x0", "y0", "x1", "y1", "z0", "z1"))
    else:
        x0, y0, x1, y1, z0, z1 = s[:6]
    return (min(x0, x1), min(y0, y1), min(z0, z1),
            max(x0, x1), max(y0, y1), max(z0, z1))


def fin_boxes():
    """Every fin from V.FIN_ARRAYS (via V.fins()), as builder boxes."""
    return [_as_box(f) for f in V.fins()]


def shade_boxes():
    """Every horizontal projection in V.SHADES, as builder boxes."""
    return [_as_box(s) for s in getattr(V, "SHADES", [])]


def solar_boxes():
    """Fins then shades: the bronze group (glTF 'fins', AutoCAD A-SHDE-3D)."""
    return fin_boxes() + shade_boxes()


def guard_boxes():
    """Every guard (V.guards(): glass balustrades at raised landings, on the
    garden platform's open edges and round the first-floor stair well), as
    builder boxes -- glTF group 'guards', AutoCAD layer A-GRDS-3D."""
    g = V.guards() if hasattr(V, "guards") else list(getattr(V, "GUARDS", []))
    return [_as_box(b) for b in g]


def guards_on(sheet):
    """Plan rectangles (x0, y0, x1, y1) of the guards standing on the floors
    a plan sheet draws: a guard belongs to the storey whose floor it stands
    on -- z0 from that floor's level up to the next floor, its ceiling and
    slab zone included (the glass on the upper flight of the stair starts
    as high as +4829, over the ground-floor ceiling, and belongs to it)."""
    spans = [(V.LEVEL[f], V.LEVEL[f] + V.CEIL[f] + V.SLAB)
             for f in sheet_floors(sheet) if f in V.LEVEL]
    return [(x0, y0, x1, y1) for x0, y0, z0, x1, y1, z1 in guard_boxes()
            if any(lo - 1 <= z0 < hi - 1 for lo, hi in spans)]


def stair_boxes():
    """The house stair (V.stair_parts(): solid treads, half-landing, top
    nosing), builder boxes -- glTF group 'stair', AutoCAD A-STRS-3D. Empty
    for design data without it."""
    return list(V.stair_parts()) if hasattr(V, "stair_parts") else []


def rail_parts():
    """Every handrail (V.rail_parts(): sloping bars as y-z / x-z profiles,
    and the posts of the outside ones as boxes) -- glTF group 'rails',
    AutoCAD A-RAIL-3D."""
    return list(V.rail_parts()) if hasattr(V, "rail_parts") else []


def rails_on(sheet):
    """Plan rectangles of the handrails over the floors a plan sheet draws
    (as guards_on: a rail belongs to the storey its flight starts from)."""
    if not hasattr(V, "handrails"):
        return []
    spans = [(V.LEVEL[f], V.LEVEL[f] + V.CEIL[f] + V.SLAB)
             for f in sheet_floors(sheet) if f in V.LEVEL]
    out = []
    for h in V.handrails():
        f = h["f"]
        if f["along"] == "y":
            r = (h["c0"], h["t0"], h["c1"], h["t1"])
        else:
            r = (h["t0"], h["c0"], h["t1"], h["c1"])
        # outside steps start below the GF (on the forecourt): they are drawn
        # with the ground floor. A house stair down to a basement is not.
        if any(lo - 1 <= f["z_foot"] < hi - 1 for lo, hi in spans) or (
                f["z_foot"] < V.GF and sheet == "GF" and not f.get("inside")):
            out.append(r)
    return out


def grate_boxes():
    """The walkable grate over the balance basin (V.grate()), builder boxes
    -- glTF group 'grate', AutoCAD layer A-GRAT-3D. Empty if not grated."""
    return list(V.grate()) if hasattr(V, "grate") else []


def is_profile(part):
    """True for a profile part -- y-z (V.yz_prism: the sloping pool floor, a
    handrail running north-south) or x-z (V.xz_prism: a handrail running
    east-west) -- False for a plain box (x0, y0, z0, x1, y1, z1)."""
    return isinstance(part, dict) and ("yz" in part or "xz" in part)


def profile_bounds(part):
    """(x0, y0, z0, x1, y1, z1) of a part, box or profile."""
    if not is_profile(part):
        return tuple(part)
    if "xz" in part:
        xs = [p[0] for p in part["xz"]]
        zs = [p[1] for p in part["xz"]]
        return (min(xs), part["y"][0], min(zs), max(xs), part["y"][1], max(zs))
    ys = [p[0] for p in part["yz"]]
    zs = [p[1] for p in part["yz"]]
    return (part["x"][0], min(ys), min(zs), part["x"][1], max(ys), max(zs))


# ------------------------------------------------------------------- stair
def stair_flights():
    """Risers per flight: a dog-leg splits V.RISERS as evenly as it can, the
    first flight taking the odd one (villa_elevations builds it the same;
    villa_design.stair_split says the same, and is read when present)."""
    if hasattr(V, "stair_split"):
        return list(V.stair_split())
    n, f = int(V.RISERS), int(V.STAIR_FLIGHTS)
    if f <= 1:
        return [n]
    first = -(-n // 2)
    return [first, n - first]


def stair_landing_edge():
    """y of the half-landing's edge (the last riser of the first flight), or
    None for a single flight. The first flight rises north from STAIR's y0
    on the west half, the second south on the east half back to y0."""
    if int(V.STAIR_FLIGHTS) <= 1:
        return None
    return V.STAIR[1] + (stair_flights()[0] - 1) * V.STAIR_GOING


def stair_risers():
    """Every riser as a plan line (x0, y, x1): at STAIR_GOING from the foot."""
    sx0, sy0, sx1, sy1 = V.STAIR
    g = V.STAIR_GOING
    fl = stair_flights()
    if len(fl) == 1:
        return [(sx0, sy0 + k * g, sx1) for k in range(fl[0])]
    mid = (sx0 + sx1) / 2.0
    yl = stair_landing_edge()
    out = [(sx0, sy0 + k * g, mid - 60) for k in range(fl[0])]
    out += [(mid + 60, yl - k * g, sx1) for k in range(fl[1])]
    return out


# ------------------------------------------------------------------- gates
def gates():
    """[(name, x0, x1, head)] in the street wall, from V.gates() -- head None
    is open to the sky. Older design data without gates() still gets its
    vehicle gate and the historical pedestrian gate."""
    if hasattr(V, "gates"):
        return list(V.gates())
    return [("VEHICLE GATE", V.GATE_X0, V.GATE_X1, None),
            ("PEDESTRIAN GATE", 15400.0, 16600.0, 2200.0)]


def gate_cuts(wall_h):
    """What each gate cuts from the boundary wall, as builder boxes: through
    the street wall, from the ground to its head (the wall's full height for
    the vehicle gate)."""
    T = getattr(V, "BOUNDARY_T", BW)
    return [(g0, V.PLOT_D - T - 200.0, 0.0, g1, V.PLOT_D + 200.0,
             wall_h if head is None else min(head, wall_h))
            for _n, g0, g1, head in gates()]


def overhead(sheet):
    """Plan rectangles (x0, y0, x1, y1) of the shading devices a plan sheet
    shows dashed: every fin or shade whose height range meets a storey drawn
    on that sheet, floor to the top of the slab over it."""
    spans = [(V.LEVEL[f], V.LEVEL[f] + V.CEIL[f] + V.SLAB)
             for f in sheet_floors(sheet) if f in V.LEVEL]
    out = []
    for x0, y0, z0, x1, y1, z1 in solar_boxes():
        if any(z1 > lo + 1 and z0 < hi - 1 for lo, hi in spans):
            out.append((x0, y0, x1, y1))
    return out


# ------------------------------------------------------ standalone storeys
PARAPET_BAND = 350.0            # as V.envelope(): parapet thinner than wall


def storey(fl):
    """A floor built as its own single-storey volume, stacked the way the
    house is: floor slab under the finished floor, walls from floor to
    ceiling, roof slab over them, parapet on the roof edge, and a stone base
    under the slab where the floor stands clear of the ground.

    A roof pavilion stands on the house roof, so only what overhangs that roof
    needs a floor slab of its own, and it has no base.

    Returns shapely footprints and levels (mm):
      out, inner, edge          outside face, internal envelope, parapet band
      z0, z1                    finished floor, ceiling (= top of walls)
      slab_poly, slab           floor-slab footprint (None if none), (z0, z1)
      roof, parapet             (z0, z1) of each, over `out` / `edge`
      base                      (z0, z1) over `out`, or None
    """
    _, _, inner = V.fabric(fl)
    out = inner.buffer(V.WALL, join_style=2, mitre_limit=8)
    z0 = float(V.LEVEL[fl])
    z1 = z0 + float(V.CEIL[fl])
    edge = out.difference(out.buffer(-PARAPET_BAND, join_style=2, mitre_limit=8))
    slab_poly, base = out, None
    if fl == "RF":
        slab_poly = out.difference(V.envelope()["upper"])
    else:
        ground = V.ground_at(out.representative_point().y)
        if z0 - V.SLAB > ground + 1.0:
            base = (ground, z0 - V.SLAB)
    if slab_poly.is_empty or slab_poly.area < 1.0:
        slab_poly = None
    return {"out": out, "inner": inner, "edge": edge, "z0": z0, "z1": z1,
            "slab_poly": slab_poly, "slab": (z0 - V.SLAB, z0),
            "roof": (z1, z1 + V.SLAB),
            "parapet": (z1 + V.SLAB, z1 + V.SLAB + V.PARAPET),
            "base": base}


def roof_parapet(E=None):
    """The house's roof parapet (V.envelope()['parapet_roof']) less wherever a
    roof pavilion stands on it -- a parapet does not run through a room."""
    E = E or V.envelope()
    g = E["parapet_roof"]
    if "RF" in V.floors():
        g = g.difference(V.outline("RF"))
    return g


# ------------------------------------------------------------------ probes
def _pt(g):
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda p: p.area)
    c = g.representative_point()
    return c.x, c.y


def _clear_band(out, inner):
    """External wall band clear of every opening on any floor (+300 each side)."""
    band = out.difference(inner)
    cuts = [V.void_rect(o).buffer(300, join_style=2) for o in V.OPENINGS]
    return band.difference(unary_union(cuts)) if cuts else band


def probes():
    """V.probes() plus what the newer language adds, (name, x, y, z, expect, r).

    Shared by villa_gltf.verify() and villa_3d_verify.py like V.probes():
      * every standalone storey has a floor slab, a roof slab, a parapet and a
        solid external wall, and is open to its ceiling;
      * every SLIDE is cut to the floor and to the head (a window's cut would
        pass the mid-height probe and fail these);
      * every shade box, and the first fin of the array, is solid."""
    out = list(V.probes())
    for fl in standalone_floors():
        S = storey(fl)
        rooms = [V.net_poly(r) for r in V.rooms_on(fl)]
        x, y = _pt(max(rooms, key=lambda g: g.area))
        out.append((f"{fl} roof slab", x, y, S["z1"] + V.SLAB / 2, "solid", 200.0))
        out.append((f"{fl} open to its ceiling", x, y, S["z1"] - 300, "void", 200.0))
        if S["slab_poly"] is not None:
            sx, sy = (x, y) if S["slab_poly"].contains(
                _box(x - 1, y - 1, x + 1, y + 1)) else _pt(S["slab_poly"])
            out.append((f"{fl} floor slab", sx, sy, S["z0"] - V.SLAB / 2,
                        "solid", 200.0))
        band = _clear_band(S["out"], S["inner"])
        if not band.is_empty:
            bx, by = _pt(band)
            out.append((f"{fl} external wall", bx, by, (S["z0"] + S["z1"]) / 2,
                        "solid", 120.0))
        ex, ey = _pt(S["edge"])
        out.append((f"{fl} parapet", ex, ey, S["parapet"][0] + V.PARAPET / 2,
                    "solid", 120.0))
    for o in V.OPENINGS:
        if o[1] != V.SLIDE:
            continue
        x0, y0, z0, x1, y1, z1 = cut_box(o)
        # a quarter along, not the middle: the meeting stile is in the middle
        cx = x0 + (x1 - x0) * (0.25 if o[2] == "h" else 0.5)
        cy = y0 + (y1 - y0) * (0.5 if o[2] == "h" else 0.25)
        out.append((f"{o[0]} slide {o[7]}: cut to the floor", cx, cy, z0 + 150,
                    "void", 120.0))
        out.append((f"{o[0]} slide {o[7]}: cut to the head", cx, cy, z1 - 150,
                    "void", 120.0))
    for i, b in enumerate(shade_boxes()):
        r = max(20.0, min(120.0, 0.4 * min(b[3] - b[0], b[4] - b[1], b[5] - b[2])))
        out.append((f"shade {i}", (b[0] + b[3]) / 2, (b[1] + b[4]) / 2,
                    (b[2] + b[5]) / 2, "solid", r))
    fb = fin_boxes()
    if fb:
        b = fb[0]
        r = max(20.0, min(120.0, 0.4 * min(b[3] - b[0], b[4] - b[1])))
        out.append(("fin 0", (b[0] + b[3]) / 2, (b[1] + b[4]) / 2,
                    (b[2] + b[5]) / 2, "solid", r))
    return out


def controls():
    """Points that must be SOLID fabric, (name, x, y, z, r) -- the fixed
    control points villa_3d_verify.py used to type in (north wall at y 23800,
    ...), derived instead, so moving a wall moves its probe with it."""
    E = V.envelope()
    band_gf = _clear_band(E["out_gf"], E["in_gf"])
    band_ff = _clear_band(E["out_ff"], V.fabric("FF")[2])

    def face(band, side):
        x0, y0, x1, y1 = band.bounds
        clip = {"N": _box(x0, y1 - V.WALL, x1, y1), "W": _box(x0, y0, x0 + V.WALL, y1),
                "E": _box(x1 - V.WALL, y0, x1, y1), "S": _box(x0, y0, x1, y0 + V.WALL)}
        g = band.intersection(clip[side])
        return _pt(g if not g.is_empty else band)

    R = 250.0
    out = []
    x, y = face(band_gf, "N")
    out.append(("north wall", x, y, V.GF + 1500, R))
    x, y = face(band_gf, "W")
    out.append(("west wall", x, y, V.GF + 1500, R))
    x, y = face(band_ff, "E")
    out.append(("east wall", x, y, V.FF + 1500, R))
    # a design whose GF slab has a hole (a stair well to a basement) says so
    # with envelope()['gf_slab']; the control stands on the slab, not the well
    x, y = _pt(E["gf_slab"].intersection(E["in_gf"]) if "gf_slab" in E else E["in_gf"])
    out.append(("ground slab", x, y, V.GF - V.SLAB / 2, R))
    x, y = _pt(E["upper"])
    out.append(("roof slab", x, y, V.RF + V.SLAB / 2, R))
    out.append(("boundary wall", V.PLOT_W / 2, 175.0, 1200.0, 120.0))
    return out


# ------------------------------------------------------- title-block numbers
BW = getattr(V, "BOUNDARY_T", 350.0)     # boundary wall thickness (design data)
BH = getattr(V, "BOUNDARY_H", 2400.0)    # and height


def plot_area():
    return V.PLOT_W * V.PLOT_D / 1e6


def floor_areas(fl):
    """(net, gross) m2 of one floor: net = sum of rooms' net floor (what the
    room labels and the schedule say), gross = outside face of its walls."""
    net = sum(V.net_area(r) for r in V.rooms_on(fl))
    gross = V.outline(fl).area / 1e6 if V.rooms_on(fl) else 0.0
    return net, gross


FLOOR_NAME = {"AX": "ANNEX", "GF": "GF", "FF": "FF", "RF": "ROOF",
              **dict(getattr(V, "FLOOR_NAME", {}))}


def area_text(fls):
    """'GF NET 187.3 / GROSS 226.3 m2  +  ANNEX NET .. / GROSS .. m2'."""
    parts = []
    for fl in fls:
        if not V.rooms_on(fl):
            continue
        net, gross = floor_areas(fl)
        parts.append(f"{FLOOR_NAME.get(fl, fl)} NET {net:.1f} / GROSS {gross:.1f} m2")
    return "   +   ".join(parts) if parts else "NO ROOMS"


def site_numbers():
    """GFA, building footprint and site cover, all computed."""
    fp = footprint().area / 1e6
    return {"gfa": V.gross_area(), "footprint": fp, "plot": plot_area(),
            "cover": 100.0 * fp / plot_area()}


def site_text():
    s = site_numbers()
    return (f"GFA (GROSS) {s['gfa']:.1f} m2 = {s['gfa'] * 10.7639:.0f} sq ft   "
            f"FOOTPRINT {s['footprint']:.1f} m2   COVER {s['cover']:.1f}%")


def validation():
    """The validator's real counts, and the furniture check's."""
    iss = V.validate()
    count = lambda tag: sum(1 for i in iss if i.startswith(tag))
    furn = None
    try:
        import villa_furniture_spec as F
        furn = len(F.check())
    except Exception:                       # a broken layout is reported, not fatal
        furn = None
    return {"fatal": count("[FATAL]"), "major": count("[MAJOR]"),
            "note": count("[NOTE"), "furniture": furn, "issues": iss}


def validation_text(v=None):
    v = v or validation()
    s = f"VALIDATION  {v['fatal']} FATAL / {v['major']} MAJOR"
    if v.get("furniture") is not None:
        s += f"   FURNITURE {v['furniture']} ISSUE(S)"
    return s


def bedroom_count():
    roles = getattr(V, "ROLE", {}) or {}
    if roles:
        return sum(1 for r in V.ROOMS
                   if roles.get(r[0]) in ("bedroom", "master_bedroom"))
    return sum(1 for r in V.ROOMS if "BEDROOM" in r[0] and "ENS" not in r[0])


def project_line():
    name = getattr(V, "PROJECT_TITLE", None) or "VILLA"
    return f"{name}  --  {bedroom_count()} BEDROOM, {plot_area():.0f} m2 PLOT"


def design_date():
    """The date of the design data the sheet was drawn from."""
    return datetime.date.fromtimestamp(os.path.getmtime(V.__file__)).isoformat()


def forecourt():
    """(depth, width) of the forecourt, MEASURED as validate() check 8 does:
    from the house's street face to the boundary wall -- not read from
    PORCH_Y0, which once sat 600 mm inside the house."""
    house = V.outline("GF")
    front = house.intersection(_box(V.PORCH_X0, 0, V.PORCH_X1, V.PLOT_D))
    face = front.bounds[3] if not front.is_empty else V.PORCH_Y0
    return (V.PLOT_D - BW) - face, V.PORCH_X1 - V.PORCH_X0


def forecourt_text():
    d, w = forecourt()
    return f"{d:.0f} x {w:.0f}"


def pool_text():
    w, l = V.POOL_X1 - V.POOL_X0, V.POOL_Y1 - V.POOL_Y0
    return f"{w:.0f} x {l:.0f}   {w * l / 1e6:.1f} m2"


# --------------------------------------------------------------- furniture
def furniture():
    """[(floor, placements)] from villa_furniture_spec, the optional ANNEX and
    ROOF lists included -- GF and FF first, so the manifest of a design with
    neither is unchanged."""
    import villa_furniture_spec as F
    out = [("GF", list(F.GROUND)), ("FF", list(F.FIRST)),
           ("AX", list(getattr(F, "ANNEX", None) or [])),
           ("RF", list(getattr(F, "ROOF", None) or []))]
    # a basement's list goes LAST and only when there is one, so a design
    # without it produces the same manifest as before
    if getattr(F, "BASEMENT", None):
        out.append(("B1", list(F.BASEMENT)))
    return out


def sheet_furniture(sheet):
    """[(floor, (key, x, y, rot))] drawn on the plan sheet for `sheet`."""
    fls = sheet_floors(sheet)
    return [(fl, it) for fl, lst in furniture() if fl in fls for it in lst]


# ------------------------------------------------ design groups -> parts
# One reading of a design's own massing() / landscape_parts() for BOTH 3D
# builders -- villa_gltf (build123d) and villa_3d_build (AutoCAD) -- so the
# two models cannot disagree about which parts make which group. A part is a
# box (x0, y0, z0, x1, y1, z1), a y-z / x-z profile (is_profile) or a poly
# part {'poly': shapely geometry, 'z': (z0, z1)} (poly_parts).

def part_is_empty(part):
    """True for a poly part with no area or no height (an empty
    intersection, a void that misses its floor): it makes no solid."""
    pp = poly_parts(part)
    if pp is None:
        return False
    g, z0, z1 = pp
    return g is None or g.is_empty or g.area < 1.0 or z1 - z0 <= 0.0


def building_parts():
    """The design's building groups as both builders make them,
    {group: [(op, part)]} in the design's order -- or None when the design
    has no massing() (the builders then stack the villa's envelope() as they
    always have).

    Each group is normalised to its adds, then its cuts (a group IS
    union(adds) - union(cuts)); the landings and flights at the external
    doors (V.external_steps(), empty when every threshold is level) follow
    on 'base', added after its cuts as the villa's base has them. Empty
    poly parts are dropped and a group with nothing to add is left out. The
    openings are already cut by the design: a builder applies these ops in
    order and cuts nothing else from these groups."""
    m = massing()
    if m is None:
        return None
    out = {}
    for grp, ops in m.items():
        adds, cuts = [], []
        for op, p in ops:
            if op not in ("add", "cut"):
                raise ValueError(f"massing group {grp!r}: unknown op {op!r}")
            if not part_is_empty(p):
                (adds if op == "add" else cuts).append(p)
        if adds:
            out[grp] = [("add", p) for p in adds] + [("cut", p) for p in cuts]
    steps = [tuple(b) for b in (V.external_steps() if hasattr(V, "external_steps") else [])]
    if steps:
        out.setdefault("base", [])
        out["base"] += [("add", b) for b in steps]
    return out


def site_parts():
    """The design's landscape, {group: [part]} (V.landscape_parts(): terrain,
    paving, deck, lawn, planting, gravel, drive ...), empty poly parts
    dropped and empty groups left out -- or None when the design has none
    (the builders then lay villa_colour's surfaces on the villa's terrain
    slab and raised garden). It replaces only the terrain and the surfaces:
    glass and door leaves (infill) and the water (water_parts) are the
    builders' own, from OPENINGS and pool_parts()."""
    L = landscape_parts()
    if L is None:
        return None
    out = {}
    for grp, parts in L.items():
        ps = [p for p in parts if not part_is_empty(p)]
        if ps:
            out[grp] = ps
    return out


def water_parts():
    """The water group's parts, in the order the builders union them: the
    villa's rill when the design has one (RILL_W: on AXIS from the pool's
    end to the wings, 75 deep on the raised garden), then V.pool_parts()[2]
    -- the pool on its floor profile, a balance basin, the sheet over a
    weir. A design without a rill (no RILL_W) gets none."""
    out = []
    if hasattr(V, "RILL_W"):
        gz = getattr(V, "GARDEN_Z", 700.0)
        out.append((V.AXIS - V.RILL_W / 2, V.POOL_Y1, gz,
                    V.AXIS + V.RILL_W / 2, V.WG_Y0, gz + 75))
    return out + list(V.pool_parts()[2])


# The AutoCAD layer (and ACI colour) of every building group, by the glTF
# group name -- villa_3d_build puts each on its own A-*-3D layer, which is
# what villa_3d_verify probes. A group not named here goes on A-<NAME>-3D.
LAYER_3D = {"walls": ("A-WALL-3D", 32), "slabs": ("A-SLAB-3D", 8),
            "roof": ("A-ROOF-3D", 253), "base": ("A-BASE-3D", 44),
            "stone": ("A-STON-3D", 250), "fins": ("A-SHDE-3D", 42),
            "pool": ("A-POOL-3D", 254), "boundary": ("A-BDRY-3D", 43),
            "grate": ("A-GRAT-3D", 42), "guards": ("A-GRDS-3D", 151),
            "stair": ("A-STRS-3D", 44), "rails": ("A-RAIL-3D", 42)}
# ... and of every landscape group (the L-* layers)
SITE_LAYER = {"terrain": "L-TERRAIN", "lawn": "L-LAWN", "planting": "L-PLANT",
              "gravel": "L-GRAVEL", "paving": "L-PAVE", "deck": "L-DECK",
              "drive": "L-DRIVE", "water": "L-WATER", "glass": "L-GLAZ",
              "door": "L-DOOR"}
# The fabric an opening is cut through, as AutoCAD layers: the render walls,
# a stone skin over them, and the basement's walls (villa_window_check).
WALL_LAYERS_3D = ("A-WALL-3D", "A-STON-3D", "A-BASE-3D")


def layer_3d(group):
    """(layer, ACI) of a building group in the AutoCAD model."""
    if group in LAYER_3D:
        return LAYER_3D[group]
    return f"A-{group.upper()[:4]}-3D", 7


def site_layer(group):
    """The L-* layer of a landscape group in the AutoCAD model."""
    return SITE_LAYER.get(group) or f"L-{group.upper()[:6]}"


# ------------------------------------------------- plan sheets (2-D builders)
# What villa_cad / villa_colour draw on a plan sheet for the newer design
# language: several house stairs (V.STAIRS through V.flights()), the
# building's own projections (V.OVERHANGS, V.BALCONY), fins the plan cuts,
# stone (V.STONE_ZONES, V.STONE_FREE). Each is empty for design data without
# the hook, so the villa's sheets do not change.
PLAN_CUT = 1200.0               # the plan's cut plane over its floor (convention)


def storey_span(fl):
    """(finished floor, top of the slab over it) of a storey -- the height a
    plan sheet of that storey owns (guards_on, overhead use the same)."""
    return V.LEVEL[fl], V.LEVEL[fl] + V.CEIL[fl] + V.SLAB


def balcony():
    """((x0, y0, x1, y1), level) of V.BALCONY, or None. The level is the
    floor its guards stand on (V.guards_labelled() kind 'balcony'), else the
    highest storey whose outline the balcony adjoins."""
    b = getattr(V, "BALCONY", None)
    if not b:
        return None
    x0, y0, x1, y1 = (float(v) for v in b[:4])
    lv = None
    if hasattr(V, "guards_labelled"):
        zs = [g[4] for k, g in V.guards_labelled() if k == "balcony"]
        lv = min(zs) if zs else None
    if lv is None:
        r = _box(x0, y0, x1, y1).buffer(1.0)
        lv = max((V.LEVEL[f] for f in V.floors()
                  if f not in BELOW_GRADE and V.outline(f).intersects(r)), default=None)
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), lv


def balcony_on(sheet):
    """The balcony's plan rectangle when it is a floor of this sheet's storey
    (walked on, drawn seen with its guards), else None."""
    b = balcony()
    if b is None or b[1] is None:
        return None
    if any(abs(V.LEVEL[f] - b[1]) < 1.0 for f in sheet_floors(sheet) if f in V.LEVEL):
        return b[0]
    return None


def overhangs_over(sheet):
    """Plan rectangles (x0, y0, x1, y1) of the building's own projections
    passing OVER a storey the plan sheet draws -- V.OVERHANGS (a cantilevered
    floor, a roof frame) and the balcony's slab (SLAB under its level): the
    underside above that floor, no higher than the top of the slab over it
    (a roof frame at the roof slab's soffit belongs to the top storey). The
    plan shows them dashed, as it shows overhead()'s shading."""
    boxes = [_as_box(o) for o in (getattr(V, "OVERHANGS", None) or [])]
    b = balcony()
    if b is not None and b[1] is not None:
        (x0, y0, x1, y1), lv = b
        boxes.append((x0, y0, lv - V.SLAB, x1, y1, lv))
    spans = [storey_span(f) for f in sheet_floors(sheet) if f in V.LEVEL]
    return [(x0, y0, x1, y1) for x0, y0, z0, x1, y1, z1 in boxes
            if any(lo + 1.0 < z0 <= hi + 1.0 for lo, hi in spans)]


def cut_fins(sheet):
    """Plan rectangles of the fins the plan's cut plane (PLAN_CUT over the
    floor) passes through: drawn cut, solid -- the rest of overhead() dashed."""
    out = []
    for f in sheet_floors(sheet):
        if f not in V.LEVEL:
            continue
        z = V.LEVEL[f] + PLAN_CUT
        out += [(x0, y0, x1, y1) for x0, y0, z0, x1, y1, z1 in fin_boxes()
                if z0 <= z <= z1]
    return out


def stone_on(sheet):
    """[(kind, (x0, y0, x1, y1))] of the stone the plan's cut plane passes
    through: 'clad' for V.STONE_ZONES (a cladding skin on a wall face),
    'free' for V.STONE_FREE (free-standing stone walls and piers). Both are
    builder boxes (x0, y0, z0, x1, y1, z1)."""
    out = []
    for kind, lst in (("clad", getattr(V, "STONE_ZONES", None) or []),
                      ("free", getattr(V, "STONE_FREE", None) or [])):
        for s in lst:
            x0, y0, z0, x1, y1, z1 = s[:6]
            for f in sheet_floors(sheet):
                if f in V.LEVEL and z0 - 1.0 <= V.LEVEL[f] + PLAN_CUT <= z1 + 1.0:
                    out.append((kind, (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))))
                    break
    return out


def _floor_at(z):
    return next((f for f in V.floors() if f in V.LEVEL and abs(V.LEVEL[f] - z) < 1.0), None)


def stair_names():
    """The house stairs, by name (V.STAIRS), in the design's order; one
    unnamed 'stair' for design data with a single STAIR."""
    if hasattr(V, "STAIRS"):
        return [s["name"] for s in V.STAIRS]
    return ["stair"] if hasattr(V, "flights") else []


def stair_flights_of(name):
    """The inside flights of the house stair `name` (V.flights() carries a
    'stair' key when the design has several; without it every inside flight
    is the one house stair)."""
    if not hasattr(V, "flights"):
        return []
    fl = [f for f in V.flights() if f.get("inside")]
    if any("stair" in f for f in fl):
        return [f for f in fl if f.get("stair") == name]
    return fl if name == "stair" else []


def stair_floors(name):
    """(bottom floor, top floor) a house stair joins: the floors at the level
    of its lowest foot and of its highest arrival (None where no floor is)."""
    fl = stair_flights_of(name)
    if not fl:
        return None, None
    lo = min(f["z_foot"] for f in fl)
    hi = max(f["z_foot"] + f["n"] * f["rise"] for f in fl)
    return _floor_at(lo), _floor_at(hi)


def stair_role(name, sheet):
    """How the plan sheet for `sheet` shows the house stair `name`: 'up' on
    the storey at its foot, 'down' on the floor it arrives at, 'through' on a
    storey it passes, None when it is not on this sheet."""
    lo, hi = stair_floors(name)
    if lo is None or hi is None:
        return None
    zl, zh = V.LEVEL[lo], V.LEVEL[hi]
    for f in sheet_floors(sheet):
        if f not in V.LEVEL:
            continue
        z = V.LEVEL[f]
        if abs(z - zl) < 1.0:
            return "up"
        if abs(z - zh) < 1.0:
            return "down"
        if zl < z < zh:
            return "through"
    return None


def flights_on(sheet):
    """[(flight, role)] -- every inside flight drawn on the plan sheet for
    `sheet`, a whole stair at a time: from the floor at its foot ('up') to
    the floor it arrives at ('down'). A dog-leg's upper flight is on its
    foot's sheet too (above the cut, overhead) and its lower flight on the
    arrival's sheet (seen down the well)."""
    out = []
    for name in stair_names():
        role = stair_role(name, sheet)
        if role:
            out += [(f, role) for f in stair_flights_of(name)]
    return out


def stair_landings():
    """[(stair name, (x0, y0, x1, y1), level)] -- every half-landing, from
    V.stair_landing() (a design's one dog-leg), matched to its stair: the one
    whose flights it adjoins."""
    L = V.stair_landing() if hasattr(V, "stair_landing") else None
    if not L:
        return []
    rect_, lv = L
    r = _box(*rect_).buffer(5.0)
    for name in stair_names():
        for f in stair_flights_of(name):
            t0, t1 = V.flight_run(f)
            if r.intersects(_box(*V.flight_plan(f, t0, t1))):
                return [(name, tuple(rect_), lv)]
    return [(None, tuple(rect_), lv)]


def voids_on(sheet):
    """[(name, (x0, y0, x1, y1))] of the V.VOIDS cutting a floor of this sheet."""
    fls = set(sheet_floors(sheet))
    return [(v[0], (v[1], v[2], v[3], v[4])) for v in getattr(V, "VOIDS", [])
            if fls & set(v[5])]


# --------------------------------------------------------- AutoCAD documents
def find_doc(app, name, folder=None):
    """The open AutoCAD drawing called `name` -- and, when `folder` is given,
    saved in that folder (or never saved yet). Two projects write drawings
    with the same NAMES (VILLA_3D_MODEL.dwg, VILLA_A102.dwg) into different
    folders, and a lookup by name alone finds the other project's: the
    Fairway's 3D build would have closed the villa's open model unsaved, and
    its verifier would have probed the wrong building. Every COM script
    looks its drawings up through this."""
    want = os.path.normcase(os.path.abspath(folder)) if folder else None
    for i in range(app.Documents.Count):
        d = app.Documents.Item(i)
        if str(d.Name).lower() != str(name).lower():
            continue
        if want is None:
            return d
        try:
            full = str(d.FullName or "")
        except Exception:                   # a drawing still opening
            full = ""
        if not full or os.path.normcase(os.path.dirname(os.path.abspath(full))) == want:
            return d
    return None
