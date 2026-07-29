#!/usr/bin/env python3
"""Phase 1c: download unique legacy images referenced by inventoried pages
into src/assets/legacy/, preserving the CFN Images/ folder structure.
Throttled ~1 req/sec; resumable."""
import json
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
META = json.load(open(ROOT / "crawl" / "pagemeta.json"))
OUT = ROOT / "src" / "assets" / "legacy"
OUT.mkdir(parents=True, exist_ok=True)

seen: dict[str, dict] = {}
for url, m in META.items():
    for img in m.get("images", []):
        src = img["src"]
        if "charterflightnetwork.com" not in src:
            continue
        if src not in seen:
            seen[src] = {"alt": img.get("alt", ""), "pages": 0}
        seen[src]["pages"] += 1

print(f"{len(seen)} unique legacy images referenced")

session = requests.Session()
session.headers["User-Agent"] = "CFN-migration-crawler/1.0"
manifest = {}
downloaded = skipped = failed = 0
for src, info in sorted(seen.items()):
    path = urllib.parse.unquote(urllib.parse.urlparse(src).path).lstrip("/")
    local = OUT / path.replace(" ", "_")
    manifest[src] = {"local": str(local.relative_to(ROOT)), **info}
    if local.exists() and local.stat().st_size > 0:
        skipped += 1
        continue
    local.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = session.get(src, timeout=30)
        if r.status_code == 200 and len(r.content) > 100:
            local.write_bytes(r.content)
            downloaded += 1
        else:
            manifest[src]["error"] = f"HTTP {r.status_code}"
            failed += 1
    except Exception as e:
        manifest[src]["error"] = str(e)[:120]
        failed += 1
    time.sleep(1.0)

json.dump(manifest, open(ROOT / "crawl" / "image_manifest.json", "w"), indent=1)
print(f"downloaded={downloaded} cached={skipped} failed={failed}")
