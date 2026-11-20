"""Plan preview of candidate A, drawn from the design DATA only.

python preview.py  ->  preview_GF.png (with the annex), preview_FF.png
"""
from __future__ import annotations

import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Arc, FancyArrow

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import villa_design as V            # noqa: E402
import villa_furniture_spec as F    # noqa: E402

COL = {V.DOOR: "#d62728", V.SLIDE: "#2ca02c", V.WIN: "#1f77b4", V.OPEN: "#ff7f0e"}
ZCOL = {"circ": "#f2f2f2", "guest": "#fde9c9", "family": "#dff0d8",
        "private": "#e3e0f5", "service": "#f3d9d9", None: "#ffffff"}


def draw_geom(ax, g, **kw):
    if g.is_empty:
        return
    geoms = g.geoms if hasattr(g, "geoms") else [g]
    for p in geoms:
        if p.geom_type != "Polygon":
            continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc="white",
                               ec=kw.get("ec", "none"), lw=kw.get("lw", 0)))


def draw_floor(floors, fname, title):
    fig, ax = plt.subplots(figsize=(13, 15.5))
    ax.set_aspect("equal")
    # plot + setbacks
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="k", lw=1.5))
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="#999",
                           lw=6, alpha=0.25))            # boundary wall 350
    ax.add_patch(Rectangle((V.SB_SIDE, V.SB_REAR), V.PLOT_W - 2 * V.SB_SIDE,
                           V.PLOT_D - V.SB_FRONT - V.SB_REAR, fill=False,
                           ec="#888", ls=(0, (6, 4)), lw=0.8))
    ax.text(V.SB_SIDE + 100, V.PLOT_D - V.SB_FRONT + 120, "setback", fontsize=6,
            color="#888")
    ax.text(V.PLOT_W / 2, V.PLOT_D + 250, "STREET (north)", ha="center", fontsize=9)
    if "GF" in floors:
        # pool, basin, porch, gate
        ax.add_patch(Rectangle((V.POOL_X0, V.POOL_Y0), V.POOL_X1 - V.POOL_X0,
                               V.POOL_Y1 - V.POOL_Y0, fc="#bde0f6", ec="#3a87c8"))
        ax.add_patch(Rectangle((V.POOL_X0 - 100, V.BASIN_Y0), V.POOL_X1 - V.POOL_X0 + 200,
                               V.BASIN_Y1 - V.BASIN_Y0, fc="#d7ecfa", ec="#3a87c8",
                               ls="--"))
        ax.text((V.POOL_X0 + V.POOL_X1) / 2, (V.POOL_Y0 + V.POOL_Y1) / 2, "POOL",
                ha="center", color="#3a87c8")
        ax.add_patch(Rectangle((V.PORCH_X0, V.PORCH_Y0), V.PORCH_X1 - V.PORCH_X0,
                               V.PORCH_Y1 - V.PORCH_Y0, fill=False, ec="#8c564b",
                               ls="-.", lw=1.2))
        ax.text(V.PORCH_X0 + 150, V.PORCH_Y1 - 400, "CAR PORCH", fontsize=7,
                color="#8c564b")
        ax.plot([V.GATE_X0, V.GATE_X1], [V.PLOT_D - 175, V.PLOT_D - 175], color="#8c564b",
                lw=5)
        for x0, y0, z0, x1, y1, z1 in V.external_steps():
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                   ec="#777", lw=0.5, hatch="///"))
    # voids
    for name, x0, y0, x1, y1, fl in V.VOIDS:
        if any(f in fl for f in floors) or (not fl and "GF" in floors):
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                   ec="#aaa", hatch="xx", lw=0.3))
    # underlay: the GF outline on FF
    if "FF" in floors:
        draw_geom(ax, V.outline("GF"), fc="none", ec="#bbb", lw=0.8, ls="--")
    for fl in floors:
        ext, part, inner = V.fabric(fl)
        draw_geom(ax, ext, fc="#333", ec="#333", lw=0.3)
        draw_geom(ax, part, fc="#777", ec="#777", lw=0.2)
        for r in V.rooms_on(fl):
            np_ = V.net_poly(r)
            draw_geom(ax, np_, fc=ZCOL.get(V.ZONE.get(r[0])), ec="none", lw=0)
        for r in V.rooms_on(fl):
            np_ = V.net_poly(r)
            c = np_.representative_point()
            x0, y0, x1, y1 = V.rect(r)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if not np_.contains(__import__("shapely.geometry", fromlist=["Point"]).Point(cx, cy)):
                cx, cy = c.x, c.y
            fs = 7 if (x1 - x0) > 2500 else 5.5
            ax.text(cx, cy, f"{r[0]}\n{V.net_area(r):.1f} m2\n{(x1-x0)/1000:.2f}x{(y1-y0)/1000:.2f}",
                    ha="center", va="center", fontsize=fs, color="#222",
                    zorder=6, bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.5))
        # furniture
        items = dict(F.BY_FLOOR).get(fl, [])
        for key, x, y, rot in items:
            fp = F.footprint(key, x, y, rot)
            if fp is None:
                continue
            ax.add_patch(Rectangle((fp[0], fp[1]), fp[2] - fp[0], fp[3] - fp[1],
                                   fc="#c9b28f", ec="#6b5530", lw=0.5, alpha=0.8,
                                   zorder=4))
            ax.text((fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2,
                    key.replace("fia_", ""), fontsize=3.5, ha="center",
                    va="center", zorder=5, rotation=90 if (fp[3]-fp[1]) > 1.6*(fp[2]-fp[0]) else 0)
        # openings
        for o in V.OPENINGS:
            if o[0] != fl:
                continue
            flo, kind, axis, t0, t1, a, b, ra, rb, sw = o
            g = V.void_rect(o)
            x0, y0, x1, y1 = g.bounds
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=COL[kind],
                                   ec=COL[kind], lw=0.5, zorder=7))
            pts = F._swing(o)
            if pts:
                xs, ys = zip(*pts)
                ax.plot(xs + (xs[0],), ys + (ys[0],), color=COL[kind], lw=0.5,
                        zorder=7)
    # stair: two flights running north from the hall, half-landing at the north
    if "GF" in floors or "FF" in floors:
        sx0, sy0, sx1, sy1 = V.STAIR
        mid = (sx0 + sx1) / 2
        land = 1100.0
        ax.add_patch(Rectangle((sx0, sy0), sx1 - sx0, sy1 - sy0, fill=False,
                               ec="#444", lw=0.8, zorder=6))
        ax.add_patch(Rectangle((sx0, sy1 - land), sx1 - sx0, land, fill=False,
                               ec="#444", lw=0.5, zorder=6))
        n = V.RISERS // V.STAIR_FLIGHTS - 1
        for i in range(1, n + 1):
            y = sy0 + i * V.STAIR_GOING
            ax.plot([sx0, sx1], [y, y], color="#666", lw=0.3, zorder=6)
        ax.plot([mid, mid], [sy0, sy1 - land], color="#444", lw=0.6, zorder=6)
        ax.annotate("", xy=(mid + 500, sy1 - land - 100), xytext=(mid + 500, sy0 + 100),
                    arrowprops=dict(arrowstyle="->", lw=0.6), zorder=6)
        ax.text(mid, sy0 - 180, "UP" if "GF" in floors else "DN", fontsize=5,
                ha="center", zorder=6)
    # shades & fins
    zlo = min(V.LEVEL[f] for f in floors)
    zhi = max(V.LEVEL[f] + V.CEIL[f] for f in floors)
    for s in V.SHADES:
        ax.add_patch(Rectangle((s[0], s[1]), s[2] - s[0], s[3] - s[1], fill=False,
                               ec="#9467bd", ls="--", lw=0.9, zorder=8))
    for f in V.fins():
        if f[5] < zlo or f[4] > zhi:
            continue
        ax.add_patch(Rectangle((f[0], f[1]), f[2] - f[0], f[3] - f[1], fill=False,
                               ec="#9467bd", ls="--", lw=0.6, zorder=8))
    # north arrow
    ax.add_patch(FancyArrow(22500, 1500, 0, 1400, width=120, head_width=500,
                            head_length=500, color="k"))
    ax.text(22500, 3600, "N", ha="center", fontsize=12, weight="bold")
    # legend
    y = 500
    for k, c in COL.items():
        ax.add_patch(Rectangle((500, y), 600, 250, fc=c))
        ax.text(1200, y, k, fontsize=7)
        y += 400
    ax.set_xlim(-500, V.PLOT_W + 500)
    ax.set_ylim(-500, V.PLOT_D + 700)
    ax.set_xticks(range(0, 24001, 3000))
    ax.set_yticks(range(0, 29001, 3000))
    ax.tick_params(labelsize=6)
    ax.grid(True, lw=0.2, color="#ddd")
    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    out = os.path.join(HERE, fname)
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


if __name__ == "__main__":
    fl = V.floors()
    gf = ["AX", "GF"] if "AX" in fl else ["GF"]
    print(draw_floor(gf, "preview_GF.png", "Candidate A - ground floor" + (" + annex" if "AX" in fl else "")))
    print(draw_floor(["FF"], "preview_FF.png", "Candidate A - first floor"))
