#!/usr/bin/env python3
"""
[BI Playground] Google Search Console 연동 — sitemap 제출 + 색인 상태 조회.

목적: "글마다 GSC에 등록/수동 색인 요청"을 없애기 위해,
      (1) sitemap 을 GSC 에 다시 제출(ping)하고
      (2) 새 글 URL 의 실제 색인 상태를 자동 조회해 리포트로 남긴다.

사용:
    python3 _automation/gsc_sync.py --site https://a7420174.github.io --urls-file urls.txt
환경:
    GOOGLE_SA_JSON  — 서비스 계정 JSON 전체 (GSC '소유자' 로 추가된 계정)
의존: google-auth, requests
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse

SITEMAP_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
INSPECT_ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"


def get_session():
    raw = os.environ.get("GOOGLE_SA_JSON", "").strip()
    if not raw:
        print("[ERROR] GOOGLE_SA_JSON secret 이 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("[ERROR] google-auth / requests 필요: pip install google-auth requests",
              file=sys.stderr)
        sys.exit(1)
    creds = service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=["https://www.googleapis.com/auth/webmasters"])
    return AuthorizedSession(creds)


def submit_sitemap(session, site: str) -> bool:
    feed = f"{site}/sitemap.xml"
    url = SITEMAP_ENDPOINT.format(site=site, feed=urllib.parse.quote(feed, safe=""))
    r = session.put(url)
    if r.status_code in (200, 204):
        print(f"[ OK ] sitemap 제출 완료: {feed}")
        return True
    print(f"[FAIL] sitemap 제출 실패 :: HTTP {r.status_code} {r.text[:300]}")
    return False


def inspect(session, site: str, urls: list[str]) -> list[dict]:
    rows = []
    for u in urls:
        body = {
            "inspectionUrl": u,
            "siteUrl": site,
            "languageCode": "ko-KR",
        }
        try:
            r = session.post(INSPECT_ENDPOINT, json=body)
        except Exception as e:
            print(f"[FAIL] {u} :: {e}")
            rows.append({"url": u, "indexingState": "ERROR", "verdict": str(e)[:120]})
            continue
        if r.status_code != 200:
            print(f"[FAIL] {u} :: HTTP {r.status_code} {r.text[:200]}")
            rows.append({"url": u, "indexingState": "ERROR", "verdict": f"HTTP {r.status_code}"})
            continue
        res = (r.json().get("inspectionResult", {})
                 .get("indexStatusResult", {}))
        row = {
            "url": u,
            "indexingState": res.get("indexingState", "UNKNOWN"),
            "verdict": res.get("verdict", ""),
            "coverage": res.get("indexingState", ""),
            "lastCrawlTime": res.get("lastCrawlTime", ""),
        }
        rows.append(row)
        print(f"[ {row['indexingState']:<10} ] {u}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://a7420174.github.io")
    ap.add_argument("--urls-file", default="")
    ap.add_argument("--sitemap", action="store_true", help="sitemap 제출만 수행")
    args = ap.parse_args()

    site = args.site.rstrip("/")
    session = get_session()

    ok = submit_sitemap(session, site)

    rows = []
    if args.urls_file and os.path.exists(args.urls_file):
        urls = [l.strip() for l in open(args.urls_file, encoding="utf-8") if l.strip()]
        rows = inspect(session, site, urls)
        with open("gsc-index-status.json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        indexed = sum(1 for r in rows if r["indexingState"] == "INDEXING_ALLOWED")
        print(f"\n색인 허용 {indexed} / 전체 {len(rows)}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
