"""Assemble the villa drawing set as a single multi-page vector PDF.

Renders straight from the DXFs with matplotlib, so it needs no AutoCAD. Each
page is real vector output, not a raster screenshot.
"""

import os

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, LineweightPolicy

import villa_design as V
import villa_geom as G

# VILLA_OUT redirects it (the villa's Desktop\Villa when unset; a project
# design run through run_project.py, its own folder)
OUT = G.out_dir()
PROJECT = bool(getattr(V, "PLAN_SHEETS", None))

# (file stem, page caption). Order is the issue order of the set.
PAGES = [
    ("A-201_GROUND_FLOOR_PLAN", "A-201  GROUND FLOOR PLAN"),
    ("A-202_FIRST_FLOOR_PLAN",  "A-202  FIRST FLOOR PLAN"),
    ("VILLA_PLAN_BASEMENT",     "A-200  BASEMENT PLAN"),
    ("VILLA_PLAN_ROOF",         "A-203  ROOF PLAN"),
    ("VILLA_ELEV_S",            "A-301  SOUTH ELEVATION  (garden / pool)"),
    ("VILLA_ELEV_N",            "A-302  NORTH ELEVATION  (street)"),
    ("VILLA_ELEV_E",            "A-303  EAST ELEVATION"),
    ("VILLA_ELEV_W",            "A-304  WEST ELEVATION  (brise-soleil)"),
    ("VILLA_SECTION_AA",        "A-401  SECTION A-A  (on the water axis)"),
    ("VILLA_VIEW_AERIAL_SW",    "A-501  AERIAL FROM SOUTH WEST"),
    ("VILLA_VIEW_POOL_EYE",     "A-502  EYE LEVEL FROM THE POOL"),
    ("VILLA_VIEW_AERIAL_NE",    "A-503  AERIAL FROM NORTH EAST"),
]
if PROJECT:
    # a project design's set: the site plan and its PLAN_SHEETS (villa_cad),
    # then the presentation set (villa_colour); pages that are missing are
    # skipped as always
    _plans = [("A-101", "SITE PLAN")] + [(no, t or fl) for fl, no, t in G.plan_sheets()]
    PAGES = ([(f"VILLA_{no.replace('-', '')}", f"{no}  {t}") for no, t in _plans]
             + [(f"VILLA_{no.replace('-', '')}P", f"{no}P  {t} - PRESENTATION")
                for no, t in _plans])
FOOTER = (G.project_line() if PROJECT
          else "PRIVATE VILLA  |  4 BEDROOM  |  696 m2 PLOT")


def draw(dxf_path, ax):
    doc = ezdxf.readfile(dxf_path)
    ctx = RenderContext(doc)
    lp = ctx.current_layout_properties
    lp.set_colors(bg="#FFFFFF")   # else ACI 7 draws white on white
    Frontend(ctx, MatplotlibBackend(ax),
             config=Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE)
             ).draw_layout(doc.modelspace(), finalize=True, layout_properties=lp)


if __name__ == "__main__":
    out = os.path.join(OUT, "VILLA_DRAWING_SET.pdf")
    made = skipped = 0
    with PdfPages(out) as pdf:
        for stem, caption in PAGES:
            src = os.path.join(OUT, stem + ".dxf")
            if not os.path.exists(src):
                print(f"  skip  {stem} (missing)")
                skipped += 1
                continue
            fig = plt.figure(figsize=(16.54, 11.69))      # A3 landscape
            ax = fig.add_axes([0.03, 0.05, 0.94, 0.90])
            ax.set_axis_off()
            draw(src, ax)
            fig.text(0.03, 0.017, caption, fontsize=9, family="monospace")
            fig.text(0.97, 0.017, FOOTER,
                     fontsize=8, family="monospace", ha="right", color="#555555")
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
            made += 1
            print(f"  page  {caption}")
        d = pdf.infodict()
        if PROJECT:
            d["Title"] = f"{getattr(V, 'PROJECT_TITLE', 'Villa')} - Drawing Set"
            d["Subject"] = G.project_line()
        else:
            d["Title"] = "Private Villa - Drawing Set"
            d["Subject"] = "4 bedroom villa, 696 m2 plot, 407 m2 GFA"
    print("")
    print(f"{made} pages, {skipped} skipped -> {out} "
          f"({os.path.getsize(out) // 1024} KB)")
