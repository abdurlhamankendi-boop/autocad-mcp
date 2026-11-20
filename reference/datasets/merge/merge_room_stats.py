"""Merge resplan_stats.json + swiss_stats.json into one typicality file for the
villa validator:

    C:\\Users\\lsire\\.claude\\skills\\architectural-cad\\references\\room_stats.json

Schema (one shape for every statistic):
    room_types.<canonical type>.<source> -> normalised stats   (source = resplan | swiss)
    dwelling.<metric>.<source>           -> dwelling-level stats
    villa_role_map.<villa_design.py role> -> canonical type (+ match quality per source)

Only aggregate statistics are copied; nothing here is per-plan data.
Both inputs are CC BY 4.0 -- the attribution lines travel inside the output.
"""
import hashlib
import json
import os
import datetime

DS = r"C:\Users\lsire\autocad-mcp\reference\datasets"
RESPLAN = os.path.join(DS, "resplan_stats.json")
SWISS = os.path.join(DS, "swiss_stats.json")
OUT = r"C:\Users\lsire\.claude\skills\architectural-cad\references\room_stats.json"

MIN_N = 50            # below this, fall back to the next segment in the list
R_SEGS = ["bed4plus", "house_like", "all"]            # ResPlan preference order
S_SEGS = ["bedrooms_ge4", "rooms_ge4", "all"]          # Swiss preference order

R_TYPE = {"living": "living", "bedroom": "bedroom", "bathroom": "bathroom", "kitchen": "kitchen",
          "storage": "storage", "stair": "stair", "balcony": "balcony_terrace"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pick(d, keys):
    return {k: d[k] for k in keys if k in d} if d else None


def rename_targets(m):
    return {R_TYPE.get(k, k): v for k, v in (m or {}).items()}


# ------------------------------------------------------------------ ResPlan
def r_block(R, seg, key, match, note=None):
    rb = R["segments"][seg]["rooms"].get(key)
    if not rb or not rb.get("n"):
        return None
    d = rb["doors_per_room"]
    out = {
        "segment": seg, "source_key": f"segments.{seg}.rooms.{key}", "match": match,
        "n": rb["n"],
        "area_m2": rb["area_m2"],
        "short_side_m": rb["short_side_m"],
        "long_side_m": rb["long_side_m"],
        "inscribed_width_m": rb.get("inscribed_width_m"),
        "aspect_ratio": rb["aspect_ratio"],
        "shape": {"rectangular_share": rb.get("rectangular_share")},
        "doors_per_room": {"mean": d.get("mean"), "p50": d.get("p50"), "p95": d.get("p95"),
                           "share_by_count": d.get("dist")},
        "entrance_share": rb.get("has_front_door_share"),
        "links": {
            "definition": "share of rooms of this type with >= 1 link of that kind to a room of the target type "
                          "(target 'living' = ResPlan living zone, which also contains dining, hall and corridors)",
            "door": rename_targets(rb.get("door_to_share")),
            "access": rename_targets(rb.get("access_to_share")),
            "adjacent": rename_targets(rb.get("adjacent_to_share")),
            "no_access_share": rb.get("no_access_share"),
        },
    }
    for extra in ("wc_sized_share", "small_room_share"):
        if extra in rb:
            out[extra] = rb[extra]
    if note:
        out["note"] = note
    others = {}
    for s2 in ("all", "bed4plus", "house_like", "bed4plus_house_like"):
        if s2 == seg:
            continue
        b2 = R["segments"].get(s2, {}).get("rooms", {}).get(key)
        if b2 and b2.get("n"):
            others[s2] = {"n": b2["n"], "area_m2": pick(b2["area_m2"], ("p5", "p50", "p95")),
                          "short_side_m": pick(b2["short_side_m"], ("p5", "p50")),
                          "aspect_ratio": pick(b2["aspect_ratio"], ("p50", "p95"))}
    out["other_segments"] = others
    return out


def r_room(R, key, match, note=None, segs=R_SEGS):
    for seg in segs:
        rb = R["segments"][seg]["rooms"].get(key)
        if rb and rb.get("n", 0) >= MIN_N:
            return r_block(R, seg, key, match, note)
    return r_block(R, segs[-1], key, match, note)


# ------------------------------------------------------------------ Swiss
S_DERIVED_BASE = {"bedroom_master_proxy": "bedroom", "bedroom_secondary": "bedroom",
                  "bathroom_ensuite": "bathroom", "bathroom_shared": "bathroom",
                  "hall_entrance": "corridor", "corridor_internal": "corridor"}


def s_block(S, grp, section, key, match, note=None):
    g = S["groups"][grp]
    sb = g[section].get(key)
    if not sb or not sb.get("n_rooms"):
        return None
    d = sb["doors_per_room"]
    base = S_DERIVED_BASE.get(key, key)
    con = g["connections"]
    out = {
        "segment": grp, "source_key": f"groups.{grp}.{section}.{key}", "match": match,
        "n": sb["n_rooms"], "n_dwellings": sb.get("n_dwellings"),
        "area_m2": sb["area_m2"],
        "short_side_m": sb["short_side_m"],
        "long_side_m": sb["long_side_m"],
        "aspect_ratio": sb["aspect_ratio"],
        "shape": {"rectangularity_p50": sb.get("rectangularity_p50"),
                  "near_rectangular_subset": sb.get("near_rectangular_subset")},
        "doors_per_room": {"mean": d.get("mean"), "p50": d.get("p50"), "p95": d.get("p95"),
                           "share_by_count": d.get("share_by_count")},
        "door_or_open_per_room": sb.get("door_or_open_connections_per_room"),
        "windows_per_room": sb.get("windows_per_room"),
        "entrance_share": sb.get("share_containing_entrance_door"),
        "door_width_m": sb.get("door_width_m"),
        "links": {
            "definition": "share of rooms of this type with >= 1 link of that kind to a room of the target type "
                          "(ENTRANCE = dwelling entrance door, EXTERNAL = door to outside/common areas)",
            "links_of_type": base,
            "door": con["door"].get(base),
            "door_or_open": con["door_or_open"].get(base),
            "adjacent": con["shares_wall_or_boundary"].get(base),
        },
    }
    if base != key:
        out["links"]["note"] = f"link shares are for all '{base}' rooms of the segment (not computed per derived subtype)"
    if note:
        out["note"] = note
    others = {}
    for g2 in ("all", "rooms_ge4", "bedrooms_ge4", "multi_floor"):
        if g2 == grp:
            continue
        b2 = S["groups"].get(g2, {}).get(section, {}).get(key)
        if b2 and b2.get("n_rooms"):
            others[g2] = {"n": b2["n_rooms"], "area_m2": pick(b2["area_m2"], ("p5", "p50", "p95")),
                          "short_side_m": pick(b2["short_side_m"], ("p5", "p50")),
                          "aspect_ratio": pick(b2["aspect_ratio"], ("p50", "p95"))}
    out["other_segments"] = others
    return out


def s_room(S, section, key, match, note=None, segs=S_SEGS):
    for grp in segs:
        sb = S["groups"][grp][section].get(key)
        if sb and sb.get("n_rooms", 0) >= MIN_N:
            return s_block(S, grp, section, key, match, note)
    for grp in segs:
        if S["groups"][grp][section].get(key):
            return s_block(S, grp, section, key, match, note)
    return None


def absent(why):
    return {"match": "none", "note": why}


def main():
    R = json.load(open(RESPLAN, encoding="utf-8"))
    S = json.load(open(SWISS, encoding="utf-8"))
    rb4 = R["segments"]["bed4plus"]
    sg4 = S["groups"]["bedrooms_ge4"]
    sr4 = S["groups"]["rooms_ge4"]

    rt = {}
    rt["living"] = {
        "resplan": r_room(R, "living_zone", "poor",
                          "ResPlan 'living' is one merged zone: living + dining + hall + corridors. Compare the villa's "
                          "family living + formal dining + hall together, or use it only for the upper tail."),
        "swiss": s_room(S, "rooms", "living", "good",
                        "LIVING_ROOM + LIVING_DINING areas; dining is usually inside LIVING_DINING."),
    }
    rt["living"]["resplan"]["living_zone_broad"] = rb4["rooms"].get("living_zone_broad")
    rt["dining"] = {
        "resplan": absent("dining is merged into ResPlan's living zone"),
        "swiss": s_room(S, "rooms", "dining", "fair",
                        "separate DINING areas only (small n); most Swiss dining sits inside LIVING_DINING"),
    }
    rt["kitchen"] = {"resplan": r_room(R, "kitchen", "good"), "swiss": s_room(S, "rooms", "kitchen", "good")}
    rt["bedroom"] = {"resplan": r_room(R, "bedroom", "good"), "swiss": s_room(S, "rooms", "bedroom", "good")}
    rt["bedroom_master"] = {
        "resplan": r_room(R, "bedroom_master", "good", "largest bedroom of a plan with >= 2 bedrooms (my label)"),
        "swiss": s_room(S, "rooms_derived", "bedroom_master_proxy", "good",
                        "largest bedroom of a dwelling with >= 2 bedrooms (proxy label)"),
    }
    rt["bedroom_secondary"] = {
        "resplan": r_room(R, "bedroom_other", "good", "every bedroom except the largest"),
        "swiss": s_room(S, "rooms_derived", "bedroom_secondary", "good", "every bedroom except the largest"),
    }
    rt["bathroom"] = {
        "resplan": r_room(R, "bathroom", "fair",
                          "all sanitary rooms: ResPlan has no WC label, so WC-sized rooms are included (see wc_sized_share)"),
        "swiss": s_room(S, "rooms", "bathroom", "good", "full bathroom = BATHROOM area containing a shower or bathtub"),
    }
    rt["bathroom_ensuite"] = {
        "resplan": r_room(R, "bathroom_ensuite", "good",
                          "reachable from a bedroom and not from living/kitchen (my label)"),
        "swiss": s_room(S, "rooms_derived", "bathroom_ensuite", "fair",
                        "full bathroom with a direct door/open link to a bedroom; en-suites are rare in Swiss flats"),
    }
    rt["bathroom_common"] = {
        "resplan": r_room(R, "bathroom_common", "good", "bathroom not reachable from any bedroom"),
        "swiss": s_room(S, "rooms_derived", "bathroom_shared", "good", "full bathroom with no direct bedroom link"),
    }
    wc_r = absent("no WC label; use rooms.bathroom wc_sized_share (share of ResPlan bathrooms under 2.0/2.5/3.0 m2)")
    wc_r["wc_sized_share"] = rb4["rooms"]["bathroom"].get("wc_sized_share")
    wc_r["segment"] = "bed4plus"
    rt["wc"] = {"resplan": wc_r,
                "swiss": s_room(S, "rooms", "wc", "good", "BATHROOM area with a toilet but no shower/bath")}
    rt["corridor"] = {
        "resplan": absent("no corridor label; see dwelling.circulation_share for bounds"),
        "swiss": s_room(S, "rooms", "corridor", "good", "CORRIDOR, CORRIDORS_AND_HALLS, LOBBY, FOYER (halls included)"),
    }
    rt["corridor_internal"] = {
        "resplan": absent("no corridor label"),
        "swiss": s_room(S, "rooms_derived", "corridor_internal", "good", "corridors that do NOT hold the entrance door"),
    }
    rt["hall"] = {
        "resplan": absent("hall merged into ResPlan's living zone (the front door opens into it in >99% of plans)"),
        "swiss": s_room(S, "rooms_derived", "hall_entrance", "good", "the corridor/hall that holds the dwelling entrance door"),
    }
    st_s = s_room(S, "rooms", "stair", "poor",
                  "STAIRCASE areas inside dwellings are rare; prefer internal_stair_fixture below",
                  segs=["multi_floor", "rooms_ge4", "all"])
    st_s = st_s or {"match": "poor"}
    st_s["internal_stair_fixture"] = dict(S["groups"]["multi_floor"]["dwelling"]["internal_stair_fixture"],
                                          segment="multi_floor")
    rt["stair"] = {
        "resplan": r_room(R, "stair", "fair",
                          "single-storey unit plans: the stair polygon is a stair drawn inside the unit or at its entry; "
                          "house_like segment used because bed4plus has only 43",
                          segs=["house_like", "all"]),
        "swiss": st_s,
    }
    rt["storage"] = {"resplan": r_room(R, "storage", "fair", "present in ~20% of >=4-bed plans"),
                     "swiss": s_room(S, "rooms", "storage", "good", "STOREROOM + CLOAKROOM")}
    rt["balcony_terrace"] = {
        "resplan": r_room(R, "balcony", "fair", "balconies only; no roof terraces or gardens"),
        "swiss": s_room(S, "rooms", "balcony_terrace", "good", "BALCONY, LOGGIA, TERRACE, WINTERGARTEN, PATIO"),
    }
    rt["study"] = {"resplan": absent("no study label"),
                   "swiss": s_room(S, "rooms", "study", "fair",
                                   "OFFICE/STUDIO, plus ROOM when both BEDROOM and LIVING labels exist (small n)")}
    rt["laundry"] = {
        "resplan": absent("no laundry label"),
        "swiss": {"match": "proxy", "segment": "bedrooms_ge4",
                  "note": "no in-unit laundry rooms (Swiss laundry is a shared basement room); presence proxy only",
                  "in_unit_washing_machine": sg4["dwelling"]["in_unit_washing_machine"],
                  "in_unit_washing_machine_rooms_ge4": sr4["dwelling"]["in_unit_washing_machine"]},
    }
    maid_r = {"match": "proxy", "segment": "bed4plus",
              "note": "no staff-room label; small 'bedrooms' are the only analogue. Not usable for size checks.",
              "small_bedroom_share": rb4["rooms"]["bedroom"].get("small_room_share"),
              "kitchen_connects_to_bedroom_plan_share": rb4["connections"]["pair_plan_share"]["bedroom|kitchen"]}
    rt["maid"] = {"resplan": maid_r, "swiss": absent("no maid/driver rooms in Swiss flats")}

    # ------------------------------------------------------------ dwelling level
    rd = rb4["dwelling"]
    sd = sg4["dwelling"]
    dw = {}
    dw["segment_sizes"] = {
        "resplan": {**R["plan_counts"]["segments"],
                    "unit": "plans (original listings; augmented plans removed; near-duplicates NOT removed)"},
        "swiss": {g: S["groups"][g]["dwelling"]["n_layouts"] for g in S["groups"]} | {
            "unit": "unique layouts with explicit room labels (floors reusing one plan counted once)"},
    }
    dw["net_area_m2"] = {
        "resplan": {"segment": "bed4plus", "net_interior_area_m2": rd["net_interior_area_m2"],
                    "listed_area_m2": rd["listed_area_m2"], "balcony_area_m2_if_any": rd["balcony_area_m2_if_any"]},
        "swiss": {"segment": "bedrooms_ge4", "indoor_net_area_m2": sd["indoor_net_area_m2"],
                  "outdoor_area_m2_if_any": sd["outdoor_area_m2_if_any"],
                  "rooms_ge4_indoor_net_area_m2": sr4["dwelling"]["indoor_net_area_m2"]},
    }
    dw["circulation_share"] = {
        "resplan": {"segment": "bed4plus", "kind": "bounds only (no corridor label)",
                    "upper_bound_living_zone_share": rb4["circulation"]["living_zone_share_of_net_interior"],
                    "lower_bound_corridor_like_w1.8": rb4["circulation"]["corridor_like_share_w1.8"],
                    "lower_bound_corridor_like_w1.5": rb4["circulation"]["corridor_like_share_w1.5"],
                    "share_plans_with_corridor_ge_2m2_w1.8": rb4["circulation"].get("share_plans_with_corridor_ge_2m2_w1.8")},
        "swiss": {"segment": "bedrooms_ge4",
                  "circulation_share_of_indoor_area": sd["circulation_share_of_indoor_area"],
                  "corridor_only_share_of_indoor_area": sd["corridor_only_share_of_indoor_area"],
                  "rooms_ge4_circulation_share": sr4["dwelling"]["circulation_share_of_indoor_area"],
                  "share_with_corridor": sd.get("share_with_corridor")},
    }
    bpb = rb4["bathrooms_per_bedroom"]
    dw["bathrooms_per_bedroom"] = {
        "resplan": {"segment": "bed4plus", "definition": "all bathrooms (incl. WC-sized, no WC label) / bedrooms",
                    "ratio": bpb["ratio"], "bathrooms_minus_bedrooms_dist": bpb["bathrooms_minus_bedrooms_dist"],
                    "by_bedroom_count": bpb["by_bedroom_count"],
                    "bedrooms_with_private_ensuite_share": bpb["bedrooms_with_private_ensuite_share"],
                    "master_with_private_ensuite_share": bpb["master_with_private_ensuite_share"],
                    "bathroom_role_share": bpb["bathroom_role_share"],
                    "plans_with_at_least_one_common_bathroom": bpb["plans_with_at_least_one_common_bathroom"]},
        "swiss": {"segment": "bedrooms_ge4", **{k: v for k, v in sd["multi_bedroom"].items()},
                  "rooms_ge4_full_bathrooms_per_bedroom": sr4["dwelling"]["multi_bedroom"]["full_bathrooms_per_bedroom"]},
    }
    dw["room_counts"] = {
        "resplan": {"segment": "bed4plus", "bedrooms_dist": rd["bedrooms_dist"], "bathrooms_dist": rd["bathrooms_dist"],
                    "functional_rooms_per_plan": rd["functional_rooms_per_plan"],
                    "interior_doors_per_plan": rd["interior_doors_per_plan"],
                    "share_with_storage": rd["share_with_storage"], "share_with_balcony": rd["share_with_balcony"],
                    "share_with_stair": rd["share_with_stair"]},
        "swiss": {"segment": "bedrooms_ge4", **{k: sd[k] for k in ("n_rooms_swiss", "n_bedrooms", "n_full_bathrooms",
                                                                   "n_wc", "n_floors", "share_with_storage_room",
                                                                   "share_with_laundry_room", "share_with_any_ensuite",
                                                                   "share_with_outdoor_space")}},
    }
    kl = rb4["connections"]["pair_plan_share"]["kitchen|living"]
    dw["kitchen_mode"] = {
        "resplan": {"segment": "bed4plus", "definition": "plans with a kitchen: link kinds between kitchen and living zone "
                    "(a plan can have several kinds)", "door": kl["door"], "open": kl["open"],
                    "interior_window_passthrough": kl["interior_window_passthrough"], "any_access": kl["access"]},
        "swiss": {"segment": "bedrooms_ge4", "kitchen_mode_share": sd["kitchen_mode_share"],
                  "rooms_ge4_kitchen_mode_share": sr4["dwelling"]["kitchen_mode_share"]},
    }
    dw["entrance_opens_into"] = {
        "resplan": {"segment": "bed4plus", "share": rename_targets(rb4["connections"]["front_door_opens_to_share"]),
                    "note": "'living' = living zone incl. hall"},
        "swiss": {"segment": "bedrooms_ge4", "share": sd["entrance_door_opens_into_share"]},
    }
    dw["type_pair_links"] = {
        "resplan": {"segment": "bed4plus",
                    "definition": "per PLAN: among plans containing both types (A|A: >= 2 rooms of A), share with >= 1 "
                                  "link of that kind. access = door or open passage or interior window pass-through.",
                    "pairs": {"|".join(sorted(R_TYPE.get(t, t) for t in k.split("|"))): v
                              for k, v in rb4["connections"]["pair_plan_share"].items()},
                    "edges_per_plan_mean": rb4["connections"]["edges_per_plan_mean"]},
        "swiss": {"segment": "bedrooms_ge4",
                  "definition": "share of ALL door (resp. open) links in the segment that join this type pair",
                  "link_pair_share": sg4["connections"]["link_pair_share"]},
    }
    dw["door_width_m"] = {
        "resplan": {"segment": "bed4plus", "interior_opening": rd["interior_door_opening_width_m"],
                    "front_door_opening": rd["front_door_opening_width_m"],
                    "note": "likely 10-15% wide because of the listing-area scale (see sources.resplan.scale)"},
        "swiss": {"segment": "bedrooms_ge4", "bedroom": rt["bedroom"]["swiss"]["door_width_m"],
                  "bathroom": rt["bathroom"]["swiss"]["door_width_m"],
                  "note": "long side of the door polygon's minimum rotated rectangle (can include swing/leaf drawing)"},
    }

    # ------------------------------------------------------------ villa roles
    Q = lambda t, r, s, note=None: {"type": t, "resplan_match": r, "swiss_match": s, **({"note": note} if note else {})}
    roles = {
        "family_living": Q("living", "poor", "good"),
        "majlis": Q("living", "poor", "poor", "no majlis in either dataset; living room is the nearest reception room"),
        "formal_dining": Q("dining", "none", "fair"),
        "hall": Q("hall", "none", "good"),
        "corridor": Q("corridor_internal", "none", "good"),
        "landing": Q("corridor", "none", "fair", "Swiss multi_floor corridor stats in other_segments are the nearest"),
        "kitchen": Q("kitchen", "good", "good"),
        "prep_kitchen": Q("kitchen", "none", "none", "compare only against the lower tail; no dirty-kitchen label anywhere"),
        "pantry": Q("storage", "poor", "fair"),
        "study": Q("study", "none", "fair"),
        "master_bedroom": Q("bedroom_master", "good", "good"),
        "bedroom": Q("bedroom_secondary", "good", "good"),
        "ensuite": Q("bathroom_ensuite", "good", "fair"),
        "guest_wc": Q("wc", "poor", "good"),
        "maid_room": Q("maid", "proxy", "none", "no size statistics; do not warn on size"),
        "maid_bath": Q("bathroom", "poor", "fair", "lower tail only"),
        "driver_room": Q("maid", "none", "none", "no comparator; do not warn"),
        "driver_bath": Q("bathroom", "poor", "fair", "lower tail only"),
        "laundry": Q("laundry", "none", "proxy", "presence proxy only; do not warn on size"),
        "store": Q("storage", "fair", "good"),
        "plant": Q(None, "none", "none", "no comparator; do not warn"),
        "stair": Q("stair", "fair", "poor"),
        "balcony_terrace": Q("balcony_terrace", "fair", "good"),
    }

    out = {
        "schema_version": "1.0",
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "purpose": "TYPICALITY WARNINGS for the villa validator (villa_design.py / validate_plan.py). Never hard failures. "
                   "Both sources are APARTMENT datasets (South Asian listings; Swiss flats), not Gulf villas.",
        "units": "areas m2 (net polygon area inside walls), lengths m; percentiles are linear-interpolated over rooms "
                 "(room stats) or dwellings (dwelling stats)",
        "schema": {
            "room_types.<type>.<source>": "normalised room stats: segment, source_key, match, n, area_m2 {p5,p25,p50,p75,p95,mean}, "
                                          "short_side_m, long_side_m, aspect_ratio {p50,p75,p95}, doors_per_room {mean,p50,p95,share_by_count}, "
                                          "links {door, access|door_or_open, adjacent -> {target_type: share}}, other_segments",
            "dwelling.<metric>.<source>": "dwelling-level stats (circulation share, bathrooms per bedroom, counts, kitchen mode ...)",
            "villa_role_map.<role>": "villa_design.py ROLE -> room_types key, with match quality per source",
            "match": "good | fair | poor | proxy | none. Warn only on good/fair; poor = info; proxy/none = never warn.",
            "segment": "which subset the numbers come from. Defaults: resplan bed4plus (>= 4 bedrooms), swiss bedrooms_ge4 "
                       f"(>= 4 bedrooms); a type with fewer than {MIN_N} rooms falls back to the next segment "
                       "(resplan: house_like, all; swiss: rooms_ge4, all; stair: multi_floor).",
        },
        "sources": {
            "resplan": {
                "title": R["dataset"]["name"],
                "url": R["dataset"]["repo"],
                "file": "ResPlan.zip (GitHub, commit 4b02e05, 'dataset v8'), sha256 " + R["dataset"]["zip_sha256"],
                "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
                "licence_evidence": R["licence"]["source_of_statement"],
                "licence_discrepancy": R["licence"]["DISCREPANCY"],
                "attribution": "Statistics derived from the ResPlan dataset (The ResPlan Authors, 2025), "
                               "https://github.com/m-agour/ResPlan, licensed CC BY 4.0 "
                               "(https://creativecommons.org/licenses/by/4.0/). Aggregated and re-scaled by this project; "
                               "not endorsed by the authors.",
                "n_units_used": R["plan_counts"]["used"],
                "scale": {"note": R["method"]["calibration_uncertainty"],
                          "length_factor_range": [0.85, 1.0], "area_factor_range": [0.72, 1.0]},
                "full_stats": RESPLAN, "full_stats_sha256": sha256(RESPLAN),
            },
            "swiss": {
                "title": S["source"]["title"],
                "url": S["source"]["zenodo_record_resolved"], "doi": S["source"]["doi"],
                "creators": S["source"]["creators"],
                "file": "swiss-dwellings-v3.0.0.zip member geometries.csv only (CRC-32 0x1be5b7b9 matches the archive)",
                "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "licence_evidence": S["source"]["licence"]["verified_how"],
                "attribution": "Statistics derived from Swiss Dwellings v3.0.0 (Standfest, Franzen, Schroeder, Gonzalez Medina, "
                               "Villanueva Hernandez, Buck, Tan, Niedzwiecka, Colmegna; Archilyse AG), Zenodo, "
                               "doi:10.5281/zenodo.7788422, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). "
                               "Aggregated by this project; not endorsed by the authors.",
                "n_units_used": S["qa"]["n_layouts_explicit_labels"],
                "full_stats": SWISS, "full_stats_sha256": sha256(SWISS),
            },
        },
        "validator_guidance": {
            "severity": "WARN or INFO only. Never FAIL/MAJOR on these numbers.",
            "size_low_side": "area_m2 / short_side_m below p5 of a good/fair source -> WARN; between p5 and p25 -> no message. "
                             "Before comparing with ResPlan sizes multiply its p-values by sources.resplan.scale "
                             "area_factor_range[0] (0.72) / length_factor_range[0] (0.85) so a listing-area inflation "
                             "cannot raise a false 'too small'.",
            "size_high_side": "above p95 -> INFO only (Gulf villas are expected to be larger than both apartment sets).",
            "aspect_ratio": "above p95 of both sources -> WARN; above p95 of one -> INFO.",
            "doors_per_room": "above p95 -> INFO (possible through-room); 0 doors on a room that needs one is a route check, not this file.",
            "links": "a villa link whose per-room share is < 0.02 in every source with that type (e.g. bedroom door to kitchen) -> INFO "
                     "'uncommon connection'. Gulf privacy rules stay in the route checks.",
            "circulation_share": "compare dedicated corridor+hall+landing area / net indoor area with swiss "
                                 "circulation_share_of_indoor_area: above p95 -> WARN, below p5 -> INFO.",
            "bathrooms_per_bedroom": "below resplan bed4plus p5 (0.75) -> WARN; the Swiss ratio (p50 0.5) is not a villa norm, "
                                     "never warn for exceeding it.",
            "message_format": "'<room> <metric> <value> is below/above the <pNN> (<value>) of <source> <segment> "
                              "(n=<n>)' plus the source's attribution line once per report.",
        },
        "villa_role_map": roles,
        "room_types": rt,
        "dwelling": dw,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    for t, v in rt.items():
        print(f"{t:18s}", {s: (x.get("segment"), x.get("n"), x.get("match")) if x else None for s, x in v.items()})


if __name__ == "__main__":
    main()
