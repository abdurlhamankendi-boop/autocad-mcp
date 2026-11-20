"""Clear a stuck AutoCAD command prompt.

A SendCommand that leaves AutoCAD mid-prompt also makes the COM interface
reject calls, so "send ESC over COM" cannot get in. PostMessage to the frame
does not reach it either, because the command line is a child window.

So do what a person would do: bring AutoCAD to the front and press Escape.
Only Escape is sent -- nothing is clicked, typed or confirmed.

Root cause worth remembering: `-WBLOCK` prompts for a block name, and AutoCAD's
command line treats a SPACE as Enter. A block called "PNL 15C Bed Plan" can
never be typed at that prompt. Use CopyObjects between documents instead.
"""

import ctypes
import ctypes.wintypes as wt
import time

u = ctypes.windll.user32
VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002


def find_frame():
    hits = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _l):
        if not u.IsWindowVisible(hwnd):
            return True
        n = u.GetWindowTextLengthW(hwnd)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(hwnd, buf, n + 1)
            cls = ctypes.create_unicode_buffer(256)
            u.GetClassNameW(hwnd, cls, 256)
            if cls.value.startswith("AfxMDIFrame"):
                hits.append((hwnd, buf.value))
        return True

    u.EnumWindows(cb, 0)
    return hits


def main():
    frames = find_frame()
    if not frames:
        print("no AutoCAD main frame found")
        return
    hwnd, title = frames[0]
    print(f"frame: {title[:70]}")

    u.ShowWindow(hwnd, 9)                      # SW_RESTORE
    u.SetForegroundWindow(hwnd)
    time.sleep(1.0)

    for _ in range(4):
        u.keybd_event(VK_ESCAPE, 0, 0, 0)
        u.keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
    print("Escape sent 4x to the focused AutoCAD window")

    time.sleep(3)
    import pythoncom
    import win32com.client as w
    pythoncom.CoInitialize()
    for attempt in range(6):
        try:
            a = w.GetActiveObject("AutoCAD.Application")
            n = a.Documents.Count
            name = a.ActiveDocument.Name
            print(f"COM is back: {n} document(s), active {name}")
            return
        except Exception:
            time.sleep(5)
    print("COM still refusing - AutoCAD needs a manual Escape or a restart")


if __name__ == "__main__":
    main()
