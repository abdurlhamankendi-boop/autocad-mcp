"""Bring AutoCAD forward with the villa on screen.

Saves whatever is dirty first, then fronts the window and sets a shaded
south-west isometric on the 3D model.
"""

import os
import time

import pythoncom
import win32com.client as w
from win32com.client import VARIANT

import villa_geom as G

OUT = G.out_dir()                   # VILLA_OUT redirects it (a project's own)
SHOW = "VILLA_3D_MODEL.dwg"

pythoncom.CoInitialize()

acMax = 3


def mine():
    """The set's drawings, by name: the site plan and every plan sheet
    (villa_geom.plan_sheets()), the same with the P suffix, the 3D model."""
    nos = ["A-101"] + [no for _fl, no, _t in G.plan_sheets()]
    names = [f"VILLA_{no.replace('-', '')}" for no in nos]
    return tuple([n + ".dwg" for n in names] + [n + "P.dwg" for n in names]
                 + [SHOW])


MINE = mine()


def pt(x, y, z=0.0):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                   [float(x), float(y), float(z)])


def app():
    return w.GetActiveObject("AutoCAD.Application")


def get_doc(a, name):
    # by name AND folder: projects share drawing names (villa_geom.find_doc)
    return G.find_doc(a, name, OUT)


def main():
    a = app()
    saved = []
    for name in MINE:
        d = get_doc(a, name)
        if d is None:
            continue
        try:
            if not d.Saved:
                d.Save()
                saved.append(name)
        except Exception as exc:
            print(f"  {name}: {str(exc)[:50]}")

    a = app()
    a.Visible = True
    try:
        a.WindowState = acMax
    except Exception:
        pass

    doc = get_doc(a, SHOW)
    if doc is not None:
        doc.Activate()
        try:
            doc.SendCommand("_.-VIEW\n_SWISO\n_.VSCURRENT\n_Realistic\n"
                            "_.ZOOM\n_E\n")
        except Exception as exc:
            print("  view:", str(exc)[:60])
        time.sleep(2)

    a = app()
    try:
        a.WindowState = acMax
        hwnd = int(a.HWND)
        import ctypes
        u = ctypes.windll.user32
        u.ShowWindow(hwnd, 3)                 # SW_MAXIMIZE
        u.SetForegroundWindow(hwnd)
        u.BringWindowToTop(hwnd)
    except Exception as exc:
        print("  front:", str(exc)[:60])

    a = app()
    print(f"AutoCAD {a.Version}   {a.Documents.Count} drawing(s) open")
    print(f"active: {a.ActiveDocument.Name}")
    if saved:
        print("saved before showing: " + ", ".join(saved))
    print("\nthe villa set:")
    for name in MINE:
        d = get_doc(a, name)
        if d is None:
            print(f"   {name:22s} NOT OPEN")
            continue
        n = int(d.ModelSpace.Count)
        print(f"   {name:22s} {n:>4} entities")


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


if __name__ == "__main__":
    # The one script here that was not wrapped -- and of course it is the one
    # that runs straight after a heavy load, when AutoCAD is busiest.
    last = None
    for attempt in range(8):
        try:
            main()
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  AutoCAD busy, retrying ({attempt + 1})...")
            time.sleep(8)
    if last is not None:
        print("gave up: AutoCAD stayed busy")
