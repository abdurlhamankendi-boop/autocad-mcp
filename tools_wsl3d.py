"""Run a build123d / OpenCascade stage inside WSL instead of Windows Python.

    python tools_wsl3d.py villa_gltf.py
    python tools_wsl3d.py villa_elevations.py
    python tools_wsl3d.py run_project.py fairway villa_gltf.py
    python tools_wsl3d.py tests\\regress_villa.py gltf elevations

Why: from 2026-10-08 Windows Smart App Control blocks the unsigned
OpenCascade DLLs, so every build123d stage fails on Windows Python. The same
pipeline folder runs in WSL (Ubuntu-24.04) through /mnt/c, with a venv that
mirrors the Windows package versions (tools_wsl3d_setup.sh, run once).

Windows paths are translated to /mnt/<drive>/... in VILLA_OUT,
VILLA_DESIGN_DIR and the script's arguments. VILLA_OUT keeps the Windows
default when unset (Desktop\\<OUT_NAME> for a project, Desktop\\Villa for the
villa), so outputs land where the Windows run would have put them. The exit
code is the script's.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DISTRO = os.environ.get("VILLA3D_DISTRO", "Ubuntu-24.04")
VENV_PY = os.environ.get("VILLA3D_PYTHON", "~/villa3d/bin/python")
DESKTOP = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")


def to_wsl(p):
    """C:\\Users\\x -> /mnt/c/Users/x; anything that is not a drive path is
    returned unchanged (relative paths stay relative to the pipeline)."""
    if p.startswith("\\\\"):
        raise SystemExit(f"UNC path not supported in WSL: {p}")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if not m:
        return p.replace("\\", "/")
    return f"/mnt/{m.group(1).lower()}/" + m.group(2).replace("\\", "/")


def default_out(argv):
    """The VILLA_OUT the Windows run would use."""
    if argv and os.path.basename(argv[0]) == "run_project.py" and len(argv) > 1:
        sys.path.insert(0, ROOT)
        import run_project
        d = run_project.project_dir(argv[1])
        return os.path.join(DESKTOP, run_project.out_name(d))
    return os.path.join(DESKTOP, "Villa")


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    env = {"VILLA_OUT": os.environ.get("VILLA_OUT") or default_out(argv)}
    if os.environ.get("VILLA_DESIGN_DIR"):
        env["VILLA_DESIGN_DIR"] = os.environ["VILLA_DESIGN_DIR"]
    os.makedirs(env["VILLA_OUT"], exist_ok=True)
    assigns = " ".join(f"{k}={shlex.quote(to_wsl(v))}" for k, v in env.items())
    args = " ".join(shlex.quote(to_wsl(a)) for a in argv)
    cmd = (f"cd {shlex.quote(to_wsl(ROOT))} && {assigns} PYTHONPATH= "
           f"{VENV_PY} -X utf8 {args}")
    print(f"[wsl3d] {DISTRO}: {cmd}", flush=True)
    r = subprocess.run(["wsl.exe", "-d", DISTRO, "--cd", "/", "--", "bash", "-lc", cmd])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
