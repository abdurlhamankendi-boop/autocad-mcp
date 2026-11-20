"""Insert each candidate ACA content block into a scratch drawing and measure
its real extents, so the plan generator can place it correctly instead of
guessing. Writes block_catalog.json."""
import json, os, pythoncom, win32com.client as w
from win32com.client import VARIANT

pythoncom.CoInitialize()
B = r"C:\ProgramData\Autodesk\ACA 2027\enu\AEC Content\Metric\Design"
CANDIDATES = {
    # Static blocks only. The "Dynamic Block 2D" versions carry every
    # visibility state in their extents (a 20m-deep dining table), so they
    # cannot be placed by bounding box.
    "bed_double":   r"Domestic Furniture\Bedroom\Double - plain.dwg",
    "bed_single":   r"Furniture\Home\Single_bed_90x210.dwg",
    "wardrobe":     r"Domestic Furniture\Bedroom\Closet - Double door.dwg",
    "bedside":      r"Furniture\Home\Bedside_Table.dwg",
    "dresser":      r"Domestic Furniture\Bedroom\Dresser.dwg",
    "sofa":         r"Domestic Furniture\Sofas\Classic.dwg",
    "sofa_l":       r"Domestic Furniture\Sofas\L-shape.dwg",
    "coffee_table": r"Furniture\Home\Coffee_table_elliptical_1200x700.dwg",
    "dining":       r"Furniture\Home\Dining_area_rectangular_4_person.dwg",
    "wc":           r"Bathroom\Toilet\Flush - Modern.dwg",
    "bath":         r"Bathroom\Bath\Tub - Rectangular 1700x800.dwg",
    "basin":        r"Bathroom\Basin\Oval.Dwg",
    "fridge":       r"Appliances\Kitchen\Fridge_Freezer.dwg",
    "hob":          r"Appliances\Kitchen\Ceramic_hob_6M.dwg",
    "dishwasher":   r"Appliances\Kitchen\Dishwasher_6M.dwg",
    "sink_unit":    r"Kitchen Fittings\Base Cabinet\Base_Cabinet-Double_Door_Sink_Unit.dwg",
}

def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x), float(y), float(z)])

SCALE = 25.4   # inch-authored content -> millimetre drawing

app = w.GetActiveObject("AutoCAD.Application")
doc = app.Documents.Add()
# AutoCAD scales an inserted block by source INSUNITS / target INSUNITS. The
# default template is imperial, so metric content came in at 1/25.4 size.
doc.SetVariable("INSUNITS", 4)      # 4 = millimetres
ms = doc.ModelSpace
out = {}
for key, rel in CANDIDATES.items():
    full = os.path.join(B, rel)
    if not os.path.exists(full):
        out[key] = {"error": "not found", "path": rel}
        print(f"  MISSING  {key:14s} {rel}")
        continue
    try:
        # Despite living under "Metric", this content is authored in INCHES
        # (a 1600x2000 bed is drawn 63x79). Inserted at 1.0 into a millimetre
        # drawing it comes in 25.4x too small.
        ref = ms.InsertBlock(pt(0, 0), full, SCALE, SCALE, SCALE, 0.0)
        lo, hi = ref.GetBoundingBox()
        wdt, dep = hi[0] - lo[0], hi[1] - lo[1]
        out[key] = {"path": full, "scale": SCALE,
                    "w": round(wdt, 1), "d": round(dep, 1),
                    "offx": round(lo[0], 1), "offy": round(lo[1], 1)}
        print(f"  OK       {key:14s} {wdt:7.0f} x {dep:7.0f}  origin offset "
              f"({lo[0]:.0f},{lo[1]:.0f})")
        ref.Delete()
    except Exception as exc:
        out[key] = {"error": str(exc)[:90], "path": rel}
        print(f"  FAIL     {key:14s} {str(exc)[:60]}")

doc.Close(False)
dst = r"C:\Users\lsire\autocad-mcp\block_catalog.json"
json.dump(out, open(dst, "w"), indent=2)
print("\nwrote", dst)
