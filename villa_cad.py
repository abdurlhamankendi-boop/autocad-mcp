"""Author the villa drawing set as DXF, straight from villa_design.py.

Walls are derived, never typed: the gaps between room rectangles ARE the
partitions, so a wall cannot contradict the schedule. Openings are subtracted
from the wall polygons, which is why every door is a real hole rather than a
line drawn over solid poche.

Furniture is deliberately NOT drawn here. Real ACA content blocks are inserted
over COM by villa_load.py -- a rectangle labelled "bed" is exactly what the
client rejected. furniture_manifest() tells it where, for every floor.

The annex (floor "AX") is drawn on the ground-floor sheet and the site plan;
sliding doors (SLIDE) are glazed openings with a slider line, never a swing;
fins and V.SHADES are dashed overhead outlines; every number in a title block
is computed (villa_geom), including the validator's real counts. The glass
guards (V.guards) are drawn on A-GRDS on the sheet of the floor they stand
on; the site plan draws the gates from V.gates(), the pool's floor breaks and
depths, the basin grate and the plant vault; the stair is drawn riser by
riser at STAIR_GOING.

VILLA_OUT (environment) redirects the output folder.

Project designs (projects\\<name>, run through run_project.py) add hooks the
villa does not have, and each is drawn only when the design provides it:
PLAN_SHEETS (sheet numbers and titles, via villa_geom.plan_sheets, the level
in the title block, and a PNG beside every DXF), STAIRS (every house stair
through V.flights(), drawn on the storey at its foot -- UP, cut at the plan's
cut plane, dashed above it -- and on the floor it arrives at -- DN, seen down
the void), OVERHANGS / BALCONY (dashed over the storey below, the balcony
drawn on its own floor), cut fins, STONE_ZONES / STONE_FREE, POOL_LEDGE,
POOL_LABEL, SITE_TREES and the forecourt RAMP on the site plan. `--png`
renders PNGs for the villa too (plan_dxf.render_png).
"""

from __future__ import annotations

import json
import math
import os
import sys

import ezdxf
from shapely.geometry import box
from shapely.ops import unary_union

import plan_dxf as PD
import villa_design as V
import villa_furniture_spec as F
import villa_geom as G
import villa_svg as SVG

OUT = G.out_dir()

TXT_NAME, TXT_AREA, TXT_SM = 260.0, 200.0, 180.0
SHADE_LAYER = "A-SHDE-OVHD"     # overhead shading, dashed

# Project hooks -- the villa has none of them, so its sheets are unchanged.
MULTI_STAIR = hasattr(V, "STAIRS")             # several stairs, via V.flights()
PROJECT_SHEETS = bool(getattr(V, "PLAN_SHEETS", None))
STAIR_OVHD = "A-FLOR-STRS-OVHD"   # treads above the plan's cut plane, dashed
FIN_LAYER = "A-SHDE-FINS"         # fins the plan cuts, solid
CLAD_LAYER = "A-WALL-CLAD"        # stone cladding skin on a wall face
BGRD_LAYER = "A-FLOR-BGRD"        # a storey below grade, dotted, site plan


def want_png():
    """A PNG beside every DXF: always for a project design, on request
    (--png) for the villa -- whose issued set is DXF only."""
    return PROJECT_SHEETS or "--png" in sys.argv


def save(p, path):
    """Save the DXF, and its PNG when want_png()."""
    p.doc.saveas(path)
    if want_png():
        PD.render_png(p.doc, path[:-4] + ".png")
    return path


# ------------------------------------------------------------------ helpers
def rings(geom):
    """(exterior, [interiors]) for every polygon in a possibly-multi geometry."""
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        yield (list(g.exterior.coords),
               [list(r.coords) for r in g.interiors])


def draw_fabric(p, geom, layer):
    """Wall polygons: outline on `layer`, solid poche behind it."""
    for ext, holes in rings(geom):
        PD.poly(p.msp, ext, layer)
        for h in holes:
            PD.poly(p.msp, h, layer)
        hatch = p.msp.add_hatch(color=8, dxfattribs={"layer": "A-WALL-PATT"})
        hatch.paths.add_polyline_path(ext, is_closed=True)
        for h in holes:
            hatch.paths.add_polyline_path(h, is_closed=True)


def door_symbols(p, o):
    """Leaf and swept arc, both derived from the opening -- never free-drawn."""
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    width = abs(b - a)
    mid = (t0 + t1) / 2.0
    if axis == "h":
        hinge, closed = (a, mid), 0.0
    else:
        hinge, closed = (mid, a), 90.0
    delta = (sw - closed + 540.0) % 360.0 - 180.0
    a0, a1 = (closed + delta, closed) if delta < 0 else (closed, closed + delta)
    p.arc(hinge[0], hinge[1], width, a0, a1, "A-DOOR-SWNG")
    lx = hinge[0] + width * math.cos(math.radians(sw))
    ly = hinge[1] + width * math.sin(math.radians(sw))
    p.line(hinge[0], hinge[1], lx, ly, "A-DOOR")


def window_symbol(p, o):
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    lo, hi = min(a, b), max(a, b)
    if axis == "h":
        p.line(lo, t0, hi, t0, "A-GLAZ")
        p.line(lo, t1, hi, t1, "A-GLAZ")
        p.line(lo, (t0 + t1) / 2, hi, (t0 + t1) / 2, "A-GLAZ")
    else:
        p.line(t0, lo, t0, hi, "A-GLAZ")
        p.line(t1, lo, t1, hi, "A-GLAZ")
        p.line((t0 + t1) / 2, lo, (t0 + t1) / 2, hi, "A-GLAZ")


def slide_symbol(p, o):
    """A glazed sliding door: the frame jambs across the wall, two glazed
    leaves on their tracks overlapping at the middle, and a slider line with
    its arrow on the moving leaf. No swing arc -- it does not swing, and no
    sill lines -- it runs to the floor."""
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    lo, hi = min(a, b), max(a, b)
    w0, w1 = min(t0, t1), max(t0, t1)
    c, mid, span = (w0 + w1) / 2, (lo + hi) / 2, hi - lo
    off, lap = 40.0, min(100.0, 0.05 * span)

    def seg(a0, c0, a1, c1, layer):          # (along, across) -> plan
        if axis == "h":
            p.line(a0, c0, a1, c1, layer)
        else:
            p.line(c0, a0, c1, a1, layer)

    seg(lo, w0, lo, w1, "A-GLAZ")            # jambs
    seg(hi, w0, hi, w1, "A-GLAZ")
    seg(lo, c - off, mid + lap, c - off, "A-GLAZ")     # fixed leaf
    seg(mid - lap, c + off, hi, c + off, "A-GLAZ")     # sliding leaf
    # slider line: the moving leaf slides over the fixed one
    s = c + 3 * off
    tip = mid - 0.25 * span
    seg(hi - 0.1 * span, s, tip, s, "A-DOOR")
    ah = min(150.0, 0.08 * span)
    seg(tip, s, tip + ah, s + 0.6 * ah, "A-DOOR")
    seg(tip, s, tip + ah, s - 0.6 * ah, "A-DOOR")


def opening_symbols(p, floor):
    """Window, sliding door or door symbol for every opening on `floor`."""
    for o in V.OPENINGS:
        if o[0] != floor:
            continue
        if o[1] == V.WIN:
            window_symbol(p, o)
        elif o[1] == V.SLIDE:
            slide_symbol(p, o)
        elif o[1] == V.DOOR and o[9] is not None:
            door_symbols(p, o)


def overhead(p, sheet):
    """Fins and shades over this sheet's floors, as dashed outlines -- they
    are above (or cut far outside) the plan's cut plane, so they are drawn the
    way a canopy is: dashed, on their own layer. From V.FIN_ARRAYS and
    V.SHADES via villa_geom, never typed."""
    if SHADE_LAYER not in p.doc.layers:
        p.doc.layers.add(SHADE_LAYER, color=8, lineweight=18, linetype="DASHED")
    # fins the plan's cut plane passes through are drawn cut (solid), not
    # dashed (G.cut_fins; none unless the design has FIN_ARRAYS)
    cut = set(G.cut_fins(sheet)) if getattr(V, "FIN_ARRAYS", None) else set()
    n = 0
    for x0, y0, x1, y1 in G.overhead(sheet):
        if (x0, y0, x1, y1) in cut:
            continue
        e = PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), SHADE_LAYER)
        # DASHED is defined in inches-ish units; at 1:100 in mm it needs this
        # to plot as ~2.5 mm dashes rather than a continuous line
        e.dxf.ltscale = 200.0
        n += 1
    # the building's own projections over this storey: a cantilevered floor,
    # a roof frame, the balcony's slab (V.OVERHANGS, V.BALCONY)
    for x0, y0, x1, y1 in G.overhangs_over(sheet):
        e = PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), SHADE_LAYER)
        e.dxf.ltscale = 200.0
        n += 1
    if cut:
        if FIN_LAYER not in p.doc.layers:
            p.doc.layers.add(FIN_LAYER, color=7, lineweight=25)
        for x0, y0, x1, y1 in sorted(cut):
            pts = PD.rect_pts(x0, y0, x1, y1)
            PD.poly(p.msp, pts, FIN_LAYER)
            h = p.msp.add_hatch(color=8, dxfattribs={"layer": FIN_LAYER})
            h.paths.add_polyline_path(pts, is_closed=True)
    if PROJECT_SHEETS:              # say what each dashed outline is
        for s, x, y, w in overhead_names(sheet):
            p.fit_text(s, x, y, 200, "A-ANNO-TEXT", max_w=w, centre=True)
    return n


def overhead_names(sheet):
    """[(name, x, y, width)] for the dashed outlines of a sheet: a shade over
    the car porch is the CARPORT, any other a CANOPY; a projection inside an
    upper storey's outline is that storey, one at the roof slab the ROOF, the
    balcony's slab the BALCONY -- each 'OVER'. Nothing where the outline is
    the balcony drawn on its own floor, or too small to name."""
    porch = (box(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, V.PORCH_Y1)
             if hasattr(V, "PORCH_X0") else None)
    spans = [G.storey_span(f) for f in G.sheet_floors(sheet) if f in V.LEVEL]
    seen_b = G.balcony_on(sheet)
    grid = sorted({v for r in V.ROOMS if r[6] == sheet for v in (r[1], r[3])})

    def clear_x(x0, x1):
        """Centre and width of the widest stretch of x0..x1 between two room
        edges -- where no dimension's extension line runs."""
        xs = [x0] + [v for v in grid if x0 < v < x1] + [x1]
        w, a = max((b - a, a) for a, b in zip(xs, xs[1:]))
        return a + w / 2, w - 300

    out = []
    for x0, y0, z0, x1, y1, z1 in G.shade_boxes():
        if not any(z1 > lo + 1 and z0 < hi - 1 for lo, hi in spans):
            continue
        s = box(x0, y0, x1, y1)
        name = ("CARPORT OVER" if porch is not None
                and s.intersection(porch).area > 0.5 * s.area else "CANOPY OVER")
        cx, w = clear_x(x0, x1)
        out.append((name, cx, (y0 + y1) / 2, w))
    bal = G.balcony()
    at_roof = {(b[0], b[1], b[3], b[4]) for b in map(G._as_box, getattr(V, "OVERHANGS", None) or [])
               if b[2] >= V.RF - 1.0}
    for r in G.overhangs_over(sheet):
        r = tuple(r)
        s = box(*r)
        if seen_b is not None and s.intersection(box(*seen_b)).area > 0.5 * s.area:
            continue                # the balcony itself is named on this floor
        ups = [f for f in G.STACKED if f in V.LEVEL and V.rooms_on(f)
               and V.outline(f).buffer(1.0).contains(s)]
        if bal is not None and r == tuple(bal[0]):
            name = "BALCONY OVER"
        elif ups:
            name = f"{G.FLOOR_NAME.get(ups[0], ups[0])} OVER"
        elif r in at_roof:
            name = "ROOF OVER"
        else:
            name = "OVERHANG"
        if min(r[2] - r[0], r[3] - r[1]) >= 800:
            cx, w = clear_x(r[0], r[2])
            out.append((name, cx, (r[1] + r[3]) / 2, w))
    return out


def stone(p, sheet):
    """The stone the plan cuts (G.stone_on): a cladding skin on a wall face
    as a dark band over the wall's poche, free-standing stone walls and
    piers as cut walls. Nothing for design data without STONE_ZONES /
    STONE_FREE."""
    items = G.stone_on(sheet)
    if not items:
        return 0
    if CLAD_LAYER not in p.doc.layers:
        p.doc.layers.add(CLAD_LAYER, color=7, lineweight=35)
    # a skin is drawn where it is on a wall face of this sheet's storeys (a
    # zone that runs past the wall -- under a cantilever -- stops there)
    walls = unary_union([V.outline(f) for f in G.sheet_floors(sheet)
                         if V.rooms_on(f)]).buffer(1.0, join_style=2)
    n = 0
    for kind, (x0, y0, x1, y1) in items:
        if kind == "free":
            draw_fabric(p, box(x0, y0, x1, y1), "A-WALL-EXTR")
            n += 1
            continue
        for ext_, _h in rings(box(x0, y0, x1, y1).intersection(walls)):
            PD.poly(p.msp, ext_, CLAD_LAYER)
            h = p.msp.add_hatch(color=7, dxfattribs={"layer": CLAD_LAYER})
            h.paths.add_polyline_path(ext_, is_closed=True)
            n += 1
    return n


def balcony_plan(p, sheet):
    """The balcony on the storey it is a floor of (G.balcony_on): its slab
    edge seen, named, with its area; its glass guards come with guards()."""
    b = G.balcony_on(sheet)
    if b is None:
        return
    x0, y0, x1, y1 = b
    PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), "A-FLOR-OTLN")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    p.fit_text("BALCONY", cx, cy + 180, TXT_NAME, "A-ANNO-TEXT",
               max_w=x1 - x0 - 600, centre=True)
    p.fit_text(f"{(x1 - x0) * (y1 - y0) / 1e6:.1f} m2", cx, cy - 300, TXT_AREA,
               "A-ANNO-TEXT", max_w=x1 - x0 - 600, centre=True)


GUARD_LAYER = "A-GRDS"          # glass balustrades (guards), in plan
RAIL_LAYER = "A-GRDS-RAIL"      # handrails, in plan


def guards(p, sheet, outside=None):
    """Every guard standing on a floor this sheet draws (G.guards_on): the
    glass balustrades at raised landings, on the garden platform's open
    edges, round the first-floor stair well and on the stair's own open
    sides -- V.guards(), never typed. The handrails beside them (G.rails_on,
    V.handrails) go on a layer of their own. `outside` (a footprint): only
    what stands outside it -- a project's site plan shows the garden's
    guards, not the glass of the stairs inside the house."""
    if GUARD_LAYER not in p.doc.layers:
        p.doc.layers.add(GUARD_LAYER, color=4, lineweight=25)
    inside = (lambda r: outside.buffer(1.0).contains(box(*r))) if outside is not None \
        else (lambda r: False)
    n = 0
    for x0, y0, x1, y1 in G.guards_on(sheet):
        if inside((x0, y0, x1, y1)):
            continue
        PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), GUARD_LAYER)
        n += 1
    if hasattr(G, "rails_on"):
        if RAIL_LAYER not in p.doc.layers:
            p.doc.layers.add(RAIL_LAYER, color=8, lineweight=18)
        for x0, y0, x1, y1 in G.rails_on(sheet):
            if inside((x0, y0, x1, y1)):
                continue
            PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), RAIL_LAYER)
    return n


def site_water(p, P_D):
    """The pool on the site plan: water, the floor profile's breaks with
    their depths (V.POOL_FLOOR), the weir, the balance basin with its grate
    (V.grate()), the plant vault below the deck (dashed) and the rill."""
    PD.poly(p.msp, PD.rect_pts(V.POOL_X0, V.POOL_Y0, V.POOL_X1, V.POOL_Y1),
            "A-FLOR-OTLN")
    for y, z in sorted(getattr(V, "POOL_FLOOR", ()))[1:-1]:
        p.line(V.POOL_X0, y, V.POOL_X1, y, "A-FLOR-PATT")
    if getattr(V, "POOL_LEDGE", None):
        pool_depths(p)              # a project's pool: the ledge, its flats
    else:
        for y, z in sorted(getattr(V, "POOL_FLOOR", ()), reverse=True)[::3]:
            p.fit_text(f"{V.POOL_TW - z:.0f} DEEP", V.POOL_X0 + 1300,
                       min(max(y, V.POOL_Y0 + 400), V.POOL_Y1 - 400), 180,
                       "A-ANNO-TEXT", max_w=2400, centre=True)
    if hasattr(V, "BASIN_Y0"):      # a balance basin (an overflow pool's)
        PD.poly(p.msp, PD.rect_pts(V.POOL_X0 - 400, V.BASIN_Y0,
                                   V.POOL_X1 + 400, V.BASIN_Y1), "A-FLOR-PATT")
    for x0, y0, z0, x1, y1, z1 in G.grate_boxes():
        h = p.msp.add_hatch(color=8, dxfattribs={"layer": "A-FLOR-PATT"})
        h.set_pattern_fill("ANSI37", scale=80.0)
        h.paths.add_polyline_path(PD.rect_pts(x0, y0, x1, y1), is_closed=True)
        p.fit_text("GRATE OVER BALANCE BASIN", (x0 + x1) / 2, (y0 + y1) / 2, 160,
                   "A-ANNO-TEXT", max_w=x1 - x0 - 400, centre=True)
    if getattr(V, "POOL_PLANT", None):
        x0, y0, x1, y1 = V.POOL_PLANT
        e = PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), SHADE_LAYER)
        e.dxf.ltscale = 200.0
        p.fit_text("POOL PLANT BELOW", (x0 + x1) / 2, (y0 + y1) / 2, 160,
                   "A-ANNO-TEXT", max_w=x1 - x0 - 300, centre=True)
    if has_rill():
        PD.poly(p.msp, PD.rect_pts(V.AXIS - V.RILL_W / 2, V.POOL_Y1,
                                   V.AXIS + V.RILL_W / 2, V.WG_Y0), "A-FLOR-OTLN")


def has_rill():
    """The villa's rill from the pool to the wings (AXIS, RILL_W, WG_Y0)."""
    return all(hasattr(V, a) for a in ("AXIS", "RILL_W", "WG_Y0"))


def pool_flats():
    """[(y0, y1, depth)] -- the level stretches of the pool floor
    (V.POOL_FLOOR), less the sun ledge (V.POOL_LEDGE) where it covers them;
    and the ledge itself as ('ledge', y0, y1, depth)."""
    pts = sorted(getattr(V, "POOL_FLOOR", ()))
    ledge = getattr(V, "POOL_LEDGE", None)
    out = []
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        if abs(za - zb) > 1.0 or yb - ya < 1.0:
            continue
        a, b = ya, yb
        if ledge:
            la, lb = ledge[1], ledge[3]
            if la <= a + 1 and lb >= b - 1:
                continue
            if la < b and lb > a:           # trim the ledge off one end
                if la > a:
                    b = la
                else:
                    a = lb
        out.append((a, b, V.POOL_TW - za))
    return out


def pool_depths(p):
    """A project pool's depths on the site plan: each level stretch of the
    floor profile and the sun ledge (outlined), from the design data."""
    cx = (V.POOL_X0 + V.POOL_X1) / 2
    wmax = V.POOL_X1 - V.POOL_X0 - 600
    for a, b, depth in pool_flats():
        h = 180 if b - a >= 900 else 140
        p.fit_text(f"{depth:.0f} DEEP", cx, (a + b) / 2, h, "A-ANNO-TEXT",
                   max_w=wmax, centre=True)
    lx0, ly0, lx1, ly1, lz = V.POOL_LEDGE
    PD.poly(p.msp, PD.rect_pts(lx0, ly0, lx1, ly1), "A-FLOR-PATT")
    p.fit_text(f"SUN LEDGE {V.POOL_TW - lz:.0f} DEEP", (lx0 + lx1) / 2,
               (ly0 + ly1) / 2, 180, "A-ANNO-TEXT", max_w=lx1 - lx0 - 600,
               centre=True)


def stair(p, floor):
    """The stair as built: every riser at STAIR_GOING (G.stair_risers), the
    half-landing edge, the line between the flights -- not treads spread
    evenly over the well, which drew 20 treads of 170 in a 250-going stair."""
    sx0, sy0, sx1, sy1 = V.STAIR
    mid = (sx0 + sx1) / 2.0
    L = "A-FLOR-STRS"
    PD.poly(p.msp, PD.rect_pts(sx0, sy0, sx1, sy1), L)
    for x0, y, x1 in G.stair_risers():
        p.line(x0, y, x1, y, L)
    yl = G.stair_landing_edge()
    if yl is not None:
        p.line(sx0, yl, sx1, yl, L)
        p.line(mid, sy0, mid, yl, L)
    y0 = sy0 + (sy1 - sy0) * 0.30
    y1 = sy0 + (sy1 - sy0) * 0.72
    xa = (sx0 + mid) / 2.0
    p.line(xa, y0, xa, y1, L)
    p.line(xa, y1, xa - 130, y1 - 220, L)
    p.line(xa, y1, xa + 130, y1 - 220, L)
    p.text("UP" if floor == "GF" else "DN", xa + 220, y0, TXT_SM, "A-ANNO-TEXT")


# ------------------------------------------------- stairs of a STAIRS design
def _lines(g):
    """Every LineString in a (possibly collection) geometry."""
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    out = []
    for s in getattr(g, "geoms", []):
        out += _lines(s)
    return out


def _seg(p, a, b, layer, clip=None, dashed=False):
    """A line a -> b, clipped to `clip` (a shapely area) when given; dashed
    lines get the overhead linetype scale."""
    from shapely.geometry import LineString
    if clip is None:
        segs = [(a, b)]
    else:
        segs = [(tuple(s.coords)[0], tuple(s.coords)[-1])
                for s in _lines(LineString([a, b]).intersection(clip)) if s.length > 1.0]
    for (x0, y0), (x1, y1) in segs:
        e = p.msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": layer})
        if dashed:
            e.dxf.ltscale = 200.0
    return len(segs)


def _arrow(p, a, b, layer, clip=None):
    """An arrow a -> b (the head at b's end), clipped to `clip`."""
    from shapely.geometry import LineString
    ln = LineString([a, b])
    if clip is not None:
        parts = _lines(ln.intersection(clip))
        if not parts:
            return False
        ln = max(parts, key=lambda s: s.length)
        c = list(ln.coords)
        # keep the direction a -> b
        if math.dist(c[0], a) > math.dist(c[-1], a):
            c = c[::-1]
        ln = LineString(c)
    if ln.length < 300.0:
        return False
    (x0, y0), (x1, y1) = ln.coords[0], ln.coords[-1]
    p.line(x0, y0, x1, y1, layer)
    ux, uy = (x1 - x0) / ln.length, (y1 - y0) / ln.length
    ah = min(260.0, 0.3 * ln.length)
    for s in (1, -1):
        p.line(x1, y1, x1 - ah * ux + s * 0.45 * ah * uy,
               y1 - ah * uy - s * 0.45 * ah * ux, layer)
    return True


def _fpt(f, c, t):
    """Plan point of a flight at `c` across and `t` along it."""
    return (c, t) if f["along"] == "y" else (t, c)


def _flight(p, f, role, level, clip):
    """One flight as the sheet sees it. 'up' (the storey at the stair's
    foot): every riser up to the plan's cut plane solid, a break line, the
    rest dashed overhead. 'down' / 'through': every riser seen from above,
    clipped to the void it is seen through. An arrow runs up the flight on
    'up', down it otherwise; UP / DN is written where the flight meets this
    floor."""
    L = "A-FLOR-STRS"
    d, g, n = f["dir"], f["going"], f["n"]
    t0 = f["t_foot"]
    t_top = t0 + d * (n - 1) * g
    c0, c1 = f["c0"], f["c1"]
    cm = (c0 + c1) / 2.0
    if role == "up":
        cut = level + G.PLAN_CUT
        k_b = sum(1 for k in range(n) if f["z_foot"] + (k + 1) * f["rise"] <= cut + 1e-6)
    else:
        k_b = n
    for k in range(n):                                  # risers
        t = t0 + d * k * g
        solid = k < k_b
        _seg(p, _fpt(f, c0, t), _fpt(f, c1, t), L if solid else STAIR_OVHD,
             clip, dashed=not solid)
    t_b = t0 + d * (k_b - 0.5) * g if 0 < k_b < n else (t_top if k_b >= n else t0)
    for c in (c0, c1):                                  # strings
        if k_b > 0:
            _seg(p, _fpt(f, c, t0), _fpt(f, c, t_b), L, clip)
        if k_b < n:
            _seg(p, _fpt(f, c, t_b), _fpt(f, c, t_top), STAIR_OVHD, clip, dashed=True)
    if 0 < k_b < n:                                     # break line at the cut
        h, w = 0.45 * g, c1 - c0
        zz = [(0.0, -h), (0.44, -0.12 * h), (0.50, 0.9 * h), (0.50, -0.9 * h),
              (0.56, 0.12 * h), (1.0, h)]
        pts = [_fpt(f, c0 + fa * w, t_b + d * dt) for fa, dt in zz]
        for a, b in zip(pts, pts[1:]):
            p.line(a[0], a[1], b[0], b[1], L)
    if role == "up":
        a, b = _fpt(f, cm, t0 + d * 0.3 * g), _fpt(f, cm, t_top - d * 0.2 * g)
    else:
        a, b = _fpt(f, cm, t_top - d * 0.3 * g), _fpt(f, cm, t0 + d * 0.2 * g)
    _arrow(p, a, b, L, clip)
    # UP / DN on the tread at the arrow's tail, beside the arrow -- where the
    # flight meets this floor
    z_top = f["z_foot"] + n * f["rise"]
    ca = cm + 0.27 * (c1 - c0)
    if role == "up" and abs(f["z_foot"] - level) < 1.0:
        x, y = _fpt(f, ca, t0 + d * 0.5 * g)
        p.text("UP", x, y, TXT_SM, "A-ANNO-TEXT", align="MIDDLE_CENTER")
    elif role != "up" and abs(z_top - level) < 1.0:
        x, y = _fpt(f, ca, t_top - d * 0.5 * g)
        p.text("DN", x, y, TXT_SM, "A-ANNO-TEXT", align="MIDDLE_CENTER")


def stair_clip(sheet):
    """Where a stair below is seen from this sheet's floor: the voids that
    cut it (None: nothing to clip to)."""
    vs = [box(*r) for _n, r in G.voids_on(sheet)]
    return unary_union(vs) if vs else None


def stairs(p, sheet):
    """Every house stair of a STAIRS design on the sheets it runs through
    (G.flights_on): its flights, its half-landing (dashed where it is over
    the cut plane), arrows by direction, UP / DN. The handrails and guards
    come with guards() (G.rails_on / G.guards_on)."""
    if STAIR_OVHD not in p.doc.layers:
        p.doc.layers.add(STAIR_OVHD, color=7, lineweight=18, linetype="DASHED")
    level = V.LEVEL[sheet]
    clip = stair_clip(sheet)
    roles = {}
    for f, role in G.flights_on(sheet):
        roles[f.get("stair", "stair")] = role
        _flight(p, f, role, level, None if role == "up" else clip)
    for name, (x0, y0, x1, y1), lv in G.stair_landings():
        role = roles.get(name if name is not None else "stair")
        if role is None:
            continue
        over = role == "up" and lv > level + G.PLAN_CUT
        pts = PD.rect_pts(x0, y0, x1, y1)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            _seg(p, a, b, STAIR_OVHD if over else "A-FLOR-STRS",
                 None if role == "up" else clip, dashed=over)
    return len(roles)


def _label_frag(r, floor):
    """Label position clear of nested rooms AND of the stair, which is not a
    room but is very much in the way."""
    from shapely.geometry import box as _b
    g = _b(*V.rect(r))
    for q in V.ROOMS:
        if q[6] == floor and q[0] != r[0] and V.contains(V.rect(r), V.rect(q)):
            g = g.difference(_b(*V.rect(q)))
    if MULTI_STAIR:
        return _label_frag_multi(g, floor)
    st = _b(*V.STAIR).buffer(400)
    if g.intersects(st) and not g.difference(st).is_empty:
        g = g.difference(st)
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda x: x.area)
    pt = g.representative_point()
    b = g.bounds
    return pt.x, pt.y, b[2] - b[0]


def _obstacles(floor):
    """What a label must keep clear of on a STAIRS design's sheet: every
    flight drawn there (300 round it), its half-landing, the voids."""
    obs = []
    for f, _role in G.flights_on(floor):
        t0, t1 = V.flight_run(f)
        obs.append(box(*V.flight_plan(f, t0, t1)).buffer(300.0, join_style=2))
    obs += [box(*rc) for _n, rc, _lv in G.stair_landings()]
    obs += [box(*rc) for _n, rc in G.voids_on(floor)]
    if hasattr(F, "_swing"):        # and the doors' swings
        from shapely.geometry import Polygon
        for o in V.OPENINGS:
            pts = F._swing(o) if o[0] == floor else None
            if pts:
                obs.append(Polygon(pts).buffer(80.0))
    return obs


def _label_frag_multi(g, floor):
    """_label_frag for a STAIRS design: the room (less nested rooms) less
    every stair and void on the sheet, where at least 1.5 m2 is left."""
    from shapely.geometry import LineString
    from shapely.ops import polylabel
    for o in _obstacles(floor):
        if g.intersects(o):
            rest = g.difference(o)
            if rest.area >= 1.5e6:
                g = rest
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda x: x.area)
    # the height farthest from every edge (an L-shaped room's label sits in
    # its widest part, not on the partition), centred on the room's width
    # there
    pt = polylabel(g, tolerance=20.0)
    b = g.bounds
    chord = [s for s in _lines(LineString([(b[0] - 1, pt.y), (b[2] + 1, pt.y)])
                               .intersection(g)) if s.distance(pt) < 1.0]
    if not chord:
        return pt.x, pt.y, b[2] - b[0]
    (x0, _y0), (x1, _y1) = chord[0].coords[0], chord[0].coords[-1]
    return (x0 + x1) / 2.0, pt.y, abs(x1 - x0)


def void_label_at(sheet, rect_):
    """(x, y, width) for a void's name: the void less the flights seen in
    it (a stair well's name goes on its half-landing, not over the treads)."""
    g = box(*rect_)
    for f, _role in G.flights_on(sheet):
        t0, t1 = V.flight_run(f)
        rest = g.difference(box(*V.flight_plan(f, t0, t1)))
        if rest.area >= 1.0e6:
            g = rest
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda x: x.area)
    c = g.representative_point()
    b = g.bounds
    return c.x, c.y, b[2] - b[0]


def labels(p, floor):
    for r in V.ROOMS:
        if r[6] != floor:
            continue
        lx, ly, fw = _label_frag(r, floor)
        w = r[3] - r[1]
        a = V.net_area(r)          # net, matching the schedule and the checks
        small = a < 7.0
        hn = TXT_SM if small else TXT_NAME
        ha = 160.0 if small else TXT_AREA
        cap = max(1200.0, min(w, fw) - 300)
        p.fit_text(r[0], lx, ly + hn * 0.55, hn, "A-ANNO-TEXT",
                   max_w=cap, centre=True)
        p.fit_text(f"{a:.1f} m2", lx, ly - ha * 1.7, ha, "A-ANNO-TEXT",
                   max_w=cap, centre=True)


def dim_runs(p, floor, bnds, reach=None):
    """External dimension runs: overall, then the room grid on both faces.
    `reach` (x, y): the lower-left of everything drawn on the sheet, when
    something stands beyond the house (a canopy, a cantilever) -- the runs
    are then set out beyond it, still measuring the house."""
    x0, y0, x1, y1 = bnds
    ox = oy = 0                         # the villa: the runs 1500 / 3300 out
    if reach is not None:
        ox, oy = max(0.0, x0 - reach[0]), max(0.0, y0 - reach[1])
    xs = sorted({v for r in V.ROOMS if r[6] == floor for v in (r[1], r[3])})
    ys = sorted({v for r in V.ROOMS if r[6] == floor for v in (r[2], r[4])})
    def chain(vals, lo, hi):
        """Every segment >= 900 and the run adds up to the overall. Short
        segments are absorbed into their neighbour rather than dropped, which
        is how the last chain came to read 17250 against an 18000 overall."""
        pts, out = [lo] + [v for v in vals if lo + 300 < v < hi - 300] + [hi], [lo]
        for v in pts[1:]:
            if v - out[-1] >= 900:
                out.append(v)
        out[-1] = hi
        if len(out) > 2 and out[-1] - out[-2] < 900:
            out.pop(-2)
        return out

    for c in chain(xs, x0, x1):
        pass
    cx = chain(xs, x0, x1)
    cy = chain(ys, y0, y1)
    for i in range(len(cx) - 1):
        p.dim_h(cx[i], cx[i + 1], y0, 1500 + oy)
    for i in range(len(cy) - 1):
        p.dim_v(cy[i], cy[i + 1], x0, 1500 + ox)
    p.dim_h(x0, x1, y0, 3300 + oy)
    p.dim_v(y0, y1, x0, 3300 + ox)


def titleblock(p, sheet_no, sheet_name, areas, x0, y0, w=18000.0, val=None):
    """Title block. Every number on it is computed: the project line from the
    brief's bedrooms and the plot, `areas` (villa_geom.area_text / site_text:
    NET vs GROSS, labelled), the validator's and the furniture check's real
    counts, and the date of the design data. It used to say "GROSS INTERNAL
    AREA" over a sum of NET room areas, and "VALIDATED 0 FATAL / 0 MAJOR"
    while the validator reported 5 and 22."""
    L, h = "A-ANNO-TTLB", 2600.0
    c1, c2 = w * 0.56, w * 0.78
    if not isinstance(areas, str):                  # a bare number: net m2
        areas = f"NET FLOOR AREA {float(areas):.1f} m2"
    PD.poly(p.msp, PD.rect_pts(x0, y0, x0 + w, y0 + h), L)
    p.line(x0, y0 + 1700, x0 + w, y0 + 1700, L)
    for c in (c1, c2):
        p.line(x0 + c, y0, x0 + c, y0 + 1700, L)
    p.fit_text(G.project_line(), x0 + 300, y0 + 2000, 380, L, c1 - 500)
    p.fit_text(sheet_name, x0 + 300, y0 + 1250, 280, L, c1 - 500)
    p.fit_text("ALL DIMENSIONS IN MILLIMETRES.  DO NOT SCALE FROM DRAWING.",
               x0 + 300, y0 + 900, 150, L, c1 - 500)
    p.fit_text(areas, x0 + 300, y0 + 560, 150, L, c1 - 500)
    p.fit_text(G.validation_text(val), x0 + 300, y0 + 220, 150, L, c1 - 500)
    p.text("SCALE", x0 + c1 + 250, y0 + 1180, 170, L)
    p.text("1:100 @ A1", x0 + c1 + 250, y0 + 820, 200, L)
    p.text("DATE", x0 + c1 + 250, y0 + 420, 170, L)
    p.text(G.design_date(), x0 + c1 + 250, y0 + 140, 170, L)
    p.text("DWG No.", x0 + c2 + 250, y0 + 1180, 170, L)
    p.text(sheet_no, x0 + c2 + 250, y0 + 700, 320, L)
    p.text("REV  B", x0 + c2 + 250, y0 + 260, 170, L)


# --------------------------------------------------------------------- plan
def cut_fabric(floor):
    """(external, partitions, internal envelope) of a floor with every one of
    its openings cut out, so a door is a real hole in the poche."""
    ext, part, inner = SVG._fabric(floor)
    voids = [SVG._void_rect(o) for o in V.OPENINGS if o[0] == floor]
    if voids:
        cut = unary_union(voids)
        ext, part = ext.difference(cut), part.difference(cut)
    return ext, part, inner


def sheet_bounds(floors):
    """Outside faces of every floor drawn on a sheet (house + annex)."""
    return unary_union([V.outline(f) for f in floors if V.rooms_on(f)]).bounds


def build_plan(floor, sheet_no, sheet_name, val=None):
    """One plan sheet: `floor` and every floor drawn with it -- the annex
    (AX) on the ground-floor sheet (villa_geom.sheet_floors)."""
    p = PD.Plan(sheet_name)
    fls = G.sheet_floors(floor)

    for fl in fls:
        if not V.rooms_on(fl):
            continue
        ext, part, _ = cut_fabric(fl)
        draw_fabric(p, ext, "A-WALL-EXTR")
        draw_fabric(p, part, "A-WALL")
        opening_symbols(p, fl)

    if floor == "RF":               # a roof pavilion stands on the house roof
        E = V.envelope()
        for ext_, _h in rings(E["upper"]):
            PD.poly(p.msp, ext_, "A-FLOR-OTLN")
    if MULTI_STAIR:                 # every stair, on the storeys it joins
        stairs(p, floor)
    elif floor in ("GF", "FF"):
        stair(p, floor)
    if G.GROUND_FLOOR in fls or "AX" in fls:  # external landings and flights
        for x0, y0, z0, x1, y1, z1 in V.external_steps():
            PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), "A-FLOR-PATT")
    guards(p, floor)
    stone(p, floor)                 # STONE_ZONES / STONE_FREE, when designed
    balcony_plan(p, floor)          # BALCONY, on the floor it is part of
    for fl in fls:
        labels(p, fl)
    for vname, vx0, vy0, vx1, vy1, floors in V.VOIDS:
        if floor not in floors:
            continue
        PD.poly(p.msp, PD.rect_pts(vx0, vy0, vx1, vy1), "A-FLOR-PATT")
        if MULTI_STAIR:             # clear of the treads seen in it
            lx, ly, lw = void_label_at(floor, (vx0, vy0, vx1, vy1))
            p.fit_text(vname, lx, ly, 240, "A-ANNO-TEXT", max_w=lw - 400,
                       centre=True)
            continue
        p.fit_text(vname, (vx0 + vx1) / 2, (vy0 + vy1) / 2, 240,
                   "A-ANNO-TEXT", max_w=vx1 - vx0 - 400, centre=True)
    overhead(p, floor)

    main = [floor] if V.rooms_on(floor) else fls
    b = sheet_bounds(main)
    reach = None
    if PROJECT_SHEETS:              # set out beyond a canopy or a cantilever
        B = drawn_bounds(floor, fls)
        reach = (B[0], B[1])
    dim_runs(p, floor, b, reach)
    for fl in fls:                  # overall dimensions of the annex
        if fl == floor or not V.rooms_on(fl):
            continue
        ax0, ay0, ax1, ay1 = V.outline(fl).bounds
        p.dim_h(ax0, ax1, ay1, -1200)
        p.dim_v(ay0, ay1, ax1, -1200)
    if not PROJECT_SHEETS:
        B = sheet_bounds(fls)
    p.north(B[2] + 2200, B[3] - 900, 620)
    p.scale_bar(B[0], B[3] + 1400, 5)

    name = sheet_name.upper()
    if PROJECT_SHEETS:
        name += f"   --   {level_text(floor)}"
    titleblock(p, sheet_no, name, G.area_text(fls),
               B[0] - 3600, B[1] - 8200, val=val)

    path = os.path.join(OUT, f"VILLA_{sheet_no.replace('-', '')}.dxf")
    save(p, path)
    return p, path


def level_text(floor):
    """'B1 FFL -3800' -- the floor and its finished level, for a title block."""
    return f"{floor} FFL {V.LEVEL[floor]:+.0f}"


def drawn_bounds(sheet, fls):
    """Bounds of everything a plan sheet draws: the house, and whatever
    stands beyond it -- shading and fins (G.overhead), the building's own
    projections (G.overhangs_over), the balcony, the stone walls."""
    gs = [V.outline(f) for f in fls if V.rooms_on(f)]
    gs += [box(*r) for r in G.overhead(sheet) + G.overhangs_over(sheet)]
    gs += [box(*r) for _k, r in G.stone_on(sheet)]
    gs += [box(*r) for r in G.guards_on(sheet) + G.rails_on(sheet)]
    b = G.balcony_on(sheet)
    if b is not None:
        gs.append(box(*b))
    return unary_union(gs).bounds


def _top_level(r, floor):
    for q in V.ROOMS:
        if q[6] == floor and q[0] != r[0] and q[1] <= r[1] and q[2] <= r[2] \
                and q[3] >= r[3] and q[4] >= r[4]:
            return False
    return True


# --------------------------------------------------------------------- site
TREES = ((5200, 26000, 1400), (9400, 26900, 1200), (4600, 6000, 1700),
         (19400, 6600, 1700), (19600, 2600, 1500))


def build_site(val=None):
    p = PD.Plan("Site plan")
    P_W, P_D, BW = V.PLOT_W, V.PLOT_D, G.BW

    ring = box(0, 0, P_W, P_D).difference(box(BW, BW, P_W - BW, P_D - BW))
    gates = unary_union([box(g0, P_D - BW - 60, g1, P_D + 60)
                         for _n, g0, g1, _h in G.gates()])
    draw_fabric(p, ring.difference(gates), "A-WALL-EXTR")

    # every building on the plot: the house, and the annex beside it
    for fl in G.ground_floors():
        ext, part, inner = SVG._fabric(fl)
        draw_fabric(p, V.outline(fl).difference(inner), "A-WALL-EXTR")

    if SHADE_LAYER not in p.doc.layers:
        p.doc.layers.add(SHADE_LAYER, color=8, lineweight=18, linetype="DASHED")
    site_water(p, P_D)
    PD.poly(p.msp, PD.rect_pts(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, V.PORCH_Y1),
            "A-FLOR-PATT")
    for x0, y0, z0, x1, y1, z1 in V.external_steps():
        PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), "A-FLOR-PATT")
    if hasattr(V, "POOL_LABEL"):    # a project: the garden's guards only
        guards(p, G.GROUND_FLOOR, outside=G.footprint())
    else:
        guards(p, G.GROUND_FLOOR)   # landings and the garden's open edges

    for name, g0, g1, _h in G.gates():
        p.line(g0, P_D - BW / 2, g1, P_D - BW / 2, "A-DOOR")
        p.fit_text(name, (g0 + g1) / 2, P_D + 500, 160, "A-ANNO-TEXT",
                   max_w=max(1200.0, g1 - g0 + 1600), centre=True)

    from shapely.geometry import Point
    built = G.footprint()
    for cx, cy, r in site_trees():  # no tree planted through a roof
        if Point(cx, cy).buffer(0.6 * r).intersects(built):
            continue
        p.circle(cx, cy, r, "A-FLOR-PATT")
        p.circle(cx, cy, 200, "A-FLOR-OTLN")

    S = G.site_numbers()
    house = V.outline(G.GROUND_FLOOR).area / 1e6
    depth, _w = G.forecourt()
    fy = (P_D - BW) - depth / 2            # halfway, house face to boundary
    if hasattr(V, "POOL_LABEL"):    # a project: labels from its own geometry
        labels_ = site_labels(S, house, fy)
        site_extras(p)
    else:
        labels_ = [("OVERFLOW POOL", V.AXIS, 6900, 320),
                   (G.pool_text(), V.AXIS, 6300, 220),
                   (f"FORECOURT {G.forecourt_text()}",
                    (V.PORCH_X0 + V.PORCH_X1) / 2, fy, 240),
                   ("VILLA", V.AXIS, 17400, 420),
                   (f"{house:.1f} m2 FOOTPRINT   {S['cover']:.1f}% SITE COVER",
                    V.AXIS, 16700, 240)]
    for fl in G.ground_floors():
        if fl == G.GROUND_FLOOR:
            continue
        out = V.outline(fl)
        c = out.representative_point()
        labels_.append((G.FLOOR_NAME.get(fl, fl), c.x, c.y + 250, 300))
        labels_.append((f"{out.area / 1e6:.1f} m2 GROSS", c.x, c.y - 250, 200))
    for s, x, y, h in labels_:
        p.fit_text(s, x, y, h, "A-ANNO-TEXT", max_w=9000, centre=True)

    p.dim_h(0, P_W, 0, 1800)
    p.dim_v(0, P_D, 0, 1800)
    if hasattr(V, "WG_Y0"):
        p.dim_v(V.POOL_Y1, V.WG_Y0, V.POOL_X0, 1000)  # the terrace, 1600
    else:                           # pool to the house's garden face
        p.dim_v(V.POOL_Y1, garden_face(), V.POOL_X0, 1000)
    p.north(P_W + 2600, P_D - 1800, 900)
    p.scale_bar(0, P_D + 1600, 5)
    titleblock(p, "A-101", "SITE PLAN", G.site_text(), -3600, -9000, val=val)

    path = os.path.join(OUT, "VILLA_A101.dxf")
    save(p, path)
    return p, path


def site_trees():
    """(x, y, crown radius) of every tree on the site plan: the design's
    SITE_TREES (x, y, crown diameter) when it has them, else the villa's."""
    if hasattr(V, "SITE_TREES"):
        return [(float(x), float(y), float(d) / 2.0) for x, y, d in V.SITE_TREES]
    return TREES


def garden_face():
    """y of the house's garden (south) face across the pool: the terrace runs
    from the pool's end to it."""
    band = V.outline(G.GROUND_FLOOR).intersection(
        box(V.POOL_X0, V.POOL_Y1, V.POOL_X1, V.PLOT_D))
    return band.bounds[1] if not band.is_empty else V.POOL_Y1


def house_name():
    """The house's name on the site plan: the project title up to its ' -- '."""
    t = getattr(V, "PROJECT_TITLE", None) or "VILLA"
    return t.split(" -- ")[0].strip()


def ramp_text():
    """'RAMP 1:28 (3.6%)' -- the forecourt's fall, from RAMP_Y0..RAMP_Y1 and
    the ground floor over the street; None without a ramp."""
    if not all(hasattr(V, a) for a in ("RAMP_Y0", "RAMP_Y1")):
        return None
    rise = V.LEVEL[G.GROUND_FLOOR] - getattr(V, "STREET", 0.0)
    run = abs(V.RAMP_Y1 - V.RAMP_Y0)
    if rise <= 0 or run <= 0:
        return None
    return f"RAMP 1:{run / rise:.0f} ({100 * rise / run:.1f}%)"


def site_labels(S, house, fy):
    """The site plan's labels for a project design: POOL_LABEL on its pool,
    the house by name with its footprint, level and a basement below grade,
    the forecourt -- positions from the geometry, not typed."""
    cx = (V.POOL_X0 + V.POOL_X1) / 2
    flats = pool_flats()
    # the pool's name and size on the sloping stretch, clear of the depths
    ys = sorted([V.POOL_Y0, V.POOL_Y1] + [y for a, b, _d in flats for y in (a, b)])
    gaps = [(b - a, (a + b) / 2) for a, b in zip(ys, ys[1:])]
    cy = max(gaps)[1] if gaps else (V.POOL_Y0 + V.POOL_Y1) / 2
    hb = V.outline(G.GROUND_FLOOR)
    c = hb.representative_point()
    hx, hy = c.x, c.y
    lv = V.LEVEL[G.GROUND_FLOOR]
    out = [(V.POOL_LABEL, cx, cy + 250, 300),
           (G.pool_text(), cx, cy - 300, 200),
           (f"FORECOURT {G.forecourt_text()}",
            (V.PORCH_X0 + V.PORCH_X1) / 2, fy, 240),
           (house_name(), hx, hy + 900, 420),
           (f"{house:.1f} m2 FOOTPRINT   {S['cover']:.1f}% SITE COVER", hx, hy + 200, 240),
           (f"{G.FLOOR_NAME.get(G.GROUND_FLOOR, G.GROUND_FLOOR)} FFL {lv:+.0f}",
            hx, hy - 400, 220)]
    for fl in G.BELOW_GRADE:
        if V.rooms_on(fl):
            out.append((f"{G.FLOOR_NAME.get(fl, fl)} BELOW ({level_text(fl)})",
                        hx, hy - 900, 200))
    return out


def upper_outline():
    """The edge of everything built over the ground floor, seen from above:
    the upper stacked storeys, V.OVERHANGS, the balcony (empty for design
    data without OVERHANGS)."""
    if not hasattr(V, "OVERHANGS"):
        return None
    gs = [V.outline(f) for f in G.STACKED
          if f != G.GROUND_FLOOR and f not in G.BELOW_GRADE and V.rooms_on(f)]
    gs += [box(*G._as_box(o)[:2], *G._as_box(o)[3:5]) for o in V.OVERHANGS]
    b = G.balcony()
    if b is not None:
        gs.append(box(*b[0]))
    return unary_union(gs) if gs else None


def site_extras(p):
    """What a project design adds to the site plan: the storeys over the
    ground floor and its projections dashed, a basement dotted (below
    grade), free-standing stone, the SHADES (carport, canopy) dashed and
    named, the forecourt ramp with its fall."""
    up = upper_outline()
    if up is not None:
        for ext_, holes in rings(up):
            e = PD.poly(p.msp, ext_, SHADE_LAYER)
            e.dxf.ltscale = 200.0
    if G.BELOW_GRADE:
        if BGRD_LAYER not in p.doc.layers:
            p.doc.layers.add(BGRD_LAYER, color=8, lineweight=18, linetype="DOT")
        for fl in G.BELOW_GRADE:
            if not V.rooms_on(fl):
                continue
            for ext_, _h in rings(V.outline(fl)):
                e = PD.poly(p.msp, ext_, BGRD_LAYER)
                e.dxf.ltscale = 200.0
    for kind, (x0, y0, x1, y1) in G.stone_on(G.GROUND_FLOOR):
        if kind == "free":
            draw_fabric(p, box(x0, y0, x1, y1), "A-WALL-EXTR")
    porch = box(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, V.PORCH_Y1)
    for x0, y0, z0, x1, y1, z1 in G.shade_boxes():
        e = PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), SHADE_LAYER)
        e.dxf.ltscale = 200.0
        s = box(x0, y0, x1, y1)
        name = ("CARPORT OVER" if s.intersection(porch).area > 0.5 * s.area
                else "CANOPY OVER")
        p.fit_text(name, (x0 + x1) / 2, y0 + 700, 200, "A-ANNO-TEXT",
                   max_w=x1 - x0 - 400, centre=True)
    rt = ramp_text()
    if rt:
        T = G.BW
        y0 = V.RAMP_Y0
        e = PD.poly(p.msp, [(T, y0), (V.PLOT_W - T, y0)], SHADE_LAYER, close=False)
        e.dxf.ltscale = 200.0
        xr = max(V.PORCH_X1, V.PLOT_W * 0.62)
        ya = min(y0 + 1900, (y0 + V.RAMP_Y1) / 2)
        _arrow(p, (xr, y0 + 250), (xr, ya), "A-ANNO-TEXT")
        p.fit_text(f"{rt} TO THE STREET", xr + 300, (y0 + ya) / 2, 200,
                   "A-ANNO-TEXT", max_w=V.PLOT_W - T - xr - 600)
        lv = V.LEVEL[G.GROUND_FLOOR]
        p.fit_text(f"{lv:+.0f}", T + 250, y0 - 250, 180, "A-ANNO-TEXT", max_w=1500)


# ------------------------------------------------------- furniture manifest
def furniture_manifest():
    """Insertion points for the real ACA blocks, for the COM step: every
    floor's list -- GF, FF, and the optional ANNEX (AX) and ROOF (RF) lists of
    villa_furniture_spec. `sheet` is the plan the block lands on: annex
    furniture goes on the ground-floor sheets."""
    items = []
    for floor, lst in G.furniture():
        for key, x, y, rot in lst:
            m = F.CATALOG.get(key)
            if not m or "w" not in m:
                print(f"  manifest: unknown block '{key}' on {floor} -- skipped "
                      f"(villa_furniture_spec.check() reports it)")
                continue
            ix, iy = F.insert_point(key, x, y, rot)
            fp = F.footprint(key, x, y, rot)
            rec = {"floor": floor, "sheet": G.SHEET_OF.get(floor, floor),
                   "key": key, "rot": rot,
                   "x": ix, "y": iy, "fp": [round(v, 1) for v in fp]}
            if m.get("path"):
                rec["path"] = m["path"]          # its own DWG file
            else:
                rec["pack"] = m["pack"]          # a definition inside a library
                rec["block"] = m["block"]
            rec["scale"] = m.get("scale", 1.0)
            items.append(rec)
    path = os.path.join(OUT, "furniture_manifest.json")
    with open(path, "w") as fh:
        json.dump(items, fh, indent=1)
    return items, path


SHEET_NAME = {"GF": "Ground floor plan", "FF": "First floor plan",
              "RF": "Roof pavilion plan"}


def plan_sheets():
    """(floor, sheet no, name) of every plan sheet the design needs, from
    villa_geom.plan_sheets(): the design's PLAN_SHEETS titles, else the
    villa's own wording (a roof plan only once the roof has rooms)."""
    return [(fl, no, t or SHEET_NAME.get(fl, f"{G.FLOOR_NAME.get(fl, fl).title()} plan"))
            for fl, no, t in G.plan_sheets()]


if __name__ == "__main__":
    val = G.validation()
    made = []
    for floor, no, name in plan_sheets():
        p, path = build_plan(floor, no, name, val=val)
        made.append((no, path, len(p.msp)))
    p, path = build_site(val=val)
    made.append(("A-101", path, len(p.msp)))
    items, mpath = furniture_manifest()

    for no, path, n in made:
        print(f"{no}  {n:>5} entities  ->  {os.path.basename(path)}")
    by = {}
    for it in items:
        by[it["floor"]] = by.get(it["floor"], 0) + 1
    print(f"furniture manifest: {len(items)} blocks "
          f"({', '.join(f'{k} {v}' for k, v in by.items())}) "
          f"-> {os.path.basename(mpath)}")
    print(f"title blocks: {G.validation_text(val)}")
    print(f"output: {OUT}")
