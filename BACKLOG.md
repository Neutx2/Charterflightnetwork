# BACKLOG — Revenue-ranked (ICE = Impact×Confidence×Ease, each 1–10; score = product)
# Human-gated items are marked [GATE] and are NOT auto-implemented.
# Items marked [DONE <date>] were shipped during the initial modernization.

## P0 — Launch-readiness / funnel integrity
1. [GATE] Production host cutover: point charterflightnetwork.com at the
   existing Apache host (upload dist/ + redirects/.htaccess, keep
   formmailer.php) OR Cloudflare Pages/Netlify (use public/_redirects; swap
   SITE.formEndpoint to a static form backend).
   ICE: 10×9×5 = 450 | Rev: nothing earns until production serves the new
   site with real 301s. GATE: DNS/host = owner action.
2. [GATE] Merge PR #1 to main (activates the weekly loop cron).
   ICE: 10×9×9 = 810 | GATE: owner review + merge.
3. GSC verification + sitemap submission + service-account read access
   ICE: 8×9×8 = 576 | Rev: no measurement = blind loop; unlocks the stack.
   (Google site-verification meta tag is already carried over site-wide.)
4. Form-submission logging the loop can read (Web3Forms webhook → CSV/KV, or
   a monthly manual count in STATE.md). Endpoint is centralized in
   src/lib/site.ts (SITE.formEndpoint), currently /formmailer.php.
   ICE: 8×8×6 = 384 | Rev: closes the loop on the conversion metric.
   PARTIAL [2026-07-26 cycle 15]: a client-side `generate_lead` GA4 event now
   fires on every validated submit (params: form_subject, source_page), so
   submissions are countable per page in GA4. Still open: server-side
   confirmation that formmailer.php actually delivered the mail — the GA4
   event proves intent, not delivery.
5. [DONE 2026-07-19] Working form funnel with success state (/quote-confirmation),
   honeypot, per-page subjects, client-side validation.

## P1 — Conversion-rate optimization (low-traffic appropriate)
5b. Intermittent layout shift on /quote. The multi-step enhancement hides
    steps 2 and 3 after first paint, so under slow conditions the form
    collapses visibly. Measured CLS 0.067 once, then 0 on three consecutive
    re-runs — a timing race, not a deterministic regression, and below the 0.1
    "good" threshold, but the kind of intermittent shift that still shows up in
    field data.
    Fix is to hide steps 2-3 before paint, which means the enhancement script
    must run during parse rather than as a deferred module. NOT done yet
    because the obvious version introduces a worse failure mode: if the script
    is prevented from running, the contact fields stay hidden and the form
    cannot be completed. Needs a self-healing fallback before it ships.
    ICE: 5×7×5 = 175 | Rev: minor; protects the highest-value page's field CWV.

6. [DONE 2026-07-19 cycle 1] Multi-step quote form (3 steps, progress bar, contact last,
   no-JS fallback verified)
   ICE: 9×7×6 = 378 | Rev: multi-step lead forms convert materially better
   than single-page at the same traffic.
7. [DONE 2026-07-19] Click-to-call on mobile (tel: link in sticky header +
   every quote section). Remaining: call tracking [GATE if paid tool].
   [DONE 2026-07-26 cycle 15] Free call *signal* now exists without a paid
   tool: a `contact_phone` GA4 event on every tel: tap, with source_page.
8. [DONE 2026-07-19] Trust signals near form ("up to 3 competitive quotes",
   "no cost", privacy note). Remaining: response-time promise — [GATE]
   (needs owner confirmation of a real turnaround time).
9. [DONE 2026-07-19] Content-migration artifacts fixed; region data corrected.
   Remaining: consolidate/noindex the 52 thin pages (crawl/thin_pages.json)
   or enrich them with real facts — enrichment items needing new facts → GATE.
10. [DONE 2026-07-19] About-page rewritten (puffery softened, E-E-A-T prose,
    unverifiable claims TODO-flagged).

## P2 — Revenue-model levers
11. [GATE] Operator featured-listing tiers page (pricing owner-set; legacy
    site documents free listing + $75/yr website-link tier + premium tier —
    confirm current rates before publishing).
    ICE: 9×6×5 = 270 | GATE: pricing.
12. [GATE] Empty-leg email alert list: signup form is live with subject tag
    "Empty Leg Alert Signup", but SENDING to the list is gated on
    CASL-compliant double opt-in + sender ID + unsubscribe.
    ICE: 8×6×4 = 192 | GATE: CASL + sending.
13. [DONE 2026-07-19 cycle 3] Evergreen fly-in fishing landing page (facts-only rebuild of the dated 2021 promo page)
    ICE: 8×7×6 = 336 | Rev: peak-intent seasonal search. Facts only; the
    migrated /travel/fly-in-fishing page is the base.
14. Per-province / per-region landing improvements (real facts only)
    ICE: 7×6×5 = 210 | Rev: long-tail organic; uniqueness floor enforced.
15. [DONE 2026-07-19] Empty-legs page with flexible-dates CTA + quote form.
16. [PARTIAL 2026-07-19 cycles 11-13] Industry/seasonal content: mining & exploration, Canadian Arctic, business travel, remote communities, Churchill rebuilt evergreen. Remaining: hunting-season + ice-road blocks (need real facts).
    ICE: 7×6×5 = 210 | Rev: diversifies beyond fishing.
17. [PARTIAL 2026-07-19 cycles 5-8] Internal linking: use-case chips on hubs, aircraft links in destination sidebars, popular routes on home, llms.txt sections. Iterate from GSC data. (baseline shipped:
    nearby-destination sidebars + breadcrumbs + hub grids; iterate from GSC data)
    ICE: 7×7×7 = 343
18. [GATE] Digital-PR / backlink outreach targets for a niche directory
    ICE: 7×5×4 = 140 | GATE: any outreach/spend.
19. [DONE 2026-07-19] Schema.org markup (Organization/LocalBusiness site-wide,
    Service+BreadcrumbList destinations, FAQPage ×28) — facts only.
20. [DONE 2026-07-19 cycle 4] Structured operator data model: scripts/build_operator_data.py -> src/data/operators.json (826 listings, 530 unique operators, 82 featured) parsed from directory pages
    ICE: 7×6×4 = 168 | Rev: foundation for featured listings.

## EXPLICITLY REJECTED
- Display ads / third-party affiliate banners: REJECT. They cheapen a lead-gen
  funnel, distract from the single conversion goal (quote request), add cookie/
  consent overhead, and revenue-per-session is trivial vs a qualified charter
  lead.
