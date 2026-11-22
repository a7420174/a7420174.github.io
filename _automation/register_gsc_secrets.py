#!/usr/bin/env python3
"""
[BI Playground] GitHub Actions Secret 등록 도우미 — GSC / Indexing API 자격증명.

서비스 계정 JSON(로컬 파일) 1개를 읽어 저장소 Secret 2개로 등록한다:
  - GOOGLE_INDEXING_SA_JSON   (scope: .../auth/indexing    → google-indexing.yml)
  - GOOGLE_SA_JSON            (scope: .../auth/webmasters  → gsc-sync.yml)

GitHub API 는 secret 값을 평문으로 못 받으므로 저장소 공개키로
AES256-GCM 암호화 후 PUT 한다.

사용:
  export GITHUB_TOKEN=...
  python3 register_gsc_secrets.py --json /path/to/sa.json --repo a7420174/a7420174.github.io
  python3 register_gsc_secrets.py --json ... --repo ... --dry-run   # 암호화만 검증
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request



def api(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw else {})


def encrypt(secret: str, key_b64: str, key_id: str) -> tuple[str, str]:
    """GitHub Secret 암호화.

    ⚠️ GitHub 는 libsodium sealed box (crypto_box_seal) 를 사용한다.
    AES-GCM 으로는 422 'improperly encrypted secret' 가 난다.
    pynacl 이 있으면 그것을 쓰고, 없으면 gh CLI 로 등록하도록 안내한다.
    """
    try:
        from nacl import public, encoding
        key = base64.b64decode(key_b64)
        pk = public.PublicKey(key)
        sealed = public.SealedBox(pk).encrypt(secret.encode("utf-8"))
        return base64.b64encode(sealed).decode(), key_id
    except ImportError:
        pass
    print("[ERROR] pynacl 이 없어 libsodium sealed box 암호화를 수행할 수 없습니다.\n"
          "       gh CLI 로 등록하세요:\n"
          "         gh secret set <NAME> --repo <owner/repo> --body \"<JSON>\"", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="서비스 계정 JSON 파일 경로")
    ap.add_argument("--repo", default="a7420174/a7420174.github.io")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.token:
        print("[ERROR] GITHUB_TOKEN 이 없습니다.", file=sys.stderr)
        return 1
    if not os.path.exists(args.json):
        print(f"[ERROR] 파일 없음: {args.json}", file=sys.stderr)
        return 1

    raw = open(args.json, encoding="utf-8").read()
    try:
        sa = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패: {e}", file=sys.stderr)
        return 1
    # 자격증명 유형: service_account(서비스 계정) 또는 authorized_user(본인 OAuth)
    ctype = sa.get("type", "")
    if ctype == "service_account":
        required = ("client_email", "private_key", "project_id")
    elif ctype == "authorized_user":
        required = ("client_id", "client_secret", "refresh_token")
    else:
        print(f"[ERROR] 알 수 없는 credential type '{ctype}'. "
              f"service_account 또는 authorized_user 여야 합니다.", file=sys.stderr)
        return 1
    for field in required:
        if field not in sa or not sa[field]:
            print(f"[ERROR] 자격증명 JSON 에 '{field}' 가 없습니다. "
                  f"올바른 JSON 인지 확인하세요.", file=sys.stderr)
            return 1
    if ctype == "service_account":
        print(f"[info] 인증 유형: 서비스 계정")
        print(f"[info] 서비스 계정: {sa['client_email']}")
        print(f"[info] 프로젝트: {sa['project_id']}")
    else:
        print(f"[info] 인증 유형: 본인 OAuth (authorized_user)")
        print(f"[info] 클라이언트 ID: {sa['client_id']}")

    st, pk = api("GET", f"https://api.github.com/repos/{args.repo}/actions/secrets/public-key",
                 args.token)
    if st != 200:
        print(f"[ERROR] 공개키 조회 실패: HTTP {st} {pk}", file=sys.stderr)
        return 1

    for name in ("GOOGLE_INDEXING_SA_JSON", "GOOGLE_SA_JSON"):
        enc, key_id = encrypt(raw, pk["key"], pk["key_id"])
        if args.dry_run:
            print(f"[dry-run] {name} 암호화 OK (len={len(enc)})")
            continue
        st, body = api("PUT",
                       f"https://api.github.com/repos/{args.repo}/actions/secrets/{name}",
                       args.token,
                       {"encrypted_value": enc, "key_id": key_id})
        print(f"[{'OK' if st in (201, 204) else 'FAIL'}] {name} :: HTTP {st} "
              f"{body if st not in (201, 204) else ''}")
        if st not in (201, 204):
            return 1

    st, body = api("GET", f"https://api.github.com/repos/{args.repo}/actions/secrets",
                   args.token)
    print("\n[info] 현재 저장소 Secret 목록:")
    for s in body.get("secrets", []):
        print(f"   - {s['name']} (updated {s['updated_at']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
