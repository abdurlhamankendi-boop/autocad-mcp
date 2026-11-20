"""
BENCH VILLA -- furniture layout.

Placements are (block_key, x, y, rotation), (x, y) the BOTTOM-LEFT of the
block's footprint in plan mm; block sizes from block_catalog.json (measured
ACA content blocks and the FIA pack, copied from the pipeline). check() proves
every item is inside its room, clear of every door swing and of every other
item, keeps its approach clearance, and that every room holds what its ROLE
needs (villa_design.FIXTURES) -- the same checks as the villa's spec, applied
to the two storeys of this design (BY_FLOOR "GF", "FF") and the dining seat
count applied to every DINING_ROLES room.

The catalogue has no cars and no washing machines: the carport is drawn empty,
and the 600 mm Dishwasher block stands in for the washer and the dryer in the
laundry. The TV consoles are the 2000 x 800 FIA table block.
"""

from __future__ import annotations

import json
import math
import os

import villa_design as V

CATALOG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "block_catalog.json")))

# ---------------------------------------------------------------- GROUND
GROUND = [
    # LIVING 3400-8800 x 9900-17800: the TV console on the north wall, a sofa
    # group facing it, a second seating corner by the garden glass (the slider
    # at y 9500-9900 keeps its 1.6 m clear)
    ("fia_tbl_toast",  5400, 17000,   0),
    ("fia_sofa_long",  4000, 13600,   0),
    ("fia_tbl_coffee", 5200, 15100,   0),
    ("fia_armchair",   3500, 15200,   0),
    ("fia_armchair",   7000, 15200,   0),
    ("fia_sofa_2",     3600, 11500,   0),
    ("fia_tbl_round",  6900, 11500,   0),
    # MAJLIS 3400-8800 x 17950-25600 (GUEST WC nested 6700-8800 x 17950-19650):
    # sofas round three walls, two low tables, two armchairs; the hall door
    # sweeps x 7375-8875, y 21000-22500
    ("fia_sofa_3",     3500, 18050,   0),
    ("fia_sofa_long",  3450, 19600,  90),
    ("fia_sofa_long",  4700, 24550,   0),
    ("fia_tbl_coffee", 5200, 20300,   0),
    ("fia_tbl_coffee", 5200, 22000,   0),
    ("fia_armchair",   6700, 19900,   0),
    ("fia_armchair",   7800, 22900,   0),
    # GUEST WC (the door from the hall opens into the hall)
    ("wc",             7100, 17950,   0),
    ("basin",          7800, 19182,   0),
    # HALL 8950-12650 x 15450-25600: console and bench on the west wall (the
    # stair stands on the east wall, x 11400-12650); the front door sweeps
    # x 9650-11050, y 24400-25800
    ("dresser",        8980, 23000,   0),
    ("fia_sofa_ke",    8980, 19000,  90),
    # DINING 8950-12650 x 9900-15300: one 2.1 m table on the long axis, eight
    # chairs (three a side and one at each end)
    ("fia_tbl_dining", 10350, 11900, 90),
    ("fia_chair",       9780, 12000,  90),
    ("fia_chair",       9780, 12700,  90),
    ("fia_chair",       9780, 13400,  90),
    ("fia_chair",      11270, 12000, 270),
    ("fia_chair",      11270, 12700, 270),
    ("fia_chair",      11270, 13400, 270),
    ("fia_chair",      10600, 14020, 180),
    ("fia_chair",      10600, 11329,   0),
    # KITCHEN 12800-16600 x 9900-15300: the working run on the east wall (the
    # sink under the window), the island 1.2 m off it with three stools
    ("fridge",         15971, 10000,  90),
    ("dishwasher",     15980, 10650,  90),
    ("sink_unit",      15965, 12700,  90),
    ("hob",            16100, 14100,  90),
    ("fia_tbl_toast",  13965, 11600,  90),
    ("fia_stool",      13405, 11700,   0),
    ("fia_stool",      13405, 12300,   0),
    ("fia_stool",      13405, 12900,   0),
    # MAID ROOM 14100-16600 x 15450-20150, MAID BATH nested 14850-16600 x
    # 15450-17050. The lobby door sweeps x 14025-15040, y 18100-19115; the bath
    # door sweeps x 15500-16310, y 17125-17935
    ("bed_single",     15650, 18050,   0),
    ("wardrobe",       14150, 19630,   0),
    # MAID BATH (the door is on the north wall at x 15500-16310, opening outwards)
    ("shower",         14850, 15450,   0),
    ("wc",             15950, 15450,   0),
    ("basin",          14900, 16582,   0),
    # LAUNDRY 14100-16600 x 20300-22700: the 600 Dishwasher block stands in for
    # the washer and the dryer; the lobby door sweeps x 14025-15040
    ("dishwasher",     15980, 20400,  90),
    ("dishwasher",     15980, 21050,  90),
    ("sink_unit",      15400, 22065,   0),
    # STORE 14100-16600 x 22850-25600: shelving on the east and south walls
    ("wardrobe",       16080, 22900,  90),
    ("wardrobe",       16080, 23700,  90),
    ("wardrobe",       16080, 24500,  90),
    ("wardrobe",       15200, 22850,   0),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # MASTER BEDROOM 3400-8800 x 7900-14950; DRESSING nested 3400-5150 x
    # 11650-14950; EN-SUITE nested 5300-7500 x 11650-14950 (two basins). The
    # corridor door (x 7690-8705) is in the alcove east of the en-suite. The
    # bed head is on the east wall; a sitting corner under the south windows
    ("fia_bed",         6475,  9300,  90),
    ("bedside",         8400,  8900,   0),
    ("bedside",         8400, 11250,   0),
    ("fia_armchair",    3550,  8100,   0),
    ("fia_tbl_coffee",  4400,  8100,   0),
    ("fia_armchair",    5500,  8100,   0),
    ("wardrobe",        3420, 12700,  90),
    ("wardrobe",        3420, 13500,  90),
    ("wardrobe",        3950, 14430,   0),
    ("bath",            5320, 14150,   0),
    ("shower",          6600, 11650,   0),
    ("wc",              5320, 12700,  90),
    ("basin",           7032, 12700, 270),
    ("basin",           7032, 13300, 270),
    # BEDROOM 2 8950-12650 x 7900-14950, en-suite nested 10150-12650 x 12650-14950
    ("fia_bed",         8970,  9000,  90),
    ("bedside",         8980,  8600,   0),
    ("bedside",         8980, 10950,   0),
    ("wardrobe",        8970, 11800,  90),
    ("wardrobe",        8970, 12600,  90),
    ("fia_armchair",   11600,  7950,   0),
    ("dresser",        12000, 10000,   0),
    ("shower",         11750, 14050,   0),
    ("wc",             10170, 14000,  90),
    ("basin",          12182, 13200, 270),
    # BEDROOM 3 12800-16600 x 7900-14950, en-suite nested 14100-16600 x 12650-14950
    ("fia_bed",        12820,  9000,  90),
    ("bedside",        12830,  8600,   0),
    ("bedside",        12830, 10950,   0),
    ("wardrobe",       12820, 11800,  90),
    ("wardrobe",       12820, 12600,  90),
    ("fia_armchair",   15500,  7950,   0),
    ("dresser",        15900, 10200,   0),
    ("shower",         15700, 14050,   0),
    ("wc",             14120, 14000,  90),
    ("basin",          16132, 13200, 270),
    # BEDROOM 4 12800-16600 x 16750-23500, en-suite nested 14100-16600 x 16750-19050
    ("fia_bed",        12820, 20000,  90),
    ("bedside",        12830, 19600,   0),
    ("bedside",        12830, 21950,   0),
    ("wardrobe",       12820, 17800,  90),
    ("wardrobe",       12820, 18600,  90),
    ("fia_armchair",   15600, 22000,   0),
    ("dresser",        15900, 19400,   0),
    ("shower",         15700, 16750,   0),
    ("wc",             14120, 16800,  90),
    ("basin",          16132, 18200, 270),
    # FAMILY LOUNGE 3400-8800 x 16750-23500: the TV console on the east wall,
    # sofas facing it; the corridor arch is on the south wall (x 4400-7800)
    ("fia_sofa_3",      4000, 17600,   0),
    ("fia_sofa_long",   3450, 19000,  90),
    ("fia_tbl_coffee",  5300, 19700,   0),
    ("fia_armchair",    6600, 18300,   0),
    ("fia_armchair",    6600, 21300,   0),
    ("fia_tbl_toast",   8000, 19500,  90),
]

ANNEX = []
ROOF = []
BY_FLOOR = (("GF", GROUND), ("FF", FIRST))


def footprint(key, x, y, rot):
    m = CATALOG.get(key)
    if not m or "w" not in m:
        return None
    w, d = m["w"], m["d"]
    if rot % 180 == 90:
        w, d = d, w
    return (x, y, x + w, y + d)


def insert_point(key, x, y, rot):
    """AutoCAD insertion point that lands the footprint at (x, y)."""
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
    return [hinge] + [(hinge[0] + width * math.cos(math.radians(t)),
                       hinge[1] + width * math.sin(math.radians(t)))
                      for t in (a0 + (a1 - a0) * i / 16 for i in range(17))]


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
    if not (room[1] - 1 <= strip[0] and room[2] - 1 <= strip[1]
            and room[3] + 1 >= strip[2] and room[4] + 1 >= strip[3]):
        return False
    for o in others:
        if not (strip[2] <= o[0] or o[2] <= strip[0]
                or strip[3] <= o[1] or o[3] <= strip[1]):
            return False
    return True


# 550 in front of a WC or basin, 700 beside a bath or a bed. The FIA double bed
# ("fia_bed") is held to the same 700 as the other beds.
CLEARANCE = {"wc": 550, "basin": 550, "bath": 700,
             "bed_double": 700, "bed_single": 700, "fia_bed": 700}


def _has(keys, token):
    return any(any(k == t or t in k for k in keys) for t in token.split("|"))


def check():
    """Prove the layout before it is drawn."""
    from shapely.geometry import Polygon, box as sbox
    issues = []
    contents = {}
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
            host = [r for r in rooms
                    if r[1] - 1 <= fp[0] and r[2] - 1 <= fp[1]
                    and r[3] + 1 >= fp[2] and r[4] + 1 >= fp[3]]
            if not host:
                issues.append(f"[{floor}] {key} at ({fp[0]:.0f},{fp[1]:.0f}) is not "
                              f"inside any room")
                continue
            host.sort(key=lambda r: (r[3] - r[1]) * (r[4] - r[2]))
            room = host[0]
            # a nested room's partition band belongs to neither: an item in
            # a parent must stay out of its children and their partitions
            kids = [q for q in rooms if q is not room and V.contains(V.rect(room), V.rect(q))]
            for q in kids:
                band = sbox(*V.rect(q)).buffer(V.PART, join_style=2)
                if band.intersection(sbox(*fp)).area > 1000:
                    issues.append(f"[{floor}] {key} in {room[0]} runs into {q[0]}")
            contents.setdefault((floor, room[0]), []).append(key)
            for o, poly in swings:
                ov = poly.intersection(sbox(*fp)).area
                if ov > 1000:
                    issues.append(f"[{floor}] door {o[7]}->{o[8] or 'out'} opens onto "
                                  f"{key} ({ov / 1e6:.2f} m2)")
            others = [f for k, f in placed if f is not fp]
            for k2, f2 in placed:
                if f2 is fp:
                    continue
                if not (fp[2] <= f2[0] or f2[2] <= fp[0]
                        or fp[3] <= f2[1] or f2[3] <= fp[1]):
                    a, b = sorted((key, k2))
                    issues.append(f"[{floor}] {a} overlaps {b}")
            need = CLEARANCE.get(key)
            if need and not any(_free(_strip(fp, sd, need), room, others) for sd in "NSEW"):
                issues.append(f"[{floor}] {key} in {room[0]} has no {need} mm clear side")
    for r in V.ROOMS:
        role = V.ROLE.get(r[0])
        keys = contents.get((r[6], r[0]), [])
        for token in V.FIXTURES.get(role, []):
            if not _has(keys, token):
                issues.append(f"[{r[6]}] {r[0]} ({role}) has no {token.replace('|', ' or ')}")
        if role in getattr(V, "DINING_ROLES", ("formal_dining",)):
            seats = sum(1 for k in keys if "chair" in k)
            if seats < V.MIN_DINING_SEATS:
                issues.append(f"[{r[6]}] {r[0]} seats {seats}, the brief needs "
                              f"{V.MIN_DINING_SEATS}")
        for token, n in V.FIXTURE_COUNT.get((r[6], r[0]), {}).items():
            got = sum(1 for k in keys if _has([k], token))
            if got < n:
                issues.append(f"[{r[6]}] {r[0]} has {got} x {token}, needs {n}")
    return sorted(set(issues))


if __name__ == "__main__":
    print(f"ground {len(GROUND)}, first {len(FIRST)} items")
    iss = check()
    print(f"{len(iss)} issue(s)")
    for i in iss:
        print("  !", i)
    if not iss:
        print("  clean.")
