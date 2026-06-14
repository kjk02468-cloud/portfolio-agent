# 텔레그램으로 메시지 전송 (윈도우)
# 사용: ./notify.ps1 "보낼 메시지"

# .env 로드
$envPath = Join-Path $PSScriptRoot ".env"
Get-Content $envPath | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') {
    Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
  }
}

$token = $env:TG_TOKEN
$chat  = $env:TG_CHAT
$msg   = $args[0]
if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "(빈 메시지)" }

# 텔레그램 4096자 제한
if ($msg.Length -gt 4000) { $msg = $msg.Substring(0,4000) }

$uri = "https://api.telegram.org/bot$token/sendMessage"
try {
  Invoke-RestMethod -Uri $uri -Method Post -Body @{ chat_id = $chat; text = $msg } | Out-Null
  Write-Host "전송 완료"
} catch {
  Write-Host "전송 실패: $_"
}
