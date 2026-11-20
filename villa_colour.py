"""Coloured presentation drawings - site plan and both floors.

The technical set (A-101/102/103) stays monochrome, because that is what gets
plotted and checked. This is the other half of the deliverable: the same
geometry, rendered in plan, so a pool reads as water and a garden reads as
green. Everything is driven from villa_design.py, so the two sets cannot
diverge.

Colours are true-colour RGB, not ACI, so they survive plotting without a CTB.

The annex (floor "AX") -- rooms, walls, openings, furniture -- is drawn on the
ground-floor sheet and the site plan; sliding doors, dashed overhead shading
and the computed title block come from villa_cad / villa_geom, so the two sets
say the same thing. VILLA_OUT (environment) redirects the output folder.

A project design (PLAN_SHEETS; run through run_project.py) gets its sheets
from villa_geom.plan_sheets() with a P suffix, a PNG beside every DXF, the
level in the title block, fills by ROLE and for the "amenity" kind, every
house stair (villa_cad.stairs), guards, stone, the balcony and the building's
projections on its plans, and -- on the site plan -- its own surfaces, sun
ledge, SITE_TREES, SHADES, forecourt ramp and labels placed from its
geometry. The villa's basin, rill and typed label positions are drawn only
when the design has them; the villa's sheets do not change.
"""

from __future__ import annotations

import math
import os

import ezdxf
from shapely.geometry import Point, box
from shapely.ops import unary_union

import plan_dxf as PD
import villa_design as V
import villa_furniture_spec as F
import villa_geom as G

OUT = G.out_dir()

# ----------------------------------------------------------------- palette
# Desaturated and daylit rather than saturated: a plan in primary colours
# reads as a schoolbook, not a proposal.
C = {
    "water":     (0x2C, 0x74, 0x86),
    "water_lt":  (0x4A, 0x94, 0xA4),
    "basin":     (0x1E, 0x55, 0x63),
    "lawn":      (0x7C, 0x9B, 0x5A),
    "lawn_dk":   (0x63, 0x82, 0x45),
    "planting":  (0x5B, 0x7C, 0x44),
    "canopy":    (0x6E, 0x92, 0x50),
    "gravel":    (0xD8, 0xCE, 0xBB),
    "paving":    (0xC6, 0xC2, 0xB8),
    "drive":     (0x9B, 0x99, 0x95),
    "deck":      (0xB4, 0x8A, 0x5E),
    "stone":     (0xE2, 0xDC, 0xCF),
    "oak":       (0xD4, 0xB4, 0x8B),
    "tile":      (0xCF, 0xDA, 0xDA),
    "service":   (0xD3, 0xCE, 0xC4),
    "circ":      (0xDD, 0xD6, 0xC6),
    "roofline":  (0xB2, 0xAE, 0xA6),
    "poche":     (0x3A, 0x3A, 0x38),
    "wall":      (0x55, 0x55, 0x52),
    "furn":      (0x8A, 0x84, 0x78),
    "ink":       (0x1A, 0x1A, 0x18),
    "porcelain": (0xFF, 0xFF, 0xFF),    # sanitaryware, on any floor
    # for project designs (no villa room or surface uses these)
    "amenity":   (0xCF, 0xB8, 0xAE),    # basement recreation rooms (carpet)
    "ledge":     (0x7F, 0xBC, 0xC8),    # a pool's in-water sun ledge
    "stonewall": (0x4A, 0x4A, 0x4C),    # dark stacked stone
    "timber":    (0x8B, 0x5A, 0x2B),    # fins, louvres
}

# floor finish per room kind, then per-room overrides
KIND_FILL = {V.HAB: "stone", V.CIRC: "circ", V.WET: "tile"}
if hasattr(V, "AMEN"):          # "amenity": a design's basement recreation rooms
    KIND_FILL[V.AMEN] = "amenity"
ROOM_FILL = {
    "BEDROOM 2": "oak", "BEDROOM 3": "oak", "BEDROOM 4": "oak",
    "MASTER BEDROOM": "oak", "LANDING": "oak", "CORRIDOR": "oak",
    "DIRTY KITCHEN": "service", "PANTRY": "service",
}
# A project design (PLAN_SHEETS) also gets its finishes by ROLE, so a fifth
# bedroom or a second corridor is oak like the villa's; the villa's fills are
# ROOM_FILL / KIND_FILL exactly as before.
ROLE_FILL = {"bedroom": "oak", "master_bedroom": "oak", "landing": "oak",
             "corridor": "oak", "dressing": "oak", "pantry": "service"}
PROJECT_SHEETS = bool(getattr(V, "PLAN_SHEETS", None))


def room_fill(r):
    """The finish colour key of room `r`."""
    if r[0] in ROOM_FILL:
        return ROOM_FILL[r[0]]
    if PROJECT_SHEETS:
        role = (getattr(V, "ROLE", None) or {}).get(r[0])
        if role in ROLE_FILL:
            return ROLE_FILL[role]
    return KIND_FILL.get(r[5], "service")

LAYERS = [
    ("L-SITE-LAWN", "lawn"), ("L-SITE-PLNT", "planting"),
    ("L-SITE-GRVL", "gravel"), ("L-SITE-PAVE", "paving"),
    ("L-SITE-DRIV", "drive"), ("L-SITE-DECK", "deck"),
    ("L-SITE-WATR", "water"), ("L-SITE-TREE", "canopy"),
    ("A-FLOR-FILL", "stone"), ("A-WALL-FILL", "poche"),
    ("A-FURN-FILL", "furn"), ("A-ROOF-FILL", "roofline"),
]


def ground_surfaces():
    """The landscape as disjoint polygons, keyed by material.

    A design that lays out its own site (V.ground_surfaces(), the same keys)
    is returned as it is; the villa's garden, rill and weir are below."""
    if hasattr(V, "ground_surfaces"):
        return V.ground_surfaces()
    return _villa_ground_surfaces()


def _villa_ground_surfaces():
    """The villa's landscape as disjoint polygons, keyed by material.

    Shared by the coloured site plan and the 3D model so the garden you see in
    plan is the garden that gets rendered. "house" is every building on the
    ground -- the annex included -- so no lawn is laid inside it."""
    W, D, BW = V.PLOT_W, V.PLOT_D, getattr(V, "BOUNDARY_T", 350.0)
    house = G.footprint()
    ground = box(BW, BW, W - BW, D - BW)

    drive = box(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, D - BW)
    pool_o = box(V.POOL_X0 - 400, V.POOL_Y0 - 400, V.POOL_X1 + 400,
                 V.POOL_Y1 + 400)
    # The water itself, and everything the ground must NOT be built over. The
    # coping is a RING: laid as a full slab it becomes a lid on the pool. And
    # not over the weir: a coping 4 mm above the crest is a lip that holds the
    # water in, so the overflow edge is left as the bare knife edge it is.
    water_r = box(V.POOL_X0, V.POOL_Y0, V.POOL_X1, V.POOL_Y1)
    weir_r = box(V.POOL_X0, V.POOL_Y0 - V.WEIR, V.POOL_X1, V.POOL_Y0)
    basin_r = box(V.POOL_X0 - 400, V.BASIN_Y0, V.POOL_X1 + 400, V.BASIN_Y1)
    pool_zone = unary_union([pool_o, basin_r])
    plant = box(*V.POOL_PLANT) if getattr(V, "POOL_PLANT", None) else None
    # DBC K-POOL-09: a continuous deck 1.2 m wide round the pool, beyond the
    # 400 coping; the terrace in front of the house is part of it. Over the
    # balance basin the deck is its grate (V.grate(), drawn and built).
    ring = pool_o.buffer(1200.0, join_style=2).difference(pool_o)
    terr = unary_union([box(V.POOL_X0 - 1800, V.POOL_Y1, V.POOL_X1 + 1800,
                            V.WG_Y0), ring]).difference(pool_zone)
    deck = box(V.POOL_X1 + 400, V.POOL_Y0, W - BW - 1200, V.POOL_Y1)
    # Paths from the gates (V.gates()) to the steps they serve, and a walk
    # from the foot of every street-side flight to the pedestrian path --
    # derived, so they follow the gates and doors.
    walks = []
    recs = V.stairs_out() if hasattr(V, "stairs_out") else []
    step_boxes = [b for r in recs for b in [r["landing"]] + r["flights"]]
    gates = V.gates() if hasattr(V, "gates") else []
    ped = next(((g0, g1) for n, g0, g1, h in gates if "PED" in n), None)
    for n, g0, g1, head in gates:
        if head is None:
            continue                       # the vehicle gate opens on the drive
        near = [b for b in step_boxes if b[0] < g1 and b[3] > g0 and b[1] > V.WG_Y1]
        y_end = max([b[4] for b in near], default=D - BW - 1400)
        walks.append(box(g0, y_end, g1, D - BW))
    for r in recs:
        if r["door"][0] == "GF" and r["axis"] == "h" and r["sign"] > 0 and ped:
            fb = (r["flights"] or [r["landing"]])[-1]
            walks.append(box(min(fb[0], ped[0]), fb[4], max(fb[3], ped[1]),
                             fb[4] + 1200))
    pathw = unary_union(walks) if walks else box(V.AXIS - 900, D - BW - 1400,
                                                  V.AXIS + 900, D - BW)
    beds = unary_union([
        box(BW, BW, W - BW, 1800),
        box(BW, 1800, V.POOL_X0 - 2400, 10400),
        box(BW, D - BW - 1200, W - BW, D - BW),
        box(W - BW - 1200, 1800, W - BW, 10400),
    ])
    mulch = beds.buffer(650, join_style=2).difference(beds)

    out, taken = {}, house
    for name, geom in (("drive", drive),
                       ("poolsurround", pool_o.difference(water_r).difference(weir_r)),
                       ("terrace", terr), ("deck", deck), ("path", pathw),
                       ("beds", beds), ("mulch", mulch)):
        g = geom.intersection(ground).difference(taken).difference(pool_zone
                                                                   if name != "poolsurround"
                                                                   else water_r)
        taken = taken.union(geom)
        if not g.is_empty:
            out[name] = g
    out["lawn"] = ground.difference(taken).difference(pool_zone)
    out["house"] = house
    # not drawn: the hole the ground needs -- the pool, the basin, and the
    # plant vault beside it (its roof is the deck and the lawn over it)
    out["poolzone"] = pool_zone if plant is None else pool_zone.union(plant)
    return out


def setup(title):
    p = PD.Plan(title)
    for name, key in LAYERS:
        if name not in p.doc.layers:
            lay = p.doc.layers.add(name)
            lay.rgb = C[key]
    return p


def fill(p, geom, layer, key, alpha=None):
    """Solid true-colour fill behind the linework."""
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        if g.is_empty or g.geom_type != "Polygon":
            continue
        h = p.msp.add_hatch(dxfattribs={"layer": layer})
        h.rgb = C[key]
        h.paths.add_polyline_path(list(g.exterior.coords), is_closed=True)
        for ring in g.interiors:
            h.paths.add_polyline_path(list(ring.coords), is_closed=True)
        if alpha is not None:
            h.transparency = alpha


def fill_rect(p, x0, y0, x1, y1, layer, key, alpha=None):
    fill(p, box(x0, y0, x1, y1), layer, key, alpha)


def pattern(p, geom, layer, key, name="ANSI31", scale=400.0, angle=0.0):
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        if g.is_empty or g.geom_type != "Polygon":
            continue
        h = p.msp.add_hatch(dxfattribs={"layer": layer})
        h.set_pattern_fill(name, scale=scale, angle=angle)
        h.rgb = C[key]
        h.paths.add_polyline_path(list(g.exterior.coords), is_closed=True)


def outline(p, geom, layer, colour=None):
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        for ring in [g.exterior] + list(g.interiors):
            e = PD.poly(p.msp, list(ring.coords), layer)
            if colour:
                e.rgb = C[colour]


def tree(p, cx, cy, r, key="canopy", seed=0):
    """A canopy with an irregular edge. A regular star reads as a cog, which
    is exactly what the first version looked like."""
    import random
    rng = random.Random(int(cx) * 7919 + int(cy) * 104729 + seed)
    n = 30
    pts = []
    lobe = rng.uniform(0.10, 0.20)
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1.0 - lobe * (0.5 + 0.5 * math.sin(a * rng.choice((3, 4, 5))))
                  + rng.uniform(-0.05, 0.05))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    h = p.msp.add_hatch(dxfattribs={"layer": "L-SITE-TREE"})
    h.rgb = C[key]
    h.paths.add_polyline_path(pts, is_closed=True)
    h.transparency = 0.25
    e = PD.poly(p.msp, pts, "L-SITE-TREE")
    e.rgb = C["lawn_dk"]
    c = p.msp.add_circle((cx, cy), r * 0.09, dxfattribs={"layer": "L-SITE-TREE"})
    c.rgb = C["lawn_dk"]


# ------------------------------------------------------------------- site
def draw_building(p, fl):
    """A floor as a coloured plan: floor finishes, poche cut by its openings,
    outside face. Used for the house and the annex on the site plan."""
    ext, part, inner = V.fabric(fl)
    for r in V.rooms_on(fl):
        fill(p, V.net_poly(r), "A-FLOR-FILL", room_fill(r))
    cut = unary_union([V.void_rect(o) for o in V.OPENINGS if o[0] == fl])
    fill(p, ext.difference(cut), "A-WALL-FILL", "poche")
    fill(p, part.difference(cut), "A-WALL-FILL", "wall")
    outline(p, V.outline(fl), "A-WALL-EXTR")


def site(val=None):
    p = setup("Site plan - presentation")
    W, D, BW = V.PLOT_W, V.PLOT_D, G.BW
    house = G.footprint()           # the house and the annex

    # Surfaces, laid down before anything else: ground_surfaces() -- the SAME
    # disjoint polygons the 3D landscape is built from (this plan used to
    # re-derive its own, and drew a deck ring the model did not have).
    surf = ground_surfaces()
    STYLE = (("drive",        "L-SITE-DRIV", "drive",    ("ANSI31", 300.0, 45.0)),
             ("poolsurround", "L-SITE-PAVE", "stone",    None),
             ("terrace",      "L-SITE-PAVE", "paving",   ("ANSI37", 600.0, 0.0)),
             ("deck",         "L-SITE-DECK", "deck",     ("ANSI31", 500.0, 90.0)),
             ("path",         "L-SITE-PAVE", "paving",   ("ANSI37", 500.0, 0.0)),
             ("beds",         "L-SITE-PLNT", "planting", ("GRASS", 450.0, 45.0)),
             ("mulch",        "L-SITE-GRVL", "gravel",   ("AR-SAND", 55.0, 0.0)))
    lawn = surf["lawn"]
    fill(p, lawn, "L-SITE-LAWN", "lawn")
    pattern(p, lawn, "L-SITE-LAWN", "lawn_dk", "GRASS", 900.0)
    for key, layer, colour, pat in STYLE:
        g = surf.get(key)
        if g is None or g.is_empty:
            continue
        fill(p, g, layer, colour)
        if pat:
            pattern(p, g, layer, "ink" if colour == "gravel" else "lawn_dk",
                    pat[0], pat[1], pat[2])

    # water last of the surfaces, so its edge stays crisp; the shallow shelf
    # (the flat of the floor profile at the house end) a lighter blue. The
    # balance basin and the rill are the villa's (an overflow pool); a
    # skimmer pool has neither, and may have a sun ledge (POOL_LEDGE).
    basin = (box(V.POOL_X0 - 400, V.BASIN_Y0, V.POOL_X1 + 400, V.BASIN_Y1)
             if hasattr(V, "BASIN_Y0") else None)
    rill = (box(V.AXIS - V.RILL_W / 2, V.POOL_Y1, V.AXIS + V.RILL_W / 2, V.WG_Y0)
            if all(hasattr(V, a) for a in ("AXIS", "RILL_W", "WG_Y0")) else None)
    fill_rect(p, V.POOL_X0, V.POOL_Y0, V.POOL_X1, V.POOL_Y1,
              "L-SITE-WATR", "water")
    shelf = [y for y, z in getattr(V, "POOL_FLOOR", ())
             if abs(z - getattr(V, "POOL_SHALLOW_FL", V.POOL_FL)) < 1]
    if shelf:
        fill_rect(p, V.POOL_X0, min(shelf), V.POOL_X1, max(shelf),
                  "L-SITE-WATR", "water_lt")
    if getattr(V, "POOL_LEDGE", None):                 # the in-water sun ledge
        lx0, ly0, lx1, ly1, _lz = V.POOL_LEDGE
        fill_rect(p, lx0, ly0, lx1, ly1, "L-SITE-WATR", "ledge")
        outline(p, box(lx0, ly0, lx1, ly1), "L-SITE-WATR", "water")
    if basin is not None:
        fill(p, basin, "L-SITE-WATR", "basin")
    for x0, y0, z0, x1, y1, z1 in G.grate_boxes():    # the walkable grate
        fill_rect(p, x0, y0, x1, y1, "L-SITE-PAVE", "roofline")
        pattern(p, box(x0, y0, x1, y1), "L-SITE-PAVE", "ink", "ANSI37", 150.0)
    if rill is not None:
        fill(p, rill, "L-SITE-WATR", "water")
    if getattr(V, "POOL_PLANT", None):                # vault below the deck
        e = PD.poly(p.msp, PD.rect_pts(*V.POOL_PLANT), "A-SHDE-OVHD"
                    if "A-SHDE-OVHD" in p.doc.layers else "A-FLOR-FILL")
        e.rgb = C["ink"]

    # the house, shown as a real ground-floor plan rather than a hollow ring,
    # and the annex beside it the same way; steps up to every external door,
    # and the glass guards at the landings and the garden's open edges
    for fl in G.ground_floors():
        draw_building(p, fl)
    for x0, y0, z0, x1, y1, z1 in V.external_steps():
        fill_rect(p, x0, y0, x1, y1, "L-SITE-PAVE", "stone")
        outline(p, box(x0, y0, x1, y1), "A-FLOR-FILL", "ink")
    in_house = house.buffer(1.0) if PROJECT_SHEETS else None
    for x0, y0, x1, y1 in G.guards_on(G.GROUND_FLOOR):
        if in_house is not None and in_house.contains(box(x0, y0, x1, y1)):
            continue                # a project: the garden's guards, not the stairs'
        fill_rect(p, x0, y0, x1, y1, "A-FLOR-FILL", "water")
        outline(p, box(x0, y0, x1, y1), "A-FLOR-FILL", "ink")
    if PROJECT_SHEETS:
        site_extras(p)

    # boundary wall and gates (V.gates())
    ring = box(0, 0, W, D).difference(box(BW, BW, W - BW, D - BW))
    gates = unary_union([box(g0, D - BW - 60, g1, D + 60)
                         for _n, g0, g1, _h in G.gates()])
    fill(p, ring.difference(gates), "A-WALL-FILL", "poche")
    outline(p, ring.difference(gates), "A-WALL-EXTR")
    for _n, a, b, _h in G.gates():
        e = p.msp.add_line((a, D - BW / 2), (b, D - BW / 2),
                           dxfattribs={"layer": "A-DOOR"})
        e.rgb = C["ink"]

    for i, (cx, cy, r) in enumerate(site_trees()):
        if Point(cx, cy).buffer(0.6 * r).intersects(house):
            continue                # no tree planted through a roof
        tree(p, cx, cy, r, seed=i)

    depth, _w = G.forecourt()
    fx, fy = (V.PORCH_X0 + V.PORCH_X1) / 2, (D - BW) - depth / 2
    if hasattr(V, "POOL_LABEL"):    # a project: labels from its own geometry
        labels_ = site_labels(surf)
    else:
        labels_ = [("OVERFLOW POOL", V.AXIS, 5200, 320),
                   (f"{G.pool_text()}   TW +{V.POOL_TW:.0f}", V.AXIS, 4550, 200),
                   (f"{V.POOL_TW - getattr(V, 'POOL_SHALLOW_FL', V.POOL_FL):.0f} TO "
                    f"{V.POOL_TW - V.POOL_FL:.0f} DEEP", V.AXIS, 3950, 180),
                   ("GARDEN", 5600, 9200, 300),
                   ("POOL DECK", 18200, 6500, 240)]
    if getattr(V, "POOL_PLANT", None):
        x0, y0, x1, y1 = V.POOL_PLANT
        labels_.append(("POOL PLANT BELOW", (x0 + x1) / 2, (y0 + y1) / 2, 160))
    labels_ += [
               ("FORECOURT", fx, fy + 300, 280),
               (G.forecourt_text(), fx, fy - 300, 200)]
    for fl in G.ground_floors():
        if fl == G.GROUND_FLOOR:
            continue
        c = V.outline(fl).representative_point()
        labels_.append((G.FLOOR_NAME.get(fl, fl), c.x, c.y, 260))
    for s, x, y, h in labels_:
        e = p.text(s, x, y, h, "A-ANNO-TEXT", align="MIDDLE_CENTER")
    p.dim_h(0, W, 0, 1800)
    p.dim_v(0, D, 0, 1800)
    p.north(W + 2600, D - 1800, 900)
    p.scale_bar(0, D + 1600, 5)
    tb(p, "A-101P", "SITE PLAN - PRESENTATION", G.site_text(), None, -3600, -9000,
       val=val)
    path = os.path.join(OUT, "VILLA_A101P.dxf")
    save(p, path)
    return p, path


VILLA_TREES = ((5000, 26100, 1500), (9600, 26800, 1250), (4400, 5600, 1800),
               (19600, 6400, 1800), (19700, 2400, 1500), (2100, 12000, 1100),
               (21900, 12000, 1100), (2200, 8000, 1200), (2200, 3000, 1300),
               (21800, 9600, 1200))


def site_trees():
    """(x, y, crown radius): the design's SITE_TREES (x, y, crown diameter)
    when it has them, else the villa's."""
    if hasattr(V, "SITE_TREES"):
        return [(float(x), float(y), float(d) / 2.0) for x, y, d in V.SITE_TREES]
    return VILLA_TREES


def save(p, path):
    """Save the DXF, and its PNG beside it for a project design (or --png)."""
    import villa_cad as CAD
    return CAD.save(p, path)


def _inner_point(g):
    """A label point well inside the largest part of `g`."""
    from shapely.ops import polylabel
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda q: q.area)
    return polylabel(g, tolerance=20.0)


def site_labels(surf):
    """The presentation site plan's labels for a project design: POOL_LABEL
    with its size, level and depths on the pool; the garden and every deck by
    what it is (the one at the pool, the one under a shade) -- positions from
    the geometry, not typed."""
    import villa_cad as CAD
    cx = (V.POOL_X0 + V.POOL_X1) / 2
    flats = CAD.pool_flats()
    ys = sorted([V.POOL_Y0, V.POOL_Y1] + [y for a, b, _d in flats for y in (a, b)])
    gaps = [(b - a, (a + b) / 2) for a, b in zip(ys, ys[1:])]
    cy = max(gaps)[1] if gaps else (V.POOL_Y0 + V.POOL_Y1) / 2
    depths = [d for _a, _b, d in flats]
    out = [(V.POOL_LABEL, cx, cy + 600, 300),
           (f"TW +{V.POOL_TW:.0f}", cx, cy + 50, 200)]
    if depths:
        out.append((f"{min(depths):.0f} TO {max(depths):.0f} DEEP", cx, cy - 450, 180))
    if getattr(V, "POOL_LEDGE", None):
        lx0, ly0, lx1, ly1, lz = V.POOL_LEDGE
        out.append((f"SUN LEDGE {V.POOL_TW - lz:.0f}", (lx0 + lx1) / 2,
                    (ly0 + ly1) / 2, 160))
    lawn = surf.get("lawn")
    if lawn is not None and not lawn.is_empty:
        pt = _inner_point(lawn)
        out.append(("GARDEN", pt.x, pt.y, 300))
    shell = surf.get("poolzone")
    shades = [box(b[0], b[1], b[3], b[4]) for b in G.shade_boxes()]
    deck = surf.get("deck")
    for d in (getattr(deck, "geoms", [deck]) if deck is not None else []):
        if d.is_empty or d.area < 6e6:
            continue
        if shell is not None and d.distance(shell) < 50.0:
            name = "POOL DECK"
        elif any(d.intersection(s).area > 0.5 * d.area for s in shades):
            name = "COVERED TERRACE"
        else:
            name = "DECK"
        pt = _inner_point(d)
        out.append((name, pt.x, pt.y, 240))
    return out


def site_extras(p):
    """A project design's additions to the presentation site plan: the
    storeys and projections over the ground floor (dashed), free-standing
    stone, the SHADES (timber, see-through, dashed), the forecourt ramp."""
    import villa_cad as CAD
    if CAD.SHADE_LAYER not in p.doc.layers:
        p.doc.layers.add(CAD.SHADE_LAYER, color=8, lineweight=18, linetype="DASHED")
    up = CAD.upper_outline()
    if up is not None:
        for ring in [g.exterior for g in getattr(up, "geoms", [up]) if not g.is_empty]:
            e = PD.poly(p.msp, list(ring.coords), CAD.SHADE_LAYER)
            e.rgb = C["ink"]
            e.dxf.ltscale = 200.0
    for kind, (x0, y0, x1, y1) in G.stone_on(G.GROUND_FLOOR):
        if kind == "free":
            fill_rect(p, x0, y0, x1, y1, "A-WALL-FILL", "stonewall")
            outline(p, box(x0, y0, x1, y1), "A-WALL-EXTR")
    porch = box(V.PORCH_X0, V.PORCH_Y0, V.PORCH_X1, V.PORCH_Y1)
    for x0, y0, z0, x1, y1, z1 in G.shade_boxes():
        fill_rect(p, x0, y0, x1, y1, "L-SITE-DECK", "timber", alpha=0.6)
        e = PD.poly(p.msp, PD.rect_pts(x0, y0, x1, y1), CAD.SHADE_LAYER)
        e.rgb = C["ink"]
        e.dxf.ltscale = 200.0
        s = box(x0, y0, x1, y1)
        name = "CARPORT" if s.intersection(porch).area > 0.5 * s.area else "CANOPY"
        p.fit_text(name, (x0 + x1) / 2, y0 + 600, 200, "A-ANNO-TEXT",
                   max_w=x1 - x0 - 400, centre=True)
    rt = CAD.ramp_text()
    if rt:
        y0 = V.RAMP_Y0
        e = PD.poly(p.msp, [(G.BW, y0), (V.PLOT_W - G.BW, y0)], CAD.SHADE_LAYER,
                    close=False)
        e.rgb = C["ink"]
        e.dxf.ltscale = 200.0
        xr = max(V.PORCH_X1, V.PLOT_W * 0.62)
        ya = min(y0 + 1900, (y0 + V.RAMP_Y1) / 2)
        CAD._arrow(p, (xr, y0 + 250), (xr, ya), "A-ANNO-TEXT")
        p.fit_text(f"{rt} TO THE STREET", xr + 300, (y0 + ya) / 2, 200,
                   "A-ANNO-TEXT", max_w=V.PLOT_W - G.BW - xr - 600)


# ------------------------------------------------------------------ plans
SANITARY = {"wc", "basin", "bath", "shower", "shower_seat"}
KITCHEN = {"sink_unit", "hob", "dishwasher", "fridge"}
SOFT = {"bed_double", "bed_single", "sofa", "sofa_l"}


def plan(floor, no, name, val=None):
    """A presentation plan: `floor` and every floor drawn with it -- the
    annex on the ground-floor sheet (villa_geom.sheet_floors)."""
    import villa_cad as CAD
    p = setup(name)
    fls = [f for f in G.sheet_floors(floor) if V.rooms_on(f)] or [floor]

    for fl in fls:
        for r in V.rooms_on(fl):
            fill(p, V.net_poly(r), "A-FLOR-FILL", room_fill(r))
    bal = G.balcony_on(floor)       # a project's balcony, on its own floor
    if bal is not None:
        fill_rect(p, *bal, "A-FLOR-FILL", "paving")

    for vname, vx0, vy0, vx1, vy1, floors in V.VOIDS:
        if floor in floors:
            fill_rect(p, vx0, vy0, vx1, vy1, "A-ROOF-FILL", "roofline")

    for fl in fls:
        ext, part, _ = CAD.cut_fabric(fl)
        fill(p, ext, "A-WALL-FILL", "poche")
        fill(p, part, "A-WALL-FILL", "wall")
        CAD.draw_fabric(p, ext, "A-WALL-EXTR")
        CAD.draw_fabric(p, part, "A-WALL")
        CAD.opening_symbols(p, fl)
    if CAD.MULTI_STAIR:             # every stair, on the storeys it joins
        CAD.stairs(p, floor)
    elif floor in ("GF", "FF"):
        CAD.stair(p, floor)
    CAD.overhead(p, floor)
    if PROJECT_SHEETS:              # the glass guards, stone, the balcony named
        CAD.guards(p, floor)
        CAD.stone(p, floor)
        CAD.balcony_plan(p, floor)
        for vname, vx0, vy0, vx1, vy1, floors in V.VOIDS:
            if floor in floors:
                lx, ly, lw = CAD.void_label_at(floor, (vx0, vy0, vx1, vy1))
                p.fit_text(vname, lx, ly, 240, "A-ANNO-TEXT", max_w=lw - 400,
                           centre=True)

    for fl, (key, x, y, rot) in G.sheet_furniture(floor):
        fp = F.footprint(key, x, y, rot)
        if not fp:
            continue
        if key in SANITARY:
            # white porcelain, opaque, outlined on the fixtures layer: drawn
            # "tile" on the wet rooms' "tile" floor it could not be seen, and
            # every bathroom read as an empty blue room
            fill_rect(p, *fp, "A-FURN-FILL", "porcelain")
            PD.poly(p.msp, PD.rect_pts(*fp), "A-FLOR-FIXT")
            continue
        col = ("roofline" if key in KITCHEN else
               "deck" if key in SOFT else "furn")
        fill_rect(p, *fp, "A-FURN-FILL", col, alpha=0.35)

    for fl in fls:
        CAD.labels(p, fl)
    b = CAD.sheet_bounds([floor] if V.rooms_on(floor) else fls)
    reach = None
    if PROJECT_SHEETS:              # set out beyond a canopy or a cantilever
        B = CAD.drawn_bounds(floor, fls)
        reach = (B[0], B[1])
    CAD.dim_runs(p, floor, b, reach)
    for fl in fls:                  # overall dimensions of the annex
        if fl == floor:
            continue
        ax0, ay0, ax1, ay1 = V.outline(fl).bounds
        p.dim_h(ax0, ax1, ay1, -1200)
        p.dim_v(ay0, ay1, ax1, -1200)
    if not PROJECT_SHEETS:
        B = CAD.sheet_bounds(fls)
    p.north(B[2] + 2200, B[3] - 900, 620)
    p.scale_bar(B[0], B[3] + 1400, 5)
    nm = name.upper()
    if PROJECT_SHEETS:
        nm += f"   --   {CAD.level_text(floor)}"
    tb(p, no, nm, G.area_text(fls), None, B[0] - 3600, B[1] - 8200,
       val=val)
    path = os.path.join(OUT, f"VILLA_{no.replace('-', '')}.dxf")
    save(p, path)
    return p, path


def tb(p, no, nm, area, cover, x0, y0, w=18000.0, val=None):
    """Title block; every number computed (see villa_cad.titleblock). `area`
    is a labelled string (villa_geom.area_text / site_text) or a bare net m2."""
    L, h = "A-ANNO-TTLB", 2600.0
    c1, c2 = w * 0.56, w * 0.78
    if not isinstance(area, str):
        area = (f"NET FLOOR AREA {float(area):.1f} m2"
                + (f"   SITE COVER {cover:.1f}%" if cover else ""))
    PD.poly(p.msp, PD.rect_pts(x0, y0, x0 + w, y0 + h), L)
    p.line(x0, y0 + 1700, x0 + w, y0 + 1700, L)
    for c in (c1, c2):
        p.line(x0 + c, y0, x0 + c, y0 + 1700, L)
    p.fit_text(G.project_line(), x0 + 300, y0 + 2000, 380, L, c1 - 500)
    p.fit_text(nm, x0 + 300, y0 + 1250, 280, L, c1 - 500)
    p.fit_text("COLOURED PRESENTATION DRAWING.  DO NOT SCALE.", x0 + 300,
               y0 + 900, 150, L, c1 - 500)
    p.fit_text(area, x0 + 300, y0 + 560, 150, L, c1 - 500)
    p.fit_text(G.validation_text(val), x0 + 300, y0 + 220, 150, L, c1 - 500)
    p.text("SCALE", x0 + c1 + 250, y0 + 1180, 170, L)
    p.text("1:100 @ A1", x0 + c1 + 250, y0 + 820, 200, L)
    p.text("DATE", x0 + c1 + 250, y0 + 420, 170, L)
    p.text(G.design_date(), x0 + c1 + 250, y0 + 140, 170, L)
    p.text("DWG No.", x0 + c2 + 250, y0 + 1180, 170, L)
    p.text(no, x0 + c2 + 250, y0 + 700, 320, L)
    p.text("REV  A", x0 + c2 + 250, y0 + 260, 170, L)


SHEET_NAME = {"GF": "Ground floor - presentation", "FF": "First floor - presentation",
              "RF": "Roof pavilion - presentation"}


def plan_sheets():
    """(floor, sheet no + 'P', name) of every presentation plan, from
    villa_geom.plan_sheets() -- the line set's sheets with a P suffix; the
    design's PLAN_SHEETS titles, else the villa's own wording."""
    return [(fl, no + "P", f"{t} - presentation" if t else
             SHEET_NAME.get(fl, f"{G.FLOOR_NAME.get(fl, fl).title()} - presentation"))
            for fl, no, t in G.plan_sheets()]


if __name__ == "__main__":
    val = G.validation()
    made = []
    p, path = site(val=val)
    made.append(("A-101P", path, len(p.msp)))
    for fl, no, nm in plan_sheets():
        p, path = plan(fl, no, nm, val=val)
        made.append((no, path, len(p.msp)))
    for no, path, n in made:
        print(f"{no}  {n:>5} entities  ->  {os.path.basename(path)}")
    print(f"title blocks: {G.validation_text(val)}")
    print(f"output: {OUT}")
