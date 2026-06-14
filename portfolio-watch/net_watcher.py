#!/usr/bin/env python3
"""
net_watcher.py — 인터넷 연결 감지 시 포트폴리오 요약을 텔레그램으로 자동 발송

동작 방식:
  - 5초마다 인터넷 연결 상태 체크
  - 오프라인 → 온라인 전환 감지 시 텔레그램 요약 발송
  - 중복 발송 방지: 같은 날 이미 발송했으면 스킵 (COOLDOWN_HOURS 기준)
  - 매일 오전 08:30 KST(시장 열리기 전) 정기 발송 추가

실행 방법:
  python net_watcher.py          # 포그라운드 (터미널 유지)
  pythonw net_watcher.py         # 백그라운드 (창 없이)

작업 스케줄러 등록 (부팅 시 자동):
  트리거: 로그온 시
  동작: pythonw "C:\\...\\portfolio-watch\\net_watcher.py"
"""

import datetime, json, os, pathlib, time, urllib.parse, urllib.request

DIR = pathlib.Path(__file__).parent
LOG = DIR / "reports" / "net_watcher.log"
STAMP = DIR / "reports" / "last_broadcast.txt"   # 마지막 발송 타임스탬프

COOLDOWN_HOURS = 4      # 연결 감지 발송 최소 간격 (시간)
DAILY_HOUR_KST = 8      # 정기 발송 시각 (KST 시 단위, 0~23)
DAILY_MIN_KST  = 30     # 정기 발송 분
CHECK_INTERVAL = 5      # 연결 체크 간격 (초)

# ── .env 로드 ──────────────────────────────────────────────────────────────
for line in (DIR / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

TOKEN = os.environ.get("TG_TOKEN", "")
CHAT  = str(os.environ.get("TG_CHAT", ""))
API   = f"https://api.telegram.org/bot{TOKEN}"


def log(msg):
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def is_online():
    try:
        urllib.request.urlopen("https://api.telegram.org", timeout=4)
        return True
    except Exception:
        return False


def tg_send(text):
    if not TOKEN or not CHAT:
        log("ERR | TG_TOKEN 또는 TG_CHAT 없음 — .env 확인")
        return
    for i in range(0, len(text), 4000):
        try:
            data = urllib.parse.urlencode({"chat_id": CHAT, "text": text[i:i+4000]}).encode()
            urllib.request.urlopen(f"{API}/sendMessage", data=data, timeout=10)
        except Exception as e:
            log(f"ERR | tg_send: {e}")


# ── 포트폴리오 요약 빌더 ───────────────────────────────────────────────────

def build_summary(reason="연결감지"):
    try:
        path = DIR / "reports" / "dashboard.json"
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"⚠️ dashboard.json 읽기 실패: {e}"

    today = datetime.date.today()
    updated = d.get("updated", "?")
    holdings = d.get("holdings", [])
    signals  = d.get("signals", {})
    meta     = d.get("meta", {})
    action   = d.get("action", "")
    events   = d.get("next_events", [])

    lines = [f"📊 포트 요약 [{updated}] — {reason}\n"]

    # 단계별 종목
    stage_icons = {1: "🟦", 2: "🟩", 3: "🟨", 4: "🏆"}
    stage_names = {1: "1단계", 2: "2단계", 3: "3단계", 4: "4단계★"}
    by_stage = {}
    for h in holdings:
        s = h.get("stage", 0)
        by_stage.setdefault(s, []).append(h)
    for s in [1, 2, 3, 4]:
        hs = by_stage.get(s, [])
        if not hs:
            continue
        parts = []
        for h in hs:
            w = h.get("weight_pct")
            kill = "🔴" if h.get("kill_signal") else ""
            parts.append(f"{h['ticker']} {w or '?'}%{kill}")
        lines.append(f"{stage_icons.get(s,'')} {stage_names.get(s,s)}: {' / '.join(parts)}")

    # 메타테마 집중도
    ai_pct  = meta.get("ai_capex_pct", "?")
    non_pct = meta.get("non_ai_pct", "?")
    lines.append(f"\n💡 AI capex {ai_pct}% | 비-AI {non_pct}%")

    # 킬신호
    kills = signals.get("kill", [])
    lines.append("\n🔴 킬신호: " + ("없음" if not kills else ""))
    for k in kills:
        lines.append(f"  {k.get('ticker')} — {k.get('reason','')[:60]}")

    # 경고
    watches = signals.get("watch", [])
    if watches:
        lines.append("⚠️ 경고:")
        for w in watches:
            lines.append(f"  {w.get('ticker')} — {w.get('reason','')[:55]}")

    # 행동
    if action:
        lines.append(f"\n💰 {action[:120]}{'…' if len(action) > 120 else ''}")

    # 이벤트 (14일 이내)
    upcoming = []
    for ev in events:
        try:
            ev_date = datetime.date.fromisoformat(ev["date"])
            delta = (ev_date - today).days
            if 0 <= delta <= 14:
                icon = "🔴" if ev.get("impact") == "high" else "🟡"
                upcoming.append((delta, f"{icon} {ev['date']} D-{delta}: {ev['desc'][:50]}"))
        except Exception:
            pass
    if upcoming:
        upcoming.sort(key=lambda x: x[0])
        lines.append("\n📅 14일내 이벤트:")
        lines.extend(item[1] for item in upcoming)

    return "\n".join(lines)


# ── 발송 쿨다운 관리 ──────────────────────────────────────────────────────

def last_broadcast_time():
    try:
        return datetime.datetime.fromisoformat(STAMP.read_text("utf-8").strip())
    except Exception:
        return datetime.datetime(2000, 1, 1)


def update_stamp():
    try:
        STAMP.write_text(datetime.datetime.now().isoformat(), "utf-8")
    except Exception:
        pass


def should_broadcast(reason=""):
    last = last_broadcast_time()
    elapsed_h = (datetime.datetime.now() - last).total_seconds() / 3600
    if elapsed_h < COOLDOWN_HOURS:
        log(f"SKIP | {reason} | 쿨다운 {elapsed_h:.1f}h < {COOLDOWN_HOURS}h")
        return False
    return True


# ── 정기 발송 타이밍 체크 ─────────────────────────────────────────────────

_daily_sent_date = None

def check_daily_send():
    global _daily_sent_date
    now_kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    today   = now_kst.date()
    if (now_kst.hour == DAILY_HOUR_KST and now_kst.minute == DAILY_MIN_KST
            and _daily_sent_date != today):
        _daily_sent_date = today
        return True
    return False


# ── 메인 루프 ─────────────────────────────────────────────────────────────

def main():
    log("NET_WATCHER START")
    was_online = is_online()
    log(f"초기 상태: {'온라인' if was_online else '오프라인'}")

    if was_online and should_broadcast("시작"):
        msg = build_summary("봇 시작")
        tg_send(msg)
        update_stamp()
        log("SENT | 시작 요약")

    while True:
        try:
            now_online = is_online()

            # 오프라인 → 온라인 전환 감지
            if not was_online and now_online:
                log("EVENT | 인터넷 연결 감지")
                if should_broadcast("연결감지"):
                    msg = build_summary("📶 인터넷 연결됨")
                    tg_send(msg)
                    update_stamp()
                    log("SENT | 연결감지 요약")

            was_online = now_online

            # 정기 발송 (매일 KST 08:30)
            if now_online and check_daily_send():
                log("EVENT | 정기 발송 08:30 KST")
                msg = build_summary("🌅 오전 정기 점검")
                tg_send(msg)
                update_stamp()
                log("SENT | 정기 요약")

        except Exception as e:
            log(f"LOOP ERR | {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
