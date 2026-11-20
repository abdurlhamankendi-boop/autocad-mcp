"""Cold-start AutoCAD with only the villa drawings.

Assumes AutoCAD is not running. Opens the 3D model first, then the six sheets,
and leaves the model on screen shaded in south-west isometric.
"""

import os
import subprocess
import time

import pythoncom
import win32com.client as w

EXE = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
SHOW = "VILLA_3D_MODEL.dwg"
SHEETS = ["VILLA_A101P.dwg", "VILLA_A102P.dwg", "VILLA_A103P.dwg",
          "VILLA_A101.dwg", "VILLA_A102.dwg", "VILLA_A103.dwg"]

pythoncom.CoInitialize()


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def app():
    return w.GetActiveObject("AutoCAD.Application")


def get_doc(a, name):
    for i in range(a.Documents.Count):
        if str(a.Documents.Item(i).Name).lower() == name.lower():
            return a.Documents.Item(i)
    return None


def wait_for_com(minutes=6):
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        try:
            a = app()
            if a.Documents.Count > 0:
                return a
        except Exception:
            pass
        time.sleep(5)
    return None


def main():
    running = True
    try:
        app()
    except Exception:
        running = False

    if not running:
        subprocess.Popen([EXE, os.path.join(OUT, SHOW)], close_fds=True)
        print(f"launching AutoCAD with {SHOW} (first start is slow)...")
    a = wait_for_com()
    if a is None:
        print("AutoCAD did not come up on COM")
        return
    print(f"COM up: {a.Documents.Count} document(s)")

    for n in SHEETS:
        p = os.path.join(OUT, n)
        if not os.path.exists(p):
            continue
        for _ in range(8):
            try:
                a = app()
                if get_doc(a, n) is None:
                    a.Documents.Open(p)
                break
            except Exception as exc:
                if not busy(exc):
                    raise
                time.sleep(6)

    for _ in range(8):
        try:
            a = app()
            d = get_doc(a, SHOW)
            if d is not None:
                d.Activate()
                d.SendCommand("_.-VIEW\n_SWISO\n_.VSCURRENT\n_Realistic\n"
                              "_.ZOOM\n_E\n")
            break
        except Exception as exc:
            if not busy(exc):
                raise
            time.sleep(6)

    time.sleep(4)
    for _ in range(8):
        try:
            a = app()
            print(f"\n{a.Documents.Count} document(s) open:")
            for i in range(a.Documents.Count):
                d = a.Documents.Item(i)
                print(f"   {str(d.Name):24s} {int(d.ModelSpace.Count):>5} "
                      f"entities")
            return
        except Exception as exc:
            if not busy(exc):
                raise
            time.sleep(6)


if __name__ == "__main__":
    main()
