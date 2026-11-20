# CAD + AI: what's new since 2026-10-08 (as of 2026-10-16)

Scope: the window is 2026-10-07 to 2026-10-16. "Verified" means an Opus check confirmed it, with the corrected wording used where Opus corrected it. "Unchecked" means it was not checked and is low-stakes. Wrong, fabricated and unverifiable findings are dropped. Rendering and pool-safety items from the researchers were mostly pre-window, so they appear as status or reference, not as news.

## 1. New skills, plugins and Claude Code features

**New this week (all verified unless marked)**

| Date | Item | Adopt? |
|---|---|---|
| 2026-10-15 | **Claude Code 2.1.301.** Adds `CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS` for unattended retries. Fixes skills vanishing after `/rewind`, workflow scripts refused after a Bash `cd`, and a case where switching to a smaller-context model could spend usage credits. OTel `tool_decision` now carries `classifier_verdict` and `permission_mode`. [Changelog](https://code.claude.com/docs/en/changelog) | Yes, after checking the installed build. The `cd` and usage-credit fixes matter for long unattended runs. |
| 2026-10-14 | **2.1.299.** The `skill.prompt` mod hook now gets skill frontmatter, source, plugin name and path. `claude plugin eval` gains `--disallow-tools`. New `/usage` warnings (max effort, workflows, large tool results). Adds `CLAUDE_CODE_DISABLE_FILE_MENTIONS`. Conversations over 200K tokens idle about 54 minutes are compacted. [Changelog](https://code.claude.com/docs/en/changelog) | Yes. Try `plugin eval --disallow-tools` on the architectural-cad skill evals. |
| 2026-10-14 | **2.1.300.** Workflow agents can have their prompt and model rewritten in the `agent.spawn` mod hook, which could previously only refuse agents. The `/advisor` command is on the primary changelog. It only runs once you choose an advisor via `/advisor`, `advisorModel` or `--advisor`. [Changelog](https://code.claude.com/docs/en/changelog) | Optional. Useful if you want hook-level control of which model each workflow agent gets. |
| 2026-10-09 | **2.1.296.** Adds `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL`, which runs every workflow agent on one model. Other subagents keep their own model. Adds `autoCompactWindow` for subagent frontmatter and `--agents`. Reprices Sonnet 5.5 cache reads to $0.10/Mtok in `/cost`, the status line, `--max-budget-usd` and SDK figures. [Changelog](https://code.claude.com/docs/en/changelog) | Yes, with care. Do not set the env var globally, or it overrides the Haiku/Sonnet/Opus routing for workflow-run `cad-*` agents. |
| 2026-10-08 | **2.1.295.** Subagents preload at most 32 skills from the `skills` field. The Skill tool can still invoke the rest. `claude plugin install/enable/disable/marketplace add` now warn when their target settings file does not load. Fixes forked skills called from Workflow subagents sending results to the main conversation. Fixes a skill's `allowed-tools`/effort being dropped, which denied Bash in `-p` runs. Adds `onFailure: 'block'` for command/HTTP hooks. [Changelog](https://code.claude.com/docs/en/changelog) | Check that no pinned `cad-*` agent lists more than 32 skills. |
| 2026-10-08 | **2.1.294.** Fixes instruction-style prompt/agent hooks that allowed what they should block. Improves judging of Stop/SubagentStop prompt hooks. [Changelog](https://code.claude.com/docs/en/changelog) | Re-test any Stop-hook guardrails. |
| 2026-10-08 | **Building effective agent automations.** Per-run spend cap for scheduled Managed Agents, set in `deployment.md` as `max_list_cost` (a string in cents, so "500" is $5). A run that hits it pauses with `budget_reached`. Advice is to start the cap at 3 to 5 times a normal run's cost. [Post](https://claude.dev/blog/building-effective-agent-automations/) | Pattern only. This is Managed Agents (beta), not local Claude Code. |
| 2026-10-08 | **Dashboards and Motion.** The page is an Announcements-category post. It covers Claude Dashboards and Claude Motion betas, and says Docs, Slides and Design are out of beta. Claude Code is only a tag and the post has no Claude Code deliverable workflow. [Post](https://claude.com/resources/articles/dashboards-and-motion) | Low relevance. Skip. |
| 2026-10-14 | **Agent observability on the Claude Platform** (OTel trace export, public beta). Found by the Opus sweep, not in the researcher's list. [Post](https://claude.com/resources/articles/agent-observability-on-the-claude-platform) | Optional, for per-agent token and cost tracking. |
| 2026-10-15 | **Code Review GA** for Team and Enterprise (found by the Opus sweep). [Post](https://claude.com/resources/articles/code-review-is-now-generally-available) | Low relevance to CAD. |
| 2026-10-09 | **anthropics/skills commits.** Two commits update only the `claude-api` skill, for dynamic workflows and Haiku 5.5 as the current Haiku. [Commits](https://github.com/anthropics/skills/commits/main) | Informational. |

**Nothing found**
- No CAD, BIM or architecture skill or plugin was announced in the window. This is "no evidence found", not proof none exists. The `anthropics/skills` commits and claude.com blog index for the window had none.
- No dedicated plugin-marketplace or skill-sharing announcement appeared. The only marketplace changes are the changelog entries above.
- The anthropic.com/news index (Oct 7 to 15) has nothing on Claude Code, skills or plugins. Product announcements went to claude.com/blog.

## 2. New trainings and upcoming events

**New in the window:** no new Claude or Autodesk training was confirmed as announced in the window. The AutoCAD/Autodesk course pages the researchers saw were either snippet-only or dated by session, not announcement. Announcement dates are not shown on the pages below, so none is counted as new.

**Upcoming or available now**

| Date | Item | Cost | Suits |
|---|---|---|---|
| Oct 21, 2026 | Anthropic webinar "Tokenomics on AWS: Control and optimize your Claude spend". [Webinars](https://claude.com/resources/webinars) | Not shown | Whoever owns agent cost. This is the closest match to the cost-control work. |
| Oct 22, 2026 | Anthropic "Claude Rearview Roadmap Review: October 2026". [Webinars](https://claude.com/resources/webinars) | Not shown | Anyone planning model routing. |
| Recurring, multiple dates | Anthropic Virtual Claude Code Workshop (with Tenex). 1.5 hours live. Ticket to pull request in about 90 minutes. You leave with a CLAUDE.md and a skill checked into git. [Page](https://claude.com/resources/webinars/recurring-virtual-claude-code-workshop) | No price on page | Engineers who build skills for repos they did not write. |
| Self-paced | Anthropic Academy catalog (Skilljar, 23 entries). Includes Claude Code 101, Claude Code in Action, Intro to MCP, MCP: Advanced Topics, Intro to agent skills and Intro to subagents. The catalog shows no dates or "new" labels. Listed as free by the validator. [Catalog](https://anthropic.skilljar.com/) | Free (per validator) | Best self-serve fit for the skill and MCP work. |
| Announced 2026-10-02 (pre-window) | Claude Frontier Academy: $100M to train 10,000 Frontier Deployed Engineers by end-2027. A multi-day in-person program with a graded practical, then a 12-week residency. Entry is by employer nomination. Cohorts run in SF, New York and London. First badges are expected early 2027. [Announcement](https://anthropic.com/news/claude-frontier-academy) | No participant pricing stated | Enterprise nomination only, not self-serve. |
| Sep 15-17 (past) | Autodesk University 2026 digital. The free Digital Pass gives on-demand keynotes and featured sessions. The page does not say the full session catalog is included or how long recordings stay up. [AU 2026](https://conferences.autodesk.com/flow/autodesk/au2026/web/page/overview) | Free | Recordings for AutoCAD/AI roadmap context. |
| Nov 23-26, 2026 | Big 5 Global, Dubai World Trade Centre. Trade show, not training. **Unchecked.** [Site](https://www.big5global.com/?p=64246) | Not shown | Dubai construction contacts. |
| Dec 7-11, 2026 | GITEX Global. The Summit (Dec 7) is at DWTC and the Expo (Dec 8-11) is at Expo City Dubai. Not in October. [Site](https://www.therecursive.com/gitex-global-2026-moves-to-expo-city/) | Not shown | General tech event. |
| Nov 4-6, 2026 | Imaginit "AutoCAD: Advanced" live online, 9 AM to 5 PM Central, $1,445 excluding tax. **Unchecked**; not a new offering; confirm with the provider. [Page](https://www.imaginit.com/training/find-a-class-and-enroll/class-schedules/CourseId/2419) | $1,445 | A paid course for a team member. Not specific to MCP or AI. |

## 3. AutoCAD / Autodesk / MCP changes

**New this week**
- **ezdxf 1.4.5 final, 2026-10-16 (verified).** Per the changelog, it drops Python 3.10 wheels as end-of-life and adds Python 3.15 wheels. It adds PLANESURFACE and the `%%%` control code, fixes HATCH pattern scale/rotation/base-point on transform, fixes aligned-dimension and ray-intersection bugs, fixes MTEXT export, and is compatible with numpy 2.5 and pyparsing 3.3.3. Confirm every pipeline interpreter (Windows and WSL) is Python 3.11 or later before bumping the pin. [PyPI](https://pypi.org/project/ezdxf/1.4.5/), [changelog](https://github.com/mozman/ezdxf/blob/master/notes/pages/CHANGELOG.md). GitHub Releases for the repo is empty; use the changelog file.
- **ezdxf 1.4.5b2, 2026-10-10 (verified).** Superseded by the final. [PyPI](https://pypi.org/project/ezdxf/)
- **Architosh AU 2026 analysis, 2026-10-07 (verified).** Autodesk is reworking Assistant into a cross-platform tool (Personal Pulse, Assistant Spaces, Assistant Builder). An expanded standalone platform is expected in 2027, not yet generally available, with pricing and licensing not expected until 2027. It does not mention MCP or training. [Article](https://architosh.com/2026/10/au2026-autodesk-shifts-ai-from-chatbots-to-agentic-ecosystems/)
- **LibreDWG 0.14.8612 Windows nightly pre-release, 13 Oct (partly true).** The year is not shown on the page; 2026 is inferred. These are nightlies, not a stable release, so do not pin to them. [Release](https://github.com/LibreDWG/libredwg/releases/tag/0.14.8612)

**Status checks (no change in the window)**
- **Autodesk MCP servers.** Autodesk has several public MCP servers, all preview or beta: Fusion, Fusion Data, Revit and Product Help (tech preview, Apr 2026), plus the Revit Public MCP Server for Revit 2027 (June 2026). None controls AutoCAD, and none was confirmed GA as of 2026-10-16. Do not assume an official AutoCAD MCP exists.
- **ODA MCP Servers.** The product page still reads pre-release, "Coming Q3 2026". The FAQ (2026-08-17) promised a September launch, so it looks slipped or the page is stale. Formats at launch are DWG, STEP and IFC. Access needs the Sustaining tier or above, and Revit and Navisworks need separate Extensions. [Product page](https://www.opendesign.com/node/4662), [FAQ](https://www.opendesign.com/blog/2026/august/oda-mcp-servers-faq.md)
- **Third-party AutoCAD MCP pins.** `autocad-mcp-pro` is still 1.6.0 (2026-09-24), with no GitHub commits after Oct 7 ([PyPI](https://pypi.org/project/autocad-mcp-pro/), [releases](https://github.com/U-C4N/Autocad-MCP/releases)). `best-cad-mcp` is still 1.7.2 (2026-09-23) ([PyPI](https://pypi.org/project/best-cad-mcp/)). Keep both pins.
- **AutoCAD 2027.1.** The package dates to about 2026-07-27. The release notes page shows only the base release, 2026-03-25. Nothing newer was found. [Release notes](https://help.autodesk.com/cloudhelp/2027/ENU/AutoCAD-ReleaseNotes/files/AUTOCAD_2027_RELEASE_NOTES.html)
- **Autodesk developer blog.** The newest post is 2026-10-01 and none of the top posts is about MCP or agents. [Blog](https://blog.autodesk.io/)

## 4. Rendering news

**Nothing dated in the window was found** for Blender, Twinmotion, Chaos (Enscape, V-Ray, Corona, Veras), D5 or the Unreal MCP plugin. This is a result for the sources opened, not proof there was no news.

**Status (not new)**
- **Blender.** 5.2.2 LTS was released 2026-09-15. 5.3 is in beta until Nov 4, with the release expected Nov 10, so these two dates do not conflict. [Download](https://www.blender.org/download/), [5.3 notes](https://developer.blender.org/docs/release_notes/5.3/)
- **Twinmotion 2026.2.** Only the Preview exists; the builds page links nothing newer. It adds dynamic sky in Realistic mode, a night sky (moon, Milky Way, aurora), MegaLights shadows (needs hardware ray tracing), EXR Cryptomattes, and Interchange import. DXF, DAE, 3DS, C4D and STL imports are dropped. Test the glTF route before upgrading. [Preview notes](https://dev.epicgames.com/documentation/twinmotion/twinmotion-2026-2-preview-release-notes?lang=en-US), [builds page](https://dev.epicgames.com/documentation/twinmotion/release-notes-for-twinmotion-2026-2-builds?lang=en-US)
- **Chaos.** The latest press release is 2026-05-27. There are none for Sep or Oct. A free V-Ray for Blender Community Edition was announced 2026-04-13. [Press releases](https://www.chaos.com/press-releases)
- **Enscape.** The what's-new page is undated. It lists a live link, removal of the 2GB scene limit, Revit 2027 support, and Veras AI on all plans. Envision includes real-time animated water, with pools as an example. "Envision 1.5" applies only to the AI guidance item. [Page](https://www.chaos.com/enscape/whats-new)
- **Unreal Engine MCP plugin** (Epic, Claude marketplace). No version or date on the page. It needs the ModelContextProtocol and AllToolsets plugins and `ModelContextProtocol.StartServer`. A repo snippet (not opened) says the SessionStart hook needs bash, which matters on native Windows PowerShell. [Plugin](https://claude.com/plugins/unreal-engine-skills-for-claude-code)

## 5. Reference for the house spec (older, not news)

**Dubai private pool safety**
- **Use 1.2 m for the enclosure, not 90 cm.** Khaleej Times (2025-07-04), citing Dubai Municipality's Health and Safety Department, reports the following. It is a secondary source, not the DM text.
  - Applies to any water feature deeper than 300 mm.
  - The enclosure must be climb-proof and at least 1.2 m high.
  - Gates open outward and are self-closing and self-latching, with locks at least 1.5 m above ground.
  - Garage or automated perimeter gates may not be used as pool access.
  - Windows over the pool open no more than 100 mm.
  - Covers and nets should meet ASTM F1346-91.
  - Pools are registered before construction.
  - [Khaleej Times](https://www.khaleejtimes.com/uae/drowning-incidents-official-guidelines-pool-owners)
- **The Gulf News 90 cm figure appears superseded.** It was last updated 2018-09-16 and the circular is likely older. Do not use it. [Gulf News](https://gulfnews.com/uae/new-safety-standards-for-balconies-pools-1.1281313)
- **The primary DM document is not yet read.** The GU80 Private Swimming Pools Safety Guidelines PDF is encrypted and gave no extractable text. A person must open it and extract the rules before the spec is final. [GU80 PDF](https://dmpmedia.dm.gov.ae/uploads/2022/03/DM-HSD-GU80_PRSPS2_Private-Swimming-Pools-Safety-Guidelines_V1-1.pdf). The GU34 pool-plan guideline URL returned the DM homepage, so it was not read either.

**Overflow and infinity-edge sizing**
- **No verified numeric rule was found for catch basin or balance tank sizing, weir tolerance, or surge volume.** The Aqua Magazine and ANSI/APSP/ICC-7 sources could not be opened, so their claims were dropped. Use the pool engineer's calculation and the current standard, not figures from this sweep.
- Unchecked, snippet-only examples, not design bases:
  - Wisconsin SPS 390.11: one vanishing-edge wall may cover up to 50% of the perimeter if adjacent water is at least 5 ft deep. It also requires a dry-side catch ledge at least 3 ft wide. US code, not Dubai. [Source](https://docs.legis.wisconsin.gov/document/administrativecode/SPS%20390.11(3)(a))
  - A vendor balance-tank calculator estimates tank size from surge displacement, evaporation, a wave reserve of about 1% of pool volume and a 25% safety factor. This is a vendor method, unvalidated. [Source](https://pooldial.com/balance-tank-calculator)

## 6. What to do this week

- **Claude Code.** Check the installed build, then move to 2.1.301. Confirm `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` is not set globally. Confirm no `cad-*` agent preloads more than 32 skills. Re-test Stop-hook guardrails after the 2.1.294 fix.
- **Cost control.** Try the new `/usage` warnings and `--max-budget-usd`. Join the Oct 21 Tokenomics webinar. Treat the Managed Agents budget-cap pattern as a design reference only.
- **ezdxf.** Confirm Windows and WSL interpreters are Python 3.11 or later, then trial 1.4.5. Re-run the drawing set for HATCH and MTEXT output differences before bumping the pin.
- **Pool rules.** Have a person extract the DM GU80 text. Use 1.2 m enclosure and outward-opening, self-latching gates as placeholders, and have the pool engineer supply the overflow sizing.
- **Renders.** Do not plan on DXF import into Twinmotion 2026.2. Test glTF import in the Preview first. Blender 5.3 final is expected Nov 10, so stay on 5.2.2 LTS for now.
- **Hold off** on the ODA MCP, an Autodesk MCP for AutoCAD, and LibreDWG nightlies. Book the Virtual Claude Code Workshop and the free Skilljar skills, subagents and MCP courses.

## 7. Research quality

| Angle | Findings | Checked | Verified | Partly | Wrong | Unverifiable | Fabricated | Validator-added |
|---|---|---|---|---|---|---|---|---|
| claude-skills | 17 | 12 | 9 | 2 | 0 | 1 | 0 | 3 |
| trainings | 17 | 10 | 3 | 5 | 0 | 2 | 0 | 1 |
| autocad | 13 | 11 | 8 | 2 | 0 | 1 | 0 | 2 |
| pools-render | 16 | 12 | 7 | 2 | 0 | 3 | 0 | 3 |

Notes
- **Nothing new in the window:** trainings (no new offering confirmed) and rendering (no dated news). Pool and Dubai rules also had no in-window items.
- **Dropped as unverifiable:**
  - The Autodesk "MCP for Transportation" webinar and the AU AutoCAD on-demand sessions post (both returned 403).
  - The third-party AutoCAD MCP repo activity claim.
  - The Dubizzle, Aqua Magazine and ANSI listing claims.
  - The "no CAD skill" negative, kept only as "no evidence found".
- **Also dropped:** the snippet-only Ledet, Graduate School, Autodesk Fusion/AutoCAD webinar and DevCon items, because their dates and content were unconfirmed.
- **Main gaps:** the DM GU80 and GU34 text, Autodesk pages blocked by 403, and exact announcement dates for webinars and the Academy catalog.