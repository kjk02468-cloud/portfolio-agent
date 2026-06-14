#!/usr/bin/env bash
# report 최신화 → dashboard.json → Gist 자동 업로드 (맥/리눅스/WSL)
# cron으로 주기 실행. 필요: .env 에 GITHUB_TOKEN, GIST_ID

DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
set -a; source .env; set +a

raw=$(claude -p "/export" --allowedTools "Read" "Write" 2>&1)

# JSON 추출 + 검증 (python 사용)
json=$(printf '%s' "$raw" | python3 -c "
import sys,json
t=sys.stdin.read(); i=t.find('{'); j=t.rfind('}')
s=t[i:j+1]; json.loads(s); print(s)
") || { echo 'JSON 추출/검증 실패'; exit 1; }

printf '%s' "$json" > reports/dashboard.json

# Gist 업로드 (payload는 python으로 안전하게 이스케이프)
payload=$(python3 -c "import json;c=open('reports/dashboard.json',encoding='utf-8').read();print(json.dumps({'files':{'dashboard.json':{'content':c}}}))")

curl -s -X PATCH "https://api.github.com/gists/$GIST_ID" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "User-Agent: pf-agent" \
  -H "Accept: application/vnd.github+json" \
  -d "$payload" > /dev/null \
  && echo "✓ 푸시 완료 $(date '+%m-%d %H:%M')" || echo "✗ 푸시 실패"
