"""Add the FIA furniture blocks to the block catalogue.

Sizes are the measured extents from catalog_new_blocks.py, not the names'
promises. These entries carry `pack` + `block` instead of `path`, because the
definition lives inside a library drawing and is copied between databases
rather than inserted from a file.

The pack is looked up from the measurements rather than hardcoded: six of these
live in pack 03, and hardcoding pack 02 silently dropped them.
"""

import json

CAT = r"C:\Users\lsire\autocad-mcp\block_catalog.json"
MEAS = r"C:\Users\lsire\OneDrive\Desktop\Villa\blocks\measured_blocks.json"

# catalogue key -> block name as it appears in the library
NEW = {
    "fia_bed":        "PNL 15C Bed Plan",
    "fia_sofa_long":  "ZC 504 Sofa Plan",
    "fia_sofa_3":     "CT 03 Sofa plan",
    "fia_sofa_2":     "AS 02 Sofa Plan",
    "fia_sofa_ph":    "PH 03 Sofa Plan",
    "fia_sofa_ke":    "KE 02 Sofa Plan",
    "fia_armchair":   "SW01M Arm chair Plan",
    "fia_recliner":   "NH 01 Recliner chair Plan",
    "fia_tbl_round":  "Circular Table Plan",
    "fia_tbl_dining": "SP09C Table Plan",
    "fia_tbl_coffee": "OP 11 Table Plan",
    "fia_tbl_low":    "Sumo Table Plan",
    "fia_tbl_toast":  "Toast Table Plan",
    # seating the tables never had: the dining check counts keys with "chair"
    "fia_chair":      "Brera Chair Plan",
    "fia_chair_cc":   "CC 01 Chair Plan",
    "fia_stool":      "UL 304 Stool Plan",
}


def main():
    meas = [m for m in json.load(open(MEAS)) if "Imperial" not in m["file"]]
    by_block = {m["block"]: m for m in meas}
    cat = json.load(open(CAT))
    added, missing = [], []
    for key, block in NEW.items():
        m = by_block.get(block)
        if not m:
            missing.append(f"{key} ({block})")
            continue
        cat[key] = {"pack": m["file"], "block": block,
                    "w": round(m["w"], 1), "d": round(m["d"], 1),
                    "offx": 0.0, "offy": 0.0, "scale": 1.0,
                    "source": "First In Architecture furniture pack, metric"}
        added.append((key, block, m["w"], m["d"], m["file"][-10:]))
    json.dump(cat, open(CAT, "w"), indent=1)

    for key, block, wd, dd, pk in sorted(added):
        print(f"  {key:16s} {block[:28]:28s} {wd:6.0f} x {dd:6.0f} mm  {pk}")
    if missing:
        print("\nnot found: " + ", ".join(missing))
    print(f"\ncatalogue now holds {len(cat)} blocks ({len(added)} added)")


if __name__ == "__main__":
    main()
