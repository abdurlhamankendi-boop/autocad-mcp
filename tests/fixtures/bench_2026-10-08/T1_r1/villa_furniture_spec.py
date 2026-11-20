"""
The Bench villa -- furniture layout.

Placements are (block_key, x, y, rotation), (x, y) the BOTTOM-LEFT of the
block's footprint in plan mm; block sizes from block_catalog.json (measured
ACA content blocks, copied from the pipeline). check() proves every item is
inside its room, clear of every door swing and of every other item, keeps
its approach clearance, and that every room holds what its ROLE needs
(villa_design.FIXTURES) -- the same checks as the Fairway's (the check code
below is the Fairway's, unchanged).

Two storeys, no basement: BY_FLOOR is GF and FF. The laundry's two machines
are drawn as the 600 dishwasher block (the catalogue has no washer); the gym,
cinema and plant rooms of the Fairway are not here.
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
    # MAJLIS 3400-8200 x 20000-24600: the guest sitting room -- sofas along the
    # west and south walls, a coffee table, an armchair
    ("fia_sofa_long",  3700, 20300,   0),
    ("fia_sofa_3",     3700, 23000,   0),
    ("fia_tbl_coffee", 4700, 21700,   0),
    ("fia_armchair",   6500, 21600,   0),
    # GUEST WC 8350-9950 x 17000-18800 (nested in the hall): basin and WC
    ("wc",             9400, 17100,   0),
    ("basin",          8450, 17100,   0),
    # HALL 8350-11450 x 17000-24600: the stair sits in its east part; a console
    # clear of the majlis and front-door swings
    ("dresser",        8450, 22600,  90),
    # LIVING 11600-16600 x 18000-24600: the family seating round a table
    ("fia_sofa_long", 12300, 19800,   0),
    ("fia_tbl_coffee", 13600, 21400,  0),
    ("fia_armchair",  15600, 21300,   0),
    ("fia_sofa_3",    12300, 22900, 180),
    # DINING 3400-8200 x 12000-19850: a table for eight, ten chairs (the brief
    # asks for eight), a sideboard
    ("fia_tbl_dining", 4900, 15200,  90),
    ("fia_chair",     4300, 15250,   0),
    ("fia_chair",     4300, 15850,   0),
    ("fia_chair",     4300, 16450,   0),
    ("fia_chair",     4300, 17050,   0),
    ("fia_chair",     5900, 15250, 180),
    ("fia_chair",     5900, 15850, 180),
    ("fia_chair",     5900, 16450, 180),
    ("fia_chair",     5900, 17050, 180),
    ("fia_chair",     4900, 14500,   0),
    ("fia_chair",     4900, 17450,   0),
    ("dresser",       3500, 18600,   0),
    # KITCHEN 8350-11450 x 12000-16850: the run on the west wall, a working
    # aisle to the east
    ("sink_unit",     8400, 12200,  90),
    ("hob",           8400, 13300,  90),
    ("fridge",        8400, 14200,  90),
    ("dishwasher",    8400, 15000,  90),
    # LAUNDRY 11600-13900 x 12000-13850: the two machines stacked on the west
    # wall, clear of the store door's swing
    ("dishwasher",    11700, 12150,   0),
    ("dishwasher",    11700, 12900,   0),
    # STORE 14050-16600 x 12000-13850: shelving along the west and north walls
    ("wardrobe",      14150, 12150,   0),
    ("wardrobe",      15050, 12150,   0),
    ("wardrobe",      14150, 12850,   0),
    ("wardrobe",      15050, 12850,   0),
    # MAID ROOM 13000-16600 x 14000-17850, MAID BATH nested 13000-16600 x
    # 16650-17850 (a 3.6 x 1.2 bath: shower, basin and WC along its north wall)
    ("bed_single",    13100, 14150,   0),
    ("wardrobe",      15600, 14100,   0),
    ("shower",        13100, 16800,   0),
    ("basin",         15150, 16750,   0),
    ("wc",            15900, 16750,   0),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # BEDROOM 2 3400-8200 x 8400-14200, ENSUITE nested 3400-5600 x 8400-10600
    ("bed_double",    5800, 11500,   0),
    ("bedside",       5300, 11700,   0),
    ("bedside",       7500, 11700,   0),
    ("wardrobe",      6000, 13600,   0),
    ("fia_armchair",  3600, 13000,  90),
    ("shower",        3450, 8450,    0),
    ("wc",            4950, 8450,    0),
    ("basin",         4950, 9300,    0),
    # BEDROOM 3 8350-11450 x 8400-14200, ENSUITE nested 9350-11450 x 8400-10600
    ("bed_double",    8500, 11800,   0),
    ("bedside",      10200, 12100,   0),
    ("wardrobe",     10250, 13300,   0),
    ("shower",        9400, 8450,    0),
    ("basin",        10850, 8450,    0),
    ("wc",           10900, 9300,    0),
    # MASTER 12850-16600 x 8400-14200, ENSUITE nested 14500-16600 x 8400-10600
    ("fia_bed",      13000, 11600,  90),
    ("bedside",      13000, 13700,   0),
    ("bedside",      15400, 13700,   0),
    ("wardrobe",     15800, 11700,   0),
    ("shower",       14550, 8450,    0),
    ("basin",        15550, 8450,    0),
    ("basin",        16050, 9000,    0),
    ("wc",           16050, 9500,    0),
    # BEDROOM 4 3400-8200 x 18000-24600, ENSUITE nested 3400-5600 x 22400-24600
    ("bed_double",    4000, 18400,   0),
    ("bedside",       5700, 18400,   0),
    ("wardrobe",      6600, 23300,   0),
    ("shower",        3450, 22450,   0),
    ("basin",         4700, 22450,   0),
    ("wc",            4900, 23500,   0),
    # STAIR LANDING and LANDING: circulation, no furniture
    # MASTER DRESSING 12850-16600 x 14350-17850: wardrobes along the north wall
    ("wardrobe",     12950, 14450,   0),
    ("wardrobe",     13800, 14450,   0),
    ("dresser",      15600, 16700,   0),
    # FAMILY LOUNGE 12850-16600 x 18000-24600: sofas facing the window wall
    ("fia_sofa_3",   13100, 19000,   0),
    ("fia_tbl_coffee", 14000, 20500,  0),
    ("fia_armchair", 15700, 20000,   0),
    ("fia_sofa_long", 13100, 22000,  0),
]

BY_FLOOR = (("GF", GROUND), ("FF", FIRST))

BASEMENT = []                                      # none in this design (the Fairway's B1)

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
    print(f"basement {len(BASEMENT)}, ground {len(GROUND)}, first {len(FIRST)} items")
    iss = check()
    print(f"{len(iss)} issue(s)")
    for i in iss:
        print("  !", i)
    if not iss:
        print("  clean.")
