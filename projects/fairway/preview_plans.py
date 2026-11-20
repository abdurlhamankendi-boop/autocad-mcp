"""Fairway plan preview: B1, GF (with the site) and FF from the design data.

Rooms filled by zone with name and NET area, walls and partitions, openings
coloured (door red, slide magenta, window blue, open green) with door swings,
furniture footprints, voids and stairs (treads), shades / overhangs dashed,
fins, guards, pool, surfaces, gates, plot and setback lines.
Run:  python ..\\..\\run_project.py fairway preview_plans.py
      -> preview_B1.png, preview_GF.png, preview_FF.png (this folder)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle

import villa_design as V
import villa_furniture_spec as F

ZCOL = {"guest": "#f3d9a4", "family": "#bfe3c0", "service": "#d8d0f0",
        "private": "#f5c6c6", "circ": "#eeeeee"}
OCOL = {V.DOOR: "#d62728", V.SLIDE: "#c000c0", V.WIN: "#1f77b4", V.OPEN: "#2ca02c"}
SCOL = {"lawn": "#cfe8b8", "beds": "#9cc587", "terrace": "#ece6d8", "deck": "#d9b48f",
        "path": "#e2dccb", "drive": "#d6d3cd", "mulch": "#ebe5d6",
        "poolsurround": "#f1ece0"}


def geom(ax, g, **kw):
    for p in getattr(g, "geoms", [g]):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc="white", ec="none",
                               zorder=kw.get("zorder", 1)))


def draw(fl, fname, site=False):
    fig, ax = plt.subplots(figsize=(12.5, 16))
    ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="k", lw=1.4))
    ax.add_patch(Rectangle((V.SB_SIDE, V.SB_REAR), V.PLOT_W - 2 * V.SB_SIDE,
                           V.PLOT_D - V.SB_FRONT - V.SB_REAR, fill=False, ec="#e67e22",
                           lw=0.8, ls="--"))
    if site:
        S = V.ground_surfaces()
        for k, c in SCOL.items():
            if k in S:
                geom(ax, S[k], fc=c, ec="none", zorder=0.5)
        x0, y0, x1, y1 = V.pool_shell_rect()
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#f1ece0", ec="#888", lw=0.5))
        ax.add_patch(Rectangle((V.POOL_X0, V.POOL_Y0), V.POOL_X1 - V.POOL_X0,
                               V.POOL_Y1 - V.POOL_Y0, fc="#7ec8e3", ec="#2a6f97", zorder=1))
        lx0, ly0, lx1, ly1, _ = V.POOL_LEDGE
        ax.add_patch(Rectangle((lx0, ly0), lx1 - lx0, ly1 - ly0, fc="#b9e3f2", ec="#2a6f97",
                               ls=":", zorder=1.1))
        ax.text((V.POOL_X0 + V.POOL_X1) / 2, 7000, V.POOL_LABEL, ha="center", fontsize=8,
                rotation=90)
        for x, y, d in V.SITE_TREES:
            ax.add_patch(plt.Circle((x, y), d / 2, fc="#6a994e", alpha=0.35, ec="#386641"))
        for name, g0, g1, head in V.gates():
            ax.plot([g0, g1], [V.PLOT_D - 175] * 2, color="#d62728", lw=4)
            ax.text((g0 + g1) / 2, V.PLOT_D + 250, name, ha="center", fontsize=7)
        # the boundary wall
        T = V.BOUNDARY_T
        ax.add_patch(Rectangle((0, 0), V.PLOT_W, V.PLOT_D, fill=False, ec="#777", lw=2.5))
        ax.add_patch(Rectangle((T, T), V.PLOT_W - 2 * T, V.PLOT_D - 2 * T, fill=False,
                               ec="#777", lw=0.5))
        ax.axhline(V.RAMP_Y0, xmin=0, xmax=1, color="#999", ls=":", lw=0.6)
        ax.text(V.PLOT_W - 400, V.RAMP_Y0 + 150, "RAMP 3.6% ->", ha="right", fontsize=6)
        for s in V.STONE_FREE:
            ax.add_patch(Rectangle((s[0], s[1]), s[3] - s[0], s[4] - s[1], fc="#333", zorder=4))
    rs = V.rooms_on(fl)
    ext, part, inner = V.fabric(fl)
    for r in rs:
        geom(ax, V.net_poly(r), fc=ZCOL.get(V.ZONE.get(r[0]), "#fff"), ec="none", zorder=2)
    geom(ax, ext, fc="#333", ec="none", zorder=3)
    geom(ax, part, fc="#777", ec="none", zorder=3)
    for s in V.STONE_ZONES:
        if s[2] <= V.LEVEL[fl] + 1 < s[5]:
            ax.add_patch(Rectangle((s[0] - 60, s[1]), 120, s[4] - s[1], fc="#111", zorder=3.5))
    for r in rs:
        c = V.net_poly(r).representative_point()
        small = V.A(*V.rect(r)) < 8
        ax.text(c.x, c.y, f"{r[0]}\n{V.net_area(r):.1f} m2", ha="center", va="center",
                fontsize=5.5 if small else 7, weight="bold", zorder=8)
    for o in V.OPENINGS:
        if o[0] != fl:
            continue
        geom(ax, V.void_rect(o), fc=OCOL[o[1]], ec="none", zorder=5)
        sw = F._swing(o)
        if sw:
            ax.add_patch(MPoly(sw, closed=True, fc="none", ec=OCOL[o[1]], lw=0.5, zorder=5))
    for key, x, y, rot in dict(F.BY_FLOOR).get(fl, []):
        fp = F.footprint(key, x, y, rot)
        if fp:
            ax.add_patch(Rectangle((fp[0], fp[1]), fp[2] - fp[0], fp[3] - fp[1], fc="white",
                                   ec="#8c564b", lw=0.5, alpha=0.9, zorder=4))
            ax.text((fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2, key.replace("fia_", ""),
                    fontsize=3.5, ha="center", va="center", color="#8c564b", zorder=4)
    for name, x0, y0, x1, y1, fls in V.VOIDS:
        if fl in fls:
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#2ca02c",
                                   ls=":", lw=1.0, zorder=6))
            ax.text((x0 + x1) / 2, y1 - 400, name, fontsize=6, color="#2ca02c",
                    ha="center", zorder=6)
    # stairs: every tread whose flight starts on or ends at this floor
    for f in V.flights():
        z0 = f["z_foot"]
        z1 = z0 + f["n"] * f["rise"]
        lvl = V.LEVEL[fl]
        if not (min(z0, z1) - 1 <= lvl <= max(z0, z1) + 1 or
                (fl == "GF" and z0 < lvl < z1)):
            continue
        for t0, t1, z in V.flight_treads(f):
            x0, y0, x1, y1 = V.flight_plan(f, t0, t1)
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="k",
                                   lw=0.4, zorder=6))
    L = V.stair_landing()
    if L and fl in ("B1", "GF"):
        (x0, y0, x1, y1), _ = L
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="k", hatch="..",
                               lw=0.4, zorder=6))
    for s in V.projections():
        if s[4] >= V.LEVEL[fl] - 600:
            ax.add_patch(Rectangle((s[0], s[1]), s[2] - s[0], s[3] - s[1], fill=False,
                                   ec="#ff7f0e", ls="--", lw=0.7, zorder=7))
    if fl == "FF":
        for f in V.fins():
            ax.add_patch(Rectangle((f[0], f[1]), f[2] - f[0], f[3] - f[1], fc="#8b5a2b",
                                   ec="none", zorder=7))
        bx0, by0, bx1, by1 = V.BALCONY
        ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="#eeeeee", ec="#555",
                               lw=0.6, zorder=2))
        ax.text((bx0 + bx1) / 2, (by0 + by1) / 2, "BALCONY", ha="center", fontsize=7)
    lvl = V.LEVEL[fl]
    for g in V.guards():
        if lvl - 1 <= g[4] < lvl + V.CEIL.get(fl, 3000) + V.SLAB - 1:
            ax.add_patch(Rectangle((g[0], g[1]), g[2] - g[0], g[3] - g[1], fc="#00bcd4",
                                   ec="#00bcd4", lw=1.2, zorder=7))
    ax.annotate("N", xy=(1200, V.PLOT_D - 1500), xytext=(1200, V.PLOT_D - 3300), ha="center",
                arrowprops=dict(arrowstyle="-|>", lw=1.5), fontsize=12, weight="bold")
    ax.text(V.PLOT_W / 2, V.PLOT_D + 700, "STREET", ha="center", fontsize=9)
    ax.text(V.PLOT_W / 2, -700, "GARDEN / GOLF COURSE", ha="center", fontsize=9)
    ax.set_xlim(-600, V.PLOT_W + 600)
    ax.set_ylim(-1200, V.PLOT_D + 1200)
    ax.set_aspect("equal")
    ax.set_title(f"{V.PROJECT_TITLE} -- {V.FLOOR_NAME.get(fl, fl)} (FFL {lvl:+.0f})",
                 fontsize=11)
    ax.set_xticks(range(0, int(V.PLOT_W) + 1, 3000))
    ax.set_yticks(range(0, int(V.PLOT_D) + 1, 2000))
    ax.tick_params(labelsize=6)
    ax.grid(True, lw=0.2, color="#ddd")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, fname), dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    draw("B1", "preview_B1.png")
    draw("GF", "preview_GF.png", site=True)
    draw("FF", "preview_FF.png")
    print("wrote preview_B1.png, preview_GF.png, preview_FF.png")
