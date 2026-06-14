# 텔레그램 봇 켜기 (양방향)

폰에서 명령 → 봇이 claude 돌려 → 답장. PC 켜져 있어야 함.

## 0. 준비
- `.env`에 TG_TOKEN·TG_CHAT 채워져 있어야 함 (ALERTS.md 참고)
- `claude` 로그인 돼있어야 함 (한번 `claude` 실행해서 확인)
- 파이썬 필요

## 1. 파이썬 설치 (없으면)
- [python.org](https://python.org) → 3.12+ 설치 (설치 시 "Add to PATH" 체크!)
- 또는: `winget install Python.Python.3.12`
- 확인: 새 터미널서 `python --version`

## 2. 봇 실행
```powershell
cd C:\Users\너\portfolio-watch
python telegram_bot.py
```
"봇 실행 중..." 뜨면 OK. 폰 텔레그램에 "🤖 포트 봇 켜짐" 옴.

## 3. 폰에서 써보기
봇한테 보내:
- `/help` — 명령 목록
- `/status` — 포트 현황
- `/check` — 킬신호·단계 점검
- `/brief` — 내일 일정
- `/rotation` — 밸류체인 로테이션
- `/concentration` — 집중도
- `/payday` — 적립 후보
- 그냥 질문도 됨: `NBIS 상태?`, `CRDO 실적 어땠어?`

## 4. 계속 켜두기 (PC 꺼지면 봇도 꺼짐)
선택지:
- **간단:** 터미널 창 그냥 열어둠 (닫으면 꺼짐)
- **백그라운드:** `pythonw telegram_bot.py` (창 없이)
- **부팅 시 자동:** 작업 스케줄러 → 트리거 "로그온 시" → `python telegram_bot.py`
- **24시간:** 클라우드 VM(소형)에 올림 (PC 안 켜도 됨)

## 보안 (중요)
- 봇은 **네 chat_id만** 응답. 딴 사람이 봇 알아내도 무시됨.
- 슬래시 명령 = 정해진 것만. 자유질문 = 읽기·검색만(쓰기 X).
- **매매·송금 절대 안 함.** 분석·알림만.
- 토큰 유출되면 @BotFather에서 `/revoke` 후 재발급.

## 알림(단방향) + 봇(양방향) 같이
- 정기 알림: 작업 스케줄러 → `run_check.ps1` (토요일 자동 푸시)
- 수시 질문: `telegram_bot.py` 켜두고 폰에서 명령
- 둘 다 같은 .env·같은 봇 씀. 동시 사용 OK.

## 막히면
- "ModuleNotFound" → 파이썬 재설치(PATH 체크)
- "claude: not found" → claude 설치/로그인 확인
- 답장 안 옴 → .env의 TG_CHAT 숫자 맞는지, 봇한테 메시지 먼저 보냈는지
