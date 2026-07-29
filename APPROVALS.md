# APPROVALS QUEUE — owner sign-off required (review during home rotation)
# The loop appends here; it NEVER acts on these without your explicit approval.

## TEMPLATE
### [YYYY-MM-DD] <item>
- Category: <PRICING | LEGAL | EMAIL/CASL | MONEY SPEND | FACT VERIFICATION | HOST/DNS>
- What the loop wants to do: <description>
- Why it matters (revenue): <rationale>
- Decision needed from owner: <the exact yes/no or value to provide>
- Blocked backlog item(s): <#>
- Owner decision: <___>   Date: <___>

## PRE-SEEDED ITEMS

### [seed] Confirm operator relationships & per-lead pricing
- Category: PRICING + FACT VERIFICATION
- What: Provide the list of real charter operators in the network, their bases,
  aircraft types, and the agreed price-per-qualified-lead and featured-listing
  fee. The legacy site documents the qualified-lead model and listing tiers
  (free basic; $75+tax/12mo website-link tier; premium tier) but no lead rates.
  No published per-lead market rate exists for charter lead-gen — pricing must
  come from direct operator agreement. The loop must never invent it.
- Why: Everything downstream (featured listings, lead pricing, revenue math)
  depends on these real facts. This is the single highest-leverage action the
  loop cannot do.
- Decision needed: operator list + pricing.
- Blocked backlog item(s): 11, 20

### [seed] Approve production host + DNS cutover
- Category: HOST/DNS
- What: Choose the production host and point charterflightnetwork.com at it.
  Option A: existing Apache shared host (upload dist/ + redirects/.htaccess;
  formmailer.php keeps working unchanged). Option B: Cloudflare Pages/Netlify
  (public/_redirects serves the 301s; swap SITE.formEndpoint to a static form
  backend first). Keep github.io strictly as noindex staging either way.
- Why: real 301s preserve legacy .htm ranking equity; nothing earns until
  production is live and indexable.
- Decision needed: host choice + DNS change window.
- Blocked backlog item(s): 1, 2, 3

### [seed] Confirm business address
- Category: FACT VERIFICATION
- What: Legacy pages show BOTH "401 A Donald St West, P7E 5Y1" (used site-wide)
  and an older "1100 Memorial Avenue, Suite 424, P7B 4A3". The Donald St W +
  P7E combination also looks internally inconsistent.
- Why: NAP consistency drives local SEO and trust; it's in the site footer,
  contact page, and LocalBusiness JSON-LD.
- Decision needed: the one correct street + postal code.

### [seed] Approve empty-leg email alert sending (CASL)
- Category: EMAIL/CASL
- What: The signup form is live (subject tag "Empty Leg Alert Signup") but it
  only emails submissions to CFN. Before SENDING alerts to the list: double
  opt-in, unchecked consent, sender identification (name + mailing address +
  contact), working unsubscribe (honored within 10 business days, functional
  ≥60 days), consent records retained 3 years. Penalties reach $1M/individual,
  $10M/business per violation. Purchased lists are a violation.
- Why: re-engageable audience for empty legs / seasonal offers.
- Decision needed: approve the sending process + confirm sender identity/address.
- Blocked backlog item(s): 12

### [seed] Supply real photography
- Category: FACT VERIFICATION (visual)
- What: Replace the SVG placeholder hero/region images (public/images/) with
  real northern-aviation photography (float plane on a boreal lake, gravel-strip
  turboprop). crawl/image_manifest.json catalogues 1,979 legacy photos that may
  be reusable.
- Why: trust/conversion; placeholders are flagged in MIGRATION_REPORT.md.
- Decision needed: provide or approve photo selection.

### [seed] Privacy policy text
- Category: LEGAL
- What: The legacy privacy_policy.htm contained destination copy, not a policy.
  The current /privacy-policy page carries only the privacy commitments stated
  elsewhere on the legacy site. Supply a real policy (PIPEDA-appropriate).
- Why: legal hygiene for a lead-gen site collecting contact details.
- Decision needed: approved policy text.
- NOTE (2026-07-28, cycle 43): the supplied policy must also disclose
  Google Analytics 4 usage (the site fires generate_lead, contact_phone,
  sign_up and contact_message events; no personal data is sent in event
  parameters, but GA4 sets cookies) and the formmailer email handling.


### [2026-07-28] "What does a charter cost" guide page
- Category: PRICING
- What the loop wants to do: publish an honest cost-education page — market
  hourly ranges attributed to third-party sources (BLADE, Stratos, Jettly
  publish such guides), what drives price (distance, aircraft class,
  floats/wheels, season, positioning), and why a quote beats a calculator for
  northern trips. No CFN prices, no invented numbers.
- Why it matters (revenue): price fear is the top reason visitors bounce from
  quote forms; every serious competitor anchors price. This is the
  highest-ICE unshipped item on the board (441).
- Decision needed from owner: approve publishing attributed third-party
  ranges (yes/no), and optionally supply any real anchor the network can
  stand behind.
- Blocked backlog item(s): 22
- DRAFT READY: drafts/what-does-a-charter-cost.md — full page copy with
  attributed sources; approving it (and each figure) makes this a same-day ship.
- Owner decision: <___>   Date: <___>

### [2026-07-28] Safety & vetting education page facts
- Category: FACT VERIFICATION
- What the loop wants to do: publish "how to choose a charter operator" —
  what Transport Canada AOC certification means, what to ask an operator
  (insurance, pilot experience, aircraft maintenance), how the quote network
  fits in. Facts are external to the site, so each needs a verifiable
  primary source (Transport Canada / CARs) before publication.
- Why it matters (revenue): converts safety anxiety into quote requests;
  education content nobody in the niche does; strong E-E-A-T signal.
- Decision needed from owner: approve the approach; flag anything about
  operator vetting the network actually does (or does not do) so the page
  never overstates CFN's role.
- Blocked backlog item(s): 23
- DRAFT READY: drafts/how-to-choose-a-charter-operator.md — full page copy;
  every external fact carries a [VERIFY] marker with its primary source, and
  the "where CFN fits" section needs your word-for-word confirmation.
- Owner decision: <___>   Date: <___>

### [2026-07-28] Route-page distance/flight-time data source
- Category: FACT VERIFICATION
- What the loop wants to do: build a handful of high-intent route pages
  (e.g. Thunder Bay → named northern destinations) with real distances and
  flight-time context computed from published airport coordinates.
- Why it matters (revenue): route-level utility content captures long-tail
  search the big brokers ignore; the lodges rank on it today.
- Decision needed from owner: approve using published airport data (e.g.
  Canada Flight Supplement / Nav Canada data) as a source, and name the
  first 3-5 routes worth building.
- Blocked backlog item(s): 24
- Owner decision: <___>   Date: <___>
