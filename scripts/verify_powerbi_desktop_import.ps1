# Copyright (c) NEXUS Football. Read-only local Power BI Desktop data audit.
# Usage: powershell -NoProfile -File scripts/verify_powerbi_desktop_import.ps1 -Output desktop-import.json
# Requires an open, authenticated PRODUCTION PBIP. Does NOT refresh, save, click
# Power BI, access credentials, or certify screenshots / publication.
param(
    [string]$Output = '',
    [string]$ExpectedSnapshot = ''
)

$ErrorActionPreference = 'Stop'
$result = [ordered]@{
    tool = 'NEXUS Desktop Import Readback'
    status = 'NOT_READY'
    source = 'Power BI Desktop local Analysis Services (read-only)'
    report_source_edition = 'UNCONFIRMED'
    bigquery_reconciliation = 'NOT_VERIFIED'
    desktop_visual_acceptance = 'NOT_VERIFIED'
    refresh_error_count = 'NOT_VERIFIED'
    portfolio_release = 'HOLD'
    counts = [ordered]@{}
    audit_label = $null
    max_club_win_rate_fraction = $null
    issues = @()
}

try {
    $p = @(Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" |
        Where-Object { $_.CommandLine -match 'Power BI Desktop' })
    if ($p.Count -ne 1) {
        throw "Expected one running Power BI Desktop model; found $($p.Count). Open only the production PBIP."
    }
    $match = [regex]::Match($p[0].CommandLine, '-s\s+"([^"]+)"')
    if (-not $match.Success) { throw 'Analysis Services workspace could not be located.' }
    $dataFolder = $match.Groups[1].Value
    $portFile = Join-Path $dataFolder 'msmdsrv.port.txt'
    if (-not (Test-Path $portFile)) { throw 'Desktop workspace port file is unavailable.' }
    $port = ([System.IO.File]::ReadAllText($portFile, [System.Text.Encoding]::Unicode)).Trim()
    if ($port -notmatch '^\d{2,5}$') { throw 'Invalid local Desktop model port.' }

    $apps = @(Get-AppxPackage -Name 'Microsoft.MicrosoftPowerBIDesktop')
    if ($apps.Count -ne 1) {
        throw 'Cannot safely select the installed Power BI Desktop ADOMD library.'
    }
    $lib = Join-Path $apps[0].InstallLocation 'bin\Microsoft.PowerBI.AdomdClient.dll'
    if (-not (Test-Path $lib)) { throw 'Power BI ADOMD client library is missing.' }
    Add-Type -Path $lib

    $conn = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new(
        "Data Source=localhost:$port;Connect Timeout=12"
    )
    try {
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandTimeout = 25
        $cmd.CommandText = @'
EVALUATE
ROW(
    "DimClubs", COUNTROWS ( dim_clubs ),
    "ClubPerformance", COUNTROWS ( fct_club_performance ),
    "ClubRisk", COUNTROWS ( fct_club_risk_profile ),
    "PlayerPerformance", COUNTROWS ( fct_player_performance ),
    "QualityAudits", COUNTROWS ( fct_analytics_refresh_audit ),
    "CurrentPredictions", COUNTROWS ( ml_player_market_value_current_predictions ),
    "MaxWinFraction", MAX ( fct_club_performance[win_rate] ),
    "AuditLabel", [Last Warehouse Audit Label]
)
'@
        $reader = $cmd.ExecuteReader()
        try {
            if (-not $reader.Read()) { throw 'Local DAX query returned no record.' }
            $values = @{}
            for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                $name = $reader.GetName($i) -replace '^\[|\]$', ''
                $value = $reader.GetValue($i)
                $values[$name] = if ($value -is [DBNull]) { $null } else { $value }
            }
        } finally {
            $reader.Close()
        }
    } finally {
        $conn.Dispose()
    }

    $mappings = [ordered]@{
        dim_clubs = 'DimClubs'
        fct_club_performance = 'ClubPerformance'
        fct_club_risk_profile = 'ClubRisk'
        fct_player_performance = 'PlayerPerformance'
        fct_analytics_refresh_audit = 'QualityAudits'
        ml_player_market_value_current_predictions = 'CurrentPredictions'
    }
    foreach ($name in $mappings.Keys) {
        $raw = $values[$mappings[$name]]
        $result.counts[$name] = if ($null -eq $raw) { $null } else { [long]$raw }
        if ($null -eq $result.counts[$name] -or $result.counts[$name] -lt 1) {
            $result.issues += "Model table $name is blank or empty; import may still be running."
        }
    }

    $result.audit_label = $values['AuditLabel']
    $result.max_club_win_rate_fraction = $values['MaxWinFraction']
    if ([string]::IsNullOrWhiteSpace($result.audit_label) -or
        $result.audit_label -eq 'AUDIT / NOT AVAILABLE') {
        $result.issues += 'The imported audit timestamp measure is not ready.'
    }
    if ($null -eq $result.max_club_win_rate_fraction -or
        $result.max_club_win_rate_fraction -lt 0 -or
        $result.max_club_win_rate_fraction -gt 1.00001) {
        $result.issues += 'Club win-rate fraction not verified in the [0, 1] domain.'
    }

    if ($ExpectedSnapshot) {
        if (-not (Test-Path $ExpectedSnapshot)) { throw 'Expected snapshot file not found.' }
        $expected = Get-Content $ExpectedSnapshot -Raw | ConvertFrom-Json
        foreach ($name in $mappings.Keys) {
            $item = $expected.$name
            if ($null -ne $item -and [long]$item -ne $result.counts[$name]) {
                $result.issues += "$name row count differs from the owner-provided warehouse snapshot."
            }
        }
        if (-not $result.issues.Count) { $result.bigquery_reconciliation = 'PASS_SNAPSHOT_COUNTS' }
    }
    if (-not $result.issues.Count) { $result.status = 'READY_FOR_VISUAL_QA' }
} catch {
    $result.status = 'ERROR'
    $result.issues += $_.Exception.Message
}
$rendered = $result | ConvertTo-Json -Depth 8
if ($Output) {
    $parent = Split-Path $Output -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $rendered | Set-Content -Path $Output -Encoding UTF8
}
Write-Output $rendered
if ($result.status -eq 'READY_FOR_VISUAL_QA') { exit 0 }
if ($result.status -eq 'NOT_READY') { exit 2 }
exit 3
