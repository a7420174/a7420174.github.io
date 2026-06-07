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

- **Weekly Bioinformatics Job Postings**: Trigger `trig_01UgCMxFR6oxHoRBqEYbfWA6`, Saturday 09:00 KST (`0 0 * * 6` UTC). Planner→Editor→Validator pipeline → `_posts/YYYY-MM-DD-Bioinformatics-채용공고-YYYY년-M월-N주차.md`. [Manage](https://claude.ai/code/scheduled/trig_01UgCMxFR6oxHoRBqEYbfWA6)
  - **Scope**: Bioinformatics & Computational Biology only (no wet-lab/general biology). **Sources**: BRIC, JobKorea, Saramin, Remember, rndjob, jobs.ac.kr. Excluded: Wanted, 하이브레인넷. 상시채용 allowed with `(상시)` label, concrete deadlines first.
  - **Duplicates**: Exclude ONLY if title exactly matches, OR (company, deadline) pair exactly matches. Same company + different role + different deadline = VALID. Same role reposted with new deadline = duplicate.
  - **Zero new postings**: do NOT create/commit an empty post.
  - **BRIC quirks**: Responses are flaky (HTTP 200 full / 200 empty / ECONNREFUSED) per sandbox instance → retry until body >1KB or fall back to WebFetch. Subagents can't reach `ibric.org`; fetch BRIC from the MAIN session. Pagination works via `?article.offset=N&articleLimit=20` (scan 0/20/40/60). Detail pages need cookies + `Referer` header. List HTML is UTF-8 but Bash stdout mangles Korean — parse with Python or WebFetch.
  - **Manual fallback**: parallel subagents (Saramin+JobKorea / Remember+rndjob+jobs.ac.kr) + BRIC in main session → Validator → commit.
  - **Trigger update API**: event object needs `{"data": {"type": "user", "message": {...}}}`; always resend full `session_context` (model `claude-opus-4-6` + git `sources`) or it resets to defaults.

- **Weekly Bioinformatics News**: Remote trigger (`trig_014R4st9j2miDXeb54bUaJzx`) runs every Saturday 09:00 KST (cron: `0 0 * * 6` UTC). Collects weekly Bioinformatics news: papers (bioRxiv MCP/PubMed MCP), tools (GitHub/Bioconductor/PyPI), conferences (ISMB/RECOMB/ASHG deadlines), industry news (Nature News/GenomeWeb/NIH). Uses parallel subagents (4 collectors) → Editor → Validator pipeline. Posts to `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`.
  - **Category**: `Bioinformatics` (new)
  - **Teaser**: `/assets/images/weekly-news-teaser.svg`
  - **Prompt source**: `_automation/weekly-bioinfo-news-prompt.md`
  - **Manage**: https://claude.ai/code/scheduled/trig_014R4st9j2miDXeb54bUaJzx
