# 색인(Indexing) 자동화 가이드 — BI Playground

> "글마다 Google Search Console 에 등록해야 하는데 귀찮다" 라는 문제를
>   실제로 없애기 위한 구성. 2026-11-21 구축.

## 0. 핵심 개념 (먼저 읽을 것)

| misconceptions | 사실 |
|---|---|
| 글마다 GSC 에 등록해야 한다 | **아니다.** GSC 속성(property) 은 사이트 단위 1개. `https://a7420174.github.io/` 하나면 그 아래 모든 글이 자동 대상. |
| Domain 속성이 낫다 | **github.io 는 서브도메인이라 DNS TXT 검증 불가.** URL-prefix 속성만 사용. 검증 파일 `google88db8dedd4b00b7b.html` 이 루트에 이미 있음 → 추가 작업 없음. |
| sitemap.xml 을 올리면 안 읽는다 | 현재 파일은 정상 (HTTP 200, `application/xml`, URL 44개, 중복 0, 전부 https). 읽히지 않는다면 ① 속성 URL 불일치 ② "Crawled - currently not indexed"(색인 판정, sitemap 문제 아님) 중 하나. |
| Indexing API 로 일반 글도 색인 요청할 수 있다 | **안 된다.** Indexing API 는 JobPosting / BroadcastEvent / Event 용도만 허용. 일반 글에 쓰면 스팸 정책 위반. |

## 1. 구성 요소

| 파일 | 역할 |
|---|---|
| `_automation/check_sitemap.py` | robots / sitemap / URL 200 / 글 반영 여부 검증 |
| `.github/workflows/check-sitemap.yml` | push·매주 자동 검증 (실패 시 Action 실패 알림) |
| `_automation/gsc_sync.py` | GSC API 로 sitemap 재제출 + 새 글 색인 상태 조회 |
| `.github/workflows/gsc-sync.yml` | push·매주 자동 실행 (secret 필요) |
| `_automation/generate_jobpostings.py` | 채용공고 글 → JobPosting JSON-LD 데이터 생성 |
| `_data/jobpostings.json` | 위 스크립트 산출물 (GitHub Actions 가 자동 갱신) |
| `_includes/jobposting-jsonld.html` | 채용공고 글에 JobPosting 마크업 삽입 |
| `.github/workflows/jobposting-jsonld.yml` | 데이터 자동 재생성·커밋 |
| `_automation/submit_indexing.py` | Indexing API 제출 (채용공고 글만) |
| `.github/workflows/google-indexing.yml` | 채용공고 글 push 시 자동 색인 요청 (secret 필요) |
| `_automation/naver_push.py` | 네이버 개별 URL 갱신 요청 (IndexNow 단일 URL) |
| `_automation/ping_sitemaps.py` | sitemap URL 을 IndexNow 로 알림 |

이미 있던 것: `.github/workflows/indexnow.yml` (push 시 Naver·Bing IndexNow 제출).

## 2. 사람이 해야 하는 준비 (1회)

### 2-1. Google Search Console 속성
1. https://search.google.com/search-console 접속
2. 속성 추가 → **URL-prefix** → `https://a7420174.github.io/` 입력
3. 인증 방식 "HTML 파일" 선택 → 다운로드 파일이
   `google88db8dedd4b00b7b.html` 이면 **저장소에 이미 있습니다.** 그대로 진행.
4. (권장) 속성이 여러 개라면 하나만 남기고 삭제. 삭제해도 인덱스 데이터는 유지됨.
5. 좌측 **색인 → Sitemaps → 입력란**에 `sitemap.xml` 제출 (1회만 하면 이후 자동)

### 2-2. 서비스 계정 (Indexing API + Search Console API 공용)
`https://console.cloud.google.com` 에서:
1. 프로젝트 생성(예: `blog-indexing`)
2. **API 및 서비스 → 라이브러리** → `Web Search Indexing API` 사용 설정
3. **API 및 서비스 → 라이브러리** → `Search Console API` 사용 설정
4. **IAM 및 관리자 → 서비스 계정** → 생성 (역할 없음)
5. 해당 서비스 계정 → **키** → 새 키(JSON) 생성 → **절대 git 에 커밋 금지**
6. **Search Console → 속성 → 설정 → 사용자 및 권한** → 서비스 계정 이메일
   (예: `indexing-bot@blog-indexing.iam.gserviceaccount.com`) 을 **권한: 소유자** 로 추가

> ⚠️ "소유자" 가 아니면 API 가 `Permission denied` 를 냅니다.

### 2-3. GitHub Secret 등록
repo → Settings → Secrets and variables → Actions → New repository secret

| Name | Value | 쓰이는 곳 |
|---|---|---|
| `GOOGLE_INDEXING_SA_JSON` | 서비스 계정 JSON 전체 | google-indexing.yml |
| `GOOGLE_SA_JSON` | **동일한** JSON 전체 | gsc-sync.yml |

두 워크플로가 scope만 다르게 씁니다 (indexing / webmasters). 같은 키 파일을 두 Secret 에 넣으면 됩니다.

## 2-4. 비용은? — **무료입니다**

둘 다 과금 대상이 아닙니다 (2026-11-22 확인).

| API | 과금 | 기본 할당량 |
|---|---|---|
| Indexing API | **"All use of the Indexing API is available without payment"** (공식 문서) | publish **200건/일** (미티시간 자정 초기화), 읽기 180/분, 전체 380/분 |
| Search Console API | **"All use of Google Search Console API is free of charge"** (공식 문서) | 사용량 한도 있음 (일 1,000,000 / 분 4,000 정도, 검색어당 16,000/일) |

- 프로젝트를 만들 때 콘솔이 결제 계정을 요구하면: **무료 체험(90일, $300 크레딧)** 을 쓰거나,
  결제가 필요 없는 API 라 결제 계정 없이 진행할 수 있습니다. 어차피 이 API 둘은 과금되지 않습니다.
- 혹시 걱정되면 **결제 → 예산 및 알림 → 예산 금액 0원 + 알림 임계값 10%** 로 걸어두면
  예상치 못한 과금이 나도 자동 차단됩니다. (Google Cloud 콘솔에서 1분 컷)
- 참고: `Indexing API` 할당량은 프로젝트당이므로, 프로젝트 1개면 충분합니다.

## 3. 자동화 흐름

```
git push (master)
  ├─ check-sitemap.yml      → robots/sitemap/200/반영 검증 (실패 시 알림)
  ├─ indexnow.yml           → Naver·Bing 에 새 글 URL 알림
  ├─ gsc-sync.yml           → GSC 에 sitemap 재제출 + 새 글 색인 상태 조회
  ├─ google-indexing.yml    → 채용공고 글만 Indexing API 색인 요청
  └─ jobposting-jsonld.yml  → _data/jobpostings.json 재생성·커밋 (JobPosting 마크업 반영)
```

## 4. 남는 수동 작업

- 일반 글: **없음.** sitemap 이 자동 반영되고, Google 이 크롤할 때 색인됩니다.
  expedite 하고 싶을 때만 GSC > URL 검사 > 색인 요청 (1회 클릭).
- 채용공고 글: 위 자동화가 색인 요청까지 수행.
- GSC 속성 자체는 위 2-1 에서 1회만.

## 5. 점검 명령 (로컬)

```bash
python3 _automation/check_sitemap.py --site https://a7420174.github.io --repo-root .
python3 _automation/generate_jobpostings.py --repo-root .
python3 _automation/naver_push.py https://a7420174.github.io/<새글URL>/
```

## 6. 주의

- Indexing API 할당량: 하루 200 URL 요청 (무료, 결제 등록 불필요).
- 마감일이 지난 공고는 JobPosting 에서 자동 제외 (구글 스팸 정책).
- Google 은 IndexNow 미지원 → Google 대상은 sitemap + GSC API 경로.
