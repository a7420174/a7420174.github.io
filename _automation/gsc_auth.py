#!/usr/bin/env python3
"""
[BI Playground] Google API 공통 인증 모듈.

서비스 계정 키(JSON) 를 만들 수 없는 환경(조직 정책
iam.disableServiceAccountKeyCreation / iam.managed.disableServiceAccountKeyCreation)
에서도 동작하도록 **3가지 인증 방식**을 지원한다.

우선순위:
  1) GOOGLE_SA_JSON            — 서비스 계정 JSON (scope: indexing / webmasters)
  2) GOOGLE_OAUTH_CLIENT_ID
     GOOGLE_OAUTH_CLIENT_SECRET
     GOOGLE_OAUTH_REFRESH_TOKEN — 본인 계정 OAuth (refresh token). GSC 소유자 계정이면 사용 가능.
  3) 워크로드 ID 페더레이션(키 없음)
     GOOGLE_APPLICATION_CREDENTIALS(없어도 됨) / gcloud auth application-default login 또는
     GitHub Actions 의 google-github-actions/auth + WIF → ADC 가 자동 구성.
     gsc_sync.py / submit_indexing.py 는 ADC 만으로 충분하다.

사용:
    from gsc_auth import get_session
    session = get_session(["https://www.googleapis.com/auth/indexing"])
"""
from __future__ import annotations

import json
import os
import sys

SCOPES_INDEXING = ["https://www.googleapis.com/auth/indexing"]
SCOPES_WEBMASTERS = ["https://www.googleapis.com/auth/webmasters"]


def _err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def get_session(scopes: list[str]):
    """인증된 AuthorizedSession 을 반환한다. 실패 시 None."""
    try:
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        _err("google-auth / requests 가 필요합니다: pip install google-auth requests")
        return None

    # 1) 서비스 계정 JSON
    sa_raw = os.environ.get("GOOGLE_SA_JSON", "").strip()
    if sa_raw:
        try:
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_info(
                json.loads(sa_raw), scopes=scopes)
            return AuthorizedSession(creds)
        except Exception as e:
            _err(f"GOOGLE_SA_JSON 인증 실패: {e}")
            return None

    # 2) 사용자 OAuth (client id/secret + refresh token)
    cid = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    csec = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    rt = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN", "").strip()
    if cid and csec and rt:
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials(token=None, refresh_token=rt,
                                token_uri="https://oauth2.googleapis.com/token",
                                client_id=cid, client_secret=csec, scopes=scopes)
            return AuthorizedSession(creds)
        except Exception as e:
            _err(f"사용자 OAuth 인증 실패: {e}")
            return None

    # 3) ADC (워크로드 ID 페더레이션 / gcloud ADC)
    try:
        import google.auth
        creds, detected = google.auth.default(scopes=scopes)
        print(f"[info] ADC 인증 사용 (credentials: {detected})", file=sys.stderr)
        return AuthorizedSession(creds)
    except Exception as e:
        _err(f"인증 수단을 찾지 못했습니다: {e}\n"
             f"  GOOGLE_SA_JSON / GOOGLE_OAUTH_* / ADC 중 하나가 필요합니다.")
        return None
