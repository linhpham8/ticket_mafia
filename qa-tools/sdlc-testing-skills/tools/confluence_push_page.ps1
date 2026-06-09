param(
    [Parameter(Mandatory = $true)]
    [string]$HtmlFile,

    [Parameter(Mandatory = $true)]
    [string]$PageId,

    [Parameter(Mandatory = $false)]
    [string]$Message = "Updated via testing-skills"
)

$ErrorActionPreference = "Stop"

function Get-AtlassianEnv([string]$Key) {
    foreach ($scope in "Process", "User", "Machine") {
        $value = [Environment]::GetEnvironmentVariable($Key, $scope)
        if ($value -and $value -notmatch "your-company|your_email|your.name|replace_with|YOURSPACE") {
            return $value
        }
    }

    $configPath = Join-Path $HOME ".atlassian"
    if (Test-Path $configPath) {
        foreach ($line in Get-Content $configPath -Encoding UTF8) {
            $line = $line.Trim()
            if ($line.StartsWith("#") -or -not $line.Contains("=")) { continue }
            $parts = $line -split "=", 2
            if ($parts[0].Trim() -eq $Key) {
                $candidate = $parts[1].Trim().Trim('"').Trim("'")
                if ($candidate -and $candidate -notmatch "your-company|your_email|your.name|replace_with|YOURSPACE") {
                    return $candidate
                }
            }
        }
    }
    return $null
}

$Email = Get-AtlassianEnv "ATLASSIAN_EMAIL"
if (-not $Email) { $Email = Get-AtlassianEnv "ATLASSIAN_USER_EMAIL" }
$Token = Get-AtlassianEnv "ATLASSIAN_API_TOKEN"
$BaseUrl = (Get-AtlassianEnv "ATLASSIAN_BASE_URL").TrimEnd("/")

if (-not $Email -or -not $Token -or -not $BaseUrl) {
    throw "Missing ATLASSIAN_EMAIL/ATLASSIAN_API_TOKEN/ATLASSIAN_BASE_URL"
}

$Root = Split-Path -Parent $PSScriptRoot
$HtmlPath = if ([IO.Path]::IsPathRooted($HtmlFile)) { $HtmlFile } else { Join-Path $Root $HtmlFile }
if (-not (Test-Path $HtmlPath)) {
    throw "File not found: $HtmlPath"
}

$Creds = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Email}:${Token}"))
$Headers = @{
    Authorization = "Basic $Creds"
    "Content-Type" = "application/json; charset=utf-8"
    Accept = "application/json"
}
$ApiBase = "$BaseUrl/wiki/api/v2"

$Meta = Invoke-RestMethod -Uri "$ApiBase/pages/$PageId" -Headers $Headers -Method Get
$Body = Get-Content -LiteralPath $HtmlPath -Raw -Encoding UTF8
$Payload = [ordered]@{
    id = $PageId
    status = "current"
    title = $Meta.title
    version = [ordered]@{ number = ($Meta.version.number + 1); message = $Message }
    body = [ordered]@{ representation = "storage"; value = $Body }
} | ConvertTo-Json -Depth 10 -Compress

$Response = Invoke-RestMethod -Uri "$ApiBase/pages/$PageId" -Headers $Headers -Method Put -Body ([Text.Encoding]::UTF8.GetBytes($Payload))
Write-Output ("UPDATED:" + $Response.id)
Write-Output ("VERSION:" + $Response.version.number)
Write-Output ("URL:" + $BaseUrl + "/wiki/pages/" + $Response.id)
