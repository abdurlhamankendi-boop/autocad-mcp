"""Plan previews for candidate C, drawn from the DATA only (no AutoCAD).

    python preview_plans.py   ->  preview_GF.png, preview_FF.png, preview_site.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, FancyArrow

import villa_design as V
import villa_furniture_spec as F

HERE = os.path.dirname(os.path.abspath(__file__))
ZC = {"circ": "#f2f2f2", "guest": "#f7e3c6", "family": "#dcebd5",
      "private": "#d9e2f3", "service": "#e6dcef"}
OC = {V.DOOR: "#c0392b", V.SLIDE: "#1f77b4", V.WIN: "#17becf", V.OPEN: "#7f7f7f"}


def draw_geom(ax, g, **kw):
    geoms = g.geoms if hasattr(g, "geoms") else [g]
    for p in geoms:
        if p.is_empty:
            continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc="white",
                               ec="none"))


def site(ax, floor):
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="k",
                           lw=1.2))
    # boundary wall 350
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, 350, fc="#bbbbbb", ec="none"))
    ax.add_patch(Rectangle((0, V.PLOT_D - 350), V.PLOT_W, 350, fc="#bbbbbb",
                           ec="none"))
    ax.add_patch(Rectangle((0, 0), 350, V.PLOT_D, fc="#bbbbbb", ec="none"))
    ax.add_patch(Rectangle((V.PLOT_W - 350, 0), 350, V.PLOT_D, fc="#bbbbbb",
                           ec="none"))
    # gates (gaps drawn white)
    for x0, x1, lab in ((V.GATE_X0, V.GATE_X1, "vehicle gate"),
                        (*V.GUEST_GATE, "guest gate"),
                        (*V.SERVICE_GATE, "service gate")):
        ax.add_patch(Rectangle((x0, V.PLOT_D - 350), x1 - x0, 350, fc="white",
                               ec="k", lw=0.6))
        ax.text((x0 + x1) / 2, V.PLOT_D + 250, lab, ha="center", fontsize=6)
    # setback line
    ax.add_patch(Rectangle((V.SB_SIDE, V.SB_REAR),
                           V.PLOT_W - 2 * V.SB_SIDE,
                           V.PLOT_D - V.SB_FRONT - V.SB_REAR, fill=False,
                           ec="#d62728", ls=(0, (6, 4)), lw=0.8))
    # porch
    ax.add_patch(Rectangle((V.PORCH_X0, V.PORCH_Y0), V.PORCH_X1 - V.PORCH_X0,
                           V.PORCH_Y1 - V.PORCH_Y0, fill=False, ec="#8c564b",
                           ls="--", lw=0.9))
    ax.text((V.PORCH_X0 + V.PORCH_X1) / 2, V.PORCH_Y1 - 700,
            f"CAR PORCH {V.PORCH_X1 - V.PORCH_X0:.0f} wide", ha="center",
            fontsize=6, color="#8c564b")
    for cx in (V.PORCH_X0 + 300, V.PORCH_X0 + 3000):
        ax.add_patch(Rectangle((cx, V.PORCH_Y0 + 400), 1900, 4800, fill=False,
                               ec="#8c564b", lw=0.5))
    # pool
    shell, cuts, water = V.pool_parts()
    for (x0, y0, z0, x1, y1, z1) in shell:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#dddddd",
                               ec="#999999", lw=0.4))
    ax.add_patch(Rectangle((V.POOL_X0, V.POOL_Y0), V.POOL_X1 - V.POOL_X0,
                           V.POOL_Y1 - V.POOL_Y0, fc="#9ecae1", ec="#3182bd"))
    ax.add_patch(Rectangle((V.POOL_X0 - 100, V.BASIN_Y0 + V.BASIN_WALL),
                           V.POOL_X1 - V.POOL_X0 + 200,
                           V.BASIN_Y1 - V.BASIN_Y0 - V.BASIN_WALL,
                           fc="#c6dbef", ec="#3182bd", lw=0.5))
    ax.text(V.AXIS, (V.POOL_Y0 + V.POOL_Y1) / 2, "POOL", ha="center",
            fontsize=8, color="#08519c")
    # external steps
    for (x0, y0, z0, x1, y1, z1) in V.external_steps():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#fff5cc",
                               ec="#b8860b", lw=0.4))
    # service-yard wall (drawn, not modelled): pool garden | service yard
    ax.plot([16300, 16300], [350, 11000], color="#555555", lw=2.0)
    ax.plot([21000, 21000], [23100, V.PLOT_D - 350], color="#555555", lw=2.0)
    ax.text(18500, 10200, "SERVICE YARD", ha="center", fontsize=6)
    ax.text(22350, 18000, "service\npassage", ha="center", fontsize=6,
            rotation=90)
    ax.text(6000, 6000, "POOL GARDEN", ha="center", fontsize=8,
            color="#2ca02c")


def plan(floor, out, extra_floors=()):
    fig, ax = plt.subplots(figsize=(12, 14.5))
    site(ax, floor)
    for fl in (floor,) + tuple(extra_floors):
        if fl not in V.floors():
            continue
        ext, part, inner = V.fabric(fl)
        draw_geom(ax, ext, fc="#444444", ec="none")
        draw_geom(ax, part, fc="#888888", ec="none")
        for r in V.rooms_on(fl):
            g = V.net_poly(r)
            draw_geom(ax, g, fc=ZC.get(V.ZONE.get(r[0]), "white"), ec="none")
        for r in V.rooms_on(fl):
            g = V.net_poly(r)
            c = g.representative_point()
            cx, cy = (r[1] + r[3]) / 2, (r[2] + r[4]) / 2
            if not g.contains(type(c)(cx, cy)):
                cx, cy = c.x, c.y
            ax.text(cx, cy, f"{r[0]}\n{V.net_area(r):.1f} m2", ha="center",
                    va="center", fontsize=6.3, weight="bold")
        for o in V.OPENINGS:
            if o[0] != fl:
                continue
            g = V.void_rect(o)
            draw_geom(ax, g, fc=OC[o[1]], ec="none")
            sw = F._swing(o)
            if sw:
                ax.add_patch(MPoly(sw, closed=True, fill=False, ec="#c0392b",
                                   lw=0.4))
        # furniture
        items = dict(F.BY_FLOOR).get(fl, [])
        for key, x, y, rot in items:
            fp = F.footprint(key, x, y, rot)
            if fp is None:
                continue
            ax.add_patch(Rectangle((fp[0], fp[1]), fp[2] - fp[0],
                                   fp[3] - fp[1], fill=False, ec="#6b4226",
                                   lw=0.5))
            ax.text((fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2,
                    key.replace("fia_", ""), ha="center", va="center",
                    fontsize=3.6, color="#6b4226")
    # the stair (dog-leg: two flights side by side, half-landing north)
    sx0, sy0, sx1, sy1 = V.STAIR
    mid = (sx0 + sx1) / 2
    ax.add_patch(Rectangle((sx0, sy0), sx1 - sx0, sy1 - sy0, fill=False,
                           ec="k", lw=0.6))
    run = (V.RISERS / V.STAIR_FLIGHTS - 1) * V.STAIR_GOING
    for i in range(int(V.RISERS / V.STAIR_FLIGHTS)):
        y = sy0 + i * V.STAIR_GOING
        ax.plot([sx0, sx1], [y, y], color="k", lw=0.3)
    ax.plot([mid, mid], [sy0, sy0 + run], color="k", lw=0.6)
    ax.text(mid, sy0 - 250, "UP" if floor == "GF" else "DN", ha="center",
            fontsize=6)
    # voids on this floor
    for name, x0, y0, x1, y1, fls in V.VOIDS:
        if floor in fls:
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                   ec="#555555", hatch="xx", lw=0.4))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 - 900, name, ha="center",
                    fontsize=6, style="italic")
    # shades and fins
    for (x0, y0, x1, y1, z0, z1) in V.SHADES:
        lvl = "GF" if z0 < V.FF else "FF"
        if lvl == floor:
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                   ec="#2ca02c", ls="--", lw=0.8))
    for (x0, y0, x1, y1, z0, z1) in V.fins():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                               ec="#2ca02c", ls="--", lw=0.4))
    # north arrow
    ax.add_patch(FancyArrow(22800, 26000, 0, 1600, width=150, head_width=600,
                            head_length=600, color="k"))
    ax.text(22800, 25400, "N", ha="center", fontsize=10, weight="bold")
    ax.text(12000, 29900, "STREET", ha="center", fontsize=9)
    ax.set_xlim(-600, V.PLOT_W + 600)
    ax.set_ylim(-600, V.PLOT_D + 1300)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, 24001, 3000))
    ax.set_yticks(range(0, 29001, 1000))
    ax.tick_params(labelsize=6)
    ax.grid(True, lw=0.2, alpha=0.4)
    gfa = V.gross_area()
    ax.set_title(f"Candidate C - {floor} plan"
                 + (" + annex" if extra_floors else "")
                 + f"   (GFA {gfa:.1f} m2)", fontsize=11)
    handles = [plt.Rectangle((0, 0), 1, 1, fc=c) for c in ZC.values()]
    handles += [plt.Rectangle((0, 0), 1, 1, fc=c) for c in OC.values()]
    ax.legend(handles, list(ZC) + ["door", "slide", "window", "open"],
              loc="lower right", fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, out), dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    plan("GF", "preview_GF.png", extra_floors=("AX",))
    plan("FF", "preview_FF.png")
    print("written preview_GF.png, preview_FF.png")
