# Charter Flight Network

Modern static rebuild of [charterflightnetwork.com](https://charterflightnetwork.com) —
a Thunder Bay, Ontario based air charter quote network. Astro + Tailwind CSS,
fully static output, migrated 1:1 from the legacy `.htm` site with a complete
301 redirect map.

- **`MIGRATION_REPORT.md`** — full migration report: inventory, redirect
  coverage, verification results, open TODOs, and step-by-step deploy
  instructions for shared hosting (Apache) and Netlify.
- **`crawl/`** — the migration pipeline (crawler, extractor, content generator,
  redirect generator, verifier) plus the cached legacy site and inventory.
- **`src/content/`** — one markdown file per migrated page (destinations, hubs,
  directory, pages) with SEO frontmatter.
- **`redirects/.htaccess`** and **`public/_redirects`** — the 301 maps.

## Quick start

```
npm install
npm run dev      # local dev server
npm run build    # static site → dist/
python3 crawl/verify.py  # after build: redirect + dead-link verification
```
