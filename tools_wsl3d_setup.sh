#!/usr/bin/env bash
# One-time setup of the build123d / OpenCascade stages inside WSL (Ubuntu).
#
#   wsl -d Ubuntu-24.04 --cd ~ -- bash /mnt/c/Users/lsire/autocad-mcp/tools_wsl3d_setup.sh
#
# Why: from 2026-10-08 Windows Smart App Control (enforcing) blocks the
# unsigned OpenCascade DLLs in cadquery_ocp_novtk.libs, so villa_gltf.py,
# villa_elevations.py and every build123d stage fail on Windows Python. Linux
# binaries inside WSL are not subject to it. The versions below mirror the
# Windows install (pip freeze, 2026-10-08) so the outputs match the baseline.
# Re-running is safe: it reuses the venv and pip skips what is installed.
set -euo pipefail
VENV="${VILLA3D_VENV:-$HOME/villa3d}"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet \
  "build123d==0.13.0" "cadquery-ocp-novtk==8.0.1.0.0" "cadquery-ocp-proxy==8.0.1.0.0" \
  "ezdxf==1.4.4" "shapely==2.1.2" "numpy==2.5.2" "matplotlib==3.11.2" \
  "pygltflib==1.16.5" "scipy==1.18.1" "pillow==12.2.0" "anytree==2.13.0" \
  "ocpsvg==0.7.0" "svgpathtools==1.8.0" "lib3mf==2.5.0" "trianglesolver==1.2" \
  "sympy==1.14.0" "webcolors==24.8.0" "ocp_gordon==0.3.1"
# The pipeline finds the skill (and its DBC rules file) at ~/.claude/skills.
# In WSL ~ is the Linux home, so link the Windows one in; without it every
# design fails closed with "DBC rules file missing" (a MAJOR on every stamp).
WINHOME="${VILLA3D_WINHOME:-/mnt/c/Users/lsire}"
mkdir -p "$HOME/.claude"
[ -e "$HOME/.claude/skills" ] || ln -s "$WINHOME/.claude/skills" "$HOME/.claude/skills"
# Same fonts as Windows for the PNG/PDF renderers (ezdxf + matplotlib scan
# ~/.fonts): link the Windows font folder, then drop both font caches so they
# are rebuilt with it.
mkdir -p "$HOME/.fonts"
[ -e "$HOME/.fonts/windows" ] || ln -s /mnt/c/Windows/Fonts "$HOME/.fonts/windows"
rm -rf "$HOME/.cache/matplotlib"
"$VENV/bin/python" -c "import ezdxf.fonts.fonts as F, pathlib; F.build_font_manager_cache(pathlib.Path(F.get_cache_file_path(None)))" 2>/dev/null \
  || "$VENV/bin/python" -c "import ezdxf.fonts.fonts as F; F.build_system_font_cache()" 2>/dev/null || true
"$VENV/bin/python" - <<'EOF'
import OCP, build123d, ezdxf, shapely
from build123d import Box
print("OK build123d", build123d.__version__, "| ezdxf", ezdxf.__version__,
      "| shapely", shapely.__version__, "| box volume", round(Box(1, 2, 3).volume, 6))
EOF
