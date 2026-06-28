# Met à jour les champs (TDM, figures, tableaux, pages), exporte le PDF et compte les pages.
$ErrorActionPreference = 'Stop'
$base = "c:\2CI-ISI\S2\Projet en Systèmes Informatiques\MedPredict\CuraMedical\soutenance\screenshots\curamedical-rapport"
$docx = Join-Path $base "Rapport_CuraMedical.docx"
$pdf  = Join-Path $base "Rapport_CuraMedical.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $false)
    # Mettre à jour deux fois pour stabiliser les numéros de page de la TDM
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
    $doc.ExportAsFixedFormat($pdf, 17)   # wdExportFormatPDF
    $doc.Save()
    $doc.Close($true)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
