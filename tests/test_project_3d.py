"""Offline tests for the 3D builders' project hooks (massing, landscape).

    python -X utf8 tests\\test_project_3d.py
        the villa (root villa_design.py) in this process, then the Fairway
        project in a subprocess (run_project.py fairway <this file>)
    python -X utf8 run_project.py fairway tests\\test_project_3d.py
        the Fairway only

No AutoCAD and no COM. villa_gltf is built with build123d as always; the
AutoCAD builder (villa_3d_build) and its checks (villa_window_check,
villa_pool_check) are imported against a FAKE AutoCAD object model --
stand-in pythoncom / win32com modules whose ModelSpace makes build123d solids
(AddExtrudedSolid on a polyline's OCS, AddBox, Boolean, Move, GetBoundingBox,
CheckInterference) -- so villa_3d_build.run() executes end to end offline
and its layers can be compared with villa_gltf's groups, group for group.

What is proved, for whichever design is loaded:
  * the shared helpers (villa_geom.building_parts / site_parts /
    water_parts / layer_3d) read the design once for both builders;
  * the villa has no massing and no landscape_parts: both builders take the
    legacy path (stacked() / surfaces()), the rill is in the water;
  * the Fairway: every massing and landscape group is built and non-empty,
    the basement (B1) walls and slab are below grade, the stone skin is on
    its own group / layer, the forecourt ramp falls 200 -> 0, no rill;
  * both designs: the glTF model passes every probe, the AutoCAD model has
    the same groups (layer by layer) with the same volume and bounds, and
    passes the same probes; every opening probe point of
    villa_window_check is clear of every wall-like layer, and the pool
    check's levels find water (and nothing else) where it wants water;
    villa_pool_check.main() verifies on the fake -- and, with
    VILLA_TEST_SPHERES=1, villa_3d_verify.main() and
    villa_window_check.main() too (their sphere probes, a few minutes).

VILLA_OUT defaults to %TEMP%\\villa_project_3d_test; the test refuses to run
against the issued folder.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import os
import subprocess
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)          # run_project.py puts the project folder first
os.environ.setdefault("VILLA_OUT",
                      os.path.join(tempfile.gettempdir(), "villa_project_3d_test"))

import villa_geom as G  # noqa: E402  (reads VILLA_OUT)

if os.path.normcase(os.path.abspath(G.out_dir())) == \
        os.path.normcase(os.path.abspath(G.DEFAULT_OUT)):
    raise SystemExit("VILLA_OUT points at the issued deliverables folder -- refusing")

from build123d import Plane, Polyline, Pos, Solid, Vector, extrude, make_face  # noqa: E402

import villa_design as V  # noqa: E402
import villa_gltf as GL  # noqa: E402

PROJECT = getattr(V, "PROJECT", None)
IS_VILLA = (os.path.normcase(os.path.dirname(os.path.abspath(V.__file__)))
            == os.path.normcase(ROOT))
PY = sys.executable


# ======================================================== a fake AutoCAD
class _Bag:
    """An attribute bag (a layer, a viewport)."""


class FakeEntity:
    ObjectName = "AcDbEntity"

    def __init__(self, ms):
        self._ms = ms
        self.Layer = "0"
        ms.items.append(self)

    def Delete(self):
        self._ms.items[:] = [e for e in self._ms.items if e is not self]


class FakePolyline(FakeEntity):
    ObjectName = "AcDbPolyline"

    def __init__(self, ms, flat):
        super().__init__(ms)
        self.pts = [(float(flat[i]), float(flat[i + 1])) for i in range(0, len(flat), 2)]
        self.Closed = False
        self.Normal = [0.0, 0.0, 1.0]
        self.Elevation = 0.0


class FakeRegion(FakeEntity):
    ObjectName = "AcDbRegion"

    def __init__(self, ms, pl):
        super().__init__(ms)
        self.pl = pl


class FakeSolid(FakeEntity):
    ObjectName = "AcDb3dSolid"

    def __init__(self, ms, shape):
        super().__init__(ms)
        self.shape = shape

    def Move(self, p0, p1):
        self.shape = Pos(*[b - a for a, b in zip(p0, p1)]) * self.shape

    def Boolean(self, op, other):
        a, b = self.shape, other.shape
        self.shape = a + b if op == 0 else (a & b if op == 1 else a - b)
        other.Delete()

    def GetBoundingBox(self):
        bb = self.shape.bounding_box()
        return (bb.min.X, bb.min.Y, bb.min.Z), (bb.max.X, bb.max.Y, bb.max.Z)

    @property
    def Volume(self):
        return 0.0 if self.shape is None else self.shape.volume

    def CheckInterference(self, other, create=True):
        a, b = self.shape.bounding_box(), other.shape.bounding_box()
        if (a.min.X > b.max.X or b.min.X > a.max.X or a.min.Y > b.max.Y
                or b.min.Y > a.max.Y or a.min.Z > b.max.Z or b.min.Z > a.max.Z):
            return (None, False)
        if getattr(other, "sphere", None) is not None:
            # OCC's sphere booleans are not to be trusted for this: a thin box
            # cut from a sphere came back with a zero-area spherical face and
            # the volume of its two flat faces only (1.8 % for 7.6 %). AutoCAD
            # (ACIS) has no such trouble; sample the sphere instead.
            v = sampled_volume(self.shape, *other.sphere)
            return (FakeInterference(self._ms, v), True) if v > 0.0 else (None, False)
        r = self.shape & other.shape
        if r is None or r.volume <= 0.0:
            return (None, False)
        return (FakeSolid(self._ms, r), True)


class FakeInterference(FakeEntity):
    """The interference solid of a sphere probe: only its volume is read."""
    ObjectName = "AcDb3dSolid"
    shape = None

    def __init__(self, ms, volume):
        super().__init__(ms)
        self.Volume = volume


def sampled_volume(shape, c, r, n=7):
    """Volume of `shape` inside the sphere (c, r), from the cell centres of
    a (2n)^3 grid over the sphere (~1400 points in it): +-1 % or so."""
    import math
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_IN
    h = r / n
    offs = [(k + 0.5) * h for k in range(-n, n)]
    pts = [(c[0] + dx, c[1] + dy, c[2] + dz) for dx in offs for dy in offs for dz in offs
           if dx * dx + dy * dy + dz * dz <= r * r]
    solids = []
    for s in shape.solids():
        bb = s.bounding_box()
        if not (bb.min.X > c[0] + r or bb.max.X < c[0] - r or bb.min.Y > c[1] + r
                or bb.max.Y < c[1] - r or bb.min.Z > c[2] + r or bb.max.Z < c[2] - r):
            solids.append(BRepClass3d_SolidClassifier(s.wrapped))
    if not solids:
        return 0.0
    hit = 0
    for p in pts:
        q = gp_Pnt(*p)
        for cl in solids:
            cl.Perform(q, 1e-6)
            if cl.State() == TopAbs_IN:
                hit += 1
                break
    return hit / len(pts) * (4.0 / 3.0 * math.pi * r ** 3)


def _ocs_extrude(pl, h):
    """A region on a polyline's OCS extruded along its normal -- AutoCAD's
    arbitrary-axis rule for the three normals the builder uses: +Z (plan),
    +X (OCS x = world Y, OCS y = world Z) and +Y (OCS x = -world X, OCS y =
    world Z); the Elevation is along the normal."""
    n = tuple(int(round(v)) for v in pl.Normal)
    pts = list(pl.pts)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    e = float(pl.Elevation)
    if n == (0, 0, 1):
        P, d = [(a, b, e) for a, b in pts], (0, 0, 1)
    elif n == (1, 0, 0):
        P, d = [(e, a, b) for a, b in pts], (1, 0, 0)
    elif n == (0, 1, 0):
        P, d = [(-a, e, b) for a, b in pts], (0, 1, 0)
    else:
        raise NotImplementedError(f"normal {pl.Normal}")
    return extrude(make_face(Polyline(*P, close=True)), amount=float(h), dir=d)


class FakeModelSpace:
    def __init__(self):
        self.items = []

    def __iter__(self):
        return iter(list(self.items))

    @property
    def Count(self):
        return len(self.items)

    def AddLightWeightPolyline(self, flat):
        return FakePolyline(self, flat)

    def AddRegion(self, objs):
        return [FakeRegion(self, pl) for pl in objs]

    def AddExtrudedSolid(self, region, height, taper):
        return FakeSolid(self, _ocs_extrude(region.pl, height))

    def AddBox(self, c, dx, dy, dz):
        return FakeSolid(self, Solid.make_box(
            dx, dy, dz, Plane((c[0] - dx / 2, c[1] - dy / 2, c[2] - dz / 2))))

    def AddSphere(self, c, r):
        s = FakeSolid(self, Pos(*c) * Solid.make_sphere(r))
        s.sphere = (tuple(float(v) for v in c), float(r))
        return s


class FakeLayers:
    def __init__(self):
        self.d = {}

    def Item(self, name):
        if name not in self.d:
            raise KeyError(name)
        return self.d[name]

    def Add(self, name):
        lay = self.d.setdefault(name, _Bag())
        lay.color = 7
        return lay


class FakeDoc:
    def __init__(self, app, name):
        self.app, self.Name = app, name
        self.ModelSpace = FakeModelSpace()
        self.Layers = FakeLayers()
        self.ActiveViewport = _Bag()

    def SetVariable(self, *a):
        pass

    def PurgeAll(self):
        pass

    def SendCommand(self, *a):
        pass

    def SaveAs(self, path):
        self.Name = os.path.basename(path)       # no file is written

    def Close(self, save=False):
        self.app.docs.remove(self)


class FakeDocuments:
    def __init__(self, app):
        self.app = app

    @property
    def Count(self):
        return len(self.app.docs)

    def Item(self, i):
        return self.app.docs[i]

    def Add(self):
        d = FakeDoc(self.app, f"Drawing{len(self.app.docs) + 1}.dwg")
        self.app.docs.append(d)
        self.app.ActiveDocument = d
        return d

    def Open(self, path):
        raise RuntimeError(f"fake AutoCAD cannot open {path}")


class FakeAcad:
    def __init__(self):
        self.docs = []
        self.Documents = FakeDocuments(self)
        self.ActiveDocument = None

    def doc(self, name):
        return next(d for d in self.docs if d.Name.lower() == name.lower())


@contextlib.contextmanager
def fake_com(app):
    """pythoncom / win32com.client stand-ins bound to `app`, in sys.modules
    only while a script is imported; the real ones (if any) are restored."""
    pc = types.ModuleType("pythoncom")
    pc.VT_ARRAY, pc.VT_R8, pc.VT_DISPATCH = 0x2000, 5, 9
    pc.CoInitialize = lambda: None
    wc = types.ModuleType("win32com.client")
    wc.VARIANT = lambda _t, v: list(v)
    wc.GetActiveObject = lambda _name: app
    wc.CastTo = lambda e, _iface: e
    wc.dynamic = types.SimpleNamespace(Dispatch=lambda o: o)
    w = types.ModuleType("win32com")
    w.client = wc
    names = ("pythoncom", "win32com", "win32com.client")
    saved = {n: sys.modules.get(n) for n in names}
    sys.modules.update({"pythoncom": pc, "win32com": w, "win32com.client": wc})
    try:
        yield
    finally:
        for n, m in saved.items():
            if m is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = m


def load_acad_script(name, app):
    """Import an AutoCAD script (villa_3d_build, villa_window_check, ...)
    against the fake: fresh, so it binds the fake modules."""
    with fake_com(app):
        sys.modules.pop(name, None)
        return importlib.import_module(name)


def acad_layers(doc):
    """{layer: [shape]} of the 3D solids in a (fake) drawing."""
    out = {}
    for e in doc.ModelSpace:
        if e.ObjectName == "AcDb3dSolid" and e.shape is not None:
            out.setdefault(e.Layer, []).append(e.shape)
    return out


# ================================================================ models
_CACHE = {}


def gltf_groups():
    """villa_gltf's model as main() builds it (building + boundary, then
    the landscape), once per process."""
    if "gltf" not in _CACHE:
        g = GL.building()
        g["boundary"] = GL.boundary()
        land = GL.landscape()
        _CACHE["gltf"] = (g, land)
    return _CACHE["gltf"]


def acad_model():
    """villa_3d_build.run() on the fake AutoCAD: (module, app, doc)."""
    if "acad" not in _CACHE:
        app = FakeAcad()
        B = load_acad_script("villa_3d_build", app)
        B.run()
        _CACHE["acad"] = (B, app, app.doc(os.path.basename(B.DWG)))
    return _CACHE["acad"]


def inside_any(shapes, x, y, z):
    return any(s is not None and s.is_inside(Vector(x, y, z)) for s in shapes)


# ============================================================= the helpers
class Helpers(unittest.TestCase):
    """villa_geom's design-groups -> parts helpers, read once for both."""

    def test_part_is_empty(self):
        from shapely.geometry import Polygon, box as _b
        self.assertTrue(G.part_is_empty({"poly": Polygon(), "z": (0, 100)}))
        self.assertTrue(G.part_is_empty({"poly": _b(0, 0, 10, 10), "z": (100, 100)}))
        self.assertFalse(G.part_is_empty({"poly": _b(0, 0, 10, 10), "z": (0, 100)}))
        self.assertFalse(G.part_is_empty((0, 0, 0, 1, 1, 1)))
        self.assertFalse(G.part_is_empty({"yz": [(0, 0), (1, 0), (1, 1)], "x": (0, 1)}))

    def test_building_parts_follow_massing(self):
        m = G.massing()
        bp = G.building_parts()
        if m is None:
            self.assertIsNone(bp)
            return
        self.assertIsNotNone(bp)
        want = {g for g, ops in m.items()
                if any(op == "add" and not G.part_is_empty(p) for op, p in ops)}
        self.assertEqual(set(bp), want | ({"base"} if V.external_steps() else set()))
        steps = [tuple(b) for b in V.external_steps()]
        for g, ops in bp.items():
            kinds = [op for op, _ in ops]
            body = ops[:len(ops) - (len(steps) if g == "base" else 0)]
            # adds first, then cuts (union(adds) - union(cuts))
            first_cut = next((i for i, (op, _) in enumerate(body) if op == "cut"), len(body))
            self.assertTrue(all(op == "add" for op, _ in body[:first_cut]), g)
            self.assertTrue(all(op == "cut" for op, _ in body[first_cut:]), g)
            self.assertTrue(set(kinds) <= {"add", "cut"})
            src = m.get(g, [])
            for op in ("add", "cut"):
                n_src = sum(1 for o, p in src if o == op and not G.part_is_empty(p))
                n_bp = sum(1 for o, _ in body if o == op)
                self.assertEqual(n_src, n_bp, f"{g} {op}")
            self.assertFalse(any(G.part_is_empty(p) for _, p in ops), g)

    def test_site_parts_follow_landscape(self):
        L = G.landscape_parts()
        sp = G.site_parts()
        if L is None:
            self.assertIsNone(sp)
            return
        self.assertEqual(set(sp), {g for g, ps in L.items()
                                   if any(not G.part_is_empty(p) for p in ps)})
        for g, ps in sp.items():
            self.assertEqual(len(ps), sum(1 for p in L[g] if not G.part_is_empty(p)), g)

    def test_water_parts(self):
        wp = G.water_parts()
        pool = list(V.pool_parts()[2])
        if hasattr(V, "RILL_W"):
            self.assertEqual(len(wp), 1 + len(pool))
            x0, y0, z0, x1, y1, z1 = wp[0]
            self.assertAlmostEqual(x1 - x0, V.RILL_W)
            self.assertAlmostEqual(z1 - z0, 75.0)
            self.assertEqual(wp[1:], pool)
        else:
            self.assertEqual(wp, pool)

    def test_layers(self):
        """Every building group has an A-*-3D layer of its own, and the
        AutoCAD builder's own table agrees with villa_geom's."""
        names = list(GL.FABRIC) + ["stone"]
        layers = [G.layer_3d(g)[0] for g in names]
        self.assertEqual(len(set(layers)), len(layers))
        self.assertTrue(all(l.startswith("A-") and l.endswith("-3D") for l in layers))
        self.assertEqual(G.layer_3d("stone"), ("A-STON-3D", 250))
        self.assertEqual(G.WALL_LAYERS_3D, ("A-WALL-3D", "A-STON-3D", "A-BASE-3D"))
        with open(os.path.join(ROOT, "villa_3d_build.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        consts = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                  and n.targets[0].id in ("BUILD_LAYER", "MASS_KEY")}
        key_of = {"walls": "WALL", "slabs": "SLAB", "roof": "ROOF", "base": "BASE",
                  "fins": "SHADE", "pool": "POOL", "boundary": "BDRY", "grate": "GRAT",
                  "guards": "GRDS", "stair": "STAIR", "rails": "RAIL"}
        for g, k in key_of.items():
            self.assertEqual(tuple(consts["BUILD_LAYER"][k]), G.LAYER_3D[g], g)
        for g, k in consts["MASS_KEY"].items():
            self.assertEqual(consts["BUILD_LAYER"].get(k, G.layer_3d(g)), G.layer_3d(g))


# ============================================================ the glTF model
class GltfModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.groups, cls.land = gltf_groups()

    def test_probes(self):
        self.assertTrue(GL.verify(self.groups), "the glTF model fails its probes")

    def test_path_taken(self):
        """Massing / landscape hooks -> massed() / site parts; none (the
        villa) -> the legacy stacked() / surfaces(), exactly as before."""
        calls = []
        saved = (GL.stacked, GL.massed, GL.surfaces)
        GL.stacked = lambda *a: calls.append("stacked") or saved[0](*a)
        GL.massed = lambda *a: calls.append("massed") or saved[1](*a)
        GL.surfaces = lambda *a: calls.append("surfaces") or saved[2](*a)
        try:
            b = GL.building()
            GL.landscape()
        finally:
            GL.stacked, GL.massed, GL.surfaces = saved
        if G.massing() is None:
            self.assertEqual(calls, ["stacked", "surfaces"])
            self.assertEqual(list(b), ["walls", "slabs", "base", "roof", "fins", "pool",
                                       "frames", "grate", "guards", "stair", "rails"])
        else:
            self.assertEqual(calls[0], "massed")
            self.assertNotIn("stacked", calls)
            self.assertEqual(list(b)[:len(G.building_parts())], list(G.building_parts()))
        self.assertEqual("surfaces" in calls, G.landscape_parts() is None)

    def test_every_group_built(self):
        mass = G.building_parts() or {}
        site = G.site_parts() or {}
        for g in list(mass) + ["fins", "pool", "frames", "guards", "stair", "rails",
                               "boundary"]:
            s = self.groups.get(g)
            self.assertIsNotNone(s, g)
            self.assertGreater(s.volume, 1.0, g)
        for g in list(site) + ["glass", "water"]:
            s = self.land.get(g)
            self.assertIsNotNone(s, g)
            self.assertGreater(s.volume, 1.0, g)
        for s in list(self.groups.values()) + list(self.land.values()):
            self.assertFalse(s is not None and GL.placed(s))

    def test_water(self):
        w = self.land["water"]
        bb = w.bounding_box()
        if hasattr(V, "RILL_W"):
            # the rill runs on to the wings: water beyond the pool's end
            self.assertGreater(bb.max.Y, V.POOL_Y1 + 100)
        else:
            self.assertAlmostEqual(bb.min.X, V.POOL_X0, delta=1)
            self.assertAlmostEqual(bb.max.X, V.POOL_X1, delta=1)
            self.assertAlmostEqual(bb.max.Y, V.POOL_Y1, delta=1)
            self.assertAlmostEqual(bb.max.Z, V.POOL_TW, delta=1)
            if hasattr(V, "pool_volume"):
                self.assertAlmostEqual(w.volume / 1e9, V.pool_volume(), delta=0.01)

    def test_colours(self):
        mats = getattr(V, "MATERIALS", None)
        for g in list(self.groups) + list(self.land):
            c = GL.colour(g)
            self.assertEqual(len(c), 3)
            if mats and g in mats:
                self.assertEqual(c, tuple(float(v) for v in mats[g]["color"][:3]))
            else:
                self.assertEqual(c, GL.COLOURS.get(g, (0.8, 0.8, 0.8)))


@unittest.skipUnless(PROJECT == "fairway", "the Fairway project only")
class FairwayModel(unittest.TestCase):
    """The Fairway through the hooks: basement below grade, stone skin,
    the forecourt ramp, the pool without a rill."""

    @classmethod
    def setUpClass(cls):
        cls.groups, cls.land = gltf_groups()

    def ins(self, g, x, y, z):
        s = self.groups.get(g) or self.land.get(g)
        return s is not None and s.is_inside(Vector(x, y, z))

    def test_groups(self):
        self.assertEqual(list(G.building_parts()), ["base", "slabs", "walls", "roof", "stone"])
        self.assertEqual(set(G.site_parts()), {"terrain", "paving", "deck", "lawn",
                                               "planting", "gravel", "drive"})
        self.assertIsNone(self.groups.get("grate"))          # no basin, no grate

    def test_basement_below_grade(self):
        bb = self.groups["base"].bounding_box()
        self.assertAlmostEqual(bb.max.Z, V.GF - V.SLAB, delta=1)   # -300: under the GF slab
        self.assertLessEqual(bb.max.Z, 0.0)
        self.assertAlmostEqual(bb.min.Z, V.B1 - V.SLAB, delta=1)   # -4300
        E = V.envelope()
        x, y = G._pt(E["out_b1"].difference(E["in_b1"]))
        self.assertTrue(self.ins("base", x, y, V.B1 + 1500))            # its wall
        self.assertTrue(self.ins("base", 14000, 19000, V.B1 - V.SLAB / 2))   # its slab
        for g in ("base", "slabs", "walls", "stone"):                   # a room open
            self.assertFalse(self.ins(g, 14000, 19000, V.B1 + 1500), g)
        self.assertFalse(self.ins("terrain", 14000, 19000, -150))       # no earth in it

    def test_levels(self):
        self.assertTrue(self.ins("slabs", 21000, 19000, V.GF - 50))      # GF slab top +200
        self.assertFalse(self.ins("slabs", 21000, 19000, V.GF + 50))
        self.assertAlmostEqual(self.groups["roof"].bounding_box().max.Z,
                               V.RF + V.SLAB + V.PARAPET, delta=1)     # parapet +8900
        self.assertTrue(self.ins("roof", 10000, 20000, V.RF + V.SLAB - 50))   # roof +8500
        self.assertFalse(self.ins("roof", 10000, 20000, V.RF + V.SLAB + 50))

    def test_stone_skin(self):
        x = V.HX1 - V.STONE_SKIN / 2
        self.assertTrue(self.ins("stone", x, 32000, V.GF + 1200))
        self.assertFalse(self.ins("walls", x, 32000, V.GF + 1200))
        self.assertTrue(self.ins("walls", x - V.STONE_SKIN, 32000, V.GF + 1200))
        bb = self.groups["walls"].bounding_box()
        self.assertAlmostEqual(bb.max.X, V.HX1 - V.STONE_SKIN, delta=1)
        # every east-face opening is cut through the stone as well
        for o in V.OPENINGS:
            if o[2] == "v" and o[8] is None and max(o[3], o[4]) >= V.HX1 - 1:
                x0, y0, z0, x1, y1, z1 = G.cut_box(o)
                self.assertFalse(self.ins("stone", x, (y0 + y1) / 2, (z0 + z1) / 2), o[7])

    def test_forecourt_ramp(self):
        for y, want in ((V.RAMP_Y0, V.GF), ((V.RAMP_Y0 + V.RAMP_Y1) / 2, 100.0),
                        (V.RAMP_Y1 - 1, 0.0), (V.GF_Y1 + 500, V.GF)):
            z = V.ramp_z(y)
            self.assertAlmostEqual(z, want, delta=0.1)
            self.assertTrue(self.ins("drive", 5000, y, z - 5), y)
            self.assertFalse(self.ins("drive", 5000, y, z + 5), y)
            self.assertTrue(self.ins("terrain", 5000, y, z - 60), y)
        self.assertAlmostEqual(V.ramp_z(V.RAMP_Y1), 0.0)
        # the terrain beyond the gate line is level with the street
        self.assertTrue(self.ins("terrain", 5000, V.PLOT_D - 100, -60))
        self.assertFalse(self.ins("terrain", 5000, V.PLOT_D - 100, -20))

    def test_no_rill(self):
        self.assertFalse(hasattr(V, "RILL_W"))
        self.assertEqual(G.water_parts(), list(V.pool_parts()[2]))


@unittest.skipUnless(IS_VILLA, "the villa only")
class VillaLegacy(unittest.TestCase):
    """The villa has neither hook: the legacy path, unchanged."""

    def test_no_hooks(self):
        self.assertIsNone(G.massing())
        self.assertIsNone(G.landscape_parts())
        self.assertIsNone(G.building_parts())
        self.assertIsNone(G.site_parts())
        self.assertFalse(hasattr(V, "MATERIALS"))
        self.assertTrue(hasattr(V, "RILL_W"))
        groups, _land = gltf_groups()
        self.assertNotIn("stone", groups)


# =========================================================== the AutoCAD model
class AcadModel(unittest.TestCase):
    """villa_3d_build.run() on the fake AutoCAD: the same groups as the glTF
    model, layer by layer, with the same volume and bounds -- and the same
    probes, window probes and pool levels pass on it."""

    @classmethod
    def setUpClass(cls):
        cls.groups, cls.land = gltf_groups()
        cls.B, cls.app, cls.doc = acad_model()
        cls.layers = acad_layers(cls.doc)

    def _pairs(self):
        """(glTF group, AutoCAD layer) for every group both builders make
        (window frames are glTF only)."""
        out = []
        for g in self.groups:
            if g != "frames":
                out.append((g, G.layer_3d(g)[0], self.groups[g]))
        for g in self.land:
            out.append((g, G.site_layer(g), self.land[g]))
        return out

    def test_same_groups(self):
        want = {lay for g, lay, s in self._pairs() if s is not None}
        got = {lay for lay in self.layers if lay.startswith(("A-", "L-"))}
        self.assertEqual(got, want)
        if G.building_parts() is not None:
            for g in G.building_parts():
                self.assertIn(G.layer_3d(g)[0], got, g)

    def test_same_volume_and_bounds(self):
        for g, lay, s in self._pairs():
            if s is None:
                continue
            shapes = self.layers.get(lay, [])
            vol = sum(x.volume for x in shapes)
            self.assertAlmostEqual(vol / 1e9, s.volume / 1e9, delta=max(1e-3, 1e-4 * s.volume / 1e9),
                                   msg=f"{g} / {lay}")
            bbs = [x.bounding_box() for x in shapes]
            lo = (min(b.min.X for b in bbs), min(b.min.Y for b in bbs), min(b.min.Z for b in bbs))
            hi = (max(b.max.X for b in bbs), max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))
            bb = s.bounding_box()
            for a, b in zip(lo + hi, (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)):
                self.assertAlmostEqual(a, b, delta=1.0, msg=f"{g} / {lay} bounds")

    def test_probes(self):
        """villa_3d_verify's questions (G.probes, G.controls on every A-*-3D
        layer), asked at the probe's centre."""
        model = [s for lay, ss in self.layers.items()
                 if lay.startswith("A-") and lay.endswith("-3D") for s in ss]
        bad = []
        for name, x, y, z, expect, _r in G.probes():
            if inside_any(model, x, y, z) != (expect == "solid"):
                bad.append(name)
        for name, x, y, z, _r in G.controls():
            if not inside_any(model, x, y, z):
                bad.append(f"control {name}")
        self.assertEqual(bad, [])

    def test_window_probes(self):
        """villa_window_check's probe points: every opening clear of every
        wall-like layer (walls, stone skin, basement walls), at its centre
        and just inside each face."""
        WC = load_acad_script("villa_window_check", self.app)
        self.assertEqual(WC.WALL_LAYERS, G.WALL_LAYERS_3D)
        walls = [s for lay in WC.WALL_LAYERS for s in self.layers.get(lay, [])]
        pts = WC.probe_points()
        # centre, the floor (not a window), and one just inside each face
        self.assertEqual(len(pts), sum((1 if o[1] == V.WIN else 2) + 2 for o in V.OPENINGS))
        bad = [tag for tag, x, y, z, _r in pts if inside_any(walls, x, y, z)]
        self.assertEqual(bad, [])
        # and a face probe does find a skin left standing: stone, where a
        # design has it, is solid 5 mm inside the face beside an opening
        if "A-STON-3D" in self.layers:
            o = next(o for o in V.OPENINGS if o[2] == "v" and o[8] is None
                     and max(o[3], o[4]) >= V.HX1 - 1)
            x0, y0, z0, x1, y1, z1 = G.cut_box(o)
            self.assertTrue(inside_any(self.layers["A-STON-3D"], x1 - 25, y1 + 300, (z0 + z1) / 2))

    def test_pool_levels(self):
        """villa_pool_check's levels: water where it wants water and nothing
        else in the way; none above top-water level."""
        PC = load_acad_script("villa_pool_check", self.app)
        levels = PC.pool_levels()
        self.assertEqual([n for n, *_ in levels][:4],
                         ["pool floor +100", "mid depth", "just below TW", "above the water"])
        self.assertEqual(len(levels), 5 if getattr(V, "POOL_LEDGE", None) else 4)
        water = self.layers.get("L-WATER", [])
        others = [s for lay, ss in self.layers.items() if lay != "L-WATER" for s in ss]
        for name, x, y, z, r, want in levels:
            self.assertEqual(inside_any(water, x, y, z), want, name)
            self.assertFalse(inside_any(others, x, y, z), name)
            if want:        # the sphere's poles too: nothing but water
                for dz in (-r, r):
                    self.assertFalse(inside_any(others, x, y, z + 0.98 * dz), f"{name} {dz}")
        self.assertEqual(PC.extra_water(), [n for n, a in (("basin", "BASIN_Y0"),
                                                           ("rill", "RILL_W")) if hasattr(V, a)])


SPHERES = os.environ.get("VILLA_TEST_SPHERES") == "1"


class AcadScriptsDryRun(unittest.TestCase):
    """The AutoCAD check scripts' own main(), run on the fake AutoCAD with
    their sphere-interference probes (a sphere's interference is sampled,
    see sampled_volume). The pool check always; villa_3d_verify and
    villa_window_check (a minute or two each) with VILLA_TEST_SPHERES=1."""

    @classmethod
    def setUpClass(cls):
        cls.B, cls.app, cls.doc = acad_model()

    def main_of(self, name):
        import io
        buf = io.StringIO()
        M = load_acad_script(name, self.app)
        with contextlib.redirect_stdout(buf):
            M.main()
        return buf.getvalue()

    def test_pool_check(self):
        out = self.main_of("villa_pool_check")
        self.assertIn("VERIFIED: the pool holds water to top-water level", out, out)

    @unittest.skipUnless(SPHERES, "set VILLA_TEST_SPHERES=1")
    def test_3d_verify(self):
        out = self.main_of("villa_3d_verify")
        self.assertIn("VERIFIED: every void is open and every solid probe is solid", out, out)

    @unittest.skipUnless(SPHERES, "set VILLA_TEST_SPHERES=1")
    def test_window_check(self):
        out = self.main_of("villa_window_check")
        self.assertIn("VERIFIED: every opening is a real hole", out, out)


# ================================================== the other design, too
@unittest.skipUnless(IS_VILLA, "run from the villa: it spawns the Fairway")
class FairwayProject(unittest.TestCase):

    def test_fairway_in_its_own_process(self):
        out = os.path.join(tempfile.gettempdir(), "fairway_project_3d_test")
        env = dict(os.environ, VILLA_OUT=out, PYTHONPATH="")
        env.pop("VILLA_DESIGN_DIR", None)
        r = subprocess.run([PY, "-X", "utf8", os.path.join(ROOT, "run_project.py"),
                            "fairway", os.path.abspath(__file__)],
                           cwd=ROOT, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=3600)
        tail = (r.stdout[-4000:] + "\n" + r.stderr[-6000:])
        print("\n---- Fairway (subprocess) ----\n" + r.stderr[-3000:])
        self.assertEqual(r.returncode, 0, tail)
        self.assertIn("OK", r.stderr)


def suite():
    loader = unittest.TestLoader()
    return unittest.TestSuite(loader.loadTestsFromTestCase(c) for c in (
        Helpers, GltfModel, FairwayModel, VillaLegacy, AcadModel, AcadScriptsDryRun,
        FairwayProject))


if __name__ == "__main__":
    print(f"design {V.__file__}\nVILLA_OUT = {G.out_dir()}", flush=True)
    res = unittest.TextTestRunner(verbosity=2).run(suite())
    sys.exit(0 if res.wasSuccessful() else 1)
