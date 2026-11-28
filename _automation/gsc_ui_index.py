#!/usr/bin/env python3
"""
[BI Playground] GSC 상단 "URL 검사" 입력창을 이용한 요청 색인 자동화.

딥링크(?id=)는 404 이므로 UI 입력창 방식을 사용한다.
절차(URL 1건당):
  1) 속성 홈으로 이동
  2) 상단 입력창(aria-label: "<property>에 있는 모든 URL 검사")에 URL 입력
  3) Enter → 검사 결과 화면 대기
  4) "요청 색인" 버튼 클릭 → 접수 확인
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "gsc_request_index.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

CDP = "http://172.30.112.1:9223"
SITE = "https://a7420174.github.io/"
HOME = ("https://search.google.com/search-console?resource_id="
        + urllib.parse.quote(SITE, safe=""))

FIND_INPUT = r"""
(() => {
  const inp = [...document.querySelectorAll('input')].find(
    x => ((x.getAttribute('aria-label') || '') + ' ' + (x.placeholder || '')).includes('URL 검사'));
  if (!inp) return 'NO_INPUT';
  const r = inp.getBoundingClientRect();
  return JSON.stringify({x: r.x + r.width / 2, y: r.y + r.height / 2});
})()
"""

FIND_BTN = r"""
(() => {
  const labels = ['색인 생성 요청', '요청 색인', 'REQUEST INDEXING', 'Request indexing'];
  const all = [...document.querySelectorAll('button,[role=button],span,div')];
  for (const el of all) {
    const t = (el.innerText || '').trim();
    if (!t || t.length > 30) continue;
    if (!labels.some(l => t === l)) continue;
    let node = el;
    for (let i = 0; i < 4 && node; i++) {
      const tag = node.tagName, role = node.getAttribute && node.getAttribute('role');
      if (tag === 'BUTTON' || tag === 'A' || role === 'button') break;
      node = node.parentElement;
    }
    if (!node) continue;
    if (node.disabled || node.getAttribute('aria-disabled') === 'true') return 'DISABLED';
    const r = node.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    return JSON.stringify({x: r.x + r.width / 2, y: r.y + r.height / 2});
  }
  return 'NOTFOUND';
})()
"""

CONFIRM = r"""
(() => {
  const txt = document.body.innerText || '';
  if (/색인 생성 요청됨|우선순위 크롤링 대기열/.test(txt)) return '색인 생성 요청됨';
  if (/요청 제출 중|테스트 중/.test(txt)) return 'PENDING';
  return '';
})()
"""


def click_at(ws, x: float, y: float) -> None:
    for typ in ("mouseMoved", "mousePressed", "mouseReleased"):
        ws.call("Input.dispatchMouseEvent", {
            "type": typ, "x": x, "y": y, "button": "left", "clickCount": 1})
        time.sleep(0.05)


def gsc_tab() -> dict:
    tabs = json.loads(urllib.request.urlopen(CDP + "/json/list", timeout=15).read())
    for t in tabs:
        if t.get("type") == "page" and "search-console" in t.get("url", ""):
            return t
    raise SystemExit("GSC 탭이 없습니다. 먼저 로그인하세요.")


def request_one(ws, url: str) -> str:
    # 1) 홈으로
    ws.call("Page.navigate", {"url": HOME}, timeout=40)
    time.sleep(6)
    if "accounts.google.com" in (ws.evaluate("location.href") or ""):
        return "LOGIN_LOST"

    # 2) 입력창 클릭 후 타이핑
    raw = ws.evaluate(FIND_INPUT)
    if raw == "NO_INPUT":
        return "NO_INPUT"
    pos = json.loads(raw)
    click_at(ws, pos["x"], pos["y"])
    time.sleep(0.8)
    ws.call("Input.insertText", {"text": url})
    time.sleep(0.8)
    ws.call("Input.dispatchKeyEvent", {
        "type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
    ws.call("Input.dispatchKeyEvent", {
        "type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
    time.sleep(9)

    # 3) 요청 색인 버튼 대기
    deadline = time.time() + 70
    while time.time() < deadline:
        raw = ws.evaluate(FIND_BTN)
        if raw == "DISABLED":
            return "DISABLED"
        if raw and raw != "NOTFOUND":
            pos = json.loads(raw)
            clicked = ws.evaluate("""
(() => {
  const els = [...document.querySelectorAll('div[role=button],button')]
    .filter(x => (x.innerText||'').trim() === '색인 생성 요청');
  if (!els.length) return 'NO';
  els[0].scrollIntoView({block:'center'});
  els[0].click();
  return 'CLICKED';
})()
""")
            if clicked != 'CLICKED':
                click_at(ws, pos["x"], pos["y"])
            # '요청 제출 중' / '테스트 중' 대화상자를 최대 150초 기다린다
            got_pending = False
            for _ in range(45):
                msg = ws.evaluate(CONFIRM)
                if msg == '색인 생성 요청됨':
                    # 다이얼로그 닫기
                    try:
                        ws.evaluate("(()=>{const b=[...document.querySelectorAll('button,span,div')].find(x=>(x.innerText||'').trim()==='닫기'); if(b) b.click(); return 1})()")
                    except Exception:
                        pass
                    return "OK"
                if msg == 'PENDING':
                    got_pending = True
                time.sleep(3)
            return "PENDING_NO_CONFIRM" if got_pending else "NO_DIALOG"
        time.sleep(2)
    return "TIMEOUT_NO_BUTTON"


def main() -> int:
    f = sys.argv[1] if len(sys.argv) > 1 else "all_urls.txt"
    start, limit = 0, 999
    for i, a in enumerate(sys.argv):
        if a == "--start":
            start = int(sys.argv[i + 1])
        if a == "--limit":
            limit = int(sys.argv[i + 1])

    urls = [l.strip() for l in open(f, encoding="utf-8") if l.strip()]
    urls = urls[start:start + limit]
    out = os.path.join(HERE, "index_request_results.json")
    results = []
    if start > 0 and os.path.exists(out):
        try:
            results = json.load(open(out, encoding="utf-8"))
        except Exception:
            results = []

    ws = g.WS("/devtools/page/" + gsc_tab()["id"])
    ws.call("Runtime.enable")
    ws.call("Page.enable")
    try:
        for n, u in enumerate(urls, 1):
            short = urllib.parse.unquote(u.replace(SITE, ""))[:52] or "/"
            print(f"[{start + n}/{start + len(urls)}] {short}", flush=True)
            try:
                res = request_one(ws, u)
            except Exception as e:
                res = "ERROR: " + str(e)[:90]
            print(f"    -> {res}", flush=True)
            results.append({"url": u, "result": res})
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(results, fh, ensure_ascii=False, indent=2)
            if res == "LOGIN_LOST":
                print("로그인 세션 만료 - 중단", flush=True)
                break
            time.sleep(2)
    finally:
        ws.close()

    ok = sum(1 for r in results if r["result"].startswith("OK"))
    print(f"\n요약: 성공 {ok} / 시도 {len(results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
