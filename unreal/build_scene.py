"""Build the villa render scene in Unreal Engine 5.8 -- run headless by
render_unreal.ps1 through `UnrealEditor-Cmd <project> -ExecutePythonScript=...`.

What it makes (all under /Game/Villa, rebuilt from scratch on every run, so a
re-exported model is simply picked up by running it again):
  Model/      the glb, imported with Interchange (meshes only, full-precision
              UVs: the UVs are baked at real-world size, 1 tile = 1 texture)
  Textures/   the ambientCG sets the Blender materials use (imported once, kept)
  Materials/  M_VillaPBR / M_VillaPlain / M_VillaGlass / M_VillaWater masters and
              one instance per surface. The glb's own materials are NOT used:
              Blender exported its height maps as normal maps.
  Maps/Villa  the level: model, context (ground, street, neighbours), shrubs,
              SunSky (Dubai), PostProcessVolume, one CineCameraActor per view
  Render/     LS_Villa (camera cuts + SunSky date/time keyed per view) and the
              Movie Render Queue path-tracer preset; the queue itself is
              saved as a manifest the -game render reads.

Frames: the model is metres, +Y north, Z up (right-handed). Unreal is
centimetres, Z up, LEFT-handed. The axis mapping is not assumed: it is measured
by matching every imported mesh's bounds against render\\groups.json, and the
cameras, context and north all go through that one measured mapping.

Configuration comes from environment variables (set by render_unreal.ps1):
  VILLA_UE_GLB, VILLA_UE_GROUPS, VILLA_UE_TEX (one folder, or several joined
  by ';'), VILLA_UE_VIEWS, VILLA_UE_SAMPLES, VILLA_UE_RES ("w,h"),
  VILLA_UE_FRAMES (MRQ output dir), VILLA_UE_STATUS (json), VILLA_UE_ROOT
  (content folder), VILLA_UE_DESIGN (villa_design.py)
and, when those are not given, from the pipeline's own two:
  VILLA_OUT         the deliverables folder (model: <VILLA_OUT>\\render\\...)
  VILLA_DESIGN_DIR  a PROJECT's design folder (projects\\<name>): its
                    villa_design.py, content under /Game/<Name>, logs under
                    logs\\<name> -- the villa's level, logs and manifest are
                    left alone.
A design with render hooks is built from them: RENDER_VIEWS (cameras; the
eyes and dates villa_blender.py rendered, from twinmotion\\views.json beside
the glb; an interior cut with the room lights turned down and a white
balance for the lamps), MATERIALS (a material per group by kind, tinted by
fit_tint from the texture averages / highs in twinmotion\\materials.json),
PLOT_W/PLOT_D/SB_* (the neighbours). The villa has none and is built as
before.
"""
import json
import math
import os
import random
import struct
import time
import traceback

import unreal

# ------------------------------------------------------------------ config
HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = r"C:\Users\lsire\OneDrive\Desktop"
DESKTOP_VILLA = os.path.join(DESKTOP, "Villa")
DESIGN_DIR = os.environ.get("VILLA_DESIGN_DIR", "")
if DESIGN_DIR and os.path.normcase(os.path.abspath(DESIGN_DIR)) == os.path.normcase(os.path.dirname(HERE)):
    DESIGN_DIR = ""                     # the pipeline folder: the villa's own design
PROJECT = os.path.basename(os.path.normpath(DESIGN_DIR)) if DESIGN_DIR else ""


def project_out_name(design_dir):
    """OUT_NAME from a project's villa_design.py, read as text (as
    run_project.out_name): the project's deliverables are Desktop\\<OUT_NAME>
    when VILLA_OUT is not set -- never the villa's Desktop\\Villa."""
    import re
    try:
        with open(os.path.join(design_dir, "villa_design.py"), encoding="utf-8") as f:
            m = re.search(r'^OUT_NAME\s*=\s*["\']([^"\']+)["\']', f.read(), re.M)
    except OSError:
        m = None
    return m.group(1) if m else os.path.basename(os.path.normpath(design_dir)).capitalize()


OUT_ROOT = os.environ.get("VILLA_OUT") or (
    os.path.join(DESKTOP, project_out_name(DESIGN_DIR)) if DESIGN_DIR else DESKTOP_VILLA)
GLB = os.environ.get("VILLA_UE_GLB") or os.path.join(OUT_ROOT, "render", "twinmotion", "villa_twinmotion.glb")
GROUPS = os.environ.get("VILLA_UE_GROUPS") or (
    os.path.join(OUT_ROOT, "render", "groups.json") if (os.environ.get("VILLA_OUT") or DESIGN_DIR) else "")
# the ambientCG sets: the run's own unpacked copies first, then the downloads'
TEX_DIRS = [d for d in os.environ.get("VILLA_UE_TEX", "").split(";") if d] or [
    os.path.join(OUT_ROOT, "render", "materials", "_tex"),
    os.path.join(DESKTOP_VILLA, "render", "materials", "_tex")]
TEX = TEX_DIRS[0]
VIEW_NAMES = [v.strip() for v in os.environ.get("VILLA_UE_VIEWS", "").split(",") if v.strip()]
SAMPLES = int(os.environ.get("VILLA_UE_SAMPLES", "1024"))
RES = tuple(int(v) for v in os.environ.get("VILLA_UE_RES", "2400,1500").split(","))
LOGS = os.path.join(HERE, "logs", PROJECT) if PROJECT else os.path.join(HERE, "logs")
FRAMES = os.environ.get("VILLA_UE_FRAMES", os.path.join(LOGS, "frames"))
STATUS = os.environ.get("VILLA_UE_STATUS", os.path.join(LOGS, "build_status.json"))
# rooms for the interior lights; 0 lux turns them off
DESIGN = os.environ.get("VILLA_UE_DESIGN") or (
    os.path.join(DESIGN_DIR, "villa_design.py") if DESIGN_DIR
    else os.path.join(os.path.dirname(HERE), "villa_design.py"))
# what villa_blender.py wrote beside the glb for a design with render hooks
SIDECAR = os.path.dirname(GLB)
# Interiors in daylight are ~30x darker than the sunlit facade and read as black
# holes; archviz lights them far above real levels (the Blender render does the
# same) so the rooms read through the glass.
INTERIOR_LUX = float(os.environ.get("VILLA_UE_INTERIOR_LUX", "12000"))
HAZE = float(os.environ.get("VILLA_UE_HAZE", "2.5"))      # x the default Mie scattering

# a project builds its own level under /Game/<Name>; the villa's stays
ROOT = os.environ.get("VILLA_UE_ROOT") or (
    "/Game/" + "".join(c for c in PROJECT.title() if c.isalnum()) if PROJECT else "/Game/Villa")
MODEL = ROOT + "/Model"
TEXP = "/Game/Villa/Textures"          # the texture library, shared, imported once
MATP = ROOT + "/Materials"
RENDER = ROOT + "/Render"
MAP = ROOT + "/Maps/Villa"
SEQ_NAME = "LS_Villa"
MANIFEST = f"QueueManifest_{PROJECT}.utxt" if PROJECT else "QueueManifest.utxt"

# Dubai, UAE: no daylight saving
SITE = {"latitude": 25.2048, "longitude": 55.2708, "timezone": 4.0}

# name: eye, target (model metres), lens (mm, 36 mm-wide filmback as in the
# Blender renders), (month, day, clock time), exposure EV100, white balance (K:
# below 6500 cools the low, warm sun a little, as a photographer would),
# two-point perspective (level camera + shifted filmback: verticals stay vertical)
VIEWS = {
    "aerial_sw": dict(eye=(-13.0, -17.0, 21.0), target=(12.0, 13.5, 3.0), lens=35.0,
                      date=(3, 20), clock=10.0, ev=14.9, wb=6300, level=False),
    "garden": dict(eye=(19.2, 3.2, 2.4), target=(11.0, 14.0, 4.4), lens=20.0,
                   date=(12, 15), clock=15.5, ev=14.5, wb=5900, level=True),
    "street": dict(eye=(5.5, 38.0, 1.7), target=(11.0, 21.0, 4.2), lens=24.0,
                   date=(6, 21), clock=18.25, ev=13.0, wb=5300, level=True),
    "aerial_ne": dict(eye=(38.0, 45.0, 24.0), target=(12.0, 13.0, 2.0), lens=35.0,
                      date=(6, 21), clock=17.0, ev=14.3, wb=6000, level=False),
}

# surfaces (the Blender render's, same texture sets and tints; the UVs already
# carry each set's real size): texture set, tint, roughness x, normal strength,
# colour detail (1 = the texture as shot, 0 = its average colour), saturation,
# roughness + (the honed/flamed stone maps are near-polished as shot).
# Travertine001's banding reads as onyx/timber and Ground054 as orange dune
# sand in raking desert light, so both are toned down.
PBR = {
    "concrete": ("Concrete034", (0.62, 0.62, 0.60), 1.0, 0.3, 0.8, 0.5, 0.0),
    "travertine": ("Travertine001", (1.0, 0.97, 0.93), 1.0, 0.35, 0.22, 0.45, 0.15),
    "travertine_flamed": ("Travertine001", (0.97, 0.94, 0.90), 1.0, 0.7, 0.2, 0.4, 0.4),
    "oak": ("WoodFloor040", (0.62, 0.53, 0.44), 1.0, 0.6, 1.0, 0.72, 0.0),
    "basalt": ("PavingStones150", (1.0, 1.0, 1.0), 1.0, 0.8, 1.0, 0.9, 0.0),
    "gravel": ("Gravel023", (1.0, 1.0, 1.0), 1.0, 1.0, 1.0, 0.8, 0.0),
    "grass": ("Grass001", (0.92, 0.95, 0.85), 1.0, 0.8, 1.0, 0.85, 0.0),
    "sand": ("Ground054", (1.08, 1.03, 0.95), 1.0, 0.6, 0.7, 0.45, 0.0),
}
ASSIGN = {
    "walls": "concrete", "slabs": "concrete", "roof": "concrete",
    "fins": "bronze", "frames": "bronze", "pool": "travertine",
    "base": "travertine", "boundary": "travertine", "paving": "travertine_flamed",
    "drive": "basalt", "deck": "oak", "gravel": "gravel", "lawn": "grass",
    "planting": "gravel", "terrain": "sand", "glass": "glass",
    "door": "oak", "water": "water",
    # groups added by the DBC integration (villa_blender.ASSIGN maps them the
    # same way): glass balustrades, the basin grate, the stair, its handrails
    "guards": "glass", "grate": "bronze", "stair": "travertine", "rails": "bronze",
    # a design's stone cladding skin (massing 'stone'), made on demand
    "stone": "stone_dark",
}
# groups whose triangles are walls / floors / solid obstacles for the room
# test, the interior lights and the shrubs ('stone' is a wall: the stone
# skin is the outer face of the east rooms)
SIDE_GROUPS = ("walls", "stone", "base", "glass", "frames", "door")   # base: a basement's walls
VERT_GROUPS = ("slabs", "roof", "base", "walls", "stone")
SOLID_GROUPS = ("boundary", "walls", "stone", "base", "pool", "paving", "deck", "fins")

# a design's MATERIALS kinds in Unreal: the ambientCG set (tinted to the
# design's colour by the averages villa_blender.py measured) and its colour
# detail; anything else is a plain colour. glass/water use the thin masters.
KIND_UE = {
    "concrete": ("Concrete034", 0.8), "timber": ("WoodFloor040", 1.0),
    "timber_dark": ("WoodFloor040", 1.0), "timber_deck": ("WoodFloor040", 1.0),
    "limestone": ("Travertine001", 0.22), "travertine": ("Travertine001", 0.8),
    "grass": ("Grass001", 1.0), "hedge": ("Grass001", 1.0), "gravel": ("Gravel023", 1.0),
    "soil": ("Ground054", 0.7), "interlock": ("PavingStones150", 1.0),
}
PLAIN_KIND = {"stone_dark": (0.20, 0.20, 0.21, 0.9), "metal_black": (0.05, 0.05, 0.055, 0.35),
              "render_white": (0.92, 0.91, 0.88, 0.85)}

# villa_blender.fit_tint's numbers: a tint up to TINT_MAX takes a set as it
# is; a set far darker than the design's colour (Grass001 under a lawn) is
# pulled toward its average (ColorDetail) until its brightest texels stay
# under ALBEDO_HI, then tinted in full up to TINT_FIT_MAX
TINT_MAX = 4.0
TINT_FIT_MAX = 16.0
ALBEDO_HI = 0.9
DETAIL_MIN = 0.25
HI_RATIO_DEFAULT = 2.5


def fit_tint(color, avg, hi=None, detail=1.0):
    """villa_blender.fit_tint (the tests hold the two equal): (tint, detail,
    clamped) that bring a set of average `avg` (99th percentile `hi`) to
    `color` on average, from the recipe's `detail`."""
    t = [c / max(a, 1e-3) for c, a in zip(color, avg)]
    if max(t) <= TINT_MAX:
        return tuple(t), detail, False
    hi = hi or [a * HI_RATIO_DEFAULT for a in avg]
    d = detail
    for c, a, h in zip(color, avg, hi):
        r = h / max(a, 1e-3)
        if c > 0 and r > 1.0:
            d = min(d, (ALBEDO_HI / c - 1.0) / (r - 1.0))
    d = max(DETAIL_MIN, min(detail, d))
    return tuple(min(TINT_FIT_MAX, v) for v in t), d, max(t) > TINT_FIT_MAX


# villa_blender.rough_fit's numbers: a design's roughness IS the surface's;
# the set's roughness map (RoughnessMap) only modulates it. Without this the
# design textured materials took the map as it is -- Travertine001 is shot
# polished (mean 0.026), so the Fairway's limestone paving and coping (0.75 /
# 0.7) and its stair (0.5) rendered as a near-mirror.
ROUGH_DEV = 0.05
ROUGH_BAND = 0.12
ROUGH_MIN = 0.02


def rough_fit(rough, mean=None, std=None):
    """villa_blender.rough_fit (the tests hold the two equal): (gain, offset,
    lo, hi) -- the master's RoughnessMul, RoughnessAdd, RoughnessMin and
    RoughnessMax -- so clamp(gain * map + offset, lo, hi) averages the
    design's `rough` over a map of mean `mean`, standard deviation `std`
    (None: no statistics -- the design's value, flat)."""
    rough = max(ROUGH_MIN, min(1.0, float(rough)))
    lo, hi = max(ROUGH_MIN, rough - ROUGH_BAND), min(1.0, rough + ROUGH_BAND)
    if mean is None or std is None or mean <= 1e-4:
        return 0.0, rough, lo, hi
    gain = rough / mean
    if std > 1e-6:
        gain = min(gain, ROUGH_DEV / std)
    return gain, rough - gain * mean, lo, hi


def kind_roughness(kind, rough):
    """The roughness a kind renders with: the design's, except a hedge's leaves
    (villa_blender.hedge_material: at most 0.75, leaves have a sheen)."""
    return min(float(rough), 0.75) if kind == "hedge" else float(rough)


# villa_blender's interior floor finishes (FLOOR_FINISH / floor_plan): the
# photographs' polished travertine downstairs, oak in the bedrooms, concrete
# in the service rooms -- (set or None, tint or colour, roughness, detail)
FLOOR_FINISH = {"travertine": ("Travertine001", (1.0, 0.98, 0.95), 0.18, 0.9),
                "oak": ("WoodFloor040", (0.95, 0.82, 0.68), 0.45, 1.0),
                "concrete": (None, (0.42, 0.42, 0.41), 0.3, 1.0)}
FLOOR_T = 0.010
FLOOR_OAK_ROLES = ("bedroom", "master_bedroom", "dressing", "family_lounge")
FLOOR_CONCRETE_ROLES = ("garage", "plant", "store", "laundry")
TILE_M = {"Travertine001": 1.20, "WoodFloor040": 1.90}      # villa_blender.TEX_SIZE


def _rect_minus_mm(rects, cut):
    """villa_blender._rect_minus (mm, slivers under 1 mm dropped)."""
    cx0, cy0, cx1, cy1 = cut
    out = []
    for x0, y0, x1, y1 in rects:
        if cx0 >= x1 or cx1 <= x0 or cy0 >= y1 or cy1 <= y0:
            out.append((x0, y0, x1, y1))
            continue
        if cy0 > y0:
            out.append((x0, y0, x1, cy0))
        if cy1 < y1:
            out.append((x0, cy1, x1, y1))
        ya, yb = max(y0, cy0), min(y1, cy1)
        if cx0 > x0:
            out.append((x0, ya, cx0, yb))
        if cx1 < x1:
            out.append((cx1, ya, x1, yb))
    return [r for r in out if r[2] - r[0] > 1.0 and r[3] - r[1] > 1.0]


def floor_plan(V):
    """villa_blender.floor_plan (the tests hold the two equal): the floor
    finishes of a design as (label, finish, x0, y0, x1, y1, z), metres."""
    level = getattr(V, "LEVEL", None) or {}
    below = set(getattr(V, "BELOW_GRADE_FLOORS", ()) or ())
    role = getattr(V, "ROLE", None) or {}
    voids = getattr(V, "VOIDS", None) or []
    out = []
    for r in V.ROOMS:
        name, x0, y0, x1, y1, _kind, fl = r[:7]
        if fl in below or fl not in level or fl == "RF":
            continue
        rects = [(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))]
        for q in V.ROOMS:
            if q[6] == fl and q[0] != name and min(q[1], q[3]) >= rects[0][0] \
                    and min(q[2], q[4]) >= rects[0][1] and max(q[1], q[3]) <= rects[0][2] \
                    and max(q[2], q[4]) <= rects[0][3]:
                rects = _rect_minus_mm(rects, (min(q[1], q[3]), min(q[2], q[4]),
                                               max(q[1], q[3]), max(q[2], q[4])))
        for v in voids:
            if fl in v[5]:
                rects = _rect_minus_mm(rects, tuple(v[1:5]))
        rl = role.get(name, "")
        finish = "oak" if rl in FLOOR_OAK_ROLES else \
            "concrete" if rl in FLOOR_CONCRETE_ROLES else "travertine"
        z = level[fl] * 0.001
        for j, (a, b, c, d) in enumerate(rects):
            out.append((f"{fl} {name} {j}", finish, a * 0.001, b * 0.001, c * 0.001, d * 0.001, z))
    return out


# a design's pool: villa_blender's water absorbs (per metre) 0.5 x (1 - the
# colour it keeps); the thin surface here tints each crossing as POOL_DEPTH_M
# of that water would, and ripples far less than the villa's (at a grazing
# eye-level view strong ripples mirror the dark garden, not the house). A
# thin surface cannot bend the camera ray down onto the lit tank floor as
# Blender's refracting water does: at a low sun it looks through to shaded
# tank walls and reads navy (0.15 still did). WATER_SCATTER of the surface
# is the water's own colour, lit where it lies -- the blue a pool's body
# scatters back; at 0.5 the eye-level pool reads blue under the reflections,
# as the Blender render's does.
POOL_DEPTH_M = 1.4
WATER_RIPPLE_DESIGN = 0.05
WATER_SCATTER = float(os.environ.get("VILLA_UE_WATER_SCATTER", "0.5"))
MOSAIC_ROUGHNESS = 0.15     # villa_blender's mosaic (kind_material('mosaic', ..., 0.15))


# ------------------------------------------------------------------ design
_DESIGN = {}


def design():
    """villa_design.py of this run (data only at import: its shapely imports
    live inside functions), loaded once; None if it cannot be."""
    if "mod" not in _DESIGN:
        _DESIGN["mod"] = None
        if os.path.exists(DESIGN):
            try:
                _DESIGN["mod"] = load_design()
            except Exception as e:
                warn(f"cannot load {DESIGN}: {e}")
    return _DESIGN["mod"]


def sidecar(name):
    p = os.path.join(SIDECAR, name)
    try:
        if not os.path.exists(p):
            return {}
        with open(p) as fh:
            return json.load(fh)
    except Exception as e:
        warn(f"{p}: {e}")
        return {}


def _sun_position(doy, hour, lat=25.2048, lon=55.2708, tz=4.0):
    """NOAA's approximate solar position (azimuth from north, elevation), deg
    -- villa_blender.sun_date's, to find a date for a design's (az, el)."""
    g = 2 * math.pi / 365.0 * (doy - 1 + (hour - 12) / 24.0)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    dec = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g)
           - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
           - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    ha = math.radians((hour * 60 + eqt + 4 * lon - 60 * tz) / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha)
    el = 90 - math.degrees(math.acos(max(-1.0, min(1.0, cz))))
    az = (math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la)
                                  - math.tan(dec) * math.cos(la))) + 180) % 360
    return az, el


def sun_date(az, el):
    """(month, day, clock hours) in Dubai whose sun is nearest (az, el)."""
    import datetime
    best = None
    for doy in range(1, 366):
        for m5 in range(5 * 12, 20 * 12):
            a, e = _sun_position(doy, m5 / 12.0)
            err = math.hypot(((a - az + 180) % 360 - 180) * math.cos(math.radians(el)), e - el)
            if best is None or err < best[0]:
                best = (err, doy, m5)
    d = datetime.date(2026, 1, 1) + datetime.timedelta(days=best[1] - 1)
    return d.month, d.day, best[2] / 12.0


def _interp(x, pts):
    if x <= pts[0][0]:
        return pts[0][1]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if x <= xb:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    return pts[-1][1]


# exposure (EV100) and white balance by sun elevation, from the villa's
# calibrated views (street 11 deg 13.0, garden 22 deg 14.5, aerial 46 deg 14.9)
EV_BY_ELEVATION = ((5.0, 12.4), (11.0, 13.0), (22.0, 14.3), (46.0, 14.9))
# Interior views, as villa_blender renders them: the INTERIOR_LUX ceiling
# lights (set for the windows seen from outside, far above real levels) are
# turned down to INTERIOR_CUT_LIGHTS for an interior camera cut (keyed in
# LS_Villa), the exposure set EV_INTERIOR from the exterior's, and the white
# balance set for the mix of 3000 K lamps and daylight (INTERIOR_WB) -- at
# the sun's balance the lamps turn white walls ochre.
EV_INTERIOR = float(os.environ.get("VILLA_UE_EV_INTERIOR", "-1.2"))
INTERIOR_CUT_LIGHTS = float(os.environ.get("VILLA_UE_INTERIOR_CUT", "0.3"))
# ... and an exterior cut sees them at villa_blender's EXTERIOR_LIGHTS: at the
# golden hour the rooms glow, they do not blaze (at full strength the ground
# floor glazing read amber in the Fairway's exterior views)
EXTERIOR_CUT_LIGHTS = float(os.environ.get("VILLA_UE_EXTERIOR_CUT", "0.5"))
INTERIOR_WB = float(os.environ.get("VILLA_UE_INTERIOR_WB", "3500"))
EV_BACKLIT = -0.4           # opened up for a front in its own shade


def design_views():
    """A design's RENDER_VIEWS as VIEWS entries -- with the eye and date
    villa_blender.py rendered (twinmotion\\views.json) when it is there."""
    V = design()
    rv = getattr(V, "RENDER_VIEWS", None) if V else None
    if not rv:
        return None
    done = sidecar("views.json")
    out = {}
    for name, v in rv.items():
        r = done.get(name, {})
        az, el = (float(c) for c in v.get("sun", (240.0, 30.0)))
        if r.get("date") and r.get("clock"):
            hh, mm = r["clock"].split(":")
            mo, dy, clock = r["date"][0], r["date"][1], int(hh) + int(mm) / 60.0
        else:
            mo, dy, clock = sun_date(az, el)
        eye = tuple(float(c) for c in r.get("eye", v["eye"]))
        tgt = tuple(float(c) for c in v["target"])
        look = math.degrees(math.atan2(tgt[0] - eye[0], tgt[1] - eye[1])) % 360
        into_sun = max(0.0, math.cos(math.radians(abs((look - az + 180) % 360 - 180))))
        interior = bool(v.get("interior"))
        ev = _interp(el, EV_BY_ELEVATION) + (EV_INTERIOR if interior else EV_BACKLIT * into_sun)
        wb = INTERIOR_WB if interior else 5300 if el < 15 else 5900 if el < 30 else 6300
        out[name] = dict(eye=eye, target=tgt, lens=float(v.get("lens", 24.0)), date=(mo, dy),
                         clock=round(clock, 3), ev=round(ev, 2), wb=wb,
                         level=eye[2] <= 3.0, sun=(az, el), interior=interior,
                         lights=INTERIOR_CUT_LIGHTS if interior else EXTERIOR_CUT_LIGHTS,
                         design_eye=tuple(float(c) for c in v["eye"]))
    return out


def all_views():
    return design_views() or VIEWS


def context_layout(W, D):
    """The neighbours, as villa_blender.context_layout: the villa's numbers,
    or a design's own setbacks when it has render hooks."""
    V = design()
    if not (V and getattr(V, "RENDER_VIEWS", None)):
        return {"side": 3.0, "near_y0": 11.0, "far_y0": 3.0, "depth": 13.0, "height": 8.4}
    side = getattr(V, "SB_SIDE", 3000.0) / 1000.0
    front = getattr(V, "SB_FRONT", 5000.0) / 1000.0
    depth = round(min(0.45 * D, D - front - getattr(V, "SB_REAR", 3000.0) / 1000.0), 2)
    parts = [getattr(V, k, None) for k in ("RF", "SLAB", "PARAPET")]
    top = sum(parts) / 1000.0 if None not in parts else 8.4
    return {"side": side, "near_y0": D - front - depth, "far_y0": front, "depth": depth,
            "height": top}


def rect_minus(rects, cut):
    """Axis-aligned rectangles less one rectangle, as rectangles."""
    cx0, cy0, cx1, cy1 = cut
    out = []
    for x0, y0, x1, y1 in rects:
        if cx0 >= x1 or cx1 <= x0 or cy0 >= y1 or cy1 <= y0:
            out.append((x0, y0, x1, y1))
            continue
        if cy0 > y0:
            out.append((x0, y0, x1, cy0))
        if cy1 < y1:
            out.append((x0, cy1, x1, y1))
        ya, yb = max(y0, cy0), min(y1, cy1)
        if cx0 > x0:
            out.append((x0, ya, cx0, yb))
        if cx1 < x1:
            out.append((cx1, ya, x1, yb))
    return [r for r in out if r[2] - r[0] > 1e-3 and r[3] - r[1] > 1e-3]

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
STATE = {"warnings": []}


def log(msg):
    unreal.log("[villa] " + str(msg))


def warn(msg):
    STATE["warnings"].append(str(msg))
    unreal.log_warning("[villa] " + str(msg))


# ------------------------------------------------------------------ glb reader
_CT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    data = open(path, "rb").read()
    magic, _ver, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError(f"{path}: not a glb")
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        off += 8
        chunk = data[off:off + clen]
        off += clen
        if ctype == 0x4E4F534A:
            js = json.loads(chunk)
        elif ctype == 0x004E4942:
            bin_ = chunk
    return js, bin_


def _accessor(js, bin_, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    n = _NC[a["type"]]
    fmt = _CT[a["componentType"]]
    size = struct.calcsize(fmt)
    stride = bv.get("byteStride") or size * n
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for k in range(a["count"]):
        v = struct.unpack_from("<" + fmt * n, bin_, base + k * stride)
        out.append(v if n > 1 else v[0])
    return out


def _mat_mul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def _node_matrix(n):
    if "matrix" in n:
        m = n["matrix"]                      # column-major
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    tx, ty, tz = n.get("translation", (0, 0, 0))
    qx, qy, qz, qw = n.get("rotation", (0, 0, 0, 1))
    sx, sy, sz = n.get("scale", (1, 1, 1))
    r = [[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
         [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
         [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]]
    return [[r[0][0] * sx, r[0][1] * sy, r[0][2] * sz, tx],
            [r[1][0] * sx, r[1][1] * sy, r[1][2] * sz, ty],
            [r[2][0] * sx, r[2][1] * sy, r[2][2] * sz, tz],
            [0, 0, 0, 1]]


_GLB_CACHE = {}


def glb_triangles(path, name):
    """World-space triangles of the node(s) called `name`, in MODEL metres
    (glTF is Y-up: model = (x, -z, y))."""
    if path not in _GLB_CACHE:
        _GLB_CACHE[path] = read_glb(path)
    js, bin_ = _GLB_CACHE[path]
    parent = {}
    for i, n in enumerate(js["nodes"]):
        for c in n.get("children", []):
            parent[c] = i
    tris = []
    for i, n in enumerate(js["nodes"]):
        if n.get("name") != name or "mesh" not in n:
            continue
        m = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        k = i
        while k is not None:
            m = _mat_mul(_node_matrix(js["nodes"][k]), m)
            k = parent.get(k)
        for prim in js["meshes"][n["mesh"]]["primitives"]:
            pos = _accessor(js, bin_, prim["attributes"]["POSITION"])
            idx = _accessor(js, bin_, prim["indices"]) if "indices" in prim else list(range(len(pos)))
            world = []
            for (x, y, z) in pos:
                gx = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]
                gy = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]
                gz = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
                world.append((gx, -gz, gy))
            for t in range(0, len(idx) - 2, 3):
                tris.append((world[idx[t]], world[idx[t + 1]], world[idx[t + 2]]))
    return tris


def axis_ray(tris, p, axis, sign):
    """Distance from p along +/- `axis` to the nearest triangle (None: no hit).
    Axis-aligned, so it is a 2D point-in-triangle test in the other two axes
    plus a barycentric interpolation of the hit coordinate."""
    u, v = [k for k in range(3) if k != axis]
    best = None
    pu, pv, pa = p[u], p[v], p[axis]
    for a, b, c in tris:
        au, av, bu, bv, cu, cv = a[u], a[v], b[u], b[v], c[u], c[v]
        if pu < min(au, bu, cu) or pu > max(au, bu, cu) or pv < min(av, bv, cv) or pv > max(av, bv, cv):
            continue
        det = (bv - cv) * (au - cu) + (cu - bu) * (av - cv)
        if abs(det) < 1e-12:
            continue
        l1 = ((bv - cv) * (pu - cu) + (cu - bu) * (pv - cv)) / det
        l2 = ((cv - av) * (pu - cu) + (au - cu) * (pv - cv)) / det
        l3 = 1.0 - l1 - l2
        if l1 < -1e-9 or l2 < -1e-9 or l3 < -1e-9:
            continue
        d = (l1 * a[axis] + l2 * b[axis] + l3 * c[axis] - pa) * sign
        if d > 1e-4 and (best is None or d < best):
            best = d
    return best


# ------------------------------------------------------------------ frames
class Frame:
    """Model metres (x east, y north, z up) <-> Unreal centimetres, as a
    signed axis permutation measured from the imported meshes."""

    def __init__(self, perm=(1, 0, 2), sign=(1, 1, 1)):
        self.perm, self.sign = perm, sign     # UE axis i = sign[i] * model[perm[i]]

    def vec(self, p, scale=100.0):
        return unreal.Vector(*(self.sign[i] * p[self.perm[i]] * scale for i in range(3)))

    def size(self, s):
        return unreal.Vector(*(abs(s[self.perm[i]]) for i in range(3)))

    def back(self, v, scale=0.01):
        """UE vector -> model tuple."""
        u = (v.x, v.y, v.z)
        out = [0.0, 0.0, 0.0]
        for i in range(3):
            out[self.perm[i]] = self.sign[i] * u[i] * scale
        return tuple(out)

    def mirrored(self):
        # a shape-preserving right-handed -> left-handed mapping has det -1
        m = [[0] * 3 for _ in range(3)]
        for i in range(3):
            m[i][self.perm[i]] = self.sign[i]
        det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
               - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
               + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
        return det > 0

    def __repr__(self):
        ax = "xyz"
        return "UE(X,Y,Z) = (" + ", ".join(("-" if self.sign[i] < 0 else "") + ax[self.perm[i]]
                                          for i in range(3)) + ") x 100"


def candidates():
    for perm in ((0, 1, 2), (1, 0, 2)):
        for sx in (1, -1):
            for sy in (1, -1):
                yield Frame(perm, (sx, sy, 1))


def measure_frame(meshes, groups):
    """Pick the axis mapping under which every mesh's bounds match groups.json."""
    best = None
    for f in candidates():
        err, n = 0.0, 0
        for key, sm in meshes.items():
            g = groups.get(key)
            if not g:
                continue
            a = f.vec((g[0] / 1000, g[1] / 1000, g[2] / 1000))
            b = f.vec((g[3] / 1000, g[4] / 1000, g[5] / 1000))
            lo = (min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))
            hi = (max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))
            bb = sm.get_bounding_box()
            got = (bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z)
            err = max(err, max(abs(u - v) for u, v in zip(got, lo + hi)))
            n += 1
        if n and (best is None or err < best[1]):
            best = (f, err, n)
    return best


# ------------------------------------------------------------------ assets
def ensure_dir(path):
    if not EAL.does_directory_exist(path):
        EAL.make_directory(path)


def wipe(path):
    if EAL.does_directory_exist(path):
        if not EAL.delete_directory(path):
            raise RuntimeError(f"could not delete {path}")
    elif EAL.does_asset_exist(path):
        if not EAL.delete_asset(path):
            raise RuntimeError(f"could not delete {path}")


def interchange_import(filename, dest, pipeline=None):
    """Synchronous Interchange import (AssetImportTask runs Interchange
    asynchronously and returns before the asset exists). Returns the paths."""
    mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
    src = unreal.InterchangeManager.create_source_data(filename)
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    if pipeline is not None:
        params.override_pipelines = [unreal.SoftObjectPath(pipeline.get_path_name())]
    res = mgr.import_asset(dest, src, params)
    try:
        mgr.wait_until_all_tasks_done(True)
    except Exception as e:
        warn(f"interchange wait: {e}")
    return list(res) if isinstance(res, (list, tuple, unreal.Array)) else []


def import_glb():
    """Meshes only, full-precision UVs, no Nanite / lightmaps / collision."""
    ensure_dir(ROOT + "/Pipelines")
    pipe_path = ROOT + "/Pipelines/P_VillaGLTFAssets"
    if EAL.does_asset_exist(pipe_path):
        EAL.delete_asset(pipe_path)
    pipe = EAL.duplicate_asset("/Interchange/Pipelines/DefaultGLTFAssetsPipeline", pipe_path)
    mp = pipe.get_editor_property("material_pipeline")
    mp.set_editor_property("import_materials", False)
    mp.get_editor_property("texture_pipeline").set_editor_property("import_textures", False)
    mesh = pipe.get_editor_property("mesh_pipeline")
    for k, v in (("build_nanite", False), ("generate_lightmap_u_vs", False),
                 ("collision", False), ("import_static_meshes", True)):
        try:
            mesh.set_editor_property(k, v)
        except Exception as e:
            warn(f"mesh pipeline {k}: {e}")
    common = pipe.get_editor_property("common_meshes_properties")
    for k, v in (("use_full_precision_u_vs", True), ("recompute_normals", False),
                 ("bake_meshes", True), ("remove_degenerates", True)):
        try:
            common.set_editor_property(k, v)
        except Exception as e:
            warn(f"common mesh {k}: {e}")
    EAL.save_loaded_asset(pipe)

    # A design's palms (villa_palms.glb) come in the SAME import: only the
    # first Interchange import of a script runs synchronously -- a second
    # one returns nothing and never completes before the script ends
    # (measured) -- so the two files are merged into one first.
    src, merged = GLB, None
    palms_glb = os.path.join(SIDECAR, "villa_palms.glb")
    if design_hooks(design()) and os.path.exists(palms_glb):
        import tempfile
        merged = os.path.join(tempfile.gettempdir(), f"villa_ue_{PROJECT or 'design'}_with_palms.glb")
        try:
            src = merge_glb(GLB, palms_glb, merged)
        except Exception as e:
            warn(f"villa_palms.glb not merged ({e}): blade palms")
            src, merged = GLB, None
    try:
        ok = interchange_import(src, MODEL, pipe)
    finally:
        if merged and os.path.exists(merged):
            try:
                os.remove(merged)
            except OSError:
                pass
    meshes = {}
    for p in EAL.list_assets(MODEL, recursive=True, include_folder=False):
        a = EAL.load_asset(p)
        if isinstance(a, unreal.StaticMesh):
            key = a.get_name()
            for pre in ("SM_", "S_"):
                if key.startswith(pre):
                    key = key[len(pre):]
            meshes[key] = a
    STATE["palm_meshes"] = {k: meshes.pop(k) for k in sorted(meshes) if k.startswith("ctx_palm")}
    log(f"import_asset -> {ok}; {len(meshes)} static meshes: {sorted(meshes)}"
        + (f"; {len(STATE['palm_meshes'])} palm meshes" if STATE["palm_meshes"] else ""))
    if not meshes:
        raise RuntimeError("the glb import produced no static meshes")
    return meshes


def _glb_chunks(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, _ver, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError(f"{path}: not a glb")
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        off += 8
        if ctype == 0x4E4F534A:
            js = json.loads(data[off:off + clen])
        elif ctype == 0x004E4942:
            bin_ = data[off:off + clen]
        off += clen
    return js, bin_


def merge_glb(a_path, b_path, out_path):
    """Append glb B's scene (nodes, meshes, their accessors and buffer views)
    to glb A's, as one glb at out_path. B's materials, images and textures
    are dropped (its meshes are given their own materials here); A is kept
    whole. Both single-buffer, as Blender writes them. Returns out_path."""
    A, abin = _glb_chunks(a_path)
    B, bbin = _glb_chunks(b_path)
    if len(A.get("buffers", [])) > 1 or len(B.get("buffers", [])) > 1:
        raise ValueError("more than one buffer")
    pad = (-len(abin)) % 4
    base = len(abin) + pad
    nbv, nacc, nmesh, nnode = (len(A.get(k, [])) for k in ("bufferViews", "accessors", "meshes", "nodes"))
    used = set()
    for bv in B.get("bufferViews", []):
        bv = dict(bv, buffer=0, byteOffset=bv.get("byteOffset", 0) + base)
        A.setdefault("bufferViews", []).append(bv)
    for acc in B.get("accessors", []):
        acc = dict(acc)
        if "bufferView" in acc:
            acc["bufferView"] += nbv
        if "sparse" in acc:
            raise ValueError("sparse accessors")
        A.setdefault("accessors", []).append(acc)
    for mesh in B.get("meshes", []):
        prims = []
        for p in mesh["primitives"]:
            p = {k: v for k, v in p.items() if k not in ("material", "targets")}
            p["attributes"] = {k: v + nacc for k, v in p["attributes"].items()}
            if "indices" in p:
                p["indices"] += nacc
            prims.append(p)
        A.setdefault("meshes", []).append(dict(mesh, primitives=prims))
    for node in B.get("nodes", []):
        node = {k: v for k, v in node.items() if k not in ("camera", "skin")}
        if "mesh" in node:
            node["mesh"] += nmesh
        if "children" in node:
            node["children"] = [c + nnode for c in node["children"]]
        A.setdefault("nodes", []).append(node)
    scene_b = B["scenes"][B.get("scene", 0)]["nodes"]
    A["scenes"][A.get("scene", 0)]["nodes"] += [n + nnode for n in scene_b]
    used.update(A.get("extensionsUsed", []))
    used.update(B.get("extensionsUsed", []))
    if used:
        A["extensionsUsed"] = sorted(used)
    blob = abin + b"\0" * pad + bbin
    blob += b"\0" * ((-len(blob)) % 4)
    A["buffers"] = [{"byteLength": len(blob)}]
    js = json.dumps(A, separators=(",", ":")).encode("utf-8")
    js += b" " * ((-len(js)) % 4)
    with open(out_path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js) + 8 + len(blob)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)
    return out_path


def import_texture(set_name, kind):
    """One ambientCG map, imported once into /Game/Villa/Textures/<set>."""
    dest = f"{TEXP}/{set_name}"
    tex_dir = next((d for d in TEX_DIRS if os.path.isdir(os.path.join(d, set_name))), TEX)
    files = [f for f in os.listdir(os.path.join(tex_dir, set_name)) if f.endswith(f"_{kind}.jpg")]
    if not files:
        raise FileNotFoundError(f"{set_name}: no *_{kind}.jpg in {tex_dir}")
    stem = os.path.splitext(files[0])[0]
    for p in EAL.list_assets(dest, recursive=False, include_folder=False) if EAL.does_directory_exist(dest) else []:
        if p.split(".")[-1].endswith(kind) or p.split("/")[-1].split(".")[0].endswith(kind):
            return EAL.load_asset(p)
    filename = os.path.join(tex_dir, set_name, files[0])
    # the classic TextureFactory imports synchronously (Interchange runs
    # texture imports on a background task and returns before they exist)
    task = unreal.AssetImportTask()
    task.filename = filename
    task.destination_path = dest
    task.automated = True
    task.replace_existing = True
    task.save = False
    task.factory = unreal.TextureFactory()
    AT.import_asset_tasks([task])
    tex = None
    for p in list(task.get_editor_property("imported_object_paths")):
        a = EAL.load_asset(p)
        if isinstance(a, unreal.Texture2D):
            tex = a
    if tex is None:                     # fall back to whatever landed in the folder
        for p in EAL.list_assets(dest, recursive=False, include_folder=False):
            if p.split(".")[-1].endswith(kind):
                tex = EAL.load_asset(p)
    if tex is None:
        raise RuntimeError(f"texture import failed: {filename}")
    if kind == "NormalDX":                 # DirectX convention = Unreal's
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property("srgb", False)
        tex.set_editor_property("flip_green_channel", False)
    elif kind == "Roughness":
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property("srgb", False)
    EAL.save_loaded_asset(tex)
    log(f"imported texture {stem}")
    return tex


# ------------------------------------------------------------------ materials
def _expr(mat, cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)


def _scalar(mat, name, value, x, y):
    e = _expr(mat, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", value)
    return e


def _vector(mat, name, rgb, x, y):
    e = _expr(mat, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    return e


def _texparam(mat, name, tex, sampler, x, y):
    e = _expr(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("texture", tex)
    e.set_editor_property("sampler_type", sampler)
    return e


def _connect(a, a_out, b, b_in):
    if not MEL.connect_material_expressions(a, a_out, b, b_in):
        raise RuntimeError(f"connect {a.get_name()}.{a_out} -> {b.get_name()}.{b_in} failed")


def _prop(a, a_out, prop):
    if not MEL.connect_material_property(a, a_out, prop):
        raise RuntimeError(f"connect {a.get_name()}.{a_out} -> {prop} failed")


def new_material(name):
    path = f"{MATP}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    return AT.create_asset(name, MATP, unreal.Material, unreal.MaterialFactoryNew())


def master_pbr(defaults):
    """Textured master: base colour (detail = contrast against the texture's own
    average, saturation) x tint (lerped by PerInstanceRandom), roughness map x
    scale, normal map with strength; mesh UVs (real-world, baked) or
    world-aligned XY UVs (WorldUV = 1) for the context boxes. No static
    switches: every instance shares the one shader map."""
    m = new_material("M_VillaPBR")
    m.set_editor_property("used_with_instanced_static_meshes", True)
    uv = _expr(m, unreal.MaterialExpressionTextureCoordinate, -1600, 0)
    uvs = _scalar(m, "UVScale", 1.0, -1600, 120)
    uv_mesh = _expr(m, unreal.MaterialExpressionMultiply, -1400, 40)
    _connect(uv, "", uv_mesh, "A")
    _connect(uvs, "", uv_mesh, "B")
    wp = _expr(m, unreal.MaterialExpressionWorldPosition, -1600, 260)
    mask = _expr(m, unreal.MaterialExpressionComponentMask, -1400, 260)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    _connect(wp, "", mask, "")
    tile = _scalar(m, "WorldTileCm", 350.0, -1400, 380)
    uv_world = _expr(m, unreal.MaterialExpressionDivide, -1200, 300)
    _connect(mask, "", uv_world, "A")
    _connect(tile, "", uv_world, "B")
    wsel = _scalar(m, "WorldUV", 0.0, -1200, 420)
    sw = _expr(m, unreal.MaterialExpressionLinearInterpolate, -1000, 120)
    _connect(uv_mesh, "", sw, "A")
    _connect(uv_world, "", sw, "B")
    _connect(wsel, "", sw, "Alpha")

    col = _texparam(m, "BaseColorMap", defaults["Color"], unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -700, -300)
    _connect(sw, "", col, "UVs")
    # the texture's average colour: the same parameter read at its smallest mip
    avg = _texparam(m, "BaseColorMap", defaults["Color"], unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -700, -560)
    avg.set_editor_property("mip_value_mode", unreal.TextureMipValueMode.TMVM_MIP_LEVEL)
    avg.set_editor_property("const_mip_value", 14)
    _connect(sw, "", avg, "UVs")
    detail = _scalar(m, "ColorDetail", 1.0, -700, -700)
    dl = _expr(m, unreal.MaterialExpressionLinearInterpolate, -450, -400)
    _connect(avg, "RGB", dl, "A")
    _connect(col, "RGB", dl, "B")
    _connect(detail, "", dl, "Alpha")
    sat = _scalar(m, "Saturation", 1.0, -450, -560)
    inv = _expr(m, unreal.MaterialExpressionOneMinus, -300, -560)
    _connect(sat, "", inv, "")
    des = _expr(m, unreal.MaterialExpressionDesaturation, -250, -420)
    _connect(dl, "", des, "")
    _connect(inv, "", des, "Fraction")
    ta = _vector(m, "Tint", (1, 1, 1), -450, -900)
    tb = _vector(m, "TintB", (1, 1, 1), -450, -800)
    pir = _expr(m, unreal.MaterialExpressionPerInstanceRandom, -450, -1000)
    tint = _expr(m, unreal.MaterialExpressionLinearInterpolate, -250, -850)
    _connect(ta, "", tint, "A")
    _connect(tb, "", tint, "B")
    _connect(pir, "", tint, "Alpha")
    base = _expr(m, unreal.MaterialExpressionMultiply, -50, -500)
    _connect(des, "", base, "A")
    _connect(tint, "", base, "B")
    _prop(base, "", unreal.MaterialProperty.MP_BASE_COLOR)

    rough = _texparam(m, "RoughnessMap", defaults["Roughness"], unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -500, 0)
    _connect(sw, "", rough, "UVs")
    rmul = _scalar(m, "RoughnessMul", 1.0, -500, 220)
    rr = _expr(m, unreal.MaterialExpressionMultiply, -250, 60)
    _connect(rough, "R", rr, "A")
    _connect(rmul, "", rr, "B")
    radd = _scalar(m, "RoughnessAdd", 0.0, -250, 220)
    ra = _expr(m, unreal.MaterialExpressionAdd, -150, 60)
    _connect(rr, "", ra, "A")
    _connect(radd, "", ra, "B")
    rsat = _expr(m, unreal.MaterialExpressionSaturate, -80, 60)
    _connect(ra, "", rsat, "")
    # a design's band round its roughness (rough_fit); the defaults 0 / 1 are
    # the identity after the saturate, so the villa's instances are unchanged
    rmin = _scalar(m, "RoughnessMin", 0.0, -80, 200)
    rmax = _scalar(m, "RoughnessMax", 1.0, -80, 280)
    rlo = _expr(m, unreal.MaterialExpressionMax, 20, 60)
    _connect(rsat, "", rlo, "A")
    _connect(rmin, "", rlo, "B")
    rhi = _expr(m, unreal.MaterialExpressionMin, 120, 60)
    _connect(rlo, "", rhi, "A")
    _connect(rmax, "", rhi, "B")
    _prop(rhi, "", unreal.MaterialProperty.MP_ROUGHNESS)

    nrm = _texparam(m, "NormalMap", defaults["NormalDX"], unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -500, 320)
    _connect(sw, "", nrm, "UVs")
    flat = _expr(m, unreal.MaterialExpressionConstant3Vector, -500, 560)
    flat.set_editor_property("constant", unreal.LinearColor(0, 0, 1, 0))
    ns = _scalar(m, "NormalStrength", 1.0, -500, 660)
    nl = _expr(m, unreal.MaterialExpressionLinearInterpolate, -250, 420)
    _connect(flat, "", nl, "A")
    _connect(nrm, "RGB", nl, "B")
    _connect(ns, "", nl, "Alpha")
    _prop(nl, "", unreal.MaterialProperty.MP_NORMAL)

    _prop(_scalar(m, "Metallic", 0.0, -250, 760), "", unreal.MaterialProperty.MP_METALLIC)
    _prop(_scalar(m, "Specular", 0.5, -250, 860), "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


def master_plain():
    m = new_material("M_VillaPlain")
    m.set_editor_property("used_with_instanced_static_meshes", True)
    a = _vector(m, "Color", (0.5, 0.5, 0.5), -600, -200)
    b = _vector(m, "ColorB", (0.5, 0.5, 0.5), -600, -60)
    pir = _expr(m, unreal.MaterialExpressionPerInstanceRandom, -600, 80)
    lerp = _expr(m, unreal.MaterialExpressionLinearInterpolate, -300, -120)
    _connect(a, "", lerp, "A")
    _connect(b, "", lerp, "B")
    _connect(pir, "", lerp, "Alpha")
    _prop(lerp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    _prop(_scalar(m, "Roughness", 0.5, -300, 100), "", unreal.MaterialProperty.MP_ROUGHNESS)
    _prop(_scalar(m, "Metallic", 0.0, -300, 200), "", unreal.MaterialProperty.MP_METALLIC)
    _prop(_scalar(m, "Specular", 0.5, -300, 300), "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


def _custom(mat, code, inputs, out_type, x, y, desc):
    """An HLSL Custom expression with named inputs."""
    e = _expr(mat, unreal.MaterialExpressionCustom, x, y)
    e.set_editor_property("code", code)
    e.set_editor_property("output_type", out_type)
    e.set_editor_property("description", desc)
    ins = []
    for n in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        ins.append(ci)
    e.set_editor_property("inputs", ins)
    return e


# villa_blender.stone_material in HLSL: dry-stacked ledgestone on the mesh UVs
# (metres, baked by villa_blender.world_uvs; V runs up the wall, so the
# courses are level) -- 68 mm courses, stones 250-700 mm long, each course
# its own offset and each stone its own shade (1.9x to 0.45x the design's
# colour, as the Blender brick colours), 3.5 mm shadow joints, a split-face
# relief from a value noise. Returns (albedo factor, dh/du, dh/dv, face).
STONE_HLSL = r"""
float rowH = 0.068;
float jw = 0.0035;
float dstep = 0.0015;
float h0 = 0.0; float hu = 0.0; float hv = 0.0;
float shade = 1.0; float face = 1.0;
for (int k = 0; k < 3; k++) {
    float2 q = UV.xy + (k == 1 ? float2(dstep, 0.0) : (k == 2 ? float2(0.0, dstep) : float2(0.0, 0.0)));
    float row = floor(q.y / rowH);
    float r1 = frac(sin(row * 12.9898 + 4.13) * 43758.5453);
    float r2 = frac(sin(row * 78.233 + 1.71) * 43758.5453);
    float w = lerp(0.25, 0.70, r2);
    float u = q.x + r1 * 3.7;
    float sn = floor(u / w);
    float fx = u - sn * w;
    float fy = q.y - row * rowH;
    float d = min(min(fx, w - fx), min(fy, rowH - fy));
    float j = saturate(d / jw);
    float id = frac(sin(dot(float2(sn, row), float2(12.9898, 78.233))) * 43758.5453);
    float n = 0.0; float amp = 0.5; float2 z = q * 14.0 + id * 17.0;
    for (int o = 0; o < 3; o++) {
        float2 i0 = floor(z); float2 f = frac(z); f = f * f * (3.0 - 2.0 * f);
        float a = frac(sin(dot(i0, float2(127.1, 311.7))) * 43758.5453);
        float b = frac(sin(dot(i0 + float2(1.0, 0.0), float2(127.1, 311.7))) * 43758.5453);
        float c = frac(sin(dot(i0 + float2(0.0, 1.0), float2(127.1, 311.7))) * 43758.5453);
        float e = frac(sin(dot(i0 + float2(1.0, 1.0), float2(127.1, 311.7))) * 43758.5453);
        n += amp * lerp(lerp(a, b, f.x), lerp(c, e, f.x), f.y);
        z = z * 2.03; amp = amp * 0.5;
    }
    float h = j * (0.006 + 0.003 * id + 0.008 * n);
    if (k == 0) { h0 = h; face = j; shade = lerp(1.9, 0.45, saturate(id - 0.1)) * (0.55 + 0.9 * n); }
    else if (k == 1) { hu = h; } else { hv = h; }
}
return float4(lerp(0.05, shade, face), (hu - h0) / dstep, (hv - h0) / dstep, face);
"""


def master_stone():
    """A design's stone_dark (the stacked-stone flank, the BBQ wall, the
    piers): STONE_HLSL on the mesh UVs, the design's colour and roughness."""
    m = new_material("M_VillaStone")
    uv = _expr(m, unreal.MaterialExpressionTextureCoordinate, -1100, 0)
    pat = _custom(m, STONE_HLSL, ["UV"], unreal.CustomMaterialOutputType.CMOT_FLOAT4,
                  -800, 0, "Ledgestone")
    _connect(uv, "", pat, "UV")
    col = _vector(m, "Color", (0.20, 0.20, 0.21), -800, -300)
    alb = _expr(m, unreal.MaterialExpressionComponentMask, -500, -150)
    alb.set_editor_property("r", True)
    alb.set_editor_property("g", False)
    alb.set_editor_property("b", False)
    alb.set_editor_property("a", False)
    _connect(pat, "", alb, "")
    base = _expr(m, unreal.MaterialExpressionMultiply, -300, -250)
    _connect(col, "", base, "A")
    _connect(alb, "", base, "B")
    _prop(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    nrm = _custom(m, "return normalize(float3(-D.y, -D.z, 1.0));", ["D"],
                  unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 150, "Ledgestone normal")
    _connect(pat, "", nrm, "D")
    _prop(nrm, "", unreal.MaterialProperty.MP_NORMAL)
    _prop(_scalar(m, "Roughness", 0.9, -500, 350), "", unreal.MaterialProperty.MP_ROUGHNESS)
    _prop(_scalar(m, "Specular", 0.5, -500, 450), "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


# villa_blender.palm_materials' frond: leaflets cut from the strip by its UVs
# (u along the frond, v across, the rib at v = 0.5): 34 diagonal leaflets a
# frond covering ~60 %, the rib solid
FROND_HLSL = r"""
float a = abs(UV.y - 0.5);
float t = frac(UV.x * 34.0 + a * 5.0);
return (t < 0.62 || a < 0.04) ? 1.0 : 0.0;
"""


def master_frond():
    """The palms' fronds (villa_palms.glb): masked by FROND_HLSL, two-sided,
    lit through (two-sided foliage, as the Blender frond's translucency)."""
    m = new_material("M_VillaFrond")
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("two_sided", True)
    foliage = True
    try:
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    except Exception as e:
        foliage = False
        warn(f"frond shading model: {e}")
    col = _vector(m, "Color", (0.09, 0.16, 0.04), -600, -300)
    _prop(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    if foliage:
        _prop(_vector(m, "Subsurface", (0.20, 0.30, 0.06), -600, -150), "",
              unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    _prop(_scalar(m, "Roughness", 0.55, -600, 0), "", unreal.MaterialProperty.MP_ROUGHNESS)
    uv = _expr(m, unreal.MaterialExpressionTextureCoordinate, -900, 200)
    cut = _custom(m, FROND_HLSL, ["UV"], unreal.CustomMaterialOutputType.CMOT_FLOAT1,
                  -600, 200, "Leaflets")
    _connect(uv, "", cut, "UV")
    _prop(cut, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


def master_thin(name, color, opacity, roughness, transmittance, ripple=None):
    """Thin Translucent surface for the path tracer: specular reflection
    (Fresnel, F0 0.04) plus transmission tinted by a transmittance colour at
    every crossing, and -- unlike a refractive (IOR) material -- shadow rays
    pass through it, so the sun reaches the rooms behind the glazing and the
    floor of the pool.
    Water: a legacy (non-Substrate) translucent surface has no absorption, so
    clear water would show the travertine basin uncoloured; the tint per
    crossing (camera ray and sun ray) gives the aqua of 1.4 m of water.
    Ripples: an engine normal map in world XY."""
    m = new_material(name)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_THIN_TRANSLUCENT)
    m.set_editor_property("translucency_lighting_mode",
                          unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    _prop(_vector(m, "Color", color, -500, -300), "", unreal.MaterialProperty.MP_BASE_COLOR)
    _prop(_scalar(m, "Opacity", opacity, -500, -150), "", unreal.MaterialProperty.MP_OPACITY)
    _prop(_scalar(m, "Roughness", roughness, -500, -50), "", unreal.MaterialProperty.MP_ROUGHNESS)
    _prop(_scalar(m, "Specular", 0.5, -500, 50), "", unreal.MaterialProperty.MP_SPECULAR)
    out = _expr(m, unreal.MaterialExpressionThinTranslucentMaterialOutput, 0, -600)
    names = [str(n) for n in MEL.get_material_expression_input_names(out)]
    tr = _vector(m, "Transmittance", transmittance, -500, -600)
    _connect(tr, "", out, names[0] if names else "")
    if ripple is None:
        MEL.recompile_material(m)
        EAL.save_loaded_asset(m)
        return m
    wp = _expr(m, unreal.MaterialExpressionWorldPosition, -1300, 300)
    mask = _expr(m, unreal.MaterialExpressionComponentMask, -1100, 300)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    _connect(wp, "", mask, "")
    tile = _scalar(m, "RippleTileCm", 260.0, -1100, 420)
    uvw = _expr(m, unreal.MaterialExpressionDivide, -900, 340)
    _connect(mask, "", uvw, "A")
    _connect(tile, "", uvw, "B")
    n = _texparam(m, "RippleMap", ripple, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -700, 300)
    _connect(uvw, "", n, "UVs")
    flat = _expr(m, unreal.MaterialExpressionConstant3Vector, -700, 520)
    flat.set_editor_property("constant", unreal.LinearColor(0, 0, 1, 0))
    ns = _scalar(m, "RippleStrength", 0.2, -700, 620)
    nl = _expr(m, unreal.MaterialExpressionLinearInterpolate, -450, 400)
    _connect(flat, "", nl, "A")
    _connect(n, "RGB", nl, "B")
    _connect(ns, "", nl, "Alpha")
    _prop(nl, "", unreal.MaterialProperty.MP_NORMAL)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


def instance(name, parent, scalars=None, vectors=None, textures=None, switches=None):
    path = f"{MATP}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mi = AT.create_asset(name, MATP, unreal.MaterialInstanceConstant,
                         unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items():
        MEL.set_material_instance_scalar_parameter_value(mi, k, float(v))
    for k, v in (vectors or {}).items():
        MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(v[0], v[1], v[2], 1.0))
    for k, v in (textures or {}).items():
        MEL.set_material_instance_texture_parameter_value(mi, k, v)
    for k, v in (switches or {}).items():
        MEL.set_material_instance_static_switch_parameter_value(mi, k, bool(v))
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi)
    return mi


def build_materials():
    ensure_dir(MATP)
    sets = sorted({s for s, *_ in PBR.values()})
    tex = {s: {k: import_texture(s, k) for k in ("Color", "NormalDX", "Roughness")} for s in sets}
    pbr = master_pbr(tex["Concrete034"])
    plain = master_plain()
    ripple = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions02/ExampleContent/Textures/water_n")
    glass = master_thin("M_VillaGlass", (0.02, 0.03, 0.03), 0.0, 0.0, (0.90, 0.94, 0.92))
    water = master_thin("M_VillaWater", (0.03, 0.12, 0.12), 0.04, 0.03, (0.72, 0.90, 0.88), ripple=ripple)
    M = {}

    def textured(name, s, tint, rmul=1.0, nstr=1.0, detail=1.0, sat=1.0, radd=0.0, **extra):
        scalars = {"RoughnessMul": rmul, "NormalStrength": nstr, "ColorDetail": detail,
                   "Saturation": sat, "RoughnessAdd": radd}
        scalars.update(extra)
        return instance(name, pbr, scalars=scalars, vectors={"Tint": tint, "TintB": tint},
                        textures={"BaseColorMap": tex[s]["Color"], "NormalMap": tex[s]["NormalDX"],
                                  "RoughnessMap": tex[s]["Roughness"]})

    for key, spec in PBR.items():
        M[key] = textured(f"MI_{key}", *spec)
    M["bronze"] = instance("MI_bronze", plain, scalars={"Roughness": 0.38, "Metallic": 1.0},
                           vectors={"Color": (0.40, 0.27, 0.16), "ColorB": (0.40, 0.27, 0.16)})
    M["glass"] = glass
    M["water"] = water
    # context: world-aligned UVs (WorldUV = 1) on the engine cube
    M["ctx_sand"] = textured("MI_ctx_sand", *PBR["sand"], WorldUV=1.0, WorldTileCm=350.0)
    M["ctx_asphalt"] = textured("MI_ctx_asphalt", "Concrete034", (0.15, 0.15, 0.155), 1.0, 0.5, 0.6, 0.0, 0.35,
                                WorldUV=1.0, WorldTileCm=220.0)
    M["ctx_pavement"] = textured("MI_ctx_pavement", "Travertine001", (0.86, 0.84, 0.80), 1.0, 0.6, 0.2, 0.35, 0.45,
                                 WorldUV=1.0, WorldTileCm=120.0)
    M["ctx_plaster"] = instance("MI_ctx_plaster", plain, scalars={"Roughness": 0.9},
                                vectors={"Color": (0.78, 0.76, 0.72), "ColorB": (0.78, 0.76, 0.72)})
    for i, t in enumerate([(0.42, 0.55, 0.26), (0.34, 0.48, 0.22), (0.50, 0.58, 0.30)]):
        M[f"shrub{i}"] = textured(f"MI_shrub{i}", "Grass001", t, 1.1, 1.0, 1.0, 0.8, 0.1, UVScale=0.6)

    # a design's own MATERIALS: one material per distinct (kind, colour,
    # roughness), under "grp:<group>"; "grp:mosaic" lines the pool tank
    V = design()
    spec = (getattr(V, "MATERIALS", None) or {}) if V else {}
    mats_json = sidecar("materials.json")
    avg = mats_json.get("_texture_average", {})
    high = mats_json.get("_texture_high", {})
    rstats = mats_json.get("_roughness_stats", {})

    def rough_scalars(s, rough):
        """The master's roughness scalars for set s at the design's `rough`
        (rough_fit over the map statistics villa_blender measured; without
        them, the design's value flat -- never the map as it is)."""
        st = rstats.get(s)
        gain, off, lo, hi = rough_fit(rough, *st) if st else rough_fit(rough)
        return {"RoughnessMul": gain, "RoughnessAdd": off, "RoughnessMin": lo, "RoughnessMax": hi}

    def textured_design(name, s, tint, rough, nstr, detail, **extra):
        rs = rough_scalars(s, rough)
        return textured(name, s, tint, rs["RoughnessMul"], nstr, detail, 1.0, rs["RoughnessAdd"],
                        RoughnessMin=rs["RoughnessMin"], RoughnessMax=rs["RoughnessMax"], **extra)

    made = {}
    fits = {}
    stone = None
    for grp, m in spec.items():
        kind = m.get("kind", "")
        col = tuple(float(c) for c in m.get("color", (0.8, 0.8, 0.8))[:3])
        rough = float(m.get("roughness", 0.8))
        key = (kind, col, rough)
        if key not in made:
            name = f"MI_{kind}_{len(made)}"
            if kind == "glass":
                made[key] = glass
            elif kind == "water":
                top = max(col) or 1.0
                keep = tuple(0.55 + 0.45 * c / top for c in col)   # villa_blender's absorb colour
                made[key] = instance(name, water, scalars={"RippleStrength": WATER_RIPPLE_DESIGN,
                                                           "Opacity": WATER_SCATTER}, vectors={
                    "Transmittance": tuple(math.exp(-0.5 * (1.0 - k) * POOL_DEPTH_M) for k in keep),
                    "Color": col})
            elif kind in KIND_UE and KIND_UE[kind][0] in avg:
                s, detail = KIND_UE[kind]
                tint, detail, clamped = fit_tint(col, avg[s], high.get(s), detail)
                r = kind_roughness(kind, rough)
                rs = rough_scalars(s, r)
                fits[kind + " " + grp] = {"tint": [round(v, 4) for v in tint],
                                          "detail": round(detail, 4), "clamped": clamped,
                                          "roughness_fit": [round(rs[k], 4) for k in (
                                              "RoughnessMul", "RoughnessAdd", "RoughnessMin",
                                              "RoughnessMax")]}
                # the design's roughness, the set's map only modulating it
                made[key] = textured_design(name, s, tint, r, 0.8, detail)
            elif kind == "stone_dark":
                # villa_blender's stone recipe (courses, shades, shadow joints),
                # not a flat grey
                if stone is None:
                    stone = master_stone()
                made[key] = instance(name, stone, scalars={"Roughness": rough},
                                     vectors={"Color": col})
            else:
                made[key] = instance(name, plain, scalars={"Roughness": rough},
                                     vectors={"Color": col, "ColorB": col})
        M["grp:" + grp] = made[key]
    STATE["tint_fits"] = fits
    if spec.get("water", {}).get("kind") == "water":
        c = tuple(float(v) for v in spec["water"].get("color", (0.05, 0.42, 0.62))[:3])
        M["grp:mosaic"] = instance("MI_pool_mosaic", plain, scalars={"Roughness": MOSAIC_ROUGHNESS},
                                   vectors={"Color": c, "ColorB": c})
    if design_hooks(V):
        # render dressing of a design: palms, gate leaves, the golf course,
        # the interior floors
        M["ctx_bark"] = instance("MI_ctx_bark", plain, scalars={"Roughness": 0.9},
                                 vectors={"Color": (0.24, 0.19, 0.13), "ColorB": (0.24, 0.19, 0.13)})
        g = avg.get("Grass001")

        def grass_tint(col, fallback):
            return tuple(min(4.0, c / max(a, 1e-3)) for c, a in zip(col, g)) if g else fallback

        # the frond: the Blender palm's leaf green (palm_materials) -- for the
        # blade palms (palms_blades), when villa_palms.glb is not there
        M["ctx_frond"] = textured("MI_ctx_frond", "Grass001", grass_tint((0.09, 0.16, 0.04), (0.42, 0.55, 0.26)),
                                  1.0, 0.6, 0.6, 1.0, 0.0)
        M["ctx_frond_b"] = textured("MI_ctx_frond_b", "Grass001", grass_tint((0.13, 0.19, 0.05), (0.50, 0.58, 0.28)),
                                    1.0, 0.6, 0.6, 1.0, 0.0)
        # ... and the Blender palms' own fronds (villa_palms.glb): leaflets cut
        # by the UVs, the two ends of palm_materials' green ramp
        try:
            frond = master_frond()
            M["ctx_leaf"] = instance("MI_ctx_leaf", frond, vectors={"Color": (0.07, 0.13, 0.03)})
            M["ctx_leaf_b"] = instance("MI_ctx_leaf_b", frond, vectors={"Color": (0.12, 0.19, 0.05)})
        except Exception as e:
            warn(f"frond material: {e}")
        M["ctx_gate"] = instance("MI_ctx_gate", plain, scalars={"Roughness": 0.4},
                                 vectors={"Color": (0.05, 0.05, 0.055), "ColorB": (0.05, 0.05, 0.055)})
        lawn = tuple(float(v) for v in spec.get("lawn", {}).get("color", (0.36, 0.55, 0.24))[:3])
        for i, k in enumerate(GOLF_SHADES):                # rough, fairway, fairway b
            col = tuple(min(1.0, c * k) for c in lawn)     # villa_blender's _scaled
            if g:
                tint, detail, _cl = fit_tint(col, g, high.get("Grass001"), 0.8)
            else:
                tint, detail = tuple(t * k for t in PBR["grass"][1]), 0.8
            # villa_blender.context: the rough at 0.95, the fairway at 0.9
            M[f"ctx_golf{i}"] = textured_design(f"MI_ctx_golf{i}", "Grass001", tint,
                                                0.95 if i == 0 else 0.9, 0.6, detail,
                                                WorldUV=1.0, WorldTileCm=140.0)
        # the interior floor finishes (FLOOR_FINISH), world-aligned on the top
        # faces of their boxes at the set's real size
        for fin, (s, tint, rough, detail) in FLOOR_FINISH.items():
            if s:
                M[f"floor_{fin}"] = textured_design(f"MI_floor_{fin}", s, tint, rough, 0.8, detail,
                                                    WorldUV=1.0, WorldTileCm=100.0 * TILE_M[s])
            else:
                M[f"floor_{fin}"] = instance(f"MI_floor_{fin}", plain, scalars={"Roughness": rough},
                                             vectors={"Color": tint, "ColorB": tint})
    return M


def golf_albedos(lawn, avg, high=None):
    """The average albedo of each GOLF_SHADES band as build_materials tints
    it (tint x the set's average): three distinct shades (tested)."""
    out = []
    for k in GOLF_SHADES:
        col = tuple(min(1.0, c * k) for c in lawn)
        tint, _d, _cl = fit_tint(col, avg, high, 0.8)
        out.append(tuple(t * a for t, a in zip(tint, avg)))
    return out


def on_demand(M, name):
    """A material ASSIGN names that build_materials did not make (the stone
    skin of a design without MATERIALS): a plain colour, made once."""
    if name not in M and name in PLAIN_KIND:
        r, g, b, rough = PLAIN_KIND[name]
        plain = EAL.load_asset(f"{MATP}/M_VillaPlain")
        M[name] = instance(f"MI_{name}", plain, scalars={"Roughness": rough},
                           vectors={"Color": (r, g, b), "ColorB": (r, g, b)})
    return M.get(name)


# ------------------------------------------------------------------ level
def spawn(cls, loc=None, rot=None, label=None, folder=None):
    a = ACTORS.spawn_actor_from_class(cls, loc or unreal.Vector(0, 0, 0), rot or unreal.Rotator(0, 0, 0))
    if label:
        a.set_actor_label(label)
    if folder:
        a.set_folder_path(folder)
    return a


def mesh_actor(mesh, mat, label, folder, loc=None, scale=None, rot=None):
    a = spawn(unreal.StaticMeshActor, loc, rot, label, folder)
    c = a.static_mesh_component
    c.set_static_mesh(mesh)
    c.set_mobility(unreal.ComponentMobility.STATIC)
    if scale is not None:
        a.set_actor_scale3d(scale)
    if mat is not None:
        for i in range(max(1, c.get_num_materials())):
            c.set_material(i, mat)
    return a


def box(F, cube, mat, label, x0, y0, z0, x1, y1, z1, folder="Context"):
    """A box between two model-space corners (metres), from the 1 m engine cube."""
    centre = F.vec(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return mesh_actor(cube, mat, label, folder, loc=centre, scale=F.size((x1 - x0, y1 - y0, z1 - z0)))


def context(F, cube, M, W, D, holes=()):
    """Ground, street and neighbours -- the Blender render's context, same numbers:
    Dubai defaults, 3 m setbacks, 2 storeys, street on the north (+Y); a
    design's own setbacks when it has render hooks (context_layout). holes:
    plan rectangles (m) cut from the ground slab -- a sunk pool, which the
    slab would otherwise floor with sand."""
    L = context_layout(W, D)
    n = 0
    ground = [(-900, -900, W + 900, D + 900)]
    for h in holes:
        ground = rect_minus(ground, h)
    for k, (a, b, c, d) in enumerate(ground):
        box(F, cube, M["ctx_sand"], "ctx_ground" if len(ground) == 1 else f"ctx_ground_{k}",
            a, b, -0.32, c, d, -0.005); n += 1
    box(F, cube, M["ctx_pavement"], "ctx_pavement_N", -900, D, -0.005, W + 900, D + 2.0, 0.15); n += 1
    box(F, cube, M["ctx_asphalt"], "ctx_street_N", -900, D + 2.0, -0.10, W + 900, D + 14.0, 0.03); n += 1
    box(F, cube, M["ctx_pavement"], "ctx_pavement_far", -900, D + 14.0, -0.005, W + 900, D + 16.0, 0.15); n += 1
    plots = [(-W, 0.0), (W, 0.0), (0.0, D + 16.0), (W, D + 16.0), (-W, D + 16.0)]
    V = design()
    hooks = design_hooks(V)
    if hooks:
        # a design's street is a row of plots, as villa_blender.context
        plots += [(k * W, oy) for k in (-3, -2, 2, 3) for oy in (0.0, D + 16.0)]
    for i, (ox, oy) in enumerate(plots):
        far = oy > D
        box(F, cube, M["ctx_plaster"], f"ctx_wall_{i}", ox, oy, 0.0, ox + W, oy + 0.35, 2.4)
        box(F, cube, M["ctx_plaster"], f"ctx_wall_{i}b", ox, oy + D - 0.35, 0.0, ox + W, oy + D, 2.4)
        hy0 = oy + (L["far_y0"] if far else L["near_y0"])
        box(F, cube, M["ctx_plaster"], f"ctx_house_{i}", ox + L["side"], hy0, 0.0,
            ox + W - L["side"], hy0 + L["depth"], L["height"] - (i % 2) * 1.2)
        n += 3
    south = render_context(V).get("south") if hooks else None
    if south in ("golf", "lawn"):
        bands = (golf_bands(W, side=4 * W) if south == "golf"
                 else [("lawn", -4 * W, -GOLF_DEPTH_M, 5 * W, 0.0, 1)])
        for name, a, b, c, d, shade in bands:
            box(F, cube, M[f"ctx_golf{shade}"], f"ctx_golf_{name.replace(' ', '_')}", a, b, -0.02, c, d, 0.0)
            n += 1
    return n


# the golf course behind a design's rear boundary (villa_blender's numbers)
GOLF_ROUGH_M = 6.0
GOLF_FAIRWAY_M = 70.0
GOLF_DEPTH_M = 240.0
GOLF_STRIPE_M = 9.0
GOLF_SHADES = (0.60, 1.15, 0.90)   # x the design's lawn colour: rough, the two mowing stripes


def render_context(V):
    """The design's RENDER_CONTEXT hook ({'south': 'golf' | 'lawn'}), or {}."""
    rc = getattr(V, "RENDER_CONTEXT", None) if V is not None else None
    return dict(rc) if isinstance(rc, dict) else {}


def golf_bands(W, side=160.0):
    """villa_blender.golf_bands: (name, x0, y0, x1, y1, shade) bands south of
    the plot, metres; shade 0 rough, 1 / 2 the fairway's mowing stripes."""
    x0, x1 = -side, W + side
    bands = [("rough near", x0, -GOLF_ROUGH_M, x1, 0.0, 0)]
    y, k = -GOLF_ROUGH_M, 0
    while y > -(GOLF_ROUGH_M + GOLF_FAIRWAY_M) + 1e-6:
        y1 = max(y - GOLF_STRIPE_M, -(GOLF_ROUGH_M + GOLF_FAIRWAY_M))
        bands.append((f"fairway {k}", x0, y1, x1, y, 1 + k % 2))
        y, k = y1, k + 1
    bands.append(("rough far", x0, -GOLF_DEPTH_M, x1, y, 0))
    return bands


def palm_specs(V):
    """V.SITE_TREES as villa_blender's palms: (x, y, ground z, trunk height,
    lean x, lean y, crown diameter) in metres, the same seeded heights and
    leans (random.Random(1000 + i)), so both renderers plant the same garden."""
    out = []
    trees = (getattr(V, "SITE_TREES", None) or []) if V is not None else []
    ground = getattr(V, "ground_at", None) if V is not None else None
    for i, t in enumerate(trees):
        x, y, crown = t[:3]
        z = ground(y) if callable(ground) else getattr(V, "GARDEN_Z", 0.0)
        rng = random.Random(1000 + i)
        h = 4.6 + 2.2 * rng.random()
        lean = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25))
        out.append((x / 1000.0, y / 1000.0, z / 1000.0, h, lean[0], lean[1], crown / 1000.0))
    return out


def palms(F, cube, M, fronds=18):
    """The palms at SITE_TREES: villa_blender's own (villa_palms.glb beside
    the model -- the tapering trunks and the arching frond strips, their
    leaflets cut by the frond material), else the blade palms."""
    V = design()
    if not (design_hooks(V) and palm_specs(V)):
        return 0
    n = palms_from_glb(F, M, [(s[0], s[1]) for s in palm_specs(V)])
    return n if n else palms_blades(F, cube, M, fronds)


def palms_from_glb(F, M, at):
    """villa_palms.glb (villa_blender.export_palms), imported with the model
    (import_glb merges the two: one import, the same measured axis mapping,
    the nodes' transforms baked) and placed at the origin: a trunk in bark,
    a crown in the leaflet-cut frond, palm by palm alternating its green.
    Every trunk must stand within 1 m of a SITE_TREES point (`at`, model
    metres), else nothing is kept. Returns the crowns placed (0: no palm
    meshes, or they landed elsewhere)."""
    found = STATE.get("palm_meshes") or {}
    if not found or "ctx_leaf" not in M:
        return 0
    path = os.path.join(SIDECAR, "villa_palms.glb")
    crowns = trunks = 0
    placed, off = [], []
    for _key, a in sorted(found.items()):
        nm = a.get_name().lower()
        if "crown" in nm:
            digits = "".join(c if c.isdigit() else " " for c in nm).split()
            k = int(digits[0]) if digits else crowns
            mat = M["ctx_leaf"] if k % 2 else M["ctx_leaf_b"]
            crowns += 1
        elif "trunk" in nm:
            mat = M["ctx_bark"]
            trunks += 1
            bb = a.get_bounding_box()
            lo, hi = F.back(bb.min), F.back(bb.max)
            c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
            if min((math.hypot(c[0] - x, c[1] - y) for x, y in at), default=99.0) > 1.0:
                off.append(f"{a.get_name()} at ({c[0]:.1f}, {c[1]:.1f})")
        else:
            continue
        placed.append(mesh_actor(a, mat, f"ctx_{a.get_name()}", "Palms"))
    if off or trunks != len(at):
        warn(f"villa_palms.glb: {trunks} trunks for {len(at)} SITE_TREES"
             + (f"; not at a SITE_TREES point: {off[:4]}" if off else "") + " -- blade palms instead")
        for actor in placed:
            ACTORS.destroy_actor(actor)
        return 0
    log(f"palms: {crowns} crowns and {trunks} trunks from {path}")
    return crowns


def floor_finishes(F, cube, M):
    """villa_blender.floor_finishes: the travertine / oak / concrete floor of
    every room above grade (floor_plan), FLOOR_T on the slab."""
    V = design()
    if not design_hooks(V) or "floor_travertine" not in M:
        return 0
    n = 0
    for label, finish, x0, y0, x1, y1, z in floor_plan(V):
        box(F, cube, M[f"floor_{finish}"], "ctx_floor_" + "".join(
            c if c.isalnum() else "_" for c in label), x0, y0, z, x1, y1, z + FLOOR_T, folder="Floors")
        n += 1
    log(f"floor finishes: {n} boxes")
    return n


def palms_blades(F, cube, M, fronds=18):
    """A palm at every SITE_TREES point: a trunk of three stacked, leaning
    segments and a crown of arching fronds -- each two thin blades (engine
    cubes), the inner one rising off the crown, the outer one drooping, so
    the crown reads as a date palm's arch rather than a pinwheel."""
    V = design()
    specs = palm_specs(V) if design_hooks(V) else []
    if not specs:
        return 0
    cyl = EAL.load_asset("/Engine/BasicShapes/Cylinder")
    n = 0
    for i, (x, y, z, h, lx, ly, crown) in enumerate(specs):
        segs = 3
        for s in range(segs):
            t0, t1 = s / segs, (s + 1) / segs
            tm = (t0 + t1) / 2
            c = (x + lx * tm * tm, y + ly * tm * tm, z + h * tm)
            r = 0.24 - 0.07 * tm
            mesh_actor(cyl, M["ctx_bark"], f"ctx_palm_{i}_trunk_{s}", "Palms", loc=F.vec(c),
                       scale=F.size((2 * r, 2 * r, h / segs + 0.02)))
        top = (x + lx, y + ly, z + h)
        rng = random.Random(2000 + i)
        R = crown / 2.0
        for k in range(fronds):
            az = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / fronds
            rise = rng.uniform(5.0, 40.0)                     # young fronds stand up
            droop = rise - rng.uniform(40.0, 70.0)
            L = R * rng.uniform(1.0, 1.25)
            d = (math.cos(az), math.sin(az), 0.0)
            ue = F.vec(d, scale=1.0)
            yaw = math.degrees(math.atan2(ue.y, ue.x))
            roll = rng.uniform(-12.0, 12.0)
            mat = M["ctx_frond"] if k % 2 else M["ctx_frond_b"]
            start = top
            for s, (pitch, frac, width) in enumerate(((rise, 0.45, 0.16), (droop, 0.62, 0.12))):
                p = math.radians(pitch)
                seg = L * frac
                c = tuple(start[j] + d[j] * seg / 2 * math.cos(p) for j in range(2)) + (
                    start[2] + seg / 2 * math.sin(p),)
                mesh_actor(cube, mat, f"ctx_palm_{i}_frond_{k}_{s}", "Palms", loc=F.vec(c),
                           scale=unreal.Vector(seg + 0.02, width * L, 0.015),
                           rot=unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
                start = tuple(start[j] + d[j] * seg * math.cos(p) for j in range(2)) + (
                    start[2] + seg * math.sin(p),)
        n += 1
    log(f"palms: {n} at SITE_TREES")
    return n


def gate_leaves(F, cube, M, slat=0.045, pitch=0.09):
    """villa_blender.gate_leaves: a leaf of dark vertical slats in every gate
    V.gates() cuts from the street wall (render dressing, not in the model)."""
    V = design()
    if not (design_hooks(V) and callable(getattr(V, "gates", None))):
        return 0
    T = getattr(V, "BOUNDARY_T", 350.0)
    BH = getattr(V, "BOUNDARY_H", 2400.0)
    yc = (V.PLOT_D - T / 2) / 1000.0
    mat = M.get("grp:frames") or M["ctx_gate"]
    n = 0
    for gname, a, b, head in V.gates():
        x0, x1 = min(a, b) / 1000.0 + 0.02, max(a, b) / 1000.0 - 0.02
        z0, z1 = 0.04, (BH if head is None else min(head, BH)) / 1000.0 - 0.02
        tag = gname.lower().replace(" ", "_")
        box(F, cube, mat, f"ctx_{tag}_rail_b", x0, yc - 0.03, z0, x1, yc + 0.03, z0 + 0.06, folder="Gates")
        box(F, cube, mat, f"ctx_{tag}_rail_t", x0, yc - 0.03, z1 - 0.06, x1, yc + 0.03, z1, folder="Gates")
        k = int((x1 - x0 - slat) // pitch)
        off = (x1 - x0 - slat - k * pitch) / 2
        for i in range(k + 1):
            sx = x0 + off + i * pitch
            box(F, cube, mat, f"ctx_{tag}_slat_{i:02d}", sx, yc - slat / 2, z0, sx + slat,
                yc + slat / 2, z1, folder="Gates")
        n += 1
    log(f"gates: {n} slatted leaves")
    return n


def shrubs(F, sphere, M, spacing=0.45, density=2.2, seed=7):
    """Low shrubs scattered over the TOP faces of the planting beds (as the
    Blender render does): Poisson-disc darts, area-weighted, fixed seed.
    None for a design whose planting is a clipped hedge: the hedge IS the
    planting (villa_blender dresses it with leaf cards, no shrubs), and
    shrubs on the bed rims at its foot read as black boulders in its shade."""
    V = design()
    if V is not None and (getattr(V, "MATERIALS", None) or {}).get("planting", {}).get("kind") == "hedge":
        log("shrubs: none -- the design's planting is a clipped hedge")
        return 0
    tris = []
    for a, b, c in glb_triangles(GLB, "planting"):
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        area2 = math.sqrt(nx * nx + ny * ny + nz * nz)
        if area2 > 1e-9 and abs(nz) / area2 > 0.9:
            tris.append((area2 / 2, a, b, c))
    if not tris:
        warn("no up-facing planting triangles: no shrubs")
        return 0
    total = sum(t[0] for t in tris)
    rng = random.Random(seed)
    cum, acc = [], 0.0
    for t in tris:
        acc += t[0]
        cum.append(acc)
    grid, pts = {}, []
    import bisect
    for _ in range(int(total * density * 3)):
        if len(pts) >= int(total * density):
            break
        a_, a, b, c = tris[min(bisect.bisect(cum, rng.random() * total), len(tris) - 1)]
        r1, r2 = rng.random(), rng.random()
        if r1 + r2 > 1:
            r1, r2 = 1 - r1, 1 - r2
        p = tuple(a[k] + r1 * (b[k] - a[k]) + r2 * (c[k] - a[k]) for k in range(3))
        gx, gy = int(p[0] // spacing), int(p[1] // spacing)
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < spacing
               for i in (-1, 0, 1) for j in (-1, 0, 1) for q in grid.get((gx + i, gy + j), [])):
            continue
        grid.setdefault((gx, gy), []).append(p)
        pts.append(p)
    # a shrub never pokes through a wall: its radius is capped by the clearance
    # to the boundary walls, the house and the hard landscape around it
    solid = [t for g in SOLID_GROUPS for t in glb_triangles(GLB, g)]
    n = 0
    for p in pts:
        r = rng.uniform(0.22, 0.55)
        yaw, squash, mat = rng.uniform(0, 360), rng.uniform(0.75, 0.95), M[f"shrub{rng.randrange(3)}"]
        q = (p[0], p[1], p[2] + 0.15)
        clear = [axis_ray(solid, q, axis, sign) for axis in (0, 1) for sign in (1, -1)]
        r = min([r] + [0.95 * d for d in clear if d is not None])
        if r < 0.15:
            continue
        s = r / 0.5                                      # engine sphere: 100 cm across
        mesh_actor(sphere, mat, f"shrub_{n:03d}", "Planting", loc=F.vec(p),
                   scale=unreal.Vector(s, s, s * squash), rot=unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        n += 1
    log(f"shrubs: {n} on {total:.0f} m2 of bed ({len(pts) - n} dropped: no room beside a wall)")
    return n


# ------------------------------------------------------------------ interior
def load_design():
    """villa_design.py (data only at import: its shapely imports live inside
    functions). No .pyc is written into the project."""
    import importlib.util
    import sys
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("villa_design_for_unreal", DESIGN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def room_fit(side, cx, cy, fl, hw, hd, tol=0.8):
    """'' when the glb has this room: from its centre, 1.2 m above the floor,
    at least three of the four sides meet a wall within `tol` of where the
    design puts it (the fourth may be a doorway or an open plan), and no wall
    stands inside it. Otherwise the reason."""
    ok, sides = 0, []
    for axis, sign, half in ((0, 1, hw), (0, -1, hw), (1, 1, hd), (1, -1, hd)):
        d = axis_ray(side, (cx, cy, fl + 1.2), axis, sign)
        tag = f"{'xy'[axis]}{'+' if sign > 0 else '-'}"
        if d is not None and d < half - tol:
            return f"a wall {d:.2f} m from its centre ({tag}), the design has {half:.2f}"
        if d is not None and d <= half + tol:
            ok += 1
        else:
            sides.append(tag)
    return "" if ok >= 3 else f"open on {', '.join(sides)}"


# ---- the room test for a design with render hooks (the villa keeps room_fit)
PROBE_MARGIN = 0.30         # m a probe keeps from a nested room or a void


def design_hooks(V):
    """True for a design with render hooks (RENDER_VIEWS / MATERIALS)."""
    return bool(V is not None and (getattr(V, "RENDER_VIEWS", None) or getattr(V, "MATERIALS", None)))


def _rect_m(r):
    x0, y0, x1, y1 = r
    return (min(x0, x1) / 1000.0, min(y0, y1) / 1000.0, max(x0, x1) / 1000.0, max(y0, y1) / 1000.0)


def room_layout(V, room):
    """What the room test must know about one room of a design, metres:
      rect      its rectangle
      kids      its nested rooms (V.children: an en-suite, a dressing), each
                grown by the partition round it -- their walls stand INSIDE
                the room by design
      voids     the design's VOIDS on this floor inside it (no floor there)
      openings  (axis, wall t0, t1, span a, b): every door / open / slide of
                this room -- a ray through one of them is 'open by design'."""
    name, fl = room[0], room[6]
    rect = _rect_m(room[1:5])
    part = float(getattr(V, "PART", 150.0)) / 1000.0
    kids = []
    for q in V.ROOMS:
        if q[6] != fl or q[0] == name:
            continue
        k = _rect_m(q[1:5])
        if k[0] >= rect[0] - 1e-6 and k[1] >= rect[1] - 1e-6 and k[2] <= rect[2] + 1e-6 \
                and k[3] <= rect[3] + 1e-6:
            kids.append((k[0] - part, k[1] - part, k[2] + part, k[3] + part))
    voids = []
    for v in getattr(V, "VOIDS", None) or []:
        if fl in tuple(v[5]):
            r = _rect_m(v[1:5])
            if r[0] < rect[2] and r[2] > rect[0] and r[1] < rect[3] and r[3] > rect[1]:
                voids.append(r)
    openings = []
    for o in getattr(V, "OPENINGS", None) or []:
        if o[0] == fl and o[1] != "window" and name in (o[7], o[8]):
            openings.append((o[2], min(o[3], o[4]) / 1000.0, max(o[3], o[4]) / 1000.0,
                             min(o[5], o[6]) / 1000.0, max(o[5], o[6]) / 1000.0))
    return {"rect": rect, "kids": kids, "voids": voids, "openings": openings}


def _rect_dist(p, r):
    """Signed distance from p to rectangle r: + outside, - inside."""
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    if dx or dy:
        return math.hypot(dx, dy)
    return -min(p[0] - r[0], r[2] - p[0], p[1] - r[1], r[3] - p[1])


def probe_point(lay, step=0.25, margin=PROBE_MARGIN):
    """Where to test (and light) a room: its centre, unless the centre is
    within `margin` of a nested room or over a void -- then the point of a
    `step` grid that stands farthest from them and from the room's own walls.
    Returns (x, y, clearance m)."""
    x0, y0, x1, y1 = lay["rect"]
    blocks = lay["kids"] + lay["voids"]

    def score(p):
        s = min(p[0] - x0, x1 - p[0], p[1] - y0, y1 - p[1])
        return min([s] + [_rect_dist(p, b) for b in blocks])

    c = ((x0 + x1) / 2, (y0 + y1) / 2)
    if all(_rect_dist(c, b) >= margin for b in blocks):
        return c[0], c[1], score(c)
    best, key = None, None
    nx, ny = max(1, int((x1 - x0) / step)), max(1, int((y1 - y0) / step))
    for i in range(nx + 1):
        for j in range(ny + 1):
            p = (x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny)
            s = score(p)
            k = (round(s, 3), -math.hypot(p[0] - c[0], p[1] - c[1]))   # ties: nearest the centre
            if key is None or k > key:
                best, key = (p[0], p[1], s), k
    return best


def room_fit_design(ray, lay, p, fl, tol=0.8):
    """room_fit for a design with render hooks: from probe point p, 1.2 m
    above the floor, each of the four rays must meet a wall where the design
    has one -- the room's own wall, or the partition of a nested room across
    the ray (an en-suite's wall is not 'a wall inside the room') -- or pass
    through one of the room's openings (a door, an open plan, a slide).
    At least two walls and three sides accounted for; a wall nearer than any
    the design has is a reason. `ray(point, axis, sign)` -> distance or None.
    Returns '' or the reason."""
    x0, y0, x1, y1 = lay["rect"]
    walls, opened, sides = 0, 0, []
    for axis, sign in ((0, 1), (0, -1), (1, 1), (1, -1)):
        tag = f"{'xy'[axis]}{'+' if sign > 0 else '-'}"
        u = p[axis]                                   # along the ray
        w = p[1 - axis]                               # across it
        lo, hi = (x0, x1) if axis == 0 else (y0, y1)
        edge = (hi - u) if sign > 0 else (u - lo)
        expect = [edge]
        for k in lay["kids"]:
            klo, khi = (k[0], k[2]) if axis == 0 else (k[1], k[3])
            wlo, whi = (k[1], k[3]) if axis == 0 else (k[0], k[2])
            if not (wlo <= w <= whi):
                continue
            for face in (klo, khi):
                d = (face - u) * sign
                if d > 1e-3:
                    expect.append(d)
        d = ray((p[0], p[1], fl + 1.2), axis, sign)
        first = min(expect)
        if d is not None and d < first - tol:
            return f"a wall {d:.2f} m from the probe ({tag}), the design has {first:.2f}"
        if d is not None and any(abs(d - e) <= tol for e in expect):
            walls += 1
            continue
        # through an opening of this room on a wall across this ray?
        wall_axis = "v" if axis == 0 else "h"
        through = False
        for ax, t0, t1, a, b in lay["openings"]:
            if ax != wall_axis or not (a - 0.05 <= w <= b + 0.05):
                continue
            mid = (t0 + t1) / 2
            if (mid - u) * sign > 0 and (mid - u) * sign <= max(expect) + tol:
                through = True
                break
        if through:
            opened += 1
        else:
            sides.append(tag)
    if walls >= 2 and walls + opened >= 3:
        return ""
    return f"open on {', '.join(sides)}" if sides else f"only {walls} walls found"


def interior_lights_design(F, V, side, vert, level, ceil):
    """interior_lights for a design with render hooks: probe_point /
    room_fit_design (nested rooms, voids and openings are the design's), the
    light at the probe, the rejected rooms listed with their reasons."""
    placed, rejected = [], []
    for r in V.ROOMS:
        name, _x0, _y0, _x1, _y1, _kind, floor = r[:7]
        if floor not in level or floor not in ceil:
            rejected.append(f"{name} ({floor}): unknown level")
            continue
        lay = room_layout(V, r)
        px, py, clear = probe_point(lay)
        x0, y0, x1, y1 = lay["rect"]
        fl, ch = level[floor] / 1000.0, ceil[floor] / 1000.0
        why = room_fit_design(lambda q, a, s: axis_ray(side, q, a, s), lay, (px, py), fl)
        up = None
        if not why:
            down = axis_ray(vert, (px, py, fl + 0.5), 2, -1)
            if down is None or abs(down - 0.5) > 0.6:
                why = "no floor at the design level"
        if not why:
            up = axis_ray(vert, (px, py, fl + 0.5), 2, 1)
            if up is None or up > 2 * ch + 1.5:
                why = "no ceiling"
        if why:
            rejected.append(f"{name} ({floor}): {why}")
            continue
        hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
        if (px, py) != ((x0 + x1) / 2, (y0 + y1) / 2):       # moved off a nested room / void
            hw = hd = max(0.3, min(hw, hd, clear))
        _room_light(F, name, (px, py, fl + 0.5 + up - 0.03), hw, hd, ch)
        placed.append(name)
    if rejected:
        warn(f"interior lights: {len(rejected)} of {len(V.ROOMS)} rooms get no light -- "
             f"the room test did not find them in the glb as the design has them: "
             + "; ".join(rejected))
    log(f"interior lights: {len(placed)} placed ({INTERIOR_LUX:.0f} lux, 3000 K)")
    return {"placed": len(placed), "rooms": placed, "rejected": rejected, "lux": INTERIOR_LUX,
            "test": "design (nested rooms, voids, openings)"}


def _room_light(F, name, at, hw, hd, ch):
    """One warm rectangular ceiling light, as interior_lights places them."""
    ext = F.size((2 * hw, 2 * hd, 0.0))
    area = 4 * hw * hd
    light = spawn(unreal.RectLight, F.vec(at), unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0),
                  label=f"light_{name.replace(' ', '_').replace(chr(39), '')}", folder="Interior")
    c = light.get_components_by_class(unreal.RectLightComponent)[0]
    # Its intensity is keyed per camera cut (light_keys). The actor's own
    # mobility (stationary) allows that in the -game render; MOVABLE does
    # too, but 45 movable lights made every -game tick ~8 s (dynamic
    # shadows in the game viewport): a 64-spp view took 10 minutes.
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", INTERIOR_LUX * area / 0.6)
    c.set_editor_property("source_height", min(0.6 * ext.x * 100.0, 400.0))   # local Z = world X
    c.set_editor_property("source_width", min(0.6 * ext.y * 100.0, 400.0))    # local Y = world Y
    c.set_editor_property("use_temperature", True)
    c.set_editor_property("temperature", 3000.0)
    c.set_editor_property("attenuation_radius", 100.0 * (2 * max(hw, hd) + ch + 2.0))
    STATE.setdefault("lights", []).append((c, INTERIOR_LUX * area / 0.6))


def interior_lights(F):
    """A warm ceiling light in every room of villa_design.ROOMS, as the Blender
    render has -- but only where the glb really has that room (room_fit: its
    walls where the design puts them, a floor at the design level, a ceiling
    above). A room the model does not have (a stale export, a design change)
    gets no light, and the status lists it."""
    if INTERIOR_LUX <= 0:
        return {"placed": 0, "note": "interior lights off"}
    if not os.path.exists(DESIGN):
        warn(f"no {DESIGN}: no interior lights")
        return {"placed": 0, "note": "no villa_design.py"}
    V = design()
    if V is None:
        return {"placed": 0, "note": f"{DESIGN} did not load"}
    level = getattr(V, "LEVEL", None) or {"GF": V.GF, "FF": V.FF}
    ceil = getattr(V, "CEIL", None) or {"GF": V.GF_CH, "FF": V.FF_CH}
    side = [t for g in SIDE_GROUPS for t in glb_triangles(GLB, g)]
    vert = [t for g in VERT_GROUPS for t in glb_triangles(GLB, g)]
    if design_hooks(V):
        return interior_lights_design(F, V, side, vert, level, ceil)
    placed, rejected = [], []
    for r in V.ROOMS:
        name, x0, y0, x1, y1, _kind, floor = r[:7]
        if floor not in level or floor not in ceil:
            rejected.append(f"{name} ({floor}): unknown level")
            continue
        cx, cy = (x0 + x1) / 2000.0, (y0 + y1) / 2000.0
        hw, hd = abs(x1 - x0) / 2000.0, abs(y1 - y0) / 2000.0
        fl, ch = level[floor] / 1000.0, ceil[floor] / 1000.0
        why = room_fit(side, cx, cy, fl, hw, hd)
        down = up = None
        if not why:
            down = axis_ray(vert, (cx, cy, fl + 0.5), 2, -1)
            if down is None or abs(down - 0.5) > 0.6:
                why = "no floor at the design level"
        if not why:
            up = axis_ray(vert, (cx, cy, fl + 0.5), 2, 1)
            if up is None or up > 2 * ch + 1.5:
                why = "no ceiling"
        if why:
            rejected.append(f"{name} ({floor}): {why}")
            continue
        z = fl + 0.5 + up - 0.03
        ext = F.size((2 * hw, 2 * hd, 0.0))
        area = 4 * hw * hd
        light = spawn(unreal.RectLight, F.vec((cx, cy, z)), unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0),
                      label=f"light_{name.replace(' ', '_').replace(chr(39), '')}", folder="Interior")
        c = light.get_components_by_class(unreal.RectLightComponent)[0]
        c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
        c.set_editor_property("intensity", INTERIOR_LUX * area / 0.6)
        c.set_editor_property("source_height", min(0.6 * ext.x * 100.0, 400.0))   # local Z = world X
        c.set_editor_property("source_width", min(0.6 * ext.y * 100.0, 400.0))    # local Y = world Y
        c.set_editor_property("use_temperature", True)
        c.set_editor_property("temperature", 3000.0)
        c.set_editor_property("attenuation_radius", 100.0 * (2 * max(hw, hd) + ch + 2.0))
        placed.append(name)
    if rejected:
        warn(f"interior lights: {len(rejected)} of {len(V.ROOMS)} rooms not found in the glb "
             f"(export older than villa_design.py?): " + "; ".join(rejected))
    log(f"interior lights: {len(placed)} placed ({INTERIOR_LUX:.0f} lux, 3000 K)")
    return {"placed": len(placed), "rooms": placed, "rejected": rejected, "lux": INTERIOR_LUX}


# ------------------------------------------------------------------ sun
def sun_truth(year, month, day, clock):
    h = int(clock)
    mnt = int(round((clock - h) * 60))
    sp = unreal.SunPositionFunctionLibrary.get_sun_position(
        SITE["latitude"], SITE["longitude"], SITE["timezone"], False, year, month, day, h, mnt, 0)
    # SunPosition reports elevation + 180 (Unreal pitch convention)
    return sp.azimuth, sp.corrected_elevation - 180.0


def clear_sky(sky):
    """No volumetric clouds (the path tracer only sees them through the sky
    light's capture, as soft blobs), and more Mie scattering than the default
    Earth atmosphere: a Dubai sky is clear but dusty, paler than a deep blue."""
    for comp in sky.get_components_by_class(unreal.VolumetricCloudComponent):
        comp.set_editor_property("visible", False)
        comp.set_editor_property("hidden_in_game", True)
    for comp in sky.get_components_by_class(unreal.SkyAtmosphereComponent):
        try:
            comp.set_editor_property("mie_scattering_scale", 0.003996 * HAZE)
        except Exception as e:
            warn(f"sky haze: {e}")


def refresh_sky(sky):
    """set_editor_property already re-runs the construction script (it posts
    PostEditChangeProperty); UpdateSun is the SunSky's own refresh, if callable."""
    try:
        sky.call_method("UpdateSun")
    except Exception:
        pass


def sun_measure(F, sky):
    """Compass azimuth / elevation of the sun the SunSky actor actually casts,
    read from its DirectionalLight and taken back into model space."""
    refresh_sky(sky)
    lights = sky.get_components_by_class(unreal.DirectionalLightComponent)
    f = lights[0].get_forward_vector()                # direction the light travels
    s = F.back(unreal.Vector(-f.x, -f.y, -f.z), scale=1.0)
    az = math.degrees(math.atan2(s[0], s[1])) % 360.0  # clockwise from north (+Y)
    el = math.degrees(math.asin(max(-1.0, min(1.0, s[2]))))
    return az, el


def set_sun(sky, month, day, clock):
    sky.set_editor_property("Month", int(month))
    sky.set_editor_property("Day", int(day))
    sky.set_editor_property("SolarTime", float(clock))


def sunsky(F):
    cls = EAL.load_blueprint_class("/SunPosition/SunSky")
    sky = spawn(cls, label="SunSky_Dubai", folder="Lighting")
    sky.set_editor_property("Latitude", SITE["latitude"])
    sky.set_editor_property("Longitude", SITE["longitude"])
    sky.set_editor_property("TimeZone", SITE["timezone"])
    sky.set_editor_property("UseDaylightSavingTime", False)
    north = F.vec((0.0, 1.0, 0.0), scale=1.0)          # model +Y in Unreal
    offset = math.degrees(math.atan2(north.y, north.x))
    year = int(sky.get_editor_property("Year"))
    # SunSky puts the sun at Unreal yaw = azimuth + NorthOffset; check it, both signs
    probe = (12, 15, 15.5)
    want = sun_truth(year, *probe)
    chosen = None
    for cand in (offset, -offset):
        sky.set_editor_property("NorthOffset", cand)
        set_sun(sky, *probe)
        got = sun_measure(F, sky)
        d_az = abs((got[0] - want[0] + 180.0) % 360.0 - 180.0)
        if d_az < 1.0 and abs(got[1] - want[1]) < 1.0:
            chosen = cand
            break
    if chosen is None:
        raise RuntimeError(f"SunSky north check failed: want az/el {want}, got {got} (offset {offset})")
    for comp in sky.get_components_by_class(unreal.DirectionalLightComponent):
        comp.set_editor_property("intensity", 120000.0)       # lux at the top of the atmosphere
    clear_sky(sky)
    log(f"SunSky: north offset {chosen:.1f} deg (model +Y = north), year {year}")
    return sky, chosen, year


# ------------------------------------------------------------------ cameras
def camera(F, name, v, aspect):
    eye, tgt = F.vec(v["eye"]), F.vec(v["target"])
    d = tgt - eye
    horiz = math.hypot(d.x, d.y)
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, horiz))
    lens = v["lens"]
    sensor_w = 36.0
    sensor_h = sensor_w / aspect
    shift = 0.0
    if v.get("level"):
        # two-point perspective: keep the camera level (verticals stay
        # vertical) and shift the filmback so the target stays centred
        shift = lens * math.tan(math.radians(pitch))
        pitch = 0.0
    cam = spawn(unreal.CineCameraActor, eye, unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw),
                label=f"CAM_{name}", folder="Cameras")
    c = cam.get_cine_camera_component()
    fb = c.get_editor_property("filmback")
    fb.set_editor_property("sensor_width", sensor_w)
    fb.set_editor_property("sensor_height", sensor_h)
    fb.set_editor_property("sensor_vertical_offset", shift)
    c.set_editor_property("filmback", fb)
    c.set_editor_property("current_focal_length", lens)
    c.set_editor_property("current_aperture", 8.0)
    fs = c.get_editor_property("focus_settings")
    fs.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    c.set_editor_property("focus_settings", fs)
    c.set_editor_property("constrain_aspect_ratio", False)
    pp = c.get_editor_property("post_process_settings")
    pp.set_editor_property("override_auto_exposure_method", True)
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("override_auto_exposure_apply_physical_camera_exposure", True)
    pp.set_editor_property("auto_exposure_apply_physical_camera_exposure", False)
    pp.set_editor_property("override_auto_exposure_bias", True)
    pp.set_editor_property("auto_exposure_bias", -float(v["ev"]))
    pp.set_editor_property("override_white_temp", True)
    pp.set_editor_property("white_temp", float(v.get("wb", 6500)))
    c.set_editor_property("post_process_settings", pp)
    c.set_editor_property("post_process_blend_weight", 1.0)
    return cam, {"eye_cm": [round(eye.x, 1), round(eye.y, 1), round(eye.z, 1)],
                 "yaw": round(yaw, 2), "pitch": round(pitch, 2), "lens_mm": lens,
                 "sensor_mm": [sensor_w, round(sensor_h, 3)], "shift_mm": round(shift, 3),
                 "ev100": v["ev"]}


def post_volume(ev):
    ppv = spawn(unreal.PostProcessVolume, label="PPV_Global", folder="Lighting")
    ppv.set_editor_property("unbound", True)
    s = ppv.get_editor_property("settings")
    for k, v in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                 ("auto_exposure_apply_physical_camera_exposure", False),
                 ("auto_exposure_bias", -ev),
                 ("path_tracing_max_bounces", 16),
                 ("path_tracing_enable_denoiser", True),
                 ("path_tracing_max_path_intensity", 24.0),
                 ("vignette_intensity", 0.25)):
        try:
            s.set_editor_property("override_" + k, True)
        except Exception:
            pass
        s.set_editor_property(k, v)
    ppv.set_editor_property("settings", s)
    return ppv


# ------------------------------------------------------------------ sequence + MRQ
def sequence(cams, sky, views, VIEWS=VIEWS):
    ensure_dir(RENDER)
    path = f"{RENDER}/{SEQ_NAME}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = AT.create_asset(SEQ_NAME, RENDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(24, 1))
    n = len(views)
    seq.set_playback_start(0)
    seq.set_playback_end(n)
    cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
    for i, name in enumerate(views):
        b = seq.add_possessable(cams[name])
        sec = cut.add_section()
        sec.set_range(i, i + 1)
        sec.set_camera_binding_id(seq.get_binding_id(b))
    sb = seq.add_possessable(sky)
    for prop, cls, values in (
            ("SolarTime", unreal.MovieSceneFloatTrack, [VIEWS[v]["clock"] for v in views]),
            ("Month", unreal.MovieSceneIntegerTrack, [VIEWS[v]["date"][0] for v in views]),
            ("Day", unreal.MovieSceneIntegerTrack, [VIEWS[v]["date"][1] for v in views])):
        tr = sb.add_track(cls)
        tr.set_property_name_and_path(prop, prop)
        sec = tr.add_section()
        sec.set_start_frame_bounded(False)
        sec.set_end_frame_bounded(False)
        ch = sec.get_all_channels()[0]
        for i, val in enumerate(values):
            if cls is unreal.MovieSceneFloatTrack:
                ch.add_key(unreal.FrameNumber(i), float(val),
                           interpolation=unreal.MovieSceneKeyInterpolation.CONSTANT)
            else:
                ch.add_key(unreal.FrameNumber(i), int(val))
    STATE["light_keys"] = light_keys(seq, views, VIEWS)
    EAL.save_loaded_asset(seq)
    return seq


def light_keys(seq, views, VIEWS):
    """A design's interior camera cut sees the room lights turned down (its
    view's 'lights' scale -- villa_blender's INTERIOR_LIGHTS): the intensity
    of every light _room_light placed, keyed per frame. The villa's views
    carry no scale and nothing is keyed. Returns the lights keyed."""
    scales = [float(VIEWS[v].get("lights", 1.0)) for v in views]
    lights = STATE.get("lights", [])
    if not lights or all(abs(s - 1.0) < 1e-9 for s in scales):
        return 0
    for comp, base in lights:
        b = seq.add_possessable(comp)            # a child of its actor's binding
        tr = b.add_track(unreal.MovieSceneFloatTrack)
        tr.set_property_name_and_path("Intensity", "Intensity")
        sec = tr.add_section()
        sec.set_start_frame_bounded(False)
        sec.set_end_frame_bounded(False)
        ch = sec.get_all_channels()[0]
        for i, s in enumerate(scales):
            ch.add_key(unreal.FrameNumber(i), float(base * s),
                       interpolation=unreal.MovieSceneKeyInterpolation.CONSTANT)
    try:
        mob = lights[0][0].get_editor_property("mobility")
    except Exception:
        mob = "?"
    log(f"room lights keyed per cut: {len(lights)} lights ({mob}), scales {scales}")
    return len(lights)


def movie_queue(seq):
    """One MRQ job: the path tracer, SAMPLES spp per view, PNG out."""
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    queue.delete_all_jobs()
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.set_editor_property("job_name", "villa")
    job.set_editor_property("sequence", unreal.SoftObjectPath(seq.get_path_name()))
    job.set_editor_property("map", unreal.SoftObjectPath(f"{MAP}.Villa"))
    cfg = job.get_configuration()
    for s in list(cfg.get_all_settings()):
        cfg.remove_setting(s)
    out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out.set_editor_property("output_directory", unreal.DirectoryPath(FRAMES.replace("\\", "/")))
    out.set_editor_property("file_name_format", "villa_{frame_number}")
    out.set_editor_property("output_resolution", unreal.IntPoint(RES[0], RES[1]))
    out.set_editor_property("override_existing_output", True)
    out.set_editor_property("zero_pad_frame_numbers", 4)
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.set_editor_property("spatial_sample_count", SAMPLES)
    aa.set_editor_property("temporal_sample_count", 1)
    aa.set_editor_property("override_anti_aliasing", True)
    aa.set_editor_property("anti_aliasing_method", unreal.AntiAliasingMethod.AAM_NONE)
    aa.set_editor_property("use_camera_cut_for_warm_up", False)
    aa.set_editor_property("engine_warm_up_count", 16)
    aa.set_editor_property("render_warm_up_frames", True)
    aa.set_editor_property("render_warm_up_count", 8)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPass_PathTracer)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    go = cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
    go.set_editor_property("cinematic_quality_settings", True)
    try:
        go.set_editor_property("texture_streaming", unreal.MoviePipelineTextureStreamingMethod.FULLY_LOAD)
    except Exception as e:
        warn(f"texture streaming override: {e}")
    cv = cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    cv.set_editor_property("start_console_commands", [
        "r.RayTracing.Culling 0",
        "r.PathTracing.ProgressDisplay 0",
    ])
    try:
        unreal.MoviePipelineEditorLibrary.export_config_to_asset(cfg, RENDER, "MRQ_VillaPathTracer", True)
    except Exception as e:
        warn(f"preset export: {e}")
    # The -game render loads the queue from this manifest. The loader only
    # accepts it under the project's Saved folder, as a path relative to it
    # (that is what MRQ's own "Render (Remote)" executor passes).
    full = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                        "MovieRenderPipeline", "QueueManifest.utxt")
    # MRQ always writes QueueManifest.utxt -- the VILLA's queue. A project's
    # build keeps what was there and puts it back after taking its own copy,
    # so a later villa `-Stage render` never renders the project's sequence.
    villa_queue = None
    if MANIFEST != "QueueManifest.utxt" and os.path.exists(full):
        with open(full, "rb") as f_in:
            villa_queue = f_in.read()
    t0 = time.time()
    res = unreal.MoviePipelineEditorLibrary.save_queue_to_manifest_file(queue)
    if not os.path.exists(full) or os.path.getmtime(full) < t0 - 1:
        raise RuntimeError(f"MRQ manifest not written ({res})")
    # a copy beside the build status, for the record
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    with open(full, "rb") as f_in, open(os.path.join(os.path.dirname(STATUS), "QueueManifest.utxt"), "wb") as f_out:
        f_out.write(f_in.read())
    if MANIFEST != "QueueManifest.utxt":
        # a project's queue under its own name, so a later villa build (which
        # rewrites QueueManifest.utxt) cannot change what this one renders
        with open(full, "rb") as f_in, open(os.path.join(os.path.dirname(full), MANIFEST), "wb") as f_out:
            f_out.write(f_in.read())
        if villa_queue is not None:
            with open(full, "wb") as f_out:
                f_out.write(villa_queue)
        else:
            os.remove(full)                  # no villa queue before: leave none
    return "MovieRenderPipeline/" + MANIFEST


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    VIEWS = all_views()                      # the design's RENDER_VIEWS, or the villa's
    if not VIEW_NAMES:
        VIEW_NAMES[:] = list(VIEWS) if VIEWS is not globals()["VIEWS"] else \
            ["aerial_sw", "garden", "street"]
    for v in VIEW_NAMES:
        if v not in VIEWS:
            raise ValueError(f"unknown view {v}; known: {sorted(VIEWS)}")
    if not os.path.exists(GLB):
        raise FileNotFoundError(GLB)
    if PROJECT and os.path.normcase(os.path.abspath(GLB)).startswith(
            os.path.normcase(DESKTOP_VILLA) + os.sep):
        # a project must never be built from (and render over) the villa's model
        raise RuntimeError(f"the project {PROJECT} would use the villa's model {GLB}; "
                           f"set VILLA_OUT to the project's deliverables")
    aspect = RES[0] / RES[1]
    log(f"glb {GLB}  design {DESIGN}  root {ROOT}  views {VIEW_NAMES}  "
        f"{RES[0]}x{RES[1]} @ {SAMPLES} spp")

    # 1. fresh level (render_unreal.ps1 also deletes these folders before launch)
    for p in (MAP, MODEL, RENDER, MATP, ROOT + "/Pipelines"):
        wipe(p)
    unreal.SystemLibrary.collect_garbage()
    ensure_dir(ROOT + "/Maps")
    if not LEVELS.new_level(MAP):
        raise RuntimeError(f"new_level {MAP} failed")

    # 2. model
    meshes = import_glb()
    groups = json.load(open(GROUPS)) if GROUPS and os.path.exists(GROUPS) else {}
    check = {}
    if groups:
        F, err, n = measure_frame(meshes, groups)
        check = {"mapping": repr(F), "max_error_cm": round(err, 2), "groups_compared": n}
        log(f"frame {F}: {n} groups, worst bound off by {err:.2f} cm")
        if err > 50.0:
            raise RuntimeError(f"imported meshes do not match groups.json (best {F}, {err:.1f} cm)")
        if err > 2.0:
            warn(f"groups.json and the glb disagree by {err:.1f} cm -- stale export?")
        missing = sorted(set(groups) - set(meshes))
        if missing:
            warn(f"groups in groups.json but not in the glb: {missing}")
    else:
        F = Frame()
        warn("no groups.json: assuming " + repr(F))
    if F.mirrored():
        raise RuntimeError(f"the import mirrored the model ({F})")

    M = build_materials()
    Vd = design()
    for key, sm in sorted(meshes.items()):
        mat = M.get("grp:" + key) or M.get(ASSIGN.get(key, "")) or on_demand(M, ASSIGN.get(key, ""))
        if mat is None:
            warn(f"no material for mesh {key}")
        a = mesh_actor(sm, mat, f"villa_{key}", "Villa")
        if key == "pool" and "grp:mosaic" in M:
            # the tank below the coping (villa_blender's second material slot)
            try:
                c = a.static_mesh_component
                for i, s in enumerate(sm.get_editor_property("static_materials")):
                    if "mosaic" in str(s.get_editor_property("material_slot_name")).lower():
                        c.set_material(i, M["grp:mosaic"])
            except Exception as e:
                warn(f"pool lining: {e}")
    # plot size from the boundary walls, measured in Unreal and taken back to model metres
    bb = meshes["boundary"].get_bounding_box() if "boundary" in meshes else None
    if bb:
        a, b = F.back(bb.min), F.back(bb.max)
        W, D = abs(b[0] - a[0]), abs(b[1] - a[1])
    elif Vd is not None and getattr(Vd, "PLOT_W", None) and getattr(Vd, "PLOT_D", None):
        W, D = Vd.PLOT_W / 1000.0, Vd.PLOT_D / 1000.0
        warn(f"no boundary mesh: plot {W} x {D} m from the design")
    else:
        W, D = 24.0, 29.0
        warn("no boundary mesh: plot assumed 24 x 29 m")
    cube = EAL.load_asset("/Engine/BasicShapes/Cube")
    sphere = EAL.load_asset("/Engine/BasicShapes/Sphere")
    holes = []
    if Vd is not None and getattr(Vd, "RENDER_VIEWS", None) and groups.get("pool"):
        g = groups["pool"]                   # mm, from groups.json
        holes.append((g[0] / 1000.0, g[1] / 1000.0, g[3] / 1000.0, g[4] / 1000.0))
    n_ctx = context(F, cube, M, W, D, holes)
    n_shrubs = shrubs(F, sphere, M)
    dressing = {}
    if design_hooks(Vd):                     # a design's palms and gate leaves, as Blender's
        dressing = {"palms": palms(F, cube, M), "gates": gate_leaves(F, cube, M),
                    "floors": floor_finishes(F, cube, M)}
    interior = interior_lights(F)

    # 3. light
    sky, north_offset, year = sunsky(F)
    suns = {}
    for name in VIEW_NAMES:
        v = VIEWS[name]
        set_sun(sky, v["date"][0], v["date"][1], v["clock"])
        got = sun_measure(F, sky)
        want = sun_truth(year, v["date"][0], v["date"][1], v["clock"])
        suns[name] = {"azimuth": round(got[0], 2), "elevation": round(got[1], 2),
                      "expected": [round(want[0], 2), round(want[1], 2)]}
        log(f"sun {name}: az {got[0]:.1f} el {got[1]:.1f} (SunPosition {want[0]:.1f} / {want[1]:.1f})")
    first = VIEWS[VIEW_NAMES[0]]
    set_sun(sky, first["date"][0], first["date"][1], first["clock"])
    refresh_sky(sky)
    clear_sky(sky)
    post_volume(first["ev"])

    # 4. cameras, sequence, queue
    cams, caminfo = {}, {}
    for name in VIEW_NAMES:
        cams[name], caminfo[name] = camera(F, name, VIEWS[name], aspect)
    LEVELS.save_current_level()
    seq = sequence(cams, sky, VIEW_NAMES, VIEWS)
    LEVELS.save_current_level()
    manifest = movie_queue(seq)
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)

    views = []
    for i, name in enumerate(VIEW_NAMES):
        v = VIEWS[name]
        views.append({"name": name, "frame": i, "file": f"villa_{i:04d}.png",
                      "when": f"{v['date'][1]:02d}/{v['date'][0]:02d} {int(v['clock']):02d}:"
                              f"{int(round((v['clock'] % 1) * 60)):02d} UTC+4",
                      "sun": suns[name], "camera": caminfo[name],
                      "eye_m": v["eye"], "target_m": v["target"]})
        if "design_eye" in v:
            views[-1].update(requested_sun=list(v["sun"]), design_eye_m=list(v["design_eye"]),
                             interior=v["interior"], white_balance_k=v["wb"],
                             room_lights_scale=v["lights"])
    result = {"ok": True, "map": MAP, "sequence": seq.get_path_name(), "manifest": manifest,
            "glb": GLB, "import_check": check, "plot_m": [round(W, 3), round(D, 3)],
            "north_offset": north_offset, "context_boxes": n_ctx, "shrubs": n_shrubs, "interior": interior,
            "meshes": sorted(meshes), "views": views, "samples": SAMPLES, "resolution": list(RES),
            "warnings": STATE["warnings"], "seconds": round(time.time() - t0, 1),
            "summary": f"{len(meshes)} meshes, {n_ctx} context boxes, {n_shrubs} shrubs, "
                       f"{len(views)} views, frame {check.get('mapping', 'assumed')}"}
    if PROJECT or design_hooks(Vd):
        # a project's / a design's report says which content folder and
        # design it was built from (the villa's report is as it was)
        result.update(root=ROOT, design=DESIGN if os.path.exists(DESIGN) else None)
        if STATE.get("tint_fits"):
            result["tint_fits"] = STATE["tint_fits"]
        if STATE.get("light_keys"):
            result["interior"]["keyed_lights"] = STATE["light_keys"]
    if dressing:
        result["dressing"] = dressing
    return result


if __name__ == "__main__":
    result = None
    try:
        result = main()
    except Exception:
        tb = traceback.format_exc()
        unreal.log_error("[villa] FAILED\n" + tb)
        result = {"ok": False, "error": tb.strip().splitlines()[-1], "traceback": tb,
                  "warnings": STATE["warnings"]}
    finally:
        try:
            os.makedirs(os.path.dirname(STATUS), exist_ok=True)
            with open(STATUS, "w") as f:
                json.dump(result, f, indent=1)
        finally:
            if os.environ.get("VILLA_UE_KEEP_OPEN") != "1":
                unreal.SystemLibrary.quit_editor()
