#!/usr/bin/env python3
"""
[BI Playground] 데스크톱 앱 OAuth 2.0 플로우 (외부 라이브러리 없이 표준 라이브러리만 사용).

pip 이 없는 환경에서도 동작하도록 urllib + http.server 만 사용한다.

동작:
  1) 로컬 서버(127.0.0.1:PORT)에서 콜백 대기
  2) 인증 URL 출력 → 사용자가 브라우저로 열고 승인
  3) 콜백으로 받은 code 를 토큰 엔드포인트에 교환
  4) refresh_token 출력 (→ GitHub Secret 등록용)

사용:
    python3 oauth_device_flow.py --client-id <ID> --client-secret <SECRET> \
        --project-id <PROJECT_ID> [--port 8765]
    또는 인증 코드만 직접 전달:
    python3 oauth_device_flow.py --client-id ... --client-secret ... --code <CODE>
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

SCOPES = [
    "https://www.googleapis.com/auth/indexing",
    "https://www.googleapis.com/auth/webmasters",
]
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"


def build_auth_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    return AUTH_URI + "?" + urllib.parse.urlencode(params)


def exchange_code(client_id: str, client_secret: str, code: str,
                  redirect_uri: str) -> dict:
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URI, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit(f"[ERROR] 토큰 교환 실패: HTTP {e.code} {body[:400]}")


class Handler(BaseHTTPRequestHandler):
    code_holder: dict = {}

    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if "code" in qs:
            Handler.code_holder["code"] = qs["code"][0]
            body = ("<html><body style='font-family:sans-serif;padding:40px'>"
                    "<h2>인증 완료 ✅</h2>"
                    "<p>이 창을 닫고 챗으로 돌아가세요.</p>"
                    "</body></html>")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            err = qs.get("error", ["unknown"])[0]
            Handler.code_holder["error"] = err
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"인증 실패: {err}".encode())

    def log_message(self, *a):  # noqa: D102 - silence
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--project-id", default="")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--code", default="", help="이미 승인 코드를 가지고 있을 때")
    args = ap.parse_args()

    redirect_uri = f"http://localhost:{args.port}"

    if args.code:
        tok = exchange_code(args.client_id, args.client_secret, args.code, redirect_uri)
    else:
        server = HTTPServer(("127.0.0.1", args.port), Handler)
        url = build_auth_url(args.client_id, redirect_uri)
        print("=" * 78, flush=True)
        print("아래 URL 을 브라우저(로그인된 Google 계정 = GSC 속성 소유자 계정)에서 열어 승인하세요.",
              flush=True)
        print("-" * 78, flush=True)
        print(url, flush=True)
        print("-" * 78, flush=True)
        print("승인 후 이 창은 그대로 두세요 (콜백 대기 중).", flush=True)
        print("=" * 78, flush=True)

        t = threading.Thread(target=server.handle_request, daemon=True)
        t.start()
        t.join(timeout=300)
        server.server_close()
        if "error" in Handler.code_holder:
            print(f"[ERROR] 사용자가 승인하지 않음: {Handler.code_holder['error']}")
            return 1
        if "code" not in Handler.code_holder:
            print("[ERROR] 시간 초과 (5분) — 승인 코드를 직접 전달해 다시 실행하세요.")
            return 1
        tok = exchange_code(args.client_id, args.client_secret,
                            Handler.code_holder["code"], redirect_uri)

    if "refresh_token" not in tok:
        print(f"[ERROR] refresh_token 이 없습니다: {json.dumps(tok)[:300]}")
        return 1

    print("\n[OK] 인증 완료")
    print("-" * 78)
    print("GOOGLE_OAUTH_CLIENT_ID     =", args.client_id)
    print("GOOGLE_OAUTH_CLIENT_SECRET =", args.client_secret)
    print("GOOGLE_OAUTH_REFRESH_TOKEN =", tok["refresh_token"])
    print("-" * 78)
    with open("oauth_creds.json", "w", encoding="utf-8") as f:
        json.dump({
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "refresh_token": tok["refresh_token"],
            "type": "authorized_user",
            "scopes": SCOPES,
        }, f, ensure_ascii=False, indent=2)
    print("[info] oauth_creds.json 저장됨 (repo 밖 경로 권장)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
