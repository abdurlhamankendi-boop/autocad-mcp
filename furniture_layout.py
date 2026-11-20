"""Furniture layout, shared by the DXF generator and the AutoCAD block inserter.

Each entry is (block_key, x, y, rotation_degrees) where (x, y) is the desired
BOTTOM-LEFT of the block's footprint, in plan millimetres.

The DXF generator uses these footprints as label-avoidance obstacles without
drawing anything, so room labels dodge furniture that is inserted later as real
AutoCAD blocks. Sizes come from block_catalog.json, measured by inserting each
block and reading its actual extents.
"""

import json
import os

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "block_catalog.json")
with open(CATALOG_PATH) as fh:
    CATALOG = json.load(fh)

# (key, x, y, rotation)
GROUND = [
    # LIVING  300..6000 x 300..5300
    ("sofa",         1000,  500,   0),
    ("coffee_table", 1300, 1800,   0),
    ("sofa_l",       3900,  500,  90),
    ("dresser",       600, 4200,   0),
    # KITCHEN / DINING  6100..12700 x 300..5300
    ("sink_unit",    9700,  400,   0),
    ("hob",         10800,  400,   0),
    ("fridge",      11800,  400,   0),
    ("dishwasher",   8900,  400,   0),
    ("dining",       6600, 2400,   0),
    # SNUG  300..4800 x 5400..9300
    ("sofa",          800, 5700,   0),
    ("coffee_table", 1100, 6900,   0),
    # WC  7700..9400 x 5400..7200  (door swings 7650-8450 x 5700-6500)
    ("wc",           8800, 5600,   0),
    ("basin",        8800, 6600,   0),
    # UTILITY  7700..9400 x 7300..9300  (door swings 7650-8450 x 7500-8300)
    ("dishwasher",   8600, 7500,   0),
    ("sink_unit",    7900, 8500,   0),
    # FAMILY  9500..12700 x 5400..9300  (door swings 11200-12100 x 5350-6250)
    ("sofa_l",       9700, 6600,   0),
    ("coffee_table", 9700, 8600,   0),
]

FIRST = [
    # BEDROOM 1 (master)  300..6000 x 300..5300
    #   landing door swings 2400-3300 x 4450-5350, so the bed goes south-west
    ("bed_double",    900,  600,   0),
    ("bedside",       450, 2600,   0),
    ("bedside",      2550, 2600,   0),
    ("wardrobe",     4900,  600,   0),
    ("dresser",      4900, 3600,   0),
    # BEDROOM 3  6100..9400 x 300..5300  (door swings 6900-7800 x 4450-5350)
    ("bed_single",   6300,  500,   0),
    ("wardrobe",     8400,  600,   0),
    # BEDROOM 4  9500..12700 x 300..5300  (door swings 10600-11500 x 4450-5350)
    ("bed_single",   9700,  500,   0),
    ("wardrobe",    11800,  600,   0),
    # BEDROOM 2  300..4800 x 5400..9300  (door swings 3950-4850 x 6300-7200)
    ("bed_double",   1300, 7000,   0),
    ("bedside",       800, 8700,   0),
    ("bedside",      3000, 8700,   0),
    ("wardrobe",      600, 5700,   0),
    # EN-SUITE  7700..9400 x 5400..6800  (door swings 7650-8450 x 5700-6500)
    ("wc",           8800, 5600,   0),
    ("basin",        8800, 6300,   0),
    # BATHROOM  7700..9400 x 6900..9300  (door swings 7650-8550 x 7400-8300)
    ("bath",         7700, 8500,   0),
    ("wc",           8800, 7100,   0),
    ("basin",        8800, 7700,   0),
    # STUDY  9500..12700 x 5400..9300  (door swings 9450-10350 x 6400-7300)
    ("dresser",      9800, 8300,   0),
    ("sofa",        10600, 5700,   0),
]


def footprint(key, x, y, rot):
    """Bounding box the block will occupy once inserted at (x, y)."""
    m = CATALOG.get(key)
    if not m or "w" not in m:
        return None
    wd, dp = m["w"], m["d"]
    if rot % 180 == 90:
        wd, dp = dp, wd
    return (x, y, x + wd, y + dp)


def insert_point(key, x, y, rot):
    """AutoCAD insertion point that lands the footprint at (x, y).

    Blocks are not drawn about their own corner -- a bed's insertion point sits
    at its top centre -- so the measured offset has to be subtracted.
    """
    m = CATALOG[key]
    ox, oy = m["offx"], m["offy"]
    if rot % 360 == 0:
        return (x - ox, y - oy)
    if rot % 360 == 90:
        return (x + oy + m["d"], y - ox)
    if rot % 360 == 180:
        return (x + ox + m["w"], y + oy + m["d"])
    return (x - oy, y + ox + m["w"])


def obstacles(floor):
    out = []
    for key, x, y, rot in (GROUND if floor == "ground" else FIRST):
        fp = footprint(key, x, y, rot)
        if fp:
            out.append(fp)
    return out
