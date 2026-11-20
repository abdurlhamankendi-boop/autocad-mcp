"""Dump DBC_2021.pdf text per page with markers (1-based pdf index + printed label)."""
import re
import pymupdf

SRC = r"C:\Users\lsire\autocad-mcp\reference\DBC_2021.pdf"
OUT = r"C:\Users\lsire\autocad-mcp\reference\dbc\dbc_text.txt"
MAP = r"C:\Users\lsire\autocad-mcp\reference\dbc\page_labels.txt"


def clean(label):
    # labels come through as '<FEFF0041>12' -> 'A 12'
    def rep(m):
        hexs = m.group(1)
        chars = [chr(int(hexs[i:i + 4], 16)) for i in range(0, len(hexs), 4)]
        return "".join(c for c in chars if c != "\ufeff")
    s = re.sub(r"<([0-9A-Fa-f]+)>", rep, label)
    m = re.match(r"^([A-Z])(\d+)$", s)
    return f"{m.group(1)} {m.group(2)}" if m else s


doc = pymupdf.open(SRC)
print("pages", doc.page_count)
with open(OUT, "w", encoding="utf-8") as f, open(MAP, "w", encoding="utf-8") as g:
    for i, p in enumerate(doc):
        label = clean(p.get_label())
        g.write(f"{i + 1}\t{label}\n")
        t = p.get_text("text")
        f.write(f"\n=====PAGE {i + 1} [{label}]=====\n")
        f.write(t)
print("written", OUT)
