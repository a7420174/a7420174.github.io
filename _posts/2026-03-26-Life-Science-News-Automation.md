---
title: "신약개발 뉴스 자동화: RSS + MCP로 매일 브리핑 받기"
header:
  teaser: /assets/images/daily-briefing-teaser.svg
  og_image: /assets/images/orange.jpg
date: 2026-03-26T23:00:00+09:00
categories:
  - AI
tags:
  - AI
  - Automation
  - Drug Discovery
  - RSS
  - MCP
---

# 왜 웹검색이 아닌 RSS인가

이전 포스트에서 논문 브리핑 자동화를 다뤘다면, 이번에는 **뉴스** 모니터링입니다.

LLM의 웹검색 기능으로 뉴스를 가져올 수도 있지만 문제가 있습니다:

| 방법 | 신뢰성 | 문제점 |
|------|--------|--------|
| **LLM 웹검색** | 낮음 | 환각 위험, 출처 불명확, 결과 재현 불가 |
| **웹 스크래핑** | 중간 | 사이트 구조 변경 시 깨짐 |
| **RSS 피드** | 높음 | 매체가 공식 발행, 구조화된 데이터 |
| **공식 API** | 높음 | 인증 필요하지만 가장 안정적 |

**RSS가 뉴스 모니터링에 가장 적합합니다.** 이유:
- 매체가 직접 발행하므로 **출처가 명확**
- XML 포맷으로 **파싱이 쉬움**
- 새 글이 올라오면 자동 반영
- 별도 인증 없이 접근 가능


# 생명과학 / 신약개발 뉴스 RSS

실제로 확인한 RSS 피드 목록입니다.

## 신약개발 / 바이오텍 뉴스

| 매체 | RSS URL | 특징 |
|------|---------|------|
| **STAT News** | `https://www.statnews.com/feed/` | 바이오텍·제약 심층 보도 |
| **FierceBiotech** | `https://www.fiercebiotech.com/rss/xml` | 바이오텍 산업 뉴스 |
| **FiercePharma** | `https://www.fiercepharma.com/rss/xml` | 제약 산업 뉴스 |
| **Endpoints News** | `https://endpoints.news/feed/` | 신약개발 전문 |
| **BioPharma Dive** | `https://www.biopharmadive.com/feeds/news/` | 바이오파마 비즈니스 |


## 학술 저널 뉴스

Nature에서는 분야별 RSS를 제공합니다:

| 저널 | RSS URL |
|------|---------|
| **Nature Biotechnology** | `https://www.nature.com/nbt.rss` |
| **Nature Reviews Drug Discovery** | `https://www.nature.com/nrd.rss` |
| **Nature Medicine** | `https://www.nature.com/nm.rss` |
| **Drug Discovery (Subject)** | `https://www.nature.com/subjects/drug-discovery.rss` |


## 규제 / 정부 소스

| 소스 | RSS URL | 특징 |
|------|---------|------|
| **FDA 보도자료** | `https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml` | 승인, 경고, 가이던스 |
| **ScienceDaily 제약** | `https://www.sciencedaily.com/rss/health_medicine/pharmaceuticals.xml` | 일반 과학 뉴스 |
| **ScienceDaily 유전자치료** | `https://www.sciencedaily.com/rss/health_medicine/gene_therapy.xml` | 유전자치료 뉴스 |


## AI 뉴스

| 매체 | RSS URL | 비고 |
|------|---------|------|
| **OpenAI Blog** | `https://openai.com/blog/rss.xml` | |
| **Google AI Blog** | `https://blog.google/technology/ai/rss/` | |
| **DeepMind Blog** | `https://deepmind.google/blog/rss.xml` | |
| **Anthropic Blog** | N/A | RSS 미제공 |

> Anthropic은 아직 RSS를 제공하지 않습니다. 웹 스크래핑이나 주기적 체크가 필요합니다.


# RSS를 MCP로 읽기

RSS 피드를 직접 파싱할 수도 있지만, **RSS MCP Server**를 사용하면 Claude가 자연어로 피드를 읽을 수 있습니다.

커뮤니티에서 제공하는 RSS MCP Server들:

| 프로젝트 | Stars | 설명 |
|----------|:-----:|------|
| [veithly/rss-mcp](https://github.com/veithly/rss-mcp) | 31 | RSS/Atom 피드 파싱, RSSHub 지원 |
| [imprvhub/mcp-rss-aggregator](https://github.com/imprvhub/mcp-rss-aggregator) | 24 | Claude Desktop용 RSS 집계 |
| [richardwooding/feed-mcp](https://github.com/richardwooding/feed-mcp) | 19 | RSS, Atom, JSON 피드 지원 |

> 모두 커뮤니티 MCP입니다. 공식 RSS MCP Server는 아직 없습니다.


# 자동화 파이프라인

논문 브리핑 포스트에서 다룬 Scheduled Trigger를 그대로 활용합니다.

```bash
claude schedule create \
  --cron "0 8 * * 1-5" \
  --prompt "다음 RSS 피드에서 지난 24시간 뉴스를 가져와줘:
    - https://www.statnews.com/feed/
    - https://www.fiercebiotech.com/rss/xml
    - https://endpoints.news/feed/
    - https://www.nature.com/subjects/drug-discovery.rss
    - https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml

    결과에서 다음 키워드 관련 뉴스를 필터링해줘:
    - 신약 승인, FDA approval, clinical trial
    - AI drug discovery, precision medicine
    - gene therapy, cell therapy, antibody
    - single cell, spatial transcriptomics

    각 뉴스를 제목, 매체, 1줄 요약 형식으로 정리하고
    news-log.md에 오늘 날짜 섹션으로 추가해줘" \
  --dir /path/to/research-repo
```


## 출력 예시 (news-log.md)

```markdown
## 2026-03-26 (수)
> 소스: 5개 피드 / 전체: 34건 / 선별: 7건

### FDA / 규제
- **[FDA Approves First AI-Guided Companion Diagnostic for NSCLC](https://...)**
  - FDA | AI 기반 동반진단 최초 승인, 비소세포폐암 바이오마커 분석

### 신약개발
- **[Lilly's Obesity Drug Shows Promise in Phase 3 Heart Failure Trial](https://...)**
  - STAT News | 릴리 비만 약물, 심부전 3상에서 유의미한 결과

- **[Small Biotech Lands $200M for AI-Driven Antibody Platform](https://...)**
  - Endpoints | AI 항체 플랫폼 스타트업 2억 달러 투자 유치

### AI + Bio
- **[DeepMind Releases Open-Source Protein Interaction Model](https://...)**
  - FierceBiotech | AlphaFold 후속 모델, 단백질 상호작용 예측 오픈소스 공개

### 학술
- **[Spatial multi-omics reveals drug resistance mechanisms in solid tumors](https://...)**
  - Nature Drug Discovery | 공간 멀티오믹스로 고형암 약물 내성 기전 규명
```


# 논문 + 뉴스 통합 브리핑

이전 포스트의 논문 브리핑과 합칠 수도 있습니다. 하나의 Trigger에서 두 작업을 순차 실행:

```
1. [논문] bioRxiv, PubMed, arXiv MCP로 최신 논문 검색 및 요약
2. [뉴스] RSS 피드에서 신약개발 뉴스 수집 및 요약
3. daily-briefing.md에 "## 논문"과 "## 뉴스" 섹션으로 나누어 기록
```

매일 아침 하나의 파일에서 논문과 뉴스를 한눈에 확인할 수 있습니다.


# RSS가 없는 소스는?

| 소스 | 상태 | 대안 |
|------|------|------|
| **GenomeWeb** | 페이월, RSS 없음 | 이메일 뉴스레터 구독 |
| **Anthropic Blog** | RSS 미제공 | 주기적 웹 체크 또는 GitHub releases 모니터링 |
| **Reddit** | RSS 차단 (403) | Reddit API (OAuth2 필요) 또는 포기 |
| **Twitter/X** | 무료 API 폐지 | 유료 API ($100/월) 또는 포기 |

현실적으로 RSS가 없는 소스는 **이메일 뉴스레터**로 대체하는 게 가장 깔끔합니다. 추천 뉴스레터:
- **TLDR AI** — AI 뉴스 일간 요약
- **The Batch (Andrew Ng)** — AI 주간 요약
- **Drug Hunter** — 신약개발 주간 큐레이션


# 마무리

정리하면:

| 정보 유형 | 소스 | 접근 방법 |
|-----------|------|-----------|
| **논문** | bioRxiv, PubMed, arXiv | MCP Server |
| **뉴스** | STAT, Fierce, Endpoints, FDA | RSS 피드 |
| **AI 동향** | OpenAI, Google AI, DeepMind 블로그 | RSS 피드 |
| **나머지** | GenomeWeb, Anthropic 등 | 뉴스레터 구독 |

웹검색에 의존하지 않고, 공식 소스에서 구조화된 데이터를 가져오는 것이 핵심입니다. RSS는 20년 넘은 기술이지만, AI 자동화 시대에 오히려 가장 신뢰할 수 있는 데이터 파이프라인입니다.


Reference
---
- [https://www.statnews.com/feed/](https://www.statnews.com/feed/)
- [https://www.fiercebiotech.com/rss/xml](https://www.fiercebiotech.com/rss/xml)
- [https://endpoints.news/feed/](https://endpoints.news/feed/)
- [https://www.biopharmadive.com/feeds/news/](https://www.biopharmadive.com/feeds/news/)
- [https://www.nature.com/subjects/drug-discovery.rss](https://www.nature.com/subjects/drug-discovery.rss)
- [https://github.com/veithly/rss-mcp](https://github.com/veithly/rss-mcp)
