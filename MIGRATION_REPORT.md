# Charter Flight Network — Migration Report

Migration of https://charterflightnetwork.com from a ~2005-era static `.htm` site
(Bootstrap 4, table-era markup, 1,000+ hand-edited files) to a modern, fully
static **Astro + Tailwind CSS** build. Faithful migration: same business model,
same content, same conversion funnel, SEO equity preserved via a complete 301
map.

## Inventory (Phase 0)

No `sitemap.xml` existed; the site was crawled from the homepage, internal links
only, throttled ~1 req/sec, respecting `robots.txt` (44 disallowed legacy paths
were not crawled). Every fetched page is cached in `crawl/raw/` and inventoried
in `crawl/inventory.json` (URL, title, meta description, H1, word count,
category).

**1,046 unique live pages** were inventoried and migrated:

| Category | Pages | New location |
|---|---|---|
| Canadian city destination pages | 689 | `/canada/<province>/<city>` |
| Operator-specific quote pages | 100 | `/quote/<operator>` |
| Charter directory pages (by province × wheel/float/helicopter/USA-licensed) | 150 | `/directory/<slug>` |
| Bahamas island destinations | 19 | `/bahamas/<island>` |
| Caribbean island destinations | 25 | `/caribbean/<island>` |
| Province/territory hubs (incl. N./S. Ontario split) | 14 | `/canada/<province>` |
| Region hubs (USA / Bahamas / Caribbean) | 3 | `/usa` `/bahamas` `/caribbean` |
| City-pair route pages (e.g. Toronto–Chicago) | 11 | `/flights/<route>` |
| Travel/audience pages (fly-in fishing, mining, Churchill, golf, arctic…) | ~18 | `/travel/<slug>` |
| Operator marketing/program pages | 4 | `/operators/*` |
| Core pages (home, about, contact, privacy, quote, USA dest) | remainder | `/`, `/about`, `/contact`, … |

Also recorded: **54 broken internal links on the legacy site** (linked pages
returning 404, including one URL with corrupted markup `kan</p>sas_air...`) —
listed in `crawl/inventory.json → errors`. These were dead *before* the
migration; nothing was lost.

## Content migration (Phase 1)

- One markdown file per page under `src/content/{destinations,hubs,directory,pages}/`
  with frontmatter: `title`, `description`, `h1`, `region`, `province`,
  `provinceSlug`, `city`, `airportCode`, `legacyUrl`, `slug`, `thin`,
  `quoteSubject`, `faqs`.
- Copy was preserved substantively: repeated site chrome (nav, footer, the
  on-page quote-form band) was stripped via frequency analysis across all 1,046
  pages + an explicit kill-list; the page-specific writing was kept as-is,
  including local operator mentions (Thunder Bay keeps Wasaya Airways, Lakehead
  Airways, Zimmer Air, Wisk Air, Air Bravo, North Star Air exactly as written).
- Legacy quote-form `subject` values (e.g. "Thunder Bay Quote") are preserved
  per page so operator email routing keeps working.
- FAQ sections found on 28 pages were parsed into frontmatter and now emit
  `FAQPage` JSON-LD.
- Northern vs Southern Ontario assignment was resolved from hub links plus an
  on-page content signal ("Southern Ontario" mention) since the legacy southern
  hub only directly linked 2 of its ~50 cities.
- 2,153 unique referenced images inventoried; **1,979 downloaded** to
  `src/assets/legacy/` (preserving the `CFN Images/` folder structure) and
  **174 were already broken (404) on the legacy server** — manifest with alt
  text, per-page usage and failures in `crawl/image_manifest.json`.

## Build (Phase 2)

- **Stack**: Astro 7 (static output, zero JS frameworks — the only client JS is
  ~1 KB vanilla for mobile nav + form validation), Tailwind CSS 4, TypeScript,
  self-hosted variable fonts (Inter + Outfit, `font-display: optional` → no CLS).
- **Design**: northern palette (deep lake blue / boreal green / warm white /
  ember CTA), sticky header with "Get Free Quotes" + click-to-call phone,
  mobile-first. Placeholder hero/region images are hand-built SVG scenes with
  descriptive filenames (`boreal-lake-float-plane-dawn.svg`) — flagged below for
  replacement with real photography.
- **Conversion funnel preserved**: every quote form POSTs to the legacy
  `/formmailer.php` endpoint with the exact legacy field names (`Name`, `City`,
  `State`, `Email`, `Phone`, `FlyFrom`, `FlyTo`, `DepartDate`, `ReturnDate`,
  `Passengers`, aircraft checkboxes, `OtherInfo`), the `website` honeypot, and
  hidden `recipient` / `redirect` / `subject` fields. Added: one-way/return
  toggle and client-side validation. Success state lives at
  `/quote-confirmation` ("Your request has been forwarded to matching charter
  operators.").
- Destination template (the SEO moat): H1 "[City] Charter Flights ([code])",
  migrated local copy, locally based operators, fly-in fishing / mining / remote
  community use cases, drive-time callouts and FAQs where present, inline quote
  form with per-page subject, nearby-destination links, breadcrumbs.

## SEO preservation (Phase 3)

- **301 map**: `redirects/.htaccess` (Apache) and `public/_redirects` (Netlify),
  ~1,048 one-to-one rules, generated from the inventory. **Zero legacy URLs
  404** — verified programmatically (see below).
- Legacy titles and meta descriptions preserved per page (already-good ones kept
  verbatim; ranking keywords never discarded).
- Canonicals, OpenGraph/Twitter cards, XML sitemap (`@astrojs/sitemap`),
  `robots.txt` (legacy robots blocked 44 retired paths; those pages no longer
  exist so the new robots.txt is clean).
- JSON-LD: site-wide `Organization` + `LocalBusiness` + `WebSite` (carried over
  from the legacy homepage, including the Google site-verification token and
  GA4 tag `G-2E2LY4BMTF`); `Service` + `BreadcrumbList` on every destination;
  `FAQPage` on the 28 pages whose copy supports it.

## Verification (Phase 4)

- `npm run build` → **1,046 static pages**.
- `python3 crawl/verify.py` → **1,047/1,047 redirect targets resolve to built
  pages; 0 dead internal links** in the built site.
- Lighthouse (mobile emulation) on home, Thunder Bay destination, and quote
  pages: **Performance 100 / Accessibility 100 / SEO 100** on all three.

## Launch-readiness audit response (post-migration hardening)

An external launch audit reviewed the Pages preview; its valid findings were
fixed, and several of its P0s were already satisfied in-repo (the auditor could
only see the rendered noindex preview):

- **Already satisfied:** forms post to the real legacy endpoint
  (`formmailer.php` — action attribute stripped by the auditor's tooling);
  `noindex` is injected only by the preview post-processor (production builds
  are index-clean with self-canonicals — the requested env toggle already
  exists as `scripts/make-preview.mjs`); the 301 map ships as 1,048 verified
  rules in both `.htaccess` and `_redirects`; sitemap/robots/JSON-LD all build.
- **Fixed region-data defects:** `group`/`pei` legacy pages were generic
  quote forms misread as destinations → now redirect to `/quote`;
  `winnipeg_red_lake` was a route page → `/flights/winnipeg-to-red-lake`;
  Nakina refiled to Northern Ontario; Burlington and Oshawa (both legacy
  variants) refiled to Southern Ontario; "London Ontario"-style city names
  normalized.
- **Fixed migration artifacts:** wrapped boilerplate paragraphs are now killed
  whole (no more mid-sentence orphans like "their needs. When you…"); legacy
  destination-link lists removed from hub bodies (the templates render
  generated grids); empty headings pruned.
- **SEO/conversion hardening:** per-operator quote pages (100 near-duplicate
  form pages) now canonicalize to `/quote`; the About page was rewritten from
  the legacy fragment wall into prose with puffery softened and unverifiable
  claims TODO-flagged (curated override at `crawl/overrides/pages/about.md`);
  `/empty-legs` gained a dedicated alert-signup form with the distinct subject
  tag "Empty Leg Alert Signup"; `public/llms.txt` added (note: not a Google
  ranking factor — a low-cost agent-readability aid only); the form endpoint is
  centralized in `src/lib/site.ts` (`SITE.formEndpoint`) with documented
  Web3Forms/Formspree/Netlify alternatives and their free-tier limits.
- **Preview hardening:** the Pages preview now also serves
  `robots.txt Disallow: /` and ~1,045 meta-refresh fallback pages at legacy
  `.htm` paths (soft redirects for preview/testing only — production hosts
  serve the real 301s).

## Content flagged thin or duplicate

- 52 pages under ~120 words (`crawl/thin_pages.json`) — mostly operator quote
  pages (form-only by design) and a handful of stub destinations. They migrated
  fine but are candidates for enrichment.
- `marketing_partners.html` is a near-duplicate of `list_your_airline.html`
  (both migrated; consider consolidating).
- 5–6 pages carry small raw-HTML fragments from malformed legacy markup; they
  render correctly but could be hand-tidied.

## Unresolved TODOs (need owner input)

1. **Form endpoint** — the build assumes deployment to the existing Apache host
   where `/formmailer.php` lives. For Netlify, switch the forms to Netlify Forms
   (instructions in `src/components/QuoteForm.astro`). The forms' hidden
   `redirect` now points to `/quote-confirmation`; update `formmailer.php`'s
   allowed-redirect list if it validates that.
2. **Address conflict** — legacy pages show both **401 A Donald St W** (used,
   per instruction) and **1100 Memorial Ave Suite 424** (on `contact_us.htm`).
   Confirm which is current (`src/lib/site.ts`, marked TODO).
3. **Privacy policy** — legacy `privacy_policy.htm` actually contained Sept-Îles
   destination copy, not a policy. The new `/privacy-policy` page contains only
   the privacy commitments stated elsewhere on the legacy site; CFN should
   supply a real policy. (The Sept-Îles copy itself lives on at
   `/canada/quebec/sept-iles` via its own page.)
4. **Imagery** — hero/region SVG placeholders (`public/images/hero/`,
   `public/images/regions/`) should be replaced with real photography (float
   plane on a boreal lake, gravel-strip turboprop). The legacy cover banner
   (dated text collage) is at `src/assets/legacy/CFN_Images/Banners/Cover/` and
   currently serves only as the OG fallback image (`public/images/og-default.jpg`
   — replace alongside). `crawl/image_manifest.json` lists all 2,153 legacy
   images; most destination photos are reusable, banner/collage graphics are not.
5. **Operator lead pricing** — the legacy site states the qualified-lead model
   and listing tiers ($75/yr website-link listing; premium tier) but no lead
   rates; `/operators` directs operators to contact CFN. Confirm current terms.
6. **`kan</p>sas` link** — a corrupted link on the legacy USA page pointed at a
   nonexistent Kansas directory page; nothing to migrate, but fix any upstream
   references if that page is recreated.

## Deploy

### Option A — existing shared hosting (Apache)
1. `npm ci && npm run build`
2. Upload the contents of `dist/` to the web root.
3. Upload `redirects/.htaccess` to the web root (merge with any existing
   `.htaccess`; the generated rules are self-contained and exact-match).
4. **Keep `formmailer.php` in the web root** (do not delete it — all forms post
   to it). Keep the `/CFN Images/` folder if you want legacy image URLs to keep
   resolving (optional; no new page references them).
5. Verify: `curl -I https://charterflightnetwork.com/thunder_bay_charter_flights.htm`
   → `301` → `/canada/northern-ontario/thunder-bay` → `200`.

### Option B — Netlify
1. Connect the repo; build command `npm run build`, publish directory `dist`
   (already in `netlify.toml`). `public/_redirects` ships automatically.
2. Switch forms to Netlify Forms (see TODO #1) or point `action` at a
   still-hosted `formmailer.php` URL on the old server.
3. Point DNS. The 301 map, sitemap and canonicals all reference
   `https://charterflightnetwork.com`, so the domain must be primary.

### Local development
```
npm install
npm run dev        # dev server
npm run build      # static build to dist/
python3 crawl/verify.py   # redirect + link verification (after build)
```

## Rebuilding content from source (repeatable pipeline)

```
python3 crawl/crawler.py            # Phase 0: crawl + inventory (resumable cache)
python3 crawl/extract.py            # Phase 1: copy → markdown, boilerplate strip
python3 crawl/generate_content.py   # Phase 1: classify, slugs, frontmatter, FAQs
python3 crawl/download_images.py    # Phase 1: legacy images (resumable)
python3 crawl/generate_redirects.py # Phase 3: .htaccess + _redirects
npm run build && python3 crawl/verify.py  # Phase 4
```
