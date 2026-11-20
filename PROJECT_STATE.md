# PROJECT STATE — resume here

Written 2026-09-06 before a context limit. Two projects: a completed **house**
drawing set, and a **villa** in progress.

---

## 0. HOW TO RESUME IN ONE COMMAND

```
cd C:\Users\lsire\autocad-mcp
C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe house_design.py   # house 2D
C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe insert_blocks.py  # real ACA blocks
C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe plot_sheets.py    # DWG -> PDF
C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe villa_3d.py       # villa 3D + derived 2D
```
Python is `C:\Users\lsire\AppData\Local\Programs\Python\Python313\python.exe` (call it
by full path; `python` on PATH may differ).

---

## 1. ENVIRONMENT (all installed, verified)

Python 3.13.15 · Node 24.19 · Claude Code CLI · git · gh · ripgrep · fd · bat · jq ·
fzf · 7-Zip · Windows Terminal · PowerShell 7 · VS Code · Go · Rust · uv · Docker 29.7.2

Python packages: `ezdxf 1.4.4`, `pymupdf`, `matplotlib 3.11.1`, `shapely 2.1.2`,
`build123d 0.11.1`, `pywin32`, `comtypes`, `mcp 2.1.1`

- **AutoCAD Architecture 2027** at `C:\Program Files\Autodesk\AutoCAD 2027`,
  COM ProgID `AutoCAD.Application.26`.
- **WSL 2.7.13 installed, Ubuntu registered but NEEDS A REBOOT** to appear.
- MCP servers registered: `autocad` (mine, 41 tools), `autocad-pro`
  (U-C4N/Autocad-MCP, 154 tools, reviewed + clean, own venv),
  `autodesk-product-help` (official, read-only), `augmentclaude` (unreviewed).
- Skills installed to `~/.claude/skills` but **NOT ACTIVE UNTIL RESTART**:
  algorithmic-art, canvas-design, mcp-builder, 3dgs-experiment-planner-jaccen,
  scientific-figure-making-chenliu-1996. The last two are third-party, unreviewed.

---

## 2. THE TOOLCHAIN DECISION (do not relitigate)

**Author drawings with ezdxf, not COM.** Driving AutoCAD over ActiveX is unreliable
for batch work: dynamic proxies go stale mid-run (`AttributeError: <unknown>.ModelSpace`),
`gencache.EnsureDispatch` fixes staleness but renames interface properties
(`IAcadLayer` loses `.Color`), and a busy editor returns
`RPC_E_CALL_REJECTED (-2147418111)`.

COM is used for exactly two things, both with **whole-job retry** (retrying individual
calls is whack-a-mole — any call can fail):
1. inserting blocks from the ACA content library (`insert_blocks.py`)
2. plotting DWG → PDF (`plot_sheets.py`)

---

## 3. HARD-WON GOTCHAS (all verified, all cost real time)

### The recurring shape: a call that silently resets settings made before it
- `Layout.RefreshPlotDeviceInfo()` resets media/scale/plot-type. Must be called
  IMMEDIATELY AFTER `ConfigName`, never last, or `PlotType` reverts to acDisplay
  and you plot the current screen view.
- `Frontend.draw_layout()` calls `set_current_layout()` and discards a background
  set on `ctx.current_layout_properties` — pass `layout_properties=lp` explicitly,
  or ACI 7 renders white-on-white and looks like nothing drew.

### AutoCAD / COM
- New dimensions inherit the ACTIVE DIMSTYLE (ISO-25, 2.5 mm text), NOT the `DIM*`
  system variables. At 1:100 that is invisible. Set sizes on the entity.
- `dimclrt/dimclrd/dimclre` hard-coded to a colour override the layer → pink dims.
  Use 256 (BYLAYER).
- `hatch.AppendOuterLoop([ent])` fails "Invalid object array" — needs
  `VARIANT(VT_ARRAY|VT_DISPATCH, [...])`.
- AutoCAD cannot `SaveAs` over a drawing it still has open.
- ACA "Metric" content is authored in **INCHES** — a 1600×2000 bed is drawn 63×79.
  **Insert at scale 25.4** into a millimetre drawing.
- The `Dynamic Block 2D` versions are unusable by bounding box: extents span every
  visibility state (`WC.dwg` measures 5135 × 22446). Use the static equivalents
  under `Bathroom\Toilet\`, `Bathroom\Bath\`, `Bathroom\Basin\`.
- **The CTB never took effect** despite `PSTYLEMODE=1`, the stylesheet assigned, and
  the file verified to contain black pens. Four attempts, including installing under
  a fresh name to defeat caching. WORKAROUND IN PLACE: choose ACI 7/8/9 in the DXF —
  7 prints black on paper and draws white on AutoCAD's dark canvas. Unresolved.

### build123d 0.11.1 (full reference at `build123d_reference.md`, 37 KB, all snippets executed)
- `Drawing`, `ColorIndex`, `SkipClean`, `Shape` are NOT in `__all__` —
  `from build123d.exporters import Drawing, ColorIndex`.
- Walls: build the wall FACE in sketch space then ONE extrude (1.4 ms vs 8.2 ms).
- `offset()` on a closed wire is BROKEN (IndexError). Use
  `offset(face, -t, kind=Kind.INTERSECTION)`.
- `section()` returns a `Sketch` left ON the cutting plane in 3D — flatten with
  `Pos(0,0,-z) * sec` or `plane.to_local_coords(sec)` before DXF export.
- `Plane.XZ.z_dir` is `(0,-1,0)`: positive `height` moves AWAY → silent empty section.
- **Batch booleans**: `Part() + [list]` then `- [list]`. 13–42× faster than looping.
- Elevations from `Drawing(...)` are architecturally correct, NOT mirrored (verified
  with an asymmetric marker).
- Unitless, work in mm. `TOLERANCE=1e-6`. `is_valid` is a property. Test emptiness
  with `if shape:` — `.wrapped` raises bare `AssertionError` on empty.

---

## 4. HOUSE — COMPLETE

Output in `C:\Users\lsire\OneDrive\Desktop\House\`:
`A-101_GF_TECH`, `A-102_FF_TECH`, `A-111_GF_PRES`, `A-112_FF_PRES`
each as `.dxf` + `.dwg` + `.pdf` + `FINAL_*.png`.

Source: `plan_dxf.py` (Plan class, layers, lineweights, title block, scale bar,
north arrow, CTB writer) · `house_design.py` (design + validator + furniture) ·
`furniture_layout.py` (block placements) · `block_catalog.json` (16 measured blocks) ·
`insert_blocks.py` · `plot_sheets.py` · `to_autocad.py` · `study_sample.py`.

Two-storey, 13.0 × 9.6 m envelope, GIA 108.5 m² GF / 108.0 m² FF.
Circulation 9.7% (target ≤8% — NOT met; a winder stair would close it).

**The validator (`validate()` in house_design.py) enforces:**
door↔opening match · door width 700–1100 · door swing vs stair · **door swing vs
furniture** (added after a user catch: 9 clashes, worst covered 74% of the WC pan
and 78% of an appliance) · stair rise ≤220 mm · every habitable room has an
EXTERNAL window (only external walls count — counting internal doors as light
sources gave a false all-clear) · circulation ≤8% of GIA · room aspect ≤2:1.

Currently reports only: WC + EN-SUITE internal (acceptable, mechanical extract)
and circulation 9.7%.

### House — still outstanding
- Door/window tags + schedules ("type measurements"). Convention learned from
  Autodesk samples: **type, variant, handing and size live in the block name** —
  `Door - Left Hung 36 in.`, `Tub - Rectangular 1700x800`, `RMNUM` room tag.
- Symbol legend / key; sheet index; cross-reference + section markers.
- Block colours to BYLAYER (ACA content carries hard-coded colours).
- Floor-finish hatch screened to 25%.
- Clearance checks: 1200 mm between opposing kitchen runs, 550 mm in front of a WC,
  bed access to one side.

---

## 5. VILLA — IN PROGRESS

`villa_3d.py` → `C:\Users\lsire\OneDrive\Desktop\Villa\`
Produces `villa.step`, `VILLA_PLAN_GF/FF.dxf`, `VILLA_ELEV_S/N/E/W.dxf`,
`VILLA_SECTION_AA.dxf`, each with a `.png` preview.

**Pipeline verified fast**: model 0.131 s (174 faces, 438 m³), each plan ~0.085 s,
each elevation ~0.021 s, section 0.038 s. Everything is CUT FROM ONE MODEL, so
plan/section/elevation cannot drift apart — the flaw that let the old house have
doors in 2D and none in 3D.

### Brief
4,500 sq ft (418 m²) GFA over 2 storeys + roof level, on 7,500 sq ft (696 m²).
Overflow pool, garden, 2-car garage, entrance gate, stone boundary wall.
Target: impress a 20-year architect. **Assumption stated to user and not yet
contradicted: 4,500 sq ft is GFA across floors, not footprint.**

### Design (coordinates in villa_3d.py, mm)
Plot 24000 × 29000. Street NORTH, garden/pool SOUTH. Setbacks 5000 front,
3000 sides, 4000 rear.

Concept: **a single water axis** — reflecting channel at the entrance court, passing
THROUGH the house under the double-height living volume, terminating in a 12 m
infinity edge. One continuous line of water from gate to garden.

- House ground: x 3000–21000, y 13000–24000 (18 × 11 m = 198 m²)
- Double-height void (first floor open): x 8500–15500, y 13000–18000
- Cantilever 2400 south over the terrace
- Levels: GF 0, ceiling 3600, slab 300, FF 3900, ceiling 3200, roof 7100,
  parapet 1100, roof pavilion 3000
- Pool 12.0 × 3.5 m at x 5000–17000, y 7500–11000, depth 1400, overflow on the
  south long edge
- Water axis x 11700–12300
- Boundary wall 300 thick × 2400 high; vehicle gate x 4200–9600, pedestrian gate
  x 15200–16600, both in the north wall

### Villa — honest status
The massing WORKS but **reads as stacked boxes** — a competent massing study, not
architecture. Not yet good enough for the stated goal.

Missing: interior walls entirely · proportional refinement · material layering
(stone base / rendered upper / timber screen) · brise-soleil · shadow gaps · a
cantilever that reads as deliberate · landscape.

Two drafting faults in the villa plan: the `A-BEYOND` projection reproduces the cut
outline and swamps the drawing (the build123d reference warned about exactly this —
project only specific objects you want dashed), and cut walls have no poche.
Intended fix: route the build123d section through `plan_dxf.Plan` so the villa gets
the same lineweight hierarchy, poche, dimensions and title block as the house.

### OPEN QUESTION PUT TO THE USER, NOT YET ANSWERED
**How many bedrooms, and is there a majlis / formal reception separate from family
living?** Big planning fork; differs a lot between a Western and a Gulf brief.

### RESEARCH RECEIVED IN FULL — see `VILLA_RESEARCH.md`
The precedent research completed and was saved before the limit. NOT lost.
Three findings that change the design:
1. **A classic infinity edge will NOT read on this plot** — needs a 1.2–1.8 m drop to
   terrain beyond; a flat walled site spills toward a wall. Use either a knife-edge
   perimeter overflow (mirror-flat) or a pool raised 600–900 mm with a one-sided
   waterwall into a visible basin.
2. **The luxury programme sums to 480–620 m² net vs the 418 m² brief.** Resolve with a
   semi-basement for majlis/staff/plant (F.LOT), 4 bedrooms not 5, and mid-range sizes.
3. **Alhambra Court of the Myrtles is 23.5 × 36.6 m with a 34.0 × 7.10 m pool** — this
   plot is 24 × 29 m, almost exactly that width. A long axial water body is the
   historically proven proportion; the swimming pool itself stays 12 × 4 m (48 m²,
   ~8% of plot) with a 500 mm rill carrying the axis (Casa Mérida).

---

## 6. REFERENCE MATERIAL ALREADY GATHERED

- `build123d_reference.md` — 37 KB, every snippet executed. Read this before
  touching villa_3d.py.
- Lineweight ladder (ISO 128-20): 0.70 external cut / 0.50 partition / 0.25
  openings / 0.18 fixtures / 0.13 furniture+dims+swings / 0.09 poche.
  FreeCAD `LineGroup.csv` is the citable source; it says 0.50 for A4–A2 and 0.70
  for A1–A0, so 0.70 on A3 is a deliberate deviation.
- Text: ISO 3098 — 1.8 / **2.5** / 3.5 / 5 / 7 mm plotted. At 1:100 → 250 model units.
- Circulation ≤8% of GIA for a house; >20% is a failed plan. Corridor 900 min /
  1000–1200 comfortable. Room aspect beyond 2:1 reads as a corridor.
- NDSS: single bed ≥7.5 m², double ≥11.5 m² and ≥2.75 m wide.
- Stairs (Approved Doc K): rise 150–220, going ≥220, 2R+G = 550–700, pitch ≤42°.
- ACA content library: 6,292 block DWGs at
  `C:\ProgramData\Autodesk\ACA 2027\enu\AEC Content\Metric\Design\`.
- Autodesk sample drawings worth re-reading: `Floor Plan Sample.dwg` (437 block
  refs from 17 definitions) and `House Designer.dwg` (block library, all on layer 0).

---

## 7. USER PREFERENCES OBSERVED
- Wants engineer/client-presentable output, not diagrams. Called earlier work
  "dull, sluggish and lazy" — fair at the time.
- Catches real defects by eye (door swinging onto a bed). **Never sign off a drawing
  by looking at it — compute every property that matters.** That principle is now
  encoded in the validator and is the single most valuable habit from this session.
- Wants real blocks/assets, not drawn rectangles.
- Wants research and references used, not invention.


---

## 8. SESSION 2 ADDITIONS (paused here)

### A REUSABLE SKILL WAS BUILT AND TESTED
`~/.claude/skills/architectural-cad/` — **not active until Claude Code restarts.**
```
SKILL.md
references/autocad-com.md          COM traps, whole-job retry, block measuring
references/ezdxf-drafting.md       layers, lineweights, poche, labels, plotting
references/build123d-modelling.md  3D + deriving 2D, all verified API notes
references/design-standards.md     circulation, rooms, stairs, pools, setbacks
references/validation.md           the checks, and why each one exists
scripts/validate_plan.py           runnable validator
```
Smoke-tested: given a plan with 8 planted defects it caught all 8, including a
door opening onto a bed (14% overlap), an illegal 223 mm stair rise (with the
14-riser fix), and correctly distinguished an acceptable internal WC from an
unacceptable dark habitable room.

### VILLA — CURRENT STATE
Design settled with the user: **4 bedrooms, women's majlis only, family living on
the GROUND floor, bedrooms above.**

`villa_3d.py` builds the model and derives 4 plans, 4 elevations, 3 perspectives
and a section in ~0.5 s. `villa_sheets.py` imports the derived plan geometry into
`plan_dxf.Plan` and adds room labels with computed areas, dimension chains, grid,
scale bar, north arrow and title block. `villa_to_autocad.py` loads all 12 views
into AutoCAD as DWG (verified 12/12, exact entity fidelity).

Measured: GFA 407 m2 = 4,381 sq ft · footprint 196 m2 · coverage 28% ·
pool 5.0 x 9.5 = 48 m2 · double-height 7.30 m clear, compression 1:3.0 ·
cantilever 3.0 m · sheets A-201 net 150.3 m2, A-202 net 131.6 m2.

**Three defects found and fixed this session:**
1. Four butted boxes gave **two 400 mm walls back to back (800 mm)** at every
   wing/bar junction. Rebuilt from the union footprint offset once — verified
   164.2 m2 as ONE connected interior.
2. **The garage did not fit** — north bar is 5.2 m deep internally, two cars need
   5.5-6.5. Became a covered car porch in the front setback (Gulf norm, often
   BUA-excluded), freeing the whole north bar for rooms.
3. **Roof plan cut at 10,400 when the parapet tops at 10,300** — the section
   floated above the building. Now 9,750.

### STILL OUTSTANDING ON THE VILLA
- No furniture in the villa (the house has real ACA blocks; the villa has none)
- Elevations and section have no annotation or title block yet
- `A-201`/`A-202` not yet pushed to AutoCAD or plotted to PDF
- Materials/landscape not modelled

### A WORKFLOW WAS STILL RUNNING AT PAUSE
Six-lens adversarial design critique (programme · section/light · pool technical ·
elevation composition · site planning · whether the water-axis concept is actually
delivered), each finding then attacked by a separate agent instructed to refute it.
Run ID `wf_69b7b587-078`. **Check for its result on resume** — if the notification
was missed, the transcript directory is under
`.claude/projects/<project>/subagents/workflows/wf_69b7b587-078`.

### OPEN ASK NOT YET DONE
User asked for the understanding to become "artifacts and skills". The **skill is
done**; an **Artifact (published page) has NOT been created yet**.


---

## 9. ALL AGENT FINDINGS SAVED  (session 3)

`VILLA_CRITIQUE_FINDINGS.md` (746 KB) holds **160 distinct findings** and **78
verdicts** (60 upheld / 18 refuted) extracted from both critique runs.
Severity: **52 fatal, 81 major, 27 minor**. Regenerate any time with
`python save_findings.py`.

GOTCHA that blocked the extraction for several attempts: the workflow journal
path runs to ~290 characters, past Windows' 260-char MAX_PATH. `os.listdir`
silently sees nothing. Prefix the path with `\?\` (which is exactly why
`cygpath -w` reports it as `\?\C:\...`).

### THE VILLA MODEL IS COMPREHENSIVELY BROKEN — do not issue it
Beyond the six defects known earlier, the full set includes systemic modelling
failures:

1. **No opening in the model penetrates its wall.** Every door and window void
   leaves a ~100 mm skin, so the villa has NO actual openings. The voids were
   sized to the wall face +/-300 against a 400 mm wall.
2. **The overflow and catch basin do not exist** - the boolean subtracts zero
   material. All four pool rims sit at +700, so there is no crest differential
   and the pool would overflow toward the house.
3. **The water axis does not exist** - two unrelated water bodies at different
   levels; the gate perspective dies 10.2 m in at an 800 mm wall.
4. **The sunken courtyard is roofed over** - basement gets zero daylight - and
   its hole guts the living volume and severs the entry axis with no bridge.
5. **The pool shell is fused into the ground-floor slab** - a tanked structure
   with no isolation.
6. **The west brise-soleil shades a blank wall** - no window behind it.
7. **Forecourt is 4.65 m deep** - no car can stand between gate and garage; and
   **garage bay 2 is unreachable**, so the two-car brief delivers one.
8. **Terrace between the living-room glass and 1.4 m of water is 300 mm wide.**
9. **Both floors are ~48 m2 short** of the minimum brief programme.
10. **The fourth bedroom is on the marooned cantilever** - unreachable.

### CONCLUSION FOR THE REPLAN
Do not patch. Rebuild the villa from a validated schedule: fix the opening
depths first (they are a one-line class of bug), then replan both floors against
`scripts/validate_plan.py` extended with reachability, fixtures-per-bedroom,
schedule-vs-minimum and void/room overlap. Prove it with the validator before
drawing anything.


---

## 10. RESTORED ON A NEW MACHINE  (2026-09-25)

Section 9 is superseded: the replan was done on 09-10 (`villa_design.py`, data-
driven, 0 fatal / 0 major). Everything was restored from `C:\Backup` onto user
`lsire` and rebuilt from source. Paths `asdfv` -> `lsire` in all scripts.

**Pipeline, in order** (all from `C:\Users\lsire\autocad-mcp`):
```
offline : villa_design -> villa_furniture_spec -> villa_cad -> villa_colour -> villa_gltf
AutoCAD : villa_3d_build -> villa_3d_verify -> villa_pool_check -> villa_window_check
          -> villa_load -> villa_verify -> villa_show
```
Rebuild result: all six DXF sheets IDENTICAL to the 09-10 originals; 3D volumes
identical; 19/19 rooms void, 6/6 fabric solid, 37/37 openings cut, pool holds
water; 52/52 blocks verified. Originals kept in `Desktop\Villa\_restored_0910`.

Fixed: `villa_3d_verify.py` and `villa_window_check.py` still assumed ONE building
solid on layer 0 -- stale since the 16-layer material split. They now probe the
`A-*-3D` solids (wall check: `A-WALL-3D`).

Gotcha: a whole-job retry in `villa_3d_build.py` calls `Documents.Add()` again, so
a busy retry leaves unsaved `DrawingN.dwg` orphans open. Close them afterwards.

Environment now: Python 3.13 (user), build123d 0.13.0 (notes above are 0.11.1),
mcp 2.2.0, ezdxf 1.4.4. MCP servers `autocad` + `autocad-pro` registered in
`~/.claude.json`; autocad-pro venv rebuilt at `autocad-mcp-pro\.venv`.


---

## 11. RENDER TRACK + GEOMETRY FIXES  (2026-09-25, later)

Installed: Blender 5.2.1 LTS (machine-wide), Twinmotion 2026.2 Preview and
UE 5.8.3 (by the user, Epic launcher). Twinmotion has NO API/CLI.

**Pipeline now ends:** `villa_gltf.py` -> `villa_blender.py` (headless Cycles,
OptiX on the RTX 5070 Ti, ~70 s for 5 views at 2400x1500/256 spp) ->
`render\out\villa_*.png`, `render\villa_render.blend`,
`render\twinmotion\villa_twinmotion.glb/.fbx` + `TWINMOTION_STEPS.md`.

**Shared geometry moved INTO villa_design.py** so the AutoCAD and glTF builders
cannot diverge again: `envelope()`, `pool_parts()`, `external_steps()`,
`ground_at()`, and `probes()` (38 solid/void probes both verifiers ask).

Defects found and fixed today (all were invisible to the old checks):
1. Double-height living was capped by a slab at FF in BOTH 3D models.
2. 500 mm open band FF-SLAB..FF along the whole street front (both models).
3. glTF had no first-floor slab over any of the 7 GF rooms.
4. House hovered 400 mm over the ground; fins hung 900 mm up -> stone base.
5. Pool: basin overlapped the tank wall, so cutting it deleted the weir, and it
   had no floor -> weir = tank's south wall at crest, basin 1600..2800 with floor.
6. No steps to a GF raised 900 mm -> landing + flight per external door,
   turned alongside the wall when a straight flight leaves < 900 mm to the boundary.
7. Landscape level chosen per GROUP from one point: south beds buried in the
   garden platform, lawn floating 700 mm over the forecourt -> split per part.
8. glTF export is displaced EXACTLY when the top-level shape's `.location` is
   not the identity (established by a 15-case test; corrected in s12 -- the
   earlier "Location written untransformed in the Y-up frame" was a guess).
   The vertex POSITIONs stay Z-up and the root node carries the Z-up -> Y-up
   rotation; a top-level Location is not composed with it correctly, so a
   lone `Location((0,0,z)) * solid` came out z mm SOUTH. Build geometry in
   place (villa_gltf prism/box/part); `villa_gltf.main()` now REFUSES to
   export any group whose location is not the identity; villa_blender still
   checks every group lands within 5 mm of `render\groups.json`.
9. Blender: a `Location * box` group imports as ONE mesh object with no
   parent (not parent + child, as first written). The stale value that
   actually reproduced is `bound_box` (cached until view_layer.update()),
   not a child's matrix_world.
10. MCP server: pywin32 early-binding cache (written by any CastTo) broke
    acad_list_layers (`IAcadLayer` has `color`, not `Color`) -> `_late()`.
11. villa_window_check failed OPEN on a probe error -> now fails closed.
12. villa_load retry now also treats AttributeError("<unknown>.X") as busy.

Audit (10 agents) findings NOT yet acted on -- design decisions for the user:
formal dining reachable only via pantry and study only via majlis (critique #33
still true; inner-room check is bedroom-only); no house->garden door; two
en-suites without shower; no maid/driver/laundry/plant; roof pavilion counted
in GFA but not built or reachable; title-block areas hand-typed; no current
elevations/sections; superseded 09-06/09-09 drawings still beside the set.


---

## 12. CANDIDATE B INTEGRATED: DBC-COMPLIANT + JUDGE GRAFTS  (2026-09-26)

The design is candidate B ("service wing"; backups of the design before it:
`villa_design.pre_B.py`, `villa_furniture_spec.pre_B.py`; A and C in
`candidates\`). Judges' reports: `%TEMP%\phase2.json` ("judged").

**Result:** `villa_design.py` 0 FATAL / 0 MAJOR (1 NOTE: roof pavilion not
built) WITH the Dubai Building Code checks; `villa_furniture_spec.py` 0 issues;
`villa_gltf.py` 93/93 probes; `villa_elevations.py` 47/47 checks, exit 0;
`tests\test_builders_offline.py` 25/25. All run with VILLA_OUT = a temp folder.
Before: 30 fatal / 3 major. Everything was fixed in DESIGN DATA -- except
that check 16 had been widened to pass a west-face door; the review withdrew
that (see 12b, where the counts are now 105/105 probes, 46/46, 27/27).

### Compliance (DBC rule ids, `dubai_villa_rules.json`)
- Stair K-STR-01/03/05/09: 24 risers of 170.8, going 280, two flights of 12,
  1120 half-landing, 2100 wide (1050 a flight); well 12800-14900 x 17900-22100.
- Doors K-DOOR-01/02: every opening 1015 (915 clear) or 810 for wet rooms.
- Pool K-POOL-02/03: the floor is a PROFILE, `POOL_FLOOR` -- 1100 deep shallow
  shelf (house end, 2 m flat), 3 m slope at 11.7 %, 1450 deep end at the weir
  (`POOL_SHALLOW_FL` -200, `POOL_FL` -550); `pool_floor_at`, `pool_section`,
  `pool_volume` (50.1 m3). Built by `pool_parts()` as a y-z profile part
  (`yz_prism`) in BOTH 3D tracks.
- Deck K-POOL-09: water moved 400 south (y 2800-9400, still 6.0 x 6.6 =
  39.6 m2): terrace 1600 = 1200 deck + 400 coping; the deck ring is paved all
  round (`villa_colour.ground_surfaces` terrace = ring); the balance basin
  (y 1200-2400) is under a walkable GRATE (`BASIN_GRATED`, `grate()`, built
  and drawn). The coping no longer lids the weir.
- Barrier K-POOL-04/08: `POOL_BARRIER` declared (house walls + 2.4 m boundary
  wall + garden-edge guards, alarmed self-closing self-latching garden
  doors) and PROVED by villa_dbc (the pool garden's edge is closed).
- K-POOL-01: formal dining south window in `FIXED_GLAZING`.
- Guards K-GRD-01/02: `guards()` / `guards_labelled()` (and `V.GUARDS`, a
  module `__getattr__`, always fresh) derive 30 mm glass balustrades 1200
  high: both sides of every raised straight landing, free side + outer edge of
  the turned one, the garden platform's open edges in the side strips, and
  round the first-floor stair well. `GUARDS_EXTRA` for hand-declared ones.

### Grafts from the judges
- Entrance bay: hall street wall set back **650** (face 22500) under the
  first floor, pivot door x 11300-12700 on the x 12000 axis. Not ~850: the DBC
  stair needs 4200 plus 1000 clear at its foot inside a 5850 hall.
- Majlis: second door from the GUEST LOBBY (food). The DBC stair now fills the
  hall's east wall where the guests' hall door was, so the guests' door is the
  majlis's OWN street door, lined up with the pedestrian gate (three
  thresholds: family on the axis, guests at the majlis, service at the west).
- FF: north window to the landing/stair; master en-suite with bath, shower,
  WC and TWO basins (`FIXTURE_COUNT`, checked by villa_furniture_spec).
- GF: FAMILY WC off the back corridor (nested in the show kitchen's NE
  corner, door opens out); BACK HALL renamed BACK CORRIDOR (check 10 counts it:
  corridor 21.7 m2 = 6.2 % of GIA).
- Service door moved to the WEST face with a turned flight in the side strip:
  no step lands in the car porch, two 3.0 x 5.5 m bays stay clear (villa_dbc
  now counts bays in the porch width no flight crosses). SUPERSEDED in 12b:
  back on the street face, the porch moved east of its steps.
- Pool plant in a vault beside the basin (`POOL_PLANT`, 15400-18400 x
  1200-3900, floor -1700, 2350 clear), built by `pool_parts()`.
- Gates as DATA: `VEHICLE_GATE` (5100-10700 since 12b), `PED_GATE`
  (15000-16200, 1300 clear of the annex since 12b), `SERVICE_GATE`
  (800-2000), `gates()`; `GATE_X0/X1` alias the vehicle
  gate. Every builder cuts/draws `villa_geom.gates()` -- no typed 15400-16600.
- East/west faces: punched windows <= 1200 (check 16): majlis x2, dining,
  master, bed 2, bed 3, and obscured windows to the master and bed 3
  en-suites; K-WIN-09 checked (faces >= 3 m from the neighbour).
- Light slots filled to garden level (`garden_platform()`), so no 900 pit.

### Builders
- villa_gltf: `part()`/`yz_prism()` for profile parts; groups `grate` (bronze)
  and `guards` (glass); gates from data; terrain on `garden_platform()`;
  **pre-export guard**: `main()` refuses any group whose top-level
  `shape.location` is not the identity (`placed()`), and the compound too.
- villa_3d_build (NOT RUN -- COM is the main agent's): `part3()`; the profile
  is an LWPOLYLINE with Normal +X / Elevation x0 (OCS x -> world Y, OCS y ->
  world Z), extruded along +X, then bbox-checked and REFUSED if it landed
  elsewhere; layers A-GRAT-3D, A-GRDS-3D; gates from `G.gate_cuts()`.
- villa_cad / villa_colour / villa_svg: guards (layer A-GRDS), gates, pool
  floor breaks and depths, grate, plant vault; stair riser by riser at
  STAIR_GOING (`G.stair_risers`); villa_colour's site plan now draws
  `ground_surfaces()` itself (it re-derived its own and drew a different deck).
- villa_elevations: stair from `G.stair_flights()`; guards are joinery; POOL
  SHALLOW datum; ground-line / steps / width checks stand on the HOUSE
  envelope (the walls group now reaches the plot boundary through the annex,
  so the ground line was sought outside the plot); with no fin array the
  orientation-on-the-model check uses an asymmetric window instead.
- villa_blender: ASSIGN `guards` -> glass, `grate` -> bronze; import comment
  corrected (item 9). villa_pool_check: floor profile + `pool_volume()`,
  VILLA_OUT.
- villa_dbc: new/stricter checks listed in its docstring (K-POOL-02 slope,
  profile-based K-POOL-03, grate must exist, POOL_BARRIER proved, every open
  landing/garden edge guarded, K-WIN-09, bays clear of steps).
- villa_design: check 7b (profile sanity), check 21 (gates), probes for the
  pool floor (shallow / slope / deep), grate, vault, one guard of each kind.

### Open
- Run the AutoCAD track: villa_3d_build (the COM profile path is untested),
  villa_3d_verify, villa_pool_check, villa_window_check, villa_load, villa_verify.
- `unreal\build_scene.py` has its own ASSIGN without `guards` / `grate`.
- The FF landing's 650 strip behind the stair-well guard (under the new north
  window) is reachable only for cleaning. (The GF stair's own balustrades:
  done in 12b.)
- (Check 16's widened door exemption: withdrawn in 12b.)
- Vault access hatch not modelled; `dubai_villa_rules.json` current_design
  statuses are stale; legacy villa_3d.py / villa_3d_native.py still type the
  old pedestrian gate.


### 12b. REVIEW FIXES  (2026-09-26, later)

A review of the integration found two blockers and a major. All three fixed
in data + checks; backups of the files before this round in
`%TEMP%\claude\fixB2\orig`.

1. **The annex could not be reached** (blocker). The majlis's street flight
   ran north to y 25550 at x <= 16565; the annex's west wall was at 16800,
   so the only way from the street to the annex doors and the whole east
   strip was a 235 mm slot. And the three annex landings (AX_FL +150 -> a
   1200 landing each) filled the 1550 service court, leaving 350 to the
   majlis wall (judge 3). Fixed:
   - annex west wall 16800 -> **17500** (plant 1250 wide / 4.4 m2, store and
     driver bath shifted 300, driver's room 2300 / 8.1 m2; furniture moved);
   - majlis street door 100 west (15150-16165): its flight is x 14850-16465,
     **1035** from the annex;
   - `AX_FL` 150 -> **0**: level thresholds (slot drains), no annex landings,
     the 1550 court is clear from the pedestrian gate to the east strip;
   - NEW check 22 `street_access()`: every external door must be reachable
     from a gate by a path >= `PATH_MIN_W` (900) -- plot less buildings,
     garden platform and every landing/flight, opened by a 900 disc; the
     target is the strip at the foot of each flight (or at a level
     threshold). The reviewer's case (annex back at 16800) fails it (test).
     The reviewer's own script `rvB\annex_access2.py` now says connected at
     every width up to 900.
2. **Check 16 had been loosened** (blocker) to exempt DOORS <= 1200 on
   east/west faces. Reverted to `kind == WIN`. The service door went back to
   the STREET face at the dirty kitchen's NW corner (3500-4515), its straight
   flight in the forecourt's NW corner (x 3200-4815, by the service gate);
   the car porch moved east of it: `PORCH_X0/X1` 4850-10900 (6050 wide, two
   3.0 m bays, no step in it), `VEHICLE_GATE` 5100-10700. A west-face service
   door now fails check 16 again (test).
3. **The stair's own open edges had no guards and nothing checked them**
   (major). Now:
   - the stair is data: `flights()` (the house stair's two flights AND every
     outside flight, with ascent direction, foot, riser, going, open sides),
     `flight_treads`, `pitch_at` (the nosing line), `stair_landing`,
     `stair_surfaces`, `stair_parts` (SOLID -- `STAIR_SOLID` -- treads and
     half-landing down to GF, plus the top nosing), `handrails`/`rail_parts`
     (`HANDRAIL_H` 900 over the nosing, 40 x 30 bronze, 100 into the flight);
   - guards: kinds 'stair flight' (a stepped glass panel per tread, 1200 over
     the nosing line's highest point on it; flight 1's west side outside the
     stair, flight 2's west side centred on the line between the flights, so
     each flight is 1035 clear) and 'stair landing' (the half-landing's west
     edge);
   - villa_dbc: `_house_guards` walks every edge of every tread, of the
     half-landing and of the first floor along every void, looks up what is
     beyond (wall / riser up or side of a solid flight / drop to the highest
     solid below) and wants a guard >= 1200 over the nosing where the drop is
     >= 760 (K-GRD-01/-02, K-SGR-01/-02); `_handrails` finds every OPEN side of
     every flight, inside and out, and wants a rail 865-965 over the nosing
     (K-HR-01) -- so the outside steps got handrails on posts too;
     `_flight_clear` measures K-STR-01 between the guards in a flight. Each
     fires on fault injection (tests): no stair glass, no well guards, no
     rails, `STAIR_SOLID = False`.
   - builders: villa_gltf groups `stair` (travertine) and `rails` (bronze),
     `xz_prism` for an east-west rail; villa_3d_build layers A-STRS-3D and
     A-RAIL-3D, `xz_prism3` (OCS normal +Y: OCS x = -X, y = +Z; bbox-checked
     and refused if wrong, NOT YET RUN against AutoCAD); villa_blender ASSIGN
     `stair`, `rails`; villa_elevations: `rails` is joinery, the section now
     projects the model's stair (`stair_solid()` builds the same parts);
     villa_cad draws the rails on A-GRDS-RAIL; `G.guards_on` counts a guard
     to the storey below up to the next floor (the upper flight's glass
     starts at +4829). Probes: the half-landing, a tread of each flight and
     clear above them, a rail inside and out, a post; the hall's void probe
     is taken clear of the stair (a 250 sphere would touch its glass).
   - villa_elevations' opening check read the wall lines from the view
     CLIPPED at street level, which by construction deletes the slab edge
     under any door at street level -- so the annex's level thresholds were
     "not in the model". It now reads them from the model (above street
     level the geometry is identical; whether a side is DRAWN is still judged
     on the view). W elevation lost its steps check (no steps face west now):
     46 checks, not 47.

Results (VILLA_OUT = `%TEMP%\claude\fixB2\final`, tests in `...\tests`):
villa_design 0 FATAL / 0 MAJOR (1 NOTE); villa_furniture_spec 0; villa_dbc 0/0;
villa_cad, villa_colour, villa_svg OK (title blocks 0/0, furniture 0);
villa_gltf 105/105 probes, 22 groups; villa_elevations 46/46, exit 0;
tests\test_builders_offline.py 27/27.

Open (added): `unreal\build_scene.py` ASSIGN also lacks `stair` / `rails`;
villa_3d_build's new STAIR/RAIL groups and `xz_prism3` are unrun (COM); the
stair's continuous inside handrail round the half-landing (K-HR-04) and the
one-tread rail extensions (K-HR-06) are detail-level and not modelled.


---

## 13. LIVE RUN, VERIFIED END TO END  (2026-09-26, main agent)

**Resume here.** Section 0 is historical; the current way in is the custom MCP
server (restart Claude Code first so it loads the new code), or by hand:
```
python villa_design.py        # 0 FATAL / 0 MAJOR incl. DBC (check 20 -> villa_dbc)
python villa_cad.py; python villa_colour.py; python villa_gltf.py; python villa_elevations.py
python villa_3d_build.py; python villa_3d_verify.py; python villa_pool_check.py; python villa_window_check.py
python villa_load.py; python villa_verify.py; python villa_show.py
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P villa_blender.py
powershell -ExecutionPolicy Bypass -File unreal\render_unreal.ps1
```
MCP: `villa_status` lists stale stages, `villa_run(stage)` runs one; COM stages
hold the server's lock.

State at the end of the session, all measured:
- Design B + integration: GFA 411.0 m2 (brief 418), 4 bed + study, majlis with
  its own street door, service wing, NE driver annex at street level.
  `villa_design.py` 0/0 (DBC included); furniture 0 issues; the skill's generic
  `validate_plan.py --dbc --hardscape villa_colour:ground_surfaces:...` 0/0.
- glTF probes 105/105; AutoCAD probes 99/99 + 6/6; 91/91 opening probes; pool
  holds water; all 21 shared groups have the SAME volume in AutoCAD and glTF
  (to the cubic mm); 98/98 blocks verified (GF 46 + AX 9 on A-102, FF 43).
- Elevations A-201..A-204 + section A-301: 46/46 checks.
- Renders: Blender (render\out, 5 views, ~60 s) and Unreal path tracer
  (render\unreal, ~2 min); Twinmotion package render\twinmotion (22 named
  groups, 11 materials, normal maps verified correct).
- 54 superseded 09-06/09-09 files MOVED (not deleted) to
  Desktop\Villa\_superseded_0906-0909\ with MOVED.txt.

Fixed live this session (each now has a check or test):
1. Catalogue fridge 572x515 and dishwasher 600x600 were wrong: multi-view AEC
   blocks, measured in the sheet at four rotations = 600x629 / 600x620 (mm).
2. Blender Bump node between normal map and BSDF made the glTF exporter write
   the displacement image as normalTexture (7/8 materials). Bump only where no
   normal map now.
3. villa_run's case-insensitive `failed` marker failed a perfect render on
   Blender's HIP driver warning. Case-sensitive now + regression test.
4. The generic validator assumed a full-storey drop under the stair arrival;
   it now reads `stair_surfaces()` (villa_dbc had it right).
5. Unreal build_scene ASSIGN lacked guards/grate/stair/rails.

Open, for the user to decide: roof pavilion not built (NOTE); majlis 25.3 m2 is
at the brief minimum and below dataset p5 (typicality INFO, not a failure);
Twinmotion render is manual (no API) - see render\twinmotion\TWINMOTION_STEPS.md;
real vegetation (palms/ghaf), people and cars need Twinmotion's library or an
approved download; the AutoCAD install is a NON-COMMERCIAL trial.


## 14. PROJECTS + THE FAIRWAY VILLA  (2026-09-26, later; supersedes 13 where they differ)

**Resume here.** The pipeline now builds any number of designs. The villa is
unchanged (the regression gate below proves it); a second design, the Fairway,
was designed, validated, drawn, modelled in AutoCAD and rendered.

What was done:
- `run_project.py <name> <script>` runs any stage against `projects\<name>\`
  (its own villa_design.py / villa_furniture_spec.py / block_catalog.json).
  Builders read opt-in hooks (STACKED, BELOW_GRADE_FLOORS, GROUND_FLOOR,
  massing(), landscape_parts(), ground_surfaces(), STAIRS/flights(),
  stair_columns(), PLAN_SHEETS, SECTION_X, RENDER_VIEWS, RENDER_CONTEXT,
  MATERIALS, OUT_NAME, PROJECT_TITLE). Generalised: villa_geom, villa_gltf,
  villa_3d_build/verify, window/pool checks, villa_cad/colour/svg/pdfset,
  villa_load/verify/show, villa_elevations, villa_blender, unreal\*, villa_dbc,
  the skill's validate_plan.py, server.py (project= on villa_validate /
  villa_status / villa_run; new `elevations` stage).
- villa_dbc: basement rules K-BSMT-01..06, every stair checked per flight
  (K-STR-03/-04/-05/-09/-11), K-GRD-03 open-riser gaps, openings passable only
  up to their head, room clear sizes measured on the NET floor, BOUNDARY_T,
  GROUND_FLOOR. Found real faults in the Fairway (maid room, bedrooms 4/5,
  master, service-stair landing and foot) -- fixed in the design, not the check.
- Fixed while doing it: server.py kept a stale villa_dbc bound to the first
  design; AutoCAD documents were found by NAME only (the Fairway build would
  have closed the villa's open model unsaved) -> villa_geom.find_doc(name,
  folder); a busy AutoCAD's AttributeError("<unknown>.Add") is now retried in
  villa_3d_build / villa_3d_verify.
- Regression gate: `python -X utf8 tests\regress_villa.py` -> IDENTICAL to the
  baseline (40 files: cad, colour, gltf, elevations). Baseline now committed
  with the code: tests\baselines\villa_baseline_snap.json. Pre-change code:
  `_pre_projects_0926\`. Offline tests: 354 pass (243 pipeline + 111 skill).

The Fairway (`projects\fairway\`, outputs in Desktop\Fairway) -- a STUDY
RECREATION of a Dubai Hills Estate listing (5 bed + maid, 12,600 sq ft BUA,
13,033 sq ft plot), designed to the published figures and 30 photographs; no
plans existed. Assumptions A1-A10 and open questions in its BRIEF.md.
- B1 (cinema, media lounge/bar, gym, spa, wine cellar, play, laundry, plant)
  + GF + FF (5 suites); BUA 1,188 m2 (+1.5 % on the listing); two stairs
  (floating feature GF-FF, enclosed service B1-GF); skimmer pool with sun ledge.
- 0 FATAL / 0 MAJOR (own validator with the stricter DBC checks, and
  validate_plan --dbc --hardscape); furniture 0 issues (147 items).
- glTF 166/166 probes; AutoCAD (live, after the last design change): 66
  solids / 21 layers incl. A-STON-3D, 160/160 probes + 6/6 controls, 277/277
  openings, pool 48.6 m3, 147/147 blocks; elevations + section 55/55.
- Renders: Blender 7 views (2400x1500, 256 spp) in render\out; Unreal 7 views
  (1024 spp) in render\unreal; Twinmotion notes in render\twinmotion.

Handover: Desktop\AutoCAD_Villa_Handover\AutoCAD_Villa_Handover_2026-09-26.zip
(report REPORT.html + code + skill + MCP notes + samples; built by
tools_pack_handover.py; no DBC PDF/text, no third-party blocks, no secrets).

Open, for the owner: commercial AutoCAD licence (the seat is a TRIAL); git;
the Fairway's real plans (from the listing agent) to replace assumptions;
Vastu/Qibla orientation not modelled; sun ledge vs DBC K-POOL-03; basement
recreation rooms treated as non-habitable (K-BSMT-03); the MCP render stage
still expects the villa's image names for projects; VILLA_ANNEX_LIGHT_FIX
(villa annex light height) awaits approval; renders are review-grade (empty
interiors, placeholder planting) -- see the report's roadmap.

## 15. RESEARCH, MODEL ROUTING, SAFETY SWITCHES, RULE-BY-RULE REPORT  (2026-10-08)

Research (5 Haiku 5.5 researchers; every finding checked by Opus 5.5):
autocad-mcp\research\2026-10-08\RESEARCH_BRIEF.md.
- 112 findings: 68% verified, 29% partly true, 1 wrong, 0 fabricated.
- Key facts:
  - Haiku 5.5 released 2026-10-07; the `haiku` alias means 4.5 off the
    Anthropic API.
  - MCP spec 2026-07-28 (no initialize handshake), negotiated by Claude Code
    since 2.1.287. Both of our servers were tested working under 2.1.293.
  - Autodesk's own AutoCAD MCP server is read-only and Assistant-only.
  - UE 5.8 has an Unreal MCP plugin plus Epic's Claude Code skill.
  - blender-mcp CVE-2026-66004.
  - Twinmotion 2026.2 drops DXF.
  - Dubai Municipality is building an AI villa-permit checker.

Blind model benchmark (offline 2D pipeline, effort xhigh, Opus judge; model
IDs confirmed from transcripts):
- Repair 6 injected faults:
  - Haiku 5.5: 7-8/10, $0.20.
  - Sonnet 5.5: 7/10, $0.74.
  - Opus 5.5: 8/10, $1.12.
- New simple villa from a brief:
  - Haiku 5.5: 2/10 and 4/10 ($1.4-2.1). Its layouts passed the checks with
    an unusable stair and doors opening into a void.
  - Sonnet 5.5: 7/10, $5.75.
  - Opus 5.5: 6/10, $12.74.
- Routing table, escalation rules and the 12 check gaps the judges found:
  skill references\model-routing.md.
- Pinned agents: ~/.claude/agents/cad-*.md.
  - design-fixer, researcher, runner: Haiku 5.5.
  - designer: Sonnet 5.5.
  - judge, fact-checker, pipeline-engineer, render-critic: Opus 5.5.
- Bench data in %TEMP%\villa_bench* (temporary); cost script in
  %TEMP%\villa_bench_tools\cost.py.

server.py safety switches (built by Opus; adversarially reviewed for
regression and security; 1 major and 7 minor findings fixed):
- ACAD_ALLOW_RAW_COMMAND (default off: acad_send_command refuses).
- ACAD_WRITE_ROOTS (default Desktop / autocad-mcp / %TEMP%; SaveAs, PDF and
  PNG paths resolved and checked).
- ACAD_READ_ONLY (also refuses project= folders outside the pipeline).
- ACAD_AUDIT_LOG (logs\mcp_calls.jsonl, rotating).
- The tool listing is byte-identical to before. Tests: test_server_safety 52
  + offline 36 + projects 30 = 118 OK. Backup server.pre_hardening_1008.py.
  The RUNNING server keeps the old code until Claude Code restarts.

validate_plan.py --rules-report PATH (.md, .csv, .json):
- One row per DBC rule (146 + 18 not-covered) with FAIL, NOTE, PASS,
  NOT CHECKED, NOT APPLICABLE or MANUAL. PASS only if the check RULE_CHECKS
  names ran and recorded testing the rule; a partly tested rule is NOT
  CHECKED (Ctx.untested).
- New checks: stair headroom (K-STR-11, needs flights()); floor landings at
  every flight's foot and head (K-STR-09); balcony guards; OVERHANGS and
  balconies as projections (K-PRJ-03/-04); pool-deck gaps; sliding doors;
  enclosed garages.
- Tests: 140 OK. Backups *.pre_rules1008.*. Sample:
  skill samples\fairway_rules_report.md. Both Haiku benchmark designs now
  FAIL (0 mm stair landing; headroom -476 mm); Sonnet's and Opus's pass.
  The villa and the Fairway are unchanged (0 FATAL / 0 MAJOR).

Fixed: projects\fairway villa_design.report() named the Fairway's second
stair and crashed one-stair designs copied from it. It now lists STAIRS, and
the Fairway output is byte-identical (backup villa_design.pre_report1008.py).

Regression gate: cad + colour IDENTICAL to the baseline (6 files). The gltf
and elevations stages are BLOCKED. Windows Smart App Control is now enforcing
(VerifiedAndReputablePolicyState=1) and refuses the unsigned OpenCascade DLLs
in site-packages\cadquery_ocp_novtk.libs (CodeIntegrity events 3033/3077).
Every build123d stage fails until the owner decides: SAC off, or run
build123d in WSL / another machine. Not changed by us; it is a security
setting.

Open: check gaps 2-10 and 12 in model-routing.md (door onto a void, door
approach zones, door-swing clashes, ensuite door, suite hierarchy, service
route, carport bays, label overlap, colour-plan sanitaryware, washer/dryer
blocks); port the new stair checks into villa_dbc; rebuild the handover zip.

### 15b. Check gaps closed  (2026-10-08, later)

New checks in validate_plan.py (175 tests OK; built by the pinned
cad-pipeline-engineer; reviewed for false positives/negatives and for
regression; all 12 findings fixed):
- door-zones: FATAL if a door opens onto a void or has less than 710 mm
  free; MAJOR if it clips a wall.
- door-approach: furniture inside 700 mm is MAJOR, 700-900 is a NOTE.
- door-swings: overlapping swings are MAJOR.
- ensuite-door: MAJOR, allowing a route through the suite's own dressing
  room.
- suite-hierarchy: NOTE.
- service-route: NOTE.
- carport piers inside dbc-parking (K-PARK-03).

New sheet_check.py (22 tests): label overlap and clearance by rendered ink.
villa_colour.py: sanitaryware now visible (opaque white plus an outline;
before, it was tile on tile).

The new checks find REAL defects in the finished designs (not fixed; the
owner decides):
- villa: the FAMILY WC basin stands across 260 of the door's 710 mm (MAJOR).
- Fairway (MAJOR):
  - the maid bed is 450 mm in front of the maid-bath door;
  - the driver bed is 300 mm in front of the driver-bath door;
  - the spa shower is 50 mm in front of the steam-room door.
- Fairway (NOTE): the carport piers leave 5400 mm clear, so 1 bay, not 2
  (3 bays in total with the garage).
- Fairway elevations A-201..204: the "200" dimension text is crossed by the
  8900 dimension line.
The benchmark designs: every judge finding is now raised by a check.

Regression gate (cad + colour): CHANGED only by the intended sanitaryware
outlines (VILLA_A102P/A103P A-FLOR-FIXT 0 -> 10/14). Not re-baselined yet:
wait for the owner's decision on the design fixes above, then re-baseline
once.

### 15c. 3D stages moved to WSL; owner decisions  (2026-10-08, later)

Owner decisions (2026-10-08):
- The four design defects found by the new checks (villa FAMILY WC basin;
  Fairway maid bed, driver bed, spa shower) are LEFT AS KNOWN ISSUES. The
  designs and Desktop deliverables are unchanged.
- The 3D stages run in WSL; Smart App Control stays ON.

Smart App Control (enforcing) judges each unsigned binary separately, and
its verdicts change: it refused OpenCascade's DLLs, later allowed them and
refused scipy's _propack.pyd / _libsvm_sparse. Windows Python therefore
cannot be trusted for build123d.

- tools_wsl3d_setup.sh (run once, done): Ubuntu-24.04 venv ~/villa3d with
  the Windows versions (build123d 0.13.0, cadquery-ocp-novtk 8.0.1.0.0,
  ezdxf 1.4.4, shapely 2.1.2, numpy 2.5.2, ...). Links ~/.claude/skills ->
  Windows, otherwise the DBC rules file is missing and every stamp reads
  "1 MAJOR". Links the Windows fonts.
- tools_wsl3d.py: runs any pipeline script in WSL, translating VILLA_OUT,
  VILLA_DESIGN_DIR and path arguments.
- server.py: stages with "occ" (gltf, elevations) are routed through
  tools_wsl3d.py while Smart App Control enforces, or when a full build123d
  import fails. VILLA3D_VIA_WSL=1 forces it, 0 forbids it. Backup
  server.pre_wsl1008.py. tests\test_server_wsl.py has 13 tests; the server
  total is 131 OK. One existing test was pinned to the native command.
  End to end: villa_run(gltf, project=fairway) via WSL gave verdict ok.
- Regression gate:
  - Windows cad + colour: IDENTICAL (6 files).
  - WSL gltf + elevations: IDENTICAL (34 files).
  - The colour baseline was re-baselined for the intended sanitaryware
    change only (VILLA_A102P/A103P). The old baseline is in
    tests\baselines\villa_baseline_snap.pre_sanitary1008.json.
  - test_builders_offline in WSL: 27/27 OK.
- The running MCP server picks all this up only after Claude Code restarts.

Handover v3 (2026-10-08): Desktop\AutoCAD_Villa_Handover\AutoCAD_Villa_Handover_2026-10-08.zip
- 125,969,352 bytes, 539 files; secret/PII scan clean; CRC OK.
- Adds:
  - COST_REDUCTION_REPORT.pdf/.md, a 2-page brief on model routing to cut
    usage;
  - UPDATE_2026-10-08.md;
  - agents/ (8 pinned cad-* agents);
  - research/ with benchmark_results.json;
  - tests/fixtures/bench_2026-10-08/, which the skill tests now use instead
    of %TEMP%.
- Packager changes:
  - skips *.pre_*.* and _pre_gaps1008;
  - the sk- key pattern now has to start a token (a URL containing
    "autodesk-" had tripped it);
  - the MCP example lists the safety switches.

## 16. DEMO PREP: VILLA ALBA PROMPT + TOOL FIXES  (2026-10-16)

- The weekly research is in research/2026-10-16/WEEKLY_UPDATE.md. It cost $1.60
  (Haiku researchers $0.05, Opus checks $1.16, Sonnet write-up $0.39). The pinned
  cad-researcher kept its prompts at 31-45K tokens, under the Haiku cliff.
- The demo prompt (not yet run) and the recording checklist are in
  Desktop\House_Demo\HOUSE_DEMO_PROMPT.md and BEFORE_YOU_RECORD.md: a G+1 villa,
  25 x 40 m plot, a one-sided overflow pool. An Opus feasibility review found 9
  blockers; all are folded into the prompt.
- Tool fixes from that review:
  - server.py: the render stage outputs are "render/out/villa_*.png" and
    render_log.json, so a project's own views count. villa_status no longer says
    "missing" for projects. Backup server.pre_demo1016.py. Server tests 131 OK.
  - tools_drawing_set.py: --title, --sub, --status "A|B|C" and --checks. The
    defaults reproduce the Fairway cover and PDF subject exactly. Backup
    tools_drawing_set.pre_demo1016.py.
  - tools_cost.py (new): the cost of a whole session (main + subagents +
    workflows) by model and by agent, with --since to cost one run. It reuses the
    benchmark cost.py arithmetic.
- Review risks the prompt now handles:
  - The Fairway validator tail needs a stair named "feature stair",
    GF-200 <= POOL_TW < GF, a POOL_LEDGE, and RAMP_Y0/Y1.
  - OUT_NAME must change, or villa_run writes into Desktop\Fairway.
  - validate_plan needs --hardscape (or DECKS) for the pool deck.
  - A detached plant pavilion fails reachability.
  - Subagents cannot write BRIEF/RESULTS files.
  - A lowered lawn must stay under the 760 mm guard threshold.
- Estimate: 2.75-3.5 h nominal; 4.5-5.5 h with AutoCAD and one redesign round.
