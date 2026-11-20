"""Offline proof that the 2-D sheet builders follow the design they are given.

    python tests/test_project_sheets.py              (from the project folder)
    python -m unittest tests.test_project_sheets

No AutoCAD, no COM (villa_load / villa_verify / villa_show are imported with
pythoncom and win32com STUBBED -- nothing reaches a COM server). Two designs:

  * the VILLA (villa_design.py here): its sheet lists are exactly what they
    were before the builders learnt project designs -- villa_cad and
    villa_colour's plan sheets and wording, villa_load's SHEETS, villa_verify's
    sheets, villa_show's MINE;
  * THE FAIRWAY (projects\\fairway, through run_project.py): A-101 site,
    A-102 B1, A-103 GF, A-104 FF from its PLAN_SHEETS, the P set beside them;
    the basement's furniture on the basement sheet; the feature stair on GF
    (UP) and FF (DN), the service stair on B1 (UP) and GF (DN, seen down its
    well) with its half-landing; villa_cad and villa_colour run into a temp
    folder and write every DXF and PNG, with the right title blocks.

Each design is loaded in a subprocess of its own (both are called
villa_design); everything is written under %TEMP%.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
TMP = os.path.join(tempfile.gettempdir(), f"villa_project_sheets_{os.getpid()}")

# A probe run inside each design: prints what the sheet builders would do.
PROBE = textwrap.dedent(r'''
    import json, sys, types

    # stub COM: villa_load / villa_verify / villa_show import these at the top
    pc = types.ModuleType("pythoncom")
    pc.CoInitialize = lambda *a, **k: None
    pc.VT_ARRAY, pc.VT_R8, pc.VT_DISPATCH = 0x2000, 5, 9
    w32 = types.ModuleType("win32com")
    cl = types.ModuleType("win32com.client")
    cl.VARIANT = lambda *a, **k: a
    def _no_com(*a, **k):
        raise RuntimeError("COM is stubbed in this test")
    cl.GetActiveObject = cl.Dispatch = _no_com
    w32.client = cl
    sys.modules.update({"pythoncom": pc, "win32com": w32, "win32com.client": cl})

    import villa_design as V
    import villa_geom as G
    import villa_cad as CAD
    import villa_colour as CC
    import villa_load as LD
    import villa_verify as VF
    import villa_show as SH

    import villa_furniture_spec as F
    items, _path = CAD.furniture_manifest()
    out = {
        "sanitary": {fl: sum(1 for _f, (k, x, y, r) in G.sheet_furniture(fl)
                             if k in CC.SANITARY and F.footprint(k, x, y, r))
                     for fl, _no, _t in G.plan_sheets()},
        "design": V.__file__,
        "plan_sheets": G.plan_sheets(),
        "cad_sheets": CAD.plan_sheets(),
        "colour_sheets": CC.plan_sheets(),
        "load_sheets": LD.SHEETS,
        "verify_sheets": VF.plan_sheets(),
        "show_mine": list(SH.MINE),
        "show_out": SH.OUT,
        "flights": {fl: [[f["name"], role] for f, role in G.flights_on(fl)]
                    for fl, _no, _t in G.plan_sheets()},
        "landings": [[n, list(r), z] for n, r, z in G.stair_landings()],
        "furniture": {fl: len(G.sheet_furniture(fl)) for fl, _no, _t in G.plan_sheets()},
        "on_sheet": {no: sorted({it["floor"] for it in items if fl and LD.on_sheet(it, fl)})
                     for no, _base, fl in LD.SHEETS},
        "stair_rects": {s["name"]: list(s["rect"]) for s in getattr(V, "STAIRS", [])},
        "voids": [[v[0], [v[1], v[2], v[3], v[4]], list(v[5])] for v in V.VOIDS],
        "levels": {k: v for k, v in V.LEVEL.items()},
        "pool_label": getattr(V, "POOL_LABEL", None),
        "project_line": G.project_line(),
        "ramp": CAD.ramp_text(),
    }
    print("@@" + json.dumps(out))
''')


def _env(out):
    env = {k: v for k, v in os.environ.items() if k not in ("VILLA_DESIGN_DIR",)}
    env["VILLA_OUT"] = out
    env["PYTHONPATH"] = ""
    return env


def run(args, out, timeout=600):
    r = subprocess.run([PY, "-X", "utf8"] + args, cwd=ROOT, env=_env(out),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    if r.returncode != 0:
        raise AssertionError(f"{args} exit {r.returncode}\n{r.stdout[-2000:]}\n"
                             f"{r.stderr[-3000:]}")
    return r.stdout


def probe(project=None):
    """The probe's JSON for the villa (project None) or a project design."""
    out = os.path.join(TMP, project or "villa")
    os.makedirs(out, exist_ok=True)
    script = os.path.join(TMP, "probe_sheets.py")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(PROBE)
    if project:
        text = run(["run_project.py", project, script], out)
    else:
        env = _env(out)
        env["PYTHONPATH"] = ROOT
        r = subprocess.run([PY, "-X", "utf8", script], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600)
        if r.returncode != 0:
            raise AssertionError(r.stdout[-2000:] + r.stderr[-3000:])
        text = r.stdout
    line = next(ln for ln in text.splitlines() if ln.startswith("@@"))
    return json.loads(line[2:])


def hidden_furniture(doc):
    """Furniture fills (A-FURN-FILL) drawn in the colour of the floor fill
    they sit on -- the floor fill drawn last under their centre, the one you
    see. Such a fill cannot be seen: the colour plans' wet rooms read as
    empty because their WC, basin and shower were "tile" on a "tile" floor."""
    from shapely.geometry import Polygon
    ents = list(doc.modelspace())

    def poly(h):
        return Polygon([(v[0], v[1]) for v in h.paths[0].vertices])

    floors = [(poly(h), h.rgb) for h in ents
              if h.dxftype() == "HATCH" and h.dxf.layer == "A-FLOR-FILL"]
    bad = []
    for h in ents:
        if h.dxftype() != "HATCH" or h.dxf.layer != "A-FURN-FILL":
            continue
        c = poly(h).centroid
        under = [rgb for g, rgb in floors if g.contains(c)]
        if under and h.rgb == under[-1]:
            bad.append((round(c.x), round(c.y), h.rgb))
    return bad


def fixture_outlines(doc):
    return sum(1 for e in doc.modelspace()
               if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "A-FLOR-FIXT")


def setUpModule():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


# ================================================================== villa
class VillaSheetLists(unittest.TestCase):
    """The villa's sheet lists are what they were (literals of the old code)."""

    @classmethod
    def setUpClass(cls):
        cls.p = probe()

    def test_design_is_the_villa(self):
        self.assertEqual(os.path.normcase(os.path.dirname(self.p["design"])),
                         os.path.normcase(ROOT))

    def test_plan_sheets(self):
        self.assertEqual(self.p["plan_sheets"], [["GF", "A-102", None], ["FF", "A-103", None]])
        self.assertEqual(self.p["cad_sheets"], [["GF", "A-102", "Ground floor plan"],
                                                ["FF", "A-103", "First floor plan"]])
        self.assertEqual(self.p["colour_sheets"],
                         [["GF", "A-102P", "Ground floor - presentation"],
                          ["FF", "A-103P", "First floor - presentation"]])

    def test_load_verify_show(self):
        self.assertEqual(self.p["load_sheets"], [
            ["A-101", "VILLA_A101", None], ["A-102", "VILLA_A102", "GF"],
            ["A-103", "VILLA_A103", "FF"], ["A-101P", "VILLA_A101P", None],
            ["A-102P", "VILLA_A102P", "GF"], ["A-103P", "VILLA_A103P", "FF"]])
        self.assertEqual(self.p["verify_sheets"], [["VILLA_A102", "GF"], ["VILLA_A103", "FF"]])
        self.assertEqual(self.p["show_mine"], [
            "VILLA_A101.dwg", "VILLA_A102.dwg", "VILLA_A103.dwg",
            "VILLA_A101P.dwg", "VILLA_A102P.dwg", "VILLA_A103P.dwg",
            "VILLA_3D_MODEL.dwg"])
        # villa_show's folder follows VILLA_OUT now (it was typed)
        self.assertEqual(os.path.normcase(self.p["show_out"]),
                         os.path.normcase(os.path.join(TMP, "villa")))

    def test_annex_furniture_on_the_ground_floor_sheet(self):
        self.assertIn("AX", self.p["on_sheet"]["A-102"])
        self.assertEqual(self.p["on_sheet"]["A-101"], [])

    def test_no_project_hooks(self):
        self.assertIsNone(self.p["pool_label"])
        self.assertIsNone(self.p["ramp"])


class VillaColourPlans(unittest.TestCase):
    """villa_colour runs for the villa into a temp folder: its wet rooms show
    their sanitaryware (gap 10, docs/model-routing section 5)."""

    @classmethod
    def setUpClass(cls):
        cls.out = os.path.join(TMP, "villa_colour")
        os.makedirs(cls.out, exist_ok=True)
        cls.p = probe()
        run(["villa_colour.py"], cls.out)

    def test_sanitaryware_seen_on_the_colour_plans(self):
        import ezdxf
        for fl, no, _t in self.p["colour_sheets"]:
            doc = ezdxf.readfile(os.path.join(self.out, f"VILLA_{no.replace('-', '')}.dxf"))
            self.assertEqual(hidden_furniture(doc), [], no)
            self.assertGreater(self.p["sanitary"][fl], 0, no)
            self.assertEqual(fixture_outlines(doc), self.p["sanitary"][fl], no)


# ================================================================ fairway
class FairwaySheetLists(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = probe("fairway")

    def test_design_is_the_fairway(self):
        self.assertIn(os.path.join("projects", "fairway"), self.p["design"])

    def test_plan_sheets_from_the_design(self):
        self.assertEqual(self.p["plan_sheets"], [["B1", "A-102", "BASEMENT PLAN"],
                                                 ["GF", "A-103", "GROUND FLOOR PLAN"],
                                                 ["FF", "A-104", "FIRST FLOOR PLAN"]])
        self.assertEqual(self.p["cad_sheets"], self.p["plan_sheets"])
        self.assertEqual(self.p["colour_sheets"], [
            ["B1", "A-102P", "BASEMENT PLAN - presentation"],
            ["GF", "A-103P", "GROUND FLOOR PLAN - presentation"],
            ["FF", "A-104P", "FIRST FLOOR PLAN - presentation"]])

    def test_load_verify_show(self):
        self.assertEqual(self.p["load_sheets"], [
            ["A-101", "VILLA_A101", None], ["A-102", "VILLA_A102", "B1"],
            ["A-103", "VILLA_A103", "GF"], ["A-104", "VILLA_A104", "FF"],
            ["A-101P", "VILLA_A101P", None], ["A-102P", "VILLA_A102P", "B1"],
            ["A-103P", "VILLA_A103P", "GF"], ["A-104P", "VILLA_A104P", "FF"]])
        self.assertEqual(self.p["verify_sheets"], [["VILLA_A102", "B1"], ["VILLA_A103", "GF"],
                                                   ["VILLA_A104", "FF"]])
        self.assertEqual(self.p["show_mine"], [
            "VILLA_A101.dwg", "VILLA_A102.dwg", "VILLA_A103.dwg", "VILLA_A104.dwg",
            "VILLA_A101P.dwg", "VILLA_A102P.dwg", "VILLA_A103P.dwg", "VILLA_A104P.dwg",
            "VILLA_3D_MODEL.dwg"])
        self.assertEqual(os.path.normcase(self.p["show_out"]),
                         os.path.normcase(os.path.join(TMP, "fairway")))

    def test_basement_furniture_on_the_basement_sheet(self):
        on = self.p["on_sheet"]
        for no in ("A-102", "A-102P"):
            self.assertEqual(on[no], ["B1"], no)
        for no in ("A-103", "A-103P"):
            self.assertEqual(on[no], ["GF"], no)
        for no in ("A-104", "A-104P"):
            self.assertEqual(on[no], ["FF"], no)
        self.assertEqual(on["A-101"], [])
        self.assertGreater(self.p["furniture"]["B1"], 0)

    def test_stair_flights_on_the_right_sheets(self):
        f = {fl: {tuple(x) for x in v} for fl, v in self.p["flights"].items()}
        self.assertEqual(f["B1"], {("service stair flight 1", "up"),
                                   ("service stair flight 2", "up")})
        self.assertEqual(f["GF"], {("feature stair", "up"),
                                   ("service stair flight 1", "down"),
                                   ("service stair flight 2", "down")})
        self.assertEqual(f["FF"], {("feature stair", "down")})
        self.assertEqual([l[0] for l in self.p["landings"]], ["service stair"])

    def test_title_line_and_ramp(self):
        self.assertTrue(self.p["project_line"].startswith("THE FAIRWAY VILLA"))
        self.assertEqual(self.p["ramp"], "RAMP 1:28 (3.6%)")


class FairwaySheets(unittest.TestCase):
    """villa_cad and villa_colour run for the Fairway into a temp folder."""

    @classmethod
    def setUpClass(cls):
        cls.out = os.path.join(TMP, "fairway_run")
        os.makedirs(cls.out, exist_ok=True)
        cls.p = probe("fairway")
        run(["run_project.py", "fairway", "villa_cad.py"], cls.out)
        run(["run_project.py", "fairway", "villa_colour.py"], cls.out)
        import ezdxf
        cls.docs = {}
        for no in ("A101", "A102", "A103", "A104"):
            for sfx in ("", "P"):
                cls.docs[no + sfx] = ezdxf.readfile(
                    os.path.join(cls.out, f"VILLA_{no}{sfx}.dxf"))

    @staticmethod
    def texts(doc):
        return [e.dxf.text for e in doc.modelspace() if e.dxftype() == "TEXT"]

    def test_every_file_written(self):
        from PIL import Image
        for no in ("A101", "A102", "A103", "A104"):
            for sfx in ("", "P"):
                for ext in (".dxf", ".png"):
                    path = os.path.join(self.out, f"VILLA_{no}{sfx}{ext}")
                    self.assertTrue(os.path.isfile(path), path)
                    self.assertGreater(os.path.getsize(path), 10000, path)
                with Image.open(os.path.join(self.out, f"VILLA_{no}{sfx}.png")) as im:
                    w, h = im.size
                self.assertGreater(min(w, h), 800)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "furniture_manifest.json")))
        with open(os.path.join(self.out, "furniture_manifest.json")) as fh:
            man = json.load(fh)
        self.assertTrue(any(it["floor"] == "B1" and it["sheet"] == "B1" for it in man))

    def test_sanitaryware_seen_on_the_colour_plans(self):
        for fl, no, _t in self.p["plan_sheets"]:
            doc = self.docs[no.replace("-", "") + "P"]
            self.assertEqual(hidden_furniture(doc), [], no + "P")
            self.assertEqual(fixture_outlines(doc), self.p["sanitary"][fl], no + "P")

    def test_no_empty_sheets(self):
        for name, doc in self.docs.items():
            self.assertGreater(len(doc.modelspace()), 80, name)
            self.assertEqual(len(doc.audit().errors), 0, name)

    def test_title_blocks(self):
        want = {"A102": ("A-102", "BASEMENT PLAN", "B1 FFL -3800", "BASEMENT NET"),
                "A103": ("A-103", "GROUND FLOOR PLAN", "GF FFL +200", "GF NET"),
                "A104": ("A-104", "FIRST FLOOR PLAN", "FF FFL +4300", "FF NET")}
        for no, (num, title, level, area) in want.items():
            for sfx in ("", "P"):
                t = self.texts(self.docs[no + sfx])
                self.assertIn(num + sfx, t, no + sfx)
                self.assertTrue(any(title in s and level in s for s in t), (no + sfx, t))
                self.assertTrue(any(s.startswith(area) for s in t), no + sfx)
                self.assertTrue(any(s.startswith("THE FAIRWAY VILLA") for s in t))
                self.assertTrue(any(s.startswith("VALIDATION") for s in t))

    def test_site_plan(self):
        for name in ("A101", "A101P"):
            t = self.texts(self.docs[name])
            self.assertIn(self.p["pool_label"], t, name)
            self.assertTrue(any(s.startswith("RAMP 1:28") for s in t), name)
            self.assertTrue(any("SUN LEDGE" in s for s in t), name)
        t = self.texts(self.docs["A101"])
        self.assertIn("BASEMENT BELOW (B1 FFL -3800)", t)
        self.assertIn("THE FAIRWAY VILLA", t)
        self.assertIn("SITE PLAN", t)
        layers = {e.dxf.layer for e in self.docs["A101"].modelspace()}
        self.assertTrue({"A-FLOR-BGRD", "A-SHDE-OVHD", "A-GRDS"} <= layers, layers)
        lay_p = {e.dxf.layer for e in self.docs["A101P"].modelspace()}
        self.assertTrue({"L-SITE-WATR", "L-SITE-LAWN", "L-SITE-DECK"} <= lay_p)

    @staticmethod
    def lines_in(doc, layers, rect):
        x0, y0, x1, y1 = rect
        n = 0
        for e in doc.modelspace():
            if e.dxftype() != "LINE" or e.dxf.layer not in layers:
                continue
            for p in (e.dxf.start, e.dxf.end):
                if x0 - 1 <= p.x <= x1 + 1 and y0 - 1 <= p.y <= y1 + 1:
                    n += 1
                    break
        return n

    def test_stairs_drawn_on_their_sheets(self):
        feat = self.p["stair_rects"]["feature stair"]
        serv = self.p["stair_rects"]["service stair"]
        S = ("A-FLOR-STRS", "A-FLOR-STRS-OVHD")
        for sfx in ("", "P"):
            b1, gf, ff = (self.docs[n + sfx] for n in ("A102", "A103", "A104"))
            # B1: the service stair, cut, overhead above the cut; no feature stair
            self.assertGreater(self.lines_in(b1, ("A-FLOR-STRS",), serv), 10)
            self.assertGreater(self.lines_in(b1, ("A-FLOR-STRS-OVHD",), serv), 10)
            self.assertEqual(self.lines_in(b1, S, feat), 0)
            self.assertIn("UP", self.texts(b1))
            # GF: the feature stair UP (cut and overhead), the service stair
            # DN seen down its well -- nothing of it under the GF landing
            self.assertGreater(self.lines_in(gf, ("A-FLOR-STRS",), feat), 10)
            self.assertGreater(self.lines_in(gf, ("A-FLOR-STRS-OVHD",), feat), 10)
            well = next(v[1] for v in self.p["voids"] if "GF" in v[2])
            self.assertGreater(self.lines_in(gf, ("A-FLOR-STRS",), well), 10)
            landing_band = (serv[0] + 1, serv[1] + 1, serv[2] - 1, well[1] - 5)
            self.assertEqual(self.lines_in(gf, S, landing_band), 0)
            t = self.texts(gf)
            self.assertIn("UP", t)
            self.assertIn("DN", t)
            # FF: the feature stair DN inside the void only
            void = next(v[1] for v in self.p["voids"] if "FF" in v[2])
            self.assertGreater(self.lines_in(ff, ("A-FLOR-STRS",), void), 10)
            north = (feat[0], void[3] + 5, feat[2], feat[3] + 1000)
            self.assertEqual(self.lines_in(ff, S, north), 0)
            self.assertEqual(self.lines_in(ff, S, serv), 0)
            self.assertIn("DN", self.texts(ff))

    def test_voids_balcony_fins_stone(self):
        gf, ff = self.docs["A103"], self.docs["A104"]
        self.assertIn("SERVICE STAIR WELL", self.texts(gf))
        self.assertIn("STAIR VOID", self.texts(ff))
        self.assertIn("BALCONY", self.texts(ff))
        self.assertIn("BALCONY OVER", self.texts(gf))
        lay_ff = {e.dxf.layer for e in ff.modelspace()}
        self.assertIn("A-SHDE-FINS", lay_ff)
        self.assertIn("A-WALL-CLAD", {e.dxf.layer for e in gf.modelspace()})
        self.assertIn("A-GRDS", lay_ff)


if __name__ == "__main__":
    unittest.main(verbosity=2)
