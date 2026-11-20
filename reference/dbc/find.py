"""find.py REGEX [first_pdf_page] [last_pdf_page] -- grep the DBC text by page.

Prints: pdf_page [printed label] | line
"""
import re
import sys

TXT = r"C:\Users\lsire\autocad-mcp\reference\dbc\dbc_text.txt"
pat = re.compile(sys.argv[1], re.I)
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
page, label = 0, ""
head = re.compile(r"^=====PAGE (\d+) \[(.*)\]=====$")
for line in open(TXT, encoding="utf-8"):
    m = head.match(line.rstrip("\n"))
    if m:
        page, label = int(m.group(1)), m.group(2)
        continue
    if lo <= page <= hi and pat.search(line):
        print(f"{page} [{label}] | {line.rstrip()}")
