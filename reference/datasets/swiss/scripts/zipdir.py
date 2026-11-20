import struct, sys, json
TOTAL = 931868205
TAIL_OFF = 931802669
data = open(sys.argv[1], 'rb').read()

# End of central directory (possibly zip64)
eocd = data.rfind(b'PK\x05\x06')
assert eocd >= 0
(_, disk, cd_disk, n_this, n_total, cd_size, cd_off, clen) = struct.unpack('<IHHHHIIH', data[eocd:eocd+22])
if cd_off == 0xFFFFFFFF or n_total == 0xFFFF:
    loc = data.rfind(b'PK\x06\x07')
    _, _, z64_off, _ = struct.unpack('<IIQI', data[loc:loc+20])
    z = data[z64_off - TAIL_OFF:]
    (sig, sz, vm, vn, d, dcd, n_this, n_total, cd_size, cd_off) = struct.unpack('<IQHHIIQQQQ', z[:56])
print('entries', n_total, 'cd_size', cd_size, 'cd_off', cd_off)
cd = data[cd_off - TAIL_OFF: cd_off - TAIL_OFF + cd_size]
p = 0
out = []
while p < len(cd):
    (sig, vm, vn, flag, meth, t, d, crc, csize, usize, fnl, exl, cml, dsk, ia, ea, lho) = struct.unpack('<IHHHHHHIIIHHHHHII', cd[p:p+46])
    assert sig == 0x02014b50
    name = cd[p+46:p+46+fnl].decode('utf-8', 'replace')
    extra = cd[p+46+fnl:p+46+fnl+exl]
    # zip64 extra
    q = 0
    while q < len(extra):
        hid, hsz = struct.unpack('<HH', extra[q:q+4])
        if hid == 1:
            vals = extra[q+4:q+4+hsz]
            k = 0
            if usize == 0xFFFFFFFF:
                usize = struct.unpack('<Q', vals[k:k+8])[0]; k += 8
            if csize == 0xFFFFFFFF:
                csize = struct.unpack('<Q', vals[k:k+8])[0]; k += 8
            if lho == 0xFFFFFFFF:
                lho = struct.unpack('<Q', vals[k:k+8])[0]; k += 8
        q += 4 + hsz
    out.append(dict(name=name, method=meth, csize=csize, usize=usize, lho=lho, crc=crc))
    p += 46 + fnl + exl + cml
for e in out:
    print(f"{e['name']:60s} m={e['method']} c={e['csize']:>12,} u={e['usize']:>14,} off={e['lho']:>12,}")
json.dump(out, open(sys.argv[2], 'w'), indent=1)
