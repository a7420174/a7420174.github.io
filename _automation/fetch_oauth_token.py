#!/usr/bin/env python3
"""
[BI Playground] 본인 계정 OAuth 토큰 발급 도우미 (서비스 계정 키 없이 Indexing/GSC API 사용).

왜 이 방법인가:
  조직 정책 `iam.disableServiceAccountKeyCreation` 때문에 서비스 계정 JSON 키를
  만들 수 없는 경우에 쓴다. Indexing API / Search Console API 는 OAuth 2.0 토큰이면
  되며, GSC 속성의 '소유자' 계정 토큰이면 정상 동작한다.

전제 (콘솔에서 1회):
  1) Google Cloud 콘솔 → 해당 프로젝트 → **API 및 서비스 → 사용자 인증 정보**
     → **클라이언트 ID 만들기** → 유형 **데스크톱 앱** → 만들기
  2) 만들어진 클라이언트 ID 의 '클라이언트 ID'/'클라이언트 비밀번호' 를 적어둠
     (OAuth 클라이언트 생성 자체가 막혀 있으면 방법 C 참고)

실행:
  python3 fetch_oauth_token.py --client-id <ID> --client-secret <SECRET> [--scopes ...]
  → 브라우저가 열리고(또는 URL 출력) 로그인·승인 후 refresh token 출력
  → 출력된 JSON 을 Secret 3개로 등록하면 끝
"""
from __future__ import annotations

import argparse
import json
import sys

SCOPES_DEFAULT = [
    "https://www.googleapis.com/auth/indexing",
    "https://www.googleapis.com/auth/webmasters",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--scopes", nargs="*", default=SCOPES_DEFAULT)
    ap.add_argument("--out", default="oauth_creds.json")
    args = ap.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("[ERROR] pip install google-auth-oauthlib google-auth", file=sys.stderr)
        return 1

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": args.client_id,
                "client_secret": args.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        scopes=args.scopes,
    )
    creds = flow.run_local_server(port=8765, prompt="consent")
    payload = {
        "client_id": args.client_id,
        "client_secret": args.client_secret,
        "refresh_token": creds.refresh_token,
        "type": "authorized_user",
        "scopes": list(args.scopes),
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[info] 저장됨: {args.out}")
    print("[info] 아래 3개를 GitHub Secret 으로 등록하세요.")
    print(f"  GOOGLE_OAUTH_CLIENT_ID     = {args.client_id}")
    print(f"  GOOGLE_OAUTH_CLIENT_SECRET = {args.client_secret}")
    print(f"  GOOGLE_OAUTH_REFRESH_TOKEN = {creds.refresh_token}")
    print("[info] (refresh token 출력은 위 파일에도 들어 있습니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
