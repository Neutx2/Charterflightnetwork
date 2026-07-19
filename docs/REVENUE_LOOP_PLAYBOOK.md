# Autonomous Revenue-Optimization Loop for Charter Flight Network

## TL;DR
- Run a **weekly** (not nightly) Claude Code "build-measure-refine" loop via **GitHub Actions cron** using your **Pro/Max subscription OAuth token** (`CLAUDE_CODE_OAUTH_TOKEN`), which keeps per-cycle cost at ~$0 above your existing subscription; the loop ingests free metrics (Search Console API + Cloudflare Web Analytics + PageSpeed API), re-scores an ICE backlog, ships the top 1–3 items as a **PR only** (never to main), and queues anything touching money/pricing/legal/email into an approvals file for your home-rotation sign-off.
- The single biggest revenue lever is **not** the loop — it is grandpa confirming real operator relationships and per-lead pricing, because charter lead-gen has **no published per-lead rate** (the industry runs on subscriptions/commissions, e.g., Avinode marketplace access at competitor-cited "up to $2,119 per month") [SkyAccess](https://skyaccess.com/blog/avinode-alternative-for-operators) and the business only monetizes when real operators agree to pay for qualified leads plus featured listings.
- Guardrails (Lighthouse floor, indexation health, disclaimer presence, uniqueness floor to avoid Google scaled-content-abuse penalties, CASL/PIPEDA gates, PR-only shipping) are what prevent the four classic autonomous-loop failure modes: drift, thin-content spam, breaking the funnel, and burning usage.

---

# PART 1 — THE LOOP ARCHITECTURE

## One cycle (text diagram)

```
        ┌─────────────────────────────────────────────────────────────┐
        │  WEEKLY TRIGGER (GitHub Actions cron, Sun 08:00 UTC)          │
        └─────────────────────────────────────────────────────────────┘
                                   │
   1. INGEST  ──►  Pull metrics into METRICS/ :
                   • GSC API (queries, pages, impressions, clicks, position)
                   • Cloudflare Web Analytics (sessions, top pages)
                   • Web3Forms submissions count (from logged webhook / CSV)
                   • PageSpeed Insights API (perf/SEO scores, key pages)
                   • Uptime check result
                                   │
   2. ANALYZE ──►  Compute KPI-tree deltas vs last cycle (STATE.md):
                   impressions→clicks→sessions→quote submits→qualified
                   leads→revenue. Flag regressions.
                                   │
   3. PRIORITIZE ─► Re-score BACKLOG.md with ICE (+ projected $ impact).
                   Sort. Select top 1–3 items that fit guardrails and
                   are NOT human-gated.
                                   │
   4. IMPLEMENT ─► Make minimal, scoped code/content changes on a new
                   branch. Never invent facts/operators/airports.
                                   │
   5. VERIFY  ──►  Build (astro build) + link crawl + Lighthouse +
                   disclaimer/canonical/noindex checks + uniqueness
                   check. HARD STOP on any failure → failure report.
                                   │
   6. SHIP    ──►  Open PR (labelled) with structured changelog.
                   NEVER push to main. Concurrency guard prevents
                   overlapping runs.
                                   │
   7. LOG     ──►  Append EXPERIMENTS.md (hypothesis/metric/read-date),
                   update STATE.md snapshot, move done items, queue
                   human-gated items into APPROVALS.md.
                                   │
        ┌─────────────────────────────────────────────────────────────┐
        │  Owner reviews PR + APPROVALS.md during home rotation        │
        └─────────────────────────────────────────────────────────────┘
```

## Recommended cadence: WEEKLY (with a monthly "deep" cycle)

Nightly is wrong for this site. Per Google's Search Console Help ("About Search Console data"), there is a lag between when numbers are calculated and visible — "Normally, however, collected data should be available in 2-3 days" [Google Support](https://support.google.com/webmasters/answer/96568?hl=en) — and Cloudflare/CrUX field data updates on rolling multi-day-to-28-day windows. Nightly cycles would therefore re-decide on statistically identical noise. For a low-traffic niche directory, meaningful metric movement takes weeks, not hours. A **weekly cadence** (e.g., Sunday night) matches data freshness, keeps token spend trivial, and produces a reviewable PR each Monday. Run a heavier **monthly** cycle for content/seasonal planning and a backlog re-rank. During your 2-weeks-on camp block you'll simply have ~2 PRs and an APPROVALS queue waiting when you get home — exactly the design intent.

## Measurement stack recommendation (free/cheap, agent-ingestible)

| Layer | Recommendation | Why | Setup effort |
|---|---|---|---|
| Search performance | **Google Search Console API** via service account (`webmasters.readonly`) | Free, 25,000 rows/call, the only source of query/impression/click/position; the agent pulls JSON each cycle. The service-account email **must be added as a user inside GSC** or you get 403 — the single most common cause of failed first calls. | ~45 min (GCP project, enable API, create service account, download JSON key, add as GSC user) |
| Analytics | **Cloudflare Web Analytics** (if you host on Cloudflare Pages — which you should) | Cookie-free, no consent banner, privacy-light, free, collects Core Web Vitals; pairs with the recommended host. Alternative: **Umami** self-hosted (MIT license, ~2KB script, single Postgres container, permanent free cloud Hobby tier at 100k events/mo) if you want a stats API you fully own. | ~15 min (CF) / ~1–2 hr (self-host Umami) |
| Performance | **PageSpeed Insights API** (free; with an API key the limit is 25,000 queries/day or 400 per 100 seconds, [DEV Community](https://dev.to/addyosmani/monitoring-performance-with-the-pagespeed-insights-api-33k7) resets midnight Pacific, [Jasmine Directory](https://www.jasminedirectory.com/blog/pagespeed-insights-api-integration-guide/) no charge) for scheduled checks; **Lighthouse CI** locally in the build for regression gating | PSI API gives a JSON score for key pages the agent reads (lab + CrUX field data); Lighthouse-in-build enforces the floor before shipping. | ~20 min (get PSI API key; add lighthouse to build) |
| Form tracking | **Web3Forms** free tier (250 submissions/mo; submissions stored 30 days on free plan; warning emails at 90% and 100% of the limit) → **webhook** to a logging endpoint (Cloudflare Worker/Pages Function writing to CSV/KV, or Google Sheet) | The free tier only emails; to let the agent read submission counts you need the webhook (paid Starter/Pro tier) OR log a monthly count manually. This is the weakest link — see caveats. | ~30 min |
| Uptime | **UptimeRobot** free (or a simple curl check in the workflow) | Guardrail: don't optimize a down site. | ~10 min |

**Total one-evening setup: ~2.5–3 hours.**

## Realistic cost per cycle

- **On subscription (recommended):** Use `CLAUDE_CODE_OAUTH_TOKEN` generated with `claude setup-token`. Per Anthropic's supported path, GitHub Actions runs authenticated with the OAuth token draw from your **subscription quota, not per-token API billing** — no separate invoice. A weekly cycle touching a handful of files is a light Sonnet session, a small fraction of a Max plan's rolling window. **GitHub Actions minutes** are the only hard cost: free unlimited on public repos; private repos draw from your monthly allowance (a ~10–20 min job weekly is negligible). Policy nuance to know: as of the Feb 2026 clarification, OAuth-token usage for *personal* automation is acceptable, but a **dedicated `ANTHROPIC_API_KEY`** is operationally cleaner if the loop's automated usage would eat the interactive quota you need for your own work (the API key takes precedence when both env vars are set).
- **On API billing (if you prefer isolation):** A weekly scoped Sonnet cycle is roughly a few cents to low single-digit dollars of tokens; even generously, well under ~$5–$10/month. Set `--max-turns` and a budget cap (`--max-budget-usd`).
- **Recommendation:** Start on the **OAuth subscription token** (zero marginal cost). Switch the loop to a dedicated **API key** only if the automation starts throttling your interactive Claude usage.

## Guardrail & approval-gate model

**Guardrails that must never regress (loop hard-stops or refuses to ship if violated):**
1. **Lighthouse floor** — performance/SEO/accessibility scores must not drop below a set threshold (e.g., 90/95/95) on key pages.
2. **Indexation health** — production must stay `index,follow`; staging must stay `noindex`. Never flip prod→noindex or staging→index by accident.
3. **Disclaimer presence** — the exact footer disclaimer must be present on every page, verbatim: *"Charter Flight Network is not a charter service provider. We do not own nor operate any aircraft. All charter quotes are generated by our charter network partners."*
4. **Zero invented facts** — no fabricated operators, airports, prices, distances, or claims. If a fact is needed and unverifiable, it goes to APPROVALS.md, not into a page.
5. **No thin-page mass generation** — respect Google's scaled-content-abuse policy: a uniqueness floor per page, consolidate rather than spawn near-duplicate destination pages, cap net new pages per cycle.
6. **Canonical + redirect integrity** — no broken internal links; canonical tags correct.

**Human-approval gates (queued into APPROVALS.md for home-rotation sign-off) — anything touching:**
- **Money/pricing** (lead prices, listing fees, ad spend).
- **Legal** (disclaimer wording changes, terms, privacy policy).
- **Email sending** (any CASL commercial electronic message; list launches; double opt-in copy).
- **Factual claims** needing owner/operator verification (new operator listings, route facts, capacity).
- **Host/DNS/production cutover** (the 301 migration off GitHub Pages).

## Failure modes of autonomous loops — and how this design prevents each

| Failure mode | What it looks like | Prevention in this design |
|---|---|---|
| **Drift** | Agent slowly changes tone/scope, "improves" things nobody asked for, breaks brand/model | Fresh context each cycle (Ralph-style); state lives in files (STATE/BACKLOG/EXPERIMENTS), not a bloated conversation; explicit non-negotiables in the master prompt; PR review by owner |
| **Thin-content spam** | Mass-generated near-duplicate destination/airport pages → Google scaled-content-abuse manual action, traffic collapse | Uniqueness floor + net-new-page cap + "consolidate, don't generate" rule as a hard guardrail; content items requiring facts route to APPROVALS |
| **Breaking the funnel** | Form endpoint removed, CTA hidden, disclaimer dropped, prod set to noindex | Pre-ship VERIFY step: build + link crawl + disclaimer/canonical/noindex checks + form-presence check; hard-stop on failure |
| **Burning usage/cost** | Runaway loop, infinite retries, token blowout | Weekly (not continuous) cadence; `--max-turns` + budget cap; concurrency guard (no overlapping runs); hard-stop on empty metrics or build failure instead of "guessing"; subscription quota ceiling as backstop |

A note on the "Ralph" continuous-loop pattern: it's the right conceptual ancestor (fresh context each iteration, filesystem-and-git as memory, mechanical verification as the exit gate — Claude Code creator Boris Cherny has noted that giving the model a way to verify its work increases quality 2–3×). But a pure `while true` loop is **wrong** for a live revenue site with irreversible external side effects. The documented Ralph disasters — an agent running `terraform destroy` on production (wiping 2.5 years of DataTalks.Club data and all snapshots), and another expanding `rm -rf tests/ patches/ plan/ ~/` to the user's entire home directory — are exactly why this design uses **scheduled discrete cycles + PR-only output + human gates on anything irreversible**, not an unattended infinite loop. Claude Code's newer supported primitives (`/goal`, `/loop`) and the `ralph-loop` plugin exist, but for scheduled unattended runs the GitHub Actions cron + headless `claude -p` pattern is the robust choice.

---

# PART 2 — COPY-PASTE-READY ARTIFACTS

## (a) SCHEDULER SETUP

### One-time setup steps

**1. Secrets (GitHub → repo Settings → Secrets and variables → Actions):**
```
CLAUDE_CODE_OAUTH_TOKEN   # run `claude setup-token` locally, paste output
GSC_SA_KEY               # contents of the GCP service-account JSON key
PSI_API_KEY              # PageSpeed Insights API key
GSC_SITE                 # e.g. sc-domain:charterflightnetwork.com
```

**2. Search Console service account:**
```
1. console.cloud.google.com → create/select a project
2. Enable "Google Search Console API"
3. IAM & Admin → Service Accounts → Create (e.g. cfn-loop-reader)
4. Create a JSON key → download → paste whole file into GSC_SA_KEY secret
5. In Search Console → Settings → Users and permissions →
   Add the service-account email (…iam.gserviceaccount.com) as a
   "Restricted"/read user.   ← REQUIRED or every call 403s
```

**3. PageSpeed Insights API key:** Google Cloud Console → APIs & Services → Credentials → Create API key → restrict to PageSpeed Insights API → store as `PSI_API_KEY`.

**4. Analytics wiring:** If on Cloudflare Pages, enable Web Analytics in the CF dashboard and add the provided beacon snippet to your Astro base layout (before `</body>`). If self-hosting Umami, add the `<script>` tag and note the stats API endpoint for the metrics puller.

**5. Metrics puller script** — commit this as `scripts/pull_metrics.py`:
```python
#!/usr/bin/env python3
"""Pull GSC + PSI metrics into METRICS/ as dated JSON. Fails loudly (exit 1)
so the loop can hard-stop on empty ingestion."""
import os, sys, json, datetime, urllib.request, urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build

OUT = "METRICS"; os.makedirs(OUT, exist_ok=True)
today = datetime.date.today().isoformat()
target = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()  # GSC 2-3 day lag

# ---- GSC ----
key = json.loads(os.environ["GSC_SA_KEY"])
site = os.environ["GSC_SITE"]
creds = service_account.Credentials.from_service_account_info(
    key, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
svc = build("searchconsole", "v1", credentials=creds)
gsc = {}
try:
    for dims in (["query"], ["page"]):
        body = {"startDate": (datetime.date.today()-datetime.timedelta(days=31)).isoformat(),
                "endDate": target, "dimensions": dims, "rowLimit": 25000, "dataState": "final"}
        gsc["_".join(dims)] = svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
except Exception as e:
    print(f"FAIL GSC: {e}", file=sys.stderr); sys.exit(1)
if not gsc.get("query") and not gsc.get("page"):
    print("FAIL GSC: empty result", file=sys.stderr); sys.exit(1)
json.dump(gsc, open(f"{OUT}/gsc_{today}.json","w"), indent=2)

# ---- PageSpeed Insights ----
psi_key = os.environ["PSI_API_KEY"]
pages = ["https://charterflightnetwork.com/",
         "https://charterflightnetwork.com/thunder_bay_charter_flights.htm"]
psi = {}
for url in pages:
    api = ("https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
           f"?url={urllib.parse.quote(url)}&strategy=mobile&category=performance"
           f"&category=seo&key={psi_key}")
    try:
        data = json.load(urllib.request.urlopen(api, timeout=90))
        psi[url] = {c: data["lighthouseResult"]["categories"][c]["score"]
                    for c in data["lighthouseResult"]["categories"]}
    except Exception as e:
        print(f"WARN PSI {url}: {e}", file=sys.stderr)
json.dump(psi, open(f"{OUT}/psi_{today}.json","w"), indent=2)
print(f"OK metrics written for {today}")
```

### GitHub Actions workflow (`.github/workflows/revenue-loop.yml`)

```yaml
name: Revenue Optimization Loop
on:
  schedule:
    - cron: "0 8 * * 0"          # Sundays 08:00 UTC
  workflow_dispatch:             # manual trigger for testing

concurrency:
  group: revenue-loop            # concurrency guard: never overlap runs
  cancel-in-progress: false

permissions:
  contents: write                # create branch/commits
  pull-requests: write           # open PR
  id-token: write

jobs:
  loop:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - uses: actions/setup-node@v4
        with: { node-version: "20" }

      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      - name: Install deps
        run: |
          npm ci
          pip install google-api-python-client google-auth

      - name: Pull metrics (hard-stop on empty)
        env:
          GSC_SA_KEY: ${{ secrets.GSC_SA_KEY }}
          GSC_SITE:   ${{ secrets.GSC_SITE }}
          PSI_API_KEY: ${{ secrets.PSI_API_KEY }}
        run: python scripts/pull_metrics.py

      - name: Run Claude Code loop (PR-only, scoped tools)
        uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          prompt_file: .claude/MASTER_LOOP_PROMPT.md
          claude_args: >
            --max-turns 40
            --model claude-sonnet-4-6
            --allowedTools "Read,Edit,Write,Glob,Grep,
            Bash(npm run build),Bash(npm run lint),
            Bash(npx lhci autorun*),Bash(git add*),Bash(git checkout -b*),
            Bash(git commit*),Bash(git push*),Bash(gh pr create*),
            Bash(node scripts/*),Bash(python scripts/*)"
            --disallowedTools "Bash(rm *),Bash(curl *),Bash(git push origin main*)"
```

Notes: the action **commits to a branch and returns a PR** — by design it does not push to main. `--allowedTools` scopes execution to build/test/git-branch/PR only; destructive commands and pushes to `main` are explicitly denied via `--disallowedTools`. Pin the action to an immutable SHA in production if you want reproducibility. (A known gotcha: cron-triggered runs can fail OIDC/GitHub-App token exchange where manual `workflow_dispatch` succeeds — if you hit "User does not have write access," authenticate with the OAuth token/PAT path shown here rather than a custom GitHub App.)

### Windows PowerShell / Task Scheduler variant (run from your desktop)

`C:\cfn-loop\run-loop.ps1`:
```powershell
# Charter Flight Network - weekly revenue loop (local desktop variant)
$ErrorActionPreference = "Stop"
Set-Location "C:\cfn-loop\Charterflightnetwork"

# Ensure we're on a fresh sync of the modernization branch
git fetch origin
git checkout claude/cfn-modernization-okp1pe
git pull --ff-only

# 1. Pull metrics (hard-stop on failure)
$env:GSC_SA_KEY  = Get-Content "C:\cfn-loop\secrets\gsc_sa.json" -Raw
$env:GSC_SITE    = "sc-domain:charterflightnetwork.com"
$env:PSI_API_KEY = (Get-Content "C:\cfn-loop\secrets\psi_key.txt" -Raw).Trim()
python scripts\pull_metrics.py
if ($LASTEXITCODE -ne 0) { Write-Error "Metrics ingestion failed - aborting"; exit 1 }

# 2. Run Claude Code headless. Uses subscription (OAuth) since you're logged in
#    locally via `claude setup-token` / `claude login`.
#    --permission-mode dontAsk = fully non-interactive; only pre-approved tools run,
#    anything else is auto-denied (nothing hangs waiting for input).
claude -p (Get-Content ".claude\MASTER_LOOP_PROMPT.md" -Raw) `
  --model claude-sonnet-4-6 `
  --max-turns 40 `
  --permission-mode dontAsk `
  --allowedTools "Read,Edit,Write,Glob,Grep,Bash(npm run build),Bash(npm run lint),Bash(npx lhci autorun*),Bash(git add*),Bash(git checkout -b*),Bash(git commit*),Bash(git push*),Bash(gh pr create*),Bash(node scripts/*),Bash(python scripts/*)" `
  --disallowedTools "Bash(rm *),Bash(git push origin main*)" `
  --output-format json 2>&1 | Tee-Object "C:\cfn-loop\logs\loop_$(Get-Date -f yyyyMMdd).log"

if ($LASTEXITCODE -ne 0) { Write-Warning "Loop exited non-zero - see log" }
```

Register it (run once in an elevated PowerShell):
```powershell
$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\cfn-loop\run-loop.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 8am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
  -DontStopOnIdleEnd -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "CFN Revenue Loop" -Action $action `
  -Trigger $trigger -Settings $settings -Description "Weekly Claude Code revenue loop"
```
`-StartWhenAvailable` ensures the task runs when your desktop next wakes if it was off Sunday morning (important given your FIFO rotation). **Prefer the GitHub Actions variant as primary** (it runs even when your PC is off during camp) and keep the PowerShell variant as a manual/backup path. Do **not** use `--dangerously-skip-permissions` here — this runs against a checkout that can push to your real repo; the scoped `--permission-mode dontAsk` + `--allowedTools` combination is the correct non-interactive posture. Reserve bypass mode strictly for throwaway containers.

## (b) THE MASTER LOOP PROMPT (`.claude/MASTER_LOOP_PROMPT.md`)

```markdown
# Charter Flight Network — Weekly Revenue-Optimization Loop

You are the autonomous optimization agent for charterflightnetwork.com, a
Thunder Bay, Ontario AIR CHARTER QUOTE NETWORK. Execute ONE cycle, then stop.

## BUSINESS MODEL (NON-NEGOTIABLE — never contradict)
- Visitors submit FREE quote requests → forwarded to charter operators →
  visitor receives up to 3 competitive quotes by email → books DIRECTLY with
  the operator.
- Charter Flight Network is NOT an air carrier and does not own/operate aircraft.
- REVENUE = organic/direct traffic × quote-form conversion rate × lead
  quality/acceptance × price-per-lead + operator featured-listing upgrades.
  Secondary: empty-legs page, email alert list.
- Every page MUST contain this exact footer disclaimer, verbatim:
  "Charter Flight Network is not a charter service provider. We do not own nor
  operate any aircraft. All charter quotes are generated by our charter network
  partners."

## HARD NON-NEGOTIABLES
1. NEVER invent facts: no fake operators, airports, distances, prices,
   capacities, routes, or testimonials. If a page needs a fact you cannot
   verify from existing repo content, DO NOT write it — queue it in APPROVALS.md.
2. PRESERVE the disclaimer and the quote-network business model on every page.
3. RESPECT Google scaled-content-abuse policy: enforce a uniqueness floor
   (each destination/location page must add genuine, non-templated value);
   CONSOLIDATE thin/near-duplicate pages rather than mass-generating new ones;
   create at most 2 net-new content pages per cycle.
4. CASL/PIPEDA: do NOT send any commercial email and do NOT ship an active
   email-capture that sends CEMs without owner approval. Any email/list feature
   must use double opt-in, unchecked-by-default consent, sender identification,
   and a working unsubscribe (functional ≥60 days) — and MUST be queued in
   APPROVALS.md before going live.
5. NEVER push to main. Open a PR. NEVER touch pricing, legal text, money spend,
   or email sends without queuing to APPROVALS.md.

## STEP 1 — READ STATE
Read: STATE.md, BACKLOG.md, EXPERIMENTS.md, APPROVALS.md, and the newest files
in METRICS/ (gsc_*.json, psi_*.json, and any analytics/form logs).
If METRICS/ has no file dated within the last 2 days → HARD STOP (see failure).

## STEP 2 — COMPUTE KPI-TREE DELTAS
Build the funnel and compare to the snapshot in STATE.md:
  impressions → clicks (CTR) → sessions → quote submissions →
  qualified leads → revenue.
Note which stage moved and by how much. Flag any guardrail regression
(Lighthouse score drop, indexation change, lost impressions on key pages).

## STEP 3 — RE-SCORE BACKLOG (ICE)
For each BACKLOG.md item compute ICE = Impact × Confidence × Ease (1–10 each),
and add a one-line PROJECTED REVENUE rationale tied to the KPI tree.
Re-sort. Exclude any item that is human-gated (money/pricing/legal/email/
unverified facts) — those stay queued, not implemented.

## STEP 4 — IMPLEMENT TOP 1–3
Select the top 1–3 non-gated items that fit guardrails and one cycle's scope.
Make minimal, focused changes on a new branch:
  git checkout -b loop/YYYY-MM-DD-<slug>
Prefer reversible, high-leverage changes. Do not refactor unrelated code.

## STEP 5 — VERIFY (pre-ship gate; HARD STOP on any failure)
Run and require passing:
  - `npm run build`  (must succeed)
  - link crawl of the build output (no broken internal links)
  - `npx lhci autorun` or PSI check on changed key pages
    (performance/SEO must not drop below floor in STATE.md)
  - disclaimer check: exact disclaimer string present on every built page
  - canonical + noindex check: production stays index,follow; staging noindex
  - uniqueness check on any new/edited content page
If any check fails → do NOT ship. Write a FAILURE REPORT (see below) and stop.

## STEP 6 — SHIP (PR ONLY)
Commit with a structured message and open a PR:
  gh pr create --title "Loop YYYY-MM-DD: <items>" --body <changelog>
Changelog MUST include: items shipped, KPI hypothesis per item, guardrail
check results, and links to the EXPERIMENTS.md entries.
NEVER merge. NEVER push to main.

## STEP 7 — LOG & QUEUE
- Append to EXPERIMENTS.md one block per shipped item:
  hypothesis / metric-to-watch / expected direction / READ-DATE (next cycle+2wk).
- Update STATE.md: new KPI snapshot, current Lighthouse floor, date, cycle #.
- Move shipped items out of BACKLOG.md "active".
- Append to APPROVALS.md any human-gated item discovered this cycle
  (pricing, CASL email sends, money spend, factual claims needing operator
  verification, host/DNS/301 cutover), each with context and the specific
  decision the owner must make.

## FAILURE MODE (instead of guessing)
If: build fails, metrics ingestion is empty/stale, a guardrail regressed, or
you cannot complete an item safely — STOP and write FAILURE_REPORT.md with:
what failed, the exact error/evidence, what you did NOT change, and the
recommended human action. Do NOT invent data, do NOT force a partial ship,
do NOT disable a guardrail to make a check pass.
```

## (c) SEED FILES

### `BACKLOG.md`

```markdown
# BACKLOG — Revenue-ranked (ICE = Impact×Confidence×Ease, each 1–10; score = product)
# Human-gated items are marked [GATE] and are NOT auto-implemented.

## P0 — Launch-readiness / funnel integrity
1. Wire working form endpoint (Web3Forms, free 250/mo) + success/redirect state
   ICE: 10×9×8 = 720 | Rev: no working form = zero leads = zero revenue. Highest.
2. [GATE] Production 301 host move off GitHub Pages → Cloudflare Pages/Netlify
   ICE: 9×8×5 = 360 | Rev: preserves legacy .htm equity; enables real 301s +
   CF Web Analytics + edge split-testing. GATE: DNS/host cutover = owner action.
3. Production noindex→index toggle at launch (keep staging noindex)
   ICE: 10×9×7 = 630 | Rev: unindexed site earns nothing organically.
4. GSC verification + sitemap submission + service-account read access
   ICE: 8×9×8 = 576 | Rev: no measurement = blind loop; unlocks the whole stack.
5. Form-submission logging via Web3Forms webhook → CSV/KV the agent can read
   ICE: 8×8×6 = 384 | Rev: closes the loop on the conversion metric.

## P1 — Conversion-rate optimization (low-traffic appropriate)
6. Convert single quote form → multi-step (progress bar; contact fields last)
   ICE: 9×7×6 = 378 | Rev: multi-step lead forms average ~13.9% vs ~4.5% for
   single-page (Formstack); HubSpot reports 86% higher conversion. More
   submissions at same traffic.
7. Prominent click-to-call on mobile (tel: link, above fold) + call tracking
   ICE: 8×8×7 = 448 | Rev: captures high-intent visitors who won't fill a form.
8. Trust signals near form: "up to 3 competitive quotes", "no cost", privacy note,
   response-time promise (e.g., "quotes within 24h") — [GATE if promising a time]
   ICE: 8×7×7 = 392 | Rev: reduces form hesitation; guardrail metric = submit rate.
9. Fix content-migration artifacts + thin destination pages (consolidate)
   ICE: 8×8×5 = 320 | Rev: removes scaled-content-abuse risk; protects rankings.
10. About-page: remove puffery, add honest E-E-A-T (online since 2008, network scope)
    ICE: 6×7×7 = 294 | Rev: trust/credibility → conversion + E-E-A-T signal.

## P2 — Revenue-model levers
11. [GATE] Operator featured-listing page + upgrade tiers (pricing owner-set)
    ICE: 9×6×5 = 270 | Rev: featured listings are a core revenue line and a
    cleaner early monetization than per-lead. Niche B2B directory featured
    listings command ~$99–$500/mo (comparable verticals). GATE: pricing.
12. [GATE] Empty-leg email alert list w/ CASL-compliant double opt-in
    ICE: 8×6×4 = 192 | Rev: builds a re-engageable audience. GATE: CASL + sending.
13. Seasonal fly-in fishing content ahead of open-water season (spring)
    ICE: 8×7×6 = 336 | Rev: captures peak-intent seasonal search; timed content.
14. Per-province / per-region landing improvements (real facts only)
    ICE: 7×6×5 = 210 | Rev: long-tail organic capture; uniqueness floor enforced.
15. Empty-legs page: structured, honest, "flexible dates" CTA to quote form
    ICE: 7×6×6 = 252 | Rev: secondary funnel entry; low-cost, high-intent.
16. Winter/mining/ice-road & hunting-season content blocks (seasonal timing)
    ICE: 7×6×5 = 210 | Rev: diversifies beyond fishing; matches regional demand.
17. Internal linking pass: hub (Thunder Bay) → destination → quote form
    ICE: 7×7×7 = 343 | Rev: distributes equity, shortens path to conversion.
18. Digital-PR / backlink targets list for a niche directory (outreach = GATE)
    ICE: 7×5×4 = 140 | Rev: authority for rankings. [GATE] if any outreach/spend.
19. Schema.org markup (LocalBusiness/Service) — facts only
    ICE: 6×7×6 = 252 | Rev: rich results / eligibility; SEO hygiene.
20. Structured operator directory data model (name/base/aircraft — verified only)
    ICE: 7×6×4 = 168 | Rev: foundation for featured listings + unique content.

## EXPLICITLY REJECTED
- Display ads / third-party affiliate banners: REJECT. They cheapen a lead-gen
  funnel, distract from the single conversion goal (quote request), add cookie/
  consent overhead, and revenue-per-session is trivial vs a qualified charter
  lead (charter trips are very high value: e.g., turboprop 2-hr charters run
  ~$2,500–$5,000; a single booked trip dwarfs any ad impression revenue).
```

### `STATE.md`

```markdown
# STATE — Charter Flight Network Revenue Loop
Cycle #: 0
Last run (UTC):  <YYYY-MM-DD>
Branch under optimization: claude/cfn-modernization-okp1pe
Production host: <GitHub Pages staging | Cloudflare Pages prod>
Indexation: staging=noindex ; production=<not launched>

## GUARDRAIL FLOORS (do not regress)
Lighthouse (mobile) — Performance ≥ 90 | SEO ≥ 95 | Accessibility ≥ 95
Disclaimer present on 100% of pages: REQUIRED
Max net-new content pages per cycle: 2
Uniqueness floor per page: REQUIRED

## KPI SNAPSHOT (updated each cycle)
Window: <date range>
Impressions:      <n>   (Δ vs last: —)
Clicks:           <n>   (Δ: —)
CTR:              <%>   (Δ: —)
Avg position:     <n>   (Δ: —)
Sessions:         <n>   (Δ: —)
Quote submissions:<n>   (Δ: —)
Qualified leads:  <n>   (owner-reported; Δ: —)
Revenue:          <$>   (owner-reported; Δ: —)

## TOP PAGES / QUERIES TO WATCH
- <page> — <query> — <impressions/clicks/pos>

## OPEN NOTES
- <anything the next cycle should know>
```

### `EXPERIMENTS.md`

```markdown
# EXPERIMENTS LOG (append-only)

## TEMPLATE
### [YYYY-MM-DD] <experiment name>  (PR #<n>)
- Hypothesis: If we <change>, then <KPI> will <direction> because <reason>.
- Change shipped: <what>
- Primary metric: <e.g., quote submission rate>
- Guardrail metrics (must not regress): <Lighthouse / impressions / disclaimer>
- Baseline value: <n>
- READ DATE: <YYYY-MM-DD> (≥2 weeks out, accounts for GSC 2-3 day lag +
  multi-week signal at low traffic)
- Result (filled on read date): <win/flat/loss + numbers>
- Decision: <keep / revert / iterate>
```

### `APPROVALS.md`

```markdown
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
  aircraft types, and the agreed price-per-qualified-lead (and featured-listing
  fee). NO published per-lead rate exists for charter lead-gen — the industry
  monetizes via subscriptions (e.g., Avinode marketplace access, competitor-cited
  "up to $2,119 per month") [SkyAccess](https://skyaccess.com/blog/avinode-alternative-for-operators) and commissions, so YOU must set the price by
  direct operator agreement. The loop must never invent it.
- Why: Everything downstream (featured listings, lead pricing, revenue math)
  depends on these real facts.
- Decision needed: operator list + pricing.

### [seed] Approve production 301 host migration off GitHub Pages
- Category: HOST/DNS
- What: Move production to Cloudflare Pages (or Netlify) so real 301 redirects
  for hundreds of legacy .htm URLs work, and enable CF Web Analytics + edge tests.
- Why: GitHub Pages cannot serve real 301s; preserving legacy URL equity is
  critical to not lose existing rankings at launch.
- Decision needed: approve host + point DNS.

### [seed] Approve empty-leg email alert list (CASL)
- Category: EMAIL/CASL
- What: Launch a double-opt-in alert list (unchecked consent box, sender
  identification with mailing address + contact, working unsubscribe honored
  within 10 business days and functional ≥60 days, consent records retained
  3 years).
- Why: Re-engageable audience for empty legs / seasonal offers.
- Decision needed: approve list + confirm sending identity/address.
```

**CASL/PIPEDA quick reference for the owner** (from CRTC/ISED guidance): a commercial electronic message needs (1) consent — express (opt-in, unchecked box, active step) or implied (e.g., existing business relationship, or a conspicuously published address with no "no CEMs" notice); (2) sender identification (name + mailing address + phone/email/web); and (3) a working unsubscribe (no cost, honored within 10 business days, functional ≥60 days). Express consent doesn't expire; **purchased lists are a violation**; penalties reach up to **$1M for individuals and $10M for businesses** per violation. Keep consent records for 3 years. A quote/estimate the visitor requested is a transactional exception to *consent* but still needs ID + unsubscribe — which is exactly why the core quote-request flow is fine, but any marketing list is gated.

---

# PART 3 — FIRST 90 DAYS

## Realistic traffic & lead math

This is a niche Canadian charter directory, not a high-volume consumer site. Be conservative. After a clean launch (indexed, 301s preserved, working form), expect low-hundreds-to-low-thousands of organic sessions per month, heavily **seasonal** — spikes ahead of open-water fly-in fishing season (spring/early summer) and hunting season, with secondary winter mining/industrial demand out of Thunder Bay (YQT), which is a genuine northern gateway to remote lodges, mines, and exploration camps. Illustrative funnel on, say, 800 sessions/month:

- 800 sessions × quote-form conversion rate → **submissions**. Single-step service forms convert in the low single digits (Ruler Analytics puts B2B services form conversion at ~2.2%); a well-built **multi-step** quote form materially outperforms that (Formstack: ~13.9% multi-page vs ~4.5% single-page; [Numinam](https://www.numinam.com/en/blog/multi-step-vs-single-page-forms-which-really-generates-more-leads-complete-guide-2026) BrokerNotes went 11%→46% in B2C financial lead-gen after switching). At 2% you get ~16 submissions/month; a strong multi-step form could push that several-fold higher.
- Of submissions, a fraction are **qualified** (real trip, dates, contactable). Expect drop-off; treat ~50–70% qualified as a working assumption until you have data.
- **Qualified leads → operator revenue**: this is where you monetize. There is **no published pay-per-lead price for charter/aviation lead-gen** — the industry runs on subscriptions and commissions, not per-lead fees. Price must be set by direct operator agreement. Use adjacent verticals only as directional anchors — high-ticket service leads range widely: home-services leads $15–$120+ (shared 3–8 ways), [LeadTruffle](https://www.leadtruffle.co/blog/complete-guide-angi-leads-home-service-contractors-2026/) legal ~$111 average paid-search CPL, [LocaliQ](https://localiq.com/blog/legal-search-advertising-benchmarks/) insurance exclusive leads $75–$150, [ActiveProspect](https://activeprospect.com/blog/insurance-leads-cost/) luxury travel inquiries $80–$200 [CausalFunnel](https://www.causalfunnel.com/blog/what-is-cost-per-lead-cpl-for-travel-businesses-complete-2025-guide/) — and remember a booked charter trip is worth thousands to tens of thousands, which supports a **premium** qualified-lead price.

The honest takeaway: at launch you optimize a **small-numbers** funnel. **Classic A/B testing will NOT reach statistical significance at this volume** — do not run split tests expecting p-values (you'll burn weeks on "inconclusive"). [Kraken Data](https://www.krakendata.com/blog/cro-for-low-traffic-sites-how-to-run-tests-that-actually-teach-you-something/) Instead: (1) ship obvious fixes without testing (broken form, invisible CTA, slow mobile load are fixes, not experiments); [Grow-conversions](https://grow-conversions.com/blog/cro-low-traffic/) (2) use **sequential before/after** comparisons over multi-week windows with guardrail metrics; (3) run qualitative review (~5 user walkthroughs surface ~80% of usability issues per Nielsen Norman research); and (4) make **high-leverage "big swing"** changes (form structure, click-to-call, trust signals) rather than micro-tweaks. Reserve edge split-testing (Cloudflare Workers/Pages Functions, zero-flicker, cookie-persisted variant) [DEV Community](https://dev.to/sohanaakbar7/ab-testing-at-warp-speed-how-cloudflare-workers-revolutionize-html-experiments-1kdf) for when traffic actually justifies it.

## When to raise lead prices or approach operators

- **First ~30 days:** focus entirely on funnel integrity and indexation. Don't touch pricing. Establish the baseline KPI snapshot.
- **Days 30–60:** once you have a consistent flow of *qualified* submissions and operator feedback on lead quality, you have leverage. Approach operators with real acceptance data ("X qualified quote requests forwarded, Y led to bookings").
- **Days 60–90 and beyond — raise lead prices / add featured listings when:** (a) qualified-lead volume is steady and predictable, (b) operators are accepting and valuing the leads (booking from them), and (c) you can demonstrate lead→booking conversion. That evidence — not a calendar date — is the trigger. **Featured directory listings are the cleaner first monetization** than per-lead pricing because they're a flat recurring fee operators can commit to (comparable niche B2B directories charge roughly $99–$500/mo for featured placement); [TurnKeyDirectories](https://turnkeydirectories.com/online-directory-pricing-how-much-charge-listings/) per-lead pricing follows once you can prove lead quality.

## The single highest-leverage MANUAL action the loop cannot do

**Grandpa confirming the real operator relationships and setting per-lead / featured-listing pricing.** The loop can optimize traffic and conversion all day, but it is forbidden from inventing operators, aircraft, or prices — and there is no market rate to look up for charter lead-gen. Revenue only materializes when real operators agree to pay for qualified leads and/or featured placement. That relationship-and-pricing work is 100% human, it's the top pre-seeded item in APPROVALS.md, and it gates the entire P2 revenue tier. Everything the loop does is leverage on top of that foundation; without it, the loop is polishing a funnel that has nothing to monetize.

**Stand-it-up-in-one-evening checklist:** (1) launch the modernization PR (form wired, prod indexable, 301s planned); (2) ~2.5 hr measurement setup (GSC service account, PSI key, CF/Umami analytics, Web3Forms webhook, uptime); (3) drop in the four seed files + master prompt + `pull_metrics.py`; (4) add the GitHub Actions workflow with the four secrets; (5) trigger once via `workflow_dispatch` to smoke-test; (6) leave APPROVALS.md for grandpa.

## Caveats
- **Form-metric closure is the weakest link.** Web3Forms' free tier only emails submissions (250/mo cap, 30-day storage); to make submission counts machine-readable for the agent you need the paid webhook tier or a manual monthly count. If lead volume grows, move to a small backend (Cloudflare Pages Function → KV/D1) that logs submissions you own.
- **Qualified-lead and revenue KPIs are owner-reported**, not automatically measurable — the loop can compute impressions→sessions→submissions from APIs but cannot know which leads operators accepted or paid for. You must feed those numbers into STATE.md.
- **OAuth-token automation policy is evolving.** Anthropic's Feb/April 2026 changes restrict subscription tokens to official tools and separate third-party/automation usage; the `claude-code-action` OAuth path is supported for personal automation today, but if policy tightens or the loop throttles your interactive work, switch to a dedicated API key. Treat the subscription-covers-Actions behavior as a current, not permanent, benefit.
- **No published charter per-lead price exists** — this is a genuine market gap, not a research miss. All per-lead figures cited are from adjacent verticals and are directional only. Set real pricing by operator agreement.
- **Pricing/plan figures** (Avinode "$2,119/mo," Claude tiers, directory listing ranges) come partly from competitor marketing and third-party blogs and can change; verify against primary sources before acting on any dollar decision.
- **Google spam enforcement is ongoing** (spam updates through 2025–2026 targeting scaled content abuse); the uniqueness floor and net-new-page cap are not optional hygiene — a manual action can suppress the whole site until a reconsideration request is approved (weeks to months). When in doubt, consolidate, don't generate.