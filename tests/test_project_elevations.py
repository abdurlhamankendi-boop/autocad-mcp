"""Offline proof that villa_elevations draws the design it is given.

    python tests/test_project_elevations.py            (from the project folder)
    python -m unittest tests.test_project_elevations

No AutoCAD, no COM. Two designs, each in a subprocess of its own (both are
called villa_design); everything is written under %TEMP%:

  * the VILLA (villa_design.py here): every project hook is off (no own
    site, no own section, nothing below grade, no standing landscape), and
    the key functions give exactly what the ORIGINAL villa_elevations gives
    (the frozen copy in _pre_projects_0926, when present): building_levels,
    storey_levels, choose_cut, upper_envelope; the section still looks east
    from choose_cut(). A full run passes 46/46 checks with the same check
    lines as the original (tests/regress_villa.py diffs its sheets);
  * THE FAIRWAY (projects\\fairway, through run_project.py): the section is
    cut at SECTION_X looking WEST, through the STAIR VOID, with the feature
    stair seen beyond; its datums include B1 (the elevations' do not);
    VILLA_DESIGN_DIR alone (no run_project) puts the project's design in
    front; a full run writes A-201..A-204 and A-301 with every check PASSED
    -- stone, hedges, basement datum, double height, stairs.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
TMP = os.path.join(tempfile.gettempdir(), f"villa_project_elev_{os.getpid()}")
FAIRWAY = os.path.join(ROOT, "projects", "fairway")
FROZEN = os.path.join(ROOT, "_pre_projects_0926", "villa_elevations.py")

# Run inside a design: what villa_elevations would do with it, and -- for
# the villa -- what the frozen original does with the same design.
PROBE = textwrap.dedent(r'''
    import importlib.util, json, os, sys
    import villa_elevations as EL
    from shapely.geometry import Polygon, box

    V = EL.V
    x_cut, why = EL.choose_cut()
    view = EL.section_view()
    level = [box(0, 0, 1000, 200), box(1000, 0, 3000, 500), box(3500, -100, 5000, 100)]
    slope = [Polygon([(0, 0), (4000, 0), (4000, 400), (0, 0)]).buffer(0),
             box(4000, 0, 6000, 400)]
    out = {
        "design": V.__file__,
        "own_site": EL.OWN_SITE, "own_section": EL.OWN_SECTION, "below": list(EL.BELOW),
        "building_levels": EL.building_levels(),
        "section_levels": EL.section_levels(),
        "storey_levels": [[f, n, z] for f, n, z, _o in EL.storey_levels()],
        "choose_cut": [x_cut, why],
        "section_view": [view[0], view[2], view[3], view[4]],
        "cut_voids": [v[0] for v in EL.cut_voids(x_cut)],
        "stairs_seen": [s["name"] for s in EL.stairs_seen(x_cut, view[4])],
        "stairs_cut": [s["name"] for s in EL.stairs_cut(x_cut)],
        "standing": {g: len(v) for g, v in EL.standing_landscape().items()},
        "has_steps": bool(V.stairs_out()) if hasattr(V, "stairs_out") else None,
        "env_level": EL.upper_envelope(level),
        "env_slope": EL.upper_envelope(slope),
        "ground_z": EL.ground_z(EL.upper_envelope(slope), 2000.0),
    }
    frozen = os.environ.get("FROZEN_ELEV")
    if frozen and os.path.isfile(frozen):
        spec = importlib.util.spec_from_file_location("elev_frozen", frozen)
        OLD = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(OLD)
        d = os.path.dirname(frozen)
        while d in sys.path:
            sys.path.remove(d)
        out["old"] = {
            "design": OLD.V.__file__,
            "building_levels": OLD.building_levels(),
            "storey_levels": [[f, n, z] for f, n, z, _o in OLD.storey_levels()],
            "choose_cut": list(OLD.choose_cut()),
            "env_level": OLD.upper_envelope(level),
        }
    print("@@" + json.dumps(out))
''')


def _env(out, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("VILLA_DESIGN_DIR",)}
    env["VILLA_OUT"] = out
    env["PYTHONPATH"] = ""
    env.update(extra)
    return env


def _run(args, env, timeout=900, ok=True):
    r = subprocess.run([PY, "-X", "utf8"] + args, cwd=ROOT, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if ok and r.returncode != 0:
        raise AssertionError(f"{args} exit {r.returncode}\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    return r


def _json(text):
    line = next(ln for ln in text.splitlines() if ln.startswith("@@"))
    return json.loads(line[2:])


def _probe_script():
    os.makedirs(TMP, exist_ok=True)
    script = os.path.join(TMP, "probe_elev.py")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(PROBE)
    return script


def _checks(stdout):
    """[(PASS|FAIL, name, detail)] from a villa_elevations run."""
    out = []
    for ln in stdout.splitlines():
        m = re.match(r"\s+(PASS|FAIL)\s{2}(.+?)\s{2,}(.*)$", ln)
        if m:
            out.append((m.group(1), m.group(2).strip(), m.group(3)))
    return out


def _summary(stdout):
    m = re.search(r"(\d+)/(\d+) checks passed", stdout)
    return (int(m.group(1)), int(m.group(2))) if m else None


class _Base(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP, ignore_errors=True)


class VillaUntouched(_Base):
    """The villa: every hook off, the key functions as the original's."""

    @classmethod
    def setUpClass(cls):
        out = os.path.join(TMP, "villa")
        os.makedirs(out, exist_ok=True)
        env = _env(out, PYTHONPATH=ROOT, FROZEN_ELEV=FROZEN)
        cls.p = _json(_run([_probe_script()], env).stdout)

    def test_design_is_the_villa(self):
        self.assertEqual(os.path.normcase(os.path.dirname(self.p["design"])),
                         os.path.normcase(ROOT))

    def test_hooks_off(self):
        p = self.p
        self.assertFalse(p["own_site"])
        self.assertFalse(p["own_section"])
        self.assertEqual(p["below"], [])
        self.assertEqual(p["standing"], {})
        # the villa has external steps: the elevations add no N/A steps check
        self.assertTrue(p["has_steps"])

    def test_section_looks_east_from_choose_cut(self):
        p = self.p
        self.assertEqual(p["section_view"][0], p["choose_cut"][0])
        self.assertEqual(p["section_view"][1:], [[-1, 0, 0], "EAST", 1])
        # the section's datums are the elevations' (nothing below grade)
        self.assertEqual(p["section_levels"], p["building_levels"])

    def test_upper_envelope_level_tops_unchanged(self):
        self.assertEqual(self.p["env_level"],
                         [[[0.0, 200.0], [1000.0, 200.0], [1000.0, 500.0], [3000.0, 500.0]],
                          [[3500.0, 100.0], [5000.0, 100.0]]])

    def test_key_functions_equal_the_original(self):
        old = self.p.get("old")
        if not old:
            self.skipTest("the frozen original (_pre_projects_0926) is not here")
        self.assertEqual(old["design"], self.p["design"])
        for k in ("building_levels", "storey_levels", "choose_cut", "env_level"):
            self.assertEqual(self.p[k], old[k], k)

    def test_full_run_matches_the_original(self):
        new_out = os.path.join(TMP, "villa_run_new")
        os.makedirs(new_out, exist_ok=True)
        r = _run(["villa_elevations.py"], _env(new_out, PYTHONPATH=ROOT))
        self.assertEqual(_summary(r.stdout), (46, 46), r.stdout[-3000:])
        if not os.path.isfile(FROZEN):
            return
        old_out = os.path.join(TMP, "villa_run_old")
        os.makedirs(old_out, exist_ok=True)
        # the frozen script puts its own folder first: copy it out, so it
        # imports this folder's modules (PYTHONPATH) like the new one
        src = os.path.join(TMP, "frozen_src")
        os.makedirs(src, exist_ok=True)
        shutil.copy(FROZEN, os.path.join(src, "villa_elevations_frozen.py"))
        ro = _run([os.path.join(src, "villa_elevations_frozen.py")],
                  _env(old_out, PYTHONPATH=ROOT))
        self.assertEqual([c[:2] for c in _checks(r.stdout)], [c[:2] for c in _checks(ro.stdout)])
        self.assertEqual([c[2] for c in _checks(r.stdout) if "DXF + PNG" not in c[1]],
                         [c[2] for c in _checks(ro.stdout) if "DXF + PNG" not in c[1]])


class FairwayProbe(_Base):
    """The Fairway's hooks, read by the functions the sheets are drawn with."""

    @classmethod
    def setUpClass(cls):
        out = os.path.join(TMP, "fairway")
        os.makedirs(out, exist_ok=True)
        cls.p = _json(_run(["run_project.py", "fairway", _probe_script()], _env(out)).stdout)

    def test_design_is_the_fairways(self):
        self.assertEqual(os.path.normcase(os.path.dirname(self.p["design"])),
                         os.path.normcase(FAIRWAY))

    def test_hooks_on(self):
        p = self.p
        self.assertTrue(p["own_site"])
        self.assertTrue(p["own_section"])
        self.assertEqual(p["below"], ["B1"])
        self.assertIn("planting", p["standing"])            # the hedges
        self.assertNotIn("terrain", p["standing"])
        self.assertFalse(p["has_steps"])                    # level thresholds

    def test_datums(self):
        p = self.p
        names = [n for n, _z in p["building_levels"]]
        self.assertNotIn("B1", names)                       # not on an elevation
        self.assertIn(["B1", -3800.0], p["section_levels"])
        for n in ("STREET", "GF", "FF", "RF", "T/PARAPET"):
            self.assertIn(n, [n_ for n_, _z in p["section_levels"]])
        self.assertEqual(p["storey_levels"], [])

    def test_section_cut_and_direction(self):
        p = self.p
        self.assertEqual(p["choose_cut"][0], 17800.0)
        self.assertEqual(p["section_view"][1:], [[1, 0, 0], "WEST", -1])
        self.assertEqual(p["cut_voids"], ["STAIR VOID"])
        self.assertEqual(p["stairs_seen"], ["feature stair"])
        self.assertEqual(p["stairs_cut"], [])

    def test_sloped_ground_followed(self):
        env = self.p["env_slope"]
        self.assertEqual(len(env), 1)
        pts = env[0]
        self.assertAlmostEqual(pts[0][0], 0.0, places=3)
        self.assertAlmostEqual(pts[0][1], 0.0, places=3)
        self.assertIn([4000.0, 400.0], [[round(a, 3), round(b, 3)] for a, b in pts])
        self.assertAlmostEqual(self.p["ground_z"], 200.0, places=3)


class DesignDirHonoured(_Base):
    """VILLA_DESIGN_DIR alone (no run_project) puts the project in front."""

    def test_design_dir(self):
        out = os.path.join(TMP, "designdir")
        os.makedirs(out, exist_ok=True)
        p = _json(_run([_probe_script()],
                       _env(out, PYTHONPATH=ROOT, VILLA_DESIGN_DIR=FAIRWAY)).stdout)
        self.assertEqual(os.path.normcase(os.path.dirname(p["design"])),
                         os.path.normcase(FAIRWAY))
        self.assertTrue(p["own_section"])


class FairwayRun(_Base):
    """A full run for the Fairway: five sheets, every check passed."""

    @classmethod
    def setUpClass(cls):
        cls.out = os.path.join(TMP, "fairway_run")
        os.makedirs(cls.out, exist_ok=True)
        cls.r = _run(["run_project.py", "fairway", "villa_elevations.py"], _env(cls.out),
                     ok=False)
        cls.checks = _checks(cls.r.stdout)
        cls.by = {c[1]: c for c in cls.checks}

    def test_exit_and_all_checks_pass(self):
        self.assertEqual(self.r.returncode, 0, self.r.stdout[-4000:] + self.r.stderr[-3000:])
        fails = [c for c in self.checks if c[0] != "PASS"]
        self.assertEqual(fails, [])
        s = _summary(self.r.stdout)
        self.assertIsNotNone(s)
        self.assertEqual(s[0], s[1])
        self.assertGreaterEqual(s[1], 50)

    def test_sheets_written(self):
        for no in ("A201", "A202", "A203", "A204", "A301"):
            for ext in (".dxf", ".png"):
                p = os.path.join(self.out, f"VILLA_{no}{ext}")
                self.assertTrue(os.path.isfile(p), p)
                self.assertGreater(os.path.getsize(p), 20_000, p)

    def _passed(self, name):
        self.assertIn(name, self.by, sorted(self.by))
        self.assertEqual(self.by[name][0], "PASS", self.by[name])
        return self.by[name][2]

    def test_elevation_checks(self):
        for k, n in (("S", 8), ("N", 10), ("E", 8), ("W", 5)):
            d = self._passed(f"{k} elevation: external openings drawn")
            self.assertIn(f"/{n} drawn", d)
            self._passed(f"{k} elevation: ground line = villa_design.ground_at")
            self._passed(f"{k} elevation: level datums sit on model edges")
            self.assertIn("N/A", self._passed(f"{k} elevation: external steps drawn"))
        for k in ("S", "N", "E"):
            self._passed(f"{k} elevation: stone drawn where STONE_ZONES put it")
        self._passed("E elevation: street end (north) on the right")
        self._passed("W elevation: street end (north) on the left")
        self._passed("S elevation: west fins on the left")

    def test_section_checks(self):
        self.assertIn("WEST", self._passed("A-A: cut passes through the double-height void"))
        self._passed("A-A: double-height STAIR VOID open GF to RF")
        self._passed("A-A: FF slab open over the STAIR VOID")
        self._passed("A-A: feature stair rises GF to FF")
        self._passed("A-A: service stair rises B1 to GF")
        self.assertIn("23/23", self._passed("A-A: feature stair drawn beyond the cut"))
        d = self._passed("A-A: level datums sit on cut edges")
        for mark in ("B1  -3800", "GF  +200", "FF  +4300", "T/PARAPET  +8900",
                     "POOL TWL  +100", "POOL FLOOR  -1400", "SUN LEDGE  -200"):
            self.assertIn(mark, d)

    def test_section_sheet_texts(self):
        import ezdxf
        doc = ezdxf.readfile(os.path.join(self.out, "VILLA_A301.dxf"))
        texts = [e.dxf.text for e in doc.modelspace() if e.dxftype() == "TEXT"]
        self.assertTrue(any(t.startswith("B1  -3800") for t in texts), texts)
        self.assertTrue(any("LOOKING WEST" in t and "BASEMENT LOUNGE" in t for t in texts))
        self.assertIn("NORTH  (STREET)", texts)
        self.assertIn("POOL 4.5 x 9.0 m", texts)
        self.assertNotIn("BASIN", texts)
        layers = {e.dxf.layer for e in doc.modelspace()}
        self.assertIn("A-SECT-EART", layers)                # the basement's earth
        e = ezdxf.readfile(os.path.join(self.out, "VILLA_A203.dxf"))
        self.assertTrue(any(h.dxftype() == "HATCH" and h.dxf.layer == "A-ELEV-PATT"
                            for h in e.modelspace()))      # the east flank's stone


if __name__ == "__main__":
    unittest.main(verbosity=2)
