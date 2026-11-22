#!/usr/bin/env python3
"""
[BI Playground] _posts/*.md → 라이브 URL 목록 생성.

permalink 규약: /:categories/:title/  (config.yml 의 permalink)
  - categories: front matter 의 categories 값(문자열 또는 목록)의 첫 항목,
    소문자 + slugify(Jekyll 규칙 근사: 공백/기호 → '-', 알파벳·숫자·한글 유지)
  - title: 파일명에서 YYYY-MM-DD- 접두사 제거, 대소문자 유지
  - 각 세그먼트를 percent-encode

사용:
    python3 collect_post_urls.py [파일...]        # 인자 없으면 전체
    python3 collect_post_urls.py --recent 10       # 최근 N개
    python3 collect_post_urls.py --from-diff A B   # 두 커밋 사이 변경 글
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys
import urllib.parse

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def slugify(text: str) -> str:
    out = []
    for ch in str(text).strip().lower():
        if ch.isalnum() or ch in "-_" or ord(ch) > 0x2E80:
            out.append(ch)
        else:
            out.append("-")
    return re.sub(r"-+", "-", "".join(out)).strip("-")


def categories_of(path: str) -> list[str]:
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m:
        return []
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
            mm = re.match(r"^\s+-\s+(.*)$", line)
            if mm:
                cats.append(mm.group(1).strip("'\""))
            else:
                in_cats = False
    return [c for c in cats if c]


def url_of(path: str) -> str:
    name = os.path.basename(path)[:-3]
    slug = DATE_PREFIX.sub("", name)
    cats = categories_of(path)
    segs = [slugify(c) for c in cats] + [slug]
    encoded = "/".join(urllib.parse.quote(s, safe="") for s in segs)
    return f"https://a7420174.github.io/{encoded}/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--recent", type=int, default=0)
    ap.add_argument("--from-diff", nargs=2, metavar=("BEFORE", "AFTER"))
    ap.add_argument("--posts-dir", default="_posts")
    args = ap.parse_args()

    paths: list[str] = []
    if args.from_diff:
        before, after = args.from_diff
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AM", before, after,
             "--", f"{args.posts_dir}/*.md"],
            capture_output=True, text=True)
        paths = [p for p in out.stdout.splitlines() if p.strip()]
    elif args.files:
        paths = list(args.files)
    else:
        paths = sorted(glob.glob(os.path.join(args.posts_dir, "*.md")))
        if args.recent:
            paths = paths[-args.recent:]

    for p in paths:
        if not os.path.exists(p):
            continue
        print(url_of(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
