param(
    [Parameter(Mandatory = $true)]
    [string]$MdFile,

    [Parameter(Mandatory = $true)]
    [string]$ParentPageId,

    [Parameter(Mandatory = $false)]
    [string]$Title = "",

    [Parameter(Mandatory = $false)]
    [string]$Message = "Auto-push",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$module     = Join-Path $scriptDir "confluence_md.py"

if (-not (Test-Path -LiteralPath $module)) {
    throw "Missing: $module"
}

$python = $null
foreach ($candidate in @("python", "python3")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch "WindowsApps") {
        $python = $cmd.Source; break
    }
}
if (-not $python) { throw "Python not found." }

$pyArgs = @($module, "--file", $MdFile, "--parent-id", $ParentPageId, "--message", $Message)
if ($Title)   { $pyArgs += @("--title", $Title) }
if ($DryRun)  { $pyArgs += "--dry-run" }

& $python @pyArgs
exit $LASTEXITCODE
