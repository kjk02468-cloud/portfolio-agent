# PostToolUse 훅: reports/YYYY-MM-DD.md 저장 시 dashboard.json → Gist 자동 푸시
param()
$raw = [System.Console]::In.ReadToEnd()
try { $d = $raw | ConvertFrom-Json; $fp = $d.tool_input.file_path } catch { exit 0 }

# reports/날짜.md 파일일 때만 실행
if (-not ($fp -match 'reports[\\/]\d{4}-\d{2}-\d{2}\.md$')) { exit 0 }

Set-Location $PSScriptRoot
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') { Set-Item "env:$($matches[1].Trim())" $matches[2].Trim() }
}

$json = Get-Content "reports\dashboard.json" -Raw -Encoding UTF8
$bodyObj = @{ files = @{ "dashboard.json" = @{ content = $json } } }
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes(($bodyObj | ConvertTo-Json -Depth 10 -Compress))

try {
  Invoke-RestMethod `
    -Uri "https://api.github.com/gists/$($env:GIST_ID)" `
    -Method Patch `
    -Headers @{
      Authorization  = "token $($env:GITHUB_TOKEN)"
      "User-Agent"   = "pf-agent"
      Accept         = "application/vnd.github+json"
      "Content-Type" = "application/json; charset=utf-8"
    } `
    -Body $bodyBytes | Out-Null
  Write-Host "✓ Gist pushed $(Get-Date -Format 'MM-dd HH:mm')"
} catch {
  Write-Host "✗ Push failed: $_"
  exit 1
}
