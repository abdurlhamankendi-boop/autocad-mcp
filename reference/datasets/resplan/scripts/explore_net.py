"""Is 'net_area' (where present) a better metric anchor than 'area'?"""
import sys, pickle, collections
import numpy as np
sys.path.insert(0, r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\scripts")
from rp_load import load
from mine_resplan import mrr_dims, parts

data = {p["id"]: p for p in load() if "area_change_sqft" not in p}
recs = [r for r in pickle.load(open(r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\work\records.pkl", "rb")) if "skip" not in r]
ratio, rows = [], []
for r in recs:
    p = data[r["id"]]
    net = float(p["net_area"]); area = float(p["area"])
    ratio.append(net / area)
    rows.append((r, p, net, area))
ratio = np.array(ratio)
print("net==0 share", np.mean(ratio == 0).round(3), " net/area in (0.4,1.0):", np.mean((ratio > 0.4) & (ratio < 1.0)).round(3),
      " >1:", np.mean(ratio > 1.0).round(3))
v = ratio[(ratio > 0) & (ratio < 3)]
print("net/area nonzero pctl 5/10/25/50/75/90/95:", np.percentile(v, [5, 10, 25, 50, 75, 90, 95]).round(3))
h, e = np.histogram(v, bins=np.arange(0, 3.01, 0.1))
print("hist", list(zip(e[:-1].round(1), h)))
# net_area vs net_interior in m2 (H1 scale)
rel = np.array([net / r["net_interior"] for r, p, net, area in rows if net > 0])
print("net_area / net_interior(H1)", np.percentile(rel, [5, 25, 50, 75, 95]).round(3))
# is net_area in sqft? ratio to area*10.7639
sq = np.array([net / (area * 10.7639) for r, p, net, area in rows if net > 0])
print("net_area/(area in sqft)", np.percentile(sq, [5, 25, 50, 75, 95]).round(3))

# door widths by connection type under H1 scale
dw = collections.defaultdict(list)
for r, p, net, area in rows:
    pass
# recompute per-door pair widths quickly using records: door_pairs order != widths order, so recompute
from shapely import affinity
import shapely
cnt = 0
for r, p, net, area in rows[:4000]:
    s = r["s"]
    rooms = []
    lv = [q for q in parts(p.get("living"))]
    for t in ["living", "bedroom", "bathroom", "kitchen", "balcony", "storage", "stair"]:
        for q in parts(p.get(t)):
            rooms.append((t, q.buffer(0.007 * 256)))
    for d in parts(p.get("door")):
        ts = sorted({t for t, g in rooms if d.intersects(g)})
        w = mrr_dims(d)[0] * s
        key = "|".join(ts) if len(ts) <= 2 else "3+"
        dw[key].append(w)
    for d in parts(p.get("front_door")):
        dw["FRONT"].append(mrr_dims(d)[0] * s)
for k, L in sorted(dw.items(), key=lambda kv: -len(kv[1]))[:10]:
    print(f"door {k:22s} n={len(L):6d} width m p5/25/50/75/95", np.percentile(L, [5, 25, 50, 75, 95]).round(2))
