# Read-only: is there a blank trailing cover page? Check physical page of first body paragraph.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$base = Join-Path $root "screenshots\curamedical-rapport"
$docx = Join-Path $base "Rapport_CuraMedical.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
$wdActiveEndPageNumber = 3
try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $doc.Repaginate()
    Write-Output ("TOTAL_PAGES=" + $doc.ComputeStatistics(2))
    $sec1End = $doc.Sections.Item(1).Range.End

    # last cover paragraph physical page
    $lastCoverPage = 1
    foreach ($p in $doc.Paragraphs) {
        if ($p.Range.Start -ge $sec1End) { break }
        if ($p.Range.Text.Trim().Length -gt 0 -or $p.Range.InlineShapes.Count -gt 0) {
            $lastCoverPage = $p.Range.Information($wdActiveEndPageNumber)
        }
    }
    Write-Output "LAST_COVER_CONTENT_ON_PAGE=$lastCoverPage"

    # first body paragraph physical page (section 2 start)
    $firstBody = $doc.Sections.Item(2).Range.Duplicate
    $fbStart = $firstBody.Start
    $fbPage = $doc.Range($fbStart, $fbStart).Information($wdActiveEndPageNumber)
    Write-Output "FIRST_BODY_ON_PHYSICAL_PAGE=$fbPage"

    if ($lastCoverPage -eq 1 -and $fbPage -eq 2) { Write-Output "VERDICT=OK_NO_BLANK_PAGE (cover=1 physical page, body starts p2)" }
    elseif ($fbPage -gt 2) { Write-Output "VERDICT=BLANK_COVER_PAGE_2 (body starts p$fbPage)" }
    else { Write-Output "VERDICT=CHECK lastCover=$lastCoverPage firstBody=$fbPage" }

    $doc.Close($false)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
