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
    # operator / marketing program pages (real content incl. listing pricing)
    "list_your_airline.html": ("page", "operators/update-your-listing"),
    "premium_listing_submit.html": ("page", "operators/listing-options"),
    "marketing_partners.html": ("page", "operators/marketing-partners"),
    # audience / use-case pages
    "subscription_marketing.html": ("page", "travel/adventure-newsletter"),
    "charter_flights_to_adventure.html": ("page", "travel/charter-flights-to-adventure"),
    "business_travel_group.html": ("page", "travel/business-travel"),
    "canadian_arctic_travel_group.html": ("page", "travel/canadian-arctic"),
    "canadian_fishing_travel_group.html": ("page", "travel/fly-in-fishing"),
    "churchill_polar_bear_travel_group.html": ("page", "travel/churchill-polar-bears"),
    "churchill_polar_bear_package.html": ("page", "travel/churchill-polar-bear-package"),
    "golf_adventure_travel_group.html": ("page", "travel/golf-adventures"),
    "mining_exploration_travel_group.html": ("page", "travel/mining-exploration"),
    "ontario_remote_community_travel.html": ("page", "travel/ontario-remote-communities"),
    "puerto_rico_fishing_adventures.html": ("page", "travel/puerto-rico-fishing"),
    "puerto_rico_golf_courses.html": ("page", "travel/puerto-rico-golf"),
    "puerto_rico_resorts.html": ("page", "travel/puerto-rico-resorts"),
    "puerto_rico_yacht_charters.html": ("page", "travel/puerto-rico-yachts"),
    "st_lucia_fishing_adventures.html": ("page", "travel/st-lucia-fishing"),
    "st_lucia_golf_resorts.html": ("page", "travel/st-lucia-golf"),
    "st_lucia_resorts.html": ("page", "travel/st-lucia-resorts"),
    "st_lucia_sail_boat_charters.html": ("page", "travel/st-lucia-sailing"),
    # aircraft-specific quote form pages → single /quote page
    "private_jet_charter_quote.html": ("alias", "quote"),
    "helicopter_charter_quote.html": ("alias", "quote"),
    "float_plane_charter_quote.html": ("alias", "quote"),
    "golf_charter_flight_quote.html": ("alias", "quote"),
    # generic quote-request pages that look like destinations by filename only
    # (both titled "Request A Charter Quote" with no destination content)
    "group_charter_flights.htm": ("alias", "quote"),
    "pei_charter_flights.htm": ("alias", "quote"),
    # route page misparsed as a city ("Winnipeg Red Lake")
    "charter_flights_winnipeg_red_lake_ontario.html": ("route-fixed", "flights/winnipeg-to-red-lake"),
    # Ontario north/south corrections (content signal misfires on these)
    "nakina_charter_flights.htm": ("dest-fixed", ("canada/northern-ontario/nakina", "Nakina", "Northern Ontario", "northern-ontario")),
    "charter_flights_to_burlington.htm": ("dest-fixed", ("canada/southern-ontario/burlington", "Burlington", "Southern Ontario", "southern-ontario")),
    "oshawa charter_flights.htm": ("dest-fixed", ("canada/southern-ontario/oshawa", "Oshawa", "Southern Ontario", "southern-ontario")),
    "oshawa_charter_flights.htm": ("dest-fixed", ("canada/southern-ontario/oshawa", "Oshawa", "Southern Ontario", "southern-ontario")),
    # odd destinations
    "flights_baffin_island.html": ("dest-fixed", ("canada/nunavut/baffin-island", "Baffin Island", "Nunavut", "nunavut")),
    "charter_flights_torngat_mountains_park.html": ("dest-fixed", ("canada/labrador/torngat-mountains-park", "Torngat Mountains Park", "Labrador", "labrador")),
    "charter_flights_rocky_mountain_house.html": ("dest-fixed", ("canada/alberta/rocky-mountain-house", "Rocky Mountain House", "Alberta", "alberta")),
    "charter_flights_port_loring.html": ("dest-fixed", ("canada/northern-ontario/port-loring", "Port Loring", "Northern Ontario", "northern-ontario")),
    "tofino_helicopter_flights_tours.html": ("dest-fixed", ("canada/british-columbia/tofino-helicopter-tours", "Tofino", "British Columbia", "british-columbia")),
    "tofino_seaplane_flights_tours.html": ("dest-fixed", ("canada/british-columbia/tofino-seaplane-tours", "Tofino", "British Columbia", "british-columbia")),
}

FULL_SUFFIX = {
    "alberta": ("Alberta", "alberta"),
    "quebec": ("Quebec", "quebec"),
    "ontario": ("Northern Ontario", "northern-ontario"),
    "bahama": None,  # → bahamas region
    "bahamas": None,
}


def pname(url: str) -> str:
    return urllib.parse.unquote(urllib.parse.urlparse(url).path).strip("/")


def slugify(s: str) -> str:
    s = s.lower().replace("&", " and ").replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


LOWER_WORDS = {"du", "de", "la", "le", "des", "aux", "sur", "and", "of", "the"}


def city_from_filename(raw: str) -> str:
    """Legacy filenames are the cleanest city source (titles carry marketing noise)."""
    words = [w for w in re.split(r"[_\-\s]+", raw.strip()) if w]
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        out.append(lw if (lw in LOWER_WORDS and i > 0) else lw.capitalize())
    return " ".join(out)


def page_text(cache_file: str) -> str:
    p = RAW / cache_file
    return p.read_text(errors="replace").lower() if p.exists() else ""


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
    # membership across every province hub for fallback assignment
    hub_membership = {}
    for hub_file, (prov, pslug) in PROV_HUBS.items():
        cache = re.sub(r"[^A-Za-z0-9._-]", "_", hub_file)
        for linked in hub_links(cache):
            hub_membership.setdefault(linked.lower(), (prov, pslug))

    result = {}
    for url, m in META.items():
        name = pname(url)
        low = name.lower()
        entry = {"legacyUrl": "/" + name if name else "/", "meta": m}

        if low in SPECIAL:
            kind, slug = SPECIAL[low]
            if kind == "dest-fixed":
                sl, city, prov, pslug = slug
                entry.update(kind="dest-canada", slug=sl, city=city, province=prov, provinceSlug=pslug)
            elif kind == "route-fixed":
                entry.update(kind="route", slug=slug)
            elif kind == "alias":
                entry.update(kind="redirect-only", slug=slug, redirect_to=slug)
            else:
                entry.update(kind=kind, slug=slug)
        elif re.match(r"^[a-z_]+_charter_flights?_[a-z_]+\.html?$", low) and re.match(r"^(toronto|kitchener|minneapolis|oshawa)", low):
            # city-pair route pages, e.g. toronto_charter_flights_chicago.html
            base = re.sub(r"\.html?$", "", low)
            m_pair = re.match(r"^(.+?)_charter_flights?_(.+)$", base)
            entry.update(kind="route", slug=f"flights/{slugify(m_pair.group(1))}-to-{slugify(m_pair.group(2))}")
        elif re.match(r"^(jet_charter|charter_flights)_toronto_[a-z_]+\.html?$", low) or low == "charter_flights_campbell_river_from_calgary.html":
            base = re.sub(r"\.html?$", "", re.sub(r"^(jet_charter|charter_flights)_", "", low))
            entry.update(kind="route", slug=f"flights/{slugify(base)}")
        elif re.match(r"^(wheel_plane|float_plane|helicopter)_charters?_[a-z_]*(bc|ontario[_0-9]*)[0-9_]*\.html?$", low) or re.match(r"^northern_ontario_float_plane_\d+\.html?$", low):
            base = re.sub(r"\.html?$", "", low)
            entry.update(kind="directory", slug=f"directory/{slugify(base)}")
        elif re.match(r"^[a-z_]+_bc_float_plane_charters\.html?$", low):
            base = re.sub(r"_bc_float_plane_charters\.html?$", "", low)
            city = extract_city(m, base)
            entry.update(kind="dest-canada", slug=f"canada/british-columbia/{slugify(base)}-float-plane-charters",
                         city=city, province="British Columbia", provinceSlug="british-columbia")
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
            m2 = re.match(r"charter_flights?_(?:to_)?(.+?)_(bahamas?|caribbean)\.html?$", low)
            m3 = re.match(r"charter_flights?_(?:to_)?(.+?)_([a-z]{2,3})\.html?$", low)
            m3b = re.match(r"charter_flights?_(?:to_)?(.+?)_(alberta|quebec|ontario)\.html?$", low)
            m4 = re.match(r"(.+?)_charter_flights?\.html?$", low)
            m5 = re.match(r"charter_flights?_(?:to_)?(.+?)\.html?$", low)
            if m2:
                region = "bahamas" if m2.group(2).startswith("bahama") else "caribbean"
                city = city_from_filename(m2.group(1))
                entry.update(kind=f"dest-{region}", slug=f"{region}/{slugify(city)}", city=city)
            elif m3b:
                prov, pslug = FULL_SUFFIX[m3b.group(2)] or ("", "")
                city = city_from_filename(m3b.group(1))
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            elif m3 and m3.group(2) in PROV_ABBR:
                prov, pslug = PROV_ABBR[m3.group(2)]
                city = city_from_filename(m3.group(1))
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            elif m3 and m3.group(2) in US_STATES:
                city = city_from_filename(m3.group(1))
                st = m3.group(2)
                entry.update(kind="dest-usa", slug=f"usa/{slugify(city)}-{st}", city=city)
            elif m4 or m5:
                raw_city = (m4 or m5).group(1)
                # strip trailing province abbr from names like armstrong_on_charter_flights
                raw_city = re.sub(r"_(on|ab|bc|mb|nb|nl|nt|ns|nu|qc|sk|yt)$", "", raw_city)
                city = city_from_filename(raw_city)
                # "london_ontario" style names → "London"
                city = re.sub(r"\s+(Ontario|Quebec|Alberta)$", "", city)
                if low in south_links and low not in north_links:
                    prov, pslug = "Southern Ontario", "southern-ontario"
                elif low in north_links:
                    prov, pslug = "Northern Ontario", "northern-ontario"
                elif low in hub_membership:
                    prov, pslug = hub_membership[low]
                elif "southern ontario" in page_text(m["cache_file"]):
                    prov, pslug = "Southern Ontario", "southern-ontario"
                else:
                    prov, pslug = "Northern Ontario", "northern-ontario"
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            elif low in hub_membership:
                prov, pslug = hub_membership[low]
                base = re.sub(r"\.html?$", "", low)
                city = city_from_filename(base)
                entry.update(kind="dest-canada", slug=f"canada/{pslug}/{slugify(city)}", city=city, province=prov, provinceSlug=pslug)
            else:
                base = re.sub(r"\.html?$", "", low)
                entry.update(kind="other", slug=f"directory/{slugify(base)}")
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
            target = e["redirect_to"]
            redirects[e["legacyUrl"]] = target if target.startswith("/") else "/" + target
            continue
        redirects[e["legacyUrl"]] = new_path

        # extract.py lowercases its output filenames — match that here
        name = re.sub(r"[^A-Za-z0-9._-]", "_", (pname(url) or "index").lower())
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
        elif kind in ("directory", "other"):
            fm = {**common, "region": "canada"}
            out = content / "directory" / (slugify(e["slug"].split("/", 1)[1]) + ".md")
        elif kind == "route":
            fm = {**common, "region": "global"}
            out = content / "pages" / (slugify(e["slug"]) + ".md")
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

    # ---- clean markdown bodies: heading levels, links, anchors
    link_map = {k.lstrip("/"): v for k, v in redirects.items()}

    def rewrite_target(target: str) -> str | None:
        """Map a legacy link target to a new path; None = drop link keep text."""
        t = target.strip()
        # our own domain → path; collapse stray protocol-relative slashes
        t = re.sub(r"^https?://(www\.)?charterflightnetwork\.com/?", "", t)
        if re.fullmatch(r"/{2,}", t):
            t = "/"
        if t.startswith(("http", "mailto:", "tel:")):
            return target  # external, keep as-is
        anchor = ""
        if "#" in t:
            t, frag = t.split("#", 1)
            anchor = "#quote" if frag == "CharterQuote" else f"#{frag}"
        t = urllib.parse.unquote(t).lstrip("/").split("?")[0]
        if not t:
            return anchor or "/"
        if t in link_map:
            return link_map[t] + anchor
        if t.endswith((".htm", ".html", ".php")):
            return None  # dead internal link
        return target

    for md in content.rglob("*.md"):
        raw = md.read_text()
        fm_end = raw.index("---", 4)
        fm, text = raw[: fm_end + 3], raw[fm_end + 3 :]

        def repl(match):
            new = rewrite_target(match.group(2))
            if new is None:
                return match.group(1)
            return f"[{match.group(1)}]({new})"

        text = re.sub(r"\[([^\]]*)\]\(<?([^)>\s]+)>?\)", repl, text)

        out_lines = []
        for ln in text.splitlines():
            m2 = re.match(r"^(#{1,6})\s*(.*)$", ln)
            if m2:
                level, head = m2.groups()
                head = head.strip()
                if not head:
                    continue  # empty heading
                if len(level) == 1:
                    continue  # page h1 comes from the template
                ln = ("##" if len(level) <= 4 else "###") + " " + head
            out_lines.append(ln)
        # collapse blank runs
        final, blank = [], False
        for ln in out_lines:
            if not ln.strip():
                if not blank:
                    final.append("")
                blank = True
            else:
                final.append(ln)
                blank = False
        md.write_text(fm + "\n" + "\n".join(final).strip() + "\n")

    # ---- hub pages: drop legacy destination-link bullet lists (the hub
    # template renders a generated destination grid, so these are duplicates)
    dest_link = re.compile(r"^\s*\*\s*\[[^\]]+\]\(/(canada|usa|bahamas|caribbean)/[^)]+\)\s*$")
    for md in (content / "hubs").glob("*.md"):
        raw = md.read_text()
        fm_end = raw.index("---", 4)
        fm, text = raw[: fm_end + 3], raw[fm_end + 3 :]
        lines = [ln for ln in text.splitlines() if not dest_link.match(ln)]
        md.write_text(fm + "\n" + "\n".join(lines))

    # ---- drop headings whose section ended up empty (next content is another
    # heading, a rule, or end of file)
    for md in content.rglob("*.md"):
        raw = md.read_text()
        fm_end = raw.index("---", 4)
        fm, text = raw[: fm_end + 3], raw[fm_end + 3 :]
        lines = text.splitlines()
        out = []
        for i, ln in enumerate(lines):
            if re.match(r"^#{2,6}\s+\S", ln):
                has_content = False
                for nxt in lines[i + 1:]:
                    if not nxt.strip() or nxt.strip() == "---":
                        continue
                    has_content = not nxt.lstrip().startswith("#")
                    break
                if not has_content:
                    continue
            out.append(ln)
        # collapse blank/rule runs left behind
        cleaned, prev_blankish = [], False
        for ln in out:
            blankish = not ln.strip() or ln.strip() == "---"
            if blankish and prev_blankish:
                continue
            cleaned.append(ln)
            prev_blankish = blankish
        md.write_text(fm + "\n" + "\n".join(cleaned).strip() + "\n")

    # ---- editorial overrides: curated replacements applied last
    overrides = ROOT / "crawl" / "overrides"
    replaced = 0
    if overrides.exists():
        for ov in overrides.rglob("*.md"):
            rel = ov.relative_to(overrides)
            target = content / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(ov.read_text())
            replaced += 1
    print(f"editorial overrides applied: {replaced}")

    # ---- extract FAQ sections into frontmatter for FAQPage JSON-LD
    faq_pages = 0
    for md in content.rglob("*.md"):
        raw = md.read_text()
        fm_end = raw.index("---", 4)
        fm, text = raw[: fm_end + 3], raw[fm_end + 3 :]
        m_faq = re.search(r"^##+ .*frequently asked questions.*$", text, re.I | re.M)
        if not m_faq:
            continue
        section = text[m_faq.end():]
        # Questions may sit at ## or ### level (legacy heading levels were
        # flattened). A heading is a question if it ends in "?" or starts with a
        # question word; any other heading ends the FAQ section.
        pairs = []
        q, answer = None, []
        qword = re.compile(r"^(what|can|how|is|are|do|does|why|when|where|which|who)\b", re.I)

        def flush():
            if q and answer:
                a = " ".join(answer)
                a = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", a)
                a = re.sub(r"[*_`]", "", a)
                a = re.sub(r"\s+", " ", a).strip()
                if len(a) > 5:
                    pairs.append({"q": q, "a": a})

        for ln in section.splitlines():
            hm = re.match(r"^(#{2,6})\s+(.+)$", ln)
            if hm:
                head = hm.group(2).strip()
                if head.endswith("?") or qword.match(head):
                    flush()
                    q, answer = head, []
                    continue
                break  # non-question heading → FAQ section over
            if q and ln.strip():
                answer.append(ln.strip())
        flush()
        if pairs:
            faq_pages += 1
            fm = fm[:-3].rstrip() + "\nfaqs: " + json.dumps(pairs, ensure_ascii=False) + "\n---"
            md.write_text(fm + text)
    print(f"faq pages: {faq_pages}")

    (ROOT / "src" / "data").mkdir(exist_ok=True)
    json.dump(operator_pages, open(ROOT / "src" / "data" / "operator-quote-pages.json", "w"), indent=1)
    json.dump(redirects, open(ROOT / "crawl" / "redirects.json", "w"), indent=1)
    json.dump(thin_pages, open(ROOT / "crawl" / "thin_pages.json", "w"), indent=1)
    print(json.dumps(counts, indent=1))
    print(f"redirects: {len(redirects)}  thin: {len(thin_pages)}  operators: {len(operator_pages)}")


if __name__ == "__main__":
    main()
