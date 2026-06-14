# Research Cycle 12 — HTML 대시보드 전면 업그레이드

날짜: 2026-06-09

## 이번 사이클 수행 내용

컨텍스트 압축 후 재개. 사이클 11에서 미완료된 항목 + 신규 개선 10+개 완료.

---

## 변경 파일: 미국 주식 포트폴리오 관리.html

### 1. analyzeEventImpact() 전면 업그레이드

- `detail` 변수에 킬신호 정의(KILL_DEFS_R) + 실적 D-day(EARN_MAP_R) 주입
- 프롬프트에 1→2→3차 파급 경로 분석 원칙 명시
- 새 JSON 필드 `killRisk` (높음/중간/낮음/해당없음) 추가
- 렌더링에 killRisk 칩 표시 (색상 코딩)

---

### 2. watchlistInsight() 전면 업그레이드

- EXPERT_LENS 주입
- 킬신호 정의(KILL_DEFS_R) + 실적 D-day(EARN_MAP_R) + 단계 메모 주입
- 프롬프트: 2문장 → 3항목 구조 (핵심포인트 / 편입 트리거 조건 / 최대 리스크)
- Lynch/Graham/Marks 베스트셀러 기준 명시

---

### 3. 거시지표 실시간화 (refreshMacroIndicators)

- 하드코딩된 S&P 5,842 / 나스닥 18,710 / VIX 22.1 → Finnhub 실시간 갱신
- `refreshMacroIndicators()` 신규 함수: SPY / QQQ / VIXY Finnhub quote 조회
- 지표 카드에 ID 추가 (ind-sp500-val, ind-qqq-val, ind-vix-val)
- "지표 갱신" 버튼 추가
- 거시/테마 탭(tab-3) 전환 시 자동 호출

---

### 4. dashboard.json 전면 업데이트

- 날짜 2026-06-04 → 2026-06-09
- 각 종목에 `kill_signal_def` + `earn_date` + `earn_note` 필드 추가
- 누락 종목 추가: PATH(2단계), TLS(2단계), OKLO(1단계)
- 전역 `kill_signal_defs` 섹션 신설
- `next_events`에 TLS/USAR/OKLO/PATH 개별 실적 이벤트 추가
- `hyperscaler_earnings` 필드 추가 (meta 섹션)

---

### 5. VC_THEMES — 양자컴퓨팅(quantum) 노드 추가

- AI 테마에 `quantum` 노드 신규 추가
- IONQ 보유 명시 + 킬신호 (RPO 순감소 / 파일럿→반복구매 전환 0%) 포함
- Lynch RPO=수주잔고 관점, Graham 안전마진 논평 포함
- 실적 D-8/12 명시

---

### 6. sxAIStageReview() 업그레이드

- KILL_DEFS_R + EARN_MAP_R 전역 상수 활용
- `ctx`에 킬신호 정의 + 실적 D-day 추가
- 6번 항목: "킬신호 발화 가능성 가장 높은 종목" 으로 교체
- max_tokens 700→800 확대

---

### 7. genBriefing() 업그레이드

- `holdingsCtx`에 KILL_DEFS_R + EARN_MAP_R 주입
- 킬신호 조건 + 실적 D-day가 브리핑 컨텍스트에 포함

---

### 8. updateMacroAI() Step 2 업그레이드

- `detail` 변수에 KILL_DEFS_R + EARN_MAP_R 주입
- 프롬프트: 자금줄별 금리 민감도 분석 + 킬신호 ON 종목 해소/가속 판단 + 실적 D-day 영향
- 새 JSON 필드 `killRisk` 추가
- 렌더링에 killRisk 칩 표시 (updateMacroAI와 analyzeEventImpact 동일 패턴)

---

### 9. runEarningsAI() 업그레이드

**단일 종목 모드:**
- KILL_DEFS_E 로컬 상수 → KILL_DEFS_R 전역 상수 활용으로 교체
- EARN_MAP_R[ticker].note를 핵심 관전포인트로 프롬프트 주입
- 실적 D-day 주입 + 프롬프트에 "EARN_MAP 관전포인트 기준으로" 명시

**전체 포트 모드:**
- KILL_DEFS_E 로컬 상수 → KILL_DEFS_R 전역 상수 교체
- `upcoming` 배열: 하드코딩 → EARN_MAP_R 동적 생성 + D-day 순 정렬
- `earnCtx`에 D-day 포함

---

### 10. Overview 실적 임박 경고 배너

- `renderSummary()`에 `earn-alert-banner` 추가
- EARN_MAP_R 기반 D-14 이내 종목 자동 감지
- 종목명 + D-day 표시, "어닝 캘린더 →" 링크 버튼
- 킬신호 배너 위에 표시

---

## 핵심 개선 원칙 (이번 사이클)

1. **KILL_DEFS_R / EARN_MAP_R 전파 완성**: 사이클 11에서 빠진 함수들 (analyzeEventImpact, watchlistInsight, genBriefing, updateMacroAI, runEarningsAI, sxAIStageReview) 전부 업그레이드
2. **거시지표 실시간화**: 하드코딩 → Finnhub 자동 갱신 (탭 전환 시 자동 호출)
3. **killRisk 필드 표준화**: analyzeEventImpact + updateMacroAI 두 함수에 동일 패턴 적용
4. **dashboard.json 정합성**: HTML 상수(KILL_DEFS_R/EARN_MAP_R)와 dashboard.json 킬신호 정의 일치
5. **Overview 실적 경보**: 킬신호 배너에 더해 실적 임박 경보 배너 추가

---

## 다음 사이클 후보

1. **OSCR watchlist 분석** — 일회성 vs 구조적 (watchlist.md 업데이트)
2. **리서치 탭 뉴스 컨텍스트 품질 향상** — Finnhub 뉴스 요약을 AI 응답에 더 구조적으로 주입
3. **종목 인사이트 탭 추가 강화** — AI capex 집중도 경보 위젯
4. **전략단계 sxAIAnalysis KILL_DEFS_R 전역 상수 교체** — 현재 로컬 KILL_DEFS 사용
5. **거시/테마 탭 이벤트 카드 UI** — impact 레벨별 색상 구분 강화
