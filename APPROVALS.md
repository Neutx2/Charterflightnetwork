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
