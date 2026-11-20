"""
Bench villa -- furniture layout.

Placements are (block_key, x, y, rotation), (x, y) the BOTTOM-LEFT of the
block's footprint in plan mm; block sizes from block_catalog.json (the
example's measured ACA / First In Architecture blocks). check() proves every
item is inside its room, clear of every door swing and of every other item,
keeps its approach clearance, and that every room holds what its ROLE needs
(villa_design.FIXTURES) and the dining seats MIN_DINING_SEATS.

The catalogue has no washing machine or dryer: the laundry's two machines
are drawn with the 600 x 620 'dishwasher' block (as the example's laundry
does), and shelving with the 'wardrobe' block.
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
    # KITCHEN 3400-7600 x 9000-14400: the working run on the west wall
    # (fridge, sink, hob, dishwasher), an island 1.27 m off it with stools.
    # Doors sweep x > 6450, y > 12900 (service corridor, dining).
    ("fridge",          3400, 13700,  90),
    ("sink_unit",       3400, 12600,  90),
    ("hob",             3400, 11700,  90),
    ("dishwasher",      3400, 10900,  90),
    ("fia_tbl_toast",   5300, 10700,  90),          # the island
    ("fia_stool",       6250, 11000,   0),
    ("fia_stool",       6250, 11700,   0),
    # DINING 7750-11050 x 9000-15000: two tables end to end, eight chairs
    ("fia_tbl_dining",  8950, 10000,  90),
    ("fia_tbl_dining",  8950, 12100,  90),
    ("fia_chair",       9150,  9420,   0),
    ("fia_chair",       9150, 14230, 180),
    ("fia_chair",       8380, 10500,  90),
    ("fia_chair",       8380, 11800,  90),
    ("fia_chair",       8380, 13100,  90),
    ("fia_chair",       9870, 10500, 270),
    ("fia_chair",       9870, 11800, 270),
    ("fia_chair",       9870, 13100, 270),
    # LIVING 11200-16600 x 9000-16600: a sofa group facing the garden glass
    # (the hall door sweeps x < 12140, y 15400-16415)
    ("fia_sofa_long",  12500, 14300,   0),
    ("fia_tbl_coffee", 13700, 12800,   0),
    ("fia_armchair",   11700, 12500,   0),
    ("fia_armchair",   15800, 12500,   0),
    # HALL: a console on the east wall, clear of the front door's sweep
    ("dresser",        10400, 22200,   0),
    # LAUNDRY 3400-6100 x 14550-17550: two machines and the sink on the
    # west wall, linen shelving on the north wall (door sweeps x > 5160)
    ("dishwasher",      3400, 14600,  90),
    ("dishwasher",      3400, 15250,  90),
    ("sink_unit",       3400, 15900,  90),
    ("wardrobe",        4000, 17030,   0),
    ("wardrobe",        4800, 17030,   0),
    # MAID ROOM 3400-6100 x 17700-22300 (bath nested 3400-5300 x 20400-22300)
    ("bed_single",      3400, 19300,  90),
    ("wardrobe",        5580, 19400,  90),
    # MAID BATH (door from the south sweeps x 4300-5110, y < 21135)
    ("shower",          3400, 21400,   0),
    ("wc",              4700, 21900,   0),
    ("basin",           3400, 20450,  90),
    # STORE 3400-6100 x 22450-24300: shelving (door sweeps x > 5160, y < 23615)
    ("wardrobe",        3450, 23780,   0),
    ("wardrobe",        4250, 23780,   0),
    ("wardrobe",        5050, 23780,   0),
    ("wardrobe",        3400, 22500,  90),
    # SERVICE LOBBY 3400-7600 x 24450-25600: kept clear (the service door
    # sweeps x 3200-4215)
    # MAJLIS 11200-16600 x 16750-25600 (guest WC nested in its north-west
    # corner): seating round three walls and a low table; the hall door
    # sweeps x < 12725, y 19500-21100
    ("fia_sofa_long",  15600, 18200,  90),
    ("fia_sofa_long",  12300, 16800,   0),
    ("fia_sofa_long",  13200, 24550,   0),
    ("fia_tbl_low",    13200, 20000,   0),
    ("fia_armchair",   11350, 22000,   0),
    ("fia_armchair",   11350, 17000,   0),
    # GUEST WC 11200-13000 x 23350-25600 (door sweeps x < 11935)
    ("wc",             12400, 25200,   0),
    ("basin",          12450, 23400,   0),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # BEDROOM 2 3400-7600 x 9000-16700, en-suite nested 3400-5800 x 14000-16700
    ("bed_double",      5600, 11000,  90),
    ("bedside",         7200, 10550,   0),
    ("bedside",         7200, 12650,   0),
    ("wardrobe",        3400, 12200,  90),
    ("wardrobe",        3400, 13000,  90),
    ("fia_armchair",    3600,  9300,   0),
    # BEDROOM 2 ENS (door sweeps x 5065-5875, y 14300-15110)
    ("shower",          3400, 15800,   0),
    ("wc",              4500, 16300,   0),
    ("basin",           3500, 14050,   0),
    # BEDROOM 3 3400-7600 x 16850-24000, en-suite nested 3400-5800 x 16850-19350
    ("bed_double",      5600, 21000,  90),
    ("bedside",         7200, 20550,   0),
    ("bedside",         7200, 22650,   0),
    ("wardrobe",        3400, 22400,  90),
    ("wardrobe",        3400, 23200,  90),
    # BEDROOM 3 ENS (door sweeps x 5065-5875, y 17200-18010)
    ("shower",          3400, 16850,   0),
    ("wc",              4600, 18950,   0),
    ("basin",           3450, 18850,   0),
    # FAMILY LOUNGE 7750-11050 x 9000-15000
    ("fia_sofa_3",      8150, 12800,   0),
    ("fia_tbl_coffee",  8900, 11300,   0),
    ("fia_armchair",    7800, 11400,  90),
    ("fia_armchair",    9950, 11400,  90),
    # MASTER BEDROOM 11200-16600 x 9000-17050; DRESSING nested 12500-14000 x
    # 13600-17050, EN-SUITE nested 14150-16600 x 13600-17050 (two basins)
    ("fia_bed",        12950, 11100,   0),
    ("bedside",        12500, 13000,   0),
    ("bedside",        14950, 13000,   0),
    ("fia_sofa_2",     13000,  9100,   0),
    ("fia_armchair",   11400,  9300,   0),
    # MASTER DRESSING (door from the south sweeps x 12750-13765, y < 14540)
    ("wardrobe",       12500, 14640,  90),
    ("wardrobe",       12500, 15440,  90),
    ("wardrobe",       12500, 16240,  90),
    # MASTER ENSUITE (door from the south sweeps x 14700-15510, y < 14335)
    ("bath",           14850, 16200,   0),
    ("shower",         14150, 14450,   0),
    ("wc",             14150, 15500,  90),
    ("basin",          16132, 14400,  90),
    ("basin",          16132, 15000,  90),
    # BEDROOM 4 11200-16600 x 17200-24000, en-suite nested 14150-16600 x 17200-19700
    ("bed_double",     14500, 19900,   0),
    ("bedside",        14050, 19900,   0),
    ("bedside",        16150, 19900,   0),
    ("wardrobe",       11200, 19500,  90),
    ("wardrobe",       11200, 20300,  90),
    ("wardrobe",       11200, 21100,  90),
    # BEDROOM 4 ENS (door from the north sweeps x 14500-15310, y > 18965)
    ("shower",         15700, 17200,   0),
    ("wc",             14300, 17250,   0),
    ("basin",          16132, 18600,  90),
]

BASEMENT = []
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


CLEARANCE = {"wc": 550, "basin": 550, "bath": 700,
             "bed_double": 700, "bed_single": 700}


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
