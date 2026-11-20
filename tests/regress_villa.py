"""Regression gate: the CURRENT villa's outputs must equal the baseline.

    python tests\\regress_villa.py                 # cad colour gltf elevations
    python tests\\regress_villa.py gltf elevations  # just these stages

Runs each stage of the pipeline in THIS folder against the root
villa_design.py (the villa -- never a project) into a fresh temp VILLA_OUT,
snapshots the outputs (tests/snapshot_outputs.py) and diffs them against the
baseline snapshot taken from the frozen code before the builders were
generalised (%TEMP%\\villa_baseline_snap.json). Only the files the chosen
stages write are compared. Exit 0 = identical.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
# The baseline is kept WITH the code (tests\baselines\), taken from the
# pre-generalisation code on 2026-09-26; %TEMP% is only the fallback where it
# was first written.
BASE = os.path.join(HERE, "baselines", "villa_baseline_snap.json")
if not os.path.isfile(BASE):
    BASE = os.path.join(tempfile.gettempdir(), "villa_baseline_snap.json")
STAGES = {"cad": "villa_cad.py", "colour": "villa_colour.py", "gltf": "villa_gltf.py",
          "elevations": "villa_elevations.py"}
OWNS = {"cad": lambda k: k.startswith("VILLA_A10") and not k.endswith("P.dxf"),
        "colour": lambda k: k.startswith("VILLA_A10") and k.endswith("P.dxf"),
        "gltf": lambda k: k.startswith("render/"),
        "elevations": lambda k: k.startswith(("VILLA_A20", "VILLA_A30"))}

sys.path.insert(0, HERE)
import snapshot_outputs as S  # noqa: E402


def main(argv):
    stages = argv or list(STAGES)
    out = os.path.join(tempfile.gettempdir(), f"villa_regress_{os.getpid()}")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    env = {k: v for k, v in os.environ.items()
           if k not in ("VILLA_DESIGN_DIR",)}
    env["VILLA_OUT"] = out
    env["PYTHONPATH"] = ""
    for st in stages:
        r = subprocess.run([PY, "-X", "utf8", STAGES[st]], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"{st:11s} exit {r.returncode}")
        if r.returncode != 0:
            print(r.stdout[-3000:], r.stderr[-3000:])
            return 1
    base = json.load(open(BASE, encoding="utf-8-sig"))
    now = S.snapshot(out)
    keep = lambda d: {k: v for k, v in d.items() if any(OWNS[s](k) for s in stages)}
    d = S.diff(keep(base), keep(now))
    print("\n".join(d) if d else f"IDENTICAL to the baseline ({len(keep(now))} files)")
    shutil.rmtree(out, ignore_errors=True)
    return 1 if d else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
