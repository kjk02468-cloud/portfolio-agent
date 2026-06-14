# Research Cycle 11 — HTML 대시보드 전면 업그레이드 (컨텍스트 재개)

날짜: 2026-06-09

## 이번 사이클 수행 내용

컨텍스트 압축 후 재개. 세션 중 완료한 HTML 대시보드 전 탭 업그레이드.

---

## 변경 파일: 미국 주식 포트폴리오 관리.html

### 1. 전역 상수 추가 (리서치 탭 init 구간)

**EARN_MAP_R** — 리서치 탭용 실적 일정 + 핵심 관전포인트 (ALAB/NBIS/IONQ/PATH/TLS/USAR/OKLO)
**KILL_DEFS_R** — 리서치 탭용 킬신호 정의 (manual.md 기반, 전 탭에서 참조 가능)

---

### 2. 리서치 탭 (tab-5) — 실적 프리뷰 패널 추가

**HTML 추가:** `#earnings-preview-btns` + `#earnings-preview-result` 패널

**신규 함수:**
- `renderEarningsPreviewBtns()` — 포트폴리오 티커별 D-day 버튼 (긴급도별 색상: 🔴14일/🟡30일/회색)
- `runEarningsPreview(ticker)` — 단일 종목 5-item 실적 프리뷰 (컨센서스 vs 독립추정, 킬신호 교차, 시나리오, 금리영향, 포지션 판단)
- `runEarningsPreviewAll()` — 전체 포트 6-item 어닝 시즌 전략 (위험/기대/하이퍼스케일러교차/포지션전략/금리순서/Marks 2nd level)

**sendResearch() 업그레이드:** 질문에 포트폴리오 티커 포함 시 `killCtx` 주입 (킬신호 정의 + 실적 D-day + 단계 + 비중 + 수익률)

---

### 3. 밸류체인 (tab-6) — 국방 테마 노드 추가

**cyber 노드 업그레이드:** TLS 보유 명시 + 연방계약 킬신호 + ~8/7 실적 관전포인트
**rare_earth 신규 노드:** USAR 보유 명시 + $1.6B 자본조달 vs 수주 구분 + PO 킬신호 + Lynch "고객이 돈 내기 전" 원칙

**analyzeRotationAI() 업그레이드:** `ownedInTheme` 배열로 이 테마 내 보유종목 전체 킬신호 + 실적 D-day 주입

---

### 4. 거시/테마 (tab-3) — 3가지 추가

**"capex 스위치 진단" 버튼** — `runCapexSwitchAI()` 함수
- 6-item: 현재 스위치 상태 / ALAB·NBIS 직접 파급 / 조기경보 5개 체크리스트 / 하향 시나리오 / 상향 시나리오 / 행동 기준

**금리 경로별 종목 영향 매트릭스** — 정적 HTML 테이블
- 7개 보유종목 × 4 금리 시나리오 (50bp인하/소프트랜딩/동결장기/50bp인상)
- 2-3차 파급 경로 포함, 종목별 자금줄에 따른 차별화 반영

**runScenarioSim() 업그레이드:** 킬신호 정의 + 실적 D-day + 비중 컨텍스트 전체 주입

---

### 5. Overview (tab-0) — 심층 진단 + D-day

**"심층 진단" 버튼** — `genDeepDiagnosis()` 함수
- 7-item: 킬신호 긴급도 순위 / 30일내 최대 촉매 / 포지션 사이징 진단(Lynch) / 밸류에이션 vs 단계 불일치 / Marks 2단계 사고 / 금리충격 취약 순서 / 30일 행동계획

**보유종목 테이블 `renderHoldingsTable()`:** 티커 셀에 실적 D-day pill 추가 (EARN_MAP_R 기반, 긴급도 색상)

---

### 6. 종목 인사이트 (tab-1) — 킬신호 스캔 + AI 업그레이드

**"킬신호 스캔" 버튼** — `runInsightKillScan()` 함수
- API 불필요, localStorage stagemeta 기반 즉시 표시
- 종목별: 위험도(🔴🟡🟢) + 킬신호 정의 + 실적 D-day + 승급/강등 트리거

**`updateInsights()` 업그레이드:** 킬신호 정의 + 실적 D-day 컨텍스트 주입
**`runSingleInsight()` 업그레이드:** 킬신호 정의 + D-day + 밸류 오버레이 주입, 금리시나리오 항목에 "금리 민감도 매트릭스 기준" 명시

---

### 7. 어닝 캘린더 (tab-4) — D-day 카운트다운 바

**`renderEarnDdayBar()`** — 탭 진입 시 항상 표시
- 포트폴리오 내 실적 예정 종목을 D-day 순 정렬
- 클릭 시 해당 종목 Finnhub 검색 자동 실행
- 14일 이내 🔴, 30일 이내 🟡, 그 이상 회색

---

### 8. 리밸런싱 (tab-2) — AI 비중 조언

**"AI 비중 조언" 버튼** — `runRebAI()` 함수
- 7-item: 단계별 이상적 비중(Lynch) / 확대 후보 / 축소 후보 / AI capex 집중도 / 목표 vs 현재 괴리 / 리밸런싱 타이밍 / 반박

---

### 9. 전략단계 (tab-7) — 실적 D-day 칩

**`sxCard()`:** `EARN_SX` 상수로 각 카드 헤더에 실적 D-day 칩 표시 (긴급도 색상)

---

## 핵심 개선 원칙 (이번 사이클)

1. **킬신호 전파**: KILL_DEFS_R를 전역 상수로 정의, 모든 AI 함수에서 참조
2. **실적 D-day 전파**: EARN_MAP_R를 전역 상수로 정의, Overview/인사이트/리밸런싱/전략단계/리서치 전 탭 표시
3. **금리 2-3차 파급**: 금리 매트릭스 테이블로 시각화 + runCapexSwitchAI로 capex 집중 분석
4. **Lynch·Marks·Graham 교차**: genDeepDiagnosis/runRebAI 프롬프트에 명시적 베스트셀러 기준 적용
5. **API 불필요 기능 우선**: runInsightKillScan, renderEarnDdayBar — 즉시 표시

---

## 다음 사이클 후보

1. **analyzeEventImpact()** — 개별 매크로 이벤트 분석에 킬신호 컨텍스트 주입
2. **watchlistInsight()** — 관심종목 한 줄 분석에 EXPERT_LENS 강화
3. **OSCR Q1 실적 품질 검증** — 일회성 vs 구조적 (watchlist.md 업데이트)
4. **dashboard.json 업데이트** — 킬신호 정의, 단계 메모 반영
5. **거시지표 실시간화** — S&P/나스닥/10Y/VIX 하드코딩 → Finnhub 자동 갱신
