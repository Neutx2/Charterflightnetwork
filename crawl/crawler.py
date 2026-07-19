#!/usr/bin/env python3
"""Polite BFS crawler for charterflightnetwork.com.

- Internal links only, respects robots.txt Disallow list
- ~1 request/second throttle
- Caches raw HTML to ./crawl/raw/ (filename = URL path, sanitized)
- Resumable: skips already-cached pages
- Emits ./crawl/inventory.json
"""
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://charterflightnetwork.com"
HOST = "charterflightnetwork.com"
RAW = Path(__file__).parent / "raw"
RAW.mkdir(exist_ok=True)
OUT = Path(__file__).parent / "inventory.json"
QUEUE_FILE = Path(__file__).parent / "queue_state.json"

HEADERS = {"User-Agent": "CFN-migration-crawler/1.0 (site owner authorized migration)"}

# robots.txt disallows (path prefixes, lowercased)
DISALLOW = set()
robots = Path(__file__).parent / "robots.txt"
if robots.exists():
    for line in robots.read_text().splitlines():
        m = re.match(r"(?i)\s*Disallow:\s*(\S+)", line)
        if m:
            DISALLOW.add(urllib.parse.unquote(m.group(1)).lower())

SKIP_EXT = re.compile(
    r"\.(jpg|jpeg|png|gif|webp|svg|ico|css|js|pdf|zip|mp4|mov|avi|woff2?|ttf|eot|xml|txt|json)$",
    re.I,
)


def norm(url: str, base_url: str) -> str | None:
    """Normalize a link to an absolute internal URL, or None if out of scope."""
    url = url.strip()
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    absu = urllib.parse.urljoin(base_url, url)
    p = urllib.parse.urlparse(absu)
    if p.scheme not in ("http", "https"):
        return None
    if p.netloc.lower().replace("www.", "") != HOST:
        return None
    path = p.path or "/"
    # strip fragment & query for canonical page identity
    clean = urllib.parse.urlunparse(("https", HOST, path, "", "", ""))
    if SKIP_EXT.search(path):
        return None
    upath = urllib.parse.unquote(path).lower()
    for d in DISALLOW:
        if d and upath.startswith(d.rstrip()):
            return None
    return clean


def cache_name(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    if path in ("", "/"):
        return "index.html"
    name = urllib.parse.unquote(path).lstrip("/")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "index.html"


def word_count(soup: BeautifulSoup) -> int:
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text = soup.get_text(" ", strip=True)
    return len(text.split())


def categorize(url: str, title: str, h1: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    name = urllib.parse.unquote(path).strip("/")
    t = (title + " " + h1).lower()
    if name in ("", "index.html", "index.htm"):
        return "home"
    if "bahama" in name:
        return "bahamas"
    if "caribbean" in name or any(k in name for k in (
        "jamaica", "st_lucia", "barbados", "turks", "cayman", "puerto_rico",
        "dominican", "antigua", "st_maarten", "bvi", "virgin")):
        return "caribbean"
    if "usa" in name or re.search(r"_(al|ak|az|ar|ca|co|ct|de|fl|ga|hi|id|il|in|ia|ks|ky|la|me|md|ma|mi|mn|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|vt|va|wa|wv|wi|wy)(\.htm|\.html)?$", name):
        return "usa"
    if name in ("canadian_air_charter_directory.html",):
        return "canada-hub"
    prov_hubs = (
        "alberta_charter_flights", "british_columbia_charter_flights",
        "labrador_charter_flights", "manitoba_charter_flights",
        "new_brunswick_charter_flights", "newfoundland_charter_flights",
        "nwt_charter_flights", "nova_scotia_charter_flights",
        "nunavut_charter_flights", "ontario_charter_flights",
        "southern_ontario_charter_flights", "quebec_charter_flights",
        "saskatchewan_charter_flights", "yukon_charter_flights",
    )
    if any(name.startswith(p) for p in prov_hubs):
        return "province-hub"
    if "empty_leg" in name or "empty-leg" in name:
        return "empty-legs"
    if any(k in name for k in ("jet_charter", "turboprop", "float_plane", "floatplane", "helicopter", "aircraft", "king_air", "pilatus", "caravan", "otter", "navajo", "citation", "learjet")):
        if "charter_flights_" not in name:
            return "aircraft"
    if any(k in name for k in ("about",)):
        return "about"
    if any(k in name for k in ("contact",)):
        return "contact"
    if any(k in name for k in ("quote_request_service", "list_your", "advertise", "featured_listing")):
        return "operators"
    if "charter_quote" in name:
        return "other"  # quote form/confirmation pages
    if re.search(r"_(ab|bc|mb|nb|nl|nt|ns|nu|on|pe|qc|sk|yt)(\.htm|\.html)$", name) or "charter_flights" in name:
        return "destination"
    return "other"


def extract(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    md = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    desc = md.get("content", "").strip() if md else ""
    h1el = soup.find("h1")
    h1 = h1el.get_text(" ", strip=True) if h1el else ""
    links = []
    for a in soup.find_all("a", href=True):
        n = norm(a["href"], url)
        if n:
            links.append(n)
    wc = word_count(soup)  # note: mutates soup (drops scripts)
    return {
        "url": url,
        "title": title,
        "meta_description": desc,
        "h1": h1,
        "word_count": wc,
        "category": categorize(url, title, h1),
        "cache_file": cache_name(url),
        "links": sorted(set(links)),
    }


def main():
    start = norm("/", BASE + "/")
    queue = [start]
    seen = {start}
    pages = {}
    errors = {}
    session = requests.Session()
    session.headers.update(HEADERS)

    n = 0
    while queue:
        url = queue.pop(0)
        cf = RAW / cache_name(url)
        html = None
        if cf.exists() and cf.stat().st_size > 0:
            html = cf.read_text(errors="replace")
        else:
            try:
                r = session.get(url, timeout=30, allow_redirects=True)
                time.sleep(1.0)
                # NB: this server mislabels .htm as "php5-fcgi", so sniff the body
                body_looks_html = "<html" in r.text[:2000].lower() or "<!doctype" in r.text[:2000].lower()
                if r.status_code == 200 and body_looks_html:
                    html = r.text
                    cf.write_text(html)
                else:
                    errors[url] = f"HTTP {r.status_code}"
                    continue
            except Exception as e:
                errors[url] = str(e)[:200]
                time.sleep(1.0)
                continue
        info = extract(url, html)
        pages[url] = {k: v for k, v in info.items() if k != "links"}
        for link in info["links"]:
            if link not in seen:
                seen.add(link)
                queue.append(link)
        n += 1
        if n % 25 == 0:
            print(f"[{n}] crawled, queue={len(queue)}", flush=True)
            OUT.write_text(json.dumps({"pages": list(pages.values()), "errors": errors}, indent=2))

    OUT.write_text(json.dumps({"pages": list(pages.values()), "errors": errors}, indent=2))
    print(f"DONE: {len(pages)} pages, {len(errors)} errors")


if __name__ == "__main__":
    main()
