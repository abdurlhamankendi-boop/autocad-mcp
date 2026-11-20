"""Fetch CC0 PBR materials for the villa's specified finishes.

ambientCG is CC0 1.0 with no carve-outs and a keyless API, which is why it can
be scripted at all -- Poliigon's terms forbid automated downloading. Every
asset carries dimensionX/dimensionY in centimetres, so the correct UV scale is
a division rather than a guess.

Nothing here is executed. Only images are written to disk.
"""

import json
import os
import urllib.request

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa\render\materials"
API = "https://ambientcg.com/api/v2/full_json"
UA = {"User-Agent": "villa-project/1.0 (architectural study)"}

# spec finish  ->  search term, and what it is for
# Chosen by asset ID, not by search: the API matches on prefix, so
# "WoodFloor" and "PavingStones" returned nothing and the pool was handed a
# ROOFING tile. Every one below publishes its real-world size, which is the
# whole reason for using this source.
WANTED = [
    ("travertine", "Travertine001",   "ground plane, inside and out"),
    ("concrete",   "Concrete034",     "board-marked exposed structure"),
    ("oak",        "WoodFloor040",    "first-floor bedrooms, stair treads"),
    ("basalt",     "PavingStones150", "forecourt setts"),
    ("gravel",     "Gravel023",       "mulch to the planting beds"),
    ("grass",      "Grass001",        "lawn"),
    ("mosaic",     "Tiles107",        "pool tank lining"),
    ("sand",       "Ground054",       "terrain"),
]
RES = "2K-JPG"


def fetch(term, limit=12):
    # id=, not q=: the free-text search does not match a full asset ID, which
    # is how the pool ended up with a roofing tile.
    url = f"{API}?id={urllib.parse.quote(term)}&include=downloadData"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read()).get("foundAssets", [])


def pick_download(asset, res=RES):
    dd = asset.get("downloadFolders", {}).get("default", {})
    for group in dd.get("downloadFiletypeCategories", {}).values():
        for f in group.get("downloads", []):
            if f.get("attribute") == res:
                return f.get("downloadLink"), f.get("size", 0), f.get("fileName")
    return None, 0, None


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for key, term, use in WANTED:
        try:
            assets = fetch(term)
        except Exception as exc:
            print(f"  {key:12s} search failed: {str(exc)[:60]}")
            continue
        if not assets:
            print(f"  {key:12s} nothing found for '{term}'")
            continue
        # prefer an asset that publishes its real-world size
        exact = [x for x in assets if str(x.get("assetId")) == term]
        if not exact:
            print(f"  {key:12s} '{term}' not returned by the API")
            continue
        a = exact[0]
        link, size, fname = pick_download(a)
        if not link:
            print(f"  {key:12s} {a.get('assetId')}: no {RES} variant")
            continue
        dest = os.path.join(OUT, fname or f"{a['assetId']}.zip")
        try:
            req = urllib.request.Request(link, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r, \
                    open(dest, "wb") as fh:
                fh.write(r.read())
        except Exception as exc:
            print(f"  {key:12s} download failed: {str(exc)[:60]}")
            continue
        dx, dy = a.get("dimensionX"), a.get("dimensionY")
        manifest.append({"key": key, "use": use, "assetId": a["assetId"],
                         "dimension_cm": [dx, dy],
                         "file": os.path.basename(dest),
                         "bytes": os.path.getsize(dest),
                         "licence": "CC0 1.0",
                         "source": f"https://ambientcg.com/view?id={a['assetId']}"})
        sz = os.path.getsize(dest) / 1e6
        dim = f"{dx}x{dy} cm" if dx else "size not published"
        print(f"  {key:12s} {a['assetId']:16s} {sz:6.1f} MB   {dim}")

    with open(os.path.join(OUT, "materials.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    total = sum(m["bytes"] for m in manifest) / 1e6
    print(f"\n{len(manifest)} materials, {total:.0f} MB  ->  {OUT}")
    print("licence: CC0 1.0 on every one - no attribution required, "
          "commercial use permitted")


if __name__ == "__main__":
    import urllib.parse
    main()
