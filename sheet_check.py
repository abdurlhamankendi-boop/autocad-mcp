"""Sheet text check: overlapping labels, and text off the sheet. Offline.

    python sheet_check.py OUT_DIR [--json]

Reads the sheet DXFs in OUT_DIR -- VILLA_A10n.dxf, VILLA_A10nP.dxf and, when
present, VILLA_A20n / VILLA_A30n -- with ezdxf and reports

  text_text      two labels whose ink overlaps
  text_clearance two labels closer than the minimum character spacing of
                 ISO 3098 (touching, or overlapping by less than a pen)
  text_dim       a label crossed by ANOTHER dimension's (or leader's) lines;
                 a dimension's own text over its own lines is not a finding
  outside_frame  a label outside the drawable area of the sheet the title
                 block names ("1:100 @ A1")
  graphics_exceed_frame  the drawing itself does not fit that sheet

Exit 0 clean, 1 findings, 2 could not run: no sheets, an unreadable DXF, a
label that could not be measured (nothing drawn for it, text out of the plan
plane), no stated scale and paper, text in a paper space layout, a bad
argument. Each of those is NOT CHECKED, never a pass.

How a label is measured. Each TEXT, MTEXT and ATTRIB (also those inside
dimensions, leaders and blocks) is DRAWN, one at a time, by ezdxf's drawing
frontend -- the renderer plan_dxf.render_png and villa_pdfset draw the PNG
and PDF sheets with, with the same RenderContext -- and its outline is the
rectangle round the glyphs it draws (the ink), in the text's own direction:
a label at 30 degrees is not judged by a box twice its size, capitals are
not given the font's empty descender band, an MTEXT is as wide as its words
and not its column, inline heights, ALIGNED / FIT and mirrored text are
drawn as they plot. Labels that are not drawn are not checked and are
counted ("not_drawn"): a layer off or frozen, an invisible attribute. Text
on a no-plot layer IS checked: the PNG and PDF renderers draw it.

Fonts. The frontend draws a style's font when it is installed; when it is
not, ezdxf draws its fallback font (ARIALUNI.ttf here: isocp.shx and
OpenSansCondensed-Light.ttf are not installed). That is what the PNG and PDF
show, so it is measured, and every substitution is listed per sheet
("fonts"). For an SHX font AutoCAD plots the shape font itself; ezdxf's own
SHX map (ezdxf.fonts.fonts.SHX_FONTS: isocp.shx -> isocp.ttf) names its
TrueType rendition, found by file name or, failing that, by family (Windows
installs isocp.ttf as isocp___.ttf, family ISOCP). When it is installed the
label is drawn in it too and the outline is the envelope of both drawings,
so a collision in either is found. When it is not, the sheet says
"plot font unknown" for that style: the result then holds for the PNG / PDF
drawing only, and the report says so.

Tolerance. text_text counts only when the overlapping ink is wider, in its
narrow direction, than the thinnest pen on the sheets: 0.09 mm plotted
(plan_dxf.LAYERS, A-WALL-PATT / A-FLOR-PATT, lineweight 9), i.e. 9 mm in the
model at 1:100 (data: the drawing's own pen table; less cannot be seen).
text_clearance counts two labels nearer than a = 0.2 h, h the smaller of
the two text heights: ISO 3098-0 lettering (the standard the sheets' text
heights follow, plan_dxf dimtxt) spaces characters a = 2 d apart, line width
d = h/10 for type B; nearer than that two labels read as one. text_dim
counts a line running more than the pen tolerance through a label's
outline -- also between two of its characters, which is where a dimension
line through "1.4 m2" cuts it in two. One text_dim per label: lines that
lie on one another (chained dimensions sharing an extension line) are one
crossing.

The frame. The sheets draw no border, so the frame is the sheet the title
block states ("1:SCALE @ An"): the ISO 216 paper less the ISO 5457 frame
borders (20 mm filing margin on the left, 10 mm on the other edges)
(standard), times the scale, centred on the drawing's non-text extents and
turned to the drawing's orientation. A label outside it would not plot.

Not checked (said, not passed): text over linework other than dimensions and
leaders (walls, hatches, furniture, fixtures).
"""

from __future__ import annotations

import json
import math
import os
import re
import sys

import ezdxf
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.properties import layer_key, table_key
from ezdxf.addons.drawing.recorder import FilledPathsRecord, PathRecord, Recorder
from ezdxf.enums import TextEntityAlignment
from ezdxf.fonts import fonts
from ezdxf.math import Vec3
from shapely.geometry import LineString, MultiPoint, box
from shapely.ops import unary_union
from shapely import affinity

SHEET_RE = re.compile(r"^VILLA_A(10\d|20\d|30\d)P?\.dxf$", re.IGNORECASE)
SCALE_RE = re.compile(r"1\s*:\s*(\d+)\s*@\s*(A[0-4])\b", re.IGNORECASE)

# Thinnest plotted pen on the sheets, mm (plan_dxf.LAYERS: lineweight 9).
MIN_PEN_MM = 0.09
# ISO 3098-0 character spacing a = 2 d, line width d = h / 10 (type B).
MIN_SPACING_H = 0.2
# ISO 216 paper, mm (long, short).
PAPER = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420),
         "A3": (420, 297), "A4": (297, 210)}
# ISO 5457 frame borders, mm: left (filing margin), and every other edge.
BORDER_LEFT, BORDER = 20.0, 10.0


class NotChecked(Exception):
    """Something the check needs is missing or could not be measured."""


# ------------------------------------------------------------- measuring
def _plain(e):
    return e.plain_text() if e.dxftype() == "MTEXT" else (e.dxf.text or "")


def _height(e):
    return e.dxf.char_height if e.dxftype() == "MTEXT" else e.dxf.height


def _direction(e):
    """The text's reading direction in the plan, degrees; NotChecked when the
    text does not lie in the plan plane."""
    ex = Vec3(e.dxf.get("extrusion", (0, 0, 1)))
    if not ex.isclose(Vec3(0, 0, 1)) and not ex.isclose(Vec3(0, 0, -1)):
        raise NotChecked(f"{e.dxftype()} {_plain(e)!r} is not in the plan plane")
    if e.dxftype() == "MTEXT" and e.dxf.hasattr("text_direction"):
        d = Vec3(e.dxf.text_direction)                 # WCS
    else:
        ang = e.dxf.get("rotation", 0.0)
        if e.dxftype() != "MTEXT" and e.get_align_enum() in (
                TextEntityAlignment.ALIGNED, TextEntityAlignment.FIT):
            _a, p1, p2 = e.get_placement()             # the angle is p1 -> p2
            if p2 is not None and not Vec3(p1).isclose(Vec3(p2)):
                ang = (Vec3(p2) - Vec3(p1)).angle_deg
        d = e.ocs().to_wcs(Vec3.from_deg_angle(ang))   # OCS (mirrored) -> WCS
    return math.degrees(math.atan2(d.y, d.x))


def _plot_face(font):
    """The TrueType face AutoCAD's plot of `font` corresponds to, or None
    when it is not known on this machine (see 'Fonts' above)."""
    if not font:
        return None
    if fonts.is_shx_font_name(font):
        font = fonts.map_shx_to_ttf(font)
        if fonts.is_shx_font_name(font):
            return None                             # no TrueType rendition known
    if fonts.font_manager.has_font(font):
        return fonts.font_manager.get_font_face(font)
    # by family, exactly (ezdxf's find_best_match matches a family PREFIX:
    # "ISOCP" would give ISOCP2)
    stem = os.path.splitext(os.path.basename(font))[0].lower()
    faces = json.loads(fonts.font_manager.dumps())["font-faces"]
    for path, family, style, _w, _wd in sorted(faces, key=lambda f: f[2] != "Regular"):
        if family.lower() == stem:
            return fonts.font_manager.get_font_face(os.path.basename(path))
    return None


class Meter:
    """Draws one label at a time with ezdxf's drawing frontend, in the font
    the PNG / PDF renderers use and, where known, the plot font."""

    def __init__(self, doc):
        self.ctx = RenderContext(doc)                  # as render_png / villa_pdfset
        self.plot = RenderContext(doc)
        self.fonts = {}                                # style -> what was drawn
        for st in doc.styles:
            key = table_key(st.dxf.name)
            face = _plot_face(st.dxf.font)
            if face is not None:
                self.plot.fonts[key] = face
            drawn = self.ctx.fonts.get(key)
            self.fonts[key] = {
                "style": st.dxf.name, "font": st.dxf.font,
                "png_pdf": drawn.filename if drawn else "default",
                "plot": face.filename if face is not None else "unknown"}
        self.used = set()
        self.views = []
        for ctx in (self.ctx, self.plot):
            rec = Recorder()
            self.views.append((ctx, Frontend(ctx, rec), rec))

    def visible(self, e, insert=None):
        """Drawn at all: not on a layer that is off or frozen, not an
        invisible attribute (as RenderContext.resolve_visible)."""
        layer = e.dxf.layer
        if insert is not None:                         # block content
            if insert.dxf.get("invisible", 0):
                return False
            if layer == "0":                            # takes the INSERT's layer
                layer = insert.dxf.layer
        lp = self.ctx.layers.get(layer_key(layer))
        if lp is not None and not lp.is_visible:
            return False
        if e.dxf.get("invisible", 0):
            return False
        return not (e.dxftype() == "ATTRIB" and e.is_invisible)

    def outline(self, e):
        """The label's ink rectangle in its own direction (a shapely
        Polygon), or NotChecked when nothing could be drawn for it."""
        rot = _direction(e)
        self.used.add(table_key(e.dxf.get("style", "Standard")))
        pts = []
        try:
            for ctx, fe, rec in self.views:
                rec.records.clear()
                fe.draw_entity(e, ctx.resolve_all(e))
                step = max(_height(e), 1.0) / 100.0
                for r in rec.records:
                    if isinstance(r, FilledPathsRecord):
                        paths = r.paths
                    elif isinstance(r, PathRecord):
                        paths = [r.path]
                    else:
                        pts += [(v.x, v.y) for v in
                                getattr(r, "points", getattr(r, "lines", None)).vertices()]
                        continue
                    for p in paths:
                        if len(p):
                            pts += [(v.x, v.y) for v in p.flattening(step)]
        except Exception as exc:                        # fail closed
            raise NotChecked(f"could not draw {e.dxftype()} {_plain(e)!r}: {exc}")
        if len(pts) < 2:
            raise NotChecked(f"nothing drawn for {e.dxftype()} {_plain(e)!r}")
        flat = affinity.rotate(MultiPoint(pts), -rot, origin=(0, 0))
        x0, y0, x1, y1 = flat.bounds
        if x1 - x0 <= 0 or y1 - y0 <= 0:
            raise NotChecked(f"no extents for {e.dxftype()} {_plain(e)!r}")
        return affinity.rotate(box(x0, y0, x1, y1), rot, origin=(0, 0))

    def used_fonts(self):
        return [self.fonts[k] for k in sorted(self.used) if k in self.fonts]


def _lines_of(entities):
    """LineStrings of the LINE / polyline linework among `entities`."""
    out = []
    for v in entities:
        t = v.dxftype()
        if t == "LINE":
            s, e = v.dxf.start, v.dxf.end
            out.append(LineString([(s.x, s.y), (e.x, e.y)]))
        elif t == "LWPOLYLINE":
            pts = [p[:2] for p in v.get_points("xy")]
            if v.closed:
                pts.append(pts[0])
            if len(pts) > 1:
                out.append(LineString(pts))
    return out


def collect(doc):
    """(labels, lines, info): labels as dicts {text, owner, layer, h, poly};
    lines as (owner, LineString) for every dimension's and leader's
    linework; info {not_drawn, fonts}. A dimension's text and lines share
    its handle as owner."""
    msp = doc.modelspace()
    raw, lines = [], []                     # raw: (entity, owner[, insert])
    leader_text = {}                        # LEADER annotation -> leader handle
    for e in msp.query("LEADER"):
        h = e.dxf.get("annotation_handle")
        if h:
            leader_text[h] = e.dxf.handle
        pts = [(v.x, v.y) for v in e.vertices]
        if len(pts) > 1:
            lines.append((e.dxf.handle, LineString(pts)))
    for e in msp:
        t = e.dxftype()
        if t in ("TEXT", "MTEXT"):
            raw.append((e, leader_text.get(e.dxf.handle)))
        elif t in ("DIMENSION", "MULTILEADER", "MLEADER"):
            try:
                ve = list(e.virtual_entities())
            except Exception as exc:
                raise NotChecked(f"could not explode {t} {e.dxf.handle}: {exc}")
            raw += [(v, e.dxf.handle, e) for v in ve if v.dxftype() in ("TEXT", "MTEXT")]
            lines += [(e.dxf.handle, ln) for ln in _lines_of(ve)]
        elif t == "INSERT":
            raw += [(a, e.dxf.handle, e) for a in e.attribs]
            try:
                ve = list(e.virtual_entities())
            except Exception as exc:
                raise NotChecked(f"could not explode block {e.dxf.name}: {exc}")
            stack = ve
            while stack:
                v = stack.pop()
                if v.dxftype() in ("TEXT", "MTEXT", "ATTRIB"):
                    raw.append((v, e.dxf.handle, e))
                elif v.dxftype() == "INSERT":
                    raw += [(a, e.dxf.handle, e) for a in v.attribs]
                    stack += list(v.virtual_entities())
    meter = Meter(doc)
    labels, not_drawn = [], 0
    for item in raw:
        e, owner, insert = (item + (None,))[:3]
        s = _plain(e).strip()
        if not s:
            continue                        # a blank string prints nothing
        if not meter.visible(e, insert):
            not_drawn += 1                  # layer off / frozen, invisible
            continue
        labels.append({"text": s, "owner": owner, "layer": e.dxf.layer,
                       "h": _height(e), "poly": meter.outline(e)})
    return labels, lines, {"not_drawn": not_drawn, "fonts": meter.used_fonts()}


def stated_sheet(labels):
    """(scale, paper) from the title block's '1:100 @ A1', or NotChecked."""
    found = {(int(m.group(1)), m.group(2).upper())
             for lb in labels for m in [SCALE_RE.search(lb["text"])] if m}
    if len(found) != 1:
        raise NotChecked("no single '1:SCALE @ An' statement on the sheet "
                         f"(found {sorted(found) or 'none'})")
    return found.pop()


def frame_box(doc, scale, paper):
    """The drawable area of the stated sheet, centred on the drawing's
    non-text extents, in its orientation; and those extents."""
    ext = bbox.extents(e for e in doc.modelspace()
                       if e.dxftype() not in ("TEXT", "MTEXT"))
    if not ext.has_data:
        raise NotChecked("the sheet has no graphics to place the frame on")
    long_, short = PAPER[paper]
    w = (long_ - BORDER_LEFT - BORDER) * scale
    h = (short - 2 * BORDER) * scale
    if ext.size.y > ext.size.x:
        w, h = (short - BORDER_LEFT - BORDER) * scale, (long_ - 2 * BORDER) * scale
    cx, cy = ext.center.x, ext.center.y
    g = (ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y)
    return box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), g


def _depth(geom):
    """Width of an overlap in its narrow direction (0 for no area)."""
    if geom.is_empty or geom.area <= 0:
        return 0.0
    r = geom.minimum_rotated_rectangle
    xs = list(r.exterior.coords)
    sides = [math.dist(xs[i], xs[i + 1]) for i in range(len(xs) - 1)]
    return min(sides) if sides else 0.0


# ---------------------------------------------------------------- checks
def check_doc(doc):
    """Findings for one sheet. Raises NotChecked when it cannot judge."""
    for lay in doc.layouts:
        if lay.name != "Model" and any(e.dxftype() != "VIEWPORT" for e in lay):
            raise NotChecked(f"paper space layout {lay.name!r} has entities "
                             "(only model space is checked)")
    labels, lines, info = collect(doc)
    scale, paper = stated_sheet(labels)
    tol = MIN_PEN_MM * scale
    out = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            need = MIN_SPACING_H * min(a["h"], b["h"])
            gap = a["poly"].distance(b["poly"])
            if gap >= need:
                continue
            both = a["poly"].intersection(b["poly"])
            d = _depth(both)
            if d > tol:
                out.append({"kind": "text_text", "a": a["text"], "b": b["text"],
                            "overlap_mm": round(d, 1), "at": _xy(both)})
            else:                           # touching, or less than a pen
                out.append({"kind": "text_clearance", "a": a["text"], "b": b["text"],
                            "overlap_mm": round(d, 1), "gap_mm": round(gap, 1),
                            "min_gap_mm": round(need, 1),
                            "at": _xy(unary_union([a["poly"], b["poly"]]))})
    for a in labels:
        hits, owners = [], []
        for owner, ln in lines:
            if owner is not None and owner == a["owner"]:
                continue                    # its own dimension / leader
            if a["poly"].intersects(ln):
                hits.append(a["poly"].intersection(ln))
                owners.append(owner)
        if not hits:
            continue
        crossing = unary_union(hits)        # lines on one another count once
        if crossing.length > tol:
            out.append({"kind": "text_dim", "a": a["text"],
                        "b": "lines of " + ", ".join(sorted(set(owners))),
                        "overlap_mm": round(crossing.length, 1), "at": _xy(crossing)})
    fr, g = frame_box(doc, scale, paper)
    for a in labels:
        if not fr.contains(a["poly"]):
            out.append({"kind": "outside_frame", "a": a["text"], "b": f"1:{scale} @ {paper}",
                        "overlap_mm": round(a["poly"].difference(fr).area ** 0.5, 1),
                        "at": _xy(a["poly"])})
    if not fr.contains(box(*g)):
        out.append({"kind": "graphics_exceed_frame", "a": "drawing extents",
                    "b": f"1:{scale} @ {paper}",
                    "overlap_mm": 0.0, "at": [round(v) for v in g]})
    meta = {"labels": len(labels), "scale": scale, "paper": paper,
            "tolerance_mm": round(tol, 2), "not_drawn": info["not_drawn"],
            "fonts": info["fonts"]}
    return out, meta


def _xy(geom):
    c = geom.centroid
    return [round(c.x), round(c.y)]


def sheets(folder):
    return sorted(f for f in os.listdir(folder) if SHEET_RE.match(f))


def run(folder):
    """{'sheets': {name: {...}}, 'status': 'clean' | 'findings' | 'not_checked'}"""
    res = {"folder": folder, "sheets": {}}
    if not os.path.isdir(folder):
        res["error"] = f"no such folder: {folder}"
        res["status"] = "not_checked"
        return res
    names = sheets(folder)
    if not names:
        res["error"] = "no sheet DXFs (VILLA_A10n[P] / A20n / A30n) in the folder"
        res["status"] = "not_checked"
        return res
    bad = found = False
    for n in names:
        try:
            doc = ezdxf.readfile(os.path.join(folder, n))
            f, meta = check_doc(doc)
            res["sheets"][n] = dict(meta, findings=f)
            found |= bool(f)
        except Exception as exc:            # fail closed: any error is NOT CHECKED
            res["sheets"][n] = {"not_checked": f"{type(exc).__name__}: {exc}",
                                "findings": []}
            bad = True
    res["status"] = "not_checked" if bad else "findings" if found else "clean"
    # Styles whose AutoCAD plot font is not known here: for their labels the
    # result holds for the PNG / PDF drawing only (see 'Fonts').
    res["plot_font_unknown"] = sorted(
        {f"{x['style']} ({x['font']})" for s in res["sheets"].values()
         for x in s.get("fonts", []) if x["plot"] == "unknown"})
    return res


def report(res):
    lines = [f"sheet_check  {res['folder']}"]
    if "error" in res:
        lines.append(f"NOT CHECKED: {res['error']}")
    for n, s in res["sheets"].items():
        if "not_checked" in s:
            lines.append(f"  {n:20s} NOT CHECKED: {s['not_checked']}")
            continue
        f = s["findings"]
        lines.append(f"  {n:20s} {s['labels']:4d} labels  1:{s['scale']} @ {s['paper']}  "
                     f"tol {s['tolerance_mm']} mm  -> "
                     f"{'clean' if not f else str(len(f)) + ' finding(s)'}")
        for x in f:
            size = (f"gap {x['gap_mm']} mm < {x['min_gap_mm']} mm" if "gap_mm" in x
                    else f"{x['overlap_mm']} mm")
            lines.append(f"      {x['kind']:22s} {x['a']!r} / {x['b']!r}  "
                         f"{size}  at {x['at']}")
    fonts_seen = {(x["style"], x["font"], x["png_pdf"], x["plot"])
                  for s in res["sheets"].values() for x in s.get("fonts", [])}
    for st, font, drawn, plot in sorted(fonts_seen):
        lines.append(f"  font  {st}: {font} -> PNG/PDF {drawn}, plot {plot}")
    if res.get("plot_font_unknown"):
        lines.append("  plot font unknown for " + ", ".join(res["plot_font_unknown"])
                     + ": for those labels the result holds for the PNG / PDF only")
    lines.append(f"RESULT: {res['status'].upper()}")
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(a != "--json" for a in flags):
        print(__doc__.split("\n\n")[1])
        return 2
    res = run(args[0])
    print(json.dumps(res, indent=1) if "--json" in argv else report(res))
    return {"clean": 0, "findings": 1}.get(res["status"], 2)


if __name__ == "__main__":
    try:
        code = main(sys.argv[1:])
    except Exception as exc:                # a crash must not read as exit 1
        print(f"NOT CHECKED: {type(exc).__name__}: {exc}")
        code = 2
    sys.exit(code)
