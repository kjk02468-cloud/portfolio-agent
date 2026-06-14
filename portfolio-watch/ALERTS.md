# 알림 연동 (텔레그램 / 카톡)

## 한 줄 결론
- **텔레그램 = 쉬움.** 10분, 무료, 안정적. **이걸로 해.**
- **카톡 = 빡셈.** "나에게 보내기" API만 개인용 가능, OAuth 토큰 만료 귀찮음. 비추.

---

## A. 텔레그램 (추천)

### 1. 봇 만들기
1. 텔레그램에서 **@BotFather** 검색 → 대화
2. `/newbot` 입력 → 봇 이름·아이디 정함
3. **토큰** 받음 (예: `123456:ABC-DEF...`). 복사.

### 2. 내 chat_id 얻기
1. 방금 만든 봇과 대화 시작 → 아무 메시지나 보냄 (예: "hi")
2. 브라우저에서:
   `https://api.telegram.org/bot<토큰>/getUpdates`
3. 결과에서 `"chat":{"id":숫자}` → 그 **숫자가 chat_id**

### 3. .env 채우기
`.env.example`를 `.env`로 복사하고:
```
TG_TOKEN=123456:ABC-DEF...
TG_CHAT=네chat_id숫자
```
⚠️ `.env`는 비밀. 남한테 보내지 마. 깃에 올리지 마.

### 4. 테스트
- **윈도우:** `./notify.ps1 "테스트"`
- **맥/리눅스:** `./notify.sh "테스트"`
텔레그램에 "테스트" 오면 성공.

### 5. 자동 점검+알림 연결
- **윈도우:** `run_check.ps1` 실행 → `/check` 돌리고 결과를 텔레그램으로
- **맥/리눅스/WSL:** `run_check.sh`

---

## B. 스케줄 걸기

### 윈도우 (작업 스케줄러)
1. "작업 스케줄러" 열기 → 기본 작업 만들기
2. 트리거: 매주 토요일 09:00
3. 동작: 프로그램 시작
   - 프로그램: `powershell.exe`
   - 인수: `-File "C:\Users\너\portfolio-watch\run_check.ps1"`
4. 저장. 끝.

### 맥/리눅스/WSL (cron)
```bash
crontab -e
```
```
0 9 * * 6 /home/너/portfolio-watch/run_check.sh
```

---

## C. 카톡 (굳이 하려면)

⚠️ 개인용은 **"나에게 보내기"**만 됨. 친구한테는 비즈니스 채널(알림톡, 유료·심사) 필요.

### 나에게 보내기 절차
1. [Kakao Developers](https://developers.kakao.com) 앱 등록 → **REST API 키** 발급
2. 카카오 로그인 OAuth로 **access_token** 받기 (scope: `talk_message`)
3. POST 호출:
   ```
   https://kapi.kakao.com/v2/api/talk/memo/default/send
   Authorization: Bearer <access_token>
   template_object={"object_type":"text","text":"메시지","link":{}}
   ```

### 왜 비추
- **access_token 만료** (~몇 시간). cron 돌리려면 **refresh_token으로 갱신 로직** 짜야 함.
- 텔레그램은 토큰 영구 + 호출 한 줄. 카톡은 토큰 관리 지옥.

→ **카톡 꼭 원하면** refresh 자동갱신 스크립트까지 필요. 말해주면 짜줄게. 근데 텔레그램 강력 추천.

---

## 흐름 정리
```
cron/작업스케줄러
  → run_check (claude -p "/check")
    → 결과 텍스트
      → notify (텔레그램/카톡 전송)
        → 네 폰에 알림 📲
```
