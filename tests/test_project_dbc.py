"""Fault injection for villa_dbc on a design with a basement and two stairs.

    python tests\\test_project_dbc.py            (from the pipeline folder)
    python -m unittest tests.test_project_dbc -v

The Fairway villa (projects\\fairway\\villa_design.py) is imported as
`villa_design` -- its folder first on sys.path, as run_project.py does -- and
patched IN MEMORY only (the file is never edited). Each test breaks one thing
and asserts that villa_dbc.checks() fires with the rule it should cite, and
where the fix was a false negative or a false positive, that the fixed
reading is the one that holds:

  * inside-house guards: the ground floor round the service stair's well
    (never walked before: a false negative), the first floor round the hall's
    void, the feature stair's glass, the open risers under the floating
    treads (K-GRD-03: closed below 100, open from 100), a door under the high
    end of the feature stair (passable only up to its head), a basement
    flight judged against the basement (a finite drop, not 1e9), the service
    stair's solid (stair_columns) closing flight 1's inner side;
  * handrails (K-HR-01), and the fill under the ground-floor landing that
    closes the service stair's lower flight at its foot;
  * stairs: K-STR-03/-04/-09/-11 per flight and per half-landing;
  * rooms: K-ROOM-01/-02 on the net floor (less the nested en-suite);
  * basement: K-BSMT-01..06.

The Fairway as designed is clean (0 FATAL / 0 MAJOR): the faults these
checks first found in it -- the bedroom 4/5 en-suites, the maid bath, the
master's south band, the service stair's 1320 half-landing and the open side
of its first tread -- were fixed in the design, and each is re-injected here
as it was and must fire again.

TestVillaUnchanged runs villa_dbc.py on the villa in a subprocess: its report
must still be "0 fatal, 0 major".
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJECT = os.path.join(ROOT, "projects", "fairway")
os.environ.setdefault("VILLA_OUT", os.path.join(tempfile.gettempdir(), "fairway_dbc_test"))
sys.dont_write_bytecode = True

V = D = None


def setUpModule():
    global V, D
    for p in (ROOT, PROJECT):                     # the project folder ends up first
        while p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    for m in [m for m in sys.modules if m.startswith("villa_")]:
        sys.modules.pop(m, None)
    import villa_design
    import villa_dbc
    V, D = villa_design, villa_dbc
    assert os.path.normcase(os.path.dirname(os.path.abspath(V.__file__))) == \
        os.path.normcase(PROJECT), V.__file__


_MISSING = object()


def issues(**patch):
    """villa_dbc.checks() on the design with `patch` set on it (restored)."""
    saved = {k: V.__dict__.get(k, _MISSING) for k in patch}
    try:
        for k, v in patch.items():
            setattr(V, k, v)
        return D.checks()
    finally:
        for k, v in saved.items():
            if v is _MISSING:
                delattr(V, k)
            else:
                setattr(V, k, v)


def failing(iss):
    return [i for i in iss if i.startswith(("[FATAL]", "[MAJOR]"))]


def text(iss):
    return "\n".join(iss)


class TestAsDesigned(unittest.TestCase):
    """The Fairway as designed (after the main session fixed the faults these
    checks found -- the en-suites, the maid bath, the service stair's well
    and the fill under its landing) passes. Each of those faults is
    re-injected below and must fire again."""

    def test_the_four_former_majors_are_gone(self):
        t = text(D.checks())
        # 1. the floating treads' back edges: closed by K-GRD-03 (171 - 90 = 81 < 100)
        self.assertNotRegex(t, r"\[MAJOR\] feature stair at ")
        # 2. a basement flight judged against the basement, the stair's own solid known
        self.assertNotIn("999996374", t)
        self.assertNotRegex(t, r"\[MAJOR\] service stair flight 1 at ")
        # 3. the hall -> service stair door is wall above its head (+2600)
        self.assertNotRegex(t, r"feature stair: its open (west|east)")
        # 4. flight 2's solid mass (and the fill under the ground-floor
        # landing, beside the first tread) closes flight 1's inner side
        self.assertNotRegex(t, r"service stair flight 1: its open")

    def test_as_designed_is_clean(self):
        iss = D.checks()
        self.assertEqual(failing(iss), [], text(iss))

    def test_the_sphere_is_the_rules_files(self):
        import json
        with open(D.RULES_FILE, encoding="utf-8") as fh:
            rules = {r["id"]: r for r in json.load(fh)["rules"]}
        want = next(v["value"] for v in rules["K-GRD-03"]["values"]
                    if v["name"] == "infill_sphere")
        self.assertEqual(D.SPHERE, want)
        self.assertEqual(want, 100)

    def test_basement_notes(self):
        t = text(D.checks())
        self.assertRegex(t, r"\[NOTE \] B1: K-BSMT-03 .*CINEMA, MEDIA LOUNGE, GYM, WINE CELLAR, "
                            r"PLAY ROOM \(amenity\); PLANT ROOM, STORE, LAUNDRY, LINEN STORE "
                            r"\(service\) -- non-habitable recreation/service rooms, "
                            r"mechanically ventilated \(BRIEF assumption A9\)")
        self.assertRegex(t, r"\[NOTE \] B1: not modelled -- sump pits .*K-BSMT-05")
        self.assertRegex(t, r"\[NOTE \] B1: not modelled -- .*emergency lighting.*K-BSMT-06")


class TestGuards(unittest.TestCase):
    """K-GRD-01/-02, K-SGR-01/-02, K-GRD-03 inside the house."""

    def test_no_well_guard_round_the_service_stair(self):
        # was a FALSE NEGATIVE: the ground floor round a well was never walked
        lab = V.guards_labelled
        t = text(issues(guards_labelled=lambda: [
            g for g in lab() if not (g[0] == "stair well" and abs(g[1][4] - V.GF) < 1)]))
        # over flight 1 (x 9550-11050): 200 - (-3452) = 3652; the last 50 mm
        # at the split line is covered by flight 2's own glass
        m = re.search(r"\[MAJOR\] ground floor round the service stair well at \+200: "
                      r"(\d+) mm .*up to 3652 mm .*K-GRD-01", t)
        self.assertTrue(m, t)
        self.assertGreaterEqual(int(m.group(1)), 1400)
        self.assertNotIn("first floor round", t)

    def test_no_guard_round_the_hall_void(self):
        lab = V.guards_labelled
        t = text(issues(guards_labelled=lambda: [
            g for g in lab() if not (g[0] == "stair well" and abs(g[1][4] - V.FF) < 1)]))
        self.assertRegex(t, r"\[MAJOR\] first floor round the stair void at \+4300: .*K-GRD-01")
        self.assertNotIn("ground floor round", t)

    def test_no_glass_on_the_feature_stair(self):
        lab = V.guards_labelled
        t = text(issues(guards_labelled=lambda: [
            g for g in lab() if not (g[0] == "stair flight" and g[1][0] > 12700)]))
        self.assertRegex(t, r"\[MAJOR\] feature stair at \+\d+: .*K-SGR-02")
        self.assertNotRegex(t, r"\[MAJOR\] service stair flight \d at ")

    def test_no_glass_on_the_service_stair(self):
        # its upper flight stands over the lower one: judged against the
        # BASEMENT's floor and the stair's own solid -- a finite drop
        lab = V.guards_labelled
        t = text(issues(guards_labelled=lambda: [
            g for g in lab() if not (g[0] == "stair flight" and g[1][0] < 12700)]))
        m = re.search(r"\[MAJOR\] service stair flight 2 at ([-+]\d+): (\d+) mm .*up to (\d+) mm", t)
        self.assertTrue(m, t)
        self.assertLess(int(m.group(3)), 4000)           # a storey, not 1e9
        self.assertNotRegex(t, r"\[MAJOR\] feature stair at ")

    def _feature_waist(self, waist):
        stairs = [dict(s, waist=waist) if s["name"] == "feature stair" else s for s in V.STAIRS]
        return text(issues(STAIRS=stairs))

    def test_open_risers_pass_a_sphere_from_100(self):
        # 171 riser - 60 tread = 111 >= 100: every back edge is open over the hall
        t = self._feature_waist(60.0)
        m = re.search(r"\[MAJOR\] feature stair at \+\d+: (\d+) mm of its edge", t)
        self.assertTrue(m, t)
        self.assertGreater(int(m.group(1)), 20000)      # 23 treads x 1250 back edge
        # 171 - 75 = 96 < 100: closed
        self.assertNotRegex(self._feature_waist(75.0), r"\[MAJOR\] feature stair at ")

    def test_the_door_under_the_feature_stair_counts_to_its_head(self):
        # a door as high as the first floor would open the stair's west side
        # to the service stair's landing; at +2600 it is wall over the treads
        t = text(issues(DOOR_HEAD=4400.0))
        self.assertRegex(t, r"\[MAJOR\] feature stair: its open west side has no handrail")
        self.assertRegex(t, r"\[MAJOR\] feature stair at \+\d+: .*K-SGR-02")

    def test_the_service_stair_solid_closes_flight_1(self):
        # without its solid (floating treads), flight 1's inner side is open
        # over the basement along its whole run
        stairs = [dict(s, solid=False) if s["name"] == "service stair" else s
                  for s in V.STAIRS]
        t = text(issues(STAIRS=stairs))
        self.assertRegex(t, r"\[MAJOR\] service stair flight 1 at [-+]\d+: .*K-SGR-02")
        m = re.search(r"service stair flight 1: its open east side .*\(open at y (\d+)-(\d+)", t)
        self.assertTrue(m, t)
        self.assertGreater(int(m.group(2)) - int(m.group(1)), 2500)


class TestHandrails(unittest.TestCase):
    def test_the_fill_closes_flight_1s_foot(self):
        # without the solid under the ground-floor landing, flight 1's first
        # tread stands one riser (174) over the basement floor beside it
        stairs = [{k: v for k, v in s.items() if k != "fill"} for s in V.STAIRS]
        self.assertRegex(text(issues(STAIRS=stairs)),
                         r"\[MAJOR\] service stair flight 1: its open east side has no handrail "
                         r".*\(open at y 23750-24030, 11050 across, up to 174 mm .*K-HR-01")

    def test_no_handrails(self):
        t = text(issues(handrails=lambda: []))
        self.assertRegex(t, r"\[MAJOR\] feature stair: its open east side has no handrail")
        self.assertRegex(t, r"\[MAJOR\] service stair flight 2: its open west side has no handrail")
        self.assertIn("K-HR-01", t)


class TestStairs(unittest.TestCase):
    def test_riser(self):
        stairs = [dict(s, risers=20) if s["name"] == "service stair" else s for s in V.STAIRS]
        self.assertRegex(text(issues(STAIRS=stairs)),
                         r"\[FATAL\] service stair flight 1: riser 200.0 mm outside 100-180.*K-STR-03")

    def test_last_riser(self):
        orig = V.flights
        t = text(issues(flights=lambda: [dict(f, n=f["n"] - 1) if f["name"] == "feature stair"
                                         else f for f in orig()]))
        self.assertRegex(t, r"\[FATAL\] feature stair arrives at \+4129, 171 mm off .*K-STR-04")

    def test_headroom(self):
        # no void over the hall: the first-floor slab over the feature stair
        voids = [v for v in V.VOIDS if v[0] != "STAIR VOID"]
        self.assertRegex(text(issues(VOIDS=voids)),
                         r"\[FATAL\] feature stair: -?\d+ mm headroom over the nosing line .*K-STR-11")

    def test_headroom_at_the_limit(self):
        # as designed: 3800 soffit over the nosing at y 27200 (+1469) = 2331
        h, at = D._headroom(next(f for f in V.flights() if f["name"] == "feature stair"),
                            D._slabs())
        self.assertAlmostEqual(h, 2331, delta=1)
        self.assertAlmostEqual(at, 27200, delta=1)

    @staticmethod
    def _service_well(y1):
        return [dict(s, rect=(9550.0, 22650.0, 12550.0, y1))
                if s["name"] == "service stair" else s for s in V.STAIRS]

    def test_landing_depth(self):
        # as designed: the well to y 28350, the half-landing 1520 >= 1485 clear
        self.assertNotIn("K-STR-09", text(D.checks()))
        # the well as it was, to y 28150: 1320 deep, narrower than the flights
        self.assertRegex(text(issues(STAIRS=self._service_well(28150.0))),
                         r"\[MAJOR\] service stair half-landing \(9550,26830\)-\(12550,28150\) "
                         r"is 1320 mm deep .*narrower than service stair flight \d "
                         r"\(1485 clear\).*K-STR-09")
        # to y 27800: 970 < 1000
        self.assertRegex(text(issues(STAIRS=self._service_well(27800.0))),
                         r"\[FATAL\] service stair half-landing .* is 970 mm deep in the "
                         r"direction of travel < 1000.*K-STR-09")


class TestBasement(unittest.TestCase):
    def test_habitable_room_below_grade(self):
        rooms = [(r[0], *r[1:5], V.HAB, r[6]) if r[0] == "CINEMA" else r for r in V.ROOMS]
        t = text(issues(ROOMS=rooms))
        self.assertRegex(t, r"\[FATAL\] B1 CINEMA is habitable below grade with 0.00 m2 .*K-BSMT-03")

    def test_open_to_the_lobby(self):
        ops = [(o[0], V.OPEN) + tuple(o[2:]) if (o[0], o[7], o[8]) == ("B1", "CORE STAIR (B1)",
                                                                          "B1 LOBBY") else o
               for o in V.OPENINGS]
        self.assertRegex(text(issues(OPENINGS=ops)),
                         r"\[FATAL\] service stair: on B1 its room CORE STAIR \(B1\) opens to "
                         r"B1 LOBBY through an open opening, not a door.*K-BSMT-04")

    def test_spiral(self):
        # The design's flights() builds only straight and dog-leg stairs, so
        # the record keeps type "dogleg" for it (s["type"]) and says "spiral"
        # to whoever asks s.get("type") -- as villa_dbc does.
        class Spiral(dict):
            def get(self, k, d=None):
                return "spiral" if k == "type" else super().get(k, d)
        stairs = [Spiral(s) if s["name"] == "service stair" else s for s in V.STAIRS]
        self.assertRegex(text(issues(STAIRS=stairs)),
                         r"\[FATAL\] service stair serves the basement and is a spiral stair")

    def test_floating_basement_stair(self):
        stairs = [dict(s, solid=False) if s["name"] == "service stair" else s
                  for s in V.STAIRS]
        self.assertRegex(text(issues(STAIRS=stairs)),
                         r"\[FATAL\] service stair flight 1 serves the basement with floating "
                         r"treads .*K-BSMT-04")

    def test_no_basement_stair(self):
        stairs = [s for s in V.STAIRS if s["name"] != "service stair"]
        self.assertRegex(text(issues(STAIRS=stairs)),
                         r"\[FATAL\] B1 is served by no stair.*K-BSMT-04")

    def test_soffit_over_the_gate(self):
        self.assertRegex(text(issues(GATE_LEVEL=-2000.0)),
                         r"\[FATAL\] B1: the slab over it has its soffit at -300, 1700 mm over "
                         r"the gate level \(-2000\) > 1500.*K-BSMT-01")

    def test_beyond_the_plot(self):
        rooms = [(r[0], -500.0, *r[2:]) if r[0] == "STORE" and r[6] == "B1" else r
                 for r in V.ROOMS]
        self.assertRegex(text(issues(ROOMS=rooms)), r"\[FATAL\] B1 .*extends beyond the plot.*K-BSMT-02")


class TestRooms(unittest.TestCase):
    """K-ROOM-01/-02 on the room's NET floor: the faults these checks found
    in the Fairway, re-injected with the nested rooms as they were."""

    @staticmethod
    def _rooms(**rects):
        return [(r[0],) + tuple(rects[r[0]]) + tuple(r[5:]) if r[0] in rects else r
                for r in V.ROOMS]

    def test_bedroom_en_suite_as_it_was(self):
        # BEDROOM 4 (4550 x 5000) with its 2300 x 2500 en-suite in the corner:
        # legs 2100 and 2350 wide, nowhere 3 m clear
        t = text(issues(ROOMS=self._rooms(**{"BEDROOM 4 ENS": (3400, 22200, 5700, 24700)})))
        self.assertRegex(t, r"\[FATAL\] BEDROOM 4 is 2350 mm wide < 3000 \(DBC K-ROOM-01 p.706\) "
                            r"-- FF \(3400,22200\)-\(7950,27200\) less BEDROOM 4 ENS\n")
        self.assertNotIn("BEDROOM 5 is", t)

    def test_maid_bath_as_it_was(self):
        t = text(issues(ROOMS=self._rooms(**{"MAID BATH": (3400, 24650, 5250, 26650)})))
        self.assertRegex(t, r"\[FATAL\] MAID ROOM 7.7 m2 / 1850 mm below 5.5 m2 / 2100 "
                            r"\(DBC K-ROOM-02 p.706\) -- GF .* less MAID BATH")

    def test_master_as_it_was(self):
        # the band along the glass 2650 deep; a 3700 x 6500 part meets both
        # minima -- flagged, and the message says the reading it depends on
        t = text(issues(ROOMS=self._rooms(**{"MASTER ENSUITE": (22400, 16700, 26600, 20400),
                                             "MASTER DRESSING": (15400, 17400, 18400, 20400)})))
        self.assertRegex(t, r"\[FATAL\] MASTER BEDROOM is 2650 mm wide < 3000 .*K-ROOM-01.*"
                            r"a 3700 x 6500 part of it meets 3000 and 10.5 m2: reading-dependent")

    def test_the_net_floor_not_the_rectangle(self):
        # the room rectangle alone (the old measure) would pass all of these
        rooms = self._rooms(**{"BEDROOM 4 ENS": (3400, 22200, 5700, 24700)})
        b4 = next(r for r in rooms if r[0] == "BEDROOM 4")
        self.assertGreaterEqual(min(b4[3] - b4[1], b4[4] - b4[2]), 3000)
        saved = V.ROOMS
        try:
            V.ROOMS = rooms
            self.assertEqual(D._clear(b4, 10.5)[0], 2350)
        finally:
            V.ROOMS = saved

    def test_rule_values_are_read(self):
        self.assertEqual(D.val("K-ROOM-01", "min_dimension"), 3.0)
        self.assertEqual(D.val("K-ROOM-02", "min_dimension"), 2.1)
        self.assertEqual(D.val("K-COR-01", "clear_width"), 1.0)


class TestDaylightAndSite(unittest.TestCase):
    def test_parking_shade_only_if_light_and_over_the_porch(self):
        t = text(D.checks())
        self.assertRegex(t, r"\[NOTE \] shading element 2 at x 3400-9400 y 33200-39200 stands "
                            r"1840 mm into the setback over the car porch.*K-SB-05")
        heavy = [s if s[1] < 30000 else (s[0], s[1], s[2], s[3], 2400.0, 2850.0)
                 for s in V.SHADES]                            # a 450 slab
        self.assertRegex(text(issues(SHADES=heavy)),
                         r"\[FATAL\] shading element 2 .*projects 1840 mm into the 3000 setback"
                         r".*K-PRJ-03")
        wide = [s if s[1] < 30000 else (s[0], s[1], 11000.0, s[3], s[4], s[5])
                for s in V.SHADES]                             # past the porch
        self.assertRegex(text(issues(SHADES=wide)), r"\[FATAL\] shading element 2 .*K-PRJ-03")

    def test_sitting_and_lounge_need_ten_percent(self):
        ops = [o for o in V.OPENINGS if not (o[8] is None and o[7] in ("SITTING ROOM",
                                                                       "FAMILY LOUNGE"))]
        ops += [("GF", V.WIN, "v", 26600, 27000, 23600, 24300, "SITTING ROOM", None, None),
                ("FF", V.WIN, "v", 26600, 27000, 23600, 24300, "FAMILY LOUNGE", None, None)]
        t = text(issues(OPENINGS=ops))
        self.assertRegex(t, r"\[FATAL\] SITTING ROOM net glazing .*K-WIN-01")
        self.assertRegex(t, r"\[FATAL\] FAMILY LOUNGE net glazing .*K-WIN-01")

    def test_parking_behind_the_boundary_wall(self):
        # a 1.5 m street wall leaves 5660 of forecourt < 5500? no: 40360-1500-33200 = 5660
        self.assertNotIn("K-PARK-03", text(issues(BOUNDARY_T=1500.0)))
        self.assertRegex(text(issues(BOUNDARY_T=1700.0)), r"\[FATAL\] parking 5460 x 6000.*K-PARK-03")


class TestVillaUnchanged(unittest.TestCase):
    def test_villa_report(self):
        env = {k: v for k, v in os.environ.items() if k != "VILLA_DESIGN_DIR"}
        env["PYTHONPATH"] = ""
        r = subprocess.run([sys.executable, "-X", "utf8", "villa_dbc.py"], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip().splitlines(),
                         ["Dubai Building Code 2021: 146 rules loaded", "0 fatal, 0 major"])


if __name__ == "__main__":
    unittest.main()
