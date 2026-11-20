"""Calibration check: which area field does the 'inner' polygon correspond to?
Uses standardised door widths as an independent ruler, grouped by net_area/area."""
import sys, pickle, collections
import numpy as np
sys.path.insert(0, r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\scripts")
from rp_load import load
from mine_resplan import mrr_dims, parts

data = {p["id"]: p for p in load() if "area_change_sqft" not in p}
recs = [r for r in pickle.load(open(r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\work\records.pkl", "rb")) if "skip" not in r]
groups = collections.defaultdict(lambda: collections.defaultdict(list))


def grp(q):
    if q == 0: return "a_net_missing"
    if q < 0.5: return "b_net_lt_0.5"
    if q <= 0.95: return "c_net_0.5-0.95"
    if q <= 1.05: return "d_net_0.95-1.05"
    return "e_net_gt_1.05"


per_plan = []
for r in recs:
    p = data[r["id"]]
    s = r["s"]
    q = float(p["net_area"]) / float(p["area"])
    g = grp(q)
    rooms = []
    for t in ["living", "bedroom", "bathroom", "kitchen", "balcony", "storage", "stair"]:
        for x in parts(p.get(t)):
            rooms.append((t, x.buffer(0.007 * 256)))
    bl, bb = [], []
    for d in parts(p.get("door")):
        ts = sorted({t for t, gg in rooms if d.intersects(gg)})
        w = mrr_dims(d)[0] * s
        if ts == ["bedroom", "living"]:
            bl.append(w)
        elif "bathroom" in ts and len(ts) == 2:
            bb.append(w)
    fd = [mrr_dims(d)[0] * s for d in parts(p.get("front_door"))]
    G = groups[g]
    G["bed_door"] += bl; G["bath_door"] += bb; G["front"] += fd
    G["wt"].append(r["wt"]); G["listed"].append(r["listed_area"]); G["q"].append(q)
    bs = [rm["short"] for rm in r["rooms"] if rm["type"] == "bedroom"]
    G["bed_short"] += bs
    G["nbed"].append(r["n"]["bedroom"])
    if bl:
        per_plan.append((q, float(np.median(bl))))

for g in sorted(groups):
    G = groups[g]
    print(f"{g:18s} plans={len(G['wt']):5d} medQ={np.median(G['q']):.3f} listed_m2 p50={np.median(G['listed']):6.1f} "
          f"nbed={np.mean(G['nbed']):.2f} | H1 bed-door p50={np.median(G['bed_door']):.3f} bath-door p50={np.median(G['bath_door']):.3f} "
          f"front p50={np.median(G['front']):.3f} wall p50={np.median(G['wt']):.3f} bed-short p50={np.median(G['bed_short']):.2f}")

# For the carpet-anchored subset, what would sqrt(q) rescaling give?
c = groups["c_net_0.5-0.95"]
k = np.sqrt(np.median(c["q"]))
print("sqrt(median q) =", round(k, 4), "-> bed door", round(np.median(c["bed_door"]) * k, 3), "bath door", round(np.median(c["bath_door"]) * k, 3),
      "front", round(np.median(c["front"]) * k, 3), "wall", round(np.median(c["wt"]) * k, 3))
# per-plan: correlation of H1 door width with sqrt(1/q) in subset c
pp = np.array([(q, w) for q, w in per_plan if 0.5 <= q <= 0.95])
print("corr(H1 bed-door width, 1/sqrt(q)) in subset c:", np.corrcoef(pp[:, 1], 1 / np.sqrt(pp[:, 0]))[0, 1].round(3))
w_net = pp[:, 1] * np.sqrt(pp[:, 0])
print("subset c per-plan bed-door width: H1 IQR/median", (np.subtract(*np.percentile(pp[:, 1], [75, 25])) / np.median(pp[:, 1])).round(3),
      " net-anchored IQR/median", (np.subtract(*np.percentile(w_net, [75, 25])) / np.median(w_net)).round(3))
