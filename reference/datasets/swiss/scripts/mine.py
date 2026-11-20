"""Mine room-typicality statistics from Swiss Dwellings v3.0.0 geometries (staged in SQLite).

Usage: python mine.py <sd.sqlite> <out.json> [limit]
"""
import sqlite3, json, sys, math, time, collections
import numpy as np
import shapely
from shapely import from_wkt

DB, OUT = sys.argv[1], sys.argv[2]
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else None

# ------------------------------------------------------------------ mapping
CANON = {
    'LIVING_ROOM': 'living', 'LIVING_DINING': 'living',
    'DINING': 'dining',
    'KITCHEN': 'kitchen', 'KITCHEN_DINING': 'kitchen',
    'BEDROOM': 'bedroom',
    # ROOM and BATHROOM are resolved per dwelling (see classify())
    'CORRIDOR': 'corridor', 'CORRIDORS_AND_HALLS': 'corridor', 'LOBBY': 'corridor', 'FOYER': 'corridor',
    'STAIRCASE': 'stair',
    'STOREROOM': 'storage', 'CLOAKROOM': 'storage',
    'BALCONY': 'balcony_terrace', 'LOGGIA': 'balcony_terrace', 'TERRACE': 'balcony_terrace',
    'WINTERGARTEN': 'balcony_terrace', 'PATIO': 'balcony_terrace',
    'GARDEN': 'garden',
    'WASH_AND_DRY_ROOM': 'laundry',
    'OFFICE': 'study', 'OFFICE_SPACE': 'study', 'STUDIO': 'study',
    'BASEMENT_COMPARTMENT': 'basement_storage', 'BASEMENT': 'basement_storage',
}
TECH = {'SHAFT', 'ELEVATOR', 'VOID', 'LIGHTWELL', 'OUTDOOR_VOID', 'TECHNICAL_AREA', 'HEATING', 'NOT_DEFINED',
        'AIR', 'TRANSPORT_SHAFT', 'ELEVATOR_FACILITIES', 'ELECTRICAL_SUPPLY', 'WATER_SUPPLY', 'GAS', 'OIL_TANK',
        'HOUSE_TECHNICS_FACILITIES', 'OFFICE_TECH_ROOM'}
INDOOR = {'living', 'dining', 'kitchen', 'bedroom', 'bathroom', 'wc', 'sanitary_nofixture', 'corridor', 'stair',
          'storage', 'laundry', 'study', 'other'}
OUTDOOR = {'balcony_terrace', 'garden'}
MAIN_TYPES = ['living', 'dining', 'kitchen', 'bedroom', 'bathroom', 'wc', 'corridor', 'stair', 'storage',
              'balcony_terrace', 'laundry', 'study', 'sanitary_nofixture', 'garden']
LINK_TYPES = MAIN_TYPES + ['ENTRANCE', 'EXTERNAL']
DERIVED = ['bedroom_master_proxy', 'bedroom_secondary', 'bathroom_ensuite', 'bathroom_shared',
           'hall_entrance', 'corridor_internal']

# thresholds (metres)
OPEN_TOL = 0.05        # opening<->area snapping distance
OPEN_MIN_CONTACT = 0.20
SPLIT_TOL = 0.02       # two areas this close share an open boundary (area splitter, no wall)
SPLIT_MIN_LEN = 0.50
ADJ_BUF = 0.30         # each side -> areas <= 0.6 m apart (i.e. across a wall) are tested
ADJ_MIN_FACING = 1.00


def clean(g):
    if g is None or g.is_empty:
        return None
    if not g.is_valid:
        g = shapely.make_valid(g)
        if g.geom_type == 'GeometryCollection':
            polys = [p for p in g.geoms if p.geom_type in ('Polygon', 'MultiPolygon')]
            if not polys:
                return None
            g = shapely.union_all(polys)
    if g.area <= 0:
        return None
    return g


def mrr_sides(g):
    r = shapely.minimum_rotated_rectangle(g)
    if r.geom_type != 'Polygon':
        return None, None
    c = list(r.exterior.coords)
    a = math.dist(c[0], c[1]); b = math.dist(c[1], c[2])
    return (min(a, b), max(a, b))


# ------------------------------------------------------------------ select layouts
con = sqlite3.connect(DB)
apt_area = collections.defaultdict(set); apt_usage = collections.defaultdict(set); apt_floor = collections.defaultdict(set)
for apt, aid, usage, floor in con.execute("SELECT apt, area_id, usage, floor FROM g WHERE et='area'"):
    apt_area[apt].add(aid); apt_usage[apt].add(usage); apt_floor[apt].add(floor)
reps = {}; inst = collections.Counter(); skipped = collections.Counter()
for apt in sorted(apt_area):
    if apt_usage[apt] != {'RESIDENTIAL'}:
        skipped['non_residential'] += 1; continue
    if len(apt_floor[apt]) > 6:
        skipped['more_than_6_floors'] += 1; continue
    sig = frozenset(apt_area[apt])
    inst[sig] += 1
    reps.setdefault(sig, apt)
rep_list = sorted(reps.items(), key=lambda kv: kv[1])
if LIMIT:
    rep_list = rep_list[:LIMIT]
print('residential apartments', sum(inst.values()), 'unique layouts', len(reps), 'skipped', dict(skipped), flush=True)

# ------------------------------------------------------------------ per-dwelling processing
QA = collections.Counter()
dwellings = []   # dicts
rooms = []       # dicts


def process(apt, n_inst):
    rows = con.execute("SELECT floor, area_id, et, st, geom FROM g WHERE apt=?", (apt,)).fetchall()
    areas = {}; feats = collections.defaultdict(set); opens = []; fgeoms = []
    for floor, aid, et, st, geom in rows:
        if et == 'area':
            if aid in areas:
                continue
            g = clean(from_wkt(geom))
            if g is None:
                QA['area_bad_geom'] += 1; continue
            areas[aid] = dict(id=aid, raw=st, floor=floor, g=g)
        elif et == 'feature':
            feats[aid].add(st)
            if st in ('STAIRS', 'WASHING_MACHINE'):
                fg = clean(from_wkt(geom))
                if fg is not None:
                    fgeoms.append((st, aid, fg, floor))
        elif et == 'opening':
            g = clean(from_wkt(geom))
            if g is None:
                QA['opening_bad_geom'] += 1; continue
            opens.append((floor, st, g))
    if len(areas) < 2:
        QA['dwelling_lt2_areas'] += 1
        return
    raw_counts = collections.Counter(a['raw'] for a in areas.values())
    hb = raw_counts['BEDROOM'] > 0
    hl = raw_counts['LIVING_ROOM'] + raw_counts['LIVING_DINING'] > 0
    hr = raw_counts['ROOM'] > 0
    scheme = ('B' if hb else '-') + ('L' if hl else '-') + ('R' if hr else '-')
    heuristic = scheme == '--R'
    room_areas = sorted((a for a in areas.values() if a['raw'] == 'ROOM'), key=lambda a: -a['g'].area)
    for a in areas.values():
        raw = a['raw']
        if raw == 'ROOM':
            if hl and not hb:
                c = 'bedroom'
            elif hb:
                c = 'study'           # ROOM next to explicit BEDROOM + LIVING labels
            else:                     # generic scheme: largest ROOM -> living (heuristic)
                c = 'living' if a is room_areas[0] else 'bedroom'
        elif raw == 'BATHROOM':
            f = feats.get(a['id'], set())
            if 'SHOWER' in f or 'BATHTUB' in f:
                c = 'bathroom'
            elif 'TOILET' in f:
                c = 'wc'
            else:
                c = 'sanitary_nofixture'
        elif raw in TECH:
            c = None
        else:
            c = CANON.get(raw, 'other')
        a['c'] = c
        a['feats'] = feats.get(a['id'], set())
        a.update(doors=0, open=0, windows=0, entrance=False, door_w=[], nb_door=set(), nb_open=set(), nb_adj=set(),
                 nb_door_ids=set())
    # per floor geometry relations
    edges = []  # (typeA, typeB, kind)
    by_floor = collections.defaultdict(list)
    for a in areas.values():
        if a['c'] is not None:
            by_floor[a['floor']].append(a)
    for floor, (A) in by_floor.items():
        polys = np.array([a['g'] for a in A], dtype=object)
        for (fl, st, d) in (o for o in opens if o[0] == floor):
            near = np.nonzero(shapely.dwithin(polys, d, OPEN_TOL))[0]
            if len(near) == 0:
                QA[f'{st}_matched_0'] += 1; continue
            db = d.buffer(OPEN_TOL)
            cands = []
            for i in near:
                contact = A[i]['g'].boundary.intersection(db).length
                if contact >= OPEN_MIN_CONTACT:
                    cands.append((contact, i))
            cands.sort(reverse=True)
            cands = [A[i] for _, i in cands[:2]]
            QA[f'{st}_matched_{len(cands)}'] += 1
            if st == 'WINDOW':
                for a in cands:
                    a['windows'] += 1
                continue
            s, l = mrr_sides(d)
            for a in cands:
                a['doors'] += 1
                if l:
                    a['door_w'].append(l)
            if st == 'ENTRANCE_DOOR':
                for a in cands:
                    a['entrance'] = True
                    edges.append((a['c'], 'ENTRANCE', 'door'))
            if len(cands) == 2:
                x, y = cands
                x['nb_door'].add(y['c']); y['nb_door'].add(x['c'])
                x['nb_door_ids'].add(y['id']); y['nb_door_ids'].add(x['id'])
                if st == 'DOOR':
                    edges.append((x['c'], y['c'], 'door'))
            elif len(cands) == 1 and st == 'DOOR':
                cands[0]['nb_door'].add('EXTERNAL')
                edges.append((cands[0]['c'], 'EXTERNAL', 'door'))
        # area-area relations
        bufs = [a['g'].buffer(ADJ_BUF) for a in A]
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                gi, gj = A[i]['g'], A[j]['g']
                dist = gi.distance(gj)
                if dist > 2 * ADJ_BUF:
                    continue
                if dist <= SPLIT_TOL:
                    shared = gi.boundary.intersection(gj.buffer(SPLIT_TOL)).length
                    if shared >= SPLIT_MIN_LEN:
                        A[i]['open'] += 1; A[j]['open'] += 1
                        A[i]['nb_open'].add(A[j]['c']); A[j]['nb_open'].add(A[i]['c'])
                        A[i]['nb_door_ids'].add(A[j]['id']); A[j]['nb_door_ids'].add(A[i]['id'])
                        edges.append((A[i]['c'], A[j]['c'], 'open'))
                inter = bufs[i].intersection(bufs[j])
                if inter.is_empty:
                    continue
                s, l = mrr_sides(inter)
                if l and l >= ADJ_MIN_FACING:
                    A[i]['nb_adj'].add(A[j]['c']); A[j]['nb_adj'].add(A[i]['c'])
    # ---------------- dwelling summary
    live = [a for a in areas.values() if a['c'] is not None]
    for a in live:
        s, l = mrr_sides(a['g'])
        a['area'] = a['g'].area
        a['short'] = s; a['long'] = l
        a['aspect'] = (l / s) if s and s > 0 else None
        a['rect'] = a['area'] / (s * l) if s and l else None
    tc = collections.Counter(a['c'] for a in live)
    indoor = sum(a['area'] for a in live if a['c'] in INDOOR)
    if indoor < 15:
        QA['dwelling_indoor_lt15m2'] += 1
        return
    outdoor = sum(a['area'] for a in live if a['c'] == 'balcony_terrace')
    circ = sum(a['area'] for a in live if a['c'] in ('corridor', 'stair'))
    corr = sum(a['area'] for a in live if a['c'] == 'corridor')
    n_bed = tc['bedroom']; n_bath = tc['bathroom']; n_wc = tc['wc']
    # derived subtypes
    beds = sorted((a for a in live if a['c'] == 'bedroom'), key=lambda a: -a['area'])
    for k, a in enumerate(beds):
        a['derived'] = ('bedroom_master_proxy' if k == 0 else 'bedroom_secondary') if len(beds) >= 2 else None
    ids = {a['id']: a for a in live}
    ensuite_any = False
    for a in live:
        if a['c'] == 'bathroom':
            linked_bed = any(ids[i]['c'] == 'bedroom' for i in a['nb_door_ids'] if i in ids)
            a['derived'] = 'bathroom_ensuite' if linked_bed else 'bathroom_shared'
            ensuite_any |= linked_bed
        elif a['c'] == 'corridor':
            a['derived'] = 'hall_entrance' if a['entrance'] else 'corridor_internal'
        elif a['c'] != 'bedroom':
            a['derived'] = None
    kit = [a for a in live if a['c'] == 'kitchen']
    if not kit:
        kmode = 'no_kitchen_area'
    elif any(('living' in a['nb_open']) or ('dining' in a['nb_open']) for a in kit):
        kmode = 'open_to_living_or_dining'
    else:
        kmode = 'enclosed'
    entr = sorted({a['c'] for a in live if a['entrance']})
    stairs = []; wm_hosts = []
    stair_pieces = collections.defaultdict(list)
    for st, aid, fg, fl in fgeoms:
        if st == 'STAIRS':
            stair_pieces[fl].append(fg)
        else:
            wm_hosts.append(areas[aid]['c'] if aid in areas and areas[aid].get('c') else 'unknown')
    for fl, pieces in stair_pieces.items():
        # STAIRS fixtures are drawn as several pieces (treads / flights / landings): merge touching pieces
        merged = shapely.union_all([p.buffer(0.03) for p in pieces]).buffer(-0.03)
        comps = list(merged.geoms) if hasattr(merged, 'geoms') else [merged]
        for comp in comps:
            if comp.is_empty or comp.area < 0.5:
                continue
            s, l = mrr_sides(comp)
            hosts = [(comp.intersection(a['g']).area, a['c']) for a in by_floor.get(fl, [])]
            hosts = [h for h in hosts if h[0] > 0]
            host = max(hosts)[1] if hosts else 'unknown'
            stairs.append(dict(area=comp.area, short=s, long=l, host=host))
    dw = dict(idx=len(dwellings), apt=apt, n_inst=n_inst, scheme=scheme, heuristic=heuristic,
              n_floors=len({a['floor'] for a in live}),
              n_rooms_swiss=raw_counts['ROOM'] + raw_counts['BEDROOM'] + raw_counts['LIVING_ROOM'] + raw_counts['LIVING_DINING'],
              n_bedrooms=n_bed, n_bathrooms=n_bath, n_wc=n_wc, n_sanitary_nofixture=tc['sanitary_nofixture'],
              n_living=tc['living'], n_kitchen=tc['kitchen'], n_dining=tc['dining'],
              indoor_m2=indoor, outdoor_m2=outdoor, circ_share=circ / indoor, corridor_share=corr / indoor,
              kitchen_mode=kmode, ensuite=ensuite_any, entrance_into=entr,
              has_corridor=tc['corridor'] > 0, has_storage=tc['storage'] > 0, has_laundry=tc['laundry'] > 0,
              has_outdoor=outdoor > 0, stairs=stairs, wm_hosts=wm_hosts)
    dwellings.append(dw)
    for a in live:
        rooms.append(dict(dw=dw['idx'], c=a['c'], raw=a['raw'], derived=a.get('derived'), area=a['area'],
                          short=a['short'], long=a['long'], aspect=a['aspect'], rect=a['rect'],
                          doors=a['doors'], open=a['open'], windows=a['windows'], entrance=a['entrance'],
                          door_w=a['door_w'], nb_door=a['nb_door'], nb_open=a['nb_open'], nb_adj=a['nb_adj']))
    dw['edges'] = edges


t0 = time.time()
for k, (sig, apt) in enumerate(rep_list):
    process(apt, inst[sig])
    if k % 2000 == 0:
        print(k, len(rep_list), round(time.time() - t0, 1), 's', flush=True)
print('processed', len(dwellings), 'dwellings', len(rooms), 'rooms', round(time.time() - t0, 1), 's', flush=True)

# ------------------------------------------------------------------ statistics


def r3(x):
    return None if x is None else round(float(x), 3)


def pct(vals, ps=(5, 25, 50, 75, 95), mean=True):
    v = np.asarray([x for x in vals if x is not None and not (isinstance(x, float) and math.isnan(x))], dtype=float)
    if len(v) == 0:
        return {'n': 0}
    out = {'n': int(len(v))}
    for p in ps:
        out[f'p{p}'] = r3(np.percentile(v, p))
    if mean:
        out['mean'] = r3(v.mean())
    return out


def count_dist(vals, cap):
    v = list(vals)
    n = len(v)
    if n == 0:
        return {}
    c = collections.Counter(min(x, cap) for x in v)
    return {(f'{k}+' if k == cap else str(k)): r3(c[k] / n) for k in range(0, cap + 1)}


def room_block(R):
    if not R:
        return {'n': 0}
    rect = [r for r in R if r['rect'] and r['rect'] >= 0.9]
    dws = {r['dw'] for r in R}
    dw_all = [r['door_w'] for r in R]
    return {
        'n_rooms': len(R), 'n_dwellings': len(dws),
        'area_m2': pct([r['area'] for r in R]),
        'short_side_m': pct([r['short'] for r in R], ps=(5, 25, 50, 75, 95)),
        'long_side_m': pct([r['long'] for r in R], ps=(5, 50, 95)),
        'aspect_ratio': pct([r['aspect'] for r in R], ps=(50, 75, 95)),
        'rectangularity_p50': r3(np.median([r['rect'] for r in R if r['rect']])) if R else None,
        'near_rectangular_subset': {
            'definition': 'area / minimum-rotated-rectangle area >= 0.9',
            'share_of_rooms': r3(len(rect) / len(R)),
            'short_side_m': pct([r['short'] for r in rect], ps=(5, 50, 95), mean=False),
            'aspect_ratio': pct([r['aspect'] for r in rect], ps=(50, 95), mean=False),
        },
        'doors_per_room': {**pct([r['doors'] for r in R], ps=(50, 95)), 'share_by_count': count_dist((r['doors'] for r in R), 4)},
        'open_connections_per_room': {'mean': r3(np.mean([r['open'] for r in R])),
                                      'share_with_any': r3(np.mean([r['open'] > 0 for r in R]))},
        'door_or_open_connections_per_room': {**pct([r['doors'] + r['open'] for r in R], ps=(50, 95)),
                                              'share_by_count': count_dist((r['doors'] + r['open'] for r in R), 4)},
        'windows_per_room': {**pct([r['windows'] for r in R], ps=(50, 95)), 'share_with_none': r3(np.mean([r['windows'] == 0 for r in R]))},
        'share_containing_entrance_door': r3(np.mean([r['entrance'] for r in R])),
        'door_width_m': pct([w for ws in dw_all for w in ws], ps=(5, 50, 95), mean=False),
    }


def link_block(R, D):
    """P(room of type t1 has >=1 link to a t2 room)."""
    by_t = collections.defaultdict(list)
    for r in R:
        by_t[r['c']].append(r)
    res = {'door': {}, 'door_or_open': {}, 'shares_wall_or_boundary': {}}
    for t1 in MAIN_TYPES:
        rs = by_t.get(t1)
        if not rs or len(rs) < 20:
            continue
        n = len(rs)
        for key, getter in (('door', lambda r: r['nb_door']), ('door_or_open', lambda r: r['nb_door'] | r['nb_open']),
                            ('shares_wall_or_boundary', lambda r: r['nb_adj'] | r['nb_door'] | r['nb_open'])):
            row = {}
            for t2 in LINK_TYPES:
                if key == 'shares_wall_or_boundary' and t2 in ('ENTRANCE', 'EXTERNAL'):
                    continue
                p = sum(1 for r in rs if t2 in getter(r)) / n
                if p >= 0.005:
                    row[t2] = r3(p)
            res[key][t1] = dict(sorted(row.items(), key=lambda kv: -kv[1]))
    # edge (pair) frequencies over all links
    pair = collections.Counter(); kinds = collections.Counter()
    for d in D:
        for a, b, k in d['edges']:
            if b in ('ENTRANCE',):
                continue
            key = '|'.join(sorted((a, b)))
            pair[(key, k)] += 1; kinds[k] += 1
    res['link_pair_share'] = {}
    for k in ('door', 'open'):
        tot = kinds[k]
        if tot:
            res['link_pair_share'][k] = {key: r3(v / tot) for (key, kk), v in pair.most_common() if kk == k and v / tot >= 0.005}
    return res


def dwelling_block(D):
    n = len(D)
    if n == 0:
        return {'n': 0}
    multi = [d for d in D if d['n_bedrooms'] >= 2]
    out = {
        'n_layouts': n, 'n_apartment_instances': int(sum(d['n_inst'] for d in D)),
        'indoor_net_area_m2': pct([d['indoor_m2'] for d in D]),
        'outdoor_area_m2_if_any': pct([d['outdoor_m2'] for d in D if d['outdoor_m2'] > 0], ps=(5, 50, 95)),
        'share_with_outdoor_space': r3(np.mean([d['has_outdoor'] for d in D])),
        'circulation_share_of_indoor_area': {
            'definition': '(corridor/hall + internal stair areas) / indoor net area; open-plan circulation inside living areas is NOT counted',
            **pct([d['circ_share'] for d in D]),
            'share_with_zero': r3(np.mean([d['circ_share'] == 0 for d in D]))},
        'corridor_only_share_of_indoor_area': pct([d['corridor_share'] for d in D], ps=(5, 50, 95)),
        'n_rooms_swiss': count_dist((d['n_rooms_swiss'] for d in D), 8),
        'n_bedrooms': count_dist((d['n_bedrooms'] for d in D), 6),
        'n_full_bathrooms': count_dist((d['n_bathrooms'] for d in D), 4),
        'n_wc': count_dist((d['n_wc'] for d in D), 3),
        'n_floors': count_dist((d['n_floors'] for d in D), 3),
        'kitchen_mode_share': {k: r3(v / n) for k, v in collections.Counter(d['kitchen_mode'] for d in D).most_common()},
        'entrance_door_opens_into_share': {k: r3(v / n) for k, v in collections.Counter(
            t for d in D for t in (d['entrance_into'] or ['none_detected'])).most_common() if v / n >= 0.005},
        'share_with_corridor': r3(np.mean([d['has_corridor'] for d in D])),
        'share_with_storage_room': r3(np.mean([d['has_storage'] for d in D])),
        'share_with_laundry_room': r3(np.mean([d['has_laundry'] for d in D])),
        'share_with_any_ensuite': r3(np.mean([d['ensuite'] for d in D])),
    }
    wm = [h for d in D for h in d['wm_hosts']]
    out['in_unit_washing_machine'] = {
        'definition': 'WASHING_MACHINE fixture drawn inside the dwelling (Swiss laundry is usually a shared basement room, so this is the in-unit laundry proxy)',
        'share_of_dwellings': r3(np.mean([len(d['wm_hosts']) > 0 for d in D])),
        'host_room_share': {k: r3(v / len(wm)) for k, v in collections.Counter(wm).most_common()} if wm else {},
    }
    st = [s for d in D for s in d['stairs']]
    out['internal_stair_fixture'] = {
        'definition': 'STAIRS fixtures inside the dwelling, touching pieces merged per floor into footprints >= 0.5 m2 (maisonette stairs are mostly drawn as a fixture inside a corridor/living area, not as a STAIRCASE area). '
                      'Dimensions are of the minimum rotated rectangle: for straight flights short side ~ flight width and long side ~ run; for L/U/winder stairs they describe the stair well footprint',
        'share_of_dwellings_with_stair_fixture': r3(np.mean([len(d['stairs']) > 0 for d in D])),
    }
    if len(st) >= 20:
        out['internal_stair_fixture'].update({
            'footprint_m2': pct([s['area'] for s in st], ps=(5, 25, 50, 75, 95)),
            'width_short_side_m': pct([s['short'] for s in st], ps=(5, 25, 50, 75, 95)),
            'run_long_side_m': pct([s['long'] for s in st], ps=(5, 50, 95)),
            'host_room_share': {k: r3(v / len(st)) for k, v in collections.Counter(s['host'] for s in st).most_common() if v / len(st) >= 0.005},
        })
    if multi:
        bb = collections.defaultdict(collections.Counter)
        for d in multi:
            bb[min(d['n_bedrooms'], 6)][min(d['n_bathrooms'], 4)] += 1
        out['multi_bedroom'] = {
            'definition': 'dwellings with >= 2 bedrooms; full bathroom = BATHROOM area containing shower or bathtub; wc = toilet without shower/bath',
            'n': len(multi),
            'full_bathrooms_per_bedroom': pct([d['n_bathrooms'] / d['n_bedrooms'] for d in multi]),
            'bathrooms_plus_wc_per_bedroom': pct([(d['n_bathrooms'] + d['n_wc']) / d['n_bedrooms'] for d in multi]),
            'all_sanitary_rooms_per_bedroom': pct([(d['n_bathrooms'] + d['n_wc'] + d['n_sanitary_nofixture']) / d['n_bedrooms'] for d in multi]),
            'full_bathrooms_given_bedrooms': {
                (f'{b}+' if b == 6 else str(b)): {'n': sum(c.values()), **{(f'{k}+' if k == 4 else str(k)): r3(c[k] / sum(c.values())) for k in range(0, 5)}}
                for b, c in sorted(bb.items())},
            'share_with_ensuite': r3(np.mean([d['ensuite'] for d in multi])),
            'share_with_separate_wc': r3(np.mean([d['n_wc'] > 0 for d in multi])),
        }
    return out


def group_stats(D):
    ids = {d['idx'] for d in D}
    R = [r for r in rooms if r['dw'] in ids]
    by_c = collections.defaultdict(list); by_d = collections.defaultdict(list)
    for r in R:
        by_c[r['c']].append(r)
        if r['derived']:
            by_d[r['derived']].append(r)
    return {
        'dwelling': dwelling_block(D),
        'rooms': {t: room_block(by_c[t]) for t in MAIN_TYPES if len(by_c.get(t, [])) >= 20},
        'rooms_derived': {t: room_block(by_d[t]) for t in DERIVED if len(by_d.get(t, [])) >= 20},
        'connections': link_block(R, D),
    }


explicit = [d for d in dwellings if not d['heuristic']]
groups = {
    'all': explicit,
    'rooms_ge4': [d for d in explicit if d['n_rooms_swiss'] >= 4],
    'bedrooms_ge3': [d for d in explicit if d['n_bedrooms'] >= 3],
    'bedrooms_ge4': [d for d in explicit if d['n_bedrooms'] >= 4],
    'multi_floor': [d for d in explicit if d['n_floors'] >= 2],
}
group_defs = {
    'all': 'all unique residential layouts with explicit room labels',
    'rooms_ge4': 'Swiss room count (ROOM+BEDROOM+LIVING_ROOM+LIVING_DINING areas) >= 4, i.e. >= "4-Zimmer"; the group the task asked for',
    'bedrooms_ge3': '>= 3 bedrooms (closest large-family analogue with a usable sample size)',
    'bedrooms_ge4': '>= 4 bedrooms (closest analogue to a 4-bedroom villa; small sample)',
    'multi_floor': 'dwelling spans >= 2 floors (maisonettes; the only source of internal-stair statistics)',
}
out_groups = {}
for g, D in groups.items():
    print('group', g, len(D), flush=True)
    out_groups[g] = {'definition': group_defs[g], **group_stats(D)}

# sensitivity: generic-ROOM scheme with heuristic living/bedroom split
gen = [d for d in dwellings if d['heuristic']]
gen_ids = {d['idx'] for d in gen}
gR = collections.defaultdict(list)
for r in rooms:
    if r['dw'] in gen_ids:
        gR[r['c']].append(r)
sens = {
    'definition': 'layouts labelled only with generic ROOM (no BEDROOM/LIVING labels); largest ROOM treated as living, others as bedrooms. '
                  'Excluded from the groups above; shown only so you can see the main stats are not an artefact of that exclusion.',
    'n_layouts': len(gen),
    'bedroom_area_m2': pct([r['area'] for r in gR['bedroom']]),
    'living_area_m2': pct([r['area'] for r in gR['living']]),
    'bathroom_area_m2': pct([r['area'] for r in gR['bathroom']]),
    'full_bathrooms_per_bedroom_ge2bed': pct([d['n_bathrooms'] / d['n_bedrooms'] for d in gen if d['n_bedrooms'] >= 2]),
    'circulation_share': pct([d['circ_share'] for d in gen], ps=(5, 50, 95)),
}

# raw subtype areas (traceability)
raw_by = collections.defaultdict(list)
exp_ids = {d['idx'] for d in explicit}
for r in rooms:
    if r['dw'] in exp_ids:
        raw_by[r['raw']].append(r['area'])
raw_stats = {k: pct(v, ps=(5, 50, 95), mean=False) for k, v in sorted(raw_by.items(), key=lambda kv: -len(kv[1])) if len(v) >= 30}

scheme_counts = collections.Counter(d['scheme'] for d in dwellings)
result = {
    'groups': out_groups,
    'sensitivity_generic_room_scheme': sens,
    'raw_swiss_subtype_area_m2_all_explicit': raw_stats,
    'qa': {
        'opening_matching_counts': dict(sorted(QA.items())),
        'layout_label_schemes': {'legend': 'B=has BEDROOM, L=has LIVING_ROOM/LIVING_DINING, R=has generic ROOM',
                                 **dict(scheme_counts.most_common())},
        'n_layouts_processed': len(dwellings), 'n_layouts_explicit_labels': len(explicit), 'n_layouts_generic_heuristic': len(gen),
        'n_rooms_processed': len(rooms), 'apartment_selection_skips': dict(skipped),
        'n_residential_apartments_total': int(sum(inst.values())), 'n_unique_layouts_total': len(reps),
    },
}
json.dump(result, open(OUT, 'w', encoding='utf-8'), indent=1)
print('wrote', OUT, round(time.time() - t0, 1), 's')
