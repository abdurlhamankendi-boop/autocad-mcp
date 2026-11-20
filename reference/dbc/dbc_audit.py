"""Measure the current villa_design.py constants against the DBC 2021 Part K values.

Read-only: imports villa_design and prints numbers. No AutoCAD, no writes.
"""
import math
import sys

sys.path.insert(0, r"C:\Users\lsire\autocad-mcp")
import villa_design as V  # noqa: E402
from shapely.geometry import box  # noqa: E402

print("== levels")
print("GF", V.GF, "GF_CH", V.GF_CH, "FF", V.FF, "FF_CH", V.FF_CH, "RF", V.RF,
      "PARAPET", V.PARAPET, "SLAB", V.SLAB, "AX", V.AX_FL, V.AX_CH)
print("top of parapet", V.RF + V.PARAPET, " pavilion top", V.LEVEL["RF"] + V.PAV_CH + V.SLAB)

print("\n== stair")
rise = V.FF2FF / V.RISERS
print(f"FF2FF {V.FF2FF}  risers {V.RISERS}  rise {rise:.1f}  going {V.STAIR_GOING}  2R+G {2*rise+V.STAIR_GOING:.0f}")
n = math.ceil(V.FF2FF / 180.0)
print(f"DBC risers needed (<=180): {n}  -> rise {V.FF2FF/n:.1f}")
x0, y0, x1, y1 = V.STAIR
print(f"stair well {x1-x0:.0f} wide x {y1-y0:.0f} deep")
for flights in (1, 2):
    per = math.ceil(n / flights)
    run = (per - 1) * 280.0
    need = run + (1000.0 if flights == 2 else 0.0)
    print(f"  {flights} flight(s): longest flight {per} risers, going run {run:.0f} + landing -> {need:.0f} mm")
print(f"  dog-leg: two flights side by side need >= 2 x 1000 = 2000 clear, well is {x1-x0:.0f}")
print("external steps: rise max", V.STEP_RISE_MAX, "going", V.STEP_GOING, "landing", V.LANDING)
for fl in ("GF",):
    ground = 0.0
    k = math.ceil((V.LEVEL[fl] - ground) / V.STEP_RISE_MAX)
    print(f"  entrance: {V.LEVEL[fl]-ground:.0f} mm in {k} risers of {(V.LEVEL[fl]-ground)/k:.0f}")

print("\n== rooms (net area, largest inscribed rectangle)")


def best_rect(poly):
    xs = sorted({round(c[0]) for c in poly.exterior.coords})
    ys = sorted({round(c[1]) for c in poly.exterior.coords})
    best = (0, 0)
    for i, a in enumerate(xs):
        for b in xs[i + 1:]:
            for j, c in enumerate(ys):
                for d in ys[j + 1:]:
                    r = box(a, c, b, d)
                    if poly.buffer(1).contains(r):
                        w, h = b - a, d - c
                        if min(w, h) > min(best) or (min(w, h) == min(best) and w * h > best[0] * best[1]):
                            best = (w, h)
    return best


for r in V.ROOMS:
    p = V.net_poly(r)
    if p.geom_type != "Polygon":
        p = max(p.geoms, key=lambda g: g.area)
    w, h = best_rect(p)
    bx = r[3] - r[1], r[4] - r[2]
    print(f"{r[6]} {r[0]:16s} {r[5]:12s} net {V.net_area(r):5.1f} m2  rect {bx[0]:.0f}x{bx[1]:.0f}"
          f"  inscribed {w:.0f}x{h:.0f}")

print("\n== windows: gross opening area (w x (head-sill)) vs 10% of net floor")
hgt = (V.WIN_HEAD - V.WIN_SILL) / 1000.0
for r in V.ROOMS:
    if r[5] != V.HAB:
        continue
    ws = [o for o in V.OPENINGS if o[0] == r[6] and o[7] == r[0] and o[8] is None and o[1] in (V.WIN, V.SLIDE)]
    area = sum(abs(o[6] - o[5]) / 1000.0 * (hgt if o[1] == V.WIN else V.DOOR_HEAD / 1000.0) for o in ws)
    na = V.net_area(r)
    print(f"{r[6]} {r[0]:16s} glazing(gross) {area:5.2f} m2 = {100*area/na:5.1f}% of {na:.1f}"
          f"   x0.8 frame -> {80*area/na:5.1f}%")

print("\n== doors (structural opening; clear ~ opening - 150)")
for o in V.OPENINGS:
    if o[1] not in (V.DOOR, V.SLIDE):
        continue
    w = abs(o[6] - o[5])
    wet = any(q[0] in (o[7], o[8]) and q[5] == V.WET for q in V.ROOMS)
    need = 710 if wet else 915
    flag = "" if w - 150 >= need else "  <-- below"
    print(f"{o[0]} {o[7]}->{o[8] or 'outside'}: opening {w:.0f}, clear~{w-150:.0f}, DBC {need}{flag}")

print("\n== corridor widths")
for r in V.ROOMS:
    if r[5] == V.CIRC:
        print(r[0], r[3] - r[1], r[4] - r[2])

print("\n== setbacks (outline to plot edges)")
for fl in V.floors():
    b = V.outline(fl).bounds
    print(fl, f"W {b[0]:.0f}  S(rear) {b[1]:.0f}  E {V.PLOT_W-b[2]:.0f}  N(front) {V.PLOT_D-b[3]:.0f}")
for f in V.FIN_ARRAYS:
    print("fin array x", f["x0"], f["x1"], "-> west setback", f["x0"], "z", f["z0"], f["z1"])
print("pool basin y0", V.BASIN_Y0, " pool y0", V.POOL_Y0, " shell y0", V.BASIN_Y0)

print("\n== areas")
gf_o = V.outline("GF").area / 1e6
ga = sum(V.fabric(fl)[2].area / 1e6 for fl in V.floors())
print(f"GF outline {gf_o:.1f} m2  coverage {100*gf_o/(V.PLOT_W*V.PLOT_D/1e6):.1f}%")
for fl in V.floors():
    print(f"  {fl} GA (inside ext walls) {V.fabric(fl)[2].area/1e6:.1f}  outline {V.outline(fl).area/1e6:.1f}")
print(f"villa GA (sum of floors, inside ext walls) {ga:.1f} m2 -> 60% = {0.6*ga:.1f} m2")
print(f"code's annex cap: 0.6 x GF outline = {0.6*gf_o:.1f} m2")

print("\n== roof")
E = V.envelope()
roof = E["upper"].area / 1e6
pv = V.A(*V.PV)
print(f"upper roof area {roof:.1f}  pavilion {pv:.1f} = {100*pv/roof:.0f}% (<=50%)")
ub = E["upper"].bounds
print("upper roof bounds", ub, " PV", V.PV)
inner = E["upper"].buffer(-1500, join_style=2)
print("PV inside 1.5 m setback line:", inner.contains(box(*V.PV)))
print("FF outline bounds", V.outline("FF").bounds)

print("\n== pool")
print(f"depth {V.POOL_TW - V.POOL_FL:.0f} mm (DBC shallowest 850-1200)")
print(f"north deck (TERRACE) {V.TERRACE:.0f}; south: weir {V.WEIR} + basin to y {V.BASIN_Y0}")
print(f"pool x {V.POOL_X0}-{V.POOL_X1}; plot W {V.PLOT_W}")
print("windows facing the pool (GF south):")
for o in V.OPENINGS:
    if o[0] == "GF" and o[1] == V.WIN and o[8] is None and V.facing(o) == "S":
        print("  ", o[7], "sill", V.WIN_SILL)

print("\n== forecourt / parking")
face = V.outline("GF").bounds[3]
print(f"GF north face {face:.0f}; boundary wall inner face {V.PLOT_D-350:.0f}; depth {V.PLOT_D-350-face:.0f}")
print(f"porch {V.PORCH_X1-V.PORCH_X0:.0f} wide")

print("\n== WWR")
per = 0.0
glz = 0.0
for fl, h in (("GF", V.GF_CH + V.SLAB), ("FF", V.FF_CH + V.SLAB)):
    per += V.outline(fl).exterior.length / 1000.0 * h / 1000.0
for o in V.OPENINGS:
    if o[8] is None and o[1] in (V.WIN, V.SLIDE):
        glz += abs(o[6] - o[5]) / 1000.0 * (hgt if o[1] == V.WIN else V.DOOR_HEAD / 1000.0)
print(f"ext wall {per:.0f} m2  glazing {glz:.1f} m2  WWR {100*glz/per:.1f}%")
