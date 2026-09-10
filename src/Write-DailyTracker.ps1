<#
.SYNOPSIS
Push rows from data/daily_log.csv into the Daily Tracker tab of the shipped workbook.

.DESCRIPTION
The workbook carries days typed by hand that nothing in src/ can regenerate, so it is edited in
place over Excel COM rather than rebuilt. Only the five input columns are touched (D Spend,
E Impressions, F Clicks, G Orders, H Gross Rev) - everything from column I rightwards is a
formula and is left alone.

The log grid starts at row 8, five rows per day in AG1..AG5 order, dated off B5. A row is
located by arithmetic and then verified against the AG code actually sitting in column B, so a
changed layout stops the run instead of writing into the wrong group.

If the workbook is already open in the user's own Excel, that instance is reused and the file is
left open and saved - the running Excel is never killed.

.EXAMPLE
powershell -File src/Write-DailyTracker.ps1
powershell -File src/Write-DailyTracker.ps1 -Date 2026-09-09 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $Csv,
    [string] $Workbook,
    [string] $Date          # write only this day; default is every day in the CSV
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $Csv)      { $Csv      = Join-Path $root 'data\daily_log.csv' }
if (-not $Workbook) { $Workbook = Join-Path $root 'output\Myntra_Campaign_Builder.xlsx' }

if (-not (Test-Path $Csv))      { throw "No daily log at $Csv - run src/fetch_daily.py first." }
if (-not (Test-Path $Workbook)) { throw "No workbook at $Workbook." }

$rows = @(Import-Csv $Csv)
if ($Date) { $rows = @($rows | Where-Object { $_.Date -eq $Date }) }
if ($rows.Count -eq 0) { throw "Nothing to write$(if ($Date) { " for $Date" })." }

$GRP      = @('AG1', 'AG2', 'AG3', 'AG4', 'AG5')
$FIRSTROW = 8
$DAYS     = 31
# CSV column -> worksheet column on the Daily Tracker.
$COLS = [ordered]@{ Spend = 4; Impressions = 5; Clicks = 6; Orders = 7; GrossRev = 8 }

# Reuse the user's Excel if it already has this workbook open; otherwise a private headless one.
$excel = $null; $wb = $null; $ownExcel = $false; $ownBook = $false
try {
    try {
        $excel = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application')
        $wb = $excel.Workbooks | Where-Object { $_.FullName -eq (Resolve-Path $Workbook).Path }
        if ($wb) { Write-Host "Using the copy already open in Excel." }
    } catch {
        $excel = $null
    }
    if (-not $wb) {
        if (-not $excel) {
            $excel = New-Object -ComObject Excel.Application
            $excel.Visible = $false
            $excel.DisplayAlerts = $false
            $ownExcel = $true
        }
        $wb = $excel.Workbooks.Open((Resolve-Path $Workbook).Path)
        $ownBook = $true
    }

    $ws = $wb.Worksheets.Item('Daily Tracker')
    # B5, the start date the dates fill from. Value2 hands back the OLE serial, not a date.
    $start = [datetime]::FromOADate([double]$ws.Cells.Item(5, 2).Value2).Date
    Write-Host ("Daily Tracker starts {0:dd-MMM-yyyy}; {1} day slots." -f $start, $DAYS)

    $written = 0; $skipped = @()
    foreach ($r in $rows) {
        $d = [datetime]::ParseExact($r.Date, 'yyyy-MM-dd', $null)
        $dayIndex = ($d - $start).Days
        $agIndex = [array]::IndexOf($GRP, $r.AG)
        if ($agIndex -lt 0)      { $skipped += "$($r.Date) $($r.AG): not one of $($GRP -join ',')"; continue }
        if ($dayIndex -lt 0 -or $dayIndex -ge $DAYS) {
            $skipped += ("{0} {1}: outside the {2}-day window that starts {3:dd-MMM-yyyy}" -f $r.Date, $r.AG, $DAYS, $start)
            continue
        }

        $row = $FIRSTROW + ($dayIndex * $GRP.Count) + $agIndex
        $found = [string]$ws.Cells.Item($row, 2).Value2
        if ($found -ne $r.AG) {
            throw "Row $row holds '$found', expected '$($r.AG)'. The Daily Tracker layout has moved - stopping before anything is written wrong."
        }

        if ($PSCmdlet.ShouldProcess("row $row ($($r.Date) $($r.AG))", "write spend/impr/clicks/orders/rev")) {
            foreach ($k in $COLS.Keys) {
                $v = $r.$k
                if ($null -ne $v -and $v -ne '') { $ws.Cells.Item($row, $COLS[$k]).Value2 = [double]$v }
            }
            $written++
        }
        Write-Host ("  row {0,-4} {1} {2,-4} spend {3,8} impr {4,8} clicks {5,6} orders {6,6} rev {7,9}" -f `
            $row, $r.Date, $r.AG, $r.Spend, $r.Impressions, $r.Clicks, $r.Orders, $r.GrossRev)
    }

    foreach ($s in $skipped) { Write-Warning $s }

    if ($written -gt 0 -and $PSCmdlet.ShouldProcess($Workbook, 'save')) {
        $wb.Save()
        Write-Host "Wrote $written rows and saved $Workbook."
    } else {
        Write-Host "Nothing written."
    }
} finally {
    if ($wb -and $ownBook) { $wb.Close($true) }
    if ($excel -and $ownExcel) {
        $excel.Quit()
        # Only ever the headless instance this script started - never a window the user has open.
        Get-Process EXCEL -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowTitle -eq '' -and $_.StartTime -gt (Get-Date).AddMinutes(-10) } |
            Stop-Process -Force -ErrorAction SilentlyContinue
    }
    [GC]::Collect()
}
