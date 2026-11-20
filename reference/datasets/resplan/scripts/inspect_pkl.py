import sys, collections, time
sys.path.insert(0, r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\scripts")
from rp_load import load

t = time.time()
data = load()
print("loaded", type(data), len(data), "in", round(time.time() - t, 1), "s")
keys = collections.Counter()
types = collections.defaultdict(collections.Counter)
for p in data:
    for k, v in p.items():
        keys[k] += 1
        types[k][type(v).__name__] += 1
for k, c in keys.most_common():
    print(f"{k:20s} {c:6d} {dict(types[k])}")

p = data[0]
for k, v in p.items():
    s = repr(v)
    print("---", k, ":", s[:300])

# scalar fields over all plans
for k in keys:
    vals = [p[k] for p in data if k in p and isinstance(p[k], (int, float, str, bool)) or (k in p and type(p[k]).__module__ == "numpy")]
    if vals and len(vals) > 100:
        try:
            import numpy as np
            a = np.array([float(x) for x in vals])
            print("SCALAR", k, "n", len(a), "min", a.min(), "p50", np.median(a), "max", a.max())
        except Exception as e:
            c = collections.Counter(map(str, vals))
            print("SCALAR", k, c.most_common(10))
