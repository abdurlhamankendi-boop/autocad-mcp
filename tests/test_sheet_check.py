"""Offline tests for sheet_check.py (label overlaps, text off the sheet).

Synthetic sheets: overlapping, touching, too close and clean labels, placed
from their GLYPHS measured independently (ezdxf text2path, not the drawing
frontend sheet_check measures with); a rotated pair; MTEXT (a column wider
than its words, several lines, inline heights, rotated), ALIGNED / FIT and
mirrored TEXT, block attributes; text that is not drawn (layer off, frozen,
invisible attribute) and text that is (a no-plot layer); a dimension's own
text, a label over another dimension and over chained dimensions; a label
off the sheet; fonts (the plot font of isocp.shx, a missing font); and the
NOT CHECKED cases (no sheets, an unreadable or truncated DXF, no stated
scale, a bad flag). Then the benchmark's A-101, where a judge saw
'POOL 3.5 x 8.0 m' over '1100 DEEP' (skipped when that output is not on this
machine).

    python -X utf8 tests\\test_sheet_check.py
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import ezdxf  # noqa: E402
from ezdxf.addons import MTextExplode, text2path  # noqa: E402
from ezdxf.enums import TextEntityAlignment as TA  # noqa: E402
from ezdxf.fonts import fonts  # noqa: E402
from shapely.geometry import MultiPoint  # noqa: E402
from shapely import affinity  # noqa: E402

import sheet_check as SC  # noqa: E402

BENCH_A101 = os.path.join(tempfile.gettempdir(), "villa_bench", "T1_r2", "out")
H = 250.0                                   # label height, mm at 1:100
MIN_GAP = SC.MIN_SPACING_H * H              # 50 mm: ISO 3098 a = 0.2 h
# A TrueType font installed here: drawn by the renderer AND the plot font, so
# text2path (same font) is an independent measure of exactly what is checked.
HAS_ARIAL = fonts.font_manager.has_font("arial.ttf")


def new_sheet(scale_text="1:100 @ A1", style="ARCH", font="isocp.shx"):
    doc = ezdxf.new("R2018", setup=True)
    doc.styles.add("ARCH", font="isocp.shx")
    if style != "ARCH":
        doc.styles.add(style, font=font)
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (20000, 0), (20000, 15000), (0, 15000)], close=True)
    if scale_text:
        msp.add_text(scale_text, height=200, dxfattribs={"style": "ARCH"}) \
            .set_placement((0, -3000))
    return doc


def label(doc, s, x, y, h=H, rot=0.0, align=TA.LEFT, style="ARCH", **attrs):
    t = doc.modelspace().add_text(s, height=h, dxfattribs=dict(
        style=style, rotation=rot, **attrs))
    t.set_placement((x, y), align=align)
    return t


def glyph_points(entities):
    """Glyph outline points of TEXT entities, by text2path (flattened)."""
    pts = []
    for t in entities:
        for p in text2path.make_paths_from_entity(t):
            pts += [(v.x, v.y) for v in p.flattening(1.0)]
    return pts


def ink(t):
    """(x0, y0, x1, y1) of a horizontal TEXT's glyphs."""
    return MultiPoint(glyph_points([t])).bounds


def outline_of(doc, text):
    labels, _lines, _info = SC.collect(doc)
    found = [lb for lb in labels if lb["text"] == text]
    assert len(found) == 1, (text, [lb["text"] for lb in labels])
    return found[0]["poly"]


class Synthetic(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="sheet_check_")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def save(self, doc, name="VILLA_A102.dxf"):
        doc.saveas(os.path.join(self.dir, name))

    def findings(self, res, name="VILLA_A102.dxf"):
        return res["sheets"][name]["findings"]

    def kinds(self, res, name="VILLA_A102.dxf"):
        return [f["kind"] for f in self.findings(res, name)]

    def test_clean(self):
        doc = new_sheet()
        label(doc, "LIVING", 2000, 5000)
        label(doc, "24.0 m2", 2000, 4000)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))

    def test_overlapping(self):
        doc = new_sheet()
        label(doc, "POOL 3.5 x 8.0 m", 5000, 5000, 300, align=TA.MIDDLE_CENTER)
        label(doc, "1100 DEEP", 5000, 4850, 180, align=TA.MIDDLE_CENTER)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "findings")
        f = self.findings(res)
        self.assertEqual([x["kind"] for x in f], ["text_text"])
        self.assertEqual({f[0]["a"], f[0]["b"]}, {"POOL 3.5 x 8.0 m", "1100 DEEP"})

    def stacked(self, gap, upper="MASTER BEDROOM", lower="LIVING ROOM"):
        """Two capital labels one above the other, `gap` mm between their
        glyphs (negative: overlapping), measured by text2path."""
        doc = new_sheet(style="ARIAL", font="arial.ttf")
        lo = label(doc, lower, 2000, 5000, style="ARIAL")
        up = label(doc, upper, 2000, 0, style="ARIAL")
        up.set_placement((2000, ink(lo)[3] + gap - ink(up)[1]))
        self.assertAlmostEqual(ink(up)[1] - ink(lo)[3], gap, places=3)
        self.save(doc)
        return SC.run(self.dir)

    @unittest.skipUnless(HAS_ARIAL, "arial.ttf not installed")
    def test_stacked_capitals_measured_by_their_glyphs(self):
        """No empty descender band: 0.3 mm plotted apart is not an overlap
        (the old box called this 44 mm) but is nearer than ISO 3098's 0.2 h;
        0.64 mm apart is clean; 20 mm into each other is a 20 mm overlap."""
        res = self.stacked(30.0)
        f = self.findings(res)
        self.assertEqual([x["kind"] for x in f], ["text_clearance"], SC.report(res))
        self.assertAlmostEqual(f[0]["gap_mm"], 30.0, delta=1.0)
        self.assertEqual(f[0]["min_gap_mm"], MIN_GAP)
        res = self.stacked(64.0)
        self.assertEqual(res["status"], "clean", SC.report(res))
        res = self.stacked(-20.0)
        f = self.findings(res)
        self.assertEqual([x["kind"] for x in f], ["text_text"], SC.report(res))
        self.assertAlmostEqual(f[0]["overlap_mm"], 20.0, delta=1.0)

    def side_by_side(self, over):
        doc = new_sheet(style="ARIAL", font="arial.ttf")
        a = label(doc, "BEDROOM", 2000, 5000, style="ARIAL")
        b = label(doc, "ENSUITE", 0, 5000, style="ARIAL")
        b.set_placement((ink(a)[2] - over - (ink(b)[0] - 0), 5000))
        self.assertAlmostEqual(ink(a)[2] - ink(b)[0], over, places=3)
        self.save(doc)
        return SC.run(self.dir)

    @unittest.skipUnless(HAS_ARIAL, "arial.ttf not installed")
    def test_touching_is_too_close_not_an_overlap(self):
        res = self.side_by_side(0.0)
        f = self.findings(res)
        self.assertEqual([x["kind"] for x in f], ["text_clearance"], SC.report(res))
        self.assertAlmostEqual(f[0]["gap_mm"], 0.0, delta=0.5)

    @unittest.skipUnless(HAS_ARIAL, "arial.ttf not installed")
    def test_tolerance_is_the_thinnest_pen(self):
        """0.09 mm at 1:100 = 9 mm: 5 mm of overlapping glyphs is not an
        overlap (it is too close), 20 mm is."""
        for over, want in ((5.0, "text_clearance"), (20.0, "text_text")):
            res = self.side_by_side(over)
            self.assertEqual(self.kinds(res), [want], (over, SC.report(res)))
            self.assertEqual(res["sheets"]["VILLA_A102.dxf"]["tolerance_mm"], 9.0)

    def test_rotated_labels_use_their_own_outline(self):
        """Two parallel labels at 45 degrees, one line apart: their axis-aligned
        boxes overlap, their outlines do not."""
        doc = new_sheet()
        label(doc, "SERVICE CORRIDOR", 6000, 6000, rot=45)
        label(doc, "SERVICE CORRIDOR", 6000 - 300, 6000 + 300, rot=45)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))

    # ------------------------------------------------------------- MTEXT
    @unittest.skipUnless(HAS_ARIAL, "arial.ttf not installed")
    def test_mtext_outline_is_its_glyphs(self):
        """A column wider than the words, several lines bottom-right, inline
        heights, a rotation: the outline is the size of the glyphs (exploded
        to TEXT and measured by text2path) and holds them. ezdxf's
        MTextExplode sets a bottom-attached last line up to a descender
        (0.28 h) lower than the drawing frontend does, hence 0.3 h."""
        cases = [("WC", {"width": 6000}),
                 ("LINE ONE\\PLINE TWO IS LONGER\\PLINE THREE",
                  {"attachment_point": 9}),
                 ("{\\H3x;BIG} small", {}),
                 ("ROTATED MTEXT", {"rotation": 60})]
        for s, attrs in cases:
            doc = new_sheet(style="ARIAL", font="arial.ttf")
            msp = doc.modelspace()
            m = msp.add_mtext(s, dxfattribs=dict(style="ARIAL", char_height=H, **attrs))
            m.dxf.insert = (5000, 5000)
            poly = outline_of(doc, m.plain_text().strip())
            scratch = doc.blocks.new("SCRATCH_" + str(len(doc.blocks)))
            with MTextExplode(scratch, doc) as xpl:
                xpl.explode(m, destroy=False)
            pts = glyph_points(scratch.query("TEXT"))
            self.assertTrue(pts, s)
            outside = [p for p in pts
                       if not poly.buffer(0.3 * H).contains(MultiPoint([p]))]
            self.assertFalse(outside, (s, len(outside), poly.bounds))
            rot = attrs.get("rotation", 0)
            x0, y0, x1, y1 = affinity.rotate(MultiPoint(pts), -rot, origin=(0, 0)).bounds
            u0, v0, u1, v1 = affinity.rotate(poly, -rot, origin=(0, 0)).bounds
            self.assertAlmostEqual(u1 - u0, x1 - x0, delta=0.1 * H, msg=s)
            self.assertAlmostEqual(v1 - v0, y1 - y0, delta=0.1 * H, msg=s)

    def test_mtext_column_is_not_the_label(self):
        doc = new_sheet()
        m = doc.modelspace().add_mtext("WC", dxfattribs={
            "style": "ARCH", "char_height": H, "width": 6000})
        m.dxf.insert = (2000, 5000)
        label(doc, "SHOWER", 5000, 4800)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))

    # ------------------------------------------------ ALIGNED / FIT / mirror
    def test_aligned_fit_and_mirrored_text(self):
        """ALIGNED / FIT (rotation 45 written as AutoCAD writes it): the text
        runs p1 -> p2 one text height high, so the outline holds that band
        (cap-height midline, ends trimmed 5 %) and is about its size -- not
        turned twice, not the box of the slanted line. Mirrored (extrusion
        -Z): the outline holds the glyphs text2path draws."""
        from shapely.geometry import LineString
        doc = new_sheet()
        for s, align, p1, p2 in (("ALIGNED", TA.ALIGNED, (3000, 3000), (6000, 6000)),
                                 ("FIT TEXT", TA.FIT, (9000, 3000), (12000, 6000))):
            t = label(doc, s, 0, 0, rot=45)
            t.set_placement(p1, p2, align=align)
            poly = outline_of(doc, s)
            n = (-math.sqrt(0.5) * H / 2, math.sqrt(0.5) * H / 2)   # half a height up
            mid = LineString([(p1[0] + n[0], p1[1] + n[1]), (p2[0] + n[0], p2[1] + n[1])])
            core = mid.interpolate(0.05, normalized=True), mid.interpolate(0.95, normalized=True)
            self.assertTrue(poly.buffer(1.0).contains(LineString(core)), (s, poly.bounds))
            L, h = math.dist(p1, p2), t.dxf.height
            if align == TA.ALIGNED:                 # ALIGNED scales the height too
                x0, _y0, x1, _y1 = ink(label(new_sheet(), s, 0, 0))
                h *= L / (x1 - x0)
            self.assertLess(poly.area, 1.5 * L * h, (s, poly.area, L * h))
        m = label(doc, "MIRROR", 0, 0, rot=30, extrusion=(0, 0, -1))
        m.dxf.insert = (-6000, 6000)
        poly = outline_of(doc, "MIRROR")
        pts = glyph_points([m])
        self.assertTrue(all(poly.buffer(1.0).contains(MultiPoint([p])) for p in pts),
                        (poly.bounds, MultiPoint(pts).bounds))
        self.assertLess(poly.area, 1.2 * MultiPoint(pts).minimum_rotated_rectangle.area)

    def test_text_out_of_the_plan_plane_is_not_checked(self):
        doc = new_sheet()
        label(doc, "TILTED", 2000, 5000, extrusion=(0, 1, 1))
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "not_checked", SC.report(res))

    # ------------------------------------------------- blocks, visibility
    def test_block_attribute_measured(self):
        doc = new_sheet()
        blk = doc.blocks.new("TAG")
        blk.add_attdef("ROOM", (0, 0), dxfattribs={"style": "ARCH", "height": H})
        ins = doc.modelspace().add_blockref("TAG", (2000, 5000))
        ins.add_auto_attribs({"ROOM": "STORE"})
        label(doc, "STORE", 2050, 5030)               # over the attribute
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(self.kinds(res), ["text_text"], SC.report(res))

    def test_text_that_is_not_drawn_is_not_checked(self):
        """Layer off, layer frozen, invisible attribute: not drawn by the
        renderers, so not findings -- counted as not_drawn. A no-plot layer
        IS drawn in the PNG and PDF, so it is checked."""
        doc = new_sheet()
        doc.layers.add("OFF").off()
        doc.layers.add("FROZEN").freeze()
        doc.layers.add("NOPLOT", dxfattribs={"plot": 0})
        label(doc, "LIVING", 2000, 5000)
        label(doc, "LIVING", 2000, 5000, layer="OFF")
        label(doc, "LIVING", 2000, 5000, layer="FROZEN")
        blk = doc.blocks.new("TAG")
        blk.add_attdef("NOTE", (0, 0), dxfattribs={"style": "ARCH", "height": H})
        ins = doc.modelspace().add_blockref("TAG", (2000, 5000))
        ins.add_auto_attribs({"NOTE": "HIDDEN ATTR"})
        ins.attribs[0].is_invisible = True
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))
        self.assertEqual(res["sheets"]["VILLA_A102.dxf"]["not_drawn"], 3)
        label(doc, "LIVING", 2000, 5000, layer="NOPLOT")
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(self.kinds(res), ["text_text"], SC.report(res))

    # -------------------------------------------------------- dimensions
    def test_own_dimension_ignored_other_dimension_reported(self):
        doc = new_sheet()
        msp = doc.modelspace()
        d = msp.add_linear_dim(base=(0, -1500), p1=(0, 0), p2=(6000, 0))
        d.render()
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))
        label(doc, "TERRACE", 2500, -1550)  # sits on the dimension line
        self.save(doc)
        res = SC.run(self.dir)
        self.assertIn("text_dim", self.kinds(res), SC.report(res))

    def test_chained_dimensions_one_finding_per_label(self):
        """Two chained dimensions share the extension line at x=6000: a
        label across it is one crossing, not one per dimension."""
        doc = new_sheet()
        msp = doc.modelspace()
        msp.add_linear_dim(base=(0, -1500), p1=(0, 0), p2=(6000, 0)).render()
        msp.add_linear_dim(base=(0, -1500), p1=(6000, 0), p2=(10000, 0)).render()
        label(doc, "BALCONY", 6000, -700, align=TA.MIDDLE_CENTER)
        self.save(doc)
        res = SC.run(self.dir)
        f = [x for x in self.findings(res) if x["kind"] == "text_dim"]
        self.assertEqual(len(f), 1, SC.report(res))
        self.assertEqual(f[0]["a"], "BALCONY")
        self.assertEqual(f[0]["b"].count(","), 1, f[0]["b"])     # both dimensions

    def test_label_off_the_sheet(self):
        doc = new_sheet()
        label(doc, "STRAY NOTE", 150000, 5000)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(self.kinds(res), ["outside_frame"], SC.report(res))

    # ------------------------------------------------------------- fonts
    def test_fonts_are_reported(self):
        """isocp.shx: the PNG / PDF font is whatever ezdxf resolves (its
        fallback here), the plot font its TrueType rendition ISOCP, found by
        exact family; both are listed. A font that is not installed and has
        no known rendition: 'plot unknown', said in the result."""
        doc = new_sheet(style="GONE", font="no_such_font_xyz.shx")
        label(doc, "LIVING", 2000, 5000)
        label(doc, "STORE", 2000, 8000, style="GONE")
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "clean", SC.report(res))
        fonts_ = {x["style"]: x for x in res["sheets"]["VILLA_A102.dxf"]["fonts"]}
        self.assertEqual(fonts_["GONE"]["plot"], "unknown")
        self.assertEqual(fonts_["GONE"]["png_pdf"], fonts.font_manager.fallback_font_name())
        self.assertIn("GONE (no_such_font_xyz.shx)", res["plot_font_unknown"])
        self.assertIn("PNG / PDF only", SC.report(res))
        isocp = SC._plot_face("isocp.shx")
        if isocp is not None:                       # ISOCP installed here
            self.assertEqual(isocp.family, "ISOCP")
            self.assertEqual(fonts_["ARCH"]["plot"], isocp.filename)

    # ----------------------------------------------------- not checked
    def test_no_stated_scale_is_not_checked(self):
        doc = new_sheet(scale_text=None)
        label(doc, "LIVING", 2000, 5000)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "not_checked")
        self.assertIn("not_checked", res["sheets"]["VILLA_A102.dxf"])

    def test_unreadable_and_empty(self):
        self.assertEqual(SC.run(self.dir)["status"], "not_checked")     # no sheets
        with open(os.path.join(self.dir, "VILLA_A101.dxf"), "w") as fh:
            fh.write("not a dxf")
        doc = new_sheet()
        label(doc, "LIVING", 2000, 5000)
        self.save(doc)
        res = SC.run(self.dir)
        self.assertEqual(res["status"], "not_checked")       # one bad sheet
        self.assertEqual(res["sheets"]["VILLA_A102.dxf"]["findings"], [])

    def test_truncated_dxf_is_not_checked(self):
        doc = new_sheet()
        label(doc, "LIVING", 2000, 5000)
        self.save(doc)
        path = os.path.join(self.dir, "VILLA_A102.dxf")
        with open(path, "rb") as fh:
            data = fh.read()
        for frac in (0.3, 0.6, 0.9, 0.99):
            with open(path, "wb") as fh:
                fh.write(data[:int(len(data) * frac)])
            self.assertEqual(SC.run(self.dir)["status"], "not_checked", frac)

    def test_only_sheet_files(self):
        doc = new_sheet()
        label(doc, "A", 2000, 5000)
        label(doc, "A", 2000, 5000)          # would overlap
        self.save(doc, "VILLA_3D_MODEL.dxf")
        self.assertEqual(SC.run(self.dir)["status"], "not_checked")   # nothing read

    def test_cli_exit_codes(self):
        py = sys.executable
        script = os.path.join(ROOT, "sheet_check.py")
        r = subprocess.run([py, "-X", "utf8", script, self.dir], capture_output=True)
        self.assertEqual(r.returncode, 2)
        doc = new_sheet()
        label(doc, "LIVING", 2000, 5000)
        self.save(doc)
        r = subprocess.run([py, "-X", "utf8", script, self.dir, "--json"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(json.loads(r.stdout)["status"], "clean")
        r = subprocess.run([py, "-X", "utf8", script, self.dir, "--jsno"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout)              # a bad flag
        label(doc, "LIVING", 2000, 5050)
        self.save(doc)
        r = subprocess.run([py, "-X", "utf8", script, self.dir], capture_output=True)
        self.assertEqual(r.returncode, 1)


@unittest.skipUnless(os.path.isfile(os.path.join(BENCH_A101, "VILLA_A101.dxf")),
                     "benchmark output T1_r2 not on this machine")
class BenchmarkA101(unittest.TestCase):
    """The judge's finding is found (read only: the file is not changed).
    The glyphs do not overlap: they are a few mm apart, far nearer than
    ISO 3098's 0.2 h, so it is a text_clearance finding."""

    def test_pool_label_over_depth(self):
        doc = ezdxf.readfile(os.path.join(BENCH_A101, "VILLA_A101.dxf"))
        f, _meta = SC.check_doc(doc)
        pairs = {frozenset((x["a"], x["b"])): x for x in f
                 if x["kind"] in ("text_text", "text_clearance")}
        x = pairs.get(frozenset(("POOL 3.5 x 8.0 m", "1100 DEEP")))
        self.assertIsNotNone(x, f)
        self.assertEqual(x["kind"], "text_clearance", x)
        self.assertLess(x["gap_mm"], 10.0, x)


if __name__ == "__main__":
    unittest.main(verbosity=2)
