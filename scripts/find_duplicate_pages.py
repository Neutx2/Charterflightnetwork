#!/usr/bin/env python3
"""Find built pages that serve byte-identical <main> content at two URLs.

The legacy site published some documents under two names, and a faithful
migration carries that through: duplicate pages competing in search, and
identical-looking links side by side in the directory index.

Run against dist/ after a build:
    python3 scripts/find_duplicate_pages.py [subdir]

Prints each group so src/lib/directory-dupes.ts can be updated deliberately —
this script reports, it does not edit. Which copy is "primary" is a judgement
call (we use: the slug whose own <h1> matches it), so it stays human-made.
"""
import hashlib
import pathlib
import re
import sys
from collections import defaultdict

root = pathlib.Path("dist") / (sys.argv[1] if len(sys.argv) > 1 else "")
if not root.exists():
    sys.exit(f"no such directory: {root} (run `npx astro build` first)")

groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
for page in sorted(root.rglob("index.html")):
    html = page.read_text(errors="ignore")
    main = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    if not main:
        continue
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", main.group(1))).strip()
    if len(text) < 200:  # stubs and near-empty pages aren't interesting
        continue
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    heading = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else ""
    url = "/" + str(page.parent.relative_to("dist")).replace("\\", "/")
    groups[hashlib.sha1(text.encode()).hexdigest()].append((url, heading))

dupes = {k: v for k, v in groups.items() if len(v) > 1}
total = sum(len(v) for v in dupes.values())
print(f"{len(dupes)} duplicate group(s), {total} page(s), scanned {root}\n")
for members in sorted(dupes.values()):
    for url, heading in members:
        print(f"  {url}\n      h1: {heading}")
    print()

sys.exit(1 if dupes else 0)
