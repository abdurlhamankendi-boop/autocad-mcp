"""
The BENCH villa -- furniture layout (ground and first floor; no basement).

Placements are (block_key, x, y, rotation), (x, y) the BOTTOM-LEFT of the
block's footprint in plan mm; block sizes from block_catalog.json (measured
ACA and First In Architecture content blocks). check() proves every item is
inside its room, clear of every door swing and of every other item, keeps
its approach clearance, and that every room holds what its ROLE needs
(villa_design.FIXTURES) -- the same checks as the other villas.
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
    # MAJLIS 3400-9400 x 19950-25600: sofas round the coffee table, facing the
    # north window; the door from the hall sweeps x > 8460 at y 21000-22015
    ("fia_sofa_long", 3600, 23600, 0),
    ("fia_sofa_3",    3700, 20300, 0),
    ("fia_tbl_coffee", 4800, 22100, 0),
    ("fia_armchair",  7000, 21000, 0),
    ("fia_armchair",  7000, 23400, 0),
    # HALL 9550-12850 x 15950-25600: a console on the west wall; the stair
    # rises along the east wall (11650-12850); the front door swings into it
    ("dresser",       9600, 17500, 90),
    # GUEST WC 13000-14650 x 23450-25600 (door from the hall, swings in)
    ("wc",            14050, 24900, 0),
    ("basin",         14100, 23600, 0),
    # CLOAK 14800-16600 x 23450-25600: coat cabinet
    ("wardrobe",      16000, 23600, 90),
    # DINING 13000-16600 x 15950-23300: a table for eight (ten with the heads)
    ("fia_tbl_dining", 14050, 17500, 90),
    ("fia_chair",     13300, 17700, 90),
    ("fia_chair",     13300, 18500, 90),
    ("fia_chair",     13300, 19300, 90),
    ("fia_chair",     15050, 17700, 270),
    ("fia_chair",     15050, 18500, 270),
    ("fia_chair",     15050, 19300, 270),
    ("fia_chair",     14300, 16850, 0),
    ("fia_chair",     14300, 19650, 180),
    # LIVING 9550-16600 x 9600-15800: seating on the garden glass
    ("fia_sofa_long", 10100, 12600, 0),
    ("fia_tbl_coffee", 11000, 11200, 0),
    ("fia_armchair",  13900, 11200, 0),
    ("fia_armchair",  15000, 11200, 0),
    ("fia_tbl_round", 14600, 13200, 0),
    # KITCHEN 3400-9400 x 16000-19800: working run on the north wall, the
    # fridge at the west, the island with stools
    ("fridge",        3450, 19000, 90),
    ("hob",           5000, 19100, 0),
    ("sink_unit",     6000, 19100, 0),
    ("dishwasher",    7050, 19100, 0),
    ("fia_tbl_toast", 4800, 17000, 0),
    ("fia_stool",     5000, 17900, 0),
    ("fia_stool",     5800, 17900, 0),
    ("fia_stool",     6600, 17900, 0),
    # MAID ROOM 3400-6400 x 9600-12700: bed, wardrobe
    ("bed_single",    3450, 10000, 90),
    ("wardrobe",      5300, 11300, 0),
    # MAID BATH 6550-8000 x 9600-12700 (door from the maid room)
    ("wc",            7050, 9600, 0),
    ("basin",         6650, 11150, 0),
    ("shower",        7000, 11700, 0),
    # STORE 8150-9400 x 9600-12700: shelving
    ("wardrobe",      8200, 9700, 90),
    ("wardrobe",      8200, 10700, 90),
    # LAUNDRY 6550-9400 x 12850-15850: two machines, a sink
    ("dishwasher",    6650, 12950, 0),
    ("dishwasher",    7350, 12950, 0),
    ("sink_unit",     7600, 14300, 0),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # STUDY 9550-12850 x 9600-12850: desk under the window, bookshelves
    ("dresser",       10000, 11000, 0),
    ("fia_chair",     10100, 10300, 0),
    ("wardrobe",      12200, 9700, 90),
    ("wardrobe",      12200, 10600, 90),
    # FAMILY LOUNGE 13000-16600 x 9600-15800: a sofa and two armchairs
    ("fia_sofa_3",    13500, 10800, 0),
    ("fia_tbl_coffee", 14500, 12300, 0),
    ("fia_armchair",  13300, 13600, 90),
    ("fia_armchair",  15300, 13600, 270),
    # MASTER BEDROOM 3400-7000 x 9600-15800 (ensuite and dressing nested at
    # x 7150-9400): the bed on the west wall, a sofa, a wardrobe
    ("fia_bed",       3600, 12200, 0),
    ("bedside",       3500, 14600, 0),
    ("bedside",       5100, 14600, 0),
    ("fia_sofa_2",    3700, 10000, 0),
    ("wardrobe",      5800, 9800, 0),
    # MASTER ENSUITE 7150-9400 x 9600-11800: WC, two basins, shower
    ("wc",            7250, 9600, 0),
    ("basin",         7250, 11200, 0),
    ("basin",         8050, 11200, 0),
    ("shower",        8350, 9700, 0),
    # MASTER DRESSING 7150-9400 x 11950-14600: wardrobes
    ("wardrobe",      7250, 12050, 90),
    ("wardrobe",      7250, 13000, 90),
    # BEDROOM 2 3400-7000 x 15950-19800 (ensuite nested at x 7150-9400)
    ("fia_bed",       3700, 17000, 0),
    ("bedside",       5750, 17100, 0),
    ("wardrobe",      6300, 18200, 90),
    # BEDROOM 2 ENS 7150-9400 x 15950-18050
    ("wc",            7250, 16050, 0),
    ("basin",         8500, 16050, 0),
    ("shower",        8450, 17000, 0),
    # BEDROOM 3 3400-9400 x 19950-25600 (ensuite nested at x 7150-9400)
    ("fia_bed",       4000, 22500, 0),
    ("bedside",       3550, 24900, 0),
    ("bedside",       6100, 24900, 0),
    ("wardrobe",      6000, 20300, 0),
    # BEDROOM 3 ENS 7150-9400 x 19950-22000
    ("wc",            7250, 20100, 0),
    ("basin",         7250, 21300, 0),
    ("shower",        8350, 20050, 0),
    # BEDROOM 4 13000-16600 x 15950-25600 (ensuite nested at x 13000-14800,
    # y 23100-25600)
    ("fia_bed",       14150, 17500, 90),
    ("bedside",       13350, 17600, 0),
    ("bedside",       13350, 19000, 0),
    ("wardrobe",      15500, 24000, 0),
    # BEDROOM 4 ENS 13000-14800 x 23100-25600
    ("basin",         13100, 23250, 0),
    ("wc",            13100, 24300, 0),
    ("shower",        13850, 23300, 0),
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
