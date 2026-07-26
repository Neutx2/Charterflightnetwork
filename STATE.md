# STATE — Charter Flight Network Revenue Loop
Cycle #: 15 (session 2026-07-26)
Last run (UTC): 2026-07-26 (manual; scheduled loop still pending secrets)
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
- 52 thin pages listed in crawl/thin_pages.json (mostly operator quote forms,
  which now canonicalize to /quote; the rest are enrichment candidates).
- Content edits should go through crawl/overrides/ so pipeline re-runs don't
  clobber them.
- TODO(owner) items live in MIGRATION_REPORT.md and APPROVALS.md.
