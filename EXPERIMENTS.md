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

## BASELINE (pre-loop)
### [2026-07-19] Full site modernization (PR #1)
- Change shipped: 1,046-page migration to Astro/Tailwind, 301 map, quote
  funnel preserved, Lighthouse 100/100/100 baseline, audit hardening.
- Primary metric: none (baseline). All future experiments compare against
  the first post-launch KPI snapshot in STATE.md.
