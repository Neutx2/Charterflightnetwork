#!/usr/bin/env python3
"""Phase 4: verify every legacy URL's redirect target resolves to a built page."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
redirects = json.load(open(ROOT / "crawl" / "redirects.json"))
redirects["/charter_quote_confirmation.htm"] = "/quote-confirmation"

missing = []
resolved = 0
for old, new in redirects.items():
    path = new.split("#")[0].rstrip("/") or "/"
    if path == "/":
        target = DIST / "index.html"
    else:
        target = DIST / path.lstrip("/") / "index.html"
    if target.exists():
        resolved += 1
    else:
        missing.append((old, new))

print(f"{resolved}/{len(redirects)} redirect targets resolve to built pages")
if missing:
    print("MISSING:")
    for old, new in missing[:50]:
        print(f"  {old} -> {new}")

# also verify no internal dead links in built HTML (sample: hub + home pages)
site_paths = {"/"} | {
    "/" + str(p.parent.relative_to(DIST)) for p in DIST.rglob("index.html")
}
dead = set()
for page in list(DIST.rglob("index.html")):
    html = page.read_text(errors="replace")
    for href in re.findall(r'href="(/[^"#?]*)', html):
        h = href.rstrip("/") or "/"
        if h.startswith(("/images", "/_astro", "/CFN", "/formmailer", "/favicon")):
            continue
        if re.search(r"\.(xml|txt|svg|jpg|webp|png|css|js)$", h):
            continue
        if h not in site_paths:
            dead.add(h)
print(f"internal dead links in built site: {len(dead)}")
for d in sorted(dead)[:40]:
    print("  ", d)

exit(1 if missing or dead else 0)
