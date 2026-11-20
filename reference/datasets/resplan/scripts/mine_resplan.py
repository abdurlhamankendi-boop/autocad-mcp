"""Mine typicality statistics from ResPlan (github.com/m-agour/ResPlan, data CC BY 4.0
per repo LICENSE) for the villa validator.

Stage 1 (this file, run as __main__): per-plan feature extraction -> records.pkl
Stage 2: aggregate_resplan.py -> ../resplan_stats.json

Connectivity logic is an independent re-implementation adapted from the ideas in
resplan_utils.plan_to_graph / add_adjacency_edges (MIT, (c) 2025 The ResPlan Authors),
re-expressed in metric units.
"""
import sys, os, math, time, pickle
import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(os.path.dirname(HERE), "work", "records.pkl")

ROOM_TYPES = ["living", "bedroom", "bathroom", "kitchen", "storage", "stair", "balcony"]
INTERIOR = {"living", "bedroom", "bathroom", "kitchen", "storage", "stair"}
MIN_PART_M2 = 0.5          # drop vectorisation crumbs smaller than this
MIN_LISTED_AREA = 20.0     # m2, QC
WT_RANGE = (0.08, 0.50)    # plausible wall thickness in metres, QC
CIRC_R = {"w1.5": 0.75, "w1.8": 0.90}   # half-widths for the corridor opening heuristic


def parts(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    out = []
    for x in getattr(g, "geoms", []):
        out.extend(parts(x))
    return out


def mrr_dims(poly):
    r = shapely.minimum_rotated_rectangle(poly)
    if r.geom_type != "Polygon":
        return 0.0, 0.0, 0.0
    c = np.asarray(r.exterior.coords)
    e = np.hypot(*np.diff(c, axis=0).T)
    a, b = float(e[0]), float(e[1])
    return max(a, b), min(a, b), r.area


def inscribed_width(poly):
    if isinstance(poly, MultiPolygon):
        poly = max(poly.geoms, key=lambda p: p.area)
    try:
        return 2.0 * shapely.maximum_inscribed_circle(poly, 0.01).length
    except Exception:
        return float("nan")


def n_vertices(poly):
    if isinstance(poly, MultiPolygon):
        return sum(len(p.exterior.coords) - 1 for p in poly.geoms)
    return len(poly.exterior.coords) - 1


def narrow_area(L, r):
    """Area of the parts of polygon L narrower than 2r (morphological opening residue),
    counting only pieces >= 1 m2 and at least 0.7 m wide (walkable)."""
    try:
        opened = L.buffer(-r, join_style=2).buffer(r, join_style=2)
        resid = L.difference(opened)
    except Exception:
        return float("nan"), float("nan"), float("nan")
    tot = 0.0
    for pc in parts(resid):
        if pc.area >= 1.0 and inscribed_width(pc) >= 0.7:
            tot += pc.area
    largest_broad = max((p.area for p in parts(opened)), default=0.0)
    return tot, opened.area, largest_broad


def process(plan):
    pid = int(plan["id"])
    if "area_change_sqft" in plan:
        return {"id": pid, "skip": "augmented"}
    inner = plan.get("inner")
    area = float(plan.get("area") or 0.0)
    if inner is None or inner.is_empty or inner.area <= 0:
        return {"id": pid, "skip": "no_inner"}
    if area < MIN_LISTED_AREA:
        return {"id": pid, "skip": "listed_area_lt_20"}
    s = math.sqrt(area / inner.area)          # metres per canvas unit
    wt = float(plan["wall_depth"]) * s        # wall thickness, metres
    if not (WT_RANGE[0] <= wt <= WT_RANGE[1]):
        return {"id": pid, "skip": "wall_thickness_out_of_range"}

    def sc(g):
        if g is None or g.is_empty:
            return None
        # scale, then validate PART BY PART (never merge touching rooms of one type)
        ps = []
        for p in parts(affinity.scale(g, s, s, origin=(0, 0))):
            if p.is_valid:
                ps.append(p)
            else:
                ps.extend(parts(shapely.make_valid(p)))
        return MultiPolygon(ps) if ps else None

    walls = unary_union(parts(sc(plan.get("wall")))) if sc(plan.get("wall")) is not None else None
    buf = 0.007 * 256.0 * s                  # same scale-aware buffer as plan_to_graph

    nodes = []                               # (type, geom)
    dropped_crumbs = 0
    lp = [p for p in parts(sc(plan.get("living")))]
    lp_keep = [p for p in lp if p.area >= MIN_PART_M2]
    dropped_crumbs += len(lp) - len(lp_keep)
    living_parts_areas = [p.area for p in lp_keep]
    if lp_keep:
        nodes.append(("living", unary_union(lp_keep)))
    for t in ["bedroom", "bathroom", "kitchen", "storage", "stair", "balcony"]:
        for p in parts(sc(plan.get(t))):
            if p.area >= MIN_PART_M2:
                nodes.append((t, p))
            else:
                dropped_crumbs += 1
    n = len(nodes)
    geoms = [g for _, g in nodes]
    types = [t for t, _ in nodes]
    nbuf = [g.buffer(buf) for g in geoms]

    door_count = [0] * n
    door_edges = set()
    door_widths_int, door_widths_single = [], []
    doors = [d for d in parts(sc(plan.get("door")))]
    for d in doors:
        touching = [i for i in range(n) if d.intersects(nbuf[i])]
        if len(touching) > 2:
            sc_ = sorted(((i, d.boundary.intersection(geoms[i].buffer(buf * 0.6)).length) for i in touching),
                         key=lambda x: -x[1])
            touching = [sc_[0][0]] + ([sc_[1][0]] if sc_[1][1] > 0 else [])
        w = mrr_dims(d)[0]
        for i in touching:
            door_count[i] += 1
        if len(touching) == 2:
            door_edges.add(tuple(sorted(touching)))
            door_widths_int.append(w)
        elif len(touching) == 1:
            door_widths_single.append(w)

    # windows shared by two rooms (e.g. bathroom -> balcony ventilation window)
    window_edges = set()
    wins = [w for w in parts(sc(plan.get("window")))]
    for wg in wins:
        touching = [i for i in range(n) if wg.intersects(nbuf[i])]
        if len(touching) > 2:
            sc_ = sorted(((i, wg.boundary.intersection(geoms[i].buffer(buf * 0.6)).length) for i in touching),
                         key=lambda x: -x[1])
            touching = [sc_[0][0]] + ([sc_[1][0]] if sc_[1][1] > 0 else [])
        if len(touching) == 2:
            e = tuple(sorted(touching))
            if e not in door_edges:
                window_edges.add(e)
    # obstacles for the open-passage test: walls, doors and windows
    obst = ([walls] if walls is not None else []) + doors + wins
    obstacles = unary_union(obst) if obst else None
    # windows shared by two INTERIOR rooms are treated as openings (resplan_utils promotes
    # them to via_door); the rest (e.g. bathroom->balcony) stay plain windows
    iwin_edges = {e for e in window_edges if types[e[0]] in INTERIOR and types[e[1]] in INTERIOR}
    window_edges -= iwin_edges

    entry = [False] * n
    fd_widths = []
    for fd in parts(sc(plan.get("front_door"))):
        fd_widths.append(mrr_dims(fd)[0])
        fb = fd.buffer(buf)
        for i in range(n):
            if fb.intersects(geoms[i]):
                entry[i] = True

    open_edges, adj_edges = set(), set()
    for i in range(n):
        for j in range(i + 1, n):
            a, b = geoms[i], geoms[j]
            if a.distance(b) > 1.5 * wt:
                continue
            # shared-wall adjacency (paper-style 'adjacency', but requiring >= 0.5 m of contact)
            try:
                contact = a.boundary.intersection(b.buffer(1.3 * wt))
                clen = contact.length
            except Exception:
                contact, clen = None, 0.0
            if clen >= 0.5:
                adj_edges.add((i, j))
            if (i, j) in door_edges or (i, j) in window_edges or (i, j) in iwin_edges:
                continue
            # open passage: dilated overlap minus walls/doors/windows, walkable extent
            is_open = False
            try:
                gap = a.buffer(0.55 * wt).intersection(b.buffer(0.55 * wt))
                if not gap.is_empty:
                    if obstacles is not None:
                        gap = gap.difference(shapely.clip_by_rect(obstacles, *gap.bounds))
                    for pc in parts(gap):
                        x1, y1, x2, y2 = pc.bounds
                        if max(x2 - x1, y2 - y1) >= 2 * wt and pc.area >= 0.25 * wt * wt:
                            is_open = True
                            break
                if not is_open and contact is not None and clen >= 2 * wt:
                    seg = contact
                    if obstacles is not None:
                        seg = contact.difference(shapely.clip_by_rect(obstacles, *contact.bounds).buffer(0.5 * s))
                    lens = [g.length for g in getattr(seg, "geoms", [seg])] if not seg.is_empty else []
                    if max(lens, default=0.0) >= 2 * wt:
                        is_open = True
            except Exception:
                pass
            if is_open:
                open_edges.add((i, j))
    for e in door_edges | open_edges | window_edges | iwin_edges:
        adj_edges.add(e)
    access_edges = door_edges | open_edges | iwin_edges

    rooms = []
    for i, (t, g) in enumerate(nodes):
        L, S, mrr_a = mrr_dims(g)
        acc_door = sorted({types[j] for e in door_edges for j in e if i in e and j != i})
        acc_open = sorted({types[j] for e in open_edges for j in e if i in e and j != i})
        acc_iwin = sorted({types[j] for e in iwin_edges for j in e if i in e and j != i})
        adj = sorted({types[j] for e in adj_edges for j in e if i in e and j != i})
        # neighbour ids for ensuite logic
        acc_ids = sorted({j for e in access_edges for j in e if i in e and j != i})
        rooms.append(dict(i=i, type=t, area=g.area, long=L, short=S,
                          aspect=(L / S) if S > 0 else float("nan"),
                          rect=(g.area / mrr_a) if mrr_a > 0 else float("nan"),
                          inscribed=inscribed_width(g), nv=n_vertices(g),
                          doors=door_count[i], entry=entry[i],
                          acc_door=acc_door, acc_open=acc_open, acc_iwin=acc_iwin, adj=adj, acc_ids=acc_ids))

    # bedroom roles
    beds = [r for r in rooms if r["type"] == "bedroom"]
    if len(beds) >= 2:
        m = max(beds, key=lambda r: r["area"])
        for r in beds:
            r["role"] = "master" if r is m else "other"
    # bathroom roles
    for r in rooms:
        if r["type"] != "bathroom":
            continue
        nb_types = {types[j] for j in r["acc_ids"]}
        if "bedroom" in nb_types and not (nb_types & {"living", "kitchen"}):
            r["role"] = "ensuite"
        elif "bedroom" in nb_types:
            r["role"] = "shared"
        else:
            r["role"] = "common"
    for r in beds:
        r["has_ensuite"] = any(rooms[j]["type"] == "bathroom" and rooms[j].get("role") == "ensuite"
                               for j in r["acc_ids"])

    net_interior = sum(g.area for t, g in nodes if t in INTERIOR)
    living_zone = next((g for t, g in nodes if t == "living"), None)
    circ = {}
    if living_zone is not None:
        for k, r in CIRC_R.items():
            na, broad, largest = narrow_area(living_zone, r)
            circ[k] = dict(narrow=na, broad=broad, largest_broad=largest)
    stair_area = sum(g.area for t, g in nodes if t == "stair")

    def has(k):
        v = plan.get(k)
        return v is not None and not v.is_empty

    rec = dict(id=pid, s=s, wt=wt, listed_area=area, net_interior=net_interior,
               balcony_area=sum(g.area for t, g in nodes if t == "balcony"),
               living_zone_area=(living_zone.area if living_zone is not None else 0.0),
               living_parts_areas=living_parts_areas,
               stair_area=stair_area, circ=circ,
               n={t: types.count(t) for t in ROOM_TYPES},
               has_garden=has("garden"), has_parking=has("parking"), has_stair=has("stair"),
               has_pool=has("pool"),
               n_doors=len(doors), door_w_int=door_widths_int, door_w_single=door_widths_single,
               fd_w=fd_widths, fd_types=sorted({types[i] for i in range(n) if entry[i]}),
               door_pairs=sorted("|".join(sorted((types[a], types[b]))) for a, b in door_edges),
               open_pairs=sorted("|".join(sorted((types[a], types[b]))) for a, b in open_edges),
               window_pairs=sorted("|".join(sorted((types[a], types[b]))) for a, b in window_edges),
               iwin_pairs=sorted("|".join(sorted((types[a], types[b]))) for a, b in iwin_edges),
               adj_pairs=sorted("|".join(sorted((types[a], types[b]))) for a, b in adj_edges),
               dropped_crumbs=dropped_crumbs, rooms=rooms)
    return rec


def _work(plan):
    try:
        return process(plan)
    except Exception as e:  # never kill the pool on one bad plan
        return {"id": int(plan.get("id", -1)), "skip": "error: %s" % (type(e).__name__,), "err": str(e)[:200]}


if __name__ == "__main__":
    from rp_load import load
    import multiprocessing as mp
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    t0 = time.time()
    data = load()
    if limit:
        data = data[:limit]
    print("loaded", len(data), round(time.time() - t0, 1), "s", flush=True)
    recs = []
    if nproc <= 1:
        for k, p in enumerate(data):
            recs.append(_work(p))
    else:
        with mp.Pool(nproc) as pool:
            for k, r in enumerate(pool.imap(_work, data, chunksize=40)):
                recs.append(r)
                if k % 2000 == 0:
                    print(k, round(time.time() - t0, 1), "s", flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = OUT if not limit else OUT.replace(".pkl", "_test.pkl")
    with open(out, "wb") as f:
        pickle.dump(recs, f)
    from collections import Counter
    print("done", len(recs), "in", round(time.time() - t0, 1), "s ->", out)
    print(Counter(r.get("skip", "ok") for r in recs))
