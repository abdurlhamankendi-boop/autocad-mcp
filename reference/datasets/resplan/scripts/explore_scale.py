"""Figure out which polygon the per-plan 'area' (m^2) refers to, using door widths
and wall thickness as independent sanity checks."""
import sys, collections
import numpy as np
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
sys.path.insert(0, r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\scripts")
from rp_load import load

data = load()
aug = [p for p in data if "area_change_sqft" in p]
print("augmented-key plans:", len(aug), "ids sample", [p["id"] for p in aug[:10]])
print("id range of non-aug", min(p["id"] for p in data if "area_change_sqft" not in p), max(p["id"] for p in data if "area_change_sqft" not in p))
print("stair plans", sum(1 for p in data if p.get("stair") is not None and not p["stair"].is_empty))
print("stair & aug", sum(1 for p in aug if p.get("stair") is not None and not p["stair"].is_empty))
for k in ["garden", "parking", "pool", "land", "balcony", "storage", "stair", "neighbor"]:
    ne = 0
    for p in data:
        v = p.get(k)
        if v is None:
            continue
        if isinstance(v, tuple):
            ne += any(not g.is_empty for g in v)
        else:
            ne += not v.is_empty
    print("non-empty", k, ne)


def parts(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon) and not x.is_empty]


def door_long(g):
    r = g.minimum_rotated_rectangle
    xs = np.array(r.exterior.coords)
    e = np.hypot(*np.diff(xs, axis=0).T)
    return max(e[:2]), min(e[:2])


rows = []
rng = np.random.default_rng(0)
idx = rng.choice(len(data), 1500, replace=False)
for i in idx:
    p = data[i]
    if "area_change_sqft" in p:
        continue
    inner = p["inner"]
    rooms = []
    for k in ["living", "bedroom", "bathroom", "kitchen", "storage", "stair", "balcony"]:
        rooms += parts(p.get(k))
    rooms_nb = []
    for k in ["living", "bedroom", "bathroom", "kitchen", "storage", "stair"]:
        rooms_nb += parts(p.get(k))
    A_inner = inner.area
    A_gross = unary_union([inner, p["wall"]]).area
    A_rooms = sum(r.area for r in rooms)
    A_rooms_nb = sum(r.area for r in rooms_nb)
    A_bal = sum(r.area for r in parts(p.get("balcony")))
    ds = [door_long(d) for d in parts(p.get("door"))]
    dl = np.median([d[0] for d in ds]) if ds else np.nan
    minx, miny, maxx, maxy = inner.bounds
    rows.append(dict(area=float(p["area"]), net=float(p["net_area"]), A_inner=A_inner, A_gross=A_gross,
                     A_rooms=A_rooms, A_rooms_nb=A_rooms_nb, A_bal=A_bal, door=dl, wd=p["wall_depth"],
                     W=max(maxx - minx, maxy - miny), fd=door_long(p["front_door"])[0] if p.get("front_door") is not None else np.nan))

R = {k: np.array([r[k] for r in rows]) for k in rows[0]}
print("n", len(rows))
print("plan max extent units p5/50/95", np.percentile(R["W"], [5, 50, 95]))
print("A_rooms/A_inner", np.percentile(R["A_rooms"] / R["A_inner"], [5, 50, 95]))
print("A_rooms_nb/A_inner", np.percentile(R["A_rooms_nb"] / R["A_inner"], [5, 50, 95]))
print("A_gross/A_inner", np.percentile(R["A_gross"] / R["A_inner"], [5, 50, 95]))
print("net/area", np.nanpercentile(R["net"] / R["area"], [5, 25, 50, 75, 95]))
for cand in ["A_inner", "A_gross", "A_rooms", "A_rooms_nb"]:
    s = np.sqrt(R["area"] / R[cand])
    print(f"--- scale from area/{cand}: m per unit p5/50/95", np.round(np.percentile(s, [5, 50, 95]), 4))
    print("    wall thickness m p1/5/50/95/99", np.round(np.percentile(R["wd"] * s, [1, 5, 50, 95, 99]), 3),
          "share in 0.10-0.40:", np.mean((R["wd"] * s >= 0.1) & (R["wd"] * s <= 0.4)).round(3))
    print("    median door long side m p5/25/50/75/95", np.round(np.nanpercentile(R["door"] * s, [5, 25, 50, 75, 95]), 3))
    print("    front door m p5/50/95", np.round(np.nanpercentile(R["fd"] * s, [5, 50, 95]), 3))
s = np.sqrt(R["net"] / R["A_inner"])
ok = np.isfinite(s) & (s > 0)
print("--- scale from net/A_inner: wall m", np.round(np.percentile((R["wd"] * s)[ok], [5, 50, 95]), 3),
      "door", np.round(np.nanpercentile((R["door"] * s)[ok], [5, 50, 95]), 3))
