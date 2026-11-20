"""Skeptic spot-check: recompute Swiss Dwellings numbers straight from
geometries.csv (streamed out of the local zip; no SQLite staging, no reuse of
mine.py) and compare with room_stats.json.

Checks
  C. bedrooms_ge4 bedroom area p50 (+ n), master-proxy area p50,
     circulation share p50; and the same for rooms_ge4
"""
import csv, io, json, zipfile, collections
import numpy as np
import shapely
from shapely import from_wkt

ZIP = r"C:\Users\lsire\autocad-mcp\reference\datasets\swiss\swiss-dwellings-v3.0.0_geometries.zip"
STATS = r"C:\Users\lsire\.claude\skills\architectural-cad\references\room_stats.json"
FULL = r"C:\Users\lsire\autocad-mcp\reference\datasets\swiss_stats.json"
OUT = r"C:\Users\lsire\autocad-mcp\reference\datasets\merge\spotcheck_swiss.json"
csv.field_size_limit(1 << 30)

CORR = {"CORRIDOR", "CORRIDORS_AND_HALLS", "LOBBY", "FOYER"}
NOT_INDOOR = {  # technical, basement and outdoor subtypes are outside the indoor net area
    "SHAFT", "ELEVATOR", "VOID", "LIGHTWELL", "OUTDOOR_VOID", "TECHNICAL_AREA", "HEATING", "NOT_DEFINED", "AIR",
    "TRANSPORT_SHAFT", "ELEVATOR_FACILITIES", "ELECTRICAL_SUPPLY", "WATER_SUPPLY", "GAS", "OIL_TANK",
    "HOUSE_TECHNICS_FACILITIES", "OFFICE_TECH_ROOM", "BASEMENT_COMPARTMENT", "BASEMENT",
    "BALCONY", "LOGGIA", "TERRACE", "WINTERGARTEN", "PATIO", "GARDEN"}


def area_of(wkt):
    g = from_wkt(wkt)
    if g is None or g.is_empty:
        return 0.0
    if not g.is_valid:
        g = shapely.make_valid(g)
    return float(g.area)   # lines/points in a repaired collection contribute 0


apt_areas = collections.defaultdict(dict)       # apt -> area_id -> (subtype, m2)
apt_usage = collections.defaultdict(set)
apt_floor = collections.defaultdict(set)
z = zipfile.ZipFile(ZIP)
with io.TextIOWrapper(z.open(z.infolist()[0]), encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh)
    h = {k: i for i, k in enumerate(next(rd))}
    for row in rd:
        if row[h["entity_type"]] != "area" or not row[h["apartment_id"]]:
            continue
        apt = row[h["site_id"]] + ":" + row[h["apartment_id"]]
        aid = row[h["area_id"]]
        apt_usage[apt].add(row[h["unit_usage"]])
        apt_floor[apt].add(row[h["floor_id"]])
        if aid not in apt_areas[apt]:
            apt_areas[apt][aid] = (row[h["entity_subtype"]], area_of(row[h["geometry"]]))

reps = {}
for apt in sorted(apt_areas):
    if apt_usage[apt] != {"RESIDENTIAL"} or len(apt_floor[apt]) > 6:
        continue
    reps.setdefault(frozenset(apt_areas[apt]), apt)

G = {"rooms_ge4": {"bed": [], "master": [], "circ": []}, "bedrooms_ge4": {"bed": [], "master": [], "circ": []}}
for sig, apt in reps.items():
    A = [(st, a) for st, a in apt_areas[apt].values() if a > 0]
    if len(A) < 2:
        continue
    c = collections.Counter(st for st, _ in A)
    hb, hl, hr = c["BEDROOM"] > 0, c["LIVING_ROOM"] + c["LIVING_DINING"] > 0, c["ROOM"] > 0
    if hr and not hb and not hl:
        continue                                   # generic-ROOM scheme: excluded from the groups
    beds = sorted((a for st, a in A if st == "BEDROOM" or (st == "ROOM" and hl and not hb)), reverse=True)
    indoor = sum(a for st, a in A if st not in NOT_INDOOR)
    if indoor < 15:
        continue
    circ = sum(a for st, a in A if st in CORR or st == "STAIRCASE") / indoor
    n_rooms = c["ROOM"] + c["BEDROOM"] + c["LIVING_ROOM"] + c["LIVING_DINING"]
    for g, ok in (("rooms_ge4", n_rooms >= 4), ("bedrooms_ge4", len(beds) >= 4)):
        if ok:
            G[g]["bed"] += beds
            G[g]["circ"].append(circ)
            if len(beds) >= 2:
                G[g]["master"].append(beds[0])

J = json.load(open(STATS, encoding="utf-8"))
F = json.load(open(FULL, encoding="utf-8"))
p50 = lambda v: round(float(np.percentile(v, 50)), 3)
res = {"unique_layouts_selected": len(reps)}
for g in G:
    fg = F["groups"][g]
    res[g] = {
        "n_layouts": {"recomputed": len(G[g]["circ"]), "stats": fg["dwelling"]["n_layouts"]},
        "bedroom_n": {"recomputed": len(G[g]["bed"]), "stats": fg["rooms"]["bedroom"]["n_rooms"]},
        "bedroom_area_p50": {"recomputed": p50(G[g]["bed"]), "stats": fg["rooms"]["bedroom"]["area_m2"]["p50"]},
        "master_proxy_area_p50": {"recomputed": p50(G[g]["master"]),
                                  "stats": fg["rooms_derived"]["bedroom_master_proxy"]["area_m2"]["p50"]},
        "circulation_share_p50": {"recomputed": p50(G[g]["circ"]),
                                  "stats": fg["dwelling"]["circulation_share_of_indoor_area"]["p50"]},
    }
res["room_stats_json_values"] = {
    "bedroom_area_p50": J["room_types"]["bedroom"]["swiss"]["area_m2"]["p50"],
    "bedroom_master_area_p50": J["room_types"]["bedroom_master"]["swiss"]["area_m2"]["p50"],
    "circulation_share_p50": J["dwelling"]["circulation_share"]["swiss"]["circulation_share_of_indoor_area"]["p50"],
    "segment": J["room_types"]["bedroom"]["swiss"]["segment"],
}
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
print(json.dumps(res, indent=1))
