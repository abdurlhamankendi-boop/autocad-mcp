import json, sys
J = json.load(open(r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan_stats.json", encoding="utf-8"))
for seg in (sys.argv[1:] or ["all", "bed4plus"]):
    S = J["segments"][seg]
    print("=" * 30, seg, S["n_plans"])
    d = S["dwelling"]
    for k in ["listed_area_m2", "net_interior_area_m2", "bedrooms_dist", "bathrooms_dist", "share_with_storage", "share_with_stair", "share_with_balcony", "wall_thickness_m", "interior_door_opening_width_m", "front_door_opening_width_m"]:
        print(" ", k, d[k])
    for t, b in S["rooms"].items():
        if "area_m2" in b:
            a = b["area_m2"]; s = b["short_side_m"]; ar = b["aspect_ratio"]; dp = b["doors_per_room"]
            print(f"  {t:18s} n={b['n']:6d} area {a['p5']}/{a['p25']}/{a['p50']}/{a['p75']}/{a['p95']}  short p5/p50 {s['p5']}/{s['p50']}  AR p50/p95 {ar['p50']}/{ar['p95']}  doors mean {dp['mean']} {dp['dist']} rect {b['rectangular_share']} entry {b['has_front_door_share']}")
            print(f"  {'':18s} access_to {b['access_to_share']}")
        else:
            print("  ", t, b)
    print("  front door ->", S["connections"]["front_door_opens_to_share"])
    for k, v in S["connections"]["pair_plan_share"].items():
        if v["access"] and v["access"] > 0.03:
            print("   pair", k, v)
    print("  circ", json.dumps(S["circulation"]))
    print("  bpb", json.dumps({k: v for k, v in S.get("bathrooms_per_bedroom", {}).items() if k != "by_bedroom_count"}))
    print("  bpb cross", json.dumps(S.get("bathrooms_per_bedroom", {}).get("by_bedroom_count")))
