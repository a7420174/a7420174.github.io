#!/usr/bin/env python3
"""
[BI Playground] sitemap lastmod 생성기.

문제: Jekyll 기본 sitemap 은 lastmod 를 front matter 의 date(=발행일)로 쓴다.
      글을 나중에 수정해도 lastmod 가 그대로여서 Google 이 신선도 신호를 신뢰하지 않는다.

해결: git 의 **실제 최종 커밋 시각**으로 lastmod 를 만들어
      `_data/sitemap_lastmod.json` 에 저장하고, sitemap 템플릿이 이를 참조한다.

사용:
    python3 _automation/gen_sitemap_lastmod.py --repo-root .
    # git 이 없는 환경이면 파일 mtime 으로 대체
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

DEFAULT_GIT = "/mnt/c/Program Files/Git/cmd/git.exe"


def git_time(repo_win: str, rel_path: str, git_bin: str) -> str | None:
    try:
        r = subprocess.run(
            [git_bin, "-C", repo_win, "log", "-1", "--format=%cI", "--", rel_path],
            capture_output=True, text=True, timeout=20)
        out = r.stdout.strip()
        return out or None
    except Exception:
        return None


def mtime_iso(path: str) -> str:
    import datetime as dt
    ts = os.path.getmtime(path)
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def post_slug(path: str) -> str:
    """Jekyll post.url 재현: /:categories/:title/ (카테고리 소문자·slugify, title 원형)."""
    name = os.path.basename(path)[:-3]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    cats: list[str] = []
    if m:
        in_cats = False
        for line in m.group(1).splitlines():
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

    def slugify(t: str) -> str:
        out = []
        for ch in str(t).strip().lower():
            if ch.isalnum() or ch in "-_" or ord(ch) > 0x2E80:
                out.append(ch)
            else:
                out.append("-")
        return re.sub(r"-+", "-", "".join(out)).strip("-")

    segs = [slugify(c) for c in cats if c] + [slug]
    return "/" + "/".join(segs) + "/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--repo-win", default="C:/Users/Kim JaeHyun/a7420174.github.io")
    ap.add_argument("--git", default=DEFAULT_GIT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    repo = args.repo_root
    out = args.out or os.path.join(repo, "_data", "sitemap_lastmod.json")

    data: dict[str, str] = {}
    missing = 0
    for path in sorted(glob.glob(os.path.join(repo, "_posts", "*.md"))):
        rel = os.path.relpath(path, repo).replace("\\", "/")
        ts = git_time(args.repo_win, rel, args.git)
        if not ts:
            ts = mtime_iso(path)
            missing += 1
        data[post_slug(path)] = ts

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"[info] {len(data)}개 글 lastmod 저장: {out}")
    if missing:
        print(f"[warn] git 시각 없어 mtime 사용: {missing}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
