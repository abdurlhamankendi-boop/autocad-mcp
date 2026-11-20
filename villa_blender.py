"""Render the villa -- or a PROJECT's design -- in Blender (Cycles), and
package it for Twinmotion.

Run inside Blender, headless:

    blender -b --factory-startup -P villa_blender.py -- [options]

    --samples 256          Cycles samples per view (denoised)
    --res 2400x1500        output size
    --views aerial_sw,garden,street,aerial_ne,plan
                           (a project: its RENDER_VIEWS, all by default)
    --hdri goegap          file stem in render/hdri
    --sun-az 225           sun azimuth, degrees clockwise from north
    --no-render            build, save .blend and export only

Everything is driven from what villa_gltf.py writes, which is driven from
villa_design.py -- so the render cannot show a different building from the
drawings. Materials follow villa_materials_spec.md: board-marked concrete,
travertine, fumed oak, bronze-anodised aluminium.

Texture scale is not guessed. Every face gets world-space UVs at 1 unit = 1 m,
and each ambientCG set is scaled by the physical size it declares
(materials.json), so a 1.2 m travertine tile renders at 1.2 m.

PROJECTS (projects\\<name>\\, see run_project.py). The environment says which
design and where:
  VILLA_DESIGN_DIR  the folder whose villa_design.py is imported (first on
                    sys.path); unset, the villa's beside this file
  VILLA_OUT         a project's deliverables folder: the glb groups are read
                    from VILLA_OUT\\render, the .blend, the renders
                    (render\\out) and the Twinmotion package
                    (render\\twinmotion) written there. Unset: Desktop\\
                    <OUT_NAME> (else Desktop\\<Folder>); a project that would
                    land in the villa's Desktop\\Villa is refused, and so is a
                    VILLA_DESIGN_DIR without its own villa_design.py.
                    The VILLA keeps Desktop\\Villa\\render (the pre-projects
                    constant) and ignores VILLA_OUT unless
                    VILLA_RENDER_FOLLOWS_OUT=1
  VILLA_ASSETS      where the downloaded ambientCG sets and HDRIs live
                    (materials\\, hdri\\); default Desktop\\Villa\\render. A set
                    not yet unpacked there is unpacked into VILLA_OUT\\render\\
                    materials\\_tex, never beside the downloads. Nothing is
                    downloaded.
A design that declares them is rendered with its own hooks, and the villa
(which declares none) exactly as before:
  MATERIALS     {group: {kind, color, roughness}} -- a recipe per kind
                (KIND_RECIPES), coloured to the design's colour (a texture
                set is tinted, and flattened toward its average where a
                tint alone would blow out its highlights -- fit_tint;
                materials.json flags a colour it still cannot reach), at the
                design's roughness (a set's roughness map only modulates it
                -- rough_fit; materials.json carries the fit and the maps'
                statistics for the Unreal build); the villa's ASSIGN is the
                fallback for a group it does not list
  RENDER_VIEWS  {name: {eye, target (m), lens (mm), sun (az, el), interior}}
                -- eye-level cameras are two-point (level + shifted), an
                interior view gets its own exposure
  SITE_TREES    (x, y, crown mm) -- palms in the render context (also
                written as twinmotion\\villa_palms.glb, which the Unreal
                build plants)
  PLOT_W/PLOT_D/SB_*  the neighbours stand at the design's setbacks
  RENDER_CONTEXT  {"south": "golf" | "lawn"}: what lies behind the rear
                (south) boundary; a design's context also reaches the horizon
                (FAR_FIELD_M), so the HDRI's photographed ground never shows
The villa's annex room lights keep the original (FF-ceiling) height unless
VILLA_ANNEX_LIGHT_FIX=1 (see interior_lights).
"""

import json
import math
import os
import sys
import time
import zipfile

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
# A PROJECT's design goes FIRST on sys.path (run_project.py and server.py's
# render stage set VILLA_DESIGN_DIR); unset, the villa's, beside this file.
DESIGN_DIR = os.path.abspath(os.environ.get("VILLA_DESIGN_DIR") or HERE)
IS_PROJECT = os.path.normcase(DESIGN_DIR) != os.path.normcase(HERE)
if IS_PROJECT and not os.path.isfile(os.path.join(DESIGN_DIR, "villa_design.py")):
    # the import below would silently fall through to the villa's design
    raise RuntimeError(f"VILLA_DESIGN_DIR {DESIGN_DIR} has no villa_design.py")
sys.path.insert(0, HERE)
if IS_PROJECT:
    sys.path.insert(0, DESIGN_DIR)
import villa_design as V  # noqa: E402  (constants only; no shapely at import)

if os.path.normcase(os.path.dirname(os.path.abspath(V.__file__))) != os.path.normcase(DESIGN_DIR):
    raise RuntimeError(f"imported {V.__file__}, not the design in {DESIGN_DIR}")

DESKTOP = r"C:\Users\lsire\OneDrive\Desktop"
DESKTOP_VILLA = os.path.join(DESKTOP, "Villa")
# the downloaded assets (ambientCG sets, HDRIs) stay where they were fetched
ASSETS = os.environ.get("VILLA_ASSETS") or os.path.join(DESKTOP_VILLA, "render")
# The deliverables. A PROJECT: VILLA_OUT, as every builder (villa_geom.out_dir);
# unset, Desktop\<OUT_NAME> -- without one Desktop\<Folder>, as run_project.py
# -- never the villa's Desktop\Villa. The VILLA: Desktop\Villa, as the
# pre-projects code always had it, whatever VILLA_OUT says -- unless
# VILLA_RENDER_FOLLOWS_OUT=1 opts in to VILLA_OUT (a villa behaviour change
# awaiting the user's approval: server.py hands VILLA_OUT to every stage).
RENDER_FOLLOWS_OUT = os.environ.get("VILLA_RENDER_FOLLOWS_OUT") == "1"
if IS_PROJECT:
    BASE = os.environ.get("VILLA_OUT") or os.path.join(
        DESKTOP, getattr(V, "OUT_NAME", None) or os.path.basename(DESIGN_DIR).capitalize())
    if os.path.normcase(os.path.abspath(BASE)) == os.path.normcase(DESKTOP_VILLA):
        raise RuntimeError(f"the project {os.path.basename(DESIGN_DIR)} would render into the "
                           f"villa's deliverables ({DESKTOP_VILLA}); set VILLA_OUT")
elif RENDER_FOLLOWS_OUT:
    BASE = os.environ.get("VILLA_OUT") or DESKTOP_VILLA
else:
    BASE = DESKTOP_VILLA
RENDER = os.path.join(BASE, "render")
MATS = os.path.join(ASSETS, "materials")
TEX = os.path.join(MATS, "_tex")
TEX_CACHE = os.path.join(RENDER, "materials", "_tex")   # == TEX for the villa
HDRI = os.path.join(ASSETS, "hdri")
OUT = os.path.join(RENDER, "out")
TM = os.path.join(RENDER, "twinmotion")

MM = 0.001

# the design's own render hooks (the villa has none)
DESIGN_MATERIALS = dict(getattr(V, "MATERIALS", None) or {})
DESIGN_VIEWS = dict(getattr(V, "RENDER_VIEWS", None) or {})
VILLA_VIEWS = ["aerial_sw", "garden", "street", "aerial_ne", "plan"]
# The villa's annex room lights hang at the FF ceiling (+8.05 m), a bug in
# the original rule. The per-storey fix changes the villa's renders, so it
# is OFF for a design without render hooks until the user approves it
# (VILLA_ANNEX_LIGHT_FIX=1 opts in; re-baseline the villa renders then).
ANNEX_LIGHT_FIX = os.environ.get("VILLA_ANNEX_LIGHT_FIX") == "1"


# ------------------------------------------------------------------ args
def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = {"samples": 256, "res": (2400, 1500),
         "views": list(DESIGN_VIEWS) or list(VILLA_VIEWS),
         "hdri": "goegap", "sun_az": 225.0, "render": True}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--samples":
            o["samples"] = int(argv[i + 1]); i += 1
        elif k == "--res":
            w, h = argv[i + 1].lower().split("x"); o["res"] = (int(w), int(h)); i += 1
        elif k == "--views":
            o["views"] = argv[i + 1].split(","); i += 1
        elif k == "--hdri":
            o["hdri"] = argv[i + 1]; i += 1
            o["hdri_given"] = True
        elif k == "--sun-az":
            o["sun_az"] = float(argv[i + 1]); i += 1
        elif k == "--no-render":
            o["render"] = False
        i += 1
    return o


# ------------------------------------------------------------------ scene
def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights, bpy.data.images):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)


def import_groups():
    """One glb per material group -> {group: [objects]}, transforms baked,
    in metres."""
    groups = {}
    files = sorted(f for f in os.listdir(RENDER)
                   if f.startswith("villa_") and f.endswith(".glb"))
    for f in files:
        key = f[len("villa_"):-len(".glb")]
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(RENDER, f))
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == "MESH"]
        # A group exported with a Location imports as ONE mesh object, no
        # parent: the displacement (the pool deck 700 mm south) was already in
        # the file -- villa_gltf.main now refuses to export a group whose
        # top-level Location is not the identity. The update here is cheap
        # insurance before the matrices are baked; the stale value that
        # actually reproduced is bound_box (see below), not matrix_world.
        bpy.context.view_layer.update()
        world = {o: o.matrix_world.copy() for o in meshes}
        for o in meshes:
            o.data.transform(world[o])
            o.parent = None
            o.matrix_world = Matrix.Identity(4)
            o.name = f"{key}"
        for o in new:
            if o.type != "MESH":
                bpy.data.objects.remove(o, do_unlink=True)
        groups[key] = meshes

    # bound_box is cached until the depsgraph re-evaluates. Without this the
    # LAST group imported (water) reported its pre-bake box -- rotated 90 deg
    # -- and the size check below read a building that did not exist.
    bpy.context.view_layer.update()
    # glTF is metres by spec; if an exporter ignored that, the plot is 24 km
    lo, hi = bbox([o for obs in groups.values() for o in obs])
    if hi.x - lo.x > 1000:
        for obs in groups.values():
            for o in obs:
                o.data.transform(Matrix.Scale(MM, 4))
    for obs in groups.values():
        for o in obs:
            try:
                o.data.shade_flat()
            except Exception:
                for p in o.data.polygons:
                    p.use_smooth = False
    return groups


def bbox(objs):
    lo = Vector((1e18, 1e18, 1e18))
    hi = Vector((-1e18, -1e18, -1e18))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def world_uvs(obj, size=(1.0, 1.0)):
    """Box-projected UVs, V running up walls so boards and stone courses run
    horizontal. One UV tile = the texture's real size in metres, BAKED into
    the mesh: Twinmotion's glTF import does not document KHR_texture_transform,
    so a Mapping-node scale would be silently dropped on the way there."""
    sx, sy = size
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            co = loop.vert.co
            if ax == 0:
                u, v = co.y, co.z
            elif ax == 1:
                u, v = co.x, co.z
            else:
                u, v = co.x, co.y
            loop[uv].uv = (u / sx, v / sy)
    bm.to_mesh(me)
    bm.free()


# ------------------------------------------------------------------ materials
def extract(asset):
    """An ambientCG set's maps. Unpacked beside the downloads (TEX) when it
    already is; otherwise unpacked into this run's TEX_CACHE (VILLA_OUT --
    the same folder as TEX for the villa), never beside the downloads."""
    d = os.path.join(TEX, asset)
    if not os.path.isdir(d):
        d = os.path.join(TEX_CACHE, asset)
    if not os.path.isdir(d):
        z = [f for f in os.listdir(MATS) if f.startswith(asset) and f.endswith(".zip")][0]
        with zipfile.ZipFile(os.path.join(MATS, z)) as zf:
            for n in zf.namelist():
                if n.lower().endswith(".jpg"):
                    zf.extract(n, d)
    maps = {}
    for f in os.listdir(d):
        for k in ("Color", "Roughness", "NormalGL", "Displacement", "AmbientOcclusion"):
            if f.endswith(f"_{k}.jpg"):
                maps[k] = os.path.join(d, f)
    return maps


def _nodes(mat):
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf, out


def _set(bsdf, name, value):
    for n in (name, {"Transmission": "Transmission Weight",
                     "Transmission Weight": "Transmission"}.get(name, name)):
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return


def pbr(name, asset, size_m, tint=None, rough_mul=1.0, bump=0.0, detail=1.0,
        joints=None, rfit=None, normal=1.0):
    """ambientCG set at its declared physical size. The size lives in the UVs
    (see world_uvs); it is recorded on the material so the two cannot part.

    Options the design recipes use (the defaults add no node, so the
    villa's materials are unchanged):
      detail < 1   pulls the texture toward its own average colour (a pale
                   honed stone from a veined one);
      joints       (width m, height m, mortar m, darken) -- a slab/paver grid
                   laid over the texture, in metres, darkened and bumped;
      rfit         (gain, offset, lo, hi) from rough_fit: the roughness is
                   the design's, the set's map only modulating it gently
                   (clamp(gain * map + offset, lo, hi)); rough_mul is then
                   not used. No map: the design's value, flat;
      normal < 1   the normal map's strength."""
    maps = extract(asset)
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = list(size_m)
    nt, bsdf, _ = _nodes(mat)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")            # identity; kept for tweaking
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])

    def tex(key, colour):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(maps[key], check_existing=True)
        if not colour:
            t.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
        return t

    col = tex("Color", True)
    col_out = col.outputs["Color"]
    if detail < 1.0:
        avg = nt.nodes.new("ShaderNodeRGB")
        avg.outputs[0].default_value = (*tex_average(maps["Color"]), 1.0)
        flat = nt.nodes.new("ShaderNodeMixRGB")
        flat.inputs["Fac"].default_value = detail
        nt.links.new(avg.outputs[0], flat.inputs["Color1"])
        nt.links.new(col_out, flat.inputs["Color2"])
        col_out = flat.outputs["Color"]
    joint_fac = None
    if joints:
        jw, jh, mortar, darken = joints
        metres = nt.nodes.new("ShaderNodeMapping")
        metres.inputs["Scale"].default_value = (size_m[0], size_m[1], 1.0)
        nt.links.new(tc.outputs["UV"], metres.inputs["Vector"])
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = 0.5
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Brick Width"].default_value = jw
        br.inputs["Row Height"].default_value = jh
        br.inputs["Mortar Size"].default_value = mortar
        br.inputs["Mortar Smooth"].default_value = 0.3
        nt.links.new(metres.outputs["Vector"], br.inputs["Vector"])
        joint_fac = br.outputs["Fac"]
        dark = nt.nodes.new("ShaderNodeMixRGB")
        dark.blend_type = "MULTIPLY"
        nt.links.new(joint_fac, dark.inputs["Fac"])
        nt.links.new(col_out, dark.inputs["Color1"])
        dark.inputs["Color2"].default_value = (darken, darken, darken, 1.0)
        col_out = dark.outputs["Color"]
    if tint:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs["Fac"].default_value = 1.0
        mix.inputs["Color2"].default_value = (*tint, 1.0)
        nt.links.new(col_out, mix.inputs["Color1"])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        nt.links.new(col_out, bsdf.inputs["Base Color"])
    if rfit is not None:
        gain, offset, lo, hi = (float(v) for v in rfit)
        mat["roughness_fit"] = [round(gain, 4), round(offset, 4), round(lo, 4), round(hi, 4)]
        if "Roughness" in maps and gain > 0.0:
            r = tex("Roughness", False)
            m = nt.nodes.new("ShaderNodeMath")
            m.operation = "MULTIPLY_ADD"
            nt.links.new(r.outputs["Color"], m.inputs[0])
            m.inputs[1].default_value = gain
            m.inputs[2].default_value = offset
            c = nt.nodes.new("ShaderNodeClamp")
            c.inputs["Min"].default_value = lo
            c.inputs["Max"].default_value = hi
            nt.links.new(m.outputs["Value"], c.inputs["Value"])
            nt.links.new(c.outputs["Result"], bsdf.inputs["Roughness"])
        else:
            bsdf.inputs["Roughness"].default_value = max(lo, min(hi, offset))
    elif "Roughness" in maps:
        r = tex("Roughness", False)
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = "MULTIPLY"
        m.inputs[1].default_value = rough_mul
        nt.links.new(r.outputs["Color"], m.inputs[0])
        nt.links.new(m.outputs["Value"], bsdf.inputs["Roughness"])
    normal_in = None
    if "NormalGL" in maps:
        n = tex("NormalGL", False)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        if normal != 1.0:
            nm.inputs["Strength"].default_value = normal
        nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        normal_in = nm.outputs["Normal"]
    # A Bump node between the normal map and the shader made Blender's glTF
    # exporter write the DISPLACEMENT image as the material's normalTexture
    # (7 of 8 materials in the Twinmotion package; found by the Unreal
    # import). So height bump is used only where there is no normal map: the
    # render loses a little relief, and every exported normal map is right.
    if bump > 0 and "Displacement" in maps and normal_in is None:
        d = tex("Displacement", False)
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = 0.01
        nt.links.new(d.outputs["Color"], b.inputs["Height"])
        if normal_in is not None:
            nt.links.new(normal_in, b.inputs["Normal"])
        normal_in = b.outputs["Normal"]
    if joint_fac is not None:
        # the joints are recessed: a bump from the grid, fed the texture's
        # own normal (a procedural bump, not an image, so the exporter is
        # not confused about which map is the normal map)
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(joint_fac, inv.inputs[1])
        jb = nt.nodes.new("ShaderNodeBump")
        jb.inputs["Strength"].default_value = 0.6
        jb.inputs["Distance"].default_value = 0.004
        nt.links.new(inv.outputs["Value"], jb.inputs["Height"])
        if normal_in is not None:
            nt.links.new(normal_in, jb.inputs["Normal"])
        normal_in = jb.outputs["Normal"]
    if normal_in is not None:
        nt.links.new(normal_in, bsdf.inputs["Normal"])
    return mat


def plain(name, rgb, rough, metal=0.0):
    mat = bpy.data.materials.new(name)
    nt, bsdf, _ = _nodes(mat)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def glass():
    """Clear glass that does not block sunlight from the interior: shadow rays
    see a transparent surface, camera rays see real refraction."""
    mat = bpy.data.materials.new("glass")
    nt, bsdf, out = _nodes(mat)
    bsdf.inputs["Base Color"].default_value = (0.90, 0.95, 0.96, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["IOR"].default_value = 1.5
    _set(bsdf, "Transmission Weight", 1.0)
    lp = nt.nodes.new("ShaderNodeLightPath")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def water(name="water", absorb=(0.35, 0.80, 0.82), density=0.6, shadow_clear=False):
    """Pool water: refractive, rippled, absorbing with depth. shadow_clear:
    shadow rays pass the surface (as glass() does) so the sun reaches the
    tank floor -- tinted by the water on the way -- instead of leaving it to
    caustic paths Cycles barely finds (a lined pool then reads its lining's
    colour, not olive murk)."""
    mat = bpy.data.materials.new(name)
    nt, bsdf, out = _nodes(mat)
    if shadow_clear:
        lp = nt.nodes.new("ShaderNodeLightPath")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs["Fac"])
        nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
        nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (0.80, 0.95, 0.95, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.333
    _set(bsdf, "Transmission Weight", 1.0)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.5
    noise.inputs["Detail"].default_value = 6.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (*absorb, 1.0)
    vol.inputs["Density"].default_value = density
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return mat


def shrub_material():
    mat = bpy.data.materials.new("shrub")
    nt, bsdf, _ = _nodes(mat)
    info = nt.nodes.new("ShaderNodeObjectInfo")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.04, 0.09, 0.025, 1.0)
    ramp.color_ramp.elements[1].color = (0.13, 0.19, 0.05, 1.0)
    nt.links.new(info.outputs["Random"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 18.0
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.6
    nt.links.new(vor.outputs["Distance"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def materials():
    M = {}
    # Concrete034's albedo is plaster-white; exposed in-situ concrete is a
    # mid grey, and anything lighter reads as render in the desert sun.
    M["concrete"] = pbr("board-marked concrete", "Concrete034", (1.10, 0.55),
                        tint=(0.66, 0.64, 0.61), bump=0.3)
    # Travertine001's banding reads as timber grain in raking desert light; a
    # cool, pale tint pulls it back toward honed stone.
    M["travertine"] = pbr("travertine, honed", "Travertine001", (1.20, 1.20),
                          tint=(1.0, 0.97, 0.93), bump=0.2)
    M["travertine_flamed"] = pbr("travertine, flamed", "Travertine001",
                                 (1.20, 1.20), tint=(1.0, 0.97, 0.93),
                                 rough_mul=1.25, bump=0.5)
    M["oak"] = pbr("fumed oak", "WoodFloor040", (1.90, 1.90),
                   tint=(0.72, 0.62, 0.52))
    M["basalt"] = pbr("basalt setts", "PavingStones150", (0.90, 0.90), bump=0.5)
    M["gravel"] = pbr("gravel mulch", "Gravel023", (1.50, 1.50), bump=0.8)
    M["grass"] = pbr("lawn", "Grass001", (1.40, 1.40), bump=0.6)
    M["sand"] = pbr("desert ground", "Ground054", (3.50, 3.50), bump=0.4)
    M["bronze"] = plain("bronze anodised aluminium", (0.40, 0.27, 0.16), 0.38, 1.0)
    M["glass"] = glass()
    M["water"] = water()
    M["shrub"] = shrub_material()
    return M


ASSIGN = {
    "walls": "concrete", "slabs": "concrete", "roof": "concrete",
    "fins": "bronze", "frames": "bronze", "pool": "travertine",
    "base": "travertine",
    "boundary": "travertine", "paving": "travertine_flamed",
    "drive": "basalt", "deck": "oak", "gravel": "gravel", "lawn": "grass",
    "planting": "gravel", "terrain": "sand", "glass": "glass",
    "door": "oak", "water": "water",
    "guards": "glass",          # glass balustrades (villa_design.guards)
    "grate": "bronze",          # the walkable grate over the balance basin
    "stair": "travertine",      # the house stair, solid (villa_design.stair_parts)
    "rails": "bronze",          # every handrail (villa_design.rail_parts)
    "stone": "stone_dark",      # a design's stone cladding skin (massing 'stone')
}


# ------------------------------------------------------------------ design kinds
# A design's MATERIALS name a KIND per group; each kind is a recipe here, and
# the design's colour sets its average albedo (a textured recipe is tinted by
# colour / the texture's own average). "texture" names the ambientCG set a
# recipe is built on (None: procedural) -- the Twinmotion and Unreal packages
# read it from twinmotion\materials.json.
KIND_RECIPES = {
    "render_white": {"texture": None, "about": "white render, fine sand-float texture"},
    "concrete": {"texture": "Concrete034", "about": "in-situ concrete"},
    "stone_dark": {"texture": None, "about": "dark grey dry-stacked ledgestone"},
    "timber": {"texture": "WoodFloor040", "about": "timber louvres / soffit boards"},
    "timber_dark": {"texture": "WoodFloor040", "about": "dark stained timber"},
    "timber_deck": {"texture": "WoodFloor040", "about": "composite timber decking"},
    "metal_black": {"texture": None, "about": "black powder-coated aluminium"},
    "limestone": {"texture": "Travertine001", "about": "pale honed limestone slabs"},
    "interlock": {"texture": None, "about": "interlocking concrete pavers"},
    "grass": {"texture": "Grass001", "about": "irrigated lawn"},
    "hedge": {"texture": None, "about": "clipped hedge (leaf clumps scattered on it)"},
    "gravel": {"texture": "Gravel023", "about": "gravel"},
    "soil": {"texture": "Ground054", "about": "soil / sand"},
    "water": {"texture": None, "about": "pool water over a blue glass mosaic lining"},
    "glass": {"texture": None, "about": "clear glazing"},
    "travertine": {"texture": "Travertine001", "about": "veined travertine"},
    "mosaic": {"texture": "Tiles107", "about": "glass mosaic, 50 mm"},
}
# the physical size of each set (materials.json declares them; these are the
# fallbacks when it cannot be read)
TEX_SIZE = {"Travertine001": 1.20, "Concrete034": (1.10, 0.55), "WoodFloor040": 1.90,
            "PavingStones150": 0.90, "Gravel023": 1.50, "Grass001": 1.40,
            "Tiles107": 1.00, "Ground054": 3.50}
DEFAULT_KIND_COLOR = {"stone_dark": (0.20, 0.20, 0.21)}
MOSAIC_TILE_M = 0.20        # one Tiles107 repeat (4 x 4 tiles) = 50 mm mosaic
_AVG = {}


def _srgb_to_linear(a):
    import numpy as np
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def tex_average(path, colour=True):
    """The average of an image (linear for a colour map), cached -- what a
    tint divides by so a textured surface averages the design's colour."""
    key = (path, colour)
    if key not in _AVG:
        import numpy as np
        img = bpy.data.images.load(path, check_existing=True)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        rgb = px.reshape(-1, 4)[::7, :3]                   # a sample is plenty
        if colour:
            rgb = _srgb_to_linear(rgb)
        _AVG[key] = tuple(float(v) for v in rgb.mean(axis=0))
    return _AVG[key]


def tex_size(asset):
    try:
        with open(os.path.join(MATS, "materials.json"), encoding="utf-8") as fh:
            table = json.load(fh)
        for e in table:
            if e.get("assetId") == asset:
                w, h = e["dimension_cm"]
                return (w / 100.0, h / 100.0)
    except Exception:
        pass
    s = TEX_SIZE.get(asset, 1.0)
    return tuple(s) if isinstance(s, tuple) else (s, s)


_HI = {}


def tex_high(path, q=99.0):
    """The q-th percentile of a colour map, linear, per channel, cached: how
    far above its average the brightest texels of the set go (fit_tint)."""
    key = (path, q)
    if key not in _HI:
        import numpy as np
        img = bpy.data.images.load(path, check_existing=True)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        rgb = _srgb_to_linear(px.reshape(-1, 4)[::7, :3])
        _HI[key] = tuple(float(v) for v in np.percentile(rgb, q, axis=0))
    return _HI[key]


# A tint up to TINT_MAX takes a texture set as it is. A set far darker than
# the design's colour (Grass001 under a lawn needs x5-x10) is instead pulled
# toward its own average colour -- pbr's detail, which keeps the average --
# until its brightest texels (the 99th percentile) stay under ALBEDO_HI, and
# then tinted in full, up to TINT_FIT_MAX. Only beyond that is the design's
# colour missed, and materials.json says so ('tint_clamped').
TINT_MAX = 4.0
TINT_FIT_MAX = 16.0
ALBEDO_HI = 0.9
DETAIL_MIN = 0.25           # never flatter than this: the texture still reads
HI_RATIO_DEFAULT = 2.5      # 99th percentile / mean of a set not measured
KIND_DETAIL = {"limestone": 0.22, "travertine": 0.8}   # a recipe's own detail


def fit_tint(color, avg, hi=None, detail=1.0):
    """(tint, detail, clamped) that bring a texture set whose linear average
    colour is `avg` (99th percentile `hi`) to the design's `color` on
    average, starting from the recipe's `detail`. Pure: unreal/build_scene.py
    has the same function, and the tests hold them equal."""
    t = [c / max(a, 1e-3) for c, a in zip(color, avg)]
    if max(t) <= TINT_MAX:
        return tuple(t), detail, False
    hi = hi or [a * HI_RATIO_DEFAULT for a in avg]
    d = detail
    for c, a, h in zip(color, avg, hi):
        r = h / max(a, 1e-3)
        if c > 0 and r > 1.0:
            d = min(d, (ALBEDO_HI / c - 1.0) / (r - 1.0))
    d = max(DETAIL_MIN, min(detail, d))
    return tuple(min(TINT_FIT_MAX, v) for v in t), d, max(t) > TINT_FIT_MAX


def _fit_to(asset, color, detail=1.0):
    maps = extract(asset)
    return fit_tint(color, tex_average(maps["Color"]), tex_high(maps["Color"]), detail)


# A design's roughness (MATERIALS[group].roughness) IS the surface's: a set's
# roughness map only modulates it, gently, around that value. Scaling the map
# to the design's value does not work for every set: Travertine001 is shot
# polished (its map averages 0.026), so x29 to reach the paving's 0.75 left a
# quarter of every slab under 0.35 and most of the rest clipped at 1.0 --
# blotchy, wet-looking stone -- and Unreal, taking the map as it was, rendered
# the paving and coping as a mirror. rough_fit keeps the map's own spread when
# it is small (timber, concrete), caps it at ROUGH_DEV (one standard deviation
# of the map) when it is not, and never strays more than ROUGH_BAND from the
# design's value. Pure: unreal/build_scene.py has the same function, and the
# tests hold them equal.
ROUGH_DEV = 0.05
ROUGH_BAND = 0.12
ROUGH_MIN = 0.02


def rough_fit(rough, mean=None, std=None):
    """(gain, offset, lo, hi): roughness = clamp(gain * map + offset, lo, hi)
    averages the design's `rough` over a roughness map of mean `mean` and
    standard deviation `std` (None: no map -- the design's value, flat)."""
    rough = max(ROUGH_MIN, min(1.0, float(rough)))
    lo, hi = max(ROUGH_MIN, rough - ROUGH_BAND), min(1.0, rough + ROUGH_BAND)
    if mean is None or std is None or mean <= 1e-4:
        return 0.0, rough, lo, hi
    gain = rough / mean
    if std > 1e-6:
        gain = min(gain, ROUGH_DEV / std)
    return gain, rough - gain * mean, lo, hi


_RSTATS = {}


def tex_rough_stats(path):
    """(mean, standard deviation) of a roughness map (its first channel, as
    Unreal reads it), sampled as tex_average samples, cached."""
    if path not in _RSTATS:
        import numpy as np
        img = bpy.data.images.load(path, check_existing=True)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        v = px.reshape(-1, 4)[::7, 0]
        _RSTATS[path] = (float(v.mean()), float(v.std()))
    return _RSTATS[path]


def _rough_fit_to(asset, rough):
    """rough_fit for an ambientCG set: its map's statistics, if it has one."""
    maps = extract(asset)
    if "Roughness" not in maps:
        return rough_fit(rough)
    return rough_fit(rough, *tex_rough_stats(maps["Roughness"]))


def _uvm(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["UV"]


def _ramp(nt, fac, c0, c1):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (*c0, 1.0)
    r.color_ramp.elements[1].color = (*c1, 1.0)
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def _scaled(c, k):
    return tuple(max(0.0, min(1.0, v * k)) for v in c)


def render_material(name, color, rough):
    """White render: a sand-float grain (fine bump) and a faint trowel cloud
    (large, +/-3 % albedo). UVs in metres."""
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = [1.0, 1.0]
    nt, bsdf, _ = _nodes(mat)
    uv = _uvm(nt)
    cloud = nt.nodes.new("ShaderNodeTexNoise")
    cloud.inputs["Scale"].default_value = 0.8
    cloud.inputs["Detail"].default_value = 3.0
    nt.links.new(uv, cloud.inputs["Vector"])
    nt.links.new(_ramp(nt, cloud.outputs["Fac"], _scaled(color, 0.955), _scaled(color, 1.02)),
                 bsdf.inputs["Base Color"])
    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.inputs["Scale"].default_value = 140.0
    grain.inputs["Detail"].default_value = 4.0
    nt.links.new(uv, grain.inputs["Vector"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.05
    b.inputs["Distance"].default_value = 0.002
    nt.links.new(grain.outputs["Fac"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def stone_material(name, color, rough):
    """Dark dry-stacked ledgestone: courses 50-110 mm high, 250-700 long, no
    mortar (the joints are shadow), each stone its own shade, a rough split
    face. UVs in metres, V up the wall, so the courses run level."""
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = [1.0, 1.0]
    nt, bsdf, _ = _nodes(mat)
    uv = _uvm(nt)
    # courses that wander a little, as split stone does: the UVs pushed by a
    # slow noise before the course pattern reads them
    wob = nt.nodes.new("ShaderNodeTexNoise")
    wob.inputs["Scale"].default_value = 2.2
    nt.links.new(uv, wob.inputs["Vector"])
    cen = nt.nodes.new("ShaderNodeVectorMath")
    cen.operation = "SUBTRACT"
    cen.inputs[1].default_value = (0.5, 0.5, 0.5)
    nt.links.new(wob.outputs["Color"], cen.inputs[0])
    amp = nt.nodes.new("ShaderNodeVectorMath")
    amp.operation = "MULTIPLY"
    amp.inputs[1].default_value = (0.06, 0.012, 0.0)
    nt.links.new(cen.outputs["Vector"], amp.inputs[0])
    push = nt.nodes.new("ShaderNodeVectorMath")
    push.operation = "ADD"
    nt.links.new(uv, push.inputs[0])
    nt.links.new(amp.outputs["Vector"], push.inputs[1])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.41
    br.offset_frequency = 1
    br.squash = 0.45
    br.squash_frequency = 3
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.52
    br.inputs["Row Height"].default_value = 0.068
    br.inputs["Mortar Size"].default_value = 0.0035
    br.inputs["Mortar Smooth"].default_value = 0.2
    br.inputs["Bias"].default_value = -0.1
    br.inputs["Color1"].default_value = (*_scaled(color, 1.9), 1.0)
    br.inputs["Color2"].default_value = (*_scaled(color, 0.45), 1.0)
    br.inputs["Mortar"].default_value = (*_scaled(color, 0.05), 1.0)
    nt.links.new(push.outputs["Vector"], br.inputs["Vector"])
    # the split face: coarse and fine noise, also breaking up each stone's tone
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 9.0
    n1.inputs["Detail"].default_value = 8.0
    n1.inputs["Roughness"].default_value = 0.65
    nt.links.new(uv, n1.inputs["Vector"])
    tone = nt.nodes.new("ShaderNodeMixRGB")
    tone.blend_type = "OVERLAY"
    tone.inputs["Fac"].default_value = 0.55
    nt.links.new(br.outputs["Color"], tone.inputs["Color1"])
    nt.links.new(n1.outputs["Color"], tone.inputs["Color2"])
    nt.links.new(tone.outputs["Color"], bsdf.inputs["Base Color"])
    h = nt.nodes.new("ShaderNodeMath")
    h.operation = "MULTIPLY_ADD"
    nt.links.new(n1.outputs["Fac"], h.inputs[0])
    h.inputs[1].default_value = 0.35
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], h.inputs[2])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.9
    b.inputs["Distance"].default_value = 0.012
    nt.links.new(h.outputs["Value"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def pavers_material(name, color, rough):
    """Interlocking concrete pavers 200 x 100, stretcher bond, 4 mm joints,
    each paver its own shade. UVs in metres."""
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = [1.0, 1.0]
    nt, bsdf, _ = _nodes(mat)
    uv = _uvm(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.20
    br.inputs["Row Height"].default_value = 0.10
    br.inputs["Mortar Size"].default_value = 0.004
    br.inputs["Mortar Smooth"].default_value = 0.3
    br.inputs["Color1"].default_value = (*_scaled(color, 1.10), 1.0)
    br.inputs["Color2"].default_value = (*_scaled(color, 0.88), 1.0)
    br.inputs["Mortar"].default_value = (*_scaled(color, 0.55), 1.0)
    nt.links.new(uv, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 60.0
    nt.links.new(uv, n.inputs["Vector"])
    h = nt.nodes.new("ShaderNodeMath")
    h.operation = "MULTIPLY_ADD"
    nt.links.new(n.outputs["Fac"], h.inputs[0])
    h.inputs[1].default_value = 0.15
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], h.inputs[2])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.5
    b.inputs["Distance"].default_value = 0.004
    nt.links.new(h.outputs["Value"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def hedge_material(name, color, rough):
    """Leaves: two greens mixed by a noise cloud and, on a scattered leaf
    clump, by its own random value; a leafy bump; a little translucency (the
    low sun through a hedge)."""
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = [1.0, 1.0]
    nt, bsdf, out = _nodes(mat)
    info = nt.nodes.new("ShaderNodeObjectInfo")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    cloud = nt.nodes.new("ShaderNodeTexNoise")
    cloud.inputs["Scale"].default_value = 1.6
    nt.links.new(geo.outputs["Position"], cloud.inputs["Vector"])
    f = nt.nodes.new("ShaderNodeMath")
    f.operation = "MULTIPLY_ADD"
    nt.links.new(info.outputs["Random"], f.inputs[0])
    f.inputs[1].default_value = 0.5
    nt.links.new(cloud.outputs["Fac"], f.inputs[2])
    col = _ramp(nt, f.outputs["Value"], _scaled(color, 0.45), _scaled(color, 1.05))
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = min(rough, 0.75)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 38.0
    nt.links.new(geo.outputs["Position"], vor.inputs["Vector"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.8
    nt.links.new(vor.outputs["Distance"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (*_scaled(color, 0.9), 1.0)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.15
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    nt.links.new(tl.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def kind_material(kind, color=None, rough=None, name=None):
    """One material for a design MATERIALS kind, coloured to `color`
    (linear base colour) and `rough`. The recipe book is KIND_RECIPES."""
    color = tuple(float(c) for c in (color or DEFAULT_KIND_COLOR.get(kind, (0.8, 0.8, 0.8)))[:3])
    rough = 0.8 if rough is None else float(rough)
    name = name or kind.replace("_", " ")
    rec = KIND_RECIPES.get(kind, {})
    asset = rec.get("texture")
    if kind == "render_white":
        return render_material(name, color, rough)
    if kind == "stone_dark":
        return stone_material(name, color, rough)
    if kind == "interlock":
        return pavers_material(name, color, rough)
    if kind == "hedge":
        return hedge_material(name, color, rough)
    if kind == "metal_black":
        return plain(name, color, rough, 0.0)           # powder coat, not bare metal
    if kind == "glass":
        return glass()
    if kind == "water":
        # the blue is the mosaic's (mosaic_lining); the water only clears it
        # a little toward that blue with depth
        top = max(color) or 1.0
        absorb = tuple(0.55 + 0.45 * c / top for c in color)
        return water(name, absorb=absorb, density=0.5, shadow_clear=True)
    if not asset:
        return plain(name, color, rough)
    # the tint (and, for a set far darker than the colour, the detail) that
    # bring the set to the design's colour -- fit_tint
    tint, detail, clamped = _fit_to(asset, color, KIND_DETAIL.get(kind, 1.0))
    # the design's roughness, the set's map only modulating it (rough_fit)
    rfit = _rough_fit_to(asset, rough)
    if kind == "limestone":
        mat = pbr(name, asset, tex_size(asset), tint=tint, rfit=rfit, detail=detail,
                  joints=(0.90, 0.60, 0.003, 0.72))
    elif kind in ("timber", "timber_dark", "timber_deck"):
        mat = pbr(name, asset, tex_size(asset), tint=tint, rfit=rfit, detail=detail)
    elif kind == "travertine":
        mat = pbr(name, asset, tex_size(asset), tint=tint, rfit=rfit, detail=detail, bump=0.2)
    elif kind == "mosaic":
        mat = pbr(name, asset, (MOSAIC_TILE_M, MOSAIC_TILE_M), tint=tint, rfit=rfit,
                  detail=detail)
    else:                                       # concrete, grass, gravel, soil
        mat = pbr(name, asset, tex_size(asset), tint=tint, rfit=rfit, bump=0.4, detail=detail)
    mat["tint_fit"] = {"tint": [round(v, 4) for v in tint], "detail": round(detail, 4),
                       "clamped": clamped}
    return mat


def design_material(group, spec, cache):
    """A group's material from the design's MATERIALS entry -- one per
    distinct (kind, colour, roughness), shared by the groups that match."""
    kind = spec.get("kind", "")
    key = (kind, tuple(round(float(c), 4) for c in spec.get("color", ())[:3]),
           round(float(spec.get("roughness", 0.8)), 4))
    if key not in cache:
        cache[key] = kind_material(kind, spec.get("color"), spec.get("roughness"),
                                   name=kind.replace("_", " "))
        cache[key]["kind"] = kind
    return cache[key]


def settle_water(ob, gap=0.003):
    """The water body shares its floor and walls with the tank. Coincident
    faces let a camera ray refract out of the water through the floor and see
    the HDRI's ground under the plot (a sandy, rippled 'floor'). Draw every
    wall and floor vertex `gap` inside the tank; the surface stays where it is.
    Done after the import check, so the check still proves the export."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    moves = []
    for v in bm.verts:
        n = Vector((0.0, 0.0, 0.0))
        for f in v.link_faces:
            if f.normal.z < 0.99:              # not the water surface
                n += f.normal
        moves.append((v, Vector(tuple(-gap if c > 0.1 else gap if c < -0.1 else 0.0
                                      for c in n))))
    for v, d in moves:                         # every wall, floor and step face, inward
        v.co += d
    bm.to_mesh(me)
    bm.free()
    me.update()


def mosaic_lining(ob, lining, tile_m):
    """The pool tank below its coping: every face of the pool group lower
    than the group's top (the coping, flush with the deck) is lined with
    `lining`. The UVs are the coping's, so the lining scales its own."""
    me = ob.data
    top = max(v.co.z for v in me.vertices)
    me.materials.append(lining)
    slot = len(me.materials) - 1
    n = 0
    for p in me.polygons:
        if p.center.z < top - 0.005:
            p.material_index = slot
            n += 1
    # The object's UVs are in coping tiles; the lining's Mapping node (pbr's
    # identity one, the only Mapping in a set without joints) rescales them
    # to mosaic tiles. A Mapping scale does not survive the Twinmotion glTF
    # import -- there the pool gets the library's mosaic anyway.
    k = tile_m[0] / MOSAIC_TILE_M
    for nd in lining.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeMapping":
            nd.inputs["Scale"].default_value = (k, k, 1.0)
            break
    lining["uv_tile_m"] = list(tile_m)
    return n


# ------------------------------------------------------------------ planting
def _sock(node, name, value, kind):
    """Set the ENABLED input `name` of socket type `kind` ('VALUE', 'VECTOR',
    'INT'...). Random Value keeps a Min/Max pair per data type and the order
    of that list changed across Blender versions, so never index it."""
    for s in node.inputs:
        if s.name == name and s.type == kind and getattr(s, "enabled", True):
            s.default_value = value
            return
    raise KeyError(f"{node.bl_idname}: no enabled {kind} input '{name}'")


def _out(node, kind):
    for s in node.outputs:
        if s.type == kind and getattr(s, "enabled", True):
            return s
    raise KeyError(f"{node.bl_idname}: no enabled {kind} output")


def shrubs(obj, mat, density=2.2, radius=(0.22, 0.55), spacing=0.45, up_only=True,
           leaf=None):
    """Scatter low shrubs over the TOP faces of the planting beds -- or, with
    up_only=False, over every face but the undersides; with leaf=(w, h) the
    instance is a single leaf card of that size, turned every way, not a
    sphere (a clipped hedge: its sides as well as its top, so it does not
    read as a green box)."""
    ng = bpy.data.node_groups.new("shrub scatter", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, l = ng.nodes, ng.links
    gi = n.new("NodeGroupInput")
    go = n.new("NodeGroupOutput")
    nrm = n.new("GeometryNodeInputNormal")
    sep = n.new("ShaderNodeSeparateXYZ")
    cmp = n.new("FunctionNodeCompare")
    cmp.data_type = "FLOAT"
    cmp.operation = "GREATER_THAN"
    cmp.inputs[1].default_value = 0.9 if up_only else -0.5
    dist = n.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "POISSON"
    dist.inputs["Distance Min"].default_value = spacing
    dist.inputs["Density Max"].default_value = density
    if leaf is None:
        ico = n.new("GeometryNodeMeshIcoSphere")
        ico.inputs["Radius"].default_value = 1.0
        ico.inputs["Subdivisions"].default_value = 3
    else:
        ico = n.new("GeometryNodeMeshGrid")
        ico.inputs["Size X"].default_value = leaf[0]
        ico.inputs["Size Y"].default_value = leaf[1]
        ico.inputs["Vertices X"].default_value = 2
        ico.inputs["Vertices Y"].default_value = 2
    rs = n.new("FunctionNodeRandomValue")
    rs.data_type = "FLOAT"
    _sock(rs, "Min", radius[0], "VALUE")
    _sock(rs, "Max", radius[1], "VALUE")
    rr = n.new("FunctionNodeRandomValue")
    rr.data_type = "FLOAT_VECTOR"
    _sock(rr, "Min", (0.0, 0.0, 0.0), "VECTOR")
    _sock(rr, "Max", (0.0, 0.0, 6.283) if leaf is None else (6.283, 6.283, 6.283), "VECTOR")
    inst = n.new("GeometryNodeInstanceOnPoints")
    sm = n.new("GeometryNodeSetMaterial")
    sm.inputs["Material"].default_value = mat
    join = n.new("GeometryNodeJoinGeometry")
    l.new(nrm.outputs["Normal"], sep.inputs["Vector"])
    l.new(sep.outputs["Z"], cmp.inputs[0])
    l.new(gi.outputs[0], dist.inputs["Mesh"])
    l.new(cmp.outputs["Result"], dist.inputs["Selection"])
    l.new(dist.outputs["Points"], inst.inputs["Points"])
    l.new(ico.outputs["Mesh"], inst.inputs["Instance"])
    l.new(_out(rs, "VALUE"), inst.inputs["Scale"])
    l.new(_out(rr, "VECTOR"), inst.inputs["Rotation"])
    l.new(inst.outputs["Instances"], sm.inputs["Geometry"])
    l.new(gi.outputs[0], join.inputs["Geometry"])
    l.new(sm.outputs["Geometry"], join.inputs["Geometry"])
    l.new(join.outputs["Geometry"], go.inputs[0])
    mod = obj.modifiers.new("shrubs", "NODES")
    mod.node_group = ng


# ------------------------------------------------------------------ context
def _box_obj(name, x0, y0, z0, x1, y1, z1, mat):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def context_layout():
    """The neighbours' numbers, metres. The villa keeps the ones it has
    always rendered with; a design with render hooks (RENDER_VIEWS) gets
    them from its own plot: neighbours of the same plot size, their houses
    at the design's front and side setbacks (across the street mirrored, so
    their fronts face it too), as deep as this house and as high as its
    parapet."""
    W, D = V.PLOT_W * MM, V.PLOT_D * MM
    side = getattr(V, "SB_SIDE", 3000.0) * MM
    front = getattr(V, "SB_FRONT", 5000.0) * MM
    if not DESIGN_VIEWS:
        return {"W": W, "D": D, "side": 3.0, "near_y0": 11.0, "far_y0": 3.0,
                "depth": 13.0, "height": 8.4}
    parts = [getattr(V, k, None) for k in ("RF", "SLAB", "PARAPET")]
    top = sum(parts) * MM if None not in parts else None
    depth = round(min(0.45 * D, D - front - getattr(V, "SB_REAR", 3000.0) * MM), 2)
    return {"W": W, "D": D, "side": side, "near_y0": D - front - depth,
            "far_y0": front, "depth": depth, "height": top or 8.4}


# A design with render hooks gets a far-field ground: FAR_FIELD_M round the
# plot, so from the aerial the HDRI's own photographed ground (a bushveld
# slope for aarfontein, rocky hills for goegap) never shows under the sky --
# the villa keeps its 160 m slab. RENDER_CONTEXT = {"south": "golf"} (a design
# hook) lays a golf course behind the rear (south) boundary: GOLF_ROUGH_M of
# rough, the mown fairway, rough again out to GOLF_DEPTH_M.
FAR_FIELD_M = 4000.0
GOLF_ROUGH_M = 6.0
GOLF_FAIRWAY_M = 70.0
GOLF_DEPTH_M = 240.0
GOLF_STRIPE_M = 9.0
GOLF_SHADES = (0.60, 1.15, 0.90)   # x the design's lawn colour: rough, the two mowing stripes


def render_context():
    """The design's RENDER_CONTEXT hook ({'south': 'golf' | 'lawn'}), or {}."""
    rc = getattr(V, "RENDER_CONTEXT", None)
    return dict(rc) if isinstance(rc, dict) else {}


def golf_bands(W, side=160.0):
    """The golf course south of the plot as (name, x0, y0, x1, y1, shade)
    bands, metres; shade 0 is rough, 1 and 2 the fairway's two mowing
    directions. Pure geometry (unit-tested)."""
    x0, x1 = -side, W + side
    bands = [("rough near", x0, -GOLF_ROUGH_M, x1, 0.0, 0)]
    y, k = -GOLF_ROUGH_M, 0
    while y > -(GOLF_ROUGH_M + GOLF_FAIRWAY_M) + 1e-6:
        y1 = max(y - GOLF_STRIPE_M, -(GOLF_ROUGH_M + GOLF_FAIRWAY_M))
        bands.append((f"fairway {k}", x0, y1, x1, y, 1 + k % 2))
        y, k = y1, k + 1
    bands.append(("rough far", x0, -GOLF_DEPTH_M, x1, y, 0))
    return bands


def context(M, holes=()):
    """Ground, street and neighbours -- deliberately plain. Without them the
    plot is a model on a tabletop floating over the HDRI's photographed ground.
    Neighbours are massing only (Dubai defaults: 3 m setbacks, 2 storeys; a
    design's own setbacks when it has render hooks -- context_layout).
    holes: plan rectangles (m) cut out of the ground slab -- a pool sunk
    below it, which the slab would otherwise floor with sand."""
    L = context_layout()
    W, D = L["W"], L["D"]
    plaster = plain("neighbour plaster", (0.80, 0.78, 0.74), 0.9)
    asphalt = plain("asphalt", (0.07, 0.07, 0.075), 0.85)
    kerb = plain("pavement", (0.62, 0.60, 0.56), 0.8)
    reach = FAR_FIELD_M if DESIGN_VIEWS else 160
    ground = [(-reach, -reach, W + reach, D + reach)]
    for h in holes:
        ground = _rect_minus(ground, h)
    obs = [_box_obj("ctx ground" if len(ground) == 1 else f"ctx ground {k}",
                    a, b, -0.32, c, d, -0.005, M["sand"])
           for k, (a, b, c, d) in enumerate(ground)]
    obs += [
        _box_obj("ctx pavement N", -reach, D, -0.005, W + reach, D + 2.0, 0.15, kerb),
        _box_obj("ctx street N", -reach, D + 2.0, -0.02, W + reach, D + 14.0, 0.0, asphalt),
        _box_obj("ctx pavement far", -reach, D + 14.0, -0.005, W + reach, D + 16.0, 0.15, kerb),
    ]
    plots = [(-W, 0.0), (W, 0.0), (0.0, D + 16.0), (W, D + 16.0), (-W, D + 16.0)]
    if DESIGN_VIEWS:
        # a design's street is a row of plots, not five: three a side
        plots += [(k * W, oy) for k in (-3, -2, 2, 3) for oy in (0.0, D + 16.0)]
    south = render_context().get("south")
    if DESIGN_VIEWS and south in ("golf", "lawn"):
        lawn = DESIGN_MATERIALS.get("lawn", {})
        base = tuple(lawn.get("color", (0.36, 0.55, 0.24)))
        shades = {i: kind_material("grass", _scaled(base, k), 0.95 if i == 0 else 0.9,
                                   name=("golf rough", "golf fairway", "golf fairway b")[i])
                  for i, k in enumerate(GOLF_SHADES)}
        bands = (golf_bands(W, side=4 * W) if south == "golf"
                 else [("lawn", -4 * W, -GOLF_DEPTH_M, 5 * W, 0.0, 1)])
        for name, a, b, c, d, shade in bands:
            obs.append(_box_obj(f"ctx golf {name}", a, b, -0.02, c, d, 0.0, shades[shade]))
    s, dp = L["side"], L["depth"]
    for i, (ox, oy) in enumerate(plots):
        far = oy > D
        obs.append(_box_obj(f"ctx wall {i}", ox, oy, 0.0, ox + W, oy + 0.35, 2.4, plaster))
        obs.append(_box_obj(f"ctx wall {i}b", ox, oy + D - 0.35, 0.0, ox + W, oy + D, 2.4, plaster))
        hy0 = oy + (L["far_y0"] if far else L["near_y0"])
        obs.append(_box_obj(f"ctx house {i}", ox + s, hy0, 0.0, ox + W - s,
                            hy0 + dp, L["height"] - (i % 2) * 1.2, plaster))
    for ob in obs:
        if ob.data.materials and ob.data.materials[0].get("tile_m"):
            world_uvs(ob, tuple(ob.data.materials[0]["tile_m"]))
    return len(obs)


# ------------------------------------------------------------------ palms
def palm_materials():
    bark = bpy.data.materials.new("palm trunk")
    nt, bsdf, _ = _nodes(bark)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    ring = nt.nodes.new("ShaderNodeMath")
    ring.operation = "SINE"
    k = nt.nodes.new("ShaderNodeMath")
    k.operation = "MULTIPLY"
    k.inputs[1].default_value = 40.0                 # a leaf scar every ~150 mm
    nt.links.new(sep.outputs["Z"], k.inputs[0])
    nt.links.new(k.outputs["Value"], ring.inputs[0])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.7
    b.inputs["Distance"].default_value = 0.02
    nt.links.new(ring.outputs["Value"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Base Color"].default_value = (0.24, 0.19, 0.13, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9

    frond = bpy.data.materials.new("palm frond")
    nt, bsdf, out = _nodes(frond)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs["Vector"])
    # leaflets: diagonal stripes off the rib (u along the frond, v across)
    dv = nt.nodes.new("ShaderNodeMath")
    dv.operation = "SUBTRACT"
    dv.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs["Y"], dv.inputs[0])
    adv = nt.nodes.new("ShaderNodeMath")
    adv.operation = "ABSOLUTE"
    nt.links.new(dv.outputs["Value"], adv.inputs[0])
    t = nt.nodes.new("ShaderNodeMath")
    t.operation = "MULTIPLY_ADD"
    nt.links.new(sep.outputs["X"], t.inputs[0])
    t.inputs[1].default_value = 34.0
    a3 = nt.nodes.new("ShaderNodeMath")
    a3.operation = "MULTIPLY"
    a3.inputs[1].default_value = 5.0
    nt.links.new(adv.outputs["Value"], a3.inputs[0])
    nt.links.new(a3.outputs["Value"], t.inputs[2])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(t.outputs["Value"], fr.inputs[0])
    leaf = nt.nodes.new("ShaderNodeMath")
    leaf.operation = "LESS_THAN"
    leaf.inputs[1].default_value = 0.62                # leaflets cover ~60 %
    nt.links.new(fr.outputs["Value"], leaf.inputs[0])
    rib = nt.nodes.new("ShaderNodeMath")
    rib.operation = "LESS_THAN"
    rib.inputs[1].default_value = 0.04
    nt.links.new(adv.outputs["Value"], rib.inputs[0])
    solid = nt.nodes.new("ShaderNodeMath")
    solid.operation = "MAXIMUM"
    nt.links.new(leaf.outputs["Value"], solid.inputs[0])
    nt.links.new(rib.outputs["Value"], solid.inputs[1])
    info = nt.nodes.new("ShaderNodeObjectInfo")
    col = _ramp(nt, info.outputs["Random"], (0.05, 0.11, 0.025), (0.13, 0.20, 0.05))
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.55
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (0.20, 0.30, 0.06, 1.0)
    leafy = nt.nodes.new("ShaderNodeMixShader")
    leafy.inputs["Fac"].default_value = 0.25
    nt.links.new(bsdf.outputs["BSDF"], leafy.inputs[1])
    nt.links.new(tl.outputs["BSDF"], leafy.inputs[2])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(solid.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[1])
    nt.links.new(leafy.outputs["Shader"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return bark, frond


def palm(i, x, y, z0, crown, bark, frond):
    """A date palm: a tapering, slightly leaning ringed trunk and a crown of
    arching fronds, each a strip whose leaflets are cut by the material.
    Seeded by its index, so a re-render is the same garden."""
    import random
    rng = random.Random(1000 + i)
    h = 4.6 + 2.2 * rng.random()
    lean = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.24,
                          radius2=0.17, depth=h)
    for v in bm.verts:
        t = (v.co.z + h / 2) / h
        v.co.z += h / 2
        v.co.x += lean[0] * t * t
        v.co.y += lean[1] * t * t
    me = bpy.data.meshes.new(f"ctx palm {i} trunk")
    bm.to_mesh(me)
    bm.free()
    trunk = bpy.data.objects.new(f"ctx palm {i} trunk", me)
    trunk.location = (x, y, z0)
    me.materials.append(bark)
    bpy.context.scene.collection.objects.link(trunk)

    top = Vector((x + lean[0], y + lean[1], z0 + h))
    R = crown / 2.0
    verts, faces, uvs = [], [], []
    n_fronds = 16
    for k in range(n_fronds):
        az = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / n_fronds
        up = rng.uniform(0.25, 0.8)                # young fronds stand up
        droop = rng.uniform(0.8, 1.4)
        L = R * rng.uniform(1.0, 1.25)
        d = Vector((math.cos(az), math.sin(az), 0.0))
        across = Vector((-d.y, d.x, 0.0))
        base = len(verts)
        segs = 10
        for s in range(segs + 1):
            u = s / segs
            c = top + d * (L * u) + Vector((0, 0, L * (up * u - droop * u * u)))
            w = 0.30 * L * math.sin(math.pi * min(1.0, 0.15 + 0.95 * u)) ** 0.7 + 0.02
            fold = Vector((0, 0, 0.18 * w))        # leaflets rise off the rib: a V
            verts += [c - across * w + fold, c, c + across * w + fold]
            uvs += [(u, 0.0), (u, 0.5), (u, 1.0)]
        for s in range(segs):
            a = base + 3 * s
            faces += [(a, a + 3, a + 4, a + 1), (a + 1, a + 4, a + 5, a + 2)]
    me = bpy.data.meshes.new(f"ctx palm {i} crown")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[me.loops[li].vertex_index]
    me.materials.append(frond)
    ob = bpy.data.objects.new(f"ctx palm {i} crown", me)
    bpy.context.scene.collection.objects.link(ob)
    return 2


def palms():
    """V.SITE_TREES (x, y, crown mm) as palms, standing on the finished
    ground (V.ground_at when the design has it, else the garden level)."""
    trees = getattr(V, "SITE_TREES", None) or []
    if not trees:
        return 0
    bark, frond = palm_materials()
    ground = getattr(V, "ground_at", None)
    n = 0
    for i, t in enumerate(trees):
        x, y, crown = t[:3]
        z = ground(y) if callable(ground) else getattr(V, "GARDEN_Z", 0.0)
        n += palm(i, x * MM, y * MM, z * MM, crown * MM, bark, frond)
    return n


def gate_leaves(mat, slat=0.045, pitch=0.09):
    """A leaf of dark vertical slats in every gate V.gates() cuts from the
    street wall (the listing's street photograph) -- render dressing: the
    model has the opening, not the leaf."""
    if not callable(getattr(V, "gates", None)):
        return 0
    T = getattr(V, "BOUNDARY_T", 350.0)
    BH = getattr(V, "BOUNDARY_H", 2400.0)
    yc = (V.PLOT_D - T / 2) * MM
    bm = bmesh.new()
    n = 0

    def cube(x0, y0, z0, x1, y1, z1):
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
            v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
            v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)

    for _name, a, b, head in V.gates():
        x0, x1 = min(a, b) * MM + 0.02, max(a, b) * MM - 0.02
        z0, z1 = 0.04, (BH if head is None else min(head, BH)) * MM - 0.02
        cube(x0, yc - 0.03, z0, x1, yc + 0.03, z0 + 0.06)       # bottom rail
        cube(x0, yc - 0.03, z1 - 0.06, x1, yc + 0.03, z1)       # top rail
        k = int((x1 - x0 - slat) // pitch)
        off = (x1 - x0 - slat - k * pitch) / 2
        for i in range(k + 1):
            sx = x0 + off + i * pitch
            cube(sx, yc - slat / 2, z0, sx + slat, yc + slat / 2, z1)
        n += 1
    me = bpy.data.meshes.new("ctx gates")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("ctx gates", me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    world_uvs(ob, tuple(mat.get("tile_m", (1.0, 1.0))))
    return n


# ------------------------------------------------------------------ interiors
# Floor finishes for a design with render hooks (MATERIALS): the photographs'
# travertine downstairs and oak in the bedrooms, 10 mm on the slab, room by
# room (nested rooms and the voids cut out). Render dressing like the lights:
# 'ctx', so not in the Twinmotion package.
FLOOR_OAK_ROLES = ("bedroom", "master_bedroom", "dressing", "family_lounge")
FLOOR_CONCRETE_ROLES = ("garage", "plant", "store", "laundry")


def _rect_minus(rects, cut):
    """Axis-aligned rectangles less one rectangle, as rectangles."""
    cx0, cy0, cx1, cy1 = cut
    out = []
    for x0, y0, x1, y1 in rects:
        if cx0 >= x1 or cx1 <= x0 or cy0 >= y1 or cy1 <= y0:
            out.append((x0, y0, x1, y1))
            continue
        if cy0 > y0:
            out.append((x0, y0, x1, cy0))
        if cy1 < y1:
            out.append((x0, cy1, x1, y1))
        ya, yb = max(y0, cy0), min(y1, cy1)
        if cx0 > x0:
            out.append((x0, ya, cx0, yb))
        if cx1 < x1:
            out.append((cx1, ya, x1, yb))
    return [r for r in out if r[2] - r[0] > 1.0 and r[3] - r[1] > 1.0]


# finish: (ambientCG set or None, tint -- or the colour of a plain finish --,
# roughness, colour detail). The roughness is the finish's (rough_fit): the
# old travertine floor took Travertine001's polished map x 0.45 -- 0.01, a
# mirror. unreal/build_scene.py lays the same floors from the same table.
FLOOR_FINISH = {"travertine": ("Travertine001", (1.0, 0.98, 0.95), 0.18, 0.9),
                "oak": ("WoodFloor040", (0.95, 0.82, 0.68), 0.45, 1.0),
                "concrete": (None, (0.42, 0.42, 0.41), 0.3, 1.0)}
FLOOR_T = 0.010             # m, the finish on the slab


def floor_plan(V):
    """The floor finishes of a design, as (label, finish, x0, y0, x1, y1, z)
    in metres: every room above grade (the roof excepted), less its nested
    rooms and the VOIDS on its floor, oak where ROLE says bedroom / dressing
    / family lounge, concrete in the service rooms, travertine elsewhere.
    Pure (unit-tested; build_scene.floor_plan is the same)."""
    level = getattr(V, "LEVEL", None) or {}
    below = set(getattr(V, "BELOW_GRADE_FLOORS", ()) or ())
    role = getattr(V, "ROLE", None) or {}
    voids = getattr(V, "VOIDS", None) or []
    out = []
    for r in V.ROOMS:
        name, x0, y0, x1, y1, _kind, fl = r[:7]
        if fl in below or fl not in level or fl == "RF":
            continue
        rects = [(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))]
        for q in V.ROOMS:
            if q[6] == fl and q[0] != name and min(q[1], q[3]) >= rects[0][0] \
                    and min(q[2], q[4]) >= rects[0][1] and max(q[1], q[3]) <= rects[0][2] \
                    and max(q[2], q[4]) <= rects[0][3]:
                rects = _rect_minus(rects, (min(q[1], q[3]), min(q[2], q[4]),
                                            max(q[1], q[3]), max(q[2], q[4])))
        for v in voids:
            if fl in v[5]:
                rects = _rect_minus(rects, tuple(v[1:5]))
        rl = role.get(name, "")
        finish = "oak" if rl in FLOOR_OAK_ROLES else \
            "concrete" if rl in FLOOR_CONCRETE_ROLES else "travertine"
        z = level[fl] * MM
        for j, (a, b, c, d) in enumerate(rects):
            out.append((f"{fl} {name} {j}", finish, a * MM, b * MM, c * MM, d * MM, z))
    return out


def floor_finishes(F):
    n = 0
    for label, finish, x0, y0, x1, y1, z in floor_plan(V):
        mat = F[finish]
        ob = _box_obj(f"ctx floor {label}", x0, y0, z, x1, y1, z + FLOOR_T, mat)
        world_uvs(ob, tuple(mat.get("tile_m", (1.0, 1.0))))
        n += 1
    return n


def floor_materials():
    out = {}
    for key, (asset, tint, rough, detail) in FLOOR_FINISH.items():
        label = {"travertine": "travertine floor, polished", "oak": "oak floor",
                 "concrete": "polished concrete"}[key]
        if asset:
            out[key] = pbr(label, asset, tex_size(asset), tint=tint,
                           rfit=_rough_fit_to(asset, rough), detail=detail)
        else:
            out[key] = plain(label, tint, rough)
    return out


# ------------------------------------------------------------------ light
SKY_CLAMP = 30.0            # radiance above this is "the sun", not "the sky"


HORIZON_LIFT_DEG = 10.0     # a design's sky: nothing of the HDRI's land shows


def world(hdri_stem, sun_az_deg, lift_deg=0.0):
    """Sky from the HDRI, sun from a lamp whose direction is set explicitly.

    The first version let the HDRI's own sun cast the shadows and rotated the
    image to aim it -- with the equirect convention inverted, so the garden
    front came out lit from the north-east. Now the HDRI is clamped at
    SKY_CLAMP (its sun removed), the energy clamped away is MEASURED and
    handed to a Sun lamp at the requested azimuth: one shadow, pointing the
    way it says, at the brightness the photograph recorded.

    lift_deg > 0 (a design with render hooks, HORIZON_LIFT_DEG): every
    direction below that elevation looks up the sky AT that elevation, so
    the photographed land -- aarfontein's bushveld hills rise ~9 deg above
    its horizon -- never shows over the render's own far-field ground; the
    sky just above them runs down to the horizon instead. The villa: 0, the
    graph exactly as before."""
    H = measure_hdri(hdri_stem)
    img, az_h, el, strength, colour = H["img"], H["az_h"], H["el"], H["strength"], H["colour"]
    az_t = math.radians(90.0 - sun_az_deg)          # compass -> maths angle
    rot = az_h - az_t                               # align the sky's bright side

    wd = bpy.data.worlds.new("desert")
    bpy.context.scene.world = wd
    try:
        wd.use_nodes = True
    except Exception:
        pass
    nt = wd.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0.0, 0.0, rot)
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = img
    clamp = nt.nodes.new("ShaderNodeVectorMath")
    clamp.operation = "MINIMUM"
    clamp.inputs[1].default_value = (SKY_CLAMP, SKY_CLAMP, SKY_CLAMP)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    if lift_deg > 0:
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        low = nt.nodes.new("ShaderNodeMath")
        low.operation = "MAXIMUM"
        low.inputs[1].default_value = math.sin(math.radians(lift_deg))
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        norm = nt.nodes.new("ShaderNodeVectorMath")
        norm.operation = "NORMALIZE"
        nt.links.new(mp.outputs["Vector"], sep.inputs["Vector"])
        nt.links.new(sep.outputs["X"], comb.inputs["X"])
        nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
        nt.links.new(sep.outputs["Z"], low.inputs[0])
        nt.links.new(low.outputs["Value"], comb.inputs["Z"])
        nt.links.new(comb.outputs["Vector"], norm.inputs[0])
        nt.links.new(norm.outputs["Vector"], env.inputs["Vector"])
    else:
        nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], clamp.inputs[0])
    nt.links.new(clamp.outputs["Vector"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    sd = bpy.data.lights.new("sun", "SUN")
    sd.energy = strength
    sd.color = colour
    sd.angle = math.radians(0.53)                   # the real sun's disc
    sun = bpy.data.objects.new("sun", sd)
    bpy.context.scene.collection.objects.link(sun)
    SUN.update(obj=sun, mapping=mp, az_h=az_h, colour=colour, energy=strength,
               background=bg, env=env, hdri=hdri_stem, el=math.degrees(el))
    aim_sun(sun_az_deg, math.degrees(el))
    return {"hdri": hdri_stem, "hdri_sun_elevation_deg": round(math.degrees(el), 1),
            "sun_strength": round(strength, 2)}


SUN = {}                    # the lamp and sky mapping, re-aimed per view
_HDRI = {}


def measure_hdri(stem):
    """An HDRI's sun, measured: the brightest pixel's direction (maths
    azimuth az_h, elevation el in radians) and the irradiance the SKY_CLAMP
    removes (strength, colour) -- the sun as the photograph recorded it."""
    if stem in _HDRI:
        return _HDRI[stem]
    import numpy as np
    path = os.path.join(HDRI, f"{stem}_4k.hdr")
    img = bpy.data.images.load(path, check_existing=True)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    rgb = px.reshape(h, w, 4)[:, :, :3]            # row 0 is the BOTTOM of the image
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    row, col = np.unravel_index(int(np.argmax(lum)), lum.shape)
    u = (col + 0.5) / w
    el = ((row + 0.5) / h - 0.5) * math.pi
    # Blender (Cycles) equirect: u = 0.5 - atan2(y, x) / 2pi
    az_h = (0.5 - u) * 2 * math.pi                  # maths angle of the HDRI sun

    # irradiance the clamp removes = the sun, measured from the photograph
    el_rows = ((np.arange(h) + 0.5) / h - 0.5) * math.pi
    omega = (2 * math.pi / w) * (math.pi / h) * np.cos(el_rows)
    excess = np.clip(rgb - SKY_CLAMP, 0.0, None)
    E = (excess * omega[:, None, None]).sum(axis=(0, 1))
    strength = float(E @ np.array([0.2126, 0.7152, 0.0722]))
    colour = tuple(float(c) for c in (E / max(E.max(), 1e-6)))
    _HDRI[stem] = {"img": img, "az_h": az_h, "el": el, "strength": strength,
                   "colour": colour}
    return _HDRI[stem]


def hdri_stems():
    return sorted(f[:-len("_4k.hdr")] for f in os.listdir(HDRI) if f.endswith("_4k.hdr"))


def pick_hdri(el_deg):
    """For a design's views: the HDRI whose own sun stands nearest `el_deg`
    (main passes the median of the views' suns, so a set shares one sky, as
    a photographer's shoot does) -- golden-hour views get a golden-hour sky
    (the warm glow on the horizon, the dimmer, oranger sun), not a noon sky
    under a low lamp. sun_for_view carries the lamp to each view's own sun.
    Only the SKY is chosen: none of the downloaded HDRIs is Dubai (aarfontein
    is a South African bushveld slope under a clear golden-hour sky, goegap
    rocky hills under a noon sun, kloppenheim_06 green fields under cloud,
    its sun hidden), so a design's context lays a far-field ground over the
    HDRI's photographed ground (context, FAR_FIELD_M)."""
    sunny = [s for s in hdri_stems() if measure_hdri(s)["strength"] >= 1.0]   # not overcast
    return min(sunny, key=lambda s: abs(math.degrees(measure_hdri(s)["el"]) - el_deg))


def aim_sun(az_deg, el_deg):
    """Point the Sun lamp from compass azimuth `az_deg`, elevation `el_deg`,
    and turn the sky so its bright side agrees. Low sun is warmer."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    towards = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
    SUN["obj"].rotation_euler = Vector((0, 0, -1)).rotation_difference(-towards).to_euler()
    SUN["mapping"].inputs["Rotation"].default_value = (
        0.0, 0.0, SUN["az_h"] - math.radians(90.0 - az_deg))
    warm = max(0.0, min(1.0, (30.0 - el_deg) / 20.0))    # 0 above 30 deg, 1 at 10
    r, g, b = SUN["colour"]
    SUN["obj"].data.color = (r, g * (1 - 0.10 * warm), b * (1 - 0.25 * warm))


def _transmittance(el_deg):
    """Direct sunlight through the air mass at elevation el (Kasten-Young),
    per R G B -- a rural, slightly dusty atmosphere."""
    e = max(el_deg, 1.0)
    am = 1.0 / (math.sin(math.radians(e)) + 0.50572 * (e + 6.07995) ** -1.6364)
    return [math.exp(-k * am) for k in (0.09, 0.14, 0.26)]


REF_SUN = 17.0              # the villa's noon sun (goegap, measured), exposure -0.5


def sun_for_view(el_deg):
    """For a design's own views, after aim_sun: the lamp's strength and
    colour carried from the HDRI's own sun elevation to the view's through
    the air mass (1.0 when they match), the sky dimmed with it, and the
    exposure a photographer would give the scene: -0.5 at the noon sun,
    opened up (3/4 of the difference) as the light falls."""
    t, t0 = _transmittance(el_deg), _transmittance(SUN["el"])
    rel = [a / b for a, b in zip(t, t0)]
    lum = 0.2126 * rel[0] + 0.7152 * rel[1] + 0.0722 * rel[2]
    energy = SUN["energy"] * lum
    SUN["obj"].data.energy = energy
    r, g, b = SUN["colour"]
    m = max(rel)
    SUN["obj"].data.color = (r * rel[0] / m, g * rel[1] / m, b * rel[2] / m)
    sky = max(0.4, min(1.0, math.sqrt(lum)))
    SUN["background"].inputs["Strength"].default_value = sky
    exposure = -0.5 + 0.75 * max(0.0, math.log2(REF_SUN / max(energy, 0.5)))
    return {"hdri": SUN["hdri"], "sun_energy": round(energy, 2),
            "sky_strength": round(sky, 2), "exterior_exposure": round(exposure, 2)}


def interior_lights():
    """Warm 3000 K ceiling light in every room, so the glazing reads as a
    lived-in house instead of black holes.

    A design with render hooks (MATERIALS / RENDER_VIEWS) hangs each room's
    light under its own storey's ceiling (LEVEL + CEIL) -- a basement's too.
    Without them (the villa) the original rule stands unchanged: GF rooms
    under the GF ceiling, every other room under the FF ceiling. (That rule
    puts the villa's 4 annex lights at +8.05 m instead of +2.85 m; correcting
    it changes the villa's renders, so it waits for the user's approval and
    a re-baseline -- see ANNEX_LIGHT_FIX.)"""
    n = 0
    per_storey = bool(DESIGN_VIEWS or DESIGN_MATERIALS) or ANNEX_LIGHT_FIX
    level = (getattr(V, "LEVEL", None) or {}) if per_storey else {}
    ceil_h = (getattr(V, "CEIL", None) or {}) if per_storey else {}
    for r in V.ROOMS:
        name, x0, y0, x1, y1, kind, floor = r
        if floor in level and floor in ceil_h:
            base, height = level[floor], ceil_h[floor]
        else:
            base = V.GF if floor == "GF" else V.FF
            height = V.GF_CH if floor == "GF" else V.FF_CH
        ceil = base + height - 150
        wx, wy = abs(x1 - x0) * MM, abs(y1 - y0) * MM
        ld = bpy.data.lights.new(f"room {name}", "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = wx * 0.6, wy * 0.6
        ld.energy = 18.0 * wx * wy
        ld.color = (1.0, 0.78, 0.55)
        ob = bpy.data.objects.new(f"light {name}", ld)
        ob.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, ceil * MM)
        bpy.context.scene.collection.objects.link(ob)
        n += 1
    return n


# ------------------------------------------------------------------ cameras
def views():
    if DESIGN_VIEWS:
        return design_views()
    cx, cy = V.PLOT_W / 2 * MM, V.PLOT_D / 2 * MM
    gz = 0.7                                      # pool-garden level, m
    ax = V.AXIS * MM
    # Each view has its own sun, from the SIDE: a sun behind the camera throws
    # every shadow out of sight and the massing reads flat (the first set did
    # exactly that). Azimuth compass degrees, elevation degrees.
    return {
        # name: (location, target, lens mm, ortho scale or None, (sun az, el))
        "aerial_sw": ((-13.0, -17.0, 21.0), (cx, cy - 1.0, 3.0), 35, None, (150, 38)),
        # from the pool deck, eye level, across the water to the garden front
        "garden":    ((19.2, 3.2, gz + 0.08 + 1.6), (ax - 1.0, 14.0, 4.4), 20, None, (215, 30)),
        # north front, raked by a low evening sun from the north-west
        "street":    ((5.5, 38.0, 1.7), (11.0, 21.0, 4.2), 24, None, (295, 16)),
        "aerial_ne": ((38.0, 45.0, 24.0), (cx, cy - 1.5, 2.0), 35, None, (320, 28)),
        # ortho_scale spans the WIDER side: a 29 m plot at 16:10 needs ~48
        "plan":      ((cx, cy, 60.0), (cx, cy, 0.0), None, 48.0, (150, 55)),
    }


# A design view's exposure (AgX, stops) follows its sun (sun_for_view); an
# interior view opens up INTERIOR_OPEN more, its ceiling lights turned down
# to INTERIOR_LIGHTS (they are there to make the windows read from outside,
# and inside by day they would wash every wall warm).
INTERIOR_OPEN = 1.0
INTERIOR_LIGHTS = 0.3
EXTERIOR_LIGHTS = 0.5       # golden hour: the rooms glow, they do not blaze
LEVEL_EYE_MAX = 3.0         # an eye this low gets two-point perspective
_LIGHT_BASE = {}


BACKLIT_OPEN = 0.5          # stops, a camera looking straight into the sun


def backlight(eye, target, sun_az):
    """A photographer opens up for a subject in its own shade: the more the
    camera looks toward the sun (compass), the more -- nothing from 90 deg
    off the sun or with the sun behind."""
    look = math.degrees(math.atan2(target[0] - eye[0], target[1] - eye[1])) % 360
    off = abs((look - sun_az + 180) % 360 - 180)
    return round(BACKLIT_OPEN * max(0.0, math.cos(math.radians(off))), 2)


def room_lights(k):
    for ld in bpy.data.lights:
        if ld.name.startswith("room "):
            base = _LIGHT_BASE.setdefault(ld.name, ld.energy)
            ld.energy = base * k


def design_views():
    """V.RENDER_VIEWS as views() tuples: eye, target (m), lens (mm), no ortho,
    (sun az, el)."""
    out = {}
    for name, v in DESIGN_VIEWS.items():
        out[name] = (tuple(float(c) for c in v["eye"]), tuple(float(c) for c in v["target"]),
                     float(v.get("lens", 24.0)), v.get("ortho"),
                     tuple(float(c) for c in v.get("sun", (240.0, 30.0))))
    return out


def view_setup(name):
    """Per-view extras for a design's own views: interior?, a fixed exposure
    if the view names one, level (two-point) camera."""
    v = DESIGN_VIEWS.get(name, {})
    interior = bool(v.get("interior"))
    level = bool(v.get("level", float(v.get("eye", (0, 0, 99))[2]) <= LEVEL_EYE_MAX))
    return {"interior": interior, "exposure": v.get("exposure"), "level": level}


EYE_CLEARANCE = 0.40        # m from any surface of the model


def clear_eye(eye, target, groups, clearance=EYE_CLEARANCE):
    """A design's camera must see the house, not the inside of a hedge. If
    the eye is inside a solid of the model, or nearer than `clearance` to
    one, walk it level toward the target (5 cm steps, at most half the way)
    until it is clear. Returns (eye, metres moved, status):
      'clear'    the design's eye was already clear (moved 0)
      'moved'    it was not; the returned eye is the first clear one, and
                 main() records a WARNING (the design's eye is wrong)
      'blocked'  no clear eye within half the way: the design's eye is
                 returned UNCHANGED (still inside or against the model), and
                 main() warns and records it -- the view needs a new eye.
    Every move and every failure is reported so the design's RENDER_VIEWS
    can be corrected."""
    return _clear_eye(eye, target, groups, clearance)


def _clear_eye(eye, target, groups, clearance):
    """clear_eye's search against the model's BVH trees (Blender only)."""
    from mathutils.bvhtree import BVHTree
    trees = []
    for obs in groups.values():
        for ob in obs:
            me, mw = ob.data, ob.matrix_world
            trees.append(BVHTree.FromPolygons([mw @ v.co for v in me.vertices],
                                              [tuple(p.vertices) for p in me.polygons]))
    dirs = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

    def inside(p):
        back = 0
        for d in dirs:
            best = None
            for t in trees:
                loc, nrm, _i, dist = t.ray_cast(p, d)
                if loc is not None and (best is None or dist < best[1]):
                    best = (nrm, dist)
            if best is not None and best[0].dot(d) > 0:
                back += 1
        return back >= 4

    def near(p):
        return any(t.find_nearest(p, clearance)[0] is not None for t in trees)

    return walk_clear(eye, target, lambda p: not inside(Vector(p)) and not near(Vector(p)))


def walk_clear(eye, target, is_clear, step=0.05, reach_frac=0.5):
    """Walk from `eye` level toward `target` in `step` m steps, at most
    `reach_frac` of the way, to the first point `is_clear` accepts:
    (eye, metres moved, 'clear' | 'moved' | 'blocked'). Pure Python (the
    Blender test is the callback), so the statuses are unit-tested."""
    ex, ey, ez = (float(c) for c in eye)
    hx, hy = float(target[0]) - ex, float(target[1]) - ey
    length = math.hypot(hx, hy)
    if is_clear((ex, ey, ez)):
        return (ex, ey, ez), 0.0, "clear"
    if length < 1e-6:
        return (ex, ey, ez), 0.0, "blocked"
    hx, hy = hx / length, hy / length
    k = 1
    while k * step <= length * reach_frac + 1e-9:
        s = k * step
        p = (ex + hx * s, ey + hy * s, ez)
        if is_clear(p):
            return (round(p[0], 3), round(p[1], 3), round(p[2], 3)), round(s, 2), "moved"
        k += 1
    return (ex, ey, ez), 0.0, "blocked"


def camera(name, loc, target, lens, ortho, level=False):
    """A camera at `loc` looking at `target`. level=True: two-point
    perspective -- the camera is kept level (verticals stay vertical) and
    the lens shifted so the target stays where a tilted camera put it."""
    cd = bpy.data.cameras.new(name)
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.lens = lens
    cd.clip_end = 500.0
    ob = bpy.data.objects.new(f"cam {name}", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    if level and not ortho:
        horiz = Vector((direction.x, direction.y, 0.0))
        pitch = math.atan2(direction.z, horiz.length)
        cd.sensor_fit = "HORIZONTAL"
        cd.shift_y = lens * math.tan(pitch) / cd.sensor_width
        direction = horiz
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return ob


# ------------------------------------------------------------------ render
def cycles(samples, res):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == kind]
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == kind
                    device = f"{kind}: " + ", ".join(sorted({d.name for d in gpus}))
                    sc.cycles.device = "GPU"
                    break
            except Exception:
                continue
    except Exception:
        pass
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPTIX" if device.startswith("OPTIX") else "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.cycles.volume_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
        sc.view_settings.exposure = -0.5    # desert sun otherwise bleaches concrete to plaster
    except Exception:
        pass
    sc.render.film_transparent = False
    return device


def export_twinmotion():
    """FBX with textures copied beside it, plus a glb. Both carry the real-
    world UVs (1 unit = 1 m), which is what Twinmotion's own materials expect
    when you swap ours for its library."""
    os.makedirs(TM, exist_ok=True)
    fbx = os.path.join(TM, "villa_twinmotion.fbx")
    glb = os.path.join(TM, "villa_twinmotion.glb")
    for o in bpy.data.objects:
        # the villa only: neighbours and street are render context, and
        # Twinmotion has its own tools (and library) for that
        o.select_set(o.type == "MESH" and not o.name.startswith("ctx "))
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True,
                             object_types={"MESH"}, path_mode="COPY",
                             embed_textures=True, apply_unit_scale=True,
                             use_mesh_modifiers=False)
    try:
        bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB",
                                  use_selection=True, export_apply=False)
    except Exception as exc:
        print("  glb export skipped:", str(exc)[:80])
        glb = None
    return fbx, glb


def export_palms():
    """A design's palms (render dressing, so not in the Twinmotion model) as
    their own glb beside it -- villa_palms.glb, trunks and frond strips with
    their UVs (the leaflets are cut by the material from them) -- so the
    Unreal build plants these very palms instead of approximating them.
    Returns the path, or None (no palms, or the export failed)."""
    obs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("ctx palm ")]
    if not obs:
        return None
    os.makedirs(TM, exist_ok=True)
    path = os.path.join(TM, "villa_palms.glb")
    for o in bpy.data.objects:
        o.select_set(o in obs)
    try:
        try:
            bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                                      export_apply=False, export_materials="NONE")
        except TypeError:
            bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                                      export_apply=False)
    except Exception as exc:
        print("  palms glb export skipped:", str(exc)[:80])
        return None
    return path


# ------------------------------------------------------------------ Twinmotion notes
def _sun_position(doy, hour, lat=25.2048, lon=55.2708, tz=4.0):
    """NOAA's approximate solar position: (azimuth from north, elevation), deg."""
    g = 2 * math.pi / 365.0 * (doy - 1 + (hour - 12) / 24.0)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    dec = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g)
           - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
           - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    ha = math.radians((hour * 60 + eqt + 4 * lon - 60 * tz) / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha)
    el = 90 - math.degrees(math.acos(max(-1.0, min(1.0, cz))))
    az = (math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la)
                                  - math.tan(dec) * math.cos(la))) + 180) % 360
    return az, el


def sun_date(az, el):
    """The Dubai date and clock time (UTC+4) whose sun is nearest (az, el),
    for a renderer that places the sun by date: (month, day, 'hh:mm', error deg)."""
    import datetime
    best = None
    for doy in range(1, 366):
        for m5 in range(5 * 12, 20 * 12):
            a, e = _sun_position(doy, m5 / 12.0)
            err = math.hypot(((a - az + 180) % 360 - 180) * math.cos(math.radians(el)), e - el)
            if best is None or err < best[0]:
                best = (err, doy, m5)
    err, doy, m5 = best
    d = datetime.date(2026, 1, 1) + datetime.timedelta(days=doy - 1)
    return d.month, d.day, f"{m5 // 12:02d}:{(m5 % 12) * 5:02d}", round(err, 1)


def design_package(assigned, eyes=None):
    """For a design with render hooks, beside the Twinmotion model:
      materials.json  group -> kind, colour, roughness, the texture set a
                      recipe is built on, the tint and detail it needs
                      (fit_tint), the colour it then averages
                      ('effective_color') and whether the tint had to be
                      clamped short of the design's colour ('tint_clamped');
                      plus every set's average colour ('_texture_average')
                      and 99th percentile ('_texture_high')
      views.json      RENDER_VIEWS as rendered: the eye (moved clear of the
                      model when it had to be), the design's eye, the Dubai
                      date and time of each view's sun
      TWINMOTION_STEPS.md  the import, the material swaps, the views.
    The Unreal build (unreal/build_scene.py) reads the two json files."""
    eyes = eyes or {}
    os.makedirs(TM, exist_ok=True)
    table = {}
    for grp, kind in sorted(assigned.items()):
        spec = DESIGN_MATERIALS.get(grp, {})
        asset = KIND_RECIPES.get(kind, {}).get("texture")
        e = {"kind": kind, "color": list(spec.get("color", ())), "roughness": spec.get("roughness"),
             "texture": asset, "about": KIND_RECIPES.get(kind, {}).get("about", "")}
        if asset and spec.get("color"):
            try:
                e["tile_m"] = list(tex_size(asset))
                tint, detail, clamped = _fit_to(asset, spec["color"], KIND_DETAIL.get(kind, 1.0))
                avg = tex_average(extract(asset)["Color"])
                e["tint"] = [round(v, 4) for v in tint]
                e["detail"] = round(detail, 4)
                e["texture_average"] = [round(v, 4) for v in avg]
                # what the textured surface averages: the design's colour
                # unless the tint had to be clamped (then say so)
                e["effective_color"] = [round(t * a, 4) for t, a in zip(tint, avg)]
                e["tint_clamped"] = clamped
            except Exception as exc:
                e["tint_error"] = str(exc)[:80]
        if asset and spec.get("roughness") is not None:
            try:
                # the design's roughness over the set's map: (gain, offset, lo, hi)
                e["roughness_fit"] = [round(v, 5) for v in _rough_fit_to(asset, spec["roughness"])]
            except Exception as exc:
                e["roughness_error"] = str(exc)[:80]
        table[grp] = e
    avgs, highs, rstats = {}, {}, {}
    for asset in sorted({r["texture"] for r in KIND_RECIPES.values() if r.get("texture")}):
        try:
            avgs[asset] = [round(v, 4) for v in tex_average(extract(asset)["Color"])]
            highs[asset] = [round(v, 4) for v in tex_high(extract(asset)["Color"])]
            maps = extract(asset)
            if "Roughness" in maps:
                rstats[asset] = [round(v, 5) for v in tex_rough_stats(maps["Roughness"])]
        except Exception:
            pass
    with open(os.path.join(TM, "materials.json"), "w") as f:
        json.dump(dict(table, _texture_average=avgs, _texture_high=highs,
                       _roughness_stats=rstats), f, indent=1)

    views_out = {}
    for name, v in DESIGN_VIEWS.items():
        az, el = v.get("sun", (240.0, 30.0))
        mo, dy, hm, err = sun_date(az, el)
        eye, moved, status = eyes.get(name, (tuple(v["eye"]), 0.0, "unchecked"))
        views_out[name] = {"eye": list(eye), "design_eye": list(v["eye"]), "eye_moved_m": moved,
                           "eye_status": status,
                           "target": list(v["target"]), "lens": v.get("lens", 24.0),
                           "sun": [az, el], "interior": bool(v.get("interior")),
                           "date": [mo, dy], "clock": hm, "sun_date_error_deg": err,
                           "photo": v.get("photo")}
    with open(os.path.join(TM, "views.json"), "w") as f:
        json.dump(views_out, f, indent=1)

    title = getattr(V, "PROJECT_TITLE", None) or getattr(V, "PROJECT", "the villa")
    L = [f"# Twinmotion: {title}", "",
         "Generated by villa_blender.py from the design data "
         f"({os.path.join(DESIGN_DIR, 'villa_design.py')}). Re-run it after a design change.",
         "", "## 1. Import", "",
         "1. Twinmotion > Import > `villa_twinmotion.fbx` (this folder); units metres,",
         "   'Collapse' off, so each material group stays a separate object.",
         "   (`villa_twinmotion.glb` is the same model for a glTF import.)",
         "2. The UVs are baked at real-world size (1 UV tile = the texture's size in",
         "   metres); set a library material's scale to its real size and it lines up.",
         "3. Location: Dubai, 25.2048 N 55.2708 E, UTC+4. Model +Y is north.",
         "", "## 2. Materials (from MATERIALS)", "",
         "| Group | Kind | Colour (linear RGB) | Roughness | Swap for |",
         "|---|---|---|---|---|"]
    swap = {"render_white": "Plaster > white render", "stone_dark": "Stone > dark slate / ledgestone",
            "timber": "Wood > teak / iroko boards", "timber_dark": "Wood > dark walnut",
            "timber_deck": "Wood > composite decking", "metal_black": "Metal > black powder coat",
            "limestone": "Stone > limestone, honed", "interlock": "Ground > concrete pavers",
            "grass": "Vegetation > grass", "hedge": "Vegetation > hedge (or a hedge asset)",
            "gravel": "Ground > gravel", "soil": "Ground > soil", "water": "Water > pool, over "
            "a blue mosaic tile on the pool shell", "glass": "Glass > clear",
            "travertine": "Stone > travertine", "concrete": "Concrete > smooth"}
    for grp, e in table.items():
        c = ", ".join(f"{v:.2f}" for v in e["color"]) if e["color"] else "-"
        L.append(f"| {grp} | {e['kind']} | {c} | {e['roughness'] if e['roughness'] is not None else '-'} "
                 f"| {swap.get(e['kind'], '-')} |")
    L += ["", "## 3. Views (from RENDER_VIEWS)", "",
          "Place a camera at the eye, aim it at the target (model metres: x east, "
          "y north, z up), set the focal length (36 mm film) and the date and time "
          "whose sun matches the render's.", "",
          "| View | Eye (m) | Target (m) | Lens | Sun az / el | Date, time (UTC+4) | Photo |",
          "|---|---|---|---|---|---|---|"]
    for name, r in views_out.items():
        az, el = r["sun"]
        mo, dy = r["date"]
        eye = ", ".join(f"{c:g}" for c in r["eye"])
        if r["eye_status"] == "moved":
            eye += (f" (design: {', '.join(f'{c:g}' for c in r['design_eye'])}, inside a "
                    f"hedge or wall; moved {r['eye_moved_m']} m)")
        elif r["eye_status"] == "blocked":
            eye += " (**inside the model and no clear eye found: pick a new eye**)"
        tgt = ", ".join(f"{c:g}" for c in r["target"])
        L.append(f"| {name}{' (interior)' if r['interior'] else ''} | {eye} | {tgt} | "
                 f"{r['lens']} mm | {az:g} / {el:g} | {dy} {_MONTHS[mo - 1]} {r['clock']} "
                 f"(within {r['sun_date_error_deg']} deg) | {r['photo'] or '-'} |")
    lay = context_layout()
    L += ["", "## 4. Context", "",
          "The package holds the house and its plot only (the planting group "
          "carries the design's hedge colour; the Blender renders add leaf "
          "cards on top). Add the rest from Twinmotion's library, where the "
          "Blender renders have it:", "",
          f"- Street north of the plot (y {lay['D']:g} m): 2 m pavement, 12 m road, 2 m pavement.",
          f"- Neighbours: plots {lay['W']:g} x {lay['D']:g} m either side and across the "
          f"street; houses {lay['side']:g} m off the side boundaries, "
          f"{lay['depth']:g} m deep, {lay['height']:g} m high."]
    south = render_context().get("south")
    if south == "golf":
        L.append("- South of the rear boundary: a golf course (rough, then the fairway "
                 f"from {GOLF_ROUGH_M:g} m out, to {GOLF_DEPTH_M:g} m).")
    trees = getattr(V, "SITE_TREES", None) or []
    if trees:
        L += [f"- Palms (date palm, 5-7 m trunk), {len(trees)} at SITE_TREES "
              "(model metres, crown diameter):", "",
              "| # | x (m) | y (m) | Crown (m) |", "|---|---|---|---|"]
        for i, t in enumerate(trees):
            L.append(f"| {i + 1} | {t[0] * MM:g} | {t[1] * MM:g} | {t[2] * MM:g} |")
        L.append("")
    gates = list(V.gates()) if callable(getattr(V, "gates", None)) else []
    if gates:
        L.append("- Gates (dark vertical slats, 45 mm at 90 mm, the boundary wall's height) "
                 "in the street wall at x " + ", ".join(
                     f"{min(g[1], g[2]) * MM:g}-{max(g[1], g[2]) * MM:g} m ({g[0].lower()})"
                     for g in gates) + ".")
    L += ["", "## 5. Sky", "",
          f"The Blender renders light the scene with the {SUN.get('hdri', 'chosen')} HDRI "
          "for its clear golden-hour sky (its measured sun re-aimed per view). It is not "
          "Dubai: its photographed land is kept out of the renders -- the far-field "
          f"ground covers it and the sky {HORIZON_LIFT_DEG:g} deg up is carried down to "
          "the horizon. In Twinmotion use the Dubai sun of section 3 and a clear sky.", ""]
    with open(os.path.join(TM, "TWINMOTION_STEPS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return os.path.join(TM, "TWINMOTION_STEPS.md")


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def main():
    o = args()
    t0 = time.perf_counter()
    os.makedirs(OUT, exist_ok=True)
    clear()
    groups = import_groups()
    lo, hi = bbox([ob for obs in groups.values() for ob in obs])
    print(f"  design {DESIGN_DIR}\n  out    {RENDER}")
    if (not IS_PROJECT and not RENDER_FOLLOWS_OUT and os.environ.get("VILLA_OUT")
            and os.path.normcase(os.path.abspath(os.environ["VILLA_OUT"])) != os.path.normcase(BASE)):
        print(f"  NOTE the villa renders from and into {RENDER} as it always did: VILLA_OUT "
              f"({os.environ['VILLA_OUT']}) is not used for the villa unless "
              f"VILLA_RENDER_FOLLOWS_OUT=1")
    print(f"  imported {sum(len(v) for v in groups.values())} objects in "
          f"{len(groups)} groups   bbox {hi.x - lo.x:.1f} x {hi.y - lo.y:.1f} x "
          f"{hi.z - lo.z:.1f} m")
    # Every group must land exactly where villa_gltf.py built it. The
    # exporter's probes prove the model; this proves the IMPORT of it.
    expect = json.load(open(os.path.join(RENDER, "groups.json")))
    wrong = []
    for key, obs in sorted(groups.items()):
        a, b = bbox(obs)
        e = expect.get(key)
        if e is None:
            wrong.append(f"{key}: not in groups.json")
            continue
        got = [a.x, a.y, a.z, b.x, b.y, b.z]
        err = max(abs(g - v * MM) for g, v in zip(got, e))
        if err > 0.005:
            wrong.append(f"{key}: off by {err * 1000:.0f} mm  got "
                         f"{[round(g, 2) for g in got]}")
    if wrong:
        raise SystemExit("import does not match the model:\n  " + "\n  ".join(wrong))
    print(f"  all {len(groups)} groups within 5 mm of the exported model")

    M = materials()
    missing = []
    assigned = {}               # group -> the kind (design) or ASSIGN name
    cache = {}
    for key, obs in groups.items():
        spec = DESIGN_MATERIALS.get(key)
        if spec and spec.get("kind"):
            mat = design_material(key, spec, cache)
            assigned[key] = spec["kind"]
        else:
            name = ASSIGN.get(key, "")
            mat = M.get(name)
            if mat is None and name in KIND_RECIPES:
                mat = M[name] = kind_material(name)
            assigned[key] = name or None
        if mat is None:
            missing.append(key)
            continue
        size = tuple(mat.get("tile_m", (1.0, 1.0)))
        for ob in obs:
            world_uvs(ob, size)
            ob.data.materials.clear()
            ob.data.materials.append(mat)
    if missing:
        print("  no material for:", missing)
    lined = 0
    if DESIGN_MATERIALS.get("water", {}).get("kind") == "water" and groups.get("pool"):
        # the blue mosaic tank under the pool coping (the listing's pool)
        lining = kind_material("mosaic", DESIGN_MATERIALS["water"].get("color"), 0.15,
                               name="pool mosaic")
        size = tuple(groups["pool"][0].data.materials[0].get("tile_m", (1.0, 1.0)))
        for ob in groups["pool"]:
            lined += mosaic_lining(ob, lining, size)
        for ob in groups.get("water", []):
            settle_water(ob)
    planting = DESIGN_MATERIALS.get("planting", {})
    hedge_swap = []             # (object, design's hedge, render-only inside)
    for ob in groups.get("planting", []):
        if planting.get("kind") == "hedge":
            # a clipped hedge: leaf cards on every face, the design's green,
            # over a body in the shade deep inside a hedge. The dark body is
            # for the render only: the Twinmotion package gets the design's
            # hedge (export_twinmotion below swaps it back).
            leaves = ob.data.materials[0]
            inside = hedge_material(
                "hedge, inside", _scaled(tuple(planting.get("color", (0.2, 0.36, 0.15))), 0.3),
                float(planting.get("roughness", 0.9)))
            ob.data.materials[0] = inside
            hedge_swap.append((ob, leaves, inside))
            shrubs(ob, leaves, density=500.0, radius=(0.7, 1.3), spacing=0.02,
                   up_only=False, leaf=(0.06, 0.035))
        else:
            shrubs(ob, M["shrub"])
    holes = []
    if DESIGN_MATERIALS or DESIGN_VIEWS:
        for ob in groups.get("pool", []):
            a, b = bbox([ob])
            holes.append((a.x, a.y, b.x, b.y))
    n_ctx = context(M, holes)
    print(f"  context: {n_ctx} objects (ground, street, {13 if DESIGN_VIEWS else 5} neighbouring plots"
          + (f", far field {FAR_FIELD_M:g} m" if DESIGN_VIEWS else "") + ")")
    extras = {}
    if DESIGN_MATERIALS or DESIGN_VIEWS:
        extras["palms"] = palms()
        extras["floor_finishes"] = floor_finishes(floor_materials())
        extras["pool_faces_lined"] = lined
        frames = DESIGN_MATERIALS.get("frames")
        extras["gates"] = gate_leaves(design_material("frames", frames, cache) if frames
                                      else plain("gate", (0.05, 0.05, 0.055), 0.4))
        print(f"  design extras: {extras}")

    hdri0 = o["hdri"]
    if DESIGN_VIEWS and not o.get("hdri_given"):
        els = sorted(float(v.get("sun", (0, 30.0))[1]) for v in DESIGN_VIEWS.values())
        hdri0 = pick_hdri(els[len(els) // 2])
    light = world(hdri0, o["sun_az"], HORIZON_LIFT_DEG if DESIGN_VIEWS else 0.0)
    if DESIGN_VIEWS:
        light["horizon_lift_deg"] = HORIZON_LIFT_DEG
    if DESIGN_VIEWS and not o.get("hdri_given"):
        light["hdris"] = {s: {"sun_elevation_deg": round(math.degrees(measure_hdri(s)["el"]), 1),
                              "sun_strength": round(measure_hdri(s)["strength"], 2)}
                          for s in hdri_stems()}
    n_lights = interior_lights()
    device = cycles(o["samples"], o["res"])
    print(f"  sky {light}   {n_lights} room lights   device {device}")

    # a design camera must stand clear of the model (and of the palms)
    eyes = {}
    warnings = []
    if DESIGN_VIEWS:
        bpy.context.view_layer.update()          # the palms' matrix_world
        solid = dict(groups, palms=[ob for ob in bpy.data.objects
                                    if ob.name.startswith("ctx palm") and ob.name.endswith("trunk")])
        for name, (loc, tgt, _l, _o, _s) in views().items():
            eyes[name] = clear_eye(loc, tgt, solid)
            eye, moved, status = eyes[name]
            if status == "moved":
                # rendered, from a clear eye -- but the design's eye is wrong,
                # and a run with one is not reported as clean
                msg = (f"{name}: the eye {tuple(loc)} is inside or within {EYE_CLEARANCE} m "
                       f"of the model; rendered from {eye} ({moved} m away) -- set that eye "
                       f"in RENDER_VIEWS")
                warnings.append(msg)
                print("  WARNING " + msg)
            elif status == "blocked":
                msg = (f"{name}: the eye {tuple(loc)} is inside or within {EYE_CLEARANCE} m of "
                       f"the model and no clear eye lies within half the way to the target: "
                       f"rendered from INSIDE the model -- give the view a new eye")
                warnings.append(msg)
                print("  WARNING " + msg)

    blend = os.path.join(RENDER, "villa_render.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    for ob, leaves, _inside in hedge_swap:      # the package: the design's hedge
        ob.data.materials[0] = leaves
    fbx, glb = export_twinmotion()
    for ob, _leaves, inside in hedge_swap:      # the render: leaf cards over shade
        ob.data.materials[0] = inside
    steps = design_package(assigned, eyes) if (DESIGN_MATERIALS or DESIGN_VIEWS) else None
    if DESIGN_MATERIALS or DESIGN_VIEWS:
        extras["palms_glb"] = export_palms()
    print(f"  saved {os.path.basename(blend)}; Twinmotion: {os.path.basename(fbx)}"
          + (f", {os.path.basename(glb)}" if glb else "")
          + (f", {os.path.basename(steps)}" if steps else ""))

    rendered = []
    if o["render"]:
        V_ = views()
        for name in o["views"]:
            if name not in V_:
                print(f"  unknown view {name}")
                continue
            loc, tgt, lens, ortho, (saz, sel) = V_[name]
            extra = {}
            if DESIGN_VIEWS:
                vs = view_setup(name)
                eye, moved, eye_status = eyes[name]
                cam = camera(name, eye, tgt, lens, ortho, level=vs["level"])
                aim_sun(saz, sel)
                extra = sun_for_view(sel)
                exposure = vs["exposure"]
                if exposure is None:
                    exposure = extra["exterior_exposure"] + (
                        INTERIOR_OPEN if vs["interior"] else backlight(eye, tgt, saz))
                bpy.context.scene.view_settings.exposure = float(exposure)
                room_lights(INTERIOR_LIGHTS if vs["interior"] else EXTERIOR_LIGHTS)
                extra.update(vs, exposure=round(float(exposure), 2), eye=list(eye),
                             eye_moved_m=moved, eye_status=eye_status)
            else:
                cam = camera(name, loc, tgt, lens, ortho)
                aim_sun(saz, sel)
            bpy.context.scene.camera = cam
            path = os.path.join(OUT, f"villa_{name}.png")
            bpy.context.scene.render.filepath = path
            t = time.perf_counter()
            bpy.ops.render.render(write_still=True)
            rec = {"view": name, "file": path, "sun": [saz, sel],
                   "seconds": round(time.perf_counter() - t, 1)}
            rec.update(extra)
            rendered.append(rec)
            print(f"  rendered {name:10s} {time.perf_counter() - t:6.1f}s -> {path}")

    log = {"device": device, "samples": o["samples"], "resolution": o["res"],
           "light": light, "groups": {k: len(v) for k, v in groups.items()},
           "materials": {k: assigned.get(k) for k in groups},
           "rendered": rendered, "blend": blend, "fbx": fbx, "glb": glb,
           "seconds": round(time.perf_counter() - t0, 1)}
    if DESIGN_MATERIALS or DESIGN_VIEWS:
        log.update({"design": DESIGN_DIR, "extras": extras, "twinmotion_steps": steps,
                    "eyes": {k: {"eye": list(e), "moved_m": m, "status": s}
                             for k, (e, m, s) in eyes.items()},
                    "warnings": warnings})
    with open(os.path.join(OUT, "render_log.json"), "w") as f:
        json.dump(log, f, indent=1)
    print(f"  done in {log['seconds']}s")


if __name__ == "__main__":
    main()
