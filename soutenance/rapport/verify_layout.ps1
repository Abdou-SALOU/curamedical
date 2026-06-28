# Read-only layout check: total pages, cover spans 1 page?, cover/footer inline shapes.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$base = Join-Path $root "screenshots\curamedical-rapport"
$fname = if ($args.Count -ge 1) { $args[0] } else { "Rapport_CuraMedical.docx" }
$docx = Join-Path $base $fname
Write-Output "FILE=$fname"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$wdCollapseEnd = 0
$wdActiveEndPageNumber = 3
try {
    $doc = $word.Documents.Open($docx, $false, $true)   # ReadOnly = true
    $doc.Repaginate()
    $total = $doc.ComputeStatistics(2)
    Write-Output "TOTAL_PAGES=$total"

    $sec1 = $doc.Sections.Item(1)
    $sec1End = $sec1.Range.End
    $cend = $sec1.Range.Duplicate; $cend.Collapse($wdCollapseEnd)
    $coverEndPage = $cend.Information($wdActiveEndPageNumber)
    Write-Output "COVER_ENDS_ON_PAGE=$coverEndPage"

    $coverShapes = 0
    foreach ($ish in $doc.InlineShapes) {
        if ($ish.Range.Start -lt $sec1End) {
            $coverShapes++
            Write-Output ("  cover shape #$coverShapes  H=" + [math]::Round($ish.Height,1) + "pt  W=" + [math]::Round($ish.Width,1) + "pt")
        }
    }
    Write-Output "COVER_INLINE_SHAPES=$coverShapes"

    $bf = $doc.Sections.Item(2).Footers.Item(1)
    Write-Output ("BODY_FOOTER_SHAPES=" + $bf.Range.InlineShapes.Count + "  hasPageField=" + ($bf.Range.Text -match 'Page'))
    Write-Output ("BODY_FOOTER_TEXT='" + ($bf.Range.Text.Trim() -replace '[\r\n\x07]',' ') + "'")

    $doc.Close($false)   # do not save
    Write-Output "CHECK_OK"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
