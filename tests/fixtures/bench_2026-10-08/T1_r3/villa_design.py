"""
BENCH VILLA -- a simple modern two-storey, four-bedroom villa, Dubai, no
basement. The design as DATA, plus its derived geometry and its validator.

Brief (see BRIEF.md): plot 20000 x 32000 mm, street on the north (+y) edge,
garden south. Ground floor: entrance hall, majlis with guest WC, family
living, dining, kitchen, maid room with its own bath, laundry, store, covered
parking for two cars (carport in the front setback). First floor: master
bedroom with ensuite and dressing, three bedrooms with ensuites, family
lounge. One stair GF -> FF. Pool: an 8000 x 3500 mm pool across the garden.

Same design language as the villa pipeline and the Fairway project -- ROOMS,
OPENINGS, VOIDS, ZONE, ROLE, ... -- read by the same builders and checks.
No shapely import at module level: Blender and Unreal load this file.
"""

from __future__ import annotations

import math
import os

PROJECT = "bench"
PROJECT_TITLE = "BENCH VILLA"
OUT_NAME = "Bench"                                  # Desktop\\Bench

# ---------------------------------------------------------------- site
PLOT_W, PLOT_D = 20000.0, 32000.0
SB_FRONT, SB_SIDE, SB_REAR = 6000.0, 3000.0, 3000.0  # DBC K-SB-02 defaults

# ---------------------------------------------------------------- levels
STREET = 0.0
GF, GF_CH = 200.0, 3600.0                          # +200: forecourt rises <= 4 %
SLAB = 500.0
FF = GF + GF_CH + SLAB                             # 4300
FF_CH = 3200.0
RF = FF + FF_CH + SLAB                             # 8000 (roof slab soffit)
PARAPET, PAV_CH = 400.0, 3000.0                    # roof not accessible
WALL = 400.0
PART = 150.0
FF2FF = FF - GF                                    # 4100 (the stair rise)

LEVEL = {"GF": GF, "FF": FF, "RF": RF + SLAB}
CEIL = {"GF": GF_CH, "FF": FF_CH, "RF": PAV_CH}
FLOOR_ORDER = ("GF", "FF", "RF")
STACKED = ("GF", "FF")                             # the two storeys of the house
BELOW_GRADE_FLOORS = ()                            # no basement
GROUND_FLOOR = "GF"
STAIR_SERVES = ("GF", "FF")
FLOOR_NAME = {"GF": "GF", "FF": "FF", "RF": "ROOF"}

# Opening heights (above that floor's finished floor).
WIN_SILL, WIN_HEAD, DOOR_HEAD = 900.0, 3300.0, 2400.0
HEAD = {"GF": 3300.0, "FF": 3000.0}                # windows and slides
EXT_DOOR_HEAD = 3000.0                             # the front door
GARAGE_DOOR_HEAD = 2600.0

# Built-up area: about 420-520 m2 in the brief; 470 is the midpoint, and
# check 17 holds the outline sum to +/-10 % of it.
BRIEF_GFA = 470.0
BRIEF_SQFT = round(BRIEF_GFA * 10.7639)

# ---------------------------------------------------------------- the house
# Both storeys share one footprint: 14.0 x 16.8 m outside the walls, set back
# 6 m from the street, 3 m from the sides and 3 m from the rear.
HX0, HX1 = 3000.0, 17000.0
GF_Y0, GF_Y1 = 9200.0, 26000.0
FF_Y0, FF_Y1 = 9200.0, 26000.0


def A(x0, y0, x1, y1):
    return abs(x1 - x0) * abs(y1 - y0) / 1e6


# ================================================================= ROOMS
# (name, x1, y1, x2, y2, kind, floor)
#   kind: habitable | wet | circulation | service | amenity
CIRC, HAB, WET, SVC, AMEN = "circulation", "habitable", "wet", "service", "amenity"

ROOMS = [
    # ---- GROUND. North band: the majlis (west), the entrance HALL with the
    #      stair (centre), guest WC and cloak (east). South: the living room
    #      on the garden glass, with the dining on the east. West block: the
    #      kitchen, and the service wing (maid room and bath, laundry, store)
    #      with its own door from the west side.
    ("MAJLIS",          3400, 19950,  9400, 25600, HAB,  "GF"),
    ("HALL",            9550, 15950, 12850, 25600, CIRC, "GF"),
    ("GUEST WC",       13000, 22450, 14650, 25600, WET,  "GF"),
    ("CLOAK",          14800, 22450, 16600, 25600, SVC,  "GF"),
    ("DINING",         13000, 15950, 16600, 22300, HAB,  "GF"),
    ("LIVING",          9550,  9600, 16600, 15800, HAB,  "GF"),
    ("KITCHEN",         3400, 16000,  9400, 19800, HAB,  "GF"),
    ("SERVICE LOBBY",   3400, 12850,  6400, 15850, CIRC, "GF"),
    ("MAID ROOM",       3400,  9600,  6400, 12700, HAB,  "GF"),
    ("MAID BATH",       6550,  9600,  8000, 12700, WET,  "GF"),
    ("STORE",           8150,  9600,  9400, 12700, SVC,  "GF"),
    ("LAUNDRY",         6550, 12850,  9400, 15850, SVC,  "GF"),

    # ---- FIRST. The landing (north centre) is open to the hall below through
    #      the stair void. A corridor (centre south) serves the master, the
    #      study and the family lounge; the corridor west serves bedroom 2.
    ("LANDING",          9550, 15950, 12850, 25600, CIRC, "FF"),
    ("CORRIDOR S",       9550, 13000, 12850, 15800, CIRC, "FF"),
    ("STUDY",            9550,  9600, 12850, 12850, HAB,  "FF"),
    ("FAMILY LOUNGE",   13000,  9600, 16600, 15800, HAB,  "FF"),
    ("MASTER BEDROOM",   3400,  9600,  9400, 15800, HAB,  "FF"),
    ("MASTER ENSUITE",   7150,  9600,  9400, 11800, WET,  "FF"),   # nested
    ("MASTER DRESSING",  7150, 11950,  9400, 14600, SVC,  "FF"),   # nested
    ("BEDROOM 2",        3400, 15950,  7000, 19800, HAB,  "FF"),
    ("BEDROOM 2 ENS",    7150, 15950,  9400, 18050, WET,  "FF"),
    ("CORRIDOR W",       7150, 18200,  9400, 19800, CIRC, "FF"),
    ("BEDROOM 3",        3400, 19950,  9400, 25600, HAB,  "FF"),
    ("BEDROOM 3 ENS",    7150, 19950,  9400, 22000, WET,  "FF"),   # nested
    ("BEDROOM 4",       13000, 15950, 16600, 22950, HAB,  "FF"),
    ("BEDROOM 4 DRESSING", 14950, 23100, 16600, 25600, SVC, "FF"),
    ("BEDROOM 4 ENS",   13000, 23100, 14800, 25600, WET,  "FF"),   # nested
]

MIN_AREA = {
    "MAJLIS": 20.0, "LIVING": 30.0, "DINING": 14.0, "KITCHEN": 12.0,
    "MASTER BEDROOM": 14.0, "BEDROOM 2": 12.0, "BEDROOM 3": 12.0,
    "BEDROOM 4": 12.0, "FAMILY LOUNGE": 16.0, "MAID ROOM": 7.5,
    "MASTER ENSUITE": 4.5, "BEDROOM 2 ENS": 4.5, "BEDROOM 3 ENS": 4.5,
    "BEDROOM 4 ENS": 4.5, "MAID BATH": 2.5, "GUEST WC": 2.5,
}

ENSUITE_OF = {
    "MASTER BEDROOM": "MASTER ENSUITE",
    "BEDROOM 2": "BEDROOM 2 ENS",
    "BEDROOM 3": "BEDROOM 3 ENS",
    "BEDROOM 4": "BEDROOM 4 ENS",
}

# ============================================================ ZONES & ROLES
CIRC_Z, GUEST, FAMILY, PRIVATE, SERVICE = "circ", "guest", "family", "private", "service"
ZONE = {
    # ground
    "MAJLIS": GUEST, "GUEST WC": GUEST, "CLOAK": GUEST,
    "HALL": CIRC_Z,
    "DINING": FAMILY, "LIVING": FAMILY, "KITCHEN": SERVICE,
    "SERVICE LOBBY": CIRC_Z, "MAID ROOM": SERVICE, "MAID BATH": SERVICE,
    "STORE": SERVICE, "LAUNDRY": SERVICE,
    # first
    "LANDING": CIRC_Z, "CORRIDOR S": CIRC_Z, "CORRIDOR W": CIRC_Z,
    "STUDY": FAMILY, "FAMILY LOUNGE": FAMILY,
    "MASTER BEDROOM": PRIVATE, "MASTER ENSUITE": PRIVATE,
    "MASTER DRESSING": PRIVATE,
    "BEDROOM 2": PRIVATE, "BEDROOM 2 ENS": PRIVATE,
    "BEDROOM 3": PRIVATE, "BEDROOM 3 ENS": PRIVATE,
    "BEDROOM 4": PRIVATE, "BEDROOM 4 ENS": PRIVATE, "BEDROOM 4 DRESSING": PRIVATE,
}
ROLE = {
    "MAJLIS": "majlis", "HALL": "hall", "GUEST WC": "guest_wc",
    "CLOAK": "store", "DINING": "dining", "LIVING": "family_living",
    "KITCHEN": "kitchen", "SERVICE LOBBY": "lobby", "MAID ROOM": "maid_room",
    "MAID BATH": "maid_bath", "STORE": "store", "LAUNDRY": "laundry",
    "LANDING": "landing", "CORRIDOR S": "corridor", "CORRIDOR W": "corridor",
    "STUDY": "study", "FAMILY LOUNGE": "family_lounge",
    "MASTER BEDROOM": "master_bedroom", "MASTER ENSUITE": "ensuite",
    "MASTER DRESSING": "dressing",
    "BEDROOM 2": "bedroom", "BEDROOM 2 ENS": "ensuite",
    "BEDROOM 3": "bedroom", "BEDROOM 3 ENS": "ensuite",
    "BEDROOM 4": "bedroom", "BEDROOM 4 ENS": "ensuite", "BEDROOM 4 DRESSING": "walk_in",
}
# The brief as roles: (role, how many, minimum NET m2 each).
REQUIRED = [
    ("majlis", 1, 20.0), ("guest_wc", 1, 2.5), ("family_living", 1, 30.0),
    ("dining", 1, 14.0), ("kitchen", 1, 12.0), ("maid_room", 1, 7.5),
    ("maid_bath", 1, 2.5), ("laundry", 1, 4.0), ("store", 2, 3.0),
    ("master_bedroom", 1, 14.0), ("bedroom", 3, 12.0), ("ensuite", 4, 4.5),
    ("dressing", 1, 5.0), ("family_lounge", 1, 16.0),
]
FIXTURES = {
    "ensuite": ["wc", "basin", "shower|bath"],
    "guest_wc": ["wc", "basin"],
    "maid_bath": ["wc", "basin", "shower"],
    "kitchen": ["sink_unit", "hob", "fridge"],
    "dining": ["chair"],
}
DINING_ROLES = ("dining", "formal_dining")
MIN_DINING_SEATS = 8
FIXTURE_COUNT = {("FF", "MASTER ENSUITE"): {"basin": 2}}
DAYLIGHT_EXEMPT_ROLES = ("laundry", "store")

# ============================================================== SHADING
# SHADES: boxes (x0, y0, x1, y1, z0, z1). The carport pergola over the two open
# bays in the front setback (K-SB-05 allows light parking shades there), and
# the timber canopy over the living room's garden glass.
SHADES = [
    (3400.0, 26000.0, 9400.0, 31650.0, 3000.0, 3150.0),
    (9800.0, 7200.0, 16200.0, 9550.0, GF + 3300.0, GF + 3600.0),
]
# OVERHANGS: horizontal projections that are part of the building -- the roof
# frame over the first floor's garden windows (2.0 m out, over the glass).
OVERHANGS = [
    (3000.0, 7200.0, 16600.0, 9550.0, RF, RF + SLAB),

]
FIN_ARRAYS = []
BALCONY = None
STONE_SKIN = 50.0
STONE_ZONES = []
STONE_FREE = [
    (3400.0, 31300.0, 0.0, 3700.0, 31600.0, 3000.0),                 # carport piers
    (9100.0, 31300.0, 0.0, 9400.0, 31600.0, 3000.0),
]

# ============================================================== OPENINGS
# (floor, kind, axis, wall_t0, wall_t1, a, b, room_a, room_b, swing_deg)
#   axis "v": wall spans x t0..t1, opening runs y a..b
#   axis "h": wall spans y t0..t1, opening runs x a..b
# Doors: 1015 general, 810 wet rooms (DBC K-DOOR-01/-02 + 100). Swing: 90 =
# leaf opens to +y, 270 to -y, 0 to +x, 180 to -x.
DOOR, WIN, OPEN, SLIDE = "door", "window", "open", "slide"

OPENINGS = [
    # ================= GROUND, external
    ("GF", DOOR, "h", 25600, 26000, 10000, 11015, "HALL", None, 270),      # front door
    ("GF", WIN, "h", 25600, 26000, 3600, 5600, "MAJLIS", None, None),      # north
    ("GF", WIN, "h", 25600, 26000, 13400, 14300, "GUEST WC", None, None),
    ("GF", WIN, "h", 25600, 26000, 15000, 16300, "CLOAK", None, None),
    ("GF", WIN, "v", 16600, 17000, 17000, 18200, "DINING", None, None),    # east
    ("GF", WIN, "v", 16600, 17000, 20000, 21200, "DINING", None, None),
    ("GF", WIN, "v", 3000, 3400, 16600, 17800, "KITCHEN", None, None),     # west
    ("GF", WIN, "v", 3000, 3400, 10000, 11000, "MAID ROOM", None, None),
    ("GF", DOOR, "v", 3000, 3400, 13600, 14615, "SERVICE LOBBY", None, 0),  # service door
    ("GF", SLIDE, "h", 9200, 9600, 10000, 15800, "LIVING", None, None),    # garden glass
    # ================= GROUND, internal
    ("GF", DOOR, "v", 9400, 9550, 18300, 19315, "KITCHEN", "HALL", 0),
    ("GF", DOOR, "v", 9400, 9550, 21000, 22015, "MAJLIS", "HALL", 180),
    ("GF", DOOR, "h", 15800, 15950, 10000, 11015, "LIVING", "HALL", 90),
    ("GF", DOOR, "v", 12850, 13000, 17500, 18515, "HALL", "DINING", 180),
    ("GF", DOOR, "h", 15800, 15950, 13600, 14615, "LIVING", "DINING", 90),
    ("GF", DOOR, "v", 12850, 13000, 23600, 24615, "HALL", "GUEST WC", 0),
    ("GF", DOOR, "v", 14650, 14800, 24000, 25015, "GUEST WC", "CLOAK", 0),
    ("GF", DOOR, "h", 12700, 12850, 4100, 5115, "MAID ROOM", "SERVICE LOBBY", 90),
    ("GF", DOOR, "v", 6400, 6550, 10000, 11015, "MAID ROOM", "MAID BATH", 0),
    ("GF", DOOR, "v", 6400, 6550, 13600, 14615, "SERVICE LOBBY", "LAUNDRY", 0),
    ("GF", DOOR, "h", 12700, 12850, 8300, 9315, "STORE", "LAUNDRY", 90),
    ("GF", DOOR, "h", 15850, 16000, 4000, 5015, "SERVICE LOBBY", "KITCHEN", 90),

    # ================= FIRST, external
    ("FF", WIN, "v", 3000, 3400, 10500, 11700, "MASTER BEDROOM", None, None),
    ("FF", WIN, "v", 3000, 3400, 16800, 17900, "BEDROOM 2", None, None),
    ("FF", WIN, "v", 3000, 3400, 23000, 24100, "BEDROOM 3", None, None),
    ("FF", WIN, "v", 16600, 17000, 10200, 11400, "FAMILY LOUNGE", None, None),
    ("FF", WIN, "v", 16600, 17000, 21000, 22200, "BEDROOM 4", None, None),
    ("FF", WIN, "v", 16600, 17000, 17600, 18800, "BEDROOM 4", None, None),
    ("FF", WIN, "h", 9200, 9600, 4000, 5200, "MASTER BEDROOM", None, None),
    ("FF", WIN, "h", 9200, 9600, 14000, 15200, "FAMILY LOUNGE", None, None),
    ("FF", WIN, "h", 9200, 9600, 10400, 11600, "STUDY", None, None),
    ("FF", WIN, "h", 25600, 26000, 4400, 5500, "BEDROOM 3", None, None),
    ("FF", WIN, "h", 25600, 26000, 15000, 16200, "BEDROOM 4 DRESSING", None, None),
    # ================= FIRST, internal
    ("FF", DOOR, "v", 9400, 9550, 18400, 19415, "CORRIDOR W", "LANDING", 180),
    ("FF", DOOR, "v", 9400, 9550, 22500, 23515, "BEDROOM 3", "LANDING", 180),
    ("FF", DOOR, "v", 12850, 13000, 20600, 21615, "LANDING", "BEDROOM 4", 0),
    ("FF", DOOR, "h", 15800, 15950, 10500, 11515, "CORRIDOR S", "LANDING", 90),
    ("FF", DOOR, "h", 12850, 13000, 10500, 11515, "STUDY", "CORRIDOR S", 90),
    ("FF", DOOR, "v", 12850, 13000, 14000, 15015, "CORRIDOR S", "FAMILY LOUNGE", 180),
    ("FF", DOOR, "v", 9400, 9550, 14750, 15765, "MASTER BEDROOM", "CORRIDOR S", 180),
    ("FF", DOOR, "v", 7000, 7150, 10000, 11015, "MASTER BEDROOM", "MASTER ENSUITE", 0),
    ("FF", DOOR, "h", 11800, 11950, 8350, 9365, "MASTER ENSUITE", "MASTER DRESSING", 90),
    ("FF", DOOR, "v", 7000, 7150, 12500, 13515, "MASTER BEDROOM", "MASTER DRESSING", 180),
    ("FF", DOOR, "v", 7000, 7150, 16600, 17615, "BEDROOM 2", "BEDROOM 2 ENS", 0),
    ("FF", DOOR, "v", 7000, 7150, 18400, 19415, "BEDROOM 2", "CORRIDOR W", 0),
    ("FF", DOOR, "h", 19800, 19950, 7600, 8615, "CORRIDOR W", "BEDROOM 3 ENS", 270),
    ("FF", DOOR, "h", 22950, 23100, 13300, 14315, "BEDROOM 4", "BEDROOM 4 ENS", 270),
    ("FF", DOOR, "h", 22950, 23100, 15100, 16115, "BEDROOM 4", "BEDROOM 4 DRESSING", 270),
]

# Windows facing the pool that do not open (K-POOL-01): none here.
FIXED_GLAZING = {("GF", "MAID ROOM")}   # its west window is fixed: the pool is 4 m away (K-POOL-01)
SCREENED = {("GF", "SERVICE LOBBY")}   # the service door on the west face: a screened service yard

# ================================================================= VOIDS
# (name, x1, y1, x2, y2, floors cut): the double-height hall -- an opening in
# the first-floor slab over the hall's north part, inside the landing room.
VOIDS = [
    ("STAIR VOID", 9550, 19200, 12850, 25600, ("FF",)),
]
ENTRY_ROOM = {"GF": "HALL", "FF": "LANDING"}

# ================================================================= STAIRS
# One stair, GF -> FF: a straight flight rising south from the north wall of
# the hall, 24 risers of 170.8 mm, treads 280 mm, 1200 mm wide.
STAIRS = [
    {"name": "feature stair", "type": "straight", "from": "GF", "to": "FF",
     "rect": (11650.0, 18880.0, 12850.0, 25600.0), "risers": 24,
     "going": 280.0, "dir": -1, "foot": 25600.0, "open": ("c0", "c1"),
     "solid": False, "waist": 90.0, "room": "HALL"},
]
STAIR = STAIRS[0]["rect"]
RISERS = STAIRS[0]["risers"]
STAIR_GOING = STAIRS[0]["going"]
STAIR_FLIGHTS = 1
STAIR_SOLID = False
HANDRAIL_H, RAIL_W, RAIL_T, RAIL_GAP, POST_W = 900.0, 40.0, 30.0, 60.0, 40.0
GUARD_H, GUARD_T, GUARD_DROP = 1200.0, 30.0, 760.0

# ================================================================= POOL
# A skimmer pool 8.0 m across the garden by 3.5 m deep, blue mosaic, coping
# flush with the deck at +200, water 100 below. The floor runs from 1.5 m deep
# at the south end to 1.1 m at the house end: 11.4 % (K-POOL-02/-03).
POOL_X0, POOL_X1 = 6000.0, 14000.0
POOL_Y0, POOL_Y1 = 3500.0, 7000.0
POOL_COPING = 400.0
POOL_TW = GF - 100.0                               # +100 water, coping at +200
POOL_CREST = POOL_TW                               # a skimmer pool: no weir
POOL_SHALLOW_FL = POOL_TW - 1100.0
POOL_FL = POOL_TW - 1500.0
POOL_FLOOR = (
    (POOL_Y0, POOL_FL),
    (POOL_Y1, POOL_SHALLOW_FL),
)
# The sun ledge: an in-water bench 300 below the water along the house end.
POOL_LEDGE = (POOL_X0, POOL_Y1 - 1500.0, POOL_X1, POOL_Y1, POOL_TW - 300.0)
POOL_PLANT = None
BASIN_GRATED = False
POOL_BARRIER = {
    "type": "house walls + boundary walls + 1.2 m glass fences with self-closing "
            "gates across both side strips (K-POOL-04/-07/-08)",
    "garden_doors": "self-closing, self-latching, alarmed (K-POOL-07/-08)",
}
TERRACE = GF_Y0 - POOL_Y1                          # 2200: house glass to the water

# ================================================================= SITE
BOUNDARY_T, BOUNDARY_H = 350.0, 2400.0
VEHICLE_GATE = (3500.0, 9300.0)                    # sliding, onto the car porch
PED_GATE = (10000.0, 11600.0)                      # onto the front door
GATE_HEAD = 2400.0
PATH_MIN_W = 900.0
PORCH_X0, PORCH_X1 = 3400.0, 9400.0               # two open bays, 3000 each
PORCH_Y0, PORCH_Y1 = GF_Y1, PLOT_D - BOUNDARY_T
GATE_X0, GATE_X1 = VEHICLE_GATE
# The forecourt falls from the house threshold to the street: 200 over 5650
# = 3.5 % (K-PARK-02 <= 4 %).
RAMP_Y0, RAMP_Y1 = GF_Y1, PLOT_D - BOUNDARY_T
GARDEN_Z = GF                                      # the garden is level with GF
POOL_GARDEN_Y1 = GF_Y0                             # the pool garden: south of the house
GUARDS_EXTRA = [
    (BOUNDARY_T, GF_Y0, HX0, GF_Y0 + GUARD_T, GF, GF + 1200.0),
    (HX1, GF_Y0, PLOT_W - BOUNDARY_T, GF_Y0 + GUARD_T, GF, GF + 1200.0),
]
ROOF_ACCESSIBLE = False
DEEP_REVEAL_MAX_W = 1200.0

# ================================================================= OUTPUTS
PLAN_SHEETS = [("GF", "A-102", "GROUND FLOOR PLAN"),
               ("FF", "A-103", "FIRST FLOOR PLAN")]
SECTION_X = 11700.0
SECTION_TEXT = ("SECTION A-A (x 11700): HALL WITH THE STAIR AND THE LANDING "
                "VOID, LIVING, POOL")
POOL_LABEL = "POOL 8.0 x 3.5 m"
SITE_TREES = [(1600, 4000, 3200), (1600, 17000, 3200), (18400, 4000, 3200),
              (18400, 16000, 3000), (1600, 24000, 3000)]
RENDER_VIEWS = {
    "garden_se":   {"eye": (16.5, 3.0, 1.7), "target": (10.0, 14.0, 3.0),
                    "lens": 24, "sun": (255.0, 12.0), "photo": "-"},
    "street":      {"eye": (10.0, 42.0, 1.7), "target": (10.0, 28.0, 4.0),
                    "lens": 28, "sun": (250.0, 12.0), "photo": "-"},
    "aerial_sw":   {"eye": (-12.0, -10.0, 22.0), "target": (10.0, 16.0, 2.0),
                    "lens": 28, "sun": (240.0, 28.0), "photo": "-"},
}
RENDER_CONTEXT = {"south": "garden"}
MATERIALS = {
    "walls":    {"kind": "render_white", "color": (0.92, 0.91, 0.88), "roughness": 0.85},
    "slabs":    {"kind": "render_white", "color": (0.92, 0.91, 0.88), "roughness": 0.85},
    "roof":     {"kind": "render_white", "color": (0.93, 0.92, 0.90), "roughness": 0.85},
    "base":     {"kind": "concrete", "color": (0.55, 0.55, 0.53), "roughness": 0.9},
    "stone":    {"kind": "stone_dark", "color": (0.20, 0.20, 0.21), "roughness": 0.9},
    "fins":     {"kind": "timber", "color": (0.45, 0.30, 0.18), "roughness": 0.6},
    "frames":   {"kind": "metal_black", "color": (0.05, 0.05, 0.055), "roughness": 0.35},
    "door":     {"kind": "timber_dark", "color": (0.24, 0.16, 0.10), "roughness": 0.5},
    "pool":     {"kind": "limestone", "color": (0.86, 0.84, 0.78), "roughness": 0.7},
    "water":    {"kind": "water", "color": (0.05, 0.42, 0.62), "roughness": 0.02},
    "paving":   {"kind": "limestone", "color": (0.87, 0.84, 0.77), "roughness": 0.75},
    "deck":     {"kind": "timber_deck", "color": (0.47, 0.31, 0.20), "roughness": 0.65},
    "drive":    {"kind": "interlock", "color": (0.58, 0.56, 0.53), "roughness": 0.85},
    "lawn":     {"kind": "grass", "color": (0.26, 0.50, 0.15), "roughness": 0.95},
    "planting": {"kind": "hedge", "color": (0.20, 0.36, 0.15), "roughness": 0.95},
    "gravel":   {"kind": "gravel", "color": (0.80, 0.77, 0.70), "roughness": 0.95},
    "terrain":  {"kind": "soil", "color": (0.55, 0.47, 0.36), "roughness": 1.0},
    "boundary": {"kind": "render_white", "color": (0.90, 0.89, 0.86), "roughness": 0.85},
    "glass":    {"kind": "glass", "color": (0.60, 0.70, 0.72), "roughness": 0.02},
    "guards":   {"kind": "glass", "color": (0.60, 0.72, 0.74), "roughness": 0.02},
    "stair":    {"kind": "travertine", "color": (0.86, 0.82, 0.74), "roughness": 0.5},
    "rails":    {"kind": "metal_black", "color": (0.05, 0.05, 0.055), "roughness": 0.35},
}


def ground_surfaces():
    """The site as 2-D surfaces (bench): house, pool zone, terrace round the
    deck under the canopy, path, lawn, beds, gravel side strip and the forecourt
    drive. Keys as the builders read them."""
    from shapely.geometry import box as _b
    from shapely.ops import unary_union
    T, W, D = BOUNDARY_T, PLOT_W, PLOT_D
    house = unary_union([outline(f) for f in ("GF", "FF")])
    shell = _b(*pool_shell_rect())
    pool = _b(POOL_X0, POOL_Y0, POOL_X1, POOL_Y1)
    terr = _b(HX0, POOL_Y1 + POOL_COPING, HX1, GF_Y0)
    ring = _b(POOL_X0 - POOL_COPING - 1200.0, POOL_Y0 - POOL_COPING - 1200.0, POOL_X1 + POOL_COPING + 1200.0, POOL_Y1 + POOL_COPING + 1200.0).difference(shell)
    deck = unary_union([ring, _b(9800.0, POOL_Y1 + POOL_COPING, 16200.0, GF_Y0)])
    paving = terr.difference(deck).difference(shell)
    beds = unary_union([_b(T, T, W - T, T + 1200.0), _b(T, T, T + 1200.0, GF_Y0),
                        _b(W - T - 1200.0, T, W - T, GF_Y0)]) \
        .difference(unary_union([deck, paving, shell, house]))
    west = _b(T, GF_Y0, HX0, GF_Y1)
    east = _b(HX1, GF_Y0, W - T, GF_Y1)
    path_e = _b(HX1 + 800.0, GF_Y0, HX1 + 1800.0, GF_Y1)
    garden = _b(T, T, W - T, GF_Y0)
    lawn = unary_union([garden.difference(unary_union([deck, paving, shell, beds])),
                        east.difference(path_e)])
    fore = _b(T, GF_Y1, W - T, D - T)
    entry = _b(9700.0, GF_Y1, 11900.0, D - T)
    planters = _b(13900.0, GF_Y1, W - T, D - T)
    drive = fore.difference(entry).difference(planters)
    return {"house": house, "poolzone": shell, "poolsurround": shell.difference(pool),
            "terrace": paving, "deck": deck, "path": unary_union([path_e, entry]),
            "lawn": lawn, "beds": unary_union([beds, planters]),
            "mulch": west, "drive": drive}

# ================================================================ HELPERS
def rooms_on(floor):
    return [r for r in ROOMS if r[6] == floor]


def rect(r):
    return (r[1], r[2], r[3], r[4])


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def contains(outer, inner):
    return (outer[0] <= inner[0] and outer[1] <= inner[1]
            and outer[2] >= inner[2] and outer[3] >= inner[3])


def threshold(room_rect, axis, t0, t1, a, b, reach=900.0):
    """The strip of floor a door lands on, 900 inside `room_rect`, or None if
    the wall is not on an edge of this room."""
    x0, y0, x1, y1 = room_rect
    if axis == "h":
        if abs(t1 - y0) < 200:
            lo, hi = y0, y0 + reach
        elif abs(t0 - y1) < 200:
            lo, hi = y1 - reach, y1
        else:
            return None
        return (min(a, b), lo, max(a, b), hi)
    if abs(t1 - x0) < 200:
        lo, hi = x0, x0 + reach
    elif abs(t0 - x1) < 200:
        lo, hi = x1 - reach, x1
    else:
        return None
    return (lo, min(a, b), hi, max(a, b))


def children(room):
    """Rooms fully inside `room` on the same floor -- its en-suite, dressing."""
    return [q for q in ROOMS if q[6] == room[6] and q[0] != room[0]
            and contains(rect(room), rect(q))]


def net_poly(room):
    """A room's floor: its rectangle less every nested child and the
    partition round it."""
    from shapely.geometry import box as _box
    g = _box(*rect(room))
    for c in children(room):
        g = g.difference(_box(*rect(c)).buffer(PART, join_style=2, mitre_limit=8))
    return g


def net_area(room):
    return net_poly(room).area / 1e6


def fabric(floor):
    """External skin, partitions, internal envelope -- derived from the rooms
    (the 150 gaps between room polygons ARE the partitions)."""
    from shapely.ops import unary_union
    polys = [net_poly(r) for r in ROOMS if r[6] == floor]
    rooms = unary_union(polys)
    half = PART / 2.0
    inner = rooms.buffer(half, join_style=2, mitre_limit=8.0) \
                 .buffer(-half, join_style=2, mitre_limit=8.0)
    outer = inner.buffer(WALL, join_style=2, mitre_limit=8.0)
    return outer.difference(inner), inner.difference(rooms), inner


def void_rect(o):
    from shapely.geometry import box as _box
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    if axis == "h":
        return _box(min(a, b), min(t0, t1), max(a, b), max(t0, t1))
    return _box(min(t0, t1), min(a, b), max(t0, t1), max(a, b))


def floors():
    """Floors that actually have rooms, bottom-up."""
    present = {r[6] for r in ROOMS}
    return [f for f in FLOOR_ORDER if f in present]


def outline(floor):
    """Outside face of a floor's external walls."""
    return fabric(floor)[2].buffer(WALL, join_style=2, mitre_limit=8)


def opening_z(o):
    """(bottom, top) of an opening's void, absolute mm: windows sill-to-head,
    slides floor-to-head (floor-to-ceiling glass), doors to DOOR_HEAD (the
    front door and the garage door have their own)."""
    fl, kind, ra, rb = o[0], o[1], o[7], o[8]
    base = LEVEL[fl]
    head = HEAD.get(fl, WIN_HEAD)
    if kind == WIN:
        return base + WIN_SILL, base + head
    if kind == SLIDE:
        if ra == "GARAGE" and rb is None:
            return base, base + GARAGE_DOOR_HEAD
        return base, base + head
    if kind == DOOR and rb is None:
        return base, base + EXT_DOOR_HEAD
    return base, base + DOOR_HEAD


def fins():
    """Every fin as a box (x0, y0, x1, y1, z0, z1), from FIN_ARRAYS."""
    out = []
    for f in FIN_ARRAYS:
        a0, a1 = (f["y0"], f["y1"]) if f["along"] == "y" else (f["x0"], f["x1"])
        s = a0
        while s + f["t"] <= a1 + 1e-6:
            if f["along"] == "y":
                out.append((f["x0"], s, f["x1"], s + f["t"], f["z0"], f["z1"]))
            else:
                out.append((s, f["y0"], s + f["t"], f["y1"], f["z0"], f["z1"]))
            s += f["pitch"]
    return out


def facing(o):
    """Compass face of an EXTERNAL opening: 'N', 'S', 'E' or 'W'."""
    from shapely.geometry import Point
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    w0, w1 = min(t0, t1), max(t0, t1)
    mid = (a + b) / 2
    out = outline(fl)
    if axis == "h":
        return "N" if not out.contains(Point(mid, w1 + 10)) else "S"
    return "E" if not out.contains(Point(w1 + 10, mid)) else "W"


def door_graph(fl):
    adj = {r[0]: set() for r in rooms_on(fl)}
    ext = set()
    for o in OPENINGS:
        if o[0] != fl or o[1] == WIN:
            continue
        ra, rb = o[7], o[8]
        if rb is None:
            if ra in adj:
                ext.add(ra)
            continue
        if ra in adj and rb in adj:
            adj[ra].add(rb)
            adj[rb].add(ra)
    return adj, ext


def reach(adj, starts, through):
    seen = set(starts)
    stack = list(starts)
    while stack:
        n = stack.pop()
        for m in adj.get(n, ()):
            if m in seen:
                continue
            seen.add(m)
            if through(m):
                stack.append(m)
    return seen


def cut_box(o):
    """The void an opening cuts (x0, y0, z0, x1, y1, z1) -- through the whole
    wall, at opening_z (villa_geom.cut_box says the same)."""
    x0, y0, x1, y1 = void_rect(o).bounds
    z0, z1 = opening_z(o)
    return (x0, y0, z0, x1, y1, z1)


def yz_prism(ring, x0, x1):
    return {"yz": [(float(y), float(z)) for y, z in ring], "x": (float(x0), float(x1))}


def xz_prism(ring, y0, y1):
    return {"xz": [(float(x), float(z)) for x, z in ring], "y": (float(y0), float(y1))}


def poly_prism(poly, z0, z1):
    """A plan polygon extruded z0..z1 -- the builders' third part type."""
    return {"poly": poly, "z": (float(z0), float(z1))}


# ============================================================== ENVELOPE
def _edge(g, w=350.0):
    return g.difference(g.buffer(-w, join_style=2, mitre_limit=8))


def roof_poly():
    """The roof slab's plan: the first floor plus the roof frame overhangs."""
    from shapely.geometry import box as _box
    from shapely.ops import unary_union
    _, _, in_ff = fabric("FF")
    out_ff = in_ff.buffer(WALL, join_style=2, mitre_limit=8)
    return unary_union([out_ff] + [_box(o[0], o[1], o[2], o[3]) for o in OVERHANGS
                                   if abs(o[4] - RF) < 1.0])


def envelope():
    """Every footprint the builders extrude, derived once. The villa's keys
    (out_gf, out_ff, in_gf, upper, dh, dh_in, ff_slab, single,
    parapet_single, parapet_roof) plus the basement's (out_b1, in_b1) and
    the ground floor's slab (gf_slab: over the basement, less the service
    stair well). No double-height box outside the first floor: the hall's
    void is INSIDE it (dh / dh_in empty)."""
    from shapely.geometry import Polygon, box as _box
    from shapely.ops import unary_union
    in_b1 = Polygon()                  # no basement in this design
    _, _, in_gf = fabric("GF")
    _, _, in_ff = fabric("FF")
    out_b1 = in_b1
    out_gf = in_gf.buffer(WALL, join_style=2, mitre_limit=8)
    out_ff = in_ff.buffer(WALL, join_style=2, mitre_limit=8)
    ff_slab = unary_union([out_gf, out_ff])
    gf_slab = out_gf
    for _, x0, y0, x1, y1, fls in VOIDS:
        if "FF" in fls:
            ff_slab = ff_slab.difference(_box(x0, y0, x1, y1).intersection(in_ff))
        if "GF" in fls:
            gf_slab = gf_slab.difference(_box(x0, y0, x1, y1).intersection(in_gf))
    single = out_gf.difference(out_ff)
    empty = Polygon()
    return {"out_b1": out_b1, "in_b1": in_b1, "out_gf": out_gf, "in_gf": in_gf,
            "out_ff": out_ff, "in_ff": in_ff, "upper": out_ff, "dh": empty,
            "dh_in": empty, "ff_slab": ff_slab, "gf_slab": gf_slab,
            "single": single,
            "parapet_single": single.intersection(_edge(out_gf)),
            "parapet_roof": _edge(roof_poly())}


def _stone_cut_boxes():
    return [tuple(z) for z in STONE_ZONES]


def massing():
    """The building's material groups, COMPLETE: {group: [(op, part)]}, op
    'add' or 'cut'; a part is a box (x0, y0, z0, x1, y1, z1), a y-z / x-z
    profile, or poly_prism(). A builder makes each group as union(adds) -
    union(cuts) and does NOT cut openings again -- they are cut here, in
    every group they pass through.

      base   the basement: its floor slab and walls (concrete, below grade)
      slabs  the GF slab (over the basement, less the service-stair well),
             the FF slab (incl. the 2 m cantilever and the ground floor's
             roof, less the hall's stair void), the balcony
      walls  GF and FF walls, white render (less the stone skin)
      roof   the roof slab with its frame overhangs, and the parapets
      stone  the east flank's cladding skin, the BBQ wall, the canopy pier,
             the carport piers
    """
    from shapely.geometry import box as _box
    E = envelope()
    gf_top = FF - SLAB
    stone = _stone_cut_boxes()
    opening_cuts = {fl: [cut_box(o) for o in OPENINGS if o[0] == fl]
                    for fl in ("GF", "FF")}
    g = {k: [] for k in ("base", "slabs", "walls", "roof", "stone")}
   # ---- slabs
    g["slabs"].append(("add", poly_prism(E["gf_slab"], GF - SLAB, GF)))
    g["slabs"].append(("add", poly_prism(E["ff_slab"], FF - SLAB, FF)))
    if BALCONY:
        bx0, by0, bx1, by1 = BALCONY
        g["slabs"].append(("add", (bx0, by0, FF - SLAB, bx1, by1, FF)))
    g["slabs"] += [("cut", b) for b in stone]
    # ---- walls
    g["walls"].append(("add", poly_prism(E["out_gf"], GF, gf_top)))
    g["walls"].append(("add", poly_prism(E["out_ff"], FF, RF)))
    for r in rooms_on("GF"):
        g["walls"].append(("cut", poly_prism(net_poly(r), GF, gf_top)))
    for r in rooms_on("FF"):
        g["walls"].append(("cut", poly_prism(net_poly(r), FF, RF)))
    for _, x0, y0, x1, y1, fls in VOIDS:
        if "FF" in fls:
            g["walls"].append(("cut", poly_prism(
                _box(x0, y0, x1, y1).intersection(E["in_ff"]), FF, RF)))
    g["walls"] += [("cut", b) for b in opening_cuts["GF"] + opening_cuts["FF"]]
    g["walls"] += [("cut", b) for b in stone]
    # ---- roof
    g["roof"].append(("add", poly_prism(roof_poly(), RF, RF + SLAB)))
    g["roof"].append(("add", poly_prism(E["parapet_roof"], RF + SLAB,
                                        RF + SLAB + PARAPET)))
    if E["parapet_single"].area > 1.0:
        g["roof"].append(("add", poly_prism(E["parapet_single"], FF, FF + PARAPET)))
    g["roof"] += [("cut", b) for b in stone]
    # ---- stone
    g["stone"] += [("add", b) for b in stone + [tuple(s) for s in STONE_FREE]]
    g["stone"] += [("cut", b) for b in opening_cuts["GF"] + opening_cuts["FF"]]
    return g


# ================================================================ THE SITE
def ramp_z(y):
    """Finished level of the forecourt at y: GF at the house, the street at
    the gate line, straight between RAMP_Y0 and RAMP_Y1."""
    if y <= RAMP_Y0:
        return GF
    if y >= RAMP_Y1:
        return STREET
    return GF + (STREET - GF) * (y - RAMP_Y0) / (RAMP_Y1 - RAMP_Y0)


def ground_at(y):
    """Finished ground outside the house: level with the ground floor
    everywhere inside the boundary, except the forecourt ramp."""
    return ramp_z(y)


def garden_platform():
    """The POOL GARDEN: the plot inside the boundary wall south of the
    house, at GARDEN_Z. villa_dbc proves its edge is closed (K-POOL-08) --
    by the house, the boundary wall and the two side-strip fences."""
    from shapely.geometry import box as _box
    T = BOUNDARY_T
    return _box(T, T, PLOT_W - T, POOL_GARDEN_Y1)


def pool_shell_rect():
    c = POOL_COPING
    return (POOL_X0 - c, POOL_Y0 - c, POOL_X1 + c, POOL_Y1 + c)


def _ground_surfaces_fairway():
    """The site as 2-D surfaces, one shapely geometry each -- the hook
    villa_colour.ground_surfaces() returns when the design has one (site
    plan fills, the glTF / AutoCAD landscape of the villa builders, and
    villa_dbc's K-POOL-09 deck ring). Keys as the villa's: house, poolzone,
    poolsurround, terrace, deck, path, lawn, beds, mulch, drive."""
    from shapely.geometry import box as _b
    from shapely.ops import unary_union
    T, W, D = BOUNDARY_T, PLOT_W, PLOT_D
    house = unary_union([outline(f) for f in ("GF", "FF")]
                        + [_b(s[0], s[1], s[3], s[4]) for s in STONE_FREE])
    shell = _b(*pool_shell_rect())
    pool = _b(POOL_X0, POOL_Y0, POOL_X1, POOL_Y1)
    site = _b(T, T, W - T, D - T)
    # hard surfaces of the pool garden
    bbq = _b(HX0 + 300.0, 9500.0, 9400.0, GF_Y0)
    sun = _b(POOL_X1 + POOL_COPING, 1900.0, HX1 - 400.0, POOL_Y1 + POOL_COPING)
    terrace = _b(9400.0, POOL_Y1 + POOL_COPING, HX1, GF_Y0)
    ring = _b(POOL_X0 - POOL_COPING - 1200.0, 1900.0, POOL_X1 + POOL_COPING,
              POOL_Y1 + POOL_COPING).difference(shell).difference(sun)
    deck = unary_union([bbq, sun])
    paving = unary_union([terrace, ring]).difference(deck)
    # planting: hedges along the rear and side boundaries of the garden
    beds = unary_union([_b(T, T, W - T, T + 1200.0),
                        _b(T, T, T + 1200.0, GF_Y0),
                        _b(W - T - 1200.0, T, W - T, GF_Y0)]) \
        .difference(unary_union([deck, paving, shell]))
    # side strips: gravel west (service side), lawn + stepping path east
    west = _b(T, GF_Y0, HX0, GF_Y1)
    east = _b(HX1, GF_Y0, W - T, GF_Y1)
    path_e = _b(HX1 + 800.0, GF_Y0, HX1 + 1800.0, GF_Y1)
    # forecourt: drive, the entrance path, two planters
    fore = _b(T, GF_Y1, W - T, D - T)
    entry = _b(PED_GATE[0] - 300.0, GF_Y1, PED_GATE[1] + 300.0, D - T)
    planters = unary_union([_b(10000.0, 36400.0, 14500.0, D - T),
                            _b(17300.0, 36400.0, W - T, D - T)])
    drive = fore.difference(entry).difference(planters)
    garden = _b(T, T, W - T, GF_Y0)
    lawn = unary_union([garden.difference(unary_union([deck, paving, shell, beds])),
                        east.difference(path_e)])
    return {"house": house, "poolzone": shell, "poolsurround": shell.difference(pool),
            "terrace": paving, "deck": deck, "path": unary_union([path_e, entry]),
            "lawn": lawn, "beds": unary_union([beds, planters]),
            "mulch": west, "drive": drive}


FINISH_T = 40.0
HEDGE_H = 1800.0


def _forecourt_part(poly, z_top_off, thick):
    """A forecourt surface on the ramp, `thick` deep, its top offset
    z_top_off from the finished level ramp_z(y). `poly` is split at RAMP_Y0
    and RAMP_Y1: south of the ramp's head a prism at GF, past the gate line
    a prism at STREET, and between them y-z wedges. A y-z wedge is extruded
    along x, so the ramp band is cut into rectangles, in bands between every
    y the outline turns at (the drive is an L round the planters, which the
    single-rectangle version refused). Surfaces must be rectilinear."""
    from shapely.geometry import box as _b

    def polys(g):
        return [q for q in getattr(g, "geoms", [g])
                if q.geom_type == "Polygon" and not q.is_empty and q.area >= 1.0]

    parts = []
    for p in polys(poly):
        flat = p.intersection(_b(-1e6, -1e6, 1e6, RAMP_Y0))
        if flat.area > 1.0:
            parts.append(poly_prism(flat, GF + z_top_off - thick, GF + z_top_off))
        street = p.intersection(_b(-1e6, RAMP_Y1, 1e6, 1e6))
        if street.area > 1.0:
            parts.append(poly_prism(street, STREET + z_top_off - thick,
                                    STREET + z_top_off))
        ramp = p.intersection(_b(-1e6, RAMP_Y0, 1e6, RAMP_Y1))
        ys = sorted({RAMP_Y0, RAMP_Y1} | {round(y, 6) for q in polys(ramp)
                                          for ring in [q.exterior, *q.interiors]
                                          for _x, y in ring.coords})
        for ya, yb in zip(ys, ys[1:]):
            if yb - ya < 1.0:
                continue
            for q in polys(ramp.intersection(_b(-1e6, ya, 1e6, yb))):
                x0, y0, x1, y1 = q.bounds
                if abs(q.area - (x1 - x0) * (y1 - y0)) > 1.0:
                    raise ValueError("forecourt surfaces must be rectilinear")
                ring = [(y0, ramp_z(y0) + z_top_off - thick),
                        (y1, ramp_z(y1) + z_top_off - thick),
                        (y1, ramp_z(y1) + z_top_off), (y0, ramp_z(y0) + z_top_off)]
                parts.append(yz_prism(ring, x0, x1))
    return parts


def landscape_parts():
    """The landscape as builder parts, {group: [part]} -- replaces the villa
    builders' terrain slab and surfaces (glass, doors and water still come
    from OPENINGS and pool_parts()):
      terrain  -300 up to the underside of the finishes, everywhere inside the
               plot except the house (the basement is under it) and the pool;
               under the forecourt a wedge that follows the ramp;
      paving / deck / lawn / gravel / drive / path   FINISH_T thick on top;
      planting the beds, and hedges HEDGE_H high along the garden boundary."""
    from shapely.geometry import box as _b
    from shapely.ops import unary_union
    S = ground_surfaces()
    T, W, D = BOUNDARY_T, PLOT_W, PLOT_D
    house = outline("GF")
    shell = S["poolzone"]
    fore = _b(0.0, GF_Y1, W, D)
    base = _b(0.0, 0.0, W, D).difference(house).difference(shell).difference(fore)
    top = GF - FINISH_T
    out = {"terrain": [poly_prism(base, -300.0, top)]}
    # the forecourt's terrain, a 400-deep wedge under the finishes
    out["terrain"] += _forecourt_part(_b(0.0, GF_Y1, W, D), -FINISH_T, 400.0)
    groups = {"paving": ["terrace", "path"], "deck": ["deck"], "lawn": ["lawn"],
              "planting": ["beds"], "gravel": ["mulch"], "drive": ["drive"]}
    for grp, keys in groups.items():
        g = unary_union([S[k] for k in keys])
        garden_part = g.difference(fore)
        fore_part = g.intersection(fore)
        lst = out.setdefault(grp, [])
        if garden_part.area > 1.0:
            lst.append(poly_prism(garden_part, top, GF))
        if fore_part.area > 1.0:
            lst += _forecourt_part(fore_part, 0.0, FINISH_T)
    # hedges on the garden beds (not the forecourt planters)
    hedge = S["beds"].difference(fore).buffer(-150.0, join_style=2)
    if hedge.area > 1.0:
        out["planting"].append(poly_prism(hedge, GF, GF + HEDGE_H))
    return out


# ================================================================== POOL
def pool_floor_at(y):
    pts = sorted(POOL_FLOOR)
    if y <= pts[0][0]:
        return pts[0][1]
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        if ya <= y <= yb:
            return za if yb - ya < 1e-9 else za + (zb - za) * (y - ya) / (yb - ya)
    return pts[-1][1]


def pool_section(top):
    return sorted(POOL_FLOOR, reverse=True) + [(POOL_Y0, top), (POOL_Y1, top)]


def pool_volume():
    pts = sorted(POOL_FLOOR)
    a = sum((yb - ya) * ((POOL_TW - za) + (POOL_TW - zb)) / 2
            for (ya, za), (yb, zb) in zip(pts, pts[1:]))
    lx0, ly0, lx1, ly1, lz = POOL_LEDGE
    ledge = (lx1 - lx0) * (ly1 - ly0) * (lz - POOL_SHALLOW_FL) / 1e9
    return a * (POOL_X1 - POOL_X0) / 1e9 - ledge


def pool_parts():
    """(shell, cuts, water) for both 3D builders: the concrete tank with its
    coping flush with the deck, the water on the floor PROFILE, and the sun
    ledge -- the tank is left solid up to the ledge's top across the house
    end (the cut stops there), the water runs over it."""
    c = POOL_COPING
    lx0, ly0, lx1, ly1, lz = POOL_LEDGE
    shell = [(POOL_X0 - c, POOL_Y0 - c, POOL_FL - 400.0,
              POOL_X1 + c, POOL_Y1 + c, GF)]

    def body(top):
        # the swimming area: along the floor from the ledge to the far wall
        return ([(ly0, pool_floor_at(ly0))]
                + [(y, z) for y, z in sorted(POOL_FLOOR, reverse=True) if y < ly0]
                + [(POOL_Y0, top), (ly0, top)])

    cuts = [yz_prism(body(GF + 100.0), POOL_X0, POOL_X1),
            (lx0, ly0, lz, lx1, ly1, GF + 100.0)]
    water = [yz_prism(body(POOL_TW), POOL_X0, POOL_X1),
             (lx0, ly0, lz, lx1, ly1, POOL_TW)]
    return shell, cuts, water


def grate():
    return []


def gates():
    return [("VEHICLE GATE", VEHICLE_GATE[0], VEHICLE_GATE[1], None),
            ("PEDESTRIAN GATE", PED_GATE[0], PED_GATE[1], GATE_HEAD)]


# ============================================================ OUTSIDE STEPS
STEP_RISE_MAX, STEP_GOING, LANDING = 180.0, 300.0, 1200.0


def _place(r, a0, a1, d0, d1, z0, z1):
    q0, q1 = sorted((r["face"] + r["sign"] * d0, r["face"] + r["sign"] * d1))
    if r["axis"] == "h":
        return (a0, q0, z0, a1, q1, z1)
    return (q0, a0, z0, q1, a1, z1)


def stairs_out():
    """Landing + flight at every external door above its ground. The whole
    site is level with the ground floor at the house (the forecourt ramp
    starts 1.3 m out), so every threshold is level and this is empty -- it
    is kept, derived, so moving a level brings the steps back."""
    import math as _m
    from shapely.geometry import Point
    recs = []
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if fl != "GF" or kind not in (DOOR, SLIDE) or rb is not None:
            continue
        out_gf = outline(fl)
        FLV = LEVEL[fl]
        w0, w1 = min(t0, t1), max(t0, t1)
        s0, s1 = min(a, b) - 300.0, max(a, b) + 300.0
        mid = (s0 + s1) / 2
        probe = Point(mid, w1 + 10) if axis == "h" else Point(w1 + 10, mid)
        sign = -1.0 if out_gf.contains(probe) else 1.0
        face = w1 if sign > 0 else w0
        ground = ground_at(face + sign * LANDING if axis == "h" else mid)
        if FLV - ground <= 1e-6:
            continue
        n = max(1, _m.ceil((FLV - ground) / STEP_RISE_MAX))
        rise = (FLV - ground) / n
        r = {"door": o, "axis": axis, "face": face, "sign": sign, "s0": s0,
             "s1": s1, "level": FLV, "ground": ground, "straight": True, "flights": []}
        r["landing"] = _place(r, s0, s1, 0.0, LANDING, ground, FLV)
        for j in range(1, n):
            r["flights"].append(_place(r, s0, s1, LANDING + (j - 1) * STEP_GOING,
                                       LANDING + j * STEP_GOING, ground, FLV - j * rise))
        recs.append(r)
    return recs


def external_steps():
    boxes = []
    for r in stairs_out():
        boxes.append(r["landing"])
        boxes += r["flights"]
    return boxes


# ================================================================ STAIRS
def _flight(name, along, dir_, t_foot, c0, c1, z_foot, n, rise, going, open_,
            inside, stair, solid_to=None, waist=None):
    return {"name": name, "along": along, "dir": dir_, "t_foot": t_foot,
            "c0": c0, "c1": c1, "z_foot": z_foot, "n": n, "rise": rise,
            "going": going, "open": tuple(open_), "inside": inside,
            "stair": stair, "solid_to": solid_to, "waist": waist}


def _stair_levels(s):
    return LEVEL[s["from"]], LEVEL[s["to"]]


def stair_split(s=None):
    """Risers per flight of a stair (the feature stair by default)."""
    s = s or STAIRS[0]
    n = int(s["risers"])
    if s["type"] != "dogleg":
        return [n]
    first = -(-n // 2)
    return [first, n - first]


def _landings():
    """[(stair, (x0, y0, x1, y1), level)] -- every dog-leg's half-landing."""
    out = []
    for s in STAIRS:
        if s["type"] != "dogleg":
            continue
        z0, z1 = _stair_levels(s)
        rise = (z1 - z0) / s["risers"]
        n1 = stair_split(s)[0]
        sx0, sy0, sx1, sy1 = s["rect"]
        y_hl = s["foot"] + (n1 - 1) * s["going"]
        out.append((s, (sx0, y_hl, sx1, sy1), z0 + n1 * rise))
    return out


def stair_landing():
    """The half-landing ((x0, y0, x1, y1), level) -- the service stair's
    (the only one); None if there is none."""
    L = _landings()
    return (L[0][1], L[0][2]) if L else None


def flights():
    """Every flight of steps, as dicts (villa_design's language):
      along 'y'/'x', dir +1/-1 the way it ASCENDS, t_foot the first riser,
      c0..c1 across, z_foot the floor at its foot, n risers of `rise`, treads
      of `going`, open the declared open sides, inside True for the house's
      stairs; and, for the multi-stair checks, `stair` (its name),
      `solid_to` (the level a solid flight is built up from; None when it
      floats) and `waist` (a floating tread's thickness)."""
    out = []
    for s in STAIRS:
        z0, z1 = _stair_levels(s)
        rise = (z1 - z0) / s["risers"]
        sx0, sy0, sx1, sy1 = s["rect"]
        solid_to = LEVEL[s["from"]] if s["solid"] else None
        if s["type"] == "straight":
            out.append(_flight(s["name"], "y", s["dir"], s["foot"], sx0, sx1, z0,
                               s["risers"], rise, s["going"], s["open"], True,
                               s["name"], solid_to, s.get("waist")))
            continue
        n1, n2 = stair_split(s)
        mid = s["split"]
        (_lx0, y_hl, _lx1, _ly1), z_hl = next(
            (b, z) for st, b, z in _landings() if st is s)
        # flight 1 rises north on the west half, from the floor landing at
        # the south end; its east side is flight 2's solid mass. Flight 2
        # rises south on the east half from the half-landing; its west side
        # stands over flight 1 (open, guarded).
        out.append(_flight(f"{s['name']} flight 1", "y", +1, s["foot"], sx0, mid,
                           z0, n1, rise, s["going"], (), True, s["name"], solid_to))
        out.append(_flight(f"{s['name']} flight 2", "y", -1, y_hl, mid, sx1,
                           z_hl, n2, rise, s["going"], ("c0",), True, s["name"],
                           solid_to))
    return out


def flight_treads(f):
    out = []
    for k in range(1, f["n"]):
        a = f["t_foot"] + f["dir"] * (k - 1) * f["going"]
        b = f["t_foot"] + f["dir"] * k * f["going"]
        out.append((min(a, b), max(a, b), f["z_foot"] + k * f["rise"]))
    return out


def flight_run(f):
    a = f["t_foot"]
    b = a + f["dir"] * (f["n"] - 1) * f["going"]
    return min(a, b), max(a, b)


def pitch_at(f, t):
    return (f["z_foot"] + f["rise"]
            + f["dir"] * (t - f["t_foot"]) * f["rise"] / f["going"])


def flight_plan(f, t0, t1, c0=None, c1=None):
    c0 = f["c0"] if c0 is None else c0
    c1 = f["c1"] if c1 is None else c1
    if f["along"] == "y":
        return (min(c0, c1), t0, max(c0, c1), t1)
    return (t0, min(c0, c1), t1, max(c0, c1))


def stair_surfaces():
    """Every house stair's walking surfaces [((x0, y0, x1, y1), level, rise)]:
    each tread and each half-landing (rise 0)."""
    out = []
    for f in flights():
        if f["inside"]:
            out += [(flight_plan(f, t0, t1), z, f["rise"])
                    for t0, t1, z in flight_treads(f)]
    for _s, b, z in _landings():
        out.append((b, z, 0.0))
    return out


def stair_columns():
    """The stairs' solid, as columns [((x0, y0, x1, y1), z0, z1)]: a solid
    stair's treads and half-landing from its base floor up, a floating
    tread its own waist -- what villa_dbc stands on and falls to."""
    out = []
    by_stair = {s["name"]: s for s in STAIRS}
    for f in flights():
        s = by_stair[f["stair"]]
        for t0, t1, z in flight_treads(f):
            b = flight_plan(f, t0, t1)
            out.append((b, LEVEL[s["from"]] if s["solid"] else z - (s.get("waist") or 90.0), z))
    for s, b, z in _landings():
        out.append((b, LEVEL[s["from"]] if s["solid"] else z - 150.0, z))
    for s in STAIRS:
        if s.get("fill"):
            out.append((tuple(s["fill"]), LEVEL[s["from"]], LEVEL[s["to"]] - SLAB))
    return out


def stair_parts():
    """The house stairs as builder boxes -- glTF group 'stair', AutoCAD
    A-STRS-3D: the service stair solid from the basement floor, the feature
    stair's treads floating (a 90 waist, cantilevered from the wall), and
    at each arrival the nosing the last riser rises to, 150 into the slab."""
    out = [(b[0], b[1], z0, b[2], b[3], z1) for b, z0, z1 in stair_columns()]
    for f in flights():
        top = f["z_foot"] + f["n"] * f["rise"]
        if not any(abs(top - LEVEL[fl]) < 1.0 for fl in ("GF", "FF")):
            continue                               # arrives at a half-landing
        t_top = f["t_foot"] + f["dir"] * (f["n"] - 1) * f["going"]
        t_out = t_top + f["dir"] * 150.0
        x0, y0, x1, y1 = flight_plan(f, min(t_top, t_out), max(t_top, t_out))
        out.append((x0, y0, top - f["rise"], x1, y1, top))
    return out


def _guard_face(f, side):
    """Across position of the glass on a flight's side: centred on the line
    between two flights of one stair, else outside the flight."""
    c = f[side]
    # by NAME: flights() builds new dicts on every call, so `g is not f` was
    # always true and a lone flight's glass was centred on its own edge
    shared = any(g["name"] != f["name"] and g["stair"] == f["stair"] and
                 (abs(g["c0"] - c) < 1.0 or abs(g["c1"] - c) < 1.0) for g in flights())
    if shared:
        return c - GUARD_T / 2, c + GUARD_T / 2
    return (c - GUARD_T, c) if side == "c0" else (c, c + GUARD_T)


def handrails():
    """Every handrail (K-HR-01): one on each declared open side of every
    flight, fixed to its glass, top HANDRAIL_H over the nosing line."""
    fl = flights()
    out = []
    for f in fl:
        t0, t1 = flight_run(f)
        for side in f["open"]:
            into = 1.0 if side == "c0" else -1.0
            g0, g1 = _guard_face(f, side)
            face = g1 if into > 0 else g0
            a = face + into * RAIL_GAP
            c0, c1 = sorted((a, a + into * RAIL_W))
            out.append({"f": f, "along": f["along"], "t0": t0, "t1": t1, "c0": c0,
                        "c1": c1, "top0": pitch_at(f, t0) + HANDRAIL_H,
                        "top1": pitch_at(f, t1) + HANDRAIL_H, "posts": []})
    return out


def rail_parts():
    out = []
    for h in handrails():
        t0, t1 = h["t0"], h["t1"]
        ring = [(t0, h["top0"] - RAIL_T), (t1, h["top1"] - RAIL_T),
                (t1, h["top1"]), (t0, h["top0"])]
        out.append(yz_prism(ring, h["c0"], h["c1"]) if h["along"] == "y"
                   else xz_prism(ring, h["c0"], h["c1"]))
        out += [tuple(p) for p in h["posts"]]
    return out


# ================================================================ GUARDS
def guards_labelled():
    """Every guard as (kind, (x0, y0, x1, y1, z0, z1)) -- GUARD_T glass, GUARD_H
    over the floor it protects (K-GRD-01/-02, K-SGR-01/-02):
      'stair well'   on each floor along a stair void's edge where a flight
                     does not arrive: the FF landing over the hall (the
                     feature stair arrives at its west end) and the GF
                     landing over the service stair's lower flight;
      'stair flight' stepped panels over every tread of an open flight side;
      'balcony'      the master's balcony, three open edges;
      'declared'     GUARDS_EXTRA (the pool-garden fences)."""
    T, H = GUARD_T, GUARD_H
    out = []
    fl_all = flights()
    for vname, vx0, vy0, vx1, vy1, fls in VOIDS:
        for fl in fls:
            z = LEVEL[fl]
            # the edge the floor lies beyond: the void's south edge on both
            # (the landings are south of both wells)
            arrive = [f for f in fl_all
                      if abs(f["z_foot"] + f["n"] * f["rise"] - z) < 1.0
                      and abs(flight_run(f)[0 if f["dir"] < 0 else 1] - vy0) < 1.0]
            spans = sorted((f["c0"], f["c1"]) for f in arrive)
            x = vx0
            for a, b in spans + [(vx1, vx1)]:
                if a - x > 10.0:
                    out.append(("stair well", (x, vy0 - T, a, vy0, z, z + H)))
                x = max(x, b)
    # the hall void's north edge (the outer wall side): glass at first-floor level
    for vname, vx0, vy0, vx1, vy1, fls in VOIDS:
        for fl in fls:
            out.append(("void edge", (vx0, vy1 - T, vx1, vy1, LEVEL[fl], LEVEL[fl] + H)))
            out.append(("void edge", (vx0 - T, vy0, vx0, vy1, LEVEL[fl], LEVEL[fl] + H)))
            out.append(("void edge", (vx1, vy0, vx1 + T, vy1, LEVEL[fl], LEVEL[fl] + H)))
    for f in fl_all:
        for side in f["open"]:
            g0, g1 = _guard_face(f, side)
            for t0, t1, z in flight_treads(f):
                x0, y0, x1, y1 = flight_plan(f, t0, t1, g0, g1)
                out.append(("stair flight", (x0, y0, x1, y1, z, z + f["rise"] + H)))
    if BALCONY:
        bx0, by0, bx1, by1 = BALCONY
        out += [("balcony", (bx0, by0, bx1, by0 + T, FF, FF + H)),
                ("balcony", (bx0, by0, bx0 + T, by1, FF, FF + H)),
                ("balcony", (bx1 - T, by0, bx1, by1, FF, FF + H))]
    out += [("declared", tuple(g)) for g in GUARDS_EXTRA]
    return out


def guards():
    return [b for _, b in guards_labelled()]


def __getattr__(name):
    if name == "GUARDS":
        return guards()
    raise AttributeError(name)


# ============================================================ STREET ACCESS
def _segments(lines):
    from shapely.ops import linemerge
    if lines.is_empty:
        return []
    g = linemerge(lines) if lines.geom_type != "LineString" else lines
    out = []
    for ln in getattr(g, "geoms", [g]):
        cs = list(ln.coords)
        out += list(zip(cs, cs[1:]))
    return out


def street_access(width=None):
    """Can every external door be reached on foot from a gate by a path at
    least `width` wide? [(door, target box, ok)]; doors onto the pool garden
    are skipped (it is entered from the house)."""
    from shapely.geometry import Point, box as _b
    from shapely.ops import unary_union
    w = PATH_MIN_W if width is None else width
    T = BOUNDARY_T
    site = _b(T, T, PLOT_W - T, PLOT_D - T)
    plat = garden_platform()
    blocked = unary_union([outline("GF"), plat]
                          + [_b(s[0], s[1], s[3], s[4]) for s in STONE_FREE])
    walk = site.difference(blocked).buffer(-w / 2).buffer(w / 2)
    parts = [p for p in getattr(walk, "geoms", [walk]) if not p.is_empty]
    zones = [_b(g0, PLOT_D - T - 1.0, g1, PLOT_D - T)
             for _n, g0, g1, _h in gates() if g1 - g0 >= w]
    reached = unary_union([p for p in parts if any(p.intersects(z) for z in zones)]
                          or [_b(0, 0, 0, 0)])
    out = []
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if fl != "GF" or kind not in (DOOR, SLIDE) or rb is not None:
            continue
        w0, w1 = min(t0, t1), max(t0, t1)
        mid = (a + b) / 2
        probe = Point(mid, w1 + 10) if axis == "h" else Point(w1 + 10, mid)
        sign = -1.0 if outline(fl).contains(probe) else 1.0
        face = w1 if sign > 0 else w0
        rr = {"axis": axis, "face": face, "sign": sign}
        tb = _place(rr, min(a, b), max(a, b), 0.0, 50.0, 0.0, 0.0)
        box_ = (tb[0], tb[1], tb[3], tb[4])
        if plat.buffer(60).contains(_b(*box_)):
            continue                              # onto the pool garden
        got = reached.intersection(_b(*box_)).area
        out.append((o, box_, got >= 0.9 * 50.0 * min(w, abs(b - a))))
    return out


# ================================================================ PROBES
def probes():
    """Points the 3D fabric must be SOLID or VOID at: (name, x, y, z, expect,
    r). Shared by the glTF and AutoCAD verifiers."""
    from shapely.geometry import box as _box
    E = envelope()
    out = []

    def centre(g):
        if hasattr(g, "geoms"):
            g = max(g.geoms, key=lambda p: p.area)
        c = g.representative_point()
        return c.x, c.y

    stairs = [_box(*s["rect"]).buffer(700, join_style=2) for s in STAIRS]
    wells = {fl: [_box(v[1], v[2], v[3], v[4]) for v in VOIDS if fl in v[5]]
             for fl in ("GF", "FF")}
    upper = {"B1": "GF", "GF": "FF", "FF": None}
    for r in ROOMS:
        fl = r[6]
        base = LEVEL[fl]
        g = net_poly(r)
        for z in stairs:
            if g.intersects(z):
                rest = g.difference(z)
                g = rest if rest.area > 1e6 else g
        x, y = centre(g)
        out.append((f"{fl} {r[0]}", x, y, base + 1500, "void", 250.0))
        pt = _box(x - 1, y - 1, x + 1, y + 1)
        up = upper[fl]
        if up is not None and not any(w.contains(pt) for w in wells.get(up, [])):
            if up == "FF" and not E["ff_slab"].contains(pt):
                pass
            else:
                out.append((f"slab over {fl} {r[0]}", x, y, LEVEL[up] - SLAB / 2,
                            "solid", 200.0))
        if fl == "FF":
            out.append((f"roof over {r[0]}", x, y, RF + SLAB / 2, "solid", 200.0))
        if fl == "B1":
            out.append((f"basement floor under {r[0]}", x, y, B1 - SLAB / 2,
                        "solid", 200.0))
    # the hall's double height: no cap at FF, open at FF+1500, roofed
    v = next(v for v in VOIDS if v[0] == "STAIR VOID")
    cx, cy = (v[1] + 16000.0) / 2 + 3000.0, (v[2] + v[4]) / 2
    out.append(("hall void: no cap at FF", cx, cy, FF - SLAB / 2, "void", 200.0))
    out.append(("hall void at FF+1500", cx, cy, FF + 1500, "void", 250.0))
    out.append(("roof over the hall void", cx, cy, RF + SLAB / 2, "solid", 200.0))

    # every flight: a tread solid, clear over it; the floating one open under
    for f in flights():
        tr = flight_treads(f)
        t0, t1, z = tr[len(tr) // 2]
        x0, y0, x1, y1 = flight_plan(f, t0, t1)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out.append((f"{f['name']}: tread", cx, cy, z - 45, "solid", 30.0))
        out.append((f"{f['name']}: clear over the tread", cx, cy, z + 1000, "void", 200.0))
        if f["solid_to"] is None:
            out.append((f"{f['name']}: floats (open under the tread)", cx, cy,
                        z - (f.get("waist") or 90.0) - 300.0, "void", 120.0))
    # the first-floor roof frame over the garden windows (OVERHANGS)
    out.append(("roof frame overhang", 14800.0, 8400.0, RF + SLAB / 2, "solid", 150.0))
    # stone: the east flank skin (between windows) and the BBQ wall
    out.append(("stone skin, east flank", HX1 - STONE_SKIN / 2, 32000.0, GF + 1200,
                "solid", 15.0))
    out.append(("render behind the stone", HX1 - STONE_SKIN - 150.0, 32000.0, GF + 1200,
                "solid", 60.0))
    out.append(("BBQ stone wall", 3150.0, 11500.0, GF + 1500, "solid", 80.0))
    # the pool: floor profile, the ledge, water over them
    ax = (POOL_X0 + POOL_X1) / 2
    for name, y in (("pool floor, deep end", POOL_Y0 + 500.0),
                    ("pool floor, on the slope", 8750.0)):
        z = pool_floor_at(y)
        out.append((name, ax, y, z - 120, "solid", 80.0))
        out.append((f"{name}: water over it", ax, y, z + 120, "void", 80.0))
    lx0, ly0, lx1, ly1, lz = POOL_LEDGE
    out.append(("sun ledge", ax, (ly0 + ly1) / 2, lz - 100, "solid", 60.0))
    out.append(("sun ledge: water over it", ax, (ly0 + ly1) / 2, lz + 60, "void", 30.0))
    # one guard of each kind, glass where the data says
    seen = set()
    for kind, (gx0, gy0, gx1, gy1, gz0, gz1) in guards_labelled():
        if kind in seen:
            continue
        seen.add(kind)
        cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
        out.append((f"guard ({kind})", cx, cy, gz1 - 100, "solid", 10.0))
        out.append((f"guard ({kind}): nothing above it", cx, cy, gz1 + 100, "void", 10.0))
    seen = set()
    for h in handrails():
        if h["f"]["stair"] in seen:
            continue
        seen.add(h["f"]["stair"])
        tm = (h["t0"] + h["t1"]) / 2
        zm = (h["top0"] + h["top1"]) / 2 - RAIL_T / 2
        cm = (h["c0"] + h["c1"]) / 2
        x, y = (cm, tm) if h["along"] == "y" else (tm, cm)
        out.append((f"handrail ({h['f']['stair']})", x, y, zm, "solid", 10.0))
        out.append((f"handrail ({h['f']['stair']}): clear over it", x, y, zm + 150,
                    "void", 10.0))
    return out


# ============================================================== VALIDATOR
def validate():
    issues = []

    # --- 1. every opening PENETRATES its wall; door and slide widths ------
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        depth = abs(t1 - t0)
        need = WALL if rb is None else PART
        if depth < need - 1e-6:
            issues.append(f"[FATAL] {kind} {ra}->{rb or 'outside'}: void depth "
                          f"{depth:.0f} < wall {need:.0f}")
        if kind == DOOR and not (700 <= abs(b - a) <= 1800):
            issues.append(f"[MAJOR] door {ra}->{rb or 'outside'} width {abs(b - a):.0f} "
                          f"outside 700-1800")
        if kind == SLIDE and not (1800 <= abs(b - a) <= 7200):
            issues.append(f"[MAJOR] sliding door {ra}->{rb or 'outside'} width "
                          f"{abs(b - a):.0f} outside 1800-7200")

    # --- 1b. a door lands in the room it names, not a nested one ----------
    byname = {(r[6], r[0]): r for r in ROOMS}
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        for side in (ra, rb):
            host = byname.get((fl, side))
            if host is None:
                continue
            thr = threshold(rect(host), axis, t0, t1, a, b)
            if thr is None:
                continue
            ta = (thr[2] - thr[0]) * (thr[3] - thr[1])
            for q in rooms_on(fl):
                if q[0] in (ra, rb) or not contains(rect(host), rect(q)):
                    continue
                qx0, qy0, qx1, qy1 = rect(q)
                ov = (max(0.0, min(thr[2], qx1) - max(thr[0], qx0))
                      * max(0.0, min(thr[3], qy1) - max(thr[1], qy0)))
                if ov > 0.25 * ta:
                    issues.append(f"[FATAL] {kind} {ra}->{rb or 'outside'} lands "
                                  f"{100 * ov / ta:.0f}% inside {q[0]}, nested in {side}")

    # --- 1c. an opening sits ON a wall ------------------------------------
    for fl in floors():
        ex, pt_, _in = fabric(fl)
        skin = ex.union(pt_)
        for o in OPENINGS:
            if o[0] != fl:
                continue
            r = void_rect(o)
            frac = r.intersection(skin).area / r.area if r.area else 0.0
            if frac < 0.80:
                issues.append(f"[FATAL] {o[0]} {o[1]} {o[7]}->{o[8] or 'outside'} sits "
                              f"{100 * frac:.0f}% on a wall -- it cuts thin air")

    # --- 1d. an internal opening joins rooms that SHARE a wall ------------
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if rb is None or kind == WIN:
            continue
        A_, B_ = byname.get((fl, ra)), byname.get((fl, rb))
        if A_ is None or B_ is None:
            issues.append(f"[FATAL] {kind} {ra}->{rb}: room not on floor {fl}")
            continue
        if contains(rect(A_), rect(B_)) or contains(rect(B_), rect(A_)):
            continue
        i = 1 if axis == "v" else 2
        gap = max(A_[i] - B_[i + 2], B_[i] - A_[i + 2])
        if gap < -1 or gap > PART + 1:
            issues.append(f"[FATAL] {kind} {ra}->{rb}: the rooms are {gap:.0f} mm apart "
                          f"-- they do not share a wall")

    # --- 2/3. reachability; no bedroom reached through another ------------
    for fl in floors():
        names = {r[0] for r in rooms_on(fl)}
        adj, ext = door_graph(fl)
        start = ENTRY_ROOM.get(fl) or (sorted(ext)[0] if ext else None)
        if start is None:
            issues.append(f"[FATAL] {fl} has no entry room and no external door")
            continue
        seen, stack = {start}, [start]
        while stack:
            for nxt in adj.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        for n in sorted(names - seen):
            issues.append(f"[FATAL] {fl} {n} is UNREACHABLE from {start}")
        beds = {r[0] for r in rooms_on(fl)
                if ROLE.get(r[0]) in ("bedroom", "master_bedroom")}
        for bed in sorted(beds):
            others = beds - {bed}
            sub = {n: {m for m in adj[n] if m not in others} for n in adj}
            seen2, st2 = {start}, [start]
            while st2:
                for nxt in sub.get(st2.pop(), ()):
                    if nxt not in seen2:
                        seen2.add(nxt)
                        st2.append(nxt)
            if bed not in seen2:
                issues.append(f"[FATAL] {bed} is an INNER ROOM")

    # --- 4. every bedroom has its bathroom --------------------------------
    wet = {r[0] for r in ROOMS if r[5] == WET}
    for bed, ens in ENSUITE_OF.items():
        if ens not in wet:
            issues.append(f"[FATAL] {bed} has no bathroom")

    # --- 5. areas ---------------------------------------------------------
    for r in ROOMS:
        m = MIN_AREA.get(r[0])
        if m and net_area(r) < m - 1e-6:
            issues.append(f"[MAJOR] {r[0]} {net_area(r):.1f} m2 net < minimum {m:.1f} m2")

    # --- 6. overlaps; voids through non-circulation rooms -----------------
    for fl in floors():
        rs = rooms_on(fl)
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                ra_, rb_ = rect(a), rect(b)
                if overlap(ra_, rb_) and not (contains(ra_, rb_) or contains(rb_, ra_)):
                    issues.append(f"[MAJOR] {fl} {a[0]} partially overlaps {b[0]}")
            for vname, vx0, vy0, vx1, vy1, vfl in VOIDS:
                if a[5] != CIRC and fl in vfl and overlap(rect(a), (vx0, vy0, vx1, vy1)):
                    issues.append(f"[FATAL] {fl} {vname} cuts through {a[0]}")

    # --- 6b. no unallocated space inside the envelope ---------------------
    from shapely.ops import unary_union as _uu
    for fl in floors():
        _e, _p, _in = fabric(fl)
        spare = _in.difference(_uu([net_poly(r) for r in rooms_on(fl)]))
        fat = spare.buffer(-(PART / 2 + 5), join_style=2)
        for g in (fat.geoms if hasattr(fat, "geoms") else ([fat] if not fat.is_empty else [])):
            b = g.bounds
            issues.append(f"[MAJOR] {fl} {g.area / 1e6:.1f} m2 at ({b[0]:.0f},{b[1]:.0f})-"
                          f"({b[2]:.0f},{b[3]:.0f}) belongs to no room")

    # --- 7. pool: a skimmer pool on a real profile, a terrace, the ledge --
    if TERRACE < 1200:
        issues.append(f"[FATAL] terrace between the glass and the water {TERRACE:.0f} < 1200")
    prof = sorted(POOL_FLOOR)
    if abs(prof[0][0] - POOL_Y0) > 1 or abs(prof[-1][0] - POOL_Y1) > 1:
        issues.append("[FATAL] POOL_FLOOR does not run wall to wall")
    if abs(min(z for _, z in prof) - POOL_FL) > 1 or \
            abs(max(z for _, z in prof) - POOL_SHALLOW_FL) > 1:
        issues.append("[FATAL] POOL_FL / POOL_SHALLOW_FL are not the profile's extremes")
    if not (GF - 200 <= POOL_TW < GF):
        issues.append(f"[MAJOR] water at {POOL_TW:.0f}: a skimmer pool's water sits "
                      f"just below its coping (+{GF:.0f})")
    lx0, ly0, lx1, ly1, lz = POOL_LEDGE
    issues.append(f"[NOTE ] the sun ledge ({lx1 - lx0:.0f} x {ly1 - ly0:.0f}, "
                  f"{POOL_TW - lz:.0f} deep) is modelled as a bench; DBC K-POOL-03 "
                  f"reads the floor profile (BRIEF open question 2)")

    # --- 8. forecourt: a car stands clear of the street -------------------
    from shapely.geometry import box as _fb
    _house = outline("GF")
    _front = _house.intersection(_fb(PORCH_X0, 0, PORCH_X1, PLOT_D))
    _face = _front.bounds[3] if not _front.is_empty else PORCH_Y0
    fore = (PLOT_D - BOUNDARY_T) - _face
    if fore < 5500:
        issues.append(f"[FATAL] forecourt {fore:.0f} mm deep < 5500 (a DBC open bay)")
    if (PORCH_X1 - PORCH_X0) < 5500:
        issues.append(f"[FATAL] car porch {PORCH_X1 - PORCH_X0:.0f} wide: two cars need 5500")
    slope = 100.0 * (GF - STREET) / (RAMP_Y1 - RAMP_Y0)
    if slope > 4.0 + 1e-9:
        issues.append(f"[FATAL] forecourt ramp {slope:.1f}% > 4% (DBC K-PARK-02)")

    # --- 9. every stair fits its room, from its own risers ----------------
    for s in STAIRS:
        z0, z1 = _stair_levels(s)
        rise = (z1 - z0) / s["risers"]
        if not (100 <= rise <= 180):
            issues.append(f"[FATAL] {s['name']} riser {rise:.1f} outside 100-180")
        if s["going"] < 280:
            issues.append(f"[FATAL] {s['name']} tread {s['going']:.0f} < 280")
        sx0, sy0, sx1, sy1 = s["rect"]
        per = stair_split(s)
        run = (max(per) - 1) * s["going"] + (1100 + 1000 if s["type"] == "dogleg" else 0)
        if run > (sy1 - sy0) + 1e-6:
            issues.append(f"[FATAL] {s['name']}: {run:.0f} mm of flights and landings "
                          f"in {sy1 - sy0:.0f}")
    # headroom under the ground floor's roof over the feature stair (K-STR-11)
    f = next(f for f in flights() if f["stair"] == "feature stair")
    worst = min((FF - SLAB) - pitch_at(f, t) for t in range(int(FF_Y1 - WALL), int(f["t_foot"]) + 1, 50))
    if worst < 2300:
        issues.append(f"[FATAL] feature stair headroom {worst:.0f} < 2300 under the slab")

    # --- 10. circulation ---------------------------------------------------
    gia = sum(A(*rect(r)) for r in ROOMS if not any(
        contains(rect(p), rect(r)) and p is not r for p in ROOMS if p[6] == r[6]))
    corridor = sum(A(*rect(r)) for r in ROOMS if r[5] == CIRC and "CORRIDOR" in r[0])
    if gia and 100 * corridor / gia > 8:
        issues.append(f"[MAJOR] dedicated corridor {100 * corridor / gia:.1f}% of GIA > 8%")
    globals()["_CIRC_REPORT"] = (corridor, gia)
    issues += checks_brief()
    return issues


def projections():
    """Every horizontal projection that can shade an opening: SHADES (timber)
    and OVERHANGS (the building's own cantilever and roof frame)."""
    return [tuple(s) for s in SHADES] + [tuple(o) for o in OVERHANGS]


def checks_brief():
    """Checks 11-23: programme, routes, garden, daylight, climate, BUA,
    setbacks, the Dubai Building Code (20), gates (21), street access (22),
    height (23)."""
    from shapely.geometry import box as _b
    issues = []
    fls = floors()

    # --- 11. every room has a zone and a role ------------------------------
    for r in ROOMS:
        if r[0] not in ZONE:
            issues.append(f"[FATAL] {r[6]} {r[0]} has no ZONE")
        if r[0] not in ROLE:
            issues.append(f"[FATAL] {r[6]} {r[0]} has no ROLE")

    # --- 12. routes: who walks through what --------------------------------
    z = lambda n: ZONE.get(n)
    for fl in fls:
        adj, ext = door_graph(fl)
        entry = ENTRY_ROOM.get(fl)
        starts = {entry} if entry else set(ext)
        for r in rooms_on(fl):
            n, zn, role = r[0], z(r[0]), ROLE.get(r[0])
            if n in starts or zn is None:
                continue
            if zn == GUEST:
                ok = {CIRC_Z, GUEST}
            elif zn == FAMILY:
                ok = {CIRC_Z, FAMILY}
            elif zn == PRIVATE:
                ok = {CIRC_Z} if role in ("bedroom", "master_bedroom") else {CIRC_Z, PRIVATE}
            elif zn == SERVICE:
                ok = {CIRC_Z, SERVICE, FAMILY}
            else:
                continue
            got = reach(adj, starts | (ext if zn == SERVICE else set()),
                        lambda m, ok=ok: z(m) in ok)
            if n not in got:
                issues.append(f"[FATAL] {fl} {n} ({zn}) cannot be reached without "
                              f"passing through a room outside {sorted(ok)}")

    # --- 13. the brief, as roles -------------------------------------------
    for role, count, amin in REQUIRED:
        rs = [r for r in ROOMS if ROLE.get(r[0]) == role]
        if len(rs) < count:
            issues.append(f"[MAJOR] programme: {len(rs)} x {role}, the listing needs {count}")
        for r in rs:
            if net_area(r) < amin - 1e-6:
                issues.append(f"[MAJOR] {r[0]} ({role}) {net_area(r):.1f} m2 net < {amin:.1f}")

    # --- 14. the house opens to its garden ---------------------------------
    if not any(o[0] == "GF" and o[1] != WIN and o[8] is None
               and z(o[7]) == FAMILY and facing(o) == "S" for o in OPENINGS):
        issues.append("[FATAL] no door from a family room to the garden")

    # --- 15. daylight: every HABITABLE room has an external window ----------
    lit = {(o[0], o[7]) for o in OPENINGS if o[8] is None and o[1] in (WIN, SLIDE)}
    for r in ROOMS:
        if r[5] == HAB and (r[6], r[0]) not in lit:
            issues.append(f"[MAJOR] {r[6]} {r[0]} is habitable with no external window")
        if r[6] in BELOW_GRADE_FLOORS and r[5] == HAB:
            issues.append(f"[FATAL] {r[0]} is a habitable room below grade with no "
                          f"lightwell (DBC K-BSMT-03)")

    # --- 16. climate: south openings under a projection; east/west punched --
    fin_boxes = fins()
    for o in OPENINGS:
        if o[8] is not None or o[0] in BELOW_GRADE_FLOORS:
            continue
        face = facing(o)
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        lo, hi = opening_z(o)
        a0, a1 = min(a, b), max(a, b)
        if face == "S":
            need = 0.6 * (hi - lo)
            wy = min(t0, t1)
            ok = any(s[0] <= a0 + 100 and s[2] >= a1 - 100 and s[1] <= wy - need + 1
                     and s[3] >= wy - 50 and hi - 50 <= s[4] <= hi + 800
                     for s in projections())
            if not ok:
                issues.append(f"[MAJOR] {fl} {kind} {ra} faces south with no projection "
                              f">= {need:.0f} mm over it")
        elif face in ("E", "W"):
            if kind == WIN and (a1 - a0) <= DEEP_REVEAL_MAX_W and WALL >= 400:
                continue
            if (fl, ra) in SCREENED:
                continue
            wx = min(t0, t1) if face == "W" else max(t0, t1)
            cover = [f for f in fin_boxes
                     if (f[2] <= wx + 20 and f[0] >= wx - 1500 if face == "W"
                         else f[0] >= wx - 20 and f[2] <= wx + 1500)
                     and f[4] <= lo and f[5] >= hi]
            if not cover:
                issues.append(f"[MAJOR] {fl} {kind} {ra} faces "
                              f"{'west' if face == 'W' else 'east'} with no fins")

    # --- 17. BUA against the listing ---------------------------------------
    bua = gross_area()
    if abs(bua - BRIEF_GFA) / BRIEF_GFA > 0.10:
        issues.append(f"[MAJOR] BUA {bua:.1f} m2 is more than 10% from the listing's "
                      f"{BRIEF_GFA:.0f} m2")

    # --- 19. setbacks (the basement may occupy them, K-SB-05) ---------------
    inner = _b(SB_SIDE, SB_REAR, PLOT_W - SB_SIDE, PLOT_D - SB_FRONT)
    for fl in fls:
        if fl in BELOW_GRADE_FLOORS:
            if not _b(0, 0, PLOT_W, PLOT_D).contains(outline(fl)):
                issues.append(f"[FATAL] the basement leaves the plot (DBC K-BSMT-02)")
            continue
        spill = outline(fl).difference(inner)
        if spill.area > 1e4:
            b_ = spill.bounds
            issues.append(f"[MAJOR] {fl} crosses the setback line by {spill.area / 1e6:.1f} m2 "
                          f"around ({b_[0]:.0f},{b_[1]:.0f})-({b_[2]:.0f},{b_[3]:.0f})")
    for i, p in enumerate(projections()):
        if p[1] < SB_REAR - 1e-6 or p[0] < SB_SIDE - 1e-6 or p[2] > PLOT_W - SB_SIDE + 1e-6:
            issues.append(f"[MAJOR] projection {i} reaches into a side/rear setback")

    # --- 21. gates ----------------------------------------------------------
    T = BOUNDARY_T
    gs = gates()
    for i, (gn, g0, g1, head) in enumerate(gs):
        if not (T <= g0 < g1 <= PLOT_W - T):
            issues.append(f"[FATAL] {gn} {g0:.0f}-{g1:.0f} is not in the street wall")
        if g1 - g0 < (3000 if head is None else 1000):
            issues.append(f"[MAJOR] {gn} is {g1 - g0:.0f} wide")
        for gn2, h0, h1, _h in gs[i + 1:]:
            if min(g1, h1) - max(g0, h0) > -300:
                issues.append(f"[FATAL] {gn} and {gn2} overlap or leave < 300")
        if head is None and not (PORCH_X0 <= g0 and g1 <= PORCH_X1):
            issues.append(f"[MAJOR] {gn} does not open onto the car porch")

    # --- 22. every street-side door reachable from a gate ------------------
    for o, tb, ok in street_access():
        if not ok:
            issues.append(f"[FATAL] {o[0]} {o[1]} {o[7]} cannot be reached from a gate "
                          f"by a {PATH_MIN_W:.0f} path")

    # --- 23. height (DBC K-HGT-01, from the road at the main access) --------
    top = max(RF + SLAB + PARAPET, max(s[5] for s in SHADES))
    if top - STREET > 16000:
        issues.append(f"[FATAL] building {top - STREET:.0f} mm high > 16 m (K-HGT-01)")

    # --- 20. the Dubai Building Code, from page-cited rules (villa_dbc.py) --
    try:
        import villa_dbc
        issues += villa_dbc.checks()
    except Exception as exc:
        issues.append(f"[MAJOR] Dubai Building Code checks did not run: {exc}")
    return issues


def gross_area():
    """BUA as the listing quotes it: every built storey's outline, the
    basement included."""
    return sum(outline(fl).area / 1e6 for fl in floors())


def dbc_gfa():
    """GFA the DBC way (K-COV-01 note): basements excluded."""
    return sum(outline(fl).area / 1e6 for fl in floors() if fl not in BELOW_GRADE_FLOORS)


def report():
    print("=" * 72)
    print(PROJECT_TITLE)
    for fl in floors():
        rs = rooms_on(fl)
        tot = sum(net_area(r) for r in rs)
        print(f"{fl}: {len(rs):2d} rooms   net {tot:6.1f} m2   gross "
              f"{outline(fl).area / 1e6:6.1f} m2")
    bua = gross_area()
    print(f"BUA {bua:.1f} m2 = {bua * 10.7639:.0f} sq ft   (listing {BRIEF_SQFT} sq ft = "
          f"{BRIEF_GFA:.0f} m2, {100 * (bua - BRIEF_GFA) / BRIEF_GFA:+.1f}%)")
    print(f"DBC GFA (no basement) {dbc_gfa():.1f} m2   plot {PLOT_W * PLOT_D / 1e6:.1f} m2 = "
          f"{PLOT_W * PLOT_D / 1e6 * 10.7639:.0f} sq ft   cover "
          f"{100 * outline('GF').area / (PLOT_W * PLOT_D):.0f}%")
    print(f"pool {A(POOL_X0, POOL_Y0, POOL_X1, POOL_Y1):.1f} m2 ({pool_volume():.1f} m3)   "
          f"terrace {TERRACE:.0f}   feature stair {FF2FF / RISERS:.1f} x {STAIR_GOING:.0f}   "
          f"service stair {B12GF / STAIRS[1]['risers']:.1f} x {STAIRS[1]['going']:.0f}")
    print("=" * 72)
    issues = validate()
    fatal = [i for i in issues if i.startswith("[FATAL]")]
    major = [i for i in issues if i.startswith("[MAJOR]")]
    print(f"VALIDATION: {len(fatal)} fatal, {len(major)} major\n")
    for i in issues:
        print("  " + i)
    if not issues:
        print("  clean.")
    return issues


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    root = os.path.dirname(os.path.dirname(here))
    if root not in sys.path:
        sys.path.append(root)
    sys.modules.setdefault("villa_design", sys.modules[__name__])
    report()
