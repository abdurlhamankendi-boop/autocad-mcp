"""Fetch CC0 HDRIs for lighting the villa exterior.

Poly Haven is CC0 1.0 with a keyless API. For a walled villa under a hot-dry
sky the HDRI does most of the work in a render: it is the light source, the
reflection in the pool, and the thing visible over the boundary wall.
"""

import json
import os
import urllib.request

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa\render\hdri"
API = "https://api.polyhaven.com"
UA = {"User-Agent": "villa-project/1.0 (architectural study)"}
RES = "4k"
WANT = ("desert", "dry", "clear", "sunny", "sky")


def get(path):
    req = urllib.request.Request(API + path, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def main():
    os.makedirs(OUT, exist_ok=True)
    assets = get("/assets?t=hdris")
    # Chosen by name, not by tag score: scoring on loose tags handed back
    # "Harvest" and "Gothic Manor" for a Gulf villa. These are a clear midday
    # desert sky, a hard-sun arid noon, and a warm low sun for the evening
    # shot -- the three exterior conditions this scheme needs.
    PICKS = ["goegap", "kloppenheim_06", "aarfontein_dirt_road",
             "hausdorf_clear_sky", "syferfontein_18d_clear"]
    scored = [(0, 0, aid, assets[aid].get("name", aid))
              for aid in PICKS if aid in assets]
    missing = [a for a in PICKS if a not in assets]
    print(f"{len(assets)} HDRIs available; taking {len(scored)}"
          + (f"; not present: {missing}" if missing else "") + chr(10))

    picked = 0
    manifest = []
    for score, _evs, aid, name in scored:
        if picked >= 3:
            break
        try:
            files = get(f"/files/{aid}")
            link = files["hdri"][RES]["hdr"]["url"]
            size = files["hdri"][RES]["hdr"].get("size", 0)
        except Exception as exc:
            print(f"  {aid:28s} no {RES} hdr ({str(exc)[:40]})")
            continue
        dest = os.path.join(OUT, f"{aid}_{RES}.hdr")
        try:
            req = urllib.request.Request(link, headers=UA)
            with urllib.request.urlopen(req, timeout=600) as r, \
                    open(dest, "wb") as fh:
                fh.write(r.read())
        except Exception as exc:
            print(f"  {aid:28s} download failed: {str(exc)[:50]}")
            continue
        mb = os.path.getsize(dest) / 1e6
        print(f"  {aid:28s} {mb:6.1f} MB   {name}")
        manifest.append({"id": aid, "name": name, "file": os.path.basename(dest),
                         "bytes": os.path.getsize(dest), "licence": "CC0 1.0",
                         "source": f"https://polyhaven.com/a/{aid}"})
        picked += 1

    with open(os.path.join(OUT, "hdri.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    total = sum(m["bytes"] for m in manifest) / 1e6
    print(f"\n{picked} HDRIs, {total:.0f} MB  ->  {OUT}")
    print("licence: CC0 1.0 - no attribution required, commercial use permitted")


if __name__ == "__main__":
    main()
