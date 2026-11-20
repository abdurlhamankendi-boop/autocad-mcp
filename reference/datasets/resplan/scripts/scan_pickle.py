"""Extract ResPlan.pkl from the zip and scan its pickle opcodes for every
global it would import, WITHOUT unpickling (safety check before load)."""
import zipfile, pickletools, collections, os, hashlib

D = r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan"
zp = os.path.join(D, "ResPlan.zip")
pk = os.path.join(D, "ResPlan.pkl")
if not os.path.exists(pk):
    with zipfile.ZipFile(zp) as z:
        z.extract("ResPlan.pkl", D)
h = hashlib.sha256()
with open(pk, "rb") as f:
    for ch in iter(lambda: f.read(1 << 20), b""):
        h.update(ch)
print("pkl size", os.path.getsize(pk), "sha256", h.hexdigest())

globals_seen = collections.Counter()
ops = collections.Counter()
recent_strings = collections.deque(maxlen=2)
memo = {}
last = None
with open(pk, "rb") as f:
    for op, arg, pos in pickletools.genops(f):
        ops[op.name] += 1
        if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE", "BINUNICODE8"):
            recent_strings.append(arg)
            last = arg
            continue
        if op.name == "MEMOIZE":
            memo[len(memo)] = last
            continue
        if op.name in ("BINPUT", "LONG_BINPUT", "PUT"):
            memo[arg] = last
            continue
        if op.name in ("BINGET", "LONG_BINGET", "GET"):
            v = memo.get(arg)
            if isinstance(v, str):
                recent_strings.append(v)
            last = v
            continue
        last = None
        if False:
            pass
        elif op.name == "GLOBAL":
            globals_seen[arg] += 1
        elif op.name == "STACK_GLOBAL":
            globals_seen[" ".join(recent_strings)] += 1
        elif op.name in ("REDUCE", "BUILD", "INST", "OBJ", "NEWOBJ", "NEWOBJ_EX"):
            pass
print("GLOBALS:")
for k, v in globals_seen.most_common():
    print("  ", v, k)
print("OPS:", dict(ops.most_common(40)))
