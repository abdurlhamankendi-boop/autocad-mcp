"""Offline proof that the builders and sheets speak villa_design's new language.

    python tests/test_builders_offline.py            (from the project folder)
    python -m unittest tests.test_builders_offline

No AutoCAD, no COM: villa_gltf (build123d), villa_cad / villa_colour (ezdxf)
and villa_svg only. Everything is written under VILLA_OUT -- by default
%TEMP%\\villa_builders_test -- and the test refuses to run against the issued
Villa folder.

Two designs are exercised:

  * the CURRENT design, untouched: the glTF model passes every probe and the
    title blocks print the validator's real counts;
  * a SYNTHETIC design: villa_design is monkeypatched in memory (the file is
    never edited) with
      - an annex room on floor "AX", north of the house, with an external door
        and a street window, and annex furniture (villa_furniture_spec.ANNEX),
      - the family living's south window replaced by a SLIDE,
      - one SHADES box over that slide,
      - FIN_ARRAYS kept as they are;
    and it is proved that villa_gltf builds it (annex walls/slab/roof/parapet
    at LEVEL["AX"], the slide cut through the wall floor-to-head with a pane
    and a meeting stile in it, the shade box in the bronze group, every probe
    passing) and that villa_cad / villa_colour / villa_svg draw it. The
    design has an annex of its own now; the synthetic one replaces it.

  * the INTEGRATED design (PROJECT_STATE s12): 0 fatal / 0 major with the
    DBC checks; the pool floor profile, the basin grate, the plant vault,
    the glass guards and the gates are in the model and on the sheets; the
    stair is DBC and drawn riser by riser; every group has a Blender
    material; the glTF pre-export guard refuses a displaced group; and each
    new check fires on a broken design (fault injection, in memory).

  * the REVIEW FIXES (2026-09-26): every external door is reachable from a
    gate by a 900 path (check 22), and the reviewer's case -- the annex 235
    from the majlis's flight -- fails it; the house stair is in the model,
    solid, with glass on its open sides and a handrail on every open side of
    every flight (K-SGR-01/-02, K-GRD-01/-02, K-HR-01 checked, and firing
    when the glass, the rails or the solid stair are taken away); check 16
    exempts windows only, and the west-face service door fails it again.
"""

from __future__ import annotations

import contextlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(ROOT)

OUT = os.environ.setdefault(
    "VILLA_OUT", os.path.join(tempfile.gettempdir(), "villa_builders_test"))

import villa_geom as G  # noqa: E402  (reads VILLA_OUT)

if os.path.normcase(os.path.abspath(G.out_dir())) == \
        os.path.normcase(os.path.abspath(G.DEFAULT_OUT)):
    raise SystemExit("VILLA_OUT points at the issued Villa folder -- refusing")

import ezdxf  # noqa: E402
from build123d import Vector  # noqa: E402

import villa_cad as CAD  # noqa: E402
import villa_colour as CC  # noqa: E402
import villa_design as V  # noqa: E402
import villa_furniture_spec as F  # noqa: E402
import villa_gltf as GL  # noqa: E402
import villa_svg as SVG  # noqa: E402

SYN = os.path.join(G.out_dir(), "synthetic")
CUR = os.path.join(G.out_dir(), "current")


# ============================================================ the synthetic
def synthetic():
    """The patches, computed from the design so they stay valid if the
    designers move things: the annex sits 1600 clear of the house's street
    face (DBC K.5.2.3 wants >= 1500), against the north boundary."""
    face = V.outline("GF").bounds[3]
    oy0 = face + 1600.0                         # annex outside face, south
    # on the street boundary (DBC K-ANX-03: on the boundary or within the
    # setbacks), its door 1015 wide (K-DOOR-01: 915 clear)
    ry0, ry1 = oy0 + V.WALL, V.PLOT_D - V.WALL
    # its west wall 1035 clear of the majlis's street flight (check 22: a
    # 900 path from the gates to every external door)
    rx0, rx1 = 17900.0, 23000.0
    room = ("DRIVER ROOM", rx0, ry0, rx1, ry1, V.HAB, "AX")
    door = ("AX", V.DOOR, "h", ry0 - V.WALL, ry0, rx0 + 600, rx0 + 1615,
            "DRIVER ROOM", None, 90)
    win = ("AX", V.WIN, "h", ry1, ry1 + V.WALL, rx0 + 2600, rx0 + 4100,
           "DRIVER ROOM", None, None)

    fam = next(r for r in V.ROOMS if r[0] == "FAMILY LIVING" and r[6] == "GF")
    fx0, fy0, fx1 = fam[1], fam[2], fam[3]
    slide = ("GF", V.SLIDE, "h", fy0 - V.WALL, fy0, fx0 + 500, fx1 - 500,
             "FAMILY LIVING", None, None)
    z_head = V.LEVEL["GF"] + V.DOOR_HEAD
    need = 0.6 * V.DOOR_HEAD
    shade = (fx0 + 400, fy0 - V.WALL - need - 100, fx1 - 400, fy0 - V.WALL,
             z_head, z_head + 200)              # (x0, y0, x1, y1, z0, z1)

    def not_living_south(o):
        return not (o[0] == "GF" and o[2] == "h" and o[8] is None
                    and o[7] == "FAMILY LIVING" and abs(max(o[3], o[4]) - fy0) < 1)

    annex_furniture = [("bed_single", rx0 + 1900, ry0 + 300, 90),
                       ("wardrobe", rx0 + 4400, ry1 - 600, 0)]
    return dict(room=room, door=door, win=win, slide=slide, shade=shade,
                keep=not_living_south, furniture=annex_furniture)


@contextlib.contextmanager
def patched():
    """villa_design / villa_furniture_spec with the synthetic changes, in
    memory only; everything is put back on exit."""
    S = synthetic()
    saved_v = {k: getattr(V, k) for k in ("ROOMS", "OPENINGS", "SHADES", "ZONE",
                                           "ROLE", "FIN_ARRAYS")}
    saved_f = {k: getattr(F, k) for k in ("ANNEX", "BY_FLOOR")}
    try:
        # the design now has an annex of its own: the synthetic one REPLACES
        # it (two DRIVER ROOMs on one floor would prove nothing)
        V.ROOMS = [r for r in V.ROOMS if r[6] != "AX"] + [S["room"]]
        V.OPENINGS = ([o for o in V.OPENINGS if S["keep"](o) and o[0] != "AX"]
                      + [S["slide"], S["door"], S["win"]])
        V.SHADES = list(V.SHADES) + [S["shade"]]
        V.ZONE = dict(V.ZONE, **{S["room"][0]: V.SERVICE})
        V.ROLE = dict(V.ROLE, **{S["room"][0]: "driver_room"})
        F.ANNEX = list(S["furniture"])
        F.BY_FLOOR = (("AX", F.ANNEX), ("GF", F.GROUND), ("FF", F.FIRST),
                      ("RF", F.ROOF))
        yield S
    finally:
        for k, v in saved_v.items():
            setattr(V, k, v)
        for k, v in saved_f.items():
            setattr(F, k, v)


@contextlib.contextmanager
def output(folder):
    """Point the sheet generators' OUT at `folder` (they read it at import)."""
    os.makedirs(folder, exist_ok=True)
    saved = (CAD.OUT, CC.OUT, GL.OUT)
    CAD.OUT = CC.OUT = folder
    GL.OUT = os.path.join(folder, "render")
    os.makedirs(GL.OUT, exist_ok=True)
    try:
        yield folder
    finally:
        CAD.OUT, CC.OUT, GL.OUT = saved


def inside(solid, x, y, z):
    return solid is not None and solid.is_inside(Vector(x, y, z))


def any_inside(groups, x, y, z, keys=("walls", "slabs", "base", "roof", "fins",
                                      "pool", "boundary")):
    return any(inside(groups.get(k), x, y, z) for k in keys)


def texts(doc):
    return [e.dxf.text for e in doc.modelspace() if e.dxftype() == "TEXT"]


def in_box(pts, bx, tol=1.0):
    x0, y0, x1, y1 = bx
    return all(x0 - tol <= x <= x1 + tol and y0 - tol <= y <= y1 + tol
               for x, y in pts)


def entity_points(e):
    t = e.dxftype()
    if t == "LINE":
        return [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    if t == "LWPOLYLINE":
        return [(p[0], p[1]) for p in e.get_points("xy")]
    if t == "HATCH":
        pts = []
        for path in e.paths:
            if hasattr(path, "vertices"):
                pts += [(v[0], v[1]) for v in path.vertices]
        return pts
    return []


def on_layer_in(doc, layer, bx, types=None):
    """Entities on `layer` lying entirely inside the plan box `bx`."""
    out = []
    for e in doc.modelspace():
        if e.dxf.layer != layer or (types and e.dxftype() not in types):
            continue
        pts = entity_points(e)
        if pts and in_box(pts, bx):
            out.append(e)
    return out


# ============================================================ the current
class CurrentDesign(unittest.TestCase):
    """The design as it stands must still build, probe clean, and be drawn."""

    def test_gltf_probes(self):
        groups = GL.building()
        groups["boundary"] = GL.boundary()
        self.assertTrue(GL.verify(groups), "current design fails its probes")
        # the fins come from V.fins(), not a loop: same count, same place
        fb = G.fin_boxes()
        self.assertEqual(len(fb), len(V.fins()))
        for b in fb:
            self.assertTrue(inside(groups["fins"], (b[0] + b[3]) / 2,
                                   (b[1] + b[4]) / 2, (b[2] + b[5]) / 2))

    def test_sheets_title_block_is_computed(self):
        val = G.validation()
        with output(CUR):
            _, path = CAD.build_plan("GF", "A-102", "Ground floor plan", val=val)
            _, spath = CAD.build_site(val=val)
            _, ppath = CC.plan("GF", "A-102P", "Ground floor - presentation", val=val)
        want = f"{val['fatal']} FATAL / {val['major']} MAJOR"
        for pth in (path, spath, ppath):
            tx = " | ".join(texts(ezdxf.readfile(pth)))
            self.assertIn(want, tx, pth)
            if val["fatal"] or val["major"]:
                self.assertNotIn("0 FATAL / 0 MAJOR", tx, pth)
            self.assertNotIn("GROSS INTERNAL AREA", tx, pth)
        tx = " | ".join(texts(ezdxf.readfile(path)))
        net, gross = G.floor_areas("GF")
        self.assertIn(f"GF NET {net:.1f} / GROSS {gross:.1f} m2", tx)
        stx = " | ".join(texts(ezdxf.readfile(spath)))
        self.assertIn(f"GFA (GROSS) {V.gross_area():.1f} m2", stx)
        self.assertIn(f"FORECOURT {G.forecourt_text()}", stx)


# ================================================ the integrated design (s12)
class IntegratedDesign(unittest.TestCase):
    """The data added in the integration -- pool floor profile, basin grate,
    plant vault, glass guards, gates, DBC stair -- reaches BOTH the model and
    the sheets, and the new checks fire on a broken design."""

    @classmethod
    def setUpClass(cls):
        cls.groups = GL.building()
        cls.groups["boundary"] = GL.boundary()
        cls.land = GL.landscape()

    def test_compliant(self):
        iss = V.validate()
        self.assertFalse([i for i in iss if i.startswith(("[FATAL]", "[MAJOR]"))], iss)
        self.assertEqual(F.check(), [])

    def test_pool_floor_is_the_profile(self):
        pool, water = self.groups["pool"], self.land["water"]
        pts = sorted(V.POOL_FLOOR)
        slope = max(zip(pts, pts[1:]), key=lambda s: abs(s[1][1] - s[0][1]))
        for y in (V.POOL_Y1 - 500, (slope[0][0] + slope[1][0]) / 2, V.POOL_Y0 + 500):
            z = V.pool_floor_at(y)
            self.assertTrue(inside(pool, V.AXIS, y, z - 100), f"no floor under y {y}")
            self.assertFalse(inside(pool, V.AXIS, y, z + 100), f"floor over y {y}")
            self.assertTrue(inside(water, V.AXIS, y, z + 100), f"no water at y {y}")
            self.assertFalse(inside(water, V.AXIS, y, z - 100), f"water in the floor {y}")
        # shallowest 1100, deepest 1450 -- and never a constant 1.4 m box
        self.assertAlmostEqual(V.POOL_TW - V.pool_floor_at(V.POOL_Y1 - 1), 1100, delta=1)
        self.assertAlmostEqual(V.POOL_TW - V.pool_floor_at(V.POOL_Y0 + 1), 1450, delta=1)

    def test_grate_vault_and_guards_are_built(self):
        g = self.groups
        by = (V.BASIN_Y0 + V.BASIN_WALL + V.BASIN_Y1) / 2
        self.assertTrue(inside(g["grate"], V.AXIS, by, V.GARDEN_Z + V.GRATE_T / 2))
        self.assertFalse(any_inside(g, V.AXIS, by, V.BASIN_FL + 300))   # open below
        # the weir is not lidded: no coping over it, water can spill
        surf = CC.ground_surfaces()
        from shapely.geometry import Point
        self.assertFalse(surf["poolsurround"].contains(Point(V.AXIS, V.POOL_Y0 - 200)))
        px0, py0, px1, py1 = V.POOL_PLANT
        self.assertFalse(any_inside(g, (px0 + px1) / 2, (py0 + py1) / 2, V.POOL_PLANT_FL + 1000))
        self.assertFalse(inside(self.land["terrain"], (px0 + px1) / 2, (py0 + py1) / 2, 0.0))
        boxes = G.guard_boxes()
        kinds = {k for k, _ in V.guards_labelled()}
        self.assertEqual(kinds, {"landing", "garden edge", "stair well",
                                 "stair flight", "stair landing"})
        for x0, y0, z0, x1, y1, z1 in boxes:
            self.assertGreaterEqual(z1 - z0, 1200 - 1e-6)
            self.assertTrue(inside(g["guards"], (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

    def test_stair_and_handrails_are_built(self):
        """The house stair is in the model (solid, both flights and the
        half-landing), its glass stands on its open sides, and every handrail
        is a bar 900 over the nosing line (review of 2026-09-26)."""
        g = self.groups
        (lx0, ly0, lx1, ly1), zl = V.stair_landing()
        self.assertTrue(inside(g["stair"], (lx0 + lx1) / 2, (ly0 + ly1) / 2, zl - 50))
        self.assertFalse(any_inside(g, (lx0 + lx1) / 2, (ly0 + ly1) / 2, zl + 300,
                                    keys=("walls", "slabs", "stair", "guards", "rails")))
        for f in V.flights():
            for t0, t1, z in V.flight_treads(f)[:1]:
                x0, y0, x1, y1 = V.flight_plan(f, t0, t1)
                grp = "stair" if f["inside"] else "base"
                self.assertTrue(inside(g[grp], (x0 + x1) / 2, (y0 + y1) / 2, z - 30), f["name"])
        kinds = [k for k, _ in V.guards_labelled()]
        # flight 1 west, flight 2 over flight 1: a panel per tread each
        self.assertEqual(kinds.count("stair flight"), sum(len(V.flight_treads(f))
                                                          for f in V.flights() if f["inside"]))
        rails = V.handrails()
        self.assertEqual(len(rails), sum(len(f["open"]) for f in V.flights()))
        for h in rails:
            f = h["f"]
            for t in (h["t0"], (h["t0"] + h["t1"]) / 2, h["t1"]):
                top = h["top0"] + (h["top1"] - h["top0"]) * (t - h["t0"]) / (h["t1"] - h["t0"])
                self.assertAlmostEqual(top - V.pitch_at(f, t), V.HANDRAIL_H, delta=0.5)
            tm = (h["t0"] + h["t1"]) / 2
            zm = (h["top0"] + h["top1"]) / 2 - V.RAIL_T / 2
            cm = (h["c0"] + h["c1"]) / 2
            x, y = (cm, tm) if h["along"] == "y" else (tm, cm)
            self.assertTrue(inside(g["rails"], x, y, zm), f["name"])
            for x0, y0, z0, x1, y1, z1 in h["posts"]:
                self.assertTrue(inside(g["rails"], (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        # a 250 probe in the hall does not touch the stair, its glass or rails
        name = "GF ENTRANCE HALL"
        _n, x, y, z, _e, r = next(p for p in G.probes() if p[0] == name)
        from shapely.geometry import Point, box as _b
        from shapely.ops import unary_union
        things = unary_union([_b(b[0], b[1], b[3], b[4]) for b in G.stair_boxes()]
                             + [_b(b[0], b[1], b[3], b[4]) for b in G.guard_boxes()
                                if b[2] < z + r and b[5] > z - r])
        self.assertGreater(things.distance(Point(x, y)), r)

    def test_every_external_door_is_reachable(self):
        """Check 22: a 900 path from a gate to the foot of every external
        door's steps. The reviewer's case -- the annex back at 16800, 235
        from the majlis's flight -- fails it."""
        res = V.street_access()
        self.assertTrue(res)
        self.assertTrue(all(ok for _o, _b, ok in res), res)
        self.assertEqual({o[7] for o, _b, _ok in res},
                         {o[7] for o in V.OPENINGS if o[8] is None and o[1] == V.DOOR})
        # the annex's west wall back at 16800 (its plant room 700 wider)
        rooms = [(r[0], r[1] - 700 if r[0] == "PLANT ROOM" else r[1]) + tuple(r[2:])
                 for r in V.ROOMS]
        saved = V.ROOMS
        try:
            V.ROOMS = rooms
            bad = [o[7] for o, _b, ok in V.street_access() if not ok]
            text = " | ".join(V.validate())
        finally:
            V.ROOMS = saved
        self.assertEqual(sorted(bad), ["DRIVER ROOM", "PLANT ROOM", "STORE"])
        self.assertIn("cannot be reached from any gate", text)

    def test_gates_cut_from_data(self):
        b = self.groups["boundary"]
        y = V.PLOT_D - G.BW / 2
        for name, g0, g1, head in V.gates():
            self.assertFalse(inside(b, (g0 + g1) / 2, y, 1000), name)
            if head is not None:
                self.assertTrue(inside(b, (g0 + g1) / 2, y, (head + G.BH) / 2), name)
        # the old typed pedestrian gate (15400-16600) is wall again at 16500
        self.assertTrue(inside(b, 16500, y, 1000))

    def test_every_group_has_a_blender_material(self):
        import ast
        with open(os.path.join(ROOT, "villa_blender.py"), encoding="utf-8") as fh:
            src = fh.read()
        node = next(n for n in ast.parse(src).body if isinstance(n, ast.Assign)
                    and getattr(n.targets[0], "id", "") == "ASSIGN")
        assign = ast.literal_eval(node.value)
        for k in list(self.groups) + list(self.land):
            self.assertIn(k, assign, f"villa_blender.ASSIGN has no material for {k}")

    def test_pre_export_guard(self):
        from build123d import Location
        good = GL.box(0, 0, 0, 100, 100, 100)
        moved = Location((0, 0, 700)) * GL.box(0, 0, 0, 100, 100, 100)
        self.assertFalse(GL.placed(good))
        self.assertTrue(GL.placed(moved))
        saved = (GL.building, GL.boundary, GL.verify, GL.landscape)
        folder = os.path.join(G.out_dir(), "guard")
        try:
            GL.building = lambda: {"walls": good, "slabs": moved}
            GL.boundary = lambda: good
            GL.verify = lambda groups: True
            GL.landscape = lambda: {}
            with output(folder):
                with self.assertRaises(SystemExit) as cm:
                    GL.main()
            self.assertIn("slabs", str(cm.exception))
            self.assertFalse(os.path.exists(os.path.join(folder, "render", "villa_walls.glb")))
        finally:
            GL.building, GL.boundary, GL.verify, GL.landscape = saved

    def test_stair_meets_the_code_and_is_drawn_so(self):
        import villa_elevations as EL
        self.assertLessEqual(V.FF2FF / V.RISERS, 180)
        self.assertGreaterEqual(V.STAIR_GOING, 280)
        risers = G.stair_risers()
        self.assertEqual(len(risers), V.RISERS)
        ys = sorted({round(y) for _, y, _ in risers})
        self.assertTrue(all(abs((b - a) - V.STAIR_GOING) < 1 for a, b in zip(ys, ys[1:])))
        bb = EL.stair_solid().bounding_box()
        self.assertAlmostEqual(bb.min.Z, V.GF, delta=1)
        self.assertAlmostEqual(bb.max.Z, V.FF, delta=1)

    def test_new_checks_fire(self):
        def issues(**patch):
            saved = {k: getattr(V, k) for k in patch}
            try:
                for k, v in patch.items():
                    setattr(V, k, v)
                return " | ".join(V.validate())
            finally:
                for k, v in saved.items():
                    setattr(V, k, v)
        t = issues(guards_labelled=lambda: [])
        self.assertIn("K-POOL-08", t)
        self.assertIn("open edge has no guard", t)
        t = issues(POOL_FLOOR=((V.POOL_Y1, -200.0), (V.POOL_Y1 - 1000, -200.0),
                               (V.POOL_Y1 - 2000, -550.0), (V.POOL_Y0, -550.0)))
        self.assertIn("K-POOL-02", t)
        self.assertIn("BASIN_GRATED but", issues(grate=lambda: []))
        # a street door whose flight lands in the car porch costs a bay: the
        # maid room's, near the porch's east end
        ops = list(V.OPENINGS) + [("GF", V.DOOR, "h", 22750, 23150, 9000, 10015,
                                   "MAID ROOM", None, 270)]
        self.assertIn("parking holds 1 bay", issues(OPENINGS=ops))
        # check 16 exempts punched WINDOWS only: the service door back on the
        # west face (where the integration had put it) fails it again
        ops = [o for o in V.OPENINGS if not (o[7] == "DIRTY KITCHEN" and o[1] == V.DOOR
                                            and o[8] is None)]
        ops.append(("GF", V.DOOR, "v", 3000, 3400, 21600, 22615, "DIRTY KITCHEN", None, 0))
        self.assertIn("DIRTY KITCHEN faces west with no fins", issues(OPENINGS=ops))
        # the house stair's own open sides: without their glass, K-SGR-02
        # fires for both flights and the half-landing; without the first
        # floor's guards round the well, K-GRD-01 for the floor
        lab = V.guards_labelled
        t = issues(guards_labelled=lambda: [g for g in lab()
                                            if g[0] not in ("stair flight", "stair landing")])
        for what in ("stair flight 1", "stair flight 2", "stair half-landing", "K-SGR-02"):
            self.assertIn(what, t)
        self.assertNotIn("first floor round", t)
        t = issues(guards_labelled=lambda: [g for g in lab() if g[0] != "stair well"])
        self.assertIn("first floor round the stair void", t)
        # K-HR-01: every open side of every flight, inside and out
        t = issues(handrails=lambda: [])
        self.assertIn("K-HR-01", t)
        for f in V.flights():
            self.assertIn(f["name"], t)
        # with the stair NOT solid, the lower flight's inner side opens too
        self.assertIn("stair flight 1: its open east/north side", issues(STAIR_SOLID=False))
        # a window in the annex's EAST wall -- on the boundary -- faces the
        # neighbour at 0 mm (K-WIN-09)
        ax = V.outline("AX").bounds
        ops = list(V.OPENINGS) + [("AX", V.WIN, "v", ax[2] - V.WALL, ax[2], 26000, 27000,
                                    "DRIVER ROOM", None, None)]
        self.assertIn("K-WIN-09", issues(OPENINGS=ops))
        ax0 = V.outline("AX").bounds[0]            # 200 from the annex's west wall
        self.assertIn("from a building on the boundary",
                      issues(PED_GATE=(ax0 - 1400.0, ax0 - 200.0)))

    def test_sheets_draw_the_new_data(self):
        val = G.validation()
        with output(CUR):
            _, spath = CAD.build_site(val=val)
            _, gpath = CAD.build_plan("GF", "A-102", "Ground floor plan", val=val)
            _, fpath = CAD.build_plan("FF", "A-103", "First floor plan", val=val)
        sdoc, gdoc, fdoc = (ezdxf.readfile(p) for p in (spath, gpath, fpath))
        tx = " | ".join(texts(sdoc))
        for name, g0, g1, _h in V.gates():
            self.assertIn(name, tx)
        doors = [e for e in sdoc.modelspace() if e.dxf.layer == "A-DOOR"
                 and e.dxftype() == "LINE"]
        spans = sorted((round(min(e.dxf.start.x, e.dxf.end.x)),
                        round(max(e.dxf.start.x, e.dxf.end.x))) for e in doors)
        self.assertEqual(spans, sorted((round(g0), round(g1)) for _n, g0, g1, _h in V.gates()))
        self.assertIn("GRATE OVER BALANCE BASIN", tx)
        self.assertIn("POOL PLANT BELOW", tx)
        self.assertIn(f"{V.POOL_TW - V.POOL_SHALLOW_FL:.0f} DEEP", tx)
        n_gf = len([e for e in gdoc.modelspace() if e.dxf.layer == CAD.GUARD_LAYER])
        n_ff = len([e for e in fdoc.modelspace() if e.dxf.layer == CAD.GUARD_LAYER])
        self.assertEqual(n_gf, len(G.guards_on("GF")))
        self.assertEqual(n_ff, len(G.guards_on("FF")))
        self.assertGreater(n_ff, 0)
        stairs = [e for e in gdoc.modelspace() if e.dxf.layer == "A-FLOR-STRS"
                  and e.dxftype() == "LINE"]
        self.assertGreaterEqual(len(stairs), V.RISERS)
        sec = SVG.section()
        self.assertIn(f"TW +{V.POOL_TW:.0f}", sec)
        self.assertIn(" TO ", sec)


# ========================================================== the synthetic
class SyntheticDesign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ctx = patched()
        cls.S = cls._ctx.__enter__()
        cls.groups = GL.building()
        cls.groups["boundary"] = GL.boundary()
        cls.land = GL.landscape()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    # ---------------------------------------------------------- design data
    def test_patch_is_the_new_language(self):
        self.assertIn("AX", V.floors())
        self.assertEqual(G.standalone_floors(), ["AX"])
        self.assertEqual(G.sheet_floors("GF"), ["GF", "AX"])
        gap = V.outline("AX").distance(V.outline("GF"))
        self.assertGreaterEqual(gap, 1500.0)
        issues = V.validate()                   # runs on the patched design
        self.assertFalse(any("annex" in i and "FATAL" in i for i in issues), issues)
        # the annex door gets a landing if the annex floor stands above the
        # ground in front of it, and none at a level threshold (AX_FL is the
        # street level since the review of 2026-09-26)
        steps = V.external_steps()
        landed = any(abs(b[5] - V.LEVEL["AX"]) < 1e-6 and b[5] > b[2] for b in steps)
        self.assertEqual(landed, V.LEVEL["AX"] > V.STREET + 1e-6,
                         "annex door landing does not match its floor level")
        self.assertFalse([i for i in issues if "cannot be reached" in i], issues)

    # ----------------------------------------------------------- glTF model
    def test_all_probes_pass(self):
        self.assertTrue(GL.verify(self.groups))
        names = [p[0] for p in G.probes()]
        for want in ("AX roof slab", "AX floor slab", "AX parapet",
                     "AX external wall", "shade 0"):
            self.assertIn(want, names)
        self.assertTrue(any("cut to the floor" in n for n in names))

    def test_annex_solid_at_its_level(self):
        g = self.groups
        S = G.storey("AX")
        z0, z1 = S["z0"], S["z1"]
        self.assertEqual(z0, V.LEVEL["AX"])
        self.assertEqual(z1, V.LEVEL["AX"] + V.CEIL["AX"])
        bx, by = G._pt(G._clear_band(S["out"], S["inner"]))
        # walls run floor to ceiling of the annex, not the house's levels
        self.assertTrue(inside(g["walls"], bx, by, z0 + 100))
        self.assertTrue(inside(g["walls"], bx, by, z1 - 100))
        self.assertFalse(inside(g["walls"], bx, by, z0 - 100))
        self.assertFalse(inside(g["walls"], bx, by, z1 + 100))
        # slab under, roof over, parapet on the edge
        self.assertTrue(inside(g["slabs"], bx, by, z0 - 100))
        self.assertTrue(inside(g["roof"], bx, by, z1 + V.SLAB / 2))
        ex, ey = G._pt(S["edge"])
        self.assertTrue(inside(g["roof"], ex, ey, S["parapet"][1] - 50))
        self.assertFalse(inside(g["roof"], ex, ey, S["parapet"][1] + 50))
        # the room is open from floor to ceiling
        r = self.S["room"]
        cx, cy = (r[1] + r[3]) / 2, (r[2] + r[4]) / 2
        for z in (z0 + 200, z0 + 1500, z1 - 200):
            self.assertFalse(any_inside(g, cx, cy, z), f"annex room solid at {z}")
        # bounding box of the walls now reaches the annex
        bb = g["walls"].bounding_box()
        self.assertGreaterEqual(bb.max.Y, V.outline("AX").bounds[3] - 1)
        self.assertLessEqual(bb.min.Z, z0 + 1)

    def test_annex_openings_cut(self):
        g = self.groups
        for o in (self.S["door"], self.S["win"]):
            x0, y0, lo, x1, y1, hi = G.cut_box(o)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            self.assertFalse(inside(g["walls"], cx, cy, (lo + hi) / 2), o[1])
            self.assertTrue(inside(g["walls"], cx, cy, hi + 150), o[1])
        # the window has a sill; the door does not
        x0, y0, lo, x1, y1, hi = G.cut_box(self.S["win"])
        self.assertTrue(inside(g["walls"], (x0 + x1) / 2, (y0 + y1) / 2, lo - 150))
        x0, y0, lo, x1, y1, hi = G.cut_box(self.S["door"])
        self.assertFalse(inside(g["walls"], (x0 + x1) / 2, (y0 + y1) / 2, lo + 150))
        self.assertTrue(inside(self.land["door"], (x0 + x1) / 2, (y0 + y1) / 2,
                               lo + 1000), "external annex door has no leaf")

    def test_slide_full_height_with_a_pane(self):
        g, land = self.groups, self.land
        o = self.S["slide"]
        x0, y0, lo, x1, y1, hi = G.cut_box(o)
        self.assertEqual((lo, hi), V.opening_z(o))
        self.assertEqual(lo, V.LEVEL["GF"])            # cut like a door
        xq, cy = x0 + 0.25 * (x1 - x0), (y0 + y1) / 2
        # through the wall, floor to head: a window would be solid below its sill
        for z in (lo + 50, lo + V.WIN_SILL / 2, (lo + hi) / 2, hi - 50):
            self.assertFalse(inside(g["walls"], xq, cy, z), f"wall at z {z}")
        for y in (y0 + 20, y1 - 20):                    # both faces, all through
            self.assertFalse(inside(g["walls"], xq, y, lo + 100))
        self.assertTrue(inside(g["walls"], xq, cy, hi + 150), "no head over it")
        # a glass pane in it, from the floor -- not a door leaf
        self.assertTrue(inside(land["glass"], xq, cy, lo + 300))
        self.assertTrue(inside(land["glass"], xq, cy, hi - 100))
        self.assertFalse(inside(land.get("door"), xq, cy, lo + 300))
        # framed, with a meeting stile in the middle
        self.assertTrue(inside(g["frames"], (x0 + x1) / 2, cy, (lo + hi) / 2))

    def test_shade_box_present(self):
        g = self.groups
        x0, y0, x1, y1, z0, z1 = self.S["shade"]
        for x, y in (((x0 + x1) / 2, (y0 + y1) / 2), (x0 + 50, y0 + 50),
                     (x1 - 50, y1 - 50)):
            self.assertTrue(inside(g["fins"], x, y, (z0 + z1) / 2))
        self.assertFalse(inside(g["fins"], (x0 + x1) / 2, (y0 + y1) / 2, z1 + 50))
        # and the fins are still there -- if the design has any (it has none
        # since the DBC setback rules; the side walls have punched windows)
        for fb in G.fin_boxes()[:1]:
            self.assertTrue(inside(g["fins"], (fb[0] + fb[3]) / 2,
                                   (fb[1] + fb[4]) / 2, (fb[2] + fb[5]) / 2))

    def test_ground_is_not_laid_inside_the_annex(self):
        r = self.S["room"]
        cx, cy = (r[1] + r[3]) / 2, (r[2] + r[4]) / 2
        self.assertFalse(inside(self.land["terrain"], cx, cy, -150))
        self.assertFalse(inside(self.land.get("lawn"), cx, cy, 15))

    def test_gltf_export(self):
        with output(SYN):
            GL.main()
        render = os.path.join(SYN, "render")
        import json
        with open(os.path.join(render, "groups.json")) as fh:
            man = json.load(fh)
        for k in ("walls", "slabs", "roof", "fins", "glass", "frames"):
            self.assertTrue(os.path.exists(os.path.join(render, f"villa_{k}.glb")), k)
        self.assertGreaterEqual(man["walls"][4], V.outline("AX").bounds[3] - 1)
        self.assertTrue(os.path.exists(os.path.join(render, "villa.glb")))

    # --------------------------------------------------------------- sheets
    def test_cad_ground_floor_sheet(self):
        val = G.validation()
        with output(SYN):
            _, path = CAD.build_plan("GF", "A-102", "Ground floor plan", val=val)
        doc = ezdxf.readfile(path)
        ax = V.outline("AX").bounds
        # annex walls, poche, window and door symbols, label
        self.assertTrue(on_layer_in(doc, "A-WALL-EXTR", ax, {"LWPOLYLINE"}))
        self.assertTrue(on_layer_in(doc, "A-WALL-PATT", ax, {"HATCH"}))
        self.assertTrue(on_layer_in(doc, "A-GLAZ", G.cut_box(self.S["win"])[0:2]
                                    + G.cut_box(self.S["win"])[3:5]))
        swings = [e for e in doc.modelspace() if e.dxf.layer == "A-DOOR-SWNG"]
        dx = G.cut_box(self.S["door"])
        self.assertTrue(any(abs(e.dxf.center.x - dx[0]) < 1
                            and abs(e.dxf.center.y - (dx[1] + dx[4]) / 2) < 1
                            for e in swings), "annex door has no swing")
        tx = texts(doc)
        self.assertIn("DRIVER ROOM", tx)
        # the slide: glazed opening + slider line, and NO swing arc
        sx0, sy0, _, sx1, sy1, _ = G.cut_box(self.S["slide"])
        near = (sx0 - 5, sy0 - 300, sx1 + 5, sy1 + 300)
        self.assertGreaterEqual(len(on_layer_in(doc, "A-GLAZ", near, {"LINE"})), 4)
        self.assertGreaterEqual(len(on_layer_in(doc, "A-DOOR", near, {"LINE"})), 3)
        for e in swings:
            c = e.dxf.center
            self.assertFalse(sx0 - 1 <= c.x <= sx1 + 1 and sy0 - 1 <= c.y <= sy1 + 1,
                             "the slide was drawn with a swing arc")
        # the old window symbol is gone from the living room's south wall
        mid = [e for e in on_layer_in(doc, "A-GLAZ", near, {"LINE"})
               if abs(e.dxf.start.y - (sy0 + sy1) / 2) < 1
               and abs(e.dxf.end.y - (sy0 + sy1) / 2) < 1]
        self.assertFalse(mid, "a window centre line is drawn over the slide")
        # shading: dashed overhead outlines, the shade among them
        ov = [e for e in doc.modelspace() if e.dxf.layer == CAD.SHADE_LAYER]
        self.assertEqual(len(ov), len(G.overhead("GF")))
        x0, y0, x1, y1, z0, z1 = self.S["shade"]
        self.assertTrue(on_layer_in(doc, CAD.SHADE_LAYER, (x0, y0, x1, y1)))
        self.assertEqual(doc.layers.get(CAD.SHADE_LAYER).dxf.linetype, "DASHED")
        # computed title block, labelled areas
        joined = " | ".join(tx)
        self.assertIn(f"{val['fatal']} FATAL / {val['major']} MAJOR", joined)
        self.assertIn("ANNEX NET", joined)
        self.assertIn("GF NET", joined)
        self.assertIn(G.design_date(), joined)

    def test_cad_site_and_manifest(self):
        val = G.validation()
        with output(SYN):
            _, spath = CAD.build_site(val=val)
            items, mpath = CAD.furniture_manifest()
        doc = ezdxf.readfile(spath)
        ax = V.outline("AX").bounds
        self.assertTrue(on_layer_in(doc, "A-WALL-EXTR", ax, {"LWPOLYLINE"}))
        self.assertIn("ANNEX", texts(doc))
        self.assertIn(f"GFA (GROSS) {V.gross_area():.1f} m2", " | ".join(texts(doc)))
        ann = [it for it in items if it["floor"] == "AX"]
        self.assertEqual(len(ann), len(self.S["furniture"]))
        self.assertTrue(all(it["sheet"] == "GF" for it in ann))
        self.assertTrue(os.path.dirname(mpath).startswith(SYN))
        # villa_verify expects them on the ground-floor sheet
        keys = [it[0] for fl, it in G.sheet_furniture("GF") if fl == "AX"]
        self.assertEqual(sorted(keys), sorted(k for k, *_ in self.S["furniture"]))

    def test_colour_sheets(self):
        val = G.validation()
        with output(SYN):
            _, ppath = CC.plan("GF", "A-102P", "Ground floor - presentation", val=val)
            _, spath = CC.site(val=val)
        ax = V.outline("AX").bounds
        doc = ezdxf.readfile(ppath)
        self.assertTrue(on_layer_in(doc, "A-FLOR-FILL", ax, {"HATCH"}), "annex floor")
        self.assertTrue(on_layer_in(doc, "A-WALL-FILL", ax, {"HATCH"}), "annex poche")
        furn = on_layer_in(doc, "A-FURN-FILL", ax, {"HATCH"})
        self.assertEqual(len(furn), len(self.S["furniture"]), "annex furniture")
        self.assertTrue([e for e in doc.modelspace() if e.dxf.layer == CAD.SHADE_LAYER])
        self.assertIn(f"{val['fatal']} FATAL / {val['major']} MAJOR",
                      " | ".join(texts(doc)))
        sdoc = ezdxf.readfile(spath)
        self.assertTrue(on_layer_in(sdoc, "A-FLOR-FILL", ax, {"HATCH"}), "site annex")
        self.assertIn("ANNEX", texts(sdoc))
        # no lawn laid inside the annex
        surf = CC.ground_surfaces()
        self.assertLess(surf["lawn"].intersection(V.outline("AX")).area, 1.0)

    def test_svg_plate(self):
        s = SVG.plan("GF", "A-102", "Ground floor")
        self.assertIn("DRIVER ROOM", s)
        self.assertIn("ovhd", s)
        site = SVG.site()
        self.assertIn("ANNEX", site)
        os.makedirs(SYN, exist_ok=True)
        for name, text in (("plate_gf.svg", s), ("plate_site.svg", site)):
            with open(os.path.join(SYN, name), "w", encoding="utf-8") as fh:
                fh.write(text)


# ======================================================= a roof pavilion
class RoofPavilion(unittest.TestCase):
    """Floor "RF" is the same language: a storey of its own on the house roof,
    with a roof plan sheet of its own. Rooms on V.PV, the declared pavilion."""

    @classmethod
    def setUpClass(cls):
        px0, py0, px1, py1 = V.PV
        cls.room = ("ROOF PAVILION", px0 + V.WALL, py0 + V.WALL, px1 - V.WALL,
                    py1 - V.WALL, V.HAB, "RF")
        cls.saved = (V.ROOMS, V.ZONE, V.ROLE)
        V.ROOMS = list(V.ROOMS) + [cls.room]
        V.ZONE = dict(V.ZONE, **{cls.room[0]: V.FAMILY})
        V.ROLE = dict(V.ROLE, **{cls.room[0]: "family_living"})
        cls.groups = GL.building()
        cls.groups["boundary"] = GL.boundary()

    @classmethod
    def tearDownClass(cls):
        V.ROOMS, V.ZONE, V.ROLE = cls.saved

    def test_pavilion_built_on_the_roof(self):
        self.assertTrue(GL.verify(self.groups))
        S = G.storey("RF")
        self.assertEqual(S["z0"], V.LEVEL["RF"])
        self.assertIsNone(S["base"])
        r = self.room
        cx, cy = (r[1] + r[3]) / 2, (r[2] + r[4]) / 2
        self.assertTrue(inside(self.groups["roof"], cx, cy, V.RF + V.SLAB / 2))
        self.assertTrue(inside(self.groups["roof"], cx, cy, S["z1"] + V.SLAB / 2))
        self.assertFalse(any_inside(self.groups, cx, cy, S["z0"] + 1500))
        # the house parapet does not run through the pavilion
        band = V.envelope()["parapet_roof"].intersection(V.net_poly(r))
        if not band.is_empty:
            bx, by = G._pt(band)
            self.assertFalse(inside(self.groups["roof"], bx, by,
                                    V.RF + V.SLAB + V.PARAPET / 2))

    def test_roof_plan_sheets(self):
        self.assertIn(("RF", "A-104", "Roof pavilion plan"), CAD.plan_sheets())
        folder = os.path.join(G.out_dir(), "roof")
        with output(folder):
            _, path = CAD.build_plan("RF", "A-104", "Roof pavilion plan")
            _, ppath = CC.plan("RF", "A-104P", "Roof pavilion - presentation")
        self.assertIn("ROOF PAVILION", texts(ezdxf.readfile(path)))
        self.assertIn("ROOF NET", " | ".join(texts(ezdxf.readfile(ppath))))


if __name__ == "__main__":
    print(f"VILLA_OUT = {G.out_dir()}")
    unittest.main(verbosity=2)
