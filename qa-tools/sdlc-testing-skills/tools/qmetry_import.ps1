param(
    [Parameter(Mandatory = $true)]
    [string]$TsvFile,

    [Parameter(Mandatory = $false)]
    [string]$ConfigFile = "",

    [Parameter(Mandatory = $false)]
    [switch]$DryRun,

    [Parameter(Mandatory = $false)]
    [switch]$ContinueOnError,

    [Parameter(Mandatory = $false)]
    [string]$FolderPath = "",

    [Parameter(Mandatory = $false)]
    [string]$FolderId = "",

    [Parameter(Mandatory = $false)]
    [switch]$CreateFolder,

    [Parameter(Mandatory = $false)]
    [int]$MaxRows = 0
)

$ErrorActionPreference = "Stop"

Write-Output "Usage for a specific QMetry folder:"
Write-Output "  1) In QTM4J Test Case folders, right-click the folder and choose Copy Folder Id."
Write-Output "  2) Run with -FolderId <copied-folder-id>. Example: .\qmetry_import.ps1 -TsvFile <file.tsv> -FolderId <folderId>"
Write-Output "  3) -FolderPath can try find/create by folder name, but QMetry Cloud may not expose folder APIs for every tenant."

function Get-TrimmedValue {
    param([hashtable]$Row, [string]$Key)
    if ([string]::IsNullOrWhiteSpace($Key)) { return "" }
    if ($Row.ContainsKey($Key) -and $null -ne $Row[$Key]) { return [string]$Row[$Key] }
    return ""
}

function Convert-TsvRowToPayload {
    param([hashtable]$Row, [pscustomobject]$Config, [string]$ResolvedFolderId = "")

    $summary = (Get-TrimmedValue -Row $Row -Key $Config.mapping.summary).Trim()
    if ([string]::IsNullOrWhiteSpace($summary)) { throw "Missing summary field in row. Check mapping.summary" }

    $precondition = (Get-TrimmedValue -Row $Row -Key $Config.mapping.precondition).Trim()
    $testData     = (Get-TrimmedValue -Row $Row -Key $Config.mapping.testData).Trim()
    $stepsRaw     = (Get-TrimmedValue -Row $Row -Key $Config.mapping.steps).Trim()
    $expected     = (Get-TrimmedValue -Row $Row -Key $Config.mapping.expectedResult).Trim()
    $priority     = (Get-TrimmedValue -Row $Row -Key $Config.mapping.priority).Trim()
    $labelsRaw    = (Get-TrimmedValue -Row $Row -Key $Config.mapping.labels).Trim()

    $labels = @()
    if (-not [string]::IsNullOrWhiteSpace($labelsRaw)) {
        $labels = $labelsRaw -split "[;,]" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    }

    $sprint = ""
    if ($Config.mapping.sprint -and -not [string]::IsNullOrWhiteSpace([string]$Config.mapping.sprint)) {
        $sprint = (Get-TrimmedValue -Row $Row -Key $Config.mapping.sprint).Trim()
    }
    if ([string]::IsNullOrWhiteSpace($sprint) -and $Config.defaults.sprint) {
        $sprint = [string]$Config.defaults.sprint
    }

    # Build TC create payload (steps added separately via /teststeps endpoint)
    $payload = [ordered]@{
        projectId    = [int]$Config.project.jiraProjectId
        summary      = $summary
        precondition = $precondition
    }

    $priorityValue = Resolve-PriorityValue -Priority $priority -Config $Config
    if ($priorityValue) { $payload.priority = $priorityValue }
    # QMetry uses "story" (string, first value) for Story Linkages — "labels" array causes 400
    if ($labels.Count -gt 0)                        { $payload.story  = $labels[0] }
    if (-not [string]::IsNullOrWhiteSpace($sprint)) { $payload.sprint = $sprint }
    if ($Config.defaults.moduleId) { $payload.moduleId = $Config.defaults.moduleId }
    if ($ResolvedFolderId) { $payload.folderId = $ResolvedFolderId }
    elseif ($Config.defaults.folderId) { $payload.folderId = $Config.defaults.folderId }

    # Build step objects — split on " | " to create one step per action
    $stepActions = if ([string]::IsNullOrWhiteSpace($stepsRaw)) {
        @("Execute test")
    } else {
        $stepsRaw -split "\s*\|\s*" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    }
    $stepObjects = for ($i = 0; $i -lt $stepActions.Count; $i++) {
        $stepObj = [ordered]@{ stepDetails = $stepActions[$i] }
        if ($i -eq 0)                              { $stepObj.testData       = $testData }
        if ($i -eq $stepActions.Count - 1)         { $stepObj.expectedResult = $expected }
        $stepObj
    }

    return [pscustomobject]@{ payload = $payload; steps = @($stepObjects) }
}

function Resolve-PriorityValue {
    param([string]$Priority, [pscustomobject]$Config)

    if ([string]::IsNullOrWhiteSpace($Priority)) { return $null }
    $priorityValue = $Priority.Trim()

    if ($Config.priorityMap) {
        foreach ($property in $Config.priorityMap.PSObject.Properties) {
            if ($property.Name.Equals($priorityValue, [StringComparison]::OrdinalIgnoreCase)) {
                return [string]$property.Value
            }
        }
    }

    $normalized = $priorityValue.ToLowerInvariant()
    switch ($normalized) {
        "critical" { return "Critical" }
        "high"     { return "High" }
        "medium"   { return "Medium" }
        "low"      { return "Low" }
        default {
            Write-Warning "Priority '$priorityValue' is not configured in priorityMap. Skipping priority."
            return $null
        }
    }
}

function Invoke-QMetryRequest {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers,
        [object]$Body = $null
    )

    $params = @{
        Uri         = $Url
        Method      = $Method
        Headers     = $Headers
        ContentType = "application/json; charset=utf-8"
    }
    if ($null -ne $Body) {
        $json = $Body | ConvertTo-Json -Depth 20
        $params.Body = [Text.Encoding]::UTF8.GetBytes($json)
    }
    return Invoke-RestMethod @params
}

function Get-ObjectId {
    param([object]$Value)
    if ($null -eq $Value) { return "" }
    foreach ($name in @("id", "folderId", "moduleId", "key")) {
        if ($Value.PSObject.Properties[$name] -and $Value.$name) { return [string]$Value.$name }
    }
    return ""
}

function Find-FolderByName {
    param(
        [array]$Folders,
        [string]$Name,
        [string]$ParentId = ""
    )

    foreach ($folder in $Folders) {
        $folderName = if ($folder.name) { [string]$folder.name } elseif ($folder.folderName) { [string]$folder.folderName } else { "" }
        $folderParentId = if ($folder.parentId) { [string]$folder.parentId } elseif ($folder.parentFolderId) { [string]$folder.parentFolderId } elseif ($folder.parentFolderID) { [string]$folder.parentFolderID } else { "" }
        if ($folderName.Equals($Name, [StringComparison]::OrdinalIgnoreCase) -and ($ParentId -eq "" -or $folderParentId -eq $ParentId)) {
            return $folder
        }
    }
    return $null
}

function Get-QMetryFolders {
    param([pscustomobject]$Config, [hashtable]$Headers)

    $base = $Config.apiBaseUrl.TrimEnd("/")
    $projectId = [int]$Config.project.jiraProjectId
    $candidatePaths = @(
        "/rest/api/latest/testcases/folders?projectId=$projectId",
        "/rest/api/latest/folders?projectId=$projectId&entityType=TEST_CASE",
        "/rest/api/latest/testcase-folders?projectId=$projectId"
    )

    foreach ($path in $candidatePaths) {
        $url = $base + $path
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -Headers $Headers -ContentType "application/json; charset=utf-8"
            $items = @()
            if ($response.data) { $items = @($response.data) }
            elseif ($response.folders) { $items = @($response.folders) }
            elseif ($response -is [array]) { $items = @($response) }
            if ($items.Count -gt 0) { return @(Expand-QMetryFolders -Folders $items) }
        } catch {
            continue
        }
    }

    return @()
}

function Expand-QMetryFolders {
    param([array]$Folders, [string]$ParentId = "")

    $expanded = @()
    foreach ($folder in $Folders) {
        if ($ParentId -and -not $folder.PSObject.Properties["parentId"]) {
            $folder | Add-Member -NotePropertyName "parentId" -NotePropertyValue $ParentId -Force
        }
        $expanded += $folder
        $id = Get-ObjectId -Value $folder
        foreach ($childrenName in @("children", "childFolders", "folders")) {
            if ($folder.PSObject.Properties[$childrenName] -and $folder.$childrenName) {
                $expanded += @(Expand-QMetryFolders -Folders @($folder.$childrenName) -ParentId $id)
            }
        }
    }
    return $expanded
}

function New-QMetryFolder {
    param(
        [pscustomobject]$Config,
        [hashtable]$Headers,
        [string]$Name,
        [string]$ParentId = ""
    )

    $base = $Config.apiBaseUrl.TrimEnd("/")
    $projectId = [int]$Config.project.jiraProjectId
    $payloads = @()
    $payload1 = [ordered]@{ projectId = $projectId; name = $Name }
    $payload2 = [ordered]@{ projectId = $projectId; folderName = $Name }
    $payload3 = [ordered]@{ projectId = $projectId; name = $Name; entityType = "TEST_CASE" }
    if ($ParentId) {
        $payload1.parentId = $ParentId
        $payload2.parentFolderId = $ParentId
        $payload3.parentId = $ParentId
    }
    $payloads += $payload1
    $payloads += $payload2
    $payloads += $payload3

    $candidatePaths = @(
        "/rest/api/latest/testcases/folders",
        "/rest/api/latest/folders",
        "/rest/api/latest/testcase-folders"
    )

    foreach ($path in $candidatePaths) {
        $url = $base + $path
        foreach ($payload in $payloads) {
            try {
                $created = Invoke-QMetryRequest -Method Post -Url $url -Headers $Headers -Body $payload
                $id = Get-ObjectId -Value $created
                if ($id) { return $id }
            } catch {
                continue
            }
        }
    }

    throw "Could not create QMetry folder '$Name'. Check QMetry folder API endpoint/permissions."
}

function Resolve-QMetryFolderPath {
    param(
        [pscustomobject]$Config,
        [hashtable]$Headers,
        [string]$Path,
        [switch]$Create
    )

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $parts = $Path -split "[\\/]" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    if ($parts.Count -eq 0) { return "" }

    $folders = @(Get-QMetryFolders -Config $Config -Headers $Headers)
    $parentId = ""
    foreach ($part in $parts) {
        $match = Find-FolderByName -Folders $folders -Name $part -ParentId $parentId
        if ($match) {
            $parentId = Get-ObjectId -Value $match
            continue
        }
        if (-not $Create) { throw "QMetry folder '$part' not found in path '$Path'." }
        Write-Output "Creating QMetry folder: $part"
        $parentId = New-QMetryFolder -Config $Config -Headers $Headers -Name $part -ParentId $parentId
        $folders = @(Get-QMetryFolders -Config $Config -Headers $Headers)
    }

    return $parentId
}

$Root = Split-Path -Parent $PSScriptRoot
$ResolvedTsv = if ([IO.Path]::IsPathRooted($TsvFile)) { $TsvFile } else { Join-Path $Root $TsvFile }
if ([string]::IsNullOrWhiteSpace($ConfigFile)) {
    $ResolvedConfig = Join-Path $Root "tools\qmetry-config.json"
    if (-not (Test-Path -LiteralPath $ResolvedConfig)) {
        $ResolvedConfig = Join-Path $Root "tools\qmetry-config.sample.json"
    }
} else {
    $ResolvedConfig = if ([IO.Path]::IsPathRooted($ConfigFile)) { $ConfigFile } else { Join-Path $Root $ConfigFile }
}
if (-not (Test-Path -LiteralPath $ResolvedTsv)) { throw "TSV file not found: $ResolvedTsv" }
if (-not (Test-Path -LiteralPath $ResolvedConfig)) { throw "Config file not found: $ResolvedConfig" }
Write-Output "Config: $ResolvedConfig"

$config = Get-Content -LiteralPath $ResolvedConfig -Raw -Encoding UTF8 | ConvertFrom-Json
$token = [Environment]::GetEnvironmentVariable($config.auth.tokenEnvVar, "Process")
if (-not $token) { $token = [Environment]::GetEnvironmentVariable($config.auth.tokenEnvVar, "User") }
if (-not $token) {
    $EnvFile = Join-Path $Root ".env"
    if (Test-Path -LiteralPath $EnvFile) {
        $tokenLine = Get-Content -LiteralPath $EnvFile -Encoding UTF8 |
            Where-Object { $_ -match ("^\s*" + [regex]::Escape([string]$config.auth.tokenEnvVar) + "\s*=") } |
            Select-Object -First 1
        if ($tokenLine) {
            $token = ($tokenLine -split "=", 2)[1].Trim().Trim('"').Trim("'")
            [Environment]::SetEnvironmentVariable($config.auth.tokenEnvVar, $token, "Process")
        }
    }
}
if (-not $DryRun -and [string]::IsNullOrWhiteSpace($token)) { throw "Missing token env var: $($config.auth.tokenEnvVar)" }

$endpoint = ($config.apiBaseUrl.TrimEnd("/")) + "/" + ($config.createTestCasePath.TrimStart("/"))
$headers = @{ Accept = "application/json" }
if (-not $DryRun) {
    $headerName = if ($config.auth.headerName) { [string]$config.auth.headerName } else { "Authorization" }
    $scheme = [string]$config.auth.scheme
    $headers[$headerName] = if ([string]::IsNullOrWhiteSpace($scheme) -or $scheme -eq "Raw") { $token } else { "$scheme $token" }
}

$rows = Import-Csv -LiteralPath $ResolvedTsv -Delimiter "`t" -Encoding UTF8
if ($MaxRows -gt 0) {
    $rows = @($rows | Select-Object -First $MaxRows)
}

$resolvedFolderId = ""
if (-not [string]::IsNullOrWhiteSpace($FolderId)) {
    $resolvedFolderId = $FolderId.Trim()
} elseif (-not [string]::IsNullOrWhiteSpace($FolderPath)) {
    if ($DryRun) {
        $resolvedFolderId = "__DRY_RUN_FOLDER__"
        Write-Output "FolderPath: $FolderPath"
        Write-Output "FolderMode: DRY_RUN_FIND_OR_CREATE"
    } else {
        $resolvedFolderId = Resolve-QMetryFolderPath -Config $config -Headers $headers -Path $FolderPath -Create
        Write-Output "FolderPath: $FolderPath"
        Write-Output "FolderId: $resolvedFolderId"
    }
}

$report = @()
$success = 0
$failed = 0
$skipped = 0

foreach ($csvRow in $rows) {
    $row = @{}
    foreach ($property in $csvRow.PSObject.Properties) { $row[$property.Name] = $property.Value }
    $summaryKey = [string]$config.mapping.summary
    $summaryValue = if ($row.ContainsKey($summaryKey)) { ([string]$row[$summaryKey]).Trim() } else { "" }
    if ([string]::IsNullOrWhiteSpace($summaryValue)) {
        $skipped++
        $report += [pscustomobject]@{ summary = ""; result = "skipped"; reason = "empty summary" }
        continue
    }

    try {
        $converted = Convert-TsvRowToPayload -Row $row -Config $config -ResolvedFolderId $resolvedFolderId
        $payload   = $converted.payload
        $steps     = $converted.steps
        $jsonBody  = $payload | ConvertTo-Json -Depth 20

        if ($DryRun) {
            $success++
            $report += [pscustomobject]@{ summary = $payload.summary; result = "dry-run"; endpoint = $endpoint; priority = $payload.priority; folderId = $payload.folderId; stepCount = $steps.Count }
            continue
        }

        $result    = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($jsonBody))
        $createdId = if ($result.id) { [string]$result.id } elseif ($result.key) { [string]$result.key } else { "" }

        # POST steps separately — QMetry requires stepDetails field via /versions/1/teststeps
        if ($createdId -and $steps.Count -gt 0) {
            $stepsUrl  = ($config.apiBaseUrl.TrimEnd("/")) + "/rest/api/latest/testcases/$createdId/versions/1/teststeps"
            $stepsJson = $steps | ConvertTo-Json -Depth 10
            if ($stepsJson -notmatch '^\s*\[') { $stepsJson = "[$stepsJson]" }
            Invoke-RestMethod -Uri $stepsUrl -Method Post -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($stepsJson)) | Out-Null
        }

        $success++
        $report += [pscustomobject]@{ summary = $payload.summary; result = "created"; id = $createdId; priority = $payload.priority; folderId = $payload.folderId; stepCount = $steps.Count }
    } catch {
        $failed++
        $report += [pscustomobject]@{ summary = $summaryValue; result = "failed"; error = $_.Exception.Message }
        if (-not $ContinueOnError) { break }
    }
}

$ReportDir = Join-Path $Root "testing-output\qmetry"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ReportFile = Join-Path $ReportDir ("qmetry-import-report-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".json")
$report | ConvertTo-Json -Depth 10 | Out-File -LiteralPath $ReportFile -Encoding UTF8

Write-Output ("TOTAL:" + $rows.Count)
Write-Output ("SUCCESS:" + $success)
Write-Output ("FAILED:" + $failed)
Write-Output ("SKIPPED:" + $skipped)
Write-Output ("REPORT:" + $ReportFile)
if ($DryRun) { Write-Output "MODE:DRY_RUN" }
