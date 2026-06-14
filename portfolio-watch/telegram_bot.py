#!/usr/bin/env python3
# 텔레그램 양방향 봇 (폴링)
# 폰에서 명령 → claude 실행 → 답장
# 보안: 등록된 chat_id만 허용. 매매 실행 절대 X (claude는 알림/분석만).

import json, os, subprocess, sys, time, traceback, urllib.request, urllib.parse, pathlib, shutil, datetime

DIR = pathlib.Path(__file__).parent
LOG = DIR / "reports" / "bot.log"

# claude CLI 경로 탐색
def _find_claude():
    candidates = [
        pathlib.Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
        pathlib.Path(os.environ.get("APPDATA", "")) / "npm" / "claude.CMD",
        pathlib.Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claude" / "claude.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    found = shutil.which("claude")
    if found:
        return found
    return "claude"

CLAUDE_BIN = _find_claude()

# .env 로드
for line in (DIR / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

TOKEN = os.environ["TG_TOKEN"]
CHAT  = str(os.environ["TG_CHAT"])
API   = f"https://api.telegram.org/bot{TOKEN}"

# 허용 슬래시 명령 (쓰기 권한 줌)
CMDS = {"/check", "/brief", "/rotation", "/concentration", "/payday", "/status", "/dashboard"}

def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def tg(method, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"{API}/{method}", data=data, timeout=70) as r:
        return json.load(r)

def send(text):
    text = text or " "
    for i in range(0, len(text), 4000):
        try:
            tg("sendMessage", chat_id=CHAT, text=text[i:i+4000])
        except Exception:
            pass

def run_claude(prompt, write=False):
    tools = ["Read", "WebSearch", "WebFetch"] + (["Write"] if write else [])
    try:
        # Windows: .cmd/.exe 모두 cmd /c 로 실행 (가장 안정적)
        if sys.platform == "win32":
            cmd = ["cmd", "/c", CLAUDE_BIN, "-p", prompt, "--allowedTools"] + tools
        else:
            cmd = [CLAUDE_BIN, "-p", prompt, "--allowedTools"] + tools

        log(f"RUN | bin={CLAUDE_BIN} | prompt={prompt[:50]}")

        out = subprocess.run(
            cmd,
            cwd=str(DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900
        )
        res = (out.stdout or out.stderr or "(빈 응답)").strip()
        log(f"OK  | rc={out.returncode} | len={len(res)}")
        return res

    except subprocess.TimeoutExpired:
        log("ERR | TimeoutExpired")
        return "시간초과 (claude 응답 없음)"
    except Exception as e:
        tb = traceback.format_exc()
        log(f"ERR | {type(e).__name__}: {e}\n{tb}")
        return f"실행 실패: {type(e).__name__}: {e}"

def dashboard_summary():
    """dashboard.json을 읽어 텔레그램 요약 메시지 생성 (Claude 호출 없음, 즉시)"""
    try:
        path = DIR / "reports" / "dashboard.json"
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"dashboard.json 읽기 실패: {e}"

    updated = d.get("updated", "?")
    holdings = d.get("holdings", [])
    signals  = d.get("signals", {})
    alerts   = d.get("alerts", [])
    events   = d.get("next_events", [])
    meta     = d.get("meta", {})
    action   = d.get("action", "")

    # 종목 by 단계
    by_stage = {}
    for h in holdings:
        s = h.get("stage", 0)
        by_stage.setdefault(s, []).append(h)

    lines = [f"📊 포트 대시보드 [{updated}]\n"]

    stage_names = {1: "1단계", 2: "2단계", 3: "3단계", 4: "4단계★"}
    for s in [1, 2, 3, 4]:
        hs = by_stage.get(s, [])
        if not hs:
            continue
        parts = []
        for h in hs:
            w = h.get("weight_pct")
            w_str = f"{w}%" if w else "+α"
            kill = " 🔴" if h.get("kill_signal") else ""
            parts.append(f"{h['ticker']} {w_str}{kill}")
        lines.append(f"{'🟦' if s==1 else '🟩' if s==2 else '🟨' if s==3 else '🏆'} {stage_names.get(s,str(s))}: {' / '.join(parts)}")

    # AI capex
    ai_pct = meta.get("ai_capex_pct", "?")
    non_pct = meta.get("non_ai_pct", "?")
    lines.append(f"\n💡 AI capex {ai_pct}% | 비-AI {non_pct}%")

    # 마스터스위치
    sw = meta.get("master_switch", "")
    if sw:
        lines.append(f"🔌 {sw[:80]}{'…' if len(sw)>80 else ''}")

    # 킬신호
    kills = signals.get("kill", [])
    if kills:
        lines.append("\n🔴 킬신호:")
        for k in kills:
            lines.append(f"  {k.get('ticker')} — {k.get('reason','')}")
    else:
        lines.append("\n🔴 킬신호: 없음")

    # 경고
    watches = signals.get("watch", [])
    if watches:
        lines.append("⚠️ 경고:")
        for w in watches:
            lines.append(f"  {w.get('ticker')} — {w.get('reason','')[:60]}")

    # 알림
    if alerts:
        lines.append("\n📣 알림:")
        for a in alerts:
            lines.append(f"  {a}")

    # 다음 이벤트 (7일 이내)
    today = datetime.date.today()
    upcoming = []
    for ev in events:
        try:
            ev_date = datetime.date.fromisoformat(ev["date"])
            if 0 <= (ev_date - today).days <= 7:
                impact = "🔴" if ev.get("impact") == "high" else "🟡"
                upcoming.append(f"  {impact} {ev['date']} {ev['desc'][:45]}")
        except Exception:
            pass
    if upcoming:
        lines.append("\n📅 7일내:")
        lines.extend(upcoming)

    # 행동
    if action:
        lines.append(f"\n💰 {action[:120]}{'…' if len(action)>120 else ''}")

    return "\n".join(lines)


def events_summary(days=30):
    """dashboard.json의 next_events에서 향후 N일 이벤트 요약"""
    try:
        path = DIR / "reports" / "dashboard.json"
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"dashboard.json 읽기 실패: {e}"

    today = datetime.date.today()
    events = d.get("next_events", [])
    upcoming = []
    for ev in events:
        try:
            ev_date = datetime.date.fromisoformat(ev["date"])
            delta = (ev_date - today).days
            if 0 <= delta <= days:
                impact = ev.get("impact", "medium")
                icon = "🔴" if impact == "high" else "🟡" if impact == "medium" else "⚪"
                tickers = ev.get("tickers", [])
                tk_str = f" [{', '.join(tickers)}]" if tickers else ""
                upcoming.append((delta, f"{icon} {ev['date']} (D-{delta})\n   {ev['desc']}{tk_str}"))
        except Exception:
            pass

    upcoming.sort(key=lambda x: x[0])
    if not upcoming:
        return f"📅 향후 {days}일 내 주요 이벤트 없음"

    lines = [f"📅 향후 {days}일 주요 이벤트 ({today})\n"]
    lines.extend(item[1] for item in upcoming)
    return "\n".join(lines)


def handle(text):
    text = text.strip()
    if text in ("/help", "/start"):
        return ("명령:\n/dashboard 대시보드 요약 (즉시)\n/events 향후 30일 이벤트\n"
                "/check 킬신호·단계 점검\n/brief 내일 일정\n"
                "/rotation 밸류체인 로테이션\n/concentration 집중도\n"
                "/payday 적립 후보\n/status 포트 현황\n\n또는 그냥 질문 쳐 (예: NBIS 상태?)")
    if text == "/dashboard":
        return dashboard_summary()
    if text == "/events":
        return events_summary(30)
    if text in CMDS:
        return run_claude(text, write=True)
    return run_claude(f"원시인처럼 핵심만 짧게. 매매 권유 말고 분석만. 질문: {text}", write=False)

def main():
    log(f"BOT START | CLAUDE_BIN={CLAUDE_BIN} | platform={sys.platform}")
    offset = None
    send("🤖 포트 봇 켜짐. /help 쳐봐")
    print(f"봇 실행 중 (claude={CLAUDE_BIN})... Ctrl+C로 종료")
    while True:
        try:
            res = tg("getUpdates", offset=(offset or ""), timeout=50)
            for u in res.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                cid = str((msg.get("chat") or {}).get("id"))
                txt = msg.get("text")
                if not txt:
                    continue
                if cid != CHAT:
                    log(f"SKIP | unknown chat {cid}")
                    continue
                send("⏳ 처리중...")
                send(handle(txt))
        except KeyboardInterrupt:
            print("종료"); break
        except Exception as e:
            log(f"LOOP ERR | {e}")
            time.sleep(5)
        time.sleep(2)

if __name__ == "__main__":
    main()
