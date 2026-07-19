# EXPERIMENTS LOG (append-only)

## TEMPLATE
### [YYYY-MM-DD] <experiment name>  (PR #<n>)
- Hypothesis: If we <change>, then <KPI> will <direction> because <reason>.
- Change shipped: <what>
- Primary metric: <e.g., quote submission rate>
- Guardrail metrics (must not regress): <Lighthouse / impressions / disclaimer>
- Baseline value: <n>
- READ DATE: <YYYY-MM-DD> (≥2 weeks out; accounts for GSC 2-3 day lag +
  multi-week signal at low traffic)
- Result (filled on read date): <win/flat/loss + numbers>
- Decision: <keep / revert / iterate>

### [2026-07-19] Multi-step quote form  (PR #1, cycle 1)
- Hypothesis: If the quote form becomes a 3-step flow (trip → aircraft →
  contact, contact fields last), then quote-submission rate will increase,
  because multi-step lead forms reduce perceived effort and front-load the
  low-friction fields.
- Change shipped: QuoteForm.astro renders 3 steps with progress bar,
  per-step validation, Back/Continue; degrades to a plain single-page form
  without JS (verified both modes with Playwright).
- Primary metric: quote submissions / sessions (needs GSC + form logging).
- Guardrail metrics: Lighthouse (still 100/100/100 on /quote), disclaimer,
  native no-JS submit path.
- Baseline value: unknown until measurement stack is live.
- READ DATE: two weeks after production launch + metrics activation.
- Result: —
- Decision: —

### [2026-07-19] Internal-links + crawl hygiene batch  (PR #1, cycle 1)
- Changes shipped: custom 404 page with funnel links; "Popular charter
  routes" section on home linking the 11 migrated route pages; sitemap now
  excludes canonicalized-away operator quote pages + utility pages
  (1,044 built pages → 943 sitemap URLs); skip-to-content link;
  prefers-reduced-motion support; security + cache headers in the generated
  .htaccess (mirrors netlify.toml).
- Primary metric: crawl efficiency / indexation of canonical pages (GSC
  coverage report), 404 exit rate.
- Guardrail metrics: 1,047/1,047 redirects resolve, 0 dead links, Lighthouse
  100s — all confirmed post-change.
- READ DATE: two weeks after production launch.
- Result: —
- Decision: —

### [2026-07-19] 8-cycle optimization session  (PR #1, cycles 1-8)
- Cycle 1 SourcePage hidden field on all forms — leads arrive tagged with the
  originating page (metric: lead routing accuracy / operator acceptance).
- Cycle 2 Fly-to prefilled with the page city on all 733 destination forms
  (metric: destination-page form completion rate).
- Cycle 3 Evergreen fly-in fishing landing page replacing dated 2021 promo
  (metric: impressions/clicks for fly-in fishing queries; READ +2wk post-launch).
- Cycle 4 Operator data model: 826 listings / 530 operators parsed to
  src/data/operators.json; /directory shows derived 530+ operator count
  (foundation metric: none — enables featured-listing product).
- Cycle 5 Use-case chips on province hubs + aircraft links in destination
  sidebars (metric: internal CTR to /travel/* and /aircraft/*).
- Cycle 6 Visible FAQ + FAQPage JSON-LD on /quote (metric: /quote rich
  results + conversion rate).
- Cycles 7-8 Service/BreadcrumbList JSON-LD on region hubs, aircraft pages,
  province hubs; llms.txt use-case sections (metric: coverage in GSC
  enhancements report).
- Guardrails after every cycle: build clean, 1,047/1,047 redirects, 0 dead
  links, disclaimer 1,043/1,043, Lighthouse 100/100/100 spot-checks.
- READ DATE: two weeks after production launch + metrics activation.

## BASELINE (pre-loop)
### [2026-07-19] Full site modernization (PR #1)
- Change shipped: 1,046-page migration to Astro/Tailwind, 301 map, quote
  funnel preserved, Lighthouse 100/100/100 baseline, audit hardening.
- Primary metric: none (baseline). All future experiments compare against
  the first post-launch KPI snapshot in STATE.md.
