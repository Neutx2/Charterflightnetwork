#!/usr/bin/env python3
"""Phase 1b: turn extracted markdown + pagemeta.json into the Astro content
collection, the operator-quote-page data file, and the legacy→new redirect map.
"""
import json
import re
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
META = json.load(open(ROOT / "crawl" / "pagemeta.json"))
EXTRACTED = ROOT / "crawl" / "extracted"
RAW = ROOT / "crawl" / "raw"

PROV_HUBS = {
    "alberta_charter_flights.htm": ("Alberta", "alberta"),
    "british_columbia_charter_flights.htm": ("British Columbia", "british-columbia"),
    "labrador_charter_flights.htm": ("Labrador", "labrador"),
    "manitoba_charter_flights.htm": ("Manitoba", "manitoba"),
    "new_brunswick_charter_flights.htm": ("New Brunswick", "new-brunswick"),
    "newfoundland_charter_flights.htm": ("Newfoundland", "newfoundland"),
    "nwt_charter_flights.htm": ("Northwest Territories", "northwest-territories"),
    "nova_scotia_charter_flights.htm": ("Nova Scotia", "nova-scotia"),
    "nunavut_charter_flights.htm": ("Nunavut", "nunavut"),
    "ontario_charter_flights.htm": ("Northern Ontario", "northern-ontario"),
    "southern_ontario_charter_flights.htm": ("Southern Ontario", "southern-ontario"),
    "quebec_charter_flights.htm": ("Quebec", "quebec"),
    "saskatchewan_charter_flights.htm": ("Saskatchewan", "saskatchewan"),
    "yukon_charter_flights.htm": ("Yukon", "yukon"),
}

PROV_ABBR = {
    "ab": ("Alberta", "alberta"),
    "bc": ("British Columbia", "british-columbia"),
    "mb": ("Manitoba", "manitoba"),
    "nb": ("New Brunswick", "new-brunswick"),
    "nl": ("Newfoundland", "newfoundland"),
    "nf": ("Newfoundland", "newfoundland"),
    "lab": ("Labrador", "labrador"),
    "nwt": ("Northwest Territories", "northwest-territories"),
    "nt": ("Northwest Territories", "northwest-territories"),
    "ns": ("Nova Scotia", "nova-scotia"),
    "nu": ("Nunavut", "nunavut"),
    "on": ("Northern Ontario", "northern-ontario"),
    "qc": ("Quebec", "quebec"),
    "sk": ("Saskatchewan", "saskatchewan"),
    "yt": ("Yukon", "yukon"),
    "yk": ("Yukon", "yukon"),
    "pei": ("Prince Edward Island", "prince-edward-island"),
    "pe": ("Prince Edward Island", "prince-edward-island"),
}

US_STATES = {
    "al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il","in","ia",
    "ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj",
    "nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt",
    "va","wa","wv","wi","wy","dc",
}

SPECIAL = {
    "": ("home", "/"),
    "index.html": ("home", "/"),
    "index.htm": ("home", "/"),
    "canadian_charter_flight_network.htm": ("home-alias", "/"),
    "about_charter_flight_network.htm": ("page", "about"),
    "privacy_policy.htm": ("page", "privacy-policy"),
    "contact_us.htm": ("page", "contact"),
    "charter_quote.html": ("page", "quote"),
    "charter_quote.htm": ("page", "quote"),
    "charter_quote_confirmation.htm": ("page", "quote-confirmation"),
    "charter_quote_request_service.html": ("page", "operators"),
    "canadian_air_charter_directory.html": ("page", "directory"),
    "usa_charter_flight_network.htm": ("hub-usa", "usa"),
    "charter_flights_bahamas.html": ("hub-bahamas", "bahamas"),
    "charter_flights_caribbean.html": ("hub-caribbean", "caribbean"),
}


def pname(url: str) -> str:
    return urllib.parse.unquote(urllib.parse.urlparse(url).path).strip("/")


def slugify(s: str) -> str:
    s = s.lower().replace("&", " and ").replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def extract_city(meta: dict, fallback: str) -> str:
    """Best-effort city name from H1 or title."""
    for source in (meta.get("h1") or "", meta.get("title") or ""):
        t = source
        t = re.sub(r"\(.*?\)", " ", t)
        t = re.sub(r"(?i)direct charter flights? to", " ", t)
        t = re.sub(r"(?i)charter flights? (to|from|in)\b", " ", t)
        t = re.sub(r"(?i)charter flights?", " ", t)
        t = re.sub(r"(?i)wheel,? float & helicopter charters?", " ", t)
        t = re.sub(r"(?i)wheel plane,? float plane (and|&|or) helicopter charters?", " ", t)
        t = re.sub(r"(?i)charter flight network", " ", t)
        t = re.sub(r"[|/–—-]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip(" ,.")
        # drop trailing province words
        t = re.sub(r"(?i)\s+(alberta|british columbia|labrador|manitoba|new brunswick|newfoundland|northwest territories|nova scotia|nunavut|ontario|quebec|saskatchewan|yukon|bahamas?|caribbean)$", "", t).strip(" ,.")
        if 2 <= len(t) <= 40:
            return t
    return fallback.replace("_", " ").replace("-", " ").title()


def airport_code(meta: dict) -> str | None:
    for source in (meta.get("h1") or "", meta.get("title") or ""):
        m = re.search(r"\(([A-Z]{3,4}\d?)\)", source)
        if m and m.group(1) not in ("YQT2",):
            return m.group(1)
    return None


def hub_links(cache_file: str) -> set[str]:
    """Page names linked from a hub page."""
    p = RAW / cache_file
    if not p.exists():
        return set()
    s = BeautifulSoup(p.read_text(errors="replace"), "lxml")
    out = set()
    for a in s.find_all("a", href=True):
        h = a["href"]
        if h.startswith(("http", "#", "mailto:", "tel:")):
            continue
        out.add(urllib.parse.unquote(h).lstrip("/").split("#")[0].split("?")[0])
    return out


def classify() -> dict[str, dict]:
    # ontario membership from hub links (northern vs southern)
    north_links = hub_links("ontario_charter_flights.htm")
    south_links = hub_links("southern_ontario_charter_flights.htm")

    result = {}
    for url, m in META.items():
        name = pname(url)
        low = name.lower()
        entry = {"legacyUrl": "/" + name if name else "/", "meta": m}

        if low in SPECIAL:
            kind, slug = SPECIAL[low]
            entry.update(kind=kind, slug=slug)
        elif low in PROV_HUBS or low.rsplit(".", 1)[0] + ".htm" in PROV_HUBS:
            key = low if low in PROV_HUBS else low.rsplit(".", 1)[0] + ".htm"
            prov, pslug = PROV_HUBS[key]
            entry.update(kind="hub-province", slug=f"canada/{pslug}", province=prov, provinceSlug=pslug)
        elif re.match(r"charter_quote_[a-z0-9_]+\.html?$", low):
            op = re.sub(r"^charter_quote_|\.html?$", "", low).replace("_", " ").title()
            entry.update(kind="operator-quote", slug=f"quote/{slugify(op)}", operator=op)
        elif "directory" in low or low in (
            "ontario_usa_charter_airlines.html",
            "canadian_air_charter_licenced_flights_usa_directory.html",
        ):
            base = re.sub(r"\.html?$", "", low)
            entry.update(kind="directory", slug=f"directory/{slugify(base)}")
        else:
            m2 = re.match(r"charter_flights?_(?:to_)?(.+?)_(bahamas|caribbean)\.html?$", low)
            m3 = re.match(r"charter_flights?_(?:to_)?(.+?)_([a-z]{2,3})\.html?$", low)
            m4 = re.match(r"(.+?)_charter_flights?\.html?$", low)
            m5 = re.match(r"charter_flights?_(?:to_)?(.+?)\.html?$", low)
            if m2:
                region = m2.group(2)
                city = extract_city(m, m2.group(1))
                entry.update(kind=f"dest-{region}", slug=f"{region}/{slugify(city)}", city=city)
            elif m3 and m3.group(2) in PROV_ABBR:
                prov, pslug = PROV_ABBR[m3.group(2)]
                city = extract_city(m, m3.group(1))
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            elif m3 and m3.group(2) in US_STATES:
                city = extract_city(m, m3.group(1))
                st = m3.group(2)
                entry.update(kind="dest-usa", slug=f"usa/{slugify(city)}-{st}", city=city)
            elif m4 or m5:
                raw_city = (m4 or m5).group(1)
                city = extract_city(m, raw_city)
                # Ontario naming style — assign hub by which Ontario hub links here
                if low in south_links and low not in north_links:
                    prov, pslug = "Southern Ontario", "southern-ontario"
                else:
                    prov, pslug = "Northern Ontario", "northern-ontario"
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            else:
                entry.update(kind="other", slug=f"directory/{slugify(re.sub(r'\\.html?$', '', low))}")
        result[url] = entry
    return result


def frontmatter(d: dict) -> str:
    lines = ["---"]
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        else:
            v = str(v).replace('"', "'").replace("\n", " ").strip()
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)


def main():
    classified = classify()

    # ---- resolve slug collisions (two legacy pages → same slug)
    by_slug: dict[str, list[str]] = {}
    for url, e in classified.items():
        by_slug.setdefault(e["slug"], []).append(url)
    for slug, urls in by_slug.items():
        if len(urls) > 1 and not slug.startswith(("quote", "directory")):
            # keep the page with the most extracted words as canonical; others redirect
            urls.sort(key=lambda u: classified[u]["meta"].get("extracted_words", 0), reverse=True)
            for dup in urls[1:]:
                classified[dup]["kind"] = "redirect-only"
                classified[dup]["redirect_to"] = slug

    # ---- write markdown collection
    counts = {}
    content = ROOT / "src" / "content"
    for sub in ("destinations", "hubs", "aircraft", "directory", "pages"):
        d = content / sub
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.md"):
            f.unlink()

    redirects = {}  # legacyUrl -> new path
    operator_pages = []
    thin_pages = []

    region_of = {"dest-canada": "canada", "dest-usa": "usa", "dest-bahamas": "bahamas", "dest-caribbean": "caribbean"}

    for url, e in classified.items():
        m = e["meta"]
        kind = e["kind"]
        counts[kind] = counts.get(kind, 0) + 1
        new_path = "/" + e["slug"] if e["slug"] != "/" else "/"
        if kind == "redirect-only":
            redirects[e["legacyUrl"]] = "/" + e["redirect_to"]
            continue
        redirects[e["legacyUrl"]] = new_path

        name = re.sub(r"[^A-Za-z0-9._-]", "_", pname(url) or "index")
        body_file = EXTRACTED / (name + ".md")
        body = body_file.read_text() if body_file.exists() else ""
        words = m.get("extracted_words", 0)
        thin = words < 120
        if thin:
            thin_pages.append({"url": url, "words": words, "slug": e["slug"]})

        title = (m.get("title") or "").strip() or extract_city(m, name)
        desc = (m.get("meta_description") or "").strip()
        if not desc:
            desc = f"Charter flights — receive up to 3 competitive quotes. Free, no obligation."

        common = {
            "title": title,
            "description": desc,
            "h1": (m.get("h1") or "").strip() or None,
            "legacyUrl": e["legacyUrl"],
            "slug": e["slug"],
            "thin": thin,
            "quoteSubject": m.get("quote_subject") or None,
        }

        if kind in region_of:
            fm = {
                **common,
                "region": region_of[kind],
                "province": e.get("province"),
                "provinceSlug": e.get("provinceSlug"),
                "city": e.get("city"),
                "airportCode": airport_code(m),
            }
            out = content / "destinations" / (slugify(e["slug"]) + ".md")
        elif kind == "hub-province":
            fm = {**common, "region": "canada", "province": e.get("province"), "provinceSlug": e.get("provinceSlug")}
            out = content / "hubs" / (slugify(e["slug"]) + ".md")
        elif kind in ("hub-usa", "hub-bahamas", "hub-caribbean"):
            fm = {**common, "region": kind.split("-")[1]}
            out = content / "hubs" / (slugify(e["slug"]) + ".md")
        elif kind == "directory":
            fm = {**common, "region": "canada"}
            out = content / "directory" / (slugify(e["slug"].split("/", 1)[1]) + ".md")
        elif kind == "operator-quote":
            operator_pages.append({
                "slug": e["slug"].split("/", 1)[1],
                "name": e["operator"],
                "title": title,
                "description": desc or f"Request a charter quote direct from {e['operator']} — free, no obligation.",
                "subject": m.get("quote_subject") or e["operator"],
            })
            continue
        elif kind == "page":
            fm = {**common, "region": "global"}
            out = content / "pages" / (slugify(e["slug"]) + ".md")
        else:  # home, home-alias, other→directory already handled by slug
            continue

        out.write_text(frontmatter(fm) + "\n\n" + body + "\n")

    # ---- rewrite internal legacy links inside markdown bodies
    link_map = {k.lstrip("/"): v for k, v in redirects.items()}
    for md in content.rglob("*.md"):
        text = md.read_text()
        def repl(match):
            target = match.group(2).strip()
            t = urllib.parse.unquote(target).lstrip("/").split("#")[0]
            if t in link_map:
                return f"[{match.group(1)}]({link_map[t]})"
            if t.endswith((".htm", ".html")) and not t.startswith("http"):
                return match.group(1)  # drop dead internal link, keep text
            return match.group(0)
        text = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", repl, text)
        md.write_text(text)

    (ROOT / "src" / "data").mkdir(exist_ok=True)
    json.dump(operator_pages, open(ROOT / "src" / "data" / "operator-quote-pages.json", "w"), indent=1)
    json.dump(redirects, open(ROOT / "crawl" / "redirects.json", "w"), indent=1)
    json.dump(thin_pages, open(ROOT / "crawl" / "thin_pages.json", "w"), indent=1)
    print(json.dumps(counts, indent=1))
    print(f"redirects: {len(redirects)}  thin: {len(thin_pages)}  operators: {len(operator_pages)}")


if __name__ == "__main__":
    main()
