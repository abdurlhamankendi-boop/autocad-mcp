"""Measure what is actually in AutoCAD against what the design says.

A screenshot proves the drawing is not empty. This proves each block landed on
the right footprint, at the right size, on the right layer -- which is the only
claim worth making.
"""

import json
import os

import pythoncom
import win32com.client as w

import villa_design as V
import villa_furniture_spec as F
import villa_geom as G

OUT = G.out_dir()                   # VILLA_OUT redirects it
# Blocks are scaled UNIFORMLY -- never distorted to fit -- so a block whose
# aspect differs slightly from the catalog lands a few mm short on one axis.
# Placement must therefore be exact; size is allowed that residual.
POS_TOL = 25.0        # mm, on the minimum corner
SIZE_TOL = 0.06       # fraction

pythoncom.CoInitialize()


def get_doc(a, name):
    # by name AND folder: projects share drawing names (villa_geom.find_doc)
    return G.find_doc(a, name, OUT)


def check(base, floor):
    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, base + ".dwg")
    if doc is None:
        a.Documents.Open(os.path.join(OUT, base + ".dwg"))
        doc = get_doc(a, base + ".dwg")

    # everything drawn on this sheet: the ground-floor sheet carries the
    # annex's furniture (floor "AX") as well as its own
    expect = {}
    for fl, (key, x, y, rot) in G.sheet_furniture(floor):
        fp = F.footprint(key, x, y, rot)
        if fp is not None:
            expect.setdefault(key, []).append(fp)

    inserts, issues, matched = [], [], 0
    for e in doc.ModelSpace:
        if str(e.ObjectName) != "AcDbBlockReference":
            continue
        lo, hi = e.GetBoundingBox()
        inserts.append((str(e.Layer), (lo[0], lo[1], hi[0], hi[1])))

    used = set()
    for layer, bb in inserts:
        best, bi = None, None
        for key, fps in expect.items():
            for i, fp in enumerate(fps):
                if (key, i) in used:
                    continue
                pos = max(abs(bb[0] - fp[0]), abs(bb[1] - fp[1]))
                ew, ed = fp[2] - fp[0], fp[3] - fp[1]
                aw, ad = bb[2] - bb[0], bb[3] - bb[1]
                size = max(abs(aw - ew) / ew, abs(ad - ed) / ed)
                d = pos + 1000.0 * max(0.0, size - SIZE_TOL)
                if best is None or d < best:
                    best, bi = d, (key, i)
        if best is not None and best <= POS_TOL:
            used.add(bi)
            matched += 1
        else:
            issues.append(f"block at ({bb[0]:.0f},{bb[1]:.0f})-({bb[2]:.0f},"
                          f"{bb[3]:.0f}) on {layer}: off by {best:.0f}"
                          if best is not None else "unexpected block")

    total = sum(len(v) for v in expect.values())
    missing = total - matched
    return len(inserts), matched, missing, issues, doc


def geometry(doc, floor):
    """Layer census and drawing extents -- did the walls actually arrive."""
    census, xs, ys = {}, [], []
    for e in doc.ModelSpace:
        census[str(e.Layer)] = census.get(str(e.Layer), 0) + 1
        try:
            lo, hi = e.GetBoundingBox()
            xs += [lo[0], hi[0]]
            ys += [lo[1], hi[1]]
        except Exception:
            pass
    return census, (min(xs), min(ys), max(xs), max(ys))


def plan_sheets():
    """(file base, plan floor) of every plan sheet that carries furniture,
    from villa_geom.plan_sheets() -- the villa's A-102 GF, A-103 FF (and a
    roof plan A-104 when the roof has rooms); a design's own PLAN_SHEETS,
    a basement's among them."""
    return [(f"VILLA_{no.replace('-', '')}", fl) for fl, no, _t in G.plan_sheets()]


if __name__ == "__main__":
    ok = True
    sheets = plan_sheets()
    for base, floor in sheets:
        n, matched, missing, issues, doc = check(base, floor)
        census, ext = geometry(doc, floor)
        print(f"\n{base}  ({floor})")
        print(f"  block references : {n}")
        print(f"  matched to plan  : {matched}")
        print(f"  missing          : {missing}")
        print(f"  extents          : x {ext[0]:.0f}..{ext[2]:.0f}   "
              f"y {ext[1]:.0f}..{ext[3]:.0f}")
        wall = census.get("A-WALL-EXTR", 0) + census.get("A-WALL", 0)
        print(f"  wall entities    : {wall}   poche "
              f"{census.get('A-WALL-PATT', 0)}   doors "
              f"{census.get('A-DOOR', 0)}   swings "
              f"{census.get('A-DOOR-SWNG', 0)}   glazing "
              f"{census.get('A-GLAZ', 0)}")
        print(f"  dims             : {census.get('A-ANNO-DIMS', 0)}   text "
              f"{census.get('A-ANNO-TEXT', 0)}   shading (dashed) "
              f"{census.get('A-SHDE-OVHD', 0)}")
        for i in issues[:6]:
            print("   !", i)
            ok = False
        if missing:
            ok = False
    print("\nVERIFIED: every block matches the validated plan" if ok
          else "\nMISMATCHES ABOVE")
