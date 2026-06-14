# 셋업 (원시인 버전)

## 1. 설치
```bash
npm install -g @anthropic-ai/claude-code
```
(Node.js 필요)

## 2. 폴더 통째로 홈에 둬
```
~/portfolio-watch/
```
이 안에서 클로드 코드 실행. CLAUDE.md가 자동으로 규칙 읽음.

## 3. 수동 점검 (먼저 이걸로 테스트)
```bash
cd ~/portfolio-watch
claude
> /check
```

## 4. 자동 점검 (cron, 리눅스/맥)
```bash
crontab -e
```
추가:
```
# 매주 토 09:00 킬신호 스캔
0 9 * * 6 cd ~/portfolio-watch && claude -p "/check" \
  --allowedTools "Read" "Write" "WebSearch" "WebFetch" \
  >> reports/cron.log 2>&1

# 매월 10일 09:00 월급날 매수 후보
0 9 10 * * cd ~/portfolio-watch && claude -p "월급날. manual 규칙대로 가장 신선한 1~2단계 추가매수 후보 3개만 원시인처럼." \
  --allowedTools "Read" "WebSearch" >> reports/cron.log 2>&1
```
맥/윈도우면 데스크톱 Scheduled Task GUI도 가능 (리눅스는 cron만).

## 5. 알림 (선택)
```bash
claude -p "/check" --allowedTools "Read" "Write" "WebSearch" | mail -s "포트점검" 너@메일
```
슬랙/텔레그램은 MCP 연결.

## 6. 실적일 전날 브리핑 (선택)
calendar.md 보고 cron에 종목별 추가:
```
# CRDO 실적 전날(5/31) 브리핑
0 18 31 5 * cd ~/portfolio-watch && claude -p "CRDO 내일 실적. 컨센·관전포인트·단계판정기준 원시인처럼 5줄." --allowedTools "Read" "WebSearch" >> reports/cron.log
```

## 주의
- 매 실행 = full 세션 = 토큰 소모. Pro면 빈도 조절. Max 여유.
- 가격 기반 킬신호 정확히 하려면 가격 API/데이터 MCP 붙여 (웹검색 가격은 부정확).
- **매매·자금이동은 너가 직접.** 이건 알림 비서.
- 파일 내용(보유·단계·비중)은 바뀔 때마다 너가 수정. 에이전트는 읽기만.

## 업데이트 루틴
- 단계 바뀌면 → portfolio.md 수정
- 새 종목 편입 → portfolio.md + (필요시) manual 킬신호 추가
- 매달 → calendar.md 새 일정 갱신
