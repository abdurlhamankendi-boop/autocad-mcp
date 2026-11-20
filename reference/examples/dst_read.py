"""Read an AutoCAD Sheet Set (.dst) file WITHOUT AutoCAD.

A .dst is UTF-8 XML hidden behind a fixed per-byte substitution:

    stored = ((plain + 0x11) & 0xFF) ^ 0x9D      so      plain = ((stored ^ 0x9D) - 0x11) & 0xFF

The constants were recovered by known-plaintext search on the XML prolog
(`<?xml version="1.0" encoding="UTF-8"?>`), and the decode is accepted only if
the whole result parses as XML (every sample on this PC does).

Read-only. No COM. Usage:
    python dst_read.py "path\\to\\set.dst"            -> prints JSON summary
    python dst_read.py "path\\to\\set.dst" --xml out   -> also writes decoded XML
"""

from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET


def decode(raw: bytes) -> bytes:
    return bytes((((c ^ 0x9D) - 0x11) & 0xFF) for c in raw)


def _props(el):
    """Direct AcSmProp children -> {propname: text}."""
    out = {}
    for p in el.findall("AcSmProp"):
        name = p.get("propname")
        if name and (p.text or "").strip():
            out[name] = p.text.strip()
    return out


def _custom(el):
    """AcSmCustomPropertyBag -> {name: value}. Flags 1 = sheet-set level,
    2 = per-sheet (the title-block fields a sheet fills in)."""
    out = {}
    bag = el.find("AcSmCustomPropertyBag")
    if bag is None:
        return out
    for v in bag.findall("AcSmCustomPropertyValue"):
        pv = _props(v)
        out[v.get("propname")] = {"value": pv.get("Value", ""),
                                  "flags": pv.get("Flags", "")}
    return out


def _layout_file(sheet):
    ref = sheet.find("AcSmAcDbLayoutReference")
    if ref is None:
        return None, None
    pr = _props(ref)
    return pr.get("Relative_FileName") or pr.get("FileName"), pr.get("Name")


def _walk(node, path, sheets, subsets):
    for child in node:
        if child.tag == "AcSmSubset":
            name = _props(child).get("Name", "?")
            subsets.append("/".join(path + [name]))
            _walk(child, path + [name], sheets, subsets)
        elif child.tag == "AcSmSheet":
            pr = _props(child)
            f, layout = _layout_file(child)
            views = []
            sv = child.find("AcSmSheetViews")
            if sv is not None:
                for v in sv.findall("AcSmSheetView"):
                    vp = _props(v)
                    views.append({"number": vp.get("Number", ""),
                                  "title": vp.get("Title", "")})
            sheets.append({
                "subset": "/".join(path),
                "number": pr.get("Number", ""),
                "title": pr.get("Title", ""),
                "desc": pr.get("Desc", ""),
                "file": f, "layout": layout,
                "custom": {k: v["value"] for k, v in _custom(child).items()},
                "views": views,
            })


def read_dst(path: str) -> dict:
    raw = open(path, "rb").read()
    xml = decode(raw)
    root = ET.fromstring(xml)            # raises if the decode is wrong
    ss = root.find("AcSmSheetSet")
    sheets, subsets = [], []
    _walk(ss, [], sheets, subsets)
    set_props = _props(ss)
    set_custom = _custom(ss)
    cats = []
    vc = ss.find("AcSmViewCategories")
    if vc is not None:
        for c in vc.findall("AcSmViewCategory"):
            cats.append(_props(c).get("Name", ""))
    return {
        "file": path,
        "bytes": len(raw),
        "decoded_ok": True,
        "sheet_set_name": set_props.get("Name", ""),
        "sheet_set_desc": set_props.get("Desc", ""),
        "custom_properties": {k: {"flags": v["flags"],
                                  "scope": {"1": "sheet set", "2": "sheet"}.get(
                                      v["flags"], v["flags"])}
                              for k, v in set_custom.items()},
        "subsets": subsets,
        "view_categories": cats,
        "sheets": sheets,
    }, xml


if __name__ == "__main__":
    info, xml = read_dst(sys.argv[1])
    if "--xml" in sys.argv:
        out = sys.argv[sys.argv.index("--xml") + 1]
        open(out, "wb").write(xml)
    print(json.dumps(info, indent=1, ensure_ascii=False))
