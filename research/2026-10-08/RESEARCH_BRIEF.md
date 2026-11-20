# Research brief: what the pipeline needs to know (2026-10-08)

**Scope.** This brief covers recent changes (mostly April to October 2026) relevant to our pipeline: design data validated against the Dubai Building Code (DBC); ezdxf sheets; AutoCAD Architecture 2027 over COM via two MCP servers (our custom `autocad` server and U-C4N "AutoCAD MCP Pro"); build123d glTF; Blender Cycles, UE 5.8 path tracing and a manual Twinmotion step; and the `architectural-cad` skill with Claude Code subagents and workflows.

**Method.** Five Haiku 5.5 researchers (`claude-haiku-5-5`) produced 112 findings. An Opus 5.5 validator (`claude-opus-5-5`) checked every finding and added 28 items the researchers missed. This brief uses only findings rated *verified* or *partly true*, in their corrected form, plus the validators' missed items.

**Dropped (3 of 112).** One finding was **wrong**: the claim that no Haiku 5.5 benchmark numbers exist (routing angle, A2). Two were **unverifiable**: AutoCAD COM troubleshooting figures from a dead Glama URL (autocad angle, A13), and the CLAUDIUS Fab listing (rendering angle, A21). No finding was fabricated.

**Labels.** *Official* means a vendor's own doc, blog or press release. *Community* means GitHub, forum or practitioner posts. *Secondary* means news or aggregators. *Vendor-reported* means the vendor's own benchmark, not independently measured.

**On your Haiku question.** The researchers' Haiku 5.5 facts came from the Haiku 5.5 pages, not Haiku 4.5 ones. One exception: the routing researcher claimed no Haiku 5.5 numbers exist, which is wrong; the Anthropic launch post has them. Several widely quoted Haiku numbers (SWE-bench 73.3%, Terminal-Bench 41%, the tau2 scores, the PlanarBench score) describe **Haiku 4.5**. Any earlier routing assumption built on those should be re-based on the 5.5 figures in section 5.

---

## 1. What changed recently (newest first)

| # | Date | Development | Why it matters to us | Source |
|---|---|---|---|---|
| 1 | 2026-10-07 | **Claude Haiku 5.5 released** (`claude-haiku-5-5`): 1M context, 128K output, effort levels (default medium), $0.10/$0.50 per MTok up to 100K-token prompts. Claude Code 2.1.293 makes it the default Haiku, **but only on the Anthropic API**. On Bedrock, Google Cloud, Foundry and Claude Platform on AWS, the `haiku` alias still resolves to Haiku 4.5. (Official) | A bare `haiku` in a subagent or workflow can silently run 4.5. Pin the full ID. | [Haiku 5.5 overview](https://platform.claude.com/docs/en/models/haiku-5-5/overview), [model-config](https://code.claude.com/docs/en/model-config), [changelog](https://code.claude.com/docs/en/changelog) |
| 2 | 2026-10-01 to 10-06 | **Claude Code 2.1.287 to 2.1.292:** local stdio MCP servers now negotiate protocol 2026-07-28 by default (`MCP_PROTOCOL_NEGOTIATION=legacy` opts out); a tool name over 128 characters is dropped with an error; `alwaysLoad: false` defers a server's tools behind tool search; the Agent tool takes `effort`. (Official) | Both AutoCAD servers are stdio and large (autocad-pro advertises about 240 tools). They may break, or flood context, under the new defaults. | [changelog](https://code.claude.com/docs/en/changelog) |
| 3 | 2026-09-30 | **ezdxf 1.4.5b1** pre-release; 1.4.4 (2026-05-14) is still the latest stable. PyPI states Python >=3.10. (Official) | It is our sheet generator, and 1.4.5 is close to release. | [PyPI ezdxf](https://pypi.org/project/ezdxf/) |
| 4 | 2026-09-22 to 09-30 | **Opus 5.5 (Sep 22) and Sonnet 5.5 (Sep 28):** the API rejects (HTTP 400) thinking-disabled or budget_tokens on Opus 5.5, and forced `tool_choice` on both (Haiku 5.5 and Fable 5.1 differ). Python SDK v1.0+ removes `temperature`/`top_p`/`top_k` and raises a TypeError. **Sonnet 4.5 was deprecated Sep 30 and retires Nov 30, 2026.** Haiku 4.5 is still Active: Oct 15 is only a "not sooner than" floor, no deprecation notice exists, and the 60-day notice rule applies. (Official) | Any Python harness with 4.x-style parameters will fail. Sonnet 4.5 pins break on Nov 30. | [Opus 5.5 what's new](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5), [Sonnet 5.5 what's new](https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5), [deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) |
| 5 | 2026-09-29 | **Autodesk Revit MCP update:** separate Read, Read+Write and Read+Write+Experimental installers (Revit 2027.2+, Technical Preview, local stdio; no approval step, backups advised). Autodesk's MCP docs also list an **"AutoCAD and Civil 3D MCP Server"**: Tech Preview (Public Beta), local, with Autodesk Assistant as the only supported client and read and analysis tools only for AutoCAD. (Official) | AutoCAD now has an official MCP server, but it is read-only and not open to external clients, so our authoring servers stay necessary. The read/write split is a pattern to copy. | [Revit MCP update](https://blog.autodesk.io/revit-mcp-server-update/), [Autodesk MCP docs](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html) |
| 6 | 2026-09-23 / 09-24 | **autocad-mcp-pro 1.6.0** (Sep 24): MIT, COM plus ezdxf. Defaults: raw command and LISP guarded only by a 36-verb denylist the project calls a guardrail; `ALLOWED_PATHS` empty, with a system-directory denylist that does not cover C:/Users. **best-cad-mcp 1.7.2** (Sep 23) documents the clearest safety model: scan, plan, validate, dry-run, then transactional execute, with client approval for delete, purge, raw command, save, close, audit and execute. (Community) | autocad-pro is one of our two servers, and its defaults are open. best-cad-mcp is the pattern to borrow, not a server to install beside ours. | [PyPI autocad-mcp-pro](https://pypi.org/project/autocad-mcp-pro/), [GitHub U-C4N/Autocad-MCP](https://github.com/U-C4N/Autocad-MCP), [PyPI best-cad-mcp](https://pypi.org/project/best-cad-mcp/) |
| 7 | 2026-09-22 | **Blender 5.3 adds native Gaussian splats** (PLY, SPZ and USD import; renders in Cycles and EEVEE; no export). Final release expected **2026-11-10**. (Secondary) | Site-context scans could go straight into Cycles renders with no add-on. | [Digital Production](https://digitalproduction.com/2026/09/22/blender-5-3-brings-gaussian-splats-home/) |
| 8 | 2026-08-31 | **Chaos Veras 5.0 "Image to 3D":** free Cosmos asset match, or HY3D/Trellis2 generation (credit cost not stated), exported to Revit, SketchUp and Rhino at scale. Since May 27, Veras is bundled in Enscape, V-Ray and Corona, and AI and cloud features draw on credits. (Official) | First mainstream image-to-BIM-geometry path. Generated geometry must never bypass `villa_validate`, and per-call cost is unknown. | [Veras 5.0](https://blog.chaos.com/veras-5.0), [Chaos press release](https://www.chaos.com/press/veras-ai-architecture-enscape-vray-corona) |
| 9 | 2026-08-17 | **ODA MCP Servers:** pre-release, covering DWG/DXF, STEP and IFC over STDIO or TLS HTTP. Read and analysis tools, renders and basic writes; FAQ claims DWG save-back. FAQ says launch in September 2026, from the Sustaining membership tier up. **No "now available" post found.** (Official, pre-release) | Possible AutoCAD-free DWG reading and checking for CI. Paid and not confirmed shipped. | [ODA MCP Servers](https://opendesign.com/products/mcp-servers), [ODA FAQ](https://www.opendesign.com/blog/2026/august/oda-mcp-servers-faq.md) |
| 10 | 2026-08-09 | **Dubai Municipality is building an AI villa-permit checker.** It reviews plot planning, architecture, MEP and structure against the DBC, cross-checks drawings, and offers pre-submission self-checks. Rollout is 26 weeks in three stages ending in Build in Dubai integration. No report found that the pilot has started. (Secondary, citing an official release) | This is the official direction for exactly what our validator does. Our output format should anticipate it. | [Khaleej Times](https://www.khaleejtimes.com/uae/dubai-ai-system-villa-construction-permits) |
| 11 | 2026-07-28 | **MCP specification 2026-07-28 final:** removes sessions, `Mcp-Session-Id` **and the initialize handshake** (this affects stdio too); requires `server/discover`; deprecates Roots, Sampling and Logging; removes SSE resumability. (Official) | Our custom server and autocad-pro need an SDK and compatibility check (see row 2). | [MCP spec changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) |
| 12 | 2026-07-24 | **CVE-2026-66004** in ahujasid/blender-mcp (about 30.2K stars): path traversal in the Poly Haven download, reachable by prompt injection; CVSS 4.0 score 6.0; fixed from commit 30a3308. The official **Blender Lab MCP** server (v1.0.3, Blender 5.1+) is the code behind Anthropic's Blender connector. It also runs LLM-generated code without guards, and Blender recommends a VM. (Official / CVE) | Any Blender MCP in the render leg needs pinning and isolation. The official server is not safer. | [cvefeed CVE-2026-66004](https://cvefeed.io/vuln/detail/CVE-2026-66004), [Blender Lab MCP](https://www.blender.org/lab/mcp-server/), [Anthropic: Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work) |
| 13 | 2026-07-14 | **Blender 5.2 LTS** (supported to July 2028): Cycles texture cache (less memory, more disk space, small speed cost) and Principled BSDF Thin Wall. 5.2.1 (Aug 25) and 5.2.2 (Sep 15) are broad bug-fix releases, including texture-cache and NVIDIA 50-series fixes. (Official) | A stable Cycles target for the villa stills. | [Blender 5.2](https://www.blender.org/releases/5-2/) |
| 14 | 2026-06-17 / 06-19 | **UE 5.8 ships an experimental Unreal MCP plugin**: HTTP and SSE only at `127.0.0.1:8000/mcp`, no authentication, calls serialised on the game thread. **Epic also publishes an official Claude Code skill plugin** for it. 5.8 also makes MegaLights and Movie Render Graph production-ready. (Official) | A first-party route for Claude Code to drive our UE 5.8 render scenes. | [Unreal MCP doc](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor), [Epic Claude Code skill](https://github.com/epicgames/unreal-engine-skills-for-claude-code-plugin), [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes) |
| 15 | 2026.2 Preview (undated) | **Twinmotion 2026.2 Preview drops DXF** (plus 3DS, C4D, DAE and STL) and removes the legacy importer. Legacy-imported assets cannot be reimported, so they must come in again from source as FBX, OBJ, glTF, GLB or SKP. Still no AI or automation API. (Official) | Any DXF handoff into our manual Twinmotion step will break on upgrade. glTF is already our format. | [Twinmotion 2026.2 Preview notes](https://dev.epicgames.com/documentation/twinmotion/twinmotion-2026-2-preview-release-notes) |

---

## 2. Adopt / test / watch (ranked)

Effort: **S** is under half a day, **M** is one to three days, **L** is more than a week. Payoff is for this pipeline.

### Adopt now

| Rank | Action | Effort | Payoff | Source |
|---|---|---|---|---|
| 1 | **Pin full model IDs and effort everywhere.** Set `model: claude-haiku-5-5` (Bedrock: `anthropic.claude-haiku-5-5`) and an explicit `effort` in every `.claude/agents` frontmatter and every workflow `agent()` call. Log the model and effort that actually ran. Note that `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` overrides frontmatter. Upgrade to Claude Code ≥2.1.293. | S | High: stops silent Haiku 4.5 use on cloud providers, and makes effort, which changes Haiku 5.5's capability, explicit. | [model-config](https://code.claude.com/docs/en/model-config), [sub-agents](https://code.claude.com/docs/en/sub-agents), [workflows](https://code.claude.com/docs/en/workflows) |
| 2 | **Make both AutoCAD servers work under MCP 2026-07-28.** Smoke-test the custom `autocad` server and autocad-pro under Claude Code's default negotiation, with `MCP_PROTOCOL_NEGOTIATION=legacy` as the fallback. Check that tool names are ≤128 characters. Set `alwaysLoad: false` for autocad-pro. | M | High: avoids a broken toolchain and saves context. | [changelog](https://code.claude.com/docs/en/changelog), [spec changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) |
| 3 | **Harden autocad-pro.** Leave `DANGEROUS_COMMANDS_ENABLED` unset, set `ALLOWED_PATHS` to the project folder, and keep stdio (no HTTP). Never run it against the same AutoCAD session as our server. | S | High: closes arbitrary LISP and unscoped file access. | [PyPI autocad-mcp-pro](https://pypi.org/project/autocad-mcp-pro/) |
| 4 | **Add plan → dry-run → approve to our own server, and split read from write.** Borrow best-cad-mcp's flow and Erfouni/AutoCAD-AI's defaults: `acad_send_command` off behind a flag, file writes scoped to the project folder, every call logged with its arguments. Put `dxf_*`, `villa_validate` and `acad_list_*` in a read-only server that can run without the write server, following Autodesk's Revit Read/Write split. Wrap each write batch with an UNDO mark **and** a saved scratch copy, because best-cad-mcp itself calls undo-mark rollback best-effort. | M | High: safety for agent-driven writes. | [best-cad-mcp](https://pypi.org/project/best-cad-mcp/), [Erfouni/AutoCAD-AI](https://github.com/Erfouni/AutoCAD-AI), [Revit MCP update](https://blog.autodesk.io/revit-mcp-server-update/) |
| 5 | **Purge 4.x-era API parameters from Python code.** Remove `budget_tokens`, `temperature`/`top_p`/`top_k`, assistant prefill and forced `tool_choice` (use `auto` plus strict tools or structured outputs). Handle `stop_reason: refusal`. Recount token budgets, because Haiku 5.5's tokenizer uses about 30% more tokens for the same text. | S–M | High: prevents 400s and TypeErrors. | [Haiku 5.5 migration guide](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide), [deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) |
| 6 | **Add an LLM-written AutoLISP checklist to the skill.** Require: an error handler that restores OSMODE, CMDECHO and CLAYER; an UNDO group; an explicit layer; no raw points under running osnaps; a scratch DWG only. Also check every called symbol against the AutoLISP function list, because chatbots sometimes invent function names. | S | Medium-high | [Draftsperson, Jul 25](https://blog.draftsperson.net/claude-autocad-mcp-autolisp/), [Draftsperson, Jul 26](https://blog.draftsperson.net/does-autodesk-ai-write-autolisp/) |
| 7 | **Reshape validator output for the Dubai Municipality checker.** Report rule by rule, citing the DBC article and page, with pass/fail and the measured value. Ask consultancy contacts about entry to the pilot. | M | High (strategic) | [Khaleej Times](https://www.khaleejtimes.com/uae/dubai-ai-system-villa-construction-permits) |

### Test next

| Rank | Action | Effort | Payoff | Source |
|---|---|---|---|---|
| 8 | **In-house Haiku 5.5 routing eval.** Build 30 to 50 tasks from the pipeline (tool-argument validity, COM call sequences, rule-by-rule classification, room-adjacency JSON). Run each on Haiku 5.5 at medium and at max effort, and on Sonnet 5.5. Route only the task classes where Haiku matches Sonnet. | M | High: Sonnet 5.5 costs 20x as much as Haiku 5.5 on list input. | [Haiku 5.5 announcement](https://www.anthropic.com/claude-haiku-5-5), [cost guide](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence) |
| 9 | **Per-sheet check workflow.** Haiku 5.5 extracts, Sonnet 5.5 judges, with model IDs pinned. Set `workflowSizeGuideline` deliberately: the default concurrency is 16, a warning appears above 25 agents or 1.5M tokens, and a run allows at most 1,000 agents. Ship it in the skill or plugin `workflows/` folder. | M | Medium-high | [workflows doc](https://code.claude.com/docs/en/workflows) |
| 10 | **Unreal MCP plus Epic's Claude Code skill** on a copy of the UE 5.8 render project. Run one import and one capture job. Keep it on loopback, serialise calls, and watch for a port 8000 clash. On Windows the skill needs Git Bash or WSL. | M | Medium-high | [Unreal MCP](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor), [Epic skill](https://github.com/epicgames/unreal-engine-skills-for-claude-code-plugin) |
| 11 | **ezdxf 1.4.5b1** in a scratch venv: run the sheet generator and the Dubai checks; keep 1.4.4 pinned in production. | S | Medium | [PyPI ezdxf](https://pypi.org/project/ezdxf/) |
| 12 | **Move the Twinmotion handoff to GLB/glTF** (or FBX/SKP) before adopting 2026.2, and remove any DXF path. | S | Medium | [Twinmotion 2026.2 Preview](https://dev.epicgames.com/documentation/twinmotion/twinmotion-2026-2-preview-release-notes) |
| 13 | **Blender MCP, only if wanted.** Use either Blender Lab MCP or ahujasid pinned at or after commit 30a3308 with safe mode on and Poly Haven downloads off. Run on a scene copy as a low-privilege user or in a VM. Separately, test the Cycles texture cache on and off in 5.2 LTS. | S–M | Medium | [Blender Lab MCP](https://www.blender.org/lab/mcp-server/), [CVE](https://cvefeed.io/vuln/detail/CVE-2026-66004), [Blender 5.2](https://www.blender.org/releases/5-2/) |
| 14 | **ifcopenshell-mcp** (`pip install ifcopenshell-mcp[mcp]`, command `ifcmcp`, in the official IfcOpenShell repo, LGPL-3.0+) if we export IFC from AutoCAD Architecture. Try `ifc_validate`, `ifc_clash` and `ifc_plot` (2-D). Add checks for IfcSpace, openings, property sets and wall connectivity, the gaps MCP4IFC found in LLM-generated IFC. | S–M | Medium | [IfcOpenShell (official repo)](https://github.com/IfcOpenShell/IfcOpenShell), [MCP4IFC](https://arxiv.org/html/2511.05533v1) |
| 15 | **Grounding and probes.** Attach Autodesk's Product Help MCP (listed as GA in Autodesk's MCP docs) read-only to the COM/LISP-writing subagent. On the AutoCAD 2027 box, probe read-only whether Claude Code can reach the embedded AutoCAD MCP server. Autodesk lists Assistant as the only supported client, so expect a no. | S | Medium | [Autodesk MCP docs](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html), [DE247 Product Help MCP](https://www.digitalengineering247.com/article/autodesk-unveils-product-help-mcp-server/Autodesk), [AutoCAD 2027 + agentic AI](https://blog.autodesk.io/autocad-2027-and-agentic-ai/) |
| 16 | **Skill refactor.** Keep `SKILL.md` under 500 lines, move scripts under `${CLAUDE_SKILL_DIR}/scripts` with matching `allowed-tools`, and try `context: fork` with a pinned Haiku 5.5 model for validation passes. | M | Medium | [skills doc](https://code.claude.com/docs/en/skills) |
| 17 | **TUM EC3 2026 paper** (code and data on GitHub): use its LLM-written compliance-function approach only where we have gold cases. Keep geometric rules hand-coded. | M | Medium | [EC3 2026 paper 318](https://ec-3.org/publication/ec32026_318/) |
| 18 | **Render AI extras, manual only:** single-photo PBR for villa finishes (V-Ray 7 Update 4) and Veras 5.0 Image to 3D. Get Chaos credit prices before any automation. | S | Low-medium | [Architosh](https://architosh.com/2026/07/looking-at-chaos-v-ray-7-update-4/), [Veras 5.0](https://blog.chaos.com/veras-5.0) |

### Watch

- **ODA MCP Servers.** Ask ODA whether they have shipped and which membership tier is needed ([FAQ](https://www.opendesign.com/blog/2026/august/oda-mcp-servers-faq.md)). Pin the ODA File Converter version; the platform is now on the 27.x line (27.4 dated May 15, 2026 per search; secondary).
- **LibreDWG.** Use for reads only, with a 0.14 nightly in a sandbox: 0.13.4 has CVE-2026-15184 ([OpenCVE](https://app.opencve.io/cve/CVE-2026-15184)).
- **Blender 5.3 (2026-11-10)** for native splats ([Digital Production](https://digitalproduction.com/2026/09/22/blender-5-3-brings-gaussian-splats-home/)). Stay on 5.2 LTS until then.
- **AutoCAD 2027.1 Assistant** now answers about the current selection (Count, Query) but still cannot author ([CADTutor repost, Aug 4](https://www.cadtutor.net/forum/topic/99229-autocad-20271%C2%A0now-available-smarter%C2%A0autodesk%C2%A0ai-assistance%C2%A0and%C2%A0smoother-collaboration%C2%A0/)).
- **Research to read:**
  - ARCHER, agentic checker generation, waiting for a code release ([arXiv 2607.25566](https://arxiv.org/abs/2607.25566)).
  - Architect-Ant, rule-scored furniture layout ([arXiv 2606.10953](https://arxiv.org/abs/2606.10953)).
  - Agentic Designer, generator/evaluator/refiner layout ([arXiv 2607.20866](https://arxiv.org/abs/2607.20866)).
  - AgentRouter ([arXiv 2609.22951](https://arxiv.org/abs/2609.22951)).
- **Not for the pipeline:**
  - Lumion, D5 and Enscape have no automation API found ([Lumion 2026.1](https://support.lumion.com/knowledge-base/api/v2/help-center/en-us/articles/lumion-2026.1-release-notes), [D5 3.0](https://www.d5render.com/posts/d5-render-3-0-ai-rendering-design-workflow)).
  - Trimble's SketchUp connector produces .skp files in a cloud session ([Trimble](https://news.trimble.com/2026-04-28-Trimble-Links-SketchUp-with-Anthropics-Claude,-Bringing-New-Conversational-AI-powered-Capabilities-to-3D-Modeling)).
  - Krea and LookX are concept tools only.

---

## 3. Where we are already ahead / behind

The "behind" items are written as conditional ("unless already done"), because the research did not inspect our code.

**Ahead**
- **Data-first design with deterministic, code-cited validation.** The literature backs this split:
  - LLMs write rule code reasonably well ([arXiv 2506.20551](https://arxiv.org/pdf/2506.20551v1)) but are weak on code tables and multi-step calculation ([AECBench, arXiv 2509.18776](https://arxiv.org/abs/2509.18776)).
  - Geometric checks that need auxiliary constructions stay hard ([EC3 2026](https://ec-3.org/publication/ec32026_318/)).
  - Frontier models break physical layout constraints ([FloorplanQA](https://arxiv.org/abs/2507.07644)).
  - Practice elsewhere is still prototype-stage ([AIA thread](https://communityhub.aia.org/discussion/mcp-bim-equals-exciting-opportunities)).
  - Dubai Municipality is now building the same kind of checker ([Khaleej Times](https://www.khaleejtimes.com/uae/dubai-ai-system-villa-construction-permits)).
- **AutoCAD authoring through MCP.** Autodesk's own AutoCAD MCP server is read-only and Assistant-only ([Autodesk MCP docs](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html)), and AutoCAD 2027's Assistant cannot create or edit content ([Autodesk dev blog](https://blog.autodesk.io/autocad-2027-and-agentic-ai/)).
- **A single COM lock with busy retry.** This matches the best practice others document: best-cad-mcp serialises COM on one thread under the same Windows user ([PyPI](https://pypi.org/project/best-cad-mcp/)), and Unreal MCP serialises calls on the game thread ([Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor)). Most community AutoCAD servers document no lock ([Porta048](https://github.com/Porta048/AutoCad-MCP), [puran-water](https://github.com/puran-water/autocad-mcp)).
- **Scripted path-traced renders.** Chaos, D5, Lumion and Twinmotion still expose no scripting or MCP surface that the researchers found, so our scripted Blender and UE renders are more automatable than most archviz stacks.

**Behind, or at risk**
- **No dry-run or approval gate on write tools, and read and write tools mixed in one server**, unless already in place. best-cad-mcp and Autodesk's Revit split are now the reference ([best-cad-mcp](https://pypi.org/project/best-cad-mcp/), [Revit MCP update](https://blog.autodesk.io/revit-mcp-server-update/)).
- **autocad-pro defaults** (open LISP and unscoped paths) unless already hardened ([PyPI](https://pypi.org/project/autocad-mcp-pro/)).
- **MCP 2026-07-28 compatibility** for both servers is untested, and Claude Code now negotiates that protocol version by default ([changelog](https://code.claude.com/docs/en/changelog)).
- **Model pinning.** Any `haiku` alias, Haiku 4.5 assumption, or Sonnet 4.5 pin (retiring Nov 30) in agents, workflows or the skill ([model-config](https://code.claude.com/docs/en/model-config), [deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)).
- **Rollback relies on AutoCAD undo.** Others treat undo-mark rollback as best-effort, so we need file snapshots per batch ([best-cad-mcp](https://pypi.org/project/best-cad-mcp/)).
- **No IFC check path**, if we deliver IFC; ifcopenshell-mcp exists in the official IfcOpenShell repo ([IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell)).
- **UE automation** is not yet on Epic's first-party MCP or its Claude Code skill ([Epic skill](https://github.com/epicgames/unreal-engine-skills-for-claude-code-plugin)).
- **Vision checks.** Anthropic says Opus 5.5 reads dense charts and layout-dependent visuals much more precisely. If our screenshot or render checks run on Haiku, we may be under-using that ([Opus 5.5 what's new](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5)).
- **Twinmotion stays manual.** No vendor offers an automation API, so nobody is ahead here, but a DXF handoff would break under 2026.2 ([Twinmotion](https://dev.epicgames.com/documentation/twinmotion/twinmotion-2026-2-preview-release-notes)).

---

## 4. How good was Haiku 5.5 as a researcher?

Researcher: `claude-haiku-5-5` (self-reported from its system prompt). Validator: `claude-opus-5-5`.

| Angle | Findings | Verified | Partly true | Wrong | Unverifiable | Fabricated | Date accuracy | Missed (validator) |
|---|---|---|---|---|---|---|---|---|
| autocad-mcp | 20 | 11 | 8 | 0 | 1 | 0 | 18/20 | 7 |
| cad-bim-mcp | 22 | 16 | 6 | 0 | 0 | 0 | 22/22 | 5 |
| rendering | 23 | 13 | 9 | 0 | 1 | 0 | 20/23 | 5 |
| claude-platform | 23 | 18 | 5 | 0 | 0 | 0 | 23/23 | 6 |
| routing-and-archai | 24 | 18 | 5 | 1 | 0 | 0 | 23/24 | 5 |
| **Total** | **112** | **76 (68%)** | **33 (29%)** | **1 (1%)** | **2 (2%)** | **0** | **106/112 (95%)** | **28** |

The validators' reviews agreed on the following.

**Strengths**
- **No fabrication.** Version numbers, dates, star counts, prices, benchmark tables and changelog entries from opened pages were transcribed precisely.
- **Honest labelling.** It marked snippet-only evidence, lowered confidence on it, and flagged source conflicts itself.
- **Good recency.** Most items were dated September to October 2026.

**Weaknesses**
- **Stops one hop short of the primary source.** It missed:
  - Autodesk's MCP docs hub, and so concluded "no official AutoCAD MCP";
  - the official workflows doc, leaving availability and limits "unconfirmed";
  - the Haiku 5.5 launch post: it read only a page with an image chart and wrongly concluded no 5.5 numbers exist, which is its only "wrong" verdict;
  - the official IfcOpenShell repo, labelling ifcmcp "mirror only";
  - McNeel's own GitHub org (mcneel/RhinoAI).
- **Leaves easy verifications open.** CVE-2026-66004 and Blender 5.3 native splats were each one search away.
- **Over-reads vendor tables and dates.** Two separate researchers read Haiku 4.5's "not sooner than Oct 15" floor as an imminent retirement. Another trusted an April source over a newer, correct vendor claim, the Vagon statement about Autodesk's server.
- **Small embellishments.** Examples: "saved workflows" in Veras 5.0, "competition for light" in UE 5.8's vegetation editor, Maket zoning and DXF export, and mixed Terminal-Bench 2.0 and 2.1 numbers.
- **Coverage gaps in our own stack.** The cad-bim researcher missed Unreal MCP and Blender Lab MCP, and the rendering researcher missed Epic's Claude Code skill.

**Verdict**
- **Good enough alone for:** extracting facts from a known set of pages, such as release notes, PyPI versions, changelogs, spec diffs and price tables; catalogue sweeps (repos, licences, star counts) where a missed item is acceptable; and first-pass landscape scans.
- **Needs a verifier for:**
  - **negative claims** ("X does not exist", "no official server");
  - **official-status and recency questions** about vendors;
  - **security items**;
  - **deprecation and date inferences**;
  - **resolving conflicts between sources**;
  - **any finding that drives a decision.**
- **Cheap fixes for a Haiku-only run:**
  - make "open the vendor's docs hub and the dated launch post" a required step;
  - treat every "none found" as unverified;
  - route high-relevance findings to an Opus or Sonnet check, which here cost one validator pass per angle and changed several conclusions.

---

## 5. Evidence for model routing

**Haiku 5.5's own numbers** (Oct 7, 2026; vendor-reported; [Anthropic](https://www.anthropic.com/claude-haiku-5-5)). Scores are Haiku 5.5 vs Sonnet 5.5, with Haiku 4.5 in brackets where reported:

| Benchmark | Haiku 5.5 | Sonnet 5.5 | Haiku 4.5 |
|---|---|---|---|
| Terminal-Bench 4.0 | 39.2% | 70.6% | 0.0% |
| OSWorld 2.1 offline subset | 72.4% | 83.9% | 15.7% |
| HLE with tools | 57.4% | 64.5% | 18.7% |
| GDPval-AA (Elo) | 1620 | 1840 | 735 |
| FrontierCode 1.1 | 46.4% | 52.1% | n/a |
| Chartography | 46.4% | 61.6% | 6.4% |

- **Anthropic's positioning:** Haiku for summaries, classification, lookups and subagents; Sonnet or Opus 5.5 for complex agentic coding.
- **Effort matters.** Press coverage says the 39.2% Terminal-Bench score is at max effort and about 20% at medium (secondary, not on the Anthropic page).
- **Independent listing:** Artificial Analysis puts Haiku 5.5 (medium) at 34 on its Intelligence Index, rank 15 of 182, at about 137 tokens/s with about 12.6 s to first token ([Artificial Analysis](https://artificialanalysis.ai/models/claude-haiku-5-5-medium)).
- **Do not reuse Haiku 4.5 numbers for 5.5.** SWE-bench Verified 73.3% and Terminal-Bench (about 41%) are Haiku 4.5 launch figures ([TechCrunch](https://techcrunch.com/2025/10/15/anthropic-launches-new-version-of-scaled-down-haiku-model)).

**Cost**
- List prices per MTok (input/output): Haiku 5.5 $0.10/$0.50 (≤100K-token prompts; $0.50/$2.50 above), Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, Fable 5.1 $10/$50. Batch is 50% off ([pricing](https://platform.claude.com/docs/en/about-claude/pricing), [models overview](https://platform.claude.com/docs/en/models/overview)).
- Fable 5.1 carries 30-day data retention, which matters for client data ([Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1)).

**Orchestration patterns (measured)**
- **Anthropic's cost guide:**
  - A Haiku 5.5 executor with an Opus 5.5 advisor consulted it 0 times on 198 GPQA questions, while the advisor tool alone added about 1,000 tokens per request (+12% cost).
  - A Fable 5.1 coordinator over 25 Sonnet 5 workers cost 47–55% less than Fable alone but scored 10–12 points lower.
  - Advice: start with Opus 5.5 and sweep effort before switching models ([cost guide](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)).
- **Minions/MinionS:** when a frontier model decomposes the work and a small model runs the chunks, cost fell 5.7x with 97.9% of quality kept. Naive back-and-forth chat kept only about 87% ([arXiv 2502.15964](https://arxiv.org/abs/2502.15964)).
- **AgentRouter:** per-step learned routing cut cost 72% with 97.3% of quality kept, on unnamed models in the authors' own tests ([arXiv 2609.22951](https://arxiv.org/abs/2609.22951)).
- **Anthropic multi-agent research system:** a lead with subagents beat a single agent by 90.2% on an internal eval but used about 15x chat tokens, and coding is a weaker fit ([Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)).
- **ARCHER:** an open-weights model reached 97.8% of frontier accuracy at about a quarter of the cost on BIM-checker generation (self-reported; [arXiv 2607.25566](https://arxiv.org/abs/2607.25566)).

**Where small models fail (spatial and AEC)**
- **PlanarBench**, 32k thinking budget, all 4.5-generation models: Haiku 4.5 scored 83.5, Sonnet 4.5 112.5 and Opus 4.5 144.0 out of 199 on constrained spatial drawing. Edge count predicts failure (r = −0.85) ([arXiv 2606.02010](https://arxiv.org/abs/2606.02010)).
- **IFC querying:** GPT-5 mini scored 83.1% and Sonnet 4.5 75.4%, and the tool definitions alone cost about 40k tokens ([MCP4IFC](https://arxiv.org/html/2511.05533v1)).
- **Tmax-9B**, a small open model at 27% on Terminal-Bench 2.0, is described by its authors as performing similarly to Haiku 4.5 ([arXiv 2606.23321](https://arxiv.org/pdf/2606.23321)).
- **Blueprint-Bench:** most models were at or below a random baseline on photo-to-plan, and agent refinement loops gave no meaningful gain ([arXiv 2509.25229](https://arxiv.org/abs/2509.25229)).
- **Haiku 5.5 failure modes** from Anthropic's prompting guide: at low effort it stops early and skips checks; medium is the agentic default; it needs an explicit "run a real check" instruction. Haiku 5.5 accepts forced `tool_choice`, which Opus, Sonnet and Fable reject ([Haiku 5.5 prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5)).

**Implied routing for this pipeline.** These are hypotheses; confirm each with the in-house eval in section 2, row 8.

| Stage | Suggested model | Basis |
|---|---|---|
| DXF text and entity extraction, sheet inventories, rule lookups, summaries | Haiku 5.5, medium effort, pinned ID | Anthropic positioning; 20x price gap |
| Applying a rule to a room or sheet, where deterministic code does the geometry | Haiku 5.5 executing chunks; Sonnet 5.5 decomposing | MinionS; AECBench / EC3 |
| Writing COM, AutoLISP or ezdxf code; multi-step tool sequences | Sonnet 5.5 | Terminal-Bench 4.0 gap (39% vs 71%) |
| Layout, adjacency and circulation reasoning; redesign judges | Sonnet or Opus 5.5, with deterministic checks always gating | PlanarBench, FloorplanQA, Blueprint-Bench |
| Screenshot and render checks against design data | Opus 5.5 (benchmark first) | Opus 5.5 vision claim |
| Fable 5.1 or advisor escalation | Only where the eval shows a gain; check data retention | Cost guide; Fable 30-day retention |
| Geometry, areas, code-table values | Deterministic code, never model memory | AECBench, EC3 2026 |
