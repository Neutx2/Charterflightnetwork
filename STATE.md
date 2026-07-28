# STATE — Charter Flight Network Revenue Loop
Cycle #: 29 (2026-07-28 — operators-page value prop now reflects reality:
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
