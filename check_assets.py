"""Verify the downloaded assets are what they claim to be.

A 30 MB file is not proof of anything: a rate-limit page saved as .zip is also
a file. Check the ZIP central directory and the Radiance HDR header, and list
which PBR maps each material actually contains.
"""

import json
import os
import zipfile

BASE = r"C:\Users\lsire\OneDrive\Desktop\Villa\render"
MAPS = ("color", "normal", "roughness", "displacement", "ambientocclusion",
        "metalness", "opacity")


def check_materials():
    d = os.path.join(BASE, "materials")
    man = json.load(open(os.path.join(d, "materials.json")))
    print(f"MATERIALS  ({len(man)})\n")
    ok = True
    for m in man:
        p = os.path.join(d, m["file"])
        if not os.path.exists(p):
            print(f"  {m['key']:12s} MISSING")
            ok = False
            continue
        try:
            with zipfile.ZipFile(p) as z:
                bad = z.testzip()
                names = [n.lower() for n in z.namelist()]
        except Exception as exc:
            print(f"  {m['key']:12s} NOT A VALID ZIP: {str(exc)[:50]}")
            ok = False
            continue
        if bad:
            print(f"  {m['key']:12s} corrupt member: {bad}")
            ok = False
        found = sorted({mp for mp in MAPS if any(mp in n for n in names)})
        dx, dy = m["dimension_cm"]
        core = {"color", "normal", "roughness"} <= set(found)
        print(f"  {m['key']:12s} {m['assetId']:16s} {len(names):>2} files  "
              f"{dx}x{dy} cm  maps: {', '.join(found)}")
        if not core:
            print("      ! missing one of colour / normal / roughness")
            ok = False
    return ok


def check_hdri():
    d = os.path.join(BASE, "hdri")
    man = json.load(open(os.path.join(d, "hdri.json")))
    print(f"\nHDRI  ({len(man)})\n")
    ok = True
    for h in man:
        p = os.path.join(d, h["file"])
        with open(p, "rb") as fh:
            head = fh.read(16)
        valid = head.startswith(b"#?RADIANCE") or head.startswith(b"#?RGBE")
        print(f"  {h['id']:26s} {os.path.getsize(p) / 1e6:6.1f} MB  "
              f"{'valid Radiance HDR' if valid else 'NOT AN HDR'}")
        if not valid:
            ok = False
    return ok


if __name__ == "__main__":
    a = check_materials()
    b = check_hdri()
    print("\nVERIFIED: every asset is intact and carries its PBR maps"
          if a and b else "\nPROBLEMS ABOVE")
