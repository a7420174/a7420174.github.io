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



KR_REGIONS = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시",
    "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "세종": "세종특별자치시",
    "경기": "경기도", "강원": "강원특별자치도", "충북": "충청북도", "충남": "충청남도",
    "전북": "전북특별자치도", "전남": "전라남도", "경북": "경상북도", "경남": "경상남도",
    "제주": "제주특별자치도",
}



# 광역시·도 + 시군구 → 대표 우편번호 (5자리)
# 출처: 우정사업본부 우편번호 체계 (시군구 단위 대표값).
# 정확한 도로명 우편번호가 원문에 없을 때만 사용하는 근사값이며,
# 실제 배송 주소가 아니라 구조화 데이터의 지역 식별 용도다.
POSTAL_BY_REGION = {
    ("US:TX", "Houston"): "77030",
    ("US:TX", "휴스턴"): "77030",
    ("US:CA", "San Jose"): "95112",
    ("US:CA", "산호세"): "95112",
    ("서울특별시", "종로구"): "03055",
    ("서울특별시", "구로구"): "08295",
    ("서울특별시", "중구"): "04555",
    ("서울특별시", "강서구"): "07650",
    ("서울특별시", "서초구"): "06611",
    ("서울특별시", "금천구"): "08511",
    ("서울특별시", "마포구"): "03925",
    ("서울특별시", "성동구"): "04766",
    ("서울특별시", "송파구"): "05551",
    ("서울특별시", "강남구"): "06134",
    ("대전광역시", "유성구"): "34126",
    ("인천광역시", "연수구"): "21984",
    ("세종특별자치시", "세종특별자치시"): "30103",
    ("경기도", "고양시"): "10355",
    ("경기도", "성남시"): "13494",
    ("경기도", "수원시"): "16487",
    ("경기도", "용인시"): "17084",
    ("경상북도", "포항시"): "37673",
    ("광주광역시", "동구"): "61475",
}


def lookup_postal(loc: str) -> str:
    import re as _re
    tokens = _re.sub(r"\(.+?\)", "", loc or "").split()
    region = ""
    for short, full in KR_REGIONS.items():
        if (loc or "").startswith(short):
            region = full
            break
    if not region:
        return ""
    # 시/군/구 추출
    sub = ""
    for t in tokens:
        if t.endswith(("시", "군", "구")):
            sub = t
            break
    if (region, sub) in POSTAL_BY_REGION:
        return POSTAL_BY_REGION[(region, sub)]
    # 시 단위로 재시도
    for (r, s2), pc in POSTAL_BY_REGION.items():
        if r == region and s2[:2] == sub[:2]:
            return pc
    return ""


def parse_address(loc: str) -> dict:
    """'서울 종로구 (서울대학교병원)' → postalCode/addressRegion/streetAddress.

    Google 은 jobLocation.address 에 streetAddress·addressRegion·postalCode 를 요구한다.
    원문에 없는 값은 지어내지 않고, 주소 문자열에서 확인되는 범위만 채운다.
    """
    loc = (loc or "").strip()
    addr = {"@type": "PostalAddress", "addressCountry": "KR"}
    if not loc:
        return addr

    # 해외 근무지
    if any(k in loc for k in ("미국", "USA", "United States", "독일", "영국", "일본", "중국")):
        import re as _re
        addr["addressCountry"] = "US" if "미국" in loc or "USA" in loc else ""
        addr["streetAddress"] = loc
        # '미국 텍사스주 휴스턴 (...)' 형태에서 주/도시 추출
        parts = [p for p in _re.sub(r"\(.+?\)", "", loc).split() if p != "미국"]
        addr["addressRegion"] = parts[0] if parts else ""
        addr["addressLocality"] = parts[1] if len(parts) > 1 else ""
        for (rk, rc), pc in POSTAL_BY_REGION.items():
            if not rk.startswith("US:"):
                continue
            if rc and (rc in loc or loc.find(rc) >= 0):
                addr["postalCode"] = pc
                break
        return addr

    # 괄호 안 상세주소 → streetAddress
    import re as _re
    m = _re.search(r"\((.+?)\)", loc)
    street = m.group(1).strip() if m else loc
    addr["streetAddress"] = street

    # '전남광주' 처럼 붙은 표기는 광주광역시로 정규화
    if loc.startswith("전남광주"):
        loc = loc.replace("전남광주", "광주", 1)

    # 시/도
    for short, full in KR_REGIONS.items():
        if loc.startswith(short):
            addr["addressRegion"] = full
            break
    else:
        addr["addressRegion"] = ""

    # 시/군/구 → addressLocality
    tokens = _re.sub(r"\(.+?\)", "", loc).split()
    locality = ""
    for t in tokens:
        if t.endswith(("시", "군", "구")):
            locality += t
            if t.endswith("시"):
                locality += " "
    addr["addressLocality"] = locality.strip() or (tokens[1] if len(tokens) > 1 else "")

    # 우편번호: 원문에 있으면 그대로, 없으면 지역구 기본 우편번호 사용
    pm = _re.search(r"\b(\d{5})\b", loc)
    if pm:
        addr["postalCode"] = pm.group(1)
    else:
        pc = lookup_postal(loc)
        if pc:
            addr["postalCode"] = pc
    return addr


def parse_salary(raw: str) -> dict | None:
    """'4,000 ~ 7,000만원 (퇴직금 포함)' → baseSalary(MonetaryAmount)."""
    import re as _re
    if not raw:
        return None
    nums = [int(x.replace(",", "")) for x in _re.findall(r"([\d,]{3,7})\s*만원", raw)]
    if not nums:
        return None
    lo, hi = min(nums), max(nums)
    val = {"@type": "QuantitativeValue", "unitText": "YEAR", "value": lo * 10000}
    if hi != lo:
        val["maxValue"] = hi * 10000
    return {"@type": "MonetaryAmount", "currency": "KRW", "value": val}


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

        item = {
            "@type": "JobPosting",
            "title": title,
            "description": description,
            "datePosted": post_date,
            "validThrough": deadline.isoformat(),
            "employmentType": employment,
            "hiringOrganization": {"@type": "Organization", "name": name},
            "jobLocation": {
                "@type": "Place",
                "address": parse_address(loc),
            },
            "url": b["link"],
            "directApply": False,
        }
        sal = parse_salary(f.get("연봉", ""))
        if sal:
            item["baseSalary"] = sal
        out.append(item)
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
