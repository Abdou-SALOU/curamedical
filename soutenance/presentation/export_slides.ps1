param([int[]]$Slides = @(18))
$ErrorActionPreference = 'Stop'
$pptx = (Get-ChildItem -Path $PSScriptRoot -Filter "*.pptx" | Where-Object { $_.Name -notlike "*BAK*" } | Select-Object -First 1).FullName
$outdir = Join-Path $PSScriptRoot "_preview"
if (-not (Test-Path $outdir)) { New-Item -ItemType Directory -Path $outdir | Out-Null }

$ppt = New-Object -ComObject PowerPoint.Application
try {
    $pres = $ppt.Presentations.Open($pptx, $true, $false, $false)  # ReadOnly, Untitled, WithWindow=False
    foreach ($n in $Slides) {
        $out = Join-Path $outdir ("slide_{0:D2}.png" -f $n)
        $pres.Slides.Item($n).Export($out, "PNG", 1280, 720)
        Write-Output "EXPORorted $out"
    }
    $pres.Close()
}
finally {
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
Write-Output "DONE"
