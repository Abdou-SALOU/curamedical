# Verifie qu'aucun titre n'est orphelin (dernier element rendu de sa page) et controle le cas A4.
$ErrorActionPreference = 'Stop'
$docx = (Resolve-Path (Join-Path $PSScriptRoot "..\screenshots\curamedical-rapport\Rapport_CuraMedical.docx")).Path
$wdActiveEndPageNumber = 3

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $false)
    $doc.Repaginate()
    $paras = $doc.Paragraphs
    $n = $paras.Count
    # Pre-collecte : page de FIN du paragraphe, et page de DEBUT (range collapse start)
    $arr = New-Object System.Collections.ArrayList
    for ($i = 1; $i -le $n; $i++) {
        $p = $paras.Item($i)
        $style = [string]$p.Range.Style.NameLocal
        $txt = ($p.Range.Text -replace '[\r\n\f\a\x07\x0c]', ' ').Trim()
        $endPg = $p.Range.Information($wdActiveEndPageNumber)
        $sr = $p.Range.Duplicate; $sr.Collapse(1)   # wdCollapseStart=1
        $startPg = $sr.Information($wdActiveEndPageNumber)
        [void]$arr.Add([pscustomobject]@{ Idx=$i; Style=$style; Txt=$txt; EndPage=$endPg; StartPage=$startPg })
    }
    # Vrai orphelin : un titre dont le paragraphe IMMEDIATEMENT suivant DEBUTE sur une page > la page de fin du titre
    $orphans = 0
    for ($i = 0; $i -lt $arr.Count - 1; $i++) {
        $cur = $arr[$i]
        if ($cur.Style -like 'Titre*' -or $cur.Style -like 'Heading*') {
            $nx = $arr[$i + 1]
            if ($nx.StartPage -gt $cur.EndPage) {
                $orphans++
                Write-Output ("ORPHELIN p{0}: [{1}] {2}" -f $cur.EndPage, $cur.Style, ($cur.Txt.Substring(0, [Math]::Min(55,$cur.Txt.Length))))
            }
        }
    }
    Write-Output ("ORPHELINS_TOTAL={0}" -f $orphans)
    # Cas A4
    foreach ($row in $arr) {
        if ($row.Txt -like 'A4 : Configuration SMTP*') { Write-Output ("A4_TITRE page={0}" -f $row.Page) }
    }
    $doc.Close($false)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
