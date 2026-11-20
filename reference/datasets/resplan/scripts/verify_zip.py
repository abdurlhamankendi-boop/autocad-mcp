import hashlib, zipfile, os

p = r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\ResPlan.zip"
n = os.path.getsize(p)
h = hashlib.sha1(b"blob %d\0" % n)
with open(p, "rb") as f:
    for ch in iter(lambda: f.read(1 << 20), b""):
        h.update(ch)
print("size", n)
print("git blob sha1", h.hexdigest())
z = zipfile.ZipFile(p)
for i in z.infolist():
    print(i.filename, i.file_size, i.compress_size, hex(i.CRC), i.date_time)
print("testzip:", z.testzip())
