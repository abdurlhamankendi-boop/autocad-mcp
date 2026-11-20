"""Prove the windows and doors are actually cut through the walls.

A void that is exactly coincident with both wall faces is a boolean edge case:
the solid modeller can leave a zero-thickness skin, so the plan shows a window
and the model shows solid masonry. Probe the middle of every opening.

Every wall-like layer is asked (villa_geom.WALL_LAYERS_3D: the render walls
A-WALL-3D, a stone skin A-STON-3D, the basement's walls A-BASE-3D), not only
A-WALL-3D: a basement door is cut in A-BASE-3D, and an opening whose stone
skin was left standing would read "cut" from the walls alone. A probe at the
wall's centre cannot reach a 50 mm skin on its outer face either, so every
opening is also probed just inside each face of the wall (probe_points()).
"""

import os

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_design as V
import villa_geom as G

OUT = G.out_dir()
DWG = "VILLA_3D_MODEL.dwg"
R = 120.0
SKIN_R = 20.0          # the face probes: 5 mm in from each face of the wall
WALL_LAYERS = tuple(getattr(G, "WALL_LAYERS_3D", ("A-WALL-3D",)))

pythoncom.CoInitialize()


def probe_points():
    """[(tag, x, y, z, r)] -- every point that must be clear of every
    wall-like layer: the middle of every opening (and its floor for a door,
    a sliding door or an opening -- a window's cut would not reach it), at
    the wall's centre with R; and at mid-height, SKIN_R + 5 in from each face
    of the wall with SKIN_R -- where a 50 mm stone skin stands."""
    out = []
    for o in V.OPENINGS:
        fl, kind, axis, t0, t1, aa, bb, ra, rb, sw = o
        x0, y0, lo, x1, y1, hi = G.cut_box(o)      # V.opening_z, every floor
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tag = (f"{fl} {kind:6s} {str(ra)[:18]:18s}-> "
               f"{str(rb or 'outside')[:16]:16s}")
        # the middle of every opening; and a door, sliding door or opening
        # must also be cut down to its floor (a window's cut would not be)
        heights = [("mid", (lo + hi) / 2)]
        if kind != V.WIN:
            heights.append(("floor", lo + R + 30))
        for where, cz in heights:
            out.append((f"{tag} {where}", cx, cy, cz, R))
        d = SKIN_R + 5.0
        faces = (((cx, y0 + d), (cx, y1 - d)) if axis == "h"
                 else ((x0 + d, cy), (x1 - d, cy)))
        for k, (fx, fy) in enumerate(faces):
            out.append((f"{tag} face {k}", fx, fy, (lo + hi) / 2, SKIN_R))
    return out


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def as_solid(e):
    try:
        return w.CastTo(e, "IAcad3DSolid")
    except Exception:
        return e


def get_doc(a, name):
    # by name AND folder: projects share drawing names (villa_geom.find_doc)
    return G.find_doc(a, name, OUT)


def main():
    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, DWG)
    if doc is None:
        a.Documents.Open(os.path.join(OUT, DWG))
        doc = get_doc(a, DWG)
    ms = doc.ModelSpace

    # Openings are cut from the wall-like groups. Since the material split the
    # building is no longer one solid on layer 0: it is A-WALL-3D, a stone
    # skin A-STON-3D over it, the basement's walls A-BASE-3D (WALL_LAYERS).
    # Glass panes (L-GLAZ) sit in the holes on purpose and are not masonry,
    # so skip them. Every solid on those layers is asked, not the first
    # found: the annex's walls may arrive as a solid of their own.
    walls = [as_solid(e) for e in ms
             if str(e.ObjectName) == "AcDb3dSolid" and str(e.Layer) in WALL_LAYERS]
    if not walls:
        print(f"no wall solid on layers {', '.join(WALL_LAYERS)}")
        return

    blocked, open_ = [], []

    def solid_frac(cx, cy, cz, r=R):
        pv = 4.0 / 3.0 * 3.141592653589793 * r ** 3
        sph = ms.AddSphere(pt(cx, cy, cz), r)
        frac = 0.0
        try:
            for model in walls:
                res = model.CheckInterference(sph, True)
                inter = res[0] if isinstance(res, tuple) else res
                if inter is not None:
                    frac += float(as_solid(inter).Volume) / pv
                    try:
                        inter.Delete()
                    except Exception:
                        pass
        except Exception as exc:
            # Fail CLOSED: a probe that could not be asked is not a hole. This
            # used to leave frac at 0.0 and count the opening as cut through.
            print("   probe failed:", str(exc)[:50])
            frac = 1.0
        sph.Delete()
        return frac

    pts = probe_points()
    for tag, cx, cy, cz, r in pts:
        frac = solid_frac(cx, cy, cz, r)
        (blocked if frac > 0.05 else open_).append((tag, frac))
    n = len(pts)

    print(f"{len(V.OPENINGS)} openings, {n} probes on {', '.join(WALL_LAYERS)} "
          f"(centre; floor for doors and sliding doors; 5 mm in from each face)\n")
    print(f"  cut through : {len(open_)}")
    print(f"  still solid : {len(blocked)}")
    for tag, frac in blocked[:20]:
        print(f"     {tag}   {100 * frac:.0f}% solid")
    print("\nVERIFIED: every opening is a real hole" if not blocked
          else "\nOPENINGS ABOVE ARE NOT CUT")


if __name__ == "__main__":
    main()
