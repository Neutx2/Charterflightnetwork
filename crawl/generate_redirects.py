#!/usr/bin/env python3
"""Phase 3: emit redirects/.htaccess (Apache) and public/_redirects (Netlify)
from crawl/redirects.json. Every inventoried legacy URL gets a 301."""
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
redirects = json.load(open(ROOT / "crawl" / "redirects.json"))

# Defensive extras: legacy URLs that are referenced (form redirect target,
# old bookmarks) but were not linked from any crawled page.
redirects.setdefault("/charter_quote_confirmation.htm", "/quote-confirmation")
redirects.setdefault("/charter_quote_confirmation.html", "/quote-confirmation")
redirects.setdefault("/index.htm", "/")

# skip self-maps (e.g. "/" -> "/")
pairs = sorted(
    (old, new) for old, new in redirects.items()
    if old.rstrip("/") != new.rstrip("/") and old != "/"
)

# ---------- Apache .htaccess ----------
ht = [
    "# Charter Flight Network — legacy URL 301 map (generated, do not hand-edit)",
    "# Every inventoried legacy .htm/.html URL redirects to its new clean URL.",
    "RewriteEngine On",
    "",
    "# Serve pre-built directory indexes cleanly",
    "DirectoryIndex index.html",
    "",
    "# Security headers (mirrors netlify.toml)",
    "<IfModule mod_headers.c>",
    '  Header set X-Content-Type-Options "nosniff"',
    '  Header set X-Frame-Options "SAMEORIGIN"',
    '  Header set Referrer-Policy "strict-origin-when-cross-origin"',
    '  <FilesMatch "\\.(css|js|woff2)$">',
    '    Header set Cache-Control "public, max-age=31536000, immutable"',
    "  </FilesMatch>",
    "</IfModule>",
    "",
]
for old, new in pairs:
    # exact-match rule; escape regex specials, spaces (from %20) need escaping
    path = old.lstrip("/")
    esc = ""
    for ch in path:
        esc += "\\" + ch if ch in r".+()[]{}^$?|* " else ch
    ht.append(f"RewriteRule ^{esc}$ {new} [R=301,L]")
ht += [
    "",
    "# Legacy image folder kept at /CFN Images/ — no redirect needed if copied as-is.",
    "",
]

(ROOT / "redirects").mkdir(exist_ok=True)
(ROOT / "redirects" / ".htaccess").write_text("\n".join(ht) + "\n")

# ---------- Netlify _redirects ----------
nl = [
    "# Charter Flight Network — legacy URL 301 map (generated, do not hand-edit)",
]
for old, new in pairs:
    # Netlify matches URL-decoded paths; quote spaces
    old_q = urllib.parse.quote(old, safe="/%")
    nl.append(f"{old_q}  {new}  301!")
(ROOT / "public" / "_redirects").write_text("\n".join(nl) + "\n")

print(f"wrote {len(pairs)} redirect rules to redirects/.htaccess and public/_redirects")
