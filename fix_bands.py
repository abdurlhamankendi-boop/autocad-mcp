"""Snap every opening onto the wall it belongs to.

The bands were typed against an earlier envelope and a 800 mm plan shift left
them cutting thin air. Rather than retype twenty numbers, derive each band from
the rooms the opening connects -- which is the only definition that stays true
when the plan moves again.
"""

import ast
import io
import re

import villa_design as V

SRC = "villa_design.py"
NAMES = {V.DOOR: "DOOR", V.WIN: "WIN", V.OPEN: "OPEN"}
ROOM = {(r[6], r[0]): r for r in V.ROOMS}


def band_external(o):
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    r = ROOM[(fl, ra)]
    mid = (t0 + t1) / 2.0
    lo, hi = (r[2], r[4]) if axis == "h" else (r[1], r[3])
    if abs(mid - lo) <= abs(mid - hi):
        return lo - V.WALL, lo
    return hi, hi + V.WALL


def band_internal(o):
    fl, kind, axis, t0, t1, a, b, ra, rb, sw = o
    A, B = ROOM[(fl, ra)], ROOM[(fl, rb)]
    i = 1 if axis == "v" else 2                     # index of the low edge
    j = i + 2                                       # index of the high edge
    ax0, ax1, bx0, bx1 = A[i], A[j], B[i], B[j]
    # side by side: the gap between them is the wall
    if ax1 <= bx0:
        return ax1, max(bx0, ax1 + V.PART)
    if bx1 <= ax0:
        return bx1, max(ax0, bx1 + V.PART)
    # nested: the wall hugs the child's inboard face
    child, host = (B, A) if _contains(A, B) else (A, B)
    mid = (t0 + t1) / 2.0
    cands = [(child[i] - V.PART, child[i]), (child[j], child[j] + V.PART)]
    cands = [c for c in cands if host[i] - 1 <= c[0] and c[1] <= host[j] + 1]
    if not cands:
        return t0, t1
    return min(cands, key=lambda c: abs((c[0] + c[1]) / 2 - mid))


def _contains(a, b):
    return a[1] <= b[1] and a[2] <= b[2] and a[3] >= b[3] and a[4] >= b[4]


def fixed(o):
    t0, t1 = (band_external(o) if o[8] is None else band_internal(o))
    return float(t0), float(t1)


def fmt(o, t0, t1):
    fl, kind, axis, _, _, a, b, ra, rb, sw = o
    sw = "None" if sw is None else str(sw)
    rb = "None" if rb is None else f'"{rb}"'
    return (f'    ("{fl}", {NAMES[kind]}, "{axis}", {t0:.0f}, {t1:.0f}, '
            f'{a:.0f}, {b:.0f},\n     "{ra}", {rb}, {sw}),')


def main():
    src = io.open(SRC, encoding="utf-8").read()
    lines = src.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("OPENINGS = ["))
    end = next(i for i in range(start, len(lines)) if lines[i].rstrip() == "]")

    out, i, changed = [], start + 1, 0
    while i < end:
        raw = lines[i]
        if not raw.lstrip().startswith("("):
            out.append(raw)
            i += 1
            continue
        chunk, j = raw, i
        while chunk.count("(") > chunk.count(")"):
            j += 1
            chunk += "\n" + lines[j]
        expr = re.sub(r"#.*$", "", chunk, flags=re.M).strip().rstrip(",")
        env = {k: getattr(V, k) for k in dir(V) if k.isupper()}
        env.update(DOOR=V.DOOR, WIN=V.WIN, OPEN=V.OPEN)
        o = eval(expr, {"__builtins__": {}}, env)
        if not isinstance(o, tuple) or len(o) != 10:
            print("SKIP malformed:", repr(expr)[:160]); out.append(raw); i = j + 1; continue
        t0, t1 = fixed(o)
        if abs(t0 - o[3]) > 0.5 or abs(t1 - o[4]) > 0.5:
            changed += 1
            print(f"  {o[1]:6s} {str(o[7])[:16]:16s}-> {str(o[8] or 'outside')[:16]:16s} "
                  f"{o[3]:.0f}-{o[4]:.0f}  =>  {t0:.0f}-{t1:.0f}")
        out.append(fmt(o, t0, t1))
        i = j + 1

    lines[start + 1:end] = out
    io.open(SRC, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n{changed} band(s) snapped onto their wall")


if __name__ == "__main__":
    main()
