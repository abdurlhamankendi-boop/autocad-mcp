"""Derive presentation drawings straight from the validated design data.

Nothing here invents geometry. Walls are the *gaps* between room rectangles,
which is why they cannot disagree with the schedule: closing the 150 mm gaps
with a +75/-75 buffer pair gives the internal envelope, offsetting that by the
wall thickness gives the external skin, and subtracting the rooms from the
envelope gives the partitions. Openings are then cut out of both.

Classes on the emitted elements (w-ext, w-part, furn, swing...) are styled by
the page's CSS from theme tokens, so one drawing renders correctly in light
and dark.
"""

from __future__ import annotations

import math

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import villa_design as V
import villa_furniture_spec as F
import villa_geom as G

# ISO 128-20 lineweight ladder, in plotted millimetres.
LW = {"ext": 0.70, "part": 0.50, "seen": 0.35, "open": 0.25,
      "fix": 0.18, "furn": 0.13, "dim": 0.13, "thin": 0.09}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


class Draw:
    """A drawing at a fixed scale. Model units are millimetres; y runs up."""

    def __init__(self, scale, title, number):
        self.s = float(scale)
        self.title = title
        self.number = number
        self.parts = []

    def w(self, key):
        return LW[key] * self.s

    # -- primitives ------------------------------------------------------
    def poly(self, geom, cls, lw, fill="none"):
        """A shapely Polygon/MultiPolygon as one path, holes included."""
        if geom.is_empty:
            return
        geoms = getattr(geom, "geoms", [geom])
        d = []
        for g in geoms:
            if not isinstance(g, Polygon):
                continue
            for ring in [g.exterior] + list(g.interiors):
                pts = list(ring.coords)
                d.append("M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + " Z")
        if d:
            self.parts.append(
                f'<path class="{cls}" d="{" ".join(d)}" fill="{fill}" '
                f'stroke-width="{self.w(lw):.0f}"/>')

    def rect(self, x0, y0, x1, y1, cls, lw, fill="none", style=None):
        st = f' style="{style}"' if style else ""
        self.parts.append(
            f'<rect class="{cls}" x="{x0:.0f}" y="{y0:.0f}" '
            f'width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" fill="{fill}" '
            f'stroke-width="{self.w(lw):.0f}"{st}/>')

    def line(self, x0, y0, x1, y1, cls, lw):
        self.parts.append(
            f'<line class="{cls}" x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" '
            f'y2="{y1:.0f}" stroke-width="{self.w(lw):.0f}"/>')

    def path(self, pts, cls, lw, fill="none", close=False):
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + (" Z" if close else "")
        self.parts.append(f'<path class="{cls}" d="{d}" fill="{fill}" '
                          f'stroke-width="{self.w(lw):.0f}"/>')

    def circle(self, cx, cy, r, cls, lw, fill="none"):
        self.parts.append(
            f'<circle class="{cls}" cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" '
            f'fill="{fill}" stroke-width="{self.w(lw):.0f}"/>')

    def text(self, x, y, s, cls="lbl", size=2.5, anchor="middle"):
        """Text is counter-flipped so it reads the right way up in a y-up frame."""
        self.parts.append(
            f'<text class="{cls}" transform="translate({x:.0f},{y:.0f}) '
            f'scale(1,-1)" text-anchor="{anchor}" '
            f'font-size="{size * self.s:.0f}">{esc(s)}</text>')

    # -- annotation ------------------------------------------------------
    def dim(self, x0, y0, x1, y1, off, label=None, vertical=False):
        """A dimension string with ticks, offset `off` from the measured line."""
        if vertical:
            xa = x0 + off
            self.line(xa, y0, xa, y1, "dim", "dim")
            for yy in (y0, y1):
                self.line(xa - 0.9 * self.s, yy - 0.9 * self.s,
                          xa + 0.9 * self.s, yy + 0.9 * self.s, "dim", "dim")
                self.line(x0, yy, xa, yy, "dim", "thin")
            self.parts.append(
                f'<text class="dimtxt" transform="translate({xa - 0.9 * self.s:.0f},'
                f'{(y0 + y1) / 2:.0f}) scale(1,-1) rotate(-90)" text-anchor="middle" '
                f'font-size="{2.2 * self.s:.0f}">'
                f'{esc(label or f"{abs(y1 - y0):.0f}")}</text>')
        else:
            ya = y0 + off
            self.line(x0, ya, x1, ya, "dim", "dim")
            for xx in (x0, x1):
                self.line(xx - 0.9 * self.s, ya - 0.9 * self.s,
                          xx + 0.9 * self.s, ya + 0.9 * self.s, "dim", "dim")
                self.line(xx, y0, xx, ya, "dim", "thin")
            self.text((x0 + x1) / 2, ya + 0.9 * self.s,
                      label or f"{abs(x1 - x0):.0f}", "dimtxt", 2.2)

    def north(self, x, y, r):
        self.path([(x, y + r), (x - r * 0.38, y - r * 0.55), (x, y - r * 0.22),
                   (x + r * 0.38, y - r * 0.55)], "north", "seen", fill="currentColor",
                  close=True)
        self.circle(x, y, r * 1.5, "dim", "thin")
        self.text(x, y + r * 1.9, "N", "lbl", 3.0)

    def scalebar(self, x, y, metres=5):
        u = metres * 1000.0
        for i in range(4):
            cls = "bar-on" if i % 2 == 0 else "bar-off"
            self.rect(x + i * u, y, x + (i + 1) * u, y + 0.7 * self.s,
                      cls, "thin", fill="currentColor")
        for i in range(5):
            self.text(x + i * u, y - 2.6 * self.s, f"{i * metres}", "dimtxt", 2.0)
        self.text(x + 4 * u + 1.2 * self.s, y - 2.6 * self.s, "m", "dimtxt", 2.0,
                  anchor="start")

    # -- output ----------------------------------------------------------
    def svg(self, bounds, pad=2000):
        x0, y0, x1, y1 = bounds
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
        return (f'<svg class="plate-svg" viewBox="{x0:.0f} {-y1:.0f} '
                f'{x1 - x0:.0f} {y1 - y0:.0f}" role="img" '
                f'aria-label="{esc(self.number)} {esc(self.title)}">'
                f'<g transform="scale(1,-1)">' + "".join(self.parts)
                + "</g></svg>")


# ====================================================================== PLAN
def _fabric(floor):
    """Delegates to villa_design -- one definition of the walls, not two."""
    return V.fabric(floor)


def _void_rect(o):
    return V.void_rect(o)


def _label_point(room, floor):
    """Somewhere the label actually fits: the room less anything nested in it."""
    g = box(room[1], room[2], room[3], room[4])
    for q in V.ROOMS:
        if q[6] != floor or q[0] == room[0]:
            continue
        qb = box(q[1], q[2], q[3], q[4])
        if g.contains(qb.buffer(-1)):
            g = g.difference(qb)
    if g.is_empty:
        g = box(room[1], room[2], room[3], room[4])
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda p: p.area)
    p = g.representative_point()
    return p.x, p.y


def _slide(d, o):
    """A sliding door: jambs, two glazed leaves overlapping at the middle and
    a slider line with its arrow -- no swing, no sill."""
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    lo, hi = min(a, b), max(a, b)
    w0, w1 = min(t0, t1), max(t0, t1)
    c, mid, span = (w0 + w1) / 2, (lo + hi) / 2, hi - lo
    off, lap = 40.0, min(100.0, 0.05 * span)

    def seg(a0, c0, a1, c1, cls, lw):
        if axis == "h":
            d.line(a0, c0, a1, c1, cls, lw)
        else:
            d.line(c0, a0, c1, a1, cls, lw)

    seg(lo, w0, lo, w1, "win", "open")
    seg(hi, w0, hi, w1, "win", "open")
    seg(lo, c - off, mid + lap, c - off, "win", "open")
    seg(mid - lap, c + off, hi, c + off, "win", "open")
    s, tip, ah = c + 3 * off, mid - 0.25 * span, min(150.0, 0.08 * span)
    seg(hi - 0.1 * span, s, tip, s, "leaf", "furn")
    seg(tip, s, tip + ah, s + 0.6 * ah, "leaf", "furn")
    seg(tip, s, tip + ah, s - 0.6 * ah, "leaf", "furn")


def _stairs(d, floor):
    """A STAIRS design's flights on this plate: each riser across its flight
    (clipped to the voids it is seen through on the floor it arrives at),
    the half-landing, UP / DN where the flight meets this floor."""
    from shapely.geometry import LineString
    vs = [box(*r) for _n, r in G.voids_on(floor)]
    clip = unary_union(vs) if vs else None
    lv = V.LEVEL[floor]

    def seg(a, b, role):
        g = LineString([a, b])
        if role != "up" and clip is not None:
            g = g.intersection(clip)
        for s in getattr(g, "geoms", [g]):
            if s.geom_type == "LineString" and s.length > 1.0:
                (x0, y0), (x1, y1) = s.coords[0], s.coords[-1]
                d.line(x0, y0, x1, y1, "seen", "seen")

    roles = {}
    for f, role in G.flights_on(floor):
        roles[f.get("stair", "stair")] = role
        pt = (lambda c, t: (c, t)) if f["along"] == "y" else (lambda c, t: (t, c))
        t_top = f["t_foot"] + f["dir"] * (f["n"] - 1) * f["going"]
        for k in range(f["n"]):
            t = f["t_foot"] + f["dir"] * k * f["going"]
            seg(pt(f["c0"], t), pt(f["c1"], t), role)
        for c in (f["c0"], f["c1"]):
            seg(pt(c, f["t_foot"]), pt(c, t_top), role)
        cm = (f["c0"] + f["c1"]) / 2
        if role == "up" and abs(f["z_foot"] - lv) < 1.0:
            x, y = pt(cm, f["t_foot"] + f["dir"] * 0.5 * f["going"])
            d.text(x, y - 250, "UP", "lbl", 1.8)
        elif role != "up" and abs(f["z_foot"] + f["n"] * f["rise"] - lv) < 1.0:
            x, y = pt(cm, t_top - f["dir"] * 0.5 * f["going"])
            d.text(x, y - 250, "DN", "lbl", 1.8)
    for name, (x0, y0, x1, y1), _z in G.stair_landings():
        role = roles.get(name if name is not None else "stair")
        if role:
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                seg(a, b, role)


def plan(floor, number, title):
    """A plan plate: `floor` and every floor drawn with it (the annex on the
    ground floor, villa_geom.sheet_floors)."""
    d = Draw(100, title, number)
    fls = [f for f in G.sheet_floors(floor) if V.rooms_on(f)] or [floor]
    ext, part, inner = _fabric(floor)

    for fl in fls:
        e_, p_, _ = _fabric(fl)
        voids = [_void_rect(o) for o in V.OPENINGS if o[0] == fl]
        if voids:
            cut = unary_union(voids)
            e_, p_ = e_.difference(cut), p_.difference(cut)
        # cut fabric, poche filled
        d.poly(e_, "w-ext", "ext", fill="var(--poche)")
        d.poly(p_, "w-part", "part", fill="var(--poche)")

    # shading overhead (fins, V.SHADES), dashed
    for x0, y0, x1, y1 in G.overhead(floor):
        d.rect(x0, y0, x1, y1, "terr ovhd", "fix",
               style=f"stroke-dasharray:{1.2 * d.s:.0f} {0.8 * d.s:.0f}")
    # glass guards standing on this sheet's floors (V.guards)
    for x0, y0, x1, y1 in G.guards_on(floor):
        d.rect(x0, y0, x1, y1, "win guard", "open")
    # landings and flights outside the external doors
    if floor == "GF":
        for x0, y0, z0, x1, y1, z1 in V.external_steps():
            d.rect(x0, y0, x1, y1, "terr", "thin")

    # stair, drawn as real treads at STAIR_GOING (villa_geom.stair_risers);
    # a design with several STAIRS: every flight on the sheets it joins
    # (villa_geom.flights_on), seen down its void on the arrival floor
    if hasattr(V, "STAIRS"):
        _stairs(d, floor)
    elif floor in ("GF", "FF"):
        sx0, sy0, sx1, sy1 = V.STAIR
        mid = (sx0 + sx1) / 2
        d.rect(sx0, sy0, sx1, sy1, "seen", "seen")
        for x0_, yy, x1_ in G.stair_risers():
            d.line(x0_ + 60, yy, x1_ - 60, yy, "seen", "seen")
        yl = G.stair_landing_edge()
        if yl is not None:
            d.line(sx0, yl, sx1, yl, "seen", "seen")
            d.line(mid, sy0, mid, yl, "seen", "seen")
        d.path([(sx0 + 60, sy0 + (sy1 - sy0) * 0.42),
                (mid - 60, sy0 + (sy1 - sy0) * 0.58)], "arrow", "seen")
        d.text(mid, sy1 + 400, "UP" if floor == "GF" else "DN", "lbl", 2.2)

    # openings
    for o in V.OPENINGS:
        if o[0] not in fls:
            continue
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        r = _void_rect(o)
        bx = r.bounds
        if kind == V.SLIDE:
            _slide(d, o)
            continue
        if kind == V.WIN:
            if axis == "h":
                d.line(bx[0], (bx[1] + bx[3]) / 2, bx[2], (bx[1] + bx[3]) / 2,
                       "win", "open")
            else:
                d.line((bx[0] + bx[2]) / 2, bx[1], (bx[0] + bx[2]) / 2, bx[3],
                       "win", "open")
            d.rect(bx[0], bx[1], bx[2], bx[3], "win", "thin")
            continue
        if kind == V.OPEN or sw is None:
            d.line(bx[0], bx[1], bx[0], bx[3], "open", "open") if axis == "v" \
                else d.line(bx[0], bx[1], bx[2], bx[1], "open", "open")
            continue
        pts = F._swing(o)
        if pts:
            d.path(pts[1:], "swing", "furn")
            d.line(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], "leaf", "open")

    # furniture, the annex's included
    for fl, (key, x, y, rot) in G.sheet_furniture(floor):
        fp = F.footprint(key, x, y, rot)
        if fp:
            d.rect(fp[0], fp[1], fp[2], fp[3], "furn", "furn")
            if key in ("bed_double", "bed_single"):
                d.line(fp[0], fp[3] - 500, fp[2], fp[3] - 500, "furn", "furn")

    # labels: NET area, as the schedule and the DXF sheets give it -- the
    # rectangle of a bedroom includes its en-suite
    for fl in fls:
        for r in V.rooms_on(fl):
            lx, ly = _label_point(r, fl)
            area = V.net_area(r)
            small = area < 7.0
            d.text(lx, ly + (60 if small else 140), r[0], "lbl", 2.1 if small else 2.5)
            d.text(lx, ly - (330 if small else 320), f"{area:.1f} m2", "lblnum",
                   1.8 if small else 2.0)

    b = inner.buffer(V.WALL, join_style=2).bounds
    d.dim(b[0], b[1], b[2], b[1], -1800, f"{b[2] - b[0]:.0f}")
    d.dim(b[0], b[1], b[0], b[3], -1800, f"{b[3] - b[1]:.0f}", vertical=True)
    B = unary_union([V.outline(f) for f in fls]).bounds
    for fl in fls:                  # overall dimensions of the annex
        if fl == floor:
            continue
        a0, a1, a2, a3 = V.outline(fl).bounds
        d.dim(a0, a3, a2, a3, 1200, f"{a2 - a0:.0f}")
        d.dim(a2, a1, a2, a3, 1200, f"{a3 - a1:.0f}", vertical=True)
    d.north(B[2] + 1400 + (2400 if len(fls) > 1 else 0), B[3] - 900, 600)
    d.scalebar(B[0], B[3] + 1500 + (1200 if len(fls) > 1 else 0), 5)
    top = B[3] + 2600 + (1200 if len(fls) > 1 else 0)
    right = B[2] + 2400 + (2400 if len(fls) > 1 else 0)
    return d.svg((min(b[0], B[0]) - 2600, min(b[1], B[1]) - 2600, right, top),
                 pad=400)


# ====================================================================== SITE
def site():
    d = Draw(200, "Site plan", "A-101")
    P_W, P_D, BW = V.PLOT_W, V.PLOT_D, G.BW

    d.rect(0, 0, P_W, P_D, "plot", "seen")
    ring = box(0, 0, P_W, P_D).difference(box(BW, BW, P_W - BW, P_D - BW))
    gates = unary_union([box(g0, P_D - BW - 50, g1, P_D + 50)
                         for _n, g0, g1, _h in G.gates()])
    d.poly(ring.difference(gates), "w-ext", "ext", fill="var(--poche)")

    for fl in G.ground_floors():    # the house, and the annex beside it
        ext, part, inner = _fabric(fl)
        d.poly(V.outline(fl), "bldg", "ext", fill="var(--bldg)")
        d.poly(inner, "bldg-in", "seen", fill="none")
        if fl != "GF":
            c = V.outline(fl).representative_point()
            d.text(c.x, c.y - 300, G.FLOOR_NAME.get(fl, fl), "lbl", 2.2)

    # water
    d.rect(V.POOL_X0, V.POOL_Y0, V.POOL_X1, V.POOL_Y1, "water", "seen",
           fill="var(--water)")
    if hasattr(V, "BASIN_Y0"):      # an overflow pool's balance basin
        d.rect(V.POOL_X0 - 400, V.BASIN_Y0, V.POOL_X1 + 400, V.BASIN_Y1,
               "basin", "open")
    if getattr(V, "POOL_LEDGE", None):              # a sun ledge
        lx0, ly0, lx1, ly1, _lz = V.POOL_LEDGE
        d.rect(lx0, ly0, lx1, ly1, "basin", "thin")
    for x0, y0, z0, x1, y1, z1 in G.grate_boxes():      # the walkable grate
        for xx in range(int(x0) + 150, int(x1), 300):
            d.line(xx, y0, xx, y1, "basin", "thin")
    for y, z in sorted(getattr(V, "POOL_FLOOR", ()))[1:-1]:   # floor breaks
        d.line(V.POOL_X0, y, V.POOL_X1, y, "basin", "thin")
    if getattr(V, "POOL_PLANT", None):
        x0, y0, x1, y1 = V.POOL_PLANT
        d.rect(x0, y0, x1, y1, "terr ovhd", "fix",
               style=f"stroke-dasharray:{1.2 * d.s:.0f} {0.8 * d.s:.0f}")
        d.text((x0 + x1) / 2, (y0 + y1) / 2, "POOL PLANT BELOW", "lblnum", 1.6)
    for x0, y0, z0, x1, y1, z1 in V.external_steps():
        d.rect(x0, y0, x1, y1, "terr", "thin")
    for x0, y0, x1, y1 in G.guards_on(G.GROUND_FLOOR):
        d.rect(x0, y0, x1, y1, "win guard", "open")
    villa = all(hasattr(V, a) for a in ("AXIS", "RILL_W", "WG_Y0"))
    if villa:                       # the villa's rill and terrace
        d.rect(V.AXIS - V.RILL_W / 2, V.POOL_Y1, V.AXIS + V.RILL_W / 2, V.WG_Y0,
               "water", "fix", fill="var(--water)")

    # terrace, forecourt (measured, as validate() measures it)
    if villa:
        d.rect(V.POOL_X0 - 1800, V.POOL_Y1, V.POOL_X1 + 1800, V.WG_Y0, "terr", "thin")
    d.rect(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, V.PORCH_Y1, "terr", "thin")
    depth, _w = G.forecourt()
    fy = (P_D - BW) - depth / 2
    d.text((V.PORCH_X0 + V.PORCH_X1) / 2, fy + 400, "FORECOURT", "lbl", 2.4)
    d.text((V.PORCH_X0 + V.PORCH_X1) / 2, fy - 400, G.forecourt_text(),
           "lblnum", 1.9)

    # gates, from the design data (V.gates)
    for name, g0, g1, _h in G.gates():
        d.line(g0, P_D - BW / 2, g1, P_D - BW / 2, "gate", "part")
        d.text((g0 + g1) / 2, P_D + 700, f"{name.split()[0]} {g1 - g0:.0f}",
               "lblnum", 1.6)

    from shapely.geometry import Point
    built = G.footprint()
    trees = (((5200, 26000, 1400), (9400, 26900, 1200),
              (4600, 6000, 1700), (19400, 6600, 1700), (19600, 2600, 1500))
             if not hasattr(V, "SITE_TREES")
             else [(x, y, dd / 2.0) for x, y, dd in V.SITE_TREES])
    for cx, cy, r in trees:
        if Point(cx, cy).buffer(0.6 * r).intersects(built):
            continue                # no tree planted through a roof
        d.circle(cx, cy, r, "tree", "furn")
        d.circle(cx, cy, 180, "tree", "fix")

    _gf = V.outline(G.GROUND_FLOOR).area / 1e6
    _cv = G.site_numbers()["cover"]
    if villa:
        d.text(V.AXIS, 6800, "OVERFLOW POOL", "lbl", 2.6)
        d.text(V.AXIS, 5800, G.pool_text().replace("   ", "  /  "), "lblnum", 2.0)
        d.text(V.AXIS, (V.BASIN_Y0 + V.BASIN_Y1) / 2 - 150,
               "BALANCE BASIN" + (" UNDER A GRATE" if G.grate_boxes() else ""),
               "lblnum", 1.6)
        d.text(V.AXIS, 17000, "VILLA", "lbl", 3.2)
        d.text(V.AXIS, 15900,
               f"{_gf:.1f} m2 FOOTPRINT  /  {_cv:.1f}% COVER", "lblnum", 2.0)
    else:                           # a project: from its own geometry
        pcx, pcy = (V.POOL_X0 + V.POOL_X1) / 2, (V.POOL_Y0 + V.POOL_Y1) / 2
        d.text(pcx, pcy + 300, getattr(V, "POOL_LABEL", "POOL"), "lbl", 2.2)
        d.text(pcx, pcy - 600, G.pool_text().replace("   ", "  /  "), "lblnum", 1.6)
        c = V.outline(G.GROUND_FLOOR).representative_point()
        name = (getattr(V, "PROJECT_TITLE", None) or "VILLA").split(" -- ")[0]
        d.text(c.x, c.y + 500, name, "lbl", 3.2)
        d.text(c.x, c.y - 600,
               f"{_gf:.1f} m2 FOOTPRINT  /  {_cv:.1f}% COVER", "lblnum", 2.0)

    d.dim(0, 0, P_W, 0, -2200, f"{P_W:.0f}")
    d.dim(0, 0, 0, P_D, -2200, f"{P_D:.0f}", vertical=True)
    if villa:
        d.dim(V.POOL_X0, V.POOL_Y1, V.POOL_X0, V.WG_Y0, -1200,
              f"{V.WG_Y0 - V.POOL_Y1:.0f}", vertical=True)
    d.north(P_W + 2600, P_D - 1800, 1000)
    d.scalebar(0, P_D + 1800, 5)
    return d.svg((-3400, -3400, P_W + 4200, P_D + 4200), pad=600)


# =================================================================== SECTION
def section():
    """Long section on the axis at x = 12000, looking west."""
    d = Draw(100, "Section AA", "A-201")
    GF, FF, RF = V.GF, V.FF, V.RF
    # taken from the derived envelope, not from constants the plan has moved
    # away from: the ground floor runs to 24000, the first floor stops at 23200
    gb = V.fabric("GF")[2].buffer(V.WALL, join_style=2).bounds
    fb = V.fabric("FF")[2].buffer(V.WALL, join_style=2).bounds
    Y0, Y1 = gb[1], gb[3]
    FY1 = fb[3]
    LV0, LV1 = Y0, 16750.0             # the double-height slice on this axis

    d.line(-1500, 0, V.PLOT_D + 1500, 0, "ground", "part")
    for x in range(-1000, int(V.PLOT_D) + 1500, 700):
        d.line(x, 0, x - 420, -420, "hatch", "thin")

    # boundary walls
    d.rect(0, 0, 350, 2400, "w-ext", "ext", fill="var(--poche)")
    d.rect(V.PLOT_D - 350, 0, V.PLOT_D, 2000, "w-ext", "ext", fill="var(--poche)")

    # pool, basin, water -- the pool's water on its floor PROFILE
    # (V.pool_section), not a constant-depth box
    d.rect(V.POOL_Y0 - 400, V.POOL_FL - 400, V.POOL_Y1 + 400, V.POOL_TW,
           "w-ext", "ext", fill="var(--poche)")
    d.path(V.pool_section(V.POOL_TW), "water", "seen", fill="var(--water)",
           close=True)
    if hasattr(V, "BASIN_Y0"):      # an overflow pool's balance basin
        d.rect(V.BASIN_Y0, V.BASIN_FL, V.BASIN_Y1, V.BASIN_WL, "water", "open",
               fill="var(--water)")
    for gx0, gy0, gz0, gx1, gy1, gz1 in G.grate_boxes():   # section is along y
        d.rect(gy0, gz0, gy1, gz1, "w-part", "part", fill="var(--poche)")
    d.text(V.POOL_Y0 + 3300, V.POOL_TW + 700, f"TW +{V.POOL_TW:.0f}", "lblnum", 2.0)
    if hasattr(V, "BASIN_Y0"):
        d.text(V.BASIN_Y0 + 600, V.BASIN_FL + 500, "BALANCE", "lblnum", 1.8)

    # slabs
    d.rect(Y0, GF - V.SLAB, Y1, GF, "slab", "ext", fill="var(--poche)")
    d.rect(LV1, FF - V.SLAB, FY1, FF, "slab", "ext", fill="var(--poche)")
    d.rect(Y0, RF, FY1, RF + V.SLAB, "slab", "ext", fill="var(--poche)")
    d.rect(Y0, RF + V.SLAB, Y0 + 350, RF + V.SLAB + V.PARAPET, "slab", "part",
           fill="var(--poche)")
    d.rect(FY1 - 350, RF + V.SLAB, FY1, RF + V.SLAB + V.PARAPET, "slab", "part",
           fill="var(--poche)")

    # end walls and the one internal wall this cut passes
    d.rect(Y0, GF, Y0 + 350, RF, "w-ext", "ext", fill="var(--poche)")
    d.rect(FY1 - 350, GF, FY1, RF, "w-ext", "ext", fill="var(--poche)")
    d.rect(LV1, FF, LV1 + 150, RF, "w-part", "part", fill="var(--poche)")

    # cantilever over the terrace
    d.rect(LV0 - 3000, RF, LV0, RF + V.SLAB, "slab", "ext", fill="var(--poche)")

    # level tags
    for z, tag in ((GF, f"+{GF:.0f}  GROUND"), (FF, f"+{FF:.0f}  FIRST"),
                   (RF + V.SLAB, f"+{RF + V.SLAB:.0f}  ROOF")):
        d.line(Y1 + 400, z, Y1 + 3400, z, "dim", "thin")
        d.path([(Y1 + 3400, z), (Y1 + 3700, z + 300), (Y1 + 4000, z)], "dim", "thin")
        d.text(Y1 + 4200, z + 160, tag, "lblnum", 2.0, anchor="start")
    d.text((LV1 + FY1) / 2, 2400, "", "lbl", 0.1)

    d.text((LV0 + LV1) / 2, 4200, "DOUBLE HEIGHT", "lbl", 2.6)
    d.text((LV0 + LV1) / 2, 3200, "6400 CLEAR", "lblnum", 2.1)
    d.text((LV1 + FY1) / 2, 2400, "MAJLIS / HALL", "lbl", 2.3)
    d.text((LV1 + FY1) / 2, 6400, "BEDROOMS", "lbl", 2.3)
    d.text(V.POOL_Y0 + 3300, V.POOL_FL - 1100,
           f"POOL {V.POOL_TW - V.POOL_SHALLOW_FL:.0f} TO {V.POOL_TW - V.POOL_FL:.0f} DEEP",
           "lblnum", 2.0)
    d.text(LV0 - 1500, RF + 1300, "CANTILEVER 3000", "lblnum", 2.0)

    d.dim(LV0, GF, LV0, RF, -1400, f"{RF - GF:.0f}", vertical=True)
    d.scalebar(Y0, -3600, 5)
    return d.svg((-2000, -4600, V.PLOT_D + 9000, RF + 4000), pad=500)


if __name__ == "__main__":
    import os
    # plates go beside the script, as always -- or into VILLA_OUT when set
    dest = os.environ.get("VILLA_OUT") or ""
    if dest:
        os.makedirs(dest, exist_ok=True)
    plates = (("site", site), ("gf", lambda: plan("GF", "A-102", "Ground floor")),
              ("ff", lambda: plan("FF", "A-103", "First floor")),
              ("section", section))
    if getattr(V, "PLAN_SHEETS", None):
        # a project design: its own plan sheets (villa_geom.plan_sheets); the
        # section plate is the villa's (villa_elevations draws a project's)
        plates = (("site", site),) + tuple(
            (fl.lower(), (lambda fl=fl, no=no, t=t: plan(fl, no, (t or fl).title())))
            for fl, no, t in G.plan_sheets())
    for name, fn in plates:
        s = fn()
        path = os.path.join(dest, f"plate_{name}.svg")
        open(path, "w", encoding="utf-8").write(s)
        print(f"{name:8s} {len(s):>7,} bytes  ->  {os.path.abspath(path)}")
