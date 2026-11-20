"""Open a professionally-authored sample drawing and dump its drafting
conventions: layers + lineweights, text heights, dimension styles, blocks,
hatch patterns. Reading a real DWG teaches structure that prose cannot."""
import sys, pythoncom, win32com.client as w
from collections import Counter, defaultdict
pythoncom.CoInitialize()
path = sys.argv[1]
app = w.GetActiveObject("AutoCAD.Application")
doc = app.Documents.Open(path, True)   # read-only
print("=" * 68)
print("STUDY:", doc.Name)
ms = doc.ModelSpace
print("modelspace entities:", ms.Count)

print("\n-- LAYERS (name, colour, lineweight 1/100mm, linetype) --")
rows = []
for l in doc.Layers:
    # read each property separately: under early binding some IAcadLayer
    # accessors raise, and one failure was discarding the whole row
    def g(fn, default="?"):
        try: return fn()
        except Exception: return default
    rows.append((g(lambda: str(l.Name)), g(lambda: int(l.Color)),
                 g(lambda: int(l.Lineweight)), g(lambda: str(l.Linetype))))
for r in sorted(rows)[:40]:
    print(f"  {str(r[0]):26s} c{str(r[1]):<5} lw{str(r[2]):<6} {r[3]}")
print(f"  ...{len(rows)} layers total")

print("\n-- ENTITY MIX --")
c = Counter(); lay = Counter(); th = Counter(); pat = Counter()
for e in ms:
    n = str(e.EntityName); c[n] += 1
    try: lay[str(e.Layer)] += 1
    except Exception: pass
    if n in ("AcDbText", "AcDbMText"):
        try: th[round(float(e.Height), 1)] += 1
        except Exception: pass
    if n == "AcDbHatch":
        try: pat[str(e.PatternName)] += 1
        except Exception: pass
for k, v in c.most_common(12): print(f"  {v:5d}  {k}")

print("\n-- BUSIEST LAYERS --")
for k, v in lay.most_common(12): print(f"  {v:5d}  {k}")
print("\n-- TEXT HEIGHTS USED --")
for k, v in th.most_common(10): print(f"  {v:5d} x  {k}")
print("\n-- HATCH PATTERNS USED --")
for k, v in pat.most_common(10): print(f"  {v:5d} x  {k}")

print("\n-- DIMENSION STYLES --")
for ds in doc.DimStyles:
    print("  ", ds.Name)
print("\n-- BLOCKS (non-anonymous) --")
bl = [str(b.Name) for b in doc.Blocks if not str(b.Name).startswith("*")]
print("  count:", len(bl)); print("  ", ", ".join(sorted(bl)[:22]))
doc.Close(False)
