# 주간 Bioinformatics 뉴스 자동 수집 및 발행 (OpenClaw 버전)

먼저 `/home/a7420174/.openclaw/workspace/writer/automation/COMMON.md` 를 읽고 그 지침을 따른다.

오늘 날짜 기준으로 이번 주 Bioinformatics 주간 뉴스 포스트를 수집·작성·윤문·발행한다.

## 사전 준비

1. 실행일 날짜(YYYY-MM-DD)와 이번 주 주차(해당 월의 몇 번째 토요일인지)를 계산한다.
2. 파일명: `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`
3. 기존 주간뉴스 포스트 전체 목록을 기록해 중복 제거에 활용:
   `ls /mnt/c/Users/Kim\ JaeHyun/a7420174.github.io/_posts/*주간뉴스*`
   각 포스트의 논문 제목·툴명·뉴스 제목·학회명을 읽어 블랙리스트로 만든다.

## 1단계: 수집 (4개 소스, 병렬 우선)

가능하면 `sessions_spawn`(runtime subagent, context isolated)으로 4개를 병렬 실행하고, 안 되면 순차 실행한다.
**중요**: 서브에이전트 결과는 "보고서"다. 숫자·URL·제목을 절대 새로 만들어내지 말고,
수집된 원문 값만 사용한다.

### A. 논문 (최근 7일)
- bioRxiv API(curl 사용):
  `curl -s "https://api.biorxiv.org/details/biorxiv/$(date -d '7 days ago' +%F)/$(date +%F)/0"` →
  category 가 bioinformatics / genomics / systems-biology 인 항목 상위 5건씩
- PubMed E-utilities(curl 사용, API 키 없이 초당 3회 이하로 호출):
  `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=20&term=("Nature Methods"[Journal] OR "Genome Biology"[Journal] OR "Bioinformatics"[Journal] OR "Genome Research"[Journal]) AND ("2026/11/14"[Date - Publication] : "3000"[Date - Publication])`
  → 각 PMID 를 `esummary.fcgi?db=pubmed&retmode=json&id=...` 로 요약
- 중복 제거 후 임팩트 높은 논문 + 툴/방법론 소개 논문 우선 3~5편 선별
- 각 논문: 원문 제목(영어) / 저자(성 et al.) / 저널·서버 / 한국어 1~2문장 요약 / DOI 또는 논문 페이지 URL

### B. 툴 · 소프트웨어
- web_search: "bioinformatics tool released this week site:github.com",
  "bioinformatics github trending this week", "Bioconductor new package 2026",
  "bioinformatics python package release 2026"
- 이번 주 첫 릴리즈 또는 major 업데이트 2~3개 선별 (상시 유명 툴 업데이트는 제외)
- 필터(필수):
  - GitHub 저장소는 **star 100개 미만이면 제외**. star 수 확인이 안 되면 제외.
    (확인 방법: `https://api.github.com/repos/{owner}/{repo}` → `stargazers_count`)
  - GitHub 외 툴(Bioconductor, PyPI 등)은 citation 50회 이상이거나 해당 분야에 널리 알려진
    공식 문서·튜토리얼·학회 자료가 있을 때만 포함.
- 각 항목: 툴명 / 한국어 설명 1~2문장 / 공식 URL / 주요 기능 1줄 / 인기도(⭐ star 수 또는 📄 citation 수)

### C. 컨퍼런스 · 이벤트
- web_search: "ISMB 2027 deadline", "RECOMB 2027 deadline", "ASHG 2027 abstract deadline",
  "bioinformatics conference workshop 2027 abstract deadline"
- 오늘부터 4주 이내 마감, 또는 다음 달 이내 개최되는 이벤트만. 이미 마감된 것은 제외.
- 항목: 학회명 / 개최일 / 마감일 / 공식 URL

### D. 업계 뉴스
- web_search: "bioinformatics news this week site:nature.com", "genomics news site:genomeweb.com",
  "NIH NHGRI announcement 2026", "Illumina OR 10x Genomics news 2026"
- 생물정보학 커뮤니티에 직접 영향 있는 뉴스 2~3건 (새 DB, 펀딩, 정책, 제품 등)
- Bioinformatics 와 무관한 일반 의학/생물학 뉴스는 제외
- 항목: 제목(한국어 번역) / 출처 / 원문 URL / 한국어 1~2문장 요약

## 2단계: Editor — 포스트 작성

수집 결과만 사용한다(새로운 URL·수치 생성 금지).

YAML front matter:
```yaml
---
title: "Bioinformatics 주간 뉴스 - YYYY년 M월 N주차"
date: YYYY-MM-DD
categories:
  - Bioinformatics
tags:
  - Bioinformatics
  - Computational Biology
  - 생명정보학
  - Weekly News
toc: true
toc_sticky: true
header:
  teaser: /assets/images/weekly-news-teaser.svg
---
```

본문 구조:
```
이번 주 Bioinformatics 커뮤니티 주요 소식을 모았습니다. (논문 X편, 툴 X개, 이벤트 X건, 뉴스 X건)

## 이번 주 논문

### [논문 제목]
- **저널/서버**: [저널명]
- **저자**: [저자 et al.]
- **요약**: [한국어 요약]
- **링크**: [[DOI]](URL)

## 새로운 툴 & 소프트웨어

### [툴명]
- **설명**: [한국어 설명]
- **링크**: [GitHub](URL)
- **주요 기능**: [한줄]
- **인기도**: ⭐ [star 수] (GitHub) 또는 📄 [citation 수]회 인용

## 컨퍼런스 & 이벤트

| 학회 | 개최일 | 마감 | 링크 |
|------|--------|------|------|
| [학회명] | [날짜] | [마감일] | [공식 사이트](URL) |

(이벤트 없으면: "이번 주 임박한 마감 일정이 없습니다.")

## 업계 뉴스

### [뉴스 제목 (한국어)]
- **출처**: [출처명]
- **요약**: [한국어 요약]
- **링크**: [원문](URL)
```

- 논문 3편 미만 / 툴 2개 미만이면 해당 섹션에 "이번 주는 X건 수집됨" 안내를 넣고 계속 진행한다.
- 문체는 CLAUDE.md의 기록 기준(한국어 + 영어 기술 용어, 캐주얼하면서 명료한 톤)을 따른다.

## 3단계: Validator

1. **링크 유효성**: 포스트의 모든 URL 을 web_fetch(또는 curl -I)로 확인. 404/접근 불가 링크는
   해당 아이템을 제거한다.
2. **중복 제거**: `_posts/` 의 모든 `*주간뉴스*` 포스트를 읽어 동일 논문 제목·툴명·뉴스 제목 제거.
3. **형식 검증**: front matter 7개 필드 존재 확인, 없으면 추가.
4. **날짜 정합성**: 마감일이 오늘 이전인 컨퍼런스 행 제거.
5. **수량 확인**: 최소 미달 섹션 안내 문구 추가.

## 4단계: 윤문 (COMMON.md 5절)

본문(front matter 제외)에 humanize-korean 스킬을 적용한다. 링크·URL·고유명사·수치·논문 제목은
그대로 보존한다. 윤문된 본문을 포스트 파일에 반영한다.

## 5단계: 저장 · 커밋 · 배포 · 보고

COMMON.md 6~8절을 따른다. 커밋 메시지 예:
`feat: YYYY년 M월 N주차 Bioinformatics 주간뉴스 자동 발행`
