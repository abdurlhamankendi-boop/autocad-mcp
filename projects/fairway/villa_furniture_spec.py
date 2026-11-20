"""
The Fairway villa -- furniture layout.

Placements are (block_key, x, y, rotation), (x, y) the BOTTOM-LEFT of the
block's footprint in plan mm; block sizes from block_catalog.json (measured
ACA content blocks, copied from the pipeline). check() proves every item is
inside its room, clear of every door swing and of every other item, keeps
its approach clearance, and that every room holds what its ROLE needs
(villa_design.FIXTURES) -- the same checks as the villa's spec, with the
basement added (BY_FLOOR "B1") and the dining seat count applied to every
DINING_ROLES room.

The catalogue has no cars, gym machines or plant; the garage, gym and plant
room are drawn empty (the cinema's two tiers are fia_sofa_long, photograph
13; the jacuzzi is the bath block).
"""

from __future__ import annotations

import json
import math
import os

import villa_design as V

CATALOG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "block_catalog.json")))

# ---------------------------------------------------------------- BASEMENT
BASEMENT = [
    # CINEMA 3400-9400 x 15900-22500: two tiers of modular sofas facing the
    # screen on the south wall; the lounge door sweeps x > 8385, y 20500-21515
    ("fia_sofa_long",  4600, 18200,   0),
    ("fia_sofa_long",  4600, 20000,   0),
    ("fia_tbl_toast",  4300, 16000,   0),          # media console under the screen
    # MEDIA LOUNGE 9550-18700 x 15900-22500: sofas round a low table (west),
    # the bar with stools (east)
    ("fia_sofa_long", 10500, 16300,   0),
    ("fia_tbl_low",   11100, 17600,   0),
    ("fia_sofa_3",    10700, 19800,   0),
    ("fia_armchair",  14000, 18000,   0),
    ("fia_tbl_toast", 15500, 21200,   0),          # bar counter
    ("fia_stool",     15600, 20500,   0),
    ("fia_stool",     16300, 20500,   0),
    ("fia_stool",     17000, 20500,   0),
    # WINE CELLAR 14350-17350 x 24300-27300: racks on the north wall, a
    # tasting table
    ("wardrobe",      14400, 26730,   0),
    ("wardrobe",      15200, 26730,   0),
    ("wardrobe",      16000, 26730,   0),
    ("fia_tbl_coffee", 15900, 25300,  0),
    # SPA 17500-20500 x 24300-29300, STEAM ROOM nested 17500-19500 x
    # 27300-29300. Jacuzzi (bath) on the east wall, shower, WC, basin.
    ("bath",          19650, 25200,  90),
    ("shower",        17550, 26200,   0),
    ("wc",            19900, 28800,   0),
    ("basin",         19700, 27400,  90),
    # LAUNDRY 14350-17350 x 27450-32800: two machines (600 block), the sink,
    # a folding table; the linen-store door stays clear
    ("dishwasher",    16700, 28200,  90),
    ("dishwasher",    16700, 28850,  90),
    ("sink_unit",     16700, 31600,  90),
    ("fia_tbl_toast", 14500, 31900,   0),
    # LINEN STORE 17500-20500 x 29450-32800
    ("wardrobe",      17550, 32230,   0),
    ("wardrobe",      18350, 32230,   0),
    ("wardrobe",      19150, 32230,   0),
    # STORE 3400-12550 x 28300-32800: shelving along the north wall
    ("wardrobe",       3500, 32230,   0),
    ("wardrobe",       4300, 32230,   0),
    ("wardrobe",       5100, 32230,   0),
    ("wardrobe",       5900, 32230,   0),
    ("wardrobe",       6700, 32230,   0),
    # PLANT ROOM 3400-9400 x 22650-28150: control cabinets (wardrobe block)
    ("wardrobe",       3450, 27580,   0),
    ("wardrobe",       4250, 27580,   0),
    # PLAY ROOM 20650-26600 x 24300-32800
    ("fia_tbl_round", 22500, 28600,   0),
    ("fia_chair_cc",  21950, 29100,  90),
    ("fia_chair_cc",  24050, 29100, 270),
    ("fia_sofa_2",    23500, 31700,   0),
    ("wardrobe",      26050, 25000,  90),
    ("wardrobe",      26050, 25800,  90),
]

# ---------------------------------------------------------------- GROUND
GROUND = [
    # KITCHEN 3400-9400 x 15900-22500 (open to the dining): the working run on
    # the west wall, the island 1.3 m off it (K-ROOM-05 1.2 m) with stools
    ("fridge",         3450, 20900,  90),
    ("hob",            3450, 19600,  90),
    ("sink_unit",      3450, 18400,  90),
    ("dishwasher",     3450, 17600,  90),
    ("fia_tbl_toast",  5400, 18300,  90),          # the marble island
    ("fia_stool",      6300, 18500,   0),
    ("fia_stool",      6300, 19100,   0),
    ("fia_stool",      6300, 19700,   0),
    # DINING 9550-15250 x 15900-22500: two tables end to end, ten chairs
    # (photograph 12): four a side and one at each end
    ("fia_tbl_dining", 11950, 16800,  90),
    ("fia_tbl_dining", 11950, 18900,  90),
    ("fia_chair",     11390, 17050,  90),
    ("fia_chair",     11390, 18050,  90),
    ("fia_chair",     11390, 19050,  90),
    ("fia_chair",     11390, 20050,  90),
    ("fia_chair",     12860, 17050, 270),
    ("fia_chair",     12860, 18050, 270),
    ("fia_chair",     12860, 19050, 270),
    ("fia_chair",     12860, 20050, 270),
    ("fia_chair",     12150, 16230,   0),
    ("fia_chair",     12150, 21020, 180),
    # LIVING 15400-26600 x 15900-22500: two seating groups facing the pool
    ("fia_sofa_long", 16500, 20500,   0),
    ("fia_tbl_coffee", 17700, 18900,  0),
    ("fia_sofa_3",    16940, 17200,   0),
    ("fia_armchair",  15700, 18400,   0),
    ("fia_sofa_ph",   22000, 20600,   0),
    ("fia_tbl_round", 22700, 18700,   0),
    ("fia_sofa_2",    22540, 17000,   0),
    # SITTING ROOM 21000-26600 x 22650-28650: shelving on the west wall
    # (photograph 8), sofa and chairs round a table
    ("wardrobe",      21050, 25000,  90),
    ("wardrobe",      21050, 25800,  90),
    ("fia_sofa_3",    22500, 26800,   0),
    ("fia_tbl_coffee", 23300, 25300,  0),
    ("fia_armchair",  22000, 24000,   0),
    ("fia_armchair",  24900, 24000,   0),
    # OFFICE 18850-26600 x 28800-32800 (hall door sweeps x < 19790)
    ("dresser",       22500, 31700,   0),          # the desk, under the window
    ("fia_chair",     22570, 31100, 180),
    ("wardrobe",      24500, 32250,   0),          # bookcases
    ("wardrobe",      25300, 32250,   0),
    ("fia_sofa_2",    20500, 28900,   0),
    ("fia_tbl_coffee", 20900, 30100,  0),
    # POWDER ROOM 18850-20850 x 22650-24400 (door sweeps x < 19585)
    ("wc",            20250, 22700,   0),
    ("basin",         19700, 23900,   0),
    # CLOAK 18850-20850 x 24550-28650
    ("wardrobe",      20300, 24650,  90),
    ("wardrobe",      20300, 25500,  90),
    ("wardrobe",      20300, 26350,  90),
    ("wardrobe",      20300, 27200,  90),
    # HALL: a console on the east wall by the front door
    ("dresser",       17780, 31000,  90),
    # MAID ROOM 3400-6400 x 22650-26650, MAID BATH nested 3400-5250 x 25000-26650
    ("bed_single",     3450, 23500,  90),
    ("wardrobe",       5550, 26050,   0),
    # MAID BATH (door from the south sweeps x 4200-5010, y < 25735)
    ("shower",         3400, 25750,   0),
    ("wc",             4450, 26250,   0),
    ("basin",          3400, 25050,   0),
    # PANTRY 6550-9400 x 24300-26650: fridge and servery sink, east wall
    ("fridge",         8750, 24400,  90),
    ("sink_unit",      8750, 25300,  90),
    # DRIVER ROOM 9550-12550 x 28500-32800, DRIVER BATH nested 11000-12550 x 28500-30200
    ("bed_single",    11550, 30650,   0),
    ("wardrobe",       9600, 28600,  90),
    # DRIVER BATH (door from the north sweeps x 11200-12010, y > 29465)
    ("shower",        11650, 28500,   0),
    ("wc",            11000, 28600,  90),
    ("basin",         12080, 29700,  90),
]

# ----------------------------------------------------------------- FIRST
FIRST = [
    # BEDROOM 2 3400-9400 x 13900-20400, en-suite nested 3400-6200 x 17600-20400
    ("fia_bed",        7050, 14800,  90),
    ("bedside",        8950, 14350,   0),
    ("bedside",        8950, 16800,   0),
    ("wardrobe",       7600, 19860,   0),
    ("wardrobe",       8400, 19860,   0),
    ("fia_armchair",   3600, 14200,   0),
    ("shower",         3400, 19500,   0),
    ("wc",             3450, 17650,   0),
    ("basin",          5280, 19900,   0),
    # BEDROOM 3 9550-15250 x 13900-20400, en-suite nested 12450-15250 x 17600-20400
    ("fia_bed",        9600, 14600,  90),
    ("bedside",        9600, 14150,   0),
    ("bedside",        9600, 16600,   0),
    ("wardrobe",      11200, 19860,   0),
    ("fia_armchair",  14200, 14100,   0),
    ("shower",        14350, 19500,   0),
    ("wc",            14700, 17650,   0),
    ("basin",         12500, 19900,   0),
    # MASTER BEDROOM 15400-26600 x 13900-20400; DRESSING nested 15400-18400 x
    # 17050-20400; EN-SUITE nested 22400-26600 x 17050-20400 (two basins)
    ("fia_bed",       19300, 15200,   0),
    ("bedside",       18850, 16600,   0),
    ("bedside",       21300, 16600,   0),
    ("fia_sofa_2",    23500, 14100,   0),
    ("fia_armchair",  15600, 14200,   0),
    ("wardrobe",      15450, 19860,   0),
    ("wardrobe",      16250, 19860,   0),
    ("wardrobe",      17050, 19860,   0),
    ("wardrobe",      15420, 18200,  90),
    ("bath",          24800, 19550,   0),
    ("basin",         22500, 19900,   0),
    ("basin",         23000, 19900,   0),
    ("shower",        25650, 17100,   0),
    ("wc",            24000, 17100,   0),
    # BEDROOM 4 3400-7950 x 22200-27200, en-suite nested 3400-5900 x 22200-24050
    # (the room's body 4.55 x 3.0 clear north of it, K-ROOM-01)
    ("bed_double",     4500, 25100,   0),
    ("bedside",        4050, 26650,   0),
    ("bedside",        6150, 26650,   0),
    ("wardrobe",       7400, 23300,  90),
    ("wardrobe",       7400, 24100,  90),
    ("shower",         3400, 23150,   0),
    ("wc",             4450, 23650,   0),
    ("basin",          3450, 22200,   0),
    # BEDROOM 5 8100-12550 x 22200-27200, en-suite nested 10050-12550 x 22200-24050
    ("bed_double",     9600, 25100,   0),
    ("bedside",        9150, 26650,   0),
    ("bedside",       11250, 26650,   0),
    ("wardrobe",       8150, 23300,  90),
    ("shower",        11650, 23150,   0),
    ("wc",            11000, 23650,   0),
    ("basin",         12050, 22200,   0),
    # FAMILY LOUNGE 18850-26600 x 22200-27200 (photograph 20)
    ("fia_sofa_long", 20500, 26000,   0),
    ("fia_tbl_coffee", 21700, 24600,  0),
    ("fia_armchair",  19300, 24300,   0),
    ("fia_armchair",  24300, 24300,   0),
]

ANNEX = []
ROOF = []
BY_FLOOR = (("B1", BASEMENT), ("GF", GROUND), ("FF", FIRST))


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
