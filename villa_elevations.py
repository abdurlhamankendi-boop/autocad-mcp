"""Elevations A-201..A-204 and section A-301, PROJECTED from the render model.

Why this exists: the only elevations and sections in Desktop\\Villa were drawn
from the superseded 09-06 massing (PROJECT_STATE s9-s11, audit P0/P1). These are
not drawn at all -- they are hidden-line projections of the SAME build123d model
villa_gltf.py renders. building(), boundary() and landscape() are called here,
read-only, so a sheet cannot show a window the render does not have, and a
change to villa_design.py reaches the elevations on the next run.

    villa_design -> villa_gltf.building()/boundary()/landscape()
                 -> OCCT HLR (the projector build123d.exporters.Drawing builds)
                 -> plan_dxf.Plan (layers, lineweights, text, scale bar)
                 -> VILLA_A20x.dxf / VILLA_A301.dxf  -> PNG preview

Orientation (verified on build123d 0.13 with an asymmetric marker, and again
at run time by check_orientation): look_at is the world origin, so a projected
point is u = P . (up x dir), v = P . Z -- true heights, never re-centred.
    south  look_from (0,-1,0)  u = +X   east on the right
    north  look_from (0, 1,0)  u = -X   east on the left
    east   look_from (1, 0,0)  u = +Y   north on the right
    west   look_from (-1,0,0)  u = -Y   north on the left
    A-A    look_from (-1,0,0)  u = -Y   looking EAST, north on the left

Lineweights: cut 0.70 / beyond 0.25 / hidden not drawn / ground line 1.00.

The front boundary wall is left out of each elevation (it would hide the whole
ground floor -- the elevation is taken from inside the plot), and the terrain
is clipped at street level (the 300 mm sub-base is not drawn above ground).
The render model now HAS the stair (villa_gltf group 'stair', from
villa_design.stair_parts: solid treads and half-landing, the glass guards on
its open sides and its handrails -- review of 2026-09-26), so the section
projects it like everything else. stair_solid() builds the same parts here
for design data without a 'stair' group (it used to be the only stair).

Checks -- the script exits 1 if any fails (sheets are still written, stamped
CHECKS FAILED, so the failure can be inspected rather than a stale sheet kept):
  * projection is not mirrored (synthetic marker + fins/garden on the model),
    and the per-group HLR equals build123d's Drawing (same total length);
  * every external opening in villa_design.OPENINGS on a facade is found in
    that elevation. Its outline is the edge of its void in the house FABRIC
    (never the joinery: frame and glass edges run 60 mm inside every void).
    ALL FOUR sides must be in the model at their villa_design u/v: the
    nearest line parallel to each side, in a projection (hidden lines
    included) of the fabric within the opening's own wall thickness, lies
    within 20 mm. 3+ of those four lines must also be drawn (half visible in
    the elevation); a side not drawn is thereby present-but-hidden in the
    model. Fault-injected: any side moved by more than 20 mm fails;
  * the top of every drawing equals the model's bounding box; the ground line
    matches villa_design.ground_at();
  * every level marker (computed from villa_design constants) sits on a model
    edge; the external steps appear in the elevation of their door;
  * the section is open GF..RF through the double-height volume, the first
    floor slab is open over the stair well, and the stair spans GF..FF.

A PROJECT design (projects\\<name>, run through run_project.py, or with
VILLA_DESIGN_DIR set -- that folder goes first on sys.path) is drawn by the
same code; what it declares switches on what the villa does not have, each
read with hasattr/getattr so the villa's sheets are unchanged
(tests/regress_villa.py, tests/test_project_elevations.py):
  * landscape_parts (OWN_SITE): the finished ground is the top of the terrain
    AND its surfacing; the hedges standing in front of the house are left out
    of an elevation like the boundary wall; a threshold flush with the paving
    is drawn by the ground line; E/W also check the forecourt ramp falls to
    the street on the north; no external steps is reported N/A;
  * a 'stone' group is hatched where it is seen, and checked against
    STONE_ZONES on the house's own face (less openings and what is in front);
  * SECTION_X (OWN_SECTION): A-A is cut there and looks towards the stair
    rising in the void it cuts (the Fairway: WEST, the feature stair beyond);
    each cut VOID is open from the floor under it to the soffit over it, its
    slab open over it; every STAIRS record rises in the model as flights()
    says (every tread probed), a stair seen beyond is drawn at every tread;
    SECTION_TEXT, POOL_LABEL and the pool's own datums (sun ledge) are used;
  * BELOW_GRADE_FLOORS (a basement): never an elevation datum or opening (the
    view is clipped at the street); in the section a datum, cut, and drawn
    in earth hatched below the model's terrain slab.

Run:  python villa_elevations.py
      python run_project.py fairway villa_elevations.py   (VILLA_OUT set first)
"""

from __future__ import annotations

import bisect
import datetime
import importlib
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
# A PROJECT's design folder (run_project.py and the MCP server set
# VILLA_DESIGN_DIR) goes in FRONT of this folder, so its villa_design.py is
# never shadowed by the villa's. Unset (the villa), nothing changes.
_DESIGN_DIR = os.environ.get("VILLA_DESIGN_DIR")
if _DESIGN_DIR and os.path.isfile(os.path.join(_DESIGN_DIR, "villa_design.py")):
    _DESIGN_DIR = os.path.abspath(_DESIGN_DIR)
    while _DESIGN_DIR in sys.path:
        sys.path.remove(_DESIGN_DIR)
    sys.path.insert(0, _DESIGN_DIR)


def _load(name, tries=4, wait=30.0):
    """Import a project module, retrying: villa_design / villa_gltf are edited
    by another agent while this runs and can be caught half-written."""
    for i in range(tries):
        try:
            return importlib.import_module(name)
        except Exception as exc:                        # noqa: BLE001
            for m in [m for m in sys.modules if m.startswith("villa_")]:
                sys.modules.pop(m, None)                # re-import the chain
            if i == tries - 1:
                raise
            print(f"  import {name} failed ({type(exc).__name__}: {exc}) -- "
                  f"retrying in {wait:.0f}s")
            time.sleep(wait)


V = _load("villa_design")
G = _load("villa_gltf")          # read-only: building(), boundary(), landscape()
PD = _load("plan_dxf")
try:                             # builder-side helpers (newer); optional
    VG = importlib.import_module("villa_geom")
except Exception:                                       # noqa: BLE001
    VG = None

from OCP.BRepLib import BRepLib                                   # noqa: E402
from OCP.HLRAlgo import HLRAlgo_Projector                         # noqa: E402
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape          # noqa: E402
from OCP.gp import gp_Ax2, gp_Pnt                                 # noqa: E402
from build123d import (Compound, GeomType, Polyline, Shape, Vector,  # noqa: E402
                       extrude, make_face)
from build123d.exporters import Drawing                           # noqa: E402
from build123d.geometry import TOLERANCE                          # noqa: E402
from shapely.geometry import LineString, Point, Polygon            # noqa: E402
from shapely.geometry import box as sbox                          # noqa: E402
from shapely.ops import polygonize, unary_union                   # noqa: E402

# VILLA_OUT redirects the set, as villa_geom.out_dir() does for every builder
OUT = VG.out_dir() if VG and hasattr(VG, "out_dir") else (
    os.environ.get("VILLA_OUT") or r"C:\Users\lsire\OneDrive\Desktop\Villa")
BWALL = getattr(G, "BW", None) or getattr(VG, "BW", None) or 350.0
TOL = 20.0                 # an opening edge must lie within 20 mm of its place
SEARCH = 250.0             # how far either way a side's nearest line is looked for
OUTLINE_SKIP = ("fins", "pool", "grate")   # house groups no opening is cut in
JOINERY = ("frames", "guards", "rails")   # building groups drawn as joinery
BIG = 1.0e5
WAIST = 150.0               # stair waist and half-landing slab (drawing only)

# ---- project hooks. Each is read from the design and is empty / False for
# the villa, whose sheets are drawn exactly as before.
# Storeys under the ground (a basement): never an elevation datum (the view
# is clipped at the street), a datum and a cut storey in the section.
BELOW = tuple(getattr(V, "BELOW_GRADE_FLOORS", ()))
# A design that brings its own landscape (V.landscape_parts: the terrain up to
# the UNDERSIDE of the finishes) has its finished ground at the top of the
# surfacing, not of the terrain: the ground line is the top of the terrain
# and of every site layer no thicker than SURFACE_MAX (paving, deck, lawn,
# gravel, drive, beds -- not a hedge). The villa's terrain IS its ground.
OWN_SITE = hasattr(V, "landscape_parts")
SURFACE_MAX = 300.0
# A design's own section: SECTION_X names the cut (the villa's is derived
# from its stair and double-height volume, choose_cut).
OWN_SECTION = hasattr(V, "SECTION_X")

# name, ACI, lineweight (1/100 mm), linetype -- same conventions as plan_dxf:
# ACI 7 prints black, hierarchy is carried by lineweight, not hue.
EXTRA_LAYERS = [
    ("A-ELEV-OTLN", 7, 25, "CONTINUOUS"),   # elevation, fabric seen   0.25
    ("A-ELEV-SITE", 8, 13, "CONTINUOUS"),   # landscape seen           0.13
    ("A-SECT-MCUT", 7, 70, "CONTINUOUS"),   # section, material cut    0.70
    ("A-SECT-PATT", 8, 9, "CONTINUOUS"),    # section poche            0.09
    ("A-SECT-MBND", 7, 25, "CONTINUOUS"),   # section, beyond          0.25
    ("A-SECT-EART", 8, 9, "CONTINUOUS"),    # earth hatch              0.09
    ("A-SECT-WATR", 8, 18, "CONTINUOUS"),   # water in section         0.18
    ("A-SITE-GRND", 7, 100, "CONTINUOUS"),  # ground line              1.00
    ("A-ANNO-KEYP", 8, 13, "CONTINUOUS"),   # key plan                 0.13
    ("A-ANNO-NOTE", 1, 35, "CONTINUOUS"),   # check-failure stamp
]

CHECKS: list[tuple[str, bool, str]] = []
G_BUILDING: set = set()          # group names that came from villa_gltf.building()


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    return ok


# =============================================================== the model
def model():
    """Every group villa_gltf renders, classed by how a drawing treats it.

    Classes: fabric (poche when cut), joinery (frames/glass/doors), terrain,
    water, site (thin landscape surfaces). Unknown groups default to fabric
    (building) or site (landscape), so a group added later still draws."""
    groups, cls = {}, {}
    for k, s in G.building().items():
        if s is not None:
            # the glass guards are joinery like the frames: never poche, and
            # never mistaken for the edge of an opening in the fabric
            groups[k], cls[k] = s, ("joinery" if k in JOINERY else "fabric")
            G_BUILDING.add(k)
    groups["boundary"], cls["boundary"] = G.boundary(), "fabric"
    for k, s in G.landscape().items():
        if s is None:
            continue
        name = k if k not in groups else "land_" + k
        groups[name] = s
        cls[name] = {"glass": "joinery", "door": "joinery", "terrain": "terrain",
                     "water": "water"}.get(k, "site")
    return groups, cls


def hs(axis, lo=None, hi=None):
    """A half-space (or slab) as a big box, for clipping by boolean."""
    b = [-BIG, -BIG, -BIG, BIG, BIG, BIG]
    i = "xyz".index(axis)
    if lo is not None:
        b[i] = lo
    if hi is not None:
        b[i + 3] = hi
    return G.box(*b)


def clip(shape, box_):
    try:
        r = shape & box_
    except Exception:                                    # noqa: BLE001
        return None
    if r is None or not r.solids() or r.volume < 1.0:
        return None
    return r


def bbox(shapes):
    bbs = [s.bounding_box() for s in shapes]
    return (min(b.min.X for b in bbs), min(b.min.Y for b in bbs),
            min(b.min.Z for b in bbs), max(b.max.X for b in bbs),
            max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))


# ============================================================ stair (data)
def stair_solid():
    """The stair: villa_design.stair_parts() when the design has it (the
    render model's own 'stair' group, built the same way), else from the
    stair constants. Dog-leg: the west half rises north from GF (villa_cad
    draws the UP arrow there), a half-landing across the well, the east half
    rises south to FF. A single flight runs straight north."""
    if hasattr(V, "stair_parts"):
        s = None
        for b in V.stair_parts():
            p = G.box(*b)
            s = p if s is None else s + p
        return s
    sx0, sy0, sx1, sy1 = V.STAIR
    nfl = int(V.STAIR_FLIGHTS)
    if nfl not in (1, 2):
        return None
    # risers per flight as villa_geom splits them (the first takes the odd
    # one); RISERS // nfl dropped a riser from an odd count
    per = (VG.stair_flights() if VG and hasattr(VG, "stair_flights")
           else [-(-V.RISERS // nfl), V.RISERS - (-(-V.RISERS // nfl))][:nfl])
    r = (V.FF - V.GF) / V.RISERS
    g = V.STAIR_GOING
    cos = g / math.hypot(g, r)

    def flight(x0, x1, y_start, z_start, s, n):
        """n risers, n-1 treads, then WAIST of the level it arrives at, so the
        last riser is not a spike folded back down the soffit (make_face
        dropped it and the stair stopped one riser short)."""
        pts = [(y_start, z_start)]
        for k in range(1, n + 1):
            pts.append((y_start + s * (k - 1) * g, z_start + k * r))
            if k < n:
                pts.append((y_start + s * k * g, z_start + k * r))
        y_top, z_top = y_start + s * (n - 1) * g, z_start + n * r

        def soffit(y):
            return z_start + s * (y - y_start) * r / g - WAIST / cos

        yb = y_top + s * WAIST
        pts.append((yb, z_top))
        if soffit(yb) < z_top - WAIST:
            pts.append((yb, soffit(yb)))
        else:
            pts.append((yb, z_top - WAIST))
            pts.append((y_start + s * (z_top - WAIST - z_start + WAIST / cos) * g / r,
                        z_top - WAIST))
        pts.append((y_start + s * (WAIST / cos) * g / r, z_start))
        face = make_face(Polyline(*[(x0, y, z) for y, z in pts], close=True))
        return extrude(face, amount=x1 - x0, dir=(1, 0, 0))

    if nfl == 1:
        return flight(sx0, sx1, sy0, V.GF, +1, per[0])
    mid = (sx0 + sx1) / 2
    y_top = sy0 + (per[0] - 1) * g
    z_land = V.GF + per[0] * r
    f1 = flight(sx0, mid, sy0, V.GF, +1, per[0])
    f2 = flight(mid, sx1, y_top, z_land, -1, per[1])
    land = G.box(sx0, y_top - WAIST, z_land - WAIST, sx1, sy1, z_land)
    return f1 + land + f2


# ================================================================ projection
def frame(look_from, look_up=(0, 0, 1)):
    d = Vector(*look_from).normalized()
    x = Vector(*look_up).normalized().cross(d)
    return d, x, d.cross(x)


def uv(p, fr):
    P = Vector(*p) if not isinstance(p, Vector) else p
    return P.dot(fr[1]), P.dot(fr[2])


def _pts(e):
    if e.geom_type == GeomType.LINE:
        return [e.start_point(), e.end_point()]
    n = max(8, int(e.length / 150))
    return [e.position_at(i / n) for i in range(n + 1)]


def _collect(h, s, names):
    segs = []
    for nm in names:
        c = getattr(h, nm)(s.wrapped)
        if c.IsNull():
            continue
        BRepLib.BuildCurves3d_s(c, TOLERANCE)
        for e in Compound([Shape(c)]).edges():
            p = _pts(e)
            for a, b in zip(p, p[1:]):
                if math.hypot(b.X - a.X, b.Y - a.Y) > 0.5:
                    segs.append((a.X, a.Y, b.X, b.Y))
    return segs


def hlr(groups, look_from, hidden=False):
    """Visible (and hidden) edges per group, as 2D segments (u, v).

    The projector is exactly the one build123d.exporters.Drawing builds
    (gp_Ax2(look_at, look_from, up x look_from)) with look_at at the origin;
    the only difference is that each group is added to the algorithm
    separately so its edges can go to its own layer. check_hlr_equals_drawing
    proves the union is the same linework Drawing returns."""
    algo = HLRBRep_Algo()
    for s in groups.values():
        algo.Add(s.wrapped)
    d, x, _ = frame(look_from)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), d.to_dir(), x.to_dir())))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    vis = {k: _collect(h, s, ("VCompound", "Rg1LineVCompound", "OutLineVCompound"))
           for k, s in groups.items()}
    hid = ({k: _collect(h, s, ("HCompound", "OutLineHCompound"))
            for k, s in groups.items()} if hidden else {})
    return vis, hid


def seglen(segs):
    return sum(math.hypot(c - a, d - b) for a, b, c, d in segs)


def merge(segs):
    """Merge collinear, touching horizontal/vertical segments; drop duplicates.
    HLR splits an edge wherever anything crosses in front of it."""
    hz, vt, other = {}, {}, []
    for a, b, c, d in segs:
        if abs(b - d) < 0.05:
            hz.setdefault(round((b + d) / 2, 1), []).append(tuple(sorted((a, c))))
        elif abs(a - c) < 0.05:
            vt.setdefault(round((a + c) / 2, 1), []).append(tuple(sorted((b, d))))
        else:
            other.append((a, b, c, d))
    out = []
    for dic, horiz in ((hz, True), (vt, False)):
        for k, ivs in dic.items():
            ivs.sort()
            cur = list(ivs[0])
            for s0, s1 in ivs[1:]:
                if s0 <= cur[1] + 0.05:
                    cur[1] = max(cur[1], s1)
                else:
                    out.append((cur[0], k, cur[1], k) if horiz else (k, cur[0], k, cur[1]))
                    cur = [s0, s1]
            out.append((cur[0], k, cur[1], k) if horiz else (k, cur[0], k, cur[1]))
    return out + other


def coverage(segs, kind, c, lo, hi, tol=TOL):
    """Fraction of the line (kind 'v': u=c, v lo..hi; 'h': v=c, u lo..hi)
    covered by segments parallel to it and within `tol` of it."""
    ivs = []
    for a, b, cc, d in segs:
        if kind == "v":
            if abs(a - cc) > 1.0 or abs((a + cc) / 2 - c) > tol:
                continue
            s0, s1 = sorted((b, d))
        else:
            if abs(b - d) > 1.0 or abs((b + d) / 2 - c) > tol:
                continue
            s0, s1 = sorted((a, cc))
        s0, s1 = max(s0, lo), min(s1, hi)
        if s1 > s0:
            ivs.append((s0, s1))
    ivs.sort()
    tot, cur = 0.0, None
    for s0, s1 in ivs:
        if cur is None or s0 > cur[1]:
            if cur:
                tot += cur[1] - cur[0]
            cur = [s0, s1]
        else:
            cur[1] = max(cur[1], s1)
    if cur:
        tot += cur[1] - cur[0]
    return tot / (hi - lo) if hi > lo else 0.0


def _union_len(ivs):
    ivs = sorted(ivs)
    tot, cur = 0.0, list(ivs[0])
    for s0, s1 in ivs[1:]:
        if s0 > cur[1]:
            tot, cur = tot + cur[1] - cur[0], [s0, s1]
        else:
            cur[1] = max(cur[1], s1)
    return tot + cur[1] - cur[0]


class Lines:
    """Horizontal and vertical 2D segments, sorted by position, to answer
    'where is the nearest line parallel to this side, and how much of the
    side does it cover?' without rescanning the whole projection."""

    def __init__(self, segs):
        rows = {"v": [], "h": []}
        for a, b, c, d in segs:
            if abs(a - c) <= 1.0:
                rows["v"].append(((a + c) / 2, min(b, d), max(b, d)))
            elif abs(b - d) <= 1.0:
                rows["h"].append(((b + d) / 2, min(a, c), max(a, c)))
        self.rows = {k: sorted(v) for k, v in rows.items()}
        self.keys = {k: [r[0] for r in v] for k, v in self.rows.items()}

    def clusters(self, kind, c, lo, hi, band):
        """[(position, fraction of lo..hi covered)] for the lines parallel to
        the side (kind 'v': u = c over v lo..hi; 'h': v = c over u lo..hi)
        within `band` of c; lines less than 1 mm apart are one line (HLR
        splits an edge wherever anything crosses in front of it)."""
        if hi <= lo:
            return []
        rows, keys = self.rows[kind], self.keys[kind]
        near = [r for r in rows[bisect.bisect_left(keys, c - band):
                                bisect.bisect_right(keys, c + band)]
                if min(r[2], hi) > max(r[1], lo)]
        out, grp = [], []
        for r in near + [None]:
            if grp and (r is None or r[0] - grp[-1][0] > 1.0):
                cov = _union_len([(max(s0, lo), min(s1, hi)) for _, s0, s1 in grp])
                out.append((sum(g[0] for g in grp) / len(grp), cov / (hi - lo)))
                grp = []
            if r is not None:
                grp.append(r)
        return out

    def nearest(self, kind, c, lo, hi, need, band=SEARCH):
        """(offset from c, coverage) of the NEAREST line covering at least
        `need` of the side, or (None, 0.0) if none lies within `band`."""
        ok = [(p - c, f) for p, f in self.clusters(kind, c, lo, hi, band) if f >= need]
        return min(ok, key=lambda t: abs(t[0])) if ok else (None, 0.0)

    def cover_at(self, kind, p, lo, hi):
        """Coverage of lo..hi by the line at position p (+-1 mm)."""
        return max([f for q, f in self.clusters(kind, p, lo, hi, 1.0)], default=0.0)


# ================================================================ cut faces
def cut_polys(shape, axis, value, fr, keep="above"):
    """Faces of `shape` cut by the plane axis=value, as shapely polygons in
    the view's (u, v). Taken from the clipped solid itself, so the poche is
    exactly the face the beyond-projection sees first. `keep` is the half
    beyond the cut: 'above' (axis >= value, a section looking towards +axis,
    the villa's) or 'below' (axis <= value, looking towards -axis)."""
    half = clip(shape, hs(axis, lo=value) if keep == "above" else hs(axis, hi=value))
    if half is None:
        return [], None
    i = "xyz".index(axis)
    polys = []
    for f in half.faces():
        c = f.center()
        n = f.normal_at()
        if abs((c.X, c.Y, c.Z)[i] - value) > 0.01 or abs(abs((n.X, n.Y, n.Z)[i]) - 1) > 1e-6:
            continue
        g = _ring(f.outer_wire(), fr)
        for w in f.inner_wires():
            g = g.difference(_ring(w, fr))
        if not g.is_empty and g.area > 1.0:
            polys.append(g)
    return polys, half


def _ring(w, fr):
    """A face wire as a polygon: its edges chained end to end. polygonize()
    alone silently returned nothing for the roof's U-shaped cut, because the
    shared vertices differ in the last bits; it is only the fallback, snapped."""
    segs = [[uv(q, fr) for q in _pts(e)] for e in w.edges()]
    close = lambda a, b: abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01  # noqa: E731
    for first in (segs[0], segs[0][::-1]):
        pts, rest = list(first), segs[1:]
        while rest:
            for i, s in enumerate(rest):
                if close(s[0], pts[-1]):
                    pts += s[1:]
                    break
                if close(s[-1], pts[-1]):
                    pts += s[::-1][1:]
                    break
            else:
                break
            rest.pop(i)
        if not rest and close(pts[0], pts[-1]) and len(pts) >= 4:
            return Polygon(pts).buffer(0)
    snapped = [LineString([(round(a, 2), round(b, 2)) for a, b in s]) for s in segs]
    return unary_union(list(polygonize(unary_union(snapped))))


def geoms(g):
    if g is None or g.is_empty:
        return []
    return [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon" and not q.is_empty]


def upper_envelope(polys):
    """The top silhouette of a set of polygons: for each u interval, the
    highest v -- a stepped polyline list. Gaps (no polygon) break it.

    A top that SLOPES across an interval (a forecourt ramp: the design's
    ramp_z, built as y-z wedges) is followed: the top is sampled near both
    ends of the interval and, where they differ, the run is drawn from end
    to end at those heights. A level top is drawn exactly as before."""
    g = unary_union(polys)
    if g.is_empty:
        return []
    xs = sorted({round(c[0], 3) for q in geoms(g)
                 for ring in [q.exterior, *q.interiors] for c in ring.coords})

    def top(u):
        hit = g.intersection(LineString([(u, -BIG), (u, BIG)]))
        return None if hit.is_empty else hit.bounds[3]

    lines, cur = [], []
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-3:
            continue
        m = (a + b) / 2
        hit = g.intersection(LineString([(m, -BIG), (m, BIG)]))
        if hit.is_empty:
            if cur:
                lines.append(cur)
                cur = []
            continue
        z = hit.bounds[3]
        za = zb = z
        d = 0.01 * (b - a)
        ta, tb = top(a + d), top(b - d)
        if ta is not None and tb is not None and abs(ta - tb) > 1e-3:
            k = (tb - ta) / (b - a - 2 * d)          # a straight slope: extend
            za, zb = ta - k * d, tb + k * d          # it to the interval's ends
        if cur and abs(cur[-1][0] - a) < 1e-3:
            if abs(cur[-1][1] - za) > 1e-3:
                cur.append((a, za))
            cur.append((b, zb))
        else:
            if cur:
                lines.append(cur)
            cur = [(a, za), (b, zb)]
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:                  # drop mid-points on straight runs
        s = [ln[0]]
        for p, q in zip(ln[1:], ln[2:] + [None]):
            if q is not None and ((abs(s[-1][1] - p[1]) < 1e-3 and abs(p[1] - q[1]) < 1e-3)
                                  or (abs(s[-1][0] - p[0]) < 1e-3 and abs(p[0] - q[0]) < 1e-3)):
                continue
            s.append(p)
        out.append(s)
    return out


# =================================================================== sheet
class Sheet:
    """plan_dxf.Plan plus a u-offset, so view coordinates draw directly."""

    def __init__(self, title, ox):
        self.p = PD.Plan(title)
        for name, col, lw, lt in EXTRA_LAYERS:
            if name not in self.p.doc.layers:
                self.p.doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
        self.ox = ox
        self.msp = self.p.msp

    def segs(self, segs, layer):
        for a, b, c, d in merge(segs):
            self.p.line(a + self.ox, b, c + self.ox, d, layer)

    def polyline(self, pts, layer, close=False):
        PD.poly(self.msp, [(u + self.ox, v) for u, v in pts], layer, close=close)

    def hatch(self, poly, layer, pattern=None, scale=1.0, color=8):
        for q in geoms(poly):
            h = self.msp.add_hatch(color=color, dxfattribs={"layer": layer})
            if pattern:
                h.set_pattern_fill(pattern, scale=scale, color=color)
            h.paths.add_polyline_path([(u + self.ox, v) for u, v in q.exterior.coords],
                                      is_closed=True)
            for ring in q.interiors:
                h.paths.add_polyline_path([(u + self.ox, v) for u, v in ring.coords],
                                          is_closed=True)

    def outline(self, poly, layer):
        for q in geoms(poly):
            self.polyline(list(q.exterior.coords), layer, close=True)
            for ring in q.interiors:
                self.polyline(list(ring.coords), layer, close=True)

    def text(self, s, u, v, h, layer="A-ANNO-TEXT", align="LEFT"):
        return self.p.text(s, u + self.ox, v, h, layer, align=align)


def level_label(name, z):
    return f"{name}  {'%%p0' if abs(z) < 0.5 else f'{z:+.0f}'}"   # %%p = plus/minus


def levels(sh, marks, u_from, u_at, side="right"):
    """Level datums: a line from the drawing to a solid marker, the name and
    level over it. `marks` = [(name, z)] computed from villa_design, merged
    where two share a level, and the lower of two close ones is lettered
    under its line so they do not overprint."""
    by = {}
    for nm, z in marks:
        by.setdefault(round(z, 1), []).append(nm)
    rows = sorted((z, " / ".join(ns)) for z, ns in by.items())
    s = 1 if side == "right" else -1
    end = u_at + s * 2900
    for i, (z, nm) in enumerate(rows):
        below = i + 1 < len(rows) and rows[i + 1][0] - z < 420
        sh.p.line(u_from + sh.ox, z, end + sh.ox, z, "A-ANNO-SYMB")
        d = -190 if below else 190          # the lower of a close pair hangs below
        tri = [(u_at, z), (u_at - 110, z + d), (u_at + 110, z + d)]
        h = sh.msp.add_hatch(color=7, dxfattribs={"layer": "A-ANNO-SYMB"})
        h.paths.add_polyline_path([(a + sh.ox, b) for a, b in tri], is_closed=True)
        sh.polyline(tri, "A-ANNO-SYMB", close=True)
        tv = z - 270 if below else z + 70
        if side == "right":
            sh.text(level_label(nm, z), u_at + 330, tv, 190)
        else:
            sh.text(level_label(nm, z), u_at - 330, tv, 190, align="BOTTOM_RIGHT")


def building_levels():
    """The house's datums from villa_design constants -- never typed on the
    sheet. The parapet level is where villa_gltf builds it: RF + SLAB +
    PARAPET (so RF is the roof slab's SOFFIT in the model)."""
    return [("STREET", V.STREET), ("GF", V.GF), ("FF", V.FF), ("RF", V.RF),
            ("T/PARAPET", V.RF + V.SLAB + V.PARAPET)]


def below_levels():
    """Datums of the storeys under the ground (V.BELOW_GRADE_FLOORS: a
    basement 'B1' at LEVEL['B1']), for the SECTION only -- an elevation is
    clipped at the street and cannot show them. Empty for the villa."""
    lv = getattr(V, "LEVEL", {})
    return [(fl, float(lv[fl])) for fl in BELOW if fl in lv]


def section_levels():
    """The section's house datums: the elevations' (building_levels) and,
    below them, every below-grade storey's finished floor."""
    return below_levels() + building_levels()


def storey_levels():
    """Datums of floors built as storeys of their own (annex, roof pavilion):
    [(floor, name, z, outline)] from villa_geom.storey(), empty if none. A
    below-grade storey is never one (it is stacked under the house)."""
    out = []
    if not (VG and hasattr(VG, "standalone_floors")):
        return out
    try:
        for fl in VG.standalone_floors():
            if fl in BELOW:
                continue
            S = VG.storey(fl)
            nm = getattr(VG, "FLOOR_NAME", {}).get(fl, fl)
            out.append((fl, f"{nm} FFL", S["z0"], S["out"]))
            out.append((fl, f"{nm} T/PARAPET", S["parapet"][1], S["out"]))
    except Exception as exc:                            # noqa: BLE001
        print(f"  standalone storeys skipped: {type(exc).__name__}: {exc}")
    return out


# ============================================================ title block
TB = {}                          # title-block inputs, computed once per run


def _tb_inputs():
    """Area line, validator result and design date -- computed, as villa_cad's
    own sheets compute them (villa_geom), with a local fallback."""
    if TB:
        return TB
    try:
        TB["val"] = VG.validation() if VG else None
    except Exception as exc:                            # noqa: BLE001
        print(f"  villa_geom.validation raised {type(exc).__name__}: {exc}")
        TB["val"] = None
    try:
        TB["areas"] = VG.site_text()
    except Exception:                                   # noqa: BLE001
        TB["areas"] = f"NET FLOOR AREA {sum(V.net_area(r) for r in V.ROOMS):.1f} m2"
    if TB["val"] is not None:
        v = TB["val"]
        TB["valtext"] = f"VALIDATION  {v['fatal']} FATAL / {v['major']} MAJOR"
    else:
        try:
            iss = V.validate()
            TB["valtext"] = (f"VALIDATION  {sum(i.startswith('[FATAL]') for i in iss)} FATAL"
                             f" / {sum(i.startswith('[MAJOR]') for i in iss)} MAJOR")
        except Exception as exc:                        # noqa: BLE001
            TB["valtext"] = f"VALIDATION DID NOT RUN ({type(exc).__name__})"
    TB["date"] = datetime.date.fromtimestamp(os.path.getmtime(V.__file__)).isoformat()
    return TB


def titleblock(sh, sheet_no, sheet_name, x0, y0):
    """villa_cad.titleblock itself, so these sheets match the plans exactly.
    It now computes every field (villa_geom); an older villa_cad printed a
    literal 'VALIDATED 0 FATAL / 0 MAJOR', a net area labelled gross and a
    fixed date, so those literals -- and only those -- are replaced if seen.
    Falls back to a replica of the same layout if villa_cad cannot be imported
    (it is edited concurrently)."""
    t = _tb_inputs()
    p = sh.p
    n0 = len(p.msp)
    used = "villa_cad.titleblock"
    try:
        VC = importlib.import_module("villa_cad")
        try:
            VC.titleblock(p, sheet_no, sheet_name, t["areas"], x0, y0, val=t["val"])
        except TypeError:                               # older signature
            VC.titleblock(p, sheet_no, sheet_name,
                          sum(V.net_area(r) for r in V.ROOMS), x0, y0)
    except Exception as exc:                            # noqa: BLE001
        used = f"replica ({type(exc).__name__}: {exc})"
        for e in list(p.msp)[n0:]:
            p.msp.delete_entity(e)
        _titleblock_replica(p, sheet_no, sheet_name, x0, y0, t)
    for e in list(p.msp)[n0:]:
        if e.dxftype() != "TEXT":
            continue
        s = e.dxf.text
        if "VALIDATED  0 FATAL" in s or s.startswith("GROSS INTERNAL AREA"):
            e.dxf.text = f"{t['areas']}      {t['valtext']}"
            used += " (legacy literals replaced)"
        elif s == "2026-09-09":
            e.dxf.text = t["date"]
    return used


def _titleblock_replica(p, sheet_no, sheet_name, x0, y0, t, w=18000.0):
    """villa_cad.titleblock's layout (as of 2026-09-26), fields computed."""
    L, h = "A-ANNO-TTLB", 2600.0
    c1, c2 = w * 0.56, w * 0.78
    PD.poly(p.msp, PD.rect_pts(x0, y0, x0 + w, y0 + h), L)
    p.line(x0, y0 + 1700, x0 + w, y0 + 1700, L)
    for c in (c1, c2):
        p.line(x0 + c, y0, x0 + c, y0 + 1700, L)
    beds = sum(1 for r in V.ROOMS if "BEDROOM" in r[0] and "ENS" not in r[0])
    p.fit_text(f"VILLA  --  {beds} BEDROOM, {V.PLOT_W * V.PLOT_D / 1e6:.0f} m2 PLOT",
               x0 + 300, y0 + 2000, 380, L, c1 - 500)
    p.fit_text(sheet_name, x0 + 300, y0 + 1250, 280, L, c1 - 500)
    p.fit_text("ALL DIMENSIONS IN MILLIMETRES.  DO NOT SCALE FROM DRAWING.",
               x0 + 300, y0 + 900, 150, L, c1 - 500)
    p.fit_text(t["areas"], x0 + 300, y0 + 560, 150, L, c1 - 500)
    p.fit_text(t["valtext"], x0 + 300, y0 + 220, 150, L, c1 - 500)
    p.text("SCALE", x0 + c1 + 250, y0 + 1180, 170, L)
    p.text("1:100 @ A1", x0 + c1 + 250, y0 + 820, 200, L)
    p.text("DATE", x0 + c1 + 250, y0 + 420, 170, L)
    p.text(t["date"], x0 + c1 + 250, y0 + 140, 170, L)
    p.text("DWG No.", x0 + c2 + 250, y0 + 1180, 170, L)
    p.text(sheet_no, x0 + c2 + 250, y0 + 700, 320, L)
    p.text("REV  B", x0 + c2 + 250, y0 + 260, 170, L)


# ================================================================ key plan
def key_plan(sh, x0, y0, k, view=None, x_cut=None, look=1):
    """Plot, ground-floor outline and pool at 1:(100/k), with the view arrow
    or the cut line (its arrows point the way the section looks: `look` +1
    east, -1 west), so the sheet says where it looks from."""
    L = "A-ANNO-KEYP"
    E = V.envelope()

    def T(x, y):
        return (x0 + x * k, y0 + y * k)

    PD.poly(sh.msp, [T(0, 0), T(V.PLOT_W, 0), T(V.PLOT_W, V.PLOT_D), T(0, V.PLOT_D)], L)
    for key in ("out_gf", "upper"):
        for q in geoms(E[key]):
            PD.poly(sh.msp, [T(*c) for c in q.exterior.coords], L)
    PD.poly(sh.msp, [T(V.POOL_X0, V.POOL_Y0), T(V.POOL_X1, V.POOL_Y0),
                     T(V.POOL_X1, V.POOL_Y1), T(V.POOL_X0, V.POOL_Y1)], L)

    def arrow(tip, direction, size=2400.0):
        dx, dy = direction
        px, py = -dy, dx
        bx, by = tip[0] - dx * size, tip[1] - dy * size
        pts = [T(*tip), T(bx + px * size * .45, by + py * size * .45),
               T(bx - px * size * .45, by - py * size * .45)]
        hh = sh.msp.add_hatch(color=7, dxfattribs={"layer": "A-ANNO-SYMB"})
        hh.paths.add_polyline_path(pts, is_closed=True)

    cx, cy = V.PLOT_W / 2, V.PLOT_D / 2
    if view:
        tip, d = {"S": ((cx, -700), (0, 1)), "N": ((cx, V.PLOT_D + 700), (0, -1)),
                  "E": ((V.PLOT_W + 700, cy), (-1, 0)), "W": ((-700, cy), (1, 0))}[view]
        arrow(tip, d)
    if x_cut is not None:
        a, b = T(x_cut, -2500), T(x_cut, V.PLOT_D + 2500)
        sh.p.line(a[0], a[1], b[0], b[1], "A-ANNO-SYMB")
        for yy in (-2500, V.PLOT_D + 2500):
            arrow((x_cut + 3200 * look, yy), (look, 0), 2400)
            tx, ty = T(x_cut - 1400 * look, yy)
            sh.p.text("A", tx, ty, 240, "A-ANNO-TEXT", align="MIDDLE_CENTER")
    sh.p.north(*T(V.PLOT_W + 3500, V.PLOT_D - 2500), 300)
    sh.p.text("KEY PLAN", *T(0, -9000), 200, "A-ANNO-TEXT")


# =============================================================== render
def render(doc, png, dpi=200, scale=100.0):
    """plan_dxf.Plan.render's pattern, writing next to the DXF (Plan.render
    writes to the House folder). layout_properties is passed explicitly:
    draw_layout() otherwise resets the white background set beforehand.

    One change: the figure is the sheet's true plot size at 1:`scale`, and
    the backend is told not to shrink it (adjust_figure=False). With the
    default the preview came out 1424 px wide, and ABSOLUTE lineweights were
    drawn at twice their plotted width relative to the geometry."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf import bbox as ebbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import Configuration, LineweightPolicy
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    ext = ebbox.extents(doc.modelspace())
    w_in = (ext.extmax.x - ext.extmin.x) / scale / 25.4
    h_in = (ext.extmax.y - ext.extmin.y) / scale / 25.4
    m = 0.4                                              # margin, inches
    fig = plt.figure(figsize=(w_in + 2 * m, h_in + 2 * m))
    ax = fig.add_axes([m / (w_in + 2 * m), m / (h_in + 2 * m),
                       w_in / (w_in + 2 * m), h_in / (h_in + 2 * m)])
    ax.set_axis_off()
    cfg = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0)
    ctx = RenderContext(doc)
    lp = ctx.current_layout_properties
    lp.set_colors(bg="#FFFFFF")
    Frontend(ctx, MatplotlibBackend(ax, adjust_figure=False), config=cfg).draw_layout(
        doc.modelspace(), finalize=True, layout_properties=lp)
    fig.savefig(png, dpi=dpi, facecolor="white")
    plt.close(fig)
    return png


# ============================================================ orientation
def check_orientation():
    """An asymmetric marker (a block on the +X +Y top corner of a cube) must
    land where an architect expects it in all four views."""
    big = G.box(0, 0, 0, 1000, 1000, 1000)
    mark = G.box(800, 800, 1000, 1000, 1000, 1300)
    want = {"S": "right", "N": "left", "E": "right", "W": "left"}
    for key, _, _, lf in VIEWS:
        vis, _ = hlr({"big": big, "mark": mark}, lf)
        us = [c for s in vis["mark"] for c in (s[0], s[2])]
        ub = [c for s in vis["big"] for c in (s[0], s[2])]
        vs = [c for s in vis["mark"] for c in (s[1], s[3])]
        side = "right" if sum(us) / len(us) > (min(ub) + max(ub)) / 2 else "left"
        ok = side == want[key] and abs(max(vs) - 1300) < 1e-6
        check(f"orientation marker {key}", ok,
              f"+X+Y marker on the {side} (want {want[key]}), top v={max(vs):.0f} (want 1300)")


# =============================================================== openings
def facade_of(o, E):
    """S/N/E/W for an external opening -- villa_design.facing() when the
    design has it (its own definition), else from which side of its wall band
    the envelope lies. None for internal openings and plain openings."""
    fl, kind, axis, t0, t1, a, b, ra, rb = o[:9]
    if rb is not None or kind == getattr(V, "OPEN", "open"):
        return None
    if hasattr(V, "facing"):
        try:
            return V.facing(o)
        except Exception:                               # noqa: BLE001
            pass
    env = E["out_gf"] if fl == "GF" else E["upper"]
    lo, hi, mid = min(t0, t1), max(t0, t1), (a + b) / 2
    if axis == "h":
        up, dn = env.contains(Point(mid, hi + 10)), env.contains(Point(mid, lo - 10))
        return "S" if up and not dn else "N" if dn and not up else None
    east, west = env.contains(Point(hi + 10, mid)), env.contains(Point(lo - 10, mid))
    return "W" if east and not west else "E" if west and not east else None


def opening_z(o):
    """(bottom, top) of the void: villa_design.opening_z() -- what villa_gltf
    cuts with -- or, on an older design module, villa_gltf's constants."""
    if hasattr(V, "opening_z"):
        return V.opening_z(o)
    zb = G.GF if o[0] == "GF" else G.FF
    return (zb + G.SILL, zb + G.HEAD) if o[1] == V.WIN else (zb, zb + G.DOOR_H)


def opening_rect(o, fr):
    """(u0, u1, v0, v1) of the opening's outline in this view."""
    z0, z1 = opening_z(o)
    x0, y0, x1, y1 = V.void_rect(o).bounds
    us = (uv((x0, y0, 0), fr)[0], uv((x1, y1, 0), fr)[0])
    return min(us), max(us), z0, z1


def opening_sides(o, fr):
    """The four sides of the opening's outline in this view, from
    villa_design: {name: (kind, position, lo, hi)} -- 'v' a vertical line
    u = position over v lo..hi, 'h' a horizontal one v = position."""
    u0, u1, v0, v1 = opening_rect(o, fr)
    return {"left jamb": ("v", u0, v0, v1), "right jamb": ("v", u1, v0, v1),
            "sill" if o[1] == V.WIN else "threshold": ("h", v0, u0, u1),
            "head": ("h", v1, u0, u1)}


def _span(lo, hi):
    """A side is judged over its length less TOL at each end, so a line
    displaced by up to TOL along it still counts as covering it."""
    return (lo + TOL, hi - TOL) if hi - lo > 4 * TOL else (lo, hi)


def locate(o, fr, lines, need):
    """{side: (offset, coverage)}: where the NEAREST line parallel to each
    side lies, among lines covering at least `need` of it, relative to its
    villa_design position ((None, 0) if none within SEARCH)."""
    return {n: lines.nearest(kind, c, *_span(lo, hi), need)
            for n, (kind, c, lo, hi) in opening_sides(o, fr).items()}


def seen_on(o, fr, lines, model):
    """{side: coverage by `lines` of the line the MODEL has for that side}:
    how much of the opening's own outline a projection draws."""
    return {n: lines.cover_at(kind, c + model[n][0], *_span(lo, hi))
            for n, (kind, c, lo, hi) in opening_sides(o, fr).items()}


def wall_band(o):
    """(axis, lo, hi): the thickness of the wall the opening is cut through,
    from villa_design.void_rect (the void spans the wall, t0..t1)."""
    x0, y0, x1, y1 = V.void_rect(o).bounds
    return ("y", y0, y1) if o[2] == "h" else ("x", x0, x1)


def _at(off_cov):
    return off_cov[0] is not None and abs(off_cov[0]) <= TOL


def _offsets(loc):
    return " ".join(f"{n.split()[0]} " + ("none" if off is None else f"{off:+.0f}")
                    for n, (off, _) in loc.items())


def check_openings(key, fr, vis, bvis, wall_lines, E, ground=None):
    """Every external opening facing this way must be in the model at its
    villa_design position AND drawn there.

    Only the house FABRIC's linework is used: `vis` the full view's visible
    lines, `bvis` the house-alone projection's visible lines, and
    `wall_lines(o)` the lines (visible and hidden) of the fabric within the
    thickness of the opening's own wall. An opening's outline is the edge of
    its void in the wall (and the slab edge under a door). Joinery is left
    out on purpose: the frame's inner edge and the glass or leaf edge run
    60 mm (villa_geom FRAME_W, REVEAL) inside every void, and with them in,
    an outline displaced by ~60 mm matched one of its own inner lines, while
    3-of-4 sides let any single side be anywhere (review 2026-09-26).

      in the model   ALL FOUR sides: the NEAREST line parallel to the side
                     in its own wall (covering 95% of it) lies within TOL of
                     the villa_design position. The wall alone, because the
                     whole house's hidden lines -- other facades, partitions
                     -- put a full-height line every 50 mm or so behind a
                     jamb, and any of them would stand in for a displaced one;
      drawn          and 3+ of those four model lines are at least half
                     VISIBLE in the full view -- so a side not drawn is
                     present-but-hidden in the model (a door threshold behind
                     its landing, a sill behind a parapet).

    In the model but not drawn is a failure unless the house itself hides it
    (a face recessed behind another part of the house cannot appear in an
    orthographic view): told apart by the house-alone visible lines. Hidden
    by the boundary or the landscape, or not in the model at its position,
    fails; the failure lists each side's measured offset.

    `ground` (a design with its own landscape, OWN_SITE): the horizontal
    runs of the drawn ground line. A threshold FLUSH with the finished
    ground (a level-access door onto paving) is drawn by the ground line --
    the paving's edge hides the slab's in the model, correctly -- so the
    ground line counts as drawing it. It stands in for horizontal sides
    only, and only in the full view: the side must still be in the model.
    Openings on a below-grade storey (V.BELOW_GRADE_FLOORS) are not on an
    elevation: it is clipped at the street."""
    expected = [o for o in V.OPENINGS if facade_of(o, E) == key and o[0] not in BELOW]
    L_vis, L_bvis = Lines(vis + list(ground or [])), Lines(bvis)
    drawn_n, self_hidden, worst, notes, bad = 0, 0, 0.0, [], []
    for o in expected:
        label = f"{o[0]} {o[1]} {o[7]} ({o[5]:.0f}-{o[6]:.0f})"
        model = locate(o, fr, wall_lines(o), 0.95)
        if not all(_at(x) for x in model.values()):
            bad.append(f"{label} NOT IN THE MODEL at its villa_design position "
                       f"(nearest line per side in its wall, mm: {_offsets(model)})")
            continue
        worst = max([worst] + [abs(off) for off, _ in model.values()])
        cov = seen_on(o, fr, L_vis, model)
        if sum(c >= 0.5 for c in cov.values()) >= 3:
            drawn_n += 1
            if any(c < 0.95 for c in cov.values()):
                notes.append(f"partly hidden by the model in front: {label} "
                             + " ".join(f"{n.split()[0]}={100 * c:.0f}%"
                                        for n, c in cov.items()))
            continue
        txt = " ".join(f"{n.split()[0]}={100 * c:.0f}%" for n, c in cov.items())
        if sum(c >= 0.5 for c in seen_on(o, fr, L_bvis, model).values()) >= 3:
            bad.append(f"{label} hidden by the boundary/landscape (drawn: {txt})")
        else:
            self_hidden += 1
            notes.append(f"hidden behind the house itself (not a facade face): "
                         f"{label} (drawn: {txt})")
    notes += [f"FAIL {b}" for b in bad]
    check(f"{key} elevation: external openings drawn", not bad,
          (f"{len(bad)}/{len(expected)} FAILED: {bad[0]}"
           + (f" (+{len(bad) - 1} more above)" if len(bad) > 1 else "") + "; "
           if bad else "")
          + f"{drawn_n}/{len(expected)} drawn with all 4 sides within "
          f"+-{TOL:.0f} mm of villa_design (worst {worst:.1f} mm)"
          + (f", {self_hidden} behind the house itself" if self_hidden else ""))
    return notes, expected


# ============================================================ elevations
VIEWS = [
    ("S", "A-201", "SOUTH ELEVATION", (0, -1, 0)),
    ("N", "A-202", "NORTH ELEVATION", (0, 1, 0)),
    ("E", "A-203", "EAST ELEVATION", (1, 0, 0)),
    ("W", "A-204", "WEST ELEVATION", (-1, 0, 0)),
]
LAYER_OF = {"fabric": "A-ELEV-OTLN", "joinery": "A-GLAZ", "terrain": "A-ELEV-SITE",
            "water": "A-ELEV-SITE", "site": "A-ELEV-SITE"}


class _Box:
    """min/max corners, the shape of a build123d BoundBox."""

    def __init__(self, x0, y0, z0, x1, y1, z1):
        self.min, self.max = Vector(x0, y0, z0), Vector(x1, y1, z1)


def house_box(groups):
    """Extents of the HOUSE proper -- the stacked envelope (V.envelope) --
    that the ground-line, steps and overall-width checks stand against.
    It was the walls group's bounding box, which reaches the plot boundary
    now that the annex stands on it: the ground line was then looked for
    outside the plot (1 mm past the boundary) and never found."""
    E = V.envelope()
    b = unary_union([E["out_gf"], E["upper"]]).bounds
    wb = groups["walls"].bounding_box()
    return _Box(b[0], b[1], wb.min.Z, b[2], b[3], wb.max.Z)


def steps_facing(key, walls_bb):
    """The house's external steps in front of facade `key`: (box, ...) of
    every landing and flight whose door is on that face. The annex's steps
    stand between the annex and the house, hidden from both sides."""
    if hasattr(V, "stairs_out"):
        want = {"N": ("h", 1), "S": ("h", -1), "E": ("v", 1), "W": ("v", -1)}[key]
        return [b for r in V.stairs_out() if r["door"][0] == "GF"
                and (r["axis"], int(r["sign"])) == want
                for b in [r["landing"]] + r["flights"]]
    out = []
    for b in V.external_steps():
        x0, y0, z0, x1, y1, z1 = b
        if {"S": y1 <= walls_bb.min.Y + 1, "N": y0 >= walls_bb.max.Y - 1,
            "E": x0 >= walls_bb.max.X - 1, "W": x1 <= walls_bb.min.X + 1}[key]:
            out.append(b)
    return out


def ground_polys(groups, cls, axis, value, fr, keep="above"):
    """The polygons the ground line is the top of, cut at axis = value: the
    terrain's; and with OWN_SITE also the surfacing laid on it -- every site
    polygon no thicker than SURFACE_MAX (a hedge standing on its bed is
    seen, it is not ground)."""
    out = []
    for k, s in groups.items():
        if cls[k] == "terrain":
            out += cut_polys(s, axis, value, fr, keep)[0]
        elif OWN_SITE and cls[k] == "site":
            out += [q for p in cut_polys(s, axis, value, fr, keep)[0] for q in geoms(p)
                    if q.bounds[3] - q.bounds[1] <= SURFACE_MAX]
    return out


def ground_z(ground, u):
    """Height of the drawn ground line at u, a sloped run interpolated (None
    where it is not drawn). Vertical steps are skipped."""
    for ln in ground:
        for (pa, pz), (pb, qz) in zip(ln, ln[1:]):
            if abs(pb - pa) > 1e-9 and min(pa, pb) <= u <= max(pa, pb):
                return pz + (qz - pz) * (u - pa) / (pb - pa)
    return None


def standing_landscape():
    """{landscape group: [solid]} of the design's landscape parts that stand
    proud of the ground -- a site layer (never the terrain or the water)
    standing ON the ground (its base at or above the street) and taller than
    SURFACE_MAX: hedges -- built as villa_gltf builds them (part). Only a
    design with its own landscape (OWN_SITE) has them; the villa's surfaces
    are all thin."""
    if not OWN_SITE:
        return {}
    site = VG.site_parts() if VG and hasattr(VG, "site_parts") else None
    out = {}
    for grp, parts in (site or {}).items():
        if grp in ("terrain", "water", "glass", "door"):     # not site layers
            continue
        for p in parts:
            pp = VG.poly_parts(p)
            if pp is not None:
                z0, z1 = pp[1], pp[2]
            else:
                b = VG.profile_bounds(p)
                z0, z1 = b[2], b[5]
            if z1 - z0 > SURFACE_MAX and z0 >= V.STREET - 1.0:
                s = G.part(p)
                if s is not None:
                    out.setdefault(grp, []).append(s)
    return out


def foreground(key, house_bb, standing):
    """{group: solid to leave out of this elevation}: the standing landscape
    (hedges) IN FRONT of the house -- between the viewer's plot edge and the
    house's nearest face -- as the boundary wall is left out. An elevation
    is a view of the house from its own face: a hedge along the rear
    boundary hid the whole garden glass of the ground floor. What stands
    beside the house, and every surface, stays."""
    region = {"S": hs("y", hi=house_bb.min.Y), "N": hs("y", lo=house_bb.max.Y),
              "E": hs("x", lo=house_bb.max.X), "W": hs("x", hi=house_bb.min.X)}[key]
    out = {}
    for grp, solids in standing.items():
        for s in solids:
            r = clip(s, region)
            if r is not None:
                out[grp] = r if grp not in out else out[grp] + r
    return out


# Building groups hatched in elevation where they are SEEN, as a material
# (name: (DXF pattern, scale)). Only groups a design has: the villa has none.
MATERIAL_HATCH = {"stone": ("AR-RSHKE", 2.5)}


def facing_faces(shape, look_from, fr, min_dot=1e-6):
    """[(t, t_max, polygon)] of the faces of `shape` that face the viewer
    (outward normal . look_from > min_dot), projected to (u, v) with their
    holes: t is the face centre's distance towards the viewer (P . d), t_max
    the face's nearest point to the viewer."""
    d = Vector(*look_from).normalized()
    i = max(range(3), key=lambda j: abs((d.X, d.Y, d.Z)[j]))
    sgn = 1.0 if (d.X, d.Y, d.Z)[i] > 0 else -1.0
    out = []
    for f in shape.faces():
        n = f.normal_at()
        if n.X * d.X + n.Y * d.Y + n.Z * d.Z <= min_dot:
            continue
        g = _ring(f.outer_wire(), fr)
        for w in f.inner_wires():
            g = g.difference(_ring(w, fr))
        if g.is_empty or g.area <= 1.0:
            continue
        c = f.center()
        bb = f.bounding_box()
        t_max = sgn * ((bb.max.X, bb.max.Y, bb.max.Z)[i] if sgn > 0
                       else (bb.min.X, bb.min.Y, bb.min.Z)[i])
        out.append((c.X * d.X + c.Y * d.Y + c.Z * d.Z, t_max, g))
    return out


def hole_free(poly):
    """`poly` cut into horizontal strips at every vertex height, so no piece
    has a hole (for a rectilinear polygon): a patterned hatch with holes
    drew its dashed strokes straight through the openings in the preview.
    The pattern is anchored to the drawing origin, so the pieces align."""
    out = []
    for q in geoms(poly):
        if not q.interiors:
            out.append(q)
            continue
        vs = sorted({round(c[1], 3) for ring in [q.exterior, *q.interiors] for c in ring.coords})
        x0, _y0, x1, _y1 = q.bounds
        for a, b in zip(vs, vs[1:]):
            if b - a > 1e-3:
                out += geoms(q.intersection(sbox(x0 - 1, a, x1 + 1, b)))
    return out


def front_faces(view, look_from, fr):
    """[(t_max, polygon)] of every view group's viewer-facing faces: the
    occluders seen_material and check_stone subtract."""
    return [(tm, g) for s in view.values() for _t, tm, g in facing_faces(s, look_from, fr)]


def seen_material(view, group, look_from, fr, front):
    """{t: polygon} -- the faces of `group` squarely facing the viewer, at
    each depth t, less the silhouette of everything nearer the viewer (the
    union of the viewer-facing faces `front` in front of t: for any point of
    a solid's projection the ray to the viewer leaves it through such a
    face). What the elevation shows of that material."""
    if group not in view:
        return {}
    mine = {}
    for t, _tm, g in facing_faces(view[group], look_from, fr, min_dot=1 - 1e-6):
        mine.setdefault(round(t, 1), []).append(g)
    if not mine:
        return {}
    out = {}
    for t, gs in mine.items():
        poly = unary_union(gs)
        occ = [g for tm, g in front if tm > t + 1.0 and g.intersects(poly)]
        out[t] = poly.difference(unary_union(occ)) if occ else poly
    return out


def check_stone(key, fr, look_from, walls_bb, seen, front):
    """The stone the elevation hatches on the HOUSE's own face against the
    design: the faces of V.STONE_ZONES lying on the house's outer face in
    this view, less every opening on this facade (cut through the stone
    too), less what stands in front of that face -- equal, to 0.01 m2, to
    the stone faces the model has there. Nothing to check (no check) when no
    zone lies on this face."""
    zones = [tuple(z) for z in getattr(V, "STONE_ZONES", None) or []]
    face = {"S": ("y", walls_bb.min.Y, 1), "N": ("y", walls_bb.max.Y, 4),
            "E": ("x", walls_bb.max.X, 3), "W": ("x", walls_bb.min.X, 0)}[key]
    ax, at, idx = face
    rects = []
    for z in zones:                           # (x0, y0, z0, x1, y1, z1)
        if abs(z[idx] - at) > 1.0:
            continue
        a0, a1 = (z[0], z[3]) if ax == "y" else (z[1], z[4])
        p0 = (a0, at, 0) if ax == "y" else (at, a0, 0)
        p1 = (a1, at, 0) if ax == "y" else (at, a1, 0)
        u0, u1 = sorted((uv(p0, fr)[0], uv(p1, fr)[0]))
        rects.append(sbox(u0, z[2], u1, z[5]))
    if not rects:
        return
    E = V.envelope()
    holes = [sbox(*[opening_rect(o, fr)[i] for i in (0, 2, 1, 3)])
             for o in V.OPENINGS if facade_of(o, E) == key and o[0] not in BELOW]
    want = unary_union(rects).difference(unary_union(holes)) if holes else unary_union(rects)
    d = Vector(*look_from).normalized()
    t_face = at * (d.X if ax == "x" else d.Y)
    occ = [g for tm, g in front if tm > t_face + 1.0 and g.intersects(want)]
    if occ:
        want = want.difference(unary_union(occ))
    got = unary_union([g for t, g in seen.items() if abs(t - t_face) < 1.0])
    diff = got.symmetric_difference(want).area
    check(f"{key} elevation: stone drawn where STONE_ZONES put it", diff < 1e4,
          f"{got.area / 1e6:.2f} m2 of stone hatched on the house face, design "
          f"{want.area / 1e6:.2f} m2 ({len(rects)} zone face(s) less {len(holes)} "
          f"opening(s) and what stands in front); difference {diff / 1e6:.3f} m2")


def elevation(key, sheet_no, title, look_from, groups, cls, standing=None):
    fr = frame(look_from)
    E = V.envelope()
    walls_bb = house_box(groups)
    # --- the view model: drop the boundary wall between viewer and house, and
    #     everything below street level (the pool shell, the sub-base) --
    #     an elevation shows what stands above the ground
    front = {"S": ("y", None, BWALL), "N": ("y", V.PLOT_D - BWALL, None),
             "E": ("x", V.PLOT_W - BWALL, None), "W": ("x", None, BWALL)}[key]
    ax_, lo, hi = front
    # the standing landscape in front of the house (hedges; OWN_SITE only)
    fg = foreground(key, walls_bb, standing) if standing else {}
    fg = {(g if g in groups else "land_" + g): s for g, s in fg.items()}
    view = {}
    for k, s in groups.items():
        if k == "boundary":
            s = s - hs(ax_, lo=lo if lo is not None else -BIG,
                       hi=hi if hi is not None else BIG)
        if k in fg:
            s = s - fg[k]
        if s.bounding_box().min.Z < V.STREET - 0.5:
            s = clip(s, hs("z", lo=V.STREET))
            if s is None:
                continue
        view[k] = s
    vis, _ = hlr(view, look_from)
    vis_all = [s for k in vis for s in vis[k]]
    # the house alone (fabric + its glazing), to tell self-occlusion apart
    bonly = {k: s for k, s in view.items() if k in G_BUILDING or cls[k] == "joinery"}
    bvis, bhid = hlr(bonly, look_from, hidden=True)
    bvis_all = [s for k in bvis for s in bvis[k]]
    bhid_all = [s for k in bhid for s in bhid[k]]

    # --- HLR == build123d Drawing
    d = Drawing(Compound(children=list(view.values())), look_at=(0, 0, 0),
                look_from=look_from, look_up=(0, 0, 1), with_hidden=False)
    ld = sum(e.length for e in d.visible_lines.edges())
    lm = seglen(vis_all)
    check(f"{key} elevation: per-group HLR equals build123d Drawing",
          abs(ld - lm) <= 1e-3 * max(ld, 1.0), f"{lm:.0f} vs {ld:.0f} mm of line")

    # --- ground line, from the terrain cut just outside the facade
    face_at = {"S": ("y", walls_bb.min.Y - 1.0), "N": ("y", walls_bb.max.Y + 1.0),
               "E": ("x", walls_bb.max.X + 1.0), "W": ("x", walls_bb.min.X - 1.0)}[key]
    # (the terrain; with OWN_SITE its surfacing too -- the finished ground)
    tpolys = ground_polys(groups, cls, face_at[0], face_at[1], fr)
    ground = upper_envelope(tpolys)

    # --- extents in u
    corners = [(x, y) for x in (0.0, V.PLOT_W) for y in (0.0, V.PLOT_D)]
    us = [uv((x, y, 0), fr)[0] for x, y in corners]
    umin, umax = min(us), max(us)
    ox = -umin
    sh = Sheet(title, ox)

    # --- a material's faces where they are seen (a design's stone), hatched
    #     under the linework
    mats, front = {}, None
    if any(g in view for g in MATERIAL_HATCH):
        front = front_faces(view, look_from, fr)
        if "A-ELEV-PATT" not in sh.p.doc.layers:
            sh.p.doc.layers.add("A-ELEV-PATT", color=8, lineweight=9)
        for g, (pat, sc) in MATERIAL_HATCH.items():
            if g in view:
                mats[g] = seen_material(view, g, look_from, fr, front)
                for q in hole_free(unary_union(list(mats[g].values()))):
                    sh.hatch(q, "A-ELEV-PATT", pattern=pat, scale=sc, color=8)

    # --- linework: site first, fabric over it, glazing, then the ground line
    for c in ("terrain", "water", "site", "fabric", "joinery"):
        segs = [s for k in vis if cls[k] == c for s in vis[k]]
        sh.segs(segs, LAYER_OF[c])
    for ln in ground:
        sh.polyline(ln, "A-SITE-GRND")

    # --- checks: openings, heights, ground, orientation, steps, levels
    # an opening's outline is found in the house fabric only (see
    # check_openings): not the joinery 60 mm inside it, the shading in front
    # of it, the pool, the boundary or the landscape
    ol = [k for k in view if k in G_BUILDING and cls[k] == "fabric" and k not in OUTLINE_SKIP]

    def fabric(d):
        return [s for k in ol for s in d.get(k, [])]

    bands = {}

    def wall_lines(o):
        """Visible + hidden lines of the house fabric clipped to the opening's
        wall thickness (1 mm inside each face), one projection per wall.

        From the MODEL (`groups`), not from the view clipped at street level:
        that clip is for drawing, and it deletes, by construction, the slab
        edge under every door whose threshold is AT street level -- the
        annex's, level with the court since the review of 2026-09-26 -- so
        such a door could never be found 'in the model'. Above street level
        the two are the same geometry (the clip removes only what is below
        z = STREET); whether a side is DRAWN is still judged on the view."""
        ax, lo, hi = wall_band(o)
        if hi - lo > 4.0:
            lo, hi = lo + 1.0, hi - 1.0
        k = (ax, round(lo, 1), round(hi, 1))
        if k not in bands:
            part = {g: s for g in ol
                    for s in [clip(groups[g], hs(ax, lo=lo, hi=hi))] if s is not None}
            wv, wh = hlr(part, look_from, hidden=True) if part else ({}, {})
            bands[k] = Lines([s for d_ in (wv, wh) for g in d_ for s in d_[g]])
        return bands[k]

    ground_h = None
    if OWN_SITE:        # flush thresholds are drawn by the ground line
        ground_h = [(pa, pz, pb, qz) for ln in ground for (pa, pz), (pb, qz) in zip(ln, ln[1:])
                    if abs(pz - qz) < 1e-6 and abs(pb - pa) > 1e-6]
    notes, expected = check_openings(key, fr, fabric(vis), fabric(bvis), wall_lines, E,
                                     ground=ground_h)
    if "stone" in mats:
        check_stone(key, fr, look_from, walls_bb, mats["stone"], front)
    bb = bbox(list(view.values()))
    vtop = max(max(s[1], s[3]) for s in vis_all)
    u_lo = min(min(s[0], s[2]) for s in vis_all)
    u_hi = max(max(s[0], s[2]) for s in vis_all)
    bu = sorted(uv((x, y, 0), fr)[0] for x in (bb[0], bb[3]) for y in (bb[1], bb[4]))
    b_top = max(s.bounding_box().max.Z for k, s in groups.items() if k in G_BUILDING)
    check(f"{key} elevation: overall height = model bbox",
          abs(vtop - bb[5]) <= 1.0 and abs(vtop - b_top) <= 1.0,
          f"drawing top {vtop:.1f}, model bbox top {bb[5]:.1f}, building() top {b_top:.1f}")
    check(f"{key} elevation: overall width = model bbox",
          abs(u_lo - bu[0]) <= 1.0 and abs(u_hi - bu[-1]) <= 1.0,
          f"drawing u {u_lo:.0f}..{u_hi:.0f}, model {bu[0]:.0f}..{bu[-1]:.0f}")

    # ground line against villa_design.ground_at, along the building
    bad = []
    wu = sorted(uv((x, y, 0), fr)[0] for x in (walls_bb.min.X, walls_bb.max.X)
                for y in (walls_bb.min.Y, walls_bb.max.Y))
    for i in range(1, 20):
        u = wu[0] + (wu[-1] - wu[0]) * i / 20
        if key in ("S", "N"):
            y = face_at[1]
        else:
            y = u if key == "E" else -u
        want = V.ground_at(y)
        if OWN_SITE:        # the finished ground: level or sloped runs
            gz_ = ground_z(ground, u)
            got = [] if gz_ is None else [gz_]
        else:
            got = [pz for ln in ground for (pa, pz), (pb, _) in zip(ln, ln[1:])
                   if abs(pz - _) < 1e-6 and min(pa, pb) <= u <= max(pa, pb)]
        if not got or abs(got[0] - want) > 1.0:
            bad.append(f"u={u:.0f} ground {got[:1]} vs ground_at {want:.0f}")
    check(f"{key} elevation: ground line = villa_design.ground_at", not bad,
          "; ".join(bad[:3]) or (
              f"{len(ground)} run(s) from the terrain group" if not OWN_SITE else
              f"{len(ground)} run(s): the terrain and its surfacing (finished ground), "
              f"19 points along the house"))

    # orientation on the model itself
    if key in ("S", "N"):
        fu = [c for s in vis.get("fins", []) for c in (s[0], s[2])]
        mid = (wu[0] + wu[-1]) / 2
        if fu and V.fins():
            side = "left" if sum(fu) / len(fu) < mid else "right"
            want = "left" if key == "S" else "right"
            check(f"{key} elevation: west fins on the {want}", side == want,
                  f"fins drawn on the {side}")
        else:
            # No fin array to tell west from east (the 'fins' group is only
            # the symmetric eyebrows now), so use the model's own asymmetry:
            # a window on this face whose mirror image about the house centre
            # is NOT a window must have its sill drawn where villa_design puts
            # it, and nothing drawn at the mirror image.
            for o in V.OPENINGS:
                if o[1] != V.WIN or facade_of(o, E) != key:
                    continue
                u0, u1, v0, _v1 = opening_rect(o, fr)
                m0, m1 = 2 * mid - u1, 2 * mid - u0
                here = coverage(vis_all, "h", v0, u0 + TOL, u1 - TOL, tol=1.0)
                there = coverage(vis_all, "h", v0, m0 + TOL, m1 - TOL, tol=1.0)
                if here > 0.5 and there < 0.2:
                    check(f"{key} elevation: not mirrored (model asymmetry)", True,
                          f"{o[0]} {o[7]} sill drawn at u {u0:.0f}..{u1:.0f} "
                          f"({100 * here:.0f}%), nothing at its mirror image "
                          f"({100 * there:.0f}%)")
                    break
            else:
                check(f"{key} elevation: not mirrored (model asymmetry)", False,
                      "no asymmetric window found to test -- only the synthetic "
                      "marker proves the orientation")
    else:
        gz = getattr(V, "GARDEN_Z", None)
        hi_runs = [(pa + pb) / 2 for ln in ground for (pa, pz), (pb, _) in zip(ln, ln[1:])
                   if gz is not None and abs(pz - gz) < 1.0 and abs(pz - _) < 1e-6]
        mid = (wu[0] + wu[-1]) / 2
        if hi_runs:
            side = "left" if sum(hi_runs) / len(hi_runs) < mid else "right"
            want = "left" if key == "E" else "right"
            check(f"{key} elevation: pool garden (south) on the {want}", side == want,
                  f"garden ground drawn on the {side}")
        if hasattr(V, "ramp_z") and ground:
            # A garden level with the ground floor runs at GARDEN_Z along the
            # whole side of the house, so the model's other asymmetry is used
            # as well: the forecourt ramp (V.ramp_z) falls to the STREET, on
            # the north. The lowest point of the drawn ground line must be on
            # the north side: right in the east elevation, left in the west.
            pts = [p for ln in ground for p in ln]
            low_z = min(p[1] for p in pts)
            lows = [p[0] for p in pts if p[1] < low_z + 1.0]
            low_u = sum(lows) / len(lows)
            side = "left" if low_u < mid else "right"
            want = "right" if key == "E" else "left"
            check(f"{key} elevation: street end (north) on the {want}", side == want,
                  f"ground line falls to {low_z:+.0f} at u={low_u:.0f}, drawn on the "
                  f"{side} (the forecourt ramp to the street)")

    # the external steps in front of this facade
    steps = []
    for b in steps_facing(key, walls_bb):
        x0, y0, z0, x1, y1, z1 = b
        ua = sorted((uv((x0, y0, 0), fr)[0], uv((x1, y1, 0), fr)[0]))
        steps.append((z1, coverage(vis_all, "h", z1, ua[0], ua[1], tol=1.0)))
    if steps:
        seen = sum(1 for _, c in steps if c > 0.3)
        check(f"{key} elevation: external steps drawn", seen == len(steps),
              f"{seen}/{len(steps)} step/landing tops at "
              + ", ".join(f"+{z:.0f}" for z, _ in sorted(steps)))
    elif hasattr(V, "stairs_out") and not V.stairs_out():
        # the check cannot apply: the design has no external steps at all
        check(f"{key} elevation: external steps drawn", True,
              "N/A -- the design has no external steps (V.stairs_out() is empty: "
              "every external threshold is level with the ground)")

    # level datums: the house's must sit on an edge this elevation draws; an
    # annex / pavilion datum on an edge of the house-only projection (it may
    # stand behind the house in this view). A below-grade storey is not one
    # (building_levels never names it: the view is clipped at the street).
    marks = [m for m in building_levels()]
    gz = getattr(V, "GARDEN_Z", None)
    if gz is not None and any(abs(pz - gz) < 1 for ln in ground for _, pz in ln):
        marks.append(("GARDEN", gz))
    miss = [f"{n} {z:+.0f}" for n, z in marks
            if coverage(vis_all, "h", z, u_lo, u_hi, tol=1.0) <= 0.0]
    for _fl, n, z, _o in storey_levels():
        marks.append((n, z))
        if coverage(bvis_all + bhid_all, "h", z, u_lo, u_hi, tol=1.0) <= 0.0:
            miss.append(f"{n} {z:+.0f}")
    check(f"{key} elevation: level datums sit on model edges", not miss,
          ("no edge at " + ", ".join(miss)) if miss else
          ", ".join(level_label(n, z).replace("%%p", "+-") for n, z in marks))

    # --- annotation
    top = bb[5]
    levels(sh, marks, u_hi + 300, u_hi + 1200, "right")
    chain = sorted({V.STREET, V.GF, V.FF, V.RF, top})
    for a, b in zip(chain, chain[1:]):
        sh.p.dim_v(a, b, u_lo + ox, 1400)
    sh.p.dim_v(V.STREET, top, u_lo + ox, 2900)
    sh.p.dim_h(walls_bb_u(walls_bb, fr)[0] + ox, walls_bb_u(walls_bb, fr)[1] + ox,
               V.STREET, 900)
    sh.text(title, u_lo, -2500, 520)
    sh.text("SCALE 1:100   --   PROJECTED FROM THE RENDER MODEL (villa_gltf), "
            "HIDDEN LINES REMOVED", u_lo, -3150, 200)
    nv = -3550
    if fg:
        sh.text("THE BOUNDARY WALL AND THE HEDGES STANDING IN FRONT OF THE HOUSE ("
                + " / ".join(sorted(fg)).upper() + ") ARE LEFT OUT OF THE VIEW",
                u_lo, nv, 160)
        nv -= 350
    if any(not unary_union(list(m.values())).is_empty for m in mats.values()):
        sh.text("HATCHED: " + ", ".join(
            {"stone": "STACKED STONE CLADDING AND STONE WALLS"}.get(g, g.upper())
            for g, m in mats.items() if not unary_union(list(m.values())).is_empty)
            + " (villa_gltf group " + " / ".join(f"'{g}'" for g in mats) + ")",
            u_lo, nv, 160)
    sh.p.scale_bar(u_lo + ox, -4600, 5)
    key_plan(sh, u_hi + ox + 4600, -6200, 0.125, view=key)
    tb = titleblock(sh, sheet_no, title, u_hi + ox + 4300 - 18000, -9400)
    return sh, notes, tb, len(expected)


def walls_bb_u(bb, fr):
    us = sorted(uv((x, y, 0), fr)[0] for x in (bb.min.X, bb.max.X) for y in (bb.min.Y, bb.max.Y))
    return us[0], us[-1]


# ================================================================ section
def choose_cut():
    """x of the N-S section: the design's own SECTION_X when it names one;
    else the design axis if it passes through both the stair well and the
    double-height volume, else the middle of the first flight. Stated on
    the sheet."""
    if OWN_SECTION:
        return float(V.SECTION_X), "SECTION_X of the design"
    sx0, sy0, sx1, sy1 = V.STAIR
    dh = V.envelope()["dh_in"].bounds
    lo, hi = max(sx0, dh[0]), min(sx1, dh[2])
    if lo < V.AXIS < hi:
        return V.AXIS, "the design axis"
    x = (sx0 + (sx0 + sx1) / 2) / 2
    return x, "the middle of the first flight"


def cut_voids(x_cut):
    """The V.VOIDS the N-S cut at x_cut passes through."""
    return [v for v in getattr(V, "VOIDS", []) if v[1] < x_cut < v[3]]


def _rect_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def stairs_cut(x_cut):
    """The V.STAIRS records the cut passes through."""
    return [s for s in getattr(V, "STAIRS", []) if s["rect"][0] < x_cut < s["rect"][2]]


def stairs_seen(x_cut, look):
    """The house stairs A-A shows BEYOND the cut: those rising in a void the
    cut passes through (a feature stair in a double-height hall) and not cut
    themselves, on the side the section looks towards (`look` +1 east, -1
    west). An enclosed stair in its own room is not seen: its walls hide it."""
    cv = [(v[1], v[2], v[3], v[4]) for v in cut_voids(x_cut)]
    out = []
    for s in getattr(V, "STAIRS", []):
        x0, y0, x1, y1 = s["rect"]
        if x0 < x_cut < x1 or not any(_rect_overlap(s["rect"], v) for v in cv):
            continue
        if (look > 0 and x0 >= x_cut) or (look < 0 and x1 <= x_cut):
            out.append(s)
    return out


def section_view():
    """(x_cut, why, look_from, facing, look) of section A-A. The villa's is
    cut by choose_cut() and looks EAST. A design with its own SECTION_X looks
    towards the stair rising in the double-height void it cuts (so the
    stair is drawn beyond the cut, in projection), east when there is none."""
    x_cut, why = choose_cut()
    if OWN_SECTION:
        cand = [s for s in getattr(V, "STAIRS", [])
                if not (s["rect"][0] < x_cut < s["rect"][2])
                and any(_rect_overlap(s["rect"], (v[1], v[2], v[3], v[4]))
                        for v in cut_voids(x_cut))]
        if cand:
            cx = sum((s["rect"][0] + s["rect"][2]) / 2 for s in cand) / len(cand)
            if cx < x_cut:
                return x_cut, why, (1, 0, 0), "WEST", -1
    return x_cut, why, (-1, 0, 0), "EAST", 1


def _floor_order():
    lv = getattr(V, "LEVEL", {})
    order = getattr(V, "FLOOR_ORDER", None) or sorted(lv, key=lambda f: lv[f])
    return [f for f in order if f in lv]


def floor_below(fl):
    """The storey under `fl` in the design's FLOOR_ORDER (None at the bottom)."""
    order = _floor_order()
    i = order.index(fl)
    return order[i - 1] if i > 0 else None


def soffit_over(fl):
    """(name, z) of the underside of the slab over storey `fl`: the next
    storey's finished floor less SLAB (the roof slab's soffit, V.RF, over
    the top storey); fl's ceiling if nothing is over it."""
    order = _floor_order()
    i = order.index(fl)
    if i + 1 < len(order):
        nxt = order[i + 1]
        return nxt, V.LEVEL[nxt] - V.SLAB
    return "CEILING", V.LEVEL[fl] + V.CEIL[fl]


def check_cut_project(x_cut, why, facing, look):
    """A-A for a design with its own SECTION_X: the cut must pass through a
    void of the design (its double-height volume); the stair rising in it
    is drawn beyond the cut; the voids and stairs it misses are named."""
    voids = list(getattr(V, "VOIDS", []))
    cv = cut_voids(x_cut)
    seen = stairs_seen(x_cut, look)
    cut = stairs_cut(x_cut)
    others = [v[0] for v in voids if v not in cv]
    missed = [s["name"] for s in getattr(V, "STAIRS", []) if s not in seen and s not in cut]
    detail = (f"x={x_cut:.0f} ({why}), looking {facing}: through "
              + (", ".join(f"{v[0]} x {v[1]:.0f}-{v[3]:.0f}" for v in cv) or "NO void")
              + ("; stair cut: " + ", ".join(s["name"] for s in cut) if cut else "")
              + ("; seen beyond: " + ", ".join(
                  f"{s['name']} x {s['rect'][0]:.0f}-{s['rect'][2]:.0f}" for s in seen)
                 if seen else "")
              + (f"; not on the cut: {', '.join(others)}" if others else "")
              + (f"; not shown: {', '.join(missed)}" if missed else ""))
    if not voids:
        check("A-A: cut passes through the double-height void", True,
              "N/A -- the design has no VOIDS; " + detail)
    else:
        check("A-A: cut passes through the double-height void", bool(cv), detail)


def soil_region(env, fr, x_cut, umin, umax):
    """The EARTH a section through a basement stands in: everything under the
    finished-ground profile `env` (upper_envelope runs; the gaps over the
    house and the pool bridged) down to 600 below the lowest below-grade
    slab, less the below-grade storeys' outlines on the cut (from their
    slab's underside up) and the pool's tank. The model's terrain is a
    300 mm slab under the surfacing; the earth under it is drawn, as a
    section through a basement is. The caller removes every cut polygon."""
    lv = V.LEVEL
    zb = min(lv[f] for f in BELOW) - V.SLAB - 600.0
    pts = [p for ln in env for p in ln]
    if not pts:
        return None
    ring = [(umin, pts[0][1])] + pts + [(umax, pts[-1][1]), (umax, zb), (umin, zb)]
    region = Polygon(ring).buffer(0)
    out = []
    line = LineString([(x_cut, -BIG), (x_cut, BIG)])
    for fl in BELOW:
        g = V.outline(fl).intersection(line)
        for seg in getattr(g, "geoms", [g]):
            if seg.is_empty or seg.length < 1.0:
                continue
            ys = [c[1] for c in seg.coords]
            u0, u1 = sorted((uv((0, min(ys), 0), fr)[0], uv((0, max(ys), 0), fr)[0]))
            out.append(sbox(u0, lv[fl] - V.SLAB, u1, BIG))
    if V.POOL_X0 < x_cut < V.POOL_X1:
        u0, u1 = sorted((uv((0, V.POOL_Y0, 0), fr)[0], uv((0, V.POOL_Y1, 0), fr)[0]))
        out.append(sbox(u0, min(V.POOL_FL, getattr(V, "POOL_SHALLOW_FL", V.POOL_FL)), u1, BIG))
    return region.difference(unary_union(out)) if out else region


def section(groups, cls):
    key, sheet_no, title = "A", "A-301", "SECTION A-A"
    x_cut, why, look_from, facing, look = section_view()
    keep = "above" if look > 0 else "below"      # the half beyond the cut
    fr = frame(look_from)
    if not OWN_SECTION:
        sx0, sy0, sx1, sy1 = V.STAIR
        dh = V.envelope()["dh_in"].bounds
        check("A-A: cut passes through stair well and double-height volume",
              sx0 < x_cut < sx1 and dh[0] < x_cut < dh[2],
              f"x={x_cut:.0f} ({why}); stair x {sx0:.0f}-{sx1:.0f}, "
              f"double height x {dh[0]:.0f}-{dh[2]:.0f}")
    else:
        check_cut_project(x_cut, why, facing, look)

    sec = dict(groups)
    scls = dict(cls)
    if not any("stair" in k for k in groups):
        st = stair_solid()
        if st is not None:
            sec["stair"], scls["stair"] = st, "fabric"

    # a face lying ON the cut plane would be drawn as cut where nothing is cut
    on_plane = [k for k, s in sec.items() for f in s.faces()
                if abs(f.center().X - x_cut) < 0.5 and abs(abs(f.normal_at().X) - 1) < 1e-6]
    check("A-A: no model face lies on the cut plane", not on_plane,
          ", ".join(sorted(set(on_plane))) or f"x={x_cut:.0f} clear")

    cuts, halves = {}, {}
    for k, s in sec.items():
        polys, half = cut_polys(s, "x", x_cut, fr, keep)
        if half is not None:
            halves[k] = half
        if polys:
            cuts[k] = polys
    # Beyond the cut the house's fabric is projected as ONE fused solid. As
    # separate material groups, the FF slab band that villa_gltf runs through
    # the double-height walls drew a line across the far wall at +4500/+5000,
    # and the open double height read as two storeys. A section shows form,
    # not finishes; the elevations keep the material joints.
    fab_keys = [k for k in halves if scls[k] == "fabric" and (k in G_BUILDING or k == "stair")]
    beyond = {k: v for k, v in halves.items() if k not in fab_keys}
    if fab_keys:
        fused = halves[fab_keys[0]]
        for k in fab_keys[1:]:
            fused = fused + halves[k]
        beyond["house"] = fused
        scls["house"] = "fabric"
    vis, _ = hlr(beyond, look_from)

    fabric = unary_union([q for k, ps in cuts.items() if scls[k] == "fabric" for q in ps])
    terrain = unary_union([q for k, ps in cuts.items() if scls[k] == "terrain" for q in ps])
    water = unary_union([q for k, ps in cuts.items() if scls[k] == "water" for q in ps])
    joinery = [q for k, ps in cuts.items() if scls[k] == "joinery" for q in ps]
    site = [q for k, ps in cuts.items() if scls[k] == "site" for q in ps]
    allcut = unary_union([q for ps in cuts.values() for q in ps])
    bnd = unary_union([q.boundary for q in geoms(allcut)] +
                      [q.boundary for ps in cuts.values() for q in ps]).buffer(0.5)

    umin, umax = sorted((uv((0, 0, 0), fr)[0], uv((0, V.PLOT_D, 0), fr)[0]))
    ox = -umin
    sh = Sheet(title, ox)

    # the finished ground: the terrain's top (the villa), or with OWN_SITE
    # the top of the terrain and its surfacing
    if OWN_SITE:
        env = upper_envelope(list(geoms(terrain)) + [
            q for k, ps in cuts.items() if scls[k] == "site" for p in ps for q in geoms(p)
            if q.bounds[3] - q.bounds[1] <= SURFACE_MAX])
    else:
        env = upper_envelope(geoms(terrain))
    # a basement (BELOW) stands in earth: hatched with the terrain
    soil = None
    if BELOW:
        soil = soil_region(env, fr, x_cut, umin, umax)
        if soil is not None:
            soil = soil.difference(allcut)
    from shapely.prepared import prep
    in_soil = prep(soil) if soil is not None and not soil.is_empty else None

    # --- hatches first, then beyond, then cut outlines, then the ground line
    sh.hatch(terrain if in_soil is None else unary_union([terrain, soil]),
             "A-SECT-EART", pattern="EARTH", scale=12.0, color=8)
    sh.hatch(fabric, "A-SECT-PATT", color=8)
    drawn = []                                   # the beyond linework, all classes
    for c, layer in (("terrain", "A-ELEV-SITE"), ("water", "A-ELEV-SITE"),
                     ("site", "A-ELEV-SITE"), ("fabric", "A-SECT-MBND"),
                     ("joinery", "A-GLAZ")):
        segs = []
        for k in vis:
            if scls[k] != c:
                continue
            for s in vis[k]:
                ls = LineString([(s[0], s[1]), (s[2], s[3])])
                # (a line beyond the cut that lies in the earth is behind it)
                if not ls.within(bnd) and not (in_soil is not None and in_soil.contains(ls)):
                    segs.append(s)
        sh.segs(segs, layer)
        drawn += segs
    sh.outline(water, "A-SECT-WATR")
    for q in site:
        sh.outline(q, "A-ELEV-SITE")
    for q in joinery:
        sh.outline(q, "A-GLAZ")
    sh.outline(fabric, "A-SECT-MCUT")
    ground = []
    for ln in env:
        g = LineString(ln).difference(fabric.buffer(1.0))
        for part in getattr(g, "geoms", [g]):
            if part.length > 1.0:
                ground.append(list(part.coords))
                sh.polyline(list(part.coords), "A-SITE-GRND")

    if OWN_SECTION:
        return _section_project(
            sh=sh, fr=fr, ox=ox, umin=umin, umax=umax, x_cut=x_cut, why=why,
            facing=facing, look=look, sec=sec, scls=scls, cuts=cuts, halves=halves,
            vis=vis, fabric=fabric, joinery=joinery, allcut=allcut, ground=ground,
            soil=soil, title=title, sheet_no=sheet_no, drawn=drawn)

    # --- checks
    E = V.envelope()
    dy0, dy1 = E["dh_in"].bounds[1], E["dh_in"].bounds[3]
    du = sorted((uv((0, dy0, 0), fr)[0], uv((0, dy1, 0), fr)[0]))
    open_box = sbox(du[0] + 1, V.GF + 1, du[1] - 1, V.RF - 1)
    blocked = open_box.intersection(unary_union([fabric] + joinery)).area
    um = (du[0] + du[1]) / 2
    floor_ok = fabric.contains(Point(um, V.GF - V.SLAB / 2))
    roof_ok = fabric.contains(Point(um, V.RF + V.SLAB / 2))
    check("A-A: double-height volume open GF to RF", blocked < 1.0 and floor_ok and roof_ok,
          f"y {dy0:.0f}-{dy1:.0f}: {blocked / 1e6:.3f} m2 of cut fabric between "
          f"+{V.GF:.0f} and +{V.RF:.0f}; floor slab {'yes' if floor_ok else 'NO'}, "
          f"roof slab {'yes' if roof_ok else 'NO'}")
    stair_void = next((vv for vv in V.VOIDS if "STAIR" in vv[0]), None)
    if stair_void is None:
        check("A-A: stair void in the first-floor slab", False, "no STAIR VOID in V.VOIDS")
    else:
        _, vx0, vy0, vx1, vy1, _f = stair_void
        su = sorted((uv((0, vy0, 0), fr)[0], uv((0, vy1, 0), fr)[0]))
        slab_band = sbox(su[0] + 1, V.FF - V.SLAB + 1, su[1] - 1, V.FF - 1)
        slab_fabric = unary_union([q for k, ps in cuts.items()
                                   if scls[k] == "fabric" and k != "stair" for q in ps])
        in_void = slab_band.intersection(slab_fabric).area
        edge_a = slab_fabric.contains(Point(su[0] - 150, V.FF - V.SLAB / 2))
        edge_b = slab_fabric.contains(Point(su[1] + 150, V.FF - V.SLAB / 2))
        check("A-A: first-floor slab open over the stair well",
              in_void < 1.0 and edge_a and edge_b,
              f"y {vy0:.0f}-{vy1:.0f}: {in_void / 1e6:.3f} m2 of slab in the void; "
              f"slab each side {'yes' if edge_a and edge_b else 'NO'}")
    if "stair" in cuts:
        sb = unary_union(cuts["stair"]).bounds
        check("A-A: stair cut spans GF to the half-landing", abs(sb[1] - V.GF) < 1.0
              and sb[3] > V.GF + (V.FF - V.GF) / 2 - 1.0,
              f"stair cut v {sb[1]:.0f}..{sb[3]:.0f}")
    if "stair" in sec:
        # the solid, not its visible edges: the top riser lies on the FF slab's
        # cut edge, so HLR rightly hides it behind the poche
        sb3 = sec["stair"].bounding_box()
        check("A-A: stair rises GF to FF", abs(sb3.min.Z - V.GF) < 1.0
              and abs(sb3.max.Z - V.FF) < 1.0,
              f"stair +{sb3.min.Z:.0f}..+{sb3.max.Z:.0f}: {V.RISERS} risers of "
              f"{(V.FF - V.GF) / V.RISERS:.1f}, {V.STAIR_FLIGHTS} flights")

    b_all = bbox(list(halves.values()))
    vtop = max(max(s[1], s[3]) for k in vis for s in vis[k])
    check("A-A: overall height = model bbox", abs(vtop - b_all[5]) <= 1.0,
          f"drawing top {vtop:.1f}, cut model top {b_all[5]:.1f}")

    pool_marks = []
    if V.POOL_X0 < x_cut < V.POOL_X1:
        pool_marks = [("POOL TWL", V.POOL_TW), ("POOL FLOOR", V.POOL_FL),
                      ("BASIN WL", V.BASIN_WL), ("BASIN FLOOR", V.BASIN_FL)]
        if getattr(V, "POOL_SHALLOW_FL", V.POOL_FL) != V.POOL_FL:
            # the floor is a profile: its shallow shelf is a datum of its own
            pool_marks.append(("POOL SHALLOW", V.POOL_SHALLOW_FL))
    if any(abs(p_[1] - V.GARDEN_Z) < 1 for ln in ground for p_ in ln):
        pool_marks.append(("GARDEN", V.GARDEN_Z))
    cut_line = LineString([(x_cut, -BIG), (x_cut, BIG)])
    house_marks = building_levels() + [(n, z) for _f, n, z, o in storey_levels()
                                       if o.intersects(cut_line)]
    hedges = []
    for q in geoms(allcut):
        for ring in [q.exterior, *q.interiors]:
            cs = list(ring.coords)
            hedges += [(a[0], a[1], b[0], b[1]) for a, b in zip(cs, cs[1:])]
    for ps in cuts.values():
        for q in ps:
            for g_ in geoms(q):
                cs = list(g_.exterior.coords)
                hedges += [(a[0], a[1], b[0], b[1]) for a, b in zip(cs, cs[1:])]
    miss = [f"{n} {z:+.0f}" for n, z in house_marks + pool_marks
            if coverage(hedges, "h", z, umin, umax, tol=1.0) <= 0.0]
    check("A-A: level datums sit on cut edges", not miss,
          ("no cut edge at " + ", ".join(miss)) if miss else
          ", ".join(level_label(n, z).replace("%%p", "+-")
                    for n, z in house_marks + pool_marks))

    # --- annotation
    levels(sh, house_marks, umin - 300, umin - 1200, "left")
    pool_u = sorted((uv((0, V.BASIN_Y0, 0), fr)[0], uv((0, V.POOL_Y1, 0), fr)[0]))
    levels(sh, pool_marks, pool_u[1] + 200, umax + 1200, "right")
    # the double height, dimensioned GF to the roof soffit inside the volume,
    # beside its south wall, clear of the room labels (kept to the middle)
    sh.p.dim_v(V.GF, V.RF, du[1] + ox - 150, 400)

    def free_mid(y0, y1):
        """Centre of the longest part of y0..y1 not over the stair well."""
        parts = [(y0, y1)]
        if y0 < sy1 and sy0 < y1:
            parts = [(y0, max(y0, sy0)), (min(y1, sy1), y1)]
        a, b = max(parts, key=lambda p: p[1] - p[0])
        return (a + b) / 2, b - a

    for r in V.ROOMS:
        if not (r[1] < x_cut < r[3]):
            continue
        # a ground-floor label keeps off the flights; upstairs the stair is
        # below the floor and the landing is open space over its well
        ym, w = free_mid(r[2], r[4]) if r[6] == "GF" else ((r[2] + r[4]) / 2, r[4] - r[2])
        lvl = getattr(V, "LEVEL", {}).get(r[6], V.GF if r[6] == "GF" else V.FF)
        z = lvl + 1500
        sh.p.fit_text(r[0], uv((0, ym, 0), fr)[0] + ox, z, 200, "A-ANNO-TEXT",
                      max_w=max(600.0, w - 200), centre=True)
    dim_u = du[1] - 150 - 400                 # where the 7800 dimension line runs
    for vname, vx0, vy0, vx1, vy1, floors in V.VOIDS:
        if vx0 < x_cut < vx1 and "FF" in floors and "STAIR" not in vname:
            a, b = sorted((uv((0, vy0, 0), fr)[0], uv((0, vy1, 0), fr)[0]))
            if a < dim_u < b:
                b = min(b, dim_u - 400)
            sh.p.fit_text(vname, (a + b) / 2 + ox, V.FF + 1500, 200, "A-ANNO-TEXT",
                          max_w=max(600.0, b - a - 400), centre=True)
    if V.POOL_X0 < x_cut < V.POOL_X1:
        sh.p.fit_text("POOL", uv((0, (V.POOL_Y0 + V.POOL_Y1) / 2, 0), fr)[0] + ox,
                      (V.POOL_TW + V.POOL_FL) / 2, 220, "A-ANNO-TEXT", max_w=3000, centre=True)
        sh.p.fit_text("BASIN", uv((0, (V.BASIN_Y0 + V.BASIN_Y1) / 2 + 150, 0), fr)[0] + ox,
                      V.BASIN_FL - 700, 180, "A-ANNO-TEXT", max_w=2000, centre=True)
    sh.p.fit_text("NORTH  (STREET)", umin + ox + 800, -900, 180, "A-ANNO-TEXT", max_w=4000)
    sh.p.fit_text("SOUTH  (GARDEN)", umax + ox - 3500, -2500, 180, "A-ANNO-TEXT", max_w=4000)

    top = V.RF + V.SLAB + V.PARAPET
    sh.text(title, umin, -4200, 520)
    sh.text(f"SCALE 1:100   --   CUT AT x = {x_cut:.0f} ({why.upper()}), LOOKING EAST: "
            f"THROUGH THE FIRST STAIR FLIGHT AND THE DOUBLE-HEIGHT LIVING", umin, -4850, 200)
    sh.text("STAIR, ITS GLASS GUARDS AND HANDRAILS PROJECTED FROM villa_gltf LIKE "
            "EVERYTHING ELSE (villa_design.stair_parts / guards / rail_parts)",
            umin, -5250, 160)
    sh.p.scale_bar(umin + ox, -6600, 5)
    key_plan(sh, umax + ox + 1200, -9200 + 3400, 0.125, x_cut=x_cut)
    tb = titleblock(sh, sheet_no, title, umax + ox + 4600 - 18000, -11200)
    return sh, tb, x_cut, top


def _y_spans(geom, x_cut, y0=-BIG, y1=BIG):
    """[(y0, y1)] of a plan geometry along the cut line x = x_cut."""
    g = geom.intersection(LineString([(x_cut, y0), (x_cut, y1)]))
    out = []
    for seg in getattr(g, "geoms", [g]):
        if seg.is_empty or seg.geom_type != "LineString" or seg.length < 1.0:
            continue
        ys = [c[1] for c in seg.coords]
        out.append((min(ys), max(ys)))
    return sorted(out)


def stair_model_probe(solid, s):
    """(found, total, lowest, highest): the model's stair `s` (a V.STAIRS
    record) against V.flights(): every tread's top at its level (solid just
    under it, air just over it, at the tread's centre), the half-landing's,
    and the arrival nosing's at the floor it arrives at."""
    lv = V.LEVEL
    z0, z1 = lv[s["from"]], lv[s["to"]]
    fl = [f for f in V.flights() if f.get("stair", s["name"]) == s["name"] and f.get("inside")]
    tops = []                                   # (x, y, z) to probe
    for f in fl:
        for t0, t1, z in V.flight_treads(f):
            x0, y0, x1, y1 = V.flight_plan(f, t0, t1)
            tops.append(((x0 + x1) / 2, (y0 + y1) / 2, z))
        top = f["z_foot"] + f["n"] * f["rise"]
        if abs(top - z1) < 1.0:                  # the arrival nosing, 150 deep
            t = f["t_foot"] + f["dir"] * (f["n"] - 1) * f["going"]
            x0, y0, x1, y1 = V.flight_plan(f, min(t, t + f["dir"] * 150.0),
                                           max(t, t + f["dir"] * 150.0))
            tops.append(((x0 + x1) / 2, (y0 + y1) / 2, top))
    for name, (x0, y0, x1, y1), z in (VG.stair_landings() if VG else []):
        if name == s["name"]:
            tops.append(((x0 + x1) / 2, (y0 + y1) / 2, z))
    found = [z for x, y, z in tops
             if solid.is_inside(Vector(x, y, z - 1.0)) and not solid.is_inside(Vector(x, y, z + 1.0))]
    zs = [z for _x, _y, z in tops]
    return len(found), len(tops), min(zs, default=z0), max(zs, default=z1)


def _section_project(*, sh, fr, ox, umin, umax, x_cut, why, facing, look, sec, scls,
                     cuts, halves, vis, fabric, joinery, allcut, ground, soil, title,
                     sheet_no, drawn=()):
    """Checks and annotation of A-A for a design with its own SECTION_X --
    the villa's (in section()) generalised to the design's VOIDS, STAIRS,
    basement (BELOW) and pool:
      * every void on the cut is open from the floor under it to the slab
        soffit over its top storey (the double height), with a floor slab
        under and a slab over it, and each slab it cuts is open over it;
      * every house stair (STAIRS) rises in the model as flights() says:
        each tread, landing and arrival top at its level; a stair seen
        beyond the cut is DRAWN there (a line at every tread);
      * datums STREET, the below-grade storeys, GF, FF, RF, T/PARAPET and the
        pool's (water, floor, shallow floor, sun ledge) sit on cut edges."""
    lv = V.LEVEL
    north_right = uv((0, V.PLOT_D, 0), fr)[0] > uv((0, 0, 0), fr)[0]

    def u_of(y):
        return uv((0, y, 0), fr)[0]

    def u_span(y0, y1):
        return tuple(sorted((u_of(y0), u_of(y1))))

    joined = unary_union([fabric] + joinery)
    cv = cut_voids(x_cut)
    volumes = []                                     # (void, lower, u0, u1, z0, z1)
    for v in cv:
        fls = sorted((f for f in v[5] if f in lv), key=lambda f: lv[f])
        if not fls:
            continue
        lower = floor_below(fls[0])
        top_name, z_hi = soffit_over(fls[-1])
        if lower is None:
            continue
        z_lo = lv[lower]
        rooms = unary_union([V.net_poly(r) for r in V.rooms_on(lower)])
        for y0, y1 in _y_spans(rooms, x_cut, v[2], v[4]):
            u0, u1 = u_span(y0, y1)
            box_ = sbox(u0 + 1, z_lo + 1, u1 - 1, z_hi - 1)
            blocked = box_.intersection(joined).area
            um = (u0 + u1) / 2
            floor_ok = fabric.contains(Point(um, z_lo - V.SLAB / 2))
            roof_ok = fabric.contains(Point(um, z_hi + V.SLAB / 2))
            volumes.append((v, lower, u0, u1, z_lo, z_hi))
            check(f"A-A: double-height {v[0]} open {lower} to {top_name}",
                  blocked < 1.0 and floor_ok and roof_ok,
                  f"y {y0:.0f}-{y1:.0f} (the {v[0]} over the {lower} rooms on the cut): "
                  f"{blocked / 1e6:.3f} m2 of cut fabric or glass between {lower} "
                  f"{z_lo:+.0f} and the soffit {z_hi:+.0f}; floor slab "
                  f"{'yes' if floor_ok else 'NO'}, slab over {'yes' if roof_ok else 'NO'}")
    slab_fabric = unary_union([q for k, ps in cuts.items()
                               if scls[k] == "fabric" and k != "stair" for q in ps])
    for v in cv:
        for fl in (f for f in v[5] if f in lv):
            z = lv[fl]
            su = u_span(v[2], v[4])
            slab_band = sbox(su[0] + 1, z - V.SLAB + 1, su[1] - 1, z - 1)
            in_void = slab_band.intersection(slab_fabric).area
            edge_a = slab_fabric.contains(Point(su[0] - 150, z - V.SLAB / 2))
            edge_b = slab_fabric.contains(Point(su[1] + 150, z - V.SLAB / 2))
            check(f"A-A: {fl} slab open over the {v[0]}", in_void < 1.0 and edge_a and edge_b,
                  f"y {v[2]:.0f}-{v[4]:.0f}: {in_void / 1e6:.3f} m2 of slab in the void; "
                  f"slab each side {'yes' if edge_a and edge_b else 'NO'}")

    # --- the house stairs: in the model as flights() says; drawn where seen
    seen = stairs_seen(x_cut, look)
    cut_st = stairs_cut(x_cut)
    house = vis.get("house", [])
    st_solid = sec.get("stair")
    for s in getattr(V, "STAIRS", []):
        if st_solid is None:
            check(f"A-A: {s['name']} rises {s['from']} to {s['to']}", False,
                  "no 'stair' group in the model")
            continue
        n_ok, n, lo, hi = stair_model_probe(st_solid, s)
        rise = (lv[s["to"]] - lv[s["from"]]) / s["risers"]
        where = ("cut by A-A" if s in cut_st else "seen beyond the cut" if s in seen
                 else "not on the cut, not seen from it")
        check(f"A-A: {s['name']} rises {s['from']} to {s['to']}",
              n_ok == n and n > 0 and abs(lo - (lv[s["from"]] + rise)) < 1.0
              and abs(hi - lv[s["to"]]) < 1.0,
              f"{n_ok}/{n} tread, landing and arrival tops at their levels in the model, "
              f"{lo:+.0f}..{hi:+.0f}: {s['risers']} risers of {rise:.1f} from "
              f"{s['from']} {lv[s['from']]:+.0f} ({where})")
    for s in seen:
        waist = s.get("waist") or WAIST
        treads = [(t0, t1, z) for f in V.flights() if f.get("stair") == s["name"]
                  for t0, t1, z in V.flight_treads(f)]
        n_drawn = 0
        for t0, t1, z in treads:
            a, b = u_span(t0, t1)
            lo_, hi_ = a + TOL, b - TOL
            c = max(coverage(house, "h", z, lo_, hi_, tol=1.0),
                    coverage(house, "h", z - waist, lo_, hi_, tol=1.0) if not s.get("solid") else 0.0)
            n_drawn += c >= 0.5
        check(f"A-A: {s['name']} drawn beyond the cut", treads and n_drawn == len(treads),
              f"{n_drawn}/{len(treads)} treads drawn at their level (top or soffit, over half "
              f"their going) in the projection beyond x={x_cut:.0f}")
    for s in cut_st:
        sx0, sy0, sx1, sy1 = s["rect"]
        a, b = u_span(sy0, sy1)
        polys = [q for q in cuts.get("stair", []) if q.intersects(sbox(a, -BIG, b, BIG))]
        sb = unary_union(polys).bounds if polys else None
        check(f"A-A: {s['name']} cut", sb is not None and sb[3] > lv[s["from"]] + 1.0,
              f"stair cut v {sb[1]:.0f}..{sb[3]:.0f}" if sb else "nothing of it cut")

    b_all = bbox(list(halves.values()))
    vtop = max(max(s_[1], s_[3]) for k in vis for s_ in vis[k])
    check("A-A: overall height = model bbox", abs(vtop - b_all[5]) <= 1.0,
          f"drawing top {vtop:.1f}, cut model top {b_all[5]:.1f}")

    # --- datums
    pool_on = V.POOL_X0 < x_cut < V.POOL_X1
    pool_marks = []
    if pool_on:
        pool_marks = [("POOL TWL", V.POOL_TW), ("POOL FLOOR", V.POOL_FL)]
        if hasattr(V, "BASIN_WL"):
            pool_marks += [("BASIN WL", V.BASIN_WL), ("BASIN FLOOR", V.BASIN_FL)]
        if getattr(V, "POOL_SHALLOW_FL", V.POOL_FL) != V.POOL_FL:
            pool_marks.append(("POOL SHALLOW", V.POOL_SHALLOW_FL))
        ledge = getattr(V, "POOL_LEDGE", None)
        if ledge and ledge[0] < x_cut < ledge[2]:
            pool_marks.append(("SUN LEDGE", ledge[4]))
    gz = getattr(V, "GARDEN_Z", None)
    if gz is not None and any(abs(p_[1] - gz) < 1 for ln in ground for p_ in ln):
        pool_marks.append(("GARDEN", gz))
    cut_line = LineString([(x_cut, -BIG), (x_cut, BIG)])
    house_marks = section_levels() + [(n, z) for _f, n, z, o in storey_levels()
                                      if o.intersects(cut_line)]
    hedges = []
    for q in geoms(allcut):
        for ring in [q.exterior, *q.interiors]:
            cs = list(ring.coords)
            hedges += [(a[0], a[1], b[0], b[1]) for a, b in zip(cs, cs[1:])]
    for ps in cuts.values():
        for q in ps:
            for g_ in geoms(q):
                cs = list(g_.exterior.coords)
                hedges += [(a[0], a[1], b[0], b[1]) for a, b in zip(cs, cs[1:])]
    miss = [f"{n} {z:+.0f}" for n, z in house_marks + pool_marks
            if coverage(hedges, "h", z, umin, umax, tol=1.0) <= 0.0]
    check("A-A: level datums sit on cut edges", not miss,
          ("no cut edge at " + ", ".join(miss)) if miss else
          ", ".join(level_label(n, z).replace("%%p", "+-")
                    for n, z in house_marks + pool_marks))

    # --- annotation: the house's datums on the north (street) side, the
    #     pool's on the south (garden) side
    if north_right:
        levels(sh, house_marks, umax + 300, umax + 1200, "right")
    else:
        levels(sh, house_marks, umin - 300, umin - 1200, "left")
    if pool_marks:
        py0 = getattr(V, "BASIN_Y0", V.POOL_Y0 - getattr(V, "POOL_COPING", 0.0))
        pu = u_span(py0, V.POOL_Y1)
        if north_right:
            levels(sh, pool_marks, pu[0] - 200, umin - 1200, "left")
        else:
            levels(sh, pool_marks, pu[1] + 200, umax + 1200, "right")
    # each double height dimensioned floor to soffit, inside the volume, 550
    # in from the end where the stair seen beyond is lowest (its text, half
    # way up, then stands clear of the flight)
    def stair_top_at(y):
        zs = [z for s in seen for f in V.flights() if f.get("stair") == s["name"]
              for t0, t1, z in V.flight_treads(f) if t0 - 1 <= y <= t1 + 1]
        return max(zs, default=-BIG)

    dims = []
    for v, lower, u0, u1, z_lo, z_hi in volumes:
        ends = [(u0 + 550, u0 + 150, -400), (u1 - 550, u1 - 150, 400)]
        if not north_right:
            ends.reverse()                       # the south end first
        y_of = (lambda u: u) if north_right else (lambda u: -u)
        line_u, at_u, off = min(ends, key=lambda e: stair_top_at(y_of(e[0])))
        sh.p.dim_v(z_lo, z_hi, at_u + ox, off)
        dims.append(line_u)

    # labels keep off the linework drawn beyond: tried at 1500 over the
    # floor, then lower and higher, the first height whose text crosses no
    # line wins (1500 if none is clear)
    from ezdxf.enums import TextEntityAlignment as TA
    from shapely.strtree import STRtree
    lines_ = [LineString([(s_[0], s_[1]), (s_[2], s_[3])]) for s_ in drawn]
    tree = STRtree(lines_) if lines_ else None

    def label(txt, u, z_floor, max_w):
        t = None
        for dz in (1500, 1100, 1900, 700, 2300, 2700):
            if t is None:
                t = sh.p.text(txt, u + ox, z_floor + dz, 200, "A-ANNO-TEXT",
                              align="MIDDLE_CENTER")
                h = 200.0
                for _ in range(14):              # plan_dxf.fit_text's shrink
                    x0_, _a, x1_, _b = sh.p.bbox(t)
                    if x1_ - x0_ <= max_w or h <= 90:
                        break
                    h *= 0.90
                    t.dxf.height = h
                    t.set_placement((u + ox, z_floor + dz), align=TA.MIDDLE_CENTER)
            else:
                t.set_placement((u + ox, z_floor + dz), align=TA.MIDDLE_CENTER)
            x0_, y0_, x1_, y1_ = sh.p.bbox(t)
            box_ = sbox(x0_ - ox - 60, y0_ - 60, x1_ - ox + 60, y1_ + 60)
            if tree is None or not any(lines_[i].intersects(box_) for i in tree.query(box_)):
                return
        t.set_placement((u + ox, z_floor + 1500), align=TA.MIDDLE_CENTER)

    # room labels: over each room's floor on the cut, clear of the voids
    # through that floor, of nested rooms (net_poly) and, on the floor a
    # seen stair starts from, of the stair drawn beyond
    for r in V.ROOMS:
        if not (r[1] < x_cut < r[3]) or r[6] not in lv:
            continue
        g = V.net_poly(r)
        for v in getattr(V, "VOIDS", []):
            if r[6] in v[5]:
                g = g.difference(sbox(v[1], v[2], v[3], v[4]))
        for s in seen:
            if lv[s["from"]] == lv[r[6]]:
                g = g.difference(sbox(-BIG, s["rect"][1], BIG, s["rect"][3]))
        spans = _y_spans(g, x_cut)
        if not spans:
            continue
        y0, y1 = max(spans, key=lambda p: p[1] - p[0])
        label(r[0], u_of((y0 + y1) / 2), lv[r[6]], max(600.0, y1 - y0 - 200))
    for v in cv:
        a, b = u_span(v[2], v[4])
        for d in dims:
            if a < d < b:
                if d - a > b - d:
                    b = min(b, d - 400)
                else:
                    a = max(a, d + 400)
        for fl in (f for f in v[5] if f in lv):
            label(v[0], (a + b) / 2, lv[fl], max(600.0, b - a - 400))
    if pool_on:
        sh.p.fit_text(getattr(V, "POOL_LABEL", "POOL"),
                      u_of((V.POOL_Y0 + V.POOL_Y1) / 2) + ox,
                      (V.POOL_TW + V.POOL_FL) / 2, 220, "A-ANNO-TEXT", max_w=3000, centre=True)
        if hasattr(V, "BASIN_Y0"):
            sh.p.fit_text("BASIN", u_of((V.BASIN_Y0 + V.BASIN_Y1) / 2 + 150) + ox,
                          V.BASIN_FL - 700, 180, "A-ANNO-TEXT", max_w=2000, centre=True)
    # below everything drawn (the basement and its earth), then the titles
    low = min([allcut.bounds[1]] + ([soil.bounds[1]] if soil is not None and not soil.is_empty
                                    else []))
    v_lab = min(-900.0, low - 700.0)
    n_u, s_u = (umax - 3500, umin + 800) if north_right else (umin + 800, umax - 3500)
    sh.p.fit_text("NORTH  (STREET)", n_u + ox, v_lab, 180, "A-ANNO-TEXT", max_w=4000)
    sh.p.fit_text("SOUTH  (GARDEN)", s_u + ox, v_lab, 180, "A-ANNO-TEXT", max_w=4000)
    dv = v_lab - (-2500.0)                           # the villa's layout, moved down

    top = V.RF + V.SLAB + V.PARAPET
    text = getattr(V, "SECTION_TEXT", None) or f"CUT AT x = {x_cut:.0f}"
    sh.text(title, umin, -4200 + dv, 520)
    sh.text(f"SCALE 1:100   --   {text}   --   LOOKING {facing}", umin, -4850 + dv, 200)
    notes = ["STAIRS, GLASS GUARDS AND HANDRAILS PROJECTED FROM villa_gltf LIKE EVERYTHING ELSE"]
    if soil is not None:
        notes.append("EARTH HATCHED BELOW THE MODEL'S TERRAIN TO 600 UNDER THE BASEMENT SLAB")
    sh.text(";  ".join(notes), umin, -5250 + dv, 160)
    sh.p.scale_bar(umin + ox, -6600 + dv, 5)
    # the key plan (1:800, its cut arrows ~3600 past the plot) under the
    # lowest datum drawn on its side of the sheet
    kp_y = -9200 + 3400 + dv
    right = [z for z in [z for _n, z in house_marks] if north_right] + \
            [z for z in [z for _n, z in pool_marks] if not north_right]
    if right:
        kp_y = min(kp_y, min(right) - 700 - (V.PLOT_D + 3600) * 0.125)
    key_plan(sh, umax + ox + 1200, kp_y, 0.125, x_cut=x_cut, look=look)
    tb = titleblock(sh, sheet_no, title, umax + ox + 4600 - 18000,
                    min(-11200 + dv, kp_y - 1500 - 2600))
    return sh, tb, x_cut, top


# ================================================================== main
def main():
    t0 = time.perf_counter()
    print("  building the render model (villa_gltf.building/boundary/landscape) ...")
    groups, cls = model()
    print(f"  {len(groups)} groups in {time.perf_counter() - t0:.1f}s: "
          + ", ".join(f"{k}[{cls[k]}]" for k in groups))
    check_orientation()
    standing = standing_landscape()      # hedges (a design's own landscape only)

    made = []
    for key, sheet_no, title, lf in VIEWS:
        sh, notes, tb, n = elevation(key, sheet_no, title, lf, groups, cls, standing)
        made.append((sheet_no, sh, notes, tb))
        print(f"  {sheet_no} {title}: {n} external openings on this facade; title block: {tb}")
        for nt in notes:
            print(f"       {nt}")
    sh, tb, x_cut, _ = section(groups, cls)
    made.append(("A-301", sh, [], tb))
    print(f"  A-301 SECTION A-A at x={x_cut:.0f}; title block: {tb}")

    failed = [c for c in CHECKS if not c[1]]
    for no, sh, _, _ in made:
        if failed:
            sh.p.text(f"CHECKS FAILED ({len(failed)}) -- NOT FOR ISSUE",
                      0, 11600, 500, "A-ANNO-NOTE")
        path = os.path.join(OUT, f"VILLA_{no.replace('-', '')}.dxf")
        sh.p.doc.saveas(path)
        png = render(sh.p.doc, path[:-4] + ".png")
        ok = os.path.getsize(png) > 20_000
        check(f"{no}: DXF + PNG written", os.path.exists(path) and ok,
              f"{os.path.basename(path)} {os.path.getsize(path) // 1024} KB, "
              f"{os.path.basename(png)} {os.path.getsize(png) // 1024} KB")

    print()
    w = max(len(c[0]) for c in CHECKS)
    for name, ok, detail in CHECKS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{w}}  {detail}")
    failed = [c for c in CHECKS if not c[1]]
    print(f"\n  {len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed"
          f"   {time.perf_counter() - t0:.0f}s   -> {OUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
