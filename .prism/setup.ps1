# PRISM Setup Script for Windows PowerShell / PowerShell
# Installs PRISM adapter files to your project.
# Usage:
#   From the project root after unzipping a release to .prism:
#     powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1
#     powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Style freedom
#   From inside the PRISM directory:
#     .\setup.ps1 -Style guided -ProjectRoot C:\path\to\project
#   Upgrade:
#     powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Upgrade
#     powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Upgrade -Force

[CmdletBinding()]
param(
    [switch]$Upgrade,
    [switch]$Force,
    [string]$Platform = "core",
    [string]$Mode = "",
    [string]$Style = "",
    [string]$ProjectRoot = "",
    [Alias("h")]
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$VersionFile = Join-Path $ScriptDir "VERSION"
$PlatformsHelper = Join-Path $ScriptDir "scripts/platforms.py"
$Action = if ($Upgrade) { "upgrade" } else { "install" }

function Write-Info($Message) { Write-Host "[PRISM] $Message" -ForegroundColor Cyan }
function Write-Warn($Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Ok($Message) { Write-Host "[OK]   $Message" -ForegroundColor Green }
function Fail($Message) { Write-Error "[ERROR] $Message"; exit 1 }
function Header($Message) { Write-Host ""; Write-Host $Message -ForegroundColor White }

function Read-FrameworkVersion {
    if (Test-Path -LiteralPath $VersionFile) {
        return (Get-Content -LiteralPath $VersionFile -Raw).Trim()
    }
    return ""
}

# --- Platform registry (loaded from adapters/platforms.json via scripts/platforms.py) ---

function Get-PythonCommand {
    foreach ($Cmd in @("python3", "python", "py")) {
        try {
            $null = & $Cmd --version 2>$null
            if ($LASTEXITCODE -eq 0) { return $Cmd }
        } catch {
            # Try next command
        }
    }
    return $null
}

$PythonCmd = Get-PythonCommand
if (-not $PythonCmd) {
    Fail "Could not find python3/python/py on PATH. PRISM setup requires Python to read adapters/platforms.json."
}

if (-not (Test-Path -LiteralPath $PlatformsHelper -PathType Leaf)) {
    Fail "Platform registry helper missing: $PlatformsHelper"
}

# Each row: key, label, dest, guided_src, freedom_src, legacy_dests(comma), size_warning_chars
$PlatformRows = @()
$RawTsv = & $PythonCmd $PlatformsHelper tsv 2>$null
if ($LASTEXITCODE -ne 0 -or -not $RawTsv) {
    Fail "Failed to load platform registry via $PythonCmd $PlatformsHelper tsv"
}
function Convert-Sentinel([string]$Value) {
    # platforms.py emits "-" for empty optional fields so shell `read` doesn't
    # collapse adjacent tabs. Translate it back to an empty string here.
    if ($Value -eq "-") { return "" }
    return $Value
}

foreach ($Line in ($RawTsv -split "`r?`n")) {
    if (-not $Line.Trim()) { continue }
    $Parts = $Line -split "`t"
    if ($Parts.Count -lt 7) { $Parts += @("") * (7 - $Parts.Count) }
    $LegacyRaw = Convert-Sentinel $Parts[5]
    $SizeRaw = Convert-Sentinel $Parts[6]
    $PlatformRows += [pscustomobject]@{
        Key            = $Parts[0]
        Label          = $Parts[1]
        Dest           = $Parts[2]
        GuidedSrc      = $Parts[3]
        FreedomSrc     = $Parts[4]
        LegacyDests    = if ($LegacyRaw) { $LegacyRaw -split "," } else { @() }
        SizeWarnChars  = if ($SizeRaw) { [int]$SizeRaw } else { 0 }
    }
}
$AllPlatformKeys = $PlatformRows | ForEach-Object { $_.Key }
$CorePlatformKeys = @("claude", "copilot", "codex", "cursor")  # Default 4-platform install set; other 7 install only via explicit --Platform

function Get-PlatformRow([string]$Key) {
    return ($PlatformRows | Where-Object { $_.Key -eq $Key } | Select-Object -First 1)
}

function Get-AdapterSource([string]$Name, [string]$SelectedMode) {
    $Row = Get-PlatformRow $Name
    if (-not $Row) { return $null }
    $Rel = if ($SelectedMode -eq "freedom") { $Row.FreedomSrc } else { $Row.GuidedSrc }
    return (Join-Path $ScriptDir $Rel)
}

function Get-AdapterDest([string]$Name) {
    $Row = Get-PlatformRow $Name
    if (-not $Row) { return $null }
    return (Join-Path $ProjectRoot $Row.Dest)
}

function Get-AdapterLegacyDests([string]$Name) {
    $Row = Get-PlatformRow $Name
    if (-not $Row) { return @() }
    return @($Row.LegacyDests | Where-Object { $_ })
}

# Emit a one-line warning if the installed adapter exceeds the platform's
# documented size limit (e.g. Windsurf 12,000 chars). Does NOT fail or truncate.
function Test-OversizeWarning([string]$Name, [string]$DestPath) {
    $Row = Get-PlatformRow $Name
    if (-not $Row -or $Row.SizeWarnChars -le 0) { return }
    if (-not (Test-Path -LiteralPath $DestPath -PathType Leaf)) { return }
    $Size = (Get-Item -LiteralPath $DestPath).Length
    if ($Size -gt $Row.SizeWarnChars) {
        Write-Warn "${Name}: adapter is ${Size} chars; ${Name} loader limit is $($Row.SizeWarnChars) chars - content past byte $($Row.SizeWarnChars) will be truncated by the tool."
        Write-Warn "  See README 'Supported AI Coding Tools' section for per-tool size caveats."
    }
}

function Test-KnownPlatform([string]$Name) {
    return ($AllPlatformKeys -contains $Name)
}

function Normalize-Mode([string]$Value) {
    switch ($Value) {
        "" { return "" }
        "guided" { return "guided" }
        "freedom" { return "freedom" }
        "freestyle" { return "guided" }
        default { return $null }
    }
}

function Require-AdapterSource([string]$Source) {
    if (Test-Path -LiteralPath $Source -PathType Leaf) { return }

    Fail @"
Source adapter not found: $Source

This PRISM directory does not contain generated adapter outputs.
That usually means you are running setup.ps1 from a source checkout instead of a release package.

Use one of these paths:
  1. Recommended: build a release package, then run setup from the unzipped .prism directory:
       cd "$ScriptDir"
       .\scripts\release.sh
       Expand-Archive prism-v$PrismVersion.zip -DestinationPath C:\path\to\target-project -Force
       cd C:\path\to\target-project
       powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Style <guided|freedom>

  2. Local testing only: generate active adapters into this checkout, run setup, then remove generated adapter outputs before source validation or committing:
       cd "$ScriptDir"
       python scripts\generate_adapters.py --output-root .
       powershell -ExecutionPolicy Bypass -File .\setup.ps1 -ProjectRoot C:\path\to\target-project -Style <guided|freedom>

Source validation intentionally fails when generated active adapter outputs are left in the source tree.
"@
}

function Read-ConfigValue([string]$ConfigPath, [string]$Key, [string]$DefaultValue) {
    if (-not (Test-Path -LiteralPath $ConfigPath)) { return $DefaultValue }
    $Line = Get-Content -LiteralPath $ConfigPath | Where-Object { $_.Trim().StartsWith("${Key}: ") } | Select-Object -First 1
    if (-not $Line) { return $DefaultValue }
    if ($Line -match '"([^"]*)"') { return $Matches[1] }
    return $DefaultValue
}

function Write-ConfigText([string]$ConfigPath, [string]$Text) {
    [System.IO.File]::WriteAllText($ConfigPath, $Text, [System.Text.Encoding]::UTF8)
}

function Test-ManagedPackagePath([string]$RelativePath) {
    $Path = $RelativePath.Replace("\", "/")
    if ($Path -match '^(adapters|core|docs|scripts|legacy|sessions|dist|vi)/') { return $true }
    return @(
        "README.md",
        "README_vi.md",
        "diagram.xml",
        "prism-config.md",
        "prism.json",
        "setup.sh",
        "setup.ps1",
        "VERSION",
        "MANIFEST.txt"
    ) -contains $Path
}

function Remove-StalePackageFiles {
    $Manifest = Join-Path $ScriptDir "MANIFEST.txt"
    if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
        Write-Warn "Package manifest not found; skipping stale .prism file cleanup"
        return
    }

    $Managed = @{}
    Get-Content -LiteralPath $Manifest | ForEach-Object {
        $Entry = $_.Trim().Replace("\", "/")
        if ($Entry) { $Managed[$Entry] = $true }
    }

    $Base = $ScriptDir.TrimEnd("\", "/")
    $PrunedCount = 0
    Get-ChildItem -LiteralPath $ScriptDir -File -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $RelativePath = $_.FullName.Substring($Base.Length).TrimStart("\", "/").Replace("\", "/")
        if ($RelativePath.StartsWith("backups/")) { return }
        if ((Test-ManagedPackagePath $RelativePath) -and (-not $Managed.ContainsKey($RelativePath))) {
            Remove-Item -LiteralPath $_.FullName -Force
            $PrunedCount += 1
        }
    }

    foreach ($Name in @("adapters", "core", "docs", "scripts", "legacy", "sessions", "dist", "vi")) {
        $Root = Join-Path $ScriptDir $Name
        if (-not (Test-Path -LiteralPath $Root -PathType Container)) { continue }
        Get-ChildItem -LiteralPath $Root -Directory -Recurse -Force -ErrorAction SilentlyContinue |
            Sort-Object { $_.FullName.Length } -Descending |
            ForEach-Object {
                if (-not (Get-ChildItem -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue)) {
                    Remove-Item -LiteralPath $_.FullName -Force
                }
            }
    }

    if ($PrunedCount -gt 0) {
        Write-Ok "Removed $PrunedCount stale managed .prism file(s)"
    } else {
        Write-Ok "No stale managed .prism files found"
    }
}

function Move-LegacyPrismBackups {
    $LegacyBackupDir = Join-Path $ScriptDir "backups"
    if (-not (Test-Path -LiteralPath $LegacyBackupDir -PathType Container)) { return }

    $BackupRoot = Join-Path $ProjectRoot ".prism-backups"
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    $LegacyTarget = Join-Path $BackupRoot ("legacy-prism-backups-" + (Get-Date -Format "yyyy-MM-dd-HHmmss"))
    Move-Item -LiteralPath $LegacyBackupDir -Destination $LegacyTarget -Force
    Write-Ok "Moved legacy .prism/backups to $LegacyTarget"
}

# Backup + remove legacy adapter paths (e.g. cursor's old .cursorrules) for a given platform.
function Migrate-LegacyAdapterPaths([string]$Name, [string]$BackupDir) {
    $LegacyList = Get-AdapterLegacyDests $Name
    if (-not $LegacyList -or $LegacyList.Count -eq 0) { return }

    foreach ($LegacyRel in $LegacyList) {
        $Abs = Join-Path $ProjectRoot $LegacyRel
        if (Test-Path -LiteralPath $Abs -PathType Leaf) {
            New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
            $LegacyBaseName = Split-Path -Leaf $Abs
            Copy-Item -LiteralPath $Abs -Destination (Join-Path $BackupDir "$LegacyBaseName.legacy") -Force
            Remove-Item -LiteralPath $Abs -Force
            Write-Ok "${Name}: removed legacy $LegacyRel (backup: $LegacyBaseName.legacy)"
        }
    }
}

function Install-GuidedPrecommitHook([string]$SelectedMode) {
    if ($SelectedMode -ne "guided") {
        return
    }
    $GitDir = Join-Path $ProjectRoot ".git"
    if (-not (Test-Path -LiteralPath $GitDir -PathType Container)) {
        Write-Warn "No .git directory found; skipped PRISM Living Truth pre-commit hook install"
        return
    }
    $HookSrc = Join-Path $ScriptDir "core/tools/precommit_living_truth.py"
    $HookDir = Join-Path $GitDir "hooks"
    $HookDest = Join-Path $HookDir "pre-commit"
    if (-not (Test-Path -LiteralPath $HookSrc -PathType Leaf)) {
        Write-Warn "PRISM pre-commit hook source not found; skipped hook install"
        return
    }
    New-Item -ItemType Directory -Force -Path $HookDir | Out-Null
    if (Test-Path -LiteralPath $HookDest -PathType Leaf) {
        $Existing = Get-Content -LiteralPath $HookDest -Raw
        if ($Existing.Contains("precommit_living_truth.py") -or $Existing.Contains("PRISM pre-commit hook")) {
            Write-Ok "PRISM Living Truth pre-commit hook already installed"
        } else {
            Write-Warn "Existing git pre-commit hook found; PRISM Living Truth hook not installed automatically"
            Write-Warn "To enable it, chain $HookSrc from $HookDest"
        }
        return
    }
    Copy-Item -LiteralPath $HookSrc -Destination $HookDest -Force
    try {
        & chmod +x $HookDest 2>$null
    } catch {
        # Windows may not have chmod; Git for Windows can still run the hook by path.
    }
    Write-Ok "Installed PRISM Living Truth pre-commit hook"
}

$PrismVersion = Read-FrameworkVersion
if ([string]::IsNullOrWhiteSpace($PrismVersion)) {
    Fail "Could not resolve PRISM framework version from $VersionFile"
}

if ($Help) {
    Write-Host "PRISM Setup v$PrismVersion"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  From the project root after unzipping a release:"
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 [OPTIONS]"
    Write-Host "    pwsh -File .\.prism\setup.ps1 [OPTIONS]"
    Write-Host "  From inside the PRISM directory:"
    Write-Host "    .\setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  (default)               Fresh install - set up PRISM for a new or existing project"
    Write-Host "  -Upgrade                Upgrade PRISM to v$PrismVersion (preserves docs and config values)"
    Write-Host "  -Force                  With -Upgrade: re-apply even when installed version equals target"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Style <name>           guided | freedom (default: guided; install only, not upgrade)"
    $PlatformChoices = ($AllPlatformKeys -join '|') + '|core|all'
    Write-Host "  -Platform <name>        $PlatformChoices (default: core = claude/copilot/codex/cursor)"
    Write-Host "  -ProjectRoot <path>     Target project root (defaults to parent of PRISM directory)"
    Write-Host "  -Help                   Show this help"
    Write-Host ""
    Write-Host "Platforms supported:"
    foreach ($Row in $PlatformRows) {
        $Legacy = if ($Row.LegacyDests.Count -gt 0) { "  (legacy: " + ($Row.LegacyDests -join ',') + ")" } else { "" }
        Write-Host ("  {0,-12} {1,-20} -> {2}{3}" -f $Row.Key, $Row.Label, $Row.Dest, $Legacy)
    }
    Write-Host ""
    Write-Host "Note: codex / opencode / kiro / antigravity all write to AGENTS.md."
    Write-Host "      When -Platform all is used, AGENTS.md is written once (dedupe by destination)."
    Write-Host ""
    Write-Host "Styles:"
    Write-Host "  guided     Full framework with explicit commands (start product, approve, etc.)"
    Write-Host "  freedom    No gates, no approval, no immutable versioning. Edit in-place. PERMANENT choice."
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Style freedom"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Upgrade"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Upgrade -Force"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\.prism\setup.ps1 -Platform gemini -Style guided"
    exit 0
}

$StyleExplicit = $false
if ($Style) {
    $Mode = $Style
    $StyleExplicit = $true
} elseif ($Mode) {
    $StyleExplicit = $true
} else {
    $Mode = "guided"
}

if ($Mode) {
    $RequestedMode = $Mode
    $NormalizedMode = Normalize-Mode $Mode
    if ($null -eq $NormalizedMode) {
        Write-Warn "Invalid style: $RequestedMode"
        Write-Warn "Supported styles: guided, freedom"
        exit 1
    }
    $Mode = $NormalizedMode
    if ($StyleExplicit -and $RequestedMode -eq "freestyle") {
        Write-Warn "freestyle has been removed. Using guided instead."
    }
}

if ($Platform -and $Platform -ne "all" -and $Platform -ne "core" -and -not (Test-KnownPlatform $Platform)) {
    Write-Warn "Invalid platform: $Platform"
    Write-Warn ("Supported platforms: " + ($AllPlatformKeys -join ', ') + ", core, all")
    exit 1
}

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $ScriptDir
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

if ($Action -eq "upgrade") {
    Header "PRISM Upgrade to v$PrismVersion"
    Write-Info "PRISM directory: $ScriptDir"
    Write-Info "Project root:    $ProjectRoot"

    $ConfigTemplate = Join-Path $ScriptDir "prism-config.md"
    $Config = Join-Path $ProjectRoot "prism-config.md"
    $BackupDir = Join-Path (Join-Path $ProjectRoot ".prism-backups") ("pre-upgrade-" + (Get-Date -Format "yyyy-MM-dd-HHmmss"))

    Header "Step 1: Pre-flight Check"
    $InstalledVersion = Read-ConfigValue $Config "version" ""
    if (-not $InstalledVersion) {
        Write-Warn "Could not detect installed PRISM version from prism-config.md"
        Write-Warn "Treating as upgrade from unknown version"
        $InstalledVersion = "unknown"
    }

    if ($InstalledVersion -eq $PrismVersion -and -not $Force) {
        Write-Ok "Already at v$PrismVersion. Use -Force to re-apply."
        exit 0
    }

    if ($InstalledVersion -eq $PrismVersion) {
        Write-Info "Re-applying v$PrismVersion (-Force)"
    } else {
        Write-Info "Installed: v$InstalledVersion -> Upgrading to: v$PrismVersion"
    }

    $ConfigMode = Read-ConfigValue $Config "mode" "guided"
    $CurrentMode = Normalize-Mode $ConfigMode
    if ($null -eq $CurrentMode) {
        Write-Warn "Unknown installed mode '$ConfigMode'. Defaulting to guided for upgrade."
        $CurrentMode = "guided"
    } elseif ($ConfigMode -eq "freestyle") {
        Write-Warn "Legacy freestyle install detected. Upgrade will migrate it to guided."
    }

    if ($ConfigMode -eq "freestyle") {
        Write-Info "Mode: $CurrentMode (legacy freestyle normalized)"
    } else {
        Write-Info "Mode: $CurrentMode (preserved)"
    }

    if ($StyleExplicit) {
        Write-Warn "-Style/-Mode is ignored during upgrade. Style is preserved from existing config."
        Write-Warn "To change style after upgrade, reinstall with -Style guided or -Style freedom."
    }

    $DocsDir = Join-Path $ProjectRoot "docs"
    $DraftCount = 0
    if (Test-Path -LiteralPath $DocsDir) {
        $DraftCount = (Get-ChildItem -LiteralPath $DocsDir -Recurse -File -ErrorAction SilentlyContinue |
            Select-String -SimpleMatch "status: DRAFT" -List -ErrorAction SilentlyContinue |
            Measure-Object).Count
    }

    Header "Step 2: Backup"
    Move-LegacyPrismBackups
    $BackupRoot = Join-Path $ProjectRoot ".prism-backups"
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    $BackupGitignore = Join-Path $BackupRoot ".gitignore"
    if (-not (Test-Path -LiteralPath $BackupGitignore -PathType Leaf)) {
        [System.IO.File]::WriteAllText($BackupGitignore, "*`n!.gitignore`n", [System.Text.Encoding]::UTF8)
    }
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

    foreach ($Name in $AllPlatformKeys) {
        $Dest = Get-AdapterDest $Name
        if (Test-Path -LiteralPath $Dest -PathType Leaf) {
            # Multiple platforms may share a dest (e.g. AGENTS.md). Backing up
            # by basename is safe: subsequent iterations overwrite the same
            # file with identical content.
            Copy-Item -LiteralPath $Dest -Destination (Join-Path $BackupDir (Split-Path -Leaf $Dest)) -Force
            Write-Ok "Backed up: $(Split-Path -Leaf $Dest)"
        }
        foreach ($LegacyRel in (Get-AdapterLegacyDests $Name)) {
            $LegacyAbs = Join-Path $ProjectRoot $LegacyRel
            if (Test-Path -LiteralPath $LegacyAbs -PathType Leaf) {
                Copy-Item -LiteralPath $LegacyAbs -Destination (Join-Path $BackupDir "$(Split-Path -Leaf $LegacyAbs).legacy") -Force
                Write-Ok "Backed up legacy: $LegacyRel"
            }
        }
    }

    if (Test-Path -LiteralPath $Config -PathType Leaf) {
        Copy-Item -LiteralPath $Config -Destination (Join-Path $BackupDir "prism-config.md") -Force
        Write-Ok "Backed up: prism-config.md"
    }

    Write-Ok "Backup saved to: $BackupDir"

    Header "Step 3: Package Cleanup"
    Remove-StalePackageFiles

    if ($Platform -eq "all" -or $Platform -eq "core") {
        # Auto-detect installed adapters by checking both current and legacy dests
        $Platforms = @()
        foreach ($Name in $AllPlatformKeys) {
            $Dest = Get-AdapterDest $Name
            $Found = (Test-Path -LiteralPath $Dest -PathType Leaf)
            if (-not $Found) {
                foreach ($LegacyRel in (Get-AdapterLegacyDests $Name)) {
                    if (Test-Path -LiteralPath (Join-Path $ProjectRoot $LegacyRel) -PathType Leaf) {
                        $Found = $true
                        break
                    }
                }
            }
            if ($Found) { $Platforms += $Name }
        }
        if (-not $Platforms) {
            Write-Info "No existing adapters found; installing all platforms"
            $Platforms = $AllPlatformKeys
        }
    } else {
        $Platforms = @($Platform)
    }
    Write-Info "Platforms: $($Platforms -join ' ')"

    Header "Step 4: Adapter Update"
    $InstalledDests = @{}
    foreach ($Name in $Platforms) {
        $Source = Get-AdapterSource $Name $CurrentMode
        $Dest = Get-AdapterDest $Name
        $AdapterName = Split-Path -Leaf $Dest

        Require-AdapterSource $Source

        Migrate-LegacyAdapterPaths $Name $BackupDir

        if ($InstalledDests.ContainsKey($Dest)) {
            Write-Info "${Name}: skipped - $AdapterName already written by another platform"
            continue
        }

        if (-not (Test-Path -LiteralPath $Dest -PathType Leaf)) {
            $DestDir = Split-Path -Parent $Dest
            if ($DestDir -and -not (Test-Path -LiteralPath $DestDir)) {
                New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
            }
            Copy-Item -LiteralPath $Source -Destination $Dest -Force
            Write-Ok "${AdapterName}: fresh install ($Name)"
            Test-OversizeWarning $Name $Dest
            $InstalledDests[$Dest] = $true
            continue
        }

        $FoundMatch = $false
        foreach ($CheckMode in @("guided", "freedom")) {
            foreach ($CheckPlatform in $AllPlatformKeys) {
                $CheckSource = Get-AdapterSource $CheckPlatform $CheckMode
                if ((Test-Path -LiteralPath $CheckSource -PathType Leaf) -and
                    ((Get-FileHash -LiteralPath $Dest).Hash -eq (Get-FileHash -LiteralPath $CheckSource).Hash)) {
                    $FoundMatch = $true
                    break
                }
            }
            if ($FoundMatch) { break }
        }

        $DestDir = Split-Path -Parent $Dest
        if ($DestDir -and -not (Test-Path -LiteralPath $DestDir)) {
            New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
        }
        Copy-Item -LiteralPath $Source -Destination $Dest -Force
        if ($FoundMatch) {
            Write-Ok "${AdapterName}: updated (no customizations detected) - $Name"
        } else {
            Write-Warn "${AdapterName}: updated - your previous version is in $BackupDir"
            Write-Warn "  Review the backup and re-add any custom rules if needed"
        }
        Test-OversizeWarning $Name $Dest
        $InstalledDests[$Dest] = $true
    }

    Header "Step 5: Config Version"
    if (-not (Test-Path -LiteralPath $Config -PathType Leaf) -and (Test-Path -LiteralPath $ConfigTemplate -PathType Leaf)) {
        Copy-Item -LiteralPath $ConfigTemplate -Destination $Config -Force
        Write-Ok "Created missing project config at $Config"
    }

    if (Test-Path -LiteralPath $Config -PathType Leaf) {
        $Text = Get-Content -LiteralPath $Config -Raw
        if ($Text -match 'version:\s*"[^"]*"') {
            $Text = $Text -replace 'version:\s*"[^"]*"', "version: `"$PrismVersion`""
            Write-Ok "Updated prism.version to $PrismVersion"
        } else {
            $Text = $Text -replace '(?m)^prism:\s*$', "prism:`n  version: `"$PrismVersion`"             # installed PRISM version"
            Write-Ok "Added prism.version field ($PrismVersion)"
        }

        if ($Text -match 'mode:\s*"[^"]*"') {
            $Text = $Text -replace 'mode:\s*"[^"]*"', "mode: `"$CurrentMode`""
            if ($ConfigMode -eq "freestyle") {
                Write-Ok "Migrated prism.mode from freestyle to $CurrentMode"
            } else {
                Write-Ok "Preserved prism.mode as $CurrentMode"
            }
        } else {
            $Text = $Text -replace '(?m)^prism:\s*$', "prism:`n  mode: `"$CurrentMode`"                  # guided | freedom"
            Write-Ok "Added prism.mode field ($CurrentMode)"
        }
        Write-ConfigText $Config $Text
    }

    $SprintSupportCount = 0
    if (Test-Path -LiteralPath $DocsDir) {
        New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "product/epics") | Out-Null
        New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "design") | Out-Null
        New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "architecture") | Out-Null
        New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "testing") | Out-Null
        Get-ChildItem -LiteralPath $DocsDir -Directory -Filter "sprint-v*" -ErrorAction SilentlyContinue | ForEach-Object {
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "product/proposals/epics") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "design/proposals") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "architecture/proposals") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "testing/proposals") | Out-Null
            New-Item -ItemType File -Force -Path (Join-Path $_.FullName "product/proposals/epics/.gitkeep") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "tempo/in-progress") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "tempo/completed") | Out-Null
            New-Item -ItemType Directory -Force -Path (Join-Path $_.FullName "changes") | Out-Null
            $script:SprintSupportCount += 1
        }
    }

    if ($SprintSupportCount -gt 0) {
        Write-Ok "Ensured tempo/ and changes/ directories for $SprintSupportCount sprint(s)"
    }

    Install-GuidedPrecommitHook $CurrentMode

    Header "Upgrade Complete: v$InstalledVersion -> v$PrismVersion"
    Write-Ok "Core:     Updated (phase engines, orchestrator, templates)"
    Write-Info "Adapter:  See results above"
    Write-Ok "Config:   Project-root prism-config.md updated, project values preserved"
    if ($DraftCount -gt 0) {
        Write-Warn "Docs:     $DraftCount in-progress doc(s) - will be checked on next resume"
    } else {
        Write-Ok "Docs:     No in-progress documents"
    }
    Write-Ok "Backup:   $BackupDir"
    Write-Info "Your existing sprints and approved documents are untouched."
    Write-Info "Next: open your AI tool and continue where you left off."
    Write-Info "To rollback: restore files from $BackupDir"
    exit 0
}

Header "PRISM Setup v$PrismVersion"
Write-Info "PRISM directory: $ScriptDir"
Write-Info "Project root:    $ProjectRoot"
Write-Info "Style:           $Mode"

if ($Platform -eq "all") {
    $Platforms = $AllPlatformKeys
} elseif ($Platform -eq "core") {
    $Platforms = $CorePlatformKeys
} else {
    $Platforms = @($Platform)
}
Write-Info "Adapters:        $($Platforms -join ' ')"

# Hint about extended platforms when running default core install
if ($Platform -eq "core" -and $Action -eq "install") {
    $ExtendedKeys = $AllPlatformKeys | Where-Object { $CorePlatformKeys -notcontains $_ }
    if ($ExtendedKeys.Count -gt 0) {
        Write-Info "(extended platforms not installed: $($ExtendedKeys -join ' ') -- re-run with '-Platform <name>' or '-Platform all' to add)"
    }
}

Header "Installing Adapters"
$InstalledDests = @{}
foreach ($Name in $Platforms) {
    $Source = Get-AdapterSource $Name $Mode
    $Dest = Get-AdapterDest $Name

    Require-AdapterSource $Source

    if ($InstalledDests.ContainsKey($Dest)) {
        Write-Info "Skipping $Name - $(Split-Path -Leaf $Dest) already installed by another platform"
        continue
    }

    if (Test-Path -LiteralPath $Dest -PathType Leaf) {
        Write-Warn "$(Split-Path -Leaf $Dest) already exists at $Dest"
        $Answer = Read-Host "  Overwrite? [y/N]"
        if ($Answer -notmatch '^[yY]') {
            Write-Info "Skipping $(Split-Path -Leaf $Dest)"
            continue
        }
    }

    $DestDir = Split-Path -Parent $Dest
    if ($DestDir -and -not (Test-Path -LiteralPath $DestDir)) {
        New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
    }

    Copy-Item -LiteralPath $Source -Destination $Dest -Force
    Write-Ok "Installed $(Split-Path -Leaf $Dest) ($Mode) -> $Dest  [$Name]"
    Test-OversizeWarning $Name $Dest
    $InstalledDests[$Dest] = $true
}

Header "Setting Up Documents Directory"
$DocsDir = Join-Path $ProjectRoot "docs"
New-Item -ItemType Directory -Force -Path $DocsDir | Out-Null
Write-Ok "Docs directory ready: $DocsDir"

$InboxDir = Join-Path $DocsDir "inbox"
New-Item -ItemType Directory -Force -Path (Join-Path $InboxDir "processed") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $InboxDir ".gitkeep") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path (Join-Path $InboxDir "processed") ".gitkeep") | Out-Null
Write-Ok "docs/inbox/ staging directory ready"

New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "product/epics") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "design") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "architecture") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DocsDir "testing") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $DocsDir "product/epics/.gitkeep") | Out-Null
Write-Ok "Living Truth phase folders ready (product/, design/, architecture/, testing/)"

$SprintDir = Join-Path $DocsDir "sprint-v1"
foreach ($Name in @("product", "design", "architecture", "planning", "testing", "tempo/in-progress", "tempo/completed", "changes")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $SprintDir $Name) | Out-Null
}
New-Item -ItemType Directory -Force -Path (Join-Path $SprintDir "product/proposals/epics") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SprintDir "design/proposals") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SprintDir "architecture/proposals") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SprintDir "testing/proposals") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $SprintDir "product/proposals/epics/.gitkeep") | Out-Null
Write-Ok "sprint-v1 directory structure ready"

$ConfigTemplate = Join-Path $ScriptDir "prism-config.md"
$Config = Join-Path $ProjectRoot "prism-config.md"

if (-not (Test-Path -LiteralPath $Config -PathType Leaf) -and (Test-Path -LiteralPath $ConfigTemplate -PathType Leaf)) {
    Copy-Item -LiteralPath $ConfigTemplate -Destination $Config -Force
    Write-Ok "Created project config: $Config"
}

if (Test-Path -LiteralPath $Config -PathType Leaf) {
    $ProjectName = Split-Path -Leaf $ProjectRoot
    $Text = Get-Content -LiteralPath $Config -Raw
    $Text = $Text -replace 'mode:\s*"guided"', "mode: `"$Mode`""
    $Text = $Text -replace 'mode:\s*"freestyle"', "mode: `"$Mode`""
    $Text = $Text -replace 'mode:\s*"freedom"', "mode: `"$Mode`""
    $Text = $Text.Replace("__PRISM_VERSION__", $PrismVersion)
    $Text = $Text -replace 'version:\s*"[^"]*"', "version: `"$PrismVersion`""
    $Text = $Text.Replace("{{PROJECT_NAME}}", $ProjectName)
    Write-ConfigText $Config $Text
}

Header "Configuration"
if (Test-Path -LiteralPath $Config -PathType Leaf) {
    $Text = Get-Content -LiteralPath $Config -Raw
    if ($Text.Contains("{{PROJECT_NAME}}")) {
        Write-Warn "Could not auto-fill the project name. Please edit $Config manually."
        Write-Host ""
        Write-Host "  Edit: $Config"
    } else {
        Write-Ok "Project config ready: $Config"
        Write-Info "Project name defaulted to: $(Split-Path -Leaf $ProjectRoot)"
    }
    Write-Info "Optional: add a one-line project summary in $Config"
}

Install-GuidedPrecommitHook $Mode

Header "Installed Layout"
Write-Host "  PRISM home:   $ScriptDir"
Write-Host "  Framework v:  $PrismVersion"
Write-Host "  Project docs: $DocsDir"
Write-Host "  Project cfg:  $Config"
$ShownDests = @{}
foreach ($Name in $Platforms) {
    $Dest = Get-AdapterDest $Name
    if ($ShownDests.ContainsKey($Dest)) { continue }
    if (Test-Path -LiteralPath $Dest -PathType Leaf) {
        Write-Host "  Adapter:      $Dest"
        $ShownDests[$Dest] = $true
    }
}

Header "Setup Complete!"
Write-Host ""
Write-Info "Next steps:"
Write-Host "  1. Review $Config (project name has been prefilled when possible)"
Write-Host "  2. Install Python dependencies (required by PRISM tools):"
Write-Host "       pip install -r $ScriptDir\requirements.txt"
Write-Host "     (Skip if pyyaml is already available in your Python environment.)"
Write-Host "  3. Open your AI tool (Claude Code, Copilot, etc.)"
if ($Mode -eq "freedom") {
    Write-Host "  4. Just start talking - work on any phase in any order"
    Write-Host "     No commands needed. No gates. No approval."
    Write-Host "     AI detects intent and uses the right template."
    Write-Host "     NOTE: Freedom mode is permanent."
} else {
    Write-Host "  4. Type: start product"
    Write-Host "     OR: drop existing docs into $ProjectRoot\docs\inbox\ and run: import [phase]"
}
Write-Host ""
Write-Info "Style: $Mode - See $ScriptDir\README.md for style details and role-specific instructions."
Write-Info "PRISM framework files stay in $ScriptDir; project artifacts live in $ProjectRoot\docs and $Config."
Write-Info "To import existing documents: copy your-doc.md $ProjectRoot\docs\inbox\product.md -> import product"
