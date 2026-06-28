# Dump le texte rendu (longueur + apercu + nb images) de pages donnees.
$ErrorActionPreference = 'Stop'
$docx = (Resolve-Path (Join-Path $PSScriptRoot "..\screenshots\curamedical-rapport\Rapport_CuraMedical.docx")).Path
$wdGoToPage = 1; $wdGoToAbsolute = 1
$pagesToCheck = @(6,9,33,34,37,38,65,66,73,74,77,78,80)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $false)
    $doc.Repaginate()
    $sel = $word.Selection
    foreach ($pg in $pagesToCheck) {
        $null = $sel.GoTo($wdGoToPage, $wdGoToAbsolute, $pg)
        $rng = $sel.Bookmarks.Item("\Page").Range
        $txt = $rng.Text
        $imgs = $rng.InlineShapes.Count
        $clean = ($txt -replace '[\r\n\f\a\x07\x0c]', ' ') -replace '\s+', ' '
        $clean = $clean.Trim()
        $len = ($txt -replace '[\r\n\f\a\x07\x0c\s]', '').Length
        $prev = $clean
        if ($prev.Length -gt 110) { $prev = $prev.Substring(0,110) }
        Write-Output ("PAGE {0,3} | textlen={1,4} | imgs={2} | {3}" -f $pg, $len, $imgs, $prev)
    }
    $doc.Close($false)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
