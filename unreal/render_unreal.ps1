<#
.SYNOPSIS
    Scripted, path-traced renders of the villa in Unreal Engine 5.8 -- one command.

.DESCRIPTION
    Stages (default: all, in this order):
      setup   create the UE project VillaRender from the TP_AEC_BlankBP template
              (skipped when it exists; -Recreate rebuilds it from scratch)
      build   headless editor + build_scene.py: new level, glb import, materials,
              context, SunSky (Dubai), cameras, LevelSequence, MRQ queue manifest
      render  headless Movie Render Queue, Path Tracer pass -> PNG per view,
              copied to <Villa>\render\unreal\villa_<view>.png + unreal_log.json

    The first run compiles shaders for a long time (tens of minutes); later runs
    reuse the DDC. Nothing is installed or downloaded.

    A PROJECT (projects\<name>, see run_project.py): set VILLA_DESIGN_DIR to its
    folder and VILLA_OUT to its deliverables. The model and groups are read
    from VILLA_OUT\render, the design's RENDER_VIEWS / MATERIALS drive the
    cameras and materials (build_scene.py), the level is built under
    /Game/<Name> with logs in logs\<name>, so the villa's level, logs and
    queue manifest are left as they were. Without VILLA_OUT a project uses
    Desktop\<OUT_NAME> (run_project.py's rule), never the villa's Desktop\Villa.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File C:\Users\lsire\autocad-mcp\unreal\render_unreal.ps1

.EXAMPLE
    .\render_unreal.ps1 -Samples 256 -Width 1200 -Height 750 -OutDir $env:TEMP\villa_ue_test

.EXAMPLE
    $env:VILLA_DESIGN_DIR = 'C:\Users\lsire\autocad-mcp\projects\fairway'
    $env:VILLA_OUT = 'C:\Users\lsire\OneDrive\Desktop\Fairway'
    .\render_unreal.ps1 -Samples 256          # every RENDER_VIEWS view
#>
[CmdletBinding()]
param(
    # 'paths' only prints the folders a run would use (JSON) and starts nothing
    [ValidateSet('all', 'setup', 'build', 'render', 'paths')]
    [string]$Stage = 'all',
    # model: the Blender-exported glb with named materials and real-world UVs
    [string]$Glb = '',
    # render\groups.json written by villa_gltf.py: the import is checked against it
    [string]$Groups = '',
    # ambientCG texture sets (Color / NormalDX / Roughness) used by the UE materials
    [string]$TexDir = '',
    [string]$OutDir = '',
    # empty: the villa's aerial_sw,garden,street, or every RENDER_VIEWS view of a project
    [string]$Views = '',
    [int]$Samples = 1024,
    [int]$Width = 2400,
    [int]$Height = 1500,
    [switch]$Recreate,
    [int]$TimeoutMinutes = 360
)

$ErrorActionPreference = 'Stop'
$Here = $PSScriptRoot
$Engine = 'C:\Program Files\Epic Games\UE_5.8'
$EditorCmd = Join-Path $Engine 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Template = Join-Path $Engine 'Templates\TP_AEC_BlankBP'
$ProjectName = 'VillaRender'
$ProjectDir = Join-Path $Here $ProjectName
$UProject = Join-Path $ProjectDir "$ProjectName.uproject"

# A project's design (VILLA_DESIGN_DIR, as run_project.py sets it): its own
# content folder, logs and queue manifest; the villa's are left alone
$DesignDir = $env:VILLA_DESIGN_DIR
if ($DesignDir -and ([System.IO.Path]::GetFullPath($DesignDir).TrimEnd('\') -eq
        [System.IO.Path]::GetFullPath((Split-Path $Here -Parent)).TrimEnd('\'))) {
    $DesignDir = ''                     # the pipeline folder itself: the villa's design
}
if ($DesignDir -and -not (Test-Path (Join-Path $DesignDir 'villa_design.py'))) {
    throw "VILLA_DESIGN_DIR $DesignDir has no villa_design.py"
}
$Design = if ($DesignDir) { Split-Path $DesignDir -Leaf } else { '' }
$ContentRoot = if ($Design) { (Get-Culture).TextInfo.ToTitleCase($Design.ToLower()) -replace '[^A-Za-z0-9]', '' } else { 'Villa' }
$LogDir = if ($Design) { Join-Path (Join-Path $Here 'logs') $Design } else { Join-Path $Here 'logs' }

# VILLA_OUT redirects the whole deliverables folder, as it does for every builder.
# Unset: the villa's Desktop\Villa; a PROJECT's Desktop\<OUT_NAME> (read from its
# villa_design.py as text, else the folder name capitalised -- run_project.py's
# rule), never the villa's folder: its model would be rendered with the
# project's cameras and its PNGs overwritten.
$DefaultVilla = 'C:\Users\lsire\OneDrive\Desktop\Villa'
if ($env:VILLA_OUT) {
    $VillaRoot = $env:VILLA_OUT
} elseif ($DesignDir) {
    $src = [System.IO.File]::ReadAllText((Join-Path $DesignDir 'villa_design.py'))
    $m = [regex]::Match($src, '(?m)^OUT_NAME\s*=\s*["'']([^"'']+)["'']')
    $OutName = if ($m.Success) { $m.Groups[1].Value } else { $Design.Substring(0, 1).ToUpper() + $Design.Substring(1).ToLower() }
    if ($OutName -notmatch '^[A-Za-z0-9 _.-]+$' -or $OutName.Trim('. ') -eq '') { throw "OUT_NAME '$OutName' is not a plain folder name" }
    $VillaRoot = Join-Path (Split-Path $DefaultVilla -Parent) $OutName
} else {
    $VillaRoot = $DefaultVilla
}
if ($DesignDir -and ([System.IO.Path]::GetFullPath($VillaRoot).TrimEnd('\') -eq $DefaultVilla)) {
    throw "the project $Design would read and write the villa's deliverables ($DefaultVilla); set VILLA_OUT"
}
if (-not $Glb) { $Glb = Join-Path $VillaRoot 'render\twinmotion\villa_twinmotion.glb' }
if (-not $Groups) { $Groups = Join-Path $VillaRoot 'render\groups.json' }
if (-not $TexDir) {
    # the run's own unpacked sets first, then the downloads' (build_scene.py
    # takes a ';'-joined list and looks for each set in turn)
    $TexDir = (@((Join-Path $VillaRoot 'render\materials\_tex'), (Join-Path $DefaultVilla 'render\materials\_tex')) |
        Where-Object { Test-Path $_ } | Select-Object -Unique) -join ';'
}
if (-not $OutDir) { $OutDir = Join-Path $VillaRoot 'render\unreal' }

# the plugins this pipeline needs, on top of the template's own list
$RequiredPlugins = @('PythonScriptPlugin', 'EditorScriptingUtilities', 'SequencerScripting',
    'MovieRenderPipeline', 'SunPosition', 'Interchange', 'InterchangeEditor',
    'InterchangeAssets', 'NNEDenoiser')

function Write-Utf8([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($false)))
}

function Add-IniLines([string]$Path, [string]$Section, [string[]]$Lines) {
    # append $Lines under [$Section], creating the section when missing
    $text = if (Test-Path $Path) { [System.IO.File]::ReadAllText($Path) } else { '' }
    $hdr = "[$Section]"
    $idx = $text.IndexOf($hdr)
    if ($idx -lt 0) {
        $text = $text.TrimEnd() + "`r`n`r`n$hdr`r`n" + ($Lines -join "`r`n") + "`r`n"
    } else {
        $at = $idx + $hdr.Length
        $text = $text.Substring(0, $at) + "`r`n" + ($Lines -join "`r`n") + $text.Substring($at)
    }
    Write-Utf8 $Path $text
}

function Sync-PluginPlatforms {
    # The editor flags a project as "requires update" when a plugin entry's
    # SupportedTargetPlatforms differs from the plugin's own descriptor (the
    # template itself is stale for DatasmithCADImporter). Mirror the engine.
    $up = Get-Content $UProject -Raw | ConvertFrom-Json
    $index = @{}
    Get-ChildItem (Join-Path $Engine 'Engine\Plugins') -Recurse -Filter *.uplugin | ForEach-Object { $index[$_.BaseName] = $_.FullName }
    $changed = $false
    foreach ($p in $up.Plugins) {
        if (-not $index.ContainsKey($p.Name)) { throw "plugin $($p.Name) is not installed in $Engine" }
        # UE's JSON reader accepts trailing commas (VariantManager has one); PowerShell's does not
        $d = (Get-Content $index[$p.Name] -Raw) -replace ',(\s*[\]}])', '$1' | ConvertFrom-Json
        $want = @($d.SupportedTargetPlatforms | Where-Object { $_ })
        $have = @($p.SupportedTargetPlatforms | Where-Object { $_ })
        if (($want -join ',') -ne ($have -join ',')) {
            if ($p.PSObject.Properties['SupportedTargetPlatforms']) { $p.PSObject.Properties.Remove('SupportedTargetPlatforms') }
            if ($want.Count) { $p | Add-Member -NotePropertyName SupportedTargetPlatforms -NotePropertyValue $want }
            $changed = $true
        }
    }
    if ($changed) { Write-Utf8 $UProject ($up | ConvertTo-Json -Depth 6); Write-Host '[setup] plugin platforms synced with the engine' }
}

function Set-NoUnattendedCrashUpload {
    # An -unattended editor sends crash reports to Epic by default
    # (bSendUnattendedBugReports=true); a scripted run should not send anything.
    $ini = Join-Path $ProjectDir 'Config\DefaultEditorSettings.ini'
    $text = if (Test-Path $ini) { [System.IO.File]::ReadAllText($ini) } else { '' }
    if ($text -notmatch 'bSendUnattendedBugReports') {
        Add-IniLines $ini '/Script/UnrealEd.CrashReportsPrivacySettings' @('bSendUnattendedBugReports=False')
    }
}

function New-VillaProject {
    if ((Test-Path $UProject) -and -not $Recreate) {
        Write-Host "[setup] project exists: $UProject"
        Sync-PluginPlatforms
        Set-NoUnattendedCrashUpload
        return
    }
    if (Test-Path $ProjectDir) { Remove-Item -Recurse -Force $ProjectDir }
    $tname = Split-Path $Template -Leaf
    Write-Host "[setup] $tname -> $ProjectDir"

    # 1. copy the template the way GameProjectUtils does: everything except the
    #    TemplateDefs.ini FoldersToIgnore / FilesToIgnore
    $defs = Get-Content (Join-Path $Template 'Config\TemplateDefs.ini')
    $ignoreDirs = @($defs | Where-Object { $_ -match '^FoldersToIgnore=' } |
        ForEach-Object { ($_ -split '=', 2)[1].Trim('"') })
    $ignoreFiles = @($defs | Where-Object { $_ -match '^FilesToIgnore=' } |
        ForEach-Object { ($_ -split '=', 2)[1].Trim('"').Replace('%TEMPLATENAME%', $tname).Replace('/', '\') })
    New-Item -ItemType Directory -Force $ProjectDir | Out-Null
    Get-ChildItem $Template -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Template.Length + 1)
        $top = ($rel -split '\\')[0]
        if ($ignoreDirs -contains $top) { return }
        if ($ignoreFiles -contains $rel) { return }
        $dst = Join-Path $ProjectDir $rel
        New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
        Copy-Item $_.FullName $dst
    }

    # 2. ReplacementsInFiles / FilenameReplacements (cpp, h, ini, cs): template name -> project name
    Get-ChildItem $ProjectDir -Recurse -File -Include *.ini, *.cs, *.cpp, *.h | ForEach-Object {
        $t = [System.IO.File]::ReadAllText($_.FullName)
        $n = [regex]::Replace($t, [regex]::Escape($tname), $ProjectName, 'IgnoreCase')
        if ($n -ne $t) { Write-Utf8 $_.FullName $n }
        if ($_.Name -match [regex]::Escape($tname)) {
            Rename-Item $_.FullName ($_.Name -ireplace [regex]::Escape($tname), $ProjectName)
        }
    }

    # 3. <Project>.uproject from the template's descriptor + the plugins we need
    $up = Get-Content (Join-Path $Template "$tname.uproject") -Raw | ConvertFrom-Json
    $up.EngineAssociation = '5.8'
    $up.Description = 'Villa renders: scripted Movie Render Queue path tracing (autocad-mcp\unreal)'
    $plugins = [System.Collections.ArrayList]@($up.Plugins)
    foreach ($name in $RequiredPlugins) {
        $p = $plugins | Where-Object { $_.Name -eq $name } | Select-Object -First 1
        if ($p) { $p.Enabled = $true }
        else { [void]$plugins.Add([pscustomobject]@{ Name = $name; Enabled = $true }) }
    }
    $up.Plugins = $plugins.ToArray()
    Write-Utf8 $UProject ($up | ConvertTo-Json -Depth 6)
    Sync-PluginPlatforms
    Set-NoUnattendedCrashUpload

    # 4. config fix-ups GameProjectUtils applies to a project made from a template
    $eng = Join-Path $ProjectDir 'Config\DefaultEngine.ini'
    $game = Join-Path $ProjectDir 'Config\DefaultGame.ini'
    $t = [System.IO.File]::ReadAllText($eng)
    # the template's default map comes from the BlankDefault feature pack, which a
    # plain copy does not install: point both maps at the template's own Main
    $t = $t -replace '(?m)^GameDefaultMap=.*$', 'GameDefaultMap=/Game/Main.Main'
    $t = $t -replace '(?m)^\+EditorTemplateMapOverrides=.*BlankDefault.*\r?\n', ''
    # path tracing only: no baked lighting (no "lighting needs rebuild", fewer
    # shader permutations); legacy (non-Substrate) materials for predictable
    # translucency in the path tracer
    $t = $t -replace '(?m)^r\.AllowStaticLighting=True', 'r.AllowStaticLighting=False'
    $t = $t -replace '(?m)^r\.Substrate=True', 'r.Substrate=False'
    Write-Utf8 $eng $t
    Add-IniLines $eng 'URL' @("GameName=$ProjectName")
    Add-IniLines $eng '/Script/Engine.Engine' @(
        "+ActiveGameNameRedirects=(OldGameName=`"$tname`",NewGameName=`"/Script/$ProjectName`")",
        "+ActiveGameNameRedirects=(OldGameName=`"/Script/$tname`",NewGameName=`"/Script/$ProjectName`")")
    Add-IniLines $eng '/Script/PythonScriptPlugin.PythonScriptPluginSettings' @(
        'bDeveloperMode=True', 'bRemoteExecution=False')
    $guid = [guid]::NewGuid().ToString('N').ToUpper()
    Add-IniLines $game '/Script/EngineSettings.GeneralProjectSettings' @(
        "ProjectID=$guid", "ProjectName=$ProjectName",
        'Description=Scripted path-traced renders of the Dubai villa')
    Write-Host "[setup] done: $UProject"
}

function Invoke-Unreal([string[]]$Arguments, [string]$Name) {
    New-Item -ItemType Directory -Force $LogDir | Out-Null
    $log = Join-Path $LogDir "$Name.log"
    $out = Join-Path $LogDir "$Name.stdout.txt"
    if (Test-Path $log) { Remove-Item $log -Force }
    $all = @("`"$UProject`"") + $Arguments + @('-unattended', '-nopause', '-nosplash', '-NoSound',
        '-stdout', '-FullStdOutLogOutput', "-abslog=`"$log`"")
    Write-Host "[$Name] UnrealEditor-Cmd $($all -join ' ')"
    $t0 = Get-Date
    $p = Start-Process -FilePath $EditorCmd -ArgumentList $all -PassThru -NoNewWindow `
        -RedirectStandardOutput $out -RedirectStandardError "$out.err"
    $null = $p.Handle          # without this, PowerShell 5.1 loses ExitCode
    if (-not $p.WaitForExit($TimeoutMinutes * 60 * 1000)) {
        Stop-Process -Id $p.Id -Force
        throw "[$Name] timed out after $TimeoutMinutes min (log: $log)"
    }
    $p.WaitForExit()
    $mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
    # UE 5.8 sometimes faults in teardown after its log has closed (exit
    # -1073741819); the work is done by then and the status file says so. Its
    # crash-monitor process is then left behind: stop the one this run started.
    Get-Process CrashReportClient* -ErrorAction SilentlyContinue |
        Where-Object { $_.StartTime -ge $t0 -and $_.Path -like "$Engine*" } |
        Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "[$Name] exit $($p.ExitCode) after $mins min (log: $log)"
    return $p.ExitCode
}

function Set-BuildEnv {
    $env:VILLA_UE_GLB = (Resolve-Path $Glb).Path
    $env:VILLA_UE_GROUPS = $Groups
    $env:VILLA_UE_TEX = $TexDir
    $env:VILLA_UE_VIEWS = $Views
    $env:VILLA_UE_SAMPLES = "$Samples"
    $env:VILLA_UE_RES = "$Width,$Height"
    $env:VILLA_UE_FRAMES = (Join-Path $LogDir 'frames')
    $env:VILLA_UE_STATUS = (Join-Path $LogDir 'build_status.json')
    $env:VILLA_UE_ROOT = "/Game/$ContentRoot"
    if ($DesignDir) { $env:VILLA_UE_DESIGN = (Join-Path $DesignDir 'villa_design.py') }
    else { Remove-Item Env:\VILLA_UE_DESIGN -ErrorAction SilentlyContinue }
}

function Invoke-Build {
    if (-not (Test-Path $Glb)) { throw "model not found: $Glb" }
    Set-BuildEnv
    if (Test-Path $env:VILLA_UE_STATUS) { Remove-Item $env:VILLA_UE_STATUS -Force }
    # idempotent re-import: everything build_scene.py makes is deleted before the
    # editor starts (nothing is loaded yet, so nothing can hold a reference);
    # the imported textures are kept, they never change
    foreach ($d in 'Maps', 'Model', 'Render', 'Materials', 'Pipelines') {
        $p = Join-Path $ProjectDir "Content\$ContentRoot\$d"
        if (Test-Path $p) { Remove-Item -Recurse -Force $p }
    }
    [void](Invoke-Unreal @("-ExecutePythonScript=`"$Here\build_scene.py`"") 'build_scene')
    if (-not (Test-Path $env:VILLA_UE_STATUS)) { throw "[build] build_scene.py wrote no status (see logs\build_scene.log)" }
    $st = Get-Content $env:VILLA_UE_STATUS -Raw | ConvertFrom-Json
    if (-not $st.ok) { throw "[build] failed: $($st.error)" }
    Write-Host "[build] ok: $($st.summary)"
    return $st
}

function Invoke-Render {
    Set-BuildEnv
    if (-not (Test-Path $env:VILLA_UE_STATUS)) { throw "[render] run the build stage first" }
    $st = Get-Content $env:VILLA_UE_STATUS -Raw | ConvertFrom-Json
    $frames = $env:VILLA_UE_FRAMES
    if (Test-Path $frames) { Remove-Item -Recurse -Force $frames }
    New-Item -ItemType Directory -Force $frames | Out-Null
    $t0 = Get-Date
    [void](Invoke-Unreal @($st.map, '-game', "-MoviePipelineConfig=`"$($st.manifest)`"",
            '-windowed', '-ResX=1280', '-ResY=720', '-RenderOffscreen') 'render_mrq')
    New-Item -ItemType Directory -Force $OutDir | Out-Null
    $done = @()
    foreach ($v in $st.views) {
        $src = Get-ChildItem $frames -Recurse -Filter $v.file | Select-Object -First 1
        if (-not $src) { Write-Warning "[render] no frame for $($v.name)"; continue }
        $dst = Join-Path $OutDir "villa_$($v.name).png"
        Copy-Item $src.FullName $dst -Force
        $done += [pscustomobject]@{ view = $v.name; file = $dst; when = $v.when; sun = $v.sun }
        Write-Host "[render] $dst"
    }
    $log = [pscustomobject]@{
        engine = 'Unreal Engine 5.8.3, Movie Render Queue, Path Tracer'
        model = $Glb; samples = $Samples; resolution = @($Width, $Height)
        minutes = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
        rendered = $done; build = $st
    }
    Write-Utf8 (Join-Path $OutDir 'unreal_log.json') ($log | ConvertTo-Json -Depth 8)
    if ($done.Count -ne @($st.views).Count) { throw "[render] $($done.Count) of $(@($st.views).Count) views rendered (see logs\render_mrq.log)" }
}

switch ($Stage) {
    'paths' {
        [pscustomobject]@{ design = $Design; design_dir = $DesignDir; villa_root = $VillaRoot
            glb = $Glb; groups = $Groups; tex_dir = $TexDir; out_dir = $OutDir
            content_root = "/Game/$ContentRoot"; log_dir = $LogDir } | ConvertTo-Json -Compress
    }
    'setup' { New-VillaProject }
    'build' { New-VillaProject; [void](Invoke-Build) }
    'render' { Invoke-Render }
    'all' { New-VillaProject; [void](Invoke-Build); Invoke-Render }
}
