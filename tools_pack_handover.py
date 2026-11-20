"""Build the handover package: AutoCAD_Villa_Handover_<date>.zip on the Desktop.

    python tools_pack_handover.py REPORT_DIR [--date 2026-09-26]

REPORT_DIR holds REPORT.md, REPORT.html and README_FIRST.md (from the report
workflow). The package layout (the report refers to these paths):

  README_FIRST.md, REPORT.html, REPORT.md, MANIFEST.txt
  COST_REDUCTION_REPORT.pdf/.md, UPDATE_<date>.md   (version 3: copied when REPORT_DIR has them)
  pipeline/                  autocad-mcp code, tests, unreal scripts, projects/, candidates/,
                             PROJECT_STATE.md, research/, reference/ (no DBC PDF, no raw datasets)
  skill/architectural-cad/   the Claude skill
  agents/                    the pinned Claude Code agents (~/.claude/agents/cad-*.md)
  mcp/autocad-mcp-pro-notes/ LOCAL_PATCHES.md, README, LICENSE of the third-party server
  mcp/claude_mcp_config.example.json   sanitised MCP registration
  samples/villa/, samples/fairway/     sheets (PNG/PDF/DXF), 3-D DWG, glTF, renders

NOT included, on purpose: installed software; the Dubai Building Code PDF
(Dubai Municipality's document -- link in the report); raw datasets (links);
the third-party furniture block library and the sheet DWGs that embed its
blocks; downloaded textures/HDRI; backups (_pre_projects_0926, *.pre_*.py,
*.bak.py); caches. Every text file is scanned for secrets and personal data
before zipping; the build fails if anything is found.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

HOME = os.path.expanduser("~")
PIPE = os.path.join(HOME, "autocad-mcp")
SKILL = os.path.join(HOME, ".claude", "skills", "architectural-cad")
PRO = os.path.join(HOME, "autocad-mcp-pro")
DESK = os.path.join(HOME, "OneDrive", "Desktop")
NAME = "AutoCAD_Villa_Handover"

SKIP_DIRS = {"__pycache__", ".pytest_cache", "_pre_projects_0926", ".venv", "venv",
             ".git", "node_modules", "datasets", "blocks", "Saved", "Intermediate",
             "DerivedDataCache", "materials", "hdri",
             # Unreal: textures/assets are rebuilt by unreal\build_scene.py, logs
             # and frames are run output
             "Content", "Binaries", "logs", "frames",
             # superseded / restored deliverables: history, not the current set
             "_restored_0910", "_superseded_0906-0909",
             # backups taken by the 2026-10-08 changes
             "_pre_gaps1008"}
SKIP_FILES = ["*.pyc", "*.pre_*.*", "*.bak.py", "DBC_2021.pdf", "*.log", "*.tmp",
              "tools_pack_handover.py"]
TEXT_EXT = {".py", ".md", ".json", ".txt", ".ps1", ".html", ".csv", ".toml", ".ini",
            ".cfg", ".yaml", ".yml", ".js", ".svg", ".sh"}
AGENTS = os.path.join(HOME, ".claude", "agents")
EXTRA_TOP = ["COST_REDUCTION_REPORT.pdf", "COST_REDUCTION_REPORT.md"]
MAX_BYTES = 60 * 1024 * 1024

SECRET = [re.compile(p, re.I) for p in (
    # a key starts a token: "autodesk-unveils-..." in a URL is not "sk-..."
    r"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"ghp_[A-Za-z0-9]{30,}",
    r"xox[abp]-[A-Za-z0-9-]{10,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(api[_-]?key|secret|password|passwd|bearer|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
)]
PERSONAL = [re.compile(r"abdurlhaman\.kendi@gmail\.com", re.I),
            re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.I)]


def skip(name, is_dir):
    if is_dir:
        return name in SKIP_DIRS
    return any(fnmatch.fnmatch(name, p) for p in SKIP_FILES)


def copy_tree(src, dst, keep=None):
    n = 0
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if not skip(d, True)]
        for fn in fns:
            if skip(fn, False):
                continue
            p = os.path.join(dp, fn)
            if keep and not keep(p):
                continue
            if os.path.getsize(p) > MAX_BYTES:
                print(f"  too large, skipped: {p}")
                continue
            q = os.path.join(dst, os.path.relpath(p, src))
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(p, q)
            n += 1
    return n


def pipeline_keep(p):
    """Everything in the pipeline folder except third-party content kept in
    reference\\: the full text extracted from the DBC PDF, page images of it,
    and thumbnails of the sample drawings mined for layer conventions (the
    code that made them, and the derived rules/metadata, stay)."""
    rel = os.path.relpath(p, PIPE).replace("\\", "/").lower()
    if rel.startswith("reference/"):
        fn = os.path.basename(rel)
        if fn == "dbc_text.txt" or fn.endswith((".png", ".jpg", ".pdf")):
            return False
    return True


def sample_keep(p):
    """Deliverables only: sheets as PNG/PDF/DXF (not the sheet DWGs, which
    embed the third-party furniture blocks), the 3-D model DWG, glTF groups,
    renders, notes."""
    fn = os.path.basename(p).lower()
    if fn.endswith(".dwg"):
        return fn == "villa_3d_model.dwg"
    return os.path.splitext(fn)[1] in (".png", ".jpg", ".pdf", ".dxf", ".glb", ".json",
                                        ".md", ".txt", ".svg")


def sanitised_mcp_config():
    cfg = json.load(open(os.path.join(HOME, ".claude.json"), encoding="utf-8"))["mcpServers"]
    out = {}
    for name, s in cfg.items():
        if name not in ("autocad", "autocad-pro"):
            continue
        env = {}
        for k, v in (s.get("env") or {}).items():
            if re.search(r"key|token|secret|pass", k, re.I):
                v = "<SET-ME>"
            env[k] = str(v).replace(HOME, "%USERPROFILE%")
        out[name] = {"command": s["command"].replace(HOME, "%USERPROFILE%"),
                     "args": [a.replace(HOME, "%USERPROFILE%") for a in s.get("args", [])],
                     **({"env": env} if env else {})}
    return {"_comment": "Add under \"mcpServers\" in %USERPROFILE%\\.claude.json (or with `claude mcp add`); "
                        "replace %USERPROFILE% with your real paths; restart Claude Code after changes. "
                        "The autocad server also reads ACAD_ALLOW_RAW_COMMAND (default off), ACAD_WRITE_ROOTS, "
                        "ACAD_READ_ONLY, ACAD_AUDIT_LOG and VILLA3D_VIA_WSL from its env (UPDATE_2026-10-08.md).",
            "mcpServers": out}


def scan(root):
    bad = []
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for rx in SECRET + PERSONAL:
                for m in rx.finditer(t):
                    bad.append(f"{os.path.relpath(p, root)}: {rx.pattern[:40]} -> {m.group(0)[:60]}")
    return bad


def main(argv):
    rep = argv[0]
    date = argv[argv.index("--date") + 1] if "--date" in argv else "2026-09-26"
    stage = os.path.join(os.environ.get("TEMP", HOME), "handover", "package", NAME)
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    for fn in ("README_FIRST.md", "REPORT.md", "REPORT.html"):
        shutil.copy2(os.path.join(rep, fn), os.path.join(stage, fn))
    extras = EXTRA_TOP + sorted(f for f in os.listdir(rep) if fnmatch.fnmatch(f, "UPDATE_*.md"))
    for fn in extras:
        if os.path.isfile(os.path.join(rep, fn)):
            shutil.copy2(os.path.join(rep, fn), os.path.join(stage, fn))
    counts = {
        "pipeline": copy_tree(PIPE, os.path.join(stage, "pipeline"), keep=pipeline_keep),
        "skill": copy_tree(SKILL, os.path.join(stage, "skill", "architectural-cad")),
        "samples/villa": copy_tree(os.path.join(DESK, "Villa"), os.path.join(stage, "samples", "villa"),
                                   keep=sample_keep),
        "samples/fairway": copy_tree(os.path.join(DESK, "Fairway"), os.path.join(stage, "samples", "fairway"),
                                     keep=sample_keep),
        # the pinned agents (model per job): only this project's cad-* ones
        "agents": copy_tree(AGENTS, os.path.join(stage, "agents"),
                            keep=lambda p: fnmatch.fnmatch(os.path.basename(p), "cad-*.md"))
        if os.path.isdir(AGENTS) else 0,
    }
    # the two pre-generalisation files the render tests compare against (the
    # rest of the _pre_projects_0926 snapshot stays home)
    for rel in ("villa_blender.py", os.path.join("unreal", "build_scene.py"),
                "README.txt"):
        src = os.path.join(PIPE, "_pre_projects_0926", rel)
        if os.path.isfile(src):
            dst = os.path.join(stage, "pipeline", "_pre_projects_0926", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    status = os.path.join(stage, "samples", "fairway", "STATUS_STUDY_RECREATION.txt")
    os.makedirs(os.path.dirname(status), exist_ok=True)
    with open(status, "w", encoding="utf-8") as f:
        f.write("THE FAIRWAY VILLA -- STUDY RECREATION, NOT THE REAL HOUSE'S DRAWINGS\n\n"
                "These drawings, models and images recreate a Dubai Hills Estate villa from its\n"
                "public listing's figures and photographs. No floor plans were available: the\n"
                "layout, dimensions and levels are DESIGNED to match the published numbers\n"
                "(see pipeline/projects/fairway/BRIEF.md, assumptions A1-A10). The original\n"
                "design belongs to its architect and builder. Not for construction, permit\n"
                "submission or marketing of that property.\n")
    if os.path.isfile(os.path.join(rep, "PACKAGE_NOTES.md")):
        shutil.copy2(os.path.join(rep, "PACKAGE_NOTES.md"), os.path.join(stage, "PACKAGE_NOTES.md"))
    # the third-party AutoCAD MCP Pro server, full source WITH the local
    # patches (MIT licence, its LICENSE file travels with it); no .venv/.git
    counts["mcp/autocad-mcp-pro"] = copy_tree(PRO, os.path.join(stage, "mcp", "autocad-mcp-pro"))
    notes = os.path.join(stage, "mcp", "autocad-mcp-pro-notes")
    os.makedirs(notes)
    for fn in os.listdir(PRO):
        if re.match(r"(LOCAL_PATCHES|README|LICEN[CS]E|NOTICE)", fn, re.I) and os.path.isfile(os.path.join(PRO, fn)):
            shutil.copy2(os.path.join(PRO, fn), os.path.join(notes, fn))
    with open(os.path.join(stage, "mcp", "claude_mcp_config.example.json"), "w", encoding="utf-8") as f:
        json.dump(sanitised_mcp_config(), f, indent=2)
    bad = scan(stage)
    if bad:
        print("SECRET/PERSONAL DATA FOUND -- not zipping:")
        print("\n".join(bad[:50]))
        return 2
    rows, total = [], 0
    for dp, _dn, fns in os.walk(stage):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
            sz = os.path.getsize(p)
            total += sz
            rows.append(f"{sz:>12,}  {h[:16]}  {os.path.relpath(p, stage)}")
    with open(os.path.join(stage, "MANIFEST.txt"), "w", encoding="utf-8") as f:
        f.write(f"{NAME} -- {date}\n{len(rows)} files, {total:,} bytes (sha256 prefix)\n\n")
        f.write("\n".join(sorted(rows, key=lambda r: r[32:])) + "\n")
    if "--dry" in argv:
        print(json.dumps({"staged": stage, "files": len(rows), "bytes": total,
                          "counts": counts}, indent=1))
        return 0
    out_dir = os.path.join(DESK, NAME)
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, f"{NAME}_{date}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for dp, _dn, fns in os.walk(stage):
            for fn in fns:
                p = os.path.join(dp, fn)
                z.write(p, os.path.join(NAME, os.path.relpath(p, stage)))
    for fn in ["REPORT.html", "README_FIRST.md"] + extras:
        if os.path.isfile(os.path.join(stage, fn)):
            shutil.copy2(os.path.join(stage, fn), os.path.join(out_dir, fn))
    print(json.dumps({"zip": zpath, "bytes": os.path.getsize(zpath), "files": len(rows),
                      "counts": counts, "folder": out_dir}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
