"""
VILLA — the design as DATA, plus the validator that proves it.

Why this module exists: the first villa was built procedurally, with opening
voids and wall positions written inline as magic numbers. Nothing could inspect
it, and a 45-agent critique found 52 fatal defects — including that NO opening
in the entire model actually penetrated its wall, because every void was sized
+/-300 against a 400 mm wall.

So the design is declared here as rooms, wall runs and openings. Geometry is
generated from this; the validator reads the same source. A defect that the
validator cannot see is a missing check, not a missing agent.

Run:  python villa_design.py      -> prints the validation report
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------- site
PLOT_W, PLOT_D = 24000.0, 29000.0            # 696 m2 = 7,492 sq ft
SB_FRONT, SB_SIDE, SB_REAR = 5000.0, 3000.0, 3000.0

# ---------------------------------------------------------------- levels
STREET = 0.0
GF, GF_CH = 900.0, 3600.0                    # raised half a level for privacy
SLAB = 500.0
FF = GF + GF_CH + SLAB                       # 5000
FF_CH = 3200.0
RF = FF + FF_CH + SLAB                       # 8700
PARAPET, PAV_CH = 1100.0, 3000.0
BASE_FL = -2800.0

WALL = 400.0                                 # external
PART = 150.0                                 # internal partition
FF2FF = FF - GF                              # floor to floor, for the stair

# Annex (floor "AX"): a single-storey service building on the plot, allowed on
# the boundary by DBC K.5.2.3 (>= 1.5 m from the villa, <= 5.5 m high, <= 60 %
# of the villa's GA). Roof pavilion (floor "RF"): rooms on the roof slab.
AX_FL, AX_CH = 150.0, 3000.0
LEVEL = {"AX": AX_FL, "GF": GF, "FF": FF, "RF": RF + SLAB}   # finished floor
CEIL = {"AX": AX_CH, "GF": GF_CH, "FF": FF_CH, "RF": PAV_CH}
FLOOR_ORDER = ("AX", "GF", "FF", "RF")

# Opening heights above finished floor. SLIDE = glazed sliding door: full
# height, no swing, any width -- how a living room opens to a terrace.
WIN_SILL, WIN_HEAD, DOOR_HEAD = 900.0, 2400.0, 2400.0

BRIEF_GFA = 4500 / 10.7639                   # the client's 4,500 sq ft, m2

# ---------------------------------------------------------------- grid
# North bar deepened 6.0 -> 7.5 m: the first floor was 43 m2 short of four
# suites and the plate is 18 m wide here, so depth is cheapest to buy in the bar.
HX0, HX1 = 3000.0, 21000.0
NB_Y0, NB_Y1 = 16500.0, 23200.0              # north bar, 6.7 deep
WG_Y0, WG_Y1 = 11000.0, 16500.0              # wings, 5.5 deep
WW_X0, WW_X1 = 3000.0, 8000.0
EW_X0, EW_X1 = 16000.0, 21000.0
LV_X0, LV_X1 = 8700.0, 15300.0               # double-height living volume
SLOT_A = (8000.0, 8700.0)                    # light slots, 700 wide
SLOT_B = (15300.0, 16000.0)

AXIS = 12000.0
RILL_W = 600.0

# Pool: crest differential is REAL this time. The south rim sits 40 mm below
# the other three so the sheet runs one way, into a basin that is actually cut.
POOL_X0, POOL_X1 = 9000.0, 15000.0           # 6.0 m wide
POOL_Y0, POOL_Y1 = 3200.0, 9800.0            # 6.6 m long
# Candidate B: the pool garden is raised to the ground-floor level (+900).
# At +700 the living-room slide needed a 200 mm step, and external_steps()
# put that step's tread 300 mm INTO the pool (the terrace is only 1200 deep).
# All four pool/basin levels move up 200 together, so every relationship the
# checks and probes test (crest -4, depth 1.4 m, basin 2.1 m below water) holds.
POOL_TW = 900.0                              # top water level = GF finished floor
POOL_CREST = POOL_TW - 4.0                   # 4 mm: research says 2-6
POOL_FL = -500.0                             # 1.4 m constant depth
# Catch basin / balance chamber, IN FRONT of the weir. It used to run to 3200
# -- over the tank's own south wall -- so cutting it deleted the weir the water
# is meant to spill over, and it went deeper than the shell: no floor.
WEIR = 400.0                                 # the tank's south wall, top = crest
BASIN_WALL = 300.0
BASIN_Y0, BASIN_Y1 = 1600.0, POOL_Y0 - WEIR  # footprint incl. its south wall
BASIN_FL = -1200.0
BASIN_WL = -300.0                            # balance water level

TERRACE = WG_Y0 - POOL_Y1                    # gap between glass and water

# Forecourt: a car must stand clear of the street with the gate shut.
# Candidate B pulls the whole street face (both floors, stacked) back from
# 24000 to 23150, so the forecourt is 28650 - 23150 = 5500 deep, and the
# porch starts AT the house face instead of 250 mm inside it.
PORCH_X0, PORCH_X1 = 3400.0, 10600.0
PORCH_Y0, PORCH_Y1 = 23150.0, 28650.0
GATE_X0, GATE_X1 = 4200.0, 9800.0

PV = (9000.0, 18000.0, 15000.0, 23600.0)     # roof pavilion

BS_X0, BS_X1 = 3000.0, 21000.0               # semi-basement
BS_Y0, BS_Y1 = 16500.0, 24000.0
# The sunken court used to sit inside the living volume and was roofed over.
# It now sits in the SLOT between masses, open to sky the whole way up.
CT_X0, CT_X1 = 15000.0, 16000.0
CT_Y0, CT_Y1 = 17500.0, 22500.0


def A(x0, y0, x1, y1):
    return abs(x1 - x0) * abs(y1 - y0) / 1e6


# ================================================================= ROOMS
# (name, x1, y1, x2, y2, kind, floor)
#   kind: habitable | wet | circulation | service
CIRC, HAB, WET, SVC = "circulation", "habitable", "wet", "service"

ROOMS = [
    # ---- GROUND (candidate B, "service wing"). Three zones across the bar:
    #  WEST  = SERVICE wing (service door off the car porch, dirty kitchen as
    #          the hub, pantry, laundry, maid room + bath) over the family
    #          SHOW KITCHEN in the west garden pavilion;
    #  CENTRE= ENTRANCE HALL (front door on the axis, stair) opening to the
    #          double-height FAMILY LIVING; a BACK HALL ties hall, living,
    #          kitchen and service together without crossing a guest room;
    #  EAST  = GUEST wing: WOMEN'S MAJLIS on the street side, GUEST LOBBY,
    #          GUEST WC, FORMAL DINING in the east garden pavilion.
    # Street face at 22750 + 400 = 23150 on BOTH floors (stacked).
    ("ENTRANCE HALL",  10300, 16900, 14900, 22750, CIRC, "GF"),
    ("BACK HALL",       5350, 16900, 10150, 18200, CIRC, "GF"),
    ("FAMILY LIVING",   9100, 11400, 14900, 16750, HAB,  "GF"),
    ("SHOW KITCHEN",    3400, 11400,  7600, 16750, HAB,  "GF"),
    # butler's pantry: the pass-through between dirty and show kitchens
    ("PANTRY",          3400, 16900,  5200, 18200, SVC,  "GF"),
    # dirty kitchen takes the service door and a street window (DBC K.5.4.2:
    # kitchens need 10 % glazing, and its west wall is on the setback line)
    ("DIRTY KITCHEN",   3400, 18350,  6350, 22750, SVC,  "GF"),
    ("LAUNDRY",         6500, 18350,  8550, 20400, SVC,  "GF"),
    ("MAID BATH",       8700, 18350, 10150, 20400, WET,  "GF"),
    # maid's room opens off the laundry -- never off a kitchen or guest route
    ("MAID ROOM",       6500, 20550, 10150, 22750, HAB,  "GF"),
    ("GUEST LOBBY",    15050, 16900, 17600, 18050, CIRC, "GF"),
    ("GUEST WC",       17750, 16900, 20600, 18050, WET,  "GF"),
    ("WOMEN'S MAJLIS", 15050, 18200, 20600, 22750, HAB,  "GF"),
    ("FORMAL DINING",  16400, 11400, 20600, 16750, HAB,  "GF"),

    # ---- FIRST. Four bedrooms, each with its OWN nested en-suite, every one
    #      doored off a single corridor spine; the family study moves up here
    #      (the ground floor cannot hold it with a window -- see notes).
    ("CORRIDOR",        3400, 16900, 16250, 18100, CIRC, "FF"),
    ("LANDING",        12650, 18250, 14900, 22750, CIRC, "FF"),
    ("BEDROOM 2",       3400, 18250,  8850, 22750, HAB,  "FF"),
    ("BEDROOM 2 ENS",   3400, 20250,  5300, 22750, WET,  "FF"),
    ("STUDY",           9000, 18250, 12500, 22750, HAB,  "FF"),
    ("BEDROOM 4",      15050, 18250, 20600, 22750, HAB,  "FF"),
    ("BEDROOM 4 ENS",  18400, 20500, 20600, 22750, WET,  "FF"),
    ("MASTER BEDROOM", 16400, 11400, 20600, 18100, HAB,  "FF"),
    ("MASTER ENSUITE", 18000, 15700, 20600, 18100, WET,  "FF"),
    ("BEDROOM 3",       3400, 11400,  7600, 16750, HAB,  "FF"),
    ("BEDROOM 3 ENS",   3400, 14550,  5600, 16750, WET,  "FF"),

    # ---- ANNEX (floor "AX"). Single storey on the street and east
    #      boundaries, 1550 clear of the villa. Driver's room + bath, store,
    #      plant; every room entered from outside or from the driver's room.
    # Plant at the west end (blank wall to the pedestrian gate), driver at
    # the east end, looking down the east side strip -- NOT at the guests'
    # path from the pedestrian gate, and not at a house window.
    ("PLANT ROOM",     17200, 25100, 18850, 28600, SVC,  "AX"),
    ("STORE",          19000, 25100, 20850, 26800, SVC,  "AX"),
    ("DRIVER BATH",    19000, 26950, 20850, 28600, WET,  "AX"),
    ("DRIVER ROOM",    21000, 25100, 23600, 28600, HAB,  "AX"),
]

# researched luxury minima, m2 (design-standards.md)
# Minimum NET floor area per room. The researched luxury figures (master bed
# 28-35 m2, suite 55-75) come from villas of 700 m2+; this house is 432 m2, so
# the master is held to 20 m2 net -- scaled to the building, and written down
# here rather than quietly dropped the moment it failed.
MIN_AREA = {
    "MASTER BEDROOM": 20.0,
    "BEDROOM 2": 14.0,
    "BEDROOM 3": 14.0,
    "BEDROOM 4": 14.0,
    "WOMEN'S MAJLIS": 25.0, "FAMILY LIVING": 28.0,
    "FORMAL DINING": 20.0, "SHOW KITCHEN": 20.0, "STUDY": 14.0,
    "DIRTY KITCHEN": 7.0, "MASTER ENSUITE": 4.0, "GUEST WC": 2.5,
}

# which bathroom serves which bedroom
ENSUITE_OF = {
    "MASTER BEDROOM": "MASTER ENSUITE",
    "BEDROOM 2": "BEDROOM 2 ENS",
    "BEDROOM 3": "BEDROOM 3 ENS",
    "BEDROOM 4": "BEDROOM 4 ENS",
}

# ============================================================ ZONES & ROLES
# A Gulf villa is judged by who walks through what. GUEST rooms (majlis,
# formal dining, guest WC) are reached from the entrance without passing
# family or private rooms; food reaches them from SERVICE without crossing
# FAMILY living; PRIVATE bedrooms open off circulation only. The route checks
# (validate, check 12) read these tables, so a door is judged by whom it lets
# through -- which is how "dining reached only through the pantry" and "study
# only through the women's majlis" survived three reviews.
CIRC_Z, GUEST, FAMILY, PRIVATE, SERVICE = "circ", "guest", "family", "private", "service"
ZONE = {
    "ENTRANCE HALL": CIRC_Z, "BACK HALL": CIRC_Z, "GUEST LOBBY": CIRC_Z,
    "GUEST WC": GUEST, "WOMEN'S MAJLIS": GUEST, "FORMAL DINING": GUEST,
    "SHOW KITCHEN": FAMILY, "FAMILY LIVING": FAMILY, "STUDY": FAMILY,
    "DIRTY KITCHEN": SERVICE, "PANTRY": SERVICE, "LAUNDRY": SERVICE,
    "MAID ROOM": SERVICE, "MAID BATH": SERVICE,
    "CORRIDOR": CIRC_Z, "LANDING": CIRC_Z,
    "MASTER BEDROOM": PRIVATE, "MASTER ENSUITE": PRIVATE,
    "BEDROOM 2": PRIVATE, "BEDROOM 2 ENS": PRIVATE,
    "BEDROOM 3": PRIVATE, "BEDROOM 3 ENS": PRIVATE,
    "BEDROOM 4": PRIVATE, "BEDROOM 4 ENS": PRIVATE,
    "DRIVER ROOM": SERVICE, "DRIVER BATH": SERVICE,
    "STORE": SERVICE, "PLANT ROOM": SERVICE,
}
ROLE = {
    "ENTRANCE HALL": "hall", "BACK HALL": "lobby", "GUEST LOBBY": "lobby",
    "GUEST WC": "guest_wc", "WOMEN'S MAJLIS": "majlis",
    "SHOW KITCHEN": "kitchen", "DIRTY KITCHEN": "prep_kitchen",
    "PANTRY": "pantry", "FORMAL DINING": "formal_dining",
    "FAMILY LIVING": "family_living", "STUDY": "study",
    "LAUNDRY": "laundry",
    "MAID ROOM": "maid_room", "MAID BATH": "maid_bath",
    "CORRIDOR": "corridor", "LANDING": "landing",
    "MASTER BEDROOM": "master_bedroom", "MASTER ENSUITE": "ensuite",
    "BEDROOM 2": "bedroom", "BEDROOM 2 ENS": "ensuite",
    "BEDROOM 3": "bedroom", "BEDROOM 3 ENS": "ensuite",
    "BEDROOM 4": "bedroom", "BEDROOM 4 ENS": "ensuite",
    "DRIVER ROOM": "driver_room", "DRIVER BATH": "driver_bath",
    "STORE": "store", "PLANT ROOM": "plant",
}
# The brief as roles: (role, how many, minimum NET m2 each). Gulf practice
# norms for a 4-bedroom family villa; Dubai Building Code minima, where the
# DBC sets one, are checked separately and win (references/
# dubai_villa_rules.json). Service rooms may sit in the house or the annex.
REQUIRED = [
    ("majlis", 1, 25.0), ("family_living", 1, 28.0), ("formal_dining", 1, 16.0),
    ("kitchen", 1, 14.0), ("prep_kitchen", 1, 7.0), ("guest_wc", 1, 2.5),
    ("master_bedroom", 1, 20.0), ("bedroom", 3, 14.0), ("ensuite", 4, 4.0),
    ("maid_room", 1, 7.5), ("maid_bath", 1, 2.5), ("laundry", 1, 4.0),
    ("driver_room", 1, 7.5), ("driver_bath", 1, 2.0),
    ("store", 1, 3.0), ("plant", 1, 4.0),
]
# What each kind of room must actually contain -- checked against the
# furniture layout by villa_furniture_spec.check(). "a|b" means either.
FIXTURES = {
    "ensuite": ["wc", "basin", "shower|bath"],
    "guest_wc": ["wc", "basin"],
    "maid_bath": ["wc", "basin", "shower"],
    "driver_bath": ["wc", "basin", "shower"],
    "kitchen": ["sink_unit", "hob", "fridge"],
    "prep_kitchen": ["sink_unit"],
    "formal_dining": ["chair"],
}
MIN_DINING_SEATS = 8

# ============================================================== SHADING
# Horizontal projections over south openings (depth >= 0.6 x opening height,
# villa_materials_spec.md s5) and vertical fin arrays on east/west faces
# (horizontals cannot shade a low east/west sun). Both are DATA, drawn by the
# builders and checked by validate(), not hard-coded in a builder -- the west
# brise-soleil used to be a loop inside two builders, and nothing checked
# which windows it actually shaded.
# SHADES: boxes (x0, y0, x1, y1, z0, z1), absolute mm.
# Candidate B: one eyebrow per pavilion per floor, the full width of the
# pavilion, its soffit 2.7 m above finished floor (+3600 GF / +7700 FF) --
# DBC K.5.2.5.1(a) puts every projection at least 2.7 m above FFL. Windows are
# 1500 high -> 900 deep needed; the slides are 2400 high -> 1440 needed, so
# the living canopy and the west (kitchen) eyebrow are 1500 deep. The living
# canopy oversails the 1200 terrace by 300 at the pool edge.
SHADES = [
    (3000.0, 9500.0, 8000.0, 11000.0, 3600.0, 3750.0),     # GF west pavilion
    (8700.0, 9500.0, 15300.0, 11000.0, 3600.0, 3750.0),    # GF living canopy
    (16000.0, 10000.0, 21000.0, 11000.0, 3600.0, 3750.0),  # GF east pavilion
    (3000.0, 10000.0, 8000.0, 11000.0, 7700.0, 7850.0),    # FF west pavilion
    (16000.0, 10000.0, 21000.0, 11000.0, 7700.0, 7850.0),  # FF east pavilion
]
# FIN_ARRAYS: vertical fins of thickness t at `pitch` along the face; `along`
# is the axis the fins are spaced on ("y" for an east/west face).
# Candidate B has NO east- or west-facing openings, so it needs no fins. The
# villa's east and west faces sit exactly on the 3 m side-setback lines, and
# DBC K.5.2.4 / K.5.2.5.1 (dubai_villa_rules.json K-SB-05, K-PRJ-02..04)
# allows no fin, of any depth below 2.7 m, in that setback -- the old
# full-height west array at x 2300-2750 was flagged NON-COMPLIANT. The side
# walls are blank: neighbour privacy, and no low east/west sun to shade.
FIN_ARRAYS = []

# ============================================================== OPENINGS
# (floor, kind, axis, wall_t0, wall_t1, a, b, room_a, room_b, swing_deg)
#   axis "v": wall spans x wall_t0..wall_t1, opening runs y a..b
#   axis "h": wall spans y wall_t0..wall_t1, opening runs x a..b
# room_b None means "outside".
DOOR, WIN, OPEN, SLIDE = "door", "window", "open", "slide"

OPENINGS = [
    # Candidate B. Doors 1000 wide (~915 clear, DBC K.5.5) except bathroom
    # doors at 800 (~710 clear); no opening on the east or west faces (they
    # stand on the side-setback lines, where DBC allows no shading fins).
    # ---- GROUND, external
    # front door on the entry axis (x 12000), 1400 pivot
    ("GF", DOOR, "h", 22750, 23150, 11300, 12700,
     "ENTRANCE HALL", None, 270),
    ("GF", WIN, "h", 22750, 23150, 10450, 11100,
     "ENTRANCE HALL", None, None),                   # sidelight to the door
    # service door straight into the dirty kitchen, off the car porch
    ("GF", DOOR, "h", 22750, 23150, 3600, 4600,
     "DIRTY KITCHEN", None, 270),
    ("GF", WIN, "h", 22750, 23150, 4900, 6200,
     "DIRTY KITCHEN", None, None),
    ("GF", WIN, "h", 22750, 23150, 7300, 9700,
     "MAID ROOM", None, None),
    # majlis street window: west end of its wall, clear of the annex (x>16800)
    ("GF", WIN, "h", 22750, 23150, 15250, 17350,
     "WOMEN'S MAJLIS", None, None),
    # the family kitchen opens to its own breakfast terrace, west of the pool
    ("GF", SLIDE, "h", 11000, 11400, 4100, 7100,
     "SHOW KITCHEN", None, None),
    # the living opens to the pool terrace: 4.8 m sliding wall, level threshold
    ("GF", SLIDE, "h", 11000, 11400, 9600, 14400,
     "FAMILY LIVING", None, None),
    ("GF", WIN, "h", 11000, 11400, 17000, 20000,
     "FORMAL DINING", None, None),
    # ---- GROUND, internal: family / guest / service routes
    # glazed sliding screen, not an open arch: the axial view from the front
    # door to the pool survives, but guests walking to the majlis do not
    # walk past an open family living room
    ("GF", SLIDE, "h", 16750, 16900, 10800, 14200,
     "ENTRANCE HALL", "FAMILY LIVING", None),
    ("GF", OPEN, "v", 10150, 10300, 17000, 18100,
     "BACK HALL", "ENTRANCE HALL", None),
    ("GF", OPEN, "h", 16750, 16900, 9250, 10050,
     "BACK HALL", "FAMILY LIVING", None),
    ("GF", DOOR, "h", 16750, 16900, 5650, 6650,
     "BACK HALL", "SHOW KITCHEN", 270),
    ("GF", DOOR, "h", 16750, 16900, 4100, 5100,
     "PANTRY", "SHOW KITCHEN", 270),
    ("GF", DOOR, "h", 18200, 18350, 4150, 5150,
     "PANTRY", "DIRTY KITCHEN", 90),
    ("GF", DOOR, "h", 18200, 18350, 5350, 6350,
     "BACK HALL", "DIRTY KITCHEN", 90),
    ("GF", DOOR, "v", 6350, 6500, 18500, 19500,
     "DIRTY KITCHEN", "LAUNDRY", 0),
    ("GF", DOOR, "h", 20400, 20550, 6550, 7550,
     "LAUNDRY", "MAID ROOM", 90),
    ("GF", DOOR, "h", 20400, 20550, 8850, 9650,
     "MAID ROOM", "MAID BATH", 270),
    ("GF", DOOR, "v", 14900, 15050, 16950, 17950,
     "ENTRANCE HALL", "GUEST LOBBY", 180),          # leaf swings into the hall
    ("GF", DOOR, "h", 16750, 16900, 16500, 17500,
     "GUEST LOBBY", "FORMAL DINING", 270),
    ("GF", DOOR, "v", 17600, 17750, 17050, 17850,
     "GUEST LOBBY", "GUEST WC", 0),
    ("GF", DOOR, "v", 14900, 15050, 18300, 19300,
     "ENTRANCE HALL", "WOMEN'S MAJLIS", 0),

    # ---- FIRST, external (north and south only)
    ("FF", WIN, "h", 11000, 11400, 4200, 6900,
     "BEDROOM 3", None, None),
    ("FF", WIN, "h", 11000, 11400, 16900, 20100,
     "MASTER BEDROOM", None, None),
    ("FF", WIN, "h", 22750, 23150, 5700, 8200,
     "BEDROOM 2", None, None),
    ("FF", WIN, "h", 22750, 23150, 3700, 4900,
     "BEDROOM 2 ENS", None, None),
    ("FF", WIN, "h", 22750, 23150, 9700, 11900,
     "STUDY", None, None),
    ("FF", WIN, "h", 22750, 23150, 15500, 17700,
     "BEDROOM 4", None, None),
    ("FF", WIN, "h", 22750, 23150, 18800, 20200,
     "BEDROOM 4 ENS", None, None),
    # ---- FIRST, internal. Every bedroom doors off the CORRIDOR; every
    #      en-suite doors off the bedroom it serves.
    ("FF", OPEN, "h", 18100, 18250, 12750, 14800,
     "CORRIDOR", "LANDING", None),
    ("FF", DOOR, "h", 18100, 18250, 7700, 8700,
     "CORRIDOR", "BEDROOM 2", 90),
    ("FF", DOOR, "h", 18100, 18250, 9150, 10150,
     "CORRIDOR", "STUDY", 90),
    ("FF", DOOR, "h", 18100, 18250, 15200, 16200,
     "CORRIDOR", "BEDROOM 4", 90),
    ("FF", DOOR, "v", 16250, 16400, 17000, 18000,
     "CORRIDOR", "MASTER BEDROOM", 0),
    ("FF", DOOR, "h", 16750, 16900, 6000, 7000,
     "CORRIDOR", "BEDROOM 3", 270),
    ("FF", DOOR, "h", 15550, 15700, 18200, 19000,
     "MASTER BEDROOM", "MASTER ENSUITE", 90),
    ("FF", DOOR, "h", 20100, 20250, 3600, 4400,
     "BEDROOM 2", "BEDROOM 2 ENS", 90),     # from the wardrobe bay, not the bed
    ("FF", DOOR, "v", 5600, 5750, 14750, 15550,
     "BEDROOM 3", "BEDROOM 3 ENS", 180),
    ("FF", DOOR, "v", 18250, 18400, 20700, 21500,
     "BEDROOM 4", "BEDROOM 4 ENS", 0),

    # ---- ANNEX. All doors open south into the 1550 service gap; the only
    #      window (driver) faces south past the house's NE corner, down the
    #      east side strip. West wall (pedestrian gate) and street wall blank.
    ("AX", DOOR, "h", 24700, 25100, 21300, 22300,
     "DRIVER ROOM", None, 90),
    ("AX", WIN, "h", 24700, 25100, 22500, 23450,
     "DRIVER ROOM", None, None),
    ("AX", DOOR, "v", 20850, 21000, 27250, 28050,
     "DRIVER ROOM", "DRIVER BATH", 180),
    ("AX", DOOR, "h", 24700, 25100, 19450, 20450,
     "STORE", None, 90),
    ("AX", DOOR, "h", 24700, 25100, 17500, 18500,
     "PLANT ROOM", None, 90),
]

# voids cut through floors: (name, x1, y1, x2, y2, floors_affected)
VOIDS = [
    ("DOUBLE-HEIGHT VOLUME", LV_X0 + WALL, WG_Y0, LV_X1 - WALL, WG_Y1, ("FF",)),
    # (The inert "SUNKEN COURT" entry -- no floors, a relic of the unbuilt
    #  semi-basement, sitting inside the north bar -- is dropped in candidate B.)
    ("STAIR VOID", 12800, 19350, 14900, 22750, ("FF",)),
    # The 700 mm gaps that make the south side read as three pavilions rather
    # than one block. They were real in the geometry but declared nowhere, so
    # nothing labelled them and nothing checked them -- they simply appeared
    # as unexplained notches in the outline.
    ("LIGHT SLOT",  8000, 11000,  8700, 16500, ("GF", "FF")),
    ("LIGHT SLOT", 15300, 11000, 16000, 16500, ("GF", "FF")),
]

ENTRY_ROOM = {"GF": "ENTRANCE HALL", "FF": "LANDING"}
# Dog-leg: 4100 floor-to-floor at 205 rise needs 20 risers / 19 goings, and
# 19 x 250 = 4750 will not fit the 4050-deep landing as a straight flight.
# Two flights of 10 with a half-landing fit in 3400.
# Candidate B: moved against the hall's east and north walls, so the front
# door on the axis looks straight through the hall to the living and pool;
# half-landing at the street end, both flights start/finish at y 19350.
STAIR = (12800.0, 19350.0, 14900.0, 22750.0)
RISERS = 20
STAIR_FLIGHTS = 2
STAIR_GOING = 250.0


# ================================================================ CHECKS
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
    """The strip of floor a door actually lands on, 900 mm inside `room_rect`.

    Which way it projects depends on which edge of the room the wall sits on;
    if the wall is not on an edge of this room the door does not serve it and
    None is returned."""
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
    """The floor a room actually has: its rectangle less every nested child
    AND the partition that separates them. Without the partition band there is
    no wall between a bedroom and its en-suite for a door to sit in."""
    from shapely.geometry import box as _box
    g = _box(*rect(room))
    for c in children(room):
        g = g.difference(_box(*rect(c)).buffer(PART, join_style=2, mitre_limit=8))
    return g


def net_area(room):
    return net_poly(room).area / 1e6


def fabric(floor):
    """External skin, partitions, internal envelope -- derived from the rooms.

    The 150 mm gaps between room polygons ARE the partitions; closing them with
    a +75/-75 buffer pair yields the internal envelope, and subtracting the
    rooms back out re-opens them as wall."""
    from shapely.ops import unary_union
    polys = [net_poly(r) for r in ROOMS if r[6] == floor]
    rooms = unary_union(polys)
    half = PART / 2.0
    inner = rooms.buffer(half, join_style=2, mitre_limit=8.0)                  .buffer(-half, join_style=2, mitre_limit=8.0)
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
    """Outside face of a floor's external walls (any floor, incl. AX/RF)."""
    return fabric(floor)[2].buffer(WALL, join_style=2, mitre_limit=8)


def opening_z(o):
    """(bottom, top) of an opening's void, absolute mm."""
    base = LEVEL[o[0]]
    if o[1] == WIN:
        return base + WIN_SILL, base + WIN_HEAD
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
    """Compass face of an EXTERNAL opening: 'N', 'S', 'E' or 'W', from which
    side of its wall is outside the building."""
    from shapely.geometry import Point
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    w0, w1 = min(t0, t1), max(t0, t1)
    mid = (a + b) / 2
    out = outline(fl)
    if axis == "h":
        return "N" if not out.contains(Point(mid, w1 + 10)) else "S"
    return "E" if not out.contains(Point(w1 + 10, mid)) else "W"


def door_graph(fl):
    """Room adjacency through doors/openings on one floor, and the rooms that
    have a door to the outside."""
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
    """Rooms reachable from `starts` passing THROUGH only rooms for which
    through(room) is true. The destination itself may be anything."""
    seen = set(starts)
    stack = [s for s in starts]
    while stack:
        n = stack.pop()
        for m in adj.get(n, ()):
            if m in seen:
                continue
            seen.add(m)
            if through(m):
                stack.append(m)
    return seen


def envelope():
    """Every footprint the 3D builders extrude, derived once, here.

    villa_3d_build.py (AutoCAD) and villa_gltf.py (render) each derived these
    for themselves, and both got the same thing wrong:
      * the DOUBLE-HEIGHT VOLUME has no first-floor room over it, so it fell
        outside the first-floor footprint and was capped by a slab at FF --
        the family living was a single storey in 3D;
      * wherever the ground floor reaches past the first floor (the whole
        18 m street front) the walls stopped at FF - SLAB while the roof over
        them started at FF: a 500 mm open band nobody probed;
      * the glTF track subtracted each ground-floor room from GF to FF, which
        cut the first-floor slab away over every one of them.
    Deriving it once means a builder cannot disagree with the design.
    """
    from shapely.geometry import box as _box
    from shapely.ops import unary_union
    _, _, in_gf = fabric("GF")
    _, _, in_ff = fabric("FF")
    out_gf = in_gf.buffer(WALL, join_style=2, mitre_limit=8)
    out_ff = in_ff.buffer(WALL, join_style=2, mitre_limit=8)
    dh = _box(LV_X0, WG_Y0, LV_X1, WG_Y1)
    dh_in = _box(LV_X0 + WALL, WG_Y0 + WALL, LV_X1 - WALL, WG_Y1)
    upper = unary_union([out_ff, dh])            # everything that rises to RF
    # A void opens the floor INSIDE the envelope only: the external wall band
    # carries on through the slab zone, or the facade gets a 500 mm slot.
    ff_slab = unary_union([out_gf, out_ff])
    for _, x0, y0, x1, y1, floors in VOIDS:
        if "FF" in floors:
            ff_slab = ff_slab.difference(_box(x0, y0, x1, y1).intersection(in_gf))
    single = out_gf.difference(upper)            # single-storey roof, top at FF
    edge = lambda g: g.difference(g.buffer(-350, join_style=2, mitre_limit=8))
    return {"out_gf": out_gf, "out_ff": out_ff, "in_gf": in_gf, "upper": upper,
            "dh": dh, "dh_in": dh_in, "ff_slab": ff_slab, "single": single,
            "parapet_single": single.intersection(edge(out_gf)),
            "parapet_roof": edge(upper)}


def pool_parts():
    """Pool structure and water as boxes (x0, y0, z0, x1, y1, z1), shared by
    both 3D builders so neither can re-invent the overflow.

    shell - cuts = the concrete; water = what fills it, including the sheet
    that runs down the face of the weir into the basin."""
    bx0, bx1 = POOL_X0 - 100, POOL_X1 + 100          # basin interior
    by0 = BASIN_Y0 + BASIN_WALL
    shell = [(POOL_X0 - 400, POOL_Y0 - WEIR, POOL_FL - 400,
              POOL_X1 + 400, POOL_Y1 + 400, POOL_TW),
             (POOL_X0 - 400, BASIN_Y0, BASIN_FL - 300,
              POOL_X1 + 400, BASIN_Y1, POOL_TW)]
    cuts = [(POOL_X0, POOL_Y0, POOL_FL, POOL_X1, POOL_Y1, POOL_TW + 100),
            (POOL_X0, POOL_Y0 - WEIR, POOL_CREST, POOL_X1, POOL_Y0, POOL_TW + 100),
            (bx0, by0, BASIN_FL, bx1, BASIN_Y1, POOL_TW + 100)]
    water = [(POOL_X0, POOL_Y0, POOL_FL, POOL_X1, POOL_Y1, POOL_TW),
             (bx0, by0, BASIN_FL, bx1, BASIN_Y1, BASIN_WL),
             (POOL_X0, BASIN_Y1 - 12, BASIN_WL, POOL_X1, BASIN_Y1, POOL_CREST)]
    return shell, cuts, water


GARDEN_Z = POOL_TW                  # the pool garden sits at top-water level
STEP_RISE_MAX, STEP_GOING, LANDING = 180.0, 300.0, 1200.0


def ground_at(y):
    """Finished ground outside the house: the raised pool garden south of the
    wings, street level everywhere else."""
    return GARDEN_Z if y < WG_Y0 else STREET


def external_steps():
    """Landing + flight outside every ground-floor external door, as boxes.

    The ground floor is raised 900 mm for privacy, and nothing got you up to
    it: the entrance door opened 900 mm above the forecourt. Each flight is
    derived from its door, so moving a door moves its steps."""
    import math as _m
    from shapely.geometry import Point
    boxes = []
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if fl not in ("GF", "AX") or kind not in (DOOR, SLIDE) or rb is not None:
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
        n = max(1, _m.ceil((FLV - ground) / STEP_RISE_MAX))
        rise = (FLV - ground) / n
        # room in front of the door: to the boundary wall, less a 900 path
        lim = (PLOT_D if axis == "h" else PLOT_W) - 350.0 if sign > 0 else 350.0
        room = abs(lim - face) - 900.0
        straight = LANDING + (n - 1) * STEP_GOING <= room

        def put(a0, a1, d0, d1, top):             # along-wall a, outward d
            q0, q1 = sorted((face + sign * d0, face + sign * d1))
            if axis == "h":
                boxes.append((a0, q0, ground, a1, q1, top))
            else:
                boxes.append((q0, a0, ground, q1, a1, top))

        if FLV - ground <= 1e-6:
            continue                              # level threshold: no steps
        put(s0, s1, 0.0, LANDING, FLV)
        for j in range(1, n):
            if straight:
                put(s0, s1, LANDING + (j - 1) * STEP_GOING,
                    LANDING + j * STEP_GOING, FLV - j * rise)
            else:
                # A straight flight would run into the boundary wall (the
                # west service door's reached 250 mm from it), so the flight
                # turns and runs alongside the house from the landing.
                put(s1 + (j - 1) * STEP_GOING, s1 + j * STEP_GOING,
                    0.0, LANDING, FLV - j * rise)
    return boxes


def probes():
    """Points the 3D fabric must be SOLID or VOID at: (name, x, y, z, expect, r).

    Shared by villa_3d_verify.py (AutoCAD interference) and villa_gltf.py
    (build123d is_inside), so both tracks answer the same questions. Each
    probe exists because a model once failed it without anything noticing.
    """
    from shapely.geometry import box as _box
    E = envelope()
    out = []

    def centre(g):
        if hasattr(g, "geoms"):
            g = max(g.geoms, key=lambda p: p.area)
        c = g.representative_point()
        return c.x, c.y

    for r in ROOMS:
        base = LEVEL[r[6]]
        x, y = centre(net_poly(r))
        out.append((f"{r[6]} {r[0]}", x, y, base + 1500, "void", 250.0))
        if r[6] == "GF":
            under_void = any("FF" in fl and _box(x0, y0, x1, y1).contains(
                _box(x - 1, y - 1, x + 1, y + 1))
                for _, x0, y0, x1, y1, fl in VOIDS)
            if not under_void:
                out.append((f"slab over {r[0]}", x, y, FF - SLAB / 2, "solid", 200.0))

    x, y = centre(E["dh_in"])
    # FF+1500 alone passes on a volume capped at FF -- above the cap is sky.
    # The cap itself sits at FF..FF+SLAB, so probe there too.
    out.append(("double height: no cap at FF", x, y, FF + SLAB / 2, "void", 200.0))
    out.append(("double height at FF+1500", x, y, FF + 1500, "void", 250.0))
    out.append(("roof over double height", x, y, RF + SLAB / 2, "solid", 200.0))
    band = (E["out_gf"].difference(E["in_gf"])).intersection(E["single"])
    if not band.is_empty:
        x, y = centre(band)
        out.append(("single-storey wall band", x, y, FF - SLAB / 2, "solid", 120.0))
    if not E["single"].is_empty:
        x, y = centre(E["single"])
        out.append(("single-storey roof", x, y, FF - SLAB / 2, "solid", 200.0))

    # every external door has a landing to step out onto
    for i, (x0, y0, z0, x1, y1, z1) in enumerate(external_steps()):
        if z1 in (LEVEL["GF"], LEVEL["AX"]):
            out.append((f"landing {i}", (x0 + x1) / 2, (y0 + y1) / 2, z1 - 60,
                        "solid", 40.0))

    # the house stands on the ground, not 400 mm above it
    x, y = centre(E["out_gf"])
    out.append(("plinth under the house", x, y, (GF - SLAB) / 2, "solid", 150.0))
    # the overflow: a weir to spill over, and a basin with a floor to catch it
    by = (BASIN_Y0 + BASIN_WALL + BASIN_Y1) / 2
    out.append(("weir below the crest", AXIS, POOL_Y0 - WEIR / 2,
                POOL_CREST - 150, "solid", 120.0))
    out.append(("weir clear above the crest", AXIS, POOL_Y0 - WEIR / 2,
                POOL_TW + 150, "void", 120.0))
    out.append(("basin floor", AXIS, by, BASIN_FL - 150, "solid", 120.0))
    out.append(("basin open", AXIS, by, BASIN_FL + 400, "void", 200.0))
    return out


def validate():
    issues = []

    # --- 1. every opening must PENETRATE its wall -------------------------
    # This is the class that produced 52 fatal findings: voids sized to the
    # wall face rather than through it leave a skin, so nothing is cut.
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        depth = abs(t1 - t0)
        need = WALL if rb is None else PART
        if depth < need - 1e-6:
            issues.append(
                f"[FATAL] {kind} {ra}->{rb or 'outside'}: void depth "
                f"{depth:.0f} < wall {need:.0f} — leaves a skin, cuts nothing")
        if kind == DOOR and not (700 <= abs(b - a) <= 1800):
            issues.append(f"[MAJOR] door {ra}->{rb or 'outside'} width "
                          f"{abs(b - a):.0f} outside 700-1800")
        if kind == SLIDE and not (1800 <= abs(b - a) <= 7200):
            issues.append(f"[MAJOR] sliding door {ra}->{rb or 'outside'} width "
                          f"{abs(b - a):.0f} outside 1800-7200")

    # --- 1b. a door must land in the room it names, not in a nested one ---
    # A corridor door whose leaf sweeps inside the ensuite is not a door to
    # the bedroom; it is a door to the ensuite wearing a bedroom's label. The
    # furniture pass finds this as a clash, but it is a PLAN fault, so it is
    # caught here where it is cheap.
    byname = {(r[6], r[0]): r for r in ROOMS}
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        # windows included: a window labelled to the bedroom but cut in the
        # en-suite's stretch of external wall is the same fault as a door
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
                    continue                       # only NESTED sub-rooms
                qx0, qy0, qx1, qy1 = rect(q)
                ov = (max(0.0, min(thr[2], qx1) - max(thr[0], qx0))
                      * max(0.0, min(thr[3], qy1) - max(thr[1], qy0)))
                if ov > 0.25 * ta:
                    issues.append(
                        f"[FATAL] door {ra}->{rb or 'outside'} lands "
                        f"{100 * ov / ta:.0f}% inside {q[0]}, which is nested "
                        f"in {side} -- it does not reach {side}")

    # --- 1c. an opening must sit ON a wall --------------------------------
    # Check 1 proves the void is deep enough. It does not prove the void is in
    # the right place: a window band left behind by a plan shift is the correct
    # thickness and cuts thin air. Intersect every void with the derived
    # fabric instead.
    for fl in floors():
        ex, pt_, _in = fabric(fl)
        skin = ex.union(pt_)
        for o in OPENINGS:
            if o[0] != fl:
                continue
            r = void_rect(o)
            frac = r.intersection(skin).area / r.area if r.area else 0.0
            if frac < 0.80:
                issues.append(
                    f"[FATAL] {o[1]} {o[7]}->{o[8] or 'outside'} sits "
                    f"{100 * frac:.0f}% on a wall (band {o[3]:.0f}-{o[4]:.0f}) "
                    f"-- it cuts thin air")

    # --- 1d. an internal opening must join rooms that SHARE a wall --------
    # A door was declared between the show kitchen and the formal dining room.
    # They are two rooms apart -- the pantry sits between them -- so the
    # "wall" it cut was 2850 mm of other people's rooms.
    for o in OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if rb is None or kind == WIN:
            continue
        A_, B_ = None, None
        for r in ROOMS:
            if r[6] == fl and r[0] == ra:
                A_ = r
            if r[6] == fl and r[0] == rb:
                B_ = r
        if A_ is None or B_ is None:
            issues.append(f"[FATAL] {kind} {ra}->{rb}: room not on floor {fl}")
            continue
        if contains(rect(A_), rect(B_)) or contains(rect(B_), rect(A_)):
            continue                                   # nested: wall is derived
        i = 1 if axis == "v" else 2
        gap = max(A_[i] - B_[i + 2], B_[i] - A_[i + 2])
        if gap < -1 or gap > PART + 1:
            issues.append(
                f"[FATAL] {kind} {ra}->{rb}: the rooms are {gap:.0f} mm apart, "
                f"not {PART:.0f} -- they do not share a wall")

    # --- 2. reachability: every room reached from the entry, through doors --
    for fl in floors():
        names = {r[0] for r in rooms_on(fl)}
        adj, ext = door_graph(fl)
        # the annex has no internal entry room: it is entered from outside
        start = ENTRY_ROOM.get(fl) or (sorted(ext)[0] if ext else None)
        if start is None:
            issues.append(f"[FATAL] {fl} has no entry room and no external door")
            continue
        seen, stack = {start} | set(ext if fl == "AX" else ()), [start] + (sorted(ext) if fl == "AX" else [])
        while stack:
            for nxt in adj.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        for n in sorted(names - seen):
            issues.append(f"[FATAL] {fl} {n} is UNREACHABLE from {start}")

        # --- 3. no bedroom reached only through another bedroom ------------
        beds = {r[0] for r in rooms_on(fl)
                if (r[0].startswith("BEDROOM") or r[0] == "MASTER BEDROOM")
                and "ENS" not in r[0]}
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
                issues.append(f"[FATAL] {bed} is an INNER ROOM — only reachable "
                              f"through another bedroom")

    # --- 4. every bedroom has a bathroom, reachable without another bedroom -
    wet = {r[0] for r in ROOMS if r[5] == WET}
    for bed, ens in ENSUITE_OF.items():
        if ens not in wet:
            issues.append(f"[FATAL] {bed} has no bathroom")
    beds_ff = [r[0] for r in rooms_on("FF")
               if (r[0].startswith("BEDROOM") or r[0] == "MASTER BEDROOM")
               and "ENS" not in r[0]]
    n_wet_ff = len([r for r in rooms_on("FF") if r[5] == WET])
    if n_wet_ff < len(beds_ff):
        issues.append(f"[FATAL] {len(beds_ff)} bedrooms share {n_wet_ff} "
                      f"bathroom(s) on FF")

    # --- 5. areas against the researched minima ---------------------------
    for r in ROOMS:
        m = MIN_AREA.get(r[0])
        if not m:
            continue
        # NET, not the rectangle: a master bedroom's rect includes its dressing
        # room and en-suite, and counting those as bedroom is how a 16 m2 room
        # passes a 26 m2 minimum.
        a_net = net_area(r)
        if a_net < m - 1e-6:
            issues.append(f"[MAJOR] {r[0]} {a_net:.1f} m2 net < "
                          f"minimum {m:.1f} m2")

    # --- 6. rooms must not overlap each other, or a void ------------------
    for fl in floors():
        rs = rooms_on(fl)
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                ra_, rb_ = rect(a), rect(b)
                if overlap(ra_, rb_):
                    # full containment is a nested sub-room (en-suite,
                    # dressing) and is intentional; only PARTIAL overlap is a
                    # geometry conflict.
                    if contains(ra_, rb_) or contains(rb_, ra_):
                        continue
                    issues.append(f"[MAJOR] {fl} {a[0]} partially overlaps "
                                  f"{b[0]}")
            for vname, vx0, vy0, vx1, vy1, vfl in VOIDS:
                if a[5] == CIRC:
                    continue          # a stair void inside a landing is correct
                if fl in vfl and overlap(rect(a), (vx0, vy0, vx1, vy1)):
                    issues.append(f"[FATAL] {fl} {vname} cuts through {a[0]}")

    # --- 6b. no unallocated space inside the envelope ---------------------
    # Whatever is inside the walls and is not a room becomes wall by default.
    # A 550-1050 mm strip between the north block and the south wing did
    # exactly that and rendered as a metre of solid masonry, because it was
    # nobody's problem. Anything left over that is thicker than a partition is
    # a hole in the brief, not a wall.
    from shapely.ops import unary_union as _uu
    for fl in floors():
        _e, _p, _in = fabric(fl)
        spare = _in.difference(_uu([net_poly(r) for r in rooms_on(fl)]))
        fat = spare.buffer(-(PART / 2 + 5), join_style=2)
        for g in (fat.geoms if hasattr(fat, "geoms") else
                  ([fat] if not fat.is_empty else [])):
            b = g.bounds
            issues.append(
                f"[MAJOR] {fl} {g.area / 1e6:.1f} m2 at "
                f"({b[0]:.0f},{b[1]:.0f})-({b[2]:.0f},{b[3]:.0f}) belongs to no "
                f"room and is thicker than a partition -- it will render as wall")

    # --- 7. pool: a real crest differential, and a basin that is cut ------
    if POOL_CREST >= POOL_TW:
        issues.append("[FATAL] pool has no crest differential — it cannot "
                      "overflow one way")
    if not (2 <= POOL_TW - POOL_CREST <= 6):
        issues.append(f"[MAJOR] crest differential {POOL_TW - POOL_CREST:.0f} mm "
                      f"outside the 2-6 mm the research specifies")
    if BASIN_FL >= POOL_CREST - 150:
        issues.append("[MAJOR] catch basin not low enough below the crest "
                      "(research: 150-300 mm)")
    if TERRACE < 1200:
        issues.append(f"[FATAL] terrace between glazing and water is "
                      f"{TERRACE:.0f} mm (min 1200)")

    # --- 8. forecourt: a car must stand clear of the street ---------------
    # MEASURED from the building, not read from PORCH_Y0: the declared porch
    # started at 23400 -- 600 mm INSIDE the house -- so the typed 5200 passed
    # while the real forecourt was 4650 and no car could stand in it.
    from shapely.geometry import box as _fb
    _house = outline("GF")
    _front = _house.intersection(_fb(PORCH_X0, 0, PORCH_X1, PLOT_D))
    _face = _front.bounds[3] if not _front.is_empty else PORCH_Y0
    if _house.intersection(_fb(PORCH_X0, PORCH_Y0, PORCH_X1, PORCH_Y1)).area > 1e4:
        issues.append(f"[FATAL] car porch {PORCH_X0:.0f}-{PORCH_X1:.0f} x "
                      f"{PORCH_Y0:.0f}-{PORCH_Y1:.0f} overlaps the house")
    fore = (PLOT_D - 350.0) - _face
    if fore < 5000:
        issues.append(f"[FATAL] forecourt {fore:.0f} mm deep — a car is "
                      f"~4800 long and does not fit")
    elif fore < 5500:
        issues.append(f"[NOTE ] forecourt {fore:.0f} mm: a car fits, but the "
                      f"researched comfort figure is 5500-6000")
    if (PORCH_X1 - PORCH_X0) < 5500:
        issues.append(f"[FATAL] car porch {PORCH_X1 - PORCH_X0:.0f} mm wide — "
                      f"two cars need 5500 minimum")

    # --- 9. stair ---------------------------------------------------------
    rise = FF2FF / RISERS
    going_run = (RISERS / STAIR_FLIGHTS - 1) * STAIR_GOING
    depth = STAIR[3] - STAIR[1]
    if going_run + 1100 > depth:          # flight + half-landing
        issues.append(f"[FATAL] stair: a {STAIR_FLIGHTS}-flight run needs "
                      f"{going_run + 1100:.0f} mm, the well is {depth:.0f} mm")
    if 2 * rise + STAIR_GOING < 550 or 2 * rise + STAIR_GOING > 700:
        issues.append(f"[MAJOR] stair 2R+G = {2 * rise + STAIR_GOING:.0f} "
                      f"(must be 550-700)")
    if rise > 220:
        issues.append(f"[MAJOR] stair rise {rise:.1f} mm > 220 "
                      f"({math.ceil(FF2FF / 220)} risers needed)")

    # --- 10. circulation. The researched <=8% is DEDICATED CORRIDOR measured
    #         against whole-house GIA; a hall or landing is an occupied room,
    #         so it is reported separately rather than folded in.
    gia = sum(A(*rect(r)) for r in ROOMS)
    corridor = sum(A(*rect(r)) for r in ROOMS
                   if r[5] == CIRC and "CORRIDOR" in r[0])
    halls = sum(A(*rect(r)) for r in ROOMS
                if r[5] == CIRC and "CORRIDOR" not in r[0])
    if gia and 100 * corridor / gia > 8:
        issues.append(f"[MAJOR] dedicated corridor {corridor:.1f} m2 = "
                      f"{100 * corridor / gia:.1f}% of GIA (target <=8%)")
    globals()["_CIRC_REPORT"] = (corridor, halls, gia)
    issues += checks_brief()
    return issues


def checks_brief():
    """Checks 11-20: programme, routes, garden, daylight, climate, GFA, annex,
    setbacks. Each exists because the design passed every earlier check while
    failing it (see the audit of 2026-09-25)."""
    from shapely.geometry import box as _b
    issues = []
    fls = floors()

    # --- 11. every room has a zone and a role ------------------------------
    for r in ROOMS:
        if r[0] not in ZONE:
            issues.append(f"[FATAL] {r[6]} {r[0]} has no ZONE -- routes cannot be judged")
        if r[0] not in ROLE:
            issues.append(f"[FATAL] {r[6]} {r[0]} has no ROLE -- programme cannot be judged")

    # --- 12. routes: who walks through what --------------------------------
    z = lambda n: ZONE.get(n)
    for fl in fls:
        adj, ext = door_graph(fl)
        entry = ENTRY_ROOM.get(fl)
        starts = {entry} if entry else set(ext)
        if not starts:
            issues.append(f"[FATAL] {fl} has no entry room and no external door")
            continue
        for r in rooms_on(fl):
            n, zn, role = r[0], z(r[0]), ROLE.get(r[0])
            if n in starts or zn is None:
                continue
            if zn == GUEST:
                ok = {CIRC_Z, GUEST}
            elif zn == FAMILY:
                ok = {CIRC_Z, FAMILY}
            elif zn == PRIVATE:
                # a bedroom opens off circulation; its en-suite off the bedroom
                ok = {CIRC_Z} if role in ("bedroom", "master_bedroom") else {CIRC_Z, PRIVATE}
            elif zn == SERVICE:
                ok = {CIRC_Z, SERVICE, FAMILY}
            else:
                continue
            got = reach(adj, starts | (ext if zn == SERVICE else set()),
                        lambda m, ok=ok: z(m) in ok)
            if n not in got:
                issues.append(
                    f"[FATAL] {fl} {n} ({zn}) cannot be reached without passing "
                    f"through a room outside {sorted(ok)} -- check its doors")
        # food to the guests without crossing the family: from any service
        # room to every guest dining/majlis room, through service/circ/guest
        src = {r[0] for r in rooms_on(fl) if z(r[0]) == SERVICE}
        for r in rooms_on(fl):
            if ROLE.get(r[0]) not in ("majlis", "formal_dining") or not src:
                continue
            got = reach(adj, src, lambda m: z(m) in (SERVICE, CIRC_Z, GUEST))
            if r[0] not in got:
                issues.append(f"[MAJOR] {fl} service cannot reach {r[0]} without "
                              f"crossing family or private rooms")

    # --- 13. the brief, as roles -------------------------------------------
    for role, count, amin in REQUIRED:
        rs = [r for r in ROOMS if ROLE.get(r[0]) == role]
        if len(rs) < count:
            issues.append(f"[MAJOR] programme: {len(rs)} x {role}, brief needs {count}")
        for r in rs:
            if net_area(r) < amin - 1e-6:
                issues.append(f"[MAJOR] {r[0]} ({role}) {net_area(r):.1f} m2 net "
                              f"< {amin:.1f} m2")

    # --- 14. the house opens to its garden ---------------------------------
    garden_doors = []
    for o in OPENINGS:
        if o[0] != "GF" or o[1] == WIN or o[8] is not None:
            continue
        if z(o[7]) in (FAMILY, GUEST) and facing(o) == "S":
            garden_doors.append(o)
    if not garden_doors:
        issues.append("[FATAL] no door from a family or guest room to the garden -- "
                      "the pool is reached through the service door")

    # --- 15. daylight: every habitable room has a window to the outside ----
    lit = {o[7] for o in OPENINGS if o[8] is None and o[1] in (WIN, SLIDE)}
    for r in ROOMS:
        if r[5] == HAB and r[0] not in lit:
            issues.append(f"[MAJOR] {r[6]} {r[0]} is habitable with no external window")

    # --- 16. climate: south openings under a projection, east/west behind fins
    fin_boxes = fins()
    for o in OPENINGS:
        if o[8] is not None or o[0] not in ("GF", "FF", "RF"):
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
                     for s in SHADES)
            if not ok:
                issues.append(f"[MAJOR] {fl} {kind} {ra} faces south with no "
                              f"projection >= {need:.0f} mm over it")
        elif face in ("E", "W"):
            wx = min(t0, t1) if face == "W" else max(t0, t1)
            cover = [f for f in fin_boxes
                     if (f[2] <= wx + 20 and f[0] >= wx - 1500 if face == "W"
                         else f[0] >= wx - 20 and f[2] <= wx + 1500)
                     and f[4] <= lo and f[5] >= hi]
            ys = sorted((f[1], f[3]) for f in cover if f[3] > a0 and f[1] < a1)
            if not ys or ys[0][0] > a0 + 600 or ys[-1][1] < a1 - 600:
                issues.append(f"[MAJOR] {fl} {kind} {ra} faces {'west' if face == 'W' else 'east'} "
                              f"with no fins in front of it")

    # --- 17. GFA counts only what is built ---------------------------------
    if "RF" not in fls:
        issues.append(f"[NOTE ] no rooms on the roof: the {A(*PV):.1f} m2 pavilion is "
                      f"not built and is excluded from GFA")
    gfa = gross_area()
    if abs(gfa - BRIEF_GFA) / BRIEF_GFA > 0.10:
        issues.append(f"[MAJOR] GFA {gfa:.1f} m2 is more than 10% from the "
                      f"{BRIEF_GFA:.0f} m2 brief")

    # --- 18. annex: DBC K.5.2.3 --------------------------------------------
    if "AX" in fls:
        ax = outline("AX")
        villa = outline("GF")
        gap = ax.distance(villa)
        if gap < 1500:
            issues.append(f"[FATAL] annex is {gap:.0f} mm from the villa (DBC K.5.2.3: >= 1500)")
        if AX_FL + AX_CH + SLAB + PARAPET > 5500 + 1e-6:
            issues.append(f"[FATAL] annex height {AX_FL + AX_CH + SLAB + PARAPET:.0f} mm "
                          f"> 5500 (DBC K.5.2.3)")
        if ax.area > 0.6 * villa.area:
            issues.append("[FATAL] annex larger than 60% of the villa footprint")
        if not _b(0, 0, PLOT_W, PLOT_D).contains(ax):
            issues.append("[FATAL] annex outside the plot")

    # --- 19. setbacks (the villa; the annex may sit on the boundary) -------
    inner = _b(SB_SIDE, SB_REAR, PLOT_W - SB_SIDE, PLOT_D - SB_FRONT)
    for fl in fls:
        if fl == "AX":
            continue
        spill = outline(fl).difference(inner)
        if spill.area > 1e4:
            b_ = spill.bounds
            issues.append(f"[MAJOR] {fl} outline crosses the setback line by "
                          f"{spill.area / 1e6:.1f} m2 around ({b_[0]:.0f},{b_[1]:.0f})"
                          f"-({b_[2]:.0f},{b_[3]:.0f})")
    return issues


def gross_area():
    """GFA: external outline of every built floor. The roof pavilion counts
    only if it has rooms -- it was counted for weeks while it did not exist."""
    return sum(outline(fl).area / 1e6 for fl in floors())


def report():
    print("=" * 66)
    for fl in floors():
        rs = rooms_on(fl)
        tot = sum(net_area(r) for r in rs)
        hab = sum(net_area(r) for r in rs if r[5] == HAB)
        print(f"{fl}: {len(rs):2d} rooms   net {tot:6.1f} m2   "
              f"habitable {hab:6.1f} m2")
    gf_gross = outline("GF").area / 1e6
    gfa = gross_area()
    parts = "  +  ".join(f"{fl} {outline(fl).area / 1e6:.1f}" for fl in floors())
    print(f"gross: {parts}  =  GFA {gfa:.1f} m2 = {gfa * 10.7639:.0f} sq ft"
          f"   (brief {BRIEF_GFA:.0f} m2)")
    c = globals().get("_CIRC_REPORT")
    if c:
        print(f"corridor {c[0]:.1f} m2 = {100 * c[0] / c[2]:.1f}% of GIA   "
              f"halls/landing {c[1]:.1f} m2")
    print(f"coverage {100 * gf_gross / (PLOT_W * PLOT_D / 1e6):.0f}%   "
          f"pool {A(POOL_X0, POOL_Y0, POOL_X1, POOL_Y1):.0f} m2   "
          f"terrace {TERRACE:.0f} mm   stair rise {FF2FF / RISERS:.1f} mm")
    print("=" * 66)
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
    report()
