"""Inventory the ACA Metric\\Design content library for 3D dressing of the
villa model and render (read-only, no AutoCAD).

For every DWG under AEC Content\\Metric\\Design: object census via
dwg_read.census() -> is it a multi-view block (AEC_MVBLOCK_DEF/REF objects),
does it carry real 3D geometry (3DSOLID/BODY/3DFACE/PFACE/MESH/mass elements),
preview kind; joined with the Design - Metric tool-catalog entry (name,
description, units) where one exists. Then a deterministic Gulf-villa
priority tier from the category path and name.

Also re-checks the villa's own block_catalog.json paths (read-only) so the
claim "13 of 16 ACA blocks in use are 3D" is measured, not eyeballed.

Output: out\\content_3d.json, thumbs\\content_tierA_contact.png
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import xml.etree.ElementTree as ET

import dwg_read as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\ProgramData\Autodesk\ACA 2027\enu\AEC Content\Metric\Design"
ATC = (r"C:\ProgramData\Autodesk\ACA 2027\enu\Tool Catalogs\Design - Metric"
       r"\Categories\*.atc")
CATALOG = r"C:\Users\lsire\autocad-mcp\block_catalog.json"
OUT = os.path.join(HERE, "out", "content_3d.json")
THUMBS = os.path.join(HERE, "thumbs", "content")

# (tier, regex on 'Category\\Sub\\Name', reason). First match wins.
# A-site     = exterior render dressing (garden, forecourt, pool deck)
# A-interior = the rooms of the villa's furniture manifest
# B = other residential / garden extras;  C = not for a villa.
TIERS = [
    # dining chairs live under Office Furniture\Chairs but are domestic
    ("A-interior", r"(?i)dining chair|dining table|\\3D Dining|bar stool",
     "dining / breakfast"),
    ("A-interior", r"(?i)executive chair|secretary chair",
     "study desk chair"),
    ("C", r"(?i)office|school|urinal|drinking fountain|floor sink|cubicle|"
          r"workstation|conference|elevator|escalator|boat|street light|"
          r"traffic|parking|bus|truck|lorry|sport|grab rail|crane|trailer|"
          r"container|coach|hgv|umbrella stand",
     "commercial / public-realm / construction item"),
    ("A-site", r"(?i)^site\\trees|^illustrations\\trees|^illustrations\\"
               r"plants|domestic furniture\\plants",
     "vegetation for garden and courtyard"),
    ("A-site", r"(?i)^site\\vehicles|^illustrations\\vehicle\\car",
     "cars for forecourt / garage"),
    ("A-site", r"(?i)^illustrations\\people|^site\\humans", "people for "
                                                            "scale"),
    ("A-site", r"(?i)domestic furniture\\garden|furniture\\outdoors|"
               r"lounger|umbrella|parasol|pergola", "pool deck and garden"),
    ("A-interior", r"(?i)sofa|armchair|easy chair|majlis|coffee",
     "living / majlis seating"),
    ("A-interior", r"(?i)bed|wardrobe|closet|chest|dresser|bedside",
     "bedrooms"),
    ("A-interior", r"(?i)dining|chair|table", "dining / breakfast"),
    ("A-interior", r"(?i)^bathroom\\(toilet|basin|bath|shower|bidet)|"
                   r"furnishing\\bathroom",
     "bathrooms (bidet/shattaf is expected in the Gulf)"),
    ("A-interior", r"(?i)^kitchen fittings|^appliances\\kitchen", "kitchen"),
    ("B", r"(?i)^illustrations\\park|^site\\recreation|^site\\street furniture"
          r"|bollard|external lighting", "garden structures and lighting"),
    ("B", r"(?i)^appliances|^bathroom|^furnishing|^domestic furniture|"
          r"^furniture\\home|^lighting", "other residential"),
    ("C", r".", "not residential"),
]
# what a Gulf villa render wants; checked against ALL names and 3D-only names
GULF_WANTED = {"date palm": r"(?i)palm", "ghaf / acacia": r"(?i)ghaf|acacia",
               "any 3D tree": r"(?i)^(site|illustrations)\\trees\\|\btree\b|"
                              r"poplar|spruce|\bpine\b|hedge",
               "3D people": r"(?i)\\(people|humans)\\|\b(man|woman|human|"
                            r"figure)\b(?! 8)",
               "bidet / shattaf": r"(?i)bidet|shattaf",
               "4x4 / SUV": r"(?i)\bjeep\b|\bsuv\b|\b4x4\b|land ?cruiser",
               "sun lounger": r"(?i)lounger|sunbed|sun bed",
               "parasol / umbrella": r"(?i)\\3D umbrella|parasol",
               "pergola": r"(?i)pergola",
               "floor seating / majlis": r"(?i)majlis|floor seat|cushion"}


def atc_index():
    idx = {}
    for f in glob.glob(ATC):
        root = ET.parse(f).getroot()
        for tool in root.iter("Tool"):
            cf = tool.findtext("Data/AecDbDcContent/ContentFilename")
            if not cf:
                continue
            rel = cf.split("Metric\\Design\\", 1)[-1].lower()
            idx[rel] = {"tool": tool.findtext("Properties/ItemName"),
                        "description": tool.findtext("Properties/Description"),
                        "units": tool.findtext("Data/Units"),
                        "catalog": os.path.basename(f).split("_")[0]}
    return idx


def tier(rel):
    for t, rx, why in TIERS:
        if re.search(rx, rel):
            return t, why
    return "C", "not residential"


def scan(path):
    data = open(path, "rb").read()
    rec = {"preview": D.preview(data)[0]}
    try:
        _s, _c, ot = D.census(data)
    except (D.DwgError, KeyError, IndexError) as e:
        rec["error"] = f"{type(e).__name__}: {e}"
        return rec, None
    g3 = {k: v for k, v in ot.items() if k in D.GEOM_3D}
    rec.update({
        "mvblock_defs": ot.get("AEC_MVBLOCK_DEF", 0),
        "mvblock_refs": ot.get("AEC_MVBLOCK_REF", 0),
        "is_mvblock": bool(ot.get("AEC_MVBLOCK_DEF") or
                           ot.get("AEC_MVBLOCK_REF")),
        "geometry_3d": g3,
        "is_3d": bool(g3),
        "faces": ot.get("3DFACE", 0) + ot.get("VERTEX_PFACE_FACE", 0),
        "block_defs": ot.get("BLOCK_HEADER", 0),
        "entities_2d": sum(ot.get(k, 0) for k in (
            "LINE", "LWPOLYLINE", "ARC", "CIRCLE", "HATCH", "POLYLINE_2D",
            "ELLIPSE", "SPLINE")),
    })
    return rec, data


def main():
    idx = atc_index()
    rows = []
    for dp, _dn, fn in os.walk(ROOT):
        for f in sorted(fn):
            if not f.lower().endswith(".dwg"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT)
            parts = rel.split(os.sep)
            rec, data = scan(p)
            t, why = tier(rel)
            meta = idx.get(rel.lower(), {})
            rows.append({"file": rel, "category": parts[0],
                         "subcategory": "\\".join(parts[1:-1]),
                         "name": os.path.splitext(parts[-1])[0],
                         "named_3d": "3d" in parts[-1].lower() or
                         any("3d" in x.lower() for x in parts[:-1]),
                         "tier": t, "tier_reason": why,
                         "catalog_units": meta.get("units"),
                         "catalog_description": meta.get("description")}
                        | rec)
    rows.sort(key=lambda r: (r["tier"], r["category"], r["subcategory"],
                             r["name"]))
    ok = [r for r in rows if "error" not in r]
    usable = [r for r in ok if r["is_3d"]]
    # thumbnails + contact sheet for tier-A 3D items
    os.makedirs(THUMBS, exist_ok=True)
    tier_a = [r for r in usable if r["tier"] == "A-site"]
    for r in tier_a:
        png = D.preview_png(open(os.path.join(ROOT, r["file"]), "rb").read())
        if png:
            t = os.path.join(THUMBS, re.sub(r"[^A-Za-z0-9_-]+", "_",
                                            r["file"][:-4]) + ".png")
            open(t, "wb").write(png)
            r["thumb"] = os.path.relpath(t, HERE)
    contact = None
    try:
        from mine_projects import contact_sheet
        contact = contact_sheet(
            [(r["file"][:-4].replace("\\", " / ")[-44:], r.get("thumb"))
             for r in tier_a],
            os.path.join(HERE, "thumbs", "content_tierA_contact.png"),
            "ACA Metric\\Design: A-site 3D content (garden, forecourt, pool "
            "deck) - embedded previews")
    except ImportError:
        pass
    # villa's block_catalog.json, read-only
    villa = []
    try:
        cat = json.load(open(CATALOG, encoding="utf-8"))
        for key, v in cat.items():
            pth = v.get("path", "")
            if "AEC Content" not in pth or not os.path.exists(pth):
                continue
            rel = os.path.relpath(pth, ROOT)
            hit = next((r for r in rows if r["file"].lower() == rel.lower()),
                       None)
            villa.append({"key": key, "file": rel,
                          "is_3d": hit and hit.get("is_3d"),
                          "is_mvblock": hit and hit.get("is_mvblock"),
                          "geometry_3d": hit and hit.get("geometry_3d"),
                          "catalog_units": hit and hit.get("catalog_units"),
                          "villa_scale": v.get("scale")})
    except (OSError, ValueError) as e:
        villa = [{"error": str(e)}]
    gaps = {}
    for k, rx in GULF_WANTED.items():
        anyf = [r["file"] for r in rows if re.search(rx, r["file"])]
        in3d = [r["file"] for r in usable if re.search(rx, r["file"])]
        gaps[k] = {"any_file": len(anyf), "with_3d_geometry": len(in3d),
                   "examples_3d": in3d[:6]}
    by_cat = collections.Counter(r["category"] for r in usable)
    mismatch = {
        "named_3d_but_no_3d_geometry": [r["file"] for r in ok
                                        if r["named_3d"] and not r["is_3d"]],
        "3d_geometry_but_not_named_3d": sum(1 for r in ok if r["is_3d"]
                                            and not r["named_3d"]),
    }
    res = {
        "root": ROOT,
        "scanned": len(rows), "parsed": len(ok),
        "errors": [{"file": r["file"], "error": r["error"]}
                   for r in rows if "error" in r],
        "with_3d_geometry": len(usable),
        "multi_view_blocks": sum(1 for r in ok if r["is_mvblock"]),
        "multi_view_and_3d": sum(1 for r in ok if r["is_mvblock"]
                                 and r["is_3d"]),
        "usable_3d_by_category": dict(by_cat.most_common()),
        "tier_counts_3d": dict(collections.Counter(r["tier"]
                                                   for r in usable)),
        "gulf_items_present": gaps,
        "name_vs_geometry": mismatch,
        "villa_block_catalog_check": villa,
        "contact_sheet": contact,
        "items_3d": usable,
        "items_not_3d": [{k: r[k] for k in ("file", "tier", "is_mvblock",
                                            "entities_2d")}
                         for r in ok if not r["is_3d"]],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"scanned {len(rows)}, parsed {len(ok)}, 3D {len(usable)}, "
          f"MV blocks {res['multi_view_blocks']}, A-site 3D {len(tier_a)}, "
          f"tiers {res['tier_counts_3d']}")
    print("gulf wants (any file / with 3D):",
          {k: (v["any_file"], v["with_3d_geometry"]) for k, v in gaps.items()})
    print("wrote", OUT)
    return res


if __name__ == "__main__":
    main()
