# IndexNow 자동 색인 설계서

- **날짜**: 2026-06-07
- **목표**: 새 블로그 글 발행(= master push) 시 **네이버·Bing**에 IndexNow로 자동 색인 요청을 보낸다. 구글은 IndexNow 미지원이므로 기존 sitemap 자동 크롤에 맡긴다.
- **배경**: 현재 GSC에서 글마다 수동으로 색인 요청 중. 구글 Indexing API는 GCP 필요 + JobPosting 페이지 제약이 있어 채택 불가 → 제약 없는 IndexNow로 네이버·Bing 자동화.

## 범위

- **대상**: `_posts/**`의 모든 새 글 (AI, Hail, Bioinformatics, 채용공고 등 카테고리 무관). IndexNow는 콘텐츠 유형 제약이 없다.
- **제외**: JobPosting JSON-LD 마크업, front matter backfill (구글 Indexing API 전용이었으므로 불필요). 구글 색인 자동화(불가능 — sitemap이 유일 경로, 이미 정상).

## URL 도출 규칙 (실측 확정)

라이브 sitemap에서 확인한 규칙:

```
https://a7420174.github.io/{categories}/{slug}/
```

- `{slug}` = 파일명에서 `YYYY-MM-DD-` 접두사와 `.md` 확장자를 제거한 문자열. **대소문자·한글 보존** (소문자화 안 함).
  - 예: `2026-06-06-Bioinformatics-채용공고-2026년-6월-1주차.md` → slug = `Bioinformatics-채용공고-2026년-6월-1주차`
- `{categories}` = front matter `categories` 값. 문자열이면 그대로, 리스트면 `/`로 결합 (permalink `/:categories/:title/` 규칙).
- 각 경로 세그먼트는 **URL 인코딩**(percent-encoding). 예: `채용공고` → `%EC%B1%84%EC%9A%A9%EA%B3%B5%EA%B3%A0`
- 구현 시 라이브 sitemap의 실제 URL과 대조 검증한다 (AI/Hail 등 비채용 카테고리 포함).

## 컴포넌트

### 1. IndexNow 키 파일
- 32자 hex 랜덤 키 생성 (구현 시 PowerShell `New-Guid` 등 안전한 난수 사용).
- repo 루트에 `{key}.txt` 커밋 → `https://a7420174.github.io/{key}.txt`로 서빙. 파일 내용 = 키 문자열 한 줄.
- 키는 비밀이 아님(공개 파일이 소유권 증명) → GitHub Secret 불필요.
- Jekyll이 가공하지 않도록: front matter 없는 `.txt`는 그대로 복사됨. `_config.yml`의 include/exclude 영향 없는지 확인.

### 2. 제출 스크립트 `_automation/submit_indexnow.py`
- **입력**: 변경된 `_posts/*.md` 경로들을 명령행 인자로 받음.
- **처리**: 각 파일의 front matter `categories` 파싱 + 파일명에서 slug 도출 → 위 규칙으로 URL 생성.
- **출력**: IndexNow POST 호출. 표준 라이브러리만 사용(`urllib`, `re`, `sys`, `pathlib`) — 외부 의존성 없음(CI 단순화).
- **POST 바디** (엔드포인트별 동일):
  ```json
  {
    "host": "a7420174.github.io",
    "key": "<key>",
    "keyLocation": "https://a7420174.github.io/<key>.txt",
    "urlList": ["https://a7420174.github.io/..."]
  }
  ```
  `Content-Type: application/json`.
- **엔드포인트** (둘 다 제출):
  - `https://api.indexnow.org/indexnow` (참여 엔진 전체 전파)
  - `https://searchadvisor.naver.com/indexnow` (네이버 명시)
- **키 전달**: 환경변수 `INDEXNOW_KEY`로 주입(키 파일명과 동일 값). 워크플로에서 설정.
- **에러 처리**: 각 엔드포인트 응답 코드 로그. 200/202 정상. 한 엔드포인트 실패해도 다른 엔드포인트 시도 계속(non-fatal). 제출할 URL이 0개면 조용히 종료.

### 3. GitHub Actions 워크플로 `.github/workflows/indexnow.yml`
- 트리거: `on: push: { branches: [master], paths: ['_posts/**'] }`
- 잡 스텝:
  1. `actions/checkout@v4` with `fetch-depth: 0` (push 범위 diff 위해 전체 히스토리)
  2. 변경 파일 산출:
     - `BEFORE=${{ github.event.before }}`, `AFTER=${{ github.event.after }}`
     - `BEFORE`가 `0000000...`(새 브랜치/첫 푸시)면 fallback `HEAD~1` (없으면 빈 트리 `4b825dc...`)
     - `git diff --name-only --diff-filter=AM $BEFORE $AFTER -- '_posts/*.md'`
  3. 변경된 `_posts` 파일이 있으면 `python _automation/submit_indexnow.py <files...>` 실행
     - `env: INDEXNOW_KEY: <키>` (워크플로 파일에 평문 — 키는 공개값이므로 무방)
  4. 변경 없으면 스킵.
- `actions/setup-python@v5` (python 3.x).

### 4. 문서화
- CLAUDE.md "Scheduled Automation" 또는 신규 "SEO / Indexing" 섹션에:
  - IndexNow 워크플로 존재·동작 방식
  - 키 파일 위치(`/{key}.txt`)
  - 구글은 sitemap 자동 크롤(수동 색인요청 불필요), 네이버·Bing은 IndexNow 자동
  - 네이버 Search Advisor 등록 필요 사실

## 사용자 수동 작업

- **네이버 Search Advisor에 사이트 등록·검증** 여부 확인 (미등록 시 네이버가 IndexNow 핑 거부). Bing은 키 파일만으로 동작.

## 데이터 흐름

```
새 글 commit & push (master)
  → GitHub Actions 트리거 (paths: _posts/**)
  → git diff로 추가/수정된 _posts/*.md 산출
  → submit_indexnow.py: 파일명+categories → 라이브 URL
  → POST {host,key,keyLocation,urlList} → api.indexnow.org + naver
  → 네이버·Bing이 수 분~수 시간 내 크롤 (이때 GitHub Pages 배포 완료되어 URL 라이브)
```

## 엣지 케이스

- **slug에 한글/특수문자**: URL 인코딩 처리.
- **categories 리스트**: `/`로 결합.
- **categories 누락**: permalink 기본값상 발생 가능성 낮음. 누락 시 해당 파일 건너뛰고 경고 로그.
- **첫 푸시 / force push**: `github.event.before` = 0 → fallback diff.
- **삭제만 된 푸시**: `--diff-filter=AM`이라 삭제는 제외 → 제출 0건.
- **타이밍**: Pages 배포(~1분)보다 핑이 먼저 나갈 수 있으나, 엔진 크롤은 수 분 뒤라 라이브 보장됨.

## 검증 계획

- `submit_indexnow.py`의 URL 도출 결과를 라이브 sitemap의 실제 URL과 대조(여러 카테고리).
- 로컬에서 스크립트를 `--dry-run`으로 실행해 생성 URL 확인 후 실제 제출.
- 워크플로 첫 실행 후 네이버 Search Advisor / Bing Webmaster의 IndexNow 제출 로그 확인.
```
