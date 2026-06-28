$ErrorActionPreference = 'Stop'
$docx = (Resolve-Path (Join-Path $PSScriptRoot "..\screenshots\curamedical-rapport\Rapport_CuraMedical.docx")).Path
$wdGoToPage = 1; $wdGoToAbsolute = 1
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $false)
    $doc.Repaginate()
    $sel = $word.Selection
    foreach ($pg in @(37,38,65,66,73,74)) {
        $null = $sel.GoTo($wdGoToPage, $wdGoToAbsolute, $pg)
        $rng = $sel.Bookmarks.Item("\Page").Range
        $t = ($rng.Text -replace '[\r\n\f\a\x07\x0c]+', ' | ') -replace ' +', ' '
        Write-Output ("===== PAGE $pg =====")
        Write-Output $t.Trim()
        Write-Output ""
    }
    $doc.Close($false)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
