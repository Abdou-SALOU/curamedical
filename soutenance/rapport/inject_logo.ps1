# Injects the CuraMedical icon (cover + footer) into the existing .docx
# WITHOUT regenerating/overwriting content (preserves manual edits). Save-only, no PDF.
# Paths derived from $PSScriptRoot to avoid accented literals (encoding-safe under PS 5.1).
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent                 # ...\CuraMedical
$base = Join-Path $root "screenshots\curamedical-rapport"
$docx = Join-Path $base "Rapport_CuraMedical.docx"
$logo = Join-Path $base "Logo_CuraMedical.png"
if (-not (Test-Path $logo)) { throw "Logo not found: $logo" }
if (-not (Test-Path $docx)) { throw "Docx not found: $docx" }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$wdCollapseStart = 1; $wdCollapseEnd = 0; $wdAlignCenter = 1
try {
    $doc = $word.Documents.Open($docx, $false, $false)   # ConfirmConversions=false, ReadOnly=false
    $pagesBefore = $doc.ComputeStatistics(2)
    Write-Output "PAGES_BEFORE=$pagesBefore  SECTIONS=$($doc.Sections.Count)"

    # 1) Cover: icon above the title, anchored after the "RAPPORT DE PROJET" overline
    $sec1End = $doc.Sections.Item(1).Range.End
    $overIdx = 0; $idx = 0
    foreach ($p in $doc.Paragraphs) {
        $idx++
        if ($p.Range.Start -ge $sec1End) { break }
        if ($p.Range.Text.Trim().ToUpper() -eq "RAPPORT DE PROJET") { $overIdx = $idx; break }
    }
    if ($overIdx -eq 0) { Write-Output "COVER_ANCHOR_NOT_FOUND" }
    else {
        $titlePara = $doc.Paragraphs.Item($overIdx + 1)
        $titleTxt  = $titlePara.Range.Text.Trim()
        Write-Output ("COVER_ANCHOR_OK idx=$overIdx  next='" + $titleTxt + "'  nextShapes=" + $titlePara.Range.InlineShapes.Count)
        if ($titlePara.Range.InlineShapes.Count -gt 0) {
            Write-Output "COVER_ALREADY_HAS_ICON -> skip"
        } else {
            $ins = $titlePara.Range.Duplicate
            $ins.Collapse($wdCollapseStart)
            $shape = $doc.InlineShapes.AddPicture($logo, $false, $true, $ins)
            $shape.LockAspectRatio = -1
            $shape.Height = $word.CentimetersToPoints(2.3)
            $sr = $shape.Range.Duplicate; $sr.Collapse($wdCollapseEnd)
            $sr.InsertParagraphBefore()
            $shape.Range.Paragraphs.Alignment = $wdAlignCenter
            $shape.Range.ParagraphFormat.SpaceBefore = 2
            $shape.Range.ParagraphFormat.SpaceAfter  = 4
            Write-Output ("COVER_ICON_ADDED H=" + [math]::Round($shape.Height,1) + "pt W=" + [math]::Round($shape.Width,1) + "pt")
        }
    }

    # 2) Footer: small icon on the right, just before "Page"
    $footAdded = 0
    for ($s = 1; $s -le $doc.Sections.Count; $s++) {
        for ($fi = 1; $fi -le 3; $fi++) {
            $f = $doc.Sections.Item($s).Footers.Item($fi)
            if (-not $f.Exists) { continue }
            if ($f.LinkToPrevious) { continue }
            $txt = $f.Range.Text
            if ($txt -notmatch "Page") { continue }
            if ($f.Range.InlineShapes.Count -gt 0) { Write-Output "FOOTER s$s f$fi ALREADY_HAS_SHAPE -> skip"; continue }
            $fr = $f.Range.Duplicate
            $fnd = $fr.Find; $fnd.ClearFormatting(); $fnd.Forward = $true; $fnd.Text = "Page"
            $null = $fnd.Execute()
            if ($fnd.Found) {
                $fr.Collapse($wdCollapseStart)
                $sh = $doc.InlineShapes.AddPicture($logo, $false, $true, $fr)
                $sh.LockAspectRatio = -1
                $sh.Height = $word.CentimetersToPoints(0.42)
                $sh.Range.InsertAfter("  ")
                $footAdded++
                Write-Output ("FOOTER_ICON_ADDED s$s f$fi  H=" + [math]::Round($sh.Height,1) + "pt")
            }
        }
    }
    Write-Output "FOOTER_ICONS_ADDED=$footAdded"

    $doc.Repaginate()
    $pagesAfter = $doc.ComputeStatistics(2)
    Write-Output "PAGES_AFTER=$pagesAfter"
    $doc.Save()
    $doc.Close($true)
    Write-Output "SAVED_OK"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
