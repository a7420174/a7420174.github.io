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

- **Weekly Bioinformatics Job Postings**: Remote trigger (`trig_01UgCMxFR6oxHoRBqEYbfWA6`) runs every Saturday 09:00 KST (cron: `0 0 * * 6` UTC). Collects Bioinformatics & Computational Biology job postings from BRIC BioJob, JobKorea, Saramin, jobs.ac.kr, rndjob.or.kr. Uses Ralph-Loop (Planner→Editor→Validator) role-switching pipeline. Posts to `_posts/YYYY-MM-DD-Bioinformatics-채용공고-YYYY년-M월-N주차.md`.
  - **Excluded sources**: Wanted (unreliable deadlines), 하이브레인넷 (403 bot block)
  - **Scope**: Bioinformatics & Computational Biology only (no wet-lab/general biology)
  - **상시채용**: Allowed with `(상시)` label; concrete deadline postings listed first
  - **Manage**: https://claude.ai/code/scheduled/trig_01UgCMxFR6oxHoRBqEYbfWA6

- **Weekly Bioinformatics News**: Remote trigger (`trig_014R4st9j2miDXeb54bUaJzx`) runs every Saturday 09:00 KST (cron: `0 0 * * 6` UTC). Collects weekly Bioinformatics news: papers (bioRxiv MCP/PubMed MCP), tools (GitHub/Bioconductor/PyPI), conferences (ISMB/RECOMB/ASHG deadlines), industry news (Nature News/GenomeWeb/NIH). Uses parallel subagents (4 collectors) → Editor → Validator pipeline. Posts to `_posts/YYYY-MM-DD-Bioinformatics-주간뉴스-YYYY년-M월-N주차.md`.
  - **Category**: `Bioinformatics` (new)
  - **Teaser**: `/assets/images/weekly-news-teaser.svg`
  - **Prompt source**: `_automation/weekly-bioinfo-news-prompt.md`
  - **Manage**: https://claude.ai/code/scheduled/trig_014R4st9j2miDXeb54bUaJzx
