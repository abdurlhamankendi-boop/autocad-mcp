"""Extra audit of candidate A: things the validator does not look at."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import villa_design as V
from shapely.geometry import box

V.validate()
c, h, g = V._CIRC_REPORT
print(f"corridor {c:.1f} m2 = {100*c/g:.1f}% of GIA {g:.1f}; halls/landing/lobby {h:.1f}")

print("\nexternal steps (x0,y0,z0,x1,y1,z1):")
pool = box(V.POOL_X0 - 400, V.BASIN_Y0, V.POOL_X1 + 400, V.POOL_Y1 + 400)
for b in V.external_steps():
    hit = box(b[0], b[1], b[3], b[4]).intersection(pool).area
    print("  ", tuple(round(v) for v in b), "IN POOL SHELL" if hit > 0 else "")

E = V.envelope()
print("\nenvelope keys ok:", sorted(E))
pr = V.probes()
print("probes:", len(pr))
sh, cu, wa = V.pool_parts()
print("pool parts:", len(sh), len(cu), len(wa))

# stacking: FF external wall band vs GF external wall band
ex_gf = V.fabric("GF")[0]
ex_ff = V.fabric("FF")[0]
unsupported = ex_ff.difference(ex_gf.buffer(1))
print(f"\nFF external wall NOT over a GF external wall: {unsupported.area/1e6:.2f} m2 of plan")
geoms = unsupported.geoms if hasattr(unsupported, "geoms") else [unsupported]
for p in sorted(geoms, key=lambda p: -p.area):
    if p.area > 2e4:
        b = p.bounds
        print(f"   {p.area/1e6:.2f} m2  x {b[0]:.0f}-{b[2]:.0f}  y {b[1]:.0f}-{b[3]:.0f}")

# annex gap and heights
print("\nannex gap to villa:", round(V.outline("AX").distance(V.outline("GF"))), "mm")
print("forecourt depth:", V.PLOT_D - 350 - V.outline("GF").intersection(
    box(V.PORCH_X0, 0, V.PORCH_X1, V.PLOT_D)).bounds[3])
for r in V.ROOMS:
    x0, y0, x1, y1 = V.rect(r)
    w, d = sorted((x1 - x0, y1 - y0))
    if r[5] == V.HAB and d / w > 2.0:
        print("  aspect > 2:1 :", r[0], f"{d/w:.2f}")
