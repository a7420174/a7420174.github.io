#!/usr/bin/env python3
"""
[BI Playground] sitemap 알림(ping) — IndexNow 경유.

주의: Google/Bing 의 옛 ping 엔드포인트(google.com/ping, bing.com/ping)는 모두
현재 404/410 으로 폐기 상태다. 대신 IndexNow 프로토콜(Bing·Naver 등 참여사 공통)로
sitemap URL 을 알린다. Google 은 IndexNow 미지원이므로 sitemap 재제출은
Search Console API(gsc_sync.py)로 처리한다.

사용:
    python3 _automation/ping_sitemaps.py --site https://a7420174.github.io
환경:
    INDEXNOW_KEY  (기본값: 저장소의 키 파일명)
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

HOST = "a7420174.github.io"
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://searchadvisor.naver.com/indexnow",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://a7420174.github.io")
    ap.add_argument("--key", default=os.environ.get("INDEXNOW_KEY",
                                                     "9cf15a8b80a04134b863d5567f3d18da"))
    args = ap.parse_args()
    site = args.site.rstrip("/")
    sitemap = f"{site}/sitemap.xml"
    payload = json.dumps({
        "host": HOST,
        "key": args.key,
        "keyLocation": f"{site}/{args.key}.txt",
        "urlList": [sitemap],
    }).encode("utf-8")
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"{ep} -> HTTP {r.status}")
        except urllib.error.HTTPError as e:
            print(f"{ep} -> HTTP {e.code}")
        except Exception as e:
            print(f"{ep} -> ERROR: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
