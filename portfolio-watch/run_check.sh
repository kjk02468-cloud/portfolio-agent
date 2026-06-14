#!/usr/bin/env bash
# /check 돌리고 결과를 텔레그램으로 (맥/리눅스/WSL)
# cron에서 이거 실행

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

OUT=$(claude -p "/check" --allowedTools "Read" "Write" "WebSearch" "WebFetch" 2>&1)

# 로그 저장
echo "=== $(date '+%Y-%m-%d %H:%M') ===" >> "$DIR/reports/run.log"
echo "$OUT" >> "$DIR/reports/run.log"

# 텔레그램 전송
"$DIR/notify.sh" "$OUT"
