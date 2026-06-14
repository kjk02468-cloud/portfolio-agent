# /check 돌리고 결과를 텔레그램으로 (윈도우)
# 작업 스케줄러에서 이거 실행

Set-Location $PSScriptRoot

$out = claude -p "/check" --allowedTools "Read" "Write" "WebSearch" "WebFetch" 2>&1 | Out-String

# 로그 저장
$date = Get-Date -Format "yyyy-MM-dd_HHmm"
$out | Out-File -Append (Join-Path $PSScriptRoot "reports\run.log")

# 텔레그램 전송
& (Join-Path $PSScriptRoot "notify.ps1") $out
