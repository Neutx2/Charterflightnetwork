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

### [2026-07-28] Cycle 23: local operators on every destination page  (PR #1)
- Hypothesis: If each of the 689 destination pages shows the charter
  operators actually based in that city (province fallback, featured first,
  phones inline), then destination-page conversion (phone taps + quote
  submissions) and organic performance improve, because the pages gain real
  local utility and uniqueness where organic traffic lands - the largest
  visible product gap on the site.
- Change shipped: src/lib/operator-data.ts (shared merged dataset used by
  both the finder endpoint and the new module), LocalOperators.astro
  (fully static, no-JS-safe, GA contact_phone inherited, finder deep link
  per province), wired into the city template. Dedup corrected from
  name+base to normalized-name keying after the module surfaced Wilderness
  North Air twice (slash vs comma base strings): 530 -> 480 true unique
  operators, verified zero disjoint-base name collisions (the only 2 were
  punctuation variants). Public counts corrected to 480 (directory hero,
  llms.txt) - accuracy over the bigger number.
- Primary metric: contact_phone and generate_lead events with destination
  source_page values (GA4, post-launch); destination-page impressions (GSC).
- Guardrail metrics: npm run verify 6/6; Thunder Bay page Lighthouse
  100/100/100 CLS 0 with the module rendered.
- Baseline value: destination pages previously showed no operator data.
- READ DATE: two weeks after production launch.
- Result (filled on read date): —
- Decision: —

### [2026-07-28] Cycle 21: godmode sweep — deep links, unified gate, drafts  (PR #1)
- Hypothesis: (a) province hubs deep-linking into a pre-filtered operator
  finder shortens the path from regional intent to operator contact;
  (b) approval-ready drafts convert owner sign-off into same-day ships,
  compressing the revenue-critical approval latency.
- Change shipped: finder URL params (?q,prov,type) + #find-an-operator anchor;
  all 15 province-hub directory links now land pre-filtered; unified
  verification gate (npm run verify, scripts/verify_all.mjs) shared by
  humans, the Sunday Routine and the Actions workflow; quotability round 2 on
  /usa /bahamas /caribbean via pipeline-safe overrides; legacy typo fixed at
  source; thin-page item closed with build evidence (all 52 verified);
  drafts/what-does-a-charter-cost.md + drafts/how-to-choose-a-charter-operator.md
  written, sourced, [VERIFY]-marked and linked from APPROVALS (not built,
  not published).
- Primary metric: directory-finder engagement from hub referrals
  (contact_phone with source_page=/directory after arriving via ?prov= links)
  once GA4 has traffic; approval-to-ship latency for items 22/23.
- Guardrail metrics: npm run verify 6/6 suites (finder suite now 7 checks,
  incl. URL-param prefiltering); /canada/manitoba Lighthouse 100/100/100
  CLS 0; drafts confirmed absent from dist.
- Baseline value: none (features new).
- READ DATE: two weeks after production launch.
- Result (filled on read date): —
- Decision: —

### [2026-07-28] Cycle 20: AI-quotability pass, first round  (PR #1)
- Hypothesis: If key pages open with self-contained, entity-named answers and
  llms.txt carries a stable-facts section, then AI assistants and answer
  engines cite Charter Flight Network for charter-in-Canada questions,
  because extraction favours passages that stand alone with the entity named
  — a channel none of the niche competitors optimize for.
- Change shipped: hero paragraphs on /, /quote, /aircraft, /empty-legs
  rewritten as quotable answers using only on-site facts (empty-legs now
  opens with the definition of an empty leg; aircraft names all six classes;
  quote states the full process; home names the entity). llms.txt: "Stable
  facts (citable)" section + finder-aware directory line. robots.txt already
  allows all crawlers — no change needed.
- Primary metric: AI/LLM referral sessions and branded-query impressions
  (GSC), once measurement exists; qualitatively, whether assistants cite the
  site for "charter a float plane in northern Ontario"-class questions.
- Guardrail metrics: all copy statements verified against existing site
  facts (no new claims); full suite green — redirects 1047/1047, dead links
  0, disclaimer 1044/1044, nav 13/13, GA 4/4, quote fallback 5/5, finder
  6/6, home Lighthouse 100/100/100 CLS 0.
- Baseline value: no AI-referral baseline exists pre-launch.
- READ DATE: four weeks after production launch (AI citation shifts slowly).
- Result (filled on read date): —
- Decision: —

### [2026-07-28] Cycle 19: operator finder on /directory  (PR #1)
- Hypothesis: If the 530-operator directory becomes searchable and filterable
  (name/base search, province, aircraft type) instead of flat link lists,
  then directory engagement (phone taps via contact_phone, quote submissions
  from directory sessions) rises, because the dataset becomes a product no
  competitor in the niche offers — the market review found brokers competing
  on estimators and lodges on content, with nobody serving "find me a float
  plane operator near X" directly.
- Change shipped: OperatorFinder component on /directory; static
  /data/operator-finder.json endpoint (built from src/data/operators.json,
  duplicates merged by unioning fields — naive dedup lost 56 phone numbers;
  merged coverage is 223/530 operators with phones, the rest genuinely have
  none on the source pages). Lazy fetch keeps the page light; no-JS visitors
  see the unchanged province lists; tel links inherit the delegated
  contact_phone GA event. Also fixed two a11y findings the new page surfaced
  (badge contrast; logo link accessible-name mismatch, site-wide).
- Primary metric: contact_phone events with source_page=/directory, and
  generate_lead from directory-originated sessions (GA4, post-launch).
- Guardrail metrics: /directory Lighthouse 100/100/100 + CLS 0 after fixes;
  scripts/verify_operator_finder.mjs 6/6; full suite green (redirects
  1047/1047, dead links 0, disclaimer 1044/1044, nav 13/13, GA 4/4,
  quote fallback 5/5).
- Baseline value: no baseline (feature is new); directory sessions currently
  unmeasured until launch.
- READ DATE: two weeks after production launch.
- Result (filled on read date): —
- Decision: —

### [2026-07-28] Cycle 18: /quote pre-paint step collapse + self-healing fallback  (PR #1)
- Hypothesis: If the multi-step enhancement's step-1 state is applied before
  first paint instead of after it, the intermittent CLS on /quote (0.067
  observed once in lab) disappears from field data, protecting the
  highest-value page's Core Web Vitals as real traffic arrives.
- Change shipped: inline js-ms script inside the form applies CSS reproducing
  the enhancement's step-1 state pre-paint; the enhancement module hands over
  via data-ms-ready and drops the class; a 3s watchdog restores the full
  single-page form if the module never runs. This is BACKLOG 5b, previously
  parked because the naive version traps the contact fields hidden when the
  script fails — the watchdog is the missing piece that made it safe.
- Primary metric: lab CLS on /quote (0 across 4 consecutive runs, was
  intermittently 0.067); field CLS in CrUX/GA4 once launched.
- Guardrail metrics: form must remain completable in ALL degradation modes —
  scripts/verify_quote_fallback.mjs asserts takeover, blocked-module watchdog
  restore, and no-JS; GA 4/4 (drives the real step flow); nav 13/13;
  1,047/1,047 redirects; 0 dead links; disclaimer 1,044/1,044; perf 100.
- Baseline value: CLS 0.067 (one lab observation, then 0×3 — a timing race).
- READ DATE: two weeks after production launch (needs field data).
- Result (filled on read date): —
- Decision: —

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

### [2026-07-19] Cycles 9-10: operator-data surfacing
- Cycle 9 Province hubs show derived operator counts (from operators.json)
  with deep links into that province's directory pages + a quote-form CTA
  (metric: hub -> directory/quote click-through).
- Cycle 10 /directory index grouped into 13 province sections instead of a
  flat 143-link list (metric: directory navigation depth, operator-page views
  — the surface the featured-listing product sells on).
- Guardrails: build clean, 1,047/1,047 redirects, 0 dead links (one bad
  Alberta link caught by the crawl check and fixed in-cycle).

### [2026-07-19] Cycles 11-14: stale-content and title-integrity sweep
- Cycles 11-13 Rebuilt five Covid-era membership-promo pages as evergreen
  industry landing pages using only facts already on the site:
  /travel/mining-exploration, /travel/canadian-arctic, /travel/business-travel,
  /travel/ontario-remote-communities, /travel/churchill-polar-bears. These
  were the targets of the province-hub use-case chips added in cycle 5, so the
  hub link graph now points at pages that describe the actual service.
  Also retitled 3 travel pages that shared the generic legacy title
  "Charter Flight Network/Charter Flights Canada".
- Cycle 14 Title integrity: 40 operator quote pages carried a copy-pasted
  legacy <title> naming a DIFFERENT operator (e.g. /quote/wasaya titled
  "…From Lakehead Airways"); titles/descriptions now derive from the operator
  name, matching the visible H1. Six Canadian Air Charter Directory pages
  mis-titled "Charter Flights To Pickle Lake Ontario" retitled by their real
  role. Duplicate titles: 21 groups / 78 pages -> 15 groups / 30 pages.
- Metrics to watch: CTR on retitled pages; impressions for industry-intent
  queries (mining charter, arctic charter, remote community charter).
- Guardrails: build clean, 1,047/1,047 redirects, 0 dead links, disclaimer
  1,043/1,043 after every cycle.
- READ DATE: two weeks after production launch + metrics activation.

### [2026-07-26] Cycle 15: GA4 conversion events (measurement, not layout)
- Change shipped: the funnel is now measurable. `generate_lead` fires on a
  quote form submit that passes validation (params: form_subject, source_page);
  `contact_phone` fires on any tel: link tap (param: source_page), via one
  delegated listener in BaseLayout. Both push into the existing GA4 tag
  (G-2E2LY4BMTF) already carried over from the legacy site. No personal data is
  sent — only which form and which page.
- Why: every prior cycle optimised on judgement because there was no
  conversion signal at all. Phone calls in particular are a real close path for
  this business and were previously invisible.
- Primary metric: quote submissions per session, and phone taps per session,
  split by source_page — so the next cycles can rank pages by conversion
  instead of by traffic guesswork.
- Verification: scripts/verify_ga_events.mjs drives a real browser and asserts
  against window.dataLayer (the page defines its own gtag(), so a stubbed
  window.gtag is overwritten and would give a false negative). 4/4 checks pass:
  phone tap fires, an incomplete submit does NOT fire generate_lead, a complete
  submit does, and the params are populated.
- Guardrails: build clean, 1,047/1,047 redirects, 0 dead links.
- READ DATE: two weeks after production launch (GA4 needs live traffic).

## BASELINE (pre-loop)
### [2026-07-19] Full site modernization (PR #1)
- Change shipped: 1,046-page migration to Astro/Tailwind, 301 map, quote
  funnel preserved, Lighthouse 100/100/100 baseline, audit hardening.
- Primary metric: none (baseline). All future experiments compare against
  the first post-launch KPI snapshot in STATE.md.
