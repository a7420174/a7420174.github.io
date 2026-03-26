---
title: "AI 시대 생물정보학자의 논문 브리핑 자동화"
header:
  teaser: /assets/images/ai-agent-skill-teaser.svg
  og_image: /assets/images/orange.jpg
date: 2026-03-26T22:00:00+09:00
categories:
  - AI
tags:
  - AI
  - Automation
  - Bioinformatics
  - MCP
  - Claude Code
---

# 매일 쏟아지는 논문, 어떻게 따라갈까

생물정보학 분야에서 하루에 bioRxiv에만 수십 편의 프리프린트가 올라옵니다. 여기에 PubMed, arXiv cs.AI까지 합치면 관련 논문을 추적하는 것 자체가 하나의 업무가 됩니다.

결국 핵심은 두 가지입니다:
1. **어디서** 긁어올 것인가 (신뢰성 있는 소스)
2. **어떻게** 자동으로 받아볼 것인가 (자동화)

이 포스트에서는 Claude Code의 **Scheduled Trigger**를 이용해서 매일 아침 관련 논문 브리핑을 자동으로 받는 방법을 소개합니다.


# 신뢰성 있는 소스

| 소스 | 특징 | 접근 방법 |
|------|------|-----------|
| **bioRxiv** | 피어리뷰 전 최신 연구 | RSS, REST API, MCP Server |
| **PubMed** | 검증된 Biomedical 논문 | E-utilities API, MCP Server |
| **arXiv** | AI/ML 최신 연구 | Atom API, RSS |
| **Nature Methods** | 방법론 중심 고품질 저널 | RSS |
| **Genome Biology** | Genomics 핵심 저널 | RSS |

각 소스는 API 또는 RSS를 통해 프로그래밍 방식으로 접근할 수 있습니다.


## bioRxiv API

bioRxiv는 REST API를 제공합니다:

```bash
# 특정 날짜 범위의 bioinformatics 프리프린트 조회
curl "https://api.biorxiv.org/details/biorxiv/2026-03-25/2026-03-26"
```

RSS 피드도 있습니다:
```
https://connect.biorxiv.org/biorxiv_xml.php?subject=bioinformatics
```


## PubMed E-utilities

PubMed는 NCBI E-utilities API를 통해 검색할 수 있습니다:

```bash
# single cell RNA-seq 최신 논문 검색
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?\
db=pubmed&term=single+cell+RNA-seq&retmax=10&sort=date&retmode=json"
```

> API key를 등록하면 초당 10건까지 요청 가능합니다 (기본 3건). [NCBI 계정](https://www.ncbi.nlm.nih.gov/account/)에서 발급받을 수 있습니다.


## arXiv API

AI/ML 분야 논문은 arXiv에서 추적합니다:

```bash
# cs.AI 최신 논문 10건
curl "http://export.arxiv.org/api/query?\
search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

RSS도 제공됩니다: `https://rss.arxiv.org/rss/cs.AI`


# Claude Code Scheduled Trigger

여기서 핵심입니다. **Scheduled Trigger**는 Claude Code에서 제공하는 스케줄 기반 자동 실행 기능입니다. cron 표현식으로 실행 주기를 정하고, 프롬프트를 지정하면 Claude Code가 해당 시간에 자동으로 작업을 수행합니다.


## Trigger 생성

Claude Code CLI에서 `/schedule` 명령어로 생성합니다:

```bash
# 매일 아침 8시에 논문 브리핑 실행
claude schedule create \
  --cron "0 8 * * *" \
  --prompt "bioRxiv에서 지난 24시간 동안의 bioinformatics 프리프린트를 검색하고, \
    single-cell RNA-seq, spatial transcriptomics, LLM 관련 논문을 필터링해서 \
    상위 5편을 1~2줄로 요약한 뒤 papers-log.md에 오늘 날짜 섹션으로 추가해줘" \
  --dir /path/to/research-repo
```

## Trigger 관리

```bash
# 목록 확인
claude schedule list

# 삭제
claude schedule delete <schedule-id>
```


## Cron 표현식 참고

| 표현식 | 의미 |
|--------|------|
| `0 8 * * *` | 매일 오전 8시 |
| `0 8 * * 1-5` | 평일 오전 8시 |
| `0 */6 * * *` | 6시간마다 |
| `0 9 * * 1` | 매주 월요일 오전 9시 |


# 실전 예시: 데일리 논문 브리핑 파이프라인

Scheduled Trigger에서 MCP Server를 활용하면 API를 직접 호출하지 않아도 됩니다. 이미 설치된 bioRxiv, PubMed MCP Server가 자동으로 사용됩니다.


## 프롬프트 예시

```
다음 작업을 수행해줘:

1. bioRxiv MCP로 지난 24시간 bioinformatics 프리프린트 검색
2. PubMed MCP로 "single cell RNA-seq" OR "spatial transcriptomics" 최신 논문 검색
3. 결과에서 다음 키워드와 관련된 논문만 필터링:
   - single cell, spatial, scRNA-seq, GWAS, polygenic risk score
   - LLM, AI agent, foundation model
   - scanpy, scvi-tools, cellxgene
4. 각 논문을 제목, 저자, 1줄 요약 형식으로 정리
5. papers-log.md 파일에 오늘 날짜(## 2026-03-26) 섹션으로 추가
6. 총 몇 편을 검토했고 몇 편을 선별했는지 상단에 기록
```


## 출력 예시 (papers-log.md)

```markdown
## 2026-03-26
> 검토: 47편 / 선별: 6편

### bioRxiv
- **[Single-cell atlas of human liver aging](https://doi.org/xxx)**
  - Kim et al. | 인간 간 노화의 단일세포 수준 변화를 매핑, 면역세포 구성 변화 확인

- **[Spatial transcriptomics reveals tumor microenvironment heterogeneity](https://doi.org/xxx)**
  - Lee et al. | Visium 기반 종양 미세환경 이질성 분석, T cell exhaustion 패턴 보고

### PubMed
- **[LLM-assisted variant classification in clinical genomics](https://doi.org/xxx)**
  - Park et al. | GPT-4 기반 변이 분류 보조 시스템, ACMG 가이드라인 일치율 92%

### arXiv
- **[Foundation models for biological sequence understanding](https://arxiv.org/abs/xxx)**
  - Zhang et al. | DNA/RNA/protein 통합 foundation model, 기존 대비 벤치마크 향상
```


# Notion 연동 (선택)

논문 브리핑을 Notion 데이터베이스에 자동 정리할 수도 있습니다. Notion MCP Server가 이미 설치되어 있으므로 프롬프트에 다음을 추가합니다:

```
선별된 논문을 Notion 데이터베이스 "Paper Tracker"에 추가해줘.
속성: Title, Authors, Source (bioRxiv/PubMed/arXiv), Date, Tags, Summary
```


# 주의사항

- Scheduled Trigger는 Claude Code가 **실행 중**이어야 동작합니다. 항상 켜둘 수 없다면 **GitHub Actions** 연동을 고려하세요.
- MCP Server 가용성은 외부 서비스에 의존하므로, 중요한 워크플로우에서는 API 직접 호출(curl)을 백업으로 프롬프트에 포함하는 것이 안정적입니다.
- PubMed API는 NCBI API key 없이 초당 3건 제한이 있습니다. 매일 실행 수준에서는 문제없지만, 대량 검색 시 key 등록을 권장합니다.


# 마무리

매일 아침 커피 한 잔 하는 동안, AI가 알아서 논문을 긁어오고 요약해주는 시대입니다. 소스를 정하고, 키워드를 세팅하고, Trigger 하나 걸어두면 끝입니다.

개떡같이 프롬프트를 써도 MCP Server가 알아서 API를 호출하고, Claude가 알아서 요약해줍니다. 생물정보학자의 아침 루틴에 논문 브리핑을 자동으로 추가해보세요.


Reference
---
- [https://docs.anthropic.com/en/docs/claude-code/cli](https://docs.anthropic.com/en/docs/claude-code/cli)
- [https://docs.anthropic.com/en/docs/claude-code/sdk](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [https://api.biorxiv.org/](https://api.biorxiv.org/)
- [https://www.ncbi.nlm.nih.gov/books/NBK25500/](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- [https://info.arxiv.org/help/api/index.html](https://info.arxiv.org/help/api/index.html)
- [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
