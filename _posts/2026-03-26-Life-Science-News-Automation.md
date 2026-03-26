---
title: "신약개발 뉴스 자동화: RSS로 매일 브리핑 받기"
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
  - Claude Code
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



# 자동화 파이프라인

RSS는 별도의 MCP Server 없이 `curl`만으로 가져올 수 있습니다. Scheduled Trigger 프롬프트 안에서 RSS URL을 지정하면 Claude가 알아서 피드를 읽고 파싱합니다.

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

아래는 2026년 3월 26일에 STAT News, Endpoints News RSS 피드에서 실제 가져온 결과입니다.

```markdown
## 2026-03-26 (수)
> 소스: STAT News, Endpoints News RSS

### 신약개발 / 임상
- **[Allogene's off-the-shelf CAR-T is nearing an early but pivotal study readout](https://www.statnews.com/2026/03/26/allogene-car-t-lymphoma-treatment-study/)**
  - STAT News | Allogene의 기성품(off-the-shelf) CAR-T 세포치료제, 림프종 대상 핵심 임상 결과 임박

- **[FDA gives Denali accelerated approval for rare disease drug](https://endpoints.news/fda-gives-denali-accelerated-approval-for-rare-disease-drug/)**
  - Endpoints | Denali Therapeutics 희귀질환 약물 FDA 가속 승인 획득

- **[Oral peptides biotech Pinnacle Medicines gets $89M from US, China investors](https://endpoints.news/oral-peptides-biotech-pinnacle-medicines-gets-89m-from-us-china-investors/)**
  - Endpoints | 경구 펩타이드 바이오텍 Pinnacle Medicines, 미·중 투자자로부터 8,900만 달러 유치

### AI + 헬스케어
- **[Data show people racing to chatbots for health advice](https://www.statnews.com/2026/03/26/data-show-people-racing-to-chatbots-health-tech/)**
  - STAT News | 건강 상담 목적 챗봇 사용 급증 추세 데이터 공개

- **[Limbic aims to show AI beats humans in delivering therapy](https://endpoints.news/limbic-aims-to-show-ai-beats-humans-in-delivering-therapy/)**
  - Endpoints | AI 치료 전달이 인간 치료사를 능가할 수 있는지 검증 시도
```


# 논문 + 뉴스 통합 브리핑

이전 포스트의 논문 브리핑과 합칠 수도 있습니다. 하나의 Trigger에서 두 작업을 순차 실행:

```
1. [논문] bioRxiv, PubMed, arXiv MCP로 최신 논문 검색 및 요약
2. [뉴스] RSS 피드에서 신약개발 뉴스 수집 및 요약
3. daily-briefing.md에 "## 논문"과 "## 뉴스" 섹션으로 나누어 기록
```

매일 아침 하나의 파일에서 논문과 뉴스를 한눈에 확인할 수 있습니다.



# 마무리

정리하면:

웹검색에 의존하지 않고, 공식 소스에서 구조화된 데이터를 가져오는 것이 핵심입니다. RSS는 20년 넘은 기술이지만, AI 자동화 시대에 오히려 가장 신뢰할 수 있는 데이터 파이프라인입니다.


Reference
---
- [https://www.statnews.com/feed/](https://www.statnews.com/feed/)
- [https://www.fiercebiotech.com/rss/xml](https://www.fiercebiotech.com/rss/xml)
- [https://endpoints.news/feed/](https://endpoints.news/feed/)
- [https://www.biopharmadive.com/feeds/news/](https://www.biopharmadive.com/feeds/news/)
- [https://www.nature.com/subjects/drug-discovery.rss](https://www.nature.com/subjects/drug-discovery.rss)
