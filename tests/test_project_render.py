"""Offline tests for the render track's project hooks (Blender + Unreal).

    python -X utf8 tests\\test_project_render.py

Mostly without Blender or Unreal: villa_blender.py and unreal\\build_scene.py
are imported in plain Python with stand-in bpy / bmesh / mathutils / unreal
modules, so their data paths -- which design, which folders, which views,
which materials -- are tested without either program. Two tests run
Blender itself when it is installed (skipped otherwise): the villa's
material node graphs against the pre-projects code, and the Fairway's stone
roughness nodes. render_unreal.ps1 is run for real with -Stage paths (it
starts nothing).

What is proved:
  * paths: VILLA_DESIGN_DIR picks the design villa_blender imports (the
    Fairway's with it, the villa's without); VILLA_OUT moves every output
    (render\\, out\\, twinmotion\\, the unpacked-texture cache) and nothing
    else; the downloaded assets stay put unless VILLA_ASSETS says otherwise;
    build_scene.py takes the model, groups, logs, content folder, queue
    manifest and design from VILLA_OUT / VILLA_DESIGN_DIR;
  * views: a design's RENDER_VIEWS are the default views, as cameras with
    their eye / target / lens / sun (and interior flag), two-point below
    3 m; build_scene.py makes the same cameras, with the eye and date
    villa_blender.py rendered when its views.json is there, and a Dubai date
    whose sun is the design's (az, el); the villa keeps its typed views,
    exactly as the pre-projects code had them;
  * materials: ASSIGN (villa_blender and build_scene) is a literal covering
    every glTF group of BOTH designs; every MATERIALS kind of the Fairway has
    a Blender recipe and an Unreal mapping; the villa's ASSIGN is the
    pre-projects one plus 'stone' only;
  * context: the neighbours stand at the Fairway's own setbacks, the
    villa's at the numbers it always rendered with; the golf bands tile the
    course with no gap, the same in both renderers;
  * a project never falls back to the villa's Desktop\\Villa (Blender,
    build_scene.py and render_unreal.ps1 all pick Desktop\\<OUT_NAME>, as
    run_project.py does); villa_blender refuses a project folder without its
    own villa_design.py, a design imported from elsewhere, and a project
    VILLA_OUT that is the villa's folder; the VILLA keeps its pre-projects
    Desktop\\Villa\\render whatever VILLA_OUT says, unless
    VILLA_RENDER_FOLLOWS_OUT=1;
  * colour: fit_tint (the same in both renderers) brings a texture set to
    the design's colour on average -- the lawn too, which the old x4 clamp
    missed -- leaves every in-range tint as it was, flags a colour it cannot
    reach, and keeps the golf course's three shades distinct;
  * Unreal: an interior cut dims the room lights to villa_blender's
    INTERIOR_LIGHTS (keyed per cut) and balances for the lamps; no shrubs
    under a clipped hedge; the villa's build report keeps its old keys;
  * lights: the villa's room lights hang exactly where the pre-projects code
    hung them (the annex fix is opt-in, VILLA_ANNEX_LIGHT_FIX=1); a design's
    under its own storey's ceiling;
  * eyes: walk_clear reports clear / moved / blocked, never a silent 0;
  * the Unreal room test of a design knows nested rooms, openings and voids
    (synthetic walls), and still rejects a wall the design does not have;
  * roughness: a design's MATERIALS roughness is the surface's in both
    renderers (rough_fit, the same in both): over the real Travertine001 map
    the Fairway's limestone paving / coping and stair average their design
    value with no gloss patches (the old rules: a mirror in Unreal, a
    quarter of each slab under 0.35 in Blender); Unreal's instances carry
    the fit, the stacked stone is the stone recipe, and the villa's Unreal
    instances and Blender node graphs are the pre-projects ones;
  * parity dressing: the interior floor plan is the same in both renderers;
    merge_glb (the palms imported with the model) keeps both files'
    triangles; exterior camera cuts dim the room lights as Blender does;
  * the server's render guard lets the Fairway through only because
    villa_blender really imports the design VILLA_DESIGN_DIR names.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FAIRWAY = os.path.join(ROOT, "projects", "fairway")
VB = os.path.join(ROOT, "villa_blender.py")
VB_ORIG = os.path.join(ROOT, "_pre_projects_0926", "villa_blender.py")
BS = os.path.join(ROOT, "unreal", "build_scene.py")
DESKTOP_VILLA = r"C:\Users\lsire\OneDrive\Desktop\Villa"
ENV_KEYS = ("VILLA_DESIGN_DIR", "VILLA_OUT", "VILLA_ASSETS", "VILLA_UE_GLB", "VILLA_UE_GROUPS",
            "VILLA_UE_TEX", "VILLA_UE_VIEWS", "VILLA_UE_FRAMES", "VILLA_UE_STATUS",
            "VILLA_UE_ROOT", "VILLA_UE_DESIGN", "VILLA_ANNEX_LIGHT_FIX", "VILLA_RENDER_FOLLOWS_OUT",
            "VILLA_UE_EV_INTERIOR", "VILLA_UE_INTERIOR_CUT", "VILLA_UE_INTERIOR_WB",
            "VILLA_UE_WATER_SCATTER")
# Grass001 as villa_blender measured it (materials.json): linear average and
# 99th percentile of the colour map
GRASS_AVG = (0.0612, 0.1104, 0.0229)
GRASS_HI = (0.147, 0.227, 0.0497)
TMP = os.path.join(tempfile.gettempdir(), "villa_project_render_test")


@contextlib.contextmanager
def environment(**env):
    """Exactly these pipeline variables set (others removed); sys.path,
    sys.modules' villa_design and the stubs restored afterwards."""
    saved_env = {k: os.environ.get(k) for k in ENV_KEYS}
    saved_path = list(sys.path)
    saved_mods = {k: sys.modules.get(k) for k in ("villa_design", "bpy", "bmesh", "mathutils",
                                                  "mathutils.bvhtree", "unreal")}
    for k in ENV_KEYS:
        os.environ.pop(k, None)
    os.environ.update({k: v for k, v in env.items() if v is not None})
    sys.modules.pop("villa_design", None)
    for name in ("bpy", "bmesh", "unreal"):
        sys.modules[name] = mock.MagicMock(name=name)
    mu = types.ModuleType("mathutils")
    mu.Matrix, mu.Vector = mock.MagicMock(), mock.MagicMock()
    sys.modules["mathutils"] = mu
    try:
        yield
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        sys.path[:] = saved_path
        for k, v in saved_mods.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blender(**env):
    with environment(**env):
        return load(VB, "villa_blender_under_test")


def unreal_build(**env):
    with environment(**env):
        return load(BS, "build_scene_under_test")


def source(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def literal(path, name):
    tree = ast.parse(source(path))
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and getattr(n.targets[0], "id", "") == name)
    return ast.literal_eval(node.value)


def run_ps1(stage, **env):
    """render_unreal.ps1 -Stage <stage> with exactly these pipeline
    variables set (the others removed)."""
    e = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    e.update(env)
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                           os.path.join(ROOT, "unreal", "render_unreal.ps1"), "-Stage", stage],
                          env=e, capture_output=True, text=True, timeout=120)


def ps1_paths(**env):
    r = run_ps1("paths", **env)
    if r.returncode != 0:
        raise AssertionError(f"render_unreal.ps1 -Stage paths failed: {r.stdout}{r.stderr}")
    return json.loads(r.stdout.strip().splitlines()[-1])


# Roughness maps as villa_blender measures them (tex_rough_stats; the
# Fairway's materials.json '_roughness_stats'): mean, standard deviation
ROUGH_STATS = {"Travertine001": (0.02633, 0.01639), "WoodFloor040": (0.60373, 0.02484),
               "Concrete034": (0.51612, 0.02464), "Grass001": (0.54404, 0.08715),
               "Gravel023": (0.46752, 0.05062), "Ground054": (0.66544, 0.05238),
               "Tiles107": (0.05358, 0.1372)}
TEX_DIR = os.path.join(DESKTOP_VILLA, "render", "materials", "_tex")


def roughness_map(asset):
    """An ambientCG set's roughness map (first channel, 0..1), or None when
    numpy / PIL / the unpacked set is not here."""
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None
    p = os.path.join(TEX_DIR, asset, f"{asset}_2K-JPG_Roughness.jpg")
    if not os.path.exists(p):
        return None
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)[..., 0] / 255.0


def blender_exe():
    exe = os.environ.get("BLENDER_EXE") or r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    return exe if os.path.exists(exe) else None


def villa_groups():
    """Every group villa_gltf.py can export for the villa: its FABRIC and
    NOT_FABRIC lists (the builder's own inventory)."""
    src = os.path.join(ROOT, "villa_gltf.py")
    return set(literal(src, "FABRIC")) | set(literal(src, "NOT_FABRIC"))


_FW = {}


def fairway_design():
    """The Fairway's villa_design, imported under its own name (shapely is
    fine here: this is plain Python)."""
    if "V" not in _FW:
        saved = list(sys.path)
        sys.path.insert(0, FAIRWAY)
        try:
            _FW["V"] = load(os.path.join(FAIRWAY, "villa_design.py"), "fairway_design_under_test")
        finally:
            sys.path[:] = saved
    return _FW["V"]


def fairway_groups():
    """The Fairway's glTF groups: its massing() and landscape_parts() groups
    plus the ones every design is built with (fittings, boundary, infill,
    water) -- villa_gltf's inventory."""
    V = fairway_design()
    return set(V.massing()) | set(V.landscape_parts()) | villa_groups()


class Paths(unittest.TestCase):
    def test_project_design_and_outputs_follow_the_environment(self):
        out = os.path.join(TMP, "fw")
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)
        self.assertEqual(getattr(B.V, "PROJECT", None), "fairway")
        self.assertEqual(os.path.normcase(B.DESIGN_DIR), os.path.normcase(FAIRWAY))
        self.assertEqual(B.RENDER, os.path.join(out, "render"))
        self.assertEqual(B.OUT, os.path.join(out, "render", "out"))
        self.assertEqual(B.TM, os.path.join(out, "render", "twinmotion"))
        self.assertEqual(B.TEX_CACHE, os.path.join(out, "render", "materials", "_tex"))
        # the downloads stay where they were fetched
        self.assertEqual(B.MATS, os.path.join(DESKTOP_VILLA, "render", "materials"))
        self.assertEqual(B.HDRI, os.path.join(DESKTOP_VILLA, "render", "hdri"))

    def test_assets_override(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP, VILLA_ASSETS=r"D:\assets")
        self.assertEqual(B.MATS, os.path.join(r"D:\assets", "materials"))
        self.assertEqual(B.TEX, os.path.join(r"D:\assets", "materials", "_tex"))
        self.assertEqual(B.HDRI, os.path.join(r"D:\assets", "hdri"))

    def test_project_without_villa_out_goes_to_its_own_folder(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY)
        self.assertEqual(B.RENDER, os.path.join(r"C:\Users\lsire\OneDrive\Desktop", "Fairway", "render"))

    def test_villa_paths_are_the_old_constants(self):
        B = blender()
        self.assertFalse(hasattr(B.V, "PROJECT"))
        self.assertEqual(B.RENDER, os.path.join(DESKTOP_VILLA, "render"))
        self.assertEqual(B.TEX, B.TEX_CACHE)      # the villa unpacks where it always did
        self.assertEqual(B.OUT, os.path.join(DESKTOP_VILLA, "render", "out"))

    def test_villa_ignores_villa_out_unless_opted_in(self):
        # the pre-projects villa_blender always used Desktop\Villa\render;
        # server.py now hands VILLA_OUT to every stage, so honouring it for
        # the villa is opt-in (VILLA_RENDER_FOLLOWS_OUT=1) until approved
        out = os.path.join(TMP, "villa_out")
        B = blender(VILLA_OUT=out)
        with environment():
            old = load(VB_ORIG, "villa_blender_orig_paths")
        for k in ("RENDER", "MATS", "TEX", "HDRI", "OUT", "TM"):
            self.assertEqual(getattr(B, k), getattr(old, k), k)
        self.assertEqual(B.TEX, B.TEX_CACHE)
        B = blender(VILLA_OUT=out, VILLA_RENDER_FOLLOWS_OUT="1")
        self.assertEqual(B.RENDER, os.path.join(out, "render"))
        self.assertEqual(B.OUT, os.path.join(out, "render", "out"))
        self.assertEqual(B.MATS, os.path.join(DESKTOP_VILLA, "render", "materials"))   # downloads stay

    def test_project_without_its_own_design_is_refused(self):
        d = os.path.join(TMP, "nodesign")
        os.makedirs(d, exist_ok=True)
        with contextlib.suppress(FileNotFoundError):
            os.remove(os.path.join(d, "villa_design.py"))
        with self.assertRaisesRegex(RuntimeError, "has no villa_design.py"):
            blender(VILLA_DESIGN_DIR=d, VILLA_OUT=TMP)

    def test_project_into_the_villa_folder_is_refused(self):
        for out in (DESKTOP_VILLA, DESKTOP_VILLA + "\\", DESKTOP_VILLA.lower()):
            with self.assertRaisesRegex(RuntimeError, "villa's deliverables"):
                blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)

    def test_a_design_imported_from_elsewhere_is_refused(self):
        # a villa_design already imported (from the villa) must not stand in
        # for the project's
        with environment(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP):
            sys.modules["villa_design"] = load(os.path.join(ROOT, "villa_design.py"), "villa_design")
            with self.assertRaisesRegex(RuntimeError, "not the design in"):
                load(VB, "villa_blender_stale_design")

    def test_unreal_paths_from_villa_out_and_design_dir(self):
        out = os.path.join(TMP, "fw")
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)
        self.assertEqual(U.GLB, os.path.join(out, "render", "twinmotion", "villa_twinmotion.glb"))
        self.assertEqual(U.GROUPS, os.path.join(out, "render", "groups.json"))
        self.assertEqual(U.TEX_DIRS[0], os.path.join(out, "render", "materials", "_tex"))
        self.assertIn(os.path.join(DESKTOP_VILLA, "render", "materials", "_tex"), U.TEX_DIRS)
        self.assertEqual(U.DESIGN, os.path.join(FAIRWAY, "villa_design.py"))
        self.assertEqual(U.ROOT, "/Game/Fairway")
        self.assertEqual(U.MAP, "/Game/Fairway/Maps/Villa")
        self.assertEqual(U.TEXP, "/Game/Villa/Textures")          # shared library
        self.assertEqual(U.LOGS, os.path.join(ROOT, "unreal", "logs", "fairway"))
        self.assertEqual(U.STATUS, os.path.join(U.LOGS, "build_status.json"))
        self.assertEqual(U.MANIFEST, "QueueManifest_fairway.utxt")

    def test_unreal_villa_defaults_unchanged(self):
        U = unreal_build()
        self.assertEqual(U.GLB, os.path.join(DESKTOP_VILLA, "render", "twinmotion",
                                             "villa_twinmotion.glb"))
        self.assertEqual(U.GROUPS, "")
        self.assertEqual(U.ROOT, "/Game/Villa")
        self.assertEqual(U.MANIFEST, "QueueManifest.utxt")
        self.assertEqual(U.STATUS, os.path.join(ROOT, "unreal", "logs", "build_status.json"))
        self.assertEqual(U.DESIGN, os.path.join(ROOT, "villa_design.py"))
        self.assertIs(U.all_views(), U.VIEWS)

    def test_unreal_project_without_villa_out_never_uses_the_villa_folder(self):
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY)
        fw = os.path.join(r"C:\Users\lsire\OneDrive\Desktop", "Fairway")
        self.assertEqual(U.OUT_ROOT, fw)                          # OUT_NAME, as run_project.py
        self.assertEqual(U.GLB, os.path.join(fw, "render", "twinmotion", "villa_twinmotion.glb"))
        self.assertEqual(U.GROUPS, os.path.join(fw, "render", "groups.json"))
        self.assertNotIn(os.path.normcase(DESKTOP_VILLA) + os.sep, os.path.normcase(U.GLB))
        # the same folder villa_blender.py and run_project.py pick
        B = blender(VILLA_DESIGN_DIR=FAIRWAY)
        self.assertEqual(B.BASE, U.OUT_ROOT)
        sys.path.insert(0, ROOT)
        try:
            import run_project
        finally:
            sys.path.remove(ROOT)
        self.assertEqual(os.path.join(run_project.DESKTOP, run_project.out_name(FAIRWAY)), fw)

    def test_project_without_out_name_uses_its_folder_name(self):
        d = os.path.join(TMP, "gardenia")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "villa_design.py"), "w", encoding="utf-8") as f:
            f.write("ROOMS = []\nPLOT_W = 20000.0\nPLOT_D = 30000.0\n")
        B = blender(VILLA_DESIGN_DIR=d)
        U = unreal_build(VILLA_DESIGN_DIR=d)
        want = os.path.join(r"C:\Users\lsire\OneDrive\Desktop", "Gardenia")
        self.assertEqual((B.BASE, U.OUT_ROOT), (want, want))

    def test_pipeline_folder_as_design_dir_is_the_villa(self):
        U = unreal_build(VILLA_DESIGN_DIR=ROOT)
        self.assertEqual((U.PROJECT, U.ROOT, U.MANIFEST), ("", "/Game/Villa", "QueueManifest.utxt"))
        self.assertEqual(U.OUT_ROOT, DESKTOP_VILLA)

    def test_render_unreal_ps1_paths_and_refusal(self):
        """render_unreal.ps1 run for real (-Stage paths starts nothing): a
        project without VILLA_OUT reads and writes Desktop\\<OUT_NAME> -- the
        folder build_scene.py and run_project.py pick -- under its own
        content root and logs; the villa keeps Desktop\\Villa and /Game/Villa;
        a project whose VILLA_OUT is the villa's folder is refused before
        anything starts."""
        if not shutil.which("powershell"):
            self.skipTest("no powershell")
        fw = os.path.join(r"C:\Users\lsire\OneDrive\Desktop", "Fairway")
        got = ps1_paths(VILLA_DESIGN_DIR=FAIRWAY)
        self.assertEqual(got["villa_root"], fw)
        self.assertEqual(got["glb"], os.path.join(fw, "render", "twinmotion", "villa_twinmotion.glb"))
        self.assertEqual(got["groups"], os.path.join(fw, "render", "groups.json"))
        self.assertEqual(got["out_dir"], os.path.join(fw, "render", "unreal"))
        self.assertEqual(got["content_root"], "/Game/Fairway")
        self.assertEqual(os.path.normcase(got["log_dir"]),
                         os.path.normcase(os.path.join(ROOT, "unreal", "logs", "fairway")))
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY)
        self.assertEqual((U.OUT_ROOT, U.GLB, U.ROOT), (fw, got["glb"], got["content_root"]))
        out = os.path.join(TMP, "ps1_out")
        got = ps1_paths(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)
        self.assertEqual(got["villa_root"], out)
        self.assertEqual(got["glb"], os.path.join(out, "render", "twinmotion", "villa_twinmotion.glb"))
        villa = ps1_paths()
        self.assertEqual((villa["villa_root"], villa["content_root"]), (DESKTOP_VILLA, "/Game/Villa"))
        self.assertEqual(os.path.normcase(villa["log_dir"]),
                         os.path.normcase(os.path.join(ROOT, "unreal", "logs")))
        for bad in (DESKTOP_VILLA, DESKTOP_VILLA + "\\"):
            r = run_ps1("paths", VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=bad)
            self.assertNotEqual(r.returncode, 0, bad)
            self.assertIn("would read and write the villa's deliverables", r.stdout + r.stderr)

    def test_server_render_guard_matches_what_villa_blender_does(self):
        """server.py refuses a project render unless villa_blender.py reads
        VILLA_DESIGN_DIR. It lets the Fairway's through -- and the environment
        it hands the render stage makes villa_blender import the Fairway's
        design and write into the project's folder, not the villa's."""
        try:
            sys.path.insert(0, ROOT)
            import server
            from mcp.server.mcpserver.exceptions import ToolError
        except Exception as e:                        # the MCP stack is not installed
            self.skipTest(f"server.py does not import here: {e}")
        finally:
            sys.path.remove(ROOT)
        if not server.BLENDER.exists():
            self.skipTest("Blender not installed")
        os.environ.setdefault("ACAD_AUDIT_LOG", "0")    # stay out of logs\mcp_calls.jsonl
        r = server.villa_run(stage="render", project="fairway", dry_run=True)
        self.assertNotIn("warning", r)
        self.assertTrue(any("villa_blender.py" in c for c in r["commands"]))
        env = {k: v for k, v in r["env"].items() if v is not None}
        env.setdefault("VILLA_OUT", os.path.join(TMP, "guard"))
        B = blender(**{k: v for k, v in env.items() if k in ENV_KEYS})
        self.assertEqual(os.path.normcase(os.path.dirname(os.path.abspath(B.V.__file__))),
                         os.path.normcase(FAIRWAY))
        self.assertEqual(B.V.PROJECT, "fairway")
        self.assertTrue(B.IS_PROJECT)
        self.assertNotIn(os.path.normcase(DESKTOP_VILLA) + os.sep, os.path.normcase(B.RENDER) + os.sep)
        # the guard itself: with a villa_blender that did NOT read the design
        # dir, the render is refused before anything starts
        old = server._mentions
        server._mentions = lambda *a: False
        try:
            with self.assertRaises(ToolError):
                server.villa_run(stage="render", project="fairway")
        finally:
            server._mentions = old


class Views(unittest.TestCase):
    def test_render_views_are_the_default_views(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        rv = B.V.RENDER_VIEWS
        with mock.patch.object(sys, "argv", ["blender"]):
            self.assertEqual(B.args()["views"], list(rv))
        views = B.views()
        self.assertEqual(set(views), set(rv))
        for name, v in rv.items():
            eye, tgt, lens, ortho, sun = views[name]
            self.assertEqual(eye, tuple(float(c) for c in v["eye"]), name)
            self.assertEqual(tgt, tuple(float(c) for c in v["target"]), name)
            self.assertEqual(lens, float(v["lens"]), name)
            self.assertIsNone(ortho)
            self.assertEqual(sun, tuple(float(c) for c in v["sun"]), name)
            s = B.view_setup(name)
            self.assertEqual(s["interior"], bool(v.get("interior")), name)
            self.assertEqual(s["level"], v["eye"][2] <= B.LEVEL_EYE_MAX, name)

    def test_a_dubai_date_for_every_sun(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        for name, v in B.V.RENDER_VIEWS.items():
            mo, dy, hm, err = B.sun_date(*v["sun"])
            self.assertLess(err, 1.0, name)
            az, el = B._sun_position(
                (__import__("datetime").date(2026, mo, dy) - __import__("datetime").date(2026, 1, 1)).days + 1,
                int(hm[:2]) + int(hm[3:]) / 60.0)
            self.assertLess(abs(el - v["sun"][1]), 1.0, name)

    def test_backlight_opens_up_only_into_the_sun(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        self.assertAlmostEqual(B.backlight((0, 0, 1), (-1, 0, 1), 270.0), B.BACKLIT_OPEN)
        self.assertEqual(B.backlight((0, 0, 1), (1, 0, 1), 270.0), 0.0)
        self.assertEqual(B.backlight((0, 0, 1), (0, 1, 1), 270.0), 0.0)

    def test_villa_views_are_the_pre_projects_views(self):
        new = blender()
        with environment():
            old = load(VB_ORIG, "villa_blender_orig_under_test")
        self.assertEqual(new.views(), old.views())
        with mock.patch.object(sys, "argv", ["blender"]):
            self.assertEqual(new.args(), old.args())

    def test_unreal_cameras_from_render_views(self):
        out = os.path.join(TMP, "ue")
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)
        rv = fairway_design().RENDER_VIEWS
        views = U.design_views()
        self.assertEqual(set(views), set(rv))
        for name, v in views.items():
            self.assertEqual(v["eye"], tuple(float(c) for c in rv[name]["eye"]), name)
            self.assertEqual(v["target"], tuple(float(c) for c in rv[name]["target"]), name)
            self.assertEqual(v["lens"], float(rv[name]["lens"]), name)
            self.assertEqual(v["interior"], bool(rv[name].get("interior")), name)
            self.assertEqual(v["level"], rv[name]["eye"][2] <= 3.0, name)
            self.assertTrue(10.0 < v["ev"] < 16.0, name)
            doy = (__import__("datetime").date(2026, *v["date"])
                   - __import__("datetime").date(2026, 1, 1)).days + 1
            az, el = U._sun_position(doy, v["clock"])
            self.assertLess(abs(el - rv[name]["sun"][1]), 1.0, name)
            self.assertLess(abs((az - rv[name]["sun"][0] + 180) % 360 - 180), 2.5, name)

    def test_unreal_interior_cuts_dim_the_lamps_and_balance_for_them(self):
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=os.path.join(TMP, "ue"))
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        views = U.design_views()
        self.assertTrue(any(v["interior"] for v in views.values()))
        for name, v in views.items():
            if v["interior"]:
                # villa_blender's INTERIOR_LIGHTS, and a balance near the
                # 3000 K lamps -- not the sun's 5300-6300 K (the ochre walls;
                # measured: 4200 K still left the hall's walls B/R 0.71,
                # 3500 K brings them to 0.86)
                self.assertEqual(v["lights"], B.INTERIOR_LIGHTS, name)
                self.assertTrue(3000 < v["wb"] < 4600, name)
            else:
                # villa_blender's EXTERIOR_LIGHTS (at full strength the GF
                # glazing glowed amber in the Unreal exteriors)
                self.assertEqual(v["lights"], B.EXTERIOR_LIGHTS, name)
                self.assertIn(v["wb"], (5300, 5900, 6300), name)
        self.assertEqual((U.INTERIOR_CUT_LIGHTS, U.EXTERIOR_CUT_LIGHTS),
                         (B.INTERIOR_LIGHTS, B.EXTERIOR_LIGHTS))
        # the keys: each light's own intensity x its cut's scale, constant
        seq = mock.MagicMock()
        comp = mock.MagicMock()
        U.STATE["lights"] = [(comp, 1000.0)]
        order = list(views)
        self.assertEqual(U.light_keys(seq, order, views), 1)
        ch = seq.add_possessable.return_value.add_track.return_value.add_section.return_value \
            .get_all_channels.return_value[0]
        got = [(c.args[0], c.args[1]) for c in ch.add_key.call_args_list]
        self.assertEqual([v for _f, v in got], [1000.0 * views[n]["lights"] for n in order])
        seq.add_possessable.assert_called_once_with(comp)
        # the villa's typed views carry no scale: nothing is keyed
        V0 = unreal_build()
        V0.STATE["lights"] = [(comp, 1000.0)]
        self.assertEqual(V0.light_keys(mock.MagicMock(), list(V0.VIEWS), V0.VIEWS), 0)
        self.assertFalse(any("lights" in v for v in V0.VIEWS.values()))

    def test_unreal_takes_the_rendered_eyes(self):
        out = os.path.join(TMP, "ue_sidecar")
        tm = os.path.join(out, "render", "twinmotion")
        os.makedirs(tm, exist_ok=True)
        with open(os.path.join(tm, "views.json"), "w") as f:
            json.dump({"garden_se": {"eye": [27.7, 2.7, 1.7], "date": [10, 18], "clock": "17:05"}}, f)
        try:
            U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=out)
            v = U.design_views()["garden_se"]
            self.assertEqual(v["eye"], (27.7, 2.7, 1.7))
            self.assertEqual(v["date"], (10, 18))
            self.assertAlmostEqual(v["clock"], 17 + 5 / 60, places=3)
        finally:
            os.remove(os.path.join(tm, "views.json"))


class Materials(unittest.TestCase):
    def test_assign_is_a_literal_covering_both_designs(self):
        for path in (VB, BS):
            assign = literal(path, "ASSIGN")
            for g in sorted(villa_groups() | fairway_groups()):
                self.assertIn(g, assign, f"{os.path.basename(path)}: ASSIGN has no {g}")

    def test_villa_assign_is_the_pre_projects_one_plus_stone(self):
        old, new = literal(VB_ORIG, "ASSIGN"), literal(VB, "ASSIGN")
        self.assertEqual({k: v for k, v in new.items() if k != "stone"}, old)
        self.assertEqual(new["stone"], "stone_dark")

    def test_every_fairway_group_and_kind_has_a_recipe(self):
        V = fairway_design()
        recipes = literal(VB, "KIND_RECIPES")
        ue_tex, ue_plain = literal(BS, "KIND_UE"), literal(BS, "PLAIN_KIND")
        for g in fairway_groups() - {"grate"}:            # the Fairway has no grate
            self.assertIn(g, V.MATERIALS, f"MATERIALS has no {g}")
        for g, m in V.MATERIALS.items():
            self.assertIn(m["kind"], recipes, f"{g}: no Blender recipe for {m['kind']}")
            self.assertTrue(m["kind"] in ue_tex or m["kind"] in ue_plain
                            or m["kind"] in ("glass", "water"),
                            f"{g}: no Unreal mapping for {m['kind']}")
        pbr_sets = {s for s, *_ in literal(BS, "PBR").values()}
        for kind, (s, _detail) in ue_tex.items():
            self.assertIn(s, pbr_sets, f"{kind}: {s} is not a set build_scene imports")
        for kind, r in recipes.items():
            if r["texture"] and r["texture"] != "Tiles107":
                self.assertIn(r["texture"], literal(VB, "TEX_SIZE"), kind)

    def test_fit_tint_is_the_same_in_both_renderers(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        for k in ("TINT_MAX", "TINT_FIT_MAX", "ALBEDO_HI", "DETAIL_MIN", "HI_RATIO_DEFAULT"):
            self.assertEqual(getattr(B, k), getattr(U, k), k)
        cases = [((0.36, 0.55, 0.24), GRASS_AVG, GRASS_HI, 1.0),
                 ((0.36, 0.55, 0.24), GRASS_AVG, None, 0.8),
                 ((0.20, 0.36, 0.15), GRASS_AVG, GRASS_HI, 1.0),
                 ((0.87, 0.84, 0.77), (0.3828, 0.3234, 0.2285), (0.617, 0.527, 0.402), 0.22),
                 ((0.95, 0.95, 0.95), (0.05, 0.05, 0.05), None, 1.0)]
        for c in cases:
            self.assertEqual(B.fit_tint(*c), U.fit_tint(*c), c)

    def test_lawn_reaches_the_design_colour(self):
        # Grass001 is ~6-10x darker than the Fairway's lawn: the old clamp
        # (tint <= 4 per channel) left it (0.245, 0.44, 0.092)
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        lawn = B.V.MATERIALS["lawn"]["color"]
        tint, detail, clamped = B.fit_tint(lawn, GRASS_AVG, GRASS_HI)
        self.assertFalse(clamped)
        for t, a, c in zip(tint, GRASS_AVG, lawn):
            self.assertAlmostEqual(t * a, c, places=9)                  # averages the colour
        self.assertTrue(B.DETAIL_MIN <= detail < 1.0)
        for t, a, h in zip(tint, GRASS_AVG, GRASS_HI):                  # highlights not blown
            self.assertLessEqual(t * (detail * h + (1 - detail) * a), B.ALBEDO_HI + 1e-9)
        # a colour no tint can reach is flagged, not claimed
        _t, _d, clamped = B.fit_tint((0.9, 0.9, 0.9), (0.02, 0.02, 0.02), None)
        self.assertTrue(clamped)

    def test_in_range_tints_are_as_before(self):
        # every Fairway set but the lawn's was within the old clamp: the fit
        # leaves those tints and the recipes' own detail exactly as they were
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        avgs = {"Travertine001": (0.3828, 0.3234, 0.2285), "WoodFloor040": (0.4744, 0.2473, 0.0932),
                "Concrete034": (0.482, 0.482, 0.482), "Gravel023": (0.7071, 0.681, 0.6276),
                "Ground054": (0.3351, 0.261, 0.1581)}
        recipes = literal(VB, "KIND_RECIPES")
        for grp, m in B.V.MATERIALS.items():
            s = recipes[m["kind"]]["texture"]
            if s not in avgs:
                continue
            d0 = B.KIND_DETAIL.get(m["kind"], 1.0)
            tint, detail, clamped = B.fit_tint(m["color"], avgs[s], None, d0)
            old = tuple(min(4.0, c / max(a, 1e-3)) for c, a in zip(m["color"], avgs[s]))
            self.assertEqual((tint, detail, clamped), (old, d0, False), grp)

    def test_golf_shades_stay_distinct(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        lawn = tuple(B.V.MATERIALS["lawn"]["color"])
        for hi in (GRASS_HI, None):
            bl = []
            for k in B.GOLF_SHADES:                     # villa_blender.context's colours
                col = B._scaled(lawn, k)
                tint, _d, clamped = B.fit_tint(col, GRASS_AVG, hi)
                self.assertFalse(clamped)
                bl.append(tuple(round(t * a, 6) for t, a in zip(tint, GRASS_AVG)))
                self.assertEqual(bl[-1], tuple(round(c, 6) for c in col))
            ue = [tuple(round(c, 6) for c in a) for a in U.golf_albedos(lawn, GRASS_AVG, hi)]
            self.assertEqual(ue, bl)
            self.assertEqual(len(set(bl)), 3, bl)
            for a, k in zip(bl, B.GOLF_SHADES):
                self.assertAlmostEqual(a[1] / lawn[1], k, places=5)

    def test_stone_is_a_wall_for_the_unreal_room_test(self):
        for name in ("SIDE_GROUPS", "VERT_GROUPS", "SOLID_GROUPS"):
            self.assertIn("stone", literal(BS, name), name)
            self.assertIn("walls", literal(BS, name), name)


# the texture averages / 99th percentiles villa_blender measured (materials.json)
TEX_AVG = {"Travertine001": (0.3828, 0.3234, 0.2285), "WoodFloor040": (0.4744, 0.2473, 0.0932),
           "Concrete034": (0.482, 0.482, 0.482), "Gravel023": (0.7071, 0.681, 0.6276),
           "Ground054": (0.3351, 0.261, 0.1581), "Grass001": GRASS_AVG}
TEX_HI = {"Grass001": GRASS_HI}


def record_unreal_materials(U, sidecar=None):
    """U.build_materials() with the editor stubbed: every material instance
    it makes as {name: parent, scalars, vectors, textures}, and M."""
    made = {}

    def instance(name, parent, scalars=None, vectors=None, textures=None, switches=None):
        made[name] = {"parent": parent, "scalars": dict(scalars or {}),
                      "vectors": {k: tuple(v) for k, v in (vectors or {}).items()},
                      "textures": dict(textures or {})}
        return name

    U.instance = instance
    U.import_texture = lambda s, k: f"{s}:{k}"
    U.master_pbr = lambda defaults: "M_VillaPBR"
    U.master_plain = lambda: "M_VillaPlain"
    U.master_thin = lambda name, *a, **k: name
    for m, name in (("master_stone", "M_VillaStone"), ("master_frond", "M_VillaFrond")):
        if hasattr(U, m):
            setattr(U, m, lambda name=name: name)
    if hasattr(U, "sidecar"):
        U.sidecar = lambda name: (sidecar or {}) if name == "materials.json" else {}
    M = U.build_materials()
    return made, M


def master_chain(r, s):
    """M_VillaPBR's roughness: min(max(saturate(map x Mul + Add), Min), Max)."""
    import numpy as np
    return np.minimum(np.maximum(np.clip(r * s["RoughnessMul"] + s.get("RoughnessAdd", 0.0), 0, 1),
                                 s.get("RoughnessMin", 0.0)), s.get("RoughnessMax", 1.0))


class Roughness(unittest.TestCase):
    """The last review's open MAJOR: a design's roughness (MATERIALS[group].
    roughness) is the surface's, in BOTH renderers. Travertine001's map is
    shot polished (mean 0.026): Unreal took it as it was (the limestone
    paving and coping a near-mirror), Blender scaled it x29 to the design's
    mean (a quarter of each slab under 0.35 -- blotchy wet patches)."""

    def test_rough_fit_is_the_same_in_both_renderers(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        for k in ("ROUGH_DEV", "ROUGH_BAND", "ROUGH_MIN", "FLOOR_FINISH", "FLOOR_T",
                  "FLOOR_OAK_ROLES", "FLOOR_CONCRETE_ROLES"):
            self.assertEqual(getattr(B, k), getattr(U, k), k)
        for m in list(B.V.MATERIALS.values()) + [{"roughness": r} for r in (0.0, 0.18, 1.0, 1.4)]:
            for st in list(ROUGH_STATS.values()) + [(None, None), (0.0, 0.0), (0.5, 0.0)]:
                self.assertEqual(B.rough_fit(m["roughness"], *st), U.rough_fit(m["roughness"], *st))
        # no statistics: the design's value, flat -- never the map as it is
        self.assertEqual(U.rough_fit(0.75)[:2], (0.0, 0.75))

    def test_the_stats_are_the_maps(self):
        import numpy as np  # noqa: F401
        for s, (mean, std) in ROUGH_STATS.items():
            r = roughness_map(s)
            if r is None:
                continue
            self.assertAlmostEqual(float(r.mean()), mean, delta=0.003, msg=s)
            self.assertAlmostEqual(float(r.std()), std, delta=0.003, msg=s)

    def test_design_roughness_over_the_real_maps(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy")
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        V = fairway_design()
        checked = []
        for grp, m in V.MATERIALS.items():
            s = U.KIND_UE.get(m["kind"], (None,))[0]
            r = roughness_map(s) if s in ROUGH_STATS else None
            if r is None:
                continue
            want = U.kind_roughness(m["kind"], m["roughness"])
            gain, off, lo, hi = U.rough_fit(want, *ROUGH_STATS[s])
            eff = master_chain(r, {"RoughnessMul": gain, "RoughnessAdd": off,
                                   "RoughnessMin": lo, "RoughnessMax": hi})
            self.assertAlmostEqual(float(eff.mean()), want, delta=0.02, msg=grp)
            self.assertGreaterEqual(float(eff.min()), lo - 1e-6, grp)
            self.assertLessEqual(float(eff.max()), hi + 1e-6, grp)
            checked.append(grp)
        if "paving" not in checked:
            self.skipTest("Travertine001 is not unpacked here")
        tr = roughness_map("Travertine001")
        for grp in ("paving", "pool", "stair"):
            want = V.MATERIALS[grp]["roughness"]
            gain, off, lo, hi = U.rough_fit(want, *ROUGH_STATS["Travertine001"])
            eff = master_chain(tr, {"RoughnessMul": gain, "RoughnessAdd": off,
                                    "RoughnessMin": lo, "RoughnessMax": hi})
            self.assertEqual(float((eff < want - 0.15).mean()), 0.0, grp)      # no gloss patches
            self.assertLess(float(eff.std()), 0.06, grp)                        # gentle, not blotchy
            # the old rules, for the record
            self.assertLess(float(tr.mean()), 0.05)                             # Unreal: a mirror
            old = np.clip(tr * want / tr.mean(), 0, 1)                          # Blender: x29
            self.assertGreater(float((old < 0.35).mean()), 0.15, grp)

    def test_unreal_design_materials_carry_the_design_roughness(self):
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        made, M = record_unreal_materials(U, {"_texture_average": TEX_AVG, "_texture_high": TEX_HI,
                                              "_roughness_stats": ROUGH_STATS})
        V = fairway_design()
        for grp, m in V.MATERIALS.items():
            kind = m["kind"]
            if kind not in U.KIND_UE or U.KIND_UE[kind][0] not in TEX_AVG:
                if kind not in ("glass", "water", "stone_dark"):
                    # a plain colour (no measured set): the design's roughness as it is
                    inst = made[M["grp:" + grp]]
                    self.assertEqual((inst["parent"], inst["scalars"]["Roughness"]),
                                     ("M_VillaPlain", m["roughness"]), grp)
                continue
            s = U.KIND_UE[kind][0]
            inst = made[M["grp:" + grp]]
            self.assertEqual(inst["parent"], "M_VillaPBR", grp)
            self.assertEqual(inst["textures"]["RoughnessMap"], f"{s}:Roughness", grp)
            gain, off, lo, hi = U.rough_fit(U.kind_roughness(kind, m["roughness"]), *ROUGH_STATS[s])
            sc = inst["scalars"]
            self.assertEqual((sc["RoughnessMul"], sc["RoughnessAdd"], sc["RoughnessMin"],
                              sc["RoughnessMax"]), (gain, off, lo, hi), grp)
        # the stacked stone is the stone recipe, in the design's colour
        stone = made[M["grp:stone"]]
        self.assertEqual(stone["parent"], "M_VillaStone")
        self.assertEqual(stone["vectors"]["Color"], tuple(V.MATERIALS["stone"]["color"]))
        self.assertEqual(stone["scalars"]["Roughness"], V.MATERIALS["stone"]["roughness"])
        # the interior floors (villa_blender's FLOOR_FINISH), world-aligned at size
        for fin, (s, tint, rough, detail) in U.FLOOR_FINISH.items():
            inst = made[M[f"floor_{fin}"]]
            if s:
                self.assertEqual(inst["scalars"]["WorldUV"], 1.0)
                self.assertAlmostEqual(inst["scalars"]["WorldTileCm"], 100 * U.TILE_M[s])
                self.assertEqual(inst["scalars"]["ColorDetail"], detail)
                self.assertEqual(inst["vectors"]["Tint"], tint)
                self.assertEqual(inst["scalars"]["RoughnessAdd"], U.rough_fit(rough, *ROUGH_STATS[s])[1])
            else:
                self.assertEqual((inst["parent"], inst["scalars"]["Roughness"]), ("M_VillaPlain", rough))
        # the golf course at villa_blender.context's 0.95 / 0.9
        for i, want in ((0, 0.95), (1, 0.9), (2, 0.9)):
            sc = made[M[f"ctx_golf{i}"]]["scalars"]
            self.assertEqual(sc["RoughnessAdd"], U.rough_fit(want, *ROUGH_STATS["Grass001"])[1])
        self.assertEqual(made[M["ctx_leaf"]]["parent"], "M_VillaFrond")

    def test_unreal_villa_materials_are_the_pre_projects_ones(self):
        """The villa (no MATERIALS): every instance build_materials makes --
        its parent, scalars, vectors and textures -- is the pre-projects
        code's; the master's new roughness band is the identity by default."""
        U = unreal_build()
        new, _M = record_unreal_materials(U)
        with environment():
            old_mod = load(os.path.join(ROOT, "_pre_projects_0926", "unreal", "build_scene.py"),
                           "build_scene_orig_materials")
            old, _M = record_unreal_materials(old_mod)
        self.assertEqual(new, old)
        self.assertFalse(any("RoughnessMin" in v["scalars"] or "RoughnessMax" in v["scalars"]
                             for v in new.values()))
        # the band's defaults: 0 / 1 after a saturate change nothing
        U2 = unreal_build()
        got = {}
        real = U2._scalar

        def rec(mat, name, value, x, y):
            got[name] = value
            return real(mat, name, value, x, y)

        U2._scalar = rec
        U2.master_pbr({"Color": None, "NormalDX": None, "Roughness": None})
        self.assertEqual((got["RoughnessMin"], got["RoughnessMax"]), (0.0, 1.0))
        self.assertEqual((got["RoughnessMul"], got["RoughnessAdd"]), (1.0, 0.0))

    def test_blender_villa_materials_are_the_pre_projects_ones(self):
        """In Blender itself: every node, setting, unlinked input value and
        link of every material villa_blender.materials() builds for the villa
        equals the pre-projects code's (pbr's new options add nothing by
        default)."""
        exe = blender_exe()
        if not exe:
            self.skipTest("Blender not installed")
        res = run_blender(exe, BLENDER_VILLA_MATERIALS, {})
        self.assertGreaterEqual(len(res["old"]), 12)                  # concrete ... shrub
        self.assertGreaterEqual(min(len(v["nodes"]) for k, v in res["old"].items()
                                    if k in ("concrete", "travertine", "oak", "grass")), 9)
        self.assertEqual(sorted(res["new"]), sorted(res["old"]))
        for k in res["old"]:
            self.assertEqual(res["new"][k], res["old"][k], k)

    def test_blender_fairway_stone_nodes_keep_the_design_roughness(self):
        """In Blender itself: the Fairway's limestone paving / coping and its
        travertine stair drive the Principled roughness through
        clamp(gain x map + offset, lo, hi) with rough_fit's numbers, and over
        the set's real map that averages the design's value with no gloss
        patches."""
        exe = blender_exe()
        if not exe:
            self.skipTest("Blender not installed")
        res = run_blender(exe, BLENDER_FAIRWAY_ROUGHNESS,
                          {"VILLA_DESIGN_DIR": FAIRWAY, "VILLA_OUT": os.path.join(TMP, "bl_fw")})
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        for grp in ("paving", "pool", "stair", "deck", "base"):
            r = res[grp]
            want = B.V.MATERIALS[grp]["roughness"]
            fit = B.rough_fit(want, *r["stats"])
            for got, exp in zip((r["gain"], r["offset"], r["lo"], r["hi"]), fit):
                self.assertAlmostEqual(got, exp, places=4, msg=grp)
            self.assertEqual(r["image"].split("_")[0], B.KIND_RECIPES[B.V.MATERIALS[grp]["kind"]]["texture"])
            self.assertAlmostEqual(r["mean"], want, delta=0.02, msg=grp)
            self.assertGreaterEqual(r["p1"], want - B.ROUGH_BAND - 1e-3, grp)
            s = B.KIND_RECIPES[B.V.MATERIALS[grp]["kind"]]["texture"]
            self.assertAlmostEqual(r["stats"][0], ROUGH_STATS[s][0], delta=0.002, msg=grp)


def run_blender(exe, script, env):
    """Run `script` in Blender (background, factory settings) with the
    pipeline variables `env`; it writes a JSON result, which is returned."""
    os.makedirs(TMP, exist_ok=True)
    path = os.path.join(TMP, "blender_check.py")
    out = os.path.join(TMP, "blender_check.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    with contextlib.suppress(FileNotFoundError):
        os.remove(out)
    e = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    e.update(env)
    r = subprocess.run([exe, "-b", "--factory-startup", "-P", path, "--", ROOT, out],
                       env=e, capture_output=True, text=True, timeout=600)
    if not os.path.exists(out):
        raise AssertionError(f"Blender wrote no result:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    with open(out, encoding="utf-8") as f:
        return json.load(f)


BLENDER_COMMON = r'''
import bpy, importlib.util, json, os, sys
ROOT, OUT = sys.argv[sys.argv.index("--") + 1:][:2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def val(v):
    if v is None or isinstance(v, (str, bool)):
        return v
    try:
        return [round(float(x), 6) for x in v]
    except TypeError:
        pass
    try:
        return round(float(v), 6)
    except Exception:
        return str(v)
'''

BLENDER_VILLA_MATERIALS = BLENDER_COMMON + r'''
KEYS = ("operation", "blend_type", "offset", "offset_frequency", "squash", "squash_frequency",
        "use_clamp", "clamp_type", "interpolation", "extension", "projection", "data_type")


def dump(mat):
    nt = mat.node_tree
    nodes = []
    for n in sorted(nt.nodes, key=lambda n: n.name):
        props = {k: val(getattr(n, k)) for k in KEYS if hasattr(n, k)}
        img = getattr(n, "image", None)
        if img is not None:
            props["image"] = os.path.basename(img.filepath)
            props["colorspace"] = img.colorspace_settings.name
        if n.bl_idname == "ShaderNodeValToRGB":
            props["ramp"] = [[round(e.position, 6), val(e.color)] for e in n.color_ramp.elements]
        ins = {f"{i}:{s.identifier}": val(s.default_value) for i, s in enumerate(n.inputs)
               if not s.is_linked and hasattr(s, "default_value")}
        nodes.append([n.name, n.bl_idname, props, ins])
    links = sorted([l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier]
                   for l in nt.links)
    return {"name": mat.name, "tile_m": val(mat.get("tile_m")), "nodes": nodes, "links": links}


res = {}
new = load(os.path.join(ROOT, "villa_blender.py"), "vb_new")          # the villa: no VILLA_DESIGN_DIR
res["new"] = {k: dump(m) for k, m in new.materials().items()}
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
old = load(os.path.join(ROOT, "_pre_projects_0926", "villa_blender.py"), "vb_old")
res["old"] = {k: dump(m) for k, m in old.materials().items()}
with open(OUT, "w") as f:
    json.dump(res, f)
'''

BLENDER_FAIRWAY_ROUGHNESS = BLENDER_COMMON + r'''
import numpy as np
B = load(os.path.join(ROOT, "villa_blender.py"), "vb_fw")
res = {}
for grp in ("paving", "pool", "stair", "deck", "base"):
    m = B.V.MATERIALS[grp]
    mat = B.kind_material(m["kind"], m["color"], m["roughness"])
    bsdf = next(n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    clamp = bsdf.inputs["Roughness"].links[0].from_node
    madd = clamp.inputs["Value"].links[0].from_node
    tex = madd.inputs[0].links[0].from_node
    img = tex.image
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    r = px.reshape(-1, 4)[:, 0]
    gain, off = madd.inputs[1].default_value, madd.inputs[2].default_value
    lo, hi = clamp.inputs["Min"].default_value, clamp.inputs["Max"].default_value
    eff = np.clip(r * gain + off, lo, hi)
    res[grp] = {"clamp": clamp.bl_idname, "op": madd.operation, "gain": gain, "offset": off,
                "lo": lo, "hi": hi, "image": os.path.basename(img.filepath),
                "colorspace": img.colorspace_settings.name,
                "stats": list(B.tex_rough_stats(B.extract(B.KIND_RECIPES[m["kind"]]["texture"])["Roughness"])),
                "mean": float(eff.mean()), "p1": float(np.percentile(eff, 1)),
                "fit": list(mat.get("roughness_fit"))}
with open(OUT, "w") as f:
    json.dump(res, f)
'''


class Floors(unittest.TestCase):
    def test_floor_plan_is_the_same_in_both_renderers(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        V = fairway_design()
        plan = B.floor_plan(V)
        self.assertEqual(plan, U.floor_plan(V))
        self.assertTrue(plan)
        self.assertEqual({p[1] for p in plan}, {"travertine", "oak", "concrete"})
        below = set(getattr(V, "BELOW_GRADE_FLOORS", ()))
        voids = getattr(V, "VOIDS", [])
        for label, _fin, x0, y0, x1, y1, z in plan:
            fl = label.split()[0]
            self.assertNotIn(fl, below)
            self.assertAlmostEqual(z, V.LEVEL[fl] / 1000.0)
            for v in voids:                       # no floor over a void of its floor
                if fl in v[5]:
                    vx0, vy0, vx1, vy1 = (c / 1000.0 for c in v[1:5])
                    self.assertFalse(x0 < vx1 - 1e-6 and vx0 < x1 - 1e-6
                                     and y0 < vy1 - 1e-6 and vy0 < y1 - 1e-6, label)
        # the polished travertine is glossy, not a mirror (it was 0.45 x the
        # polished map: 0.01)
        gain, off, lo, hi = B.rough_fit(B.FLOOR_FINISH["travertine"][2], *ROUGH_STATS["Travertine001"])
        self.assertGreaterEqual(lo, 0.06)


def write_glb(path, name, tri, material=True, pad_bin=True):
    """A one-triangle glb (POSITION + uint16 indices), as the glb reader reads."""
    pos = struct.pack("<9f", *[c for v in tri for c in v])
    idx = struct.pack("<3H", 0, 1, 2)
    blob = pos + idx
    if pad_bin:
        blob += b"\0" * ((-len(blob)) % 4)
    prim = {"attributes": {"POSITION": 0}, "indices": 1}
    js = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}],
          "nodes": [{"name": name, "mesh": 0}], "meshes": [{"name": name, "primitives": [prim]}],
          "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3"},
                        {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"}],
          "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 36},
                          {"buffer": 0, "byteOffset": 36, "byteLength": 6}],
          "buffers": [{"byteLength": len(blob)}]}
    if material:
        js["materials"] = [{"name": "m"}]
        prim["material"] = 0
    j = json.dumps(js).encode()
    j += b" " * ((-len(j)) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(j) + 8 + len(blob)))
        f.write(struct.pack("<II", len(j), 0x4E4F534A) + j)
        f.write(struct.pack("<II", len(blob), 0x004E4942) + blob)


class Glb(unittest.TestCase):
    def test_merge_glb_keeps_both_models(self):
        """build_scene imports the model and villa_blender's palms in ONE
        Interchange import (a second import in the same script never
        completes): merge_glb must keep both files' triangles exactly."""
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        os.makedirs(TMP, exist_ok=True)
        a, b, out = (os.path.join(TMP, n) for n in ("a.glb", "b.glb", "ab.glb"))
        write_glb(a, "walls", ((0, 0, 0), (1, 0, 0), (0, 1, 0)))
        write_glb(b, "ctx palm 0 trunk", ((5, 5, 0), (6, 5, 0), (5, 6, 2)), material=False, pad_bin=False)
        U.merge_glb(a, b, out)
        js, _bin = U.read_glb(out)
        self.assertEqual([n["name"] for n in js["nodes"]], ["walls", "ctx palm 0 trunk"])
        self.assertEqual(js["scenes"][0]["nodes"], [0, 1])
        self.assertEqual(len(js["materials"]), 1)
        for name, src in (("walls", a), ("ctx palm 0 trunk", b)):
            self.assertEqual(U.glb_triangles(out, name), U.glb_triangles(src, name), name)
        self.assertTrue(U.glb_triangles(out, "ctx palm 0 trunk"))


def box_tris(x0, y0, z0, x1, y1, z1):
    """The 12 triangles of an axis-aligned box (the glb reader's format)."""
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    out = []
    for a, b, c, d in quads:
        out += [(v[a], v[b], v[c]), (v[a], v[c], v[d])]
    return out


def walled_room(x0, y0, x1, y1, t=0.2, h=3.0, skip=()):
    """Walls round a room (outside faces at its rectangle + t), minus `skip`
    sides ('x+', 'x-', 'y+', 'y-')."""
    tris = []
    sides = {"x-": (x0 - t, y0 - t, x0, y1 + t), "x+": (x1, y0 - t, x1 + t, y1 + t),
             "y-": (x0 - t, y0 - t, x1 + t, y0), "y+": (x0 - t, y1, x1 + t, y1 + t)}
    for k, (a, b, c, d) in sides.items():
        if k not in skip:
            tris += box_tris(a, b, 0.0, c, d, h)
    return tris


class RoomTest(unittest.TestCase):
    """build_scene's interior-light room test for a design with render hooks
    (room_layout / probe_point / room_fit_design), on synthetic walls."""

    def setUp(self):
        self.U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)

    def fit(self, tris, lay, villa_too=False):
        U = self.U
        px, py, _c = U.probe_point(lay)
        why = U.room_fit_design(lambda q, a, s: U.axis_ray(tris, q, a, s), lay, (px, py), 0.0)
        if not villa_too:
            return why
        x0, y0, x1, y1 = lay["rect"]
        old = U.room_fit(tris, (x0 + x1) / 2, (y0 + y1) / 2, 0.0, (x1 - x0) / 2, (y1 - y0) / 2)
        return why, old

    def test_nested_ensuite_is_not_a_wall_inside(self):
        # a 6 x 5 m bedroom, an en-suite across its north half-width with a
        # 150 mm partition: the villa rule rejects it, the design rule does not
        tris = walled_room(0, 0, 6, 5)
        kid = (-0.15, 2.85, 4.15, 5.15)
        tris += box_tris(4.0, 2.85, 0, 4.15, 5.0, 3.0) + box_tris(0.0, 2.85, 0, 4.15, 3.0, 3.0)
        lay = {"rect": (0, 0, 6, 5), "kids": [kid], "voids": [], "openings": []}
        why, old = self.fit(tris, lay, villa_too=True)
        self.assertEqual(why, "")
        self.assertIn("a wall", old)

    def test_open_plan_through_its_openings(self):
        tris = walled_room(0, 0, 6, 5, skip=("x+", "x-"))
        lay = {"rect": (0, 0, 6, 5), "kids": [], "voids": [], "openings": []}
        self.assertIn("open on", self.fit(tris, lay))
        lay["openings"] = [("v", 6.0, 6.15, 0.5, 4.5), ("v", -0.15, 0.0, 0.5, 4.5)]
        self.assertEqual(self.fit(tris, lay), "")
        # an opening that the probe's ray does not pass through does not count
        lay["openings"] = [("v", 6.0, 6.15, 3.0, 4.5), ("v", -0.15, 0.0, 3.0, 4.5)]
        self.assertIn("open on", self.fit(tris, lay))

    def test_a_wall_the_design_does_not_have_rejects(self):
        tris = walled_room(0, 0, 6, 5) + box_tris(4.5, 0, 0, 4.6, 5, 3.0)
        lay = {"rect": (0, 0, 6, 5), "kids": [], "voids": [], "openings": []}
        self.assertIn("a wall 1.50 m", self.fit(tris, lay))

    def test_probe_moves_off_a_void(self):
        lay = {"rect": (0, 0, 6, 6), "kids": [], "voids": [(0, 2, 6, 6)], "openings": []}
        px, py, clear = self.U.probe_point(lay)
        self.assertAlmostEqual(px, 3.0)
        self.assertLess(py, 2.0 - self.U.PROBE_MARGIN + 1e-9)
        self.assertGreaterEqual(clear, self.U.PROBE_MARGIN)

    def test_fairway_layouts(self):
        U, V = self.U, fairway_design()
        by = {(r[6], r[0]): r for r in V.ROOMS}
        master = U.room_layout(V, by[("FF", "MASTER BEDROOM")])
        self.assertEqual(len(master["kids"]), 2)                 # ensuite + dressing
        dining = U.room_layout(V, by[("GF", "DINING")])
        self.assertEqual(sum(1 for o in dining["openings"] if o[0] == "v"), 2)   # open both x sides
        landing = U.room_layout(V, by[("FF", "LANDING")])
        self.assertTrue(landing["voids"])                         # the stair void
        px, py, _c = U.probe_point(landing)
        self.assertTrue(all(U._rect_dist((px, py), v) >= U.PROBE_MARGIN for v in landing["voids"]))
        self.assertTrue(U.design_hooks(V))
        with environment():
            villa = load(os.path.join(ROOT, "villa_design.py"), "villa_design_hooks_test")
        self.assertFalse(U.design_hooks(villa))                   # the villa keeps room_fit


def light_positions(mod):
    """{room name: (x, y, z) m} of the ceiling lights mod.interior_lights()
    hangs, with its (stand-in) bpy recording each light object."""
    made = {}

    def new(name, data):
        ob = types.SimpleNamespace(name=name, location=None)
        made[name] = ob
        return ob

    mod.bpy.data.objects.new.side_effect = new
    mod.interior_lights()
    return {k[len("light "):]: tuple(round(c, 4) for c in ob.location) for k, ob in made.items()}


class Lights(unittest.TestCase):
    def test_villa_room_lights_exactly_as_before(self):
        # the villa (no render hooks) keeps the original GF/FF rule -- its
        # annex lights too, until the user approves the fix
        new = blender()
        with environment():
            old = load(VB_ORIG, "villa_blender_orig_lights")
        a, b = light_positions(new), light_positions(old)
        self.assertEqual(a, b)
        self.assertEqual(len(a), len(new.V.ROOMS))

    def test_annex_light_fix_is_opt_in(self):
        B = blender(VILLA_ANNEX_LIGHT_FIX="1")
        V = B.V
        got = light_positions(B)
        annex = [r for r in V.ROOMS if r[6] not in ("GF", "FF")]
        self.assertTrue(annex, "the villa has annex rooms")
        for r in annex:
            self.assertAlmostEqual(got[r[0]][2], (V.LEVEL[r[6]] + V.CEIL[r[6]] - 150) / 1000, places=4)

    def test_design_lights_hang_under_their_own_storey(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        V = B.V
        got = light_positions(B)
        for r in V.ROOMS:
            self.assertAlmostEqual(got[r[0]][2], (V.LEVEL[r[6]] + V.CEIL[r[6]] - 150) / 1000,
                                   places=4, msg=r[0])


class Eyes(unittest.TestCase):
    def test_walk_clear_statuses(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        # clear where it stands
        self.assertEqual(B.walk_clear((0, 0, 1.6), (10, 0, 2), lambda p: True),
                         ((0.0, 0.0, 1.6), 0.0, "clear"))
        # a hedge 1 m thick in front of the eye: moved just past it
        eye, moved, status = B.walk_clear((0, 0, 1.6), (10, 0, 2), lambda p: p[0] > 1.0)
        self.assertEqual(status, "moved")
        self.assertAlmostEqual(moved, 1.05)
        self.assertEqual(eye, (1.05, 0.0, 1.6))
        # solid all the way to half the target: blocked, the eye left where it was
        self.assertEqual(B.walk_clear((0, 0, 1.6), (10, 0, 2), lambda p: p[0] > 6.0),
                         ((0.0, 0.0, 1.6), 0.0, "blocked"))
        self.assertEqual(B.walk_clear((3, 3, 1.6), (3, 3, 0), lambda p: False),
                         ((3.0, 3.0, 1.6), 0.0, "blocked"))


class Context(unittest.TestCase):
    def test_golf_bands_cover_the_course_and_match_unreal(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        bands = B.golf_bands(30.0, side=120.0)
        self.assertEqual(bands, U.golf_bands(30.0, side=120.0))
        for k in ("GOLF_ROUGH_M", "GOLF_FAIRWAY_M", "GOLF_DEPTH_M", "GOLF_STRIPE_M", "GOLF_SHADES"):
            self.assertEqual(getattr(B, k), getattr(U, k), k)
        ys = sorted((b[2], b[4]) for b in bands)
        self.assertAlmostEqual(ys[0][0], -B.GOLF_DEPTH_M)
        self.assertAlmostEqual(ys[-1][1], 0.0)
        for (a0, a1), (b0, b1) in zip(ys, ys[1:]):
            self.assertAlmostEqual(a1, b0)                     # no gap, no overlap
        self.assertEqual({b[5] for b in bands}, {0, 1, 2})
        self.assertEqual(B.render_context(), U.render_context(fairway_design()))

    @staticmethod
    def boxes(mod, *a):
        """The context boxes mod.context() lays: [(name, x0, y0, z0, x1, y1, z1)]."""
        got = []

        def box(name, x0, y0, z0, x1, y1, z1, mat):
            got.append((name, round(x0, 4), round(y0, 4), round(z0, 4), round(x1, 4),
                        round(y1, 4), round(z1, 4)))
            ob = mock.MagicMock()
            ob.data.materials = []
            return ob

        mod._box_obj = box
        mod.context({"sand": None}, *a)
        return got

    def test_villa_context_boxes_exactly_as_before(self):
        new = blender()
        with environment():
            old = load(VB_ORIG, "villa_blender_orig_context")
        self.assertEqual(self.boxes(new), self.boxes(old))

    def test_design_context_reaches_the_horizon(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        B.kind_material = lambda *a, **k: None                  # no textures here
        saved = getattr(B.V, "RENDER_CONTEXT", None)
        try:
            B.V.RENDER_CONTEXT = {}                             # no golf course
            got = {b[0]: b for b in self.boxes(B)}
            g = got["ctx ground"]
            self.assertEqual((g[1], g[2]), (-B.FAR_FIELD_M, -B.FAR_FIELD_M))
            self.assertEqual(sum(1 for k in got if k.startswith("ctx house")), 13)   # 3 plots a side
            self.assertFalse(any(k.startswith("ctx golf") for k in got))
            B.V.RENDER_CONTEXT = {"south": "golf"}              # the Fairway's own hook
            golf = [b for b in self.boxes(B) if b[0].startswith("ctx golf")]
        finally:
            if saved is None:
                del B.V.RENDER_CONTEXT
            else:
                B.V.RENDER_CONTEXT = saved
        self.assertEqual(len(golf), len(B.golf_bands(30.0)))
        self.assertTrue(all(b[5] <= 0.0 for b in golf))                        # south of the plot
        self.assertEqual(fairway_design().RENDER_CONTEXT.get("south"), "golf")


    def test_fairway_neighbours_at_its_setbacks(self):
        B = blender(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        V = B.V
        L = B.context_layout()
        W, D = V.PLOT_W / 1000, V.PLOT_D / 1000
        self.assertAlmostEqual(L["W"], 30.0)
        self.assertAlmostEqual(L["D"], 40.36)
        self.assertAlmostEqual(L["side"], V.SB_SIDE / 1000)
        self.assertAlmostEqual(L["near_y0"] + L["depth"], D - V.SB_FRONT / 1000)
        self.assertAlmostEqual(L["far_y0"], V.SB_FRONT / 1000)
        self.assertAlmostEqual(L["height"], (V.RF + V.SLAB + V.PARAPET) / 1000)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=TMP)
        LU = U.context_layout(W, D)
        for k in ("side", "near_y0", "far_y0", "depth", "height"):
            self.assertAlmostEqual(LU[k], L[k], msg=k)

    def test_villa_context_numbers_unchanged(self):
        B = blender()
        L = B.context_layout()
        self.assertEqual((L["side"], L["near_y0"], L["far_y0"], L["depth"], L["height"]),
                         (3.0, 11.0, 3.0, 13.0, 8.4))
        U = unreal_build()
        LU = U.context_layout(24.0, 29.0)
        self.assertEqual((LU["side"], LU["near_y0"], LU["far_y0"], LU["depth"], LU["height"]),
                         (3.0, 11.0, 3.0, 13.0, 8.4))

    def test_unreal_no_shrubs_under_a_clipped_hedge(self):
        # the Fairway's planting is a hedge: no shrub scatter (and the glb is
        # not even read -- there is none at this VILLA_OUT)
        U = unreal_build(VILLA_DESIGN_DIR=FAIRWAY, VILLA_OUT=os.path.join(TMP, "no_glb"))
        self.assertEqual(U.design().MATERIALS["planting"]["kind"], "hedge")
        self.assertEqual(U.shrubs(None, None, {}), 0)

    def test_unreal_villa_report_keys_are_the_pre_projects_ones(self):
        # 'root' / 'design' / 'tint_fits' / 'dressing' are added for a project
        # or a design with hooks only: the villa's build_status.json has the
        # keys it always had
        src = source(BS)
        main = src[src.index("def main():"):src.index('if __name__ == "__main__":')]
        lit = main[main.index('result = {"ok": True'):main.index("if PROJECT or design_hooks(Vd):")]
        orig = source(os.path.join(ROOT, "_pre_projects_0926", "unreal", "build_scene.py"))
        o = orig[orig.index('return {"ok": True'):]
        o = o[:o.index("\n\n")]
        keys = lambda s: sorted(set(__import__("re").findall(r'"(\w+)":', s.split("summary")[0])))
        self.assertEqual(keys(lit), keys(o))

    def test_rect_minus(self):
        B = blender()
        parts = B._rect_minus([(0, 0, 10, 10)], (4, 4, 6, 6))
        self.assertAlmostEqual(sum((c - a) * (d - b) for a, b, c, d in parts), 96.0)
        self.assertEqual(B._rect_minus([(0, 0, 10, 10)], (20, 20, 30, 30)), [(0, 0, 10, 10)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
