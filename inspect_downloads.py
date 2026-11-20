"""Inventory the downloaded asset ZIPs before extracting anything.

Reports what each archive actually contains by extension, flags anything
executable or script-like, and lists the DWG/DXF payload that is worth
extracting. Nothing is extracted or executed here.
"""

import collections
import os
import zipfile

DL = r"C:\Users\lsire\Downloads"
CAD = {".dwg", ".dxf"}
DOC = {".pdf", ".doc", ".docx", ".txt", ".rtf", ".csv", ".xls", ".xlsx"}
BIM = {".rfa", ".rvt", ".ifc", ".skp", ".max", ".3ds", ".obj", ".fbx"}
IMG = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp"}
# things that can run. None of these get extracted.
RISK = {".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jse",
        ".scr", ".msi", ".lsp", ".fas", ".vlx", ".arx", ".dbx", ".dvb",
        ".mnl", ".scriptx", ".reg", ".lnk", ".hta", ".jar", ".py"}


def main():
    zips = sorted(f for f in os.listdir(DL) if f.lower().endswith(".zip"))
    total_cad, risky_all = 0, []
    print(f"{len(zips)} archive(s) in Downloads\n")
    for z in zips:
        p = os.path.join(DL, z)
        try:
            with zipfile.ZipFile(p) as zf:
                names = [n for n in zf.namelist() if not n.endswith("/")]
                bad = zf.testzip()
        except Exception as exc:
            print(f"  {z[:52]:52s} NOT A VALID ZIP ({str(exc)[:40]})")
            continue
        ext = collections.Counter(os.path.splitext(n)[1].lower() for n in names)
        cad = sum(v for k, v in ext.items() if k in CAD)
        risky = [n for n in names if os.path.splitext(n)[1].lower() in RISK]
        total_cad += cad
        risky_all += [(z, n) for n in risky]
        summary = "  ".join(f"{k or '(none)'}:{v}" for k, v in
                            ext.most_common(6))
        flag = "  !! EXECUTABLE CONTENT" if risky else ""
        print(f"  {z[:52]:52s} {len(names):>4} files  DWG/DXF:{cad:<4}{flag}")
        print(f"      {summary}")
        if bad:
            print(f"      ! corrupt member: {bad}")
    print(f"\ntotal DWG/DXF across all archives: {total_cad}")
    if risky_all:
        print("\nEXECUTABLE OR SCRIPT CONTENT (will not be extracted):")
        for z, n in risky_all[:20]:
            print(f"   {z} :: {n}")
    else:
        print("no executable or script content found in any archive")


if __name__ == "__main__":
    main()
