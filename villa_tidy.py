"""Remove construction leftovers from the 3D model.

AddRegion does not consume its polyline and AddExtrudedSolid does not consume
its region, so every extrusion leaves two dead entities behind. They are
invisible in a shaded view and they still land in the DWG, in selections, and
in anything exported downstream.
"""

import os

import pythoncom
import win32com.client as w

OUT = r"C:\Users\lsire\OneDrive\Desktop\Villa"
DWG = "VILLA_3D_MODEL.dwg"
KEEP = {"AcDb3dSolid"}

pythoncom.CoInitialize()


def get_doc(a, name):
    for i in range(a.Documents.Count):
        d = a.Documents.Item(i)
        if str(d.Name).lower() == name.lower():
            return d
    return None


def main():
    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, DWG)
    if doc is None:
        a.Documents.Open(os.path.join(OUT, DWG))
        doc = get_doc(a, DWG)

    before = int(doc.ModelSpace.Count)
    junk = [e for e in doc.ModelSpace if str(e.ObjectName) not in KEEP]
    kinds = {}
    for e in junk:
        kinds[str(e.ObjectName)] = kinds.get(str(e.ObjectName), 0) + 1

    removed = 0
    for e in junk:
        try:
            e.Delete()
            removed += 1
        except Exception:
            pass

    a = w.GetActiveObject("AutoCAD.Application")
    doc = get_doc(a, DWG)
    try:
        doc.PurgeAll()
    except Exception:
        pass
    after = int(doc.ModelSpace.Count)
    solids = sum(1 for e in doc.ModelSpace
                 if str(e.ObjectName) == "AcDb3dSolid")
    doc.Save()

    print(f"before {before} entities")
    for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"   removed {v:>3}  {k}")
    print(f"after  {after} entities, {solids} 3D solids")
    print(f"file   {os.path.getsize(os.path.join(OUT, DWG)) // 1024} KB")


if __name__ == "__main__":
    main()
