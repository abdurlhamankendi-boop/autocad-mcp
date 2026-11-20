"""
Villa presentation sheets.

Geometry comes from the build123d model (VILLA_PLAN_*.dxf); this module imports
it into the ezdxf drafting layer and adds what makes it a DRAWING rather than
geometry: poche, room labels with COMPUTED areas, dimension chains, grid, scale
bar, north arrow and title block.

Room areas are computed from the schedule rectangles, never typed in.
"""

from __future__ import annotations

import os

import ezdxf
from ezdxf.addons.importer import Importer

import plan_dxf as pd
import villa_3d as v3

OUT = v3.OUT
pd.OUT = OUT          # Plan.save/render write beside the villa model

# ---- interior schedule. Extents are the CLEAR internal rectangles, taken
#      from the partition layout in villa_3d.py so they cannot drift.
GROUND = [
    ("SHOW KITCHEN",   3400, 18400,  8425, 23600, "habitable"),
    ("ENTRANCE HALL",  8575, 20550, 15425, 23600, "circulation"),
    ("GUEST WC",       8575, 18400, 10400, 20400, "wet"),
    ("WOMEN'S MAJLIS",15575, 18400, 20600, 23600, "habitable"),
    ("FORMAL DINING",  3400, 12900,  7600, 18250, "habitable"),
    ("FAMILY LIVING",  9400, 12900, 14600, 18400, "habitable"),
    ("STUDY",         16400, 12900, 20600, 18250, "habitable"),
]
FIRST = [
    ("BEDROOM 3",      3400, 18400,  8425, 23600, "habitable"),
    ("LANDING",        8575, 18400, 15425, 23600, "circulation"),
    ("MASTER BEDROOM",17750, 18400, 20600, 21600, "habitable"),
    ("DRESSING",      15575, 18400, 17600, 21600, "habitable"),
    ("MASTER ENSUITE",15575, 21750, 20600, 23600, "wet"),
    ("BEDROOM 1",      3400, 12900,  7600, 18250, "habitable"),
    ("BEDROOM 2",     16400, 12900, 20600, 18250, "habitable"),
]
SHEETS = [
    ("A-201", "GROUND FLOOR PLAN", "VILLA_PLAN_GF", GROUND),
    ("A-202", "FIRST FLOOR PLAN",  "VILLA_PLAN_FF", FIRST),
]


def import_geometry(plan, src_path, layer="A-WALL-EXTR"):
    """Copy the model-derived linework in, forcing it onto a drafting layer."""
    src = ezdxf.readfile(src_path)
    imp = Importer(src, plan.doc)
    imp.import_modelspace()
    imp.finalize()
    n = 0
    for e in plan.msp:
        if str(e.dxf.layer) in ("A-CUT", "0"):
            e.dxf.layer = layer
            n += 1
    return n


def sheet(no, title, src, rooms):
    p = pd.Plan(title)
    n = import_geometry(p, os.path.join(OUT, src + ".dxf"))

    # ---- site: pool, basin, rill, porch, boundary. On A-FLOR-OTLN (0.35) --
    #      A-FLOR-PATT is 0.09 and these vanished at plot scale.
    p.box(v3.POOL_X0, v3.POOL_Y0, v3.POOL_X1, v3.POOL_Y1, "A-FLOR-OTLN")
    p.box(v3.POOL_X0 - 400, v3.POOL_Y0 - 1400,
          v3.POOL_X1 + 400, v3.POOL_Y0 - 400, "A-FLOR-OTLN")    # catch basin
    p.box(v3.AXIS - v3.RILL_W / 2, v3.NB_Y1 + 400,
          v3.AXIS + v3.RILL_W / 2, v3.PLOT_D - 700, "A-FLOR-OTLN")   # rill
    p.box(v3.PORCH_X0, v3.PORCH_Y0, v3.PORCH_X1, v3.PORCH_Y1, "A-FLOR-OTLN")
    p.box(0, 0, v3.PLOT_W, v3.PLOT_D, "A-FLOR-OTLN")            # plot boundary

    pw = (v3.POOL_X1 - v3.POOL_X0) / 1000
    pl_ = (v3.POOL_Y1 - v3.POOL_Y0) / 1000
    p.text(f"POOL {pw:.1f} x {pl_:.1f} m", (v3.POOL_X0 + v3.POOL_X1) / 2,
           (v3.POOL_Y0 + v3.POOL_Y1) / 2, 250, "A-ANNO-TEXT",
           align="MIDDLE_CENTER")
    p.text("OVERFLOW EDGE + CATCH BASIN", (v3.POOL_X0 + v3.POOL_X1) / 2,
           v3.POOL_Y0 - 950, 180, "A-ANNO-TEXT", align="MIDDLE_CENTER")
    p.text("REFLECTING RILL ON ENTRANCE AXIS", v3.AXIS + 500,
           v3.PLOT_D - 1800, 180, "A-ANNO-TEXT")
    p.text("COVERED CAR PORCH  2 CARS",
           (v3.PORCH_X0 + v3.PORCH_X1) / 2, (v3.PORCH_Y0 + v3.PORCH_Y1) / 2,
           200, "A-ANNO-TEXT", align="MIDDLE_CENTER")

    # ---- room labels, areas COMPUTED from the schedule
    gia = net = 0.0
    for name, x1, y1, x2, y2, kind in rooms:
        a = (x2 - x1) * (y2 - y1) / 1e6
        net += a
        if kind != "circulation":
            gia += a
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        wd = (x2 - x1) - 400
        p.fit_text(name, cx, cy + 90, 250, "A-ANNO-TEXT", wd, centre=True)
        p.fit_text(f"{a:.1f} m2", cx, cy - 380, 200, "A-ANNO-TEXT", wd,
                   centre=True)

    # ---- dimension chains: overall, then structural
    p.dim_h(v3.HX0, v3.HX1, 0, 2200)          # building width, outside the plot
    p.dim_h(0, v3.PLOT_W, 0, 3600)            # plot width, further out
    p.dim_v(v3.WG_Y0 - v3.CANT, v3.NB_Y1, 0, 2200)
    p.dim_v(0, v3.PLOT_D, 0, 3600)

    # ---- structural grid on the setting-out lines
    p.grid([v3.HX0, v3.LV_X0, v3.LV_X1, v3.HX1],
           [v3.WG_Y0, v3.NB_Y0, v3.NB_Y1],
           0, v3.PLOT_W, 0, v3.PLOT_D)

    p.north(v3.PLOT_W + 3200, v3.PLOT_D - 2200)
    p.scale_bar(0, -6800)
    p.title_block(no, title, gia,
                  project="PRIVATE VILLA  |  4 BEDROOM  |  696 m2 PLOT")
    return p, n, gia, net


if __name__ == "__main__":
    for no, title, src, rooms in SHEETS:
        p, n, gia, net = sheet(no, title, src, rooms)
        base = f"{no}_{title.replace(' ', '_')}"
        p.save(base)
        png = p.render(base, dpi=170)
        print(f"{no}  {title:20s} imported {n:4d} entities   "
              f"net {net:6.1f} m2   habitable {gia:6.1f} m2")
    print("")
    print("output:", OUT)
