"""
AutoCAD MCP server (MCP Python SDK 2.x).

Three tool groups:
  * acad_*  -- live control of a RUNNING AutoCAD through COM (Windows only).
               Works with AutoCAD, AutoCAD Architecture, Civil 3D, Mechanical.
  * villa_* -- the villa pipeline: validate the design in-process, report which
               outputs are stale, and run pipeline stages as subprocesses --
               for the villa, or (project=...) any design in projects\\<name>.
  * dxf_*   -- offline inspection of DXF files via ezdxf. Needs no AutoCAD.

COM discipline -- why the plumbing below looks the way it does:
  * AutoCAD is a single-threaded-apartment (STA) server. Every COM call this
    process makes runs on ONE dedicated worker thread under ONE lock, so two
    tool calls can never interleave inside AutoCAD. villa_run holds the same
    lock while a COM pipeline stage (a separate process) drives AutoCAD.
  * A busy AutoCAD rejects calls (RPC_E_CALL_REJECTED), and pywin32 reports a
    refused late-bound name lookup as AttributeError('<unknown>.X'). Each
    individual call is retried with backoff until the tool's deadline. A whole
    job is re-run only if nothing it did had side effects yet, so a retry can
    never draw an entity twice.
  * Every object read back is re-wrapped LATE-bound (_late). pywin32's early-
    binding cache is case-sensitive and narrow: IAcadLayer has `color`, not
    `Color`, and IAcadEntity has no Length/Area/TextString.
  * Drawings are addressed BY NAME. ActiveDocument is used only when the caller
    names no drawing, and never after Open/SaveAs.
  * In SDK 2.x only ToolError text reaches the client. Any other exception is
    reported as a bare 'Error executing tool X'. So every tool converts its
    failures into a ToolError with an actionable message.

Safety switches -- this server's environment (the `env` of its MCP
registration), read on every call so a restart of Claude Code applies them:
  * ACAD_ALLOW_RAW_COMMAND=1  enables the acad_send_command tool (off by default).
  * ACAD_READ_ONLY=1          refuses every tool that changes a drawing, AutoCAD
                              or files; readOnlyHint tools, dry runs and an
                              acad_screenshot into %TEMP% (no drawing=) still work,
                              but project= only for the villa or projects\\ (reading
                              a design runs its villa_design.py).
  * ACAD_WRITE_ROOTS          os.pathsep-separated folders that acad_save (SaveAs),
                              acad_export_pdf and acad_screenshot may write under.
                              Default: Desktop (OneDrive and local), this folder
                              and %TEMP%. Saving a drawing in place is not limited.
  * ACAD_AUDIT_LOG=0          stops the audit line every tool call appends to
                              logs\\mcp_calls.jsonl (rotated at 5 MB to .1); calls
                              the SDK rejects (unknown tool, invalid arguments) too.

Note on DWG: ezdxf reads DXF, not DWG. To analyse a .dwg offline, convert it
first (ODA File Converter), or open it in AutoCAD and use the acad_* tools.
"""

from __future__ import annotations

import ast
import contextlib
import dataclasses
import datetime as _dt
import functools
import importlib
import inspect
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import types
from concurrent.futures import CancelledError, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationError

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

# --------------------------------------------------------------------------
# Locations
# --------------------------------------------------------------------------

PROJECT = Path(__file__).resolve().parent     # the pipeline folder (this server's)
PROJECTS = PROJECT / "projects"                  # one folder per further design
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"   # as run_project.py
# Deliverables folder of the VILLA (the default design). VILLA_OUT -- the
# variable every pipeline script reads (villa_geom.out_dir) -- wins; VILLA_DIR,
# this server's older name for the same folder, is still honoured; unset, it is
# Desktop\Villa, the scripts' own default. villa_run hands the folder to every
# stage as VILLA_OUT, so the server and the scripts cannot look in different
# places. A project's folder is VILLA_OUT or Desktop\<OUT_NAME> (_project()).
VILLA = Path(os.environ.get("VILLA_OUT") or os.environ.get("VILLA_DIR")
             or DESKTOP / "Villa")
RENDER = VILLA / "render"
BLENDER = Path(os.environ.get(
    "BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"))
PYTHON = sys.executable            # pipeline stages run on the SAME interpreter
STATE_DIR = Path(tempfile.gettempdir()) / "autocad-mcp"   # run logs + run records

_INSTRUCTIONS = """\
AutoCAD + villa pipeline tools.

Units: coordinates and sizes are drawing units. The villa drawings are
millimetres (INSUNITS=4); at 1:100 model-space text is 250 mm high.

Villa work: the design is DATA in villa_design.py; every drawing and model is
generated from it. Prefer villa_validate (design + probes + furniture checks),
villa_status (which outputs are stale) and villa_run(stage) over hand-editing
drawings through acad_* primitives. The three take project=<name under
projects\\ (e.g. 'fairway') or an absolute folder holding villa_design.py> to
work on another design; omit it for the villa. Every result names its design.

AutoCAD (acad_*): calls are serialised through one COM lock and retried while
AutoCAD is busy. Do not drive the same AutoCAD from another MCP server or
script at the same time. Pass drawing=<name from acad_list_drawings> whenever
more than one drawing is open; every result names the drawing it acted on.
Entity handles are unique only within one drawing, so handle-based tools refuse
to guess when several drawings are open. acad_send_command is an escape hatch,
off unless ACAD_ALLOW_RAW_COMMAND=1. ACAD_READ_ONLY=1 refuses changing tools.
SaveAs/PDF/PNG paths must lie under ACAD_WRITE_ROOTS (default: Desktop, %TEMP%,
the server folder).

Offline (dxf_*): read DXF files with ezdxf, no AutoCAD needed.
"""

mcp = MCPServer("autocad", instructions=_INSTRUCTIONS)

# --------------------------------------------------------------------------
# Errors: only ToolError text reaches the client in SDK 2.x
# --------------------------------------------------------------------------

RPC_E_CALL_REJECTED = -2147418111          # 0x80010001  AutoCAD busy
RPC_E_SERVERCALL_RETRYLATER = -2147417846  # 0x8001010A  AutoCAD busy
RPC_E_DISCONNECTED = -2147417848           # 0x80010108  stale proxy
RPC_S_SERVER_UNAVAILABLE = -2147023174     # 0x800706BA
RPC_S_CALL_FAILED = -2147023170            # 0x800706BE
CO_E_OBJNOTCONNECTED = -2147220995         # 0x800401FD
DISP_E_UNKNOWNNAME = -2147352570           # 0x80020006  no such member
DISP_E_MEMBERNOTFOUND = -2147352573        # 0x80020003
MK_E_UNAVAILABLE = -2147221021             # 0x800401E3  not in the ROT

_BUSY_HR = {RPC_E_CALL_REJECTED, RPC_E_SERVERCALL_RETRYLATER}
_STALE_HR = {RPC_E_DISCONNECTED, RPC_S_SERVER_UNAVAILABLE, RPC_S_CALL_FAILED,
             CO_E_OBJNOTCONNECTED}
_MISSING_HR = {DISP_E_UNKNOWNNAME, DISP_E_MEMBERNOTFOUND}

# pywin32 raises these when a late-bound name lookup fails. The underlying
# com_error is swallowed (dynamic.py), so "AutoCAD refused the call" and "no
# such member" look identical here; _probe_name() tells them apart.
_REFUSED_NAME = re.compile(
    r"^(?:Property ')?(?:<unknown>|AutoCAD\.Application)\.[A-Za-z_]\w*"
    r"(?:' can not be set\.)?$", re.I)


class _BusyError(ToolError):
    """AutoCAD stayed busy, or the COM lock stayed held, past the deadline."""


class _NotRunning(ToolError):
    """No AutoCAD in the running object table."""


def _hresults(exc: BaseException) -> set[int]:
    """Every HRESULT a pywintypes.com_error carries (outer + excepinfo scode)."""
    codes: set[int] = set()
    if type(exc).__name__ != "com_error":
        return codes
    args = exc.args
    if args and isinstance(args[0], int):
        codes.add(args[0])
    if len(args) > 2 and isinstance(args[2], tuple) and len(args[2]) > 5 \
            and isinstance(args[2][5], int):
        codes.add(args[2][5])
    return codes


def _probe_name(raw: Any, name: str) -> str:
    """Ask IDispatch directly whether `name` exists: 'exists' | 'missing' |
    'busy' | 'stale' | 'unknown'. Used only after pywin32 raised its generic
    AttributeError, to decide between retrying and failing fast."""
    ole = getattr(raw, "_oleobj_", None)
    ask = getattr(ole, "GetIDsOfNames", None)
    if ask is None:
        return "unknown"
    try:
        ask(0, name)
        return "exists"
    except Exception as exc:  # noqa: BLE001 - classified below
        codes = _hresults(exc)
        if codes & _MISSING_HR:
            return "missing"
        if codes & _BUSY_HR:
            return "busy"
        if codes & _STALE_HR:
            return "stale"
        return "unknown"


def _classify(exc: BaseException, raw: Any = None, name: str | None = None) -> str:
    """'busy' | 'stale' | 'refused' | 'missing' | 'other'."""
    if isinstance(exc, _BusyError):
        return "busy"
    codes = _hresults(exc)
    if codes & _BUSY_HR:
        return "busy"
    if codes & _STALE_HR:
        return "stale"
    if "rejected by callee" in str(exc).lower():
        return "busy"
    if isinstance(exc, AttributeError) and _REFUSED_NAME.match(str(exc).strip()):
        if raw is not None and name:
            probe = _probe_name(raw, name)
            if probe == "missing":
                return "missing"
            if probe in ("busy", "stale"):
                return probe
        return "refused"
    return "other"


def _hint_for(text: str) -> str:
    t = text.lower()
    if "key not found" in t:
        return ("a named object (layer, block, layout, text style) or handle "
                "does not exist in that drawing")
    if "invalid input" in t:
        return "an argument value is out of range or of the wrong kind"
    if "locked layer" in t or "on locked" in t:
        return "the entity is on a locked layer"
    return ""


def _explain(exc: BaseException) -> str:
    """Turn any exception into a message an LLM caller can act on."""
    if type(exc).__name__ == "com_error":
        a = exc.args
        desc = None
        if len(a) > 2 and isinstance(a[2], tuple) and len(a[2]) > 2 and a[2][2]:
            desc = str(a[2][2]).strip()
        base = desc or (str(a[1]) if len(a) > 1 else str(exc))
        codes = _hresults(exc)
        hx = ", ".join(f"0x{c & 0xFFFFFFFF:08X}" for c in sorted(codes))
        if codes & _BUSY_HR:
            hint = "AutoCAD is busy and rejected the call; retry once it is idle (acad_wait_idle)"
        elif codes & _STALE_HR:
            hint = ("the COM object went stale (drawing closed or reopened, or "
                    "AutoCAD restarted); retry")
        elif MK_E_UNAVAILABLE in codes:
            hint = "AutoCAD is not running"
        else:
            hint = _hint_for(base)
        return f"AutoCAD COM error: {base} [{hx}]" + (f" -- {hint}" if hint else "")
    if isinstance(exc, FileNotFoundError):
        return f"File not found: {exc.filename or exc}"
    if isinstance(exc, PermissionError):
        return (f"Permission denied: {exc.filename or exc} (is the file open in "
                "another program?)")
    if isinstance(exc, AttributeError) and _REFUSED_NAME.match(str(exc).strip()):
        return (f"AutoCAD refused or does not support {str(exc)!r} (busy, stale "
                "object, read-only property or invalid value); retry once idle")
    return f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------
# Safety gates and audit log. Every switch is read from the environment when
# a tool is CALLED, never cached at import, so tests can flip them.
# --------------------------------------------------------------------------

_RESTART = "in this server's env in the MCP registration and restart Claude Code"
_AUDIT_PATH = PROJECT / "logs" / "mcp_calls.jsonl"
_AUDIT_MAX = 5 * 1024 * 1024        # bytes; then the log moves to .1 (one kept)
_AUDIT_LOCK = threading.Lock()
_CLIP_STR, _CLIP_LIST = 300, 50     # argument truncation in the audit line
# Logged whole: padding past the clip would hide the command AutoCAD runs.
_UNCLIPPED = {("acad_send_command", "command")}
_ANNOTATIONS: dict[str, ToolAnnotations] = {}   # every registered tool, by name
_CALLS = threading.local()          # depth > 0 inside a tool: nested calls are one call


class _Refused(ToolError):
    """A safety gate refused the call; `gate` names it in the audit log."""

    def __init__(self, gate: str, message: str):
        super().__init__(message)
        self.gate = gate


def _env_is(var: str, *values: str) -> bool:
    return os.environ.get(var, "").strip().lower() in values


def _write_roots() -> list[str]:
    """Folders a tool may write a caller-chosen file under: ACAD_WRITE_ROOTS
    (os.pathsep-separated, absolute; quotes around an entry are dropped) if
    set, else Desktop (OneDrive and local), this pipeline folder and %TEMP%.
    Resolved like the paths checked. Relative entries are ignored, so the
    list can be empty: then every write is refused (_check_write_path)."""
    raw = os.environ.get("ACAD_WRITE_ROOTS", "")
    if raw.strip():
        roots = [e for e in (r.strip().strip("\"'").strip() for r in raw.split(os.pathsep))
                 if os.path.isabs(e)]
    else:
        home = os.path.expanduser("~")
        roots = [os.path.join(home, "OneDrive", "Desktop"), os.path.join(home, "Desktop"),
                 str(PROJECT), tempfile.gettempdir()]
    return [os.path.realpath(r) for r in roots]


def _within(path: str, roots: list[str]) -> bool:
    """Is `path`, symlinks and '..' resolved, inside one of `roots`? Compared
    by whole components, so autocad-mcp-evil is not inside autocad-mcp. A
    network or device path is never inside: it is not resolved at all, since
    resolving \\\\host\\share would connect to that host."""
    try:
        if os.path.abspath(path).startswith(("\\\\", "//")):
            return False
        p = os.path.normcase(os.path.realpath(path))
    except (OSError, ValueError):
        return False
    for r in roots:
        r = os.path.normcase(r)
        with contextlib.suppress(ValueError):       # another drive
            if os.path.commonpath([p, r]) == r:
                return True
    return False


def _check_write_path(path: str, what: str) -> None:
    """Refuse a caller-chosen output path outside the write roots. UNC and
    device paths (\\\\server\\share, \\\\?\\C:\\...) are refused outright."""
    roots = _write_roots()
    if not roots:
        raise _Refused("write_roots",
                       f"Refused: {what} path {path} -- ACAD_WRITE_ROOTS names no absolute "
                       f"folder, so no path is allowed. Fix it {_RESTART}.")
    if str(path).startswith(("\\\\", "//")):
        why = "network (UNC) and device paths are not accepted"
    elif not _within(path, roots):
        why = "it is outside the allowed write roots"
    else:
        return
    shown = "; ".join(roots)
    raise _Refused("write_roots",
                   f"Refused: {what} path {path} -- {why}. Allowed roots: {shown}. "
                   f"Choose a path under one of them, or set ACAD_WRITE_ROOTS {_RESTART}.")


def _png_path(path: str) -> str:
    """acad_screenshot's output file, as the tool and the read-only gate see it."""
    path = os.path.abspath(path)
    return path if path.lower().endswith(".png") else path + ".png"


def _foreign_design(project: Any) -> str | None:
    """The folder of a `project` design outside this pipeline (neither the
    villa nor under projects\\), else None."""
    if project is None or not str(project).strip():
        return None
    try:
        ctx = _project(str(project), env={})
    except ToolError:
        return None                 # the tool refuses it the same way, before running it
    if ctx.is_villa or ctx.folder.is_relative_to(PROJECTS.resolve()):
        return None
    return str(ctx.folder)


def _read_only_refusal(name: str, call: dict[str, Any]) -> str | None:
    """With ACAD_READ_ONLY=1: None if this call may run, else why not.

    The classification is the tools' own readOnlyHint (set on every tool by
    _tool), plus two kinds of call that only inspect: dry_run=True (villa_run,
    acad_purge_and_audit -- its default --, acad_close_orphans), and an
    acad_screenshot into %TEMP% without drawing= (that would activate one).
    Any of them is refused with a project= outside the villa and projects\\:
    reading a design (villa_status, villa_validate, a villa_run dry run)
    executes its villa_design.py."""
    if not _env_is("ACAD_READ_ONLY", "1", "true"):
        return None
    foreign = _foreign_design(call.get("project"))
    if foreign:
        return (f"Refused: read-only mode (ACAD_READ_ONLY=1) and project={foreign} is outside "
                f"{PROJECTS}; reading a design runs its villa_design.py. Use a project under "
                f"projects\\, or unset ACAD_READ_ONLY {_RESTART}.")
    ann = _ANNOTATIONS.get(name)
    if ann is not None and ann.read_only_hint:
        return None
    if call.get("dry_run") is True:
        return None
    if name == "acad_screenshot" and call.get("path") and not call.get("drawing") \
            and _within(_png_path(call["path"]), [os.path.realpath(tempfile.gettempdir())]):
        return None
    return (f"Refused: read-only mode (ACAD_READ_ONLY=1) and {name} changes a drawing, "
            "AutoCAD or files. Read/inspect tools and dry runs still work; unset "
            f"ACAD_READ_ONLY {_RESTART} to allow changes.")


def _clip(v: Any) -> Any:
    """Arguments for the audit line: long strings and lists cut, with a marker."""
    if isinstance(v, str) and len(v) > _CLIP_STR:
        return v[:_CLIP_STR] + f"...[truncated {len(v) - _CLIP_STR} chars]"
    if isinstance(v, (list, tuple)):
        out = [_clip(x) for x in v[:_CLIP_LIST]]
        if len(v) > _CLIP_LIST:
            out.append(f"...[truncated {len(v) - _CLIP_LIST} items]")
        return out
    if isinstance(v, dict):
        return {str(k): _clip(x) for k, x in v.items()}
    return v


def _audit(tool: str, args: dict[str, Any], t0: float, exc: BaseException | None,
           gate: str | None = None) -> None:
    """Append one JSON line for a tool call. Never raises and does no more
    than a stat and an append: a broken log must not break the call. Only the
    call is recorded -- nothing from the environment. ASCII-only JSON, so no
    argument (U+2028, U+0085, ...) can split a record for any line reader."""
    try:
        if _env_is("ACAD_AUDIT_LOG", "0", "false"):
            return
        rec: dict[str, Any] = {
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds"),
            "tool": tool,
            "args": {str(k): v if (tool, k) in _UNCLIPPED else _clip(v)
                     for k, v in args.items()},
            "outcome": "ok" if exc is None else "error",
            "ms": round((time.perf_counter() - t0) * 1000.0, 1)}
        if exc is not None:
            # A translated failure is reported by its original class.
            cause = exc.__cause__ if type(exc) is ToolError and exc.__cause__ else exc
            rec["error"] = {"class": type(cause).__name__, "message": str(exc)[:200]}
            gate = gate or getattr(exc, "gate", None)
            if gate:
                rec["gate"] = gate
        line = json.dumps(rec, ensure_ascii=True, default=repr) + "\n"
        path = _AUDIT_PATH
        with _AUDIT_LOCK:
            path.parent.mkdir(parents=True, exist_ok=True)
            with contextlib.suppress(OSError):
                if path.stat().st_size >= _AUDIT_MAX:
                    os.replace(path, path.with_name(path.name + ".1"))
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:  # noqa: BLE001 - logging must never reach the tool call
        pass


def _ann(title: str, *, ro: bool = False, destructive: bool = False,
         idempotent: bool = False, open_world: bool = False) -> ToolAnnotations:
    return ToolAnnotations(title=title, read_only_hint=ro,
                           destructive_hint=(destructive and not ro),
                           idempotent_hint=idempotent, open_world_hint=open_world)


def _tool(title: str, **hints: bool):
    """Register a tool with annotations; convert every failure to ToolError.

    The outermost call also passes the read-only gate and writes the audit
    line; a tool calling another tool (villa_run -> acad_status) is one call.
    The signature, name and docstring are the function's (functools.wraps),
    so the tool listing is unchanged."""
    ann = _ann(title, **hints)

    def deco(fn):
        name = fn.__name__
        sig = inspect.signature(fn)
        _ANNOTATIONS[name] = ann

        def run(args, kwargs):
            try:
                return fn(*args, **kwargs)
            except ToolError:
                raise
            except Exception as exc:  # noqa: BLE001 - translated for the caller
                raise ToolError(_explain(exc)) from exc

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if getattr(_CALLS, "depth", 0):
                return run(args, kwargs)
            t0 = time.perf_counter()
            try:
                # Logged with defaults filled in: what the tool runs with, and
                # what the SDK passes anyway (every field of the validated model).
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                call = dict(bound.arguments)
            except TypeError:                # bad direct call: fn raises it below
                call = {"args": list(args), **kwargs}
            err = None
            _CALLS.depth = 1
            try:
                why = _read_only_refusal(name, call)
                if why:
                    raise _Refused("read_only", why)
                return run(args, kwargs)
            except BaseException as exc:
                err = exc
                with contextlib.suppress(Exception):
                    exc._acad_audited = True     # _call_tool_audited must not log it again
                raise
            finally:
                _CALLS.depth = 0
                _audit(name, call, t0, err)

        mcp.add_tool(wrapper, name=name, title=title,
                     description=inspect.cleandoc(fn.__doc__ or ""),
                     annotations=ann)
        return wrapper

    return deco


_sdk_call_tool = mcp.call_tool


async def _call_tool_audited(name: str, arguments: dict[str, Any], context: Any = None) -> Any:
    """MCPServer.call_tool plus an audit line for a call the SDK rejects before
    any tool runs (unknown tool, arguments that fail validation). A call that
    reached a tool was logged by _tool's wrapper, which marks its exception."""
    t0 = time.perf_counter()
    try:
        return await _sdk_call_tool(name, arguments, context)
    except Exception as exc:
        e: BaseException | None = exc
        while e is not None and not getattr(e, "_acad_audited", False):
            e = e.__cause__
        if e is None:
            gate = ("validation" if isinstance(exc.__cause__, ValidationError) else
                    "unknown_tool" if name not in _ANNOTATIONS else "sdk")
            _audit(str(name), arguments if isinstance(arguments, dict) else {}, t0, exc, gate)
        raise


mcp.call_tool = _call_tool_audited    # the SDK's handler looks it up on every call


# --------------------------------------------------------------------------
# COM plumbing
# --------------------------------------------------------------------------

# Generic ProgID first (follows whatever version is running); the versioned one
# is a fallback for installs where the generic alias is missing or hijacked.
# AutoCAD 2027 registers AutoCAD.Application.26.
_PROGIDS = ("AutoCAD.Application", "AutoCAD.Application.26")

_T_READ = 30.0     # s, default deadline for read-only tools
_T_EDIT = 60.0     # s, default deadline for tools that change a drawing
_QUIESCE = 10.0    # s, how long a changing tool waits for AutoCAD to go idle
_GRACE = 15.0      # s, beyond the deadline before a call is declared hung
_REFUSED_TRIES = 4  # per-call retries for an ambiguous '<unknown>.X' failure

# Methods that only read, or are harmless to repeat. Any OTHER successful method
# call marks the job as having side effects, which forbids a whole-job retry.
_SAFE_METHODS = frozenset({
    "Item", "GetVariable", "GetBoundingBox", "HandleToObject",
    "ObjectIdToObject", "GetAcadState", "GetCanonicalMediaNames",
    "GetLocaleMediaName", "GetPlotDeviceNames", "GetPlotStyleTableNames",
    "GetCustomScale", "GetWindowToPlot", "GetPaperSize", "GetXData",
    "GetAttributes", "GetDynamicBlockProperties", "IntersectWith",
    "Activate", "ZoomExtents", "Regen", "Update",
})

_COM_LOCK = threading.Lock()
_LOCK_INFO: dict[str, Any] = {}
_EXEC: ThreadPoolExecutor | None = None
_EXEC_GUARD = threading.Lock()
_TLS = threading.local()   # per-thread: deadline + "has this job changed anything"


def _deadline() -> float:
    """The running job's deadline. Outside a job there is none, so no retry
    (a moving 'now + N' default would retry a busy call forever)."""
    d = getattr(_TLS, "deadline", None)
    return d if d is not None else time.monotonic()


def _retry_call(fn, *, raw: Any = None, name: str | None = None,
                mutating: bool = False):
    """Run one COM call, retrying while AutoCAD is busy.

    A call AutoCAD REJECTED was never executed, so repeating it is safe even
    when it changes the drawing. Proven-busy HRESULTs retry until the job's
    deadline; an ambiguous '<unknown>.X' only a few times.
    """
    delay = 0.15
    refused = 0
    while True:
        try:
            out = fn()
        except Exception as exc:
            kind = _classify(exc, raw, name)
            if kind == "missing":
                raise AttributeError(
                    f"AutoCAD object has no member {name!r}") from None
            if kind == "refused":
                refused += 1
            retry = kind == "busy" or (kind == "refused" and refused < _REFUSED_TRIES)
            if retry and time.monotonic() + delay < _deadline():
                time.sleep(delay)
                delay = min(delay * 1.7, 2.0)
                continue
            raise
        if mutating:
            _TLS.mutated = True
        return out


def _late(obj: Any) -> Any:
    """Re-wrap a COM object LATE-bound.

    Objects that come back through enumeration are wrapped via pywin32's
    early-binding cache when one exists, and the cached interfaces are
    case-sensitive and narrow: IAcadLayer has `color` not `Color`, and a
    generic IAcadEntity has no Length/Area/TextString.
    """
    if isinstance(obj, _Com):
        return obj._o
    try:
        from win32com.client import dynamic
    except ImportError:          # not Windows / no pywin32: leave it alone
        return obj
    if isinstance(obj, dynamic.CDispatch):
        return obj
    ole = obj if type(obj).__name__ == "PyIDispatch" else getattr(obj, "_oleobj_", None)
    if ole is not None and type(ole).__name__ == "PyIDispatch":
        return dynamic.Dispatch(ole)
    return obj


def _is_dispatch(v: Any) -> bool:
    return type(v).__name__ == "PyIDispatch" or hasattr(v, "_oleobj_")


def _unwrap(v: Any) -> Any:
    """Proxies -> raw objects, for passing as COM arguments."""
    if isinstance(v, _Com):
        return v._o
    if isinstance(v, (list, tuple)):
        return type(v)(_unwrap(x) for x in v)
    try:
        from win32com.client import VARIANT
    except ImportError:
        return v
    if isinstance(v, VARIANT):
        return VARIANT(v.varianttype, _unwrap(v.value))
    return v


def _wrap(v: Any, name: str = "") -> Any:
    if v is None or isinstance(v, (bool, int, float, str, bytes)):
        return v
    if isinstance(v, (_Com, _Method)):
        return v
    if isinstance(v, types.MethodType):
        return _Method(v, name or getattr(v, "__name__", "?"))
    if _is_dispatch(v):
        return _Com(_late(v))
    if isinstance(v, tuple):
        return tuple(_wrap(x) for x in v)
    if isinstance(v, list):
        return [_wrap(x) for x in v]
    return v


class _Method:
    """A bound COM method whose calls are retried while AutoCAD is busy."""

    __slots__ = ("_m", "_name")

    def __init__(self, m, name: str):
        self._m = m
        self._name = name

    def __call__(self, *args):
        ua = tuple(_unwrap(a) for a in args)
        m = self._m
        out = _retry_call(lambda: m(*ua), name=self._name,
                          mutating=self._name not in _SAFE_METHODS)
        return _wrap(out, self._name)


class _Com:
    """Late-bound COM proxy: every property read/write and method call goes
    through _retry_call, and every object read back is wrapped the same way."""

    __slots__ = ("_o",)

    def __init__(self, obj: Any):
        object.__setattr__(self, "_o", obj)

    @property
    def _oleobj_(self):
        return self._o._oleobj_

    def __getattr__(self, name: str):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        raw = self._o
        return _wrap(_retry_call(lambda: getattr(raw, name), raw=raw, name=name), name)

    def __setattr__(self, name: str, value: Any) -> None:
        raw = self._o
        v = _unwrap(value)
        _retry_call(lambda: setattr(raw, name, v), raw=raw, name=name)

    def __iter__(self):
        raw = self._o
        items = _retry_call(lambda: list(raw))
        return iter([_wrap(x) for x in items])

    def __repr__(self) -> str:
        return f"<late {self._o!r}>"


def _sta_init() -> None:
    try:
        import pythoncom
        pythoncom.CoInitialize()        # STA: AutoCAD's own apartment model
    except Exception:  # noqa: BLE001 - non-Windows: jobs will fail on attach
        pass


def _executor() -> ThreadPoolExecutor:
    global _EXEC
    with _EXEC_GUARD:
        if _EXEC is None:
            _EXEC = ThreadPoolExecutor(max_workers=1, thread_name_prefix="acad-sta",
                                       initializer=_sta_init)
        return _EXEC


def _abandon_executor(ex: ThreadPoolExecutor) -> None:
    """A call hung inside AutoCAD. Leave that thread to finish on its own; new
    calls get a fresh thread (and will wait on the lock the hung call holds)."""
    global _EXEC
    with _EXEC_GUARD:
        if _EXEC is ex:
            _EXEC = None
    ex.shutdown(wait=False, cancel_futures=True)


def _lock_snapshot() -> dict[str, Any] | None:
    info = dict(_LOCK_INFO)
    if not info:
        return None
    return {"held_by": info.get("owner"),
            "for_s": round(time.monotonic() - info.get("since", time.monotonic()), 1)}


@contextlib.contextmanager
def _holding_com_lock(owner: str, timeout: float):
    if not _COM_LOCK.acquire(timeout=max(0.0, timeout)):
        snap = _lock_snapshot() or {}
        raise _BusyError(
            f"{owner}: the AutoCAD COM lock is held by "
            f"{snap.get('held_by', 'another call')} (for {snap.get('for_s', '?')} s). "
            "Only one COM caller may drive AutoCAD at a time; retry when it finishes.")
    _LOCK_INFO.clear()
    _LOCK_INFO.update(owner=owner, since=time.monotonic())
    try:
        yield
    finally:
        _LOCK_INFO.clear()
        _COM_LOCK.release()


def _attach():
    """Attach to a running AutoCAD, late-bound. Never launches one -- that
    should be a deliberate user action, not a side effect of a tool call."""
    import pythoncom
    import pywintypes
    from win32com.client import dynamic

    last = None
    for progid in _PROGIDS:
        try:
            unk = pythoncom.GetActiveObject(pywintypes.IID(progid))
            disp = unk.QueryInterface(pythoncom.IID_IDispatch)
            return _Com(dynamic.Dispatch(disp, "AutoCAD.Application"))
        except Exception as exc:  # noqa: BLE001
            if _classify(exc) == "busy":
                raise
            last = exc
    raise _NotRunning(
        "No running AutoCAD found. Start AutoCAD (or AutoCAD Architecture), open a "
        f"drawing, then retry. COM said: {last}")


def _run_job(job, deadline: float, idempotent: bool, what: str, attach,
             quiesce: float, timeout: float):
    """Body of every COM tool call; runs on the single STA worker thread."""
    with _holding_com_lock(what, deadline - time.monotonic()):
        delay = 0.5
        while True:
            _TLS.deadline = deadline
            _TLS.mutated = False
            try:
                app = attach()
                if quiesce:
                    budget = min(quiesce, max(0.0, deadline - time.monotonic()))
                    idle, state = _wait_idle(app, budget)
                    if not idle:
                        raise _BusyError(
                            f"{what}: AutoCAD is not idle after {budget:.0f} s (a "
                            f"command, prompt or dialog is active: {state}). Finish or "
                            "cancel it in AutoCAD (Esc), then retry.")
                return job(app)
            except ToolError:
                raise
            except Exception as exc:
                kind = _classify(exc)
                transient = kind in ("busy", "stale", "refused")
                if transient and (idempotent or not _TLS.mutated) \
                        and time.monotonic() + delay < deadline:
                    time.sleep(delay)
                    delay = min(delay * 1.6, 4.0)
                    continue
                if transient:
                    raise _BusyError(
                        f"{what}: AutoCAD stayed busy or unreachable for {timeout:.0f} s "
                        f"({_explain(exc)})."
                        + (" Part of the job had already run, so it was NOT repeated: "
                           "check the drawing before retrying." if _TLS.mutated else "")
                    ) from exc
                raise
            finally:
                _TLS.deadline = None


def _com(job, *, what: str, timeout: float = _T_EDIT, idempotent: bool = False,
         quiesce: float = 0.0, attach=None):
    """Run `job(app)` on the STA thread under the COM lock, with a deadline.

    `idempotent` jobs are re-run from scratch when AutoCAD stays busy or a proxy
    goes stale; other jobs only while nothing they did has taken effect.
    `quiesce` > 0 first waits that long for AutoCAD to be idle.
    """
    deadline = time.monotonic() + timeout
    ex = _executor()
    fut = ex.submit(_run_job, job, deadline, idempotent, what, attach or _attach,
                    quiesce, timeout)
    try:
        return fut.result(timeout=timeout + _GRACE)
    except FuturesTimeout:
        if fut.done():        # the job itself raised TimeoutError
            raise
        fut.cancel()
        _abandon_executor(ex)
        raise ToolError(
            f"{what}: AutoCAD did not answer within {timeout + _GRACE:.0f} s. A modal "
            "dialog or a command waiting at a prompt blocks COM. The stuck call keeps "
            "the COM lock until AutoCAD answers: clear AutoCAD (Esc / close the "
            "dialog; acad_screenshot shows what is on screen), then retry.") from None
    except CancelledError:
        raise ToolError(f"{what}: cancelled because an earlier AutoCAD call hung; "
                        "retry.") from None


# ---- idle / quiescence ------------------------------------------------------

def _idle_state(app: Any) -> dict[str, Any]:
    """GetAcadState().IsQuiescent, with CMDACTIVE as fallback. Raw calls: a
    rejected probe just means 'not idle yet'."""
    raw = app._o if isinstance(app, _Com) else app
    st: dict[str, Any] = {"quiescent": None, "cmdactive": None}
    try:
        st["quiescent"] = bool(raw.GetAcadState().IsQuiescent)
    except Exception:  # noqa: BLE001
        pass
    if st["quiescent"] is None:
        try:
            st["cmdactive"] = int(raw.ActiveDocument.GetVariable("CMDACTIVE"))
        except Exception:  # noqa: BLE001
            pass
    return st


def _is_idle(st: dict[str, Any]) -> bool:
    return st["quiescent"] is True or (st["quiescent"] is None and st["cmdactive"] == 0)


def _wait_idle(app: Any, budget: float, *, need: int = 1,
               interval: float = 0.25) -> tuple[bool, dict[str, Any]]:
    t0 = time.monotonic()
    end = t0 + max(0.0, budget)
    streak = 0
    while True:
        st = _idle_state(app)
        streak = streak + 1 if _is_idle(st) else 0
        if streak >= need:
            return True, {**st, "waited_s": round(time.monotonic() - t0, 2)}
        if time.monotonic() >= end:
            return False, {**st, "waited_s": round(time.monotonic() - t0, 2)}
        time.sleep(interval)


# ---- variants ---------------------------------------------------------------

def _pt(coords: list[float]):
    """Build the VT_ARRAY|VT_R8 variant the AutoCAD COM API expects for a point."""
    import pythoncom
    from win32com.client import VARIANT

    if len(coords) == 2:
        coords = [coords[0], coords[1], 0.0]
    if len(coords) != 3:
        raise ValueError(f"point needs 2 or 3 numbers, got {len(coords)}")
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(c) for c in coords])


def _dbl_array(vals: list[float]):
    import pythoncom
    from win32com.client import VARIANT

    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])


def _objs(items: list[Any]):
    """VT_ARRAY|VT_DISPATCH: what AppendOuterLoop/CopyObjects demand. A plain
    Python list is rejected as 'Invalid object array'."""
    import pythoncom
    from win32com.client import VARIANT

    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [_unwrap(i) for i in items])


# ---- documents ----------------------------------------------------------------

_ORPHAN_RE = re.compile(r"^Drawing\d+\.dwg$", re.I)
_UNITS = {0: "unitless", 1: "inches", 2: "feet", 3: "miles", 4: "millimetres",
          5: "centimetres", 6: "metres", 7: "kilometres", 10: "yards",
          14: "decimetres"}
_MM_PER_UNIT = {0: 1.0, 1: 25.4, 2: 304.8, 4: 1.0, 5: 10.0, 6: 1000.0,
                10: 914.4, 14: 100.0}


def _norm(p: str) -> str:
    return os.path.normcase(os.path.abspath(p))


def _docs(app) -> list[Any]:
    docs = app.Documents
    return [docs.Item(i) for i in range(int(docs.Count))]


def _active_name(app) -> str | None:
    try:
        return str(app.ActiveDocument.Name)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001 - no document open is a normal state
        if _classify(exc) == "busy":
            raise
        return None


def _resolve_doc(app, drawing: str = "", *, explicit: bool = False) -> tuple[Any, str]:
    """Find an open drawing BY NAME (exact name, then full path, then stem).
    With no name, fall back to the active drawing -- unless `explicit` and
    several drawings are open, where guessing could hit the wrong one."""
    docs = _docs(app)
    if not docs:
        raise ToolError("AutoCAD has no open drawing (it may be on the Start tab). "
                        "Open one with acad_open_drawing or acad_new_drawing.")
    names = [str(d.Name) for d in docs]
    if drawing:
        want = drawing.strip()
        hits = [i for i, n in enumerate(names) if n.lower() == want.lower()]
        if not hits and ("\\" in want or "/" in want):
            wn = _norm(want)
            hits = [i for i, d in enumerate(docs)
                    if str(d.FullName) and _norm(str(d.FullName)) == wn]
        if not hits:
            stem = Path(want).stem.lower()
            hits = [i for i, n in enumerate(names) if Path(n).stem.lower() == stem]
        if not hits:
            raise ToolError(f"No open drawing matches {drawing!r}. Open drawings: {names}.")
        if len(hits) > 1:
            raise ToolError(f"{drawing!r} is ambiguous: it matches "
                            f"{[names[i] for i in hits]}. Use the exact name.")
        return docs[hits[0]], names[hits[0]]
    if explicit and len(docs) > 1:
        raise ToolError(
            f"{len(docs)} drawings are open ({names}). Entity handles are unique only "
            "within one drawing, so pass drawing=<name> explicitly.")
    doc = app.ActiveDocument
    return doc, str(doc.Name)


def _find_doc(app, *, name: str | None = None, path: str | None = None):
    """Re-resolve a document after Open/Add/SaveAs, never via ActiveDocument."""
    for d in _docs(app):
        if path and str(d.FullName) and _norm(str(d.FullName)) == _norm(path):
            return d
        if name and str(d.Name).lower() == name.lower():
            return d
    return None


def _ent(doc, drawing_name: str, handle: str):
    try:
        return doc.HandleToObject(handle)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        if _classify(exc) in ("busy", "stale"):
            raise
        raise ToolError(f"No entity with handle {handle!r} in {drawing_name}. Handles "
                        "are per drawing: pass the drawing the handle came from.") from None


def _require_layer(doc, layer: str) -> None:
    try:
        doc.Layers.Item(layer)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        if _classify(exc) in ("busy", "stale"):
            raise
        raise ToolError(f"Layer {layer!r} does not exist in this drawing; create it "
                        "with acad_create_layer first. Nothing was drawn.") from None


def _safe_delete(ent) -> None:
    with contextlib.suppress(Exception):
        ent.Delete()


def _create(doc, layer: str, make, finish=None):
    """Validate the layer FIRST, then create; if finishing the new entity or
    putting it on its layer fails, delete it rather than leave an orphan that a
    retry would duplicate."""
    if layer:
        _require_layer(doc, layer)
    ent = make(doc.ModelSpace)
    try:
        if finish is not None:
            finish(ent)
        if layer:
            ent.Layer = layer
    except Exception:
        _safe_delete(ent)
        raise
    return ent


def _opt(obj, prop: str, default: Any = None) -> Any:
    """Read an optional property: missing -> default, busy -> raise."""
    try:
        return getattr(obj, prop)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        if _classify(exc) in ("busy", "stale"):
            raise
        return default


def _insunits(doc) -> int:
    try:
        return int(doc.GetVariable("INSUNITS"))
    except ToolError:
        raise
    except Exception:  # noqa: BLE001
        return 0


def _bbox(ent) -> list[float] | None:
    try:
        lo, hi = ent.GetBoundingBox()
        return [round(float(v), 3) for v in (*lo[:3], *hi[:3])]
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        if _classify(exc) in ("busy", "stale"):
            raise
        return None


_PROPS = {
    "AcDbLine": ("Length", "Angle"),
    "AcDbCircle": ("Radius", "Area", "Circumference"),
    "AcDbArc": ("Radius", "ArcLength", "TotalAngle", "Area"),
    "AcDbPolyline": ("Length", "Area", "Closed"),
    "AcDb2dPolyline": ("Length", "Area", "Closed"),
    "AcDb3dPolyline": ("Length", "Closed"),
    "AcDbEllipse": ("MajorRadius", "MinorRadius", "Area"),
    "AcDbSpline": ("Area", "Closed"),
    "AcDbHatch": ("Area", "PatternName"),
    "AcDbRegion": ("Area", "Perimeter"),
    "AcDb3dSolid": ("Volume",),
    "AcDbRotatedDimension": ("Measurement", "TextOverride"),
    "AcDbAlignedDimension": ("Measurement", "TextOverride"),
    "AcDbText": ("TextString", "Height", "Rotation"),
    "AcDbMText": ("TextString", "Height", "Rotation"),
    "AcDbBlockReference": ("EffectiveName", "Name", "Rotation", "XScaleFactor",
                           "YScaleFactor"),
}
_GENERIC_PROPS = ("Length", "Area", "Radius", "ArcLength", "Circumference",
                  "Volume", "Measurement")
_ANGLE_PROPS = {"Angle", "TotalAngle", "Rotation"}
_PROP_KEYS = {"TextString": "text", "EffectiveName": "block", "Name": "name",
              "XScaleFactor": "x_scale", "YScaleFactor": "y_scale",
              "TotalAngle": "total_angle_deg", "Angle": "angle_deg",
              "Rotation": "rotation_deg", "ArcLength": "arc_length",
              "MajorRadius": "major_radius", "MinorRadius": "minor_radius",
              "PatternName": "pattern", "TextOverride": "text_override"}


def _read_props(ent, kind: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for p in _PROPS.get(kind, _GENERIC_PROPS):
        v = _opt(ent, p)
        if v is None:
            continue
        key = _PROP_KEYS.get(p, p.lower())
        if isinstance(v, bool):
            out[key] = v
        elif isinstance(v, (int, float)):
            out[key] = round(math.degrees(v), 6) if p in _ANGLE_PROPS else round(float(v), 6)
        else:
            out[key] = str(v)
    return out


# --------------------------------------------------------------------------
# Parameter types (JSON schema the LLM sees)
# --------------------------------------------------------------------------

Point = Annotated[list[float], Field(
    min_length=2, max_length=3,
    description="[x, y] or [x, y, z] in drawing units (villa drawings: millimetres).")]
Drawing = Annotated[str, Field(
    description="Open drawing to act on, by document name as acad_list_drawings "
                "shows it (e.g. 'VILLA_A102.dwg'); a full path or the bare stem also "
                "matches. Empty = the active drawing. The result names the drawing "
                "actually used.")]
Handle = Annotated[str, Field(
    min_length=1, max_length=16, pattern=r"^[0-9A-Fa-f]+$",
    description="Entity handle (hex) as returned by the draw/summarize tools. "
                "Handles are unique only within one drawing.")]
LayerName = Annotated[str, Field(
    description="Existing layer for the new entity; empty = current layer. A missing "
                "layer is an error and nothing is drawn.")]
Length = Annotated[float, Field(gt=0, description="Length in drawing units (mm for the villa).")]

# ==========================================================================
# Live AutoCAD tools
# ==========================================================================


@_tool("AutoCAD status", ro=True, idempotent=True)
def acad_status(drawing: Drawing = "") -> dict[str, Any]:
    """Check whether AutoCAD is reachable and describe one drawing.

    Reports application/version, whether AutoCAD is idle, how many drawings are
    open (and how many are unsaved DrawingN orphans), and for the named (or
    active) drawing: path, unsaved changes, current layer, model-space entity
    count and units. Never fails just because AutoCAD is busy or closed: those
    states come back as fields (connected=False, busy=True).
    """
    def job(app):
        out: dict[str, Any] = {"connected": True, "application": str(app.Name),
                               "version": str(app.Version), "idle": _idle_state(app)}
        docs = _docs(app)
        info = [(str(d.Name), str(d.FullName)) for d in docs]
        out["open_drawings"] = len(info)
        out["orphans"] = [n for n, full in info if _ORPHAN_RE.match(n) and not full]
        if not docs:
            out["drawing"] = None
            out["note"] = "AutoCAD is running with no drawing open (Start tab)."
            return out
        doc, name = _resolve_doc(app, drawing)
        units = _insunits(doc)
        out.update(drawing=name, path=str(doc.FullName) or None,
                   unsaved_changes=not bool(doc.Saved),
                   active=name == _active_name(app),
                   layer=str(doc.ActiveLayer.Name),
                   entities_in_modelspace=int(doc.ModelSpace.Count),
                   insunits=units, units=_UNITS.get(units, f"code {units}"))
        return out

    try:
        res = _com(job, what="acad_status", timeout=20.0, idempotent=True)
    except _NotRunning as exc:
        return {"connected": False, "error": str(exc)}
    except _BusyError as exc:
        return {"connected": None, "busy": True, "error": str(exc),
                "com_lock": _lock_snapshot()}
    res["com_lock"] = _lock_snapshot()
    return res


@_tool("Wait until AutoCAD is idle", ro=True, idempotent=True)
def acad_wait_idle(timeout_s: Annotated[float, Field(ge=1, le=600)] = 30.0) -> dict[str, Any]:
    """Wait until AutoCAD is quiescent (GetAcadState().IsQuiescent, falling back
    to CMDACTIVE == 0): no command, prompt or modal dialog active. Returns
    idle=False with the last state if it does not settle within timeout_s."""
    def job(app):
        idle, st = _wait_idle(app, timeout_s, need=2)
        return {"idle": idle, **st}

    return _com(job, what="acad_wait_idle", timeout=timeout_s + 20.0, idempotent=True)


@_tool("List open drawings", ro=True, idempotent=True)
def acad_list_drawings() -> dict[str, Any]:
    """List every drawing open in AutoCAD: name (use it as `drawing`), full path,
    whether it has unsaved changes, whether it was ever saved to disk, read-only,
    active, and whether it is an unsaved DrawingN orphan. AutoCAD sitting on its
    Start tab has zero open documents."""
    def job(app):
        active = _active_name(app)
        out = []
        for i, d in enumerate(_docs(app)):
            name, full = str(d.Name), str(d.FullName)
            out.append({"index": i, "name": name, "path": full or None,
                        "unsaved_changes": not bool(d.Saved), "never_saved": not full,
                        "read_only": bool(_opt(d, "ReadOnly", False)),
                        "active": name == active,
                        "orphan": bool(_ORPHAN_RE.match(name)) and not full})
        return {"count": len(out), "active": active, "drawings": out}

    return _com(job, what="acad_list_drawings", timeout=_T_READ, idempotent=True)


@_tool("New drawing")
def acad_new_drawing(template: Annotated[str, Field(
        description="Optional .dwt template path; empty = AutoCAD's default.")] = "") -> dict[str, Any]:
    """Create a new, unsaved drawing (DrawingN.dwg) and return its name. The new
    drawing is identified by diffing the document list, not via ActiveDocument."""
    if template and not os.path.exists(template):
        raise FileNotFoundError(template)

    def job(app):
        before = {n.lower() for n in (str(d.Name) for d in _docs(app))}
        ret = app.Documents.Add(template) if template else app.Documents.Add()
        new = [str(d.Name) for d in _docs(app) if str(d.Name).lower() not in before]
        name = new[0] if len(new) == 1 else str(ret.Name)
        return {"drawing": name, "open_drawings": int(app.Documents.Count)}

    return _com(job, what="acad_new_drawing", quiesce=_QUIESCE)


@_tool("Open drawing", idempotent=True)
def acad_open_drawing(path: Annotated[str, Field(description="Absolute path of a .dwg or .dxf file.")],
                      read_only: bool = False) -> dict[str, Any]:
    """Open a drawing file and make it active. If it is already open, it is
    activated instead of opened twice. The result's `drawing` is the name to
    pass to other tools (resolved by path after Open, never via ActiveDocument)."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    def job(app):
        d = _find_doc(app, path=path)
        if d is not None:
            d.Activate()
            return {"drawing": str(d.Name), "path": str(d.FullName), "already_open": True,
                    "read_only": bool(_opt(d, "ReadOnly", False))}
        app.Documents.Open(path, bool(read_only))
        d = _find_doc(app, path=path) or _find_doc(app, name=os.path.basename(path))
        if d is None:
            raise ToolError(f"AutoCAD accepted Open for {path} but the drawing is not in "
                            "the document list; check AutoCAD for a dialog.")
        return {"drawing": str(d.Name), "path": str(d.FullName), "already_open": False,
                "read_only": bool(read_only)}

    return _com(job, what="acad_open_drawing", timeout=120.0, quiesce=_QUIESCE)


@_tool("Activate drawing", idempotent=True)
def acad_activate_drawing(name: Annotated[str, Field(
        description="Drawing name as acad_list_drawings shows it (or full path / stem).")]) -> dict[str, Any]:
    """Switch AutoCAD's active drawing tab."""
    def job(app):
        doc, dn = _resolve_doc(app, name)
        doc.Activate()
        return {"active": _active_name(app), "requested": dn}

    return _com(job, what="acad_activate_drawing", timeout=_T_READ, idempotent=True)


@_tool("Save drawing", destructive=True)
def acad_save(drawing: Drawing = "",
              path: Annotated[str, Field(
                  description="Empty = save in place. Otherwise SaveAs to this .dwg/.dxf "
                              "path: the OPEN DOCUMENT IS RENAMED to it (it is not a copy), "
                              "so later saves go to the new path.")] = "",
              overwrite: Annotated[bool, Field(
                  description="Allow SaveAs over an existing file.")] = False) -> dict[str, Any]:
    """Save a drawing in place, or SaveAs to a new path (DWG 2018 for .dwg, DXF
    2018 for .dxf). Refuses to SaveAs onto a file that another open drawing
    uses. Returns the drawing's name after the save."""
    target = os.path.abspath(path) if path else ""
    if target:
        ext = os.path.splitext(target)[1].lower()
        if ext not in (".dwg", ".dxf"):
            raise ToolError("SaveAs path must end in .dwg or .dxf")
        _check_write_path(target, "acad_save")     # a save in place is not limited
        if os.path.exists(target) and not overwrite:
            raise ToolError(f"{target} exists; pass overwrite=True to replace it.")

    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        if not target:
            full = str(doc.FullName)
            if not full:
                raise ToolError(f"{name} has never been saved; pass path= to SaveAs.")
            if bool(_opt(doc, "ReadOnly", False)):
                raise ToolError(f"{name} is open read-only; SaveAs to another path.")
            doc.Save()
            return {"drawing": name, "saved": full}
        for d in _docs(app):
            full = str(d.FullName)
            if full and _norm(full) == _norm(target) and str(d.Name) != name:
                raise ToolError(f"{target} is open in AutoCAD as {d.Name}; close it first.")
        kind = 65 if target.lower().endswith(".dxf") else 64   # ac2018_dxf / ac2018_dwg
        doc.SaveAs(target, kind)
        d = _find_doc(app, path=target) or _find_doc(app, name=os.path.basename(target))
        return {"drawing": str(d.Name) if d is not None else os.path.basename(target),
                "path": target, "renamed_from": name,
                "format": "DXF 2018" if kind == 65 else "DWG 2018",
                "note": "SaveAs renamed the open document; later saves go to this path."}

    return _com(job, what="acad_save", timeout=120.0, quiesce=_QUIESCE)


@_tool("List orphan drawings", ro=True, idempotent=True)
def acad_list_orphans() -> dict[str, Any]:
    """List unsaved 'DrawingN.dwg' documents that were never saved to disk --
    typically left behind when a pipeline stage (villa_3d_build, villa_load)
    retried its whole job and called Documents.Add again."""
    def job(app):
        active = _active_name(app)
        out = []
        for d in _docs(app):
            name, full = str(d.Name), str(d.FullName)
            if _ORPHAN_RE.match(name) and not full:
                out.append({"drawing": name, "active": name == active,
                            "unsaved_changes": not bool(d.Saved),
                            "entities_in_modelspace": int(d.ModelSpace.Count)})
        return {"count": len(out), "orphans": out}

    return _com(job, what="acad_list_orphans", timeout=_T_READ, idempotent=True)


@_tool("Close orphan drawings", destructive=True)
def acad_close_orphans(
        names: Annotated[list[str] | None, Field(
            description="Only these (e.g. ['Drawing3.dwg']); omit for every orphan.")] = None,
        include_active: Annotated[bool, Field(
            description="Also close the ACTIVE drawing if it is an orphan (off by default: "
                        "someone may be working in it).")] = False,
        dry_run: bool = False) -> dict[str, Any]:
    """Close unsaved DrawingN documents WITHOUT saving. Only a document whose name
    is 'Drawing<digits>.dwg' AND that was never saved to disk qualifies; a saved
    drawing is never closed, whatever its name. Each is re-checked immediately
    before it is closed. dry_run=True lists what would be closed."""
    wanted = {n.lower() for n in (names or [])}

    def job(app):
        active = _active_name(app)
        targets, skipped = [], []
        seen = set()
        for d in _docs(app):
            n, full = str(d.Name), str(d.FullName)
            seen.add(n.lower())
            if wanted and n.lower() not in wanted:
                continue
            if not _ORPHAN_RE.match(n):
                if wanted:
                    skipped.append({"drawing": n, "reason": "not a DrawingN document"})
                continue
            if full:
                skipped.append({"drawing": n, "reason": f"saved to disk ({full})"})
                continue
            if n == active and not include_active:
                skipped.append({"drawing": n, "reason": "active drawing (include_active=True "
                                                      "to close it)"})
                continue
            targets.append((d, n))
        for w in sorted(wanted - seen):
            skipped.append({"drawing": w, "reason": "not open"})
        if dry_run:
            return {"dry_run": True, "would_close": [n for _, n in targets],
                    "skipped": skipped}
        closed = []
        for d, n in targets:
            if str(d.FullName) or not _ORPHAN_RE.match(str(d.Name)):
                skipped.append({"drawing": n, "reason": "changed before closing"})
                continue
            d.Close(False)                   # SaveChanges=False
            closed.append(n)
        return {"dry_run": False, "closed": closed, "skipped": skipped,
                "open_drawings": [str(d.Name) for d in _docs(app)]}

    return _com(job, what="acad_close_orphans", timeout=_T_EDIT, quiesce=_QUIESCE)


# ---- drawing primitives -------------------------------------------------------


@_tool("Draw line")
def acad_draw_line(start: Point, end: Point, layer: LayerName = "",
                   drawing: Drawing = "") -> dict[str, Any]:
    """Draw a line in model space between two points (drawing units, mm for the villa)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddLine(_pt(start), _pt(end)))
        return {"drawing": name, "created": "line", "handle": str(ent.Handle),
                "layer": str(ent.Layer), "length": round(float(ent.Length), 6)}

    return _com(job, what="acad_draw_line", quiesce=_QUIESCE)


@_tool("Draw circle")
def acad_draw_circle(center: Point, radius: Length, layer: LayerName = "",
                     drawing: Drawing = "") -> dict[str, Any]:
    """Draw a circle in model space. Radius in drawing units (mm for the villa)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddCircle(_pt(center), float(radius)))
        return {"drawing": name, "created": "circle", "handle": str(ent.Handle),
                "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_circle", quiesce=_QUIESCE)


@_tool("Draw polyline")
def acad_draw_polyline(points: Annotated[list[Point], Field(
                           min_length=2, description="Vertices [[x, y], ...]; z is ignored "
                                                     "(lightweight polylines are 2D).")],
                       closed: bool = False, layer: LayerName = "",
                       drawing: Drawing = "") -> dict[str, Any]:
    """Draw a lightweight (2D) polyline through the given vertices."""
    flat: list[float] = []
    for p in points:
        flat.extend([float(p[0]), float(p[1])])

    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddLightWeightPolyline(_dbl_array(flat)),
                      finish=(lambda e: setattr(e, "Closed", True)) if closed else None)
        return {"drawing": name, "created": "polyline", "handle": str(ent.Handle),
                "vertices": len(points), "closed": bool(closed), "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_polyline", quiesce=_QUIESCE)


@_tool("Draw text")
def acad_draw_text(text: Annotated[str, Field(min_length=1)], position: Point,
                   height: Annotated[float, Field(
                       ge=0, description="Text height in drawing units; 0 = automatic: "
                                         "2.5 mm on paper at plot_scale, e.g. 250 in a mm "
                                         "drawing at 1:100.")] = 0.0,
                   plot_scale: Annotated[int, Field(ge=1, le=10000)] = 100,
                   layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Place single-line text (insertion point = left baseline)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        h = float(height)
        if h <= 0:
            h = round(2.5 * plot_scale / _MM_PER_UNIT.get(_insunits(doc), 1.0), 6)
        ent = _create(doc, layer, lambda ms: ms.AddText(text, _pt(position), h))
        return {"drawing": name, "created": "text", "handle": str(ent.Handle),
                "text": text, "height": h, "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_text", quiesce=_QUIESCE)


@_tool("Draw arc")
def acad_draw_arc(center: Point, radius: Length,
                  start_angle: Annotated[float, Field(description="Degrees, CCW from east.")],
                  end_angle: Annotated[float, Field(description="Degrees, CCW from east.")],
                  layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Draw an arc counter-clockwise from start_angle to end_angle (degrees)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddArc(
            _pt(center), float(radius), math.radians(start_angle), math.radians(end_angle)))
        return {"drawing": name, "created": "arc", "handle": str(ent.Handle),
                "arc_length": round(float(ent.ArcLength), 6), "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_arc", quiesce=_QUIESCE)


@_tool("Draw rectangle")
def acad_draw_rectangle(corner1: Point, corner2: Point, layer: LayerName = "",
                        drawing: Drawing = "") -> dict[str, Any]:
    """Draw an axis-aligned rectangle as a closed polyline from two opposite corners."""
    x1, y1 = float(corner1[0]), float(corner1[1])
    x2, y2 = float(corner2[0]), float(corner2[1])

    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddLightWeightPolyline(
            _dbl_array([x1, y1, x2, y1, x2, y2, x1, y2])),
            finish=lambda e: setattr(e, "Closed", True))
        return {"drawing": name, "created": "rectangle", "handle": str(ent.Handle),
                "width": abs(x2 - x1), "height": abs(y2 - y1),
                "area": round(float(ent.Area), 6), "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_rectangle", quiesce=_QUIESCE)


@_tool("Draw ellipse")
def acad_draw_ellipse(center: Point,
                      major_axis: Annotated[Point, Field(
                          description="Vector from the centre to the major-axis endpoint.")],
                      radius_ratio: Annotated[float, Field(gt=0, le=1,
                                                           description="minor / major")],
                      layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Draw an ellipse from its centre, major-axis vector and minor/major ratio."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddEllipse(
            _pt(center), _pt(major_axis), float(radius_ratio)))
        return {"drawing": name, "created": "ellipse", "handle": str(ent.Handle),
                "layer": str(ent.Layer)}

    return _com(job, what="acad_draw_ellipse", quiesce=_QUIESCE)


@_tool("Add linear dimension")
def acad_add_linear_dimension(point1: Point, point2: Point, text_position: Point,
                              rotation: Annotated[float, Field(
                                  description="Degrees: 0 = horizontal, 90 = vertical.")] = 0.0,
                              layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Add a rotated linear dimension. It uses the current DIMSTYLE: ISO-25's
    2.5-unit text is invisible at 1:100 in a mm drawing unless DIMSCALE is 100."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddDimRotated(
            _pt(point1), _pt(point2), _pt(text_position), math.radians(rotation)))
        return {"drawing": name, "created": "linear_dimension", "handle": str(ent.Handle),
                "measurement": round(float(ent.Measurement), 6)}

    return _com(job, what="acad_add_linear_dimension", quiesce=_QUIESCE)


@_tool("Add aligned dimension")
def acad_add_aligned_dimension(point1: Point, point2: Point, text_position: Point,
                               layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Add an aligned dimension (parallel to the measured points). Uses the
    current DIMSTYLE (see acad_add_linear_dimension about DIMSCALE)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddDimAligned(
            _pt(point1), _pt(point2), _pt(text_position)))
        return {"drawing": name, "created": "aligned_dimension", "handle": str(ent.Handle),
                "measurement": round(float(ent.Measurement), 6)}

    return _com(job, what="acad_add_aligned_dimension", quiesce=_QUIESCE)


@_tool("Add hatch")
def acad_add_hatch(boundary_handles: Annotated[list[Handle], Field(
                       min_length=1, description="Closed boundary entities (closed "
                                                 "polylines, circles) in the same drawing.")],
                   pattern: Annotated[str, Field(
                       description="acad.pat name: ANSI31, SOLID, NET, AR-CONC, ...")] = "ANSI31",
                   scale: Annotated[float, Field(
                       gt=0, description="Pattern scale; ~100 for 1:100 in a mm drawing.")] = 1.0,
                   associative: bool = True, layer: LayerName = "",
                   drawing: Drawing = "") -> dict[str, Any]:
    """Hatch the area enclosed by one or more existing closed entities. A hatch
    that fails to build is deleted, not left empty in the drawing."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        bounds = [_ent(doc, name, h) for h in boundary_handles]
        if layer:
            _require_layer(doc, layer)
        hatch = doc.ModelSpace.AddHatch(0, pattern, bool(associative))  # 0 = predefined
        try:
            for b in bounds:
                hatch.AppendOuterLoop(_objs([b]))
            hatch.PatternScale = float(scale)
            hatch.Evaluate()
            if layer:
                hatch.Layer = layer
        except Exception:
            _safe_delete(hatch)
            raise
        return {"drawing": name, "created": "hatch", "handle": str(hatch.Handle),
                "pattern": pattern, "loops": len(boundary_handles),
                "area": round(float(hatch.Area), 6)}

    return _com(job, what="acad_add_hatch", quiesce=_QUIESCE)


# ---- layers -------------------------------------------------------------------


@_tool("List layers", ro=True, idempotent=True)
def acad_list_layers(drawing: Drawing = "") -> dict[str, Any]:
    """List all layers of a drawing with on/frozen/locked state and ACI colour."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        current = str(doc.ActiveLayer.Name)
        out = []
        for lyr in doc.Layers:
            try:
                color = int(lyr.Color)
            except ToolError:
                raise
            except Exception:  # noqa: BLE001 - TrueColor fallback
                color = int(lyr.TrueColor.ColorIndex)
            ln = str(lyr.Name)
            out.append({"name": ln, "on": bool(lyr.LayerOn), "frozen": bool(lyr.Freeze),
                        "locked": bool(lyr.Lock), "color": color, "active": ln == current})
        return {"drawing": name, "count": len(out), "layers": out}

    return _com(job, what="acad_list_layers", timeout=_T_READ, idempotent=True)


@_tool("Create layer", idempotent=True)
def acad_create_layer(name: Annotated[str, Field(min_length=1, max_length=255)],
                      color: Annotated[int, Field(ge=1, le=255, description=(
                          "ACI colour 1-255 (7 = white/black). Omit to leave an existing "
                          "layer's colour alone (new layers get 7)."))] | None = None,
                      activate: bool = False, drawing: Drawing = "") -> dict[str, Any]:
    """Create a layer, or fetch it if it already exists (its colour is changed
    only when `color` is given). Optionally make it current."""
    def job(app):
        doc, dn = _resolve_doc(app, drawing)
        existed = True
        try:
            lyr = doc.Layers.Item(name)
        except ToolError:
            raise
        except Exception as exc:  # noqa: BLE001
            if _classify(exc) in ("busy", "stale"):
                raise
            existed = False
            lyr = doc.Layers.Add(name)
        if color is not None or not existed:
            lyr.Color = int(color if color is not None else 7)
        if activate:
            doc.ActiveLayer = lyr
        return {"drawing": dn, "layer": str(lyr.Name), "existed": existed,
                "color": int(lyr.Color), "active": str(doc.ActiveLayer.Name) == str(lyr.Name)}

    return _com(job, what="acad_create_layer", quiesce=_QUIESCE)


@_tool("Set current layer", idempotent=True)
def acad_set_layer(name: Annotated[str, Field(min_length=1)],
                   drawing: Drawing = "") -> dict[str, Any]:
    """Make an existing layer current."""
    def job(app):
        doc, dn = _resolve_doc(app, drawing)
        _require_layer(doc, name)
        doc.ActiveLayer = doc.Layers.Item(name)
        return {"drawing": dn, "active_layer": str(doc.ActiveLayer.Name)}

    return _com(job, what="acad_set_layer", quiesce=_QUIESCE)


@_tool("Summarize entities", ro=True, idempotent=True)
def acad_summarize_entities(limit: Annotated[int, Field(
                                ge=0, le=5000, description="How many entities to describe "
                                                          "in detail; all are counted.")] = 200,
                            drawing: Drawing = "") -> dict[str, Any]:
    """Count model-space entities by type and describe the first `limit` (handle,
    layer, length/area/radius/text). Walks every entity over COM, so it is slow
    on big drawings; for a villa sheet with a DXF twin, dxf_info is far cheaper."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ms = doc.ModelSpace
        counts: dict[str, int] = {}
        sample = []
        for i, ent in enumerate(ms):
            kind = str(ent.ObjectName)
            counts[kind] = counts.get(kind, 0) + 1
            if i < limit:
                item = {"i": i, "type": kind, "handle": str(ent.Handle), "layer": str(ent.Layer)}
                if kind in _PROPS:
                    item.update(_read_props(ent, kind))
                sample.append(item)
        return {"drawing": name, "total": int(ms.Count), "by_type": counts, "sample": sample}

    return _com(job, what="acad_summarize_entities", timeout=180.0, idempotent=True)


# ---- escape hatch -------------------------------------------------------------

_DENY_TOKENS = {"SHELL", "STARTAPP", "NETLOAD", "APPLOAD", "ARX", "VBALOAD", "VBARUN",
                "-VBARUN", "VBAIDE", "QUIT", "EXIT", "CLOSEALL"}
_DENY_LISP = re.compile(r"\(\s*(?:startapp|load|arxload|vl-load-all|vl-registry-write|"
                        r"dos_\w+|command\s+\"[_.]*shell)", re.I)


def _denied(command: str) -> str | None:
    for tok in re.split(r"\s+", command):
        t = tok.strip().upper().lstrip("_.'")
        if t in _DENY_TOKENS or t.lstrip("-") in _DENY_TOKENS:
            return tok.strip()
    m = _DENY_LISP.search(command)
    return m.group(0) if m else None


@_tool("Send raw command (escape hatch)", destructive=True, open_world=True)
def acad_send_command(command: Annotated[str, Field(
                          min_length=1, description="Command-line input. Newline = Enter; "
                                                    "one is appended if missing. Example: "
                                                    "'_.ZOOM\\n_E'.")],
                      drawing: Drawing = "",
                      wait_s: Annotated[float, Field(
                          ge=1, le=600, description="How long to wait for the command to "
                                                    "finish.")] = 30.0) -> dict[str, Any]:
    """ESCAPE HATCH: type raw input at the AutoCAD command line. Use the typed
    tools whenever one exists.

    Waits for AutoCAD to be idle before sending and refuses if it is not. After
    sending, waits for it to be idle again and reports completed=False if the
    command is still at a prompt: then finish or cancel it (Esc in AutoCAD)
    before anything else -- a command stuck at a prompt makes COM reject every
    call. Command-line quirk: a SPACE is Enter, so names with spaces cannot be
    typed at prompts. SendCommand activates the target drawing. Commands that
    launch programs or load code (SHELL, STARTAPP, NETLOAD, APPLOAD, (load ...),
    QUIT, ...) are refused as a guardrail, not a security boundary.
    """
    # The gate sits on this TOOL only. Nothing in this server sends commands
    # through it; pipeline stages that need SendCommand (villa_3d_build) call
    # it in their own process, so the gate never blocks them.
    if not _env_is("ACAD_ALLOW_RAW_COMMAND", "1", "true"):
        raise _Refused("raw_command",
                       "Refused: acad_send_command is disabled. To enable it, set "
                       f"ACAD_ALLOW_RAW_COMMAND=1 {_RESTART}.")
    bad = _denied(command)
    if bad:
        raise ToolError(f"Refused: {bad!r} launches programs, loads code or quits AutoCAD. "
                        "Do that in AutoCAD itself.")
    cmd = command if command.endswith("\n") else command + "\n"

    def job(app):
        doc, name = _resolve_doc(app, drawing)
        idle, before = _wait_idle(app, min(15.0, wait_s))
        if not idle:
            raise _BusyError(f"AutoCAD is not idle ({before}); refusing to queue more "
                             "input. Finish or cancel the current command first.")
        was_active = _active_name(app)
        t0 = time.monotonic()
        doc.SendCommand(cmd)
        time.sleep(0.4)                      # let the queued input start executing
        done, after = _wait_idle(app, wait_s, need=2)
        out = {"drawing": name, "sent": cmd, "completed": done, "state_after": after,
               "seconds": round(time.monotonic() - t0, 2),
               "activated_drawing": was_active != name}
        if not done:
            out["hint"] = ("AutoCAD is still busy or at a prompt. Send the remaining input, "
                           "or press Esc in AutoCAD, before any other acad_* call.")
        return out

    return _com(job, what="acad_send_command", timeout=wait_s + 40.0)


@_tool("Zoom extents", idempotent=True)
def acad_zoom_extents(drawing: Drawing = "") -> dict[str, Any]:
    """Zoom the drawing's current viewport to its extents (activates the drawing:
    ZoomExtents is an application-level call on the active drawing)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        if _active_name(app) != name:
            doc.Activate()
        app.ZoomExtents()
        return {"drawing": name, "ok": True}

    return _com(job, what="acad_zoom_extents", quiesce=_QUIESCE, idempotent=True)


@_tool("Erase entity", destructive=True)
def acad_erase(handle: Handle, drawing: Drawing = "") -> dict[str, Any]:
    """Delete one entity by handle. Destructive; AutoCAD's own UNDO still works.
    `drawing` is required when more than one drawing is open."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        ent = _ent(doc, name, handle)
        kind, layer = str(ent.ObjectName), str(ent.Layer)
        ent.Delete()
        return {"drawing": name, "erased": handle, "was": kind, "layer": layer}

    return _com(job, what="acad_erase", quiesce=_QUIESCE)


# ---- plotting -----------------------------------------------------------------

_PDF_DEVICE = "DWG To PDF.pc3"
_A3 = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
_PLOT_TYPES = {"extents": 1, "layout": 5, "display": 0}     # acExtents/acLayout/acDisplay
_ROTATIONS = {0: 0, 90: 1, 180: 2, 270: 3}                   # ac0degrees...ac270degrees
_PLOT_PROPS = ("ConfigName", "CanonicalMediaName", "PlotType", "UseStandardScale",
               "StandardScale", "PaperUnits", "CenterPlot", "PlotRotation", "StyleSheet")
_MISSING = object()


def _plot_snapshot(lay) -> dict[str, Any]:
    snap: dict[str, Any] = {}
    for p in _PLOT_PROPS:
        v = _opt(lay, p, _MISSING)
        if v is not _MISSING:
            snap[p] = v
    with contextlib.suppress(Exception):
        snap["_custom"] = tuple(float(x) for x in lay.GetCustomScale())
    if snap.get("PlotType") == 4:
        with contextlib.suppress(Exception):
            snap["_window"] = lay.GetWindowToPlot()
    if snap.get("PlotType") == 3:
        with contextlib.suppress(Exception):
            snap["_view"] = str(lay.ViewToPlot)
    return snap


def _attempt(errors: list[str], label: str, fn) -> None:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - restore is best effort, reported
        errors.append(f"{label}: {_explain(exc)}")


def _plot_restore(lay, snap: dict[str, Any], errors: list[str]) -> None:
    """Put the layout's plot settings back, in the same dependency order they
    were set: the device first (RefreshPlotDeviceInfo resets media and scale)."""
    if "ConfigName" in snap:
        _attempt(errors, "ConfigName", lambda: setattr(lay, "ConfigName", snap["ConfigName"]))
        _attempt(errors, "RefreshPlotDeviceInfo", lambda: lay.RefreshPlotDeviceInfo())
    if "CanonicalMediaName" in snap:
        _attempt(errors, "CanonicalMediaName",
                 lambda: setattr(lay, "CanonicalMediaName", snap["CanonicalMediaName"]))
    if "PaperUnits" in snap:
        _attempt(errors, "PaperUnits", lambda: setattr(lay, "PaperUnits", snap["PaperUnits"]))
    if "_custom" in snap:
        _attempt(errors, "custom scale", lambda: lay.SetCustomScale(*snap["_custom"]))
    if "UseStandardScale" in snap:
        _attempt(errors, "UseStandardScale",
                 lambda: setattr(lay, "UseStandardScale", snap["UseStandardScale"]))
        if snap["UseStandardScale"] and "StandardScale" in snap:
            _attempt(errors, "StandardScale",
                     lambda: setattr(lay, "StandardScale", snap["StandardScale"]))
    if "_window" in snap:
        lo, hi = snap["_window"]
        _attempt(errors, "window", lambda: lay.SetWindowToPlot(
            _dbl_array(list(lo)[:2]), _dbl_array(list(hi)[:2])))
    if "_view" in snap:
        _attempt(errors, "view", lambda: setattr(lay, "ViewToPlot", snap["_view"]))
    for p in ("PlotType", "CenterPlot", "PlotRotation", "StyleSheet"):
        if p in snap:
            _attempt(errors, p, lambda p=p: setattr(lay, p, snap[p]))


def _layout_by_name(doc, name: str):
    for lay in doc.Layouts:
        if str(lay.Name).lower() == name.lower():
            return lay
    return None


def _pdf_pages(path: str) -> int | None:
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore[no-redef]
        except ImportError:
            return None
    try:
        with pymupdf.open(path) as d:
            return int(d.page_count)
    except Exception:  # noqa: BLE001
        return None


@_tool("Plot layout to PDF", idempotent=True)
def acad_export_pdf(path: Annotated[str, Field(description="Output .pdf path (absolute).")],
                    drawing: Drawing = "",
                    layout: Annotated[str, Field(description="'Model' or a paper-space "
                                                             "layout name.")] = "Model",
                    media: Annotated[str, Field(
                        description="Canonical media name of 'DWG To PDF.pc3'.")] = _A3,
                    plot_type: Annotated[Literal["extents", "layout", "display"], Field(
                        description="extents = everything drawn (right for model space); "
                                    "layout = the paper-space sheet; display = what is on "
                                    "screen.")] = "extents",
                    scale: Annotated[str, Field(
                        pattern=r"^(fit|\s*1\s*:\s*\d+(\.\d+)?\s*)$",
                        description="'fit' or '1:N' (paper mm : drawing units, e.g. 1:100 "
                                    "for a mm drawing).")] = "fit",
                    style_sheet: Annotated[str, Field(
                        description="Plot style table (.ctb); empty = leave as is. "
                                    "PLAN-MONO.ctb maps every colour to black at its "
                                    "lineweight.")] = "PLAN-MONO.ctb",
                    rotation: Literal[0, 90, 180, 270] = 0,
                    overwrite: bool = True) -> dict[str, Any]:
    """Plot one layout of a drawing to PDF with 'DWG To PDF.pc3'.

    Uses the project's proven sequence (plot_sheets.py): ConfigName, THEN
    RefreshPlotDeviceInfo (it resets media and scale, so it must come first),
    then media, plot type, scale, centring, rotation, style sheet;
    BACKGROUNDPLOT=0 so the file exists on return. Afterwards every changed
    setting is put back -- the layout's plot settings, BACKGROUNDPLOT,
    QuietErrorMode, the active layout and the active drawing -- and nothing is
    saved. AutoCAD may still flag the drawing as modified (DBMOD) after the
    restore; both values are returned. Returns file size and page count.
    """
    path = os.path.abspath(path)
    if not path.lower().endswith(".pdf"):
        path += ".pdf"
    _check_write_path(path, "acad_export_pdf")
    m = None if scale.strip() == "fit" else re.fullmatch(r"\s*1\s*:\s*(\d+(?:\.\d+)?)\s*", scale)
    if os.path.exists(path):
        if not overwrite:
            raise ToolError(f"{path} exists; pass overwrite=True.")
        with open(path, "r+b"):   # PermissionError now, not after the plot, if a viewer holds it
            pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Plot to a temporary name and swap it in, so a failed plot never costs the
    # previous PDF and 'exists' afterwards proves THIS plot wrote the file.
    tmp = path[:-4] + ".~plot.pdf"
    with contextlib.suppress(FileNotFoundError):
        os.remove(tmp)

    def job(app):
        doc, name = _resolve_doc(app, drawing)
        target = _layout_by_name(doc, layout)
        if target is None:
            raise ToolError(f"No layout {layout!r} in {name}; layouts: "
                            f"{[str(x.Name) for x in doc.Layouts]}")
        target_name = str(target.Name)
        prev_active = _active_name(app)
        prev_layout = str(doc.ActiveLayout.Name)
        dbmod_before = int(doc.GetVariable("DBMOD"))
        bg_before = doc.GetVariable("BACKGROUNDPLOT")
        errors: list[str] = []
        warnings: list[str] = []
        lay = snap = plot = None
        quiet_before = None
        ok = False
        used: dict[str, Any] = {}
        try:
            if prev_active != name:
                doc.Activate()               # plot_sheets.py plots the active drawing
            if prev_layout.lower() != target_name.lower():
                doc.ActiveLayout = target
            lay = doc.ActiveLayout
            snap = _plot_snapshot(lay)
            lay.ConfigName = _PDF_DEVICE
            lay.RefreshPlotDeviceInfo()      # resets media/scale -> must precede them
            medias = [str(x) for x in (lay.GetCanonicalMediaNames() or ())]
            if medias and media not in medias:
                near = [x for x in medias if "A3" in x or "A1" in x][:8]
                raise ToolError(f"Media {media!r} is not offered by {_PDF_DEVICE}. "
                                f"Some that are: {near or medias[:8]}")
            lay.CanonicalMediaName = media
            lay.PlotType = _PLOT_TYPES[plot_type]
            if m is None:
                lay.UseStandardScale = True
                lay.StandardScale = 0        # acScaleToFit
            else:
                lay.PaperUnits = 1           # acMillimeters
                lay.UseStandardScale = False
                lay.SetCustomScale(1.0, float(m.group(1)))
            lay.CenterPlot = plot_type != "layout"
            lay.PlotRotation = _ROTATIONS[int(rotation)]
            if style_sheet:
                # Without it ACI colours print literally: pale yellow room names,
                # near-invisible light-grey furniture.
                try:
                    lay.StyleSheet = style_sheet
                except ToolError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    if _classify(exc) in ("busy", "stale"):
                        raise
                    warnings.append(f"style sheet {style_sheet!r} not applied: {_explain(exc)}")
            doc.SetVariable("BACKGROUNDPLOT", 0)
            plot = doc.Plot
            with contextlib.suppress(Exception):
                quiet_before = bool(plot.QuietErrorMode)
                plot.QuietErrorMode = True    # errors must not raise modal dialogs
            ok = bool(plot.PlotToFile(tmp, _PDF_DEVICE))
            used = {"style_sheet": str(_opt(lay, "StyleSheet", "")),
                    "media": str(_opt(lay, "CanonicalMediaName", ""))}
        finally:
            if plot is not None and quiet_before is not None:
                _attempt(errors, "QuietErrorMode",
                         lambda: setattr(plot, "QuietErrorMode", quiet_before))
            if lay is not None and snap is not None:
                _plot_restore(lay, snap, errors)
            _attempt(errors, "BACKGROUNDPLOT",
                     lambda: doc.SetVariable("BACKGROUNDPLOT", bg_before))
            if prev_layout.lower() != target_name.lower():
                _attempt(errors, "ActiveLayout",
                         lambda: setattr(doc, "ActiveLayout", _layout_by_name(doc, prev_layout)))
            if prev_active and prev_active != name:
                _attempt(errors, "active drawing",
                         lambda: _resolve_doc(app, prev_active)[0].Activate())
        dbmod_after = None
        with contextlib.suppress(Exception):
            dbmod_after = int(doc.GetVariable("DBMOD"))
        return {"drawing": name, "layout": target_name, "plotted": ok, "used": used,
                "restore_errors": errors, "warnings": warnings,
                "dbmod_before": dbmod_before, "dbmod_after": dbmod_after}

    res = _com(job, what="acad_export_pdf", timeout=300.0, quiesce=_QUIESCE)
    if not os.path.exists(tmp):
        raise ToolError(f"PlotToFile returned {res['plotted']} but no PDF was written for "
                        f"{path}. Settings were restored (errors: {res['restore_errors']}).")
    os.replace(tmp, path)
    res.update(path=path, bytes=os.path.getsize(path), pages=_pdf_pages(path),
               media=media, plot_type=plot_type, scale=scale.strip(),
               restored=not res["restore_errors"])
    return res


# ---- more geometry ----------------------------------------------------------------


@_tool("List block definitions", ro=True, idempotent=True)
def acad_list_blocks(drawing: Drawing = "") -> dict[str, Any]:
    """List block definitions in a drawing (skips *Model_Space, *Paper_Space and
    anonymous blocks), with entity count, xref and dynamic flags, and the
    drawing's units (INSUNITS)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        units = _insunits(doc)
        out = []
        for blk in doc.Blocks:
            n = str(blk.Name)
            if n.startswith("*"):
                continue
            out.append({"name": n, "entities": int(blk.Count),
                        "is_xref": bool(_opt(blk, "IsXRef", False)),
                        "is_dynamic": bool(_opt(blk, "IsDynamicBlock", False))})
        return {"drawing": name, "insunits": units, "units": _UNITS.get(units, f"code {units}"),
                "count": len(out), "blocks": out}

    return _com(job, what="acad_list_blocks", timeout=_T_READ, idempotent=True)


@_tool("Insert block")
def acad_insert_block(name: Annotated[str, Field(
                          description="A block defined in the drawing, or a .dwg path.")],
                      position: Point,
                      scale: Annotated[float, Field(gt=0)] = 1.0,
                      rotation: Annotated[float, Field(description="Degrees CCW.")] = 0.0,
                      footprint: Annotated[list[float], Field(
                          min_length=4, max_length=4,
                          description="Optional [x0, y0, x1, y1] (drawing units). If given, "
                                      "the block is inserted, MEASURED, scaled uniformly to fit "
                                      "and moved so its bounding box starts at (x0, y0); "
                                      "`position` and `scale` are then ignored.")] | None = None,
                      layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Insert a block reference and return its handle and final bounding box.
    With `footprint`, use the villa's insert-measure-scale-move method: AutoCAD's
    own unit conversion on insert is not consistent between drawings (one came
    in 25.4x oversize), so the result is measured rather than trusted."""
    if (name.lower().endswith(".dwg") or os.sep in name) and not os.path.exists(name):
        raise FileNotFoundError(name)

    def job(app):
        doc, dn = _resolve_doc(app, drawing)
        if layer:
            _require_layer(doc, layer)
        ms = doc.ModelSpace
        if footprint is None:
            ref = ms.InsertBlock(_pt(position), name, float(scale), float(scale),
                                 float(scale), math.radians(rotation))
        else:
            ref = ms.InsertBlock(_pt([0.0, 0.0]), name, 1.0, 1.0, 1.0, math.radians(rotation))
        try:
            if footprint is not None:
                x0, y0, x1, y1 = (float(v) for v in footprint)
                lo, hi = ref.GetBoundingBox()
                aw, ad = hi[0] - lo[0], hi[1] - lo[1]
                if aw > 1e-6 and ad > 1e-6:
                    k = min((x1 - x0) / aw, (y1 - y0) / ad)
                    if abs(k - 1.0) > 1e-4:
                        ref.ScaleEntity(_pt([0.0, 0.0]), k)
                lo, hi = ref.GetBoundingBox()
                ref.Move(_pt([lo[0], lo[1]]), _pt([x0, y0]))
            if layer:
                ref.Layer = layer
        except Exception:
            _safe_delete(ref)
            raise
        return {"drawing": dn, "inserted": name, "handle": str(ref.Handle),
                "block": str(_opt(ref, "EffectiveName", name)), "bbox": _bbox(ref),
                "layer": str(ref.Layer)}

    return _com(job, what="acad_insert_block", quiesce=_QUIESCE)


# ---- editing / transforms ------------------------------------------------------


@_tool("Move entity", destructive=True)
def acad_move(handle: Handle, from_point: Point, to_point: Point,
              drawing: Drawing = "") -> dict[str, Any]:
    """Move an entity by the vector from_point -> to_point (drawing units)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        _ent(doc, name, handle).Move(_pt(from_point), _pt(to_point))
        return {"drawing": name, "moved": handle}

    return _com(job, what="acad_move", quiesce=_QUIESCE)


@_tool("Copy entity")
def acad_copy_entity(handle: Handle, from_point: Point, to_point: Point,
                     drawing: Drawing = "") -> dict[str, Any]:
    """Copy an entity and offset the copy by from_point -> to_point."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        new = _ent(doc, name, handle).Copy()
        try:
            new.Move(_pt(from_point), _pt(to_point))
        except Exception:
            _safe_delete(new)
            raise
        return {"drawing": name, "source": handle, "copy_handle": str(new.Handle)}

    return _com(job, what="acad_copy_entity", quiesce=_QUIESCE)


@_tool("Rotate entity", destructive=True)
def acad_rotate(handle: Handle, base_point: Point,
                angle: Annotated[float, Field(description="Degrees CCW.")],
                drawing: Drawing = "") -> dict[str, Any]:
    """Rotate an entity about a base point."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        _ent(doc, name, handle).Rotate(_pt(base_point), math.radians(angle))
        return {"drawing": name, "rotated": handle, "degrees": angle}

    return _com(job, what="acad_rotate", quiesce=_QUIESCE)


@_tool("Scale entity", destructive=True)
def acad_scale(handle: Handle, base_point: Point,
               factor: Annotated[float, Field(gt=0)], drawing: Drawing = "") -> dict[str, Any]:
    """Uniformly scale an entity about a base point."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        _ent(doc, name, handle).ScaleEntity(_pt(base_point), float(factor))
        return {"drawing": name, "scaled": handle, "factor": factor}

    return _com(job, what="acad_scale", quiesce=_QUIESCE)


@_tool("Mirror entity", destructive=True)
def acad_mirror(handle: Handle, point1: Point, point2: Point,
                delete_original: bool = False, drawing: Drawing = "") -> dict[str, Any]:
    """Mirror an entity across the line through point1 and point2 (optionally
    deleting the original)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        e = _ent(doc, name, handle)
        new = e.Mirror(_pt(point1), _pt(point2))
        if delete_original:
            e.Delete()
        return {"drawing": name, "source": handle, "mirror_handle": str(new.Handle),
                "original_deleted": bool(delete_original)}

    return _com(job, what="acad_mirror", quiesce=_QUIESCE)


@_tool("Offset curve")
def acad_offset(handle: Handle,
                distance: Annotated[float, Field(description="Drawing units; negative "
                                                             "offsets to the other side.")],
                drawing: Drawing = "") -> dict[str, Any]:
    """Offset a curve (line, arc, circle, polyline) by a distance."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        result = _ent(doc, name, handle).Offset(float(distance))
        return {"drawing": name, "source": handle, "distance": distance,
                "new_handles": [str(o.Handle) for o in result]}

    return _com(job, what="acad_offset", quiesce=_QUIESCE)


@_tool("Measure entity", ro=True, idempotent=True)
def acad_measure_entity(handle: Handle, drawing: Drawing = "") -> dict[str, Any]:
    """Report an entity's type, layer, bounding box and the geometric properties
    its type has (length, area, radius, volume, measurement, text, block name,
    rotation in degrees)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        e = _ent(doc, name, handle)
        kind = str(e.ObjectName)
        out: dict[str, Any] = {"drawing": name, "handle": handle, "type": kind,
                               "layer": str(e.Layer), "bbox": _bbox(e)}
        out.update(_read_props(e, kind))
        return out

    return _com(job, what="acad_measure_entity", timeout=_T_READ, idempotent=True)


# ---- 3D solids --------------------------------------------------------------------


@_tool("3D box")
def acad_3d_box(center: Annotated[Point, Field(description="CENTRE of the box (not its "
                                                           "base): base z = centre z - h/2.")],
                length: Length, width: Length, height: Length,
                layer: LayerName = "", drawing: Drawing = "") -> dict[str, Any]:
    """Create a 3D solid box centred on `center` (x = length, y = width, z = height)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddBox(
            _pt(center), float(length), float(width), float(height)))
        return {"drawing": name, "created": "box", "handle": str(ent.Handle),
                "volume": round(float(ent.Volume), 6)}

    return _com(job, what="acad_3d_box", quiesce=_QUIESCE)


@_tool("3D cylinder")
def acad_3d_cylinder(center: Annotated[Point, Field(description="CENTRE of the cylinder: "
                                                                "base z = centre z - h/2.")],
                     radius: Length, height: Length, layer: LayerName = "",
                     drawing: Drawing = "") -> dict[str, Any]:
    """Create a 3D solid cylinder (axis along Z) centred on `center`."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddCylinder(
            _pt(center), float(radius), float(height)))
        return {"drawing": name, "created": "cylinder", "handle": str(ent.Handle),
                "volume": round(float(ent.Volume), 6)}

    return _com(job, what="acad_3d_cylinder", quiesce=_QUIESCE)


@_tool("3D sphere")
def acad_3d_sphere(center: Point, radius: Length, layer: LayerName = "",
                   drawing: Drawing = "") -> dict[str, Any]:
    """Create a 3D solid sphere (the villa's probe primitive)."""
    def job(app):
        doc, name = _resolve_doc(app, drawing)
        ent = _create(doc, layer, lambda ms: ms.AddSphere(_pt(center), float(radius)))
        return {"drawing": name, "created": "sphere", "handle": str(ent.Handle),
                "volume": round(float(ent.Volume), 6)}

    return _com(job, what="acad_3d_sphere", quiesce=_QUIESCE)


@_tool("3D boolean", destructive=True)
def acad_3d_boolean(handle_a: Handle, handle_b: Handle,
                    operation: Literal["union", "subtract", "intersect"] = "union",
                    drawing: Drawing = "") -> dict[str, Any]:
    """Combine two 3D solids. The result stays in solid A; solid B is CONSUMED."""
    ops = {"union": 0, "intersect": 1, "subtract": 2}

    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=True)
        a = _ent(doc, name, handle_a)
        b = _ent(doc, name, handle_b)
        a.Boolean(ops[operation], b)
        return {"drawing": name, "result_handle": handle_a, "consumed": handle_b,
                "operation": operation, "volume": round(float(a.Volume), 6)}

    return _com(job, what="acad_3d_boolean", quiesce=_QUIESCE)


# ---- housekeeping -------------------------------------------------------------------


def _table_counts(doc) -> dict[str, int]:
    out = {}
    for key, coll in (("blocks", "Blocks"), ("layers", "Layers"), ("linetypes", "Linetypes"),
                      ("text_styles", "TextStyles"), ("dim_styles", "DimStyles")):
        with contextlib.suppress(Exception):
            out[key] = int(getattr(doc, coll).Count)
    return out


def _user_blocks(doc) -> list[str]:
    out = []
    for b in doc.Blocks:
        n = str(b.Name)
        if n.startswith("*") or bool(_opt(b, "IsXRef", False)) or bool(_opt(b, "IsLayout", False)):
            continue
        out.append(n)
    return out


@_tool("Purge and audit", destructive=True)
def acad_purge_and_audit(drawing: Drawing = "", purge: bool = True, audit: bool = True,
                         dry_run: Annotated[bool, Field(
                             description="True (default) only reports; False really "
                                         "purges/audits.")] = True,
                         max_entities: Annotated[int, Field(ge=1000, le=500000)] = 100000
                         ) -> dict[str, Any]:
    """PurgeAll (remove unreferenced definitions) and/or AUDIT with fixes.

    DRY RUN BY DEFAULT: lists block definitions that nothing references (model
    space, paper space or another block) -- the ones PurgeAll would remove --
    plus table sizes. PurgeAll also drops unused layers, linetypes, styles and
    AEC styles, which the dry run does not enumerate. A real run needs
    `drawing` when several are open, is not saved, and reports what went.
    """
    def job(app):
        doc, name = _resolve_doc(app, drawing, explicit=not dry_run)
        counts = _table_counts(doc)
        if dry_run:
            defs = _user_blocks(doc)
            refs: set[str] = set()
            scanned, complete = 0, True
            for b in doc.Blocks:
                if bool(_opt(b, "IsXRef", False)):
                    continue
                for e in b:
                    scanned += 1
                    if scanned > max_entities:
                        complete = False
                        break
                    if "BlockReference" in str(e.ObjectName) or "MInsert" in str(e.ObjectName):
                        refs.add(str(e.Name))
                        en = _opt(e, "EffectiveName")
                        if en:
                            refs.add(str(en))
                if not complete:
                    break
            return {"drawing": name, "dry_run": True,
                    "would_run": [s for s, f in (("purge", purge), ("audit", audit)) if f],
                    "unreferenced_blocks": sorted(set(defs) - refs) if purge else [],
                    "entities_scanned": scanned, "scan_complete": complete,
                    "table_counts": counts,
                    "note": "Pass dry_run=False to run. PurgeAll may also remove unused "
                            "layers, linetypes, text/dim styles and AEC styles."}
        before = set(_user_blocks(doc))
        ran = []
        if purge:
            doc.PurgeAll()
            ran.append("purge")
        if audit:
            doc.AuditInfo(True)              # True = fix errors found
            ran.append("audit")
        after = set(_user_blocks(doc))
        return {"drawing": name, "dry_run": False, "ran": ran,
                "removed_blocks": sorted(before - after), "table_counts_before": counts,
                "table_counts_after": _table_counts(doc),
                "note": "Not saved: acad_save to keep it, or UNDO in AutoCAD."}

    return _com(job, what="acad_purge_and_audit", timeout=300.0,
                idempotent=dry_run, quiesce=_QUIESCE)


# ---- screenshot -----------------------------------------------------------------------


def _find_acad_windows() -> list[tuple[int, str]]:
    """AutoCAD main frames (class AfxMDIFrame*), AutoCAD-titled first. No COM."""
    import win32gui

    found: list[tuple[int, str]] = []

    def cb(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd) and \
                    win32gui.GetClassName(hwnd).startswith("AfxMDIFrame"):
                found.append((hwnd, win32gui.GetWindowText(hwnd)))
        except Exception:  # noqa: BLE001
            pass
        return True

    win32gui.EnumWindows(cb, None)
    found.sort(key=lambda t: "autocad" not in t[1].lower())
    return found


def _capture_window(hwnd: int):
    """PrintWindow(PW_RENDERFULLCONTENT) so an occluded window still captures;
    falls back to a screen copy if that yields nothing or the window is hung."""
    import ctypes

    import win32gui
    import win32ui
    from PIL import Image as PILImage
    from PIL import ImageGrab

    user32 = ctypes.windll.user32
    with contextlib.suppress(Exception):      # real pixels on a scaled display
        user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
    if win32gui.IsIconic(hwnd):
        raise ToolError("The AutoCAD window is minimised; restore it and retry.")
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    if w <= 0 or h <= 0:
        raise ToolError("The AutoCAD window has no visible area.")
    img = None
    method = None
    if not user32.IsHungAppWindow(hwnd):
        hdc = win32gui.GetWindowDC(hwnd)
        mfc = win32ui.CreateDCFromHandle(hdc)
        mem = mfc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        try:
            bmp.CreateCompatibleBitmap(mfc, w, h)
            mem.SelectObject(bmp)
            if user32.PrintWindow(hwnd, mem.GetSafeHdc(), 2):
                bits = bmp.GetBitmapBits(True)
                img = PILImage.frombuffer("RGB", (w, h), bits, "raw", "BGRX", 0, 1).copy()
                if img.getbbox() is None:     # all black: nothing was rendered
                    img = None
                else:
                    method = "PrintWindow"
        finally:
            with contextlib.suppress(Exception):
                win32gui.DeleteObject(bmp.GetHandle())
            with contextlib.suppress(Exception):
                mem.DeleteDC()
            with contextlib.suppress(Exception):
                mfc.DeleteDC()
            with contextlib.suppress(Exception):
                win32gui.ReleaseDC(hwnd, hdc)
    if img is None:
        img = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
        method = "screen copy (whatever is visible where the window is)"
    return img, method


@_tool("Screenshot AutoCAD", idempotent=True)
def acad_screenshot(path: Annotated[str, Field(description="Where to save the PNG "
                                                           "(absolute path).")],
                    drawing: Annotated[str, Field(
                        description="Optional: activate this drawing first (uses COM). "
                                    "Empty = capture as is, without COM -- works even "
                                    "while AutoCAD is wedged by a dialog.")] = "",
                    include_image: bool = True,
                    max_inline_width: Annotated[int, Field(ge=320, le=3840)] = 1600
                    ) -> list[Image | str]:
    """Capture the AutoCAD main window to a PNG and return it inline (downscaled
    to max_inline_width) plus a JSON line with path, size and capture method.
    Use it for visual QA, or to see which dialog is blocking AutoCAD."""
    path = _png_path(path)
    _check_write_path(path, "acad_screenshot")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    hwnd, acted = None, None
    if drawing:
        def job(app):
            doc, name = _resolve_doc(app, drawing)
            if _active_name(app) != name:
                doc.Activate()
            return int(app.HWND), name

        hwnd, acted = _com(job, what="acad_screenshot", timeout=_T_READ, idempotent=True)
        time.sleep(0.8)                      # let the newly active tab repaint
    wins = _find_acad_windows()
    if hwnd is None:
        if not wins:
            raise ToolError("No AutoCAD main window found (is AutoCAD running and not "
                            "minimised to the tray?).")
        hwnd = wins[0][0]
    title = next((t for hw, t in wins if hw == hwnd), "")
    img, method = _capture_window(hwnd)
    img.save(path, "PNG")
    meta = {"path": path, "width": img.width, "height": img.height, "method": method,
            "window_title": title, "drawing": acted}
    out: list[Image | str] = []
    if include_image:
        thumb = img.copy()
        if thumb.width > max_inline_width:
            thumb = thumb.resize((max_inline_width,
                                  round(thumb.height * max_inline_width / thumb.width)))
        buf = io.BytesIO()
        thumb.save(buf, "PNG")
        out.append(Image(data=buf.getvalue(), format="png"))
        meta["inline_width"] = thumb.width
    out.append(json.dumps(meta))
    return out


# ==========================================================================
# Villa pipeline
# ==========================================================================

# One table drives villa_run AND villa_status. Paths in outputs/inputs are
# relative to the design's output folder (_Project.out); scripts are found in
# the design's folder first, then in this pipeline folder, as run_project.py
# finds them. Sheet files follow the DESIGN's sheet list (_plan_sheets), never
# a fixed set:
#   {sheet}  the site plan A101 and every plan sheet   (A101, A102, A103, ...)
#   {plan}   the plan sheets only                       (A102, A103, ...)
_STAGES: dict[str, dict[str, Any]] = {
    "plans": {
        "scripts": ["villa_cad.py"], "timeout": 600,
        "outputs": ["VILLA_{sheet}.dxf", "furniture_manifest.json"],
        "about": "technical sheets: site plan A-101 + one plan per floor of the design's "
                 "sheet list, and the furniture manifest (ezdxf, offline)"},
    "colour": {
        "scripts": ["villa_colour.py"], "timeout": 600,
        "outputs": ["VILLA_{sheet}P.dxf"],
        "about": "coloured presentation sheets: A-101P + one per plan sheet (offline)"},
    "elevations": {
        "scripts": ["villa_elevations.py"], "checks": True, "occ": True, "timeout": 1800,
        "outputs": [f"VILLA_{n}.{ext}" for n in ("A201", "A202", "A203", "A204", "A301")
                    for ext in ("dxf", "png")],
        "about": "elevations A-201..A-204 and section A-301, hidden-line projections of the "
                 "render model; verdict from its 'N/N checks passed' line (offline)"},
    "gltf": {
        "scripts": ["villa_gltf.py"], "occ": True, "timeout": 1800,
        "outputs": ["render/villa.glb", "render/villa.step", "render/groups.json",
                    "render/villa_*.glb"],
        "about": "build123d render model per material group, probe-verified (offline)"},
    "build3d": {
        "scripts": ["villa_3d_build.py"], "com": True, "timeout": 1800,
        "outputs": ["VILLA_3D_MODEL.dwg"],
        "about": "AutoCAD 3D solids model (COM)"},
    "verify3d": {
        "scripts": ["villa_3d_verify.py", "villa_pool_check.py", "villa_window_check.py"],
        "com": True, "verify": True, "timeout": 1800,
        "inputs": ["VILLA_3D_MODEL.dwg"],
        "about": "probe the AutoCAD 3D model: rooms void, fabric solid, pool, openings (COM)"},
    "load": {
        "scripts": ["villa_load.py"], "com": True, "timeout": 1800,
        "outputs": ["VILLA_{sheet}.dwg", "VILLA_{sheet}P.dwg"],
        "inputs": ["VILLA_{sheet}.dxf", "VILLA_{sheet}P.dxf", "furniture_manifest.json"],
        "about": "load DXF sheets into AutoCAD, insert real ACA blocks, save DWG (COM)"},
    "verify": {
        "scripts": ["villa_verify.py"], "com": True, "verify": True, "timeout": 900,
        "inputs": ["VILLA_{plan}.dwg", "furniture_manifest.json"],
        "about": "check every inserted block against the validated plan (COM)"},
    "render": {
        "scripts": ["villa_blender.py"], "blender": True, "timeout": 3600,
        # one PNG per RENDER_VIEWS key (villa_blender names them villa_<view>.png),
        # so a project's own views count -- not the villa's fixed five
        "outputs": ["render/out/villa_*.png", "render/out/render_log.json",
                    "render/villa_render.blend", "render/twinmotion/villa_twinmotion.fbx",
                    "render/twinmotion/villa_twinmotion.glb"],
        "inputs": ["render/groups.json", "render/villa_*.glb"],
        "about": "Blender Cycles renders + Twinmotion FBX/GLB export"},
}
_STAGE_ORDER = list(_STAGES)
Stage = Literal["plans", "colour", "elevations", "gltf", "build3d", "verify3d", "load",
                "verify", "render"]
_DATA_DEPS = {"villa_furniture_spec.py": ["block_catalog.json"]}   # read at import
_TOL = 1.0   # s of mtime slack before an output counts as older than a source

_FAIL_MARKS = [re.compile(p, re.I | re.M) for p in (
    r"^\s*gave up:", r"FAILURE\(S\)", r"OPENINGS ABOVE ARE NOT CUT", r"^\s*PROBLEMS ABOVE",
    # FAILED is matched in CAPITALS only: the scripts shout it, while Blender's
    # harmless "HIPEW initialization failed" (no AMD GPU) marked a perfect
    # render as failed on its first live run.
    r"^\s*MISMATCHES ABOVE", r"Traceback \(most recent call last\)", r"(?-i:\bFAILED\b)",
    r"^\s*FAIL\s", r"model does not match the design", r"import does not match the model")]
_UNVERIFIED_MARKS = [re.compile(r"probe failed", re.I)]
_VERIFIED_MARK = re.compile(r"^\s*VERIFIED:", re.M)
# villa_elevations' closing line: "  37/37 checks passed   212s   -> <folder>"
_CHECKS_MARK = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s+checks passed\b.*$", re.M | re.I)
_RENDER_FLAGS = {"--samples": r"\d{1,5}", "--res": r"\d{2,5}x\d{2,5}",
                 "--views": r"[a-z_]+(,[a-z_]+)*", "--hdri": r"[\w.-]+",
                 "--sun-az": r"-?\d+(\.\d+)?", "--no-render": None}
_VILLA_LOCK = threading.Lock()
_RUNS_LOCK = threading.Lock()

ProjectArg = Annotated[str | None, Field(description=(
    "Which design. Omit (None) for the villa. Otherwise a project name under "
    "projects\\ (e.g. 'fairway'), or an absolute folder holding villa_design.py."))]


# --------------------------------------------------------------------------
# Projects: which design a pipeline tool works on
# --------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class _Project:
    """One design: the villa (this folder's villa_design.py) or a project."""
    name: str            # 'villa', or the project folder's name
    folder: Path         # the folder holding its villa_design.py
    out: Path            # its deliverables folder (what the scripts get as VILLA_OUT)
    out_from: str        # what chose `out`: VILLA_OUT / VILLA_DIR / OUT_NAME / default
    is_villa: bool
    key: str = ""        # run-record prefix: '' for the villa, else name or folder

    @property
    def design_file(self) -> Path:
        return self.folder / "villa_design.py"

    @property
    def search(self) -> tuple[Path, ...]:
        """Where its modules are found: the design's folder first, then the pipeline."""
        return (self.folder,) if self.is_villa else (self.folder, PROJECT)

    @property
    def arg(self) -> str | None:
        """The `project` argument that names this design again."""
        return None if self.is_villa else (self.name if self.key == self.name else str(self.folder))

    def run_key(self, stage: str) -> str:
        """villa_runs.json key: the bare stage for the villa (as before), else per design."""
        return stage if self.is_villa else f"{self.key}:{stage}"

    def info(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "folder": str(self.folder),
                             "design_file": str(self.design_file),
                             "out_dir": str(self.out), "out_dir_from": self.out_from}
        title = _design_const(self.folder, "PROJECT_TITLE")
        if title:
            d["title"] = title
        return d


_PROJECT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}")
_FOLDER_NAME = re.compile(r"[\w][\w .-]{0,63}")


def _design_const(folder: Path, name: str) -> str | None:
    """A top-level string constant of a design, read as TEXT the way
    run_project.out_name() reads OUT_NAME (importing the design here would
    cache it)."""
    try:
        src = (folder / "villa_design.py").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(rf'^{name}\s*=\s*["\']([^"\']+)["\']', src, re.M)
    return m.group(1) if m else None


def _out_for(folder: Path, is_villa: bool, env: Any) -> tuple[Path, str]:
    """A design's deliverables folder, and what chose it.

    VILLA_OUT (the variable every script reads) wins for any design. VILLA_DIR
    names the VILLA's folder only -- honoured for the villa, ignored for a
    project, so a project can never write into the villa's issued set. Then
    Desktop\\<OUT_NAME> when the design declares one, else Desktop\\Villa (the
    villa) or Desktop\\<Folder name> (a project), as run_project.py does."""
    if env.get("VILLA_OUT"):
        return Path(env["VILLA_OUT"]), "VILLA_OUT"
    if is_villa and env.get("VILLA_DIR"):
        return Path(env["VILLA_DIR"]), "VILLA_DIR"
    name = _design_const(folder, "OUT_NAME")
    if name:
        if not _FOLDER_NAME.fullmatch(name) or set(name) <= {".", " "}:
            raise ToolError(f"{folder / 'villa_design.py'}: OUT_NAME {name!r} is not a plain "
                            "folder name (it is a folder on the Desktop).")
        return DESKTOP / name, "OUT_NAME"
    return DESKTOP / ("Villa" if is_villa else folder.name.capitalize()), "default"


def _available_projects() -> list[str]:
    try:
        return sorted(d.name for d in PROJECTS.iterdir() if (d / "villa_design.py").is_file())
    except OSError:
        return []


def _project(project: str | None, env: Any = None) -> _Project:
    """Resolve a pipeline tool's `project` argument.

      None / blank      the villa: this folder's own villa_design.py;
      'fairway'         projects\\fairway (a plain name);
      'projects\\x'      a relative path: resolved under the pipeline folder and
                        refused if it lands anywhere else;
      'C:\\...\\x'        an explicit absolute folder (or its villa_design.py).

    The folder must hold villa_design.py. '.'/'..' components, UNC/device paths
    and drive- or root-relative paths are refused, and a relative path that
    resolves (symlinks included) outside the pipeline folder is refused."""
    env = os.environ if env is None else env

    def villa() -> _Project:
        out, how = _out_for(PROJECT, True, env)
        return _Project("villa", PROJECT, out, how, True)

    if project is None or not str(project).strip():
        return villa()
    raw = str(project).strip()

    def bad(why: str) -> ToolError:
        avail = ", ".join(_available_projects()) or "none"
        return ToolError(f"project {raw!r}: {why}. Projects under {PROJECTS}: {avail}; or pass "
                         "an absolute folder holding villa_design.py; omit project for the villa.")

    if "\x00" in raw or any(c in raw for c in '<>"|?*'):
        raise bad("invalid characters")
    if raw.startswith(("\\\\", "//")):
        raise bad("network and device paths are not accepted")
    parts = [p for p in re.split(r"[\\/]+", raw) if p]
    if not parts or any(re.fullmatch(r"[.\s]+", p) for p in parts):
        raise bad("'.' and '..' path components are not allowed")
    p = Path(raw)
    if p.is_absolute():                   # drive + root: explicit, anywhere
        cand, explicit = p, True
    elif p.drive or raw[0] in "\\/":
        raise bad("drive- or root-relative paths are ambiguous; give a project name or a "
                  "full absolute path")
    elif len(parts) == 1:
        if not _PROJECT_NAME.fullmatch(parts[0]):
            raise bad("not a valid project name")
        cand, explicit = PROJECTS / parts[0], False
    else:
        cand, explicit = PROJECT.joinpath(*parts), False
    if cand.name.lower() == "villa_design.py":
        cand = cand.parent
    try:
        folder = cand.resolve(strict=True)
    except OSError:
        raise bad(f"no such folder {cand}") from None
    if not explicit and not folder.is_relative_to(PROJECT):
        raise bad(f"{folder} is outside the pipeline folder {PROJECT}")
    if not folder.is_dir():
        raise bad(f"{folder} is not a folder")
    if not (folder / "villa_design.py").is_file():
        raise bad(f"{folder} holds no villa_design.py")
    if _norm(str(folder)) == _norm(str(PROJECT)):
        return villa()
    under = _norm(str(folder.parent)) == _norm(str(PROJECTS))
    out, how = _out_for(folder, False, env)
    return _Project(folder.name, folder, out, how, False,
                    key=folder.name if under else _norm(str(folder)))


# --------------------------------------------------------------------------
# The design's sheet list, without importing the builders
# --------------------------------------------------------------------------

_SHEETS_CACHE: dict[str, tuple[int, int, list[str], str]] = {}


def _literal_plan_sheets(src: str) -> list[tuple] | None:
    """PLAN_SHEETS from a design's syntax tree, when it is a literal."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        if any(isinstance(t, ast.Name) and t.id == "PLAN_SHEETS" for t in targets):
            try:
                return [tuple(r) for r in ast.literal_eval(node.value)]
            except (ValueError, TypeError, SyntaxError):
                return None
    return None


def _design_namespace(f: Path, src: str) -> dict[str, Any]:
    """Execute a design file in a throwaway module that never stays in
    sys.modules (a design is light by contract: no shapely at module level;
    Blender and Unreal load it too)."""
    name = "_villa_design_sheets"
    mod = types.ModuleType(name)
    mod.__file__ = str(f)
    with _VILLA_LOCK:
        before = set(sys.modules)
        sys.modules[name] = mod
        try:
            with contextlib.redirect_stdout(io.StringIO()):   # stdout is the MCP channel
                exec(compile(src, str(f), "exec", dont_inherit=True), mod.__dict__)
        finally:
            for m in set(sys.modules) - before:
                if m == name or _is_pipeline_module(m, sys.modules.get(m), (f.parent, PROJECT)):
                    sys.modules.pop(m, None)
    return mod.__dict__


def _plan_sheets(folder: Path) -> tuple[list[str], str]:
    """The design's plan sheets as file stems ('A102', ...), and where they
    came from -- villa_geom.plan_sheets() without importing the builders:
    PLAN_SHEETS when the design declares it (floors without rooms dropped),
    else the villa's A-102 GF, A-103 FF, plus A-104 RF once the roof has rooms.
    A design that does not run (mid-edit) falls back to a literal PLAN_SHEETS
    read from its syntax tree, then to the default; only a design that ran is
    cached (by file time and size)."""
    f = folder / "villa_design.py"
    try:
        st = f.stat()
        src = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ["A102", "A103"], "default (no villa_design.py)"
    k = _norm(str(f))
    hit = _SHEETS_CACHE.get(k)
    if hit and hit[:2] == (st.st_mtime_ns, st.st_size):
        return list(hit[2]), hit[3]

    def stem(no: Any) -> str:
        return str(no).replace("-", "")

    try:
        ns = _design_namespace(f, src)
        floors = list(ns["floors"]())
        declared = ns.get("PLAN_SHEETS")
        if declared:
            sheets = [stem(r[1]) for r in declared if r[0] in floors]
            how = "PLAN_SHEETS"
        else:
            sheets = ["A102", "A103"] + (["A104"] if "RF" in floors else [])
            how = "default: A-102 GF, A-103 FF, A-104 RF when the roof has rooms"
        _SHEETS_CACHE[k] = (st.st_mtime_ns, st.st_size, sheets, how)
        return list(sheets), how
    except Exception as exc:  # noqa: BLE001 - mid-edit design: degrade, don't fail
        lit = _literal_plan_sheets(src)
        why = f"the design did not run ({type(exc).__name__})"
        if lit:
            return [stem(r[1]) for r in lit], f"PLAN_SHEETS read as text; {why}"
        return ["A102", "A103"], f"default; {why}"


def _stage_table(ctx: _Project) -> dict[str, dict[str, Any]]:
    """_STAGES with {sheet} / {plan} expanded to this design's sheets."""
    plans, _ = _plan_sheets(ctx.folder)
    sheets = ["A101", *plans]

    def expand(pats: list[str]) -> list[str]:
        out: list[str] = []
        for p in pats:
            if "{sheet}" in p:
                out += [p.replace("{sheet}", s) for s in sheets]
            elif "{plan}" in p:
                out += [p.replace("{plan}", s) for s in plans]
            else:
                out.append(p)
        return out

    return {st: {**spec, "outputs": expand(spec.get("outputs", [])),
                 "inputs": expand(spec.get("inputs", []))}
            for st, spec in _STAGES.items()}


# --------------------------------------------------------------------------
# Freshness
# --------------------------------------------------------------------------

def _iso(ts: float | None) -> str | None:
    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds") if ts else None


def _mtime(p: Path) -> float | None:
    try:
        return p.stat().st_mtime
    except OSError:
        return None


def _expand(base: Path, pattern: str) -> list[Path]:
    if any(c in pattern for c in "*?["):
        return sorted(base.glob(pattern))
    return [base / pattern]


# A string-named import: importlib.import_module("villa_geom"), or a helper
# such as villa_elevations' _load("villa_design"). Only names that exist as a
# local module file count (_closure checks), so a false hit costs nothing.
_DYNAMIC_IMPORT = re.compile(r"import|load", re.I)


def _local_imports(p: Path) -> set[str]:
    text = p.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:       # mid-edit: fall back to a line scan
        return (set(re.findall(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)", text, re.M))
                | set(re.findall(r"(?:import_module|_load)\(\s*[\"']([A-Za-z_]\w*)[\"']",
                                 text)))
    mods: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and not n.level and n.module:
            mods.add(n.module.split(".")[0])
        elif (isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant)
              and isinstance(n.args[0].value, str)
              and re.fullmatch(r"[A-Za-z_]\w*", n.args[0].value)):
            fn = (n.func.attr if isinstance(n.func, ast.Attribute)
                  else n.func.id if isinstance(n.func, ast.Name) else "")
            if _DYNAMIC_IMPORT.search(fn):
                mods.add(n.args[0].value)
    return mods


def _closure(scripts: list[str], search: tuple[Path, ...] = (PROJECT,)) -> list[Path]:
    """Every local module a script imports, transitively (by AST). Each name is
    looked up in `search` order -- a project's folder first, then the pipeline
    -- which is where the running script finds it."""
    def find(fname: str) -> Path | None:
        for d in search:
            if (d / fname).is_file():
                return d / fname
        return None

    seen: dict[str, Path] = {}
    todo = list(scripts)
    while todo:
        s = todo.pop()
        if s in seen:
            continue
        f = find(s)
        if f is None:
            continue
        seen[s] = f
        for mod in _local_imports(f):
            fn = f"{mod}.py"
            if fn not in seen and find(fn):
                todo.append(fn)
    return [seen[k] for k in sorted(seen)]


def _load_runs() -> dict[str, Any]:
    try:
        return json.loads((STATE_DIR / "villa_runs.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _record_run(key: str, rec: dict[str, Any]) -> None:
    with _RUNS_LOCK:
        runs = _load_runs()
        runs[key] = rec
        with contextlib.suppress(OSError):
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            (STATE_DIR / "villa_runs.json").write_text(json.dumps(runs, indent=1),
                                                       encoding="utf-8")


def _rel(p: Path, out: Path = VILLA) -> str:
    for base in (out, PROJECT):
        with contextlib.suppress(ValueError):
            return str(p.relative_to(base))
    return str(p)


def _freshness(ctx: _Project | None = None) -> dict[str, Any]:
    ctx = ctx or _project(None)
    table = _stage_table(ctx)
    out_dir = ctx.out
    runs = _load_runs()
    produced_by: dict[str, str] = {}
    for st, spec in table.items():
        for pat in spec["outputs"]:
            for f in _expand(out_dir, pat):
                produced_by[_norm(str(f))] = st
    report: dict[str, Any] = {}
    for st, spec in table.items():
        code = _closure(spec["scripts"], ctx.search)
        src: list[Path] = list(code)
        for c in code:
            src += [c.parent / d for d in _DATA_DEPS.get(c.name, [])]
        inputs: list[Path] = []
        for pat in spec["inputs"]:
            inputs += _expand(out_dir, pat)
        missing_sources = [_rel(p, out_dir) for p in src + inputs if _mtime(p) is None]
        dated = [(p, _mtime(p)) for p in src + inputs if _mtime(p) is not None]
        newest = max(dated, key=lambda t: t[1]) if dated else (None, None)
        outs = []
        newest_out = None
        for pat in spec["outputs"]:
            files = _expand(out_dir, pat)
            if not files:
                outs.append({"path": pat, "status": "missing"})
            for f in files:
                m = _mtime(f)
                status = ("missing" if m is None else
                          "stale" if newest[1] and m + _TOL < newest[1] else "fresh")
                outs.append({"path": _rel(f, out_dir), "modified": _iso(m), "status": status})
                if m is not None:
                    newest_out = max(newest_out or m, m)
        upstream = sorted({produced_by[_norm(str(i))] for i in inputs
                           if _norm(str(i)) in produced_by and produced_by[_norm(str(i))] != st})
        last = runs.get(ctx.run_key(st))
        if spec.get("verify"):
            if not last:
                state = "unverified"
            elif not last.get("ok"):
                state = "failed"
            elif newest[1] and last.get("epoch", 0) + _TOL < newest[1]:
                state = "stale"
            else:
                state = "verified"
        elif any(o["status"] == "missing" for o in outs) or missing_sources:
            state = "missing"
        elif any(o["status"] == "stale" for o in outs):
            state = "stale"
        else:
            state = "fresh"
        # A checks stage writes its sheets even when a check fails (stamped CHECKS
        # FAILED): outputs that come from a failed run are not fresh.
        if (spec.get("checks") and state == "fresh" and last and not last.get("ok")
                and newest_out and last.get("finished_epoch", 0) + _TOL >= newest_out):
            state = "failed"
        report[st] = {
            "state": state, "about": spec["about"], "com": bool(spec.get("com")),
            "newest_source": {"path": _rel(newest[0], out_dir), "modified": _iso(newest[1])}
            if newest[0] else None,
            "sources": [_rel(p, out_dir) for p in src],
            "inputs": [_rel(p, out_dir) for p in inputs],
            "missing_sources": missing_sources, "outputs": outs,
            "upstream": upstream, "last_run": last,
            "run": f"villa_run(stage='{st}'"
                   + (f", project={ctx.arg!r}" if ctx.arg else "") + ")"}
    # an input produced by a stage that is itself out of date will change again
    for st in _STAGE_ORDER:          # pipeline order, so staleness chains downstream
        r = report[st]
        bad = [u for u in r["upstream"]
               if report[u]["state"].startswith(("stale", "missing"))]
        if bad:
            r["upstream_stale"] = bad
            if r["state"] in ("fresh", "verified"):
                r["state"] = "stale (upstream)"
    return report


# --------------------------------------------------------------------------
# villa_validate: in-process, fresh modules bound to ONE design
# --------------------------------------------------------------------------

# Furniture issues are tagged with their floor: [B1], [GF], [FF], [AX], [RF] ...
_FURN_TAG = re.compile(r"^\[([A-Z][A-Z0-9]{0,3})\s*\]\s*(.*)$", re.S)


def _furniture_issues(items: list[Any]) -> list[dict[str, Any]]:
    out = []
    for i in items:
        m = _FURN_TAG.match(str(i))
        out.append({"floor": m.group(1) if m else None, "issue": m.group(2) if m else str(i)})
    return out


def _is_pipeline_module(name: str, mod: Any, folders: tuple[Path, ...]) -> bool:
    """A module that may hold one design's V: every villa_* module, and any
    other module that lives directly in the pipeline or project folder
    (plan_dxf, ...) -- never this server itself."""
    if name in ("__main__", __name__, "server"):
        return False
    if name.startswith("villa_"):
        return True
    f = getattr(mod, "__file__", None)
    if not f:
        return False
    parent = _norm(os.path.dirname(f))
    return any(parent == _norm(str(d)) for d in folders)


def _forget_pipeline_modules(folders: tuple[Path, ...]) -> list[str]:
    gone = [n for n, m in list(sys.modules.items()) if _is_pipeline_module(n, m, folders)]
    for n in gone:
        sys.modules.pop(n, None)
    return gone


def _watch_dbc(seen: dict[str, Any]) -> Any:
    """Import villa_dbc now -- bound to the design just imported -- and record
    what its checks() returns when villa_design.validate() calls it."""
    try:
        D = importlib.import_module("villa_dbc")
    except Exception as exc:  # noqa: BLE001 - validate() reports it in its own words
        sys.modules.pop("villa_dbc", None)
        seen["error"] = f"{type(exc).__name__}: {exc}"
        return None
    orig = D.checks

    def checks(*a: Any, **kw: Any) -> Any:
        try:
            res = orig(*a, **kw)
        except Exception as exc:  # validate() catches it and reports a MAJOR
            seen["error"] = f"{type(exc).__name__}: {exc}"
            raise
        seen["issues"] = [str(i) for i in res]
        return res

    D.checks = checks
    return D


def _rooms_per_floor(V: Any) -> dict[str, int]:
    try:
        floors = list(V.floors())
    except Exception:  # noqa: BLE001
        floors = []
    if hasattr(V, "rooms_on"):
        with contextlib.suppress(Exception):
            return {fl: len(V.rooms_on(fl)) for fl in floors}
    counts: dict[str, int] = {}
    for r in getattr(V, "ROOMS", []):
        with contextlib.suppress(IndexError, TypeError):
            counts[r[6]] = counts.get(r[6], 0) + 1
    return {fl: counts.get(fl, 0) for fl in floors + [f for f in counts if f not in floors]}


def _same_file(a: Any, b: Any) -> bool:
    return bool(a) and bool(b) and _norm(str(a)) == _norm(str(b))


@_tool("Validate villa design", ro=True, idempotent=True)
def villa_validate(include_probes: Annotated[bool, Field(
                       description="Also list every 3D probe (name, expect, x, y, z, r).")] = False,
                   project: ProjectArg = None) -> dict[str, Any]:
    """Validate a design in-process, freshly re-importing its villa_design.py
    and villa_furniture_spec.py -- the villa's, or with project='fairway' (a
    name under projects\\, or an absolute folder) that project's:

      * villa_design.validate(): FATAL / MAJOR / NOTE issues (openings cut
        through walls, reachability, forecourt, stair, circulation, and the
        Dubai Building Code checks of villa_dbc, reported again under 'dbc');
      * villa_design.probes(): the solid/void probes both 3D verifiers ask;
      * villa_furniture_spec.check(): furniture inside rooms, clear of door
        swings, with researched clearances -- per floor (B1, GF, FF, AX, RF).

    Every pipeline module is re-imported bound to that design (the project
    folder first on sys.path, then the pipeline); 'project' names the design
    file used. ok=True only with no fatal, no major and no furniture issues.
    Pure Python: no AutoCAD, nothing written. Coordinates are mm.
    """
    ctx = _project(project)
    t0 = time.perf_counter()
    folders = (ctx.folder, PROJECT)
    first = [str(d) for d in ctx.search]
    first_n = {_norm(p) for p in first}
    seen: dict[str, Any] = {}
    buf = io.StringIO()
    with _VILLA_LOCK:
        saved_path = list(sys.path)
        try:
            # Fresh modules every call, bound to THIS design. The design is edited
            # while the server runs, and villa_dbc / villa_geom / villa_colour cached
            # by an earlier call would still hold the design THAT call loaded.
            _forget_pipeline_modules(folders)
            sys.path[:] = first + [p for p in saved_path if _norm(p) not in first_n]
            importlib.invalidate_caches()
            with contextlib.redirect_stdout(buf):
                try:
                    V = importlib.import_module("villa_design")
                    F = importlib.import_module("villa_furniture_spec")
                except SyntaxError as exc:
                    raise ToolError(f"design code does not parse: {exc.filename}:"
                                    f"{exc.lineno}: {exc.msg} (mid-edit? retry)") from exc
                if not _same_file(V.__file__, ctx.design_file):
                    raise ToolError(f"imported {V.__file__}, not {ctx.design_file}: "
                                    "sys.path did not put the design first")
                D = _watch_dbc(seen)
                issues = list(V.validate())
                probes = list(V.probes())
                furniture = list(F.check())
                circ = getattr(V, "_CIRC_REPORT", None)
                rooms = _rooms_per_floor(V)
                by_floor = getattr(F, "BY_FLOOR", None)
                items = ({fl: len(lst) for fl, lst in by_floor} if by_floor else
                         {"GF": len(getattr(F, "GROUND", [])), "FF": len(getattr(F, "FIRST", []))})
                files = {"villa_design.py": Path(V.__file__),
                         "villa_furniture_spec.py": Path(F.__file__),
                         "block_catalog.json": Path(F.__file__).parent / "block_catalog.json"}
                dbc_mod = sys.modules.get("villa_dbc", D)
                dbc_file = getattr(dbc_mod, "__file__", None)
                dbc_bound = getattr(getattr(dbc_mod, "V", None), "__file__", None)
        finally:
            sys.path[:] = saved_path
            _forget_pipeline_modules(folders)     # leave nothing bound to this design
            importlib.invalidate_caches()
    if dbc_bound and not _same_file(dbc_bound, V.__file__):
        raise ToolError(f"villa_dbc checked {dbc_bound}, not {V.__file__} (stale module)")
    sev: dict[str, list[str]] = {"FATAL": [], "MAJOR": [], "MINOR": [], "NOTE": [], "OTHER": []}
    for i in issues:
        m = re.match(r"^\[(FATAL|MAJOR|MINOR|NOTE)\s*\]\s*(.*)$", str(i), re.S)
        (sev[m.group(1)] if m else sev["OTHER"]).append(m.group(2) if m else str(i))
    furn = _furniture_issues(furniture)
    solid = sum(1 for p in probes if p[4] == "solid")
    dbc_issues = seen.get("issues", [])
    dbc: dict[str, Any] = {
        "ran": "issues" in seen, "module": dbc_file, "bound_to": dbc_bound,
        "count": len(dbc_issues),
        "fatal": sum(i.startswith("[FATAL") for i in dbc_issues),
        "major": sum(i.startswith("[MAJOR") for i in dbc_issues),
        "issues": dbc_issues}
    if seen.get("error"):
        dbc["error"] = seen["error"]
    out: dict[str, Any] = {
        "ok": not sev["FATAL"] and not sev["MAJOR"] and not furn,
        "summary": (f"{ctx.name}: {len(sev['FATAL'])} fatal, {len(sev['MAJOR'])} major, "
                    f"{len(sev['NOTE']) + len(sev['MINOR'])} notes; {len(probes)} probes "
                    f"({solid} solid, {len(probes) - solid} void); "
                    f"{len(furn)} furniture issues; rooms "
                    + ", ".join(f"{fl} {n}" for fl, n in rooms.items())),
        "project": ctx.info(),
        "design": {"fatal": sev["FATAL"], "major": sev["MAJOR"], "minor": sev["MINOR"],
                   "notes": sev["NOTE"], "other": sev["OTHER"]},
        "dbc": dbc,
        "rooms": rooms,
        "probes": {"count": len(probes), "solid": solid, "void": len(probes) - solid},
        "furniture": {"issues": furn, "items": items},
        "sources": {n: _iso(_mtime(p)) for n, p in files.items()},
        "seconds": round(time.perf_counter() - t0, 3)}
    if circ:
        c = [float(v) for v in circ]
        if len(c) in (2, 3):
            corridor, gia = c[0], c[-1]
            circulation = {"corridor_m2": round(corridor, 2)}
            if len(c) == 3:
                circulation["halls_m2"] = round(c[1], 2)
            circulation.update(gia_m2=round(gia, 2),
                               corridor_pct=round(100 * corridor / gia, 2) if gia else None)
            out["circulation"] = circulation
        else:
            out["circulation"] = {"raw": [round(v, 2) for v in c]}
    if include_probes:
        out["probes"]["list"] = [{"name": p[0], "expect": p[4], "x": round(p[1], 1),
                                  "y": round(p[2], 1), "z": round(p[3], 1), "r": p[5]}
                                 for p in probes]
    if buf.getvalue().strip():
        out["stdout"] = buf.getvalue()[-2000:]
    return out


@_tool("Villa output freshness", ro=True, idempotent=True)
def villa_status(project: ProjectArg = None) -> dict[str, Any]:
    """Which outputs of a design are out of date -- the villa's, or with
    project='fairway' (a name under projects\\, or an absolute folder) that
    project's? For every pipeline stage: its code (the script plus every
    local module it imports, found by parsing imports -- the project folder
    first, then the pipeline), data and input files; each output's age; and
    a state:

      fresh / stale (older than a source) / missing / stale (upstream) (an
      input comes from a stage that is itself stale); verify stages report
      verified / failed / unverified / stale from their last villa_run; the
      elevations stage reports failed when its sheets come from a failed run.

    Sheet files follow the design's sheet list (e.g. the Fairway's B1 plan).
    Also lists stages to re-run in pipeline order, and files in the output
    folder that no stage produces and that predate villa_design.py (probably
    superseded). Output folder: VILLA_OUT if set, else (villa only) VILLA_DIR,
    else Desktop\\<OUT_NAME> / Desktop\\Villa. Reads file times only: no
    AutoCAD, nothing written.
    """
    ctx = _project(project)
    report = _freshness(ctx)
    table = _stage_table(ctx)
    plans, how = _plan_sheets(ctx.folder)
    design_m = _mtime(ctx.design_file)
    known: set[str] = set()
    for spec in table.values():
        for pat in spec["outputs"] + spec["inputs"]:
            known.update(_norm(str(f)) for f in _expand(ctx.out, pat))
    superseded = []
    if ctx.out.is_dir():
        for f in sorted(ctx.out.iterdir()):
            if not f.is_file() or f.suffix.lower() in (".bak", ".dwl", ".dwl2", ".tmp"):
                continue
            m = _mtime(f)
            if _norm(str(f)) not in known and design_m and m and m + _TOL < design_m:
                superseded.append({"file": f.name, "modified": _iso(m)})
    todo = [s for s in _STAGE_ORDER if report[s]["state"] not in ("fresh", "verified")]
    return {"project": ctx.info(), "villa_dir": str(ctx.out), "pipeline_dir": str(PROJECT),
            "design_modified": _iso(design_m),
            "sheets": {"plans": [f"{s[0]}-{s[1:]}" for s in plans], "from": how},
            "rerun_in_order": todo,
            "stages": report,
            "superseded_candidates": superseded,
            "note": "Freshness is by modification time. Unsaved/open drawings in AutoCAD "
                    "are not visible here: see acad_list_drawings / acad_list_orphans."}


# --------------------------------------------------------------------------
# villa_run
# --------------------------------------------------------------------------

def _script_argv(ctx: _Project, script: str) -> list[str]:
    """How a pipeline script is launched: the villa's directly, as always; a
    project's through run_project.py, which puts the project folder first on
    sys.path (then this pipeline folder) and runs the script as __main__."""
    if ctx.is_villa:
        return [PYTHON, "-X", "utf8", str(PROJECT / script)]
    return [PYTHON, "-X", "utf8", str(PROJECT / "run_project.py"), str(ctx.folder), script]


def _sac_enforcing() -> bool:
    """Windows Smart App Control in enforce mode (registry
    VerifiedAndReputablePolicyState == 1). It judges each unsigned binary on
    its own and its verdicts change over time: on 2026-10-08 it refused
    OpenCascade's DLLs, then allowed them and refused scipy's _propack.pyd."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\CI\Policy") as k:
            return winreg.QueryValueEx(k, "VerifiedAndReputablePolicyState")[0] == 1
    except (ImportError, OSError):
        return False


@functools.lru_cache(maxsize=1)
def _occ_blocked() -> bool:
    """True when the build123d stages cannot be trusted to load here: Smart
    App Control is enforcing (its per-file verdicts make a passing probe
    meaningless), or a full build123d import plus one solid fails. Probed once
    per server process, in a child, so a refused DLL cannot touch this one."""
    if _sac_enforcing():
        return True
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    probe = "import OCP.OCP, build123d; build123d.Box(1, 1, 1)"
    try:
        r = subprocess.run([PYTHON, "-c", probe], capture_output=True,
                           timeout=120, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired):
        return True
    return r.returncode != 0


def _occ_via_wsl() -> bool:
    """Run the build123d stages (stage spec "occ") in WSL through
    tools_wsl3d.py? VILLA3D_VIA_WSL=1 forces it, 0 forbids it; unset, only
    when OpenCascade cannot load here."""
    flag = os.environ.get("VILLA3D_VIA_WSL", "").strip().lower()
    if flag in ("1", "true"):
        return True
    if flag in ("0", "false"):
        return False
    return _occ_blocked()


def _stage_env(ctx: _Project) -> dict[str, str | None]:
    """Environment overrides for a stage (None = removed). VILLA_OUT always --
    the folder villa_status reads -- so a VILLA_DIR-only setting reaches the
    scripts too; VILLA_DESIGN_DIR for a project (builders that put their own
    folder on sys.path, and villa_blender, honour it), removed for the villa."""
    return {"VILLA_OUT": str(ctx.out),
            "VILLA_DESIGN_DIR": None if ctx.is_villa else str(ctx.folder)}


def _stage_commands(stage: str, render_args: list[str],
                    ctx: _Project | None = None) -> list[list[str]]:
    ctx = ctx or _project(None)
    spec = _STAGES[stage]
    if spec.get("blender"):
        # --python-exit-code: without it Blender exits 0 when the script raises.
        # A project reaches villa_blender through VILLA_DESIGN_DIR (_stage_env).
        return [[str(BLENDER), "-b", "--factory-startup", "--python-exit-code", "1",
                 "-P", str(PROJECT / "villa_blender.py"), "--", *render_args]]
    argvs = [_script_argv(ctx, s) for s in spec["scripts"]]
    if spec.get("occ") and _occ_via_wsl():
        # the same script and arguments, launched in WSL; VILLA_OUT and
        # VILLA_DESIGN_DIR (_stage_env) are translated to /mnt/... there
        argvs = [[PYTHON, str(PROJECT / "tools_wsl3d.py"), *a[3:]] for a in argvs]
    return argvs


def _check_render_args(args: list[str]) -> list[str]:
    out, i = [], 0
    while i < len(args):
        flag = args[i]
        if flag not in _RENDER_FLAGS:
            raise ToolError(f"render_args: unknown flag {flag!r}; allowed: "
                            f"{sorted(_RENDER_FLAGS)}")
        pat = _RENDER_FLAGS[flag]
        if pat is None:
            out.append(flag)
            i += 1
            continue
        if i + 1 >= len(args) or not re.fullmatch(pat, args[i + 1]):
            raise ToolError(f"render_args: {flag} needs a value matching {pat}")
        out += [flag, args[i + 1]]
        i += 2
    return out


def _tail(text: str, lines: int, chars: int) -> str:
    t = "\n".join(text.splitlines()[-lines:])
    return t[-chars:]


def _run_proc(argv: list[str], timeout: float, log,
              env_over: dict[str, str | None] | None = None) -> dict[str, Any]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONUNBUFFERED="1")
    for k, v in (env_over or {}).items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, cwd=str(PROJECT), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                            creationflags=flags)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                       capture_output=True, creationflags=flags)
        out, err = proc.communicate(timeout=60)
    so = out.decode("utf-8", "replace")
    se = err.decode("utf-8", "replace")
    log.write(f"$ {subprocess.list2cmdline(argv)}\n"
              + (f"env: {json.dumps(env_over)}\n" if env_over else "")
              + f"--- stdout ---\n{so}\n--- stderr ---\n{se}\n"
              f"--- exit {proc.returncode}{' (timed out)' if timed_out else ''} ---\n\n")
    text = so + "\n" + se
    flagged = [ln.strip() for ln in text.splitlines()
               if any(p.search(ln) for p in _FAIL_MARKS + _UNVERIFIED_MARKS)]
    checks = list(_CHECKS_MARK.finditer(so))
    return {"argv": argv, "exit_code": proc.returncode, "timed_out": timed_out,
            "seconds": round(time.monotonic() - t0, 1),
            "failed_markers": any(p.search(text) for p in _FAIL_MARKS),
            "unverified_markers": any(p.search(text) for p in _UNVERIFIED_MARKS),
            "verified_marker": bool(_VERIFIED_MARK.search(so)),
            "checks": {"passed": int(checks[-1].group(1)), "total": int(checks[-1].group(2)),
                       "line": checks[-1].group(0).strip()} if checks else None,
            "flagged_lines": flagged[:30],
            "stdout_tail": _tail(so, 40, 6000), "stderr_tail": _tail(se, 20, 3000)}


def _verdict(spec: dict[str, Any], ran: list[dict[str, Any]], n_cmds: int) -> str:
    """A stage's verdict from its runs (the scripts exit 0 even when a check
    fails, so their output is read too)."""
    if any(r["timed_out"] for r in ran) or len(ran) < n_cmds:
        return "timeout"
    if spec.get("checks"):
        # The script's own 'N/N checks passed' line decides; exiting non-zero or
        # printing CHECKS FAILED / a FAIL line is a failure whatever it says.
        lines = [r.get("checks") for r in ran]
        crashed = any(r["exit_code"] != 0 for r in ran)
        if any(c is None for c in lines):
            return "error" if crashed else "failed"
        if (any(c["passed"] < c["total"] or c["total"] == 0 for c in lines)
                or any(r["failed_markers"] for r in ran)):
            return "failed"
        return "error" if crashed else "ok"
    if any(r["exit_code"] != 0 for r in ran):
        return "error"
    if any(r["failed_markers"] for r in ran):
        return "failed"
    if spec.get("verify"):
        if any(r["unverified_markers"] for r in ran):
            return "unverified"
        if all(r["verified_marker"] for r in ran):
            return "verified"
        return "failed"
    return "ok"


def _mentions(path: Path, word: str) -> bool:
    try:
        return word in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


@_tool("Run villa pipeline stage", destructive=True)
def villa_run(stage: Annotated[Stage, Field(description=(
                  "plans=villa_cad.py, colour=villa_colour.py, elevations=villa_elevations.py "
                  "(A-201..A-204, A-301), gltf=villa_gltf.py, "
                  "build3d=villa_3d_build.py (COM), verify3d=villa_3d_verify.py + "
                  "villa_pool_check.py + villa_window_check.py (COM), load=villa_load.py "
                  "(COM), verify=villa_verify.py (COM), render=Blender villa_blender.py"))],
              timeout_s: Annotated[int, Field(
                  ge=0, le=7200, description="0 = the stage's default.")] = 0,
              render_args: Annotated[list[str] | None, Field(
                  description="render only: --samples N, --res WxH, --views a,b, --hdri "
                              "stem, --sun-az deg, --no-render")] = None,
              dry_run: Annotated[bool, Field(
                  description="Return the commands without running them.")] = False,
              project: ProjectArg = None
              ) -> dict[str, Any]:
    """Run one pipeline stage as a subprocess (the same Python as this server;
    Blender for render) and report exit code, a verdict, the lines that signal
    trouble, and output tails; the full log is saved to a file.

    project=None runs the villa's design; project='fairway' (a name under
    projects\\, or an absolute folder) runs the script through run_project.py
    against that design, writing to VILLA_OUT or Desktop\\<OUT_NAME>; the
    result's 'project' names the design and folder. Regenerates (overwrites)
    that stage's outputs there. COM stages (build3d, verify3d, load, verify)
    hold this server's AutoCAD lock for their whole run, so no acad_* call can
    interleave with them. The scripts exit 0 even when a check fails, so the
    verdict also reads their output: 'ok' / 'verified' (every check printed
    VERIFIED) / 'failed' / 'unverified' (a probe errored) / 'error' (non-zero
    exit) / 'timeout'; elevations is 'ok' only when its 'N/N checks passed'
    line shows every check passed. Check villa_status first; after build3d or
    load, acad_list_orphans shows DrawingN documents a whole-job retry left.
    """
    ctx = _project(project)
    spec = _STAGES[stage]
    if render_args and stage != "render":
        raise ToolError("render_args only applies to stage='render'")
    args = _check_render_args(render_args or []) if stage == "render" else []
    if spec.get("blender") and not BLENDER.exists():
        raise ToolError(f"Blender not found at {BLENDER} (set BLENDER_EXE).")
    warning = None
    if spec.get("blender") and not ctx.is_villa \
            and not _mentions(PROJECT / "villa_blender.py", "VILLA_DESIGN_DIR"):
        warning = ("villa_blender.py does not read VILLA_DESIGN_DIR yet, so it would render "
                   f"the villa, not {ctx.name}")
        if not dry_run:
            raise ToolError(f"render for project {ctx.name!r} refused: {warning}.")
    cmds = _stage_commands(stage, args, ctx)
    env_over = _stage_env(ctx)
    total = float(timeout_s or spec["timeout"])
    base = {"stage": stage, "about": spec["about"], "project": ctx.info(),
            "com_stage": bool(spec.get("com")),
            "commands": [subprocess.list2cmdline(c) for c in cmds], "env": env_over,
            "timeout_s": total}
    if dry_run:
        out = {**base, "dry_run": True, "outputs": _stage_table(ctx)[stage]["outputs"]}
        if warning:
            out["warning"] = warning
        return out
    if spec.get("com"):
        acad_status_now = acad_status()
        if acad_status_now.get("connected") is False:
            raise ToolError(f"{stage} drives AutoCAD, which is not running: "
                            f"{acad_status_now.get('error')}")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "logs").mkdir(exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "villa" if ctx.is_villa else "villa_" + re.sub(r"[^\w.-]", "_", ctx.name)
    log_path = STATE_DIR / "logs" / f"{tag}_{stage}_{stamp}.log"
    started = time.time()
    t_end = time.monotonic() + total
    results = []
    lock = _holding_com_lock(f"villa_run({stage})", 120.0) if spec.get("com") \
        else contextlib.nullcontext()
    with lock, open(log_path, "w", encoding="utf-8") as log:
        for argv in cmds:
            left = t_end - time.monotonic()
            if left <= 1:
                results.append({"argv": argv, "skipped": "stage timeout used up"})
                continue
            r = _run_proc(argv, left, log, env_over)
            results.append(r)
            if r["timed_out"]:
                break
    ran = [r for r in results if "exit_code" in r]
    verdict = _verdict(spec, ran, len(cmds))
    ok = verdict in ("ok", "verified")
    rec = {"ok": ok, "verdict": verdict, "epoch": started, "finished": _iso(time.time()),
           "finished_epoch": time.time(), "log": str(log_path), "project": ctx.name}
    if spec.get("checks"):
        rec["checks"] = [r.get("checks") and r["checks"]["line"] for r in ran]
    _record_run(ctx.run_key(stage), rec)
    out = {**base, "ok": ok, "verdict": verdict, "log": str(log_path),
           "seconds": round(time.time() - started, 1), "runs": results,
           "freshness": {k: v for k, v in _freshness(ctx)[stage].items()
                         if k in ("state", "outputs", "upstream_stale")}}
    if spec.get("checks"):
        out["checks"] = [r.get("checks") for r in ran]
    if stage in ("build3d", "load"):
        out["hint"] = "Whole-job retries can leave unsaved DrawingN documents: acad_list_orphans."
    return out


# ==========================================================================
# Offline DXF tools (no AutoCAD required)
# ==========================================================================


def _read_dxf(path: str):
    """ezdxf read with recover fallback. Returns (doc, note)."""
    import ezdxf
    from ezdxf import recover

    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if path.lower().endswith(".dwg"):
        raise ToolError("This tool reads DXF, not DWG. Convert the file with the ODA File "
                        "Converter first, or open it in AutoCAD and use the acad_* tools.")
    try:
        return ezdxf.readfile(path), None
    except ezdxf.DXFStructureError:
        doc, auditor = recover.readfile(path)
        return doc, f"structure errors: recovered ({len(auditor.errors)} errors, " \
                    f"{len(auditor.fixes)} fixes)"


DxfPath = Annotated[str, Field(description="Path to a .dxf file.")]


@_tool("DXF summary", ro=True, idempotent=True)
def dxf_info(path: DxfPath) -> dict[str, Any]:
    """Summarise a DXF: version, units, true model-space extents (computed, not
    the header's often-sentinel $EXTMIN/$EXTMAX), layers, entity counts, layouts,
    block definitions and the most-inserted blocks."""
    from ezdxf import bbox, units

    doc, note = _read_dxf(path)
    msp = doc.modelspace()
    counts: dict[str, int] = {}
    inserts: dict[str, int] = {}
    for e in msp:
        t = e.dxftype()
        counts[t] = counts.get(t, 0) + 1
        if t == "INSERT":
            inserts[e.dxf.name] = inserts.get(e.dxf.name, 0) + 1
    ext = bbox.extents(msp, fast=True)
    code = int(doc.header.get("$INSUNITS", 0))
    hmin = list(doc.header.get("$EXTMIN", (0, 0, 0)))
    blocks = [b.name for b in doc.blocks
              if not b.name.startswith("*") and not b.is_any_layout]
    out = {
        "path": path, "dxf_version": doc.dxfversion, "release": doc.acad_release,
        "units_code": code, "units": units.unit_name(code) if code else "unitless",
        "extents": {"min": [round(v, 3) for v in ext.extmin],
                    "max": [round(v, 3) for v in ext.extmax],
                    "size": [round(v, 3) for v in ext.size]} if ext.has_data else None,
        "header_extents_valid": abs(hmin[0]) < 1e19,
        "layers": [str(lyr.dxf.name) for lyr in doc.layers],
        "entity_counts": counts, "total_entities": sum(counts.values()),
        "layouts": [{"name": lay.name, "entities": len(lay)} for lay in doc.layouts],
        "block_definitions": len(blocks),
        "top_inserts": dict(sorted(inserts.items(), key=lambda kv: -kv[1])[:30]),
    }
    if note:
        out["note"] = note
    return out


@_tool("List DXF entities", ro=True, idempotent=True)
def dxf_list_entities(path: DxfPath,
                      dxftype: Annotated[str, Field(description="e.g. LINE, LWPOLYLINE, "
                                                                "INSERT; empty = all")] = "",
                      layer: str = "",
                      limit: Annotated[int, Field(ge=1, le=10000)] = 200,
                      layout: Annotated[str, Field(description="'Model' or a paper-space "
                                                               "layout name.")] = "Model"
                      ) -> list[dict[str, Any]]:
    """List entities of one layout, optionally filtered by type and/or layer,
    with key geometry (points in drawing units)."""
    doc, _ = _read_dxf(path)
    lay = doc.modelspace() if layout.lower() == "model" else None
    if lay is None:
        lay = next((x for x in doc.layouts if x.name.lower() == layout.lower()), None)
    if lay is None:
        raise ToolError(f"No layout {layout!r}; layouts: {[x.name for x in doc.layouts]}")
    out = []
    for e in lay:
        if dxftype and e.dxftype() != dxftype.upper():
            continue
        if layer and str(e.dxf.layer) != layer:
            continue
        rec: dict[str, Any] = {"type": e.dxftype(), "layer": str(e.dxf.layer),
                               "handle": str(e.dxf.handle)}
        try:
            if e.dxftype() == "LINE":
                rec["start"] = list(e.dxf.start)[:3]
                rec["end"] = list(e.dxf.end)[:3]
            elif e.dxftype() in ("CIRCLE", "ARC"):
                rec["center"] = list(e.dxf.center)[:3]
                rec["radius"] = float(e.dxf.radius)
            elif e.dxftype() in ("TEXT", "MTEXT"):
                rec["text"] = e.plain_text() if hasattr(e, "plain_text") else str(e.dxf.text)
            elif e.dxftype() == "LWPOLYLINE":
                rec["points"] = [list(p)[:2] for p in e.get_points()]
                rec["closed"] = bool(e.closed)
            elif e.dxftype() == "INSERT":
                rec["block"] = str(e.dxf.name)
                rec["insert"] = list(e.dxf.insert)[:3]
                rec["rotation"] = float(e.dxf.rotation)
        except Exception:  # noqa: BLE001 - a malformed entity keeps its basic fields
            pass
        out.append(rec)
        if len(out) >= limit:
            break
    return out


@_tool("Extract DXF text", ro=True, idempotent=True)
def dxf_extract_text(path: DxfPath,
                     include_paperspace: bool = False,
                     include_attributes: Annotated[bool, Field(
                         description="Also block attribute values (ATTRIB).")] = True
                     ) -> list[dict[str, Any]]:
    """Pull every TEXT/MTEXT string (and optionally block attributes) out of a
    DXF, with layer, layout and position."""
    doc, _ = _read_dxf(path)
    spaces = [doc.modelspace()] + ([lay for lay in doc.layouts if lay.name != "Model"]
                                   if include_paperspace else [])
    out = []
    for space in spaces:
        for e in space:
            try:
                t = e.dxftype()
                if t in ("TEXT", "MTEXT"):
                    content = e.plain_text() if hasattr(e, "plain_text") else str(e.dxf.text)
                    pos = e.dxf.get("insert", (0, 0, 0))
                    out.append({"text": content, "layer": str(e.dxf.layer),
                                "layout": space.name, "position": list(pos)[:3]})
                elif t == "INSERT" and include_attributes:
                    for a in e.attribs:
                        out.append({"text": str(a.dxf.text), "tag": str(a.dxf.tag),
                                    "block": str(e.dxf.name), "layer": str(a.dxf.layer),
                                    "layout": space.name,
                                    "position": list(a.dxf.get("insert", (0, 0, 0)))[:3]})
            except Exception:  # noqa: BLE001
                continue
    return out


if __name__ == "__main__":
    mcp.run()
