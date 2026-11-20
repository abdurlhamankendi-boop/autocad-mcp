"""Close AutoCAD and relaunch it with just the villa set.

Every villa drawing is already saved; the drawings being discarded are the
superseded ones from earlier attempts, whose files remain on disk untouched.
Only in-memory view changes are lost.
"""

import os
import subprocess
import time

import pythoncom
import win32com.client as w

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
KEEP = ["VILLA_A101P.dwg", "VILLA_A102P.dwg", "VILLA_A103P.dwg",
        "VILLA_A101.dwg", "VILLA_A102.dwg", "VILLA_A103.dwg",
        "VILLA_3D_MODEL.dwg"]
SHOW = "VILLA_3D_MODEL.dwg"

pythoncom.CoInitialize()


def busy(exc):
    t = str(exc).lower()
    return "rejected" in t or "-2147418111" in t or "busy" in t


def app():
    return w.GetActiveObject("AutoCAD.Application")


def get_doc(a, name):
    for i in range(a.Documents.Count):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def save_villa():
    a = app()
    saved = []
    for n in KEEP:
        d = get_doc(a, n)
        if d is None:
            continue
        try:
            if not d.Saved:
                d.Save()
                saved.append(n)
        except Exception as exc:
            print(f"  {n}: could not save ({str(exc)[:40]})")
    return saved


def quit_acad():
    a = app()
    exe = None
    try:
        exe = str(a.FullName)
    except Exception:
        pass
    # discard unsaved changes in the superseded drawings
    for i in range(a.Documents.Count - 1, -1, -1):
        try:
            a.Documents.Item(i).Close(False)
        except Exception:
            pass
    try:
        a.Quit()
    except Exception:
        pass
    return exe


def main():
    saved = save_villa()
    if saved:
        print("saved before closing: " + ", ".join(saved))
    exe = quit_acad()
    print(f"AutoCAD closing... ({exe or 'path unknown'})")

    for _ in range(30):
        time.sleep(2)
        try:
            app()
        except Exception:
            break
    else:
        print("  it is still running")
    time.sleep(4)

    if not exe or not os.path.exists(exe):
        exe = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
    first = os.path.join(OUT, SHOW)
    subprocess.Popen([exe, first], close_fds=True)
    print(f"relaunching with {SHOW} ...")

    doc = None
    for _ in range(60):
        time.sleep(5)
        try:
            a = app()
            if a.Documents.Count > 0:
                doc = a.ActiveDocument
                break
        except Exception:
            continue
    if doc is None:
        print("AutoCAD did not come back on COM within 5 minutes")
        return

    a = app()
    for n in KEEP:
        if n == SHOW:
            continue
        p = os.path.join(OUT, n)
        if not os.path.exists(p):
            continue
        for _ in range(6):
            try:
                a = app()
                if get_doc(a, n) is None:
                    a.Documents.Open(p)
                break
            except Exception as exc:
                if not busy(exc):
                    raise
                time.sleep(5)

    a = app()
    d = get_doc(a, SHOW)
    if d is not None:
        d.Activate()
        try:
            d.SendCommand("_.-VIEW\n_SWISO\n_.VSCURRENT\n_Realistic\n"
                          "_.ZOOM\n_E\n")
        except Exception:
            pass
    time.sleep(3)
    a = app()
    print(f"\n{a.Documents.Count} document(s) open:")
    for i in range(a.Documents.Count):
        print(f"   {a.Documents.Item(i).Name}")


if __name__ == "__main__":
    last = None
    for attempt in range(6):
        try:
            main()
            last = None
            break
        except Exception as exc:
            last = exc
            if not busy(exc):
                raise
            print(f"  busy, retrying ({attempt + 1})...")
            time.sleep(10)
    if last is not None:
        print("gave up")
