"""Prove the pool holds water.

Drops probes down the centre of the pool and reports which solid each one is
inside. The answer must be: water from the floor to top-water level, and
nothing else in the way.

Generic: any pool with a top-water level (POOL_TW) and a floor (a profile,
pool_floor_at, or POOL_FL). A basin or a rill is not assumed -- they only
change what the water volume is expected to exceed -- and a design with a
sun ledge (POOL_LEDGE) is also probed over it (pool_levels()).
"""

import os

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_design as V
import villa_geom as G

OUT = G.out_dir()                   # VILLA_OUT, as every builder
DWG = "VILLA_3D_MODEL.dwg"
R = 200.0

pythoncom.CoInitialize()


def pool_levels():
    """[(name, x, y, z, r, want_water)] -- the probes: down the centre of the
    pool (over the floor where the probe column stands: the floor is a
    profile, V.POOL_FLOOR), water wanted below top-water level; and, for a
    design with a sun ledge, one over the ledge, sized to its water."""
    cx = (V.POOL_X0 + V.POOL_X1) / 2
    cy = (V.POOL_Y0 + V.POOL_Y1) / 2
    fl = V.pool_floor_at(cy) if hasattr(V, "pool_floor_at") else V.POOL_FL
    levels = [("pool floor +100", fl + 250),
              ("mid depth", (fl + V.POOL_TW) / 2),
              ("just below TW", V.POOL_TW - 300),
              ("above the water", V.POOL_TW + 400)]
    out = [(name, cx, cy, z, R, z < V.POOL_TW) for name, z in levels]
    if getattr(V, "POOL_LEDGE", None):
        lx0, ly0, lx1, ly1, lz = V.POOL_LEDGE
        d = V.POOL_TW - lz
        if d > 0:
            out.append(("over the sun ledge", (lx0 + lx1) / 2, (ly0 + ly1) / 2,
                        lz + d / 2, 0.45 * d, True))
    return out


def extra_water():
    """What else the water group holds besides the pool, for the message."""
    return [n for n, has in (("basin", hasattr(V, "BASIN_Y0")),
                             ("rill", hasattr(V, "RILL_W"))) if has]


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

    solids = [(str(e.Layer), as_solid(e)) for e in ms
              if str(e.ObjectName) == "AcDb3dSolid"]
    print(f"{len(solids)} solids\n")

    ok = True
    # the floor is a profile (V.POOL_FLOOR): pool_levels probes over the
    # floor where the probe column stands, not over the deepest level
    for name, cx, cy, z, r, want_water in pool_levels():
        pv = 4.0 / 3.0 * 3.141592653589793 * r ** 3
        hits = []
        for layer, s in solids:
            sph = ms.AddSphere(pt(cx, cy, z), r)
            try:
                res = s.CheckInterference(sph, True)
                inter = res[0] if isinstance(res, tuple) else res
                if inter is not None:
                    v = float(as_solid(inter).Volume) / pv
                    if v > 0.02:
                        hits.append((layer, v))
                    try:
                        inter.Delete()
                    except Exception:
                        pass
            except Exception as exc:
                print(f"   probe failed: {str(exc)[:50]}")
            sph.Delete()
        desc = ", ".join(f"{l} {100 * v:.0f}%" for l, v in hits) or "nothing"
        print(f"  z {z:>6.0f}  {name:16s} -> {desc}")
        got_water = any(l == "L-WATER" for l, _ in hits)
        blocked = [l for l, _ in hits if l not in ("L-WATER",)]
        if want_water and not got_water:
            print("      ! no water here")
            ok = False
        if want_water and blocked:
            print(f"      ! {', '.join(blocked)} is inside the pool")
            ok = False
        if not want_water and got_water:
            print("      ! water above top-water level")
            ok = False

    wat = [s for l, s in solids if l == "L-WATER"]
    if wat:
        vol = sum(float(s.Volume) for s in wat) / 1e9
        expect = (V.pool_volume() if hasattr(V, "pool_volume") else
                  (V.POOL_X1 - V.POOL_X0) * (V.POOL_Y1 - V.POOL_Y0) *
                  (V.POOL_TW - V.POOL_FL) / 1e9)
        extra = extra_water()
        print(f"\n  water volume {vol:.1f} m3   pool alone should be "
              f"{expect:.1f} m3" + (f" (plus {' and '.join(extra)})" if extra else ""))
        # a pool with nothing else in the water group holds exactly its own
        # volume: allow the modeller's rounding (0.01 %), nothing more
        if vol < expect * (1.0 - 1e-4):
            print("      ! less water than the pool holds")
            ok = False

    print("\nVERIFIED: the pool holds water to top-water level" if ok
          else "\nPROBLEMS ABOVE")


if __name__ == "__main__":
    main()
