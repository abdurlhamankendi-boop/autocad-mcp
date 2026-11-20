"""Prove the 3D model is hollow where the plans say it is hollow.

Volume alone would pass a solid block of the right size. Instead, drop a small
probe sphere at the centre of every room and ask AutoCAD for the interference
with the model: a room must return zero, a wall must return the whole probe.
"""

import os

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_design as V
import villa_geom as G

OUT = G.out_dir()
DWG = os.path.join(OUT, "VILLA_3D_MODEL.dwg")
R = 250.0                       # probe radius, mm

pythoncom.CoInitialize()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def get_doc(a, name):
    # by name AND folder: projects share drawing names (villa_geom.find_doc)
    return G.find_doc(a, name, OUT)


def as_solid(e):
    """ModelSpace hands back IAcadEntity; the 3D-solid methods live on
    IAcad3DSolid, so cast before asking for Volume or CheckInterference."""
    try:
        return w.CastTo(e, "IAcad3DSolid")
    except Exception:
        return e


def main():
    # Entities read back off ModelSpace arrive as generic IAcadEntity from the
    # type-library cache, with no Volume and no CheckInterference. Going
    # late-bound gives the real interface. The first version of this file also
    # swallowed the resulting AttributeError and scored every probe as "void",
    # so it reported 19/19 rooms open on a model it had never actually read.
    a = w.dynamic.Dispatch(w.GetActiveObject("AutoCAD.Application"))
    doc = get_doc(a, os.path.basename(DWG))
    if doc is None:
        a.Documents.Open(DWG)
        doc = get_doc(a, os.path.basename(DWG))
    ms = doc.ModelSpace

    # The building is split into material groups (A-WALL-3D, A-SLAB-3D, ...),
    # one solid per layer. Probing only the first solid found meant the slab,
    # roof and boundary probes asked the WALL solid and read 0% -- and the
    # rooms were only ever proved clear of walls, not of slabs. Probe them all.
    model = [as_solid(e) for e in ms
             if str(e.ObjectName) == "AcDb3dSolid"
             and str(e.Layer).startswith("A-") and str(e.Layer).endswith("-3D")]
    if not model:
        print("no building solids (A-*-3D) in the drawing")
        return

    probe_vol = 4.0 / 3.0 * 3.141592653589793 * R ** 3
    voids, solids, bad = [], [], []

    def probe(x, y, z, r=R):
        s = ms.AddSphere(pt(x, y, z), r)
        v = 0.0
        for m in model:
            res = m.CheckInterference(s, True)
            inter = res[0] if isinstance(res, tuple) else res
            if inter is not None:
                inter = as_solid(inter)
                v += float(inter.Volume)
                try:
                    inter.Delete()
                except Exception:
                    pass
        pv = 4.0 / 3.0 * 3.141592653589793 * r ** 3
        s.Delete()
        return v / pv

    # The design's own probes (villa_design.probes, extended by
    # villa_geom.probes): every room open, the double height open to the
    # roof, the first-floor slab over every ground-floor room, the
    # single-storey band closed; the annex's slab, roof, parapet and wall; every
    # sliding door cut to the floor and the head; every shade and a fin solid.
    # villa_gltf.py asks the render model the same questions.
    design = G.probes()
    for name, x, y, z, expect, rr in design:
        f = probe(x, y, z, rr)
        ok = f < 0.02 if expect == "void" else f > 0.9
        (voids if ok else bad).append((name, f"{expect.upper()} expected", f))

    # a point inside the external wall must be SOLID
    # Each control carries its own probe radius: an element thinner than the
    # probe loses its spherical caps and can never read 100%. They are DERIVED
    # (villa_geom.controls) -- typed coordinates would read "void" the day the
    # street face moves, and the forecourt fix will move it.
    CONTROLS = G.controls()
    for name, x, y, z, rr in CONTROLS:
        f = probe(x, y, z, rr)
        (solids if f > 0.9 else bad).append((name, "SOLID expected", f))

    print(f"probe radius {R:.0f} mm\n")
    print(f"design probes   : {len(voids)}/{len(design)} as designed")
    print(f"fabric solid    : {len(solids)}/{len(CONTROLS)}")
    if bad:
        print(f"\n{len(bad)} FAILURE(S):")
        for a_, b_, f in bad:
            print(f"   {a_:28s} {b_:16s} filled {100 * f:5.1f}%")
    else:
        print("\nVERIFIED: every void is open and every solid probe is solid")


def _busy(exc):
    """AutoCAD refused the call (busy), as villa_3d_build.busy / villa_load.busy."""
    t = str(exc).lower()
    return ("rejected" in t or "-2147418111" in t or "busy" in t
            or (isinstance(exc, AttributeError)
                and ("autocad.application" in t or t.startswith("<unknown>."))))


if __name__ == "__main__":
    import time
    for attempt in range(6):
        try:
            main()
            break
        except Exception as exc:          # noqa: BLE001 -- only a busy AutoCAD is retried
            if not _busy(exc) or attempt == 5:
                raise
            print(f"  AutoCAD busy, retrying ({attempt + 1})...")
            time.sleep(6)
