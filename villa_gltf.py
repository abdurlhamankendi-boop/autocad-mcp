"""Export the villa as glTF for rendering - bypassing AutoCAD entirely.

AutoCAD's EXPORT command offers 3D DWF, SAT, BMP, DXX, EPS, IGES, STL, WMF and
DGN. There is no FBX, no OBJ, no glTF: FBXEXPORT was removed in AutoCAD 2019.
So the render track does not go through AutoCAD at all. It is built here, from
the same villa_design.py the drawings come from, and written straight to .glb -
which Twinmotion, D5, Blender and Unreal all read natively.

Two tracks, one source of truth:

    villa_design.py  ->  ezdxf   ->  .dxf  ->  AutoCAD  ->  drawing set
                     ->  build123d -> .glb  ->  Twinmotion -> render

Each material group is exported as its own file, because a renderer assigns
materials per object and a single welded mesh cannot be grass in one place and
water in another.

The design language it reads (villa_design.py, via villa_geom.py):
  * any floor: the stacked house is GF + FF (V.envelope()); every other floor
    with rooms -- the annex "AX", a roof pavilion "RF" -- is a single storey of
    its own at LEVEL/CEIL, with floor slab, walls, roof slab and parapet;
  * openings are cut at V.opening_z(); WIN and SLIDE get a glass pane and a
    bronze frame (a SLIDE also a meeting stile), external DOORs a leaf;
  * V.fins() and V.SHADES are the bronze 'fins' group;
  * V.pool_parts() includes y-z PROFILE parts (the sloping pool floor, built
    by part/yz_prism) and the pool-plant vault; V.grate() is the 'grate'
    group, V.guards() the glass 'guards' group, V.gates() cut the boundary
    wall, V.garden_platform() is the raised garden's terrain;
  * V.stair_parts() is the 'stair' group (the house stair, solid), and
    V.rail_parts() the bronze 'rails' group -- every handrail, a sloping bar
    built as a y-z or x-z profile (part/yz_prism/xz_prism), plus posts.

A design that declares its own massing (V.massing(), read through
villa_geom.building_parts()) is built from it instead of envelope(): each of
its groups (walls, slabs, roof, base, a 'stone' skin ...) is union(adds) -
union(cuts), openings already cut, a part being a box, a profile or a poly
part {'poly', 'z'} (part/prism). Its V.landscape_parts() (villa_geom.
site_parts()) replace the terrain slab and the surfaces. Colours come from
V.MATERIALS when the design has them. The villa has neither hook and is built
exactly as before.

main() refuses to export any group whose top-level Location is not the
identity (the one condition under which the export comes out displaced).

VILLA_OUT (environment) redirects the output folder: VILLA_OUT\\render.
"""

from __future__ import annotations

import os
import time

from build123d import (Color, Compound, Location, Mode, Part, Plane, Polyline,
                       Solid, Unit, Vector, export_gltf, export_step,
                       extrude, make_face)

import villa_colour as CC
import villa_design as V
import villa_geom as G

OUT = G.out_dir("render")

# The stacked house's levels, for the envelope() path. Read with getattr: a
# design that brings its own massing() need not name them.
GF, FF, RF = (getattr(V, k, None) for k in ("GF", "FF", "RF"))
SLAB, PARAPET = getattr(V, "SLAB", None), getattr(V, "PARAPET", None)
# Opening heights are villa_design's (V.opening_z); these names survive only
# for anything that imported them from here.
DOOR_H, SILL, HEAD = (getattr(V, k, None) for k in ("DOOR_HEAD", "WIN_SILL", "WIN_HEAD"))
BW, BH = G.BW, G.BH                      # boundary wall, from the design data
GARDEN_Z = getattr(V, "GARDEN_Z", 700.0)

# A base colour per group. Twinmotion will replace these with real materials,
# but they make the model readable the moment it opens.
COLOURS = {
    "walls":     (0.72, 0.70, 0.66),      # board-marked concrete
    "slabs":     (0.66, 0.64, 0.60),
    "roof":      (0.80, 0.78, 0.74),
    "fins":      (0.36, 0.26, 0.16),      # bronze-anodised aluminium
    "frames":    (0.36, 0.26, 0.16),
    "pool":      (0.88, 0.84, 0.76),      # travertine coping and shell
    "base":      (0.84, 0.80, 0.72),      # travertine-clad plinth
    "terrain":   (0.76, 0.70, 0.58),
    "lawn":      (0.42, 0.56, 0.29),
    "planting":  (0.31, 0.44, 0.22),
    "gravel":    (0.82, 0.78, 0.70),
    "paving":    (0.74, 0.73, 0.70),
    "deck":      (0.62, 0.46, 0.28),
    "drive":     (0.44, 0.44, 0.43),
    "water":     (0.11, 0.38, 0.45),
    "boundary":  (0.55, 0.52, 0.48),
    "glass":     (0.55, 0.72, 0.78),
    "guards":    (0.55, 0.72, 0.78),      # glass balustrades
    "grate":     (0.36, 0.26, 0.16),      # bronze grate over the basin
    "stair":     (0.84, 0.80, 0.72),      # travertine, on masonry
    "rails":     (0.36, 0.26, 0.16),      # bronze handrails
    "door":      (0.35, 0.26, 0.18),
    "stone":     (0.20, 0.20, 0.21),      # stacked stone cladding
}


def colour(name):
    """A group's base colour: the design's own (V.MATERIALS[group]['color'])
    when it declares one, else COLOURS, else a neutral grey."""
    m = (getattr(V, "MATERIALS", None) or {}).get(name) or {}
    c = m.get("color") if isinstance(m, dict) else None
    if c is not None:
        return tuple(float(v) for v in c[:3])
    return COLOURS.get(name, (0.8, 0.8, 0.8))


def prism(poly, z0, z1):
    """A shapely polygon (holes included) extruded between two levels.

    Built AT z0, never moved there. A 15-case test established what goes
    wrong: the export is wrong exactly when the TOP-LEVEL shape's .location is
    not the identity. The writer keeps the vertex POSITIONs in the Z-up model
    frame and puts the Z-up -> Y-up rotation on the root node; a top-level
    Location is not composed with that correctly, so a lone
    `Location((0, 0, z0)) * solid` came out z0 mm SOUTH instead of up (the
    pool deck, 700 mm). Geometry baked in place has an identity location, and
    main() refuses to export any group whose location is not the identity."""
    parts = []
    for g in getattr(poly, "geoms", [poly]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        face = make_face(Polyline(*[(x, y, z0) for x, y in g.exterior.coords]))
        for ring in g.interiors:
            hole = make_face(Polyline(*[(x, y, z0) for x, y in ring.coords]))
            face = face - hole
        parts.append(extrude(face, amount=z1 - z0))
    if not parts:
        return None
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out


def box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box, geometry baked in place (see prism for why)."""
    return Solid.make_box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                          Plane((min(x0, x1), min(y0, y1), min(z0, z1))))


def yz_prism(pts, x0, x1):
    """A polygon in the y-z plane extruded along x from x0 to x1, baked in
    place: the sloping pool floor (villa_design.yz_prism / pool_parts), a
    handrail on a flight running north-south (rail_parts)."""
    face = make_face(Polyline(*[(x0, y, z) for y, z in pts], close=True))
    return extrude(face, amount=x1 - x0, dir=(1, 0, 0))


def xz_prism(pts, y0, y1):
    """yz_prism's twin: a polygon in the x-z plane extruded along y from y0
    to y1, baked in place -- a handrail on a flight running east-west."""
    face = make_face(Polyline(*[(x, y0, z) for x, z in pts], close=True))
    return extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def part(p):
    """A villa_design part: a box (x0, y0, z0, x1, y1, z1), a y-z profile
    ({'yz': [...], 'x': (x0, x1)}), an x-z one ({'xz': [...], 'y': (y0,
    y1)}) or a poly part ({'poly': shapely geometry, 'z': (z0, z1)}, built
    by prism -- None for an empty footprint), as a solid."""
    pp = G.poly_parts(p)
    if pp is not None:
        return prism(*pp)
    if G.is_profile(p):
        if "xz" in p:
            return xz_prism(p["xz"], *p["y"])
        return yz_prism(p["yz"], *p["x"])
    return box(*p)


def placed(shape):
    """True if the shape's own top-level Location is not the identity -- the
    one condition under which the glTF export comes out displaced."""
    loc = getattr(shape, "location", None)
    return loc is not None and not loc.wrapped.IsIdentity()


def _plus(a, b):
    """a + b where either may be None (an empty footprint makes no prism)."""
    if b is None:
        return a
    return b if a is None else a + b


def _minus(a, b):
    return a if (a is None or b is None) else a - b


def massed(mass):
    """The design's own building groups (villa_geom.building_parts(): {group:
    [(op, part)]}, adds then cuts, openings already cut), each built as
    union(adds) - union(cuts) -- in the design's order, nothing else cut."""
    out = {}
    for grp, ops in mass.items():
        s = None
        for op, p in ops:
            s = _plus(s, part(p)) if op == "add" else _minus(s, part(p))
        out[grp] = s
    return out


def building():
    """The building as material groups, stacked exactly as villa_3d_build.py
    stacks them: the design's own massing when it has one (massed), else
    from villa_design.envelope() (stacked). The shading, pool, frames,
    grate, guards, stair and rails are the same groups either way."""
    mass = G.building_parts()
    groups = massed(mass) if mass is not None else stacked()
    groups.update(fittings())
    return groups


def stacked():
    """The villa's walls, slabs, base and roof, stacked from the same
    villa_design.envelope() villa_3d_build.py stacks them from, every opening
    cut through the walls.

    It used to be one welded mass: a renderer cannot put board-marked concrete
    on the walls and bronze on the fins of a single mesh. And it subtracted
    every ground-floor room from GF all the way to FF, which removed the
    first-floor slab over all seven of them -- see envelope().

    Floors outside the stacked house (the annex "AX", a roof pavilion "RF")
    are single storeys of their own, from villa_geom.storey(): same groups,
    same stacking, at their own LEVEL and CEIL."""
    E = V.envelope()

    walls = prism(E["out_gf"], GF, FF - SLAB) + prism(E["upper"], FF, RF)
    for floor, z0, z1 in (("GF", GF, FF), ("FF", FF, RF)):
        for r in V.ROOMS:
            if r[6] == floor:
                walls = walls - prism(V.net_poly(r), z0, z1)
    # an empty dh_in (no double height outside the first floor) cuts nothing
    walls = _minus(walls, prism(E["dh_in"], FF, RF))

    slabs = prism(E["out_gf"], GF - SLAB, GF) + prism(E["ff_slab"], FF - SLAB, FF)
    # stone base under the raised ground floor; the house used to hover 400 mm
    base = prism(E["out_gf"], 0.0, GF - SLAB)
    for b in V.external_steps():    # landings and flights at every external
        base = base + box(*b)       # door and slide, the annex's included

    roof = _plus(prism(E["upper"], RF, RF + SLAB),
                 prism(G.roof_parapet(E), RF + SLAB, RF + SLAB + PARAPET))
    if E["parapet_single"].area > 1.0:
        roof = roof + prism(E["parapet_single"], FF, FF + PARAPET)

    # the annex and any roof pavilion: a storey of their own
    for fl in G.standalone_floors():
        S = G.storey(fl)
        w = prism(S["out"], S["z0"], S["z1"])
        for r in V.rooms_on(fl):
            w = _minus(w, prism(V.net_poly(r), S["z0"], S["z1"]))
        walls = _plus(walls, w)
        if S["slab_poly"] is not None:
            slabs = _plus(slabs, prism(S["slab_poly"], *S["slab"]))
        if S["base"] is not None:
            base = _plus(base, prism(S["out"], *S["base"]))
        roof = _plus(roof, prism(S["out"], *S["roof"]))
        roof = _plus(roof, prism(S["edge"], *S["parapet"]))

    # every opening, on every floor, cut through its wall at V.opening_z()
    for o in V.OPENINGS:
        walls = walls - box(*G.cut_box(o))
    return {"walls": walls, "slabs": slabs, "base": base, "roof": roof}


def fittings():
    """The groups every design is built with the same way, massing or not:
    shading, pool, window frames, grate, guards, stair and rails."""
    # Shading, bronze-anodised aluminium per the materials spec: the fin
    # arrays (V.FIN_ARRAYS -> V.fins()) and the horizontal projections
    # (V.SHADES). Data, not a loop here -- it used to be `range(9)`.
    fins = None
    for b in G.solar_boxes():
        fins = _plus(fins, box(*b))

    # the pool shell, its sloping floor (a y-z profile part), the weir, the
    # balance basin and the plant vault beside it -- villa_design.pool_parts
    shell, cuts, _ = V.pool_parts()
    pool = None
    for b in shell:
        pool = part(b) if pool is None else pool + part(b)
    for b in cuts:
        pool = _minus(pool, part(b))
    # the walkable grate over the basin (it is part of the pool deck) and the
    # glass guards (landings, garden edges, stair well): their own groups
    grate = None
    for b in G.grate_boxes():
        grate = _plus(grate, box(*b))
    guards = None
    for b in G.guard_boxes():
        guards = _plus(guards, box(*b))
    # the house stair, solid on masonry (villa_design.stair_parts) -- the
    # render model had none, and its glass would have stood in thin air --
    # and every handrail, the stair's and the outside steps' (rail_parts:
    # sloping bars as profiles, posts as boxes)
    stair = None
    for b in G.stair_boxes():
        stair = _plus(stair, box(*b))
    rails = None
    for p in G.rail_parts():
        rails = _plus(rails, part(p))

    # Window frames: the 60 mm the glass is held back from the reveal, filled
    # with a bronze section 80 deep. Without them a window is a hole with a
    # sheet of glass floating in it, and it reads as a render placeholder. A
    # sliding door is framed the same way, plus its meeting stile.
    frames = None
    for o in V.OPENINGS:
        fr = G.frame(o)
        if fr is None:
            continue
        outer, hole, stiles = fr
        f = box(*outer) - box(*hole)
        for s in stiles:
            f = f + box(*s)
        frames = _plus(frames, f)

    return {"fins": fins, "pool": pool, "frames": frames, "grate": grate,
            "guards": guards, "stair": stair, "rails": rails}


FABRIC = ("walls", "slabs", "base", "roof", "fins", "pool", "grate", "guards",
          "stair", "rails", "boundary")
NOT_FABRIC = ("frames", "glass", "door", "water", "terrain", "lawn", "planting",
              "gravel", "paving", "deck", "drive")


def verify(groups):
    """Answer villa_geom.probes() -- villa_design.probes() plus the annex,
    sliding-door and shading probes -- against this model, as
    villa_3d_verify.py does against AutoCAD's. The glTF track shipped with no
    first-floor slab over seven rooms because nothing ever asked it."""
    # every A-*-3D layer villa_3d_verify.py probes, the boundary included
    # (A-GRAT-3D is the grate, A-GRDS-3D the guards, A-STRS-3D the stair,
    # A-RAIL-3D the handrails) -- and every other building group a design's
    # massing brings (its 'stone' skin: A-STON-3D). Not fabric: the frames
    # (AutoCAD builds none), the infill, the water and the landscape.
    keys = list(FABRIC) + [k for k in groups if k not in FABRIC and k not in NOT_FABRIC]
    fabric = [groups[k] for k in keys if groups.get(k) is not None]
    bad = []
    probes = G.probes()
    for name, x, y, z, expect, _r in probes:
        solid = any(s.is_inside(Vector(x, y, z)) for s in fabric)
        if solid != (expect == "solid"):
            bad.append(f"{name}: expected {expect}, got {'solid' if solid else 'void'}")
    ctl = G.controls()
    for name, x, y, z, _r in ctl:
        if not any(s.is_inside(Vector(x, y, z)) for s in fabric):
            bad.append(f"control {name}: expected solid, got void")
    print(f"  probes  {len(probes) + len(ctl) - len(bad)}/{len(probes) + len(ctl)}"
          f" as designed")
    for b in bad:
        print(f"     FAIL  {b}")
    return not bad


def boundary():
    """The boundary wall, with every gate of V.gates() cut through it (the
    pedestrian gate was a typed 15400-16600 here and in four other builders)."""
    w = None
    for x0, y0, x1, y1 in ((0, 0, V.PLOT_W, BW),
                           (0, V.PLOT_D - BW, V.PLOT_W, V.PLOT_D),
                           (0, 0, BW, V.PLOT_D),
                           (V.PLOT_W - BW, 0, V.PLOT_W, V.PLOT_D)):
        b = box(x0, y0, 0, x1, y1, BH)
        w = b if w is None else w + b
    for c in G.gate_cuts(BH):
        w = w - box(*c)
    return w


def landscape():
    """The site groups: the design's own landscape_parts() when it has them
    (villa_geom.site_parts(): terrain, paving, deck, lawn, planting, gravel,
    drive -- each group the union of its parts), else villa_colour's
    surfaces on the villa's terrain slab and raised garden (surfaces());
    then the glass and door leaves in the openings, and the water."""
    site = G.site_parts()
    if site is not None:
        groups = {}
        for grp, parts in site.items():
            s = None
            for p in parts:
                s = _plus(s, part(p))
            if s is not None:
                groups[grp] = s
    else:
        groups = surfaces()

    # Glazing: the openings are real holes, but a hole has no surface for a
    # renderer to put glass on -- and in a shaded view it reads as nothing.
    # Windows and sliding doors get a pane, external doors a leaf
    # (villa_geom.infill).
    glass, leaves = None, None
    for o in V.OPENINGS:
        fill = G.infill(o)
        if fill is None:
            continue
        into, b = fill[0], box(*fill[1])
        if into == "glass":
            glass = b if glass is None else glass + b
        else:
            leaves = b if leaves is None else leaves + b
    if glass is not None:
        groups["glass"] = glass
    if leaves is not None:
        groups["door"] = leaves

    # the rill (a design with RILL_W), then the pool on its floor profile, a
    # basin, the sheet over a weir -- villa_geom.water_parts
    water = None
    for b in G.water_parts():
        water = _plus(water, part(b))
    if water is not None:
        groups["water"] = water
    return groups


def surfaces():
    """The villa's site: villa_colour's ground surfaces laid on the terrain
    slab and the raised garden (V.garden_platform(), or the band south of
    the wings for older data), the pool zone and the annex cut out of it."""
    surf = CC.ground_surfaces()
    THICK = {"lawn": 30.0, "beds": 45.0, "mulch": 25.0, "terrace": 40.0,
             "path": 40.0, "poolsurround": 40.0, "deck": 80.0, "drive": 40.0}
    GROUP = {"lawn": "lawn", "beds": "planting", "mulch": "gravel",
             "terrace": "paving", "path": "paving", "poolsurround": "paving",
             "deck": "deck", "drive": "drive"}
    from shapely.geometry import box as _gb
    # the raised garden (light slots included), villa_design.garden_platform
    garden = (V.garden_platform() if hasattr(V, "garden_platform")
              else _gb(0, 0, V.PLOT_W, V.WG_Y0))
    groups = {}
    for key, geom in surf.items():
        if key in ("house", "poolzone") or key not in THICK:
            continue
        # Split at the garden edge: one level per surface, from one sample
        # point, buried the south planting beds in the garden platform and
        # floated the lawn beside the house 700 mm over the forecourt.
        for piece, z in ((geom.intersection(garden), GARDEN_Z),
                         (geom.difference(garden), 0.0)):
            if piece.is_empty or piece.area < 1.0:
                continue
            solid = prism(piece, z, z + THICK[key])
            if solid is None:
                continue
            g = GROUP[key]
            groups[g] = solid if g not in groups else groups[g] + solid

    # cut the pool out of the ground, or the water is buried in it -- and the
    # annex out of it, or its rooms fill with garden
    from shapely.geometry import box as _sb
    zone = surf["poolzone"]
    annex = G.annex_footprint()
    # either prism may be empty (no raised garden): _plus, not +
    terrain = _plus(prism(_sb(0, 0, V.PLOT_W, V.PLOT_D).difference(zone)
                          .difference(annex), -300, 0),
                    prism(garden.difference(zone).difference(annex), 0, GARDEN_Z))
    groups["terrain"] = terrain
    return groups


def main():
    t0 = time.perf_counter()
    groups = building()
    groups["boundary"] = boundary()
    print(f"  building + boundary   {time.perf_counter() - t0:.0f}s")
    if not verify(groups):
        raise SystemExit("model does not match the design -- not exporting it")
    groups.update(landscape())
    print(f"  landscape             {time.perf_counter() - t0:.0f}s")
    # PRE-EXPORT GUARD. The glTF export is displaced exactly when a group's
    # top-level shape.location is not the identity (see prism). Every group
    # is built in place; one that is not would render in the wrong place
    # without any error, so refuse to write any of it.
    moved = [name for name, shape in groups.items()
             if shape is not None and placed(shape)]
    if moved:
        raise SystemExit("refusing to export: these groups carry a non-identity "
                         f"top-level Location and would export displaced: {moved} "
                         "-- build them in place (villa_gltf.prism/box/part)")
    # the old single-mesh export; remove it so nothing imports a stale building
    stale = os.path.join(OUT, "villa_building.glb")
    if os.path.exists(stale):
        os.remove(stale)

    total = 0
    parts = []
    for name, shape in groups.items():
        if shape is None:
            continue
        r, g, b = colour(name)
        shape.color = Color(r, g, b)
        shape.label = name
        parts.append(shape)
        path = os.path.join(OUT, f"villa_{name}.glb")
        # linear_deflection defaults to 0.001, which on a 24 m building is an
        # absurd tessellation. 2 mm is invisible at render scale.
        export_gltf(shape, path, binary=True, unit=Unit.MM,
                    linear_deflection=2.0, angular_deflection=0.15)
        kb = os.path.getsize(path) // 1024
        total += kb
        print(f"  {name:10s} {shape.volume / 1e9:8.1f} m3   {kb:>6} KB")

    # Expected bounds per group, in mm, for the importer to check itself
    # against (villa_blender.py refuses to render a group that moved).
    manifest = {}
    for p in parts:
        bb = p.bounding_box()
        manifest[p.label] = [bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z]
    import json
    with open(os.path.join(OUT, "groups.json"), "w") as f:
        json.dump(manifest, f, indent=1)

    whole = Compound(children=parts)
    if placed(whole):
        raise SystemExit("refusing to export villa.glb: the compound carries a "
                         "non-identity top-level Location")
    whole_path = os.path.join(OUT, "villa.glb")
    export_gltf(whole, whole_path, binary=True, unit=Unit.MM,
                linear_deflection=2.0, angular_deflection=0.15)
    step_path = os.path.join(OUT, "villa.step")
    export_step(whole, step_path)

    bb = whole.bounding_box()
    print(f"\n  villa.glb  {os.path.getsize(whole_path) // 1024} KB"
          f"   villa.step {os.path.getsize(step_path) // 1024} KB")
    print(f"  bbox  {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    print(f"  {len(parts)} material groups, {total} KB of parts"
          f"   {time.perf_counter() - t0:.0f}s")
    print(f"\n  -> {OUT}")


if __name__ == "__main__":
    main()
