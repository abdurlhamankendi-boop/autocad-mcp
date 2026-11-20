"""Skeptic spot-check: recompute ResPlan numbers straight from ResPlan.pkl with
independent code (own restricted unpickler, no reuse of the miner's modules or
records.pkl) and compare with room_stats.json.

Checks
  A. bed4plus master-bedroom (largest bedroom) area p50, and the segment size
  B. bed4plus bathrooms-per-bedroom p50 / mean, and P(4 bathrooms | 4 bedrooms)
"""
import json, math, pickle, sys
import numpy as np
import shapely
from shapely.geometry import Polygon

PKL = r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\ResPlan.pkl"
STATS = r"C:\Users\lsire\.claude\skills\architectural-cad\references\room_stats.json"
OUT = r"C:\Users\lsire\autocad-mcp\reference\datasets\merge\spotcheck_resplan.json"
OK_GLOBALS = {("shapely.io", "from_wkb"), ("numpy._core.multiarray", "scalar"),
              ("numpy.core.multiarray", "scalar"), ("numpy", "dtype")}


class Safe(pickle.Unpickler):
    def find_class(self, m, n):
        if (m, n) not in OK_GLOBALS:
            raise pickle.UnpicklingError(f"blocked {m}.{n}")
        return super().find_class(m, n)


def polys(g):
    """Every polygon in g, repairing invalid ones piece by piece."""
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        if g.is_valid:
            return [g]
        return [q for q in polys(shapely.make_valid(g)) if q.is_valid]
    out = []
    for x in getattr(g, "geoms", []):
        out += polys(x)
    return out


def room_areas(g, s2):
    return [p.area * s2 for p in polys(g) if p.area * s2 >= 0.5]


with open(PKL, "rb") as f:
    plans = Safe(f).load()

masters, ratios, n4, n4_4 = [], [], 0, 0
used = 0
for p in plans:
    if "area_change_sqft" in p:
        continue
    inner, area = p.get("inner"), float(p.get("area") or 0)
    if inner is None or inner.is_empty or inner.area <= 0 or area < 20:
        continue
    s = math.sqrt(area / inner.area)
    if not (0.08 <= float(p["wall_depth"]) * s <= 0.5):
        continue
    used += 1
    beds = room_areas(p.get("bedroom"), s * s)
    baths = room_areas(p.get("bathroom"), s * s)
    if len(beds) >= 4:
        masters.append(max(beds))
        ratios.append(len(baths) / len(beds))
        if len(beds) == 4:
            n4 += 1
            n4_4 += len(baths) == 4
del plans

J = json.load(open(STATS, encoding="utf-8"))
m_ref = J["room_types"]["bedroom_master"]["resplan"]
b_ref = J["dwelling"]["bathrooms_per_bedroom"]["resplan"]
res = {
    "plans_used": used,
    "A_bed4plus_n": {"recomputed": len(masters), "room_stats": m_ref["n"]},
    "A_master_area_p50_m2": {"recomputed": round(float(np.percentile(masters, 50)), 2),
                             "room_stats": m_ref["area_m2"]["p50"]},
    "A_master_area_p5_p95_m2": {"recomputed": [round(float(np.percentile(masters, q)), 2) for q in (5, 95)],
                                "room_stats": [m_ref["area_m2"]["p5"], m_ref["area_m2"]["p95"]]},
    "B_bath_per_bed_p50": {"recomputed": round(float(np.percentile(ratios, 50)), 3), "room_stats": b_ref["ratio"]["p50"]},
    "B_bath_per_bed_mean": {"recomputed": round(float(np.mean(ratios)), 3), "room_stats": b_ref["ratio"]["mean"]},
    "B_P(4 bath | 4 bed)": {"recomputed": round(n4_4 / n4, 3), "n_4bed": n4,
                            "room_stats": b_ref["by_bedroom_count"]["4_bed"]["bathrooms_dist"]["4"],
                            "room_stats_n_4bed": b_ref["by_bedroom_count"]["4_bed"]["n"]},
}
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
print(json.dumps(res, indent=1))
