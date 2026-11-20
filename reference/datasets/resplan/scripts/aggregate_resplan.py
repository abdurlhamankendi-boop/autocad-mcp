"""Stage 2: aggregate per-plan records (work/records.pkl) into ../resplan_stats.json."""
import os, sys, json, pickle, math, collections, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.dirname(HERE)                                  # ...\datasets\resplan
REC = os.path.join(DS, "work", "records.pkl")
OUT = os.path.join(os.path.dirname(DS), "resplan_stats.json")  # ...\datasets\resplan_stats.json
TYPES = ["living", "bedroom", "bathroom", "kitchen", "storage", "stair", "balcony"]
INTERIOR = ["living", "bedroom", "bathroom", "kitchen", "storage", "stair"]


def pct(vals, ps=(5, 25, 50, 75, 95), nd=3, mean=True):
    a = np.asarray([v for v in vals if v is not None and not (isinstance(v, float) and math.isnan(v))], dtype=float)
    if a.size == 0:
        return {"n": 0}
    d = {"n": int(a.size)}
    for p in ps:
        d[f"p{p}"] = round(float(np.percentile(a, p)), nd)
    if mean:
        d["mean"] = round(float(a.mean()), nd)
    return d


def share(flags, nd=3):
    flags = list(flags)
    return round(sum(1 for f in flags if f) / len(flags), nd) if flags else None


def dist(vals, cap=None, nd=3):
    vals = [min(v, cap) if cap is not None else v for v in vals]
    c = collections.Counter(vals)
    n = len(vals)
    out = {}
    for k in sorted(c):
        key = f"{k}+" if cap is not None and k == cap else str(k)
        out[key] = round(c[k] / n, nd)
    return out


def room_block(rooms):
    """Stats for a list of room records of one kind."""
    if not rooms:
        return {"n": 0}
    b = {"n": len(rooms)}
    b["area_m2"] = pct([r["area"] for r in rooms], nd=2)
    b["short_side_m"] = pct([r["short"] for r in rooms], nd=2)
    b["inscribed_width_m"] = pct([r["inscribed"] for r in rooms], ps=(5, 50, 95), nd=2, mean=False)
    b["long_side_m"] = pct([r["long"] for r in rooms], ps=(5, 50, 95), nd=2, mean=False)
    b["aspect_ratio"] = pct([r["aspect"] for r in rooms], ps=(5, 50, 75, 95), nd=2, mean=False)
    b["rectangular_share"] = share(r["rect"] >= 0.95 for r in rooms)
    b["doors_per_room"] = dict(pct([r["doors"] for r in rooms], ps=(50, 95), nd=2),
                               dist=dist([r["doors"] for r in rooms], cap=4))
    b["has_front_door_share"] = share(r["entry"] for r in rooms)
    acc = collections.Counter(); door = collections.Counter(); opn = collections.Counter(); adj = collections.Counter()
    for r in rooms:
        a_types = set(r["acc_door"]) | set(r["acc_open"]) | set(r.get("acc_iwin", []))
        for t in a_types: acc[t] += 1
        for t in set(r["acc_door"]): door[t] += 1
        for t in set(r["acc_open"]) | set(r.get("acc_iwin", [])): opn[t] += 1
        for t in set(r["adj"]): adj[t] += 1
    n = len(rooms)
    b["access_to_share"] = {t: round(acc[t] / n, 3) for t in TYPES if acc[t]}
    b["door_to_share"] = {t: round(door[t] / n, 3) for t in TYPES if door[t]}
    b["open_or_passthrough_to_share"] = {t: round(opn[t] / n, 3) for t in TYPES if opn[t]}
    b["adjacent_to_share"] = {t: round(adj[t] / n, 3) for t in TYPES if adj[t]}
    b["no_access_share"] = share(not (r["acc_door"] or r["acc_open"] or r.get("acc_iwin")) and not r["entry"] for r in rooms)
    return b


def segment_stats(recs):
    S = {"n_plans": len(recs)}
    nb = [r["n"]["bedroom"] for r in recs]
    nba = [r["n"]["bathroom"] for r in recs]
    S["dwelling"] = {
        "listed_area_m2": pct([r["listed_area"] for r in recs], nd=1),
        "net_interior_area_m2": pct([r["net_interior"] for r in recs], nd=1),
        "balcony_area_m2_if_any": pct([r["balcony_area"] for r in recs if r["balcony_area"] > 0], nd=1),
        "share_with_balcony": share(r["n"]["balcony"] > 0 for r in recs),
        "share_with_storage": share(r["n"]["storage"] > 0 for r in recs),
        "share_with_stair": share(r["n"]["stair"] > 0 for r in recs),
        "share_with_garden_or_parking": share(r["has_garden"] or r["has_parking"] for r in recs),
        "bedrooms_dist": dist(nb, cap=6),
        "bathrooms_dist": dist(nba, cap=7),
        "functional_rooms_per_plan": pct([sum(r["n"][t] for t in INTERIOR) for r in recs], ps=(5, 50, 95), nd=1),
        "wall_thickness_m": pct([r["wt"] for r in recs], ps=(5, 50, 95), nd=3, mean=False),
        "interior_door_opening_width_m": pct([w for r in recs for w in r["door_w_int"]], ps=(5, 25, 50, 75, 95), nd=2, mean=False),
        "front_door_opening_width_m": pct([w for r in recs for w in r["fd_w"]], ps=(5, 50, 95), nd=2, mean=False),
        "interior_doors_per_plan": pct([r["n_doors"] for r in recs], ps=(5, 50, 95), nd=1),
    }

    rooms = collections.defaultdict(list)
    for r in recs:
        for rm in r["rooms"]:
            t = rm["type"]
            key = "living_zone" if t == "living" else t
            rooms[key].append(rm)
            if t == "bedroom" and rm.get("role"):
                rooms["bedroom_" + rm["role"]].append(rm)
            if t == "bathroom":
                rooms["bathroom_" + rm["role"]].append(rm)
    R = {k: room_block(v) for k, v in rooms.items()}
    # living zone net of narrow (<1.5 m) strips = main living/dining/hall area
    R["living_zone_broad"] = {
        "note": "living_zone minus parts narrower than 1.5 m (morphological opening, r=0.75 m)",
        "area_total_m2": pct([r["circ"]["w1.5"]["broad"] for r in recs if r.get("circ")], nd=2),
        "largest_piece_area_m2": pct([r["circ"]["w1.5"]["largest_broad"] for r in recs if r.get("circ")], nd=2),
    }
    for k in ("bedroom", "bedroom_other"):
        if rooms.get(k):
            ba = [rm["area"] for rm in rooms[k]]
            R[k]["small_room_share"] = {"note": "staff-room / study sized 'bedrooms' (no maid label in ResPlan)",
                                        "lt_8m2": share(a < 8.0 for a in ba), "lt_10m2": share(a < 10.0 for a in ba),
                                        "lt_8m2_and_kitchen_access": share(rm["area"] < 8.0 and "kitchen" in (set(rm["acc_door"]) | set(rm["acc_open"]) | set(rm.get("acc_iwin", []))) for rm in rooms[k])}
    if rooms.get("bathroom"):
        ba = [rm["area"] for rm in rooms["bathroom"]]
        R["bathroom"]["wc_sized_share"] = {"lt_2.0m2": share(a < 2.0 for a in ba),
                                           "lt_2.5m2": share(a < 2.5 for a in ba),
                                           "lt_3.0m2": share(a < 3.0 for a in ba)}
    S["rooms"] = R

    # plan-level pair frequencies
    present = [set(t for t in TYPES if r["n"][t] > 0) for r in recs]
    pairs = {}
    for i, a in enumerate(TYPES):
        for b in TYPES[i:]:
            key = "|".join(sorted((a, b)))     # records store pairs alphabetically
            idx = [k for k, pr in enumerate(present) if a in pr and b in pr and (a != b or recs[k]["n"][a] >= 2)]
            if len(idx) < 20:
                continue
            sub = [recs[k] for k in idx]

            def has(field, key=key, sub=sub):
                return share(key in set(r[field]) for r in sub)
            d = {"plans_with_both": len(idx),
                 "access": share((key in set(r["door_pairs"])) or (key in set(r["open_pairs"])) or (key in set(r["iwin_pairs"])) for r in sub),
                 "door": has("door_pairs"), "open": has("open_pairs"), "interior_window_passthrough": has("iwin_pairs"),
                 "window_only": has("window_pairs"), "adjacent": has("adj_pairs")}
            pairs[key] = d
    fd = collections.Counter(t for r in recs for t in r["fd_types"])
    S["connections"] = {
        "pair_plan_share": pairs,
        "front_door_opens_to_share": {t: round(fd[t] / len(recs), 3) for t in TYPES if fd[t]},
        "edges_per_plan_mean": {k: round(float(np.mean([len(r[f]) for r in recs])), 2)
                                for k, f in [("door", "door_pairs"), ("open", "open_pairs"),
                                             ("interior_window_passthrough", "iwin_pairs"),
                                             ("window_only", "window_pairs"), ("adjacent", "adj_pairs")]},
    }

    # circulation
    cr = [r for r in recs if r.get("circ") and r["net_interior"] > 0]
    S["circulation"] = {
        "living_zone_share_of_net_interior": pct([r["living_zone_area"] / r["net_interior"] for r in cr], nd=3),
        "corridor_like_share_w1.5": pct([(r["circ"]["w1.5"]["narrow"] + r["stair_area"]) / r["net_interior"] for r in cr], nd=3),
        "corridor_like_share_w1.8": pct([(r["circ"]["w1.8"]["narrow"] + r["stair_area"]) / r["net_interior"] for r in cr], nd=3),
        "corridor_like_area_m2_w1.5": pct([r["circ"]["w1.5"]["narrow"] for r in cr], nd=2),
        "share_plans_with_corridor_ge_2m2_w1.5": share(r["circ"]["w1.5"]["narrow"] >= 2.0 for r in cr),
        "share_plans_with_corridor_ge_2m2_w1.8": share(r["circ"]["w1.8"]["narrow"] >= 2.0 for r in cr),
    }

    # bathrooms per bedroom
    multi = [r for r in recs if r["n"]["bedroom"] >= 2]
    if multi:
        ratio = [r["n"]["bathroom"] / r["n"]["bedroom"] for r in multi]
        cross = {}
        for k in sorted(set(min(r["n"]["bedroom"], 6) for r in multi)):
            sub = [r["n"]["bathroom"] for r in multi if min(r["n"]["bedroom"], 6) == k]
            cross[f"{k}{'+' if k == 6 else ''}_bed"] = {"n": len(sub), "bathrooms_dist": dist(sub, cap=7),
                                                        "bathrooms_p50": float(np.median(sub))}
        beds = [rm for r in multi for rm in r["rooms"] if rm["type"] == "bedroom"]
        baths = [rm for r in multi for rm in r["rooms"] if rm["type"] == "bathroom"]
        S["bathrooms_per_bedroom"] = {
            "scope": "plans in this segment with >= 2 bedrooms",
            "n_plans": len(multi),
            "ratio": pct(ratio, nd=3),
            "bathrooms_minus_bedrooms_dist": dist([r["n"]["bathroom"] - r["n"]["bedroom"] for r in multi]),
            "by_bedroom_count": cross,
            "bedrooms_with_private_ensuite_share": share(rm.get("has_ensuite") for rm in beds),
            "master_with_private_ensuite_share": share(rm.get("has_ensuite") for rm in beds if rm.get("role") == "master"),
            "bathroom_role_share": {k: share(rm["role"] == k for rm in baths) for k in ("ensuite", "shared", "common")},
            "plans_with_at_least_one_common_bathroom": share(any(rm["type"] == "bathroom" and rm["role"] == "common" for rm in r["rooms"]) for r in multi),
        }
    return S


def main():
    recs_all = pickle.load(open(REC, "rb"))
    skipped = collections.Counter(r.get("skip") for r in recs_all if "skip" in r)
    recs = [r for r in recs_all if "skip" not in r]
    segs = {
        "all": recs,
        "bed4plus": [r for r in recs if r["n"]["bedroom"] >= 4],
        "bed3": [r for r in recs if r["n"]["bedroom"] == 3],
        "house_like": [r for r in recs if r["has_garden"] or r["has_parking"] or r["has_stair"]],
    }
    b4h = [r for r in segs["bed4plus"] if r["has_garden"] or r["has_parking"] or r["has_stair"]]
    if len(b4h) >= 50:
        segs["bed4plus_house_like"] = b4h
    meta = json.load(open(os.path.join(DS, "provenance.json"), encoding="utf-8"))
    out = dict(meta)
    out["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    out["plan_counts"] = {"in_pickle": len(recs_all), "used": len(recs), "excluded": dict(skipped),
                          "segments": {k: len(v) for k, v in segs.items()}}
    out["segments"] = {k: segment_stats(v) for k, v in segs.items()}
    # compact view for the validator: villa comparator segment first, 'all' as fallback
    ql = {"note": "Condensed from segments.bed4plus (villa comparator) with segments.all alongside. "
                  "Areas m2, lengths m (see method.calibration_uncertainty). Typicality warnings only."}
    for kind in ["living_zone", "bedroom_master", "bedroom_other", "bedroom", "bathroom", "bathroom_ensuite",
                 "bathroom_common", "kitchen", "balcony", "storage", "stair"]:
        row = {}
        for seg in ("bed4plus", "all"):
            b = out["segments"][seg]["rooms"].get(kind, {})
            if not b or b.get("n", 0) == 0:
                continue
            row[seg] = {"n": b["n"],
                        "area_m2": {k: b["area_m2"][k] for k in ("p5", "p25", "p50", "p75", "p95")},
                        "short_side_m": {k: b["short_side_m"][k] for k in ("p5", "p50")},
                        "aspect_ratio": {k: b["aspect_ratio"][k] for k in ("p50", "p95")},
                        "doors_per_room": {"mean": b["doors_per_room"]["mean"], "p50": b["doors_per_room"]["p50"],
                                           "p95": b["doors_per_room"]["p95"]}}
        ql[kind] = row
    for seg in ("bed4plus", "all"):
        S = out["segments"][seg]
        ql.setdefault("bathrooms_per_bedroom", {})[seg] = S["bathrooms_per_bedroom"]["ratio"]
        ql.setdefault("circulation_share_bounds", {})[seg] = {
            "upper_living_zone_p50": S["circulation"]["living_zone_share_of_net_interior"]["p50"],
            "lower_corridor_like_w1.8_p50": S["circulation"]["corridor_like_share_w1.8"]["p50"],
            "lower_corridor_like_w1.8_p95": S["circulation"]["corridor_like_share_w1.8"]["p95"]}
        ql.setdefault("key_connection_shares", {})[seg] = {
            k: S["connections"]["pair_plan_share"][k]["access"]
            for k in ("bedroom|living", "bathroom|bedroom", "bathroom|living", "kitchen|living",
                      "bedroom|kitchen", "balcony|bedroom", "balcony|living")
            if k in S["connections"]["pair_plan_share"]}
    segs_out = out.pop("segments")
    out["quicklook"] = ql
    out["segments"] = segs_out
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    print(out["plan_counts"])


if __name__ == "__main__":
    main()
