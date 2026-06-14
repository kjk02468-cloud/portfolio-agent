# setup_net_watcher.ps1
# 인터넷 감지 자동 텔레그램 발송봇을 Windows 작업 스케줄러에 등록
# 실행: 우클릭 → PowerShell로 실행 (관리자 권한 불필요)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonCmd = (Get-Command pythonw -ErrorAction SilentlyContinue)?.Source
if (-not $PythonCmd) {
    $PythonCmd = (Get-Command python -ErrorAction SilentlyContinue)?.Source
}
if (-not $PythonCmd) {
    Write-Host "❌ Python을 찾을 수 없습니다. python.org에서 설치 후 재실행하세요." -ForegroundColor Red
    exit 1
}

$TaskName   = "PortfolioNetWatcher"
$ScriptPath = Join-Path $ScriptDir "net_watcher.py"
$Action     = New-ScheduledTaskAction -Execute $PythonCmd -Argument "`"$ScriptPath`""
$Trigger    = New-ScheduledTaskTrigger -AtLogOn
$Settings   = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

# 기존 태스크 있으면 삭제 후 재등록
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Limited -Description "포트폴리오 인터넷 감지 텔레그램 봇" | Out-Null

Write-Host "✅ 작업 스케줄러 등록 완료: '$TaskName'" -ForegroundColor Green
Write-Host "   PC 로그인할 때마다 net_watcher.py 자동 시작" -ForegroundColor Cyan
Write-Host ""
Write-Host "지금 바로 시작하려면:" -ForegroundColor Yellow
Write-Host "  pythonw `"$ScriptPath`"" -ForegroundColor White
Write-Host ""
Write-Host "태스크 중지/삭제:" -ForegroundColor Yellow
Write-Host "  작업 스케줄러 열기 → '$TaskName' 찾아서 삭제" -ForegroundColor White
