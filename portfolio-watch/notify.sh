#!/usr/bin/env bash
# 텔레그램으로 메시지 전송 (맥/리눅스/WSL)
# 사용: ./notify.sh "보낼 메시지"

DIR="$(cd "$(dirname "$0")" && pwd)"
set -a; source "$DIR/.env"; set +a

MSG="${1:-(빈 메시지)}"
# 텔레그램 4096자 제한
MSG="${MSG:0:4000}"

curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
  -d chat_id="${TG_CHAT}" \
  --data-urlencode text="$MSG" > /dev/null \
  && echo "전송 완료" || echo "전송 실패"
