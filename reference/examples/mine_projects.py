"""Mine the example drawing sets already on this PC (read-only, no AutoCAD).

  * ACA 'ACA Malliprojekti (FIN)'  -- two-storey Finnish house (closest to the villa)
  * ACA 'Sample Project 2027'      -- 4-storey office
  * AutoCAD 'Sheet Sets\\Architectural' (IRD Addition)

For each: project XML (.apj: levels, divisions, detail fields), the
Construct/Element/View/Sheet tree with each drawing's sidecar XML (levels it
spans, view type, viewport scales), the sheet set (.dst, decoded by
dst_read.py), and per sheet DWG: embedded preview -> PNG, object census,
title-block field codes, xref paths and AIA-style layer names (dwg_read.py).

Personal data: detail-field VALUES and 'Drawn By'/'Checked By' are dropped;
only field NAMES are kept. Strings equal to any detail value are redacted.

Output: out\\projects.json, thumbs\\<set>\\*.png, thumbs\\<set>_contact.png
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET

import dst_read
import dwg_read as D

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "out")
THUMBS = os.path.join(HERE, "thumbs")
MYPROJ = r"C:\Users\lsire\OneDrive\Documents\Autodesk\My Projects"
SETS = {
    "fin_house": {
        "root": os.path.join(MYPROJ, "ACA Malliprojekti (FIN)"),
        "apj": "ACA Malliprojekti (FIN).apj",
        "dst": "ACA Malliprojekti (FIN).dst",
        "units": "mm",
        # schedule views (door list, space list) and the 3D/space views
        "key_views": [r"Views\Työpiirustukset\Luettelot\2009-Ovet.dwg",
                      r"Views\Työpiirustukset\Luettelot\2009-Tilat.dwg",
                      r"Views\Työpiirustukset\Tilat\2009-Tilakaavio 3d View.dwg",
                      r"Views\Työpiirustukset\Mallit\2009-Mallitalo.dwg"],
    },
    "office": {
        "root": os.path.join(MYPROJ, "Sample Project 2027"),
        "apj": "Sample Project.apj",
        "dst": "Sample Project.dst",
        "units": "inch",
        "key_views": [r"Views\Architectural\Schedules\Schedule Model.dwg",
                      r"Views\Architectural\Isometric 3D\Perspective.dwg",
                      r"Views\Architectural\Space Planning\01 Space Plan.dwg"],
    },
    "ird_sheetset": {
        "root": r"C:\Program Files\Autodesk\AutoCAD 2027\Sample\Sheet Sets"
                r"\Architectural",
        "apj": None,
        "dst": "IRD Addition.dst",
        "units": "inch",
        "key_views": [],
    },
}
PERSONAL_FIELDS = {"Drawn By", "Checked By"}
# field codes as stored in FIELD objects: \AcSm Sheet.Number \f "%tc1" etc.
FIELD_RE = re.compile(r"(\\AcSm \??[A-Za-z]+\.[A-Za-z ]+?|\\AecPr (?:\"[^\"]*\""
                      r"\s?)+|\\AcVar [A-Za-z]+)(?=\s*\\f|\s*$|\s*>|\s*%)")
AIA_LAYER = re.compile(r"^[A-Z]{1,2}-[A-Za-z]{4}(?:-[A-Za-z0-9]{2,4})*$")
XREF_LAYER = re.compile(r"^[^|\\/]{1,80}\|(?P<layer>[A-Za-z0-9_\-$ ]{2,48})$")
XREF_RE = re.compile(r"\.dwg$", re.I)
LABEL_RE = re.compile(r"^[A-ZÄÖÅ][A-ZÄÖÅ &/.:'-]{2,38}[A-ZÄÖÅ:]$")
SCHED_RE = re.compile(r"(?i)(schedule|luettelo|^\[[A-Za-z]+\](\[[A-Za-z]+\])*$|"
                      r"numbering|number|numero|tunnus|finish|hardware|"
                      r"fire rating|paloluokka|pinta-ala|area|leveys|width|"
                      r"korkeus|height)")


# ------------------------------------------------------------------ .apj
def parse_apj(path):
    root = ET.parse(path).getroot()
    levels = []
    for lv in root.findall("Level"):
        levels.append({k: lv.get(k) for k in ("Name", "Description", "Id",
                                               "ScheduleId")}
                      | {"Elevation": float(lv.get("Elevation")),
                         "Height": float(lv.get("Height"))})
    levels.sort(key=lambda r: r["Elevation"])
    elevs = [lv["Elevation"] for lv in levels]
    chain_exceptions = []
    for lv in levels:
        top = lv["Elevation"] + lv["Height"]
        above = [e for e in elevs if e > lv["Elevation"]]
        lv["next_level_elevation"] = min(above) if above else None
        lv["top"] = top
        lv["top_matches_a_level"] = top in elevs
        if above and top not in elevs:
            chain_exceptions.append(
                f"{lv['Name']}: {lv['Elevation']:g} + {lv['Height']:g} = "
                f"{top:g} is not a level elevation")
    details, secret = {}, set()
    for d in root.findall("Details"):
        details[d.get("Name")] = [
            {"field": e.get("Name"), "value_present": bool(e.get("Value"))}
            for e in d.findall("Entry")]
        secret |= {e.get("Value") for e in d.findall("Entry")
                   if e.get("Value") and len(e.get("Value")) > 3}
    tmpl = {t.tag: (t.text or "").strip() for t in root.find("Templates")}
    locs = {t.tag: (t.text or "").strip() for t in root.find("FileLocations")
            if t.tag.endswith("Location")}
    std = root.find("Standards/AECStandards/File")
    return {
        "name": root.get("Name"), "number": root.get("Number"),
        "description": (root.findtext("Description") or "").strip(),
        "use_number_prefix": root.get("UseNumberPrefix"),
        "templates": tmpl, "locations": locs,
        "standards_file": std.findtext("Path") if std is not None else None,
        "standards_objects": [o.text for o in std.findall("Objects/Object")]
        if std is not None else [],
        "levels": levels,
        "levels_chain_exceptions": chain_exceptions,
        "divisions": [{k: dv.get(k) for k in ("Name", "Id", "ScheduleId")}
                      for dv in root.findall("Division")],
        "detail_fields": details,
    }, secret


# ------------------------------------------------------------------ tree
def sidecar(xml_path, level_names):
    try:
        r = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError):
        return {"sidecar": "unreadable"}
    out = {}
    cells = r.findall("Region/Cell")
    if cells:
        out["levels"] = sorted({level_names.get(c.get("Level"), c.get("Level"))
                                for c in cells})
        out["divisions"] = sorted({c.get("Division") for c in cells})
    v = r.find("View")
    if v is not None:
        out["view_type"] = v.findtext("ViewType")
        out["viewport_scales"] = sorted(
            {int(float(s.text)) for s in v.findall("ViewportDefault/"
                                                    "ViewportScale")
             if s.text and float(s.text) > 1})
        out["display_configs"] = sorted(
            {s.text for s in v.findall("ViewportDefault/DispConfig") if s.text})
        out["context_categories"] = len(v.findall("ViewCategory/"
                                                  "ContextCategory"))
        out["file_overrides"] = len(v.findall("ViewCategory/FileOverride"))
    return out


def tree(root, level_names):
    out = {}
    for kind in ("Constructs", "Elements", "Views", "Sheets"):
        base = os.path.join(root, kind)
        if not os.path.isdir(base):
            continue
        rows = []
        for dp, _dn, fn in os.walk(base):
            for f in sorted(fn):
                if not f.lower().endswith(".dwg"):
                    continue
                p = os.path.join(dp, f)
                rec = {"file": os.path.relpath(p, root),
                       "folder": os.path.relpath(dp, base),
                       "bytes": os.path.getsize(p)}
                x = p[:-4] + ".xml"
                if os.path.exists(x):
                    rec.update(sidecar(x, level_names))
                rows.append(rec)
        out[kind] = sorted(rows, key=lambda r: r["file"])
    return out


# ------------------------------------------------------------------ sheets
def mine_dwg(path, secret, want_png=None, want_sched=False):
    data = open(path, "rb").read()
    rec = {"version": data[:6].decode("ascii", "replace")}
    png = D.preview_png(data)
    rec["preview"] = bool(png)
    if png and want_png:
        os.makedirs(os.path.dirname(want_png), exist_ok=True)
        open(want_png, "wb").write(png)
        rec["thumb"] = os.path.relpath(want_png, HERE)
    try:
        secs, _cls, ot = D.census(data)
        keep = ("TEXT", "MTEXT", "ATTRIB", "ATTDEF", "INSERT", "VIEWPORT",
                "FIELD", "LAYOUT", "HATCH", "DIMENSION_LINEAR",
                "DIMENSION_ALIGNED", "3DSOLID", "3DFACE")
        rec["census"] = {k: ot[k] for k in keep if ot.get(k)}
        # AEC building objects (not styles/display reps/definitions)
        rec["aec_objects"] = {
            k: v for k, v in sorted(ot.items()) if k.startswith(("AEC_",
                                                                  "AECS_"))
            and not any(t in k for t in ("DISP", "STYLE", "VARS", "_DEF",
                                         "DEFS", "LIST", "CLASSIFICATION",
                                         "FORMAT", "TRACKER", "PROPOSAL",
                                         "NAMES", "MODIFIER", "RENOVATION",
                                         "_CONTENT", "_TEMPLATE", "MATERIAL",
                                         "LAYER_KEY", "LAYERKEY"))}
        strs = D.readable(D.utf16_strings(secs["AcDb:AcDbObjects"], 3), 0.5)
    except (D.DwgError, KeyError, IndexError) as e:
        rec["error"] = f"{type(e).__name__}: {e}"
        return rec, set(), set()
    fields, xrefs, labels, aia, other = set(), set(), set(), set(), set()
    sched = []
    for s in strs:
        if any(v and v in s for v in secret):
            continue
        for m in FIELD_RE.finditer(s):
            fields.add(m.group(1).strip())
        if XREF_RE.search(s) and ("\\" in s or s.startswith(".")):
            xrefs.add(s.replace("C:\\ACA\\BSD\\MyDocs", "<orig>"))
            continue
        xm = XREF_LAYER.match(s)
        name = xm.group("layer") if xm else s
        if AIA_LAYER.match(name):
            aia.add(name)
        elif xm:
            other.add(name)
        elif LABEL_RE.match(s) and (" " in s or s.endswith(":")) \
                and len(s.split()) <= 6:
            labels.add(s)
        if SCHED_RE.search(s) and len(s) <= 60 and "Aec" not in s \
                and "<" not in s and s not in sched:
            sched.append(s)
    rec["field_codes"] = sorted(fields)
    rec["xrefs"] = sorted(xrefs)
    rec["labels"] = sorted(labels)[:80]
    if want_sched:
        rec["schedule_related_strings"] = sched[:150]
    return rec, aia, other


def numbering(sheets):
    """Infer the numbering pattern of a sheet list."""
    pats = {}
    for s in sheets:
        n = s["number"]
        p = re.sub(r"[A-Z]", "L", re.sub(r"\d", "9", n))
        pats.setdefault(p, []).append(n)
    return {p: v for p, v in sorted(pats.items())}


def contact_sheet(items, out_png, title):
    """Grid of thumbnails with their sheet numbers (Pillow)."""
    from PIL import Image, ImageDraw
    items = [(lab, os.path.join(HERE, t)) for lab, t in items if t]
    if not items:
        return None
    cell_w, cell_h, cols = 300, 230, 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h + 30), "white")
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), title, fill="black")
    for i, (lab, p) in enumerate(items):
        im = Image.open(p).convert("RGB")
        im.thumbnail((cell_w - 10, cell_h - 30))
        x, y = (i % cols) * cell_w + 5, (i // cols) * cell_h + 35
        sheet.paste(im, (x, y))
        dr.text((x, y + im.size[1] + 2), lab[:44], fill="black")
    sheet.save(out_png)
    return os.path.relpath(out_png, HERE)


def mine_set(key, cfg):
    root = cfg["root"]
    res = {"key": key, "root": root, "units": cfg["units"]}
    secret, level_names = set(), {}
    if cfg["apj"]:
        apj, secret = parse_apj(os.path.join(root, cfg["apj"]))
        res["project"] = apj
        level_names = {lv["Id"]: lv["Name"] for lv in apj["levels"]}
        res["tree"] = tree(root, level_names)
        res["tree_counts"] = {k: len(v) for k, v in res["tree"].items()}
    dinfo, _xml = dst_read.read_dst(os.path.join(root, cfg["dst"]))
    for s in dinfo["sheets"]:
        s["custom"] = {k: v for k, v in s["custom"].items()
                       if k not in PERSONAL_FIELDS}
    res["sheet_set"] = {k: v for k, v in dinfo.items() if k != "sheets"}
    res["sheet_set"]["custom_properties"] = {
        k: v for k, v in dinfo["custom_properties"].items()}
    res["numbering_patterns"] = numbering(dinfo["sheets"])
    all_layers, other_layers, sheets, anomalies = set(), set(), [], []
    for s in dinfo["sheets"]:
        rel = s["file"] or ""
        p = os.path.normpath(os.path.join(root, rel))
        rec = dict(s)
        if not os.path.exists(p):
            rec["missing"] = True
            anomalies.append(f"{s['number']}: file {rel} missing")
        else:
            safe = re.sub(r"[^A-Za-z0-9_-]+", "_", s["number"] or "x")
            m, lay, oth = mine_dwg(p, secret, os.path.join(THUMBS, key,
                                                           safe + ".png"))
            rec.update(m)
            all_layers |= lay
            other_layers |= oth
            base = os.path.basename(p)
            if s["number"] and s["number"] not in base:
                anomalies.append(f"{s['number']}: file name '{base}' does not "
                                 "carry the sheet number")
        sub = s["subset"].split("/")[-1] if s["subset"] else ""
        mm = re.match(r"([A-Z]\d{2})", sub)
        if mm and not s["number"].startswith(mm.group(1)):
            anomalies.append(f"{s['number']}: filed under subset '{sub}'")
        sheets.append(rec)
    idx = [s["custom"].get("Sheet Index") for s in sheets]
    if any(i for i in idx):
        bad = [s["number"] for s in sheets
               if not (s["custom"].get("Sheet Index") or "").isdigit()]
        if bad:
            anomalies.append("Sheet Index not numeric on: " + ", ".join(bad))
    res["sheets"] = sheets
    res["anomalies"] = anomalies
    views = []
    for rel in cfg.get("key_views", []):
        p = os.path.join(root, rel)
        safe = "view_" + re.sub(r"[^A-Za-z0-9_-]+", "_",
                                os.path.basename(rel)[:-4])
        m, lay, oth = mine_dwg(p, secret, os.path.join(THUMBS, key,
                                                       safe + ".png"),
                               want_sched=True)
        all_layers |= lay
        other_layers |= oth
        views.append({"file": rel} | m)
    res["key_views"] = views
    res["aia_style_layers_seen"] = sorted(all_layers, key=str.upper)
    res["other_xref_layers_seen"] = sorted(other_layers, key=str.upper)[:200]
    res["contact_sheet"] = contact_sheet(
        [(f"{s['number']} {s['title']}", s.get("thumb")) for s in sheets]
        + [(os.path.basename(v["file"])[:-4], v.get("thumb")) for v in views],
        os.path.join(THUMBS, key + "_contact.png"),
        f"{key}: embedded DWG previews (dwg_read.preview) - sheets, then "
        "key views")
    return res


def extra_ird(res):
    """IRD sample: the model resource drawings under Res\\ + the .dwt."""
    root = SETS["ird_sheetset"]["root"]
    res["resource_drawings"] = []
    for f in sorted(os.listdir(os.path.join(root, "Res"))):
        if f.lower().endswith(".dwg"):
            m, _, _ = mine_dwg(os.path.join(root, "Res", f), set(),
                               os.path.join(THUMBS, "ird_sheetset", "Res_" +
                                            re.sub(r"\W+", "_", f[:-4])
                                            + ".png"))
            res["resource_drawings"].append({"file": "Res\\" + f} | m)
    tpl = os.path.join(root, "IRD.dwt")
    m, _, _ = mine_dwg(tpl, set(), os.path.join(THUMBS, "ird_sheetset",
                                                "IRD_dwt.png"))
    res["template"] = {"file": "IRD.dwt"} | m


def fin_guide():
    """The FIN project ships a 26-page Finnish PDF guide: record its page
    headings (first line) so examples.md can cite pages."""
    import pymupdf
    p = os.path.join(SETS["fin_house"]["root"], "ACA_Malliprojekti.pdf")
    doc = pymupdf.open(p)
    pages = []
    for i, pg in enumerate(doc):
        lines = [ln.strip() for ln in pg.get_text().splitlines() if ln.strip()]
        head = next((ln for ln in lines[:4] if not ln.isdigit()), "")
        pages.append({"page": i + 1, "heading": head[:60],
                      "chars": sum(len(ln) for ln in lines)})
    return {"file": p, "pages": doc.page_count, "creator":
            doc.metadata.get("creator"), "page_headings": pages}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    result = {}
    for key, cfg in SETS.items():
        r = mine_set(key, cfg)
        if key == "ird_sheetset":
            extra_ird(r)
        result[key] = r
        n = len(r["sheets"])
        pv = sum(1 for s in r["sheets"] if s.get("preview"))
        print(f"{key}: {n} sheets, {pv} previews, "
              f"{len(r['aia_style_layers_seen'])} AIA-style layers, "
              f"{len(r['anomalies'])} anomalies")
    result["fin_house"]["guide_pdf"] = fin_guide()
    out = os.path.join(OUTDIR, "projects.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    print("wrote", out)
    return result


if __name__ == "__main__":
    main()
