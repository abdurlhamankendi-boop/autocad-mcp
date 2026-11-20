"""render.py P [zoom] [x0 y0 x1 y1] -- render 1-based pdf page P to dbc/img/pP.png (optional clip in pt)."""
import os
import sys

import pymupdf

SRC = r"C:\Users\lsire\autocad-mcp\reference\DBC_2021.pdf"
OUTD = r"C:\Users\lsire\autocad-mcp\reference\dbc\img"
os.makedirs(OUTD, exist_ok=True)
p = int(sys.argv[1])
z = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
doc = pymupdf.open(SRC)
page = doc[p - 1]
clip = None
suffix = ""
if len(sys.argv) > 6:
    clip = pymupdf.Rect(*map(float, sys.argv[3:7]))
    suffix = "_clip"
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
out = os.path.join(OUTD, f"p{p}{suffix}.png")
pix.save(out)
print(out, page.rect, pix.width, pix.height)
