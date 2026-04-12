# 주간 Bioinformatics 뉴스 자동 수집 및 발행

오늘 날짜 기준으로 이번 주 Bioinformatics 커뮤니티 주간 뉴스 포스트를 수집·작성·발행한다.
Working directory: `c:\Users\백인표\Documents\GitHub\a7420174.github.io`

## 사전 준비

오늘 날짜(YYYY-MM-DD)와 이번 주 주차 정보를 계산한다:
- M월 N주차: 해당 월에서 몇 번째 토요일인지 (예: 4월 두 번째 토요일 → 4월 2주차)
- 파일명: `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`

최근 4주 포스트 목록을 기록해 중복 제거에 활용한다:
```bash
ls _posts/*주간뉴스* 2>/dev/null | tail -4
```

## 1단계: 병렬 수집 — 4개 Agent 동시 실행

아래 4개 Agent를 **단일 메시지에서 동시에** 호출한다. 결과를 모두 받은 후 2단계로 진행한다.

### Agent A — 논문 수집
다음 작업을 수행하고 결과를 반환하라:
1. bioRxiv MCP `search_preprints` 도구로 최근 7일 내 category=bioinformatics, genomics, systems-biology 논문 검색 (각 카테고리 top 5씩)
2. PubMed MCP `search_articles` 도구로 최근 7일 내 저널 필터: "Nature Methods"[Journal] OR "Genome Biology"[Journal] OR "Bioinformatics"[Journal] OR "Genome Research"[Journal] 신규 논문 검색
3. 중복 제거 후 임팩트 높은 것 + 툴·방법론 소개 논문 우선으로 3~5편 선별
4. 각 논문을 아래 형식으로 반환:
   - 제목 (영어 원문)
   - 저자 (성 et al. 형식)
   - 저널/서버명
   - 한줄 요약 (한국어, 1~2문장)
   - URL (DOI 또는 논문 페이지)

### Agent B — 툴/소프트웨어 수집
다음 작업을 수행하고 결과를 반환하라:
1. WebSearch로 "bioinformatics tool released this week site:github.com" 및 "bioinformatics github trending this week" 검색
2. WebSearch로 "Bioconductor new package 2026" 및 "bioinformatics python package release 2026" 검색
3. 이번 주 첫 릴리즈 또는 major 업데이트(v1.0, v2.0 등) 2~3개 선별 (상시 유명 툴 업데이트 제외)
4. 각 툴을 아래 형식으로 반환:
   - 툴명 (영어)
   - 한국어 설명 (무엇을 하는 툴인지, 1~2문장)
   - GitHub 또는 공식 URL
   - 주요 기능/특징 1줄

### Agent C — 컨퍼런스/이벤트 수집
다음 작업을 수행하고 결과를 반환하라:
1. WebSearch로 "ISMB 2026 deadline", "RECOMB 2026 deadline", "ASHG 2026 abstract deadline" 검색
2. WebSearch로 "bioinformatics conference workshop 2026 abstract deadline" 검색
3. 오늘부터 4주 이내 마감 데드라인이 있거나, 다음 달 이내 개최되는 이벤트만 포함
4. 이미 마감된 이벤트 제외
5. 1~3개를 아래 형식으로 반환:
   - 학회명
   - 개최일 (YYYY-MM-DD 또는 YYYY-MM-DD ~ YYYY-MM-DD)
   - 마감일 (초록제출/등록 마감, YYYY-MM-DD)
   - 공식 URL

### Agent D — 업계 뉴스 수집
다음 작업을 수행하고 결과를 반환하라:
1. WebSearch로 "bioinformatics news this week site:nature.com", "genomics news 2026 site:genomeweb.com" 검색
2. WebSearch로 "NIH NHGRI announcement 2026", "Illumina OR 10x Genomics news 2026" 검색
3. 생물정보학 커뮤니티에 직접 영향 있는 뉴스 (새 데이터베이스, 펀딩, 정책, 제품 출시 등) 2~3개 선별
4. 일반 의학/생물학 뉴스(Bioinformatics 무관) 제외
5. 각 뉴스를 아래 형식으로 반환:
   - 제목 (한국어 번역)
   - 출처명 (예: Nature News, GenomeWeb)
   - 원문 URL
   - 한줄 요약 (한국어, 1~2문장)

## 2단계: Editor — 포스트 작성

수집 결과 A, B, C, D를 취합하여 아래 형식으로 마크다운 포스트를 작성한다.

**YAML front matter:**
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

**본문 구조:**
```
이번 주 Bioinformatics 커뮤니티 주요 소식을 모았습니다. (논문 X편, 툴 X개, 이벤트 X건, 뉴스 X건)

## 이번 주 논문

### [논문 제목]
- **저널/서버**: [저널명]
- **저자**: [저자 et al.]
- **요약**: [한국어 요약]
- **링크**: [[DOI]](URL)

(3~5편 반복)

## 새로운 툴 & 소프트웨어

### [툴명]
- **설명**: [한국어 설명]
- **링크**: [GitHub](URL)
- **주요 기능**: [한줄]

(2~3개 반복)

## 컨퍼런스 & 이벤트

| 학회 | 개최일 | 마감 | 링크 |
|------|--------|------|------|
| [학회명] | [날짜] | [마감일] | [공식 사이트](URL) |

(아이템 없을 경우: "이번 주 임박한 마감 일정이 없습니다." 기재)

## 업계 뉴스

### [뉴스 제목 (한국어)]
- **출처**: [출처명]
- **요약**: [한국어 요약]
- **링크**: [원문](URL)

(2~3개 반복)
```

수집 아이템이 최소 기준(논문 3편, 툴 2개) 미달이면 해당 섹션에 "이번 주는 X건 수집됨" 안내 문구를 추가하고 계속 진행한다.

## 3단계: Validator — 검증

아래 항목을 순서대로 확인한다. 이 단계는 별도 Agent로 실행하거나 직접 수행한다.

1. **링크 유효성**: 포스트 내 모든 URL에 WebFetch로 접근해서 404 또는 접근 불가인 링크를 찾는다. 404 링크는 해당 아이템을 제거하고 수정된 포스트를 반환한다.

2. **중복 제거**: `_posts/` 디렉토리에서 최근 4주 `*주간뉴스*` 포스트를 읽어서 동일한 논문 제목, 툴명, 뉴스 제목이 있으면 제거한다.

3. **형식 검증**: YAML front matter에 title, date, categories, tags, toc, header.teaser 필드가 모두 있는지 확인한다. 누락 시 추가한다.

4. **날짜 정합성**: 컨퍼런스 마감일이 오늘 이전이면 해당 행을 제거한다.

5. **수량 확인**: 논문 3편 미만이면 "이번 주 수집된 논문: X편" 안내를 섹션 상단에 추가한다. 툴 2개 미만이면 동일하게 처리한다. (재수집 없이 진행)

검증 완료된 최종 포스트 내용을 파일로 저장한다.

## 4단계: 파일 저장 및 배포

검증된 포스트를 Write 도구로 저장하고 GitHub에 푸시한다:

```bash
git add _posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md
git commit -m "feat: YYYY년 M월 N주차 Bioinformatics 주간뉴스 자동 발행"
git push origin master
```

배포 완료 후 포스트 파일명과 예상 URL(`https://a7420174.github.io/bioinformatics/Bioinformatics-주간뉴스-YYYY년-M월-N주차/`)을 출력한다.
