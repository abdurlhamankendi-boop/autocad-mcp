import pickle, collections
recs = pickle.load(open(r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\work\records.pkl", "rb"))
for r in recs:
    if str(r.get("skip", "")).startswith("error"):
        print(r)
ok = [r for r in recs if "skip" not in r]
wc = collections.Counter(p for r in ok for p in set(r["window_pairs"]))
print("window pairs (plans)", wc.most_common(15))
k_none = 0
for r in ok:
    if r["n"]["kitchen"] and "kitchen|living" not in r["door_pairs"] and "kitchen|living" not in r["open_pairs"] and "kitchen|living" not in r["window_pairs"]:
        k_none += 1
print("kitchen plans with no kitchen-living door/open/window:", k_none, "of", sum(1 for r in ok if r["n"]["kitchen"]))
kit_adj = sum(1 for r in ok if "kitchen|living" in r["adj_pairs"])
print("kitchen-living adjacent", kit_adj)
