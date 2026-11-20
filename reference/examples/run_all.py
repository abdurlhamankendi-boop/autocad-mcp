"""Regenerate every local-examples output and check it. Read-only on all
sources; writes only into this folder and the skill's aia_layers.json.

    python run_all.py               # everything (content scan ~3 min)
    python run_all.py --skip-content

Prints one PASS/FAIL line per check and the sha256 of each output so two
runs can be compared for determinism. Exit code 1 if any check fails.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aia_layers                                    # noqa: E402
import content_inventory                             # noqa: E402
import dst_read                                      # noqa: E402
import dwg_read as D                                 # noqa: E402
import mine_projects                                 # noqa: E402

FAIL = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        FAIL.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def main():
    # 1. .dst decode: every sheet set on the PC must decode to valid XML
    dsts = sorted(glob.glob(r"C:\Program Files\Autodesk\AutoCAD 2027\Sample"
                            r"\Sheet Sets\*\*.dst")) + sorted(glob.glob(
        os.path.join(mine_projects.MYPROJ, "*", "*.dst")))
    for p in dsts:
        try:
            info, xml = dst_read.read_dst(p)
            ET.fromstring(xml)
            check(f"dst decode {os.path.basename(p)}", len(info["sheets"]) > 0,
                  f"{len(info['sheets'])} sheets")
        except ET.ParseError as e:
            check(f"dst decode {os.path.basename(p)}", False, str(e))

    # 2. DWG reader self-checks on one file of each kind
    for p in [os.path.join(content_inventory.ROOT, r"Appliances\Kitchen"
                                                   r"\Ceramic_hob_6M.dwg"),
              os.path.join(mine_projects.SETS["office"]["root"],
                           r"Sheets\Architectural\Plans\A101 First Floor "
                           r"Plan.dwg"),
              os.path.join(mine_projects.SETS["fin_house"]["root"],
                           r"Sheets\F04 Leikkaukset\2009-F0401 "
                           r"Leikkaukset.dwg")]:
        s = D.summary(p)
        check(f"dwg sections+classes+objects {os.path.basename(p)}",
              "sections_error" not in s and s.get("self_check_ok"),
              f"{sum(s.get('object_types', {}).values())} objects, "
              f"preview={s['preview']}")

    # 3. AIA layer key + villa mapping
    r = aia_layers.main()
    check("AIA(256).ly parsed", r["row_count"] == 64, f"{r['row_count']} rows")
    un = [v["name"] for v in r["villa"]["names"] if v["status"] == "unmapped"]
    check("every villa layer classified", not un, f"unmapped={un}")

    # 4. example projects
    pr = mine_projects.main()
    for k, want in (("fin_house", 9), ("office", 35), ("ird_sheetset", 11)):
        sh = pr[k]["sheets"]
        pv = sum(1 for s in sh if s.get("preview"))
        check(f"{k}: sheets + previews", len(sh) == want and pv == want,
              f"{len(sh)} sheets, {pv} previews")
    check("fin levels chain (elev + height = next level)",
          not pr["fin_house"]["project"]["levels_chain_exceptions"])

    # 5. content library
    if "--skip-content" not in sys.argv:
        c = content_inventory.main()
        check("content: every DWG parsed", c["parsed"] == c["scanned"]
              and not c["errors"], f"{c['parsed']}/{c['scanned']}")
        check("content: villa catalog blocks all measured",
              all(v.get("is_3d") is not None
                  for v in c["villa_block_catalog_check"]),
              f"{len(c['villa_block_catalog_check'])} blocks")

    outs = [aia_layers.OUT, os.path.join(HERE, "out", "projects.json")]
    if "--skip-content" not in sys.argv:
        outs.append(content_inventory.OUT)
    for p in outs:
        print(f"sha256[:16] {sha(p)}  {p}")
    print(f"{'ALL PASS' if not FAIL else 'FAILED: ' + ', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
