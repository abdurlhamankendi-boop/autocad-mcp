import pickle, sys, collections
import numpy as np
fn = sys.argv[1]
recs = [r for r in pickle.load(open(fn, "rb")) if "skip" not in r]
print("n ok", len(recs))
for r in recs[:3]:
    print({k: v for k, v in r.items() if k not in ("rooms",)})
    for rm in r["rooms"]:
        print("   ", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in rm.items()})
by = collections.defaultdict(list)
for r in recs:
    for rm in r["rooms"]:
        by[rm["type"]].append(rm)
for t, L in by.items():
    a = np.array([x["area"] for x in L]); d = np.array([x["doors"] for x in L]); s = np.array([x["short"] for x in L])
    print(t, len(L), "area p5/50/95", np.percentile(a, [5, 50, 95]).round(1), "short p5/50", np.percentile(s, [5, 50]).round(2),
          "doors mean", d.mean().round(2), collections.Counter(np.minimum(d, 4)).most_common())
nb = collections.Counter(r["n"]["bedroom"] for r in recs); print("beds", sorted(nb.items()))
c = np.array([r["circ"]["w1.5"]["narrow"] / r["net_interior"] for r in recs if r["circ"]])
print("circ share w1.5 p5/25/50/75/95", np.nanpercentile(c, [5, 25, 50, 75, 95]).round(3), "nan", np.isnan(c).sum())
print("door w int p5/50/95", np.percentile(sum((r["door_w_int"] for r in recs), []), [5, 50, 95]).round(2))
print("door single frac", sum(len(r["door_w_single"]) for r in recs) / sum(r["n_doors"] for r in recs))
print("unassigned doors", sum(r["n_doors"] - len(r["door_w_int"]) - len(r["door_w_single"]) for r in recs))
pc = collections.Counter(p for r in recs for p in set(r["door_pairs"])); print("door pairs (plans)", pc.most_common(15))
oc = collections.Counter(p for r in recs for p in set(r["open_pairs"])); print("open pairs (plans)", oc.most_common(10))
fc = collections.Counter(t for r in recs for t in r["fd_types"]); print("front door types", fc.most_common())
