import struct, sys, zipfile, zlib, hashlib
TAIL_OFF = 931802669
tail = open(sys.argv[1], 'rb').read()
dst = sys.argv[2]

with open(dst, 'rb') as f:
    lh = f.read(30)
    sig, ver, flag, meth, t, d, crc, cs, us, fnl, exl = struct.unpack('<IHHHHHIIIHH', lh)
    assert sig == 0x04034b50, hex(sig)
    name = f.read(fnl).decode()
    extra = f.read(exl)
    print('local header:', name, 'flag', flag, 'meth', meth, 'crc', hex(crc), 'cs', cs, 'us', us, 'extra', extra.hex())

# locate the central-directory entry for geometries.csv in the tail
eocd = tail.rfind(b'PK\x05\x06')
cd_off = 931867616
cd = tail[cd_off - TAIL_OFF:eocd]
p = 0
entry = None
while p < len(cd):
    h = struct.unpack('<IHHHHHHIIIHHHHHII', cd[p:p+46])
    fnl, exl, cml = h[10], h[11], h[12]
    nm = cd[p+46:p+46+fnl].decode()
    if nm.endswith('geometries.csv'):
        entry = bytearray(cd[p:p+46+fnl+exl+cml])
        lho = h[16]
        print('cd entry lho', lho, 'crc', hex(h[7]), 'cs', h[8], 'us', h[9], 'extra', bytes(entry[46+fnl:46+fnl+exl]).hex())
        break
    p += 46 + fnl + exl + cml
assert entry is not None
fnl = struct.unpack('<H', entry[28:30])[0]
exl = struct.unpack('<H', entry[30:32])[0]
if lho != 0xFFFFFFFF:
    struct.pack_into('<I', entry, 42, 0)
else:
    raise SystemExit('zip64 offset patch not implemented')

import os
size = os.path.getsize(dst)
with open(dst, 'r+b') as f:
    f.seek(0, 2)
    # only append once
    f.seek(size - 22)
    if f.read(4) == b'PK\x05\x06':
        print('already finalised')
    else:
        f.seek(0, 2)
        cd_start = f.tell()
        f.write(entry)
        f.write(struct.pack('<IHHHHIIH', 0x06054b50, 0, 0, 1, 1, len(entry), cd_start, 0))
        print('appended CD at', cd_start)

# verify by streaming decompression + CRC
z = zipfile.ZipFile(dst)
info = z.infolist()[0]
print('zip member', info.filename, info.file_size, hex(info.CRC))
c = 0; n = 0
md5 = hashlib.md5()
with z.open(info) as fh:
    while True:
        b = fh.read(1 << 22)
        if not b: break
        c = zlib.crc32(b, c); n += len(b); md5.update(b)
print('decompressed bytes', n, 'crc32', hex(c), 'match', c == info.CRC and n == info.file_size)
print('md5 of geometries.csv', md5.hexdigest())
