"""Offline tests for server.py -- no AutoCAD and no acad_* tool is ever called.

    python tests\\test_server_offline.py            (from C:\\Users\\lsire\\autocad-mcp)
    python -m unittest tests.test_server_offline -v

What is covered:
  * registration: the original 41 tool names still exist, the new ones are added,
    schemas are typed (points, enums, ranges), annotations mark destructive and
    read-only tools, and acad_purge_and_audit is a dry run by default;
  * villa_validate / villa_status / dxf_info, each checked against an
    INDEPENDENT recomputation, not just for shape;
  * the SDK-2.x error path: a failing tool's message reaches the client;
  * the COM retry / lock / timeout machinery, driven by pure-Python fakes
    (pywintypes.com_error objects are constructed, no COM server is contacted);
  * a real stdio MCP handshake against `python server.py`: initialize,
    notifications/initialized, tools/list, and one offline tools/call.
"""

from __future__ import annotations

import asyncio
import json
import os
import queue
import subprocess
import sys
import threading
import time
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SERVER = PROJECT / "server.py"
A102 = Path(r"C:\Users\lsire\OneDrive\Desktop\Villa\VILLA_A102.dxf")

sys.path.insert(0, str(PROJECT))
# Test calls stay out of the real audit log (logs\mcp_calls.jsonl); the switch
# is read per call and inherited by the stdio server started below.
os.environ.setdefault("ACAD_AUDIT_LOG", "0")
import server  # noqa: E402

from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

# The 41 tools of the server before the upgrade (read from the old server.py).
ORIGINAL_TOOLS = {
    "acad_status", "acad_draw_line", "acad_draw_circle", "acad_draw_polyline",
    "acad_draw_text", "acad_list_layers", "acad_create_layer", "acad_set_layer",
    "acad_summarize_entities", "acad_send_command", "acad_zoom_extents", "acad_save",
    "acad_list_drawings", "acad_new_drawing", "acad_open_drawing",
    "acad_activate_drawing", "acad_erase", "acad_export_pdf", "acad_draw_arc",
    "acad_draw_rectangle", "acad_draw_ellipse", "acad_add_linear_dimension",
    "acad_add_aligned_dimension", "acad_add_hatch", "acad_list_blocks",
    "acad_insert_block", "acad_move", "acad_copy_entity", "acad_rotate", "acad_scale",
    "acad_mirror", "acad_offset", "acad_measure_entity", "acad_3d_box",
    "acad_3d_cylinder", "acad_3d_sphere", "acad_3d_boolean", "acad_purge_and_audit",
    "dxf_info", "dxf_list_entities", "dxf_extract_text",
}
NEW_TOOLS = {"acad_wait_idle", "acad_list_orphans", "acad_close_orphans",
             "acad_screenshot", "villa_validate", "villa_status", "villa_run"}

# Every tool that reads or changes ONE drawing must accept `drawing`.
DRAWING_TOOLS = {
    "acad_status", "acad_draw_line", "acad_draw_circle", "acad_draw_polyline",
    "acad_draw_text", "acad_list_layers", "acad_create_layer", "acad_set_layer",
    "acad_summarize_entities", "acad_send_command", "acad_zoom_extents", "acad_save",
    "acad_erase", "acad_export_pdf", "acad_draw_arc", "acad_draw_rectangle",
    "acad_draw_ellipse", "acad_add_linear_dimension", "acad_add_aligned_dimension",
    "acad_add_hatch", "acad_list_blocks", "acad_insert_block", "acad_move",
    "acad_copy_entity", "acad_rotate", "acad_scale", "acad_mirror", "acad_offset",
    "acad_measure_entity", "acad_3d_box", "acad_3d_cylinder", "acad_3d_sphere",
    "acad_3d_boolean", "acad_purge_and_audit", "acad_screenshot",
}
DESTRUCTIVE = {"acad_erase", "acad_purge_and_audit", "acad_send_command",
               "acad_close_orphans", "acad_save", "acad_move", "acad_rotate",
               "acad_scale", "acad_mirror", "acad_3d_boolean", "villa_run"}
READ_ONLY = {"acad_status", "acad_wait_idle", "acad_list_drawings", "acad_list_orphans",
             "acad_list_layers", "acad_summarize_entities", "acad_list_blocks",
             "acad_measure_entity", "villa_validate", "villa_status", "dxf_info",
             "dxf_list_entities", "dxf_extract_text"}

BUSY = -2147418111          # RPC_E_CALL_REJECTED
STALE = -2147417848         # RPC_E_DISCONNECTED
UNKNOWN_NAME = -2147352570  # DISP_E_UNKNOWNNAME


def _tools() -> dict:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


def _com_error(hr: int, text: str = "x"):
    import pywintypes
    return pywintypes.com_error(hr, text, None, None)


# ---------------------------------------------------------------------------


class Registration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = _tools()

    def test_original_tool_names_kept(self):
        self.assertEqual(len(ORIGINAL_TOOLS), 41)
        self.assertFalse(ORIGINAL_TOOLS - set(self.tools),
                         f"missing: {ORIGINAL_TOOLS - set(self.tools)}")

    def test_new_tools_added(self):
        self.assertFalse(NEW_TOOLS - set(self.tools))
        self.assertEqual(set(self.tools), ORIGINAL_TOOLS | NEW_TOOLS)

    def test_descriptions_and_annotations_everywhere(self):
        for name, t in self.tools.items():
            self.assertTrue(t.description and len(t.description) > 30, name)
            self.assertIsNotNone(t.annotations, name)
            self.assertEqual(t.input_schema.get("type"), "object", name)

    def test_drawing_parameter(self):
        for name in DRAWING_TOOLS:
            props = self.tools[name].input_schema["properties"]
            self.assertIn("drawing", props, name)
            self.assertNotIn("drawing", self.tools[name].input_schema.get("required", []), name)
            self.assertEqual(props["drawing"]["type"], "string", name)

    def test_points_are_typed_and_units_stated(self):
        start = self.tools["acad_draw_line"].input_schema["properties"]["start"]
        self.assertEqual((start["minItems"], start["maxItems"]), (2, 3))
        self.assertIn("millimetres", start["description"])
        fp = self.tools["acad_insert_block"].input_schema["properties"]["footprint"]
        arr = next(x for x in fp["anyOf"] if x.get("type") == "array")
        self.assertEqual((arr["minItems"], arr["maxItems"]), (4, 4))

    def test_enums(self):
        op = self.tools["acad_3d_boolean"].input_schema["properties"]["operation"]
        self.assertEqual(set(op["enum"]), {"union", "subtract", "intersect"})
        stage = self.tools["villa_run"].input_schema["properties"]["stage"]
        self.assertEqual(stage["enum"], ["plans", "colour", "elevations", "gltf", "build3d",
                                         "verify3d", "load", "verify", "render"])
        pt = self.tools["acad_export_pdf"].input_schema["properties"]["plot_type"]
        self.assertEqual(set(pt["enum"]), {"extents", "layout", "display"})

    def test_annotations(self):
        for name in DESTRUCTIVE:
            a = self.tools[name].annotations
            self.assertTrue(a.destructive_hint, name)
            self.assertFalse(a.read_only_hint, name)
        for name in READ_ONLY:
            a = self.tools[name].annotations
            self.assertTrue(a.read_only_hint, name)
            self.assertFalse(a.destructive_hint, name)
        self.assertTrue(self.tools["acad_send_command"].annotations.open_world_hint)

    def test_purge_is_dry_run_by_default(self):
        props = self.tools["acad_purge_and_audit"].input_schema["properties"]
        self.assertIs(props["dry_run"]["default"], True)

    def test_send_command_documented_as_escape_hatch(self):
        d = self.tools["acad_send_command"].description
        self.assertIn("ESCAPE HATCH", d)
        self.assertIn("idle", d)

    def test_argument_validation_without_calling(self):
        """Pydantic arg models reject bad input before any tool body could run."""
        from pydantic import ValidationError
        tm = server.mcp._tool_manager
        line = tm.get_tool("acad_draw_line").fn_metadata.arg_model
        with self.assertRaises(ValidationError):
            line.model_validate({"start": [1.0], "end": [2.0, 3.0]})
        with self.assertRaises(ValidationError):
            line.model_validate({"start": [0, 0, 0, 0], "end": [2.0, 3.0]})
        line.model_validate({"start": [0, 0], "end": [1000, 0, 0]})
        erase = tm.get_tool("acad_erase").fn_metadata.arg_model
        with self.assertRaises(ValidationError):
            erase.model_validate({"handle": "not-hex!"})
        layer = tm.get_tool("acad_create_layer").fn_metadata.arg_model
        with self.assertRaises(ValidationError):
            layer.model_validate({"name": "A-WALL", "color": 300})
        pdf = tm.get_tool("acad_export_pdf").fn_metadata.arg_model
        with self.assertRaises(ValidationError):
            pdf.model_validate({"path": "x.pdf", "scale": "100"})
        pdf.model_validate({"path": "x.pdf", "scale": "1:100"})

    def test_send_command_denylist(self):
        self.assertIsNotNone(server._denied("SHELL\n"))
        self.assertIsNotNone(server._denied("_.NETLOAD foo.dll"))
        self.assertIsNotNone(server._denied('(startapp "calc.exe")'))
        self.assertIsNotNone(server._denied("-VBARUN x"))
        self.assertIsNone(server._denied("_.ZOOM\n_E"))
        self.assertIsNone(server._denied("(vl-load-com)"))


# ---------------------------------------------------------------------------

_INDEPENDENT = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import villa_design as V, villa_furniture_spec as F
iss = V.validate(); pr = V.probes(); fu = F.check()
print(json.dumps({"fatal": sum(i.startswith("[FATAL]") for i in iss),
                  "major": sum(i.startswith("[MAJOR]") for i in iss),
                  "probes": len(pr), "solid": sum(p[4] == "solid" for p in pr),
                  "furniture": len(fu)}))
"""


class VillaValidate(unittest.TestCase):
    def _independent(self) -> dict:
        out = subprocess.run([sys.executable, "-c", _INDEPENDENT, str(PROJECT)],
                             capture_output=True, text=True, timeout=120, cwd=str(PROJECT))
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_matches_an_independent_run(self):
        # The design file is being edited while this runs: allow one retry if a
        # save lands between the two measurements.
        for attempt in range(2):
            got = server.villa_validate()
            ref = self._independent()
            mine = {"fatal": len(got["design"]["fatal"]), "major": len(got["design"]["major"]),
                    "probes": got["probes"]["count"], "solid": got["probes"]["solid"],
                    "furniture": len(got["furniture"]["issues"])}
            if mine == ref or attempt == 1:
                break
        self.assertEqual(mine, ref)
        self.assertEqual(got["ok"], mine["fatal"] == 0 and mine["major"] == 0
                         and mine["furniture"] == 0)
        self.assertGreater(got["probes"]["count"], 0)
        self.assertIn("villa_design.py", got["sources"])

    def test_probe_list_optional(self):
        got = server.villa_validate(include_probes=True)
        self.assertEqual(len(got["probes"]["list"]), got["probes"]["count"])
        self.assertEqual({p["expect"] for p in got["probes"]["list"]} - {"solid", "void"}, set())

    def test_over_mcp_call_tool(self):
        res = asyncio.run(server.mcp.call_tool("villa_validate", {}))
        self.assertFalse(res.is_error)
        self.assertIn("summary", res.structured_content)


class VillaStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = server.villa_status()

    def test_all_stages_present_with_valid_states(self):
        ok = {"fresh", "stale", "missing", "stale (upstream)", "verified", "failed",
              "unverified"}
        self.assertEqual(list(self.s["stages"]), ["plans", "colour", "elevations", "gltf",
                                                  "build3d", "verify3d", "load", "verify",
                                                  "render"])
        for name, r in self.s["stages"].items():
            self.assertIn(r["state"], ok, name)

    def test_dependency_scan_finds_imports(self):
        src = set(self.s["stages"]["plans"]["sources"])
        for need in ("villa_cad.py", "villa_design.py", "villa_furniture_spec.py",
                     "plan_dxf.py", "block_catalog.json"):
            self.assertIn(need, src)
        self.assertIn("villa_design.py", self.s["stages"]["render"]["sources"])

    def test_staleness_matches_file_times(self):
        """Recompute 'plans' output staleness straight from os.path.getmtime."""
        r = self.s["stages"]["plans"]
        newest = max(os.path.getmtime(PROJECT / p) for p in r["sources"])
        villa = Path(self.s["villa_dir"])
        for o in r["outputs"]:
            f = villa / o["path"]
            if not f.exists():
                self.assertEqual(o["status"], "missing")
                continue
            expect = "stale" if os.path.getmtime(f) + server._TOL < newest else "fresh"
            self.assertEqual(o["status"], expect, o["path"])
        self.assertEqual(r["state"] == "fresh",
                         all(o["status"] == "fresh" for o in r["outputs"]))

    def test_rerun_list_is_in_pipeline_order(self):
        order = list(self.s["stages"])
        todo = self.s["rerun_in_order"]
        self.assertEqual(todo, sorted(todo, key=order.index))
        for st in todo:
            self.assertNotIn(self.s["stages"][st]["state"], ("fresh", "verified"))


class DxfInfo(unittest.TestCase):
    def test_villa_a102(self):
        import ezdxf
        from ezdxf import bbox
        info = server.dxf_info(str(A102))
        doc = ezdxf.readfile(str(A102))
        msp = doc.modelspace()
        self.assertEqual(info["total_entities"], len(msp))
        self.assertEqual(info["units_code"], 4)
        self.assertEqual(info["layers"], [lyr.dxf.name for lyr in doc.layers])
        ext = bbox.extents(msp, fast=True)
        self.assertEqual(info["extents"]["min"], [round(v, 3) for v in ext.extmin])
        self.assertLess(abs(info["extents"]["max"][0]), 1e7)   # not the 1e20 sentinel
        self.assertGreater(info["extents"]["size"][0], 1000)   # a villa, in mm

    def test_error_text_reaches_client(self):
        """SDK 2.x hides non-ToolError text; the server must translate."""
        missing = str(PROJECT / "no_such_file.dxf")
        with self.assertRaises(ToolError) as cm:
            asyncio.run(server.mcp.call_tool("dxf_info", {"path": missing}))
        self.assertIn("File not found", str(cm.exception))
        self.assertIn("no_such_file.dxf", str(cm.exception))


class VerdictMarkers(unittest.TestCase):
    """villa_run reads the scripts' output for its verdict. Blender's GPU-
    driver warning 'HIPEW initialization failed' turned a perfect render into
    'failed' on the first live run (2026-09-26)."""

    def flagged(self, line):
        return any(p.search(line) for p in server._FAIL_MARKS)

    def test_driver_warning_is_not_a_failure(self):
        self.assertFalse(self.flagged(
            "00:01.938  cycles | WARNING HIPEW initialization failed: "
            "Error opening HIP dynamic library"))

    def test_real_failures_still_caught(self):
        for line in ("A-102   389 entities, 55 blocks inserted, 2 FAILED",
                     "Traceback (most recent call last):",
                     "  gave up: AutoCAD stayed busy",
                     "3 FAILURE(S):",
                     "import does not match the model:"):
            self.assertTrue(self.flagged(line), line)


class VillaRunDryRun(unittest.TestCase):
    def test_python_stages_use_this_interpreter(self):
        r = server.villa_run(stage="verify3d", dry_run=True)
        self.assertTrue(r["dry_run"])
        self.assertTrue(r["com_stage"])
        self.assertEqual(len(r["commands"]), 3)
        for cmd, script in zip(r["commands"], ("villa_3d_verify.py", "villa_pool_check.py",
                                               "villa_window_check.py")):
            self.assertIn(script, cmd)
            self.assertIn("python", cmd.lower())
        plans = server.villa_run(stage="plans", dry_run=True)
        self.assertFalse(plans["com_stage"])
        argv = server._stage_commands("plans", [])[0]
        self.assertEqual(argv[0], sys.executable)

    def test_render_uses_blender_and_fails_on_exceptions(self):
        r = server.villa_run(stage="render", render_args=["--samples", "32", "--no-render"],
                             dry_run=True)
        self.assertIn("blender.exe", r["commands"][0].lower())
        self.assertIn("--python-exit-code", r["commands"][0])
        self.assertTrue(r["commands"][0].rstrip().endswith("--samples 32 --no-render"))

    def test_render_args_are_whitelisted(self):
        with self.assertRaises(ToolError):
            server.villa_run(stage="render", render_args=["--python", "evil.py"], dry_run=True)
        with self.assertRaises(ToolError):
            server.villa_run(stage="render", render_args=["--samples", "many"], dry_run=True)
        with self.assertRaises(ToolError):
            server.villa_run(stage="plans", render_args=["--no-render"], dry_run=True)

    def test_verdict_markers(self):
        self.assertTrue(any(p.search("gave up: AutoCAD stayed busy") for p in server._FAIL_MARKS))
        self.assertTrue(any(p.search("\n2 FAILURE(S):") for p in server._FAIL_MARKS))
        self.assertTrue(server._VERIFIED_MARK.search("\nVERIFIED: every opening is a real hole"))
        self.assertTrue(any(p.search("   probe failed: x") for p in server._UNVERIFIED_MARKS))
        self.assertFalse(any(p.search("VERIFIED: every block matches") for p in server._FAIL_MARKS))


# ---------------------------------------------------------------------------
# COM machinery, with fakes (no COM server is contacted)


class FakeOle:
    """Stands in for PyIDispatch: GetIDsOfNames says which names exist."""

    def __init__(self, names, busy_probe=False):
        self.names, self.busy_probe = set(names), busy_probe

    def GetIDsOfNames(self, _lcid, name):
        if self.busy_probe:
            raise _com_error(BUSY)
        if name not in self.names:
            raise _com_error(UNKNOWN_NAME, "Unknown name.")
        return 1


class FakeEnt:
    def __init__(self):
        self._oleobj_ = FakeOle({"Handle", "Layer", "Delete"})
        self.Handle = "2A"
        self.Layer = "0"


class FakeDoc:
    def __init__(self, reject_add=0, refuse_count=0):
        self._oleobj_ = FakeOle({"Name", "Count", "AddLine", "Item"})
        self.Name = "VILLA_A102.dwg"
        self.reject_add, self.refuse_count = reject_add, refuse_count
        self.adds = 0

    def __getattr__(self, name):          # only reached for names not set above
        if name == "Count":
            if self.refuse_count:
                self.refuse_count -= 1
                raise AttributeError("<unknown>.Count")
            return 3
        raise AttributeError(f"<unknown>.{name}")

    def AddLine(self, a, b):
        if self.reject_add:
            self.reject_add -= 1
            raise _com_error(BUSY, "Call was rejected by callee.")
        self.adds += 1
        return FakeEnt()

    def Item(self, i):
        return FakeEnt()


class ComLogic(unittest.TestCase):
    def setUp(self):
        server._TLS.deadline = time.monotonic() + 5
        server._TLS.mutated = False

    def tearDown(self):
        server._TLS.deadline = None

    def test_classify(self):
        self.assertEqual(server._classify(_com_error(BUSY)), "busy")
        self.assertEqual(server._classify(_com_error(STALE)), "stale")
        self.assertEqual(server._classify(AttributeError("<unknown>.Count")), "refused")
        self.assertEqual(server._classify(AttributeError("AutoCAD.Application.Documents")),
                         "refused")
        self.assertEqual(server._classify(AttributeError("Property '<unknown>.Color' can not be set.")),
                         "refused")
        raw = types.SimpleNamespace(_oleobj_=FakeOle({"Length"}))
        self.assertEqual(server._classify(AttributeError("<unknown>.Radius"), raw, "Radius"),
                         "missing")
        raw_busy = types.SimpleNamespace(_oleobj_=FakeOle({"Length"}, busy_probe=True))
        self.assertEqual(server._classify(AttributeError("<unknown>.Radius"), raw_busy, "Radius"),
                         "busy")
        self.assertEqual(server._classify(ValueError("nope")), "other")

    def test_busy_call_is_retried(self):
        doc = server._Com(FakeDoc(reject_add=2))
        ent = doc.AddLine("a", "b")
        self.assertEqual(ent.Handle, "2A")
        self.assertEqual(doc._o.adds, 1)                 # executed exactly once
        self.assertTrue(server._TLS.mutated)             # a successful Add* is a side effect

    def test_reads_do_not_count_as_side_effects(self):
        doc = server._Com(FakeDoc())
        doc.Item(0)
        self.assertFalse(server._TLS.mutated)

    def test_refused_lookup_retried(self):
        doc = server._Com(FakeDoc(refuse_count=2))
        self.assertEqual(doc.Count, 3)

    def test_missing_member_fails_fast(self):
        doc = server._Com(FakeDoc())
        t0 = time.monotonic()
        with self.assertRaises(AttributeError) as cm:
            doc.Radius
        self.assertLess(time.monotonic() - t0, 0.5)
        self.assertIn("no member", str(cm.exception))

    def test_children_are_wrapped(self):
        doc = server._Com(FakeDoc())
        self.assertIsInstance(doc.Item(0), server._Com)

    def test_job_retried_only_before_side_effects(self):
        attempts = {"n": 0}

        def flaky_read(app):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise _com_error(BUSY)
            return "done"

        fake = FakeDoc()
        out = server._run_job(flaky_read, time.monotonic() + 10, False, "t",
                              lambda: server._Com(fake), 0.0, 10)
        self.assertEqual((out, attempts["n"]), ("done", 3))

        def change_then_fail(app):
            app.AddLine("a", "b")
            raise _com_error(STALE)

        fake2 = FakeDoc()
        with self.assertRaises(server._BusyError) as cm:
            server._run_job(change_then_fail, time.monotonic() + 3, False, "t",
                            lambda: server._Com(fake2), 0.0, 3)
        self.assertEqual(fake2.adds, 1)                  # never repeated
        self.assertIn("NOT repeated", str(cm.exception))

    def test_lock_serialises_callers(self):
        started = threading.Event()

        def holder():
            with server._holding_com_lock("villa_run(build3d)", 1):
                started.set()
                time.sleep(1.2)

        th = threading.Thread(target=holder)
        th.start()
        started.wait(2)
        with self.assertRaises(server._BusyError) as cm:
            server._run_job(lambda app: 1, time.monotonic() + 0.4, True, "acad_status",
                            lambda: object(), 0.0, 0.4)
        self.assertIn("villa_run(build3d)", str(cm.exception))
        th.join()
        self.assertEqual(server._run_job(lambda app: 7, time.monotonic() + 2, True, "t",
                                         lambda: object(), 0.0, 2), 7)

    def test_hung_call_times_out_and_executor_is_replaced(self):
        old_grace = server._GRACE
        server._GRACE = 0.3
        try:
            before = server._executor()
            t0 = time.monotonic()
            with self.assertRaises(ToolError) as cm:
                server._com(lambda app: time.sleep(2.0), what="hang", timeout=0.5,
                            idempotent=True, attach=lambda: object())
            self.assertLess(time.monotonic() - t0, 1.5)
            self.assertIn("did not answer", str(cm.exception))
            self.assertIsNot(server._executor(), before)
            # the hung call still holds the lock, so the next caller is refused...
            with self.assertRaises(server._BusyError):
                server._com(lambda app: 1, what="next", timeout=0.3, attach=lambda: object())
            time.sleep(2.0)
            # ...until it returns; then calls flow again
            self.assertEqual(server._com(lambda app: 42, what="after", timeout=5,
                                         attach=lambda: object()), 42)
        finally:
            server._GRACE = old_grace


# ---------------------------------------------------------------------------


class StdioHandshake(unittest.TestCase):
    """Spawn `python server.py` and speak raw JSON-RPC over its stdio."""

    def test_initialize_list_and_call(self):
        proc = subprocess.Popen([sys.executable, str(SERVER)], cwd=str(PROJECT),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        lines: queue.Queue = queue.Queue()
        raw_lines: list[bytes] = []
        err_lines: list[bytes] = []

        def reader():
            for line in proc.stdout:
                raw_lines.append(line)
                lines.put(line)

        def drain_stderr():               # a full stderr pipe would stall the server
            for line in proc.stderr:
                err_lines.append(line)

        threading.Thread(target=reader, daemon=True).start()
        threading.Thread(target=drain_stderr, daemon=True).start()

        def send(msg):
            proc.stdin.write((json.dumps(msg) + "\n").encode())
            proc.stdin.flush()

        def recv(want_id, timeout=60):
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                try:
                    msg = json.loads(lines.get(timeout=max(0.1, end - time.monotonic())))
                except queue.Empty:
                    break
                if msg.get("id") == want_id:
                    return msg
            self.fail(f"no response to id {want_id}; exit={proc.poll()}; stderr tail: "
                      f"{b''.join(err_lines[-20:]).decode('utf-8', 'replace')}")

        try:
            send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                             "clientInfo": {"name": "offline-test", "version": "1"}}})
            init = recv(1)
            self.assertNotIn("error", init, init)
            self.assertEqual(init["result"]["serverInfo"]["name"], "autocad")
            self.assertIn("tools", init["result"]["capabilities"])
            self.assertIn("villa_validate", init["result"].get("instructions", ""))
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})

            send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            listed = recv(2)["result"]
            names = {t["name"] for t in listed["tools"]}
            self.assertEqual(names, ORIGINAL_TOOLS | NEW_TOOLS)
            self.assertIsNone(listed.get("nextCursor"))
            wire = {t["name"]: t for t in listed["tools"]}
            self.assertTrue(wire["acad_erase"]["annotations"]["destructiveHint"])
            self.assertTrue(wire["villa_status"]["annotations"]["readOnlyHint"])

            send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                  "params": {"name": "dxf_info", "arguments": {"path": str(A102)}}})
            call = recv(3)["result"]
            self.assertFalse(call.get("isError"), call)
            self.assertEqual(call["structuredContent"]["units_code"], 4)

            # every line the server wrote to stdout is a JSON-RPC message
            for ln in raw_lines:
                json.loads(ln)
        finally:
            proc.stdin.close()               # EOF: the server must exit by itself
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=15)
            proc.stdout.close()
            proc.stderr.close()
        self.assertIsNotNone(proc.returncode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
