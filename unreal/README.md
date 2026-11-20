# Villa renders in Unreal Engine 5.8 (scripted, path traced)

Twinmotion has no API; Unreal does. This folder renders the villa photoreal with
the Path Tracer through Movie Render Queue, from the same glb the Twinmotion
package uses, with no clicking.

## One command

```
powershell -ExecutionPolicy Bypass -File C:\Users\lsire\autocad-mcp\unreal\render_unreal.ps1
```

Output: `C:\Users\lsire\OneDrive\Desktop\Villa\render\unreal\villa_aerial_sw.png`,
`villa_garden.png`, `villa_street.png` (2400 x 1500, 1024 spp, denoised) and
`unreal_log.json` (cameras, sun angles, import check, timings).
A full run takes about 1.5 minutes on the RTX 5070 Ti once shaders are cached.
The first run on a machine compiles shaders and takes much longer.

After the model is re-exported (`villa_gltf.py`, then `villa_blender.py`), run the
same command again. Every run rebuilds the level from the current glb.

### Options

| Option | Default | Notes |
|---|---|---|
| `-Stage all\|setup\|build\|render\|paths` | `all` | Runs `setup`, `build`, then `render`. `paths` prints the folders a run would use (JSON) and starts nothing. |
| `-Views aerial_sw,garden,street` | these three (a project: all its `RENDER_VIEWS`) | `aerial_ne` is also defined. |
| `-Samples 1024 -Width 2400 -Height 1500` | | Use 128 to 256 spp at 1200 x 750 for drafts. |
| `-Glb <path>` | `<Villa>\render\twinmotion\villa_twinmotion.glb` | |
| `-Groups <path>` | `<Villa>\render\groups.json` | The import is checked against it. |
| `-OutDir <path>` | `<Villa>\render\unreal` | |
| `-Recreate` | off | Deletes `VillaRender\` and rebuilds the project from the template. |

`<Villa>` is `%VILLA_OUT%` when it is set, otherwise `Desktop\Villa`. This is the
same rule every builder follows, so a test run with `VILLA_OUT` set to a temp
folder reads and writes only there.

### Projects

A project (`projects\<name>`, see `run_project.py`) renders the same way. Set
`VILLA_DESIGN_DIR` to its folder and `VILLA_OUT` to its deliverables, run
`villa_gltf.py` and `villa_blender.py` for it first (the Blender run writes the
glb and, beside it, `views.json` and `materials.json`), then:

```
$env:VILLA_DESIGN_DIR = 'C:\Users\lsire\autocad-mcp\projects\fairway'
$env:VILLA_OUT = 'C:\Users\lsire\OneDrive\Desktop\Fairway'
powershell -ExecutionPolicy Bypass -File C:\Users\lsire\autocad-mcp\unreal\render_unreal.ps1
```

- The level is built under `/Game/<Name>` (the villa's `/Game/Villa` is left
  alone; the texture library `/Game/Villa/Textures` is shared), the logs go to
  `logs\<name>` and the queue to `Saved\MovieRenderPipeline\QueueManifest_<name>.utxt`.
- Cameras come from the design's `RENDER_VIEWS`, with the eyes villa_blender.py
  rendered (a design eye inside a hedge or wall is moved clear there) and a
  Dubai date and time whose sun matches each view's `(azimuth, elevation)`.
  Exposure and white balance follow the sun's elevation. An interior view
  (`'interior': True`) is shot the way villa_blender.py shoots it: the room
  lights are turned down to 30 % for that camera cut (their intensity is keyed
  per cut in `LS_Villa`), the exposure is set from the exterior's, and the
  white balance is set for the 3000 K lamps (3500 K) instead of the sun's --
  at the sun's balance the lamps turn white walls ochre.
- Materials come from the design's `MATERIALS` kinds: textured kinds use the
  same ambientCG sets, tinted to the design's colour with the texture averages
  and 99th percentiles Blender measured (`materials.json`) by the same
  `fit_tint` as villa_blender.py: a set far darker than the colour (Grass001
  under the lawn needs x5-x10) is pulled toward its own average before it is
  tinted, so it reaches the colour without blown highlights (the old x4 clamp
  left the lawn dark and saturated, and the golf stripes all one shade).
- A textured kind renders with the design's **roughness**
  (`MATERIALS[group].roughness`). The set's roughness map only modulates it:
  `rough_fit`, the same function as villa_blender.py's, gives the master's
  `RoughnessMul` / `RoughnessAdd` / `RoughnessMin` / `RoughnessMax`, so the
  map is clamped to within 0.12 of the design's value and keeps at most 0.05
  of spread. The map statistics come from `materials.json`
  (`_roughness_stats`); without them, the design's value is used flat. Before
  this, the map was taken as it is. Travertine001 is shot polished (mean
  0.026), so the Fairway's limestone paving and coping (0.75 / 0.7) and its
  stair (0.5) rendered as a near-mirror. `Specular` stays 0.5 (F0 0.04, right
  for stone). The villa's instances do not set the band, and its defaults
  (0 / 1) are the identity.
- `stone_dark` (the stacked-stone flank, the BBQ wall, the piers) is
  `M_VillaStone`: villa_blender's ledgestone in HLSL on the mesh UVs (metres,
  V up the wall). It has 68 mm courses, stones 250-700 mm long, each stone
  its own shade, 3.5 mm shadow joints and a split-face relief.
  `render_white` and `metal_black` are plain colours.
- The pool's mosaic slot is blue. The water tints each crossing as 1.4 m of
  villa_blender's water would, with calm ripples. Half its surface scatters
  the water's own colour: a thin surface cannot refract the eye-level view
  down onto the tank floor, and without the scatter the pool read navy.
- The stone skin counts as a wall for the interior-light room test.
- Interior floors: villa_blender's `FLOOR_FINISH` / `floor_plan`, the same
  function in build_scene.py. Every room above grade gets a floor, less its
  nested rooms and voids: polished travertine (0.18), oak in the bedrooms,
  dressing and family lounge, and concrete in the service rooms. The floors
  are 10 mm boxes, world-aligned at the set's real size.
- The room lights are keyed per camera cut: an interior cut at 0.3, an
  exterior cut at villa_blender's `EXTERIOR_LIGHTS` (0.5,
  `VILLA_UE_EXTERIOR_CUT`). At full strength the ground-floor glazing glowed
  amber.
- No shrub scatter when the design's planting is a clipped hedge (the hedge is
  the planting; shrubs at its foot read as black boulders in its shade).
- Without `VILLA_OUT` a project reads and writes `Desktop\<OUT_NAME>` (from its
  `villa_design.py`, else the folder name capitalised -- run_project.py's rule),
  never `Desktop\Villa`: the script refuses a project whose model would come
  from the villa's folder (its PNGs share names with the villa's).
- The neighbours stand at the design's setbacks (three plots a side along the
  street), and the pool is cut out of the context ground slab. A design with
  `RENDER_CONTEXT = {"south": "golf"}` gets a golf course behind its rear
  boundary (rough, mown fairway, rough), as in the Blender render.
- Palms at `SITE_TREES` are villa_blender's own palms. The Blender run writes
  `villa_palms.glb` beside the model: the tapering trunks and the arching
  frond strips. build_scene.py merges it into the model glb (`merge_glb`) and
  imports the two together. Only the first Interchange import of a script
  runs synchronously; a second one returns nothing and never completes before
  the script ends (measured). The fronds get `M_VillaFrond`: masked,
  two-sided foliage, with the leaflets cut from the strip by its UVs as the
  Blender frond material cuts them. Every trunk must land within 1 m of its
  `SITE_TREES` point. Otherwise, or without the file, the scene falls back to
  the older blade palms (seeded heights and leans, trunk segments and frond
  blades).
- The slatted gate leaves in `V.gates()`.
- Interior lights: a design's room test knows its nested rooms (an en-suite's
  partition is not "a wall inside the bedroom"), its voids (the probe and the
  light move off a stair void) and its openings (a ray through a door or an
  open plan counts), so every room the glb has gets its light; a rejected room
  is listed with its reason. The villa keeps the original test.
- Not in the Unreal scene (Blender only): the hedges' leaf cards.

The following environment variables are read by `build_scene.py`:

- `VILLA_UE_INTERIOR_LUX`: interior lights, default 12000. Set it to 0 to turn them off.
- `VILLA_UE_INTERIOR_CUT`, `VILLA_UE_INTERIOR_WB`, `VILLA_UE_EV_INTERIOR`: a design's
  interior camera cut -- the room lights' scale (default 0.3), the white balance
  (K, default 3500) and the exposure relative to the exterior's (EV, default -1.2).
- `VILLA_UE_EXTERIOR_CUT`: a design's exterior camera cut, the room lights' scale
  (default 0.5, villa_blender's `EXTERIOR_LIGHTS`).
- `VILLA_UE_WATER_SCATTER`: the share of a design's pool surface that scatters the
  water's colour (default 0.5).
- `VILLA_UE_HAZE`: Mie scattering as a multiple of Earth's, default 2.5.
- `VILLA_UE_DESIGN`: path to `villa_design.py` (default: `VILLA_DESIGN_DIR`'s, else the villa's).
- `VILLA_UE_TEX`: the ambientCG folder, or several joined by `;` (each set is looked up in turn).
- `VILLA_UE_ROOT`: the content folder (default `/Game/Villa`, a project's `/Game/<Name>`).

## What the stages do

1. **setup**: creates `VillaRender\` from `UE_5.8\Templates\TP_AEC_BlankBP`. It uses the
   AEC template because it is Blueprint-only (TP_Blank carries a C++ module that
   would need a compiler) and already has ray tracing and the path tracer turned on.
   The copy follows `TemplateDefs.ini` exactly, the way GameProjectUtils does it:
   - It skips the template's ignore lists (`Media`, its `.uproject`, `TemplateDefs.ini`).
   - It replaces the template name in `ini`, `cs`, `cpp` and `h` files.
   - It writes `VillaRender.uproject` with `EngineAssociation 5.8`.
   - It adds the redirects:
     - `+ActiveGameNameRedirects` from `TP_AEC_BlankBP` and `/Script/TP_AEC_BlankBP`
     - `[URL] GameName`
     - a new `ProjectID` and `ProjectName` in `DefaultGame.ini`
   - It enables these plugins: PythonScriptPlugin, EditorScriptingUtilities,
     SequencerScripting (the template has it off), MovieRenderPipeline, SunPosition,
     Interchange (with its glTF translator), InterchangeEditor, InterchangeAssets and
     NNEDenoiser.
   - It copies each plugin's `SupportedTargetPlatforms` from the engine. Without this,
     the editor flags the project as "requires update".

   Deliberate project changes:
   - `r.AllowStaticLighting=False`: path tracing only, so there is no "lighting needs
     rebuild" and fewer shader permutations.
   - `r.Substrate=False`: legacy materials give predictable translucency in the path tracer.
   - The game default map points at the template's `Main` instead of the BlankDefault
     feature pack, which a plain copy does not install.
   - `DefaultEditorSettings.ini` sets `bSendUnattendedBugReports=False`. An
     `-unattended` editor otherwise sends crash reports to Epic without asking. The
     script also stops the crash-monitor process a run leaves behind.
2. **build**: runs `UnrealEditor-Cmd -ExecutePythonScript=build_scene.py -unattended
   -nopause -nosplash`. Before the editor starts, it deletes `Content\Villa\{Maps,Model,
   Render,Materials,Pipelines}`, so the build starts clean. Then `build_scene.py`:
   - **Imports the glb with Interchange.** It imports meshes only, with full-precision
     UVs, because the UVs are baked at real-world size. Nanite, lightmaps and collision
     are off. The glb's own materials are skipped because Blender exported its height
     maps as normal maps.
   - **Measures the axis mapping.** It does not assume one. It tries the eight signed
     axis permutations and keeps the one under which all 18 mesh bounds match
     `groups.json`. The result today is UE(X, Y, Z) = (x, −y, z) × 100 with an error of
     0.00 cm. Model north (+Y) is UE −Y. Cameras, context and north all go through this
     one measured mapping.
   - **Builds materials in Python.** They use the ambientCG sets and tints from the
     Blender render, with NormalDX maps (Unreal's convention).
     - The PBR master has colour detail, saturation, roughness and normal controls, and
       world-XY UVs for the context boxes. It has no static switches: static-switch
       instances rendered with the wrong parameters in the path tracer.
     - Glass and pool water use the Thin Translucent shading model. Shadow rays pass
       through it, so sun reaches the rooms and the pool floor. The per-crossing
       transmittance tints the pool aqua; legacy translucency has no absorption.
   - **Adds context:** ground, street, pavements and neighbouring plots (same numbers as
     the Blender render), and shrubs scattered over the planting-bed tops. The shrubs
     are kept clear of walls.
   - **Adds interior lights**, one warm (3000 K) light per room in `villa_design.ROOMS`. A
     light is placed only where the glb actually has that room: rays from the room
     centre must find its walls, floor and ceiling. Rooms that are missing from a stale
     export are listed in the status file.
   - **Adds a SunSky** (SunPosition) for Dubai: 25.2048 N, 55.2708 E, UTC+4, no daylight
     saving. North offset is −90° so that model +Y is north. The script checks this by
     reading back the DirectionalLight and comparing it with
     `SunPositionFunctionLibrary`. It fails if the two differ by more than 1°.
   - **Sets up exposure and cameras.** An unbound PostProcessVolume holds the path
     tracer settings (16 bounces, denoiser). There is one CineCameraActor per view: a
     36 mm filmback and the same lenses as Blender, manual exposure (EV100), and white
     balance per view. The eye-level views use two-point perspective: a level camera
     with a shifted filmback, so verticals stay vertical.
   - **Creates `LS_Villa`**, a LevelSequence with one camera cut per view. Each view is
     one frame, and SunSky `Month`/`Day`/`SolarTime` are keyed per view:

     | View | Camera (m) → target | Date and time | Sun (az / el) |
     |---|---|---|---|
     | aerial_sw | (−13, −17, 21) → (12, 13.5, 3) | 20 Mar 10:00 | 120° / 46.5° |
     | garden | (19.2, 3.2, 2.4) → (11, 14, 4.4) | 15 Dec 15:30 | 228.5° / 22.2° |
     | street | (5.5, 38, 1.7) → (11, 21, 4.2) | 21 Jun 18:15 | 290.9° / 11.0° |

   - **Sets up the render job.** It creates an MRQ job (Path Tracer pass, PNG, spatial
     samples = spp, warm-up frames, full texture loading) and saves it to
     `Saved\MovieRenderPipeline\QueueManifest.utxt`. It also exports the preset as
     `/Game/Villa/Render/MRQ_VillaPathTracer` for use from the editor UI.
   - **Writes `logs\build_status.json`.** The PowerShell script trusts this file, not the
     editor exit code, because UE 5.8 sometimes faults after the log has closed.
3. **render**: runs `UnrealEditor-Cmd <project> /Game/Villa/Maps/Villa -game
   -MoviePipelineConfig="MovieRenderPipeline/QueueManifest.utxt" -RenderOffscreen`.
   The manifest must sit under `Saved`, given relative to it, which is what MRQ's own
   remote executor passes. Frames land in `logs\frames\villa_000N.png` and are copied
   to the output folder under their view names.

## Files

| File | What it is |
|---|---|
| `render_unreal.ps1` | The one command: setup, build and render. |
| `build_scene.py` | The Unreal Python scene build. It runs inside the editor. |
| `VillaRender\` | The generated UE project. `Saved`, `Intermediate` and `DerivedDataCache` are UE caches. |
| `logs\` | Editor logs, `build_status.json`, the queue manifest copy and raw frames. |

## Known limits

- The glb on the Desktop predates the current `villa_design.py` (candidate B), so
  only 4 of 29 rooms match and get interior lights. The other windows read dark.
  This clears after a re-export.
- The vegetation is abstract shrub mounds, as in the Blender render. There are no
  palms, people or cars. Neighbouring buildings are massing boxes.
- Context boxes must not be near-coplanar with the ground. A 2 cm street slab 5 mm
  above the ground dropped out of the path-traced scene, so the street now stands
  3 cm proud of the ground.
