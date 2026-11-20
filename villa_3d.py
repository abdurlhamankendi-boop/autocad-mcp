"""
VILLA — 3D model; plans, elevations and sections are CUT FROM the model.

Modelling once and deriving every drawing means plan, section and elevation
cannot disagree. That was the structural weakness of the earlier house project.

Units: millimetres (build123d is unitless; MM == 1).

BRIEF: 4 bedrooms. Women's majlis only (no men's dewaniya) — which frees ~40 m2
and is most of the gap the research found between a full luxury programme
(480-620 m2 net) and the 418 m2 / 4,500 sq ft brief.

--------------------------------------------------------------------------
DESIGN BASIS — see VILLA_RESEARCH.md for sources. Three research findings
drove this scheme, each overturning the first attempt:

1.  A CLASSIC INFINITY EDGE CANNOT WORK HERE. It needs a 1.2-1.8 m drop to
    terrain beyond; on a flat plot inside a stone wall it spills toward a wall
    5 m away and reads as nothing. So the pool is RAISED 700 mm above the
    garden and overflows one long side as a waterwall into a visible basin.
    That also lifts the shell clear of the 45-degree load-spread zone of the
    boundary-wall footing.

2.  THE LUXURY PROGRAMME DOES NOT FIT 418 m2. Resolved the F.LOT way: staff,
    laundry, store and all plant go into a SEMI-BASEMENT lit by a sunken
    courtyard, which is what makes a basement a served space not a cellar.

3.  ALHAMBRA, COURT OF THE MYRTLES is 23.5 x 36.6 m with a 34.0 x 7.10 m pool.
    This plot is 24 x 29 m -- almost exactly the Myrtles' width. The axis is
    therefore carried the LONG way by a 500 mm rill (Casa Merida: an
    uninterrupted perspective from the entrance door to the pool), terminating
    in the swimming pool proper at 12.0 x 4.0 m.

Further moves, each with its researched dimension:
  * Ground floor raised 900 mm (Interlude House) - the cheapest privacy device
    on an urban plot: a passer-by's sightline hits the ceiling, not the sofa.
  * 3.0 m cantilever over the pool (Interlude; Eurocode 2 sweet spot 2.5-3.5 m
    in RC) shading the water's edge.
  * Double-height living volume - "3.3 m+ or 4.5-6.0 m double-height =
    ultra-luxury".
  * Two 1.0 m light slots between the wings and the central volume (AGi Wall
    House: patios developed three-dimensionally).
  * Threshold compression at a 2.4 m soffit releasing into the tall volume,
    past the 1:2.2 ratio needed for the release to register.
  * West brise-soleil fins - east/west CANNOT be shaded by horizontals.
  * Three entrances (Gulf discipline): guest on the axis, family via the
    garage, service on the east boundary reaching the dirty kitchen without
    crossing guest or family space.
"""

from __future__ import annotations

import os
import time

from build123d import (Box, Part, Plane, Pos, Rectangle, Kind, offset, extrude,
                       section, Unit, export_step)
from build123d.exporters import Drawing, ExportDXF, ColorIndex, LineType
import ezdxf

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ site
PLOT_W, PLOT_D = 24000.0, 29000.0          # 696 m2 = 7,492 sq ft
SB_FRONT, SB_SIDE, SB_REAR = 5000.0, 3000.0, 3000.0

# ------------------------------------------------------------------ levels
STREET = 0.0
GF = 900.0                                  # raised half a level for privacy
GF_CH = 3600.0
SLAB = 500.0                                # incl. services zone
FF = GF + GF_CH + SLAB                      # 5000
FF_CH = 3200.0
RF = FF + FF_CH + SLAB                      # 8700
PARAPET = 1100.0
PAV_CH = 3000.0
BASE_FL = -2800.0                           # semi-basement floor

WALL = 400.0                                # thick external wall, deep reveals

# ------------------------------------------------------------------ plan grid
# One setting-out grid: every wall, slot and opening lands on it.
HX0, HX1 = 3000.0, 21000.0                  # 18.0 m between side setbacks
NB_Y0, NB_Y1 = 18000.0, 24000.0             # north bar (garage, entry, service)
WG_Y0, WG_Y1 = 12500.0, 18000.0             # wings + central volume
WW_X0, WW_X1 = 3000.0, 8000.0               # west wing
EW_X0, EW_X1 = 16000.0, 21000.0             # east wing
LV_X0, LV_X1 = 9000.0, 15000.0              # living volume (double height)

AXIS = 12000.0                              # the water axis, dead centre
RILL_W = 500.0

POOL_X0, POOL_X1 =  9500.0, 14500.0         # 5.0 m wide
POOL_Y0, POOL_Y1 = 3000.0, 12500.0          # 9.5 m long
POOL_TW = 700.0                             # top water level, above garden
POOL_FL = -700.0                            # -> 1.4 m constant depth
BASIN_D = 900.0                             # catch basin / balance chamber

CANT = 3000.0                               # first-floor cantilever over pool

BS_X0, BS_X1 = 3000.0, 21000.0              # semi-basement
BS_Y0, BS_Y1 = 15000.0, 24000.0
CT_X0, CT_X1 = 9500.0, 14500.0              # sunken courtyard 5.0 x 4.0
CT_Y0, CT_Y1 = 15400.0, 19400.0

PV = (9000.0, 19000.0, 15000.0, 24000.0)    # roof pavilion 6.0 x 5.0

# covered car porch in the front setback (2 cars, 7.0 x 5.2)
PORCH_X0, PORCH_X1 = 3500.0, 10500.0
PORCH_Y0, PORCH_Y1 = 24400.0, 28400.0


def blk(x0, y0, z0, x1, y1, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def area(x0, y0, x1, y1):
    return abs(x1 - x0) * abs(y1 - y0) / 1e6


def build():
    t0 = time.perf_counter()
    S, V = [], []                            # solids, voids -> batched booleans

    # ============================================================ basement
    S.append(blk(BS_X0, BS_Y0, BASE_FL - 400, BS_X1, BS_Y1, BASE_FL))
    S.append(blk(BS_X0, BS_Y0, BASE_FL, BS_X1, BS_Y1, GF - SLAB))
    V.append(blk(BS_X0 + WALL, BS_Y0 + WALL, BASE_FL,
                 BS_X1 - WALL, BS_Y1 - WALL, GF - SLAB))
    V.append(blk(CT_X0, CT_Y0, BASE_FL, CT_X1, CT_Y1, GF + 200))

    # ============================================================ ground
    # Built from the UNION footprint, inset once. Four separate boxes butted
    # together gave two 400 walls back to back at every junction -- an 800 mm
    # internal wall. Offsetting the merged face yields one connected interior.
    GF_FOOT = ((HX0, NB_Y0, HX1, NB_Y1), (WW_X0, WG_Y0, WW_X1, WG_Y1),
               (EW_X0, WG_Y0, EW_X1, WG_Y1), (LV_X0, WG_Y0, LV_X1, WG_Y1))
    FF_FOOT = ((HX0, NB_Y0, HX1, NB_Y1), (WW_X0, WG_Y0, WW_X1, WG_Y1),
               (EW_X0, WG_Y0, EW_X1, WG_Y1),
               (LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + WALL))

    def shell(rects, z0, z1, t=WALL):
        fp = None
        for x0, y0, x1, y1 in rects:
            r = Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)
            fp = r if fp is None else fp + r
        ring = fp - offset(fp, -t, kind=Kind.INTERSECTION)
        return (Pos(0, 0, z0) * extrude(ring, z1 - z0),
                Pos(0, 0, z0) * extrude(fp, z1 - z0), fp)

    walls_gf, mass_gf, fp_gf = shell(GF_FOOT, GF, GF + GF_CH)
    S.append(walls_gf)
    S.append(Pos(0, 0, GF - SLAB) * extrude(fp_gf, SLAB))          # ground slab

    # ============================================================ first
    walls_ff, mass_ff, fp_ff = shell(FF_FOOT, FF, RF)
    S.append(walls_ff)
    S.append(Pos(0, 0, GF + GF_CH) * extrude(fp_ff, SLAB))         # first slab
    # the living volume stays open through both storeys
    V.append(blk(LV_X0 + WALL, WG_Y0, GF + GF_CH, LV_X1 - WALL, WG_Y1, FF))

    # ============================================================ roof
    S.append(blk(HX0, WG_Y0 - CANT, RF, HX1, NB_Y1, RF + SLAB))
    S.append(blk(HX0, WG_Y0 - CANT, RF + SLAB, HX1, NB_Y1, RF + SLAB + PARAPET))
    V.append(blk(HX0 + 250, WG_Y0 - CANT + 250, RF + SLAB,
                 HX1 - 250, NB_Y1 - 250, RF + SLAB + PARAPET))
    S.append(blk(PV[0], PV[1], RF + SLAB, PV[2], PV[3], RF + SLAB + PAV_CH))
    V.append(blk(PV[0] + 250, PV[1] + 250, RF + SLAB,
                 PV[2] - 250, PV[3] - 250, RF + SLAB + PAV_CH))

    # ---- light slots, cut AFTER the masses so they read through every level
    V.append(blk(WW_X1, WG_Y0 - 300, GF - SLAB, LV_X0, WG_Y1 + 300,
                 RF + SLAB + PARAPET))
    V.append(blk(LV_X1, WG_Y0 - 300, GF - SLAB, EW_X0, WG_Y1 + 300,
                 RF + SLAB + PARAPET))

    # ============================================================ interior
    # Family living on the GROUND floor, all four bedrooms above.
    # Ground zoning follows the comb: each wing hangs off the north-bar zone
    # directly above it, so kitchen sits over dining, hall over the
    # double-height living volume, majlis over the study.
    P = 150.0                                  # stud partition
    DH = 2700.0                                # full-height doors at ground

    PARTS_GF = [
        (8425, 18400, 8575, 23600),            # kitchen | hall
        (15425, 18400, 15575, 23600),          # hall | majlis
        (10400, 18400, 10550, 20400),          # guest WC, east wall
        (8575, 20400, 10550, 20550),           # guest WC, north wall
        (3400, 18250, 7600, 18400),            # kitchen | formal dining
        (16400, 18250, 20600, 18400),          # majlis | study
    ]
    DOORS_GF = [
        (8425, 21500, 8575, 22700),            # hall -> kitchen
        (15425, 20500, 15575, 21700),          # hall -> majlis
        (10400, 19000, 10550, 19900),          # hall -> guest WC
        (5000, 18250, 6200, 18400),            # kitchen -> dining
        (17800, 18250, 19000, 18400),          # majlis -> study
    ]
    # NOTE: the living volume is deliberately left OPEN to the hall. That is
    # the compression-release: 2.40 m entry soffit into 7.30 m clear.

    PARTS_FF = [
        (8425, 18400, 8575, 23600),            # guest 3 | landing
        (15425, 18400, 15575, 23600),          # landing | master
        (17600, 18400, 17750, 21600),          # master dressing
        (15575, 21600, 20600, 21750),          # master en-suite
        (3400, 18250, 7600, 18400),            # guest 3 | guest 1
        (16400, 18250, 20600, 18400),          # master | guest 2
    ]
    DOORS_FF = [
        (8425, 21500, 8575, 22700),            # landing -> guest 3
        (15425, 20200, 15575, 21400),          # landing -> master
        (17600, 19600, 17750, 20500),          # master -> dressing
        (16200, 21600, 17400, 21750),          # master -> en-suite
        (5000, 18250, 6200, 18400),            # guest 3 -> guest 1
        (17800, 18250, 19000, 18400),          # master -> guest 2
    ]

    for x0, y0, x1, y1 in PARTS_GF:
        S.append(blk(x0, y0, GF, x1, y1, GF + GF_CH))
    for x0, y0, x1, y1 in DOORS_GF:
        V.append(blk(x0 - 60, y0 - 60, GF, x1 + 60, y1 + 60, GF + DH))
    for x0, y0, x1, y1 in PARTS_FF:
        S.append(blk(x0, y0, FF, x1, y1, RF))
    for x0, y0, x1, y1 in DOORS_FF:
        V.append(blk(x0 - 60, y0 - 60, FF, x1 + 60, y1 + 60, FF + 2400))

    # stair, hall to landing, against the east wall of the hall
    for i in range(16):
        S.append(blk(13000, 18700 + i * 170, GF + i * 244,
                     14600, 18870 + i * 170, GF + (i + 1) * 244))
    V.append(blk(13000, 18700, GF + GF_CH, 14600, 21900, FF))   # stair void

    # ============================================================ openings
    V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 300, GF + 100,
                 LV_X1 - 200, WG_Y0 + 300, GF + 3400))     # structural glazing
    V.append(blk(LV_X0 + 200, WG_Y0 - 300, FF + 300,
                 LV_X1 - 200, WG_Y0 + WALL + 300, FF + 2900))
    for x0, x1 in ((4200.0, 6800.0), (17200.0, 19800.0)):
        V.append(blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + 300, GF + 3100))
        V.append(blk(x0, WG_Y0 - 300, FF + 450, x1, WG_Y0 + 300, FF + 2700))
    for xx in (HX0, HX1 - 500):                            # clerestory band
        V.append(blk(xx - 100, NB_Y0 + 800, RF - 900,
                     xx + 600, NB_Y1 - 800, RF - 250))
    V.append(blk(AXIS - 750, NB_Y1 - 300, GF, AXIS + 750,
                 NB_Y1 + 300, GF + 2400))                  # guest entrance
    # Car porch, not an enclosed garage: the north bar is 5.2 m deep
    # internally and a two-car garage needs 5.5-6.5 m. A covered porch in the
    # front setback is the Gulf norm and is often excluded from BUA.
    for x0 in (3600.0, 6900.0):
        S.append(blk(x0, PORCH_Y0, GF + 2900, x0 + 250, PORCH_Y1, GF + 3150))
    S.append(blk(PORCH_X0, PORCH_Y0, GF + 3150, PORCH_X1, PORCH_Y1, GF + 3350))
    S.append(blk(PORCH_X1 - 250, PORCH_Y0, GF, PORCH_X1, PORCH_Y1, GF + 3150))
    V.append(blk(HX1 - 300, NB_Y0 + 700, GF, HX1 + 300,
                 NB_Y0 + 1800, GF + 2400))                 # service entrance

    # ============================================================ west fins
    for i in range(9):
        yy = WG_Y0 + 300 + i * 600
        S.append(blk(HX0 - 700, yy, GF, HX0 - 250, yy + 180, RF))

    # ============================================================ water
    S.append(blk(POOL_X0 - 400, POOL_Y0 - 400, POOL_FL - 400,
                 POOL_X1 + 400, POOL_Y1 + 400, POOL_TW))
    V.append(blk(POOL_X0, POOL_Y0, POOL_FL, POOL_X1, POOL_Y1, POOL_TW + 100))
    V.append(blk(POOL_X0 - 400, POOL_Y0 - 1400, STREET - BASIN_D,
                 POOL_X1 + 400, POOL_Y0 - 400, POOL_TW - 60))   # spill + basin
    S.append(blk(POOL_X0, POOL_Y1 - 2200, POOL_FL, POOL_X1,
                 POOL_Y1, POOL_TW - 300))                       # Baja shelf
    S.append(blk(AXIS - RILL_W / 2 - 250, NB_Y1 + 400, STREET - 400,
                 AXIS + RILL_W / 2 + 250, PLOT_D - 700, STREET + 150))
    V.append(blk(AXIS - RILL_W / 2, NB_Y1 + 400, STREET - 300,
                 AXIS + RILL_W / 2, PLOT_D - 700, STREET + 200))

    # ============================================================ boundary
    BW, BH = 350.0, 2400.0
    S.append(blk(0, 0, STREET, PLOT_W, BW, BH))
    S.append(blk(0, PLOT_D - BW, STREET, PLOT_W, PLOT_D, BH))
    S.append(blk(0, 0, STREET, BW, PLOT_D, BH))
    S.append(blk(PLOT_W - BW, 0, STREET, PLOT_W, PLOT_D, BH))
    V.append(blk(3800, PLOT_D - BW - 200, STREET, 8300, PLOT_D + 200, BH))
    V.append(blk(15400, PLOT_D - BW - 200, STREET, 16600, PLOT_D + 200, 2200))

    model = (Part() + S) - V                 # batched: 13-42x a sequential loop

    nb = area(HX0, NB_Y0, HX1, NB_Y1)
    ww = area(WW_X0, WG_Y0, WW_X1, WG_Y1)
    ew = area(EW_X0, WG_Y0, EW_X1, WG_Y1)
    lv = area(LV_X0, WG_Y0, LV_X1, WG_Y1)
    ct = area(LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0)
    pav = area(*PV)
    gf, ff = nb + ww + ew + lv, nb + ww + ew + ct
    gfa = gf + ff + pav
    base = area(BS_X0, BS_Y0, BS_X1, BS_Y1) - area(CT_X0, CT_Y0, CT_X1, CT_Y1)
    plot = PLOT_W * PLOT_D / 1e6
    pool = area(POOL_X0, POOL_Y0, POOL_X1, POOL_Y1)

    print(f"  model      {time.perf_counter() - t0:.3f}s  "
          f"faces={len(model.faces())}  volume={model.volume / 1e9:.0f} m3")
    print(f"  ground {gf:6.1f}   first {ff:6.1f}   roof {pav:5.1f}")
    print(f"  GFA        {gfa:.0f} m2 = {gfa * 10.7639:.0f} sq ft"
          f"   (brief 418 m2 / 4,500 sq ft)")
    print(f"  basement   {base:.0f} m2 excl. sunken court "
          f"({area(CT_X0, CT_Y0, CT_X1, CT_Y1):.0f} m2)")
    print(f"  footprint  {gf:.0f} m2   site coverage {100 * gf / plot:.0f}%")
    print(f"  pool       {(POOL_X1 - POOL_X0) / 1000:.1f} x "
          f"{(POOL_Y1 - POOL_Y0) / 1000:.1f} m = {pool:.0f} m2 "
          f"({100 * pool / plot:.1f}% of plot; research target ~10%)")
    print(f"  DH volume  {(RF - SLAB - GF) / 1000:.2f} m clear; entry soffit "
          f"2.40 m -> compression ratio 1:{(RF - SLAB - GF) / 2400:.1f} "
          f"(needs >=1:2.2)")
    print(f"  cantilever {CANT / 1000:.1f} m (RC sweet spot 2.5-3.5 m)")
    return model


def render_dxf(path, png, dpi=150):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, LineweightPolicy
    doc = ezdxf.readfile(path)
    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ctx = RenderContext(doc)
    lp = ctx.current_layout_properties
    lp.set_colors(bg="#FFFFFF")          # else ACI 7 draws white on white
    Frontend(ctx, MatplotlibBackend(ax),
             config=Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE)
             ).draw_layout(doc.modelspace(), finalize=True, layout_properties=lp)
    fig.savefig(png, dpi=dpi, facecolor="white")
    plt.close(fig)


def new_dxf():
    d = ExportDXF(version=ezdxf.DXF2013, unit=Unit.MM,
                  color=ColorIndex.BLACK, line_weight=0.25,
                  line_type=LineType.CONTINUOUS)
    d.add_layer("A-CUT", color=ColorIndex.BLACK, line_weight=0.70)
    d.add_layer("A-ELEV", color=ColorIndex.BLACK, line_weight=0.35)
    return d


def derive(model):
    files = []
    # No "beyond" projection: the build123d reference warned it reproduces the
    # cut outline itself and swamps the drawing.
    for tag, z in (("BASEMENT", BASE_FL + 1200), ("GF", GF + 1200),
                   ("FF", FF + 1200), ("ROOF", RF + SLAB + 550)):
        t = time.perf_counter()
        cut = Pos(0, 0, -z) * section(model, Plane.XY, height=z)
        if not cut:
            print(f"  plan {tag:9s} EMPTY at z={z:.0f}")
            continue
        d = new_dxf(); d.add_shape(cut, layer="A-CUT")
        f = os.path.join(OUT, f"VILLA_PLAN_{tag}.dxf"); d.write(f); files.append(f)
        print(f"  plan {tag:9s} z={z:7.0f}  {time.perf_counter() - t:.3f}s")

    for tag, look in (("S", (0, -1, 0)), ("N", (0, 1, 0)),
                      ("E", (1, 0, 0)), ("W", (-1, 0, 0))):
        t = time.perf_counter()
        dr = Drawing(model, look_from=look, look_up=(0, 0, 1), with_hidden=False)
        d = new_dxf(); d.add_shape(dr.visible_lines, layer="A-ELEV")
        f = os.path.join(OUT, f"VILLA_ELEV_{tag}.dxf"); d.write(f); files.append(f)
        print(f"  elev {tag:9s} {time.perf_counter() - t:.3f}s")

    # ---- perspectives. An orthographic elevation cannot carry a scheme whose
    #      subject is depth: the cantilever, the slots and the water axis only
    #      read when the view has convergence.
    for tag, eye, foc in (
            ("AERIAL_SW", (-26000.0, -30000.0, 26000.0), 70000.0),
            ("POOL_EYE",  (12000.0, -14000.0, 2600.0), 34000.0),
            ("AERIAL_NE", (46000.0, 54000.0, 30000.0), 90000.0)):
        t = time.perf_counter()
        vis, _ = model.project_to_viewport(viewport_origin=eye,
                                           viewport_up=(0, 0, 1),
                                           look_at=(12000.0, 13000.0, 3000.0),
                                           focus=foc)
        d = new_dxf(); d.add_shape(vis, layer="A-ELEV")
        f = os.path.join(OUT, f"VILLA_VIEW_{tag}.dxf"); d.write(f); files.append(f)
        print(f"  view {tag:9s} {len(vis):4d} edges  "
              f"{time.perf_counter() - t:.3f}s")

    # long section on the water axis: gate -> rill -> house -> pool
    t = time.perf_counter()
    pl = Plane(origin=(AXIS, 0, 0), z_dir=(1, 0, 0), x_dir=(0, 1, 0))
    sec = section(model, pl)
    d = new_dxf(); d.add_shape(pl.to_local_coords(sec), layer="A-CUT")
    f = os.path.join(OUT, "VILLA_SECTION_AA.dxf"); d.write(f); files.append(f)
    print(f"  section AA  {time.perf_counter() - t:.3f}s")
    return files


if __name__ == "__main__":
    m = build()
    export_step(m, os.path.join(OUT, "villa.step"))
    files = derive(m)
    print("")
    print("rendering...")
    for f in files:
        try:
            render_dxf(f, f.replace(".dxf", ".png"))
        except Exception as exc:
            print("   render failed:", os.path.basename(f), str(exc)[:60])
    print("")
    print("output:", OUT)
