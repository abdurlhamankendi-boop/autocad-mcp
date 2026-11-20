"""
Two-storey open-plan dwelling - design definition and drawing set.

Layout decisions, and the audit findings they answer:

  * Open-plan living/dining/kitchen occupies the whole south face with full
    glazing to the garden, instead of cellular rooms off a corridor.
  * Entrance is from the north through a projecting porch into a compact hall,
    so circulation is a room, not a spine corridor.
  * Every room -- including the WC and the first-floor bathroom -- has an
    external wall and a window. The previous plan buried both internally.
  * Wet areas stack: first-floor bathroom sits directly over the ground-floor
    utility/WC so soil and supply runs are vertical.
  * Stair is 14 risers at 207mm over a 2900 floor-to-floor. The previous 13
    risers gave 226.9mm, over the 220mm limit for a private stair.
  * Doors are declared BY THE OPENING they sit in, so a leaf can never be
    drawn on a solid wall and a swing can never land on the wrong side.
"""

from __future__ import annotations

import math

from plan_dxf import Plan, OUT, rect_pts, poly

# ---------------------------------------------------------------- envelope
W, H = 13000.0, 9600.0
EXT, PART = 300.0, 100.0
IX0, IY0, IX1, IY1 = EXT, EXT, W - EXT, H - EXT      # interior face
FF = 2900.0                                          # floor to floor
RISERS = 14

PORCH = (5700.0, H, 7100.0, H + 1500.0)              # projects north
BAY = (1400.0, -900.0, 4200.0, 0.0)                  # living bay, south

# circulation
# The hall is 3700 wide with the stair centred in it, leaving ~1400 of
# circulation on BOTH sides. An earlier version put a 900 stair 100mm off the
# snug wall, so that door opened straight onto the stair string.
HALL_X0, HALL_X1 = 4900.0, 7600.0
HALL_Y0 = 5400.0
STAIR = (5800.0, 5400.0, 6700.0, 8650.0)             # 900 wide, 13 goings


class Opening:
    """A gap in a wall. Doors and windows are declared against one of these,
    which is what makes 'door on a solid wall' unrepresentable."""

    __slots__ = ("axis", "fixed0", "fixed1", "a", "b", "kind", "swing", "hinge_a")

    def __init__(self, axis, fixed0, fixed1, a, b, kind, swing=None, hinge_a=True):
        self.axis = axis          # "h": run along x; "v": run along y
        self.fixed0, self.fixed1 = fixed0, fixed1
        self.a, self.b = a, b
        self.kind = kind          # "door" | "window" | "open"
        self.swing = swing        # degrees the leaf opens toward
        self.hinge_a = hinge_a


class WallRun:
    def __init__(self, axis, fixed0, fixed1, a, b, structural=True):
        self.axis, self.fixed0, self.fixed1 = axis, fixed0, fixed1
        self.a, self.b = a, b
        self.structural = structural
        self.openings: list[Opening] = []

    def opening(self, a, b, kind, swing=None, hinge_a=True):
        o = Opening(self.axis, self.fixed0, self.fixed1, a, b, kind, swing, hinge_a)
        self.openings.append(o)
        return o

    def segments(self):
        out, cur = [], self.a
        for o in sorted(self.openings, key=lambda o: o.a):
            if o.a > cur:
                out.append((cur, o.a))
            cur = max(cur, o.b)
        if cur < self.b:
            out.append((cur, self.b))
        return out

    def solids(self):
        """Wall segment rectangles, for unioning. Drawing each as its own
        closed polyline leaves the shared edge visible at every T and corner --
        lines running straight through the poche."""
        out = []
        for s, e in self.segments():
            if self.axis == "h":
                out.append((s, self.fixed0, e, self.fixed1))
            else:
                out.append((self.fixed0, s, self.fixed1, e))
        return out

    def draw_openings(self, p: Plan):
        for o in self.openings:
            if o.kind == "window":
                if self.axis == "h":
                    p.window(o.a, self.fixed0, o.b, self.fixed1, horizontal=True)
                else:
                    p.window(self.fixed0, o.a, self.fixed1, o.b, horizontal=False)
            elif o.kind == "door":
                draw_door(p, o)


def draw_joined_walls(p: Plan, extra_solids=()):
    """Union every wall rectangle, then trace only the resulting boundary.

    unary_union deletes the edges shared by abutting rectangles, so junction
    lines simply never exist -- no cleanup pass needed. Coordinates are snapped
    first, because a sub-micron mismatch leaves a sliver instead of a merge.
    """
    from shapely import box as sbox, set_precision
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import unary_union

    polys = [set_precision(sbox(*r), 1e-6) for r in extra_solids]
    merged = unary_union(polys)
    if isinstance(merged, Polygon):
        merged = MultiPolygon([merged])

    for g in merged.geoms:
        if g.is_empty or g.area < 1.0:
            continue
        gx0, gy0, gx1, gy1 = g.bounds
        touches_envelope = (gx0 < 1 or gy0 < 1 or gx1 > W - 1 or gy1 > H - 1)
        layer = "A-WALL-EXTR" if touches_envelope else "A-WALL"
        ext = list(g.exterior.coords)[:-1]
        p.msp.add_lwpolyline(ext, close=True, dxfattribs={"layer": layer})
        hatch = p.msp.add_hatch(color=8, dxfattribs={"layer": "A-WALL-PATT"})
        hatch.paths.add_polyline_path(ext, is_closed=True, flags=1)   # external
        for ring in g.interiors:
            pts = list(ring.coords)[:-1]
            p.msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
            hatch.paths.add_polyline_path(pts, is_closed=True, flags=0)  # island
        hatch.set_solid_fill(color=8)
    return merged


def draw_door(p: Plan, o: Opening):
    """Derive leaf and swing from the opening geometry, so the closed leaf
    always lies in the gap and the arc always sweeps into the named room."""
    width = o.b - o.a
    mid = (o.fixed0 + o.fixed1) / 2.0
    if o.axis == "h":
        hinge = (o.a, mid) if o.hinge_a else (o.b, mid)
        closed = 0.0 if o.hinge_a else 180.0
    else:
        hinge = (mid, o.a) if o.hinge_a else (mid, o.b)
        closed = 90.0 if o.hinge_a else 270.0
    open_dir = o.swing
    # take the shorter sweep from closed to open
    delta = (open_dir - closed + 540.0) % 360.0 - 180.0
    a0, a1 = (closed + delta, closed) if delta < 0 else (closed, closed + delta)
    p.line(hinge[0], hinge[1],
           hinge[0] + width * math.cos(math.radians(open_dir)),
           hinge[1] + width * math.sin(math.radians(open_dir)), "A-DOOR")
    p.arc(hinge[0], hinge[1], width, a0, a1, "A-DOOR-SWNG")


# ---------------------------------------------------------------- rooms
SHORT = {"KITCHEN / DINING": "KITCHEN", "UTILITY": "UTIL",
         "EN-SUITE": "ENS", "BATHROOM": "BATH", "BEDROOM 1": "BED 1",
         "BEDROOM 2": "BED 2", "BEDROOM 3": "BED 3", "BEDROOM 4": "BED 4"}


class Room:
    def __init__(self, name, x1, y1, x2, y2, kind="habitable"):
        self.name, self.kind = name, kind
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    @property
    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1) / 1e6

    @property
    def centre(self):
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def touches_external(self):
        return (abs(self.x1 - IX0) < 1 or abs(self.x2 - IX1) < 1 or
                abs(self.y1 - IY0) < 1 or abs(self.y2 - IY1) < 1)


# ================================================================ GROUND
def ground_floor():
    runs, rooms = [], []

    ext_s = WallRun("h", 0, EXT, 0, W)
    ext_s.opening(1400, 4200, "window")          # living bay glazing
    ext_s.opening(6600, 9200, "window")          # dining, sliding doors
    ext_s.opening(10200, 12000, "window")        # kitchen
    ext_n = WallRun("h", H - EXT, H, 0, W)
    ext_n.opening(5200, 6200, "door", swing=270)  # entrance, swings into hall
    ext_n.opening(1200, 3200, "window")          # snug
    ext_n.opening(7900, 9200, "window")          # utility
    ext_n.opening(9900, 12300, "window")         # family
    ext_w = WallRun("v", 0, EXT, 0, H)
    ext_w.opening(1500, 3800, "window")          # living
    ext_w.opening(6200, 8400, "window")          # snug
    ext_e = WallRun("v", W - EXT, W, 0, H)
    ext_e.opening(1500, 3800, "window")          # kitchen
    ext_e.opening(6000, 8300, "window")          # family
    runs += [ext_s, ext_n, ext_w, ext_e]

    p1 = WallRun("h", 5300, 5400, IX0, IX1, structural=False)
    p1.opening(5100, 7400, "open")               # living side flows into hall
    p1.opening(10300, 11200, "door", swing=90)   # family
    p2 = WallRun("v", 4800, 4900, HALL_Y0, IY1, structural=False)
    p2.opening(6300, 7200, "door", swing=180)    # snug
    p3 = WallRun("v", HALL_X1, 7700, HALL_Y0, IY1, structural=False)
    p3.opening(5700, 6500, "door", swing=0)      # wc
    p3.opening(7500, 8300, "door", swing=0)      # utility
    p4 = WallRun("h", 7200, 7300, 7700, 9400, structural=False)
    p5 = WallRun("v", 9400, 9500, HALL_Y0, IY1, structural=False)
    # Living and kitchen/dining are one volume joined by a 3800 opening -- two
    # rooms at 1.14:1 and 1.32:1 rather than a single 2.48:1 tube, which the
    # proportion check flags as reading like a corridor.
    p6 = WallRun("v", 6000, 6100, IY0, 5300, structural=False)
    p6.opening(900, 4700, "open")
    runs += [p1, p2, p3, p4, p5, p6]

    rooms += [
        Room("LIVING", IX0, IY0, 6000, 5300),
        Room("KITCHEN / DINING", 6100, IY0, IX1, 5300),
        Room("HALL", HALL_X0, HALL_Y0, HALL_X1, IY1, "circulation"),
        Room("SNUG", IX0, HALL_Y0, 4800, IY1),
        Room("WC", 7700, HALL_Y0, 9400, 7200, "wet"),
        Room("UTILITY", 7700, 7300, 9400, IY1, "wet"),
        Room("FAMILY", 9500, HALL_Y0, IX1, IY1),
    ]
    return runs, rooms


# ================================================================ FIRST
def first_floor():
    runs, rooms = [], []

    ext_s = WallRun("h", 0, EXT, 0, W)
    ext_s.opening(1400, 3600, "window")
    ext_s.opening(6400, 8600, "window")
    ext_s.opening(9900, 12000, "window")
    ext_n = WallRun("h", H - EXT, H, 0, W)
    ext_n.opening(1200, 3200, "window")          # bed 2
    ext_n.opening(7900, 9200, "window")          # bathroom
    ext_n.opening(9900, 12300, "window")         # study
    ext_w = WallRun("v", 0, EXT, 0, H)
    ext_w.opening(1500, 3800, "window")          # master
    ext_w.opening(6200, 8400, "window")          # bed 2
    ext_e = WallRun("v", W - EXT, W, 0, H)
    ext_e.opening(1500, 3800, "window")          # bed 4
    ext_e.opening(6000, 8300, "window")          # study
    runs += [ext_s, ext_n, ext_w, ext_e]

    q1 = WallRun("h", 5300, 5400, IX0, IX1, structural=False)
    q1.opening(2400, 3300, "door", swing=270)    # bedroom 1
    q1.opening(6900, 7800, "door", swing=270)    # bedroom 3
    q1.opening(10600, 11500, "door", swing=270)  # bedroom 4
    q2 = WallRun("v", 4800, 4900, HALL_Y0, IY1, structural=False)
    q2.opening(6300, 7200, "door", swing=180)    # bed 2
    q3 = WallRun("v", HALL_X1, 7700, HALL_Y0, IY1, structural=False)
    q3.opening(5700, 6500, "door", swing=0)      # ensuite
    q3.opening(7400, 8300, "door", swing=0)      # bathroom
    q4 = WallRun("h", 6800, 6900, 7700, 9400, structural=False)   # ensuite|bath
    q5 = WallRun("v", 9400, 9500, HALL_Y0, IY1, structural=False)
    q5.opening(6400, 7300, "door", swing=0)      # study
    q6 = WallRun("v", 6000, 6100, IY0, 5300, structural=False)    # master|bed3
    q7 = WallRun("v", 9400, 9500, IY0, 5300, structural=False)    # bed3|bed4
    runs += [q1, q2, q3, q4, q5, q6, q7]

    rooms += [
        Room("BEDROOM 1", IX0, IY0, 6000, 5300),
        Room("BEDROOM 3", 6100, IY0, 9400, 5300),
        Room("BEDROOM 4", 9500, IY0, IX1, 5300),
        Room("LANDING", HALL_X0, HALL_Y0, HALL_X1, IY1, "circulation"),
        Room("BEDROOM 2", IX0, HALL_Y0, 4800, IY1),
        Room("EN-SUITE", 7700, HALL_Y0, 9400, 6800, "wet"),
        Room("BATHROOM", 7700, 6900, 9400, IY1, "wet"),
        Room("STUDY", 9500, HALL_Y0, IX1, IY1),
    ]
    return runs, rooms


# ================================================================ CHECKS
def validate(runs, rooms, label):
    """Catch the defect classes the audit found, before anything is issued."""
    issues = []
    for r in runs:
        for o in r.openings:
            if o.a < r.a - 1 or o.b > r.b + 1:
                issues.append(f"opening {o.a:.0f}-{o.b:.0f} runs past its wall "
                              f"({r.a:.0f}-{r.b:.0f})")
            if o.kind == "door" and o.swing is None:
                issues.append(f"door {o.a:.0f}-{o.b:.0f} has no swing direction")
            if o.kind == "door" and not (700 <= o.b - o.a <= 1100):
                issues.append(f"door {o.a:.0f}-{o.b:.0f} width "
                              f"{o.b - o.a:.0f} outside 700-1100")

    # every room reachable and lit
    # Only openings in EXTERNAL walls admit daylight. Counting internal doors
    # here made every internal room look lit and reported zero issues.
    win_edges = []
    for r in runs:
        if not r.structural:
            continue
        for o in r.openings:
            if o.kind in ("window", "door"):
                win_edges.append((r.axis, r.fixed0, r.fixed1, o.a, o.b))
    for rm in rooms:
        if rm.kind == "circulation":
            continue
        lit = False
        for axis, f0, f1, a, b in win_edges:
            if axis == "h" and (abs(f1 - rm.y1) < 1 or abs(f0 - rm.y2) < 1):
                if a < rm.x2 and b > rm.x1:
                    lit = True
            if axis == "v" and (abs(f1 - rm.x1) < 1 or abs(f0 - rm.x2) < 1):
                if a < rm.y2 and b > rm.y1:
                    lit = True
        if not lit:
            note = ("internal - needs mechanical extract"
                    if rm.kind == "wet" else "** HABITABLE ROOM, NO DAYLIGHT **")
            issues.append(f"{rm.name}: no external window ({note})")

    # A door must not open onto furniture. This was missed for a long time
    # because validate() only checked doors against walls and the stair.
    try:
        import math as _m
        import furniture_layout as _fl
        from shapely.geometry import box as _box, Polygon as _Poly
        floor = "ground" if any(r.name == "LIVING" for r in rooms) else "first"
        items = [(k, _fl.footprint(k, x, y, rot))
                 for k, x, y, rot in (_fl.GROUND if floor == "ground"
                                      else _fl.FIRST)]
        for r in runs:
            for o in r.openings:
                if o.kind != "door" or o.swing is None:
                    continue
                wd = o.b - o.a
                mid = (o.fixed0 + o.fixed1) / 2.0
                hinge, closed = (((o.a, mid), 0.0) if o.axis == "h"
                                 else ((mid, o.a), 90.0))
                d = (o.swing - closed + 540.0) % 360.0 - 180.0
                a0, a1 = (closed + d, closed) if d < 0 else (closed, closed + d)
                arc = [(hinge[0] + wd * _m.cos(_m.radians(a)),
                        hinge[1] + wd * _m.sin(_m.radians(a)))
                       for a in [a0 + (a1 - a0) * i / 16 for i in range(17)]]
                sweep = _Poly([hinge] + arc)
                for key, fp in items:
                    if not fp:
                        continue
                    ov = sweep.intersection(_box(*fp)).area
                    if ov > 1000:
                        issues.append(
                            f"door at ({hinge[0]:.0f},{hinge[1]:.0f}) opens onto "
                            f"{key} ({ov / 1e6:.2f} m2)")
    except Exception as exc:
        issues.append(f"door/furniture check skipped: {exc}")

    # stair geometry
    rise = FF / RISERS
    if rise > 220:
        issues.append(f"stair rise {rise:.1f}mm exceeds 220mm")

    # stair must not foul a doorway
    sx0, sy0, sx1, sy1 = STAIR
    for r in runs:
        if r.axis == "v" and abs(r.fixed1 - sx0) < 400:
            for o in r.openings:
                if o.kind == "door" and o.a < sy1 and o.b > sy0:
                    issues.append(f"door {o.a:.0f}-{o.b:.0f} fouls the stair")

    gia = sum(r.area for r in rooms)
    circ = sum(r.area for r in rooms if r.kind == "circulation")
    pct = 100.0 * circ / gia if gia else 0.0
    if pct > 8.0:
        issues.append(f"circulation {circ:.1f} m2 = {pct:.1f}% of GIA "
                      f"(target <=8% for a house)")
    for rm in rooms:
        w_, d_ = rm.x2 - rm.x1, rm.y2 - rm.y1
        ar = max(w_, d_) / min(w_, d_)
        if ar > 2.0 and rm.kind == "habitable":
            issues.append(f"{rm.name} aspect {ar:.2f}:1 - over 2:1 reads as "
                          f"a corridor")
    print(f"  [{label}] rise {rise:.1f}mm over {RISERS} risers; "
          f"{len(rooms)} rooms; {len(issues)} issue(s)")
    for i in issues:
        print("     !", i)
    return issues


# ================================================================ FURNITURE
def furnish(p: Plan, rooms):
    F, S = "A-FURN", "A-FLOR-FIXT"
    R = lambda x1, y1, x2, y2, L=F: p.box(x1, y1, x2, y2, L)

    def bed(cx, y, w, l):
        R(cx - w / 2, y, cx + w / 2, y + l)
        p.line(cx - w / 2, y + l - 450, cx + w / 2, y + l - 450, F)
        R(cx - w / 2 + 60, y + l - 400, cx - 60, y + l - 60)
        R(cx + 60, y + l - 400, cx + w / 2 - 60, y + l - 60)

    def seats(cx, cy, w, d, n):
        R(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2)
        step = w / (n + 1)
        for i in range(n):
            x = cx - w / 2 + step * (i + 1)
            R(x - 230, cy + d / 2 + 90, x + 230, cy + d / 2 + 560)
            R(x - 230, cy - d / 2 - 560, x + 230, cy - d / 2 - 90)

    by = {r.name: r for r in rooms}
    if "LIVING" in by:
        # kitchen run east, dining centre, living west - one open volume
        R(9700, 400, 12600, 1000)                    # counter run
        R(10100, 500, 10800, 900, S)                 # sink
        for cx in (11300, 11750):
            p.circle(cx, 700, 130, F)                # hob
        R(12000, 400, 12600, 1000)                   # oven
        R(9700, 4300, 10500, 5200)                   # fridge
        seats(8300, 2700, 1800, 1000, 3)             # dining
        R(700, 600, 1000, 3000)                      # bookcase
        R(1500, 500, 4000, 1400)                     # sofa to bay
        p.line(1500, 1150, 4000, 1150, F)
        R(4400, 1700, 5300, 3300)                    # armchair
        seats(2600, 3200, 1600, 900, 0)              # coffee table
        R(600, 4200, 3200, 4700)                     # media unit
    if "SNUG" in by:
        R(600, 5900, 1200, 8300)
        R(1800, 8600, 4400, 9200)
        seats(2900, 7100, 1700, 900, 0)
    if "FAMILY" in by:
        R(10800, 5700, 11500, 8900)
        R(12000, 6200, 12500, 8000)
    if "UTILITY" in by:
        R(8900, 8700, 10300, 9200)
        R(8950, 8750, 9550, 9150)
        R(9650, 8750, 10250, 9150)
    if "WC" in by:
        R(8850, 5600, 9450, 6250, S)
        R(9700, 5600, 10300, 6000, S)
    for nm in ("BEDROOM 1", "BEDROOM 2", "BEDROOM 3", "BEDROOM 4"):
        if nm not in by:
            continue
        r = by[nm]
        cx, cy = r.centre
        if nm == "BEDROOM 1":
            bed(2400, 500, 1800, 2100); R(700, 4300, 3400, 4900)
        elif nm == "BEDROOM 2":
            bed(2200, 5700, 1500, 2000); R(600, 8500, 3000, 9100)
        elif nm == "BEDROOM 3":
            bed(7600, 500, 1500, 2000); R(6300, 4400, 8600, 5000)
        else:
            bed(11000, 500, 1400, 2000); R(9800, 4400, 11800, 5000)
    if "BATHROOM" in by:
        R(8850, 7100, 10250, 7800, S)                # bath
        R(8850, 8500, 9450, 9150, S)                 # wc
        R(9700, 8600, 10300, 9000, S)                # basin
    if "EN-SUITE" in by:
        R(8850, 5600, 9450, 6250, S)
        R(9700, 5600, 10300, 6000, S)
        R(8850, 6350, 9700, 6750, S)
    if "STUDY" in by:
        R(10800, 5700, 12500, 6400)
        R(11500, 6600, 12000, 7100)


# ================================================================ BUILD
def _overlap(a, b, pad=140.0):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or
                a[3] + pad < b[1] or b[3] + pad < a[1])


def place_labels(p: Plan, rooms, obstacles, show_area=True):
    """Anchor each label at the largest circle that fits inside the room AFTER
    the furniture is subtracted, and size the text to that circle's radius.

    The previous grid search tested a fixed set of candidate points and took
    the least-bad one, so in a densely furnished room every candidate collided
    and the label landed on the furniture anyway.
    """
    from shapely import Polygon, MultiPolygon, box as sbox
    from shapely import maximum_inscribed_circle
    from shapely.ops import unary_union

    obs_polys = [sbox(*o) for o in obstacles]
    obs_union = unary_union(obs_polys) if obs_polys else None

    gia = 0.0
    for rm in rooms:
        gia += rm.area
        atxt = f"{rm.area:.1f} m2"
        shell = Polygon([(rm.x1, rm.y1), (rm.x2, rm.y1),
                         (rm.x2, rm.y2), (rm.x1, rm.y2)]).buffer(-150)
        free = shell.difference(obs_union) if obs_union is not None else shell
        if isinstance(free, MultiPolygon):
            free = max(free.geoms, key=lambda g: g.area)
        if free.is_empty or free.area < 1e5:
            free = shell
        try:
            circ = maximum_inscribed_circle(free)
            cx, cy = circ.coords[0]
            radius = circ.length
        except Exception:
            cx, cy = rm.centre
            radius = 600.0

        # size the text to the clear circle, within the ISO ladder
        label = rm.name
        longest = max(len(label), len(atxt))
        h = (1.75 * radius) / (longest * 0.62)
        if h < 200.0 and label in SHORT:
            label = SHORT[label]            # abbreviate before going illegible
            longest = max(len(label), len(atxt))
            h = (1.75 * radius) / (longest * 0.62)
        h = max(180.0, min(250.0, h))
        two_line = radius > (h * 1.6)

        p.text(label, cx, cy + (h * 0.35 if two_line else 0), h,
               "A-ANNO-TEXT", align="MIDDLE_CENTER")
        if show_area and two_line:
            p.text(atxt, cx, cy - h * 1.1, h * 0.82, "A-ANNO-TEXT",
                   align="MIDDLE_CENTER")
        obstacles.append((cx - h * longest * 0.35, cy - h * 1.5,
                          cx + h * longest * 0.35, cy + h * 1.2))
    return gia


def furniture_boxes(rooms):
    """Approximate obstacle boxes so labels dodge the furniture."""
    return []


def draw_floor(sheet_no, name, runs, rooms, technical=True, ground=True):
    p = Plan(name)
    solids = []
    if ground:
        px0, py0, px1, py1 = PORCH
        solids += [(px0, py0, px0 + 200, py1), (px1 - 200, py0, px1, py1),
                   (px0, py1 - 200, px1, py1)]
        bx0, by0, bx1, by1 = BAY
        solids += [(bx0, by0, bx0 + 200, by1), (bx1 - 200, by0, bx1, by1)]
    for r in runs:
        solids += r.solids()
    draw_joined_walls(p, solids)
    for r in runs:
        r.draw_openings(p)
    if ground:
        bx0, by0, bx1, by1 = BAY
        p.window(bx0 + 200, by0, bx1 - 200, by0 + 200)   # bay glazing

    # stair
    sx0, sy0, sx1, sy1 = STAIR
    poly(p.msp, rect_pts(sx0, sy0, sx1, sy1), "A-FLOR-STRS")
    goings = RISERS - 1
    d = (sy1 - sy0) / goings
    for i in range(1, goings):
        p.line(sx0, sy0 + i * d, sx1, sy0 + i * d, "A-FLOR-STRS")
    cx = (sx0 + sx1) / 2
    p.line(cx, sy0 + d * .5, cx, sy1 - d * .5, "A-FLOR-STRS")
    hd_ = sy1 - d * .5
    p.line(cx, hd_, cx - 130, hd_ - 230, "A-FLOR-STRS")
    p.line(cx, hd_, cx + 130, hd_ - 230, "A-FLOR-STRS")
    p.text("UP" if ground else "DN", sx1 + 150, (sy0 + sy1) / 2, 190,
           "A-ANNO-TEXT")
    p.text(f"{RISERS}R @ {FF / RISERS:.0f}", sx1 + 150, (sy0 + sy1) / 2 - 330,
           150, "A-ANNO-TEXT")

    # Furniture is inserted later as real AutoCAD blocks from the ACA content
    # library, so nothing is drawn here -- but the footprints those blocks will
    # occupy are reserved so room labels still dodge them.
    import furniture_layout as fl
    from ezdxf import bbox as _bbox
    obstacles = [(sx0, sy0, sx1, sy1)]
    obstacles += fl.obstacles("ground" if ground else "first")
    for e in p.msp.query("LWPOLYLINE CIRCLE ARC LINE"):
        if e.dxf.layer in ("A-FURN", "A-FLOR-FIXT", "A-DOOR", "A-FLOR-STRS"):
            try:
                ext = _bbox.extents([e])
                obstacles.append((ext.extmin.x, ext.extmin.y,
                                  ext.extmax.x, ext.extmax.y))
            except Exception:
                pass
    gia = place_labels(p, rooms, obstacles, show_area=True)

    if technical:
        p.grid([0, HALL_X0, HALL_X1, W], [0, 5300, HALL_Y0, H], 0, W, 0, H)
        p.dim_h(0, HALL_X0, 0, 3400)
        p.dim_h(HALL_X0, HALL_X1, 0, 3400)
        p.dim_h(HALL_X1, W, 0, 3400)
        p.dim_h(0, W, 0, 4600)
        p.dim_v(0, 5300, 0, 3400)
        p.dim_v(5300, H, 0, 3400)
        p.dim_v(0, H, 0, 4600)
    p.north(W + 1900, H - 900)
    p.scale_bar(0, -6800)
    p.title_block(sheet_no, name + ("" if technical else "  -  PRESENTATION"), gia)
    return p, gia


if __name__ == "__main__":
    sheets = []
    for tech in (True, False):
        for gnd in (True, False):
            runs, rooms = (ground_floor() if gnd else first_floor())
            base = "A-10" if tech else "A-11"
            no = f"{base}{1 if gnd else 2}"
            nm = ("GROUND FLOOR PLAN" if gnd else "FIRST FLOOR PLAN")
            validate(runs, rooms, no)
            p, gia = draw_floor(no, nm, runs, rooms, technical=tech, ground=gnd)
            fn = f"{no}_{'GF' if gnd else 'FF'}_{'TECH' if tech else 'PRES'}"
            p.save(fn)
            png = p.render(fn, dpi=150)
            print(f"  {no} {'TECH' if tech else 'PRES'}  GIA {gia:6.2f} m2  {png}")
            sheets.append(fn)
    print("\nsheets:", len(sheets))
