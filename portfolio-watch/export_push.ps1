# report 최신화 → dashboard.json 생성 → Gist 자동 업로드 (윈도우)
# 작업 스케줄러로 주기 실행하면, URL 내용이 자동 최신화됨.
# 필요: .env 에 GITHUB_TOKEN(gist 권한), GIST_ID

Set-Location $PSScriptRoot

# .env 로드
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') { Set-Item "env:$($matches[1].Trim())" $matches[2].Trim() }
}

# 1. 에이전트로 최신 JSON 생성
$raw = claude -p "/pf_dashboard" --allowedTools "Read" "Write" 2>&1 | Out-String

# 2. JSON만 추출 (앞뒤 잡텍스트 제거)
$s = $raw.IndexOf('{'); $e = $raw.LastIndexOf('}')
if ($s -lt 0 -or $e -le $s) { Write-Host "JSON 추출 실패"; exit 1 }
$json = $raw.Substring($s, $e - $s + 1)

# 3. 검증
try { $null = $json | ConvertFrom-Json } catch { Write-Host "JSON 검증 실패"; exit 1 }
$json | Out-File "reports\dashboard.json" -Encoding utf8

# 4. Gist 업로드 (PATCH) - UTF-8 인코딩 명시
$content = $json | ConvertTo-Json -Compress   # 문자열을 JSON 이스케이프 처리
$body = "{`"files`":{`"dashboard.json`":{`"content`":$content}}}"
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
try {
  Invoke-RestMethod -Uri "https://api.github.com/gists/$($env:GIST_ID)" -Method Patch `
    -Headers @{ Authorization = "token $($env:GITHUB_TOKEN)"; "User-Agent" = "pf-agent"; Accept = "application/vnd.github+json"; "Content-Type" = "application/json; charset=utf-8" } `
    -Body $bodyBytes | Out-Null
  Write-Host "✓ 푸시 완료 $(Get-Date -Format 'MM-dd HH:mm')"
} catch {
  Write-Host "✗ 푸시 실패: $_"
}
