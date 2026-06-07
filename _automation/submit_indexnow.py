#!/usr/bin/env python3
"""Submit changed blog post URLs to IndexNow (Naver, Bing, ...).

Usage:
    python _automation/submit_indexnow.py [--dry-run] <_posts file> ...

Google does NOT support IndexNow (it relies on sitemap crawling), so this only
notifies Naver and Bing (and other IndexNow participants).

Live URL is derived from the empirically confirmed Jekyll permalink rule
(permalink: /:categories/:title/):

    https://a7420174.github.io/{category-lowercased}/{slug}/

where slug = filename without the leading ``YYYY-MM-DD-`` and trailing ``.md``
(case preserved), and each path segment is percent-encoded.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import yaml  # PyYAML

SITE = "https://a7420174.github.io"
HOST = "a7420174.github.io"
KEY = os.environ.get("INDEXNOW_KEY", "").strip()
KEY_LOCATION = f"{SITE}/{KEY}.txt"
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",       # propagates to all participants
    "https://searchadvisor.naver.com/indexnow",  # Naver, explicit
]

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def categories_of(fm):
    val = fm.get("categories", fm.get("category"))
    if val is None:
        return []
    if isinstance(val, str):
        return [val.strip()] if val.strip() else []
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    return [str(val).strip()]


def post_url(path):
    name = os.path.basename(path)
    slug = DATE_PREFIX.sub("", name)
    slug = re.sub(r"\.(md|markdown)$", "", slug)
    with open(path, encoding="utf-8") as f:
        fm = front_matter(f.read())
    cats = categories_of(fm)
    if not cats:
        print(f"  WARN: no categories in {name}, skipping", file=sys.stderr)
        return None
    segs = [c.lower() for c in cats] + [slug]
    encoded = "/".join(urllib.parse.quote(s, safe="") for s in segs)
    return f"{SITE}/{encoded}/"


def submit(urls, dry_run=False):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    for ep in ENDPOINTS:
        if dry_run:
            print(f"  [dry-run] POST {ep} ({len(urls)} urls)")
            continue
        req = urllib.request.Request(
            ep, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"  {ep} -> {resp.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:200]
            print(f"  {ep} -> HTTP {e.code}: {body}")
        except Exception as e:  # noqa: BLE001 - non-fatal, try next endpoint
            print(f"  {ep} -> ERROR: {e}")


def main(argv):
    dry_run = "--dry-run" in argv
    files = [a for a in argv if a != "--dry-run"]
    if not dry_run and not KEY:
        print("ERROR: INDEXNOW_KEY env var not set", file=sys.stderr)
        return 1
    urls = []
    for path in files:
        if not path.endswith((".md", ".markdown")) or not os.path.exists(path):
            continue
        url = post_url(path)
        if url:
            urls.append(url)
            print(f"  {os.path.basename(path)} -> {url}")
    if not urls:
        print("No URLs to submit.")
        return 0
    submit(urls, dry_run=dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
