<#
.SYNOPSIS
Fetch a day from the Myntra ads portal and put it in both the CSV log and the workbook.

.DESCRIPTION
The whole daily loop in one call: src/fetch_daily.py replays the captured report request for
the day, then src/Write-DailyTracker.ps1 pushes the five rows into the Daily Tracker tab.

Defaults to yesterday, which is the day the portal has finished reporting.

.EXAMPLE
powershell -File src/Get-DailyLog.ps1
powershell -File src/Get-DailyLog.ps1 -Date 2026-09-09
powershell -File src/Get-DailyLog.ps1 -CsvOnly
#>
param(
    [string] $Date = (Get-Date).AddDays(-1).ToString('yyyy-MM-dd'),
    [switch] $CsvOnly       # fetch and log, but leave the workbook alone
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

Write-Host "== fetching $Date from the portal" -ForegroundColor Cyan
& python (Join-Path $root 'src\fetch_daily.py') --date $Date
if ($LASTEXITCODE -ne 0) { throw "fetch_daily.py failed ($LASTEXITCODE) - nothing written to the workbook." }

if ($CsvOnly) {
    Write-Host "== -CsvOnly: workbook not touched" -ForegroundColor Cyan
    return
}

Write-Host "== writing $Date into the workbook" -ForegroundColor Cyan
& (Join-Path $root 'src\Write-DailyTracker.ps1') -Date $Date

Write-Host "== done. Read the day back on the Daily Action Plan tab (put $Date in B4)." -ForegroundColor Cyan
