#!/usr/bin/env python3
"""
[BI Playground] sitemap/색인 준비 상태 스프린트 점검.

검사 항목
  1. robots.txt 에 Sitemap: 선언이 있는지
  2. sitemap.xml XML 파싱, 모든 <loc> 가 https + 사이트 도메인인지
  3. <loc> 중복 여부
  4. 저장소 _posts/*.md 가 sitemap 에 모두 포함되었는지 (기대 URL 재현)
  5. sitemap 에 있는 페이지가 실제 HTTP 200 인지
  6. sitemap 의 URL 이 우리 것이 아닌 외부 URL 을 포함하지 않는지

사용법
  python3 check_sitemap.py --site https://a7420174.github.io --repo-root . --wait-minutes 10

종료코드: 0 = 이상 없음 / 1 = 오류 있음
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (compatible; BI-Playground-SitemapCheck/1.0)"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

ERRORS: list[str] = []
WARNINGS: list[str] = []
INFO: list[str] = []


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}", flush=True)


def err(msg: str) -> None:
    ERRORS.append(msg)
    log("ERROR", msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    log("WARN ", msg)


def info(msg: str) -> None:
    INFO.append(msg)
    log("INFO ", msg)


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def status(url: str, timeout: int = 20) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(1)
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


# ---------------------------------------------------------------- slug 유틸
def jekyll_slug(text: str) -> str:
    """Jekyll slugify 근사: 소문자화, 공백->'-', 알파벳/숫자/한글/'-'만 유지."""
    text = str(text).strip().lower()
    out = []
    for ch in text:
        if ch.isalnum() or ch in "-_" or ord(ch) > 0x2E80:  # 한글/CJK 포함
            out.append(ch)
        else:
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug


def front_matter(path: str) -> dict:
    """PyYAML 없이 front matter 의 categories 만 추출."""
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", txt, re.S)
    if not m:
        return {}
    block = m.group(1)
    cats: list[str] = []
    in_cats = False
    for line in block.splitlines():
        if re.match(r"^categories\s*:", line):
            rest = line.split(":", 1)[1].strip()
            in_cats = True
            if rest:
                cats.append(rest.strip("'\""))
            continue
        if in_cats:
            if re.match(r"^\s+-\s+", line):
                cats.append(line.strip()[2:].strip("'\""))
            else:
                in_cats = False
    return {"categories": cats}


def post_rel_path(path: str) -> str:
    """_posts/<date>-<slug>.md -> /<category-slug>/<slug>/ (Jekyll permalink 규약 재현)."""
    name = os.path.basename(path)[:-3]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    fm = front_matter(path)
    cats = fm.get("categories") or []
    cat_slugs = [jekyll_slug(c) for c in cats if c.strip()]
    quoted = "/".join(urllib.parse.quote(s, safe="-") for s in cat_slugs)
    tail = urllib.parse.quote(slug, safe="-")
    return f"/{quoted}/{tail}/" if quoted else f"/{tail}/"


def expected_urls(repo_root: str) -> set[str]:
    """_posts/*.md -> 예상 permalink (/ :categories :title /)."""
    urls: set[str] = set()
    for path in sorted(glob.glob(os.path.join(repo_root, "_posts", "*.md"))):
        urls.add(post_rel_path(path))
    return urls


# ---------------------------------------------------------------- 검사 본체
def check_robots(site: str) -> None:
    try:
        body = fetch(f"{site}/robots.txt").decode("utf-8", "replace")
    except Exception as e:
        err(f"robots.txt 를 가져오지 못했습니다: {e}")
        return
    if "Sitemap:" not in body:
        err("robots.txt 에 'Sitemap:' 선언이 없습니다.")
        return
    declared = []
    for line in body.splitlines():
        if line.lower().startswith("sitemap:"):
            u = line.split(":", 1)[1].strip()
            declared.append(u)
            info(f"robots.txt sitemap 선언: {u}")
    # 표준 경로(sitemap.xml) 가 선언되어 있으면 하위 sitemap 추가 선언은 정상이다.
    if f"{site}/sitemap.xml" not in declared:
        warn(f"robots.txt 에 표준 sitemap 경로({site}/sitemap.xml) 선언이 없습니다: {declared}")
    for u in declared:
        if not u.startswith(site + "/"):
            err(f"robots.txt 의 sitemap 이 사이트 외부 주소입니다: {u}")
    if "Disallow: /" in body:
        err("robots.txt 에 'Disallow: /' 가 있어 크롤이 전부 막혀 있습니다.")


def _collect_xml(raw: bytes, site: str, depth: int = 0) -> tuple[list[str], dict[str, str]]:
    """urlset 또는 sitemapindex 를 재귀적으로 해석해 URL 목록을 모은다."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        err(f"sitemap XML 파싱 실패: {e}")
        return [], {}

    tag = root.tag.split('}')[-1]
    locs: list[str] = []
    lastmods: dict[str, str] = {}

    if tag == "sitemapindex":
        children = [n.findtext("sm:loc", default="", namespaces=NS).strip()
                    for n in root.findall("sm:sitemap", NS)]
        children = [c for c in children if c]
        info(f"sitemapindex: 하위 sitemap {len(children)}개")
        if depth > 2:
            err("sitemapindex 중첩이 2단계를 넘습니다.")
            return [], {}
        for child in children:
            if not child.startswith(site):
                err(f"하위 sitemap 이 사이트 외부 주소입니다: {child}")
                continue
            try:
                sub_raw = fetch(child)
            except Exception as e:
                err(f"하위 sitemap 조회 실패 {child}: {e}")
                continue
            sub_locs, sub_lm = _collect_xml(sub_raw, site, depth + 1)
            locs.extend(sub_locs)
            lastmods.update(sub_lm)
        return locs, lastmods

    for node in root.findall("sm:url", NS):
        loc = node.findtext("sm:loc", default="", namespaces=NS).strip()
        lm = node.findtext("sm:lastmod", default="", namespaces=NS).strip()
        if loc:
            locs.append(loc)
            if lm:
                lastmods[loc] = lm
    return locs, lastmods


def parse_sitemap(site: str) -> tuple[list[str], dict[str, str]]:
    raw = fetch(f"{site}/sitemap.xml")
    return _collect_xml(raw, site)


def check_locs(site: str, locs: list[str]) -> set[str]:
    seen: set[str] = set()
    dupes = set()
    for loc in locs:
        if loc in seen:
            dupes.add(loc)
        seen.add(loc)
        if not loc.startswith("https://"):
            err(f"http(s) 아닌 URL 이 sitemap 에 있습니다: {loc}")
        elif not loc.startswith(site + "/"):
            err(f"사이트 외부 URL 이 sitemap 에 있습니다: {loc}")
    for d in sorted(dupes):
        err(f"중복 URL: {d}")
    return seen


def check_expected(site: str, seen: set[str], repo_root: str) -> set[str]:
    expected = expected_urls(repo_root)
    missing = []
    for path in sorted(glob.glob(os.path.join(repo_root, "_posts", "*.md"))):
        full = site + post_rel_path(path)
        name = os.path.basename(path)
        if full not in seen:
            missing.append((name, full))
    if missing:
        for name, full in missing:
            warn(f"sitemap 에 아직 없는 글: {name} -> {full}")
    else:
        info(f"글 {len(expected)}개 모두 sitemap 에 포함되어 있습니다.")
    return expected


def check_http(site: str, seen: set[str]) -> None:
    urls = sorted(seen)
    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(status, urls))
    bad = [(u, c) for u, c in zip(urls, codes) if c != 200]
    for u, c in bad:
        err(f"HTTP {c} : {u}")
    if not bad:
        info(f"sitemap 내 {len(urls)}개 URL 모두 HTTP 200 응답.")


def wait_for_deploy(site: str, repo_root: str, minutes: int) -> tuple[list[str], dict[str, str]]:
    """push 직후 배포 지연 대비: 새 글이 sitemap 에 나타날 때까지 대기."""
    deadline = time.time() + minutes * 60
    expected_paths = {u for u in expected_urls(repo_root)}
    attempt = 0
    while True:
        attempt += 1
        try:
            locs, lastmods = parse_sitemap(site)
        except Exception as e:
            warn(f"sitemap 조회 실패({e}). 재시도합니다.")
            locs, lastmods = [], {}
        if locs:
            paths = {urllib.parse.urlparse(l).path for l in locs}
            missing = expected_paths - paths
            if not missing:
                if attempt > 1:
                    info(f"배포 반영 확인 (시도 {attempt}회).")
                return locs, lastmods
        if time.time() >= deadline:
            warn(f"제한 시간 {minutes}분 내에 새 글이 sitemap 에 반영되지 않았습니다. "
                 f"현재 sitemap 기준({len(locs)}개)으로 계속 검사합니다.")
            return locs, lastmods
        info(f"배포 대기 중... ({attempt}회)")
        time.sleep(30)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://a7420174.github.io")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--wait-minutes", type=int, default=10)
    ap.add_argument("--skip-http", action="store_true")
    args = ap.parse_args()

    site = args.site.rstrip("/")
    log("INFO ", f"점검 시작: {site} (repo: {args.repo_root})")
    started = dt.datetime.now()

    check_robots(site)
    locs, lastmods = wait_for_deploy(site, args.repo_root, args.wait_minutes)
    if not locs:
        err("sitemap.xml 을 읽지 못했습니다.")
    else:
        info(f"sitemap URL {len(locs)}개, lastmod {len(lastmods)}개.")
        seen = check_locs(site, locs)
        check_expected(site, seen, args.repo_root)
        if not args.skip_http:
            check_http(site, seen)

    print("\n===== 결과 =====")
    print(f"오류 {len(ERRORS)}건 / 경고 {len(WARNINGS)}건 / 정보 {len(INFO)}건 "
          f"({(dt.datetime.now() - started).seconds}초)")
    if ERRORS:
        print("\n[오류]")
        for e in ERRORS:
            print(" -", e)
    if WARNINGS:
        print("\n[경고]")
        for w in WARNINGS:
            print(" -", w)
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
