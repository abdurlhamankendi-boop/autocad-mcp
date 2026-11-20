# CAD + AI: what's new since 2026-10-16 (as of 2026-11-20)

The window is 2026-10-16 to 2026-11-20, with older items marked "before the window" where they still matter. Three Sonnet researchers collected the findings. Two Opus checkers then re-opened the sources and corrected or rated each claim that matters.

- **Verified**: the checker confirmed the claim.
- **Partly**: the checker corrected it, and the corrected wording is used here.
- **Unchecked**: the claim was seen only in a search snippet.

"No evidence found" means the searches turned up nothing. It is not proof that nothing exists.

## 1. AutoCAD, DWG and MCP tools

| Date | Item | Status | What it means for us |
|---|---|---|---|
| Sep and Nov 2026 releases (the hub shows no dates) | **Autodesk's official AutoCAD and Civil 3D MCP server** ([hub](https://help.autodesk.com/view/ADSKMCP/ENU/), [server page](https://help.autodesk.com/cloudhelp/ENU/ADSKMCP-AutoCADCivil3DMcp/files/ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html.html), [release notes](https://help.autodesk.com/cloudhelp/ENU/ADSKMCP-AutoCADCivil3DMcp/files/autocadcivil3dmcp_relnotes.html), [tools](https://help.autodesk.com/cloudhelp/ENU/ADSKMCP-AutoCADCivil3DMcp/files/autocadcivil3dmcp_tools.html)). It is a local Tech Preview (Public Beta) on Windows. It needs Autodesk Assistant open, and Assistant is the only documented client. Autodesk's own docs disagree on what it can change in AutoCAD. The tools reference lists AutoCAD as read-only, with writes in Civil 3D only. The Sep 2026 release notes add AutoCAD edits to layers and system variables. The Nov 2026 notes add edits to colour, linetype, lineweight, transparency, text style and polyline width. | Partly | This overturns the 2026-10-16 note's "none controls AutoCAD". It does not replace our COM server, because Claude cannot connect to it and it cannot author drawings. Running `MCPCONFIG` in AutoCAD shows which of its tools are on. |
| Hub, undated | The Autodesk **Fusion, Fusion Data and Product Help** MCP servers are General Availability. Fusion Compute is in Public Beta. Revit MCP is a Tech Preview for Revit 2027.2. | Partly (Fusion Compute was missing from the report) | This overturns "all preview or beta". |
| 2026-11-12 | **Claude for Manufacturing**: a plugin with 17 skills and 4 connectors (Autodesk Fusion, Infor, Microsoft 365, NetSuite). ([post](https://claude.com/blog/claude-for-manufacturing)) | Verified | Fusion only, not AutoCAD. |
| Page undated | **ODA MCP Servers** now say "available now", in Core Package+ for Sustaining members and above. DWG reading works, and creating and editing objects (including booleans) is available. Saving back to native files is marked "Next". Listing the servers in a general AI assistant needs a separate GAIP licence. ([page](https://opendesign.com/products/mcp-servers)) | Verified, with a caveat | The September slip is resolved. It is paid and membership-gated, and full DWG save-back is not there yet. |
| 2026-10-26 / 2026-11-06 | **autocad-mcp-pro 1.7.0 and 1.8.0** ([PyPI](https://pypi.org/project/autocad-mcp-pro/), [releases](https://github.com/U-C4N/Autocad-MCP/releases)). See the details below the table. | Verified | Our install is 1.5.1 with local patches LP-1 and LP-2 in `backends/com_backend.py`, so we are three releases behind. An upgrade-plan session was started on 2026-11-20. |
| Unchecked | Other AutoCAD MCP servers: `LuiccianDev/autocad-mcp` (open source, for AutoCAD 2027 and Civil 3D) and AEC Pilot (commercial). | Unchecked | Competitors to watch. |
| No change | best-cad-mcp is still 1.7.2 (2026-09-23). | Verified | |
| 2026-10-16 | ezdxf 1.4.5 is still the newest release. | Verified | Our Python 3.13 environment has 1.4.4. Before bumping, re-check HATCH and MTEXT output, as the 10-16 note said. |
| 2026-11-20 | LibreDWG is still nightly builds only (0.14.9154). | Verified | Do not pin to it. |
| Undated pages | Rhino 9 has an AI and MCP section (unchecked). Bentley has MCP servers for MicroStation and STAAD.Pro (unchecked). Archicad 30 has an MCP server in beta (unchecked). | Unchecked | None of them is AutoCAD. |

**autocad-mcp-pro 1.7.0 and 1.8.0, in detail**

- 1.7.0 adds `drawing_verify_requirements`, which blocks delivery when typed checks fail. It also adds a document ID and revision per file, and a Claude Code plugin, for 248 tools in all.
- 1.8.0 has 257 tools. It adds:
  - a SQLite operation journal with checkpoint create, list and restore
  - `READ_ONLY`, `TOOL_ALLOWLIST`, `TOOL_DENYLIST` and `MAX_TOOL_COST`
  - search-mode tool discovery, which cuts idle prompt cost from about 59,138 to about 1,026 tokens
  - headless `.dwg` opening, which tries ODA File Converter first and then accoreconsole
- Changed defaults in 1.8.0:
  - `DISCOVERY_MODE` is now `search`.
  - `cad_batch` now uses `on_error="auto"` and is all-or-nothing. `entity_delete_many` is all-or-none too.
  - `LISP_POLICY` is now `read`.
  - `JOURNAL_DURABLE` is now on.
  - Errors now come back in a typed envelope.
  - `strict_critique` now fails on `not_checked`.
- COM backend changes in 1.8.0:
  - Drawing targets model space until `layout_set_current` is called.
  - Commands and undo wait for completion.
  - Large create and delete jobs run as sliced STA jobs.
  - A new message filter retries `RPC_E_CALL_REJECTED`.
- Upstream ran its live tests on AutoCAD 2026, not 2027.

## 2. Research

| Date | Paper | Status | What it means for us |
|---|---|---|---|
| 2026-06-11 (v2 2026-06-30), before the window | **ComAct: Reframing Professional Software Manipulation via COM-as-Action Paradigm**. ComCADBench has 1,000 tasks across SolidWorks, Inventor and AutoCAD. GUI control scores 0.0% for GPT-5 and Qwen3.5-9B. Zero-shot COM gets GPT-5 to 33.0% on 2D sketches. Their trained ComActor reaches 81 to 89% on SolidWorks and Inventor. ([arXiv](https://arxiv.org/abs/2606.13239)) | Partly (it targets three applications, not only AutoCAD) | Strong evidence that driving AutoCAD over COM, as our server does, beats screen control. |
| 2026-11-02 | **Parametric CAD Bench v3** has 100 tasks: 30 text-to-CAD, 30 create-and-edit and 40 drawing reconstruction. The best point estimate is Claude Code with Opus 5.5 at 61.03%. Its image-to-CAD mean reward is 84.66%, which is not a pass rate. The results are a 2026-09-24 snapshot of 13 systems, so Fable 5.2 was not tested. ([arXiv](https://arxiv.org/abs/2611.02659)) | Partly | Current yardstick for CAD agents. It covers mechanical parts, not buildings. |
| 2026-10-12 | **ModRes**, a cleaned ResPlan, by Shelley, Jabi, Woolley and Kaouri. Of about 17,000 plans, it removes 8,676: 7,843 invalid and 833 duplicates. That leaves 8,431. Code and data are at [github.com/emmashelley/ModRes](https://github.com/emmashelley/ModRes) under an MIT repo licence, and ResPlan attribution (CC BY 4.0) still applies. ([arXiv](https://arxiv.org/abs/2610.17178)) | Partly (the date was 10-12, and the licence was the paper's, not the data's) | **Action:** about half of ResPlan may be invalid or duplicated. Check our `reference/datasets/resplan` references against ModRes before relying on them. |
| 2026-10-15 | **RenoLayout**: an LLM turns an existing plan plus design points into an executable "Geometry-as-Code" program. It covers renovation and furniture layout, with a 200-case before-and-after benchmark. ([arXiv](https://arxiv.org/abs/2610.21366)) | Verified | Close to our "design as data" approach, but aimed at renovation. Use it as an idea source. |
| 2026-10-25 | **Pano2BIM** (NYU Abu Dhabi): a vision-language agent builds a LOD 200 IFC from a floor plan plus one 360° photo. The preliminary result is furniture IoU 0.53 against a 0.44 baseline, on one room. ([arXiv](https://arxiv.org/html/2611.00097)) | Unchecked (opened by the researcher, not by a checker) | Gulf-based team. The evidence is thin. |
| Before the window | GRE-Diff, a diffusion model on RPLAN ([arXiv](https://arxiv.org/abs/2607.08086)). Generative floor-plan design with LLMs via RL with verifiable rewards (arXiv 2605.14117, unchecked). AI floor-plan compliance checking (arXiv 2607.00015, unchecked). | Mixed | The verifiable-reward idea maps onto our Dubai Building Code validator. |

The conference proceedings for CVPR, ICCV, NeurIPS, SIGGRAPH Asia, CAADRIA, eCAADe and ACADIA 2026 were **not searched**.

## 3. Dubai and competing products

- **Dubai Municipality AI permitting for villas**, announced 2026-08-09 ([media office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)). Status: partly verified.
  - It covers private and investment villas.
  - It checks drawings against the Dubai Building Code: plot planning, architecture, MEP and structure.
  - It runs 26 weeks in 3 phases: develop and test, a pilot with selected consultancies, then full rollout on Build in Dubai.
  - Manual review stays for exceptional cases.
  - There is no news yet on the pilot or which consultancies are in it. On paper the 26 weeks end around early February 2027.
  - **This is the same job as our DBC validator. Track it.**
- **Snaptrude Agent**, 2026-10-29 ([AEC Magazine](https://aecmag.com/bim/snaptrude-agent-launches-for-bim-workflows/)). Status: partly verified.
  - It goes from site analysis and massing to a LoD 400 model with structure, MEP and drawings, with Revit export.
  - "2,000+ designers in early access" is a vendor figure from a Digg summary, not from AEC Magazine.
  - It also announced AECBench, with no scores published.
- **Autodesk at AU 2026** (September, [Architosh](https://architosh.com/2026/09/au2026-autodesk-expands-forma-and-leverages-ai/)). It showed Drawing Compliance Review with user-defined rule sets, Drawing Change Analysis, and a next-generation Assistant. A standalone Assistant is planned for 2027. No availability dates were given.
- **Civil 3D 2027.1** (blog URL dated 2026-10-20, unchecked): Assistant is open by default.
- **Dubai BIM e-submission circular** (effective April 2026, IFC upload of up to 150 MB): unverified, because the circular PDF did not open. Whether it applies to villas is unknown.

## 4. Claude platform

- **Claude Fable 5.2 and Mythos 5.2**, 2026-11-09, amended 11-11 ([announcement](https://www.anthropic.com/claude-fable-and-mythos-5-2), [pricing](https://platform.claude.com/docs/en/about-claude/pricing)). Status: verified.
  - Model ID `claude-fable-5-2`, $8/$40 per MTok, fast mode $16/$80, cache hits $0.20.
  - 1M context and 128K max output.
  - Mythos 5.2 is restricted.
  - The docs still recommend Opus 5.5 ($4/$20) as the default starting model.
- **Claude Code 2.1.329** (2026-11-19) is the latest ([changelog](https://code.claude.com/docs/en/changelog)). Status: partly verified. Items that matter for our MCP servers:
  - 2.1.323: the v1 MCP client is removed, and `MCP_SDK_GENERATION=v1` now runs v2 in compatibility mode. Project `.mcp.json` approvals must match the exact server name. On Windows, a `.exe` now wins over a same-named `.cmd` or `.bat` in the same PATH folder.
  - 2.1.319: MCP tool calls that a server runs as a task are backgrounded. `CLAUDE_CODE_DISABLE_MCP_TASKS=1` turns this off.
  - 2.1.318: stdio servers that die within 3 seconds are pinned to the legacy handshake for 7 days.
  - 2.1.311: subagents can now use MCP servers that finish connecting late.
  - 2.1.302: fixed servers on protocol 2026-07-28 showing no tools.
  - 2.1.326 and 2.1.327: `/mcp` shows why a stdio server failed, and `claude mcp add-json` was added.
  - **Checked on 2026-11-20:** both of our servers (`autocad` on mcp 2.2.0, `autocad-pro` on mcp 1.30.0 with fastmcp 3.4.7) are connected and listing tools.
- **Agent Skills was donated to the Agentic AI Foundation** (Linux Foundation), 2026-10-22 ([post](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)). It covers the standard, the name, the GitHub org and agentskills.io. Status: verified.
- **MCP spec**: 2026-07-28 is still current. The Python SDK's latest is 2.3.0 (2026-10-02). Status: unchecked.

## 5. Rendering

- **Blender 5.3**, released 2026-11-10 ([release notes](https://developer.blender.org/docs/release_notes/5.3/)). Status: verified.
  - Vulkan is the default on Windows (not ARM) and on Linux.
  - glTF import gains Gaussian splats and KTX2.
  - Cycles gains dispersion and anisotropic glass.
  - We are on 5.2, an LTS supported to 2028. Test our bpy scripts on a copy before moving.
- **Twinmotion 2026.2** is still Preview only, and it drops DXF import. Status: unchecked as final.
- **Enscape November 2026** (2026-11-04): AI assistant, 3D model generation (beta) and Veras built in. Status: unchecked, snippet only.
- **Unreal Engine 5.8** (2026-06-23) is the last major UE5 release and ships an experimental Unreal MCP plugin. Status: unchecked.

## 6. What to do

1. **ResPlan references:** compare `reference/datasets/resplan` with ModRes and drop the invalid and duplicate plans.
2. **autocad-mcp-pro:** decide on 1.8.0 after the upgrade-plan session reports. Keep 1.5.1 until then.
3. **ezdxf:** trial 1.4.5 after re-checking HATCH and MTEXT output.
4. **Watch:**
   - the Dubai Municipality AI permitting pilot
   - whether Autodesk opens its AutoCAD MCP to other clients
   - ODA save-back
   - Blender 5.3 against our scripts
   - Twinmotion 2026.2 final
5. **Skip for now:** Autodesk's AutoCAD MCP (Assistant only) and the ODA MCP (paid membership, no save-back).

## 7. Research quality

| Opus checker | Claims checked | Verified | Partly | Wrong or unverifiable |
|---|---|---|---|---|
| CAD tools, Dubai, Snaptrude | 6 | 2 | 4 | 0 |
| Papers, Claude, Blender, Agent Skills | 8 | 4 | 4 | 0 |

Items marked "Unchecked" above were not sent to a checker.

Gaps:
- Many Autodesk pages returned 403.
- The conference proceedings were not searched.
- The official MCP registry was not searched.
- Snaptrude's own launch post was not found.
- The Dubai BIM circular did not open.
- Changelog sections 2.1.307 and 2.1.319 were only partly read.
