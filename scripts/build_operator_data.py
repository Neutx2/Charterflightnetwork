#!/usr/bin/env python3
"""Build src/data/operators.json from the migrated directory pages.

Extracts ONLY facts present in the listings: operator name, address line,
phone numbers, base locations, aircraft types, service type, details text,
featured flag, and the directory page it appears on. Foundation for the
operator featured-listing product — no facts are invented or normalized
beyond whitespace.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "src" / "content" / "directory"
OUT = ROOT / "src" / "data" / "operators.json"

FIELD = re.compile(r"\*\*(Base Locations|Aircraft Types|Service Type|Details):\*\*\s*(.+)")
PHONE = re.compile(r"\[([^\]]+)\]\(tel:([^)]+)\)")

operators = []
for md in sorted(DIR.glob("*.md")):
    raw = md.read_text()
    fm_end = raw.index("---", 4)
    body = raw[fm_end + 3:]
    slug = re.search(r'slug: "(.*?)"', raw).group(1)

    # split on level-2 headings; a listing block contains at least one field line
    blocks = re.split(r"^## ", body, flags=re.M)
    prev_featured = False
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        rest = "\n".join(lines[1:])
        fields = {m.group(1): m.group(2).strip() for m in FIELD.finditer(rest)}
        featured = prev_featured
        # a block that's just the "Featured Listing" marker flags the NEXT block
        prev_featured = rest.strip().startswith("Featured Listing") or (
            not fields and "Featured Listing" in rest[:80]
        )
        if not fields or ("Base Locations" not in fields and "Service Type" not in fields):
            continue
        phones = [{"display": d, "tel": t} for d, t in PHONE.findall(rest)]
        # address = first non-empty line before the P:/field lines
        address = None
        for ln in lines[1:]:
            s = ln.strip()
            if not s or s.startswith(("P:", "**", "[")):
                if s.startswith("P:"):
                    break
                continue
            address = s
            break
        operators.append({
            "name": name,
            "address": address,
            "phones": phones,
            "baseLocations": fields.get("Base Locations"),
            "aircraftTypes": fields.get("Aircraft Types"),
            "serviceType": fields.get("Service Type"),
            "details": fields.get("Details"),
            "featured": featured,
            "directoryPage": "/" + slug,
        })

# de-duplicate exact repeats (same operator listed on multiple pages keeps
# each appearance's directoryPage)
OUT.parent.mkdir(exist_ok=True)
json.dump(operators, open(OUT, "w"), indent=1, ensure_ascii=False)
uniq = len({(o["name"], o["baseLocations"]) for o in operators})
print(f"{len(operators)} listings extracted ({uniq} unique name+base pairs) -> {OUT.relative_to(ROOT)}")
