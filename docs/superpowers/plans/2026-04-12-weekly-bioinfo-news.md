# Weekly Bioinformatics News Automation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 매주 토요일 09:00 KST에 독립 Remote Trigger가 4개 병렬 수집 subagent → Editor → Validator 파이프라인을 실행해 Bioinformatics 주간 뉴스 포스트를 자동 발행한다.

**Architecture:** 별도 Remote Trigger (cron `0 0 * * 6`)가 4개 병렬 수집 subagent(논문/툴/컨퍼런스/뉴스)를 실행하고, Editor subagent가 취합해 마크다운 포스트를 작성하며, Validator subagent가 링크·형식·중복을 검증한 후 git push로 GitHub Pages에 배포한다. 채용공고 트리거와 완전히 독립적으로 운영한다.

**Tech Stack:** Claude Code Remote Trigger, bioRxiv MCP, PubMed MCP, WebSearch, WebFetch, Agent (subagent dispatch), Jekyll/GitHub Pages

---

## File Map

| 파일 | 동작 |
|------|------|
| `assets/images/weekly-news-teaser.svg` | Create — 포스트 썸네일, 매주 재사용 |
| `_automation/weekly-bioinfo-news-prompt.md` | Create — Remote Trigger에 붙여넣을 프롬프트 원본 |
| `CLAUDE.md` | Modify — 새 트리거 ID/설명 추가 |

---

## Task 1: Create weekly-news-teaser.svg

**Files:**
- Create: `assets/images/weekly-news-teaser.svg`

- [ ] **Step 1: Write the SVG file**

  블로그 디자인 시스템(teal #1a6b5a, earth tones)에 맞춘 800×400 썸네일. 신문/신호 모티프.

  ```xml
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#0f2a35"/>
        <stop offset="50%" style="stop-color:#1a6b5a"/>
        <stop offset="100%" style="stop-color:#134d41"/>
      </linearGradient>
      <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" style="stop-color:#c9a84c"/>
        <stop offset="100%" style="stop-color:#2d9980"/>
      </linearGradient>
    </defs>
    <rect width="800" height="400" fill="url(#bg)"/>
    <!-- Grid -->
    <g opacity="0.05" stroke="#fff" stroke-width="1">
      <line x1="0" y1="80" x2="800" y2="80"/><line x1="0" y1="160" x2="800" y2="160"/>
      <line x1="0" y1="240" x2="800" y2="240"/><line x1="0" y1="320" x2="800" y2="320"/>
      <line x1="160" y1="0" x2="160" y2="400"/><line x1="320" y1="0" x2="320" y2="400"/>
      <line x1="480" y1="0" x2="480" y2="400"/><line x1="640" y1="0" x2="640" y2="400"/>
    </g>
    <!-- Decorative circles -->
    <circle cx="680" cy="80" r="120" fill="#c9a84c" opacity="0.06"/>
    <circle cx="100" cy="320" r="80" fill="#2d9980" opacity="0.08"/>
    <!-- Signal/broadcast icon (center-left) -->
    <g transform="translate(200,200)" opacity="0.85">
      <circle cx="0" cy="0" r="14" fill="#2d9980"/>
      <path d="M-40,-40 A56,56 0 0,1 40,-40" fill="none" stroke="#2d9980" stroke-width="4" stroke-linecap="round" opacity="0.6"/>
      <path d="M-60,-60 A84,84 0 0,1 60,-60" fill="none" stroke="#2d9980" stroke-width="3" stroke-linecap="round" opacity="0.35"/>
      <path d="M-80,-80 A112,112 0 0,1 80,-80" fill="none" stroke="#2d9980" stroke-width="2" stroke-linecap="round" opacity="0.18"/>
    </g>
    <!-- Newspaper lines (right side) -->
    <g transform="translate(420,110)" opacity="0.7">
      <rect x="0" y="0" width="200" height="180" rx="6" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
      <rect x="14" y="16" width="172" height="18" rx="3" fill="rgba(201,168,76,0.4)"/>
      <rect x="14" y="46" width="80" height="8" rx="2" fill="rgba(255,255,255,0.2)"/>
      <rect x="14" y="62" width="120" height="8" rx="2" fill="rgba(255,255,255,0.15)"/>
      <rect x="14" y="78" width="100" height="8" rx="2" fill="rgba(255,255,255,0.15)"/>
      <line x1="14" y1="102" x2="186" y2="102" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
      <rect x="14" y="114" width="80" height="8" rx="2" fill="rgba(255,255,255,0.15)"/>
      <rect x="14" y="130" width="110" height="8" rx="2" fill="rgba(255,255,255,0.12)"/>
      <rect x="14" y="146" width="90" height="8" rx="2" fill="rgba(255,255,255,0.12)"/>
    </g>
    <!-- Title text -->
    <text x="60" y="290" font-family="Georgia, serif" font-size="38" font-weight="bold" fill="#fff" opacity="0.95">Bioinformatics</text>
    <text x="60" y="335" font-family="Georgia, serif" font-size="24" fill="url(#accent)" opacity="0.9">Weekly News</text>
    <!-- Accent bar -->
    <rect x="60" y="355" width="240" height="3" rx="2" fill="url(#accent)" opacity="0.7"/>
  </svg>
  ```

- [ ] **Step 2: Verify SVG renders correctly**

  브라우저에서 `assets/images/weekly-news-teaser.svg` 파일 직접 열기. 800×400 teal 배경에 신문 모티프와 텍스트가 보이면 정상.

- [ ] **Step 3: Commit**

  ```bash
  git add assets/images/weekly-news-teaser.svg
  git commit -m "feat: weekly bioinformatics news teaser SVG 추가"
  ```

---

## Task 2: Write the Remote Trigger Prompt

**Files:**
- Create: `_automation/weekly-bioinfo-news-prompt.md`

이 파일은 claude.ai/code Remote Trigger UI에 붙여넣는 프롬프트 원본이다. 버전 관리 및 재편집을 위해 repo에 보관한다.

- [ ] **Step 1: Create `_automation/` directory and write the prompt file**

  ```markdown
  # 주간 Bioinformatics 뉴스 자동 수집 및 발행

  오늘 날짜 기준으로 이번 주 Bioinformatics 커뮤니티 주간 뉴스 포스트를 수집·작성·발행한다.
  working directory: `c:\Users\백인표\Documents\GitHub\a7420174.github.io`

  ## 사전 준비

  이번 주 주차 정보를 계산한다:
  - 오늘 날짜(YYYY-MM-DD)
  - M월 N주차 (해당 월의 몇 번째 토요일인지)
  - 파일명: `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`

  최근 4주 포스트 파일명 목록을 기록해 중복 제거에 활용한다:
  ```bash
  ls _posts/*주간뉴스* 2>/dev/null | tail -4
  ```

  ## 1단계: 병렬 수집 — 4개 subagent 동시 실행

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
  3. 이번 주 첫 릴리즈 또는 major 업데이트(v1.0, v2.0 등)를 2~3개 선별 (상시 유명 툴 업데이트 제외)
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
  1. WebSearch로 "bioinformatics news this week nature.com", "genomics news 2026 site:genomeweb.com" 검색
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
  ```markdown
  이번 주 Bioinformatics 커뮤니티 주요 소식을 모았습니다. (논문 X편, 툴 X개, 이벤트 X건, 뉴스 X건)

  ## 이번 주 논문

  ### [논문 제목]
  - **저널/서버**: [저널명]
  - **저자**: [저자 et al.]
  - **요약**: [한국어 요약]
  - **링크**: [[제목 또는 'DOI']](URL)

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

  아래 항목을 순서대로 확인한다. Validator는 별도 Agent로 실행한다.

  ### Validator Agent
  다음 검증을 수행하라:

  1. **링크 유효성**: 포스트 내 모든 URL에 WebFetch로 접근해서 404 또는 접근 불가인 링크를 찾는다. 404 링크는 해당 아이템을 제거하고 수정된 포스트를 반환한다.

  2. **중복 제거**: `_posts/` 디렉토리에서 최근 4주 `*주간뉴스*` 포스트를 읽어서 동일한 논문 제목, 툴명, 뉴스 제목이 있으면 제거한다.

  3. **형식 검증**: YAML front matter에 title, date, categories, tags, toc, header.teaser 필드가 모두 있는지 확인한다. 누락 시 추가한다.

  4. **날짜 정합성**: 컨퍼런스 마감일이 오늘 이전이면 해당 행을 제거한다.

  5. **수량 확인**: 논문 3편 미만이면 "이번 주 수집된 논문: X편" 안내를 섹션 상단에 추가한다. 툴 2개 미만이면 동일하게 처리한다. (재수집 없이 진행)

  검증 완료된 최종 포스트 내용을 출력한다.

  ## 4단계: 파일 저장 및 배포

  검증된 포스트를 저장하고 GitHub에 푸시한다:

  ```bash
  # 파일 저장 (Write 도구 사용)
  # 파일명: _posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md

  git add _posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md
  git commit -m "feat: YYYY년 M월 N주차 Bioinformatics 주간뉴스 자동 발행"
  git push origin master
  ```

  배포 완료 후 포스트 파일명과 예상 URL(`https://a7420174.github.io/bioinformatics/Bioinformatics-주간뉴스-YYYY년-M월-N주차/`)을 출력한다.
  ```

- [ ] **Step 2: Verify the file was created**

  ```bash
  ls _automation/weekly-bioinfo-news-prompt.md
  wc -l _automation/weekly-bioinfo-news-prompt.md
  ```

  Expected: 파일 존재, 100줄 이상.

- [ ] **Step 3: Commit**

  ```bash
  git add _automation/weekly-bioinfo-news-prompt.md
  git commit -m "feat: 주간 Bioinformatics 뉴스 트리거 프롬프트 추가"
  ```

---

## Task 3: Register Remote Trigger

**Files:**
- Modify: `CLAUDE.md` — 트리거 ID 및 설명 추가

- [ ] **Step 1: Create the Remote Trigger via schedule skill**

  Skill tool로 `schedule` 스킬을 호출해 새 트리거를 생성한다.

  - **Name**: `weekly-bioinfo-news`
  - **Schedule**: `0 0 * * 6` (매주 토요일 00:00 UTC = 09:00 KST)
  - **Prompt**: `_automation/weekly-bioinfo-news-prompt.md` 파일 전체 내용을 붙여넣음
  - **Working directory**: `c:\Users\백인표\Documents\GitHub\a7420174.github.io`

  트리거 생성 후 발급된 **trigger ID** (형식: `trig_XXXX`)를 기록한다.

- [ ] **Step 2: Update CLAUDE.md with new trigger info**

  `CLAUDE.md`의 `## Scheduled Automation` 섹션에 아래 내용을 추가한다 (채용공고 항목 바로 아래):

  ```markdown
  - **Weekly Bioinformatics News**: Remote trigger (`trig_XXXX`) runs every Saturday 09:00 KST (cron: `0 0 * * 6` UTC). Collects Bioinformatics weekly news: papers (bioRxiv/PubMed), tools (GitHub/Bioconductor), conferences (ISMB/RECOMB/ASHG), industry news (Nature News/GenomeWeb). Uses parallel subagents (4 collectors) → Editor → Validator pipeline. Posts to `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`.
    - **Category**: `Bioinformatics` (new)
    - **Teaser**: `/assets/images/weekly-news-teaser.svg`
    - **Manage**: https://claude.ai/code/scheduled/trig_XXXX
  ```

  `trig_XXXX`를 실제 발급된 ID로 교체한다.

- [ ] **Step 3: Commit CLAUDE.md update**

  ```bash
  git add CLAUDE.md
  git commit -m "docs: 주간 Bioinformatics 뉴스 트리거 정보 CLAUDE.md에 추가"
  ```

---

## Task 4: Manual Test Run

트리거를 등록한 직후 수동으로 1회 실행해서 전체 파이프라인을 검증한다.

- [ ] **Step 1: Trigger manual run**

  claude.ai/code → Scheduled 메뉴 → `weekly-bioinfo-news` 트리거 → "Run now" 실행.
  
  또는 CLI에서:
  ```bash
  # schedule 스킬로 manual trigger 실행
  ```

- [ ] **Step 2: Verify output**

  실행 완료 후 아래를 확인한다:
  - `_posts/` 에 `*Bioinformatics-주간뉴스*` 파일이 생성됐는가?
  - YAML front matter가 올바른가? (`cat _posts/*주간뉴스*.md | head -20`)
  - GitHub Pages에 배포됐는가? (push 로그 확인)
  - 포스트 내 링크 중 404가 있는가? (Validator가 처리했어야 함)

  ```bash
  ls _posts/*주간뉴스* 
  head -20 _posts/*주간뉴스*.md
  git log --oneline -3
  ```

- [ ] **Step 3: If test post is a duplicate/test, clean up**

  테스트 실행 결과물을 실제 발행 포스트로 유지하거나, 테스트용임을 확인했으면 삭제:

  ```bash
  # 유지할 경우: 아무것도 안 해도 됨
  # 삭제할 경우:
  git rm _posts/YYYY-MM-DD-Bioinformatics-주간뉴스-*.md
  git commit -m "chore: 수동 테스트 포스트 제거"
  git push origin master
  ```

---

## Self-Review

### Spec Coverage Check

| 스펙 요구사항 | 구현 태스크 |
|---|---|
| 독립 Remote Trigger, cron `0 0 * * 6` | Task 3 Step 1 |
| 4개 병렬 수집 subagent | Task 2 Step 1 (Agent A/B/C/D) |
| 논문: bioRxiv MCP + PubMed MCP, 3~5편 | Task 2 — Agent A |
| 툴: GitHub/Bioconductor/PyPI, 2~3개 | Task 2 — Agent B |
| 컨퍼런스: ISMB/RECOMB/ASHG, 1~3개 | Task 2 — Agent C |
| 뉴스: Nature News/GenomeWeb 등, 2~3개 | Task 2 — Agent D |
| Editor가 취합해 포스트 작성 | Task 2 — 2단계 Editor |
| Validator: 링크·중복·형식·날짜 검증 | Task 2 — 3단계 Validator |
| 한국어 위주, 제목/툴명은 영어 | Task 2 — Editor 형식 지정 |
| 카테고리: `Bioinformatics` | Task 2 — YAML front matter |
| teaser: `weekly-news-teaser.svg` | Task 1, Task 2 |
| git commit + push | Task 2 — 4단계 |
| CLAUDE.md 문서화 | Task 3 Step 2 |
| 수동 테스트 | Task 4 |

모든 요구사항이 태스크에 매핑됨. 누락 없음.

### Placeholder Scan

- "TBD", "TODO" 없음
- 모든 코드 스텝에 실제 코드/명령어 포함됨
- `trig_XXXX` 는 의도적인 placeholder — Step 1 완료 후 실제 ID로 교체하는 지시가 명시됨

### Type Consistency

- 파일명 패턴 `YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md` 전 태스크 일관 사용
- SVG 경로 `/assets/images/weekly-news-teaser.svg` 전 태스크 일관 사용
