# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jekyll-based GitHub Pages personal blog **"BI Playground"** using the **Minimal Mistakes** remote theme with a custom "Scientific Editorial" design. Content focuses on Bioinformatics, AI, and Drug Discovery. Site language is Korean.

- **URL**: https://a7420174.github.io
- **Title**: BI Playground
- **Author**: 딴생각러 ("개떡이라도 일단 AI한테 던져보기")
- **Branch**: `master` — commits here trigger automatic GitHub Pages deployment (no CI/CD config needed)

## Build & Development

```bash
# Ruby PATH (Windows)
export PATH="/c/Ruby34-x64/bin:$PATH"

# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve
# Site available at http://localhost:4000

# Build without serving
bundle exec jekyll build
```

Requires Ruby 3.4+ and Bundler. The `github-pages` gem pins Jekyll and plugin versions to match GitHub Pages.

**Note**: `wdm` gem is disabled in Gemfile (incompatible with Ruby 3.4). Windows live reload uses polling instead.

## Architecture

- **Remote theme**: `mmistakes/minimal-mistakes` — overrides in `_includes/`, `_sass/`, `_layouts/`
- **`_config.yml`**: Site metadata, author info, analytics IDs, Utterances comments, plugin list, permalink structure (`/:categories/:title/`)
- **`_posts/`**: Blog posts in `YYYY-MM-DD-Title.md` format with YAML front matter
- **`_pages/`**: Static pages (about with skill cards, custom 404, category/tag/year archives)
- **`_layouts/home.html`**: Custom home layout with hero section (DNA base animations) + paginated post list
- **`_layouts/single.html`**: Overridden to include Busuanzi page view counter
- **`_includes/head/custom.html`**: Google AdSense, custom fonts (Playfair Display, Noto Sans KR, JetBrains Mono), Busuanzi script
- **`_includes/footer/custom.html`**: Reading progress bar, back-to-top button, ad-blocker detection banner
- **`_includes/archive-single.html`**: Overridden to show teaser images in post list
- **`_includes/page__meta_custom.html`**: Busuanzi page view counter display
- **`_data/navigation.yml`**: Top nav (Posts, Categories, Tags, About)
- **`assets/css/main.scss`**: Comprehensive custom SCSS (~1000 lines) — color palette, typography, hero, post cards, code blocks, 404, skill cards, archive styling

## Design System

- **Color palette**: Teal (#1a6b5a) primary, earth tones, DNA base pair colors (A/T/G/C)
- **Typography**: Playfair Display (headings), Noto Sans KR (body), JetBrains Mono (code)
- **Code blocks**: Dark theme (#1e1e2e), rounded corners
- **Post cards**: White cards with teal accent, hover lift + gradient border
- **Hero**: Deep teal gradient with floating A/T/G/C DNA base animations

## Post Front Matter Convention

```yaml
title, date, categories, tags, toc (true), toc_sticky (true),
header.teaser, header.og_image
```

Page defaults in `_config.yml` auto-apply: `layout: single`, `author_profile: true`, `read_time: true`, `comments: true`, `share: true`.

## Post Categories & Tags

Current categories: `AI`, `Hail`, `채용공고`

Common tags: `MCP`, `AI`, `Bioinformatics`, `Computational Biology`, `LLM`, `scRNA-seq`, `Scanpy`, `Automation`, `Drug Discovery`, `RSS`, `Claude Code`, `AlphaGenome`, `DeepMind`, `CELLxGENE`, `Skill`, `Tool`, `채용`, `생명정보학`

## Key Integrations

- **Comments**: Utterances (github-light theme, pathname-based issues)
- **Analytics**: Google Analytics (GTAG: G-2EFXZE61HF), Google/Naver/Bing search console
- **AdSense**: Auto ads enabled (ca-pub-5246720880132647)
- **Search**: Google Custom Search Engine + jekyll-algolia plugin
- **Pagination**: 5 posts per page via jekyll-paginate
- **RSS**: Atom feed at /feed.xml (jekyll-feed plugin)
- **Page views**: Busuanzi counter on each post
- **Ad-blocker detection**: Polite banner in footer

## SEO / Indexing

- **Google**: No public API to push indexing for general pages (Indexing API is JobPosting/BroadcastEvent only + needs GCP). Rely on **sitemap auto-crawl** (`jekyll-sitemap` → `/sitemap.xml`, already healthy). Submit `sitemap.xml` (singular!) in GSC; manual per-URL requests are optional speedups, not required.
- **Naver / Bing — IndexNow (automated)**: On every `master` push touching `_posts/**`, [.github/workflows/indexnow.yml](.github/workflows/indexnow.yml) diffs added/modified posts and runs [_automation/submit_indexnow.py](_automation/submit_indexnow.py) to POST their URLs to `api.indexnow.org` + `searchadvisor.naver.com/indexnow`.
  - **Key file**: `/{key}.txt` at repo root (public — IndexNow keys are not secret; the file IS the ownership proof). Current key `9cf15a8b80a04134b863d5567f3d18da`; same value is hardcoded as `INDEXNOW_KEY` in the workflow.
  - **URL rule** (empirically matches live sitemap): `https://a7420174.github.io/{categories-lowercased}/{slug}/` where `slug` = filename minus `YYYY-MM-DD-` prefix and `.md` (case/Korean preserved), each segment percent-encoded.
  - **Covers all posts** (any category) — IndexNow has no content-type restriction.
  - **Prereq**: site must be registered/verified in **Naver Search Advisor** for Naver to accept pings (Bing works from the key file alone).
- **Google Indexing API (not adopted)**: setup guide kept at [_automation/google-indexing-setup.md](_automation/google-indexing-setup.md) in case GCP becomes available later.

## Writing Style

- Korean language with English technical terms (e.g., Chromatin, Pathway, Biomedical, metric)
- Casual, approachable tone — matches "개떡이라도 일단 AI한테 던져보기" vibe
- When citing external data/results, clearly mark whether it's from official docs or general knowledge
- Always verify image URLs are accessible (200 OK) before using — prefer local `/assets/images/` for reliability
- Custom SVG teasers per post stored in `/assets/images/`

## Environment

- **API keys**: Stored in `.env` (gitignored) — ALPHAGENOME_API_KEY
- **WSL**: Ubuntu available for Linux-only packages (e.g., cellxgene-census/tiledbsoma)
- **MCP Plugins**: Life Sciences marketplace (bioRxiv, PubMed, ChEMBL, ClinicalTrials, Open Targets, etc.)

## Scheduled Automation

**자동화는 Claude Code 원격 트리거가 아니라 OpenClaw(Gateway) 크론으로 동작한다.**
실행 에이전트: `writer`. 스케줄: 매주 토요일 09:00 KST (`0 9 * * 6`, tz `Asia/Seoul`).
결과 보고는 OpenClaw 대화로 돌아온다.

| 작업 | 자동화 이름 | 프롬프트 |
|------|-------------|----------|
| 주간 Bioinformatics 뉴스 | `blog-weekly-bioinfo-news` | [_automation/weekly-bioinfo-news-prompt-openclaw.md](_automation/weekly-bioinfo-news-prompt-openclaw.md) |
| 주간 Bioinformatics 채용공고 | `blog-weekly-bioinfo-jobs` | [_automation/weekly-bioinfo-jobs-prompt.md](_automation/weekly-bioinfo-jobs-prompt.md) |

공통 지침: [_automation/automation-common.md](_automation/automation-common.md)
(저장소 경로, Windows git.exe 사용법, 중복 제거, 발행 체크리스트, humanize-korean 적용, 결과 보고 형식)

### 과거 Claude Code 트리거 (참고, 더 이상 사용하지 않음)
- `trig_01UgCMxFR6oxHoRBqEYbfWA6` — 주간 채용공고 (Claude Code 원격 트리거)
- `trig_014R4st9j2miDXeb54bUaJzx` — 주간 뉴스 (Claude Code 원격 트리거)
  원본 프롬프트 원문은 Claude Code 세션 로그에 남아 있다.

### 운영 노트
- **git 조작은 Windows git.exe 로 한다.** WSL 의 `git` 에는 GitHub 자격증명이 없어 push 가 실패한다.
  `/mnt/c/Program Files/Git/cmd/git.exe` -C "C:/Users/Kim JaeHyun/a7420174.github.io"
- WSL 에는 bioRxiv/PubMed MCP 가 없다. 뉴스 수집은 `web_search` / `web_fetch` 와
  bioRxiv API · PubMed E-utilities curl 로 대체한다.
- 채용공고 수집 소스는 BRIC(ibric.org), JobKorea, Saramin, Remember Career, jobs.ac.kr, rndjob.or.kr.
  Wanted·하이브레인넷은 제외. 상시채용은 `(상시)` 라벨.
- 중복 제거 기준: 제목이 같거나, (회사명, 마감일) 쌍이 같으면 중복. 같은 회사·다른 직무·다른 마감일은 유효.
- 신규 공고 0건이면 빈 포스트를 만들지 않는다.

## 문체 규칙 — humanize-korean 스킬

블로그 본문(한국어)은 발행 직전에 **humanize-korean** 스킬로 윤문한다.
스킬: <https://github.com/epoko77-ai/im-not-ai> (MIT). OpenClaw 워크스페이스 설치 위치:
`/home/a7420174/.openclaw/workspace/writer/skills/humanize-korean/`

- 의미 불변(사실·수치·날짜·고유명사·URL 100% 보존), 장르 유지(블로그), AI 티만 제거.
- 변경률 30% 초과 경고, 50% 초과 롤백. 판정은 `scripts/verify_gates.py` 출력이 SSOT.
- 실행 절차는 [_automation/automation-common.md](_automation/automation-common.md) 5절.
