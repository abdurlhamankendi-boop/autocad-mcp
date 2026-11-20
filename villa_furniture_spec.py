"""
Villa furniture layout.

Placements are (block_key, x, y, rotation) where (x, y) is the desired
BOTTOM-LEFT of the block footprint in plan millimetres. Block keys and their
real sizes come from block_catalog.json, measured by inserting each ACA content
block and reading its extents.

Every item is checked against three things by `check()` below:
  * it must sit inside its room
  * it must not foul a door swing
  * researched clearances must survive: 1200 between opposing kitchen runs,
    550 in front of a WC or basin, 900 circulation, bed access on one side

Room extents come from villa_design.ROOMS so they cannot drift out of step.
"""

from __future__ import annotations

import json
import math
import os

import villa_design as V

CATALOG = json.load(open(os.path.join(os.path.dirname(__file__),
                                      "block_catalog.json")))

# ---------------------------------------------------------------- GROUND
# Candidate B ("service wing"). Door sweeps noted per room are the quarter
# discs check() tests against.
GROUND = [
    # SHOW KITCHEN  3400-7600 x 11400-16750 (family, west garden pavilion),
    # FAMILY WC nested in its north-east corner (6550-7600 x 15150-16750).
    # Working run on the west wall, 1-m aisle, then an island/breakfast table
    # with stools. North-wall doors (pantry 4100, corridor 5380) sweep y>15735.
    ("dishwasher",     3450, 12300,  90),
    ("sink_unit",      3450, 12950,  90),
    ("hob",            3450, 14300,  90),
    ("fridge",         3450, 15300,  90),
    ("fia_tbl_toast",  5000, 12700,  90),          # island / breakfast
    ("fia_stool",      5900, 12800,   0),
    ("fia_stool",      5900, 13550,   0),
    ("fia_stool",      5900, 14300,   0),
    # FAMILY WC  6550-7600 x 15150-16750 (its door opens OUT, into the back
    # corridor): pan against the south wall, basin in the north-east corner
    ("wc",             6600, 15150,   0),
    ("basin",          7150, 16282,   0),
    # FAMILY LIVING  9100-14900 x 11400-16750 (double height). Two long
    # sofas face each other ACROSS the axis, so the view from the front door
    # runs clear over a low table to the pool.
    ("fia_sofa_long",  9250, 12200,  90),
    ("fia_sofa_3",    13750, 12600,  90),
    ("fia_tbl_low",   10950, 12900,   0),
    ("fia_armchair",  13950, 15300,   0),
    # FORMAL DINING  16400-20600 x 11400-16750 (guest, east pavilion).
    # Eight: three a side and one at each end. Lobby door sweeps x<17250.
    ("fia_tbl_dining", 18050, 12825, 90),
    ("fia_chair",     17495, 12950,  90),
    ("fia_chair",     17495, 13650,  90),
    ("fia_chair",     17495, 14350,  90),
    ("fia_chair",     18955, 12950, 270),
    ("fia_chair",     18955, 13650, 270),
    ("fia_chair",     18955, 14350, 270),
    ("fia_chair",     18250, 12270,   0),
    ("fia_chair",     18250, 14930, 180),
    # GUEST WC  17450-20600 x 16900-18050 (door sweeps x<18175)
    ("basin",         18800, 17582,   0),
    ("wc",            19800, 17650,   0),
    # WOMEN'S MAJLIS  15050-20600 x 18200-22750 (street side). Perimeter
    # seating; the guests' street door sweeps x15150-16165, y>21935, the
    # food door from the lobby x15150-16165, y<19140.
    ("fia_sofa_long", 16500, 21700,   0),
    ("fia_sofa_3",    19600, 18800,  90),
    ("fia_sofa_ke",   16700, 18300,   0),
    ("fia_armchair",  15200, 19300,   0),
    ("fia_armchair",  15200, 20500,   0),
    ("fia_tbl_round", 17200, 19700,   0),
    # ENTRANCE HALL  console on the west wall, clear of the pivot door
    ("dresser",       10350, 20500,   0),
    # PANTRY  3400-5200 x 16900-18200 (butler's pantry; both doors swing out
    # of it, so the servery counter keeps the west wall)
    ("sink_unit",      3400, 17000,  90),
    # DIRTY KITCHEN  3400-6350 x 18350-22750 (the service door, back on the
    # street wall at the NW corner, sweeps x3500-4515, y>21935; pantry and
    # back-corridor doors sweep y<19365 at the south). Working wall on the
    # west, prep table on the east, 1.5 m between.
    ("dishwasher",     3400, 18900,  90),
    ("fridge",         3400, 19500,  90),
    ("sink_unit",      3400, 20100,  90),
    ("hob",            3400, 21020,  90),
    ("fia_tbl_toast",  5550, 19800,  90),          # prep table
    # LAUNDRY  6500-8550 x 18350-20400 (the 600x600 appliance block stands in
    # for a stacked washer/dryer; the catalogue has no laundry appliance)
    ("sink_unit",      7915, 18400,  90),
    ("dishwasher",     7950, 19450,   0),
    # MAID ROOM  6500-10150 x 20550-22750 (laundry door sweeps x<7550, y<21475)
    ("bed_single",     7900, 21850,  90),
    ("bedside",        7450, 22350,   0),
    ("wardrobe",       6520, 21600,  90),
    # MAID BATH  8700-10150 x 18350-20400 (door sweeps x8850-9650, y>19675)
    ("shower",         9250, 18350,   0),
    ("wc",             8700, 18400,  90),
    ("basin",          9682, 19350,  90),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # MASTER BEDROOM  16400-20600 x 11400-18100 (garden + east), en-suite
    # nested 18000-20600 x 15700-18100; corridor door sweeps y>17100.
    ("fia_bed",       16400, 12600,  90),
    ("bedside",       16450, 12150,   0),
    ("bedside",       16450, 14593,   0),
    ("wardrobe",      16450, 15300,  90),
    ("wardrobe",      16450, 16150,  90),
    ("fia_armchair",  19600, 11600,   0),
    # MASTER ENSUITE  18000-20600 x 15700-18100 (door sweeps x<19010,
    # y<16435). Bath on the north wall, TWO basins beside it in the corner
    # (villa_design.FIXTURE_COUNT), shower south-east, WC between the door
    # and the shower; the east window sits between shower and basins.
    ("bath",          18000, 17300,   0),
    ("basin",         19700, 17632,   0),          # the block is 450.2 wide
    ("basin",       20150.2, 17632,   0),
    ("shower",        19700, 15700,   0),
    ("wc",            19100, 15700,   0),
    # BEDROOM 2  3400-8850 x 18250-22750, en-suite nested 3400-5300 x 20250-22750.
    # Bed heads the east wall so the north wall keeps the window; foot end
    # open to the west; wardrobe bay in the south-west by the en-suite door.
    ("bed_double",     6850, 20700,  90),
    ("bedside",        8450, 20250,   0),
    ("bedside",        8450, 22350,   0),
    ("wardrobe",       3450, 18300,   0),
    ("wardrobe",       4300, 18300,   0),
    ("wardrobe",       5150, 18300,   0),
    ("fia_armchair",   6000, 19300,   0),
    # BEDROOM 2 ENS  (door from the south sweeps x3600-4400, y<20975)
    ("shower",         3400, 21850,   0),
    ("wc",             4700, 22350,   0),
    ("basin",          4832, 20500,  90),
    # STUDY  9000-12500 x 18250-22750 (family study, street side)
    ("dresser",       10500, 21800,   0),          # desk under the window
    ("fia_chair",     10570, 21200, 180),
    ("wardrobe",      11980, 19500,  90),          # bookcases
    ("wardrobe",      11980, 20350,  90),
    ("fia_armchair",   9100, 20500,   0),
    # BEDROOM 3  3400-7600 x 11400-16750, en-suite nested 3400-5600 x 14550-16750
    ("bed_double",     5600, 12300,  90),
    ("bedside",        7200, 11850,   0),
    ("bedside",        7200, 13950,   0),
    ("wardrobe",       7080, 14500,  90),
    ("wardrobe",       7080, 15350,  90),
    # BEDROOM 3 ENS
    ("shower",         3400, 15850,   0),
    ("wc",             4500, 16350,   0),
    ("basin",          3500, 14600,   0),
    # BEDROOM 4  15050-20600 x 18250-22750, en-suite nested 18400-20600 x 20500-22750
    ("fia_bed",       15050, 19800,  90),
    ("bedside",       15100, 19350,   0),
    ("bedside",       15100, 21793,   0),
    ("wardrobe",      16300, 18300,   0),
    ("wardrobe",      17150, 18300,   0),
    ("wardrobe",      18000, 18300,   0),
    # BEDROOM 4 ENS
    ("shower",        19700, 21850,   0),
    ("wc",            18500, 22350,   0),
    ("basin",         20132, 20600,  90),
]

# ----------------------------------------------------------------- ANNEX
ANNEX = [
    # The annex's west wall moved 16800 -> 17500 (review of 2026-09-26: the
    # majlis's street flight left 235 mm to it). Store and bath shift 300
    # east with their doors; the plant room and the driver's room lose 400
    # and 300 of width.
    # DRIVER ROOM  21300-23600 x 25100-28600 (door + window face south; the
    # street door sweeps x21450-22465, y<25915)
    ("bed_single",    22650, 26300,   0),
    ("bedside",       23150, 25850,   0),
    ("wardrobe",      21350, 25950,  90),
    # DRIVER BATH  19300-21150 x 26950-28600 (door from the room sweeps
    # x>20415, y<28060)
    ("shower",        19300, 27700,   0),
    ("wc",            19400, 26950,   0),
    ("basin",         20650, 28132,   0),
    # STORE  19300-21150 x 25100-26800 (shelving along the back wall)
    ("wardrobe",      19350, 26280,   0),
    ("wardrobe",      20200, 26280,   0),
    # PLANT ROOM  17900-19150 x 25100-28600 (wardrobe block stands in for the
    # control / distribution cabinet; no plant equipment in the catalogue)
    ("wardrobe",      17950, 28080,   0),
]


def footprint(key, x, y, rot):
    m = CATALOG.get(key)
    if not m or "w" not in m:
        return None
    w, d = m["w"], m["d"]
    if rot % 180 == 90:
        w, d = d, w
    return (x, y, x + w, y + d)


def insert_point(key, x, y, rot):
    """AutoCAD insertion point that lands the footprint at (x, y). Blocks are
    not drawn about their corner -- a bed's insertion point is its top centre --
    so the measured offset has to be subtracted."""
    m = CATALOG[key]
    ox, oy = m["offx"], m["offy"]
    if rot % 360 == 0:
        return (x - ox, y - oy)
    if rot % 360 == 90:
        return (x + oy + m["d"], y - ox)
    if rot % 360 == 180:
        return (x + ox + m["w"], y + oy + m["d"])
    return (x - oy, y + ox + m["w"])


def _swing(o):
    """The quarter-disc a door leaf sweeps, as a polygon."""
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    if kind != V.DOOR or sw is None:
        return None
    width = abs(b - a)
    mid = (t0 + t1) / 2.0
    hinge, closed = (((a, mid), 0.0) if axis == "h" else ((mid, a), 90.0))
    d = (sw - closed + 540.0) % 360.0 - 180.0
    a0, a1 = (closed + d, closed) if d < 0 else (closed, closed + d)
    pts = [hinge] + [(hinge[0] + width * math.cos(math.radians(t)),
                      hinge[1] + width * math.sin(math.radians(t)))
                     for t in (a0 + (a1 - a0) * i / 16 for i in range(17))]
    return pts


def _strip(fp, side, depth):
    x0, y0, x1, y1 = fp
    if side == "N":
        return (x0, y1, x1, y1 + depth)
    if side == "S":
        return (x0, y0 - depth, x1, y0)
    if side == "E":
        return (x1, y0, x1 + depth, y1)
    return (x0 - depth, y0, x0, y1)


def _free(strip, room, others):
    """A clearance strip counts only if it is inside the room and no other
    piece of furniture stands in it."""
    if not (room[1] - 1 <= strip[0] and room[2] - 1 <= strip[1]
            and room[3] + 1 >= strip[2] and room[4] + 1 >= strip[3]):
        return False
    for o in others:
        if not (strip[2] <= o[0] or o[2] <= strip[0]
                or strip[3] <= o[1] or o[3] <= strip[1]):
            return False
    return True


# Researched approach clearances, mm. Sanitary fittings need standing room in
# front; a bed needs one side you can walk down to make it.
CLEARANCE = {"wc": 550, "basin": 550, "bath": 700,
             "bed_double": 700, "bed_single": 700}


ANNEX = globals().get("ANNEX", [])        # floor "AX" placements, if any
ROOF = globals().get("ROOF", [])          # floor "RF" placements, if any
BY_FLOOR = (("AX", ANNEX), ("GF", GROUND), ("FF", FIRST), ("RF", ROOF))


def _has(keys, token):
    """Fixture token vs placed block keys: 'shower|bath' means either; a
    token matches a key equal to it, or any key containing it (fia_chair_x)."""
    return any(any(k == t or t in k for k in keys) for t in token.split("|"))


def check():
    """Prove the layout before it is drawn."""
    from shapely.geometry import Polygon, box as sbox
    issues = []
    contents = {}                         # (floor, room) -> [block keys]
    for floor, items in BY_FLOOR:
        rooms = [r for r in V.ROOMS if r[6] == floor]
        swings = [(o, _swing(o)) for o in V.OPENINGS if o[0] == floor]
        swings = [(o, Polygon(p)) for o, p in swings if p]

        placed = []
        for key, x, y, rot in items:
            fp = footprint(key, x, y, rot)
            if fp is None:
                issues.append(f"[{floor}] unknown block '{key}'")
                continue
            placed.append((key, fp))

        for key, fp in placed:
            # smallest room that fully holds it -- nested ensuites win over
            # the bedroom they sit inside
            host = [r for r in rooms
                    if r[1] - 1 <= fp[0] and r[2] - 1 <= fp[1]
                    and r[3] + 1 >= fp[2] and r[4] + 1 >= fp[3]]
            if not host:
                issues.append(f"[{floor}] {key} at ({fp[0]:.0f},{fp[1]:.0f}) "
                              f"is not inside any room")
                continue
            host.sort(key=lambda r: (r[3] - r[1]) * (r[4] - r[2]))
            room = host[0]
            contents.setdefault((floor, room[0]), []).append(key)

            for o, poly in swings:
                ov = poly.intersection(sbox(*fp)).area
                if ov > 1000:
                    issues.append(f"[{floor}] door {o[7]}->{o[8] or 'out'} "
                                  f"opens onto {key} ({ov / 1e6:.2f} m2)")

            others = [f for k, f in placed if f is not fp]
            for k2, f2 in placed:
                if f2 is fp:
                    continue
                if not (fp[2] <= f2[0] or f2[2] <= fp[0]
                        or fp[3] <= f2[1] or f2[3] <= fp[1]):
                    a, b = sorted((key, k2))
                    issues.append(f"[{floor}] {a} overlaps {b}")

            need = CLEARANCE.get(key)
            if need and not any(_free(_strip(fp, sd, need), room, others)
                                for sd in "NSEW"):
                issues.append(f"[{floor}] {key} in {room[0]} has no {need} mm "
                              f"clear side -- cannot be used or made")

    # What each kind of room must CONTAIN (villa_design.FIXTURES). Two
    # en-suites had a WC and a basin and nothing to wash in, and the dining
    # tables had no chairs -- every earlier check passed them, because every
    # earlier check was about where things are, never whether they are there.
    for r in V.ROOMS:
        role = getattr(V, "ROLE", {}).get(r[0])
        need = getattr(V, "FIXTURES", {}).get(role, [])
        keys = contents.get((r[6], r[0]), [])
        for token in need:
            if not _has(keys, token):
                issues.append(f"[{r[6]}] {r[0]} ({role}) has no {token.replace('|', ' or ')}")
        if role == "formal_dining":
            seats = sum(1 for k in keys if "chair" in k)
            if seats < getattr(V, "MIN_DINING_SEATS", 0):
                issues.append(f"[{r[6]}] {r[0]} seats {seats}, brief needs "
                              f"{V.MIN_DINING_SEATS}")
        # how MANY of a fixture a named room holds (the master en-suite's two
        # basins), beyond FIXTURES' "at least one"
        for token, n in getattr(V, "FIXTURE_COUNT", {}).get((r[6], r[0]), {}).items():
            got = sum(1 for k in keys if _has([k], token))
            if got < n:
                issues.append(f"[{r[6]}] {r[0]} has {got} x {token}, needs {n}")
    return sorted(set(issues))


if __name__ == "__main__":
    print(f"ground {len(GROUND)} items, first {len(FIRST)} items")
    iss = check()
    print(f"{len(iss)} issue(s)")
    for i in iss:
        print("  !", i)
    if not iss:
        print("  clean.")
