"""Offline tests for routing the build123d stages through WSL (server.py).

    python -X utf8 tests\\test_server_wsl.py            (from C:\\Users\\lsire\\autocad-mcp)

Since 2026-10-08 Windows Smart App Control blocks OpenCascade's DLLs, so the
stages whose spec carries "occ" (gltf, elevations) run in WSL through
tools_wsl3d.py. VILLA3D_VIA_WSL=1 forces it, 0 forbids it, unset probes
whether `import OCP` works here. Nothing is launched: only the command lines
villa_run would use are checked, and tools_wsl3d's path translation.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT))
os.environ.setdefault("ACAD_AUDIT_LOG", "0")
import server  # noqa: E402
import tools_wsl3d  # noqa: E402


class StageRouting(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.get("VILLA3D_VIA_WSL")
        server._occ_blocked.cache_clear()

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("VILLA3D_VIA_WSL", None)
        else:
            os.environ["VILLA3D_VIA_WSL"] = self._saved
        server._occ_blocked.cache_clear()

    def test_occ_stages_are_the_build123d_ones(self):
        occ = {s for s, spec in server._STAGES.items() if spec.get("occ")}
        self.assertEqual(occ, {"gltf", "elevations"})

    def test_forced_wsl_routes_the_villa(self):
        os.environ["VILLA3D_VIA_WSL"] = "1"
        for stage, script in (("gltf", "villa_gltf.py"), ("elevations", "villa_elevations.py")):
            (argv,) = server._stage_commands(stage, [])
            self.assertEqual(argv[0], server.PYTHON)
            self.assertEqual(Path(argv[1]), PROJECT / "tools_wsl3d.py")
            self.assertEqual(argv[2:], [str(PROJECT / script)])

    def test_forced_wsl_routes_a_project_through_run_project(self):
        os.environ["VILLA3D_VIA_WSL"] = "1"
        ctx = server._project("fairway")
        (argv,) = server._stage_commands("gltf", [], ctx)
        self.assertEqual(Path(argv[1]), PROJECT / "tools_wsl3d.py")
        self.assertEqual(argv[2:], [str(PROJECT / "run_project.py"), str(ctx.folder),
                                    "villa_gltf.py"])

    def test_forbidden_wsl_keeps_the_native_command(self):
        os.environ["VILLA3D_VIA_WSL"] = "0"
        (argv,) = server._stage_commands("gltf", [])
        self.assertEqual(argv, [server.PYTHON, "-X", "utf8", str(PROJECT / "villa_gltf.py")])

    def test_other_stages_never_route(self):
        os.environ["VILLA3D_VIA_WSL"] = "1"
        for stage in ("plans", "colour", "build3d", "verify3d", "load", "verify"):
            for argv in server._stage_commands(stage, []):
                self.assertNotIn("tools_wsl3d.py", " ".join(argv), stage)
        (render,) = server._stage_commands("render", [])
        self.assertEqual(render[0], str(server.BLENDER))

    def test_auto_follows_the_probe(self):
        os.environ.pop("VILLA3D_VIA_WSL", None)
        with mock.patch.object(server, "_occ_blocked", return_value=True):
            self.assertTrue(server._occ_via_wsl())
        with mock.patch.object(server, "_occ_blocked", return_value=False):
            self.assertFalse(server._occ_via_wsl())

    def test_probe_failing_to_start_counts_as_blocked(self):
        with mock.patch.object(server, "_sac_enforcing", return_value=False), \
                mock.patch.object(server.subprocess, "run", side_effect=OSError("no python")):
            self.assertTrue(server._occ_blocked())

    def test_smart_app_control_enforcing_means_blocked_without_probing(self):
        with mock.patch.object(server, "_sac_enforcing", return_value=True), \
                mock.patch.object(server.subprocess, "run") as run:
            self.assertTrue(server._occ_blocked())
            run.assert_not_called()

    def test_probe_imports_build123d_not_just_ocp(self):
        seen = []

        def fake_run(argv, **kw):
            seen.append(argv)
            return mock.Mock(returncode=0)

        with mock.patch.object(server, "_sac_enforcing", return_value=False), \
                mock.patch.object(server.subprocess, "run", side_effect=fake_run):
            self.assertFalse(server._occ_blocked())
        self.assertIn("build123d", seen[0][-1])


class PathTranslation(unittest.TestCase):
    def test_drive_paths(self):
        self.assertEqual(tools_wsl3d.to_wsl(r"C:\Users\lsire\autocad-mcp\villa_gltf.py"),
                         "/mnt/c/Users/lsire/autocad-mcp/villa_gltf.py")
        self.assertEqual(tools_wsl3d.to_wsl("D:/data/x.dxf"), "/mnt/d/data/x.dxf")

    def test_relative_and_plain_arguments(self):
        self.assertEqual(tools_wsl3d.to_wsl(r"tests\regress_villa.py"), "tests/regress_villa.py")
        self.assertEqual(tools_wsl3d.to_wsl("gltf"), "gltf")

    def test_unc_refused(self):
        with self.assertRaises(SystemExit):
            tools_wsl3d.to_wsl(r"\\server\share\x.dxf")

    def test_default_out_matches_windows(self):
        self.assertEqual(tools_wsl3d.default_out(["villa_gltf.py"]),
                         os.path.join(tools_wsl3d.DESKTOP, "Villa"))
        self.assertEqual(tools_wsl3d.default_out(["run_project.py", "fairway", "villa_gltf.py"]),
                         os.path.join(tools_wsl3d.DESKTOP, "Fairway"))


if __name__ == "__main__":
    unittest.main()
