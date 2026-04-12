# Weekly Bioinformatics News — Design Spec

**Date**: 2026-04-12  
**Author**: 딴생각러  
**Status**: Approved

---

## Overview

매주 토요일 자동으로 Bioinformatics 전공자에게 유용한 주간 뉴스 포스트를 수집·작성·발행하는 자동화 파이프라인. 논문, 툴/소프트웨어, 컨퍼런스, 업계 뉴스를 병렬 subagents로 수집한 뒤 Editor가 취합하고 Validator가 검토 후 GitHub Pages에 게시한다.

---

## Architecture

```
[토요일 09:00 KST — 새 Remote Trigger]
        │
        ├──────────────────────────────────────────┐
        │  병렬 수집 subagents (동시 실행)           │
        ▼         ▼            ▼           ▼
   [논문 Agent] [툴 Agent] [컨퍼런스  [뉴스 Agent]
   bioRxiv MCP  GitHub    Agent]      WebSearch
   PubMed MCP   Releases  ISCB/ISMB
                          RECOMB 등
        │         │            │           │
        └─────────┴────────────┴───────────┘
                        │
                        ▼
               [Editor Agent]
               취합 + 포스트 작성
                        │
                        ▼
               [Validator Agent]
               링크 유효성, 중복, 형식 검토
                        │
                        ▼
               git commit & push → GitHub Pages
```

- **트리거 스케줄**: `0 0 * * 6` (UTC) = 토요일 09:00 KST
- **채용공고 트리거(`trig_01UgCMxFR6oxHoRBqEYbfWA6`)와 완전히 독립적으로 실행**
- **파일명 패턴**: `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`

---

## Collection Agents

### 논문 Agent
- **MCP 서버**: bioRxiv MCP, PubMed MCP (Life Sciences 마켓)
- **소스**:
  - bioRxiv: 최근 7일, `bioinformatics` / `genomics` / `computational biology` 카테고리
  - PubMed: 최근 7일, Nature Methods / Genome Biology / Bioinformatics 등 high-impact 저널
- **선택 기준**: 툴·방법론 소개 논문 우선, citation potential 높은 것
- **출력**: 제목(영어), 저자, 저널/서버, 한줄 요약(한국어), DOI 링크 — **3~5편**

### 툴/소프트웨어 Agent
- **소스**: GitHub Trending (bioinformatics 태그), Bioconductor 신규 패키지, PyPI 바이오 관련, Nextflow/Snakemake 워크플로우 릴리즈
- **선택 기준**: 이번 주 첫 릴리즈 또는 major 업데이트, GitHub 스타 급증
- **출력**: 툴명, 한국어 설명, GitHub 링크, 주요 기능 한줄 — **2~3개**

### 컨퍼런스/이벤트 Agent
- **소스**: ISCB, ISMB/ECCB, RECOMB, ASHG 공식 사이트, 학회 뉴스레터
- **선택 기준**: 앞으로 4주 이내 마감 데드라인(초록/등록), 또는 다음 달 이내 개최
- **출력**: 학회명, 날짜, 마감일, 링크 — **1~3개**

### 뉴스 Agent
- **소스**: Nature News, GenomeWeb, STAT News, NIH/NHGRI 공지, 주요 기업 프레스릴리즈 (Illumina, 10x Genomics 등)
- **선택 기준**: 생물정보학 커뮤니티에 직접 영향 있는 뉴스 (새 데이터베이스, 펀딩, 정책 변화 등)
- **출력**: 제목(한국어 번역), 출처, 링크, 한줄 요약 — **2~3개**

---

## Post Format

```markdown
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

이번 주 Bioinformatics 커뮤니티 주요 소식을 모았습니다.

## 이번 주 논문

### [논문 제목 (영어)]
- **저널/서버**: bioRxiv / Nature Methods 등
- **저자**: 홍길동 et al.
- **요약**: 한국어로 한두 줄 요약
- **링크**: [DOI or 원문](https://...)

## 새로운 툴 & 소프트웨어

### [툴 이름]
- **설명**: 한국어 설명
- **GitHub**: [링크](https://github.com/...)
- **주요 기능**: 핵심 기능 한줄

## 컨퍼런스 & 이벤트

| 학회 | 날짜 | 마감 | 링크 |
|------|------|------|------|
| ISMB 2026 | 2026-07-12 | 초록 2026-04-20 | [링크](https://...) |

## 업계 뉴스

### [뉴스 제목 (한국어)]
- **출처**: Nature News
- **요약**: 한두 줄 요약
- **링크**: [원문](https://...)
```

- **언어**: 한국어 위주, 논문 제목·툴 이름은 영어 그대로
- **카테고리**: `Bioinformatics` 신규 추가 (`_config.yml` 업데이트 필요)
- **teaser 이미지**: `/assets/images/weekly-news-teaser.svg` — 매주 재사용

---

## Validator Logic

### 검증 항목
1. **링크 유효성** — 각 URL HTTP 요청으로 404/오류 확인
2. **중복 제거** — `_posts/` 최근 4주 스캔해서 동일 논문/툴 제외
3. **형식 검증** — YAML front matter 필드 누락, 섹션 최소 아이템 수 충족 여부
4. **날짜 정합성** — 컨퍼런스 마감일이 이미 지난 것 제외

### 실패 시 동작
- 아이템 최소 수량 미달(논문 3편 미만, 툴 2개 미만) → 해당 Agent 재실행 1회
- 재실행 후도 미달 → 가용한 것만으로 포스트 작성 (섹션 내 안내 문구 추가)
- 링크 404 → 해당 아이템 제거 후 발행

---

## Git Commit

```bash
git add _posts/YYYY-MM-DD-Bioinformatics-주간뉴스-*.md
git commit -m "feat: YYYY년 M월 N주차 Bioinformatics 주간뉴스 자동 발행"
git push origin master
```

---

## _config.yml 변경사항

`채용공고` 옆에 `Bioinformatics` 카테고리 추가:

```yaml
# 기존
category_archive:
  type: liquid
  path: /categories/

# _pages/category-archive.md 에 새 카테고리 링크 추가 필요
```

---

## Out of Scope

- 수집 결과 캐싱 (향후 필요 시 추가)
- 논문 전문(full-text) 요약 (초록 기반 요약만)
- 개인화 필터링 (모든 독자 대상 범용 큐레이션)
