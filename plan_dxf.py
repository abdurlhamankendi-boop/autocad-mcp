"""
Architectural plan generator built directly on ezdxf (no COM).

Why not COM: driving AutoCAD over ActiveX proved unreliable for batch work --
dynamic proxies go stale mid-run, early binding renames interface properties,
and a busy editor returns "Call was rejected by callee". Writing DXF directly
is deterministic, ~100x faster, and renders to PNG without AutoCAD, so the
drawing can be inspected and iterated on in seconds. The DXF opens natively in
AutoCAD 2027 when it is time to plot.

Conventions follow the AIA CAD Layer Guidelines / NCS layer names, with a
lineweight hierarchy -- the single strongest cue that separates a professional
drawing from a flat one-weight sketch.

Units: millimetres. Plans read at 1:100 on A3.
"""

from __future__ import annotations

import math
import os

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment

OUT = r"C:\Users\lsire\OneDrive\Desktop\House"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- layers
# (name, aci colour, lineweight in 1/100 mm, linetype)
LAYERS = [
    # ACI 7 prints BLACK on paper and draws WHITE on AutoCAD's dark canvas, so
    # it is correct in both. ACI 8/9 are the greys for secondary information.
    # Hierarchy is carried by LINEWEIGHT, not by hue -- an earlier version used
    # colour-coded layers (yellow text, red dims) which plotted as washed-out
    # pastel because a CTB is required to map them back to black.
    ("A-WALL-EXTR",  7,  70, "CONTINUOUS"),   # cut external     0.70
    ("A-WALL",       7,  50, "CONTINUOUS"),   # cut partition    0.50
    ("A-WALL-PATT",  8,   9, "CONTINUOUS"),   # poche            0.09
    ("A-FLOR-OTLN",  7,  35, "CONTINUOUS"),   # seen, not cut    0.35
    ("A-GLAZ",       7,  25, "CONTINUOUS"),   # windows          0.25
    ("A-DOOR",       7,  25, "CONTINUOUS"),   # door leaves      0.25
    ("A-DOOR-SWNG",  8,  13, "CONTINUOUS"),   # swing arcs       0.13
    ("A-FLOR-STRS",  7,  25, "CONTINUOUS"),   # stairs           0.25
    ("A-FLOR-FIXT",  7,  18, "CONTINUOUS"),   # sanitaryware     0.18
    ("A-FURN",       8,  13, "CONTINUOUS"),   # loose furniture  0.13
    ("A-FLOR-PATT",  9,   9, "CONTINUOUS"),   # floor finishes   0.09
    ("A-ANNO-TEXT",  7,  18, "CONTINUOUS"),   # room names       0.18
    ("A-ANNO-DIMS",  7,  13, "CONTINUOUS"),   # dimensions       0.13
    ("A-ANNO-TTLB",  7,  35, "CONTINUOUS"),   # title block      0.35
    ("A-ANNO-SYMB",  7,  18, "CONTINUOUS"),   # north, scale bar 0.18
    ("S-GRID",       8,  13, "CENTER2"),      # structural grid  0.13
]

# ---------------------------------------------------------------- geometry
# Rectangular envelope with a projecting entrance porch and a living bay, so
# the massing reads as a designed house rather than an extruded rectangle.
W, H = 13000.0, 9600.0
EXT, PART = 300.0, 100.0          # 300 cavity wall, 100 stud partition

# Ground floor zoning. Living/dining/kitchen is one open-plan volume across
# the south face; the service core (WC, utility) stacks under the first-floor
# bathroom so the wet walls line up vertically.
HALL_X1, HALL_X2 = 7400.0, 9800.0     # circulation spine, 2400 wide
STAIR = (7700.0, 3200.0, 8700.0, 6800.0)


def poly(msp, pts, layer, close=True):
    return msp.add_lwpolyline(pts, close=close, dxfattribs={"layer": layer})


def rect_pts(x1, y1, x2, y2):
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


class Plan:
    def __init__(self, title):
        self.doc = ezdxf.new("R2018", setup=True)
        self.doc.header["$INSUNITS"] = 4          # millimetres
        self.doc.header["$MEASUREMENT"] = 1       # metric
        self.msp = self.doc.modelspace()
        self.title = title
        for name, col, lw, lt in LAYERS:
            self.doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
        # a text style with a real font reads far better than the stick font
        self.doc.styles.add("ARCH", font="isocp.shx")
        self._dimstyle()

    def _dimstyle(self):
        ds = self.doc.dimstyles.add("PLAN100")
        ds.dxf.dimtxt = 250          # 2.5mm plotted at 1:100 (ISO 3098)
        ds.dxf.dimasz = 120          # arrow / tick size
        ds.dxf.dimexe = 80           # extension past dim line
        ds.dxf.dimexo = 120          # offset from origin
        ds.dxf.dimdec = 0            # whole millimetres
        ds.dxf.dimlwd = 13
        # 256 = BYLAYER. Hard-coding a colour here overrides the layer, which
        # is why dimensions printed pink while everything else went black.
        ds.dxf.dimclrt = 256      # text
        ds.dxf.dimclrd = 256      # dimension line
        ds.dxf.dimclre = 256      # extension lines
        ds.dxf.dimtad = 1            # text above the line
        ds.dxf.dimgap = 60
        ds.dxf.dimblk = "ARCHTICK"   # architectural tick, not an arrowhead
        ds.dxf.dimtih = 0
        ds.dxf.dimtoh = 0

    # ---- primitives ----------------------------------------------------
    def wall(self, x1, y1, x2, y2, structural=True):
        layer = "A-WALL-EXTR" if structural else "A-WALL"
        poly(self.msp, rect_pts(x1, y1, x2, y2), layer)
        h = self.msp.add_hatch(color=8, dxfattribs={"layer": "A-WALL-PATT"})
        h.paths.add_polyline_path(rect_pts(x1, y1, x2, y2), is_closed=True)
        h.set_solid_fill(color=8)

    def line(self, x1, y1, x2, y2, layer):
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})

    def circle(self, cx, cy, r, layer):
        self.msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})

    def arc(self, cx, cy, r, a0, a1, layer):
        self.msp.add_arc((cx, cy), r, a0, a1, dxfattribs={"layer": layer})

    def text(self, s, x, y, h, layer, align="LEFT", style="ARCH"):
        t = self.msp.add_text(s, height=h,
                              dxfattribs={"layer": layer, "style": style})
        t.set_placement((x, y), align=getattr(TextEntityAlignment, align))
        return t

    def bbox(self, ent):
        from ezdxf import bbox as _bb
        ext = _bb.extents([ent])
        return (ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y)

    def fit_text(self, s, x, y, h, layer, max_w, centre=False):
        """Draw text, then shrink until its REAL bounding box fits max_w.
        Rendered width depends on the text style, so estimating characters
        times height overruns and overprints whatever is next to it."""
        t = self.text(s, x, y, h, layer,
                      align="MIDDLE_CENTER" if centre else "LEFT")
        for _ in range(14):
            x0, _y0, x1, _y1 = self.bbox(t)
            if (x1 - x0) <= max_w or h <= 90:
                break
            h *= 0.90
            t.dxf.height = h
            t.set_placement((x, y),
                            align=getattr(TextEntityAlignment,
                                          "MIDDLE_CENTER" if centre else "LEFT"))
        return t

    def box(self, x1, y1, x2, y2, layer="A-FURN"):
        poly(self.msp, rect_pts(x1, y1, x2, y2), layer)

    # ---- openings ------------------------------------------------------
    def door(self, hx, hy, wd, facing, hinge="left", layer="A-DOOR"):
        a = math.radians(facing)
        self.line(hx, hy, hx + wd * math.cos(a), hy + wd * math.sin(a), layer)
        sweep = -90 if hinge == "left" else 90
        a0, a1 = (facing + sweep, facing) if sweep < 0 else (facing, facing + sweep)
        self.arc(hx, hy, wd, a0, a1, "A-DOOR-SWNG")

    def window(self, x1, y1, x2, y2, horizontal=True):
        L = "A-GLAZ"
        poly(self.msp, rect_pts(x1, y1, x2, y2), L)
        if horizontal:
            ym = (y1 + y2) / 2
            self.line(x1, ym, x2, ym, L)
        else:
            xm = (x1 + x2) / 2
            self.line(xm, y1, xm, y2, L)

    # ---- annotation ----------------------------------------------------
    def dim_h(self, x1, x2, y, off):
        d = self.msp.add_linear_dim(base=(0, y - off), p1=(x1, y), p2=(x2, y),
                                    dimstyle="PLAN100",
                                    dxfattribs={"layer": "A-ANNO-DIMS"})
        d.render()

    def dim_v(self, y1, y2, x, off):
        d = self.msp.add_linear_dim(base=(x - off, 0), p1=(x, y1), p2=(x, y2),
                                    angle=90, dimstyle="PLAN100",
                                    dxfattribs={"layer": "A-ANNO-DIMS"})
        d.render()

    def scale_bar(self, x, y, metres=5):
        """A scale bar survives photocopying and rescaling; a printed
        'SCALE 1:100' does not."""
        L = "A-ANNO-SYMB"
        seg = 1000.0
        for i in range(metres):
            x1, x2 = x + i * seg, x + (i + 1) * seg
            if i % 2 == 0:
                h = self.msp.add_hatch(color=7, dxfattribs={"layer": L})
                h.paths.add_polyline_path(rect_pts(x1, y, x2, y + 150),
                                          is_closed=True)
                h.set_solid_fill(color=7)
            poly(self.msp, rect_pts(x1, y, x2, y + 150), L)
            self.text(f"{i}", x1, y - 320, 160, L, align="MIDDLE_CENTER")
        self.text(f"{metres}", x + metres * seg, y - 320, 160, L,
                  align="MIDDLE_CENTER")
        self.text("METRES", x + metres * seg / 2, y + 320, 160, L,
                  align="MIDDLE_CENTER")

    def north(self, cx, cy, r=520):
        L = "A-ANNO-SYMB"
        self.circle(cx, cy, r, L)
        h = self.msp.add_hatch(color=7, dxfattribs={"layer": L})
        h.paths.add_polyline_path(
            [(cx, cy + r * .82), (cx - r * .30, cy - r * .55), (cx, cy - r * .25)],
            is_closed=True)
        h.set_solid_fill(color=7)
        poly(self.msp, [(cx, cy + r * .82), (cx + r * .30, cy - r * .55),
                        (cx, cy - r * .25)], L)
        self.text("N", cx, cy + r + 260, 260, L, align="MIDDLE_CENTER")

    def grid(self, xs, ys, x0, x1, y0, y1):
        """Structural grid with bubbles - reads as a coordinated drawing."""
        L = "S-GRID"
        for i, x in enumerate(xs):
            self.line(x, y0 - 900, x, y1 + 1500, L)
            self.circle(x, y1 + 1900, 400, L)
            self.text(chr(65 + i), x, y1 + 1900, 240, L, align="MIDDLE_CENTER")
        for j, y in enumerate(ys):
            self.line(x0 - 1500, y, x1 + 900, y, L)
            self.circle(x0 - 1900, y, 400, L)
            self.text(str(j + 1), x0 - 1900, y, 240, L, align="MIDDLE_CENTER")

    def title_block(self, sheet_no, sheet_name, gia, scale="1:100 @ A3",
                    project="TWO-STOREY RESIDENTIAL DWELLING"):
        X, Y, BW, BH = -5200.0, -10200.0, 21000.0, 2500.0
        C1, C2 = 10000.0, 14000.0
        L = "A-ANNO-TTLB"
        poly(self.msp, rect_pts(X, Y, X + BW, Y + BH), L)
        self.line(X, Y + 1650, X + BW, Y + 1650, L)
        for c in (C1, C2):
            self.line(X + c, Y, X + c, Y + 1650, L)
        self.fit_text(project, X + 300, Y + 1950, 360, L, C1 - 400)
        self.text(sheet_name, X + 300, Y + 1150, 260, L)
        self.text("ALL DIMENSIONS IN MILLIMETRES.  DO NOT SCALE FROM DRAWING.",
                  X + 300, Y + 700, 150, L)
        self.text(f"GROSS INTERNAL AREA   {gia:.1f} m2", X + 300, Y + 300, 150, L)
        self.text("SCALE", X + C1 + 250, Y + 1150, 170, L)
        self.text(scale, X + C1 + 250, Y + 800, 200, L)
        self.text("DATE", X + C1 + 250, Y + 400, 170, L)
        self.text("2026-09-06", X + C1 + 250, Y + 120, 170, L)
        self.text("DWG No.", X + C2 + 250, Y + 1150, 170, L)
        self.text(sheet_no, X + C2 + 250, Y + 700, 300, L)
        self.text("REV  A", X + C2 + 250, Y + 250, 170, L)

    # ---- output --------------------------------------------------------
    def save(self, basename):
        path = os.path.join(OUT, basename + ".dxf")
        self.doc.saveas(path)
        return path

    def render(self, basename, dpi=170):
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        from ezdxf.addons.drawing.config import Configuration, LineweightPolicy

        fig = plt.figure(figsize=(16.5, 11.7))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        cfg = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE,
                            lineweight_scaling=1.0)
        ctx = RenderContext(self.doc)
        # ACI colour 7 is "black or white, whichever contrasts with the
        # background". The renderer defaults to a dark background, so
        # everything on colour 7 (title block, solid fills) drew white on white
        # and looked as though it had not drawn at all.
        # draw_layout() calls set_current_layout() -- which resets these
        # properties -- unless layout_properties is passed explicitly, so
        # setting ctx.current_layout_properties beforehand is silently undone.
        lp = ctx.current_layout_properties
        lp.set_colors(bg="#FFFFFF")
        Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(
            self.msp, finalize=True, layout_properties=lp)
        png = os.path.join(OUT, basename + ".png")
        fig.savefig(png, dpi=dpi, facecolor="white")
        plt.close(fig)
        return png


def render_png(doc, png, dpi=150, scale=100.0, margin=0.4):
    """Render a drawing's model space to `png` (a full path, beside its DXF),
    at the sheet's true plot size at 1:`scale` -- Plan.render writes to the
    House folder at a fixed A3 figure. layout_properties is passed
    explicitly: draw_layout() otherwise resets the white background set
    beforehand (then ACI 7 draws white on white). adjust_figure=False keeps
    the figure the plot size, so ABSOLUTE lineweights read as plotted."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf import bbox as _bb
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import Configuration, LineweightPolicy
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    ext = _bb.extents(doc.modelspace())
    w_in = max(1.0, (ext.extmax.x - ext.extmin.x) / scale / 25.4)
    h_in = max(1.0, (ext.extmax.y - ext.extmin.y) / scale / 25.4)
    m = margin
    fig = plt.figure(figsize=(w_in + 2 * m, h_in + 2 * m))
    ax = fig.add_axes([m / (w_in + 2 * m), m / (h_in + 2 * m),
                       w_in / (w_in + 2 * m), h_in / (h_in + 2 * m)])
    ax.set_axis_off()
    cfg = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE,
                        lineweight_scaling=1.0)
    ctx = RenderContext(doc)
    lp = ctx.current_layout_properties
    lp.set_colors(bg="#FFFFFF")
    Frontend(ctx, MatplotlibBackend(ax, adjust_figure=False), config=cfg).draw_layout(
        doc.modelspace(), finalize=True, layout_properties=lp)
    fig.savefig(png, dpi=dpi, facecolor="white")
    plt.close(fig)
    return png


def write_ctb(path=None):
    """Emit the colour-dependent plot style table that maps each ACI colour to
    its plotted lineweight. Without this an AutoCAD user plots everything at
    default weight and the whole hierarchy is lost.

    Only ACI index colours 1-255 obey a CTB; True Color (RGB) objects ignore it.
    """
    from ezdxf.addons import acadctb

    ctb = acadctb.new_ctb()
    # ACI -> (plotted mm, screening %)
    table = {
        1: (0.13, 100),   # dimensions
        2: (0.18, 100),   # annotation text
        3: (0.25, 100),   # doors
        4: (0.25, 100),   # glazing
        5: (0.25, 100),   # stairs
        6: (0.18, 100),   # symbols
        7: (0.50, 100),   # general / partitions / title block
        8: (0.13, 50),    # poche, screened to grey
        30: (0.18, 100),  # sanitaryware
        32: (0.13, 100),  # furniture
        254: (0.09, 25),  # floor patterns, heavily screened
    }
    for aci, (mm, screen) in table.items():
        st = ctb.new_style(aci)
        st.set_lineweight(mm)      # snaps to the nearest valid CTB pen
        st.screen = screen
        st.dithering = False
        # Force black. Left at the default the pen says "use object colour",
        # so ACI 2 prints as pale yellow text and ACI 1 as pink dimensions --
        # the lineweights apply but the sheet still looks like a screenshot.
        # A drawing plots monochrome; tone comes from `screen`, not colour.
        st.color = (0, 0, 0)
    path = path or os.path.join(OUT, "PLAN-ISO128.ctb")
    ctb.save(path)
    return path
