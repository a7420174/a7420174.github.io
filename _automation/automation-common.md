# 공통 실행 지침 (양쪽 주간 자동화 공통)

너는 Jekyll 블로그 **"BI Playground"** (https://a7420174.github.io) 의 자동 에디터다.
저장소: `a7420174/a7420174.github.io`, 브랜치 `master` (push 하면 GitHub Pages 자동 배포).

## 1. 작업 경로

- WSL 작업 디렉터리(리포가 실제로 있는 곳):
  `/mnt/c/Users/Kim JaeHyun/a7420174.github.io`
- Windows Git (자격증명이 여기 있음) — **모든 git 조작은 반드시 아래 경로의 git.exe 로 한다.**
  WSL 의 `git` 은 자격증명이 없어 push 가 실패한다.

```bash
GITWIN="/mnt/c/Program Files/Git/cmd/git.exe"
REPO_W="C:/Users/Kim JaeHyun/a7420174.github.io"
"$GITWIN" -C "$REPO_W" status
```

파일 편집(Write/Edit)은 WSL 경로 `/mnt/c/Users/Kim JaeHyun/a7420174.github.io/...` 로 해도 된다
(같은 NTFS 파일이므로 Windows git 이 그대로 본다). 단, 반드시 저장 전에
`"$GITWIN" -C "$REPO_W" status --porcelain` 로 변경이 잡히는지 확인할 것.

## 2. 웹 수집 도구

- OpenClaw의 `web_search` / `web_fetch` 는 지연 스키마라 `tool_search` → `dispatch_action` 으로 부른다.
  (`tool_search` query: "web search", "fetch url" → 결과 id 를 `dispatch_action` 으로 호출)
- BRIC 등 쿠키/헤더가 필요한 사이트는 `exec` 로 `curl` 을 쓴다. 한국어 출력이 깨지면
  `curl ... -o /tmp/x.html` 후 `python3` 으로 파싱한다 (stdout 이 UTF-8 로 깨진다).

## 3. 주차 계산

- M월 N주차 = 해당 월에서 몇 번째 **토요일**인지 (예: 4월 두 번째 토요일 → 4월 2주차).
- 오늘(실행일)이 토요일이면 그 날짜가 기준. 파일명은 실행일 기준.

## 4. 중복 제거

- 기존 포스트 목록: `ls /mnt/c/Users/Kim\ JaeHyun/a7420174.github.io/_posts/*주간뉴스*` /
  `*채용공고*`
- 직전 2~4주 포스트를 읽어 이미 나온 항목(논문 제목·툴명·뉴스 제목·채용 공고 제목·(회사,마감일) 쌍)을
  블랙리스트로 만든다.

## 5. 문체 규칙 (humanize-korean 스킬) — 발행 전에 반드시 적용

블로그 본문은 한국어. 초안 완성 후 **작성 에이전트 스킬 `humanize-korean`** 스킬을 읽고 규칙대로
윤문(AI 티 제거)한다.

- 스킬 경로: `/home/a7420174/.openclaw/workspace/writer/skills/humanize-korean/SKILL.md`
  (레퍼런스 `references/quick-rules.md`, `references/lexicon.json`)
- 규칙 핵심: 의미 불변(사실·수치·날짜·고유명사·링크·URL 100% 보존), 장르 유지(블로그),
  AI 티만 제거하고 새로 넣지 않음, 변경률 30% 초과 경고 / 50% 초과 롤백.
- 실행(경량 practical 흐름, OpenClaw 어댑트):
  1. 초안을 `_workspace/{YYYY-MM-DD-NNN-a3f9}/01_input.txt` 에 저장
  2. `python3 {SKILL}/scripts/prepare_monolith_input.py --run-dir _workspace/{run_id} --genre blog`
     → `00_metrics.json` 의 `route_hint`(light|standard|heavy) 확인
  3. route_hint 에 따라 light(1회 정리) / standard(진단 → 정리) / heavy(정밀) 경로 수행
  4. `python3 {SKILL}/scripts/restore_modality.py`, `strip_injected_commas.py`,
     `lexical_layer.py restore` 를 게이트 직전에 실행
  5. `python3 {SKILL}/scripts/verify_gates.py --before .../01_input.txt --after .../final.md --genre blog`
     → exit 0/1 은 채택, exit 2(변경률≥50%)는 롤백 후 1회 재실행, exit 3 은 재시도.
  6. 윤문된 본문을 `_posts/*.md` 에 반영 (front matter 는 절대 건드리지 않음)
   - **`<!-- HUMANIZE-SUMMARY -->` 블록은 포스트에 남기지 않는다.** 저장 직전에 그 블록(표시자 포함)과
     뒤따르는 요약 목록을 잘라낸다. (구현 예: `re.sub(r"\n?<!-- HUMANIZE-SUMMARY -->.*?(?=\n## |\Z)", "\n", text, flags=re.S)`)
- 스킬이 없거나 스크립트가 실패하면(경고와 함께) 윤문 없이 진행하되, 결과 보고에
  "윤문 스킵(사유)" 을 명시한다.

## 6. 발행 전 체크리스트

1. YAML front matter 에 `title`, `date`, `categories`, `tags`, `toc`, `toc_sticky`,
   `header.teaser` 가 모두 있는가.
2. 본문 내 모든 URL 이 실제로 접근 가능한가(404 제거). 링크는 반드시 실제 수집한 페이지 URL.
3. 카테고리/태그가 기존 규칙과 일치하는가:
   - 주간뉴스: category `Bioinformatics`, tags `Bioinformatics`, `Computational Biology`,
     `생명정보학`, `Weekly News`, teaser `/assets/images/weekly-news-teaser.svg`
   - 채용공고: category `채용공고`, tags `Bioinformatics`, `Computational Biology`,
     `채용`, `생명정보학`
4. teaser 이미지 파일이 `/assets/images/` 에 실제로 존재하는가 (`ls` 로 확인).
5. 기존 포스트를 지우거나 덮어쓰지 않았는가 (이번 주 파일이 이미 있으면 **추가만**).

## 7. 커밋 & 배포

```bash
GITWIN="/mnt/c/Program Files/Git/cmd/git.exe"
REPO_W="C:/Users/Kim JaeHyun/a7420174.github.io"
"$GITWIN" -C "$REPO_W" add "_posts/<파일명>.md"
"$GITWIN" -C "$REPO_W" commit -m "feat: YYYY년 M월 N주차 Bioinformatics <주간뉴스|채용공고> 자동 발행"
"$GITWIN" -C "$REPO_W" push origin master
```

- 커밋 메시지는 한글로, 기존 커밋 스타일(`feat: ...`)을 따른다.
- push 전에 `status` 로 변경 파일이 포스트 1개뿐인지 확인.
- 이 자동화 경로(commit + push)는 사용자가 사전 승인한 범위다. 게이트를 통과한 포스트만 push 하고,
  push 결과와 배포 확인을 8절에 보고한다.

## 8. 결과 보고 (이 채팅으로 돌아갈 최종 메시지)

- 발행한 포스트 파일명 + 예상 URL
  (`https://a7420174.github.io/{category-lower}/{slug}/`, slug = 파일명에서 `YYYY-MM-DD-` 와 `.md` 제거, 각 세그먼트 percent-encode)
- 수록 건수 (논문/툴/이벤트/뉴스 또는 채용공고 N건)
- 제외한 항목과 사유 (만료, 중복, 범위 밖)
- 윤문 결과 (경로·변경률·등급) 또는 스킵 사유
- push 성공 여부
