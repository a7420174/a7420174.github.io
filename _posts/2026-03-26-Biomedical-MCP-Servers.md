---
title: "AI × Biomedical: MCP Server로 연결하는 Biomedical Tools"
header:
  teaser: https://modelcontextprotocol.io/images/og-image.png
  og_image: https://modelcontextprotocol.io/images/og-image.png
date: 2026-03-26T20:00:00+09:00
categories:
  - AI
tags:
  - MCP
  - AI
  - Bioinformatics
  - LLM
  - Tool
---

# Model Context Protocol (MCP)란?

LLM이 아무리 똑똑해져도, 외부 데이터에 접근하지 못하면 할 수 있는 일이 제한됩니다. 논문을 검색하거나, 약물 데이터베이스를 조회하거나, 임상시험 정보를 가져오려면 LLM이 직접 외부 시스템과 소통할 수 있어야 합니다.

**Model Context Protocol (MCP)**은 Anthropic에서 2024년 11월에 발표한 오픈 표준으로, AI 모델과 외부 데이터 소스 및 도구를 연결하는 프로토콜입니다. JSON-RPC 기반의 통신을 통해 **Client** (Claude, Cursor 등 AI 앱)와 **Server** (도구 제공자) 간의 양방향 연결을 가능하게 합니다. 2025년 12월에는 Linux Foundation 산하 **Agentic AI Foundation (AAIF)**에 기증되어 Anthropic, Block, OpenAI가 공동으로 관리하고 있습니다.

<center>
  <img src="https://modelcontextprotocol.io/images/mcp-simple-diagram.png" alt="MCP Architecture" width="700"/>
  <br>
  <b>
    < MCP Architecture >
  </b>
</center>
<br>

MCP Server는 세 가지 요소를 제공합니다:
- **Tools**: 실행 가능한 함수 (예: 논문 검색, 화합물 조회)
- **Resources**: 데이터 및 콘텐츠 (예: 데이터베이스 레코드)
- **Prompts**: 템플릿화된 상호작용 (예: 분석 워크플로우)

쉽게 말하면, MCP는 LLM에게 "손과 발"을 달아주는 역할을 합니다. 이제 LLM이 직접 PubMed에서 논문을 검색하고, ChEMBL에서 약물 정보를 가져오고, 임상시험 데이터를 분석할 수 있게 된 것입니다.


# Biomedical MCP Servers

2025년 10월, Anthropic은 **Claude for Life Sciences**를 출시하면서 생명과학 분야에 특화된 MCP 커넥터들을 대거 공개했습니다. 그 중 대표적인 것들을 소개합니다.


## 1) ToolUniverse

[**ToolUniverse**][1]는 Harvard Medical School의 **Zitnik Lab**에서 개발한 AI scientist 생태계입니다. LLM이 600개 이상의 과학 도구(ML 모델, 데이터셋, API, 패키지)를 직접 호출할 수 있도록 **Scientific Model Context Protocol (SMCP)**을 구현했습니다.

<center>
  <img src="https://arxiv.org/html/2509.23426v2/x1.png" alt="ToolUniverse" width="700"/>
  <br>
  <b>
    < ToolUniverse Overview >
  </b>
</center>
<br>

주요 특징:
- **600+ 과학 도구** 통합: 약물 발견, 정밀 종양학, 희귀 질환 진단, 약물 감시 등
- **68개 사전 구축 연구 워크플로우** 제공
- 단백질 도킹, 분자 시뮬레이션 등 **비동기 장시간 작업** 지원
- GPT, Claude, Gemini 등 **모든 LLM과 호환**

예를 들어, "특정 단백질 타겟에 대한 약물 후보를 찾아줘"라고 요청하면, ToolUniverse가 자동으로 적절한 도구를 선택하여 화합물 스크리닝, ADMET 예측, 도킹 시뮬레이션까지 순차적으로 수행할 수 있습니다.


## 2) Open Targets

[**Open Targets**][2]는 **EMBL-EBI**와 **Wellcome Sanger Institute**가 공동 운영하는 약물 타겟 발굴 플랫폼입니다. GSK, Pfizer, Sanofi 등 글로벌 제약사들이 파트너로 참여하고 있습니다. 2026년 1월에 공식 MCP Server를 공개했습니다.

주요 기능:
- **20개 이상의 데이터 소스**에서 타겟-질병 연관성 점수 산출
- GWAS Catalog, UK Biobank, FinnGen 등 **유전학적 근거** 통합
- Reactome 기반 **Pathway 데이터** 제공
- ChEMBL 및 ClinicalTrials.gov 기반 **임상 근거** 연계

```
예시 질의: "BRCA1과 연관된 질병과 현재 진행 중인 임상시험을 알려줘"
→ Open Targets MCP가 타겟-질병 연관성, 유전학적 근거, 관련 약물 정보를 한 번에 반환
```


## 3) ChEMBL

[**ChEMBL**][3]은 EMBL-EBI에서 관리하는 세계 최대의 생물활성 화합물 데이터베이스입니다. **240만 개 이상의 화합물**, **1,600만 건 이상의 생물활성 데이터**를 보유하고 있습니다.

MCP Server를 통해 가능한 작업:
- 이름, SMILES 구조, ChEMBL ID로 **화합물 검색**
- IC50, EC50, Ki 등 **생물활성 데이터** 조회
- 약물의 **작용 메커니즘** 및 타겟 정보 확인
- **ADMET 속성** (약동학 및 안전성) 예측

## 4) ClinicalTrials.gov

[**ClinicalTrials.gov**][4]는 NIH/NLM에서 운영하는 세계 최대의 임상시험 등록부입니다. MCP Server를 통해 임상시험 데이터를 AI로 직접 분석할 수 있습니다.

주요 활용:
- 질환, 약물, 지역, 스폰서별 **임상시험 검색**
- 시험 설계, 적격 기준, 결과 지표 등 **상세 프로토콜** 조회
- 경쟁 파이프라인 분석 및 **연구자/사이트 탐색**


## 5) PubMed

[**PubMed**][5]는 NCBI/NLM에서 운영하는 **3,600만 건 이상**의 Biomedical 문헌 검색 엔진입니다.

MCP Server를 통해 가능한 작업:
- MeSH term, 날짜 범위, 저널 필터 등을 활용한 **정밀 검색**
- 초록, 저자, 인용 정보 등 **메타데이터 추출**
- PubMed Central의 **전문(Full-text) 접근** (오픈 액세스)
- 관련 논문 탐색 및 **인용 네트워크** 분석


## 6) bioRxiv

[**bioRxiv**][6]는 Cold Spring Harbor Laboratory에서 운영하는 생명과학 **프리프린트 서버**입니다. 자매 서버인 **medRxiv** (의학 분야)도 함께 지원합니다.

MCP Server를 통해 가능한 작업:
- 키워드, 저자, 날짜 범위별 **프리프린트 검색**
- DOI로 **상세 정보** (메타데이터, 초록, PDF 링크) 조회
- 프리프린트의 **정식 출판 여부** 확인
- 연구 펀딩 소스별 검색


# Multi-Tool Workflows

개별 MCP Server도 유용하지만, 여러 서버를 조합하면 진정한 위력을 발휘합니다.

예를 들어, 특정 질병에 대한 약물 후보를 탐색하는 워크플로우를 생각해봅시다:

1. **Open Targets**에서 질병-타겟 연관성 조회
2. **ChEMBL**에서 해당 타겟에 활성을 보이는 화합물 검색
3. **ClinicalTrials.gov**에서 관련 임상시험 진행 현황 파악
4. **PubMed**에서 최신 연구 논문 검색
5. **bioRxiv**에서 아직 출판되지 않은 최신 프리프린트 확인

이 모든 과정을 AI한테 자연어로 요청하면, MCP Server들이 알아서 데이터를 수집하고 종합해줍니다. 개떡같이 말해도 찰떡같이 알아듣는 셈이죠.


# 마무리

MCP의 등장으로 LLM과 전문 데이터베이스 사이의 벽이 사라지고 있습니다. 특히 생물정보학, 약물 발견, 임상 연구 분야에서 AI 활용의 문턱이 크게 낮아졌습니다. ToolUniverse처럼 600개 이상의 과학 도구를 하나의 프로토콜로 연결하는 시도는, 앞으로 AI가 과학 연구의 동반자로 자리잡는 데 중요한 이정표가 될 것입니다.

일단 던져보세요. AI가 알아서 찾아줄 테니까요.


Reference
---
- [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)
- [https://www.anthropic.com/news/claude-for-life-sciences](https://www.anthropic.com/news/claude-for-life-sciences)
- [https://github.com/mims-harvard/ToolUniverse](https://github.com/mims-harvard/ToolUniverse)
- [https://zitniklab.hms.harvard.edu/ToolUniverse/](https://zitniklab.hms.harvard.edu/ToolUniverse/)
- [https://blog.opentargets.org/official-open-targets-mcp/](https://blog.opentargets.org/official-open-targets-mcp/)
- [https://www.opentargets.org/](https://www.opentargets.org/)
- [https://www.ebi.ac.uk/chembl/](https://www.ebi.ac.uk/chembl/)
- [https://clinicaltrials.gov/](https://clinicaltrials.gov/)
- [https://pubmed.ncbi.nlm.nih.gov/](https://pubmed.ncbi.nlm.nih.gov/)
- [https://www.biorxiv.org/](https://www.biorxiv.org/)


[1]:https://github.com/mims-harvard/ToolUniverse
[2]:https://www.opentargets.org/
[3]:https://www.ebi.ac.uk/chembl/
[4]:https://clinicaltrials.gov/
[5]:https://pubmed.ncbi.nlm.nih.gov/
[6]:https://www.biorxiv.org/
