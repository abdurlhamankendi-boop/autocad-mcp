"""Independent re-check of every changed or new rule, straight from DBC_2021.pdf (not dbc_text.txt).

For each rule that differs from orig_rules.json (the pre-fix build) or is new:
  - every quote (main + also_quotes) must occur, whitespace-normalised, on its pdf page;
  - the same quote must NOT be the only hit on a neighbouring page (catches off-by-one);
  - printed_page must equal pymupdf's page label;
  - each numeric value must appear somewhere on the rule's cited pages (heuristic; values read
    from figure drawings are expected to miss and are listed separately).
Read-only on the PDF and the JSON.
"""
import json
import re

import pymupdf

PDF = r"C:\Users\lsire\autocad-mcp\reference\DBC_2021.pdf"
NEW = r"C:\Users\lsire\.claude\skills\architectural-cad\references\dubai_villa_rules.json"
OLD = r"C:\Users\lsire\autocad-mcp\reference\dbc\orig_rules.json"

doc = pymupdf.open(PDF)
norm = lambda s: re.sub(r"\s+", " ", s).strip()
_cache = {}


def text(p):
    if p not in _cache:
        _cache[p] = norm(doc[p - 1].get_text("text"))
    return _cache[p]


def label(p):
    raw = doc[p - 1].get_label()

    def rep(m):
        h = m.group(1)
        return "".join(chr(int(h[i:i + 4], 16)) for i in range(0, len(h), 4)).replace("\ufeff", "")
    s = re.sub(r"<([0-9A-Fa-f]+)>", rep, raw)
    m = re.match(r"^([A-Z])(\d+)$", s)
    return f"{m.group(1)} {m.group(2)}" if m else s


old = {r["id"]: r for r in json.load(open(OLD, encoding="utf-8"))["rules"]}
new = {r["id"]: r for r in json.load(open(NEW, encoding="utf-8"))["rules"]}

removed = sorted(set(old) - set(new))
added = [i for i in new if i not in old]
changed = [i for i in new if i in old and new[i] != {**old[i], "also_quotes": new[i]["also_quotes"],
                                                     "note": new[i]["note"]}]
annotated = [i for i in new if i in old and i not in changed and (new[i]["also_quotes"] or new[i]["note"])]
print(f"removed {removed}\nchanged ({len(changed)}) {changed}\nnote/also only ({len(annotated)}) {annotated}"
      f"\nadded ({len(added)}) {added}\n")

fails = 0
misses = []
for rid in changed + annotated + added:
    r = new[rid]
    qs = [(r["pdf_page"], r["printed_page"], r["quote"])] + [
        (q["pdf_page"], q["printed_page"], q["quote"]) for q in r["also_quotes"]]
    pages = sorted({p for p, _, _ in qs})
    for p, pl, q in qs:
        ok = norm(q) in text(p)
        lab = label(p) == pl
        nb = [x for x in (p - 1, p + 1) if norm(q) in text(x)]
        words = len(q.split())
        status = "OK " if ok and lab and words <= 15 else "BAD"
        if status == "BAD":
            fails += 1
        print(f"{status} {rid:10s} p.{p} [{pl}{'' if lab else ' != ' + label(p)}] {words:2d}w "
              f"{'(also on ' + str(nb) + ')' if nb else ''} {q!r}")
    # numeric values vs the cited pages' text
    blob = " ".join(text(p) for p in pages)
    for v in r["values"]:
        vals = v["value"] if isinstance(v["value"], list) else [v["value"]]
        for x in vals:
            if not isinstance(x, (int, float)):
                continue
            forms = {str(x), f"{x:g}", f"{x:,.0f}" if float(x).is_integer() else f"{x:g}"}
            if float(x).is_integer():
                forms |= {f"{int(x)}", f"{x:.1f}"}
            if not any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", blob) for f in forms):
                misses.append(f"{rid} {v['name']} {x} {v['unit']} (pages {pages})")
print(f"\nquote failures: {fails}")
print("numeric values not found in the cited pages' text layer (check each by eye):")
for m in misses:
    print("  ", m)
