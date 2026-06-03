# GitHub Actions 자동화 셋업 (노트북 무관 24시간)

목표: GitHub 서버가 하루 2회 자동으로 점검 → Gist 푸시 → 텔레그램 알림. 노트북 꺼져 있어도 됨.

═══════════════════════════════
## 1. GitHub repo 만들기
═══════════════════════════════
1. github.com → 우측 상단 + → **New repository**
2. 이름 예: `portfolio-agent`
3. **Private 권장** (설정 파일·전략 공개 안 하려면)
4. Create

## 2. 파일 올리기
repo에 이 구조 그대로 업로드:
```
portfolio-agent/
├── .github/workflows/portfolio.yml   ← 워크플로 (필수 경로)
├── CLAUDE.md
├── portfolio.md
├── manual.md
├── calendar.md
├── watchlist.md
└── .claude/commands/
    ├── check.md
    ├── export.md
    ├── status.md
    ├── brief.md
    ├── rotation.md
    ├── concentration.md
    └── payday.md
```
- 웹에서: repo → Add file → Upload files → 폴더째 드래그
- ⚠️ `.github/workflows/portfolio.yml` **경로 정확히** (안 그러면 Actions 인식 못 함)

## 3. Secrets 등록 (열쇠들)
repo → **Settings → Secrets and variables → Actions → New repository secret**

5개 등록:
| 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys에서 발급 (sk-ant-...) |
| `GIST_TOKEN` | github.com→Settings→Developer settings→Tokens, **gist 권한** PAT |
| `GIST_ID` | 네 Gist 아이디 (이미 있음) |
| `TELEGRAM_TOKEN` | BotFather 토큰 (이미 있음) |
| `TELEGRAM_CHAT` | 네 chat_id (이미 있음) |

⚠️ Secrets는 한 번 저장하면 다시 못 봄(정상). 이름 오타 주의.

## 4. 테스트 (수동 실행)
1. repo → **Actions** 탭
2. 왼쪽 `portfolio-check` 클릭
3. 우측 **Run workflow** 버튼 → Run
4. 1~2분 뒤 초록 체크 = 성공. 텔레그램 알림 오고 Gist 갱신됨
5. 실패(빨강)면 → 클릭해서 어느 step에서 멈췄는지 로그 확인

═══════════════════════════════
## ⚠️ 알아둘 것 (중요)
═══════════════════════════════

**① 시간은 UTC 기준** (한국=UTC+9)
- 워크플로 cron `30 22` = UTC 22:30 = **한국 07:30**
- `30 21` = **한국 06:30**
- 시간 바꾸려면 portfolio.yml의 cron 숫자 수정 (KST에서 9 빼면 UTC)

**② 스케줄 지연·스킵 가능**
- GitHub Actions 무료 cron은 정확하지 않아 (5~30분 늦거나 가끔 건너뜀)
- 하루 점검엔 문제없음. 초단위 실시간은 기대 X

**③ 60일 무활동 시 자동 비활성화**
- repo에 60일간 커밋 없으면 스케줄 멈춤 → 가끔 아무 커밋이나 하면 유지
- 또는 매뉴얼 갱신할 때 portfolio.md 고치면 자동 유지됨

**④ API 키 = 과금** (구독과 별개)
- 하루 2회 짧은 점검 ≈ 월 수백~수천 원. console.anthropic.com에서 사용량·한도 설정 가능
- 비용 걱정되면 cron 하루 1회로 줄여

**⑤ 권한 에러 시**
- claude가 CI에서 멈추면 portfolio.yml의 `--allowedTools` 줄을
  `--dangerously-skip-permissions` 로 바꿔 (비대화 강제 실행)

═══════════════════════════════
## 최종 그림
═══════════════════════════════
```
[GitHub 서버] 매일 07:30·18:30(예시) 자동
   → /check → 텔레그램 알림 📲
   → /export → Gist 푸시
        ↓
[폰/PC 대시보드] 열면 자동 최신
```
노트북: 이제 꺼도 됨. 수시로 직접 물어볼 때만 `claude` 켜.

## 노트북 버전과 공존
- 노트북 켜져 있을 때: 직접 `claude`로 대화 (실시간 질문)
- 꺼져 있을 때: GitHub Actions가 정기 점검·알림 대신함
- 둘이 같은 Gist·텔레그램 씀. 충돌 없음.
