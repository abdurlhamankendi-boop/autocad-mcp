"""Dubai Building Code 2021 checks for the villa, from page-cited data.

Every threshold here is READ from references/dubai_villa_rules.json (extracted
from the DBC PDF and fact-checked page by page), and every issue names the
rule id and PDF page it enforces -- so a failure can be looked up, and a
wrong threshold is fixed in one place.

This module exists because the house validator carried house-builder folklore
where the code says otherwise: it allowed a 220 mm stair riser and tested
2R+G; the DBC says 100-180 mm and a 280 mm tread, and has no 2R+G rule. It
accepted a 5.0 m parking depth; the DBC's open bay is 5.5 m. It never looked
at the pool at all.

Added in the integration (PROJECT_STATE s12), all stricter, none looser: the
pool floor SLOPE (K-POOL-02) and shallowest depth read from the floor profile
(K-POOL-03); a grated basin counts as deck only if the grate is built
(K-POOL-09); POOL_BARRIER is proved -- the pool garden's edge is closed by
house, boundary wall or guards (K-POOL-04/-08); every OPEN edge of a raised
landing and of the garden platform guarded (K-GRD-01/-02, was "a guard near
the landing"); windows facing a neighbour only past the setback (K-WIN-09);
parking bays counted in the porch width no flight of steps crosses (K-PARK-03).

Added in the review of 2026-09-26, stricter again: INSIDE the house every
edge of every stair tread, of the half-landing and of the first floor along
every void is walked, what lies beyond is looked up (a wall, a riser up or the
side of a solid flight, or a drop to the highest solid below), and a drop of
760 or more needs a guard on that edge 1200 over the nosing line (K-GRD-01/-02,
K-SGR-01/-02) -- the stair's own open sides had none and nothing looked. Every
OPEN side of every flight, inside and out, found the same way, needs a
handrail 865-965 over the nosing line (K-HR-01). A flight's clear width is
measured between the guards standing in it (K-STR-01), not as half the well.

Generalised for a design with a basement and several stairs (the Fairway,
2026-09-26). Every change is opt-in by what the design provides, so the villa
(no STAIRS, no stair_columns, no BELOW_GRADE_FLOORS) takes the paths it took:
  * inside the house the solid is every storey's slab (STACKED, the basement
    included) and the stairs' own solid (stair_columns() when the design has
    it); a walking surface is judged against the storey it stands in (the
    floor whose level <= it < the next); every floor listed by every VOID is
    walked (the ground floor round a basement stair's well too); an opening
    is passable only up to its head (V.opening_z) at the height one looks
    through it; and where solid starts less than the K-GRD-03 sphere (100)
    above the walking surface beyond an edge -- an open riser under the next
    floating tread -- that edge is closed;
  * STAIRS: every flight's riser, going, arrival (K-STR-03/-04/-05), its fit
    in its well, each half-landing's depth (K-STR-09) and the headroom over
    the nosing line (K-STR-11);
  * BELOW_GRADE_FLOORS: K-BSMT-01..06;
  * parking behind BOUNDARY_T, pool windows on GROUND_FLOOR, the ground
    floors' outlines (GROUND_FLOOR + annex), daylight roles from LIT_ROLES.
And, for every design (the villa passes both unchanged): a room's clear
length and width (K-ROOM-01/-02, K-COR-01) are its NET floor's -- less the
en-suite nested in it -- measured as validate_plan measures them, the minima
read from the rules file; K-PRJ-03 is applied at the road setback too, where
a thin shade wholly over the car porch is a K-SB-05 parking shade (a NOTE).

    python villa_dbc.py        -> the DBC report for villa_design.py
villa_design.validate() calls checks() at the end, so every validation run
includes them.
"""

from __future__ import annotations

import json
import math
import os

import villa_design as V

RULES_FILE = os.path.join(os.path.expanduser("~"), ".claude", "skills",
                          "architectural-cad", "references", "dubai_villa_rules.json")

# How much narrower than its structural opening a door's CLEAR width is: two
# frame jambs (~30 each) and the leaf thickness standing open (~40). The DBC
# sets clear widths; the design data holds structural openings.
DOOR_CLEAR_LOSS = 100.0
# Net glazing = glass only: the opening less the 60 mm bronze frame all round
# (villa_gltf.building frames).
FRAME = 60.0
# K-POOL-02 limits the floor slope in the "shallow area" and the "deep end"
# without saying where one ends; 1.5 m of water (the usual standards' shallow
# area) is taken, applied so that any doubt falls on the stricter 12 %.
SHALLOW_AREA_DEPTH = 1500.0


def _rules():
    try:
        with open(RULES_FILE, encoding="utf-8") as f:
            return {r["id"]: r for r in json.load(f)["rules"]}
    except (OSError, ValueError, KeyError):
        return {}


R = _rules()


def val(rule_id, name=None, default=None):
    """A rule's value (first value, or the one called `name`)."""
    r = R.get(rule_id)
    if not r:
        return default
    for v in r.get("values", []):
        if name is None or v.get("name") == name:
            return v.get("value")
    return default


def cite(rule_id):
    r = R.get(rule_id, {})
    return f"DBC {rule_id} p.{r.get('pdf_page', '?')}"


# K-GRD-03: no opening in a guard (or, here, between an edge and the solid
# over the space beyond it) may pass a sphere this big.
SPHERE = val("K-GRD-03", "infill_sphere", 100)
# The villa's daylight roles (K-WIN-01: bedrooms, living rooms, kitchens), and
# the living-room roles of the Fairway's vocabulary (none is a villa role, so
# the villa is judged as it was). A design's LIT_ROLES replaces the tuple.
LIT_ROLES = ("bedroom", "master_bedroom", "family_living", "majlis",
             "kitchen", "formal_dining", "study",
             "sitting", "family_lounge", "living", "dining")
# Per-run cache of derived floor geometry (cleared by checks(): a test may
# patch the design between runs).
_CACHE = {}


def checks():
    issues = []
    if not R:
        return ["[MAJOR] DBC rules file missing -- Dubai Building Code not checked "
                f"({RULES_FILE})"]
    _CACHE.clear()
    get = lambda n, d=None: getattr(V, n, d)
    rooms = V.ROOMS
    role = get("ROLE", {})
    wmin = val("K-STR-01", default=1000)

    # ---- stairs ---------------------------------------------------------
    if get("STAIRS") and hasattr(V, "flights"):
        # several stairs (STAIRS, read through flights()): every flight, its
        # well, its landings and the headroom over it -- the single-stair
        # names (STAIR, RISERS) point at one of them only
        issues += _stairs(list(get("GUARDS", [])))
    else:
        rmin, rmax = val("K-STR-03", default=[100, 180])
        rise = V.FF2FF / V.RISERS
        if not (rmin <= rise <= rmax):
            need = math.ceil(V.FF2FF / rmax)
            issues.append(f"[FATAL] stair riser {rise:.1f} mm outside {rmin}-{rmax} "
                          f"({cite('K-STR-03')}); {need} risers of {V.FF2FF / need:.1f} needed")
        tread = val("K-STR-05", default=280)
        if V.STAIR_GOING < tread:
            issues.append(f"[FATAL] stair tread {V.STAIR_GOING:.0f} mm < {tread} "
                          f"({cite('K-STR-05')})")
        sx0, sy0, sx1, sy1 = V.STAIR
        flights = get("STAIR_FLIGHTS", 2)
        width = abs(sx1 - sx0) / flights if flights > 1 else abs(sx1 - sx0)
        if width < wmin:
            issues.append(f"[FATAL] stair flight {width:.0f} mm wide < {wmin} "
                          f"({cite('K-STR-01')})")
        land = val("K-STR-09", default=1000)
        per = math.ceil(V.RISERS / flights)
        run = (per - 1) * V.STAIR_GOING + (land if flights > 1 else 0)
        if run > abs(sy1 - sy0) + 1e-6:
            issues.append(f"[FATAL] stair well {abs(sy1 - sy0):.0f} mm deep; {per - 1} "
                          f"treads x {V.STAIR_GOING:.0f} + {land} landing = {run:.0f} "
                          f"({cite('K-STR-05')}, {cite('K-STR-09')})")

    # ---- room sizes and clear heights -----------------------------------
    # The clear length and width are the room's FLOOR's, net of the rooms
    # nested in it (an en-suite in a bedroom's corner leaves an L), measured
    # as validate_plan measures them: the largest rectangle that fits in the
    # net floor, its short side. (It was the room rectangle's short side,
    # which an en-suite never reduced.)
    for r in rooms:
        rl = role.get(r[0], "")
        a = V.net_area(r)
        if r[5] == V.HAB and rl not in ("maid_room", "driver_room"):
            amin = val("K-ROOM-01", "net_area", 10.5)
            if a < amin - 1e-6:
                issues.append(f"[FATAL] {r[0]} {a:.1f} m2 < {amin} m2 ({cite('K-ROOM-01')})")
            dmin = 1000 * val("K-ROOM-01", "min_dimension", 3.0)
            short, core = _clear(r, amin)
            if short < dmin - 1:
                issues.append(f"[FATAL] {r[0]} is {short:.0f} mm wide < {dmin:.0f} "
                              f"({cite('K-ROOM-01')}){_core_note(r, core, dmin, amin)}")
        if rl in ("maid_room", "driver_room"):
            amin = val("K-ROOM-02", "net_area", 5.5)
            dmin = 1000 * val("K-ROOM-02", "min_dimension", 2.1)
            short, core = _clear(r, amin)
            if a < amin - 1e-6 or short < dmin - 1:
                issues.append(f"[FATAL] {r[0]} {a:.1f} m2 / {short:.0f} mm below "
                              f"{amin} m2 / {dmin:.0f} ({cite('K-ROOM-02')})"
                              f"{_core_note(r, core, dmin, amin)}")
        if rl in ("corridor", "landing", "hall"):
            cmin = 1000 * val("K-COR-01", "clear_width", 1.0)
            short, _core = _clear(r, 0.0)
            if short < cmin - 1:
                issues.append(f"[FATAL] {r[0]} {short:.0f} mm wide < {cmin:.0f} "
                              f"({cite('K-COR-01')})")
    for fl in V.floors():
        ch = V.CEIL[fl]
        if ch < 2700 and any(r[5] == V.HAB for r in V.rooms_on(fl)):
            issues.append(f"[FATAL] {fl} clear height {ch:.0f} < 2700 for habitable "
                          f"rooms ({cite('K-CH-01')})")
        elif ch < 2300:
            issues.append(f"[FATAL] {fl} clear height {ch:.0f} < 2300 ({cite('K-CH-02')})")

    # ---- doors: CLEAR width, not the structural opening -----------------
    for o in V.OPENINGS:
        fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
        if kind != V.DOOR:
            continue
        # clear OPENING of the doorway (a pair measured with both leaves open)
        clear = abs(b - a) - DOOR_CLEAR_LOSS
        wet = any(role.get(n, "") in ("ensuite", "guest_wc", "maid_bath",
                                      "driver_bath", "wc") for n in (ra, rb) if n)
        need = val("K-DOOR-02", default=710) if wet else val("K-DOOR-01", default=915)
        if clear < need - 1e-6:
            issues.append(f"[FATAL] door {ra}->{rb or 'outside'} clear {clear:.0f} mm "
                          f"< {need} ({cite('K-DOOR-02' if wet else 'K-DOOR-01')}; "
                          f"opening {abs(b - a):.0f})")

    # ---- daylight: net glazing as a share of floor ----------------------
    glass = {}
    for o in V.OPENINGS:
        if o[8] is not None or o[1] not in (V.WIN, getattr(V, "SLIDE", "slide")):
            continue
        lo, hi = V.opening_z(o)
        gw = max(0.0, abs(o[6] - o[5]) - 2 * FRAME)
        gh = max(0.0, (hi - lo) - 2 * FRAME)
        glass[(o[0], o[7])] = glass.get((o[0], o[7]), 0.0) + gw * gh / 1e6
    lit_roles = tuple(get("LIT_ROLES", LIT_ROLES))
    below_grade = tuple(get("BELOW_GRADE_FLOORS", ()))
    for r in rooms:
        rl = role.get(r[0], "")
        if r[6] in below_grade:
            continue                   # K-BSMT-03, below: glass open to the air only
        if rl in lit_roles:
            ratio, rid = val("K-WIN-01", default=0.1), "K-WIN-01"
        elif rl in ("maid_room", "driver_room"):
            ratio, rid = val("K-WIN-06", default=0.08), "K-WIN-06"
        else:
            continue
        g, a = glass.get((r[6], r[0]), 0.0), V.net_area(r)
        if g < ratio * a - 1e-6:
            issues.append(f"[FATAL] {r[0]} net glazing {g:.2f} m2 = {100 * g / a:.1f}% "
                          f"of {a:.1f} m2 < {100 * ratio:.0f}% ({cite(rid)})")

    # ---- setbacks and projections: EVERY structure, not room outlines ----
    sb = 1000 * (val("K-SB-02", "setback_neighbour_Z", None)
                 or val("K-SB-02", "setback_road_Z", 3) or 3)
    dec = val("K-PRJ-03", "decorative_depth_in_setback", 300)
    to_nb = 1000 * val("K-PRJ-04", "projection_to_neighbour", 3)
    # one report per fin ARRAY (its envelope) and per shade, not per fin
    arrays = [(f["x0"], f["y0"], f["x1"], f["y1"], f["z0"], f["z1"])
              for f in get("FIN_ARRAYS", [])]
    ffl = V.LEVEL.get(get("GROUND_FLOOR", "GF"), 0.0)
    clear = 1000 * val("K-PRJ-03", "clearance_above_FFL", 2.7)
    for i, bx in enumerate(arrays + list(get("SHADES", []))):
        x0, y0, x1, y1, z0, z1 = bx
        # every setback, the road's too (K-PRJ-02/-03); K-PRJ-04 below is
        # about the neighbours only
        into = max(sb - x0, x1 - (V.PLOT_W - sb), sb - y0, y1 - (V.PLOT_D - sb), 0.0)
        if into > 0 and _parking_shade(bx):
            issues.append(f"[NOTE ] shading element {i} at x {x0:.0f}-{x1:.0f} "
                          f"y {y0:.0f}-{y1:.0f} stands {into:.0f} mm into the setback over "
                          f"the car porch: a light parking shade, allowed there "
                          f"({cite('K-SB-05')})")
            into = 0.0
        if into > dec + 1e-6 or (into > 0 and z0 - ffl < clear - 1e-6):
            issues.append(f"[FATAL] shading element {i} at x {x0:.0f}-{x1:.0f} "
                          f"y {y0:.0f}-{y1:.0f} projects {into:.0f} mm into the "
                          f"{sb:.0f} setback (max {dec} and only above 2.7 m; "
                          f"{cite('K-PRJ-03')})")
        near = min(x0, V.PLOT_W - x1, y0)
        if near < to_nb - 1e-6:
            issues.append(f"[FATAL] shading element {i} is {near:.0f} mm from the plot "
                          f"limit (>= {to_nb:.0f}; {cite('K-PRJ-04')})")

    # ---- annex: K.5.2.3, measured the way the code measures -------------
    if "AX" in V.floors():
        ax = V.outline("AX")
        # GA = inside the external walls, summed over the main building's floors
        ga = sum(V.fabric(fl)[2].area for fl in V.floors() if fl != "AX") / 1e6
        if ax.area / 1e6 > val("K-ANX-04", default=0.6) * ga + 1e-6:
            issues.append(f"[FATAL] annex {ax.area / 1e6:.1f} m2 > 60% of main GA "
                          f"{ga:.1f} m2 ({cite('K-ANX-04')})")
        hmax = 1000 * val("K-ANX-05", default=5.5)
        top = V.AX_FL + V.AX_CH + V.SLAB + V.PARAPET
        if top > hmax + 1e-6:
            issues.append(f"[FATAL] annex {top:.0f} mm high > {hmax:.0f} ({cite('K-ANX-05')})")
        gap = ax.distance(V.outline("GF"))
        if gap < 1000 * val("K-ANX-02", default=1.5) - 1e-6:
            issues.append(f"[FATAL] annex {gap:.0f} mm from the villa (< 1500, {cite('K-ANX-02')})")
        bx0, by0, bx1, by1 = ax.bounds
        on_boundary = (bx0 <= 1 or by0 <= 1 or bx1 >= V.PLOT_W - 1 or by1 >= V.PLOT_D - 1)
        inside_setbacks = (bx0 >= sb and by0 >= sb and bx1 <= V.PLOT_W - sb
                           and by1 <= V.PLOT_D - V.SB_FRONT)
        if not (on_boundary or inside_setbacks):
            issues.append(f"[FATAL] annex neither on the plot boundary nor within the "
                          f"setbacks ({cite('K-ANX-03')})")

    # ---- parking: the open bay the code sizes ---------------------------
    bay_l = 1000 * val("K-PARK-03", "single_open_l", 5.5)
    bay_w = 1000 * val("K-PARK-03", "single_open_w", 3.0)
    from shapely.geometry import box as _b
    house = V.outline(get("GROUND_FLOOR", "GF"))
    front = house.intersection(_b(V.PORCH_X0, 0, V.PORCH_X1, V.PLOT_D))
    face = front.bounds[3] if not front.is_empty else V.PORCH_Y0
    wall_t = get("BOUNDARY_T", 350.0)            # the street wall's inside face
    depth = (V.PLOT_D - wall_t) - max(face, V.PORCH_Y0)
    # The bays must be CLEAR: a flight of steps landing in the porch takes
    # its width out of the bays (candidate B's service flight did, and this
    # check could not see it). Count bays in the widest full-depth run of the
    # porch that no step box crosses.
    porch = _b(V.PORCH_X0, max(face, V.PORCH_Y0), V.PORCH_X1, V.PLOT_D - wall_t)
    cuts_x = sorted((max(b[0], V.PORCH_X0), min(b[3], V.PORCH_X1))
                    for b in V.external_steps()
                    if porch.intersects(_b(b[0], b[1], b[3], b[4]))
                    and porch.intersection(_b(b[0], b[1], b[3], b[4])).area > 1.0)
    run, x = 0.0, V.PORCH_X0
    for c0, c1 in cuts_x:
        run, x = max(run, c0 - x), max(x, c1)
    run = max(run, V.PORCH_X1 - x)
    if cuts_x:
        issues.append(f"[NOTE ] external steps stand in the car porch; "
                      f"{run:.0f} mm of its width is clear")
    bays = int(run // bay_w)
    if depth < bay_l - 1e-6 or bays < 1:
        issues.append(f"[FATAL] parking {depth:.0f} x {V.PORCH_X1 - V.PORCH_X0:.0f} mm: "
                      f"an open bay is {bay_w:.0f} x {bay_l:.0f} ({cite('K-PARK-03')})")
    elif bays < 2:
        issues.append(f"[MAJOR] parking holds {bays} bay; the brief wants two "
                      f"({cite('K-PARK-03')})")

    # ---- pool -----------------------------------------------------------
    # K-POOL-03 reads the shallowest point of the FLOOR PROFILE when there is
    # one (POOL_FLOOR), not only the declared constant.
    lo_, hi_ = val("K-POOL-03", default=[850, 1200])
    prof = sorted(get("POOL_FLOOR", None) or ((V.POOL_Y0, V.POOL_FL),
                                               (V.POOL_Y1, V.POOL_FL)))
    shallow_fl = max([z for _, z in prof] + [get("POOL_SHALLOW_FL", V.POOL_FL)])
    shallow = V.POOL_TW - shallow_fl
    if not (lo_ <= shallow <= hi_):
        issues.append(f"[FATAL] pool shallowest depth {shallow:.0f} mm outside {lo_}-{hi_} "
                      f"({cite('K-POOL-03')}); declare POOL_SHALLOW_FL")
    # K-POOL-02: "Pool floor slope must not exceed 12% in the shallow area and
    # 33% in the deep end." The code gives no depth that ends the shallow
    # area; 1.5 m (the shallow area of the usual pool standards) is taken,
    # and a segment that STARTS shallower than that is held to the shallow
    # limit -- the stricter reading. A vertical step in the floor is a fault.
    sl_sh = val("K-POOL-02", "shallow_slope", 12)
    sl_dp = val("K-POOL-02", "deep_slope", 33)
    for (ya, za), (yb, zb) in zip(prof, prof[1:]):
        if yb - ya < 1.0:
            if abs(zb - za) > 1.0:
                issues.append(f"[FATAL] pool floor steps {abs(zb - za):.0f} mm at "
                              f"y {ya:.0f} ({cite('K-POOL-02')})")
            continue
        slope = 100.0 * abs(zb - za) / (yb - ya)
        top_depth = V.POOL_TW - max(za, zb)
        lim, area = ((sl_sh, "shallow area") if top_depth < SHALLOW_AREA_DEPTH
                     else (sl_dp, "deep end"))
        if slope > lim + 1e-9:
            issues.append(f"[FATAL] pool floor y {ya:.0f}-{yb:.0f} slopes {slope:.1f}% "
                          f"> {lim}% in the {area} ({cite('K-POOL-02')})")
    sill = val("K-POOL-01", default=1200)
    fixed = set(get("FIXED_GLAZING", set()))
    for o in V.OPENINGS:
        if o[1] != V.WIN or o[8] is not None or o[0] != get("GROUND_FLOOR", "GF"):
            continue
        if V.facing(o) != "S" or (o[0], o[7]) in fixed:
            continue
        if V.WIN_SILL < sill:
            issues.append(f"[FATAL] {o[7]} window faces the pool with a "
                          f"{V.WIN_SILL:.0f} sill; operable windows need {sill} "
                          f"({cite('K-POOL-01')}) -- raise it or declare it in FIXED_GLAZING")
    deck_w = 1000 * val("K-POOL-09", default=1.2)
    try:
        import villa_colour as CC
        from shapely.ops import unary_union
        s = CC.ground_surfaces()
        hard = unary_union([s[k] for k in ("poolsurround", "terrace", "deck", "path")
                            if k in s])
        if get("BASIN_GRATED", False):
            # the basin counts as deck only where a grate is actually built
            grate = [_b(g[0], g[1], g[3], g[4]) for g in (V.grate() if hasattr(V, "grate") else [])]
            basin = _b(V.POOL_X0 - 400, V.BASIN_Y0, V.POOL_X1 + 400, V.BASIN_Y1)
            covered = unary_union(grate).intersection(basin).area if grate else 0.0
            if covered < 0.95 * basin.area:
                issues.append(f"[FATAL] BASIN_GRATED but the grate built covers "
                              f"{100 * covered / basin.area:.0f}% of the basin "
                              f"({cite('K-POOL-09')})")
            hard = hard.union(unary_union(grate)) if grate else hard
        coping = _b(V.POOL_X0 - 400, V.POOL_Y0 - 400, V.POOL_X1 + 400, V.POOL_Y1 + 400)
        ring = coping.buffer(deck_w, join_style=2).difference(coping)
        missing = ring.difference(hard.buffer(1)).area / ring.area
        if missing > 0.05:
            issues.append(f"[FATAL] {100 * missing:.0f}% of the {deck_w:.0f} mm deck "
                          f"ring round the pool is not deck ({cite('K-POOL-09')})")
    except Exception as exc:                     # ground surfaces unavailable
        issues.append(f"[MAJOR] pool deck not checkable: {str(exc)[:60]}")
    guards = list(get("GUARDS", []))
    fence_h = val("K-POOL-04", default=1200)
    if not get("POOL_BARRIER"):
        issues.append(f"[MAJOR] no pool barrier declared (fence >= 1200, or house "
                      f"walls with alarmed self-closing doors; {cite('K-POOL-04')}, "
                      f"{cite('K-POOL-08')}) -- set POOL_BARRIER")
    elif hasattr(V, "garden_platform"):
        # K-POOL-08, proved: the pool garden can be left only through the
        # house, over the boundary wall, or over a guard at least as high as
        # a pool fence. Any other length of its edge is a way in.
        from shapely.ops import unary_union
        plat = V.garden_platform()
        T = get("BOUNDARY_T", 350.0)
        ring_w = _b(0, 0, V.PLOT_W, V.PLOT_D).difference(
            _b(T, T, V.PLOT_W - T, V.PLOT_D - T))
        high = [_b(g[0], g[1], g[2], g[3]) for g in guards
                if g[5] - get("GARDEN_Z", V.POOL_TW) >= fence_h - 1]
        closed = unary_union([V.outline(f) for f in _ground_floors()]
                             + [ring_w] + high).buffer(60)
        gap = plat.boundary.difference(closed)
        if gap.length > 100:
            b_ = gap.bounds
            issues.append(f"[FATAL] the pool garden is open over {gap.length:.0f} mm of "
                          f"its edge around ({b_[0]:.0f},{b_[1]:.0f})-({b_[2]:.0f},"
                          f"{b_[3]:.0f}) -- POOL_BARRIER claims walls enclose it "
                          f"({cite('K-POOL-08')})")
        above = get("BOUNDARY_H", 2400.0) - get("GARDEN_Z", V.POOL_TW)
        if above < fence_h:
            issues.append(f"[FATAL] the boundary wall stands {above:.0f} mm over the "
                          f"pool garden (< {fence_h}, {cite('K-POOL-04')})")

    # ---- guards where a floor stands >= 760 mm above the level beside it -
    # Every OPEN edge must be guarded, not just "a guard somewhere near the
    # landing": an edge is closed by the house wall or by the next step down
    # of its own flight; the rest must be >= 95 % covered by guards at least
    # GUARD height over the landing (K-GRD-01/-02).
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    drop = val("K-GRD-01", default=760)
    gh = val("K-GRD-02", default=1200)
    steps = V.external_steps()
    built = unary_union([V.outline(f) for f in _ground_floors()])

    def uncovered(edges, top, closed):
        foot = unary_union([_b(g[0], g[1], g[2], g[3]).buffer(60, join_style=2)
                            for g in guards if g[4] <= top + 1 and g[5] >= top + gh - 1]
                           or [_b(0, 0, 0, 0)])
        bad = 0.0
        for e in edges:
            e = e.difference(closed)
            bad += e.difference(foot).length
        return bad

    for i, (x0, y0, z0, x1, y1, z1) in enumerate(steps):
        if z1 - z0 < drop or z1 not in V.LEVEL.values():
            continue                              # only the landings
        lower = unary_union([_b(b[0], b[1], b[3], b[4]) for j, b in enumerate(steps)
                             if j != i and b[5] < z1 and z1 - b[5] <= 180 + 1
                             and b[5] - b[2] > 0] or [_b(0, 0, 0, 0)])
        edges = [LineString([(x0, y0), (x1, y0)]), LineString([(x1, y0), (x1, y1)]),
                 LineString([(x1, y1), (x0, y1)]), LineString([(x0, y1), (x0, y0)])]
        bad = uncovered(edges, z1, built.buffer(5).union(lower.buffer(5)))
        if bad > 50:
            issues.append(f"[MAJOR] landing {i} at +{z1:.0f} is {z1 - z0:.0f} mm above "
                          f"the ground and {bad:.0f} mm of its open edge has no guard "
                          f">= {gh} ({cite('K-GRD-01')}, {cite('K-GRD-02')})")
    if hasattr(V, "garden_platform"):
        gz = get("GARDEN_Z", V.POOL_TW)
        if gz - V.STREET >= drop:
            T = get("BOUNDARY_T", 350.0)
            ring_w = _b(0, 0, V.PLOT_W, V.PLOT_D).difference(
                _b(T, T, V.PLOT_W - T, V.PLOT_D - T))
            bad = uncovered([V.garden_platform().boundary], gz,
                            built.union(ring_w).buffer(5))
            if bad > 50:
                issues.append(f"[MAJOR] the garden platform stands {gz - V.STREET:.0f} "
                              f"over the side strips and {bad:.0f} mm of its edge has "
                              f"no guard ({cite('K-GRD-01')})")
    # ---- inside the house: the stair's own open edges and the first floor
    # round its well (K-GRD-01/-02, K-SGR-01/-02). Only the outside landings
    # and the garden were checked, so the stair's open sides -- 2050 over the
    # hall, the upper flight up to 3930 over the lower -- carried no guard and
    # nothing noticed (review of 2026-09-26).
    if hasattr(V, "stair_surfaces"):
        issues += _house_guards(guards, drop)
    # ---- the clear width of every flight, less any guard standing in it
    # (the glass between two flights side by side), K-STR-01
    if hasattr(V, "flights"):
        for f in V.flights():
            clear = _flight_clear(f, guards)
            if clear < wmin - 1e-6:
                issues.append(f"[FATAL] {f['name']} is {clear:.0f} mm clear between its "
                              f"walls and guards < {wmin} ({cite('K-STR-01')})")
        issues += _handrails()
    if get("ROOF_ACCESSIBLE", False) and V.PARAPET < val("K-ROOF-01", default=1200):
        issues.append(f"[FATAL] accessible roof with a {V.PARAPET:.0f} parapet "
                      f"(< 1200, {cite('K-ROOF-01')})")

    # ---- windows facing a neighbour: only past the setback (K-WIN-09) ----
    # The street (north) is a road, not a neighbour; the other three sides
    # are. Measured from the window's outside face to that boundary.
    nb = 1000 * (val("K-SB-02", "setback_neighbour_X", 3) or 3)
    for o in V.OPENINGS:
        if o[8] is not None or o[1] not in (V.WIN, getattr(V, "SLIDE", "slide")):
            continue
        try:
            face = V.facing(o)
        except Exception:                        # noqa: BLE001
            continue
        t0, t1 = min(o[3], o[4]), max(o[3], o[4])
        dist = {"E": V.PLOT_W - t1, "W": t0, "S": t0, "N": None}[face]
        if dist is not None and dist < nb - 1e-6:
            issues.append(f"[FATAL] {o[0]} {o[7]} window faces a neighbour {dist:.0f} mm "
                          f"from the boundary (< {nb:.0f}; {cite('K-WIN-09')}, "
                          f"{cite('K-SB-02')})")

    # ---- a basement (BELOW_GRADE_FLOORS): K-BSMT-01..06 -------------------
    if any(f in get("BELOW_GRADE_FLOORS", ()) for f in V.floors()):
        issues += _basement(list(get("GUARDS", [])))
    return issues


def _parking_shade(bx):
    """Is shade box (x0, y0, x1, y1, z0, z1) a light parking shade (K-SB-05:
    'pergolas and lightweight parking shading structures' may occupy the
    setback)? Only a thin roof (<= the K-PRJ-03 decorative depth, 300)
    standing wholly over the declared car porch."""
    x0, y0, x1, y1, z0, z1 = bx
    if not hasattr(V, "PORCH_X0") or z1 - z0 > val("K-PRJ-03", "decorative_depth_in_setback",
                                                    300) + 1e-6:
        return False
    py1 = getattr(V, "PORCH_Y1", V.PLOT_D)
    return (V.PORCH_X0 - 1 <= x0 and x1 <= V.PORCH_X1 + 1
            and getattr(V, "PORCH_Y0", 0.0) - 1 <= y0 and y1 <= py1 + 1)


# ============================================================ rooms
def _clear(r, amin):
    """(clear, core) of room r's net floor (V.net_poly: less its nested
    rooms): `clear` is the short side of the largest axis-aligned rectangle
    that fits in it (validate_plan's Design.clear_dims); `core` is the
    fitting rectangle of at least `amin` m2 with the widest short side,
    (w, h), or None -- what a reading that asks only for SOME part of the
    room to meet the minimum would accept."""
    from shapely.geometry import box as _b
    g = V.net_poly(r)
    if hasattr(g, "geoms"):
        g = max(g.geoms, key=lambda p: p.area)
    if g.is_empty:
        return 0.0, None
    pts = list(g.exterior.coords) + [c for i in g.interiors for c in i.coords]
    xs = sorted({round(p[0], 3) for p in pts})
    ys = sorted({round(p[1], 3) for p in pts})
    tol = g.buffer(1.0, join_style=2, mitre_limit=8.0)
    fits = [(xb - xa, yb - ya) for i, xa in enumerate(xs) for xb in xs[i + 1:]
            for j, ya in enumerate(ys) for yb in ys[j + 1:]
            if tol.contains(_b(xa, ya, xb, yb))]
    if not fits:
        return 0.0, None
    w, h = max(fits, key=lambda d: d[0] * d[1])
    big = [d for d in fits if d[0] * d[1] >= amin * 1e6 - 1.0]
    core = max(big, key=lambda d: min(d)) if big else None
    return min(w, h), core


def _core_note(r, core, dmin, amin):
    """Where the room is, what is nested in it, and the reading a failure
    depends on when part of the room meets both minima although its largest
    clear rectangle is too narrow."""
    nested = [q[0] for q in V.children(r)] if hasattr(V, "children") else []
    out = (f" -- {r[6]} ({r[1]:.0f},{r[2]:.0f})-({r[3]:.0f},{r[4]:.0f})"
           + (f" less {', '.join(nested)}" if nested else ""))
    if core is not None and min(core) >= dmin - 1:
        out += (f"; a {core[0]:.0f} x {core[1]:.0f} part of it meets {dmin:.0f} and "
                f"{amin} m2: reading-dependent")
    return out


# ============================================================ floors
def _stacked():
    """The house's storeys that have rooms, bottom up: STACKED (default the
    villa's GF + FF; a design with a basement stacks B1 under them). An
    annex standing beside the house is not one of them."""
    st = tuple(getattr(V, "STACKED", ("GF", "FF")))
    return sorted((f for f in V.floors() if f in st and f in V.LEVEL),
                  key=lambda f: V.LEVEL[f])


def _ground_floors():
    """Floors standing on the ground -- GROUND_FLOOR and what is drawn with
    it (the annex, SHEET_OF) -- as villa_geom.ground_floors() reads them."""
    g = getattr(V, "GROUND_FLOOR", "GF")
    sheet_of = dict(getattr(V, "SHEET_OF", {"AX": "GF"}))
    return [f for f in V.floors() if f == g or sheet_of.get(f) == g]


def _storey(z):
    """The storey a walking surface at level z belongs to: the stacked floor
    whose level <= z < the next floor's level (None below the lowest)."""
    out = None
    for f in _stacked():
        if V.LEVEL[f] <= z + 1e-6:
            out = f
    return out


def _below(fl):
    """The stacked storey under `fl`, or None."""
    st = _stacked()
    lower = [f for f in st if V.LEVEL[f] < V.LEVEL[fl] - 1e-6]
    return lower[-1] if lower else None


def _passable(o, z):
    """Can one pass through opening `o` at height z? Only between its sill
    and its head (V.opening_z), and only if the gap left between z and the
    head is at least the K-GRD-03 sphere: over a door head the wall is solid."""
    lo, hi = V.opening_z(o)
    return lo <= z + 1.0 and hi - z >= SPHERE - 1e-6


# ============================================================ inside the house
def _floor(fl, z=None):
    """Where floor `fl` can be stood on: its rooms and the doorways and
    openings between them, less every void cut through it. With a height z,
    the room test at that height: an opening counts only while it is
    passable there (_passable) -- a door under the high end of a stair is
    wall at the level of the treads over it."""
    from shapely.geometry import box as _b
    from shapely.ops import unary_union
    ops = tuple(i for i, o in enumerate(V.OPENINGS)
                if o[0] == fl and o[8] is not None and o[1] != V.WIN
                and (z is None or _passable(o, z)))
    key = ("floor", fl, ops)
    if key in _CACHE:
        return _CACHE[key]
    g = unary_union([V.net_poly(r) for r in V.rooms_on(fl)]
                    + [V.void_rect(V.OPENINGS[i]) for i in ops])
    for _n, x0, y0, x1, y1, fls in V.VOIDS:
        if fl in fls:
            g = g.difference(_b(x0, y0, x1, y1))
    _CACHE[key] = g
    return g


def _room(z):
    """Where one may be at level z inside the house: the floor of the storey
    z stands in, openings passable at z (empty below the lowest storey)."""
    from shapely.geometry import Polygon
    fl = _storey(z)
    return _floor(fl, z) if fl is not None else Polygon()


def _inside_columns():
    """Solid inside the house as columns [(plan polygon, bottom, top)]: each
    storey's floor (its slab under it) -- every stacked storey with rooms,
    a basement included -- and the stairs' own solid: V.stair_columns() when
    the design says what its stairs are made of (solid from a floor, or a
    floating tread's waist), else each surface of the stair (solid down to
    the ground floor when STAIR_SOLID, else a 150 waist)."""
    if "cols" in _CACHE:
        return _CACHE["cols"]
    cols = [(_floor(fl), V.LEVEL[fl] - V.SLAB, V.LEVEL[fl]) for fl in _stacked()]
    cols += _stair_columns()
    _CACHE["cols"] = cols
    return cols


def _stair_columns():
    """The house stairs' own solid as columns [(plan, bottom, top)]."""
    from shapely.geometry import box as _b
    cols = []
    if hasattr(V, "stair_columns"):
        for (x0, y0, x1, y1), z0, z1 in V.stair_columns():
            cols.append((_b(x0, y0, x1, y1), z0, z1))
    else:
        solid = getattr(V, "STAIR_SOLID", False)
        for (x0, y0, x1, y1), z, _r in V.stair_surfaces():
            cols.append((_b(x0, y0, x1, y1), V.GF if solid else z - 150.0, z))
    return cols


def _outside_columns(skip=()):
    """Solid outside the house: the garden platform, every landing and flight
    box (less `skip`), and the street-level ground everywhere else."""
    from shapely.geometry import box as _b
    cols = [(V.garden_platform(), -1e9, getattr(V, "GARDEN_Z", V.STREET))]
    for b in V.external_steps():
        if tuple(b) in skip:
            continue
        cols.append((_b(b[0], b[1], b[3], b[4]), b[2], b[5]))
    cols.append((_b(-1e6, -1e6, 1e6, 1e6), -1e9, V.STREET))
    return cols


def _beyond(p, own, cols, room):
    """What lies just past an edge, at p, beside a walking surface at `own`:
    None where it is closed -- `room` (where one may stand) does not hold p,
    so it is a wall; or something is solid just below `own` there (a riser
    up, the side of a solid flight); or solid STARTS there less than the
    K-GRD-03 sphere above `own` (the next floating tread over an open riser:
    no 100 mm sphere passes between the edge and its underside) -- else the
    top of the highest solid below, which is what one would fall to."""
    if not room.contains(p):
        return None
    z = own - 5.0
    below = -1e9
    for poly, z0, z1 in cols:
        if not poly.contains(p):
            continue
        if z0 <= z <= z1:
            return None
        if z1 < z:
            below = max(below, z1)
        elif z0 - own < SPHERE - 1e-6:
            return None
    return below


_FLOOR_WORDS = {"B1": "basement floor", "GF": "ground floor", "FF": "first floor",
                "SF": "second floor"}


def _half_landings():
    """[(label, (x0, y0, x1, y1), level)] -- every stair's half-landing. With
    STAIRS, each of stair_surfaces()'s flat surfaces, named after the stair
    whose well holds it; else the one stair_landing() (the villa's)."""
    stairs = getattr(V, "STAIRS", None)
    if stairs and hasattr(V, "stair_surfaces"):
        out = []
        for (x0, y0, x1, y1), z, rise in V.stair_surfaces():
            if rise:
                continue
            name = next((s["name"] for s in stairs
                         if s["rect"][0] - 1 <= x0 and s["rect"][1] - 1 <= y0
                         and x1 <= s["rect"][2] + 1 and y1 <= s["rect"][3] + 1), "stair")
            out.append((f"{name} half-landing", (x0, y0, x1, y1), z))
        return out
    L = V.stair_landing() if hasattr(V, "stair_landing") else None
    return [("stair half-landing", L[0], L[1])] if L is not None else []


def _edges(x0, y0, x1, y1, step=50.0):
    """Sample points along a box's four edges: (point on the edge, outward
    unit normal), `step` apart, starting half a step in from each corner."""
    out = []
    for (xa, ya), (xb, yb), n in (((x0, y0), (x1, y0), (0.0, -1.0)),
                                  ((x1, y0), (x1, y1), (1.0, 0.0)),
                                  ((x1, y1), (x0, y1), (0.0, 1.0)),
                                  ((x0, y1), (x0, y0), (-1.0, 0.0))):
        L = abs(xb - xa) + abs(yb - ya)
        k = max(1, int(L // step))
        for i in range(k):
            q = (i + 0.5) / k
            out.append(((xa + (xb - xa) * q, ya + (yb - ya) * q), n))
    return out


def _house_guards(guards, drop):
    """K-GRD-01/-02 and K-SGR-01/-02 inside the house. Every edge of every
    walking surface of the stair (treads and half-landing) and of the first
    floor along every void it has is walked in 50 mm steps; what lies 25 mm
    beyond is looked up (_beyond). Where the drop is >= `drop`, a guard must
    stand on that edge (within 60 mm), start at the walking level, and rise
    to the guard height over the nosing line's highest point on that surface
    -- a tread's nosing line climbs one riser across it."""
    from shapely.geometry import Point, Polygon, box as _b
    gh_st = val("K-SGR-02", "guard_height", 1200)
    gh_fl = val("K-GRD-02", default=1200)
    cols = _inside_columns()
    foot = [(_b(g[0], g[1], g[2], g[3]).buffer(60, join_style=2), g[4], g[5])
            for g in guards]
    surfaces = []                  # (label, box, level, rise, rule height)
    for f in V.flights() if hasattr(V, "flights") else []:
        if f["inside"]:
            surfaces += [(f["name"], V.flight_plan(f, t0, t1), z, f["rise"], gh_st)
                         for t0, t1, z in V.flight_treads(f)]
    for label, box_, z in _half_landings():
        surfaces.append((label, box_, z, 0.0, gh_fl))
    bad = {}
    for label, (x0, y0, x1, y1), own, rise, need in surfaces:
        # judged against the storey the surface stands in: a basement
        # flight against the basement's rooms, not the ground floor's
        room = _room(own)
        for (px, py), (nx, ny) in _edges(x0, y0, x1, y1):
            lvl = _beyond(Point(px + 25 * nx, py + 25 * ny), own, cols, room)
            if lvl is None or own - lvl < drop:
                continue
            pe = Point(px, py)
            if not any(fp.contains(pe) and z0 <= own + 1 and z1 >= own + rise + need - 1
                       for fp, z0, z1 in foot):
                b = bad.setdefault(label, [own, 0.0, own - lvl, need])
                b[1] += 50.0
                b[2] = max(b[2], own - lvl)
    # every floor along every void cut through it (the first floor round the
    # hall's void, the ground floor round a basement stair's well). The floor
    # beside the void is the floor itself. Under the void, at the level of
    # its edge, is air: the storey below has its walls only up to its own
    # ceiling, so a wall under the edge (the hall's partition under the
    # landing's edge) closes nothing -- one falls past its top into the room
    # below, to the highest SLAB (its outline: a wall stands on it) or stair
    # solid there.
    floors = V.floors()
    cols_void = _slabs() + _stair_columns()
    for vname, vx0, vy0, vx1, vy1, fls in V.VOIDS:
        for fl in fls:
            if fl not in floors or fl not in V.LEVEL:
                continue
            lv = V.LEVEL[fl]
            near = _floor(fl)
            # nothing is modelled under the lowest storey: a void listed on it
            # is a notch in its outline (the villa's light slots), closed here
            room = (_b(vx0, vy0, vx1, vy1).buffer(1.0) if _below(fl) is not None
                    else Polygon())
            for (px, py), (nx, ny) in _edges(vx0, vy0, vx1, vy1):
                if not near.contains(Point(px + 25 * nx, py + 25 * ny)):
                    continue                   # no floor on this side of the void
                lvl = _beyond(Point(px - 25 * nx, py - 25 * ny), lv, cols_void, room)
                if lvl is None or lv - lvl < drop:
                    continue
                pe = Point(px, py)
                if not any(fp.contains(pe) and z0 <= lv + 1 and z1 >= lv + gh_fl - 1
                           for fp, z0, z1 in foot):
                    label = f"{_FLOOR_WORDS.get(fl, fl + ' floor')} round the {vname.lower()}"
                    b = bad.setdefault(label, [lv, 0.0, lv - lvl, gh_fl])
                    b[1] += 50.0
                    b[2] = max(b[2], lv - lvl)
    return [f"[MAJOR] {label} at {own:+.0f}: {length:.0f} mm of its edge stands up to "
            f"{worst:.0f} mm over what is beyond it with no guard {need} mm high "
            f"(over the nosing line on a flight) ({cite('K-GRD-01')}, "
            f"{cite('K-SGR-01')}, {cite('K-SGR-02')})"
            for label, (own, length, worst, need) in bad.items()]


def _flight_run_level(f, t):
    """The tread a point t along a flight stands on, as its level."""
    for t0, t1, z in V.flight_treads(f):
        if t0 - 1e-6 <= t <= t1 + 1e-6:
            return z
    return None


def _flight_clear(f, guards):
    """A flight's clear width (K-STR-01): the widest run across it that no
    guard running along it stands in. Handrails may project 100 into it
    (K-STR-02) and are not taken off."""
    t0, t1 = V.flight_run(f)
    top = f["z_foot"] + f["n"] * f["rise"]
    cuts = []
    for g in guards:
        if f["along"] == "y":
            gc0, gc1, gt0, gt1 = g[0], g[2], g[1], g[3]
        else:
            gc0, gc1, gt0, gt1 = g[1], g[3], g[0], g[2]
        if gt1 - gt0 <= gc1 - gc0 or min(gt1, t1) - max(gt0, t0) <= 1.0:
            continue                       # across it, or beside another part
        if g[4] >= top + 2300.0 or g[5] <= f["z_foot"]:
            continue                       # over its headroom (K-STR-11), or below
        a, b = max(gc0, f["c0"]), min(gc1, f["c1"])
        if b > a:
            cuts.append((a, b))
    best, x = 0.0, f["c0"]
    for a, b in sorted(cuts):
        best, x = max(best, a - x), max(x, b)
    return max(best, f["c1"] - x)


def _handrails():
    """K-HR-01: every flight -- the house stair's and the outside steps' --
    has a handrail on each OPEN side, its top 865-965 over the nosing line.
    The open sides are found here, not read from the design: a side is open
    where anything beyond it lies lower than the tread beside it. A rail
    serves a side if it runs along it within 150 mm, over at least 90 % of
    the flight."""
    from shapely.geometry import Point
    lo, hi = val("K-HR-01", default=[865, 965])
    rails = V.handrails() if hasattr(V, "handrails") else []
    inside_cols = _inside_columns()
    from shapely.ops import unary_union
    built = unary_union([V.outline(fl) for fl in _ground_floors()])
    from shapely.geometry import box as _b
    room_out = _b(-1e6, -1e6, 1e6, 1e6).difference(built)
    issues = []
    for f in V.flights():
        t0, t1 = V.flight_run(f)
        if f["inside"]:
            cols, room = inside_cols, None       # the storey of each tread
        else:
            own_boxes = {tuple(b) for b in V.external_steps()
                         if _b(b[0], b[1], b[3], b[4]).intersects(
                             _b(*V.flight_plan(f, t0, t1)).buffer(-1))}
            cols, room = _outside_columns(own_boxes), room_out
        detail = "stair" in f                    # the multi-stair language: say where
        for side, out in (("c0", -1.0), ("c1", 1.0)):
            c = f[side]
            open_ = False
            where_open = []                      # (t, drop) of every open sample
            t = t0 + 25.0
            while t < t1 and (detail or not open_):
                own = _flight_run_level(f, t)
                q = (c + out * 25.0, t) if f["along"] == "y" else (t, c + out * 25.0)
                lvl = (_beyond(Point(*q), own, cols, room if room is not None else _room(own))
                       if own is not None else None)
                if lvl is not None and lvl < own - 5.0:
                    open_ = True
                    where_open.append((t, own - lvl))
                t += 50.0
            if not open_:
                continue
            ok = False
            for h in rails:
                if h["along"] != f["along"] or abs((h["c0"] + h["c1"]) / 2 - c) > 150.0:
                    continue
                cover = min(h["t1"], t1) - max(h["t0"], t0)
                if cover < 0.9 * (t1 - t0):
                    continue

                def top(t_):
                    return h["top0"] + (h["top1"] - h["top0"]) * (t_ - h["t0"]) / (h["t1"] - h["t0"])
                heights = [top(t_) - V.pitch_at(f, t_) for t_ in (max(h["t0"], t0),
                                                                     min(h["t1"], t1))]
                if all(lo - 1e-6 <= z <= hi + 1e-6 for z in heights):
                    ok = True
                    break
            if not ok:
                if detail:
                    where = {("y", "c0"): "west", ("y", "c1"): "east",
                             ("x", "c0"): "south", ("x", "c1"): "north"}[(f["along"], side)]
                    # the treads the open samples stand on, edge to edge
                    spans = [(a, b) for a, b, _z in V.flight_treads(f)
                             if any(a - 1e-6 <= p[0] <= b + 1e-6 for p in where_open)]
                    ts = [v for s in spans for v in s] or [p[0] for p in where_open]
                    ax = f["along"]
                    at = (f" (open at {ax} {min(ts):.0f}-{max(ts):.0f}, "
                          f"{c:.0f} across, up to {max(p[1] for p in where_open):.0f} mm "
                          f"over what is beside it)")
                else:
                    where = "west/south" if side == "c0" else "east/north"
                    at = ""
                issues.append(f"[MAJOR] {f['name']}: its open {where} "
                              f"side has no handrail {lo}-{hi} mm over the nosing line{at} "
                              f"({cite('K-HR-01')})")
    return issues


# ============================================================ several stairs
def _slabs():
    """The floor slabs as columns [(plan, bottom, top)]: under every stacked
    storey, its own outline and the one below it (the roof over the lower
    storey where the upper one stops short), less every void cut through it;
    over the top storey, its roof at the next LEVEL above (RF: finished roof
    level, the slab SLAB under it)."""
    from shapely.geometry import box as _b
    from shapely.ops import unary_union
    st = _stacked()
    if not st:
        return []
    roof = [k for k in sorted(V.LEVEL, key=V.LEVEL.get)
            if V.LEVEL[k] > V.LEVEL[st[-1]] + 1.0][:1]
    out = []
    keys = st + roof
    for i, fl in enumerate(keys):
        parts = ([V.outline(fl)] if fl in st else []) + \
                ([V.outline(keys[i - 1])] if i > 0 else [])
        g = unary_union(parts)
        for _n, x0, y0, x1, y1, fls in V.VOIDS:
            if fl in fls:
                g = g.difference(_b(x0, y0, x1, y1))
        out.append((g, V.LEVEL[fl] - V.SLAB, V.LEVEL[fl]))
    return out


def _headroom(f, solids):
    """(least headroom over the flight's nosing line, where along it) -- for
    every solid over the flight's plan (a slab, another stair) the lowest
    underside less the highest point of the nosing line under it; solids the
    nosing line is not under (the flight's own treads, the floors below) are
    skipped. (None, None) when nothing is over it."""
    from shapely.geometry import box as _b
    t0, t1 = V.flight_run(f)
    plan = _b(*V.flight_plan(f, t0, t1))
    worst = (None, None)
    for poly, z0, _z1 in solids:
        g = poly.intersection(plan)
        # each AREA of overlap on its own (an intersection may also hold the
        # zero-area lines where a slab's edge runs along the flight's)
        for part in getattr(g, "geoms", [g]):
            if part.is_empty or part.area < 1.0:
                continue
            bx = part.bounds
            a, b = (bx[1], bx[3]) if f["along"] == "y" else (bx[0], bx[2])
            na, nb = V.pitch_at(f, a), V.pitch_at(f, b)
            if z0 <= min(na, nb) + 1.0:
                continue
            h = z0 - max(na, nb)
            if worst[0] is None or h < worst[0]:
                worst = (h, a if na >= nb else b)
    return worst


def _stairs(guards):
    """Every flight of every stair (STAIRS, read through flights()):
      K-STR-03 riser 100-180 and K-STR-05 going >= 280, per flight;
      K-STR-04 the flight starts and arrives at a floor or landing level
               (else its first or last riser differs from the rest);
      K-STR-05/-09 each flight inside its stair's well;
      K-STR-09 each half-landing >= 1000 deep in the direction of travel and
               never narrower than the flights it serves (clear width);
      K-STR-11 >= 2300 headroom over the nosing line and over the landings,
               to the slabs (_slabs) and the stairs' own solid.
    The clear width (K-STR-01) and the guards and handrails are checked for
    every flight by checks() as before."""
    from shapely.geometry import box as _b
    issues = []
    rmin, rmax = val("K-STR-03", default=[100, 180])
    rvar = val("K-STR-04", default=10)
    tread = val("K-STR-05", default=280)
    land = val("K-STR-09", default=1000)
    head = 1000 * val("K-STR-11", default=2.3)
    fls = V.flights()
    landings = _half_landings()
    levels = sorted(set(V.LEVEL.values()) | {z for _l, _bx, z in landings})
    by_name = {s["name"]: s for s in V.STAIRS}
    solids = _slabs() + ([(_b(*b), z0, z1) for b, z0, z1 in V.stair_columns()]
                         if hasattr(V, "stair_columns") else [])
    for f in fls:
        nm = f["name"]
        if not (rmin <= f["rise"] <= rmax):
            need = math.ceil(f["n"] * f["rise"] / rmax)
            issues.append(f"[FATAL] {nm}: riser {f['rise']:.1f} mm outside {rmin}-{rmax} "
                          f"({cite('K-STR-03')}); {need} risers needed")
        if f["going"] < tread - 1e-6:
            issues.append(f"[FATAL] {nm}: tread {f['going']:.0f} mm < {tread} "
                          f"({cite('K-STR-05')})")
        if not f["inside"]:
            continue
        for z, what in ((f["z_foot"], "starts"),
                        (f["z_foot"] + f["n"] * f["rise"], "arrives")):
            near = min(levels, key=lambda L: abs(L - z))
            if abs(near - z) > rvar + 1e-6:
                issues.append(f"[FATAL] {nm} {what} at {z:+.0f}, {abs(near - z):.0f} mm off "
                              f"the nearest floor or landing ({near:+.0f}): a riser differs "
                              f"from the others by more than {rvar} ({cite('K-STR-04')})")
        s = by_name.get(f.get("stair"))
        t0, t1 = V.flight_run(f)
        x0, y0, x1, y1 = V.flight_plan(f, t0, t1)
        if s is not None:
            rx0, ry0, rx1, ry1 = s["rect"]
            if x0 < rx0 - 1 or y0 < ry0 - 1 or x1 > rx1 + 1 or y1 > ry1 + 1:
                issues.append(f"[FATAL] {nm} ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f}) runs "
                              f"outside its well ({rx0:.0f},{ry0:.0f})-({rx1:.0f},{ry1:.0f}) "
                              f"({cite('K-STR-05')}, {cite('K-STR-09')})")
        h, at = _headroom(f, solids)
        if h is not None and h < head - 1e-6:
            issues.append(f"[FATAL] {nm}: {h:.0f} mm headroom over the nosing line at "
                          f"{f['along']} {at:.0f} < {head:.0f} ({cite('K-STR-11')})")
    for label, (x0, y0, x1, y1), z in landings:
        lb = _b(x0, y0, x1, y1)
        served = [f for f in fls if f["inside"]
                  and min(abs(f["z_foot"] - z), abs(f["z_foot"] + f["n"] * f["rise"] - z)) < 1.0
                  and _b(*V.flight_plan(f, *V.flight_run(f))).distance(lb) < 1.0]
        if served:
            widths = [(_flight_clear(f, guards), f) for f in served]
            w, f = max(widths, key=lambda p: p[0])
            depth = (y1 - y0) if f["along"] == "y" else (x1 - x0)
            if depth < land - 1e-6:
                issues.append(f"[FATAL] {label} ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f}) is "
                              f"{depth:.0f} mm deep in the direction of travel < {land} "
                              f"({cite('K-STR-09')})")
            elif depth < w - 1e-6:
                issues.append(f"[MAJOR] {label} ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f}) is "
                              f"{depth:.0f} mm deep in the direction of travel, narrower than "
                              f"{f['name']} ({w:.0f} clear): a landing is never narrower than "
                              f"the stair and its width does not decrease along the way out "
                              f"({cite('K-STR-09')})")
        above = [z0 for poly, z0, _z1 in solids
                 if z0 > z + 1.0 and poly.intersection(lb).area > 1.0]
        if above and min(above) - z < head - 1e-6:
            issues.append(f"[FATAL] {label}: {min(above) - z:.0f} mm headroom < {head:.0f} "
                          f"({cite('K-STR-11')})")
    return issues


# ============================================================ basement
def _brief_ref():
    """Where the design writes down that its basement rooms are not
    habitable: the BRIEF.md beside it (assumption A9), if it says so."""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(V.__file__)), "BRIEF.md")
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
    except (OSError, AttributeError, TypeError):
        return "the design's assumption"
    return "BRIEF assumption A9" if "| A9 |" in txt else "the design's assumption"


def _open_to_air(o):
    """Does external opening `o` of a below-grade floor open to the air?
    Only into a declared LIGHTWELLS box (x0, y0, x1, y1, floor level) whose
    floor is at or below the opening's sill; a basement window without one
    faces the earth."""
    from shapely.geometry import Point
    wells = getattr(V, "LIGHTWELLS", None) or []
    if not wells:
        return False
    fl, kind, axis, t0, t1, a, b = o[:7]
    w0, w1, mid = min(t0, t1), max(t0, t1), (a + b) / 2.0
    face = V.facing(o)
    p = {"N": (mid, w1 + 50.0), "S": (mid, w0 - 50.0),
         "E": (w1 + 50.0, mid), "W": (w0 - 50.0, mid)}[face]
    lo = V.opening_z(o)[0]
    return any(w[0] <= p[0] <= w[2] and w[1] <= p[1] <= w[3] and w[4] <= lo + 1.0
               for w in wells)


def _basement(guards):
    """K-BSMT-01..06 for every storey in BELOW_GRADE_FLOORS."""
    from shapely.geometry import box as _b
    get = lambda n, d=None: getattr(V, n, d)
    issues = []
    below = [f for f in V.floors() if f in get("BELOW_GRADE_FLOORS", ())]
    st = _stacked()
    # K-BSMT-01: the slab over the basement, its soffit <= 1.5 m over the gate
    gate = get("GATE_LEVEL", V.STREET)
    lim = 1000 * val("K-BSMT-01", default=1.5)
    plot = _b(0, 0, V.PLOT_W, V.PLOT_D).buffer(1.0)
    for bf in below:
        over = next((f for f in st if V.LEVEL[f] > V.LEVEL[bf] + 1.0), None)
        if over is not None:
            soffit = V.LEVEL[over] - V.SLAB
            if soffit - gate > lim + 1e-6:
                issues.append(f"[FATAL] {bf}: the slab over it has its soffit at {soffit:+.0f}, "
                              f"{soffit - gate:.0f} mm over the gate level ({gate:+.0f}) > "
                              f"{lim:.0f} ({cite('K-BSMT-01')})")
        # K-BSMT-02: within the plot
        if not plot.contains(V.outline(bf)):
            b_ = V.outline(bf).bounds
            issues.append(f"[FATAL] {bf} ({b_[0]:.0f},{b_[1]:.0f})-({b_[2]:.0f},{b_[3]:.0f}) "
                          f"extends beyond the plot ({cite('K-BSMT-02')})")
    # K-BSMT-03: a HABITABLE basement room needs daylight (K.5.4.2): 10 % of
    # its floor in glass that opens to the air (a lightwell), net of frames
    ratio = val("K-WIN-01", default=0.1)
    air = {}
    for o in V.OPENINGS:
        if (o[0] not in below or o[8] is not None
                or o[1] not in (V.WIN, get("SLIDE", "slide")) or not _open_to_air(o)):
            continue
        lo, hi = V.opening_z(o)
        gw = max(0.0, abs(o[6] - o[5]) - 2 * FRAME)
        gh = max(0.0, (hi - lo) - 2 * FRAME)
        air[(o[0], o[7])] = air.get((o[0], o[7]), 0.0) + gw * gh / 1e6
    amen, svc = get("AMEN", "amenity"), get("SVC", "service")
    exempt = {amen: [], svc: []}
    for r in V.ROOMS:
        if r[6] not in below:
            continue
        if r[5] != V.HAB:
            if r[5] in exempt:
                exempt[r[5]].append(r[0])
            continue
        g, a = air.get((r[6], r[0]), 0.0), V.net_area(r)
        if g < ratio * a - 1e-6:
            issues.append(f"[FATAL] {r[6]} {r[0]} is habitable below grade with {g:.2f} m2 of "
                          f"glass open to the air = {100 * g / a:.1f}% of {a:.1f} m2 < "
                          f"{100 * ratio:.0f}% -- it needs a lightwell (LIGHTWELLS) "
                          f"({cite('K-BSMT-03')}, {cite('K-WIN-01')})")
    if exempt[amen] or exempt[svc]:
        listed = "; ".join(f"{', '.join(n)} ({k})" for k, n in exempt.items() if n)
        issues.append(f"[NOTE ] {'/'.join(below)}: K-BSMT-03 daylight applies to habitable "
                      f"rooms only; exempt: {listed} -- non-habitable recreation/service "
                      f"rooms, mechanically ventilated ({_brief_ref()}) ({cite('K-BSMT-03')})")
    # K-BSMT-04: a standard ENCLOSED exit stair, >= 1000 clear, to the exit level
    issues += _basement_stairs(below, guards)
    # K-BSMT-05/-06: services, not in the design data
    issues.append(f"[NOTE ] {'/'.join(below)}: not modelled -- sump pits >= 1 m below the "
                  f"lowest inlet with duty/standby submersible pumps; to be designed by MEP "
                  f"({cite('K-BSMT-05')})")
    issues.append(f"[NOTE ] {'/'.join(below)}: not modelled -- standalone self-contained "
                  f"emergency lighting (UAE FLSC ch. 6); to be designed by MEP "
                  f"({cite('K-BSMT-06')})")
    return issues


def _basement_stairs(below, guards):
    """K-BSMT-04: every basement is served by a stair that is not spiral,
    winder or open (no open risers), whose flights are >= 1000 clear, that
    reaches GROUND_FLOOR, and that is ENCLOSED on every floor it serves: its
    own room there, walled from every adjoining room (a partition's width
    between them), opening to them by DOORS only (not OPEN, glazed or
    sliding openings), no void opening it to another room or to the storey
    over it."""
    from shapely.geometry import box as _b
    get = lambda n, d=None: getattr(V, n, d)
    stairs = get("STAIRS", None)
    if not stairs:
        return [f"[MAJOR] {'/'.join(below)}: no STAIRS declared, so the basement's enclosed "
                f"exit stair is not checkable ({cite('K-BSMT-04')})"]
    issues = []
    wmin = val("K-BSMT-04", default=1000)
    gfl = get("GROUND_FLOOR", "GF")
    st = _stacked()
    flights = V.flights()
    part = get("PART", 150.0)
    served_by = {bf: [] for bf in below}
    for s in stairs:
        lo, hi = sorted((V.LEVEL[s["from"]], V.LEVEL[s["to"]]))
        serves = [f for f in st if lo - 1.0 <= V.LEVEL[f] <= hi + 1.0]
        if not any(f in below for f in serves):
            continue
        nm = s["name"]
        for bf in serves:
            if bf in below:
                served_by[bf].append(nm)
        typ = str(s.get("type", "straight"))
        if typ in ("spiral", "winder", "winders", "curved"):
            issues.append(f"[FATAL] {nm} serves the basement and is a {typ} stair "
                          f"({cite('K-BSMT-04')})")
        for f in (f for f in flights if f.get("stair") == nm):
            if "solid_to" in f and f["solid_to"] is None:
                issues.append(f"[FATAL] {f['name']} serves the basement with floating treads "
                              f"(open risers): an open stair ({cite('K-BSMT-04')})")
            c = _flight_clear(f, guards)
            if c < wmin - 1e-6:
                issues.append(f"[FATAL] {f['name']} serves the basement {c:.0f} mm clear "
                              f"< {wmin} ({cite('K-BSMT-04')})")
        if gfl not in serves:
            issues.append(f"[FATAL] {nm} serves the basement but does not reach the exit "
                          f"level {gfl} ({cite('K-BSMT-04')})")
        rx0, ry0, rx1, ry1 = s["rect"]
        srect = _b(rx0, ry0, rx1, ry1)
        above_top = next((f for f in st if V.LEVEL[f] > hi + 1.0), None)
        for fl in serves:
            rooms = [(r, _b(r[1], r[2], r[3], r[4]).intersection(srect).area)
                     for r in V.rooms_on(fl)]
            rooms = [p for p in rooms if p[1] > 0.5 * srect.area]
            if not rooms:
                issues.append(f"[FATAL] {nm} has no room of its own on {fl}: not enclosed "
                              f"({cite('K-BSMT-04')})")
                continue
            room = max(rooms, key=lambda p: p[1])[0]
            name, (qx0, qy0, qx1, qy1) = room[0], room[1:5]
            for o in V.OPENINGS:
                if o[0] != fl or o[8] is None or name not in (o[7], o[8]):
                    continue
                if o[1] != V.DOOR:
                    other = o[8] if o[7] == name else o[7]
                    issues.append(f"[FATAL] {nm}: on {fl} its room {name} opens to {other} "
                                  f"through a{'n' if o[1][0] in 'aeiou' else ''} {o[1]} "
                                  f"opening, not a door: not enclosed ({cite('K-BSMT-04')})")
            for q in V.rooms_on(fl):
                if q is room:
                    continue
                a0, b0, a1, b1 = q[1:5]
                if (a0 >= qx0 and b0 >= qy0 and a1 <= qx1 and b1 <= qy1) or \
                        (qx0 >= a0 and qy0 >= b0 and qx1 <= a1 and qy1 <= b1):
                    continue                        # nested: not a neighbour
                gx = max(a0 - qx1, qx0 - a1)
                gy = max(b0 - qy1, qy0 - b1)
                if (gx < part - 1.0 and gy < -1.0) or (gy < part - 1.0 and gx < -1.0):
                    issues.append(f"[FATAL] {nm}: on {fl} its room {name} and {q[0]} have no "
                                  f"wall between them ({max(gx, gy):.0f} mm): not enclosed "
                                  f"({cite('K-BSMT-04')})")
            qbox = _b(qx0, qy0, qx1, qy1)
            for vname, vx0, vy0, vx1, vy1, vfls in V.VOIDS:
                vb = _b(vx0, vy0, vx1, vy1)
                if vb.intersection(qbox).area < 1.0:
                    continue
                if fl in vfls and not qbox.buffer(1.0).contains(vb):
                    issues.append(f"[FATAL] {nm}: on {fl} the {vname.lower()} opens its room "
                                  f"{name} to the rooms round it ({cite('K-BSMT-04')})")
            # the storey over the stair's top floor must not be open to it
            if above_top is not None and abs(V.LEVEL[fl] - hi) < 1.0:
                for vname, vx0, vy0, vx1, vy1, vfls in V.VOIDS:
                    if above_top in vfls and \
                            _b(vx0, vy0, vx1, vy1).intersection(qbox).area > 1.0:
                        issues.append(f"[FATAL] {nm}: the {vname.lower()} opens its room "
                                      f"{name} to {above_top} ({cite('K-BSMT-04')})")
    for bf in below:
        if not served_by[bf]:
            issues.append(f"[FATAL] {bf} is served by no stair: a basement needs a standard "
                          f"enclosed exit stair ({cite('K-BSMT-04')})")
    return issues


if __name__ == "__main__":
    iss = checks()
    print(f"Dubai Building Code 2021: {len(R)} rules loaded")
    print(f"{sum(i.startswith('[FATAL]') for i in iss)} fatal, "
          f"{sum(i.startswith('[MAJOR]') for i in iss)} major\n")
    for i in iss:
        print("  " + i)
