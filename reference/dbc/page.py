"""page.py P [P2 ...] -- print the extracted text of the given 1-based pdf pages (a-b ranges ok)."""
import re
import sys

TXT = r"C:\Users\lsire\autocad-mcp\reference\dbc\dbc_text.txt"
want = set()
for a in sys.argv[1:]:
    if "-" in a:
        lo, hi = map(int, a.split("-"))
        want.update(range(lo, hi + 1))
    else:
        want.add(int(a))
head = re.compile(r"^=====PAGE (\d+) \[(.*)\]=====$")
page = 0
out = sys.stdout
for line in open(TXT, encoding="utf-8"):
    m = head.match(line.rstrip("\n"))
    if m:
        page = int(m.group(1))
        if page in want:
            out.write(line)
        continue
    if page in want:
        out.write(line)
