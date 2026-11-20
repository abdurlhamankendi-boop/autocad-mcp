"""Load the villa into AutoCAD: DXF sheets + real ACA content blocks.

COM is used only for what it uniquely provides -- inserting blocks from the
content library and saving DWG. The drawing itself was authored by ezdxf.

Documents are tracked BY NAME. SendCommand, Open and SaveAs all invalidate COM
proxies, and trusting ActiveDocument after one of them is how a finished sheet
once got overwritten.
"""

import json
import math
import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_design as V
import villa_geom as G

OUT = G.out_dir()                   # VILLA_OUT redirects it
MANIFEST = os.path.join(OUT, "furniture_manifest.json")

# (sheet no, file base, plan floor). A sheet's plan floor carries every floor
# villa_geom.sheet_floors() draws on it: the annex's furniture (floor "AX")
# lands on the ground-floor sheets, beside the annex villa_cad drew there, and
# a basement's (floor "B1") on the basement sheets.


def _base(no):
    return "VILLA_" + no.replace("-", "")


def sheet_list():
    """Every sheet villa_cad / villa_colour write, from villa_geom.plan_sheets():
    the site plan A-101 (no plan floor), each plan sheet, then the coloured
    presentation set (P), same geometry. The villa's order is kept: its roof
    plan's pair (A-104, A-104P, only when the roof has rooms) goes last; a
    design's own PLAN_SHEETS are taken in its order."""
    plans = G.plan_sheets()
    late = [] if getattr(V, "PLAN_SHEETS", None) else [s for s in plans if s[0] == "RF"]
    main = [s for s in plans if s not in late]
    out = [("A-101", _base("A-101"), None)]
    out += [(no, _base(no), fl) for fl, no, _t in main]
    out += [("A-101P", _base("A-101") + "P", None)]
    out += [(no + "P", _base(no) + "P", fl) for fl, no, _t in main]
    for fl, no, _t in late:
        out += [(no, _base(no), fl), (no + "P", _base(no) + "P", fl)]
    return out


SHEETS = sheet_list()

FIXTURES = {"wc", "basin", "bath", "shower", "shower_seat",
            "sink_unit", "hob", "dishwasher", "fridge"}


def on_sheet(it, floor):
    """Does manifest item `it` belong on the plan sheet for `floor`?"""
    return (it.get("sheet") == floor
            or it["floor"] in G.sheet_floors(floor))

pythoncom.CoInitialize()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def app():
    return w.GetActiveObject("AutoCAD.Application")


def get_doc(a, name, folder=None):
    # by name AND folder: projects share sheet names (villa_geom.find_doc).
    # The block packs are the same library in every project: by name.
    return G.find_doc(a, name, OUT if folder is None else folder or None)


def close_if_open(name):
    a = app()
    d = get_doc(a, name)
    if d is not None:
        try:
            d.Close(False)
        except Exception:
            pass


def ensure_layer(doc, name):
    try:
        return doc.Layers.Item(name)
    except Exception:
        return doc.Layers.Add(name)


def busy(exc):
    t = str(exc).lower()
    # A busy AutoCAD can also refuse the late-bound NAME lookup, which pywin32
    # reports as AttributeError("AutoCAD.Application.Documents") -- not a
    # missing attribute, a rejected call, and the whole-job retry must see it.
    # Same for a proxy gone stale mid-run: AttributeError("<unknown>.Count").
    return ("rejected" in t or "-2147418111" in t or "busy" in t
            or "call was rejected" in t
            or (isinstance(exc, AttributeError)
                and ("autocad.application" in t or t.startswith("<unknown>."))))


BLOCKS_DIR = os.path.join(OUT, "blocks")


def objs(items):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(items))


def find_block(doc, name):
    for i in range(doc.Blocks.Count):
        b = doc.Blocks.Item(i)
        if str(b.Name) == name:
            return b
    return None


def open_pack(pack):
    """Library drawings are opened once and reused. They are the source of the
    definitions, never something to insert whole."""
    a = app()
    d = get_doc(a, pack, "")
    if d is None:
        a.Documents.Open(os.path.join(BLOCKS_DIR, pack))
        d = get_doc(a, pack, "")
    return d


def ensure_definition(doc, pack, block):
    """Copy a block definition into `doc` if it is not already there.

    Not via -WBLOCK: that prompts for the block name on the command line, where
    a SPACE is Enter, so a block called "PNL 15C Bed Plan" can never be typed.
    It wedged AutoCAD mid-prompt and took COM down with it.
    """
    if find_block(doc, block) is not None:
        return True
    src = open_pack(pack)
    sb = find_block(src, block)
    if sb is None:
        return False
    ents = [e for e in sb]
    if not ents:
        return False
    dst = find_block(doc, block) or doc.Blocks.Add(pt(0, 0), block)
    src.CopyObjects(objs(ents), dst)
    return True


def load_sheet(sheet_no, base, floor, items):
    dxf = os.path.join(OUT, base + ".dxf")
    dwg = os.path.join(OUT, base + ".dwg")
    close_if_open(base + ".dwg")
    close_if_open(base + ".dxf")

    a = app()
    a.Documents.Open(dxf)
    doc = get_doc(a, base + ".dxf")
    if doc is None:
        raise RuntimeError(f"{base}.dxf did not open")
    doc.SetVariable("INSUNITS", 4)

    placed, failed = 0, []
    if floor:
        ensure_layer(doc, "A-FURN")
        ensure_layer(doc, "A-FLOR-FIXT")
        ms = doc.ModelSpace
        for it in items:
            if not on_sheet(it, floor):
                continue
            try:
                # AutoCAD applies its own unit conversion on insert, and it is
                # not consistent between drawings -- the ground floor came in
                # 25.4x oversize while the first floor was exact. So do not
                # trust a scale factor: insert at 1, MEASURE, then scale and
                # move onto the footprint the validated plan demands.
                fp = it["fp"]
                if it.get("pack"):
                    if not ensure_definition(doc, it["pack"], it["block"]):
                        failed.append(f'{it["key"]}: definition not in pack')
                        continue
                    src = it["block"]
                else:
                    src = it["path"]
                ref = ms.InsertBlock(pt(0, 0), src, 1.0, 1.0, 1.0,
                                     math.radians(it["rot"]))
                lo, hi = ref.GetBoundingBox()
                aw, ad = hi[0] - lo[0], hi[1] - lo[1]
                ew, ed = fp[2] - fp[0], fp[3] - fp[1]
                if aw > 1e-6 and ad > 1e-6:
                    k = min(ew / aw, ed / ad)
                    if abs(k - 1.0) > 1e-4:
                        ref.ScaleEntity(pt(0, 0), k)
                lo, hi = ref.GetBoundingBox()
                ref.Move(pt(lo[0], lo[1]), pt(fp[0], fp[1]))
                ref.Layer = ("A-FLOR-FIXT" if it["key"] in FIXTURES
                             else "A-FURN")
                placed += 1
            except Exception as exc:
                # A COM busy error is not this block's problem -- it is the
                # whole job's. Swallowing it here defeats the outer retry and
                # leaves the sheet half-furnished, which is what happened.
                if busy(exc):
                    raise
                failed.append(f'{it["key"]}: {str(exc)[:60]}')

    a = app()
    doc = get_doc(a, base + ".dxf")
    n = int(doc.ModelSpace.Count)
    doc.SaveAs(dwg)
    return placed, failed, n


def run(sheets=None, done=None):
    """Load `sheets`, recording each success in `done` so a retry resumes
    rather than starting over -- restarting from sheet one meant the job never
    reached sheet three."""
    items = json.load(open(MANIFEST))
    results = []
    for sheet_no, base, floor in (sheets if sheets is not None else SHEETS):
        if done is not None and sheet_no in done:
            continue
        placed, failed, n = load_sheet(sheet_no, base, floor, items)
        results.append((sheet_no, base, placed, failed, n))
        if done is not None:
            done.add(sheet_no)
        print(f"{sheet_no}  {n:>4} entities, {placed:>2} blocks inserted"
              + (f", {len(failed)} FAILED" if failed else ""))
        for f in failed[:5]:
            print("      !", f)
    return results


if __name__ == "__main__":
    last = None
    done = set()
    for attempt in range(10):
        try:
            run(SHEETS, done)
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy after {len(done)}/{len(SHEETS)} sheets, "
                  f"resuming ({attempt + 1})...")
            time.sleep(12)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
