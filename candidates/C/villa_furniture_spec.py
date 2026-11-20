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
GROUND = [
    # STUDY  3400-5850 x 16900-22700      (hall door sweeps x5025-5925, y19700+)
    ("dresser",        3450, 20700,   0),          # desk at the west window
    ("fia_chair_cc",   4150, 20900,   0),
    ("fia_recliner",   3450, 17100,   0),          # reading chair
    ("wardrobe",       5300, 17000,  90),          # book cases
    ("wardrobe",       5300, 17850,  90),
    # FAMILY HALL  6000-10250 x 16900-22700   (stair 7250-9350 x 19200-22600)
    ("dresser",        9500, 21600,   0),          # console by the family door
    # FAMILY WC  6000-7650 x 16900-18700  (door sweeps x6925-7725, y17700+)
    ("wc",             6100, 16950,   0),
    ("basin",          6900, 16950,   0),
    # MAJLIS  10400-14750 x 16900-22700   perimeter seating, as a majlis is
    ("fia_sofa_3",    10500, 21700,   0),          # north wall
    ("fia_sofa_3",    10500, 17000,   0),          # south wall
    ("fia_armchair",  10450, 18300,  90),          # west, below the host door
    ("fia_armchair",  10450, 20800,  90),
    ("fia_armchair",  13650, 19500,  90),          # east, between the doors
    ("fia_armchair",  13650, 20250,  90),
    ("fia_tbl_round", 11850, 18900,   0),
    # GUEST FOYER  14900-18400 x 20700-22700
    ("dresser",       17300, 22000,  90),          # console
    # GUEST WC  18550-20600 x 20700-22700 (door sweeps x18475-19275, y<21700)
    ("wc",            20000, 22250,   0),
    ("basin",         19400, 22200,   0),
    # FORMAL DINING  14900-20600 x 16900-20550  -- table for 8, no door
    # swings into the room (majlis, foyer and pantry doors all open away)
    ("fia_tbl_dining", 16700, 18275,  0),
    ("fia_chair",     16750, 17724.5, 0),          # south side
    ("fia_chair",     17500, 17724.5, 0),
    ("fia_chair",     18250, 17724.5, 0),
    ("fia_chair",     16750, 19175,   0),          # north side
    ("fia_chair",     17500, 19175,   0),
    ("fia_chair",     18250, 19175,   0),
    ("fia_chair",     16149.5, 18475, 90),         # ends
    ("fia_chair",     18800, 18475,  90),
    ("dresser",       19900, 17100,   0),          # sideboard
    # SHOW KITCHEN  3400-8950 x 11400-16750 (hall door sweeps x7800-8800)
    ("sink_unit",      3500, 16115,   0),
    ("hob",            4500, 16250,   0),
    ("dishwasher",     5150, 16150,   0),
    ("fridge",         7100, 16235,   0),
    ("fia_tbl_toast",  4300, 14500,   0),          # island / breakfast
    ("dining",         4600, 12200,   0),          # family table for 4
    # FAMILY LIVING  9100-14900 x 11400-16750  (double height, garden slide)
    ("fia_sofa_ph",   10400, 15450,   0),          # facing the garden
    ("fia_sofa_2",    13850, 12500,  90),
    ("fia_tbl_coffee", 11400, 13600,  0),
    ("fia_armchair",   9800, 12800,   0),
    # PANTRY  15050-16950 x 14550-16750
    ("wardrobe",      15900, 14580,   0),          # shelving
    ("wardrobe",      16400, 15150,  90),
    # DIRTY KITCHEN  17100-20600 x 14550-16750 (galley)
    ("sink_unit",     18000, 16115,   0),
    ("hob",           19000, 16250,   0),
    ("dishwasher",    19650, 16150,   0),
    ("fridge",        18200, 14600,   0),
    # MAID ROOM  15050-18800 x 11400-14400 (bath nested 15050-16550 x 12600+)
    ("bed_single",    15500, 11450,  90),
    ("bedside",       15050, 11450,   0),
    ("wardrobe",      18250, 13500,  90),
    ("fia_chair_cc",  17100, 13750,   0),
    # MAID BATH  15050-16550 x 12600-14400
    ("shower",        15050, 13500,   0),
    ("wc",            15050, 12650,  90),
    ("basin",         16050, 12650,   0),
    # SERVICE LOBBY  18950-20600 x 11400-14400 (service door sweeps y<12400)
    ("wardrobe",      20050, 12600,  90),          # boots / coats
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # MASTER BEDROOM  3400-8700 x 11400-16750 (ensuite nested 3400-5900 x 14050+)
    ("fia_bed",        6375, 12300,  90),          # head to the east wall
    ("bedside",        8250, 11850,   0),
    ("bedside",        8250, 14300,   0),
    ("wardrobe",       3450, 13380,   0),
    ("wardrobe",       4250, 13380,   0),
    ("wardrobe",       5050, 13380,   0),
    ("fia_armchair",   3600, 11600,   0),
    ("dresser",        6200, 15700,   0),
    # MASTER ENSUITE  3400-5900 x 14050-16750
    ("bath",           3450, 15900,   0),
    ("wc",             3450, 14100,  90),
    ("basin",          4500, 14100,   0),
    # BEDROOM 2  3400-7000 x 16900-22700 (ens nested 3400-5700 x 20300+)
    ("bed_double",     3450, 18000,  90),
    ("bedside",        3450, 17550,   0),
    ("bedside",        3450, 19650,   0),
    ("wardrobe",       6450, 18300,  90),
    ("wardrobe",       6450, 19150,  90),
    ("dresser",        6100, 20500,   0),
    # BEDROOM 2 ENS  3400-5700 x 20300-22700
    ("shower",         3450, 21750,   0),
    ("wc",             3450, 20400,  90),
    ("basin",          5200, 21600,  90),
    # BEDROOM 4  17000-20600 x 16900-22700 (ens nested 18300-20600 x 20300+)
    ("bed_double",    18550, 18000,  90),
    ("bedside",       20150, 17550,   0),
    ("bedside",       20150, 19650,   0),
    ("wardrobe",      17050, 18300,  90),
    ("wardrobe",      17050, 19150,  90),
    ("dresser",       17100, 20500,   0),
    # BEDROOM 4 ENS  18300-20600 x 20300-22700
    ("shower",        19650, 21750,   0),
    ("wc",            20150, 20400,  90),
    ("basin",         18350, 21600,  90),
    # BEDROOM 3  15300-20600 x 11400-16750 (ens nested 18100-20600 x 14050+)
    ("bed_double",    15350, 12400,  90),
    ("bedside",       15350, 11950,   0),
    ("wardrobe",      18150, 13380,   0),
    ("wardrobe",      18950, 13380,   0),
    ("wardrobe",      19750, 13380,   0),
    ("fia_armchair",  19600, 11600,   0),
    # BEDROOM 3 ENS  18100-20600 x 14050-16750
    ("shower",        19650, 15800,   0),
    ("wc",            18200, 16300,   0),
    ("basin",         20100, 14200,  90),
    # FAMILY LOUNGE  9650-16850 x 18450-22700 (door sweeps x12400-13600, y<19575)
    ("fia_sofa_long", 10000, 21500,   0),
    ("fia_sofa_3",    15800, 19300,  90),
    ("fia_tbl_coffee", 12400, 20200,  0),
    ("fia_armchair",  10100, 19000,   0),
    ("dresser",       14700, 21700,   0),          # media / console
]

# ----------------------------------------------------------------- ANNEX
ANNEX = [
    # PLANT  16900-18900 x 2600-7800   (pool plant; door sweeps y7000+)
    ("sink_unit",     16950, 2650,    0),          # backwash / utility sink
    ("wardrobe",      18050, 2650,    0),          # chemicals cabinet
    # LAUNDRY  19050-20600 x 4800-7800 (door sweeps y6900+)
    ("sink_unit",     19950, 5300,   90),
    ("dishwasher",    19100, 5400,    0),          # 600 x 600: washer
    ("dishwasher",    19100, 6050,    0),          # 600 x 600: dryer
    # STORE  19050-20600 x 2600-4650   (laundry door sweeps x19300-20200, y3825+)
    ("wardrobe",      19100, 2650,    0),          # shelving
    ("wardrobe",      20060, 2650,   90),
    # DRIVER ROOM  20750-23600 x 4800-7800 (door sweeps x21000-21900, y6900+)
    ("bed_single",    21450, 4850,   90),
    ("wardrobe",      20800, 5900,   90),
    ("bedside",       23150, 5800,    0),
    # DRIVER BATH  20750-23600 x 2600-4650 (door sweeps x21000-21800, y3925+)
    ("shower",        22650, 2650,    0),
    ("wc",            20800, 2650,    0),
    ("basin",         21900, 2650,    0),
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
    print(f"ground {len(GROUND)} items, first {len(FIRST)} items, annex {len(ANNEX)} items")
    iss = check()
    print(f"{len(iss)} issue(s)")
    for i in iss:
        print("  !", i)
    if not iss:
        print("  clean.")
