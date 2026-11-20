"""Build the villa as native AutoCAD 3D solids, from the same room data.

The old model was authored procedurally with its own magic numbers, so it drifted
from the plans. Here the mass is the derived envelope and the rooms are cut out
of it -- exactly the polygons the plans are drawn from -- so the model and the
drawings cannot disagree.

Documents are tracked BY NAME; SaveAs rebinds rather than copies.

It mirrors villa_gltf.building() group for group, through the same
villa_geom helpers: the annex / roof pavilion as storeys of their own
(G.storey), every opening cut at V.opening_z (G.cut_box), windows and sliding
doors glazed and external doors given a leaf (G.infill), and the fins and
V.SHADES on A-SHDE-3D (G.solar_boxes). The pool's sloping floor is a y-z
profile part (part3 / yz_prism3), the basin grate is A-GRAT-3D, the glass
guards A-GRDS-3D, the house stair (V.stair_parts, solid) A-STRS-3D, the
handrails (V.rail_parts: y-z / x-z profiles and posts) A-RAIL-3D, the gates
are cut from V.gates() (G.gate_cuts) and the raised garden is
V.garden_platform(). VILLA_OUT redirects the output folder.

A design with its own massing (V.massing()) and landscape (V.landscape_parts())
is built from them through the SAME helpers villa_gltf reads --
G.building_parts() (each group union(adds) - union(cuts), openings already
cut, on its own layer: walls A-WALL-3D, slabs A-SLAB-3D, roof A-ROOF-3D, the
basement A-BASE-3D, a stone skin A-STON-3D -- G.layer_3d) and G.site_parts()
(the L-* layers, G.site_layer) -- so the two models cannot disagree. The
water is G.water_parts(): the rill only when the design has one (RILL_W).
"""

import math
import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_colour as CC
import villa_design as V
import villa_geom as G

OUT = G.out_dir()
DWG = os.path.join(OUT, "VILLA_3D_MODEL.dwg")

# The stacked house's levels, for the envelope() path. Read with getattr: a
# design that brings its own massing() need not name them.
GF, FF, RF = (getattr(V, k, None) for k in ("GF", "FF", "RF"))
SLAB, PARAPET = getattr(V, "SLAB", None), getattr(V, "PARAPET", None)
BW, BH = G.BW, G.BH                      # boundary wall, from the design data

# One layer per material group (key -> layer, ACI). The massing path adds its
# groups' own through G.layer_3d (the stone skin: A-STON-3D, ACI 250 dark
# grey) -- only when the design has them, so the villa's DWG gains no layer.
BUILD_LAYER = {"WALL": ("A-WALL-3D", 32), "SLAB": ("A-SLAB-3D", 8),
               "ROOF": ("A-ROOF-3D", 253), "SHADE": ("A-SHDE-3D", 42),
               "POOL": ("A-POOL-3D", 254), "BDRY": ("A-BDRY-3D", 43),
               "BASE": ("A-BASE-3D", 44), "GRAT": ("A-GRAT-3D", 42),
               "GRDS": ("A-GRDS-3D", 151), "STAIR": ("A-STRS-3D", 44),
               "RAIL": ("A-RAIL-3D", 42)}
# villa_gltf's group name -> this file's group key, for the massing groups
MASS_KEY = {"walls": "WALL", "slabs": "SLAB", "roof": "ROOF", "base": "BASE",
            "stone": "STON"}


def mass_key(group):
    """GRP key of a massing group ('stone' -> 'STON'; an unknown group by
    its name, as G.layer_3d names its layer)."""
    return MASS_KEY.get(group) or group.upper()[:4]


pythoncom.CoInitialize()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def dbl(v):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x) for x in v])


def objs(items):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(items))


def busy(exc):
    t = str(exc).lower()
    # A busy AutoCAD can also refuse a late-bound NAME lookup -- pywin32 then
    # raises AttributeError("<unknown>.Add") -- a rejected call, not a missing
    # attribute (villa_load.busy learned this first; seen here 2026-09-26).
    return ("rejected" in t or "-2147418111" in t or "busy" in t
            or (isinstance(exc, AttributeError)
                and ("autocad.application" in t or t.startswith("<unknown>."))))


def get_doc(a, name):
    # by name AND folder: projects share drawing names (villa_geom.find_doc)
    return G.find_doc(a, name, OUT)


def region_from_ring(ms, coords):
    flat = []
    for x, y in coords:
        flat += [float(x), float(y)]
    pl = ms.AddLightWeightPolyline(dbl(flat))
    pl.Closed = True
    return ms.AddRegion(objs([pl]))[0]


def prism(ms, poly, z0, z1):
    """Extrude a shapely polygon (holes included) between two levels. None
    for an empty footprint, as villa_gltf.prism."""
    solids = []
    for g in getattr(poly, "geoms", [poly]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        s = ms.AddExtrudedSolid(region_from_ring(ms, g.exterior.coords),
                                z1 - z0, 0.0)
        s.Move(pt(0, 0, 0), pt(0, 0, z0))
        for ring in g.interiors:
            h = ms.AddExtrudedSolid(region_from_ring(ms, ring.coords),
                                    z1 - z0, 0.0)
            h.Move(pt(0, 0, 0), pt(0, 0, z0))
            s.Boolean(2, h)
        solids.append(s)
    if not solids:
        return None
    base = solids[0]
    for s in solids[1:]:
        base.Boolean(0, s)
    return base


def box3(ms, x0, y0, z0, x1, y1, z1):
    return ms.AddBox(pt((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                     abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def yz_prism3(ms, pts, x0, x1):
    """A polygon in the y-z plane extruded along x from x0 to x1 -- the
    sloping pool floor, as villa_gltf.yz_prism builds it.

    The profile is drawn as a lightweight polyline whose OCS normal is +X:
    by the arbitrary-axis rule its OCS x runs along world Y and its OCS y
    along world Z, and its Elevation is the plane x = x0. The region extrudes
    along that normal. The result is checked against the profile's extents
    and REFUSED if it landed anywhere else (this path has not been run
    against AutoCAD yet -- a wrong orientation must fail loudly, not build a
    pool in the wrong place)."""
    flat = []
    for y, z in pts:
        flat += [float(y), float(z)]
    pl = ms.AddLightWeightPolyline(dbl(flat))
    pl.Closed = True
    pl.Normal = pt(1.0, 0.0, 0.0)
    pl.Elevation = float(x0)
    reg = ms.AddRegion(objs([pl]))[0]
    s = ms.AddExtrudedSolid(reg, float(x1 - x0), 0.0)
    lo, hi = s.GetBoundingBox()
    ys, zs = [p[0] for p in pts], [p[1] for p in pts]
    want_lo, want_hi = (x0, min(ys), min(zs)), (x1, max(ys), max(zs))
    if any(abs(a - b) > 1.0 for a, b in zip(list(lo) + list(hi),
                                           list(want_lo) + list(want_hi))):
        raise RuntimeError(f"yz profile landed at {tuple(lo)}..{tuple(hi)}, "
                           f"expected {want_lo}..{want_hi}")
    return s


def xz_prism3(ms, pts, y0, y1):
    """A polygon in the x-z plane extruded along y from y0 to y1 -- a
    handrail on a flight running east-west, as villa_gltf.xz_prism builds it.

    OCS normal +Y: by the arbitrary-axis rule (|Nx| and |Ny| not both under
    1/64) OCS x = Wz x N = -X world and OCS y = N x OCS x = +Z, so an (x, z)
    point is drawn at OCS (-x, z), Elevation y0. Checked against the
    profile's extents and REFUSED if it lands anywhere else, like
    yz_prism3 (not yet run against AutoCAD)."""
    flat = []
    for x, z in pts:
        flat += [-float(x), float(z)]
    pl = ms.AddLightWeightPolyline(dbl(flat))
    pl.Closed = True
    pl.Normal = pt(0.0, 1.0, 0.0)
    pl.Elevation = float(y0)
    reg = ms.AddRegion(objs([pl]))[0]
    s = ms.AddExtrudedSolid(reg, float(y1 - y0), 0.0)
    lo, hi = s.GetBoundingBox()
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    want_lo, want_hi = (min(xs), y0, min(zs)), (max(xs), y1, max(zs))
    if any(abs(a - b) > 1.0 for a, b in zip(list(lo) + list(hi),
                                           list(want_lo) + list(want_hi))):
        raise RuntimeError(f"xz profile landed at {tuple(lo)}..{tuple(hi)}, "
                           f"expected {want_lo}..{want_hi}")
    return s


def part3(ms, p):
    """A villa_design part -- a box, a y-z / x-z profile (G.is_profile) or a
    poly part {'poly', 'z'} (G.poly_parts; None for an empty footprint, as
    prism) -- as an AutoCAD solid; villa_gltf.part is the same thing in
    build123d."""
    pp = G.poly_parts(p)
    if pp is not None:
        return prism(ms, *pp)
    if G.is_profile(p):
        if "xz" in p:
            return xz_prism3(ms, p["xz"], *p["y"])
        return yz_prism3(ms, p["yz"], *p["x"])
    return box3(ms, *p)


def run():
    a = w.GetActiveObject("AutoCAD.Application")
    old = get_doc(a, os.path.basename(DWG))
    if old is not None:
        old.Close(False)

    a = w.GetActiveObject("AutoCAD.Application")
    a.Documents.Add()
    doc = a.ActiveDocument
    created = str(doc.Name)
    doc.SetVariable("INSUNITS", 4)
    ms = doc.ModelSpace
    t0 = time.perf_counter()

    # The building used to be ONE solid on layer 0 -- which is exactly why it
    # read as a single lump. Build it as separate material groups instead, each
    # on its own coloured layer, stacked so nothing overlaps: walls stop at the
    # underside of the slab above rather than running through it.
    GRP = {}
    layers = dict(BUILD_LAYER)

    def add(key, solid):
        if solid is None:
            return
        GRP[key] = solid if key not in GRP else _u(GRP[key], solid)

    def _u(a, b):
        a.Boolean(0, b)
        return a

    def cut(key, solid):
        """Subtract a solid from one group; nothing to cut, or no group to
        cut it from (a design without a pool), is not an error."""
        if solid is None:
            return
        if key in GRP:
            GRP[key].Boolean(2, solid)
        else:
            solid.Delete()

    mass = G.building_parts()
    rooms_gf, rooms_ff, rooms_x, dh_void = [], [], [], None
    if mass is not None:
        # The design's own massing -- exactly the (op, part) lists
        # villa_gltf.massed() builds: each group union(adds) - union(cuts),
        # the openings, rooms, voids and stone skin already cut by the design,
        # nothing else cut from these groups below. One layer per group.
        for grp, ops in mass.items():
            key = mass_key(grp)
            layers.setdefault(key, G.layer_3d(grp))
            for op, p in ops:
                if op == "add":
                    add(key, part3(ms, p))
                else:
                    cut(key, part3(ms, p))
    else:
        # Footprints come from villa_design.envelope() -- deriving them here is
        # how the double-height living got capped at FF and the street front
        # got a 500 mm open band. See envelope() for the full account.
        E = V.envelope()

        rooms_gf = [prism(ms, V.net_poly(r), GF, FF)
                    for r in V.ROOMS if r[6] == "GF"]
        rooms_ff = [prism(ms, V.net_poly(r), FF, RF)
                    for r in V.ROOMS if r[6] == "FF"]

        # None when there is no double height outside the first floor
        dh_void = prism(ms, E["dh_in"], FF, RF)

        add("WALL", prism(ms, E["out_gf"], GF, FF - SLAB))
        add("WALL", prism(ms, E["upper"], FF, RF))

        add("SLAB", prism(ms, E["out_gf"], GF - SLAB, GF))
        add("SLAB", prism(ms, E["ff_slab"], FF - SLAB, FF))
        # The ground floor is raised half a level; without a base under the
        # slab the house hovered 400 mm over the forecourt.
        add("BASE", prism(ms, E["out_gf"], 0.0, GF - SLAB))
        for b in V.external_steps():    # landings and flights at the external doors
            add("BASE", box3(ms, *b))

        add("ROOF", prism(ms, E["upper"], RF, RF + SLAB))
        add("ROOF", prism(ms, G.roof_parapet(E), RF + SLAB, RF + SLAB + PARAPET))
        if E["parapet_single"].area > 1.0:
            add("ROOF", prism(ms, E["parapet_single"], FF, FF + PARAPET))

        # The annex (floor AX) and any roof pavilion (RF): single storeys of
        # their own, stacked like the house -- exactly as villa_gltf.stacked().
        for fl in G.standalone_floors():
            S = G.storey(fl)
            add("WALL", prism(ms, S["out"], S["z0"], S["z1"]))
            rooms_x += [prism(ms, V.net_poly(r), S["z0"], S["z1"])
                        for r in V.rooms_on(fl)]
            if S["slab_poly"] is not None:
                add("SLAB", prism(ms, S["slab_poly"], *S["slab"]))
            if S["base"] is not None:
                add("BASE", prism(ms, S["out"], *S["base"]))
            add("ROOF", prism(ms, S["out"], *S["roof"]))
            add("ROOF", prism(ms, S["edge"], *S["parapet"]))

    # Shading on A-SHDE-3D: the fin arrays (V.FIN_ARRAYS -> V.fins()) and the
    # horizontal projections (V.SHADES). Data -- it used to be `range(9)`.
    for b in G.solar_boxes():
        add("SHADE", box3(ms, *b))

    # pool shell, sloping floor (profile part), weir, basin, plant vault
    pool_shell, pool_cuts, pool_water = V.pool_parts()
    for b in pool_shell:
        add("POOL", part3(ms, b))
    # the grate over the basin and the glass guards -- villa_gltf's 'grate'
    # and 'guards' groups
    for b in G.grate_boxes():
        add("GRAT", box3(ms, *b))
    for b in G.guard_boxes():
        add("GRDS", box3(ms, *b))
    # the house stair, solid on masonry, and every handrail -- villa_gltf's
    # 'stair' and 'rails' groups (the rails are sloping profiles, part3)
    for b in G.stair_boxes():
        add("STAIR", box3(ms, *b))
    for p in G.rail_parts():
        add("RAIL", part3(ms, p))

    for x0, y0, x1, y1 in ((0, 0, V.PLOT_W, BW),
                           (0, V.PLOT_D - BW, V.PLOT_W, V.PLOT_D),
                           (0, 0, BW, V.PLOT_D),
                           (V.PLOT_W - BW, 0, V.PLOT_W, V.PLOT_D)):
        add("BDRY", box3(ms, x0, y0, 0, x1, y1, BH))

    # cuts, applied only to the group they belong to (the massing path's are
    # the design's own, applied above)
    if mass is None:
        for r in rooms_gf + rooms_ff + rooms_x:
            cut("WALL", r)
        cut("WALL", dh_void)
        # every opening, on every floor, cut through its wall at
        # V.opening_z(): a window from sill to head, a door or a SLIDE from
        # the floor to its head
        for o in V.OPENINGS:
            cut("WALL", box3(ms, *G.cut_box(o)))
    for b in pool_cuts:
        cut("POOL", part3(ms, b))
    # every gate in V.gates(), cut through the street wall (the pedestrian
    # gate used to be a typed 15400-16600)
    for c in G.gate_cuts(BH):
        cut("BDRY", box3(ms, *c))

    for key, (lname, aci) in layers.items():
        try:
            lay = doc.Layers.Item(lname)
        except Exception:
            lay = doc.Layers.Add(lname)
        lay.color = aci
        if key in GRP:
            GRP[key].Layer = lname
    print(f"  building: {len(GRP)} material groups   "
          f"{time.perf_counter() - t0:.0f}s")

    # ---- landscape ---------------------------------------------------------
    # Kept as SEPARATE solids on their own layers, not unioned into the
    # building: a renderer assigns materials per object, and a single welded
    # lump cannot be given grass in one place and water in another.
    GARDEN_Z = getattr(V, "GARDEN_Z", 700.0)   # pool garden at top-water level
    LAYERS = {"L-TERRAIN": (43, -300.0, 0.0),
              "L-LAWN":    (84, 0.0, 30.0),
              "L-PLANT":  (104, 0.0, 45.0),
              "L-GRAVEL":  (42, 0.0, 25.0),
              "L-PAVE":   (253, 0.0, 40.0),
              "L-DECK":    (34, 0.0, 80.0),
              "L-DRIVE":  (251, 0.0, 40.0),
              "L-WATER":  (140, 0.0, 0.0)}
    for name, (aci, _z0, _z1) in LAYERS.items():
        try:
            lay = doc.Layers.Item(name)
        except Exception:
            lay = doc.Layers.Add(name)
        lay.color = aci

    land = []

    def on(layer, solid):
        """Put a solid on its layer and count it; an empty footprint (None)
        makes no solid and is skipped."""
        if solid is None:
            return None
        solid.Layer = layer
        land.append(solid)
        return solid

    site = G.site_parts()
    if site is not None:
        # The design's own landscape (villa_geom.site_parts, the parts
        # villa_gltf.landscape unions per group): terrain, the forecourt ramp
        # as y-z wedges, surfaces and hedges -- one solid per part, on the
        # group's L-* layer (G.site_layer).
        for grp, parts in site.items():
            layer = G.site_layer(grp)
            try:
                doc.Layers.Item(layer)
            except Exception:
                doc.Layers.Add(layer).color = 7
            for p in parts:
                on(layer, part3(ms, p))
    else:
        surf = CC.ground_surfaces()
        SURF_LAYER = {"lawn": "L-LAWN", "beds": "L-PLANT", "mulch": "L-GRAVEL",
                      "terrace": "L-PAVE", "path": "L-PAVE",
                      "poolsurround": "L-PAVE", "deck": "L-DECK",
                      "drive": "L-DRIVE"}
        # The ground must have a HOLE where the pool is. Built as solid boxes,
        # the raised garden platform filled the pool to the brim and the
        # coping slab lidded it -- 1400 mm of water with 0 mm of it visible.
        # The annex stands in the ground too: cut it out, or its rooms fill
        # with garden (as villa_gltf.surfaces).
        from shapely.geometry import box as _sb
        zone = surf["poolzone"]
        annex = G.annex_footprint()
        on("L-TERRAIN", prism(
            ms, _sb(0, 0, V.PLOT_W, V.PLOT_D).difference(zone).difference(annex),
            -300, 0))
        # the raised garden, light slots included (villa_design.garden_platform)
        platform = (V.garden_platform() if hasattr(V, "garden_platform")
                    else _sb(BW, BW, V.PLOT_W - BW, V.WG_Y0))
        on("L-TERRAIN", prism(
            ms, platform.difference(zone).difference(annex), 0, GARDEN_Z))
        skipped = []
        for key, geom in surf.items():
            if key in ("house", "poolzone"):
                continue
            layer = SURF_LAYER.get(key)
            if layer is None:
                skipped.append(key)       # as villa_gltf.surfaces: no THICK
                continue
            _, _, t = LAYERS[layer]
            # Split at the garden edge. One level per surface, taken from a
            # single representative point, buried every planting bed south of
            # the house inside the 700 mm garden platform and floated the lawn
            # beside the house 700 mm above the forecourt.
            garden = platform
            for piece, z_base in ((geom.intersection(garden), GARDEN_Z),
                                  (geom.difference(garden), 0.0)):
                if piece.is_empty or piece.area < 1.0:
                    continue
                try:
                    on(layer, prism(ms, piece, z_base, z_base + t))
                except Exception as exc:
                    print(f"  landscape {key}: {str(exc)[:50]}")
        if skipped:
            print(f"  landscape: surfaces with no layer, not built: {skipped}")

    # ---- glazing -----------------------------------------------------------
    # The openings were all cut correctly -- probes confirm 37/37 are real
    # holes. But a hole with nothing in it reads as nothing in a shaded view,
    # and a renderer has no surface to put glass on. Every window and every
    # sliding door gets a pane (a SLIDE is glass, floor to head, not a leaf);
    # every external hinged door gets a leaf -- villa_geom.infill, as glTF.
    try:
        gl = doc.Layers.Item("L-GLAZ")
    except Exception:
        gl = doc.Layers.Add("L-GLAZ")
    gl.color = 151
    try:
        dl = doc.Layers.Item("L-DOOR")
    except Exception:
        dl = doc.Layers.Add("L-DOOR")
    dl.color = 33

    panes = 0
    for o in V.OPENINGS:
        fill = G.infill(o)
        if fill is None:
            continue
        layer = "L-GLAZ" if fill[0] == "glass" else "L-DOOR"
        on(layer, box3(ms, *fill[1]))
        panes += 1
    print(f"  glazing: {panes} panes and leaves")

    # water: the thing that was missing entirely -- the rill (only a design
    # with RILL_W has one), the pool on its floor profile, a basin, the sheet
    # over a weir: villa_geom.water_parts, as villa_gltf.landscape
    for b in G.water_parts():
        on("L-WATER", part3(ms, b))
    print(f"  landscape: {len(land)} solids   {time.perf_counter()-t0:.0f}s")

    # AddRegion does not consume its polyline and AddExtrudedSolid does not
    # consume its region, so every extrusion leaves two dead entities in the
    # drawing. Invisible when shaded, but they ship in the DWG and in every
    # selection -- 96 of them last time.
    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, created)
    junk = [e for e in doc.ModelSpace if str(e.ObjectName) != "AcDb3dSolid"]
    for e in junk:
        try:
            e.Delete()
        except Exception:
            pass
    try:
        doc.PurgeAll()
    except Exception:
        pass
    print(f"  cleaned {len(junk)} construction entities")

    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, created)
    n3d = sum(1 for e in doc.ModelSpace if str(e.ObjectName) == "AcDb3dSolid")
    total = int(doc.ModelSpace.Count)
    # report per LAYER now: there is no single "base" solid any more, which
    # was the whole point of the change
    per = {}
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for e in doc.ModelSpace:
        if str(e.ObjectName) != "AcDb3dSolid":
            continue
        sol = w.CastTo(e, "IAcad3DSolid")
        rec = per.setdefault(str(e.Layer), [0, 0.0])
        rec[0] += 1
        rec[1] += float(sol.Volume) / 1e9
        a_, b_ = e.GetBoundingBox()
        for k in range(3):
            lo[k] = min(lo[k], a_[k])
            hi[k] = max(hi[k], b_[k])
    vol = sum(v for _, v in per.values())
    doc.SaveAs(DWG)
    try:
        vp = doc.ActiveViewport
        vp.Direction = pt(-1, -1, 1)
        doc.ActiveViewport = vp
        doc.SendCommand("_.VSCURRENT\n_Shaded\n_.ZOOM\n_E\n")
    except Exception as exc:
        print("  view warning:", str(exc)[:60])

    print(f"\n{total} entities, {n3d} 3D solid(s)")
    for lay in sorted(per):
        print(f"   {lay:14s} {per[lay][0]:>2} solid(s)  {per[lay][1]:>8.1f} m3")
    print(f"bbox  x {lo[0]:.0f}..{hi[0]:.0f}   y {lo[1]:.0f}..{hi[1]:.0f}   "
          f"z {lo[2]:.0f}..{hi[2]:.0f}")
    print(f"volume {vol:.1f} m3   ->  {os.path.basename(DWG)}")


if __name__ == "__main__":
    last = None
    for attempt in range(6):
        try:
            run()
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy, retrying whole job ({attempt + 1})...")
            time.sleep(6)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
