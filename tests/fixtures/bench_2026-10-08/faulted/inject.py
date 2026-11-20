import os, sys
p = os.path.join(os.environ["TEMP"], "villa_bench", "_t2_base", "villa_design.py")
s = open(p, encoding="utf-8").read()
subs = [
 ('("FF", DOOR, "h", 22050, 22200, 6300, 7315, "CORRIDOR WEST", "BEDROOM 4", 90),',
  '("FF", DOOR, "h", 22050, 22200, 6300, 7000, "CORRIDOR WEST", "BEDROOM 4", 90),'),
 ('"rect": (12700.0, 22560.0, 13950.0, 29000.0), "risers": 24,',
  '"rect": (12700.0, 22560.0, 13950.0, 29000.0), "risers": 20,'),
 ('    ("GF", DOOR, "v", 18700, 18850, 22800, 23610, "HALL", "POWDER ROOM", 0),\n', ''),
 ('("DRIVER ROOM",     9550, 28500, 12550, 32800, HAB,  "GF"),',
  '("DRIVER ROOM",     9550, 28500, 13000, 32800, HAB,  "GF"),'),
 ('    ("FF", WIN, "v", 3000, 3400, 25000, 26200, "BEDROOM 4", None, None),\n    ("FF", WIN, "h", 27200, 27600, 6000, 7700, "BEDROOM 4", None, None),\n', ''),
 ('("MASTER ENSUITE", 22400, 17050, 26600, 20400, WET,  "FF"),',
  '("MASTER ENSUITE", 24600, 17050, 26600, 20400, WET,  "FF"),'),
]
for a, b in subs:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("injected", len(subs))
