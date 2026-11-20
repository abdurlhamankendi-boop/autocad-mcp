"""Validate the exported .glb without trusting the exporter's return value.

Parses the binary container by hand: magic, version, chunk table, then the
JSON chunk. A file that exists and is non-zero is not the same as a file a
renderer will open.
"""

import json
import os
import struct
import sys

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa\render"


def read_glb(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67, f"not a GLB: magic {magic:#x}"
    assert length == len(data), f"header says {length} bytes, file is {len(data)}"
    off, chunks = 12, []
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks.append((ctype, off + 8, clen))
        off += 8 + clen + (-clen % 4)
    js = next(c for c in chunks if c[0] == 0x4E4F534A)
    doc = json.loads(data[js[1]:js[1] + js[2]].decode("utf-8"))
    return version, len(data), doc, chunks


def main():
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".glb"))
    print(f"{len(files)} glb file(s) in {OUT}\n")
    ok = True
    for f in files:
        try:
            ver, size, doc, chunks = read_glb(os.path.join(OUT, f))
        except Exception as exc:
            print(f"  {f:24s} INVALID: {exc}")
            ok = False
            continue
        meshes = doc.get("meshes", [])
        prims = sum(len(m.get("primitives", [])) for m in meshes)
        tris = 0
        for m in meshes:
            for p in m.get("primitives", []):
                idx = p.get("indices")
                if idx is not None:
                    tris += doc["accessors"][idx]["count"] // 3
        mats = len(doc.get("materials", []))
        names = [n.get("name") for n in doc.get("nodes", []) if n.get("name")]
        print(f"  {f:24s} v{ver} {size // 1024:>5} KB  "
              f"{len(meshes):>2} mesh {prims:>2} prim {tris:>7} tri  "
              f"{mats} material(s)  {len(chunks)} chunks")
        if names:
            print(f"      nodes: {', '.join(str(n) for n in names[:8])}")
        if not meshes or tris == 0:
            print("      ! no geometry")
            ok = False
    print("\nVALID: every glb parses and carries geometry" if ok
          else "\nPROBLEMS ABOVE")


if __name__ == "__main__":
    main()
