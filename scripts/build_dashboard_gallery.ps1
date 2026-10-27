#Requires -Version 5.1
# Generate an editorial 3x3 contact sheet from genuine Power BI captures.
# This script does not modify any of the individual screenshots.
[CmdletBinding()]
param(
 [string]$Repo='C:\ProgramData\SentinelX\workspace\football-intelligence-qa-20261019'
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$base=Join-Path $Repo 'docs\assets\screenshots'
$images=@(
 @('01_home.png','01  HOME'),
 @('02_player_performance.png','02  PLAYER PERFORMANCE'),
 @('03_player_segmentation.png','03  PLAYER SEGMENTATION'),
 @('04_club_league.png','04  CLUBS & LEAGUES'),
 @('05_transfer_success.png','05  OBSERVED 365D OUTCOMES'),
 @('06_transfer_market.png','06  TRANSFER & MARKET VALUE'),
 @('07_market_value_prediction.png','07  PLAYER VALUATION'),
 @('08_ml_reliability.png','08  MODEL RELIABILITY'),
 @('09_closing.png','09  CLOSING')
)
$width=2040;$height=1200
$bmp=New-Object System.Drawing.Bitmap($width,$height)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.ColorTranslator]::FromHtml('#071A2B'))
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$fontTitle=New-Object System.Drawing.Font('Segoe UI',25,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$fontSubtitle=New-Object System.Drawing.Font('Segoe UI',15,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$fontLabel=New-Object System.Drawing.Font('Segoe UI',16,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$white=[System.Drawing.Brushes]::White
$muted=New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#ACCAE6'))
$line=New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#347EAC'),1)
try {
 $g.DrawString('NEXUS   /   FOOTBALL INTELLIGENCE',$fontTitle,$white,50,15)
 $g.DrawString('Real Power BI Desktop screenshots | Workintech-connected report | 27 October 2026',$fontSubtitle,$muted,51,56)
 for($i=0;$i -lt $images.Count;$i++){
  $x=45+($i%3)*665
  $y=99+[Math]::Floor($i/3)*355
  $srcPath=Join-Path (Join-Path $base 'production') $images[$i][0]
  if(-not (Test-Path -LiteralPath $srcPath)){throw ('Image missing: '+$srcPath)}
  $source=[System.Drawing.Image]::FromFile($srcPath)
  try {
   $w=645;$h=317
   $ratio=[Math]::Min($w/$source.Width,$h/$source.Height)
   $drawW=[int]($source.Width*$ratio)
   $drawH=[int]($source.Height*$ratio)
   $dx=$x+[int](($w-$drawW)/2)
   $dy=$y+[int](($h-$drawH)/2)
   $g.DrawImage($source,(New-Object System.Drawing.Rectangle($dx,$dy,$drawW,$drawH)))
   $g.DrawRectangle($line,$x,$y,$w,$h)
   $g.DrawString($images[$i][1],$fontLabel,$white,$x+3,$y+322)
  } finally{$source.Dispose()}
 }
 $output=Join-Path $base 'NEXUS_Football_Page_Gallery.png'
 $bmp.Save($output,[System.Drawing.Imaging.ImageFormat]::Png)
 Write-Output ('NEXUS_NEW_SCREENSHOT_GALLERY='+$output)
 Write-Output ('PNG_RESOLUTION='+$width+'x'+$height)
} finally {
 $g.Dispose()
 $bmp.Dispose()
 $fontTitle.Dispose();$fontSubtitle.Dispose();$fontLabel.Dispose()
 $muted.Dispose();$line.Dispose()
}
