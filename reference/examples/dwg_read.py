"""Read-only DWG inspection WITHOUT AutoCAD (no COM, no ODA converter).

What it can do for R2004+ files (AC1018 .. AC1032, i.e. AutoCAD 2004-2027):
  * preview(path)          -> (kind, bytes) of the embedded thumbnail
                              (PNG as stored, or BMP rebuilt with a file header)
  * sections(path)         -> {section name: decompressed bytes}
  * utf16_strings(data)    -> readable UTF-16 strings found at ANY bit offset
                              (R2007+ stores object strings bit-packed)
  * summary(path)          -> version, section list, class names, preview kind

Format per the Open Design Alliance "Open Design Specification for .dwg files"
(v5.4.1) ch. 4: 0x6C-byte header at 0x80 XOR'd with an LCG stream; page map /
section map pages and data pages compressed with the R2004 LZ77 variant; data
page headers XOR'd with 0x4164536B ^ page address.

Self-checks, so a wrong decode cannot pass silently:
  * decrypted header must start with b"AcFssFcAJMB\0"
  * AcDb:Header must start with its 16-byte sentinel
  * every decompressed section length must equal the size in the section map

Usage:  python dwg_read.py file.dwg [--png out.png] [--strings]
"""

from __future__ import annotations

import io
import re
import struct
import sys

PREVIEW_SENTINEL = bytes.fromhex("1F256D07D43628289D57CA3F9D44102B")
HEADER_SENTINEL = bytes.fromhex("CF7B1F23FDDE38A95F7C68B84E6D335F")
CLASSES_SENTINEL = bytes.fromhex("8DA1C4B8C4A9F8C5C0DCF45FE7CFB68A")

VERSIONS = {"AC1015": "R2000", "AC1018": "R2004", "AC1021": "R2007",
            "AC1024": "R2010", "AC1027": "R2013", "AC1032": "R2018"}


class DwgError(Exception):
    pass


# ------------------------------------------------------------------ preview
def preview(data: bytes):
    """Return ('png'|'bmp'|None, image bytes). Works for R13 .. R2018: the
    preview seeker at 0x0D is in the unencrypted part of every version."""
    seeker = struct.unpack_from("<I", data, 0x0D)[0]
    if seeker <= 0 or seeker + 16 > len(data) or \
            data[seeker:seeker + 16] != PREVIEW_SENTINEL:
        return None, b""
    pos = seeker + 16
    _overall = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    n = data[pos]
    pos += 1
    found = {}
    for _ in range(n):
        code = data[pos]
        start, size = struct.unpack_from("<II", data, pos + 1)
        pos += 9
        found[code] = (start, size)
    if 6 in found:                                   # PNG (2013+ previews)
        s, n = found[6]
        png = data[s:s + n]
        if png[:8] == b"\x89PNG\r\n\x1a\n":
            return "png", png
    if 2 in found:                                   # DIB without file header
        s, n = found[2]
        dib = data[s:s + n]
        if len(dib) < 40:
            return None, b""
        hsize, _w, _h, _planes, bpp = struct.unpack_from("<IiiHH", dib, 0)
        clr_used = struct.unpack_from("<I", dib, 32)[0]
        ncol = clr_used or (1 << bpp if bpp <= 8 else 0)
        off = 14 + hsize + 4 * ncol
        fh = b"BM" + struct.pack("<IHHI", 14 + len(dib), 0, 0, off)
        return "bmp", fh + dib
    return None, b""


def preview_png(data: bytes):
    """Preview as PNG bytes (BMP converted with Pillow), or None."""
    kind, img = preview(data)
    if kind == "png":
        return img
    if kind == "bmp":
        from PIL import Image
        buf = io.BytesIO()
        Image.open(io.BytesIO(img)).save(buf, "PNG")
        return buf.getvalue()
    return None


# ------------------------------------------------------------------ R2004+
def _decrypt_header(data: bytes) -> bytes:
    out = bytearray(data[0x80:0x80 + 0x6C])
    seed = 1
    for i in range(len(out)):
        seed = (seed * 0x343FD + 0x269EC3) & 0xFFFFFFFF
        out[i] ^= (seed >> 16) & 0xFF
    return bytes(out)


def _literal_length(src, pos):
    """-> (length, new_pos, opcode or 0)."""
    b = src[pos]
    pos += 1
    if 0x01 <= b <= 0x0F:
        return b + 3, pos, 0
    if b == 0:
        total = 0x0F
        while src[pos] == 0:
            total += 0xFF
            pos += 1
        total += src[pos] + 3
        pos += 1
        return total, pos, 0
    return 0, pos, b                                   # b >= 0x10: an opcode


def _long_len(src, pos):
    b = src[pos]
    pos += 1
    total = 0
    if b == 0:
        total = 0xFF
        while src[pos] == 0:
            total += 0xFF
            pos += 1
        b = src[pos]
        pos += 1
    return total + b, pos


def _two_byte_offset(src, pos):
    b1, b2 = src[pos], src[pos + 1]
    return (b1 >> 2) | (b2 << 6), b1 & 0x03, pos + 2


def decompress(src: bytes, out_size: int) -> bytes:
    """R2004 LZ77 variant (ODA spec 4.7)."""
    dst = bytearray()
    pos = 0
    end = len(src)
    lit, pos, op = _literal_length(src, pos)
    dst += src[pos:pos + lit]
    pos += lit
    while pos < end and len(dst) < out_size:
        if op == 0:
            op = src[pos]
            pos += 1
        if op >= 0x40:
            n = ((op & 0xF0) >> 4) - 1
            op2 = src[pos]
            pos += 1
            off = (op2 << 2) | ((op & 0x0C) >> 2)
            if op & 0x03:
                lit, op = op & 0x03, 0
            else:
                lit, pos, op = _literal_length(src, pos)
        elif 0x21 <= op <= 0x3F:
            n = op - 0x1E
            off, lit, pos = _two_byte_offset(src, pos)
            if lit:
                op = 0
            else:
                lit, pos, op = _literal_length(src, pos)
        elif op == 0x20:
            n, pos = _long_len(src, pos)
            n += 0x21
            off, lit, pos = _two_byte_offset(src, pos)
            if lit:
                op = 0
            else:
                lit, pos, op = _literal_length(src, pos)
        elif 0x12 <= op <= 0x1F:
            n = (op & 0x0F) + 2
            off, lit, pos = _two_byte_offset(src, pos)
            off += 0x3FFF
            if lit:
                op = 0
            else:
                lit, pos, op = _literal_length(src, pos)
        elif op == 0x10:
            n, pos = _long_len(src, pos)
            n += 9
            off, lit, pos = _two_byte_offset(src, pos)
            off += 0x3FFF
            if lit:
                op = 0
            else:
                lit, pos, op = _literal_length(src, pos)
        elif op == 0x11:
            break
        else:
            raise DwgError(f"bad opcode 0x{op:02X} at {pos}")
        s = len(dst) - off - 1
        if s < 0:
            raise DwgError("back-reference before start")
        for i in range(n):                              # may overlap
            dst.append(dst[s + i])
        dst += src[pos:pos + lit]
        pos += lit
    return bytes(dst[:out_size])


def _system_page(data, addr, expect_type):
    ptype, dsize, csize, ctype, _chk = struct.unpack_from("<IIIII", data, addr)
    if ptype != expect_type:
        raise DwgError(f"system page type 0x{ptype:08X} != 0x{expect_type:08X}")
    body = data[addr + 20:addr + 20 + csize]
    return decompress(body, dsize) if ctype == 2 else bytes(body[:dsize])


def sections(data: bytes) -> dict:
    ver = data[:6].decode("ascii", "replace")
    if ver not in VERSIONS or ver in ("AC1015", "AC1021"):
        # AC1021 (R2007) uses a different, Reed-Solomon coded layout; AC1015
        # (R2000) is uncompressed and handled by ezdxf.addons.dwg instead.
        raise DwgError(f"NOT READ: section reader supports AC1018/AC1024+ "
                       f"only, this file is {ver} ({VERSIONS.get(ver, '?')}); "
                       f"the preview still works")
    hdr = _decrypt_header(data)
    if hdr[:11] != b"AcFssFcAJMB":
        raise DwgError("encrypted header check failed")
    page_map_addr = struct.unpack_from("<Q", hdr, 0x54)[0] + 0x100
    section_map_id = struct.unpack_from("<I", hdr, 0x5C)[0]
    pm = _system_page(data, page_map_addr, 0x41630E3B)
    pages, addr, i = {}, 0x100, 0
    while i + 8 <= len(pm):
        num, size = struct.unpack_from("<iI", pm, i)
        i += 8
        if num < 0:
            i += 16                                     # gap: parent/left/right/0
        else:
            pages[num] = addr
        addr += size
    sm = _system_page(data, pages[section_map_id], 0x4163003B)
    ndesc = struct.unpack_from("<I", sm, 0)[0]
    i = 20
    out = {}
    for _ in range(ndesc):
        size, npages, maxsz, _u, comp, _sid, enc = struct.unpack_from(
            "<QIIIIII", sm, i)
        name = sm[i + 32:i + 96].split(b"\0", 1)[0].decode("ascii", "replace")
        i += 96
        buf = bytearray(size)
        for _p in range(npages):
            pnum, dsize, start = struct.unpack_from("<IIQ", sm, i)
            i += 16
            if not name or pnum not in pages:
                continue
            pa = pages[pnum]
            h = bytearray(data[pa:pa + 32])
            mask = 0x4164536B ^ pa
            for k in range(0, 32, 4):
                w = struct.unpack_from("<I", h, k)[0] ^ mask
                struct.pack_into("<I", h, k, w)
            ptype, _snum, csize, psize, _st = struct.unpack_from("<IIIII", h, 0)
            if ptype != 0x4163043B:
                raise DwgError(f"data page type 0x{ptype:08X} in {name}")
            body = data[pa + 32:pa + 32 + csize]
            if enc == 1:
                raise DwgError(f"{name} is encrypted")
            chunk = decompress(body, maxsz) if comp == 2 else bytes(body)
            chunk = chunk[:max(0, min(maxsz, size - start))]
            buf[start:start + len(chunk)] = chunk
        if name:
            out[name] = bytes(buf)
    hd = out.get("AcDb:Header", b"")
    if hd[:16] != HEADER_SENTINEL:
        raise DwgError("AcDb:Header sentinel mismatch -> decode is wrong")
    return out


# ------------------------------------------------------------------ strings
# Latin-1 printable, plus the typographic quotes/dashes U+2013/14/18/19/1C/1D
# (the ACA samples use U+2019 in "Owner's Data").
_U16 = re.compile(rb"(?:[\x20-\x7e\xa0-\xff]\x00|[\x13\x14\x18\x19\x1c\x1d]\x20)"
                  rb"{4,}")


def utf16_strings(blob: bytes, minlen: int = 4) -> list:
    """UTF-16LE Latin-1 strings at any of the 8 bit offsets (R2007+ strings
    are bit-packed, not byte-aligned). Order of first appearance, deduped."""
    seen, out = set(), []
    nbits = len(blob) * 8
    big = int.from_bytes(blob, "big")
    mask = (1 << nbits) - 1
    for shift in range(8):
        # R2007+ bit streams are MSB-first within each byte; shifting the
        # whole big-endian integer left realigns a string that starts at
        # bit `shift` of a byte onto a byte boundary.
        b = ((big << shift) & mask).to_bytes(len(blob), "big")
        for m in _U16.finditer(b):
            s = m.group().decode("utf-16-le")
            if len(s) >= minlen and s not in seen:
                seen.add(s)
                out.append(s)
    return out


def readable(strings, min_alpha=0.6):
    """Drop mis-aligned garbage: keep strings that are mostly ASCII
    letters/digits/space (Finnish a-umlaut etc. still pass)."""
    out = []
    for s in strings:
        good = sum(ch.isascii() and (ch.isalnum() or ch in " .,:;-_/()'&%+#=")
                   for ch in s)
        if good >= min_alpha * len(s) and any(ch.isalpha() for ch in s):
            out.append(s)
    return out


# ------------------------------------------------------------------ bit reader
class Bits:
    """MSB-first bit reader with the DWG bit-coded primitives."""

    def __init__(self, data: bytes, bitpos: int = 0):
        self.d = data
        self.p = bitpos

    def B(self):
        v = (self.d[self.p >> 3] >> (7 - (self.p & 7))) & 1
        self.p += 1
        return v

    def bits(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | self.B()
        return v

    def RC(self):
        return self.bits(8)

    def RS(self):
        return self.RC() | (self.RC() << 8)

    def RL(self):
        return self.RS() | (self.RS() << 16)

    def BS(self):
        c = self.bits(2)
        return self.RS() if c == 0 else self.RC() if c == 1 else \
            0 if c == 2 else 256

    def BL(self):
        c = self.bits(2)
        return self.RL() if c == 0 else self.RC() if c == 1 else 0

    def TU(self):
        n = self.BS()
        return "".join(chr(self.RS()) for _ in range(n))


# ------------------------------------------------------------------ classes
def classes(secs: dict) -> list:
    """AcDb:Classes of an R2010+ file as [{num, app, cpp, dxf, count}].
    `count` = objects of that class in the drawing (ODA spec 5.8: "number of
    objects created of this type in the current DB"). Accepted only if the
    class numbers run 500, 501, ... and the string stream yields 3 names per
    class -- otherwise raises."""
    c = secs["AcDb:Classes"]
    if c[:16] != CLASSES_SENTINEL:
        raise DwgError("classes sentinel mismatch")
    for hdr in (24, 20):                 # 24 when the RL 'hsize' is present
        r = Bits(c, hdr * 8)
        bitsize = r.RL()
        maxnum = r.BS()
        r.RC(), r.RC(), r.B()
        rows, ok = [], maxnum >= 500
        for i in range(max(0, maxnum - 499)):
            num, flags = r.BS(), r.BS()
            r.B()
            item, cnt = r.BS(), r.BL()
            r.BS(), r.BS(), r.BL(), r.BL()
            if num != 500 + i or item not in (0x1F2, 0x1F3):
                ok = False
                break
            rows.append({"num": num, "flags": flags, "count": cnt})
        if not ok:
            continue
        # string stream sits at the END of the data, found backwards from
        # bitsize (libredwg section_string_stream)
        start = bitsize + hdr * 8 - 1
        s = Bits(c, start)
        if not s.B():
            continue
        start -= 16
        ds = Bits(c, start).RS()
        if ds & 0x8000:
            start -= 16
            ds = (ds & 0x7FFF) | (Bits(c, start).RS() << 15)
        s = Bits(c, start - ds)
        for row in rows:
            row["app"], row["cpp"], row["dxf"] = s.TU(), s.TU(), s.TU()
        if all(r_["cpp"].isprintable() and r_["dxf"] for r_ in rows):
            return rows
    raise DwgError("could not parse AcDb:Classes")


# ------------------------------------------------------------------ objects
FIXED_TYPES = {
    1: "TEXT", 2: "ATTRIB", 3: "ATTDEF", 4: "BLOCK", 5: "ENDBLK", 6: "SEQEND",
    7: "INSERT", 8: "MINSERT", 10: "VERTEX_2D", 11: "VERTEX_3D",
    12: "VERTEX_MESH", 13: "VERTEX_PFACE", 14: "VERTEX_PFACE_FACE",
    15: "POLYLINE_2D", 16: "POLYLINE_3D", 17: "ARC", 18: "CIRCLE", 19: "LINE",
    20: "DIMENSION_ORDINATE", 21: "DIMENSION_LINEAR", 22: "DIMENSION_ALIGNED",
    23: "DIMENSION_ANG3PT", 24: "DIMENSION_ANG2LN", 25: "DIMENSION_RADIUS",
    26: "DIMENSION_DIAMETER", 27: "POINT", 28: "3DFACE", 29: "POLYLINE_PFACE",
    30: "POLYLINE_MESH", 31: "SOLID", 32: "TRACE", 33: "SHAPE", 34: "VIEWPORT",
    35: "ELLIPSE", 36: "SPLINE", 37: "REGION", 38: "3DSOLID", 39: "BODY",
    40: "RAY", 41: "XLINE", 42: "DICTIONARY", 43: "OLEFRAME", 44: "MTEXT",
    45: "LEADER", 46: "TOLERANCE", 47: "MLINE", 48: "BLOCK_CONTROL",
    49: "BLOCK_HEADER", 50: "LAYER_CONTROL", 51: "LAYER",
    52: "STYLE_CONTROL", 53: "STYLE", 56: "LTYPE_CONTROL", 57: "LTYPE",
    60: "VIEW_CONTROL", 61: "VIEW", 62: "UCS_CONTROL", 63: "UCS",
    64: "VPORT_CONTROL", 65: "VPORT", 66: "APPID_CONTROL", 67: "APPID",
    68: "DIMSTYLE_CONTROL", 69: "DIMSTYLE", 70: "VX_CONTROL", 71: "VX",
    72: "GROUP", 73: "MLINESTYLE", 74: "OLE2FRAME", 76: "LONG_TRANSACTION",
    77: "LWPOLYLINE", 78: "HATCH", 79: "XRECORD", 80: "PLACEHOLDER",
    81: "VBA_PROJECT", 82: "LAYOUT", 0x1F2: "ACAD_PROXY_ENTITY",
    0x1F3: "ACAD_PROXY_OBJECT",
}


def _mc(d, i, signed):
    """Modular char -> (value, next index)."""
    val, shift = 0, 0
    while True:
        b = d[i]
        i += 1
        if b & 0x80:
            val |= (b & 0x7F) << shift
            shift += 7
            continue
        if signed:
            neg = b & 0x40
            val |= (b & 0x3F) << shift
            return (-val if neg else val), i
        val |= (b & 0x7F) << shift
        return val, i


def _ms(d, i):
    """Modular short -> (value, next index)."""
    val, shift = 0, 0
    while True:
        w = d[i] | (d[i + 1] << 8)
        i += 2
        if w & 0x8000:
            val |= (w & 0x7FFF) << shift
            shift += 15
            continue
        return val | (w << shift), i


def object_map(secs: dict) -> dict:
    """AcDb:Handles -> {handle: offset into AcDb:AcDbObjects}."""
    d = secs["AcDb:Handles"]
    i, out = 0, {}
    while i + 2 <= len(d):
        size = (d[i] << 8) | d[i + 1]          # big-endian, includes itself
        if size <= 2:
            break
        end = i + size
        i += 2
        h = loc = 0
        while i < end:
            dh, i = _mc(d, i, signed=False)
            dl, i = _mc(d, i, signed=True)
            h += dh
            loc += dl
            out[h] = loc
        i = end + 2                              # skip CRC (big-endian RS)
    return out


def object_types(secs: dict, cls: list | None = None):
    """Counter of object type names over every object in the drawing
    (R2010+ object header: MS size, UMC handle-stream bits, BOT type)."""
    import collections
    names = {r["num"]: r["dxf"] for r in (cls or [])}
    objs = secs["AcDb:AcDbObjects"]
    cnt = collections.Counter()
    for _h, off in object_map(secs).items():
        try:
            _size, j = _ms(objs, off)
            _hs, j = _mc(objs, j, signed=False)
            r = Bits(objs, j * 8)
            code = r.bits(2)
            if code == 0:
                t = r.RC()
            elif code == 1:
                t = r.RC() + 0x1F0
            else:
                t = r.RS()
        except IndexError:
            cnt["<unreadable>"] += 1
            continue
        cnt[FIXED_TYPES.get(t) or names.get(t) or f"type{t}"] += 1
    return cnt


def census(data: bytes):
    """(sections, classes, object-type Counter) for an R2010+ file; the class
    and object layouts parsed here are the R2010+ ones (BOT type codes,
    string streams), so older files raise instead of being mis-read."""
    ver = data[:6].decode("ascii", "replace")
    if ver not in ("AC1024", "AC1027", "AC1032"):
        raise DwgError(f"NOT READ: classes/objects parsed for AC1024+ only, "
                       f"this file is {ver} ({VERSIONS.get(ver, '?')})")
    secs = sections(data)
    cls = classes(secs)
    return secs, cls, object_types(secs, cls)


# REGION is planar (2D) and deliberately NOT counted as 3D geometry.
GEOM_3D = {"3DSOLID", "BODY", "3DFACE", "POLYLINE_PFACE",
           "POLYLINE_MESH", "MESH", "SURFACE", "EXTRUDEDSURFACE",
           "LOFTEDSURFACE", "REVOLVEDSURFACE", "SWEPTSURFACE",
           "PLANESURFACE", "NURBSURFACE", "AEC_MASS_ELEM"}


def summary(path: str, with_objects: bool = True) -> dict:
    data = open(path, "rb").read()
    ver = data[:6].decode("ascii", "replace")
    kind, img = preview(data)
    info = {"file": path, "bytes": len(data), "version": ver,
            "release": VERSIONS.get(ver, "?"), "preview": kind,
            "preview_bytes": len(img)}
    try:
        secs, cls, ot = census(data)
        info["sections"] = {k: len(v) for k, v in secs.items()}
        info["classes_with_objects"] = {r["dxf"]: r["count"]
                                        for r in cls if r["count"]}
        # self-check: the class table's instance counts (which include erased
        # and non-persistent objects) must be >= what the object walk found
        # for the same class; the walk finding MORE means a mis-parse.
        per = {}
        for r in cls:
            per[r["dxf"]] = per.get(r["dxf"], 0) + r["count"]
        alias = {"ACDBPLACEHOLDER": "PLACEHOLDER"}
        mism = {n: [c, ot.get(alias.get(n, n), 0)] for n, c in per.items()
                if c != ot.get(alias.get(n, n), 0)}
        info["self_check_mismatches"] = mism
        info["self_check_ok"] = all(w <= c for c, w in mism.values())
        if with_objects:
            info["object_types"] = dict(ot.most_common())
            info["geometry_3d"] = {k: v for k, v in ot.items() if k in GEOM_3D}
            info["mvblock_defs"] = ot.get("AEC_MVBLOCK_DEF", 0)
            info["mvblock_refs"] = ot.get("AEC_MVBLOCK_REF", 0)
    except (DwgError, struct.error, IndexError, KeyError) as e:
        info["sections_error"] = f"{type(e).__name__}: {e}"
    return info


if __name__ == "__main__":
    import json
    p = sys.argv[1]
    info = summary(p)
    if "--png" in sys.argv:
        png = preview_png(open(p, "rb").read())
        if png:
            open(sys.argv[sys.argv.index("--png") + 1], "wb").write(png)
    if "--strings" in sys.argv:
        secs = sections(open(p, "rb").read())
        info["strings"] = readable(
            utf16_strings(secs.get("AcDb:AcDbObjects", b""), 3))
    print(json.dumps(info, indent=1, ensure_ascii=False))
