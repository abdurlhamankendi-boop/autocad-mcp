"""Extract only the DWG/DXF payload from the downloaded asset archives.

Everything else -- PDFs, DWF, SketchUp, Vectorworks, Word docs -- is left in
the archive, and any archive containing executable content is skipped outright
rather than filtered, because the safe move with a mixed archive is not to open
it at all.
"""

import os
import zipfile

DL = r"C:\Users\lsire\Downloads"
OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa\blocks"
CAD = {".dwg", ".dxf"}
RISK = {".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".scr",
        ".msi", ".lsp", ".fas", ".vlx", ".arx", ".dbx", ".dvb", ".reg"}
SKIP = ("adsksnactivation", "openhardwaremonitor")


def safe_name(zname, prefix):
    base = os.path.basename(zname).replace(" ", "_")
    return f"{prefix}__{base}"


def main():
    os.makedirs(OUT, exist_ok=True)
    written, skipped = [], []
    for z in sorted(f for f in os.listdir(DL) if f.lower().endswith(".zip")):
        if any(s in z.lower() for s in SKIP):
            skipped.append((z, "unrelated to the villa"))
            continue
        p = os.path.join(DL, z)
        try:
            zf = zipfile.ZipFile(p)
        except Exception as exc:
            skipped.append((z, f"unreadable: {str(exc)[:40]}"))
            continue
        with zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if any(os.path.splitext(n)[1].lower() in RISK for n in names):
                skipped.append((z, "contains executable content"))
                continue
            prefix = os.path.splitext(z)[0].split(" - ")
            prefix = (prefix[1] if len(prefix) > 1 else prefix[0])
            prefix = prefix.replace(" ", "_")[:28]
            for n in names:
                if os.path.splitext(n)[1].lower() not in CAD:
                    continue
                # never trust a path inside an archive
                dest = os.path.join(OUT, safe_name(n, prefix))
                with zf.open(n) as src, open(dest, "wb") as fh:
                    fh.write(src.read())
                written.append((os.path.basename(dest),
                                os.path.getsize(dest)))

    print(f"extracted {len(written)} CAD file(s) -> {OUT}\n")
    for name, size in sorted(written):
        print(f"  {name[:62]:62s} {size / 1024:>8.0f} KB")
    if skipped:
        print("\nskipped:")
        for z, why in skipped:
            print(f"  {z[:52]:52s} {why}")


if __name__ == "__main__":
    main()
