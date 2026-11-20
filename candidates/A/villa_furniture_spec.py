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
# Candidate A. Every room is furnished, the new ones included. Where the
# catalogue has no true block for a piece of equipment a same-footprint
# stand-in is used and SAID so in the comment (washer/dryer = the 600x600
# dishwasher footprint; shelving/cabinets = the wardrobe carcass).
GROUND = [
    # SHOW KITCHEN  3400-7600 x 11400-16750 (west pavilion, garden door x6500+)
    # galley: cooking run on the west wall under the window, island opposite
    # at 1215 clear, breakfast table by the garden glazing
    ("hob",            3400, 13300,  90),
    ("sink_unit",      3400, 13950,  90),
    ("dishwasher",     3400, 14900,   0),
    ("fridge",         3400, 15600,  90),
    ("fia_tbl_toast",  5250, 13600,  90),          # island / breakfast bar
    ("fia_stool",      6100, 13900,   0),
    ("fia_stool",      6100, 14700,   0),
    ("fia_tbl_coffee", 4300, 11950,   0),          # family breakfast table
    ("fia_chair_cc",   3700, 12200,   0),
    ("fia_chair_cc",   5400, 12200,   0),
    ("fia_chair_cc",   4550, 11400,   0),
    ("fia_chair_cc",   4550, 12980,   0),
    # DIRTY KITCHEN  3400-6250 x 16900-19800 (service door W, pass door S)
    ("dishwasher",     3400, 16900,   0),
    ("sink_unit",      3400, 17500,  90),
    ("hob",            5750, 18100,  90),
    ("fridge",         5300, 19285,   0),
    # PANTRY  3400-6250 x 19950-21550: freezer + shelving (wardrobe carcass)
    ("fridge",         3450, 20000,   0),          # chest freezer footprint
    ("wardrobe",       3450, 21030,   0),
    ("wardrobe",       4250, 21030,   0),
    ("wardrobe",       5050, 21030,   0),
    # MAID BATH  3400-6250 x 21700-23600
    ("shower",         3400, 22700,   0),
    ("wc",             3450, 21750,   0),
    ("basin",          4400, 21700,   0),
    # LAUNDRY  6400-9250 x 18250-20350: utility sink, washer + dryer
    ("sink_unit",      6400, 18400,  90),
    ("dishwasher",     8650, 19150,   0),          # washer (600x600 footprint)
    ("dishwasher",     8650, 19750,   0),          # dryer  (600x600 footprint)
    # MAID ROOM  6400-9250 x 20500-23600
    ("bed_single",     8350, 21000,   0),
    ("bedside",        8850, 23150,   0),
    ("wardrobe",       6400, 22800,  90),
    ("dresser",        7000, 22686,   0),
    # ENTRANCE HALL  9400-14600 x 16900-23600 (stair on the west wall)
    ("dresser",       13953, 21200,   0),          # console
    # GUEST WC  17800-20600 x 16900-18200
    ("basin",         18800, 17732,   0),
    ("wc",            19700, 17800,   0),
    # WOMEN'S MAJLIS  14750-20600 x 18350-22750 -- perimeter seating
    ("fia_sofa_long", 16300, 21750,   0),
    ("fia_sofa_3",    19660, 18800,  90),
    ("fia_sofa_ke",   17300, 18400,   0),
    ("fia_armchair",  14800, 21300,   0),
    ("fia_armchair",  14800, 18450,   0),
    ("fia_tbl_round", 17200, 19700,   0),
    # FORMAL DINING  16400-20600 x 11400-16750 (east pavilion) -- 8 seats
    ("fia_tbl_dining", 18100, 12900, 90),
    ("fia_chair",     17500, 13050,  90),
    ("fia_chair",     17500, 13700,  90),
    ("fia_chair",     17500, 14350,  90),
    ("fia_chair",     19050, 13050,  90),
    ("fia_chair",     19050, 13700,  90),
    ("fia_chair",     19050, 14350,  90),
    ("fia_chair",     18300, 12300,   0),
    ("fia_chair",     18300, 15050,   0),
    ("dresser",       16400, 13000,   0),          # sideboard
    # FAMILY LIVING  9100-14900 x 11400-16750 -- seating west, the route from
    # the hall opening to the garden slide kept clear on the east
    ("fia_sofa_ph",    9150, 12600,  90),
    ("fia_tbl_coffee", 10550, 13600,  0),
    ("fia_sofa_2",    12050, 13150,  90),
    ("fia_armchair",  10500, 15300,   0),
    ("fia_armchair",  10500, 11900,   0),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # MASTER BEDROOM  13750-20600 x 18250-22750 (en-suite 18000-20600 x
    # 18250-21250 nested); bed head on the landing wall, wardrobe wall
    # against the en-suite, sitting corner by the north/east windows
    ("fia_bed",       13750, 19900,  90),
    ("bedside",       13750, 19450,   0),
    ("bedside",       13750, 21900,   0),
    ("wardrobe",      17330, 18300,  90),
    ("wardrobe",      17330, 19100,  90),
    ("wardrobe",      17330, 19900,  90),
    ("wardrobe",      17330, 20700,  90),
    ("fia_armchair",  19700, 21600,   0),
    # MASTER ENSUITE  18000-20600 x 18250-21250 (door from the north)
    ("bath",          19800, 18300,  90),
    ("shower",        18000, 18250,   0),
    ("wc",            18050, 19700,  90),
    ("basin",         19200, 20782,   0),
    ("basin",         19700, 20782,   0),
    # BEDROOM 2  3400-9250 x 18250-23600 (en-suite 3400-5900 x 18250-21000)
    ("fia_bed",        6925, 20400,  90),
    ("bedside",        8850, 19950,   0),
    ("bedside",        8850, 22400,   0),
    ("wardrobe",       3450, 21150,   0),
    ("wardrobe",       4250, 21150,   0),
    ("wardrobe",       5050, 21150,   0),
    ("dresser",        4000, 22686,   0),
    # BEDROOM 2 ENS  3400-5900 x 18250-21000
    ("bath",           3400, 18250,  90),
    ("basin",          5000, 18250,   0),
    ("wc",             3450, 20600,   0),
    ("shower",         4400, 20100,   0),
    # BEDROOM 3  3400-7600 x 11400-16750 (en-suite 3400-5900 x 11400-13400)
    ("fia_bed",        4000, 14425,   0),
    ("bedside",        3550, 16350,   0),
    ("bedside",        5993, 16350,   0),
    ("wardrobe",       7080, 13600,  90),
    ("wardrobe",       7080, 14400,  90),
    ("dresser",        6800, 11400,   0),          # desk under the window
    # BEDROOM 3 ENS  3400-5900 x 11400-13400
    ("shower",         3400, 12500,   0),
    ("wc",             3450, 11450,   0),
    ("basin",          4400, 11400,   0),
    # BEDROOM 4  16400-20600 x 11400-16750 (en-suite 18100-20600 x 11400-13400)
    ("fia_bed",       18200, 14425,   0),
    ("bedside",       17750, 16350,   0),
    ("bedside",       20193, 16350,   0),
    ("wardrobe",      16400, 13600,  90),
    ("wardrobe",      16400, 14400,  90),
    ("dresser",       16500, 11400,   0),          # desk under the window
    # BEDROOM 4 ENS  18100-20600 x 11400-13400
    ("shower",        19700, 12500,   0),
    ("wc",            19700, 11450,   0),
    ("basin",         19000, 11400,   0),
    # LANDING  9400-13600 x 18250-22750: study nook under the north window
    ("dresser",       12000, 22103,  90),          # desk
    ("fia_chair_cc",  12200, 21500,   0),
    ("fia_armchair",  12700, 19300,   0),
    # LINEN  18150-20600 x 16900-18100: shelving (wardrobe carcass)
    ("wardrobe",      19000, 17580,   0),
    ("wardrobe",      19800, 17580,   0),
]

# ----------------------------------------------------------------- ANNEX
ANNEX = [
    # DRIVER ROOM  400-3750 x 25950-28600
    ("bed_single",      400, 27700,  90),
    ("bedside",        2550, 28200,   0),
    ("wardrobe",       3230, 26700,  90),
    ("dresser",        1200, 26000,   0),          # desk
    ("fia_chair",       500, 26000,   0),
    # DRIVER BATH  3900-5400 x 25950-28600
    ("shower",         4500, 25950,   0),
    ("wc",             3950, 26000,   0),
    ("basin",          4950, 28132,   0),
    # PLANT  5550-7350 x 25950-28600: controls cabinet (wardrobe carcass);
    # the pool / irrigation / water-tank plant itself is not in the catalogue
    ("wardrobe",       5600, 28080,   0),
    # STORE  7500-9000 x 25950-28600: shelving (wardrobe carcass)
    ("wardrobe",       8480, 26800,  90),
    ("wardrobe",       8480, 27600,  90),
    ("wardrobe",       7500, 27800,   0),
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
    return sorted(set(issues))


if __name__ == "__main__":
    print(f"ground {len(GROUND)} items, first {len(FIRST)} items")
    iss = check()
    print(f"{len(iss)} issue(s)")
    for i in iss:
        print("  !", i)
    if not iss:
        print("  clean.")
