# 주간 Bioinformatics 채용공고 자동 수집 및 발행 (OpenClaw 버전)

먼저 `/home/a7420174/.openclaw/workspace/writer/automation/COMMON.md` 를 읽고 그 지침을 따른다.
원본 Claude Code 크론 프롬프트(trig_01UgCMxFR6oxHoRBqEYbfWA6) 원문을
`/home/a7420174/.openclaw/workspace/writer/automation/weekly-bioinfo-jobs-raw.txt` 에 보관했으니 참고용으로 읽어라.

RULES:
- **모든 curl 은 반드시 `--max-time 25` 를 붙인다.** 응답이 안 오면 그 사이트는 건너뛴다.
  한 사이트에서 2회 이상 실패하면 그 소스는 포기하고 다음으로 넘어간다.
  전체 수집은 30분 안에 끝낼 것(그 넘어가면 지금 가진 결과로 진행한다).
- **모든 URL 요청은 한 번만** 재시도한다. 무한 재시도 금지.
- URL 추측 금지. 모든 URL 은 실제로 fetch 한 페이지에서 가져온 것만.
- 채용 공고 개별 URL 만 사용 (회사 채용포털 홈·검색결과 페이지 금지).
- 범위: Bioinformatics / Computational Biology 만. wet-lab, 일반 생물학, 화학 제외.
- 제외 소스: wanted.co.kr, hibrain.net.
- 허용 소스: BRIC(ibric.org), JobKorea(jobkorea.co.kr), Saramin(saramin.co.kr),
  Remember Career(career.rememberapp.co.kr), jobs.ac.kr, rndjob.or.kr. 그 외 소스는 reject.
- 상시채용은 (상시) 라벨로 허용. 마감일 구체적인 공고가 먼저 온다.
- **만료/마감 체크는 협상 불가.**
- 이번 주 파일이 이미 있으면 먼저 읽고, 기존 공고는 모두 유지한 채 **새 공고만 추가**한다.

Execute 3 roles in sequence: PLANNER, EDITOR, VALIDATOR.

=== ROLE 1: PLANNER ===

Step 0: 준비
- 실행일 기준 연·월·주차 계산.
- `_posts/` 에서 이전 채용공고 파일 목록 수집.
- 직전 2주 포스트를 읽어 두 가지 블랙리스트를 만든다:
  - TITLE BLACKLIST: 이미 게시한 직무 제목 전부.
  - COMPANY_DEADLINE BLACKLIST: (회사명, 마감일) 쌍. 회사명 정규화: (주)/(주식회사)/Inc 등 접두 제거.
- 새 공고가 아래 중 하나면 중복이므로 **제외**:
  (a) 직무 제목이 TITLE BLACKLIST 에 있음, 또는
  (b) (회사명, 마감일) 쌍이 COMPANY_DEADLINE BLACKLIST 에 있음.
  규칙 (b) 는 같은 회사가 다른 플랫폼에 같은 직무를 다른 제목으로 다시 올린 경우를 잡는다.
- 이번 주 포스트가 이미 있으면 읽고 기존 공고 목록을 확인.

Step 1: BRIC BioJob (최우선) — 쿠키 + Referer 필요
- 목록 페이지 먼저 워밍업(쿠키 화이기):
```bash
curl -sL --max-time 25 -c /tmp/bc.txt -b /tmp/bc.txt \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
  -H 'Accept: text/html' -H 'Accept-Language: ko-KR' \
  'https://www.ibric.org/bric/biojob/recruit.do' | grep -o 'articleNo=[0-9]*' | sort -u
```
- offset/pageIndex GET 은 페이지네이션이 되지 않는다(같은 20건). 최신 20건이면 충분.
- 상세 URL: `https://www.ibric.org/bric/biojob/recruit.do?mode=view&articleNo=NUMBER`
- 상세는 쿠키 + Referer 를 반드시 넣는다. 없으면 HTTP 200 + 빈 바디가 온다.
```bash
for aid in <articleNos>; do
  curl -sL --max-time 25 -c /tmp/bc.txt -b /tmp/bc.txt \
    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
    -H 'Accept: text/html' -H 'Accept-Language: ko-KR' \
    -H 'Referer: https://www.ibric.org/bric/biojob/recruit.do' \
    "https://www.ibric.org/bric/biojob/recruit.do?mode=view&articleNo=${aid}" \
    -o /tmp/bric_${aid}.html
done
```
- 0 바디 응답이 있으면 목록 페이지를 다시 워밍업한 뒤 재시도. 쿠키 화이기를 공유하며 병렬 curl 하지 말 것.
- 각 상세에서 확인할 것:
  1. 제목에 bioinformatics 관련 키워드 (title 또는 og:description)
  2. 만료 체크: `grep -i 'expired\|manryo\|magam-doen\|jongryo' /tmp/bric_${aid}.html`
     그리고 `grep 'alert(' /tmp/bric_${aid}.html` (JS 알림 "manryodoen jeongbo" 등)
     하나라도 걸리면 **제외**.
  3. 마감일 추출: b-deadline-box 블록의 YYYY-MM-DD.
  4. 마감일 < 오늘 이면 **제외**.

Step 2: Saramin — 마감일은 meta 태그에서만
- web_search `site:saramin.co.kr bioinformatics`. 허용 URL 패턴:
  `/zf_user/jobs/view?rec_idx=` 또는 `/jobs/relay/view?rec_idx=`
- 마감일 추출:
```bash
curl -sL --max-time 25 -H 'User-Agent: Mozilla/5.0' 'URL' | grep -i 'description\|magam\|deadline\|og:' | head -10
```
- meta 의 magamil 뒤 날짜. 오늘보다 이전이면 **제외**. 본문의 D-xx 카운트다운은 쓰지 않는다.

Step 3: JobKorea — RSC payload
- web_search `site:jobkorea.co.kr bioinformatics`. 허용 URL 패턴: `/Recruit/GI_Read/`
```bash
curl -sL --max-time 25 -H 'User-Agent: Mozilla/5.0' 'URL' | grep -o 'endDate[^,]*'
```
- 응답에 JOB_NOT_FOUND 가 있으면 제외. endDate < 오늘이면 제외. 본문 확보는 web_fetch.

Step 4: Remember Career
- web_search `site:career.rememberapp.co.kr bioinformatics` → web_fetch 각 결과.
- 페이지에 closed 또는 마감 표기면 제외.

Step 5: rndjob.or.kr, jobs.ac.kr
- web_search 로 bioinformatics 관련 검색 → web_fetch 각 공고.
- rndjob 은 jeobsu-gigan 에서 종료일을 추출해 오늘보다 이전이면 제외.
  검색 결과에 오래된 글이 많으니 날짜를 반드시 직접 확인.

필터: 범위(생물정보학/컴퓨테이셔널) · 마감일 > 오늘 또는 (상시) · TITLE BLACKLIST 없음 ·
COMPANY_DEADLINE BLACKLIST 없음 · URL 실재 확인 · 허용 소스.

출력: [PLAN] — 검증된 공고 목록.

=== ROLE 2: EDITOR ===

PLAN 의 데이터만 사용한다(새 fetch 금지).
이번 주 포스트가 있으면 Edit 로 새 공고만 추가(기존 내용 유지).
신규 생성 시 파일명:
`_posts/YYYY-MM-DD-Bioinformatics-채용공고-YYYY년-M월-N주차.md`

Front matter (기존 채용공고 포스트의 front matter 를 먼저 참고해 동일 형식을 따른다):
```yaml
---
title: "Bioinformatics 채용공고 - YYYY년 M월 N주차"
date: YYYY-MM-DD
categories:
  - 채용공고
tags:
  - Bioinformatics
  - Computational Biology
  - 채용
  - 생명정보학
toc: true
toc_sticky: true
header:
  teaser: /assets/images/weekly-jobs-teaser.svg
---
```
- teaser 파일이 없으면 가장 가까운 기존 채용공고 teaser 를 쓰고, 그것도 없으면 `header.teaser` 를 생략하고
  결과 보고에 명시한다.
- 본문: 마감일 구체적인 공고 먼저, 그 다음 (상시) 공고. 각 항목에 직무명, 회사, 마감일(또는 상시),
  출처, 공고 URL, 한줄 요약. 한국어. 하단에 면책 고지.
- 기존 채용공고 포스트의 항목 표기 형식을 반드시 먼저 읽고 동일하게 맞춘다.

출력: [DRAFT]

=== ROLE 3: VALIDATOR (적대적 만료 검사) ===

새로 추가한 모든 공고에 대해 "아직 열려 있는가" + "중복이 아닌가"를 독립적으로 다시 확인한다.

공통 확인:
- 제목이 TITLE BLACKLIST 에 있으면 FAIL(중복)
- (회사명, 마감일) 이 COMPANY_DEADLINE BLACKLIST 에 있으면 FAIL
- 허용 소스인지, 생물정보학/컴퓨테이셔널 범위인지, 개별 공고 URL 인지, 기존 공고를 삭제하지 않았는지,
  형식이 맞는지 확인

소스별 만료 검증:
1. BRIC: 위 Step 1b 패턴으로 쿠키+Referer curl → `grep -i 'manryo\|expired\|magam-doen\|jongryo'`,
   `grep 'alert('`, b-deadline-box 마감일 비교. 하나라도 걸리면 FAIL 후 제거.
2. Saramin: curl 후 meta description 의 magamil:YYYY-MM-DD. 오늘보다 이전이면 FAIL 후 제거.
3. JobKorea: curl 후 `grep 'JOB_NOT_FOUND'` = FAIL, endDate < 오늘 = FAIL 후 제거.
4. Remember Career: web_fetch. closed 상태면 FAIL 후 제거.
5. rndjob.or.kr: web_fetch. jeobsu-gigan 종료일 < 오늘 또는 연도가 현재보다 이전이면 FAIL 후 제거.
6. jobs.ac.kr: web_fetch. magam/wanryo/jongryo 표기 확인, 마감일 < 오늘이면 FAIL 후 제거.

공고마다 출력:
`Posting: [직무] | Company: [회사] | Deadline: [날짜] | Source: [출처] | Expiry: PASS/FAIL | Duplicate: PASS/FAIL | Result: PASS/FAIL [사유]`

- 1건이라도 실패하면 [REVISION_NEEDED] + 구체적 수정 지시 후 PLANNER 로 복귀(최대 3회).
- 전부 통과하면 [FINAL] + 전체 검증 로그.

=== AFTER FINAL ===
- 새 공고가 0건이면 **빈 포스트를 만들지 않는다.** 커밋도 하지 않고,
  결과 보고에 "이번 주 신규 공고 0건 — 포스트 미생성" 을 쓴다.
- 그렇지 않으면 COMMON.md 6절의 발행 전 체크리스트를 수행한 뒤
  COMMON.md 7절의 커밋/배포 절차(Windows git.exe 사용)를 따른다.
- 커밋 메시지 예: `feat: YYYY년 M월 N주차 Bioinformatics 채용공고 N건 발행`
- COMMON.md 8절에 따라 결과 보고.
