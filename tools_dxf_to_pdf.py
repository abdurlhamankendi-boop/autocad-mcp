"""Plot DXF sheets to PDF at TRUE SCALE on a fixed paper size, without AutoCAD.

    python tools_dxf_to_pdf.py OUT_DIR SRC.dxf=NAME.pdf[:mono|colour] ...
        [--paper 841x594] [--scale 100]

ezdxf's PyMuPDF backend: vector output, the model space's extents centred on
the page at 1:SCALE (drawing units are mm), white paper; 'mono' prints every
colour black (the AutoCAD monochrome.ctb look), 'colour' keeps the fills.
Refuses a sheet whose extents do not fit the paper at that scale (it would be
clipped) -- say so rather than shrink it.
"""
from __future__ import annotations

import os
import sys

import ezdxf
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
from ezdxf.addons.drawing.config import (BackgroundPolicy, ColorPolicy,
                                         Configuration, LineweightPolicy)


def plot(src, dst, mono, paper=(841.0, 594.0), scale=100.0):
    doc = ezdxf.readfile(src)
    msp = doc.modelspace()
    ext = bbox.extents(msp, fast=True)
    w = (ext.extmax.x - ext.extmin.x) / scale
    h = (ext.extmax.y - ext.extmin.y) / scale
    pw, ph = paper
    if w > pw or h > ph:
        if w <= ph and h <= pw:
            pw, ph = ph, pw                    # portrait fits
        else:
            raise SystemExit(f"{os.path.basename(src)}: {w:.0f} x {h:.0f} mm at 1:{scale:.0f} "
                             f"does not fit {paper[0]:.0f} x {paper[1]:.0f}")
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE,
                        color_policy=ColorPolicy.BLACK if mono else ColorPolicy.COLOR,
                        lineweight_policy=LineweightPolicy.ABSOLUTE)
    backend = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(msp, finalize=True)
    page = layout.Page(pw, ph, layout.Units.mm, margins=layout.Margins.all(0))
    settings = layout.Settings(scale=1.0 / scale, fit_page=False)
    data = backend.get_pdf_bytes(page, settings=settings)
    with open(dst, "wb") as f:
        f.write(data)
    return w, h, pw, ph


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    paper, scale = (841.0, 594.0), 100.0
    if "--paper" in args:
        i = args.index("--paper"); a, b = args[i + 1].split("x"); paper = (float(a), float(b)); del args[i:i + 2]
    if "--scale" in args:
        i = args.index("--scale"); scale = float(args[i + 1]); del args[i:i + 2]
    out = args[0]
    os.makedirs(out, exist_ok=True)
    for spec in args[1:]:
        src, rest = spec.split("=", 1)
        name, _, mode = rest.partition(":")
        w, h, pw, ph = plot(src, os.path.join(out, name), mode != "colour", paper, scale)
        print(f"{name:45s} {w:5.0f} x {h:4.0f} mm on {pw:.0f} x {ph:.0f} at 1:{scale:.0f}  "
              f"({'mono' if mode != 'colour' else 'colour'})")
