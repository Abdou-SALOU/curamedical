# Met a jour les champs (TDM, figures, tableaux, pages) + repagine, puis sauvegarde.
# PAS d'export PDF (bloque dans cet environnement). Livrable = .docx
$ErrorActionPreference = 'Stop'
# Resolution via $PSScriptRoot (valeur runtime) pour eviter tout souci d'accents dans le chemin.
$docx = (Resolve-Path (Join-Path $PSScriptRoot "..\screenshots\curamedical-rapport\Rapport_CuraMedical.docx")).Path
Write-Output "DOCX=$docx"

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
    $pages = $doc.ComputeStatistics(2)   # wdStatisticPages
    $words = $doc.ComputeStatistics(0)   # wdStatisticWords
    Write-Output "PAGES=$pages"
    Write-Output "WORDS=$words"
    $doc.Save()
    $doc.Close($true)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
