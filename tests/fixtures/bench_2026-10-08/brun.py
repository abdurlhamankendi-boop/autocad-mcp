"""Benchmark runner: run a pipeline script against a bench project folder,
with every output kept inside that folder.

    python brun.py PROJECT_DIR SCRIPT [args...]

Sets VILLA_OUT = PROJECT_DIR\\out (always -- never the Desktop), then runs
C:\\Users\\lsire\\autocad-mcp\\run_project.py PROJECT_DIR SCRIPT from the
pipeline folder. Exit code: the script's.
"""
import os
import subprocess
import sys

PIPE = r"C:\Users\lsire\autocad-mcp"

if len(sys.argv) < 3:
    raise SystemExit(__doc__)
proj = os.path.abspath(sys.argv[1])
env = dict(os.environ)
env["VILLA_OUT"] = os.path.join(proj, "out")
env.pop("VILLA_DESIGN_DIR", None)
os.makedirs(env["VILLA_OUT"], exist_ok=True)
r = subprocess.run([sys.executable, os.path.join(PIPE, "run_project.py"), proj] + sys.argv[2:],
                   cwd=PIPE, env=env)
sys.exit(r.returncode)
