"""Build aia_layers.json: the ACA AIA(256) layer key + the villa pipeline's
layer names mapped onto it.

Deterministic and read-only:
  * parses C:\\ProgramData\\Autodesk\\ACA 2027\\enu\\Layers\\AIA(256).ly (CSV)
  * greps the villa scripts for layer-name string literals (file:line)
  * reads the layer tables of the villa DXF sheets with ezdxf (never writes)
  * maps every villa name to the key: exact (case-insensitive) or via the
    MAP table below, each mapping with its reason

Output: C:\\Users\\lsire\\.claude\\skills\\architectural-cad\\references\\aia_layers.json
"""

from __future__ import annotations

import csv
import glob
import hashlib
import io
import json
import os
import re

LY = r"C:\ProgramData\Autodesk\ACA 2027\enu\Layers\AIA(256).ly"
PROJECT = r"C:\Users\lsire\autocad-mcp"
SCRIPTS = ["plan_dxf.py", "villa_cad.py", "villa_colour.py",
           "villa_3d_build.py", "villa_load.py"]
DXF_GLOB = r"C:\Users\lsire\OneDrive\Desktop\Villa\VILLA_A10*.dxf"
OUT = (r"C:\Users\lsire\.claude\skills\architectural-cad\references"
       r"\aia_layers.json")

# NCS / AIA CAD Layer Guidelines name form: discipline(1-2) - major(4)
# [- minor(4)]* . Used only as a SYNTAX check; the key file is the authority.
NCS_FORM = re.compile(r"^[A-Z]{1,2}-[A-Z0-9]{4}(-[A-Z0-9]{4})*$")
SHEET_NO = re.compile(r"^[A-Z]{1,2}-\d{2,4}[A-Z]?$")   # A-101, A-102P
HATCH = re.compile(r"^AR-")                            # acad.pat names

# villa name -> (AIA(256) key name, reason). Only for names that do NOT
# match a key row case-insensitively.
MAP = {
    "A-WALL-EXTR": ("A-Wall", "key has one A-Wall row; EXTR (exterior) is an "
                    "NCS minor modifier, keep as a declared extension"),
    "A-WALL-PATT": ("A-Wall", "wall poche/hatch; PATT modifier is used by the "
                    "ACA samples (A-Area-Patt, A-Area-Spce-Patt) but not in "
                    "this key"),
    "A-WALL-FILL": ("A-Wall", "solid poche; rename to A-WALL-PATT (FILL is "
                    "not a modifier any sample or the key uses)"),
    "A-FLOR-OTLN": ("(none)", "no key row for a floor/building outline; "
                    "declare as extension"),
    "A-FLOR-PATT": ("A-Flor-Iden", "floor-finish hatch: the key's finish row "
                    "is A-Flor-Iden (FINFLOOR, finish tags); hatch itself has "
                    "no row -> A-FLOR-PATT as declared extension"),
    "A-FLOR-FILL": ("A-Flor-Iden", "coloured floor finish fill; rename to "
                    "A-FLOR-PATT"),
    "A-FLOR-FIXT": ("A-Flor-Pfix + A-Flor-Appl", "SPLIT: sanitaryware (wc, "
                    "basin, bath, sink) -> A-Flor-Pfix (PFIXT); hob, fridge, "
                    "dishwasher -> A-Flor-Appl (APPL)"),
    "A-DOOR-SWNG": ("A-Door", "swing arcs belong to the door; no separate key "
                    "row. Keep as extension for lineweight control"),
    "A-FURN-FILL": ("A-Furn", "presentation fill of furniture; extension"),
    "A-ROOF-FILL": ("A-Roof", "roof outline fill on plans"),
    "A-ANNO-TEXT": ("A-Anno-Note / A-Area-Iden", "general notes -> "
                    "A-Anno-Note (ANNOBJ); ROOM NAMES AND AREAS are room tags "
                    "-> A-Area-Iden (ROOMNO)"),
    "S-GRID": ("A-Grid", "the key is architectural only: column grids are "
               "A-Grid (GRIDLINE, Center2) with bubbles on A-Grid-Iden"),
    "A-WALL-3D": ("A-Wall", "3D solid of walls; '3D' breaks the 4-char field "
                  "form"),
    "A-SLAB-3D": ("(none)", "no slab row in AIA(256).ly; ACA's AecLayerStd.dwg "
                  "has more keys but needs AutoCAD to read"),
    "A-ROOF-3D": ("A-Roof", "roof solid"),
    "A-SHDE-3D": ("(none)", "shading fins/pergola: no key row"),
    "A-SHDE-OVHD": ("(none)", "overhead shading drawn dashed on plans "
                    "(villa_cad.py SHADE_LAYER); no key row. OVHD fits the "
                    "4-char field form; declare as extension"),
    "A-POOL-3D": ("A-Site", "pool shell is site work in this key"),
    "A-BDRY-3D": ("A-Site", "boundary wall is site work in this key"),
    "A-BASE-3D": ("A-Wall", "stone plinth/base course"),
    "L-SITE-LAWN": ("A-Plnt", "planting in this key is A-Plnt (PLANTS)"),
    "L-SITE-PLNT": ("A-Plnt", "planting beds"),
    "L-SITE-TREE": ("A-Plnt", "trees are outdoor plants (PLANTS)"),
    "L-SITE-GRVL": ("A-Site", "hard landscape"),
    "L-SITE-PAVE": ("A-Site", "hard landscape"),
    "L-SITE-DRIV": ("A-Site / A-Pkng", "drive; parking symbols are A-Pkng"),
    "L-SITE-DECK": ("A-Site", "hard landscape"),
    "L-SITE-WATR": ("A-Site", "pool water / rill; no water row"),
    "L-TERRAIN": ("A-Site", "3D ground; name breaks the 4-char field form"),
    "L-LAWN": ("A-Plnt", "3D name disagrees with 2D L-SITE-LAWN"),
    "L-PLANT": ("A-Plnt", "3D name disagrees with 2D L-SITE-PLNT"),
    "L-GRAVEL": ("A-Site", "3D name disagrees with 2D L-SITE-GRVL"),
    "L-PAVE": ("A-Site", "3D name disagrees with 2D L-SITE-PAVE"),
    "L-DECK": ("A-Site", "3D name disagrees with 2D L-SITE-DECK"),
    "L-DRIVE": ("A-Site", "3D name disagrees with 2D L-SITE-DRIV"),
    "L-WATER": ("A-Site", "3D name disagrees with 2D L-SITE-WATR"),
    "L-GLAZ": ("A-Glaz", "WRONG DISCIPLINE: building window panes on a "
               "landscape (L-) layer"),
    "L-DOOR": ("A-Door", "WRONG DISCIPLINE: building door leaves on a "
               "landscape (L-) layer"),
}


def parse_ly(path):
    raw = open(path, "rb").read()
    text = raw.decode("latin-1")
    meta, fields, rows, group = {}, [], [], None
    for ln, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("*"):
            if line.startswith("*FIELD:"):
                fields.append(line[7:].split(",")[0])
            elif ":" in line:
                k, v = line[1:].split(":", 1)
                meta[k] = v.rstrip(",")
            else:
                meta.setdefault("comments", []).append(line[1:])
            continue
        if line.startswith("~"):
            group = line[1:].rstrip(",")
            continue
        cols = next(csv.reader(io.StringIO(line)))
        desc, key, name, colour, ltype = cols[:5]
        rows.append({"line": ln, "group": group, "description": desc,
                     "key": key, "layer": name, "layer_upper": name.upper(),
                     "aci": int(colour), "linetype": ltype,
                     "bits": [int(c) for c in cols[5:10] if c.strip()]})
    return meta, fields, rows, hashlib.sha256(raw).hexdigest()


def grep_scripts():
    lit = re.compile(r"""["']([A-Z]{1,2}-[A-Z0-9]+(?:-[A-Z0-9]+)*)["']""")
    names, sheets = {}, {}
    for f in SCRIPTS:
        p = os.path.join(PROJECT, f)
        for ln, line in enumerate(open(p, encoding="utf-8"), 1):
            for m in lit.finditer(line):
                s = m.group(1)
                if SHEET_NO.match(s):
                    sheets.setdefault(s, []).append(f"{f}:{ln}")
                elif HATCH.match(s):
                    continue
                else:
                    names.setdefault(s, []).append(f"{f}:{ln}")
    return names, sheets


def dxf_layers():
    import ezdxf
    out = {}
    for p in sorted(glob.glob(DXF_GLOB)):
        doc = ezdxf.readfile(p)
        used = {e.dxf.layer for e in doc.modelspace()}
        for lay in doc.layers:
            n = lay.dxf.name
            if n in ("0", "Defpoints"):
                continue
            out.setdefault(n, {"in": [], "entities_in": []})
            out[n]["in"].append(os.path.basename(p))
            if n in used:
                out[n]["entities_in"].append(os.path.basename(p))
    return out


def main():
    meta, fields, rows, sha = parse_ly(LY)
    by_upper = {r["layer_upper"]: r for r in rows}
    names, sheets = grep_scripts()
    dxf = dxf_layers()
    allnames = sorted(set(names) | set(dxf))
    villa, nonstd = [], []
    for n in allnames:
        rec = {"name": n, "sources": names.get(n, []),
               "dxf_tables": dxf.get(n, {}).get("in", []),
               "dxf_with_entities": dxf.get(n, {}).get("entities_in", []),
               "ncs_form": bool(NCS_FORM.match(n))}
        if n.upper() in by_upper:
            r = by_upper[n.upper()]
            rec.update(status="in_key", aia_layer=r["layer"], aia_key=r["key"],
                       aia_aci=r["aci"], note="matches key (case differs only)"
                       if r["layer"] != n else "exact")
        elif n in MAP:
            tgt, why = MAP[n]
            keys = [by_upper[t.strip().upper()]["key"]
                    for t in re.split(r"[/+]", tgt)
                    if t.strip().upper() in by_upper]
            rec.update(status="not_in_key", aia_layer=tgt, aia_key=keys,
                       note=why)
            nonstd.append(n)
        else:
            rec.update(status="unmapped", aia_layer=None, aia_key=[],
                       note="no mapping written; add to MAP")
            nonstd.append(n)
        villa.append(rec)
    result = {
        "generated_by": os.path.join(PROJECT, "reference", "examples",
                                     "aia_layers.py"),
        "source": LY, "source_sha256": sha, "source_meta": meta,
        "source_fields": fields,
        "row_count": len(rows),
        "note": ("ACA layer key 'AIA (256 Color)'. Names are mixed case in the "
                 "key; AutoCAD layer names are case-insensitive, so compare "
                 "upper-cased. UNITS:Imperial in the header refers to the key "
                 "file, not to the drawings."),
        "layers": rows,
        "villa": {
            "scripts_scanned": SCRIPTS,
            "dxf_scanned": sorted(os.path.basename(p)
                                  for p in glob.glob(DXF_GLOB)),
            "names": villa,
            "non_standard": nonstd,
            "sheet_numbers_found": sheets,
        },
        "validator_rules": [
            "every layer in a villa DXF must be in_key (case-insensitive) or in "
            "a declared extension list; unmapped names fail",
            "no L- (landscape) layer may carry building elements "
            "(glazing, doors): discipline must match the element",
            "the same element must have the same layer in 2D and 3D "
            "(L-SITE-LAWN vs L-LAWN is a failure)",
            "sanitaryware on A-FLOR-PFIX, appliances on A-FLOR-APPL "
            "(key rows PFIXT / APPL)",
            "room names/areas on A-AREA-IDEN, door tags on A-DOOR-IDEN, "
            "window tags on A-GLAZ-IDEN, schedules on A-ANNO-LEGN",
            "layer names follow D-MMMM[-mmmm]* (4-char fields); '3D', "
            "'TERRAIN', 'GRAVEL' style fields fail the form check",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    print(f"key rows: {len(rows)}  villa names: {len(villa)}  "
          f"in key: {sum(v['status'] == 'in_key' for v in villa)}  "
          f"not in key: {len(nonstd)}  unmapped: "
          f"{sum(v['status'] == 'unmapped' for v in villa)}")
    print("wrote", OUT)
    return result


if __name__ == "__main__":
    main()
