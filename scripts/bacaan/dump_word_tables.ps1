param([string]$Doc, [string]$Out)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
  $d = $word.Documents.Open($Doc, $false, $true)
  $lines = New-Object System.Collections.Generic.List[string]
  foreach ($t in $d.Tables) {
    foreach ($cell in $t.Range.Cells) {
      $txt = $cell.Range.Text -replace "[\r\a]+$", "" -replace "\r", " / " -replace "\t", " "
      $lines.Add([string]$cell.RowIndex + "`t" + [string]$cell.ColumnIndex + "`t" + $txt)
    }
    $lines.Add("---TABLE---")
  }
  [System.IO.File]::WriteAllLines($Out, $lines, [System.Text.UTF8Encoding]::new($false))
  $d.Close($false)
} finally { $word.Quit() }
