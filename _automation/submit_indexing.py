#!/usr/bin/env python3
"""
[BI Playground] Google Indexing API 제출 (채용공고 글 전용).

Indexing API 는 JobPosting(채용공고) / BroadcastEvent / 일반 URL 일부만
공식 지원한다. 일반 블로그 글에 남용하면 스팸 정책 위반이 될 수 있으므로
여기서는 '채용공고' 카테고리 글만 제출한다.

입력: stdin 에 URL 한 줄씩
환경: GOOGLE_INDEXING_SA_JSON (서비스 계정 JSON) 또는
      GOOGLE_OAUTH_CLIENT_ID / _SECRET / _REFRESH_TOKEN (본인 계정) 또는 ADC(키 없음)
의존: google-auth, requests
"""
from __future__ import annotations

import json
import os
import sys

SITE = "https://a7420174.github.io"


def main() -> int:
    urls = [l.strip() for l in sys.stdin if l.strip()]
    if not urls:
        print("[ERROR] 제출할 URL 이 없습니다.")
        return 1

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gsc_auth import get_session, SCOPES_INDEXING  # noqa: E402
    session = get_session(SCOPES_INDEXING)
    if session is None:
        return 1

    ok = fail = 0
    for url in urls:
        if not url.startswith(SITE + "/"):
            print(f"[SKIP] 사이트 외부 URL: {url}")
            continue
        try:
            r = session.post(
                "https://indexing.googleapis.com/v3/urlNotifications:publish",
                json={"url": url, "type": "URL_UPDATED"})
        except Exception as e:
            print(f"[FAIL] {url} :: {e}")
            fail += 1
            continue
        if r.status_code == 200:
            print(f"[ OK ] {url}")
            ok += 1
        else:
            print(f"[FAIL] {url} :: HTTP {r.status_code} {r.text[:300]}")
            fail += 1

    print(f"\n요약: 성공 {ok} / 실패 {fail}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
