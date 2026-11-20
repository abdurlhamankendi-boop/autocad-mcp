"""Run a pipeline script against a PROJECT's design instead of the villa's.

    python run_project.py fairway villa_design.py
    python run_project.py fairway villa_gltf.py
    python run_project.py fairway villa_cad.py --anything-the-script-takes

A project is a folder projects\\<name>\\ holding its own villa_design.py,
villa_furniture_spec.py and block_catalog.json (and anything else it
overrides). The builders stay here, in one place, and read the design they
find first on sys.path -- so this puts the project folder FIRST, the
pipeline folder second, and runs the script as __main__.

Environment it sets (unless already set):
  VILLA_DESIGN_DIR  the project folder (builders that insert their own folder
                    on sys.path honour it -- villa_blender, villa_elevations)
  VILLA_OUT         the deliverables folder: Desktop\\<OUT_NAME> from the
                    design (default: the project name, capitalised)
A script named without a folder is looked up in the project folder first,
then here. Exit code: the script's.
"""

from __future__ import annotations

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")


def project_dir(name):
    d = name if os.path.isdir(name) else os.path.join(ROOT, "projects", name)
    d = os.path.abspath(d)
    if not os.path.isfile(os.path.join(d, "villa_design.py")):
        raise SystemExit(f"no villa_design.py in {d}")
    return d


def out_name(d):
    """OUT_NAME from the design file, read as text (importing it here would
    cache it before the script's own imports)."""
    import re
    src = open(os.path.join(d, "villa_design.py"), encoding="utf-8").read()
    m = re.search(r'^OUT_NAME\s*=\s*["\']([^"\']+)["\']', src, re.M)
    return m.group(1) if m else os.path.basename(d).capitalize()


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    d = project_dir(argv[0])
    script = argv[1]
    if not os.path.isabs(script):
        for base in (d, ROOT):
            p = os.path.join(base, script)
            if os.path.isfile(p):
                script = p
                break
        else:
            raise SystemExit(f"no script {script} in {d} or {ROOT}")
    os.environ.setdefault("VILLA_DESIGN_DIR", d)
    os.environ.setdefault("VILLA_OUT", os.path.join(DESKTOP, out_name(d)))
    os.makedirs(os.environ["VILLA_OUT"], exist_ok=True)
    for p in (ROOT, d):                       # d ends up first
        while p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    sys.argv = [script] + argv[2:]
    os.chdir(os.path.dirname(script))
    print(f"[run_project] design {d}\n[run_project] out    {os.environ['VILLA_OUT']}\n"
          f"[run_project] script {script}", flush=True)
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main(sys.argv[1:])
