"""Export the chosen FIA block definitions to individual DWG files.

InsertBlock takes a FILE, not a block name inside another file, so each wanted
definition is WBLOCKed out on its own before it can be placed. Sizes below are
the measured extents from catalog_new_blocks.py, not the names' promises.
"""

import json
import os
import time

import pythoncom
import win32com.client as w

BLOCKS = r"C:\Users\lsire\OneDrive\Desktop\Villa\blocks"
OUT = os.path.join(BLOCKS, "single")
PACK2 = "Furniture-pack-2-and-3__FIA_Furniture_Cad_Blocks_02.dwg"
PACK3 = "Furniture-pack-2-and-3__FIA_Furniture_Cad_Blocks_03.dwg"

# key -> (pack file, block name, what it replaces)
WANT = [
    ("bed_double",   PACK2, "PNL 15C Bed Plan",      "ACA double bed"),
    ("sofa_long",    PACK2, "ZC 504 Sofa Plan",      "majlis run"),
    ("sofa_3",       PACK2, "CT 03 Sofa plan",       "ACA classic sofa"),
    ("sofa_2",       PACK2, "AS 02 Sofa Plan",       "ACA classic sofa"),
    ("sofa_ph",      PACK2, "PH 03 Sofa Plan",       "living room"),
    ("armchair",     PACK2, "SW01M Arm chair Plan",  "new"),
    ("recliner",     PACK2, "NH 01 Recliner chair Plan", "new"),
    ("table_round",  PACK2, "Circular Table Plan",   "ACA dining"),
    ("table_dining", PACK2, "SP09C Table Plan",      "ACA dining"),
    ("table_coffee", PACK2, "OP 11 Table Plan",      "ACA coffee table"),
    ("table_low",    PACK2, "Sumo Table Plan",       "majlis centre"),
]

pythoncom.CoInitialize()


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def get_doc(a, name):
    for i in range(a.Documents.Count):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def run(state):
    os.makedirs(OUT, exist_ok=True)
    measured = {(m["file"], m["block"]): m for m in
                json.load(open(os.path.join(BLOCKS, "measured_blocks.json")))}
    catalog = {}
    if os.path.exists(os.path.join(OUT, "fia_catalog.json")):
        catalog = json.load(open(os.path.join(OUT, "fia_catalog.json")))

    packs = sorted({p for _, p, _, _ in WANT})
    for pack in packs:
        todo = [x for x in WANT if x[1] == pack and x[0] not in state["done"]]
        if not todo:
            continue
        a = w.GetActiveObject("AutoCAD.Application")
        doc = get_doc(a, pack)
        if doc is None:
            a.Documents.Open(os.path.join(BLOCKS, pack))
            doc = get_doc(a, pack)
        doc.Activate()
        doc.SetVariable("FILEDIA", 0)
        for key, _p, bname, repl in todo:
            dest = os.path.join(OUT, f"{key}.dwg")
            if os.path.exists(dest):
                os.remove(dest)
            doc.SendCommand(f'_.-WBLOCK\n{dest}\n{bname}\n')
            time.sleep(1.2)
            if os.path.exists(dest):
                m = measured.get((pack, bname), {})
                catalog[key] = {"path": dest, "block": bname, "pack": pack,
                                "w": m.get("w"), "d": m.get("d"),
                                "replaces": repl, "source": "First In "
                                "Architecture furniture pack (metric)"}
                state["done"].add(key)
                print(f"  {key:14s} {bname[:30]:30s} "
                      f"{m.get('w', 0):.0f} x {m.get('d', 0):.0f} mm")
            else:
                print(f"  {key:14s} WBLOCK produced no file")
        doc.SetVariable("FILEDIA", 1)
        json.dump(catalog, open(os.path.join(OUT, "fia_catalog.json"), "w"),
                  indent=1)
    print(f"\n{len(state['done'])}/{len(WANT)} blocks exported -> {OUT}")


if __name__ == "__main__":
    last, state = None, {"done": set()}
    for attempt in range(10):
        try:
            run(state)
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy after {len(state['done'])}, "
                  f"resuming ({attempt + 1})...")
            time.sleep(10)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
