param(
    [Parameter(Mandatory = $false)]
    [string]$IssueKey,

    [Parameter(Mandatory = $false)]
    [string]$CreatePayloadFile,

    [Parameter(Mandatory = $false)]
    [string]$FieldsPayloadFile,

    [Parameter(Mandatory = $false)]
    [string]$CommentText,

    [Parameter(Mandatory = $false)]
    [string]$TransitionId
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
    throw "Missing Atlassian credentials"
}

$Creds = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Email}:${Token}"))
$Headers = @{ Authorization = "Basic $Creds"; Accept = "application/json"; "Content-Type" = "application/json" }
$ApiBase = "$BaseUrl/rest/api/3"

if ($CreatePayloadFile) {
    $payload = Get-Content -LiteralPath $CreatePayloadFile -Raw -Encoding UTF8
    $response = Invoke-RestMethod -Uri "$ApiBase/issue" -Headers $Headers -Method Post -Body ([Text.Encoding]::UTF8.GetBytes($payload))
    Write-Output ("CREATED:" + $response.key)
    return
}

if (-not $IssueKey) {
    throw "IssueKey is required unless -CreatePayloadFile is used"
}

if ($FieldsPayloadFile) {
    $payload = Get-Content -LiteralPath $FieldsPayloadFile -Raw -Encoding UTF8
    Invoke-RestMethod -Uri "$ApiBase/issue/$IssueKey" -Headers $Headers -Method Put -Body ([Text.Encoding]::UTF8.GetBytes($payload)) | Out-Null
    Write-Output ("UPDATED:" + $IssueKey)
}

if ($CommentText) {
    $commentPayload = @{
        body = @{
            version = 1
            type = "doc"
            content = @(
                @{
                    type = "paragraph"
                    content = @(@{ type = "text"; text = $CommentText })
                }
            )
        }
    } | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Uri "$ApiBase/issue/$IssueKey/comment" -Headers $Headers -Method Post -Body ([Text.Encoding]::UTF8.GetBytes($commentPayload)) | Out-Null
    Write-Output ("COMMENTED:" + $IssueKey)
}

if ($TransitionId) {
    $transitionPayload = @{ transition = @{ id = $TransitionId } } | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Uri "$ApiBase/issue/$IssueKey/transitions" -Headers $Headers -Method Post -Body ([Text.Encoding]::UTF8.GetBytes($transitionPayload)) | Out-Null
    Write-Output ("TRANSITIONED:" + $IssueKey + ":" + $TransitionId)
}
