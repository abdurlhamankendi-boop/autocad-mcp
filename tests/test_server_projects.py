"""Offline tests for projects in server.py: the `project` parameter of
villa_validate / villa_status / villa_run, the stale-module fix, the
per-design sheet list and the elevations stage.

    python -X utf8 -m unittest tests.test_server_projects -v   (from C:\\Users\\lsire\\autocad-mcp)
    python -X utf8 tests\\test_server_projects.py

No AutoCAD and no COM: villa_run is only called with dry_run=True (or made to
refuse before anything starts). Nothing is written to the Desktop: in-process
validation and the reference subprocesses run with VILLA_OUT pointed at a temp
folder (importing villa_colour creates the output folder), and the one real
subprocess -- run_project.py running the Fairway's villa_design.py, the design
validation -- writes only to a temp folder.

The designs are edited by other agents while this runs, so every comparison
with an independent reference is retried once if a save lands in between.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
FAIRWAY = PROJECT / "projects" / "fairway"

sys.path.insert(0, str(PROJECT))
os.environ.setdefault("ACAD_AUDIT_LOG", "0")    # test calls stay out of logs\mcp_calls.jsonl
import server  # noqa: E402

from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402


def _same(a, b) -> bool:
    return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))


class _TempOut:
    """VILLA_OUT -> a temp folder for the duration of a test class."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="villa_out_")
        cls._old_out = os.environ.get("VILLA_OUT")
        os.environ["VILLA_OUT"] = cls.tmp

    @classmethod
    def tearDownClass(cls):
        if cls._old_out is None:
            os.environ.pop("VILLA_OUT", None)
        else:
            os.environ["VILLA_OUT"] = cls._old_out
        shutil.rmtree(cls.tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# project resolution


class ProjectResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="villa_proj_")).resolve()
        cls.ext = cls.tmp / "outside"              # a design outside the pipeline
        cls.ext.mkdir()
        (cls.ext / "villa_design.py").write_text('OUT_NAME = "SrvTestOut"\n', encoding="utf-8")
        cls.empty = cls.tmp / "empty"              # a folder without a design
        cls.empty.mkdir()
        cls.evil = cls.tmp / "evil"                # OUT_NAME trying to leave the Desktop
        cls.evil.mkdir()
        (cls.evil / "villa_design.py").write_text('OUT_NAME = "..\\\\..\\\\Windows"\n',
                                                 encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_none_and_blank_are_the_villa(self):
        for arg in (None, "", "   "):
            ctx = server._project(arg, env={})
            self.assertTrue(ctx.is_villa, arg)
            self.assertEqual(ctx.name, "villa")
            self.assertTrue(_same(ctx.folder, PROJECT))
            self.assertIsNone(ctx.arg)
            self.assertEqual(ctx.run_key("plans"), "plans")      # records as before

    def test_name_resolves_under_projects(self):
        ctx = server._project("fairway", env={})
        self.assertFalse(ctx.is_villa)
        self.assertEqual(ctx.name, "fairway")
        self.assertTrue(_same(ctx.folder, FAIRWAY))
        self.assertTrue(_same(ctx.design_file, FAIRWAY / "villa_design.py"))
        self.assertEqual([_same(a, b) for a, b in zip(ctx.search, (FAIRWAY, PROJECT))],
                         [True, True])
        self.assertEqual(ctx.arg, "fairway")
        self.assertEqual(ctx.run_key("verify"), "fairway:verify")
        info = ctx.info()
        self.assertEqual(info["name"], "fairway")
        self.assertIn("FAIRWAY", info.get("title", ""))

    def test_paths_name_the_same_project(self):
        want = server._project("fairway", env={})
        for arg in ("projects/fairway", "projects\\fairway\\", str(FAIRWAY),
                    str(FAIRWAY) + "\\", str(FAIRWAY / "villa_design.py")):
            ctx = server._project(arg, env={})
            self.assertTrue(_same(ctx.folder, want.folder), arg)
            self.assertEqual((ctx.name, ctx.key), (want.name, want.key), arg)

    def test_pipeline_folder_is_the_villa(self):
        self.assertTrue(server._project(str(PROJECT), env={}).is_villa)
        self.assertTrue(server._project(str(PROJECT / "villa_design.py"), env={}).is_villa)

    def test_explicit_absolute_folder_elsewhere(self):
        ctx = server._project(str(self.ext), env={})
        self.assertFalse(ctx.is_villa)
        self.assertTrue(_same(ctx.folder, self.ext))
        self.assertEqual(ctx.arg, str(ctx.folder))       # not a name under projects\
        self.assertTrue(_same(ctx.key, self.ext))          # records keyed by the folder
        self.assertEqual(ctx.out, server.DESKTOP / "SrvTestOut")
        self.assertEqual(ctx.out_from, "OUT_NAME")

    def test_rejects_traversal_and_bad_paths(self):
        bad = ["..", "../fairway", "..\\projects\\fairway", "fairway/../../..",
               "projects/../../Windows", "projects/./fairway", "...", ". ",
               str(PROJECT / "projects" / ".." / "projects" / "fairway"),
               "C:fairway", "\\projects\\fairway", "/projects/fairway",
               "\\\\server\\share\\fairway", "//server/share/fairway", "\\\\?\\C:\\x",
               "nosuch", "fa*rway", "fairway?", "fair\x00way", "tests", "candidates",
               "C:\\Windows", str(self.empty), str(self.tmp / "missing"),
               "projects", "reference"]
        for arg in bad:
            with self.assertRaises(ToolError, msg=repr(arg)):
                server._project(arg, env={})

    def test_error_names_the_available_projects(self):
        with self.assertRaises(ToolError) as cm:
            server._project("nosuch", env={})
        self.assertIn("fairway", str(cm.exception))
        self.assertIn("omit project for the villa", str(cm.exception))

    def test_out_name_must_be_a_plain_folder(self):
        with self.assertRaises(ToolError):
            server._project(str(self.evil), env={})

    def test_out_dir_precedence(self):
        x, y = r"C:\somewhere\x", r"C:\somewhere\y"
        villa = lambda env: server._project(None, env=env)             # noqa: E731
        fair = lambda env: server._project("fairway", env=env)         # noqa: E731
        self.assertEqual(villa({}).out, server.DESKTOP / "Villa")
        self.assertIn(villa({}).out_from, ("default", "OUT_NAME"))
        self.assertEqual((villa({"VILLA_DIR": x}).out, villa({"VILLA_DIR": x}).out_from),
                         (Path(x), "VILLA_DIR"))
        both = {"VILLA_DIR": x, "VILLA_OUT": y}
        self.assertEqual((villa(both).out, villa(both).out_from), (Path(y), "VILLA_OUT"))
        # a project: Desktop\<OUT_NAME>; VILLA_DIR is the villa's and never applies
        self.assertEqual((fair({}).out, fair({}).out_from), (server.DESKTOP / "Fairway", "OUT_NAME"))
        self.assertEqual(fair({"VILLA_DIR": x}).out, server.DESKTOP / "Fairway")
        self.assertEqual(fair(both).out, Path(y))
        # the scripts get the same folder the server reads
        self.assertEqual(server._stage_env(villa({"VILLA_DIR": x}))["VILLA_OUT"], x)
        self.assertEqual(server._stage_env(fair({}))["VILLA_OUT"],
                         str(server.DESKTOP / "Fairway"))


# ---------------------------------------------------------------------------
# villa_validate: the stale-module fix

_REFERENCE = r"""
import contextlib, io, json, sys
root, d = sys.argv[1], sys.argv[2]
for p in (root, d):                      # as run_project.py: d first, root second
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
with contextlib.redirect_stdout(io.StringIO()):
    import villa_design as V, villa_furniture_spec as F
    issues = V.validate()
    try:                                 # villa_dbc may be mid-edit by another agent
        import villa_dbc as D
        bound = D.V.__file__
    except Exception as exc:
        D, bound = None, None
    try:
        dbc = D.checks() if D else None
    except Exception as exc:
        dbc = None
    furn = F.check()
    rooms = {fl: len(V.rooms_on(fl)) for fl in V.floors()}
    items = {fl: len(lst) for fl, lst in F.BY_FLOOR}
print(json.dumps({"design_file": V.__file__, "dbc_bound": bound, "issues": issues,
                  "dbc": dbc, "furniture": furn, "rooms": rooms, "items": items}))
"""

_SEV = re.compile(r"^\[(FATAL|MAJOR|MINOR|NOTE)\s*\]\s*(.*)$", re.S)


def _split(issues):
    out = {"fatal": [], "major": [], "minor": [], "notes": []}
    key = {"FATAL": "fatal", "MAJOR": "major", "MINOR": "minor", "NOTE": "notes"}
    for i in issues:
        m = _SEV.match(i)
        if m:
            out[key[m.group(1)]].append(m.group(2))
    return out


class StaleModules(_TempOut, unittest.TestCase):
    def _reference(self, folder: Path) -> dict:
        r = subprocess.run([sys.executable, "-X", "utf8", "-c", _REFERENCE, str(PROJECT),
                            str(folder)], capture_output=True, text=True, timeout=300,
                           cwd=str(PROJECT), env=dict(os.environ))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def _mismatch(self, got: dict, ref: dict) -> list[str]:
        bad = []
        if not _same(got["project"]["design_file"], ref["design_file"]):
            bad.append("design_file")
        if ref["dbc_bound"] and not (got["dbc"]["bound_to"]
                                     and _same(got["dbc"]["bound_to"], ref["design_file"])):
            bad.append("dbc bound to another design")
        if ref["dbc"] is None:                  # villa_dbc broken right now: not run
            if got["dbc"]["ran"]:
                bad.append("dbc ran where the reference could not")
        elif not got["dbc"]["ran"] or got["dbc"]["issues"] != ref["dbc"]:
            bad.append("dbc issues")
        want = _split(ref["issues"])
        for k in ("fatal", "major", "minor", "notes"):
            if got["design"][k] != want[k]:
                bad.append(k)
        if got["rooms"] != ref["rooms"]:
            bad.append("rooms")
        if got["furniture"]["items"] != ref["items"]:
            bad.append("furniture items")
        if len(got["furniture"]["issues"]) != len(ref["furniture"]):
            bad.append("furniture issues")
        return bad

    def test_villa_then_fairway_then_villa(self):
        order = [None, "fairway", None]
        folder = {None: PROJECT, "fairway": FAIRWAY}
        for attempt in range(2):
            got = [server.villa_validate(project=p) for p in order]
            refs = {p: self._reference(folder[p]) for p in (None, "fairway")}
            errors = {i: self._mismatch(g, refs[p]) for i, (g, p) in enumerate(zip(got, order))}
            if not any(errors.values()) or attempt == 1:
                break
        self.assertEqual({i: e for i, e in errors.items() if e}, {})
        villa, fair, villa2 = got
        self.assertEqual((villa["project"]["name"], fair["project"]["name"],
                          villa2["project"]["name"]), ("villa", "fairway", "villa"))
        # each names its own design, and its own DBC results were computed on it
        for g, p in zip(got, order):
            self.assertTrue(_same(g["project"]["design_file"], folder[p] / "villa_design.py"))
            if refs[p]["dbc_bound"]:
                self.assertTrue(_same(g["dbc"]["bound_to"], folder[p] / "villa_design.py"))
            self.assertTrue(g["summary"].startswith(g["project"]["name"] + ":"))
        # the Fairway has a basement and its own room counts
        self.assertIn("B1", fair["rooms"])
        self.assertNotIn("B1", villa["rooms"])
        self.assertNotEqual(villa["rooms"], fair["rooms"])
        self.assertIn("B1", fair["furniture"]["items"])
        self.assertEqual(villa["rooms"], villa2["rooms"])
        broken = [p or "villa" for p in refs if refs[p]["dbc"] is None]
        if broken:        # everything else matched; the DBC part could not be checked
            self.skipTest(f"villa_dbc.checks() fails right now for {broken} (being edited?)")
        for g in got:
            self.assertTrue(g["dbc"]["ran"])

    def test_a_stale_villa_dbc_left_in_sys_modules_is_not_used(self):
        """The bug itself: villa_dbc imported once stays bound to the first
        design. Seed exactly that, then validate the Fairway."""
        saved = list(sys.path)
        sys.path.insert(0, str(PROJECT))
        try:
            for m in [m for m in sys.modules if m.startswith("villa_")]:
                sys.modules.pop(m)
            import villa_dbc                                  # noqa: F401 -- the villa's
            self.assertTrue(_same(sys.modules["villa_dbc"].V.__file__,
                                  PROJECT / "villa_design.py"))
        finally:
            sys.path[:] = saved
        got = server.villa_validate(project="fairway")
        self.assertTrue(_same(got["dbc"]["bound_to"], FAIRWAY / "villa_design.py"))
        self.assertTrue(_same(got["project"]["design_file"], FAIRWAY / "villa_design.py"))

    def test_sys_path_and_modules_restored(self):
        before = list(sys.path)
        server.villa_validate(project="fairway")
        self.assertEqual(sys.path, before)
        self.assertEqual([m for m in sys.modules if m.startswith("villa_")], [])
        server.villa_validate()
        self.assertEqual(sys.path, before)
        self.assertEqual([m for m in sys.modules if m.startswith("villa_")], [])

    def test_bad_project_is_a_tool_error_before_anything_runs(self):
        import asyncio
        with self.assertRaises(ToolError) as cm:
            asyncio.run(server.mcp.call_tool("villa_validate", {"project": "../../Windows"}))
        self.assertIn("not allowed", str(cm.exception))

    def test_project_over_mcp_call_tool(self):
        import asyncio
        res = asyncio.run(server.mcp.call_tool("villa_validate", {"project": "fairway"}))
        self.assertFalse(res.is_error)
        self.assertEqual(res.structured_content["project"]["name"], "fairway")


# ---------------------------------------------------------------------------
# furniture issues on any floor


class FurnitureParse(unittest.TestCase):
    def test_every_floor_tag(self):
        got = server._furniture_issues([
            "[B1] sofa_3 in CINEMA runs into LOBBY", "[GF] bed in MASTER overlaps wc",
            "[FF] x", "[AX] y", "[RF] z", "untagged problem"])
        self.assertEqual([g["floor"] for g in got], ["B1", "GF", "FF", "AX", "RF", None])
        self.assertEqual(got[0]["issue"], "sofa_3 in CINEMA runs into LOBBY")
        self.assertEqual(got[-1]["issue"], "untagged problem")


# ---------------------------------------------------------------------------
# the stage table: elevations, and sheets from the design

_GEOM_SHEETS = r"""
import contextlib, io, json, sys
root, d = sys.argv[1], sys.argv[2]
for p in (root, d):
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
with contextlib.redirect_stdout(io.StringIO()):
    import villa_geom as G
print(json.dumps([n.replace("-", "") for _, n, _ in G.plan_sheets()]))
"""


class StageTable(_TempOut, unittest.TestCase):
    def _geom_sheets(self, folder: Path) -> list[str]:
        r = subprocess.run([sys.executable, "-X", "utf8", "-c", _GEOM_SHEETS, str(PROJECT),
                            str(folder)], capture_output=True, text=True, timeout=300,
                           cwd=str(PROJECT), env=dict(os.environ))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_elevations_stage_registered(self):
        spec = server._STAGES["elevations"]
        self.assertEqual(spec["scripts"], ["villa_elevations.py"])
        self.assertFalse(spec.get("com"))
        self.assertTrue(spec.get("checks"))
        self.assertEqual(set(spec["outputs"]),
                         {f"VILLA_{n}.{e}" for n in ("A201", "A202", "A203", "A204", "A301")
                          for e in ("dxf", "png")})
        tools = {t.name: t for t in __import__("asyncio").run(server.mcp.list_tools())}
        run = tools["villa_run"].input_schema["properties"]
        self.assertIn("elevations", run["stage"]["enum"])
        for name in ("villa_validate", "villa_status", "villa_run"):
            props = tools[name].input_schema["properties"]
            self.assertIn("project", props, name)
            self.assertNotIn("project", tools[name].input_schema.get("required", []), name)
            self.assertIn("project", tools[name].description, name)

    def test_sheet_outputs_follow_the_design(self):
        for arg, folder in ((None, PROJECT), ("fairway", FAIRWAY)):
            for attempt in range(2):
                plans = self._geom_sheets(folder)          # villa_geom.plan_sheets(), live
                ctx = server._project(arg)
                table = server._stage_table(ctx)
                if server._plan_sheets(ctx.folder)[0] == plans or attempt == 1:
                    break
            sheets = ["A101", *plans]
            self.assertEqual(table["plans"]["outputs"],
                             [f"VILLA_{s}.dxf" for s in sheets] + ["furniture_manifest.json"])
            self.assertEqual(table["colour"]["outputs"], [f"VILLA_{s}P.dxf" for s in sheets])
            self.assertEqual(table["load"]["outputs"],
                             [f"VILLA_{s}.dwg" for s in sheets] + [f"VILLA_{s}P.dwg" for s in sheets])
            self.assertEqual(table["load"]["inputs"],
                             [f"VILLA_{s}.dxf" for s in sheets] + [f"VILLA_{s}P.dxf" for s in sheets]
                             + ["furniture_manifest.json"])
            self.assertEqual(table["verify"]["inputs"],
                             [f"VILLA_{s}.dwg" for s in plans] + ["furniture_manifest.json"])
        # the Fairway's three plan sheets: A-102 B1, A-103 GF, A-104 FF
        self.assertEqual(server._plan_sheets(FAIRWAY)[0], ["A102", "A103", "A104"])

    def test_closure_resolves_in_the_project_folder_first(self):
        ctx = server._project("fairway")
        code = server._closure(["villa_cad.py"], ctx.search)
        by = {p.name: p for p in code}
        self.assertTrue(_same(by["villa_design.py"], FAIRWAY / "villa_design.py"))
        self.assertTrue(_same(by["villa_furniture_spec.py"], FAIRWAY / "villa_furniture_spec.py"))
        self.assertTrue(_same(by["villa_cad.py"], PROJECT / "villa_cad.py"))
        villa = {p.name: p for p in server._closure(["villa_cad.py"])}
        self.assertTrue(_same(villa["villa_design.py"], PROJECT / "villa_design.py"))

    def test_string_named_imports_are_traced(self):
        names = {p.name for p in server._closure(["villa_elevations.py"])}
        for need in ("villa_elevations.py", "villa_design.py", "villa_gltf.py", "plan_dxf.py"):
            self.assertIn(need, names)

    def test_sheets_from_a_failed_elevations_run_are_not_fresh(self):
        """villa_elevations writes its sheets even when a check fails (stamped
        CHECKS FAILED); status must not call them fresh. VILLA_OUT is a temp
        folder here, and the run record is faked (the real one is not touched)."""
        import time
        ctx = server._project(None)
        self.assertTrue(_same(ctx.out, self.tmp))
        for name in server._STAGES["elevations"]["outputs"]:
            (Path(self.tmp) / name).write_bytes(b"x")          # newer than every source
        now = time.time()
        old = server._load_runs
        try:
            server._load_runs = lambda: {}
            self.assertEqual(server._freshness(ctx)["elevations"]["state"], "fresh")
            server._load_runs = lambda: {"elevations": {"ok": False, "verdict": "failed",
                                                        "finished_epoch": now}}
            self.assertEqual(server._freshness(ctx)["elevations"]["state"], "failed")
            # a later regeneration outside the server wins over an old failed record
            server._load_runs = lambda: {"elevations": {"ok": False, "verdict": "failed",
                                                        "finished_epoch": now - 3600}}
            self.assertEqual(server._freshness(ctx)["elevations"]["state"], "fresh")
            # records are per design: the Fairway's failure is not the villa's
            server._load_runs = lambda: {"fairway:elevations": {"ok": False,
                                                                "finished_epoch": now}}
            self.assertEqual(server._freshness(ctx)["elevations"]["state"], "fresh")
        finally:
            server._load_runs = old

    def test_status_per_project(self):
        m0 = server._iso(os.path.getmtime(FAIRWAY / "villa_design.py"))
        s = server.villa_status(project="fairway")
        m1 = server._iso(os.path.getmtime(FAIRWAY / "villa_design.py"))
        ctx = server._project("fairway")
        self.assertEqual(s["project"]["name"], "fairway")
        self.assertTrue(_same(s["villa_dir"], ctx.out))
        self.assertEqual(s["sheets"]["plans"], ["A-102", "A-103", "A-104"])
        self.assertIn(s["design_modified"], (m0, m1))       # the design is being edited
        plans = s["stages"]["plans"]
        self.assertIn("VILLA_A104.dxf", [o["path"] for o in plans["outputs"]])
        self.assertIn(str(Path("projects", "fairway", "villa_design.py")), plans["sources"])
        self.assertIn(str(Path("projects", "fairway", "block_catalog.json")), plans["sources"])
        self.assertNotIn("villa_design.py", plans["sources"])      # not the villa's
        self.assertIn("villa_cad.py", plans["sources"])
        self.assertIn("project='fairway'", plans["run"])
        self.assertIn("elevations", s["stages"])
        villa = server.villa_status()
        self.assertEqual(villa["project"]["name"], "villa")
        self.assertIn("villa_design.py", villa["stages"]["plans"]["sources"])
        self.assertFalse(any(p.startswith("projects") for p in villa["stages"]["plans"]["sources"]))


# ---------------------------------------------------------------------------
# elevations verdict


def _fake_run(exit_code=0, checks=None, failed=False, timed_out=False):
    return {"exit_code": exit_code, "timed_out": timed_out, "failed_markers": failed,
            "unverified_markers": False, "verified_marker": False,
            "checks": None if checks is None else
            {"passed": checks[0], "total": checks[1], "line": f"{checks[0]}/{checks[1]} checks passed"}}


class ElevationsVerdict(unittest.TestCase):
    spec = server._STAGES["elevations"]

    def verdict(self, **kw):
        return server._verdict(self.spec, [_fake_run(**kw)], 1)

    def test_verdicts(self):
        self.assertEqual(self.verdict(checks=(37, 37)), "ok")
        self.assertEqual(self.verdict(exit_code=1, checks=(35, 37)), "failed")
        self.assertEqual(self.verdict(exit_code=1), "error")             # crashed, no line
        self.assertEqual(self.verdict(), "failed")                        # no verdict line
        self.assertEqual(self.verdict(checks=(37, 37), failed=True), "failed")  # CHECKS FAILED
        self.assertEqual(self.verdict(exit_code=1, checks=(37, 37)), "error")
        self.assertEqual(self.verdict(checks=(0, 0)), "failed")
        self.assertEqual(self.verdict(timed_out=True), "timeout")
        self.assertEqual(server._verdict(self.spec, [], 1), "timeout")
        # the other stages keep their rules
        self.assertEqual(server._verdict(server._STAGES["plans"], [_fake_run(exit_code=1)], 1),
                         "error")
        self.assertEqual(server._verdict(server._STAGES["plans"], [_fake_run()], 1), "ok")

    def test_lines_the_script_prints(self):
        m = server._CHECKS_MARK.search("...\n\n  37/37 checks passed   212s   -> C:\\x\\Villa\n")
        self.assertEqual((m.group(1), m.group(2)), ("37", "37"))
        fail = lambda s: any(p.search(s) for p in server._FAIL_MARKS)   # noqa: E731
        self.assertTrue(fail("CHECKS FAILED (2) -- NOT FOR ISSUE"))
        self.assertTrue(fail("  FAIL  A-201: every opening found  3 missing"))
        self.assertFalse(fail("  PASS  A-201: every opening found  24/24"))
        self.assertFalse(fail("  37/37 checks passed   212s"))

    def test_real_process_env_and_checks_line(self):
        code = ("import os, sys; print('out', os.environ.get('VILLA_OUT')); "
                "print('dd', os.environ.get('VILLA_DESIGN_DIR')); "
                "print('  3/4 checks passed   1s'); sys.exit(1)")
        os.environ["VILLA_DESIGN_DIR"] = "should-be-removed"
        try:
            r = server._run_proc([sys.executable, "-X", "utf8", "-c", code], 60, io.StringIO(),
                                 {"VILLA_OUT": r"C:\x\y", "VILLA_DESIGN_DIR": None})
        finally:
            os.environ.pop("VILLA_DESIGN_DIR", None)
        self.assertIn(r"out C:\x\y", r["stdout_tail"])
        self.assertIn("dd None", r["stdout_tail"])
        self.assertEqual(r["checks"]["passed"], 3)
        self.assertEqual(r["checks"]["total"], 4)
        self.assertEqual(server._verdict(self.spec, [r], 1), "failed")


# ---------------------------------------------------------------------------
# villa_run command lines


class ProjectRunCommands(unittest.TestCase):
    def test_villa_command_line_unchanged(self):
        r = server.villa_run(stage="plans", dry_run=True)
        self.assertEqual(r["commands"], [subprocess.list2cmdline(
            [sys.executable, "-X", "utf8", str(PROJECT / "villa_cad.py")])])
        self.assertEqual(r["project"]["name"], "villa")
        self.assertEqual(r["env"]["VILLA_OUT"], str(server._project(None).out))
        self.assertIsNone(r["env"]["VILLA_DESIGN_DIR"])

    def test_project_goes_through_run_project(self):
        ctx = server._project("fairway")
        r = server.villa_run(stage="plans", project="fairway", dry_run=True)
        argv = server._stage_commands("plans", [], ctx)[0]
        self.assertEqual(argv, [sys.executable, "-X", "utf8", str(PROJECT / "run_project.py"),
                                str(ctx.folder), "villa_cad.py"])
        self.assertEqual(r["commands"], [subprocess.list2cmdline(argv)])
        self.assertEqual(r["project"]["name"], "fairway")
        self.assertTrue(_same(r["project"]["design_file"], FAIRWAY / "villa_design.py"))
        self.assertEqual(r["env"], {"VILLA_OUT": str(ctx.out), "VILLA_DESIGN_DIR": str(ctx.folder)})
        self.assertIn("VILLA_A104.dxf", r["outputs"])            # the B1 sheet shifts FF to A-104
        # the same project named by path gives the same command
        r2 = server.villa_run(stage="plans", project=str(FAIRWAY), dry_run=True)
        self.assertEqual(r2["commands"], r["commands"])

    def test_com_and_elevations_stages_for_a_project(self):
        r = server.villa_run(stage="verify3d", project="fairway", dry_run=True)
        self.assertTrue(r["com_stage"])
        self.assertEqual(len(r["commands"]), 3)
        for cmd, script in zip(r["commands"], ("villa_3d_verify.py", "villa_pool_check.py",
                                               "villa_window_check.py")):
            self.assertIn("run_project.py", cmd)
            self.assertIn(str(FAIRWAY), cmd)
            self.assertTrue(cmd.endswith(" " + script), cmd)
        e = server.villa_run(stage="elevations", project="fairway", dry_run=True)
        self.assertFalse(e["com_stage"])
        self.assertTrue(e["commands"][0].endswith(" villa_elevations.py"))
        self.assertIn("VILLA_A301.png", e["outputs"])
        # the native command; where it runs (WSL under Smart App Control) is
        # tests\test_server_wsl.py's business
        with mock.patch.dict(os.environ, {"VILLA3D_VIA_WSL": "0"}):
            v = server.villa_run(stage="elevations", dry_run=True)
        self.assertEqual(v["commands"], [subprocess.list2cmdline(
            [sys.executable, "-X", "utf8", str(PROJECT / "villa_elevations.py")])])

    def test_render_for_a_project_needs_villa_blender_to_read_the_design_dir(self):
        blender_reads = "VILLA_DESIGN_DIR" in (PROJECT / "villa_blender.py").read_text(
            encoding="utf-8", errors="replace")
        if not server.BLENDER.exists():
            self.skipTest("Blender not installed")
        r = server.villa_run(stage="render", project="fairway", dry_run=True)
        self.assertEqual(bool(r.get("warning")), not blender_reads)
        self.assertEqual(r["env"]["VILLA_DESIGN_DIR"], str(server._project("fairway").folder))
        old = server._mentions
        server._mentions = lambda *a: False           # force the guard: nothing may start
        try:
            with self.assertRaises(ToolError) as cm:
                server.villa_run(stage="render", project="fairway")
            self.assertIn("refused", str(cm.exception))
        finally:
            server._mentions = old

    def test_bad_project_refused_by_villa_run_and_status(self):
        for bad in ("..\\..", "C:\\Windows", "nosuch"):
            with self.assertRaises(ToolError):
                server.villa_run(stage="plans", project=bad, dry_run=True)
            with self.assertRaises(ToolError):
                server.villa_status(project=bad)

    def test_design_validation_really_runs_through_the_bootstrap(self):
        """The one real subprocess: the command villa_run builds for a project,
        running the Fairway's own villa_design.py (its validation report) with
        VILLA_OUT in a temp folder. Its counts must match villa_validate."""
        ctx = server._project("fairway")
        argv = server._script_argv(ctx, "villa_design.py")
        self.assertEqual(argv[3:], [str(PROJECT / "run_project.py"), str(ctx.folder),
                                    "villa_design.py"])
        tmp = tempfile.mkdtemp(prefix="villa_out_")
        old = os.environ.get("VILLA_OUT")
        os.environ["VILLA_OUT"] = tmp            # in-process validation too
        try:
            env = dict(server._stage_env(ctx), VILLA_OUT=tmp)
            for attempt in range(2):
                log = io.StringIO()                      # the full stdout goes to the log
                r = server._run_proc(argv, 300, log, env)
                text = log.getvalue()
                got = server.villa_validate(project="fairway")
                m = re.search(r"VALIDATION: (\d+) fatal, (\d+) major", text)
                if (m and (int(m.group(1)), int(m.group(2))) ==
                        (len(got["design"]["fatal"]), len(got["design"]["major"]))) or attempt:
                    break
        finally:
            if old is None:
                os.environ.pop("VILLA_OUT", None)
            else:
                os.environ["VILLA_OUT"] = old
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(r["exit_code"], 0, r["stderr_tail"])
        self.assertIn(f"[run_project] design {ctx.folder}", text)
        self.assertIn(f"[run_project] out    {tmp}", text)
        self.assertIn("THE FAIRWAY VILLA", text)
        self.assertIn(f"env: {json.dumps(env)}", text)          # logged with the command
        self.assertIsNotNone(m, text)
        self.assertEqual((int(m.group(1)), int(m.group(2))),
                         (len(got["design"]["fatal"]), len(got["design"]["major"])))


if __name__ == "__main__":
    unittest.main(verbosity=2)
