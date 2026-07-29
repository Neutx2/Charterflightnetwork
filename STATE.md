# STATE — Charter Flight Network Revenue Loop
Cycle #: 54 (2026-07-29 — travel/route coherence: all 20+ travel and
  route heroes gain the Get Free Quotes + tap-to-call CTA row that city
  and hub heroes carry (routes anchor to the on-page form, travel pages
  to /quote; operator-facing subpages correctly excluded); fixed
  'yourself?Search Ontario operators' glue on all 12 route pages (and a
  'SearchOntario' variant Astro introduced when text precedes an
  {expression} on a new line — single template literal now); gate's
  glued-text regex extended to catch punctuation glued to anchors.
  Prior — cycle 53: the glued-text scan is now a permanent gate
  check: verify_all gains a 10th item scanning every dist page for a
  letter glued to <a …> or </a> (the Astro whitespace-collapse pattern);
  negative-tested with a planted regression (correctly FAILs) and the
  real dist scans clean. Gate is 10 checks/suites. Prior — cycle 52:
  site-wide glued-text sweep: scanned every built
  page for the Astro whitespace-collapse bug cycle 51 exposed (word glued
  to a link, e.g. 'theCanadian') — found and fixed 10 instances across 8
  source files affecting ~106 pages: quote ('…-1955and we'll'), all 99
  operator quote pages ('…request</a>reaches'), privacy ('orphil@…',
  '…comwith any questions'), contact, operators, empty-legs, directory
  (2), and a sept-iles markdown typo ('as[Havre-Saint-Pierre]'). Dist
  re-scan now finds zero glued anchors. Prior — cycle 51: coherence on
  province hubs: tap-to-call button
  added to hub heroes (city pages had it, hubs didn't — phone taps are an
  instrumented revenue path); the operator trust band ('N charter
  operators … get up to 3 competitive quotes') moved above the 50+ item
  destination grid where it was invisible; and fixed a whitespace-collapse
  bug the move exposed — Astro ate the line-break space around the band's
  anchors ('theCanadian', 'andget'), now explicit inline spacing. Prior —
  cycle 50: coherence: city pages now lead with the
  actionable operator cards (phones, featured badges, silhouettes, the
  'search all / get 3 quotes' line) directly under the hero beside the
  quote-CTA sidebar; the legacy prose, FAQ and link lists follow as
  supporting detail. Cards previously sat at the very bottom after all
  prose. Fallback cities (no local operators) verified fine. Prior —
  cycle 49: NEW OWNER DIRECTIVE folded into the loop: 'clean
  up and make all the pages as coherent and organised as possible …
  intuitive and easy to read … easy funnel to convert clicks into
  revenue.' First coherence fix, found by full-page audit: destination
  pages carried page-tall single-column lists of bare links (35+ items on
  Thunder Bay). Long lone-link lists (8+ items, incl. loose-markdown
  <li><p><a> shape) now flow into 2/3 responsive columns via :has() — no
  markup changes, prose bullets unaffected, single column kept on old
  browsers; loose-list <p> margin zeroed so list gaps stop doubling.
  Applies across hundreds of destination/hub pages. Prior — cycle 48:
  graphics/UI: finder result cards get the same
  aircraft silhouettes as the server-rendered operator cards — AircraftIcon
  instances server-rendered into a <template> and cloned by the client
  script (no duplicated path data), wheels/skis share the fixed-wing
  profile, deduped per operator. Every operator card surface now reads at
  a glance. Prior — cycle 47: graphics/UI: the brand aircraft now rides the
  quote-form progress bar — orange glyph pinned to the bar tip, left
  position synced to the same step percentage as the fill, smooth
  transition between steps; verified at steps 1 and 2 by screenshot and
  computed style (66.6667% both). Prior — cycle 46: graphics/UI:
  aircraft silhouettes on all
  operator cards (LocalOperators on 689 destination pages +
  FacetOperators on travel/aircraft pages) via new facetIconTypes()
  helper — wheels/skis share the fixed-wing profile so no duplicate
  glyphs; also found and fixed a bullet regression: `.copy ul`
  out-ranked the cards' list-none on specificity, so destination-page
  cards showed stray discs — rule is now `.copy ul:not(.list-none)`,
  prose bullets verified intact. Prior — cycle 45: graphics/UI push
  begins per owner ('work on
  graphics and ui for a while'): new HorizonRule brand-motif divider —
  the logotype's tapered teal horizon + climbing orange aircraft as a
  reusable ornament (tone teal/light, aria-hidden, em-scaled). Shipped as
  a crest atop the dark footer site-wide and as the section divider before
  the home Popular-routes band. Queue for next graphics cycles:
  aircraft-type mini-icons on operator cards, plane riding the quote-form
  progress bar, hero/region scene art, 404 artwork. Prior — cycles 43-44:
  honest no-ops + privacy APPROVALS note (policy must disclose GA4 +
  formmailer); deploy green. Prior — cycle 42: directory hero count made
  exact ('480' not
  '480+' - the dedup made the number precise, so the plus was inflation);
  PR #1 deploy confirmed green on latest push. Prior — cycle 41: two
  playbook guardrails automated into the gate:
  indexation health (production dist must be index-clean; a stray noindex
  would deindex the site at launch) and gated-draft containment (approval-
  pending pages must never reach dist). Gate now 9 checks/suites. Prior —
  cycle 40: finder 0-match dead end fixed: empty state with
  a Clear-filters button (delegated, refocuses search) and a quote-form
  escape hatch; finder suite up to 9 checks. PR #1 deploy check confirmed
  green on the latest push. Prior — cycle 39: a11y on the money paths:
  quote form announces
  step changes to screen readers (sr-only aria-live 'Step N of 3: name');
  finder anchor target focusable (tabindex=-1) so deep links land keyboard
  users correctly. Prior — cycle 38: operator application form
  instrumented: sign_up
  (method=operator_listing) GA4 event + 'Application received' confirmation
  via ?from=operator - the supply side of the funnel was the last
  un-instrumented form. Every form on the site now emits a distinct signal.
  Form-signals suite up to 7 checks. Prior — cycle 37: the directory
  finally enters the header nav:
  'Charter Directory - Search 480 operators' in the Destinations dropdown
  and the mobile Browse group; it was previously unreachable from primary
  navigation. Nav suite updated for the fifth dropdown item and the taller
  panel. Prior — cycle 36: 390px mobile pass over newest surfaces: clean,
  no overflow, no fix forced; banked the wake into a permanent
  verify_form_signals.mjs suite (5 checks: confirmation variants + sign_up
  + contact_message) - the gate is now 7 suites. Prior — cycle 35:
  /aircraft type cards gain their silhouettes
  (jet, turboprop, float, helicopter), matching the quote form. Prior —
  cycle 34: quote form aircraft step gains silhouette icons
  (AircraftIcon per option; piston/wheels share the turboprop profile);
  home popular-routes audited complete: all 11 unique routes linked, dupe
  page correctly excluded. Prior — cycle 33: contact form gets its GA4 signal
  (contact_message w/ source_page) and its own confirmation copy via
  ?from=contact ('Message received'), fixing the same two gaps the alert
  signup had. Prior — cycle 32: nationwide operator modules on the aircraft
  subpages: turboprops->wheel planes, float-planes->floats,
  helicopters->helicopters, 6 cards each; jets honestly carries none (no
  jet facet in the directory data). Prior — cycle 31: empty-legs signup
  UX: GA4 sign_up event
  (method=empty_leg_alerts, source_page) so list growth is measurable;
  confirmation page adapts its heading for ?from=alerts so signups no
  longer read a quote-request message. No sending - CASL gate untouched.
  Prior — cycle 30: 404 page gains an operator search box (old
  bookmarks are often operator links; plain GET into the finder). Prior —
  cycle 29: operators-page value prop now reflects reality:
  a listing appears in the searchable finder and on destination pages with
  fleet + tap-to-call, featured first everywhere; no pricing touched.
  Prior — cycle 28: empty-legs page teaches searching operators
  directly (finder cross-link as a 4th 'how to catch one' tip); footer
  gains a Find an Operator link site-wide. Queue from the market-review
  build-out is now complete. Prior — cycle 27: finn-loop 5-min cadence:
  all 12 flights route
  pages link into the finder pre-filtered to the route's Canadian province
  (Winnipeg-Red Lake -> Manitoba etc., generic fallback); travel openings
  audited and found already strong (honest skip). Prior — cycle 26: mobile
  review at 390px of all new modules: no
  horizontal overflow anywhere; fixed inherited list bullets on operator
  cards (.copy ul markers; not-prose was a no-op since the site doesn't
  use Tailwind Typography). 5-minute loop cadence per owner. Prior —
  cycle 25: operator modules on ALL use-case travel pages:
  mining/exploration (helicopters), Ontario remote communities (wheels),
  Churchill (Manitoba), joining fly-in fishing and Arctic. Prior — cycle
  24: finder as connective tissue: home-hero operator
  search box, aircraft-card deep links by type, float/northern operator
  modules on fly-in fishing and Arctic pages. Prior — cycle 23: LOCAL
  OPERATORS on all 689 destination pages:
  city-matched operator cards with phones, province fallback, finder deep
  links; dedup corrected to 480 true unique operators and public counts
  fixed. Prior same day — cycle 22: template Lighthouse sweep: 7 previously
  unaudited templates measured (city, travel, directory subpage, route,
  operators, about, contact) — all 100 perf / CLS 0; one finding fixed
  (about page heading-order: strapline was an h3 under the h1, now bold
  text — via content + override). Continuous godmode loop active. Cycles
  18-21 same day; all ungated backlog shipped, board waits on the 9
  APPROVALS items.)
Last run (UTC): 2026-07-28
Scheduled loop: ACTIVE — Claude Routine `trig_017fT4PmoririEtcJCUWgf5J`
  fires Sundays 08:00 UTC (first: 2026-08-02) into a fresh cloud session on
  this repo; runs one cycle in metrics-degraded mode (no GSC/PSI secrets yet),
  ships to this branch only, refreshes the owner status board.
  The GitHub Actions path (.github/workflows/revenue-loop.yml) stays INACTIVE
  until the owner adds the four secrets and the PR merges to main (cron only
  fires from the default branch); once live, disable the Routine to avoid
  double cycles.
Branch under optimization: claude/cfn-modernization-okp1pe (PR #1)
Production host: not launched (staging = GitHub Pages preview, noindex)
Indexation: staging=noindex (injected by scripts/make-preview.mjs);
            production build = index-clean, not yet deployed


## OWNER STATUS PAGE (refresh every cycle)
Stable URL: https://claude.ai/code/artifact/204ea267-296b-4fa7-a1e8-357e1497cd0e
After each cycle's verification passes and the commit lands, run:
  python3 scripts/build_status_page.py
then re-publish the SAME file path with the Artifact tool
(scratchpad/cfn-status.html) so the URL stays stable for the owner.
It reads git log (loop(cycle-N) commits), STATE.md, APPROVALS.md and dist/.

## GUARDRAIL FLOORS (do not regress)
Lighthouse (mobile) — Performance ≥ 90 | SEO ≥ 95 | Accessibility ≥ 95
  (baseline 2026-07-19: 100/100/100 on home, Thunder Bay, quote, Bahamas
   destination, and directory templates)
Redirect coverage: 1,047/1,047 legacy URLs resolve (crawl/verify.py) — REQUIRED
Dead internal links: 0 — REQUIRED
Disclaimer present on 100% of pages: REQUIRED
Max net-new content pages per cycle: 2
Uniqueness floor per page: REQUIRED

## KPI SNAPSHOT (updated each cycle)
Window: — (no metrics until GSC/PSI secrets configured and site launched)
Impressions:       —
Clicks:            —
CTR:               —
Avg position:      —
Sessions:          —
Phone taps:        — (GA4 `contact_phone` wired cycle 15)
Quote submissions: — (GA4 `generate_lead` wired cycle 15; needs live traffic)
Qualified leads:   — (owner-reported)
Revenue:           — (owner-reported)

## TOP PAGES / QUERIES TO WATCH
- / — brand + "charter flight network"
- /canada/northern-ontario/thunder-bay — "thunder bay charter flights" (YQT)
- /quote — conversion page
- /canada/* province hubs — "<province> charter flights"

## OPEN NOTES
- Logotype FINAL, decided by owner 2026-07-27 through three refinement
  rounds (decision boards in scripts/render_*.py, options 1-44): option 25 —
  tapered teal horizon (lens that fades at the ends) with the orange
  aircraft, at 2/3 the width of "Network", climbing out from behind the end
  of the word. Shipped as `teal-taper-climbout` in src/lib/wordmark-arcs.ts
  ("thats perfect" — owner); square icon (favicon/OG) unchanged.
- 52 thin pages listed in crawl/thin_pages.json (mostly operator quote forms,
  which now canonicalize to /quote; the rest are enrichment candidates).
- Content edits should go through crawl/overrides/ so pipeline re-runs don't
  clobber them.
- TODO(owner) items live in MIGRATION_REPORT.md and APPROVALS.md.
