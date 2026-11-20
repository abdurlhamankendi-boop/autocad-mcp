"""Candidate B plan preview: draws GF (+ annex) and FF from the design data.

Room rectangles with names and NET areas, openings colour-coded (door red,
slide magenta, window blue, open green), furniture footprints, shades and fins
dashed, plot and setback lines, pool, porch, north arrow.
Run from this folder:  python preview_plans.py   ->  preview_GF.png, preview_FF.png
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly, Wedge

import villa_design as V
import villa_furniture_spec as F

ZCOL = {"guest": "#f3d9a4", "family": "#bfe3c0", "service": "#d8d0f0",
        "private": "#f5c6c6", "circ": "#eeeeee"}
OCOL = {V.DOOR: "#d62728", V.SLIDE: "#c000c0", V.WIN: "#1f77b4", V.OPEN: "#2ca02c"}


def draw_geom(ax, g, **kw):
    geoms = g.geoms if hasattr(g, "geoms") else [g]
    for p in geoms:
        if p.is_empty:
            continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc="white", ec="none"))


def draw(floors, fname, title):
    fig, ax = plt.subplots(figsize=(13, 15.5))
    # plot + setbacks
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="k", lw=1.5))
    ax.add_patch(Rectangle((350, 350), V.PLOT_W - 700, V.PLOT_D - 700, fill=False,
                           ec="#999", lw=0.6, ls=":"))
    ax.add_patch(Rectangle((V.SB_SIDE, V.SB_REAR), V.PLOT_W - 2 * V.SB_SIDE,
                           V.PLOT_D - V.SB_FRONT - V.SB_REAR, fill=False, ec="#e67e22",
                           lw=0.8, ls="--"))
    # pool + basin + porch + gate
    ax.add_patch(Rectangle((V.POOL_X0, V.POOL_Y0), V.POOL_X1 - V.POOL_X0,
                           V.POOL_Y1 - V.POOL_Y0, fc="#a8d8f0", ec="#3a7ca5"))
    ax.add_patch(Rectangle((V.POOL_X0 - 100, V.BASIN_Y0), V.POOL_X1 - V.POOL_X0 + 200,
                           V.BASIN_Y1 - V.BASIN_Y0, fc="#cce8f4", ec="#3a7ca5", lw=0.6))
    ax.add_patch(Rectangle((V.PORCH_X0, V.PORCH_Y0), V.PORCH_X1 - V.PORCH_X0,
                           V.PORCH_Y1 - V.PORCH_Y0, fill=False, ec="#555", ls="-.", lw=0.8))
    ax.text((V.PORCH_X0 + V.PORCH_X1) / 2, (V.PORCH_Y0 + V.PORCH_Y1) / 2, "CAR PORCH",
            ha="center", va="center", fontsize=8, color="#555")
    ax.plot([V.GATE_X0, V.GATE_X1], [V.PLOT_D - 175] * 2, color="#d62728", lw=3)
    ax.plot([15400, 16600], [V.PLOT_D - 175] * 2, color="#ff9896", lw=3)

    for fl in floors:
        if fl not in V.floors():
            continue
        ext, part, inner = V.fabric(fl)
        rs = V.rooms_on(fl)
        for r in rs:
            poly = V.net_poly(r)
            draw_geom(ax, poly, fc=ZCOL.get(V.ZONE.get(r[0]), "#fff"), ec="none", alpha=0.9)
        draw_geom(ax, ext, fc="#333", ec="none")
        draw_geom(ax, part, fc="#666", ec="none")
        for r in rs:
            c = V.net_poly(r).representative_point()
            nested = [q for q in rs if q is not r and V.contains(V.rect(q), V.rect(r))]
            fs = 6 if nested or V.A(*V.rect(r)) < 6 else 7
            ax.text(c.x, c.y, f"{r[0]}\n{V.net_area(r):.1f} m2", ha="center",
                    va="center", fontsize=fs, weight="bold", zorder=6)
        for o in V.OPENINGS:
            if o[0] != fl:
                continue
            g = V.void_rect(o)
            draw_geom(ax, g, fc=OCOL[o[1]], ec="none", zorder=5)
            sw = F._swing(o)
            if sw:
                ax.add_patch(MPoly(sw, closed=True, fc="none", ec=OCOL[o[1]], lw=0.6,
                                   zorder=5))
        # furniture
        items = dict(F.BY_FLOOR).get(fl, [])
        for key, x, y, rot in items:
            fp = F.footprint(key, x, y, rot)
            if not fp:
                continue
            ax.add_patch(Rectangle((fp[0], fp[1]), fp[2] - fp[0], fp[3] - fp[1],
                                   fc="#ffffff", ec="#8c564b", lw=0.6, alpha=0.8, zorder=4))
            ax.text((fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2, key.replace("fia_", ""),
                    fontsize=4, ha="center", va="center", color="#8c564b", zorder=4)
    # voids on the drawn upper floor
    for name, x0, y0, x1, y1, fls in V.VOIDS:
        if any(f in fls for f in floors) or name == "LIGHT SLOT":
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#2ca02c",
                                   ls=":", lw=0.8, zorder=6))
            if name != "LIGHT SLOT":
                ax.text((x0 + x1) / 2, y0 + 250, name, fontsize=6, color="#2ca02c",
                        ha="center", zorder=6)
    # stair
    sx0, sy0, sx1, sy1 = V.STAIR
    ax.add_patch(Rectangle((sx0, sy0), sx1 - sx0, sy1 - sy0, fill=False, ec="k",
                           hatch="///", lw=0.6, zorder=6))
    # shades / fins (plan projection)
    for s in V.SHADES:
        ax.add_patch(Rectangle((s[0], s[1]), s[2] - s[0], s[3] - s[1], fill=False,
                               ec="#ff7f0e", ls="--", lw=0.8, zorder=7))
    for f in V.fins():
        ax.add_patch(Rectangle((f[0], f[1]), f[2] - f[0], f[3] - f[1], fc="#ff7f0e",
                               ec="none", alpha=0.6, zorder=7))
    # north arrow
    ax.annotate("N", xy=(1500, 28200), xytext=(1500, 26600), ha="center",
                arrowprops=dict(arrowstyle="-|>", lw=1.5), fontsize=12, weight="bold")
    ax.text(12000, V.PLOT_D + 300, "STREET", ha="center", fontsize=9)
    ax.set_xlim(-500, V.PLOT_W + 500)
    ax.set_ylim(-500, V.PLOT_D + 800)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11)
    ax.grid(True, lw=0.2, color="#ddd")
    ax.set_xticks(range(0, 24001, 3000))
    ax.set_yticks(range(0, 29001, 1000))
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, fname), dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    draw(("AX", "GF"), "preview_GF.png", "Candidate B - ground floor + annex")
    draw(("FF",), "preview_FF.png", "Candidate B - first floor")
    print("wrote preview_GF.png, preview_FF.png")
