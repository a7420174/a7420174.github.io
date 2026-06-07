# 구글 Indexing API 세팅 가이드

> 목적: 채용공고 글 발행 시 구글에 **자동 색인 요청**을 보내기 위한 사전 세팅.
> Indexing API는 **무료**입니다(결제 등록 불필요, 기본 할당량 200 URL/일).
> 이 4단계는 스크립트로 자동화 불가 — 본인이 직접 한 번 해야 합니다. 끝나면 알려주세요.

---

## 1. GCP 프로젝트 생성 + Indexing API 활성화

1. https://console.cloud.google.com 접속 → 블로그 구글 계정으로 로그인
2. 상단 프로젝트 드롭다운 → **새 프로젝트** → 이름 예: `blog-indexing` → **만들기**
3. 방금 만든 프로젝트가 선택됐는지 확인
4. 왼쪽 메뉴 **API 및 서비스 → 라이브러리** 이동
5. 검색창에 **`Web Search Indexing API`** (= Indexing API) 입력 → 클릭 → **사용 설정(Enable)**

---

## 2. 서비스 계정 + JSON 키 발급

1. **IAM 및 관리자 → 서비스 계정** 이동
2. **서비스 계정 만들기** 클릭
   - 이름: 예 `indexing-bot`
   - **만들고 계속하기** → 역할(Role)은 **건너뛰기**(Indexing API는 프로젝트 역할이 아니라 아래 3단계의 GSC 권한으로 동작) → **완료**
3. 생성된 서비스 계정 클릭 → 상단 **키(KEYS)** 탭 → **키 추가 → 새 키 만들기 → JSON** → **만들기**
   - JSON 파일이 자동 다운로드됨. **이게 자격증명 파일입니다. 절대 git에 커밋 금지.**
4. 서비스 계정 **이메일** 복사해 둠 — `indexing-bot@blog-indexing.iam.gserviceaccount.com` 형태

---

## 3. Search Console에 서비스 계정을 "소유자"로 추가

> ⚠️ 가장 자주 틀리는 단계. 권한이 **소유자(Owner)** 가 아니면 API가 `Permission denied`를 냅니다.

1. https://search.google.com/search-console 접속
2. 속성 `a7420174.github.io` 선택
3. 좌측 하단 **설정(Settings) → 사용자 및 권한(Users and permissions)**
4. **사용자 추가** → 2단계에서 복사한 **서비스 계정 이메일** 입력
5. 권한 = **소유자(Owner)** 선택 → **추가**

---

## 4. GitHub Secret 등록

> 다운로드한 JSON 키를 GitHub Actions가 읽을 수 있게 저장.

1. GitHub repo → **Settings → Secrets and variables → Actions**
2. **New repository secret**
   - Name: `GOOGLE_INDEXING_SA_JSON`
   - Value: **다운로드한 JSON 파일의 전체 내용**을 그대로 붙여넣기 (`{ "type": "service_account", ... }`)
3. **Add secret**

---

## 동작 확인 (선택, 로컬 테스트)

JSON 키 파일 경로를 알면 아래로 빠르게 검증할 수 있습니다 (Python):

```bash
pip install google-auth requests
```

```python
import json, requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SA = "다운로드한_키.json"  # 로컬 경로
creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/indexing"])
session = AuthorizedSession(creds)
r = session.post(
    "https://indexing.googleapis.com/v3/urlNotifications:publish",
    json={"url": "https://a7420174.github.io/", "type": "URL_UPDATED"})
print(r.status_code, r.text)
```

- **200 + `urlNotificationMetadata`** → 세팅 성공 🎉
- **403 `Permission denied`** → 3단계(소유자 추가) 다시 확인
- **403 `Indexing API has not been used...`** → 1단계(API 활성화) 다시 확인

---

## 완료 후

위가 200으로 확인되면 알려주세요. 그러면:
1. 채용공고 글에 JobPosting JSON-LD 마크업 추가
2. 기존 7개 글 front matter backfill
3. `.github/workflows/google-indexing.yml` — push 시 새 채용공고 URL 자동 제출
4. CLAUDE.md 문서화

를 이어서 구현합니다.
