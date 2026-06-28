# Met a jour les champs + repagine, detecte les pages VIDES (sans texte ni image), sauvegarde. PAS de PDF.
$ErrorActionPreference = 'Stop'
$docx = (Resolve-Path (Join-Path $PSScriptRoot "..\screenshots\curamedical-rapport\Rapport_CuraMedical.docx")).Path
Write-Output "DOCX=$docx"

$wdGoToPage = 1; $wdGoToAbsolute = 1

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $false)
    foreach ($pass in 1..2) {
        foreach ($toc in $doc.TablesOfContents) { try { $toc.Update() } catch {} }
        foreach ($tof in $doc.TablesOfFigures)  { try { $tof.Update() } catch {} }
        foreach ($story in $doc.StoryRanges) { try { $null = $story.Fields.Update() } catch {} }
    }
    $doc.Repaginate()
    $pages = $doc.ComputeStatistics(2)
    $words = $doc.ComputeStatistics(0)
    Write-Output "PAGES=$pages"
    Write-Output "WORDS=$words"

    # Detection des pages vides
    $sel = $word.Selection
    for ($pg = 1; $pg -le $pages; $pg++) {
        $null = $sel.GoTo($wdGoToPage, $wdGoToAbsolute, $pg)
        $rng = $sel.Bookmarks.Item("\Page").Range
        $txt = $rng.Text
        if ($null -ne $txt) {
            $clean = $txt -replace '[\r\n\f\a\t\x07\x0c\s]', ''
        } else { $clean = '' }
        $imgs = $rng.InlineShapes.Count
        $shp = 0
        try { $shp = $rng.ShapeRange.Count } catch { $shp = 0 }
        if ($clean.Length -eq 0 -and $imgs -eq 0 -and $shp -eq 0) {
            Write-Output ("BLANK_PAGE={0}" -f $pg)
        }
        elseif ($clean.Length -lt 40 -and $imgs -eq 0 -and $shp -eq 0) {
            $preview = ($txt -replace '[\r\n\f\a\x07\x0c]', ' ').Trim()
            if ($preview.Length -gt 50) { $preview = $preview.Substring(0,50) }
            Write-Output ("SPARSE_PAGE={0} len={1} :: {2}" -f $pg, $clean.Length, $preview)
        }
    }

    $doc.Save()
    $doc.Close($true)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
