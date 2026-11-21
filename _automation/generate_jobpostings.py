#!/usr/bin/env python3
"""
[BI Playground] 채용공고 글 → JobPosting JSON-LD 데이터 생성기.

입력 : _posts/*채용공고*.md
출력 : _data/jobpostings.json   (post slug → JobPosting 배열)

규칙
  - 본문의 '## 제목' 블록 단위로 공고 1건을 파싱한다.
  - '**기관**:' '**포지션**:' '**자격요건**:' '**주요업무**:' '**근무지**:'
    '**고용형태**:' '**마감일**:' '**출처**:' '[공고 링크](url)' 을 읽는다.
  - 마감일이 지난 공고는 만료 → JobPosting 에 넣지 않는다 (구글 스팸 방지).
  - 필수 필드가 빠진 공고도 제외한다 (title/기관/근무지/마감일/링크).

사용법:
  python3 _automation/generate_jobpostings.py --repo-root . [--check]
  --check : 파일만 검증하고 쓰지 않음 (CI 용)
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

FIELD_RE = re.compile(r"^-\s*\*\*(.+?)\*\*\s*[:：]\s*(.*)$")
LINK_RE = re.compile(r"\[공고\s*링크\]\((https?://[^)]+)\)")
TITLE_RE = re.compile(r"^##\s+(.+)$")
DATE_RE = re.compile(r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")

EMPLOYMENT_MAP = {
    "정규직": "FULL_TIME",
    "계약직": "CONTRACTOR",
    "인턴": "INTERN",
    "파트타임": "PART_TIME",
    "시간직": "PART_TIME",
}


def parse_date(text: str) -> dt.date | None:
    m = DATE_RE.search(text)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def parse_post(path: str, today: dt.date) -> tuple[list[dict], list[str]]:
    """(JobPosting 리스트, 제외 사유 리스트)"""
    raw = open(path, encoding="utf-8").read()
    fm = {}
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if re.match(r"^(date|permalink|title)\s*:", line):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip("'\"")
    post_date = fm.get("date", "")
    if not post_date:
        post_date = os.path.basename(path)[:10]

    blocks: list[dict] = []
    cur: dict | None = None
    for line in raw.splitlines():
        mt = TITLE_RE.match(line)
        if mt:
            cur = {"__title": mt.group(1).strip(), "fields": {}, "link": ""}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        ml = LINK_RE.search(line)
        if ml:
            cur["link"] = ml.group(1)
            continue
        mf = FIELD_RE.match(line)
        if mf:
            cur["fields"][mf.group(1).strip()] = mf.group(2).strip()

    out: list[dict] = []
    skipped: list[str] = []
    for b in blocks:
        f = b["fields"]
        name = f.get("기관", "")
        position = f.get("포지션", "")
        loc = f.get("근무지", "")
        deadline = parse_date(f.get("마감일", ""))
        title = f"{name} - {position}" if position else name
        if not (name and position and loc and b["link"]):
            skipped.append(f"{b['__title']}: 필수 필드 부족")
            continue
        if deadline is None:
            skipped.append(f"{b['__title']}: 마감일 파싱 실패")
            continue
        if deadline < today:
            skipped.append(f"{b['__title']}: 마감일({deadline}) 경과")
            continue

        emp_raw = f.get("고용형태", "")
        employment = next((v for k, v in EMPLOYMENT_MAP.items() if k in emp_raw), None)
        if employment is None:
            employment = "FULL_TIME" if "정규직" in emp_raw else "OTHER"

        desc_parts = [f.get("자격요건", ""), f.get("주요업무", ""), f.get("우대사항", "")]
        description = " ".join(p for p in desc_parts if p).strip()

        out.append({
            "@type": "JobPosting",
            "title": title,
            "description": description,
            "datePosted": post_date,
            "validThrough": deadline.isoformat(),
            "employmentType": employment,
            "hiringOrganization": {"@type": "Organization", "name": name},
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": loc,
                    "addressCountry": "KR",
                },
            },
            "url": b["link"],
            "directApply": False,
        })
    return out, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    repo = args.repo_root
    out_path = args.out or os.path.join(repo, "_data", "jobpostings.json")
    today = dt.date.today()

    data: dict[str, list[dict]] = {}
    total_skipped = 0
    for path in sorted(glob.glob(os.path.join(repo, "_posts", "*채용공고*.md"))):
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(path)[:-3])
        postings, skipped = parse_post(path, today)
        total_skipped += len(skipped)
        for s in skipped:
            print(f"[skip] {os.path.basename(path)} :: {s}", file=sys.stderr)
        if postings:
            data[slug] = postings
        print(f"[info] {os.path.basename(path)}: JobPosting {len(postings)}건")

    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    n = sum(len(v) for v in data.values())
    print(f"[info] 총 JobPosting {n}건 / 글 {len(data)}개 / 제외 {total_skipped}건")

    if args.check:
        if os.path.exists(out_path):
            cur = open(out_path, encoding="utf-8").read()
            if cur != payload:
                print("[ERROR] _data/jobpostings.json 이 최신 상태가 아닙니다. "
                      "generate_jobpostings.py 를 실행해 갱신하세요.", file=sys.stderr)
                return 1
        print("[info] _data/jobpostings.json 최신 상태 OK")
        return 0

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(payload)
    print(f"[info] 저장: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
