#!/usr/bin/env python3
"""
[BI Playground] 네이버 개별 URL 갱신 요청 (IndexNow 단일 URL 방식).

네이버 서치어드바이저는 '수집요청 API' 를 제휴제안 심사를 거쳐야 제공하므로
일반 블로그에서는 공개 IndexNow 엔드포인트로 알리는 방식만 쓸 수 있다.
  GET https://searchadvisor.naver.com/indexnow?url=<url>&key=<key>
  (여러 개는 POST urlList — submit_indexnow.py 가 이미 처리)

사용:
    python3 _automation/naver_push.py <url1> <url2> ...
환경:
    INDEXNOW_KEY (기본값 저장소 키)
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.parse
import urllib.request

SITE = "https://a7420174.github.io"
KEY = os.environ.get("INDEXNOW_KEY", "9cf15a8b80a04134b863d5567f3d18da")


def push(url: str) -> bool:
    if not url.startswith(SITE + "/"):
        print(f"[SKIP] 외부 URL: {url}")
        return False
    q = urllib.parse.urlencode({"url": url, "key": KEY})
    req = urllib.request.Request(
        f"https://searchadvisor.naver.com/indexnow?{q}",
        headers={"User-Agent": "Mozilla/5.0 (compatible; BI-Playground/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"[ OK ] {url} (HTTP {r.status})")
            return True
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {url} (HTTP {e.code})")
        return False
    except Exception as e:
        print(f"[FAIL] {url} ({e})")
        return False


def main(argv: list[str]) -> int:
    urls = [a for a in argv if a.startswith("http")]
    if not urls:
        print("사용법: python3 _automation/naver_push.py <url> [...]")
        return 1
    ok = sum(push(u) for u in urls)
    print(f"\n성공 {ok} / 전체 {len(urls)}")
    return 0 if ok == len(urls) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
