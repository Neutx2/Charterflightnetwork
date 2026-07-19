#!/usr/bin/env python3
"""Phase 1: extract legacy page copy into markdown content collection.

Two-pass:
  1. Convert each cached page's main content to markdown lines.
  2. Drop boilerplate lines that appear on many pages (nav, footer, quote-form
     intro, sidebar adverts), keeping page-specific copy.

Outputs one .md file per page under src/content/<collection>/, plus
crawl/pagemeta.json (slug map, images, quote subjects) for later phases.
"""
import json
import re
import urllib.parse
from collections import Counter
from pathlib import Path

import ftfy
from bs4 import BeautifulSoup
from markdownify import markdownify as mdify

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "crawl" / "raw"
INV = json.load(open(ROOT / "crawl" / "inventory.json"))

PROVINCES = {
    "alberta_charter_flights": ("Alberta", "alberta"),
    "british_columbia_charter_flights": ("British Columbia", "british-columbia"),
    "labrador_charter_flights": ("Labrador", "labrador"),
    "manitoba_charter_flights": ("Manitoba", "manitoba"),
    "new_brunswick_charter_flights": ("New Brunswick", "new-brunswick"),
    "newfoundland_charter_flights": ("Newfoundland", "newfoundland"),
    "nwt_charter_flights": ("Northwest Territories", "northwest-territories"),
    "nova_scotia_charter_flights": ("Nova Scotia", "nova-scotia"),
    "nunavut_charter_flights": ("Nunavut", "nunavut"),
    "ontario_charter_flights": ("Northern Ontario", "northern-ontario"),
    "southern_ontario_charter_flights": ("Southern Ontario", "southern-ontario"),
    "quebec_charter_flights": ("Quebec", "quebec"),
    "saskatchewan_charter_flights": ("Saskatchewan", "saskatchewan"),
    "yukon_charter_flights": ("Yukon", "yukon"),
}

PROV_ABBR = {
    "ab": "alberta", "bc": "british-columbia", "mb": "manitoba",
    "nb": "new-brunswick", "nl": "newfoundland", "nt": "northwest-territories",
    "ns": "nova-scotia", "nu": "nunavut", "on": "northern-ontario",
    "qc": "quebec", "sk": "saskatchewan", "yt": "yukon", "pe": "prince-edward-island",
}

US_STATES = {
    "al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il","in","ia",
    "ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj",
    "nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt",
    "va","wa","wv","wi","wy",
}


def page_name(url: str) -> str:
    return urllib.parse.unquote(urllib.parse.urlparse(url).path).strip("/").lower()


def slugify(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def soup_for(url: str, cache_file: str) -> BeautifulSoup | None:
    p = RAW / cache_file
    if not p.exists():
        return None
    # The legacy server mislabels content-type (php5-fcgi, no charset), so
    # requests decoded UTF-8 pages as latin-1 → mojibake. ftfy repairs it.
    return BeautifulSoup(ftfy.fix_text(p.read_text(errors="replace")), "lxml")


def clean_soup(s: BeautifulSoup) -> BeautifulSoup:
    for tag in s(["script", "style", "noscript", "iframe", "form"]):
        tag.decompose()
    for tag in s.find_all("nav"):
        tag.decompose()
    # footer rows (bg-dark) and the quote-form band
    for tag in s.select(".bg-dark, #CharterQuote, footer"):
        tag.decompose()
    return s


def to_md_lines(s: BeautifulSoup) -> list[str]:
    body = s.find("body") or s
    md = mdify(str(body), heading_style="ATX", strip=["img"])
    lines = []
    for ln in md.splitlines():
        ln = ln.rstrip()
        # collapse hard-space padding
        ln = re.sub(r"\xa0+", " ", ln)
        ln = re.sub(r"[ \t]{2,}", " ", ln)
        lines.append(ln)
    # collapse blank runs
    out, blank = [], False
    for ln in lines:
        if not ln.strip():
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(ln)
            blank = False
    return out


def norm_line(ln: str) -> str:
    """Normalize a markdown line for boilerplate frequency counting."""
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", ln)  # strip link targets
    t = re.sub(r"[#*>\-`]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


# Quote-band copy that repeats under the legacy on-page form. The new templates
# render their own quote section, so these lines are dropped even when slight
# wording variations keep them under the global frequency threshold.
KILL_PREFIXES = (
    "charter flight network specializes in finding clients the most cost",
    "receive up to 3 competitive price quotes",
    "receive up to 3 competitive quotes",
    "how our quote service works",
    "if a quote meets your needs and budget",
    "*privacy: we don't share your name",
    "privacy: we don't share your name",
    "complete your travel details",
    "submit form below or phone us",
    "with just one click, receive up to 3",
    "complete and submit the following no obligation",
    "complete and submit your contact & travel information",
    "each airline prepares and submits a competitive quote",
    "here is how we do that",
    "when you complete and submit the form below",
    "request a free charter quote",
)


NAV_LINK_LINE = re.compile(
    r"^\s*\[\s*(HOME|CANADA|USA|BAHAMAS|CARIBBEAN|CONTACT|ABOUT|ADVERTISE)\s*\]\([^)]*\)\s*$",
    re.I,
)


def is_killed(norm: str) -> bool:
    n = norm.replace("’", "'")
    return any(n.startswith(p) for p in KILL_PREFIXES)


def main():
    pages = INV["pages"]
    print(f"{len(pages)} pages in inventory")

    # ---- pass 1: markdown lines per page
    page_lines: dict[str, list[str]] = {}
    meta: dict[str, dict] = {}
    for p in pages:
        s = soup_for(p["url"], p["cache_file"])
        if s is None:
            continue
        # capture quote form subject + images BEFORE cleaning
        subject = None
        subj = s.select_one('form input[name="subject"]')
        if subj:
            subject = re.sub(r"\s+", " ", subj.get("value", "")).strip()
        images = []
        for img in s.find_all("img", src=True):
            src = img["src"]
            if src.startswith("data:"):
                continue
            images.append({
                "src": urllib.parse.urljoin(p["url"], src),
                "alt": img.get("alt", ""),
            })
        canonical = None
        c = s.find("link", rel="canonical")
        if c:
            canonical = c.get("href")

        # re-extract title/desc/h1 from the ftfy-repaired soup (the crawler's
        # inventory copies carry the original mojibake)
        title = s.title.get_text(strip=True) if s.title else p["title"]
        mdesc_el = s.find("meta", attrs={"name": re.compile("^description$", re.I)})
        mdesc = mdesc_el.get("content", "").strip() if mdesc_el else p["meta_description"]
        h1_el = s.find("h1")
        h1 = h1_el.get_text(" ", strip=True) if h1_el else p["h1"]

        clean_soup(s)
        page_lines[p["url"]] = to_md_lines(s)
        meta[p["url"]] = {
            **{k: p[k] for k in ("url", "word_count", "category", "cache_file")},
            "title": title,
            "meta_description": mdesc,
            "h1": h1,
            "quote_subject": subject,
            "images": images,
            "canonical": canonical,
        }

    # ---- boilerplate detection
    freq = Counter()
    for lines in page_lines.values():
        seen = {norm_line(l) for l in lines if l.strip()}
        seen.discard("")
        freq.update(seen)
    n = len(page_lines)
    threshold = max(8, int(n * 0.20))
    boiler = {t for t, c in freq.items() if c >= threshold}
    print(f"boilerplate lines (>= {threshold} of {n} pages): {len(boiler)}")

    out = ROOT / "crawl" / "extracted"
    out.mkdir(exist_ok=True)
    for url, lines in page_lines.items():
        kept = []
        for ln in lines:
            if NAV_LINK_LINE.match(ln):
                continue  # leftover nav on pages whose menu isn't a <nav>
            t = norm_line(ln)
            if t and (t in boiler or is_killed(t)):
                continue
            kept.append(ln)
        # collapse blanks again
        final, blank = [], False
        for ln in kept:
            if not ln.strip():
                if not blank:
                    final.append("")
                blank = True
            else:
                final.append(ln)
                blank = False
        body = "\n".join(final).strip()
        meta[url]["extracted_words"] = len(re.sub(r"[^\w\s]", " ", body).split())
        name = re.sub(r"[^A-Za-z0-9._-]", "_", page_name(url) or "index")
        (out / (name + ".md")).write_text(body)

    json.dump(meta, open(ROOT / "crawl" / "pagemeta.json", "w"), indent=1)
    print("wrote crawl/pagemeta.json and crawl/extracted/*.md")

    # boilerplate sample for review
    (ROOT / "crawl" / "boilerplate_sample.txt").write_text(
        "\n".join(sorted(boiler)[:400])
    )


if __name__ == "__main__":
    main()
