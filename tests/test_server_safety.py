"""Offline tests for the safety gates and the audit log of server.py.

    python -X utf8 tests\\test_server_safety.py            (from C:\\Users\\lsire\\autocad-mcp)
    python -X utf8 -m unittest tests.test_server_safety -v

No AutoCAD and no COM: server._com is replaced by a recorder for every test,
so a tool body that got past a gate returns a stub instead of attaching, and
acad_screenshot's window lookup and capture are stubbed. The audit log goes
to a temp folder, and every switch is set per test and restored afterwards:

  * raw command gate (ACAD_ALLOW_RAW_COMMAND), on and off, and proof that no
    internal caller depends on the acad_send_command tool;
  * write roots (ACAD_WRITE_ROOTS / defaults): traversal, other drive, UNC
    and device paths, the prefix trick, a junction escape, in-place save,
    quoted entries, a variable with no usable folder;
  * read-only mode (ACAD_READ_ONLY): every registered tool is classified,
    changing tools refuse, read tools, dry runs and a screenshot into %TEMP%
    still work; a design outside the villa / projects\\ never runs, and the
    screenshot check never resolves a network path;
  * audit log: one line per call (also for calls the SDK rejects), defaults
    included, truncation (the raw command is kept whole), ASCII-only lines,
    rotation, failures swallowed;
  * the tool listing (names, schemas, descriptions, annotations) is exactly
    the pre-hardening one (tests\\baselines\\tool_listing_pre_hardening_1008.json,
    generated from server.pre_hardening_1008.py before the change).
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import inspect
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SERVER = PROJECT / "server.py"
BACKUP = PROJECT / "server.pre_hardening_1008.py"
BASELINE = HERE / "baselines" / "tool_listing_pre_hardening_1008.json"

sys.path.insert(0, str(PROJECT))
import server  # noqa: E402

from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

SWITCHES = ("ACAD_ALLOW_RAW_COMMAND", "ACAD_READ_ONLY", "ACAD_WRITE_ROOTS", "ACAD_AUDIT_LOG")
TEMP = os.path.realpath(tempfile.gettempdir())
HOME = os.path.expanduser("~")

# The tools that only read (readOnlyHint=True). Written out so that a new tool,
# or a changed hint, shows up here as a decision someone has to make.
EXPECTED_READ = {
    "acad_status", "acad_wait_idle", "acad_list_drawings", "acad_list_orphans",
    "acad_list_layers", "acad_summarize_entities", "acad_list_blocks", "acad_measure_entity",
    "villa_validate", "villa_status", "dxf_info", "dxf_list_entities", "dxf_extract_text"}
# ...plus calls that only inspect: acad_purge_and_audit is a dry run by default.
ALLOWED_WITH_DEFAULTS = EXPECTED_READ | {"acad_purge_and_audit"}

_TMP: Path | None = None
_DXF: Path | None = None
_ORIGINAL_AUDIT_PATH = server._AUDIT_PATH


def setUpModule():
    global _TMP, _DXF
    _TMP = Path(tempfile.mkdtemp(prefix="acad_safety_")).resolve()
    import logging

    import ezdxf
    logging.getLogger("ezdxf").setLevel(logging.WARNING)    # new-document chatter
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0), (1000, 0))
    msp.add_text("SAFETY", dxfattribs={"insert": (0, 100), "height": 250})
    _DXF = _TMP / "safety.dxf"
    doc.saveas(str(_DXF))


def tearDownModule():
    if _TMP is not None:
        shutil.rmtree(_TMP, ignore_errors=True)


def _tools() -> dict:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


class _Safe(unittest.TestCase):
    """Every switch unset, the audit log in a temp folder, COM replaced."""

    def setUp(self):
        self._env = {k: os.environ.pop(k, None) for k in SWITCHES}
        self.tmp = Path(tempfile.mkdtemp(dir=_TMP))
        self.log = self.tmp / "logs" / "mcp_calls.jsonl"
        self.com_calls: list[str] = []

        def fake_com(job, *, what, **kw):
            self.com_calls.append(what)
            return {"stub": what, "plotted": True, "restore_errors": []}

        self._patches = [mock.patch.object(server, "_AUDIT_PATH", self.log),
                         mock.patch.object(server, "_com", fake_com)]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in reversed(self._patches):
            p.stop()
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        server._CALLS.depth = 0

    def env(self, **vals):
        """Set switches for the rest of this test (restored in tearDown)."""
        for k, v in vals.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def lines(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(ln) for ln in self.log.read_text(encoding="utf-8").splitlines()]

    def assertRefused(self, gate: str, fn, *a, **kw) -> server._Refused:
        with self.assertRaises(server._Refused) as cm:
            fn(*a, **kw)
        self.assertEqual(cm.exception.gate, gate, str(cm.exception))
        return cm.exception


# ---------------------------------------------------------------------------
# 1. raw command gate


class RawCommandGate(_Safe):
    def test_off_by_default(self):
        e = self.assertRefused("raw_command", server.acad_send_command, command="_.ZOOM\n_E")
        msg = str(e)
        self.assertIn("ACAD_ALLOW_RAW_COMMAND=1", msg)
        self.assertIn("restart Claude Code", msg)
        self.assertNotIn("\n", msg)                          # a one-line how-to
        self.assertEqual(self.com_calls, [])                 # nothing reached AutoCAD

    def test_only_1_or_true_opens_it(self):
        for v in ("0", "false", "yes", "", "2"):
            self.env(ACAD_ALLOW_RAW_COMMAND=v)
            self.assertRefused("raw_command", server.acad_send_command, command="_.REGEN")
        for v in ("1", "true", "TRUE", " True "):
            self.env(ACAD_ALLOW_RAW_COMMAND=v)
            out = server.acad_send_command(command="_.REGEN")
            self.assertEqual(out["stub"], "acad_send_command", v)
        self.assertEqual(self.com_calls, ["acad_send_command"] * 4)

    def test_read_when_called_not_at_import(self):
        self.env(ACAD_ALLOW_RAW_COMMAND="1")
        server.acad_send_command(command="_.REGEN")
        self.env(ACAD_ALLOW_RAW_COMMAND=None)
        self.assertRefused("raw_command", server.acad_send_command, command="_.REGEN")

    def test_denylist_still_applies_when_open(self):
        self.env(ACAD_ALLOW_RAW_COMMAND="1")
        with self.assertRaises(ToolError) as cm:
            server.acad_send_command(command="SHELL\n")
        self.assertIn("launches programs", str(cm.exception))
        self.assertEqual(self.com_calls, [])

    def test_refusal_reaches_the_client(self):
        with self.assertRaises(ToolError) as cm:
            asyncio.run(server.mcp.call_tool("acad_send_command", {"command": "_.REGEN"}))
        self.assertIn("ACAD_ALLOW_RAW_COMMAND=1", str(cm.exception))


class InternalCallers(_Safe):
    """The gate sits on the tool; nothing else in the server may depend on it."""

    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SERVER.read_text(encoding="utf-8"))
        cls.owner: dict[int, str] = {}                   # id(node) -> enclosing top-level def
        for top in cls.tree.body:
            if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(top):
                    cls.owner[id(n)] = top.name

    def where(self, pred) -> list[str]:
        return [self.owner.get(id(n), "<module>") for n in ast.walk(self.tree) if pred(n)]

    def test_send_command_is_used_only_by_the_tool(self):
        hits = self.where(lambda n: isinstance(n, ast.Attribute) and n.attr == "SendCommand")
        self.assertEqual(hits, ["acad_send_command"])

    def test_nobody_calls_the_tool_function(self):
        calls = self.where(lambda n: isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                           and n.func.id == "acad_send_command")
        self.assertEqual(calls, [])

    def test_gate_variable_is_read_only_by_the_tool(self):
        refs = self.where(lambda n: isinstance(n, ast.Constant)
                          and n.value == "ACAD_ALLOW_RAW_COMMAND")
        self.assertEqual(refs, ["acad_send_command"])

    def test_pipeline_stages_unaffected(self):
        """build3d sends commands from its own process (villa_3d_build.py)."""
        self.assertFalse(os.environ.get("ACAD_ALLOW_RAW_COMMAND"))
        r = server.villa_run(stage="build3d", dry_run=True)
        self.assertTrue(r["dry_run"])
        self.assertIn("villa_3d_build.py", r["commands"][0])
        self.assertIn("SendCommand", (PROJECT / "villa_3d_build.py").read_text(encoding="utf-8"))

    def test_plot_and_purge_unaffected(self):
        out = server.acad_purge_and_audit()
        self.assertEqual(out["stub"], "acad_purge_and_audit")
        pdf = self.tmp / "sheet.pdf"

        def plotting_com(job, *, what, **kw):           # the plot writes its temp file
            self.com_calls.append(what)
            Path(str(pdf)[:-4] + ".~plot.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
            return {"plotted": True, "restore_errors": []}

        with mock.patch.object(server, "_com", plotting_com):
            res = server.acad_export_pdf(path=str(pdf))
        self.assertTrue(pdf.exists())
        self.assertEqual(res["path"], str(pdf))
        self.assertEqual(self.com_calls, ["acad_purge_and_audit", "acad_export_pdf"])

    def test_nested_tool_call_is_one_call(self):
        """villa_run calls acad_status in-process: only the outer call is gated
        and logged."""
        self.env(ACAD_READ_ONLY="1")
        server._CALLS.depth = 1                         # as inside another tool
        try:
            self.assertEqual(server.acad_new_drawing()["stub"], "acad_new_drawing")
        finally:
            server._CALLS.depth = 0
        self.assertEqual(self.lines(), [])
        self.assertRefused("read_only", server.acad_new_drawing)
        self.assertEqual(len(self.lines()), 1)


# ---------------------------------------------------------------------------
# 2. write roots


class WriteRoots(_Safe):
    def test_default_roots(self):
        roots = {os.path.normcase(r) for r in server._write_roots()}
        for want in (os.path.join(HOME, "OneDrive", "Desktop"), os.path.join(HOME, "Desktop"),
                     str(PROJECT), TEMP):
            self.assertIn(os.path.normcase(os.path.realpath(want)), roots)
        self.assertEqual(len(roots), 4)

    def test_allowed(self):
        for p in (os.path.join(TEMP, "x.pdf"), str(PROJECT / "sub" / "x.pdf"),
                  str(PROJECT / "x.pdf"), os.path.join(HOME, "OneDrive", "Desktop", "V", "x.pdf"),
                  os.path.join(HOME, "Desktop", "x.png"),
                  str(PROJECT).upper() + "\\X.PDF",               # case-insensitive
                  str(PROJECT / "a" / ".." / "x.pdf")):           # '..' that stays inside
            server._check_write_path(p, "t")

    def test_refused(self):
        bad = {
            "traversal": str(PROJECT) + "\\..\\autocad-mcp-evil\\x.pdf",
            "traversal up": os.path.join(TEMP, "..", "..", "x.pdf"),
            "traversal / ": str(PROJECT).replace("\\", "/") + "/../../x.pdf",
            "other drive": "D:\\out\\x.pdf",
            "unmapped drive": "Z:\\x.pdf",
            "UNC": "\\\\server\\share\\x.pdf",
            "UNC slashes": "//server/share/x.pdf",
            "device": "\\\\?\\" + str(PROJECT / "x.pdf"),
            "prefix trick": str(PROJECT) + "-evil\\x.pdf",
            "prefix trick 2": os.path.join(HOME, "Desktop2", "x.pdf"),
            "drive root": "C:\\x.pdf",
            "windows": "C:\\Windows\\System32\\x.png",
        }
        for label, p in bad.items():
            with self.subTest(label):
                self.assertRefused("write_roots", server._check_write_path, p, "t")

    def test_error_names_the_roots(self):
        e = self.assertRefused("write_roots", server._check_write_path, "C:\\x.pdf", "acad_save")
        self.assertIn(str(PROJECT), str(e))
        self.assertIn(TEMP, str(e))
        self.assertIn("ACAD_WRITE_ROOTS", str(e))

    def test_env_roots_replace_the_defaults(self):
        mine = self.tmp / "out"
        self.env(ACAD_WRITE_ROOTS=os.pathsep.join([str(mine), "relative\\ignored", ""]))
        self.assertEqual([os.path.normcase(r) for r in server._write_roots()],
                         [os.path.normcase(os.path.realpath(mine))])
        server._check_write_path(str(mine / "x.pdf"), "t")
        self.assertRefused("write_roots", server._check_write_path, str(PROJECT / "x.pdf"), "t")
        self.assertRefused("write_roots", server._check_write_path,
                           str(mine) + "-evil\\x.pdf", "t")

    def test_quoted_entry_accepted(self):
        mine = self.tmp / "quoted"
        self.env(ACAD_WRITE_ROOTS=f'"{mine}"')
        self.assertEqual([os.path.normcase(r) for r in server._write_roots()],
                         [os.path.normcase(os.path.realpath(mine))])
        server._check_write_path(str(mine / "x.pdf"), "t")

    def test_no_usable_root_says_so(self):
        for raw in ("relative\\only", "''", os.pathsep.join(["a", "b\\c"])):
            with self.subTest(raw):
                self.env(ACAD_WRITE_ROOTS=raw)
                self.assertEqual(server._write_roots(), [])
                e = self.assertRefused("write_roots", server._check_write_path,
                                       str(PROJECT / "x.pdf"), "acad_export_pdf")
                self.assertIn("ACAD_WRITE_ROOTS names no absolute folder", str(e))

    def test_junction_escape(self):
        try:
            import _winapi
            create = _winapi.CreateJunction
        except (ImportError, AttributeError):
            self.skipTest("no junctions here")
        root, outside = self.tmp / "root", self.tmp / "outside"
        root.mkdir()
        outside.mkdir()
        link = root / "link"
        create(str(outside), str(link))
        try:
            self.env(ACAD_WRITE_ROOTS=str(root))
            server._check_write_path(str(root / "x.png"), "t")
            self.assertRefused("write_roots", server._check_write_path, str(link / "x.png"), "t")
        finally:
            os.rmdir(link)                              # the junction only

    def test_save_as_outside_refused_before_autocad(self):
        e = self.assertRefused("write_roots", server.acad_save, path="C:\\Windows\\x.dwg")
        self.assertIn("acad_save", str(e))
        self.assertEqual(self.com_calls, [])
        self.assertEqual(server.acad_save(path=str(self.tmp / "x.dwg"))["stub"], "acad_save")

    def test_save_in_place_not_limited(self):
        self.env(ACAD_WRITE_ROOTS=str(self.tmp / "nowhere"))
        self.assertEqual(server.acad_save()["stub"], "acad_save")
        self.assertEqual(server.acad_save(drawing="VILLA_A102.dwg")["stub"], "acad_save")

    def test_pdf_outside_refused_and_nothing_created(self):
        target = Path(str(PROJECT) + "-evil") / "sub" / "x.pdf"
        self.assertRefused("write_roots", server.acad_export_pdf, path=str(target))
        self.assertFalse(target.parent.exists())
        self.assertEqual(self.com_calls, [])

    def test_screenshot_outside_refused_and_inside_written(self):
        from PIL import Image as PILImage
        target = Path(str(PROJECT) + "-evil") / "shot"
        self.assertRefused("write_roots", server.acad_screenshot, path=str(target))
        self.assertFalse(target.parent.exists())
        img = PILImage.new("RGB", (64, 48), (200, 10, 10))
        with mock.patch.object(server, "_find_acad_windows", lambda: [(7, "AutoCAD")]), \
                mock.patch.object(server, "_capture_window", lambda hwnd: (img, "stub")):
            out = server.acad_screenshot(path=str(self.tmp / "shot"), include_image=False)
        meta = json.loads(out[-1])
        self.assertEqual(meta["path"], str(self.tmp / "shot.png"))
        self.assertTrue((self.tmp / "shot.png").exists())

    def test_refusal_logged_with_its_gate(self):
        with self.assertRaises(ToolError):
            asyncio.run(server.mcp.call_tool("acad_export_pdf", {"path": "C:\\x.pdf"}))
        rec = self.lines()[-1]
        self.assertEqual((rec["tool"], rec["outcome"], rec["gate"]),
                         ("acad_export_pdf", "error", "write_roots"))


# ---------------------------------------------------------------------------
# 3. read-only mode


class ReadOnlyMode(_Safe):
    @classmethod
    def setUpClass(cls):
        cls.tools = _tools()

    def defaults(self, name: str) -> dict:
        sig = inspect.signature(getattr(server, name))
        return {k: p.default for k, p in sig.parameters.items()
                if p.default is not inspect.Parameter.empty}

    def test_every_tool_classified(self):
        self.assertEqual(set(server._ANNOTATIONS), set(self.tools))
        for name, t in self.tools.items():
            self.assertIsInstance(t.annotations.read_only_hint, bool, name)
            self.assertEqual(t.annotations, server._ANNOTATIONS[name], name)
        ro = {n for n, t in self.tools.items() if t.annotations.read_only_hint}
        self.assertEqual(ro, EXPECTED_READ)
        self.env(ACAD_READ_ONLY="1")
        allowed = {n for n in self.tools
                   if server._read_only_refusal(n, self.defaults(n)) is None}
        self.assertEqual(allowed, ALLOWED_WITH_DEFAULTS)

    def test_off_unless_1_or_true(self):
        for v in ("0", "false", "", "no"):
            self.env(ACAD_READ_ONLY=v)
            self.assertEqual(server.acad_erase(handle="2A")["stub"], "acad_erase")
        for v in ("1", "true", "TRUE"):
            self.env(ACAD_READ_ONLY=v)
            self.assertRefused("read_only", server.acad_erase, handle="2A")

    def test_every_changing_tool_refuses(self):
        self.env(ACAD_READ_ONLY="1", ACAD_ALLOW_RAW_COMMAND="1")
        for name in sorted(set(self.tools) - ALLOWED_WITH_DEFAULTS):
            with self.subTest(name):
                e = self.assertRefused("read_only", getattr(server, name))
                self.assertIn("ACAD_READ_ONLY", str(e))
        self.assertEqual(self.com_calls, [])
        refused = [r for r in self.lines() if r.get("gate") == "read_only"]
        self.assertEqual(len(refused), len(set(self.tools) - ALLOWED_WITH_DEFAULTS))

    def test_refusal_over_mcp(self):
        self.env(ACAD_READ_ONLY="1")
        with self.assertRaises(ToolError) as cm:
            asyncio.run(server.mcp.call_tool("acad_erase", {"handle": "2A"}))
        self.assertIn("read-only", str(cm.exception))

    def test_read_tools_still_work(self):
        self.env(ACAD_READ_ONLY="1")
        for name, kw in (("acad_status", {}), ("acad_wait_idle", {}),
                         ("acad_list_drawings", {}), ("acad_list_orphans", {}),
                         ("acad_list_layers", {}), ("acad_summarize_entities", {}),
                         ("acad_list_blocks", {}), ("acad_measure_entity", {"handle": "2A"})):
            with self.subTest(name):
                self.assertEqual(getattr(server, name)(**kw)["stub"], name)
        self.assertEqual(server.dxf_info(str(_DXF))["total_entities"], 2)
        self.assertEqual(len(server.dxf_list_entities(str(_DXF))), 2)
        self.assertEqual(server.dxf_extract_text(str(_DXF))[0]["text"], "SAFETY")
        old = os.environ.get("VILLA_OUT")
        os.environ["VILLA_OUT"] = str(self.tmp / "villa_out")    # read nothing on the Desktop
        try:
            self.assertIn("stages", server.villa_status())
            try:
                server.villa_validate()
            except server._Refused:
                raise
            except ToolError:
                pass                                 # a design mid-edit: not the gate
        finally:
            if old is None:
                os.environ.pop("VILLA_OUT", None)
            else:
                os.environ["VILLA_OUT"] = old

    def test_dry_runs_allowed(self):
        self.env(ACAD_READ_ONLY="1")
        self.assertTrue(server.villa_run(stage="plans", dry_run=True)["dry_run"])
        self.assertRefused("read_only", server.villa_run, stage="plans")
        self.assertEqual(server.acad_purge_and_audit()["stub"], "acad_purge_and_audit")
        self.assertRefused("read_only", server.acad_purge_and_audit, dry_run=False)
        self.assertEqual(server.acad_close_orphans(dry_run=True)["stub"], "acad_close_orphans")
        self.assertRefused("read_only", server.acad_close_orphans)

    def test_screenshot_into_temp_only(self):
        from PIL import Image as PILImage
        self.env(ACAD_READ_ONLY="1")
        img = PILImage.new("RGB", (32, 32))
        with mock.patch.object(server, "_find_acad_windows", lambda: [(7, "AutoCAD")]), \
                mock.patch.object(server, "_capture_window", lambda hwnd: (img, "stub")):
            server.acad_screenshot(path=str(self.tmp / "ro"), include_image=False)
            self.assertTrue((self.tmp / "ro.png").exists())
            self.assertRefused("read_only", server.acad_screenshot,
                               path=str(PROJECT / "ro_test_shot.png"))
            self.assertRefused("read_only", server.acad_screenshot,
                               path=str(self.tmp / "ro2"), drawing="VILLA_A102.dwg")
        self.assertFalse((PROJECT / "ro_test_shot.png").exists())
        self.assertEqual(self.com_calls, [])

    def test_screenshot_gate_never_resolves_a_network_path(self):
        """Resolving \\\\host\\share would open an SMB connection to that host."""
        self.env(ACAD_READ_ONLY="1")
        seen: list[str] = []
        real = os.path.realpath

        def spy(p, *a, **kw):
            seen.append(str(p))
            return real(p, *a, **kw) if not str(p).startswith(("\\\\", "//")) else str(p)

        with mock.patch.object(server.os.path, "realpath", spy):
            for p in ("\\\\203.0.113.9\\share\\cap", "//203.0.113.9/share/cap"):
                self.assertRefused("read_only", server.acad_screenshot, path=p)
                self.assertRefused("write_roots", server._check_write_path, p, "t")
        self.assertEqual([s for s in seen if s.startswith(("\\\\", "//"))], [])
        self.assertEqual(self.com_calls, [])

    def test_foreign_design_never_runs(self):
        """villa_status / villa_validate (read-only tools) and a villa_run dry
        run all execute the design file; read-only mode refuses one from
        outside the villa and projects\\."""
        evil = self.tmp / "evil_design"
        evil.mkdir()
        marker = self.tmp / "PWNED.txt"
        (evil / "villa_design.py").write_text(
            f"open({str(marker)!r}, 'a').write('ran\\n')\n"
            "def floors():\n    return ['GF']\n", encoding="utf-8")
        self.env(ACAD_READ_ONLY="1")
        old = os.environ.get("VILLA_OUT")
        os.environ["VILLA_OUT"] = str(self.tmp / "villa_out")
        try:
            for fn, kw in ((server.villa_status, {}), (server.villa_validate, {}),
                           (server.villa_run, {"stage": "plans", "dry_run": True}),
                           (server.villa_run, {"stage": "plans"})):
                for proj in (str(evil), str(evil / "villa_design.py")):
                    with self.subTest(fn.__name__, project=proj):
                        e = self.assertRefused("read_only", fn, project=proj, **kw)
                        self.assertIn("runs its villa_design.py", str(e))
            self.assertFalse(marker.exists())
            # Over MCP too, and logged with its gate.
            with self.assertRaises(ToolError):
                asyncio.run(server.mcp.call_tool("villa_status", {"project": str(evil)}))
            self.assertFalse(marker.exists())
            self.assertEqual(self.lines()[-1]["gate"], "read_only")
        finally:
            if old is None:
                os.environ.pop("VILLA_OUT", None)
            else:
                os.environ["VILLA_OUT"] = old

    def test_pipeline_designs_still_readable(self):
        """The villa and projects\\<name> are the pipeline's own designs."""
        self.assertIsNone(server._foreign_design(None))
        self.assertIsNone(server._foreign_design("  "))
        self.assertIsNone(server._foreign_design(str(PROJECT)))
        self.assertIsNone(server._foreign_design("..\\..\\Windows"))     # the tool refuses it
        self.assertIsNone(server._foreign_design("\\\\host\\share\\d"))  # likewise, unresolved
        for name in server._available_projects():
            with self.subTest(name):
                self.assertIsNone(server._foreign_design(name))
                self.assertIsNone(server._foreign_design(str(server.PROJECTS / name)))
        self.env(ACAD_READ_ONLY="1")
        self.assertIsNone(server._read_only_refusal("villa_status", {"project": None}))


# ---------------------------------------------------------------------------
# 4. audit log


class AuditLog(_Safe):
    def test_default_location(self):
        self.assertEqual(_ORIGINAL_AUDIT_PATH, PROJECT / "logs" / "mcp_calls.jsonl")

    def test_line_for_a_successful_call(self):
        import datetime as dt
        server.dxf_info(str(_DXF))
        (rec,) = self.lines()
        self.assertEqual(rec["tool"], "dxf_info")
        self.assertEqual(rec["args"], {"path": str(_DXF)})
        self.assertEqual(rec["outcome"], "ok")
        self.assertNotIn("gate", rec)
        self.assertNotIn("error", rec)
        self.assertIsInstance(rec["ms"], float)
        ts = dt.datetime.fromisoformat(rec["ts"])
        self.assertEqual(ts.utcoffset(), dt.timedelta(0))
        self.assertLess(abs((dt.datetime.now(dt.timezone.utc) - ts).total_seconds()), 60)

    def test_line_for_an_mcp_call(self):
        asyncio.run(server.mcp.call_tool("dxf_info", {"path": str(_DXF)}))
        self.assertEqual(self.lines()[-1]["tool"], "dxf_info")
        asyncio.run(server.mcp.call_tool("acad_draw_line", {"start": [0, 0], "end": [1, 1]}))
        self.assertEqual(len(self.lines()), 2)                 # one line per call, not two
        self.assertEqual(self.lines()[-1]["args"], {"start": [0.0, 0.0], "end": [1.0, 1.0],
                                                    "layer": "", "drawing": ""})
        # The same call made directly logs the same arguments (defaults included).
        server.acad_draw_line(start=[0.0, 0.0], end=[1.0, 1.0])
        self.assertEqual(self.lines()[-1]["args"], self.lines()[-2]["args"])

    def test_calls_the_sdk_rejects_are_logged(self):
        """Invalid arguments or an unknown tool never reach the tool's wrapper;
        the MCP boundary logs them instead."""
        self.env(ACAD_ALLOW_RAW_COMMAND="1")
        bad = [("acad_erase", {}), ("acad_erase", {"handle": "2A", "drawing": 5}),
               ("acad_export_pdf", {"path": "C:\\Windows\\x.pdf", "rotation": 45}),
               ("acad_send_command", {"command": 5}), ("acad_send_command", {"command": ""})]
        for name, args in bad:
            with self.subTest(name=name, args=args), self.assertRaises(ToolError):
                asyncio.run(server.mcp.call_tool(name, args))
        recs = self.lines()
        self.assertEqual(len(recs), len(bad))
        for rec, (name, args) in zip(recs, bad):
            self.assertEqual((rec["tool"], rec["outcome"], rec["gate"], rec["error"]["class"]),
                             (name, "error", "validation", "ValidationError"))
            self.assertEqual(rec["args"], args)
        with self.assertRaises(ToolError):
            asyncio.run(server.mcp.call_tool("acad_no_such_tool", {"x": "y" * 400}))
        rec = self.lines()[-1]
        self.assertEqual((rec["tool"], rec["gate"]), ("acad_no_such_tool", "unknown_tool"))
        self.assertTrue(rec["args"]["x"].endswith("...[truncated 100 chars]"))
        self.assertEqual(self.com_calls, [])

    def test_refused_over_mcp_logged_once(self):
        with self.assertRaises(ToolError):
            asyncio.run(server.mcp.call_tool("acad_send_command", {"command": "_.REGEN"}))
        (rec,) = self.lines()
        self.assertEqual(rec["gate"], "raw_command")

    def test_one_physical_line_per_record(self):
        """U+2028/U+2029/U+0085 are line breaks to str.splitlines(); they are
        escaped, so one record is one line for any reader."""
        odd = "C:\\nope\u2028x\u2029y\u0085z\u00e9.dxf"
        with self.assertRaises(ToolError):
            server.dxf_info(odd)
        text = self.log.read_text(encoding="utf-8")
        self.assertEqual(len(text.splitlines()), 1)
        self.assertTrue(text.isascii())
        self.assertEqual(json.loads(text)["args"]["path"], odd)

    def test_raw_command_logged_whole(self):
        """Padding must not push the real command past the clip."""
        cmd = " " * 300 + "_.ERASE _ALL \n"
        self.env(ACAD_ALLOW_RAW_COMMAND="1")
        server.acad_send_command(command=cmd)
        self.env(ACAD_ALLOW_RAW_COMMAND=None)
        with self.assertRaises(ToolError):
            server.acad_send_command(command=cmd)
        ok, refused = self.lines()
        self.assertEqual(ok["args"]["command"], cmd)
        self.assertEqual(refused["args"]["command"], cmd)
        self.assertEqual(self.com_calls, ["acad_send_command"])

    def test_error_line_and_200_char_message(self):
        missing = str(self.tmp / ("n" * 400 + ".dxf"))
        with self.assertRaises(ToolError):
            server.dxf_info(missing)
        rec = self.lines()[-1]
        self.assertEqual(rec["outcome"], "error")
        self.assertEqual(rec["error"]["class"], "FileNotFoundError")
        self.assertTrue(rec["error"]["message"].startswith("File not found"))
        self.assertEqual(len(rec["error"]["message"]), 200)
        self.assertNotIn("gate", rec)

    def test_gate_recorded(self):
        with self.assertRaises(ToolError):
            server.acad_send_command(command="_.REGEN")
        rec = self.lines()[-1]
        self.assertEqual((rec["outcome"], rec["gate"], rec["error"]["class"]),
                         ("error", "raw_command", "_Refused"))

    def test_truncation(self):
        pts = [[float(i), 0.0] for i in range(80)]
        server.acad_draw_polyline(points=pts, layer="L" * 1000)
        args = self.lines()[-1]["args"]
        self.assertEqual(len(args["points"]), 51)
        self.assertEqual(args["points"][:50], pts[:50])
        self.assertEqual(args["points"][-1], "...[truncated 30 items]")
        self.assertEqual(args["layer"], "L" * 300 + "...[truncated 700 chars]")
        self.assertEqual((args["closed"], args["drawing"]), (False, ""))   # defaults filled in
        self.assertEqual(server._clip({"a": ["x" * 301]}), {"a": ["x" * 300 + "...[truncated 1 chars]"]})
        self.assertEqual(server._clip(list(range(50))), list(range(50)))

    def test_rotation_keeps_one_old_file(self):
        with mock.patch.object(server, "_AUDIT_MAX", 400):
            for _ in range(12):
                server.dxf_info(str(_DXF))
        files = sorted(p.name for p in self.log.parent.iterdir())
        self.assertEqual(files, ["mcp_calls.jsonl", "mcp_calls.jsonl.1"])
        self.assertLess(self.log.stat().st_size, 400 + 600)
        for p in self.log.parent.iterdir():                 # both are whole JSON lines
            for ln in p.read_text(encoding="utf-8").splitlines():
                self.assertEqual(json.loads(ln)["tool"], "dxf_info")

    def test_disabled(self):
        for v in ("0", "false", "FALSE"):
            self.env(ACAD_AUDIT_LOG=v)
            server.dxf_info(str(_DXF))
        self.assertFalse(self.log.exists())
        self.env(ACAD_AUDIT_LOG="1")
        server.dxf_info(str(_DXF))
        self.assertEqual(len(self.lines()), 1)

    def test_logging_failure_is_swallowed(self):
        blocker = self.tmp / "a_file"
        blocker.write_text("x", encoding="utf-8")
        with mock.patch.object(server, "_AUDIT_PATH", blocker / "logs" / "mcp_calls.jsonl"):
            self.assertEqual(server.dxf_info(str(_DXF))["total_entities"], 2)
            with self.assertRaises(ToolError) as cm:            # the tool's error, not the log's
                server.dxf_info(str(self.tmp / "missing.dxf"))
            self.assertIn("File not found", str(cm.exception))

        def boom(v):
            raise RuntimeError("log broken")

        with mock.patch.object(server, "_clip", boom):
            self.assertEqual(server.dxf_info(str(_DXF))["total_entities"], 2)
        self.assertEqual(self.lines(), [])

    def test_nothing_from_the_environment(self):
        self.env(ACAD_WRITE_ROOTS=str(self.tmp / "secret-root-xyz"))
        os.environ["ACAD_SAFETY_TEST_SECRET"] = "s3cr3t-value-xyz"
        try:
            server.dxf_info(str(_DXF))
        finally:
            os.environ.pop("ACAD_SAFETY_TEST_SECRET", None)
        text = self.log.read_text(encoding="utf-8")
        self.assertNotIn("s3cr3t-value-xyz", text)
        self.assertNotIn("secret-root-xyz", text)
        self.assertEqual(set(self.lines()[0]), {"ts", "tool", "args", "outcome", "ms"})

    def test_cheap(self):
        t0 = time.perf_counter()
        for _ in range(300):
            server._audit("dxf_info", {"path": "x" * 400, "pts": list(range(80))},
                          time.perf_counter(), None)
        per_call_ms = (time.perf_counter() - t0) * 1000 / 300
        self.assertLess(per_call_ms, 10.0)
        self.assertEqual(len(self.lines()), 300)


# ---------------------------------------------------------------------------
# 5. the tool listing is unchanged


def _listing(mcp_server) -> dict:
    snap = {t.name: {"title": t.title, "description": t.description,
                     "input_schema": t.input_schema, "output_schema": t.output_schema,
                     "annotations": t.annotations.model_dump(mode="json")
                     if t.annotations else None}
            for t in asyncio.run(mcp_server.list_tools())}
    return json.loads(json.dumps(snap, sort_keys=True))


class ToolListingUnchanged(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

    def test_same_as_before_the_change(self):
        now = _listing(server.mcp)
        self.assertEqual(sorted(now), sorted(self.baseline))
        self.assertEqual(len(now), 48)
        for name in self.baseline:
            with self.subTest(name):
                self.assertEqual(now[name], self.baseline[name])

    def test_baseline_is_the_backup_server(self):
        """The snapshot was generated from the untouched backup; prove it."""
        if not BACKUP.exists():
            self.skipTest(f"{BACKUP.name} is gone")
        spec = importlib.util.spec_from_file_location("server_pre_hardening", BACKUP)
        old = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = old
        try:
            spec.loader.exec_module(old)
            self.assertEqual(_listing(old.mcp), self.baseline)
        finally:
            sys.modules.pop(spec.name, None)

    def test_wrappers_keep_signature_and_doc(self):
        for name in self.baseline:
            fn = getattr(server, name)
            self.assertEqual(fn.__name__, name)
            self.assertEqual(inspect.signature(fn), inspect.signature(fn.__wrapped__))
            self.assertTrue(fn.__doc__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
