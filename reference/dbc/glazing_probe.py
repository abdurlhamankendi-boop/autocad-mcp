"""Read-only: list external SLIDE/DOOR/WIN openings with the level outside them (for K.7.6.2).

Imports villa_design and prints numbers. No AutoCAD, no writes.
"""
import sys

sys.path.insert(0, r"C:\Users\lsire\autocad-mcp")
import villa_design as V  # noqa: E402
from shapely.geometry import Point  # noqa: E402

gf_out = V.outline("GF")
print("floors", V.floors(), "LEVEL", V.LEVEL)
for o in V.OPENINGS:
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    if rb is not None or kind not in (V.SLIDE, V.WIN, V.DOOR):
        continue
    w0, w1 = min(t0, t1), max(t0, t1)
    mid = (a + b) / 2
    f = V.facing(o)
    # a point 600 mm outside the wall face
    if axis == "h":
        px, py = mid, (w1 + 600 if f == "N" else w0 - 600)
    else:
        px, py = (w1 + 600 if f == "E" else w0 - 600), mid
    p = Point(px, py)
    below = None
    if fl == "FF":
        on_gf_roof = gf_out.contains(p)
        below = "GF roof (terrace?) at %.0f" % (V.GF + V.GF_CH + V.SLAB) if on_gf_roof else "ground %.0f" % V.ground_at(py)
    else:
        below = "ground %.0f" % V.ground_at(py)
    z0, z1 = V.opening_z(o)
    print(f"{fl} {kind:6s} {ra:18s} face {f} w {abs(b-a):5.0f}  z {z0:.0f}-{z1:.0f}  outside: {below}")
print("SHADES", getattr(V, "SHADES", None))
print("BALCONIES", [n for n in dir(V) if "BALC" in n.upper() or "TERR" in n.upper()])
